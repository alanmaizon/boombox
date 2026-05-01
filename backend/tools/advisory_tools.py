"""
Advisory tools — what-if scenario simulation.

Every numeric claim is grounded in compute_tax_position over the vendored
irish_tax_rules.json. Citations are pulled from the same data file: no claim
is returned without a corresponding source URL or statute reference.

The Advisory chat UI calls this tool with structured deltas (additional
income, additional expense, additional mileage km) plus a free-text
question. The simulator computes baseline and scenario tax positions, then
returns the difference along with citations and any threshold flags
(e.g., crossing the €40,000 services VAT registration threshold).

No LLM is involved in computing rates or liabilities — the LLM-driven
chat layer (when wired through ADK Runner) calls this tool to ground its
answers.
"""

from __future__ import annotations

import os
from decimal import Decimal
from typing import Any

from storage import (
    get_ytd_allowable_expenses,
    get_ytd_income,
    get_ytd_mileage_deduction,
)
from tools.mileage_tools import compute_mileage
from tools.tax_data import load_tax_rules
from tools.tax_tools import compute_tax_position

_MOCK = os.getenv("BOOMBOX_MOCK", "false").lower() == "true"


def _vat_threshold_check(
    rules: dict, baseline_income: Decimal, scenario_income: Decimal
) -> tuple[list[str], list[str]]:
    """Check whether the scenario crosses the services VAT registration threshold."""
    caveats: list[str] = []
    citations: list[str] = []
    services_threshold = Decimal(str(rules["vat"]["thresholds"]["services"]["amount"]))
    services_source = rules["vat"]["thresholds"]["services"]["source"]

    if baseline_income < services_threshold <= scenario_income:
        caveats.append(
            f"This scenario crosses the €{services_threshold:,.0f} services VAT "
            "registration threshold. You would be required to register for VAT and "
            "begin charging VAT on services."
        )
        citations.append(f"Services VAT threshold: {services_source}")
    elif scenario_income > services_threshold and baseline_income > services_threshold:
        caveats.append(
            f"Both baseline and scenario income exceed the €{services_threshold:,.0f} "
            "services VAT threshold. VAT registration applies."
        )
        citations.append(f"Services VAT threshold: {services_source}")

    return caveats, citations


def _baseline_citations(rules: dict) -> list[str]:
    """Standard citations attached to every advisory answer."""
    return [
        f"Income Tax bands: {rules['income_tax']['source']}",
        f"USC bands: {rules['usc']['source']}",
        f"Class S PRSI: {rules['prsi']['class_s']['source']}",
        f"Mileage rates: {rules['mileage']['source']}",
    ]


def simulate_what_if(
    tax_year: int,
    question: str,
    additional_income: float = 0.0,
    additional_expense: float = 0.0,
    additional_mileage_km: float = 0.0,
    mileage_round_trip: bool = True,
    mileage_reimbursed: bool = False,
) -> dict[str, Any]:
    """
    Simulate a what-if scenario against current YTD position.

    Computes baseline (current YTD) and scenario (with deltas) tax positions
    using compute_tax_position, then returns:
      - the delta in net liability
      - the answer text constructed from the figures
      - citations from irish_tax_rules.json
      - caveats (e.g., VAT threshold crossing)

    All numeric facts trace to the vendored data file. No LLM is used for
    rate or liability computation.

    Args:
        tax_year: Tax year for rate lookup and YTD baseline.
        question: User's natural-language what-if question (echoed back).
        additional_income: Hypothetical extra gross income (EUR).
        additional_expense: Hypothetical extra allowable expenses (EUR).
        additional_mileage_km: Hypothetical extra one-way distance (km).
        mileage_round_trip: Treat the extra mileage as a round trip.
        mileage_reimbursed: Whether the trip is AVASO-reimbursed (≥40km RT).

    Returns:
        AdvisoryResponse-shaped dict with question, answer, citations,
        caveats, scenario figures, and disclaimer.
    """
    if _MOCK:
        return {
            "question": question,
            "answer": (
                "Based on Finance Act 2025 / Budget 2026 rates, adding €2,000 to "
                "your gross income would increase your total liability by approximately "
                "€1,030 (Income Tax €800 at 40%, USC €80 at 4%, Class S PRSI €80 at 4%). "
                "Your net retention on the extra €2,000 is approximately €1,170."
            ),
            "citations": [
                "Income Tax bands: https://www.revenue.ie/en/personal-tax-credits-reliefs-and-exemptions/tax-relief-charts/index.aspx",
                "USC bands: https://www.revenue.ie/en/jobs-and-pensions/usc/index.aspx",
                "Class S PRSI: https://www.citizensinformation.ie/en/social-welfare/irish-social-welfare-system/social-insurance-prsi/class-s-prsi/",
                "Mileage rates: https://www.revenue.ie/en/personal-tax-credits-reliefs-and-exemptions/travel/motor-travel-rates/index.aspx",
            ],
            "caveats": [],
            "baseline": {"total_liability": 4200.00, "net_profit": 22000.00},
            "scenario": {"total_liability": 5230.00, "net_profit": 24000.00},
            "delta": {"total_liability": 1030.00, "net_profit": 2000.00},
            "disclaimer": (
                "⚠️  This is NOT tax advice. It is an educational simulation based on "
                "published Irish tax rules (Finance Act 2025 / Budget 2026). Consult a "
                "registered tax adviser (AITI/CTA) for advice specific to your situation. "
                "Boombox never files anything with Revenue on your behalf."
            ),
            "mock": True,
        }

    rules = load_tax_rules(tax_year)

    baseline_income = get_ytd_income(tax_year)
    baseline_expenses = get_ytd_allowable_expenses(tax_year)
    baseline_mileage = get_ytd_mileage_deduction(tax_year)

    baseline = compute_tax_position(
        gross_income=float(baseline_income),
        allowable_expenses=float(baseline_expenses),
        mileage_deduction=float(baseline_mileage),
        tax_year=tax_year,
    )

    extra_mileage_deduction = Decimal("0")
    if additional_mileage_km > 0:
        mileage = compute_mileage(
            distance_km=additional_mileage_km,
            round_trip=mileage_round_trip,
            reimbursed_by_client=mileage_reimbursed,
            tax_year=tax_year,
        )
        extra_mileage_deduction = Decimal(str(mileage["deductible_amount"]))

    scenario_income = baseline_income + Decimal(str(additional_income))
    scenario_expenses = baseline_expenses + Decimal(str(additional_expense))
    scenario_mileage = baseline_mileage + extra_mileage_deduction

    scenario = compute_tax_position(
        gross_income=float(scenario_income),
        allowable_expenses=float(scenario_expenses),
        mileage_deduction=float(scenario_mileage),
        tax_year=tax_year,
    )

    baseline_liability = Decimal(str(baseline["total_liability"]))
    scenario_liability = Decimal(str(scenario["total_liability"]))
    delta_liability = scenario_liability - baseline_liability

    baseline_profit = Decimal(str(baseline["net_profit"]))
    scenario_profit = Decimal(str(scenario["net_profit"]))
    delta_profit = scenario_profit - baseline_profit
    net_retention = delta_profit - delta_liability

    citations = _baseline_citations(rules)
    vat_caveats, vat_citations = _vat_threshold_check(
        rules, baseline_income, scenario_income
    )
    citations.extend(vat_citations)

    parts: list[str] = []
    if additional_income > 0 or additional_expense > 0 or additional_mileage_km > 0:
        parts.append(
            f"Baseline YTD position (tax year {tax_year}): net profit "
            f"€{baseline_profit:,.2f}, total liability €{baseline_liability:,.2f}."
        )
        parts.append(
            f"Scenario position with applied deltas: net profit "
            f"€{scenario_profit:,.2f}, total liability €{scenario_liability:,.2f}."
        )
        if delta_liability >= 0:
            parts.append(
                f"Liability increases by €{delta_liability:,.2f}; net retention on "
                f"€{delta_profit:,.2f} additional profit is €{net_retention:,.2f}."
            )
        else:
            parts.append(
                f"Liability decreases by €{abs(delta_liability):,.2f} relative to "
                "baseline."
            )
    else:
        parts.append(
            f"No deltas supplied. Current baseline: net profit "
            f"€{baseline_profit:,.2f}, total liability €{baseline_liability:,.2f} "
            f"for tax year {tax_year}."
        )

    answer = " ".join(parts)

    return {
        "question": question,
        "answer": answer,
        "citations": citations,
        "caveats": vat_caveats,
        "baseline": {
            "total_liability": float(baseline_liability),
            "net_profit": float(baseline_profit),
            "ytd_income": float(baseline_income),
            "ytd_expenses": float(baseline_expenses),
            "ytd_mileage_deduction": float(baseline_mileage),
        },
        "scenario": {
            "total_liability": float(scenario_liability),
            "net_profit": float(scenario_profit),
            "ytd_income": float(scenario_income),
            "ytd_expenses": float(scenario_expenses),
            "ytd_mileage_deduction": float(scenario_mileage),
        },
        "delta": {
            "total_liability": float(delta_liability),
            "net_profit": float(delta_profit),
            "net_retention": float(net_retention),
        },
        "disclaimer": (
            "⚠️  This is NOT tax advice. It is an educational simulation based on "
            "published Irish tax rules. Consult a registered tax adviser (AITI/CTA) "
            "for advice specific to your situation. Boombox never files anything with "
            "Revenue on your behalf."
        ),
    }
