"""Utility functions for Slack Channel Downloader."""

from __future__ import annotations

import re
from datetime import datetime


def convert_date_to_ts(date_str: str | None) -> float | None:
    """Convert YYYY-MM-DD date string to Unix timestamp.

    Args:
        date_str: Date string in YYYY-MM-DD format, or None.

    Returns:
        Unix timestamp as float, or None if input is None.
    """
    if not date_str:
        return None
    dt = datetime.strptime(date_str, "%Y-%m-%d")
    return dt.timestamp()


def replace_mentions_with_names(text: str, user_map: dict[str, str]) -> str:
    """Replace user mentions in text with real names.

    Args:
        text: Message text containing mentions like <@USER_ID>.
        user_map: Mapping of user IDs to display names.

    Returns:
        Text with mentions replaced by @username format.
    """
    mentions = re.findall(r"<@([A-Z0-9]+)>", text)

    for user_id in mentions:
        if user_id in user_map:
            real_name = user_map[user_id]
            text = text.replace(f"<@{user_id}>", f"@{real_name}")

    return text


def format_timestamp(ts: str | None) -> str:
    """Convert Slack timestamp to readable datetime string.

    Args:
        ts: Slack message timestamp.

    Returns:
        Formatted datetime string or empty string if ts is None.
    """
    if not ts:
        return ""
    return datetime.fromtimestamp(float(ts)).strftime("%Y-%m-%d %H:%M:%S")
