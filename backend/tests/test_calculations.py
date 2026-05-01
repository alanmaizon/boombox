"""
Calculation correctness tests — Income Tax + USC + PRSI.

Each scenario is tested against a worked example derived from Revenue.ie
published examples and the taxman knowledge base.

These tests are non-negotiable: every computation must match to ±€1
(rounding differences between hand calculations and code).
"""

from __future__ import annotations

from decimal import Decimal

import pytest

from backend.tools.tax_tools import compute_income_tax, compute_prsi, compute_usc


# ---------------------------------------------------------------------------
# Income Tax tests
# ---------------------------------------------------------------------------

class TestIncomeTax:
    """Tests against Finance Act 2025 / Budget 2026 bands."""

    def test_below_standard_rate_band(self) -> None:
        """€20,000 net profit — all at 20%."""
        result = compute_income_tax(Decimal("20000"), 2025)
        # gross tax: 20000 * 0.20 = 4000
        # credits: 1875 personal + 1875 earned income = 3750
        # net IT: 4000 - 3750 = 250
        assert result.gross_tax == Decimal("4000.00")
        assert result.total_credits == Decimal("3750.00")
        assert result.net_income_tax == Decimal("250.00")

    def test_above_standard_rate_band(self) -> None:
        """€60,000 net profit — straddling the 20%/40% boundary at €44,000."""
        result = compute_income_tax(Decimal("60000"), 2025)
        # 44000 * 0.20 = 8800
        # 16000 * 0.40 = 6400
        # gross tax = 15200
        # credits = 3750
        # net IT = 11450
        assert result.gross_tax == Decimal("15200.00")
        assert result.net_income_tax == Decimal("11450.00")

    def test_credits_cannot_make_tax_negative(self) -> None:
        """€5,000 net profit — credits exceed gross tax, so net IT = 0."""
        result = compute_income_tax(Decimal("5000"), 2025)
        assert result.net_income_tax == Decimal("0.00")

    def test_zero_income(self) -> None:
        """Zero income — gross tax 0, net IT 0."""
        result = compute_income_tax(Decimal("0"), 2025)
        assert result.gross_tax == Decimal("0.00")
        assert result.net_income_tax == Decimal("0.00")

    def test_sources_present(self) -> None:
        """Every band result must have a non-empty source."""
        result = compute_income_tax(Decimal("50000"), 2025)
        for band in result.bands:
            assert band.source, f"Band '{band.label}' missing source"


# ---------------------------------------------------------------------------
# USC tests
# ---------------------------------------------------------------------------

class TestUSC:
    """Tests against Finance Act 2025 USC bands."""

    def test_below_exemption_threshold(self) -> None:
        """€12,000 income — below €13,000 threshold, zero USC."""
        result = compute_usc(Decimal("12000"), 2025)
        assert result.total_usc == Decimal("0.00")

    def test_band_1_only(self) -> None:
        """€10,000 income — below Band 2 threshold (€12,012), all in Band 1."""
        # But first check it's above exemption (€13,000). 
        # 10,000 < 13,000 → exempt
        result = compute_usc(Decimal("10000"), 2025)
        assert result.total_usc == Decimal("0.00")

    def test_above_exemption_multi_band(self) -> None:
        """€30,000 income — crosses Bands 1, 2, and 3."""
        result = compute_usc(Decimal("30000"), 2025)
        # Band 1: 12012 * 0.005 = 60.06
        # Band 2: (25760 - 12012) * 0.02 = 13748 * 0.02 = 274.96
        # Band 3: (30000 - 25760) * 0.04 = 4240 * 0.04 = 169.60
        # Total: 504.62
        assert result.total_usc == Decimal("504.62")

    def test_high_income_band_4(self) -> None:
        """€80,000 income — reaches the 8% surcharge band above €70,044.
        
        Worked example:
          Band 1: 12012 * 0.005 = 60.06
          Band 2: 13748 * 0.02  = 274.96
          Band 3: 44284 * 0.04  = 1771.36
          Band 4: 9956  * 0.08  = 796.48
          Total: 2902.86
        """
        result = compute_usc(Decimal("80000"), 2025)
        assert result.total_usc == Decimal("2902.86")

    def test_sources_present(self) -> None:
        """Every band result must have a non-empty source."""
        result = compute_usc(Decimal("50000"), 2025)
        for band in result.bands:
            assert band.source, f"Band '{band.label}' missing source"


# ---------------------------------------------------------------------------
# PRSI tests
# ---------------------------------------------------------------------------

class TestPRSI:
    """Tests for Class S PRSI."""

    def test_standard_rate(self) -> None:
        """€40,000 income → 4% = €1,600."""
        result = compute_prsi(Decimal("40000"), 2025)
        assert result.total_prsi == Decimal("1600.00")

    def test_minimum_prsi(self) -> None:
        """€1,000 income → 4% = €40, but minimum is €500."""
        result = compute_prsi(Decimal("1000"), 2025)
        assert result.total_prsi == Decimal("500.00")

    def test_zero_income(self) -> None:
        """Zero income → zero PRSI (minimum only applies when income > 0)."""
        result = compute_prsi(Decimal("0"), 2025)
        assert result.total_prsi == Decimal("0.00")

    def test_source_present(self) -> None:
        """PRSI result must have a non-empty source."""
        result = compute_prsi(Decimal("30000"), 2025)
        assert result.source


# ---------------------------------------------------------------------------
# Full tax position integration test
# ---------------------------------------------------------------------------

class TestTaxPosition:
    """Integration test: gross income → net profit → IT + USC + PRSI."""

    def test_typical_avaso_year(self) -> None:
        """
        Typical AVASO contracting year:
        - Gross income: €42,000 (€200/day, ~210 billable days)
        - Allowable expenses: €3,000
        - Mileage deduction: €500
        - Net profit: €38,500
        """
        from backend.tools.tax_tools import compute_tax_position

        result = compute_tax_position(42000, 3000, 500, 2025)

        assert float(result["net_profit"]) == pytest.approx(38500.0, abs=1)
        assert float(result["total_liability"]) > 0
        assert "disclaimer" in result
        assert "tax advice" in result["disclaimer"].lower()

    def test_disclaimer_always_present(self) -> None:
        """Tax position result must always include the disclaimer."""
        from backend.tools.tax_tools import compute_tax_position

        result = compute_tax_position(20000, 0, 0, 2025)
        assert "disclaimer" in result
        assert len(result["disclaimer"]) > 10
