"""
Mileage computation tests.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

from backend.tools.mileage_tools import compute_mileage


class TestMileageComputation:
    """Test mileage computations against irish_tax_rules.json data."""

    def test_avaso_reimbursed_trip(self) -> None:
        """Round trip ≥ 40 km, reimbursed by AVASO at €0.44/km."""
        result = compute_mileage(
            distance_km=65.0,
            round_trip=True,
            reimbursed_by_client=True,
            tax_year=2025,
        )
        # 65 * 2 = 130 km round trip, 130 * 0.44 = 57.20
        assert result["round_trip_km"] == pytest.approx(130.0)
        assert result["reimbursed_amount"] == pytest.approx(57.20, abs=0.01)
        assert result["deductible_amount"] == pytest.approx(0.0)

    def test_avaso_trip_below_minimum_not_reimbursed(self) -> None:
        """Round trip < 40 km — NOT reimbursed by AVASO."""
        result = compute_mileage(
            distance_km=15.0,
            round_trip=True,
            reimbursed_by_client=True,
            tax_year=2025,
        )
        # 15 * 2 = 30 km < 40 km minimum → no reimbursement
        assert result["reimbursed_amount"] == pytest.approx(0.0)

    def test_owner_deductible_trip(self) -> None:
        """Non-reimbursed business trip — owner-deductible at civil service rates."""
        result = compute_mileage(
            distance_km=50.0,
            round_trip=True,
            reimbursed_by_client=False,
            tax_year=2025,
        )
        assert result["deductible_amount"] > 0
        assert result["reimbursed_amount"] == pytest.approx(0.0)

    def test_enniskerry_to_rathdrum(self) -> None:
        """
        Demo scenario: Enniskerry → Rathdrum (approx 65 km one-way = 130 km round trip).
        AVASO-reimbursed: 130 * 0.44 = 57.20.
        """
        result = compute_mileage(
            distance_km=65.0,
            round_trip=True,
            reimbursed_by_client=True,
            tax_year=2025,
        )
        assert result["reimbursed_amount"] == pytest.approx(57.20, abs=0.01)
        assert "source" in result

    def test_source_always_present(self) -> None:
        """Result must include source URL."""
        result = compute_mileage(50.0, True, False, 2025)
        assert result["source"]
