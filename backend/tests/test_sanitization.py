"""
Sanitization tests — verify that sensitive data does not leak.

These tests mirror the Siamese pattern: structured-output safety checks.
"""

from __future__ import annotations

import os
import json
from decimal import Decimal
from unittest.mock import patch, MagicMock

import pytest

from tools.income_tools import persist_invoice
from tools.expense_tools import persist_expense
from tools.mileage_tools import persist_mileage_trip


class TestSanitization:
    """Verify that raw notes and sensitive content are not stored."""

    def test_invoice_notes_not_persisted(self) -> None:
        """Notes field should be stripped (set to None) before DB write."""
        with patch("tools.income_tools.persist_income_record") as mock_persist:
            mock_persist.return_value = 1
            persist_invoice(
                invoice_number="INV-001",
                source="AVASO",
                client_name="AVASO Technology",
                invoice_date="2025-01-31",
                gross_amount=7000.0,
                tax_year=2025,
                notes="Client contact: +353-1-XXXX XXXX bank ref: IE29AIBK93115212345678",
            )
            call_kwargs = mock_persist.call_args[0][0]
            assert call_kwargs["notes"] is None, "Notes must be stripped before DB write"

    def test_expense_notes_not_persisted(self) -> None:
        """Expense notes should be stripped before DB write."""
        with patch("tools.expense_tools.persist_expense_record") as mock_persist:
            mock_persist.return_value = 1
            persist_expense(
                vendor="Eir",
                expense_date="2025-01-10",
                amount=49.99,
                category="PHONE",
                description="Monthly broadband",
                tax_year=2025,
                notes="IBAN: IE29AIBK93115212345678",
            )
            call_kwargs = mock_persist.call_args[0][0]
            assert call_kwargs["notes"] is None, "Notes must be stripped before DB write"

    def test_mileage_notes_not_persisted(self) -> None:
        """Mileage notes should be stripped before DB write."""
        with patch("tools.mileage_tools.persist_mileage_record") as mock_persist:
            mock_persist.return_value = 1
            persist_mileage_trip(
                trip_date="2025-02-14",
                origin="Enniskerry",
                destination="Rathdrum",
                distance_km=65.0,
                tax_year=2025,
                reimbursed_by_client=True,
                notes="Client paid via bank transfer ref: 12345",
            )
            call_kwargs = mock_persist.call_args[0][0]
            assert call_kwargs["notes"] is None, "Notes must be stripped before DB write"


class TestStructuredOutput:
    """Verify that model outputs conform to expected schemas."""

    def test_income_tax_result_has_required_fields(self) -> None:
        """IncomeTaxResult must include all required fields."""
        from tools.tax_tools import compute_income_tax
        result = compute_income_tax(Decimal("30000"), 2025)
        assert hasattr(result, "gross_tax")
        assert hasattr(result, "net_income_tax")
        assert hasattr(result, "personal_credit")
        assert hasattr(result, "earned_income_credit")
        assert hasattr(result, "bands")
        assert hasattr(result, "source")

    def test_tax_position_disclaimer_not_softened(self) -> None:
        """The disclaimer must contain 'tax advice' — never soften it."""
        from tools.tax_tools import compute_tax_position
        result = compute_tax_position(40000, 2000, 0, 2025)
        disclaimer = result.get("disclaimer", "")
        assert "tax advice" in disclaimer.lower(), "Disclaimer must reference 'tax advice'"
        assert "registered tax adviser" in disclaimer.lower(), "Disclaimer must reference a registered adviser"

    def test_filing_draft_disclaimer_present(self) -> None:
        """FilingDraft disclaimer must be present and strong."""
        from models import FilingDraft, FilingStatus, Form11DraftLine
        from decimal import Decimal
        draft = FilingDraft(
            tax_year=2025,
            status=FilingStatus.DRAFT,
            lines=[
                Form11DraftLine(
                    panel="Panel B",
                    field_ref="207",
                    description="Case I/II profits",
                    value=Decimal("38500"),
                )
            ],
            total_liability_estimate=Decimal("8000"),
            balance_due=Decimal("8000"),
        )
        assert "DRAFT ONLY" in draft.disclaimer
        assert "NOT been filed" in draft.disclaimer

    def test_advisory_response_requires_citations(self) -> None:
        """AdvisoryResponse must have at least one citation."""
        from models import AdvisoryResponse
        resp = AdvisoryResponse(
            question="What is my net if I take a €5k contract?",
            answer="...",
            citations=["https://www.revenue.ie/en/..."],
        )
        assert len(resp.citations) >= 1
        assert "tax advice" in resp.disclaimer.lower()
