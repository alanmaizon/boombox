"""
MCP mock fixture tests — verify MCP stubs work correctly in mock mode.
"""

from __future__ import annotations

import os

import pytest


@pytest.fixture(autouse=True)
def set_mock_mode(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("BOOMBOX_MOCK", "true")


class TestGmailMock:
    def test_list_messages_returns_mock(self) -> None:
        from mcp.mcp_clients import gmail_list_messages
        result = gmail_list_messages()
        assert len(result) > 0
        assert result[0]["mock"] is True

    def test_list_messages_has_expected_fields(self) -> None:
        from mcp.mcp_clients import gmail_list_messages
        result = gmail_list_messages()
        msg = result[0]
        assert "id" in msg
        assert "snippet" in msg
        assert "date" in msg


class TestDriveMock:
    def test_upload_returns_mock(self) -> None:
        from mcp.mcp_clients import drive_upload_file
        result = drive_upload_file(b"test content", "test.pdf")
        assert result["mock"] is True
        assert "id" in result
        assert "webViewLink" in result

    def test_get_file_returns_mock(self) -> None:
        from mcp.mcp_clients import drive_get_file
        result = drive_get_file("file_001")
        assert result["mock"] is True
        assert result["id"] == "file_001"


class TestSheetsMock:
    def test_append_rows_returns_mock(self) -> None:
        from mcp.mcp_clients import sheets_append_rows
        rows = [["Date", "Vendor", "Amount"], ["2025-01-10", "Eir", "49.99"]]
        result = sheets_append_rows("sheet_001", "Sheet1!A1", rows)
        assert result["mock"] is True
        assert result["updatedRows"] == 2


class TestCalendarMock:
    def test_create_event_returns_mock(self) -> None:
        from mcp.mcp_clients import calendar_create_event
        result = calendar_create_event(
            summary="Form 11 Deadline",
            date_str="2025-10-31",
            description="Annual self-assessment filing deadline",
        )
        assert result["mock"] is True
        assert "id" in result
        assert "htmlLink" in result
