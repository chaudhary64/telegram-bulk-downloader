# Telegram Bulk Downloader

A small Python tool that downloads videos from a Telegram channel using Telethon. It keeps a local download folder, skips files that already exist, and shows a compact progress dashboard with total videos, remaining videos, and ETA.

## Features

- Downloads channel videos to a local folder
- Skips files that were already downloaded
- Shows overall progress and per-file progress in the terminal
- Loads configuration from a `.env` file automatically
- Supports large Telegram media files
- Faster downloads using `cryptg`

## Requirements

- Python 3.14+
- A Telegram API ID and API hash
- Access to the target Telegram channel

## GitHub Setup

If you want to use the repository from GitHub, clone it first:

```bash
git clone https://github.com/chaudhary64/telegram-bulk-downloader
cd telegram-bulk-downloader
```

Then create your `.env` file, install dependencies, and run the script using the steps below.

## Setup

Create a virtual environment and install dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Windows (PowerShell)

```bash
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Configuration

Create a `.env` file in the project root.

You can copy `.env.example`:

```bash
cp .env.example .env
```

### `.env`

```env
TELETHON_API_ID=TELETHON_API_ID
TELETHON_API_HASH=TELETHON_API_HASH
TELETHON_CHANNEL_LINK=TELETHON_CHANNEL_LINK
```

Example:

```env
TELETHON_API_ID=12345678
TELETHON_API_HASH=abcd1234abcd1234abcd1234
TELETHON_CHANNEL_LINK=https://t.me/example_channel
```

## Run

```bash
python -u downlaod.py
```

### Windows (PowerShell)

```bash
python -u .\downlaod.py
```

The first run may ask you to sign in to Telegram. After that, the session is reused automatically.

## Output

Downloaded videos are saved in:

```text
telegram_videos/
```

## Project Structure

```text
telegram-bulk-downloader/
│
├── telegram_videos/
├── .env
├── .env.example
├── requirements.txt
├── downlaod.py
└── README.md
```

## Notes

- The script skips files that already exist locally
- `cryptg` improves Telegram decryption performance
- Works with public and private channels you joined
- Large channels may take time to index initially
- Using a VPN may improve Telegram CDN speed in some regions

## Install Optional Speed Boost

```bash
pip install cryptg
```

## Troubleshooting

### Slow download speed

Try:

- Using a VPN
- Increasing parallel downloads
- Using SSD storage
- Checking ISP throttling

### Telegram login issues

Delete the old session file and login again:

```bash
rm -f session.session
```

### Windows session reset

```bash
del session.session
```

## License

MIT License
