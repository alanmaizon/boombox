"""
MCP client wrappers for Boombox.

Each wrapper is a thin adapter over the MCP server, stubbed in mock mode.
"""

from __future__ import annotations

import os
from typing import Any

_MOCK = os.getenv("BOOMBOX_MOCK", "false").lower() == "true"


def gmail_list_messages(query: str = "", max_results: int = 10) -> list[dict[str, Any]]:
    """
    List Gmail messages matching query.

    Args:
        query: Gmail search query (e.g. "from:avaso@example.com").
        max_results: Maximum number of results to return.

    Returns:
        List of message metadata dicts.
    """
    if _MOCK:
        return [
            {
                "id": "msg001",
                "snippet": "Invoice AVASO-2025-001 attached",
                "date": "2025-01-31",
                "from": "billing@avaso.com",
                "subject": "Invoice for January 2025",
                "mock": True,
            }
        ]
    raise NotImplementedError("Gmail MCP integration requires BOOMBOX_GMAIL_MCP_URL env var")


def drive_upload_file(file_content: bytes, filename: str, folder_id: str | None = None) -> dict[str, Any]:
    """
    Upload a file to Google Drive.

    Args:
        file_content: Raw file bytes.
        filename: Name for the uploaded file.
        folder_id: Optional Google Drive folder ID.

    Returns:
        A dict with ``id`` and ``webViewLink``.
    """
    if _MOCK:
        return {"id": "file_mock_001", "webViewLink": "https://drive.google.com/mock/001", "mock": True}
    raise NotImplementedError("Drive MCP integration requires BOOMBOX_DRIVE_MCP_URL env var")


def drive_get_file(file_id: str) -> dict[str, Any]:
    """
    Retrieve a file reference from Google Drive.

    Args:
        file_id: Google Drive file ID.

    Returns:
        A dict with ``id``, ``name``, and ``webViewLink``.
    """
    if _MOCK:
        return {"id": file_id, "name": "receipt_mock.pdf", "webViewLink": f"https://drive.google.com/mock/{file_id}", "mock": True}
    raise NotImplementedError("Drive MCP integration requires BOOMBOX_DRIVE_MCP_URL env var")


def sheets_append_rows(spreadsheet_id: str, range_: str, rows: list[list[Any]]) -> dict[str, Any]:
    """
    Append rows to a Google Sheet (expense ledger export).

    Args:
        spreadsheet_id: Google Sheets file ID.
        range_: A1 notation range (e.g. "Sheet1!A1").
        rows: List of row value lists.

    Returns:
        A dict with ``updatedRange`` and ``updatedRows``.
    """
    if _MOCK:
        return {"updatedRange": range_, "updatedRows": len(rows), "mock": True}
    raise NotImplementedError("Sheets MCP integration requires BOOMBOX_SHEETS_MCP_URL env var")


def calendar_create_event(
    summary: str,
    date_str: str,
    description: str = "",
    calendar_id: str = "primary",
) -> dict[str, Any]:
    """
    Create a Google Calendar event (e.g. tax filing deadline).

    Args:
        summary: Event title.
        date_str: ISO 8601 date string (YYYY-MM-DD).
        description: Optional event description.
        calendar_id: Target calendar (default "primary").

    Returns:
        A dict with ``id`` and ``htmlLink``.
    """
    if _MOCK:
        return {"id": "event_mock_001", "htmlLink": "https://calendar.google.com/mock/001", "mock": True}
    raise NotImplementedError("Calendar MCP integration requires BOOMBOX_CALENDAR_MCP_URL env var")
