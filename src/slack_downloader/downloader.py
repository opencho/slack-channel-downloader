"""File download functionality for Slack Channel Downloader."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import requests


class DownloadError(Exception):
    """Exception raised when file download fails."""

    pass


class FileDownloader:
    """Downloads files from Slack with proper authentication."""

    CHUNK_SIZE = 8192

    def __init__(self, token: str, download_dir: Path) -> None:
        """Initialize file downloader.

        Args:
            token: Slack Bot token for authentication.
            download_dir: Directory to save downloaded files.
        """
        self._token = token
        self._download_dir = Path(download_dir)
        self._download_dir.mkdir(parents=True, exist_ok=True)

    def download_file(
        self,
        file_info: dict[str, Any],
        file_number: int | None = None,
    ) -> Path | None:
        """Download a single file from Slack.

        Args:
            file_info: File information dictionary from Slack API.
            file_number: Optional number prefix for filename.

        Returns:
            Path to downloaded file, or None if download failed.

        Raises:
            DownloadError: If download fails with an error.
        """
        url = file_info.get("url_private_download")
        if not url:
            raise DownloadError("No download URL found for file")

        filename = file_info.get("name")
        if not filename:
            raise DownloadError("No filename found for file")

        headers = {
            "Authorization": f"Bearer {self._token}",
            "User-Agent": "Mozilla/5.0",
        }

        # Use context manager to properly close the response
        with requests.get(url, headers=headers, stream=True) as response:
            if response.status_code != 200:
                raise DownloadError(
                    f"Failed to download {filename} - Status Code: {response.status_code}"
                )

            content_type = response.headers.get("content-type", "")
            if "text/html" in content_type.lower():
                raise DownloadError(
                    f"Failed to download {filename} - Got HTML login page instead of file"
                )

            if file_number is not None:
                prefix = str(file_number).zfill(4)
                filepath = self._download_dir / f"{prefix}-{filename}"
            else:
                filepath = self._download_dir / filename

            with open(filepath, "wb") as f:
                for chunk in response.iter_content(chunk_size=self.CHUNK_SIZE):
                    if chunk:
                        f.write(chunk)

        return filepath

    def download_files(
        self,
        files: list[dict[str, Any]],
        on_progress: callable | None = None,
        on_error: callable | None = None,
    ) -> list[Path]:
        """Download multiple files.

        Args:
            files: List of file info dictionaries.
            on_progress: Optional callback(filename, index, total) for progress.
            on_error: Optional callback(filename, error) for errors.

        Returns:
            List of successfully downloaded file paths.
        """
        downloaded: list[Path] = []
        total = len(files)

        for i, file_info in enumerate(files):
            filename = file_info.get("name", "unknown")

            if on_progress:
                on_progress(filename, i + 1, total)

            try:
                path = self.download_file(file_info, file_number=i)
                if path:
                    downloaded.append(path)
            except DownloadError as e:
                if on_error:
                    on_error(filename, e)

        return downloaded


def extract_files_from_messages(
    messages: list[dict[str, Any]],
    file_types: list[str] | None = None,
) -> list[dict[str, Any]]:
    """Extract file information from messages.

    Args:
        messages: List of Slack messages.
        file_types: Optional list of file types to filter (e.g., ['pdf', 'xlsx']).

    Returns:
        List of file info dictionaries.
    """
    all_files: list[dict[str, Any]] = []

    for message in messages:
        files = message.get("files", [])
        if files:
            all_files.extend(files)

    if file_types:
        all_files = [f for f in all_files if f.get("filetype") in file_types]

    return all_files
