"""Slack API client wrapper."""

from __future__ import annotations

from typing import Any

from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

from .utils import convert_date_to_ts


class SlackApiException(Exception):
    """Custom exception for Slack API errors."""

    def __init__(self, message: str, error_code: str | None = None) -> None:
        super().__init__(message)
        self.error_code = error_code


class SlackClient:
    """Wrapper around Slack WebClient with convenience methods."""

    def __init__(self, token: str) -> None:
        """Initialize Slack client.

        Args:
            token: Slack Bot token with required scopes.
        """
        self._client = WebClient(token=token)
        self._token = token

    def validate_token(self) -> dict[str, Any]:
        """Validate the token and return auth info.

        Returns:
            Dictionary with user, team, user_id, team_id info.

        Raises:
            SlackApiException: If token validation fails.
        """
        try:
            response = self._client.auth_test()
            return {
                "user": response["user"],
                "team": response["team"],
                "user_id": response["user_id"],
                "team_id": response["team_id"],
            }
        except SlackApiError as e:
            raise SlackApiException(
                f"Token validation failed: {e.response['error']}",
                error_code=e.response["error"],
            ) from e

    def get_channel_info(self, channel_id: str) -> dict[str, Any]:
        """Get information about a channel.

        Args:
            channel_id: Slack channel ID.

        Returns:
            Dictionary with channel name and is_private flag.

        Raises:
            SlackApiException: If channel access fails.
        """
        try:
            result = self._client.conversations_info(channel=channel_id)
            return {
                "name": result["channel"]["name"],
                "is_private": result["channel"]["is_private"],
            }
        except SlackApiError as e:
            error = e.response["error"]
            if error == "missing_scope":
                raise SlackApiException(
                    "Token is missing required scope. Need channels:read or groups:read.",
                    error_code=error,
                ) from e
            elif error == "channel_not_found":
                raise SlackApiException(
                    f"Channel '{channel_id}' not found or bot doesn't have access.",
                    error_code=error,
                ) from e
            raise SlackApiException(f"Channel access failed: {error}", error_code=error) from e

    def get_channel_history(
        self,
        channel_id: str,
        oldest_date: str | None = None,
        newest_date: str | None = None,
        on_progress: callable | None = None,
    ) -> list[dict[str, Any]]:
        """Get all messages from a channel.

        Args:
            channel_id: Slack channel ID.
            oldest_date: Optional start date (YYYY-MM-DD).
            newest_date: Optional end date (YYYY-MM-DD).
            on_progress: Optional callback called with message count updates.

        Returns:
            List of message dictionaries.

        Raises:
            SlackApiException: If fetching messages fails.
        """
        try:
            all_messages: list[dict[str, Any]] = []
            cursor: str | None = None
            oldest_ts = convert_date_to_ts(oldest_date)
            newest_ts = convert_date_to_ts(newest_date)

            while True:
                params: dict[str, Any] = {
                    "channel": channel_id,
                    "limit": 1000,
                }

                if cursor:
                    params["cursor"] = cursor
                if oldest_ts:
                    params["oldest"] = oldest_ts
                if newest_ts:
                    params["latest"] = newest_ts

                result = self._client.conversations_history(**params)
                messages = result.get("messages", [])

                if not messages:
                    break

                all_messages.extend(messages)

                if on_progress:
                    on_progress(len(all_messages))

                if (
                    result.get("has_more")
                    and result.get("response_metadata")
                    and result["response_metadata"].get("next_cursor")
                ):
                    cursor = result["response_metadata"]["next_cursor"]
                else:
                    break

            return all_messages

        except SlackApiError as e:
            error = e.response["error"]
            if error == "missing_scope":
                raise SlackApiException(
                    "Token is missing required scope. Need channels:history or groups:history.",
                    error_code=error,
                ) from e
            elif error == "channel_not_found":
                raise SlackApiException(
                    f"Channel '{channel_id}' not found or bot doesn't have access.",
                    error_code=error,
                ) from e
            raise SlackApiException(f"Failed to fetch messages: {error}", error_code=error) from e

    def get_users(self) -> dict[str, str]:
        """Get mapping of user IDs to display names.

        Returns:
            Dictionary mapping user_id -> display_name.
        """
        try:
            user_map: dict[str, str] = {}
            cursor: str | None = None

            while True:
                params: dict[str, Any] = {}
                if cursor:
                    params["cursor"] = cursor

                result = self._client.users_list(**params)
                users = result.get("members", [])

                for user in users:
                    user_id = user.get("id")
                    real_name = (
                        user.get("real_name")
                        or user.get("profile", {}).get("real_name")
                        or user.get("profile", {}).get("display_name")
                        or user.get("name", user_id)
                    )
                    user_map[user_id] = real_name

                if result.get("response_metadata") and result["response_metadata"].get(
                    "next_cursor"
                ):
                    cursor = result["response_metadata"]["next_cursor"]
                else:
                    break

            return user_map

        except SlackApiError as e:
            raise SlackApiException(
                f"Failed to fetch users: {e.response['error']}",
                error_code=e.response["error"],
            ) from e
