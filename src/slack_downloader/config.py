"""Configuration management for Slack Channel Downloader."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv


@dataclass
class Config:
    """Configuration for Slack Channel Downloader."""

    slack_bot_token: str
    channel_id: str
    download_dir: Path = field(default_factory=lambda: Path("./slack_files"))
    messages_dir: Path = field(default_factory=lambda: Path("./slack_messages"))
    download_files: bool = True
    file_types: list[str] = field(default_factory=list)
    oldest_date: str | None = None
    newest_date: str | None = None

    def __post_init__(self) -> None:
        """Validate configuration and create directories."""
        if not self.slack_bot_token:
            raise ValueError("SLACK_BOT_TOKEN is required")
        if not self.channel_id:
            raise ValueError("CHANNEL_ID is required")

        self.download_dir = Path(self.download_dir)
        self.messages_dir = Path(self.messages_dir)

        self.download_dir.mkdir(parents=True, exist_ok=True)
        self.messages_dir.mkdir(parents=True, exist_ok=True)

    @classmethod
    def from_env(cls, env_file: str | Path | None = None) -> Config:
        """Load configuration from environment variables.

        Args:
            env_file: Optional path to .env file. If None, uses default .env location.

        Returns:
            Config instance with values from environment.
        """
        if env_file:
            load_dotenv(env_file)
        else:
            load_dotenv()

        return cls(
            slack_bot_token=os.getenv("SLACK_BOT_TOKEN", ""),
            channel_id=os.getenv("CHANNEL_ID", ""),
            download_dir=Path(os.getenv("DOWNLOAD_DIR", "./slack_files")),
            messages_dir=Path(os.getenv("MESSAGES_DIR", "./slack_messages")),
            download_files=os.getenv("DOWNLOAD_FILES", "true").lower() == "true",
            file_types=_parse_file_types(os.getenv("FILE_TYPES", "")),
            oldest_date=os.getenv("OLDEST_DATE") or None,
            newest_date=os.getenv("NEWEST_DATE") or None,
        )


def _parse_file_types(value: str) -> list[str]:
    """Parse comma-separated file types string into list."""
    if not value:
        return []
    return [ft.strip() for ft in value.split(",") if ft.strip()]
