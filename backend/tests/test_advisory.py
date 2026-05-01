"""
Advisory tests — what-if simulation grounded in the rules data.

Confirms:
  - every response carries citations (no claim without a source)
  - delta computation matches compute_tax_position semantics
  - VAT threshold crossing is flagged with a citation
  - disclaimer is always present and unmodified
  - mock mode returns canned response without DB / data dependency
"""

from __future__ import annotations

from decimal import Decimal

import pytest

from tools.advisory_tools import simulate_what_if
from tools.income_tools import persist_invoice


class TestAdvisorySimulation:
    def test_citations_always_present(self) -> None:
        result = simulate_what_if(
            tax_year=2025,
            question="What's my position?",
        )
        assert len(result["citations"]) >= 3
        # Core sources must be cited
        joined = " ".join(result["citations"])
        assert "revenue.ie" in joined.lower() or "citizensinformation" in joined.lower()

    def test_disclaimer_present(self) -> None:
        result = simulate_what_if(tax_year=2025, question="?")
        assert "NOT tax advice" in result["disclaimer"]
        assert "registered tax adviser" in result["disclaimer"]

    def test_no_deltas_baseline_only(self) -> None:
        result = simulate_what_if(tax_year=2025, question="Where am I now?")
        assert result["delta"]["total_liability"] == 0.0
        assert result["delta"]["net_profit"] == 0.0

    def test_additional_income_increases_liability(self) -> None:
        # Seed with €30k baseline
        persist_invoice(
            invoice_number="BASE-001",
            source="OTHER",
            client_name="Client",
            invoice_date="2025-01-15",
            gross_amount=30000.0,
            tax_year=2025,
        )
        result = simulate_what_if(
            tax_year=2025,
            question="What if I take an extra €5k?",
            additional_income=5000.0,
        )
        assert result["delta"]["total_liability"] > 0
        assert result["delta"]["net_profit"] == 5000.0
        # Net retention < delta profit (some tax paid)
        assert result["delta"]["net_retention"] < result["delta"]["net_profit"]

    def test_additional_expense_decreases_liability(self) -> None:
        persist_invoice(
            invoice_number="BASE-002",
            source="OTHER",
            client_name="Client",
            invoice_date="2025-01-15",
            gross_amount=50000.0,
            tax_year=2025,
        )
        result = simulate_what_if(
            tax_year=2025,
            question="What if I buy a €2k laptop?",
            additional_expense=2000.0,
        )
        # Adding expense reduces taxable profit, so liability should drop
        assert result["delta"]["total_liability"] < 0

    def test_vat_threshold_crossing_flagged(self) -> None:
        # Baseline below €40k, scenario crosses
        persist_invoice(
            invoice_number="BASE-003",
            source="OTHER",
            client_name="Client",
            invoice_date="2025-01-15",
            gross_amount=35000.0,
            tax_year=2025,
        )
        result = simulate_what_if(
            tax_year=2025,
            question="What if I take a €10k contract?",
            additional_income=10000.0,
        )
        caveats = " ".join(result["caveats"])
        assert "VAT" in caveats
        # Citation for the threshold must appear
        assert any("VAT" in c for c in result["citations"])

    def test_vat_threshold_not_flagged_when_below(self) -> None:
        result = simulate_what_if(
            tax_year=2025,
            question="Small extra income",
            additional_income=1000.0,
        )
        # No baseline income, scenario only €1k — well under €40k
        assert all("VAT" not in c for c in result["caveats"])

    def test_baseline_and_scenario_shape(self) -> None:
        result = simulate_what_if(tax_year=2025, question="?", additional_income=100.0)
        for key in ("baseline", "scenario", "delta"):
            assert key in result
        assert "total_liability" in result["baseline"]
        assert "net_profit" in result["scenario"]

    def test_mileage_delta_uses_civil_service_rates(self) -> None:
        # 100km extra round-trip at Band 1 €0.4390/km = €43.90 deductible
        result = simulate_what_if(
            tax_year=2025,
            question="What if I drive an extra 50km?",
            additional_mileage_km=50.0,
            mileage_round_trip=True,
            mileage_reimbursed=False,
        )
        # Scenario mileage deduction is at least the new amount
        assert result["scenario"]["ytd_mileage_deduction"] >= 43.0

    def test_mock_mode(self, monkeypatch) -> None:
        monkeypatch.setenv("BOOMBOX_MOCK", "true")
        import importlib
        import tools.advisory_tools as at
        importlib.reload(at)
        result = at.simulate_what_if(tax_year=2025, question="hi")
        assert result.get("mock") is True
        assert "NOT tax advice" in result["disclaimer"]
        assert len(result["citations"]) >= 3
        monkeypatch.setenv("BOOMBOX_MOCK", "false")
        importlib.reload(at)
