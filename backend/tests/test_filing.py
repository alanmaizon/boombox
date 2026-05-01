"""
Filing tests — DRAFT Form 11 generation.

Confirms:
  - draft is generated deterministically from YTD ledger
  - line items map to the expected Form 11 panels
  - balance_due math is correct
  - DRAFT disclaimer is always present and unmodified
  - mock mode returns canned data without touching DB
"""

from __future__ import annotations

from decimal import Decimal

import pytest

from tools.filing_tools import draft_form_11
from tools.income_tools import persist_invoice
from tools.expense_tools import persist_expense
from tools.mileage_tools import persist_mileage_trip


def _seed_ledger(tax_year: int) -> None:
    """Seed enough records to exercise IT, USC, and PRSI bands."""
    persist_invoice(
        invoice_number="AVASO-2025-001",
        source="AVASO",
        client_name="AVASO Technology",
        invoice_date="2025-01-31",
        gross_amount=30000.0,
        tax_year=tax_year,
    )
    persist_expense(
        vendor="Eir",
        expense_date="2025-02-10",
        amount=1230.0,
        category="PHONE",
        description="Mobile + broadband (business %)",
        tax_year=tax_year,
        vat_amount=230.0,
    )
    persist_mileage_trip(
        trip_date="2025-03-01",
        origin="Enniskerry",
        destination="Rathdrum",
        distance_km=50.0,
        tax_year=tax_year,
        round_trip=True,
        reimbursed_by_client=False,
    )


class TestFilingDraft:
    def test_status_is_draft(self) -> None:
        _seed_ledger(2025)
        draft = draft_form_11(tax_year=2025)
        assert draft["status"] == "DRAFT"

    def test_disclaimer_present_and_strong(self) -> None:
        _seed_ledger(2025)
        draft = draft_form_11(tax_year=2025)
        assert "DRAFT ONLY" in draft["disclaimer"]
        assert "never submits to ROS" in draft["disclaimer"]
        assert "NOT been filed with Revenue" in draft["disclaimer"]

    def test_filing_deadline(self) -> None:
        _seed_ledger(2025)
        draft = draft_form_11(tax_year=2025)
        # Deadline string from data file is "October 31"
        assert "31" in draft["filing_deadline"]
        assert "October" in draft["filing_deadline"]

    def test_lines_cover_required_panels(self) -> None:
        _seed_ledger(2025)
        draft = draft_form_11(tax_year=2025)
        panels = {line["panel"] for line in draft["lines"]}
        assert any("Self-Employed Income" in p for p in panels)
        assert any("Personal Tax Credits" in p for p in panels)
        assert any("Calculation of liability" in p for p in panels)

    def test_every_line_has_source(self) -> None:
        _seed_ledger(2025)
        draft = draft_form_11(tax_year=2025)
        for line in draft["lines"]:
            assert line["source"], f"Missing source on line {line}"

    def test_balance_due_math(self) -> None:
        _seed_ledger(2025)
        prelim = 500.0
        draft = draft_form_11(tax_year=2025, preliminary_tax_paid=prelim)
        total = Decimal(str(draft["total_liability_estimate"]))
        balance = Decimal(str(draft["balance_due"]))
        prelim_paid = Decimal(str(draft["preliminary_tax_paid"]))
        assert balance == total - prelim_paid
        assert prelim_paid == Decimal(str(prelim))

    def test_empty_ledger_zero_liability(self) -> None:
        # No seed; all sums should be zero
        draft = draft_form_11(tax_year=2025)
        assert Decimal(str(draft["total_liability_estimate"])) == Decimal("0")
        assert Decimal(str(draft["balance_due"])) == Decimal("0")

    def test_profit_assessable_matches_net(self) -> None:
        _seed_ledger(2025)
        draft = draft_form_11(tax_year=2025)
        profit_lines = [
            line for line in draft["lines"]
            if line["field_ref"] == "220"
        ]
        assert len(profit_lines) == 1
        # Profit = 30000 income - 1000 net expense (1230-230 VAT) - mileage deduction
        # Mileage: 100km round trip at €0.4390/km = €43.90
        expected_profit = Decimal("30000") - Decimal("1000") - Decimal("43.90")
        assert Decimal(str(profit_lines[0]["value"])) == expected_profit

    def test_mock_mode(self, monkeypatch) -> None:
        monkeypatch.setenv("BOOMBOX_MOCK", "true")
        # Re-import to pick up new env
        import importlib
        import tools.filing_tools as ft
        importlib.reload(ft)
        draft = ft.draft_form_11(tax_year=2025)
        assert draft.get("mock") is True
        assert "DRAFT" in draft["status"]
        # Reset
        monkeypatch.setenv("BOOMBOX_MOCK", "false")
        importlib.reload(ft)
