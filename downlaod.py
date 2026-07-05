import os
import asyncio
from datetime import datetime
from dotenv import load_dotenv
from telethon.sync import TelegramClient
from tqdm import tqdm

# =========================
# CONFIG
# =========================

load_dotenv()

api_id = int(os.getenv("TELETHON_API_ID"))
api_hash = os.getenv("TELETHON_API_HASH")

channel_link = os.getenv("TELETHON_CHANNEL_LINK")
download_folder = "telegram_videos"
MAX_CONCURRENT_DOWNLOADS = 3
PART_SIZE_KB = 512

# =========================

os.makedirs(download_folder, exist_ok=True)

client = TelegramClient("session", api_id, api_hash)

BAR_FORMAT = "{desc}: {percentage:3.0f}%|{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}]"


def get_download_target(message):
    # Try to get the original filename when Telegram provides one.
    if message.file and message.file.name:
        return message.file.name
    return f"{message.id}.mp4"


def format_seconds(seconds):
    if seconds is None:
        return "unknown"

    seconds = max(0, int(seconds))
    hours, remainder = divmod(seconds, 3600)
    minutes, secs = divmod(remainder, 60)

    if hours:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    return f"{minutes:02d}:{secs:02d}"


def prompt_yes_no(question):
    while True:
        answer = input(f"{question} [y/n]: ").strip().lower()
        if answer in {"y", "yes"}:
            return True
        if answer in {"n", "no"}:
            return False
        print("Please answer with y or n.")


def prompt_cutoff_date():
    while True:
        raw_value = input("Enter the start date (YYYY-MM-DD): ").strip()
        try:
            return datetime.strptime(raw_value, "%Y-%m-%d").date()
        except ValueError:
            print("Please enter a valid date in YYYY-MM-DD format.")


def message_is_on_or_after(message, cutoff_date):
    return message.date is not None and message.date.date() >= cutoff_date


async def main():
    entity = await client.get_entity(channel_link)

    use_date_filter = prompt_yes_no(
        "Do you want to download videos from a specific date till latest"
    )
    cutoff_date = prompt_cutoff_date() if use_date_filter else None

    videos = []

    async for message in client.iter_messages(entity):
        if cutoff_date and message.date and message.date.date() < cutoff_date:
            break

        if message.video:
            if cutoff_date and not message_is_on_or_after(message, cutoff_date):
                continue

            filename = get_download_target(message)
            file_path = os.path.join(download_folder, filename)
            file_size = message.file.size or 0

            videos.append({
                "message": message,
                "filename": filename,
                "file_path": file_path,
                "file_size": file_size,
                "already_downloaded": os.path.exists(file_path),
            })

    total_videos = len(videos)
    pending_videos = [item for item in videos if not item["already_downloaded"]]
    skipped_videos = total_videos - len(pending_videos)
    total_bytes = sum(item["file_size"] for item in pending_videos)

    tqdm.write("")
    tqdm.write("Download summary")
    tqdm.write(
        f"Total videos: {total_videos} | Already downloaded: {skipped_videos} | To download: {len(pending_videos)}"
    )
    tqdm.write("")

    if not pending_videos:
        print("Done!")
        return

    overall = tqdm(
        total=total_bytes,
        unit="B",
        unit_scale=True,
        desc=f"All videos | left={len(pending_videos)} | eta=unknown",
        position=0,
        dynamic_ncols=True,
        colour="green",
        bar_format=BAR_FORMAT,
    )

    files = tqdm(
        total=len(pending_videos),
        unit="video",
        desc="Videos completed | 0/" + str(len(pending_videos)),
        position=1,
        dynamic_ncols=True,
        colour="cyan",
        bar_format=BAR_FORMAT,
    )

    completed_files = 0
    progress_lock = asyncio.Lock()

    async def download_one(item):
        nonlocal completed_files

        filename = item["filename"]
        file_path = item["file_path"]
        message = item["message"]

        async def on_progress(current, total):
            async with progress_lock:
                overall.total = total_bytes
                overall.n = min(overall.total, overall.n + max(0, current - on_progress.last_current))
                overall.refresh()

                remaining_videos = len(pending_videos) - completed_files
                eta_text = format_seconds(overall.format_dict.get("remaining"))
                overall.set_description_str(
                    f"All videos | left={remaining_videos} | eta={eta_text}"
                )
                on_progress.last_current = current

        on_progress.last_current = 0

        await client.download_file(
            message.media.document,
            file=file_path,
            part_size_kb=PART_SIZE_KB,
            file_size=item["file_size"],
            progress_callback=on_progress,
        )

        async with progress_lock:
            completed_files += 1
            files.n = completed_files
            files.refresh()
            overall.set_description_str(
                f"All videos | left={len(pending_videos) - completed_files} | eta={format_seconds(overall.format_dict.get('remaining'))}"
            )
            files.set_description_str(
                f"Videos completed | {completed_files}/{len(pending_videos)}"
            )

    queue = asyncio.Queue()
    for item in pending_videos:
        queue.put_nowait(item)

    async def worker():
        while True:
            try:
                item = queue.get_nowait()
            except asyncio.QueueEmpty:
                return

            try:
                await download_one(item)
            finally:
                queue.task_done()

    workers = [asyncio.create_task(worker()) for _ in range(min(MAX_CONCURRENT_DOWNLOADS, len(pending_videos)))]

    try:
        await asyncio.gather(*workers)
        overall.set_description_str("All videos | left=0 | eta=00:00")
        files.set_description_str(f"Videos completed | {len(pending_videos)}/{len(pending_videos)}")
    finally:
        for worker_task in workers:
            worker_task.cancel()
        files.close()
        overall.close()

    print("Done!")


with client:
    client.loop.run_until_complete(main())