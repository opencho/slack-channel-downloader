# Slack Channel Downloader

Download messages and files from Slack channels to JSON, Excel, and local files.

## Requirements

- Python 3.11+
- [uv](https://docs.astral.sh/uv/) (recommended) or pip

## Installation

```bash
# Clone the repository
git clone <repository-url>
cd slack-channel-downloader

# Install dependencies with uv
uv sync
```

## Configuration

1. Copy the sample environment file:
   ```bash
   cp .env.sample .env
   ```

2. Edit `.env` with your Slack credentials:
   ```
   SLACK_BOT_TOKEN=xoxb-your-bot-token
   CHANNEL_ID=your-channel-id(begins with C)
   ```

### Required Slack Bot Scopes

Your Slack Bot token needs the following OAuth scopes:

| Scope | Purpose |
|-------|---------|
| `channels:history` | Read messages from public channels |
| `channels:read` | Access public channel info |
| `groups:history` | Read messages from private channels |
| `groups:read` | Access private channel info |
| `files:read` | Download files |
| `users:read` | Resolve user IDs to names |

### Optional Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DOWNLOAD_DIR` | `./slack_files` | Directory for downloaded files |
| `MESSAGES_DIR` | `./slack_messages` | Directory for message exports |
| `DOWNLOAD_FILES` | `true` | Set to `false` to skip file downloads |
| `FILE_TYPES` | (all) | Comma-separated file types (e.g., `pdf,xlsx`) |
| `OLDEST_DATE` | (none) | Start date filter (YYYY-MM-DD) |
| `NEWEST_DATE` | (none) | End date filter (YYYY-MM-DD) |

## Usage

```bash
uv run python main.py
```

### Output

- `slack_messages/channel_<ID>_<timestamp>.json` - Raw message data
- `slack_messages/channel_<ID>_<timestamp>.xlsx` - Excel with user_name, text, date columns
- `slack_files/` - Downloaded files (numbered for ordering)

## Project Structure

```
slack-channel-downloader/
├── src/slack_downloader/
│   ├── __init__.py      # Package exports
│   ├── config.py        # Configuration management
│   ├── client.py        # Slack API client wrapper
│   ├── downloader.py    # File download logic
│   ├── exporters.py     # JSON/Excel export
│   └── utils.py         # Helper functions
├── main.py              # Entry point
├── pyproject.toml       # Project configuration
└── .env                 # Your credentials (not committed)
```

## License

MIT
