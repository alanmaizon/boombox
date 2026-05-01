"""
Tax data loader tests — verify the irish_tax_rules.json is valid and complete.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from backend.tools.tax_data import load_tax_rules


class TestTaxDataLoader:
    def test_loads_successfully(self) -> None:
        rules = load_tax_rules(2025)
        assert rules is not None

    def test_tax_year_field(self) -> None:
        rules = load_tax_rules(2025)
        assert rules["tax_year"] == 2025

    def test_income_tax_bands_present(self) -> None:
        rules = load_tax_rules(2025)
        bands = rules["income_tax"]["bands"]
        assert len(bands) >= 2
        for band in bands:
            assert "rate" in band
            assert "lower" in band
            assert "source" in band

    def test_usc_bands_present(self) -> None:
        rules = load_tax_rules(2025)
        bands = rules["usc"]["bands"]
        assert len(bands) >= 4

    def test_prsi_rate_present(self) -> None:
        rules = load_tax_rules(2025)
        assert rules["prsi"]["class_s"]["rate"] == pytest.approx(0.04)

    def test_mileage_avaso_rate(self) -> None:
        rules = load_tax_rules(2025)
        assert rules["mileage"]["avaso_rate_per_km"] == pytest.approx(0.44)

    def test_vat_thresholds_present(self) -> None:
        rules = load_tax_rules(2025)
        assert rules["vat"]["thresholds"]["services"]["amount"] == 40000

    def test_every_entry_has_source(self) -> None:
        """Key entries must have source fields."""
        rules = load_tax_rules(2025)
        assert rules["income_tax"].get("source")
        assert rules["usc"].get("source")
        assert rules["prsi"]["class_s"].get("source")
        assert rules["mileage"].get("source")

    def test_missing_file_raises_file_not_found(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """Loading a non-existent year should raise FileNotFoundError."""
        from backend.tools import tax_data as td
        monkeypatch.setattr(td, "_DATA_DIR", tmp_path)
        td.load_tax_rules.cache_clear()
        with pytest.raises(FileNotFoundError):
            td.load_tax_rules(9999)
        td.load_tax_rules.cache_clear()
