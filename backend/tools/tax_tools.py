"""
Tax calculation tools — Income Tax, USC, PRSI.

Pure functions over the vendored irish_tax_rules.json data.
No rates are hardcoded here; all values come from the data file.

Source: Revenue.ie, Citizens Information, Finance Act 2025 / Budget 2026.
"""

from __future__ import annotations

import os
from decimal import Decimal, ROUND_HALF_UP
from typing import Any

from models import (
    IncomeTaxResult,
    PRSIResult,
    TaxBandResult,
    TaxPosition,
    USCResult,
)
from tools.tax_data import load_tax_rules

_MOCK = os.getenv("BOOMBOX_MOCK", "false").lower() == "true"


def _apply_bands(income: Decimal, bands: list[dict]) -> tuple[list[TaxBandResult], Decimal]:
    """Apply progressive tax bands to income. Returns (band results, total tax)."""
    results: list[TaxBandResult] = []
    total = Decimal("0")
    remaining = income

    for band in bands:
        lower = Decimal(str(band["lower"]))
        upper = Decimal(str(band["upper"])) if band["upper"] is not None else None
        rate = Decimal(str(band["rate"]))
        source = band.get("source", "")

        if remaining <= 0:
            break

        band_size = (upper - lower) if upper is not None else remaining
        in_band = min(remaining, band_size)
        tax_in_band = (in_band * rate).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        results.append(
            TaxBandResult(
                label=band["label"],
                taxable_in_band=in_band,
                rate=rate,
                tax=tax_in_band,
                source=source,
            )
        )
        total += tax_in_band
        remaining -= in_band

    return results, total


def compute_income_tax(net_profit: Decimal, tax_year: int) -> IncomeTaxResult:
    """
    Compute Income Tax liability for a sole trader with given net profit.

    Uses bands and credits from irish_tax_rules.json.
    Source: https://www.revenue.ie/en/personal-tax-credits-reliefs-and-exemptions/tax-relief-charts/index.aspx
    Statute: Taxes Consolidation Act 1997, Part 2

    Args:
        net_profit: Taxable profit (gross income minus allowable expenses).
        tax_year: Tax year for rate lookup.

    Returns:
        IncomeTaxResult with full breakdown.
    """
    rules = load_tax_rules(tax_year)
    bands_data = rules["income_tax"]["bands"]
    credits_data = rules["income_tax"]["credits"]

    band_results, gross_tax = _apply_bands(net_profit, bands_data)

    personal_credit = Decimal(str(credits_data["personal_credit"]["amount"]))
    earned_income_credit = Decimal(str(credits_data["earned_income_credit"]["amount"]))
    total_credits = personal_credit + earned_income_credit

    net_it = max(Decimal("0"), gross_tax - total_credits)

    return IncomeTaxResult(
        gross_income=net_profit,
        allowable_expenses=Decimal("0"),
        net_profit=net_profit,
        bands=band_results,
        gross_tax=gross_tax,
        personal_credit=personal_credit,
        earned_income_credit=earned_income_credit,
        total_credits=total_credits,
        net_income_tax=net_it,
        source=rules["income_tax"]["source"],
    )


def compute_usc(income: Decimal, tax_year: int) -> USCResult:
    """
    Compute USC liability.

    Exemption threshold: €13,000 (zero USC if income ≤ threshold).
    Source: https://www.revenue.ie/en/jobs-and-pensions/usc/index.aspx
    Statute: Finance (No. 2) Act 2008, Part 18D

    Args:
        income: Reckonable income (gross — USC is on gross, before IT deductions).
        tax_year: Tax year for rate lookup.

    Returns:
        USCResult with full breakdown.
    """
    rules = load_tax_rules(tax_year)
    usc_data = rules["usc"]
    threshold = Decimal(str(usc_data["exemption_threshold"]))

    if income <= threshold:
        return USCResult(
            reckonable_income=income,
            bands=[],
            total_usc=Decimal("0"),
            source=usc_data["source"],
        )

    band_results, total = _apply_bands(income, usc_data["bands"])
    return USCResult(
        reckonable_income=income,
        bands=band_results,
        total_usc=total,
        source=usc_data["source"],
    )


def compute_prsi(income: Decimal, tax_year: int) -> PRSIResult:
    """
    Compute Class S PRSI for self-employed individuals.

    Rate: 4% on all reckonable income (minimum €500/year).
    Source: https://www.citizensinformation.ie/en/social-welfare/irish-social-welfare-system/social-insurance-prsi/class-s-prsi/
    Statute: Social Welfare Consolidation Act 2005, Part 2

    Args:
        income: Reckonable income.
        tax_year: Tax year for rate lookup.

    Returns:
        PRSIResult with breakdown.
    """
    rules = load_tax_rules(tax_year)
    prsi_data = rules["prsi"]["class_s"]
    rate = Decimal(str(prsi_data["rate"]))
    minimum = Decimal(str(prsi_data["minimum_annual"]))

    raw = (income * rate).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    total_prsi = max(raw, minimum) if income > 0 else Decimal("0")

    return PRSIResult(
        reckonable_income=income,
        rate=rate,
        total_prsi=total_prsi,
        source=prsi_data["source"],
    )


def compute_tax_position(
    gross_income: float,
    allowable_expenses: float,
    mileage_deduction: float,
    tax_year: int,
) -> dict[str, Any]:
    """
    Compute the full YTD tax position for a sole trader.

    Steps:
      1. Net profit = gross_income − allowable_expenses − mileage_deduction
      2. Income Tax on net profit (with personal + earned income credits)
      3. USC on gross income (USC is on gross, not net profit)
      4. Class S PRSI on net profit
      5. Total liability = IT + USC + PRSI

    All rates sourced from irish_tax_rules.json.

    Args:
        gross_income: Total YTD gross income (EUR).
        allowable_expenses: Total YTD allowable expenses (EUR).
        mileage_deduction: Total YTD owner-deductible mileage (EUR).
        tax_year: Tax year.

    Returns:
        A dict representation of TaxPosition.
    """
    if _MOCK:
        return {
            "tax_year": tax_year,
            "ytd_income": gross_income,
            "ytd_expenses": allowable_expenses,
            "ytd_mileage_deduction": mileage_deduction,
            "net_profit": gross_income - allowable_expenses - mileage_deduction,
            "total_liability": 4200.00,
            "disclaimer": (
                "⚠️  This is an educational estimate only and does NOT constitute tax advice. "
                "Figures are indicative and based on vendored rate data. "
                "Always consult a registered tax adviser (AITI/CTA) for your personal circumstances."
            ),
            "mock": True,
        }

    gi = Decimal(str(gross_income))
    ae = Decimal(str(allowable_expenses))
    md = Decimal(str(mileage_deduction))
    net_profit = gi - ae - md

    it_result = compute_income_tax(net_profit, tax_year)
    usc_result = compute_usc(gi, tax_year)
    prsi_result = compute_prsi(net_profit, tax_year)

    total = it_result.net_income_tax + usc_result.total_usc + prsi_result.total_prsi

    position = TaxPosition(
        tax_year=tax_year,
        ytd_income=gi,
        ytd_expenses=ae,
        ytd_mileage_deduction=md,
        net_profit=net_profit,
        income_tax=it_result,
        usc=usc_result,
        prsi=prsi_result,
        total_liability=total,
    )
    return position.model_dump(mode="json")
