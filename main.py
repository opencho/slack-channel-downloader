"""Slack Channel Downloader - Download messages and files from Slack channels."""

from datetime import datetime

from src.slack_downloader import Config, SlackClient, SlackApiException, FileDownloader
from src.slack_downloader.downloader import extract_files_from_messages
from src.slack_downloader.exporters import save_to_json, save_to_excel


def download_channel_content() -> None:
    """Download all messages and optionally files from a specific channel."""
    try:
        config = Config.from_env()
    except ValueError as e:
        print(f"Configuration error: {e}")
        return

    print("\n=== Slack Channel Content Downloader ===")
    print(f"Channel ID: {config.channel_id}")
    print(f"Download files: {'Yes' if config.download_files else 'No'}")
    if config.oldest_date:
        print(f"Date range: {config.oldest_date} to {config.newest_date or 'present'}")
    print("======================================\n")

    client = SlackClient(config.slack_bot_token)

    # Validate token
    print("Validating Slack token...")
    try:
        auth_info = client.validate_token()
        print(f"Authenticated as: {auth_info['user']} in workspace: {auth_info['team']}")
    except SlackApiException as e:
        print(f"Token validation failed: {e}")
        return

    # Get messages
    print(f"Fetching messages from channel {config.channel_id}...")

    def on_progress(count: int) -> None:
        print(f"Found {count} messages so far...")

    try:
        messages = client.get_channel_history(
            config.channel_id,
            oldest_date=config.oldest_date,
            newest_date=config.newest_date,
            on_progress=on_progress,
        )
    except SlackApiException as e:
        print(f"Failed to fetch messages: {e}")
        return

    if not messages:
        print("\nNo messages found in the channel.")
        return

    print(f"Total messages found: {len(messages)}")

    # Get user info for name resolution
    print("Fetching user information...")
    try:
        user_map = client.get_users()
        print(f"Found information for {len(user_map)} users")
    except SlackApiException as e:
        print(f"Warning: Could not fetch user info: {e}")
        user_map = {}

    # Save messages
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    json_filepath = config.messages_dir / f"channel_{config.channel_id}_{timestamp}.json"
    save_to_json(messages, json_filepath)
    print(f"Saved {len(messages)} messages to {json_filepath.name}")

    excel_filepath = config.messages_dir / f"channel_{config.channel_id}_{timestamp}.xlsx"
    save_to_excel(messages, excel_filepath, user_map)
    print(f"Saved {len(messages)} messages to {excel_filepath.name}")

    # Download files if enabled
    files_downloaded = []
    if config.download_files:
        files = extract_files_from_messages(messages, config.file_types or None)

        if files:
            print(f"\nDownloading {len(files)} files...")
            downloader = FileDownloader(config.slack_bot_token, config.download_dir)

            def on_download_progress(filename: str, index: int, total: int) -> None:
                print(f"[{index}/{total}] Downloading: {filename}")

            def on_download_error(filename: str, error: Exception) -> None:
                print(f"Failed to download {filename}: {error}")

            files_downloaded = downloader.download_files(
                files,
                on_progress=on_download_progress,
                on_error=on_download_error,
            )
            print(f"Downloaded {len(files_downloaded)} files")
        else:
            print("No files found in the messages.")

    # Summary
    print("\n=== Summary ===")
    print(f"Messages: {len(messages)} messages saved")
    print(f"JSON file: {json_filepath}")
    print(f"Excel file: {excel_filepath}")
    if config.download_files and files_downloaded:
        print(f"Files: {len(files_downloaded)} files downloaded to {config.download_dir}")
    print("===============\n")


if __name__ == "__main__":
    download_channel_content()
