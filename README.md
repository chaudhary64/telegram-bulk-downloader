# Telegram Bulk Downloader

A small Python tool that downloads videos from a Telegram channel using Telethon. It keeps a local download folder, skips files that already exist, and shows a compact progress dashboard with total videos, remaining videos, and ETA.

## Features

- Downloads channel videos to a local folder
- Skips files that were already downloaded
- Shows overall progress and per-file progress in the terminal
- Loads configuration from a `.env` file automatically

## Requirements

- Python 3.14+ (works with the workspace venv)
- A Telegram API ID and API hash
- Access to the target Telegram channel

## GitHub Setup

If you want to use the repository from GitHub, clone it first:

```powershell
git clone https://github.com/chaudhary64/telegram-bulk-downloader
cd telegram-bulk-downloader
```

Then create your `.env` file, install dependencies, and run the script using the steps below.

## Setup

Create a virtual environment and install dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Configuration

Create a `.env` file in the project root. You can copy `.env.example`:

```env
TELETHON_API_ID=TELETHON_API_ID
TELETHON_API_HASH=TELETHON_API_HASH
TELETHON_CHANNEL_LINK=TELETHON_CHANNEL_LINK
```

The script also falls back to the built-in defaults if those values are not set.

## Run

```powershell
python -u .\downlaod.py
```

The first run may ask you to sign in to Telegram. After that, the session is reused from `session.session`.

## Output

Downloaded videos are saved in:

```text
telegram_videos/
```

## Notes

- The script uses sequential downloads with a larger download chunk size for stability and throughput.
- `cryptg` is included to speed up Telegram file decryption when available.
- If you want to download from a different channel, update `TELETHON_CHANNEL_LINK` in `.env`.
