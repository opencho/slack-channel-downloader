"""Export functionality for saving messages to different formats."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd

from .utils import format_timestamp, replace_mentions_with_names


def save_to_json(
    messages: list[dict[str, Any]],
    filepath: Path,
) -> Path:
    """Save messages to a JSON file.

    Args:
        messages: List of Slack messages.
        filepath: Path to save the JSON file.

    Returns:
        Path to the saved file.
    """
    filepath = Path(filepath)
    filepath.parent.mkdir(parents=True, exist_ok=True)

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(messages, f, ensure_ascii=False, indent=2)

    return filepath


def save_to_excel(
    messages: list[dict[str, Any]],
    filepath: Path,
    user_map: dict[str, str] | None = None,
) -> Path:
    """Save messages to an Excel file.

    Args:
        messages: List of Slack messages.
        filepath: Path to save the Excel file.
        user_map: Optional mapping of user IDs to display names.

    Returns:
        Path to the saved file.
    """
    filepath = Path(filepath)
    filepath.parent.mkdir(parents=True, exist_ok=True)

    user_map = user_map or {}

    excel_data: list[dict[str, str]] = []
    for msg in messages:
        user_id = msg.get("user")
        user_name = user_map.get(user_id, user_id) if user_id else "SYSTEM"

        text = msg.get("text", "")
        if user_map:
            text = replace_mentions_with_names(text, user_map)

        date = format_timestamp(msg.get("ts"))

        excel_data.append({
            "user_name": user_name,
            "text": text,
            "date": date,
        })

    df = pd.DataFrame(excel_data)
    df.to_excel(filepath, index=False)

    return filepath
