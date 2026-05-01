"""
Filing tools — produce a DRAFT Form 11 for review.

DRAFT ONLY. Boombox never submits to ROS. The Filing tool maps the
Calculator Agent's TaxPosition figures to Form 11 panel/field references
deterministically — no LLM is involved in the line mapping, eliminating
hallucination risk on field numbers.

Field references below are based on the published Form 11 layout
(self-assessment income tax return). They are *indicative* — Revenue may
adjust panel/field numbering between tax years, so the disclaimer instructs
the user to verify against the current Form 11 before filing.

Source: https://www.revenue.ie/en/self-assessment-and-self-employment/filing-your-tax-return/index.aspx
Statute: TCA 1997 Part 41A (self-assessment).
"""

from __future__ import annotations

import os
from decimal import Decimal
from typing import Any

from models import FilingDraft, FilingStatus, Form11DraftLine
from storage import (
    get_ytd_allowable_expenses,
    get_ytd_income,
    get_ytd_mileage_deduction,
)
from tools.tax_data import load_tax_rules
from tools.tax_tools import compute_tax_position

_MOCK = os.getenv("BOOMBOX_MOCK", "false").lower() == "true"


def _build_lines(position: dict[str, Any]) -> list[Form11DraftLine]:
    """Map a TaxPosition dict to indicative Form 11 line items."""
    income_tax = position["income_tax"]
    usc = position["usc"]
    prsi = position["prsi"]

    return [
        Form11DraftLine(
            panel="Panel B — Self-Employed Income",
            field_ref="207(a)",
            description="Gross income from trade / profession",
            value=Decimal(str(position["ytd_income"])),
            source="https://www.revenue.ie/en/self-assessment-and-self-employment/filing-your-tax-return/index.aspx",
        ),
        Form11DraftLine(
            panel="Panel B — Self-Employed Income",
            field_ref="207(b)",
            description="Allowable expenses",
            value=Decimal(str(position["ytd_expenses"])),
            source="https://www.revenue.ie/en/self-assessment-and-self-employment/expenses/index.aspx",
        ),
        Form11DraftLine(
            panel="Panel B — Self-Employed Income",
            field_ref="207(c)",
            description="Owner-deductible mileage (non-reimbursed)",
            value=Decimal(str(position["ytd_mileage_deduction"])),
            source="https://www.revenue.ie/en/personal-tax-credits-reliefs-and-exemptions/travel/motor-travel-rates/index.aspx",
        ),
        Form11DraftLine(
            panel="Panel B — Self-Employed Income",
            field_ref="220",
            description="Profit assessable (Case I/II)",
            value=Decimal(str(position["net_profit"])),
            source="https://www.revenue.ie/en/self-assessment-and-self-employment/filing-your-tax-return/index.aspx",
        ),
        Form11DraftLine(
            panel="Panel L — Personal Tax Credits",
            field_ref="422",
            description="Personal Tax Credit (single)",
            value=Decimal(str(income_tax["personal_credit"])),
            source="https://www.revenue.ie/en/personal-tax-credits-reliefs-and-exemptions/tax-relief-charts/index.aspx",
        ),
        Form11DraftLine(
            panel="Panel L — Personal Tax Credits",
            field_ref="472",
            description="Earned Income Credit",
            value=Decimal(str(income_tax["earned_income_credit"])),
            source="https://www.revenue.ie/en/personal-tax-credits-reliefs-and-exemptions/earned-income-tax-credit/index.aspx",
        ),
        Form11DraftLine(
            panel="Panel N — Calculation of liability",
            field_ref="IT",
            description="Net Income Tax",
            value=Decimal(str(income_tax["net_income_tax"])),
            source=income_tax["source"],
        ),
        Form11DraftLine(
            panel="Panel N — Calculation of liability",
            field_ref="USC",
            description="Universal Social Charge",
            value=Decimal(str(usc["total_usc"])),
            source=usc["source"],
        ),
        Form11DraftLine(
            panel="Panel N — Calculation of liability",
            field_ref="PRSI",
            description="Class S PRSI (self-employed)",
            value=Decimal(str(prsi["total_prsi"])),
            source=prsi["source"],
        ),
    ]


def draft_form_11(
    tax_year: int,
    preliminary_tax_paid: float = 0.0,
) -> dict[str, Any]:
    """
    Produce a DRAFT Form 11 for the given tax year from the YTD ledger.

    Steps:
      1. Pull YTD income, allowable expenses, and owner-deductible mileage
         from storage.
      2. Run compute_tax_position to get IT + USC + PRSI.
      3. Map each figure to its Form 11 panel/field reference.

    No LLM is involved in the mapping — line items are deterministic.

    Args:
        tax_year: Tax year to draft for.
        preliminary_tax_paid: Preliminary tax already paid for the year (EUR).

    Returns:
        FilingDraft as a dict, including status="DRAFT", lines, totals,
        balance_due, the 31 October deadline, and the no-filing disclaimer.
    """
    if _MOCK:
        rules = {"deadlines": {"form11_filing": {"date": "October 31"}}}
        return {
            "tax_year": tax_year,
            "status": "DRAFT",
            "lines": [
                {
                    "panel": "Panel B — Self-Employed Income",
                    "field_ref": "220",
                    "description": "Profit assessable (Case I/II)",
                    "value": 24800.00,
                    "source": "https://www.revenue.ie/en/self-assessment-and-self-employment/filing-your-tax-return/index.aspx",
                },
                {
                    "panel": "Panel N — Calculation of liability",
                    "field_ref": "IT",
                    "description": "Net Income Tax",
                    "value": 1210.00,
                    "source": "https://www.revenue.ie/en/personal-tax-credits-reliefs-and-exemptions/tax-relief-charts/index.aspx",
                },
                {
                    "panel": "Panel N — Calculation of liability",
                    "field_ref": "USC",
                    "description": "Universal Social Charge",
                    "value": 720.00,
                    "source": "https://www.revenue.ie/en/jobs-and-pensions/usc/index.aspx",
                },
                {
                    "panel": "Panel N — Calculation of liability",
                    "field_ref": "PRSI",
                    "description": "Class S PRSI (self-employed)",
                    "value": 992.00,
                    "source": "https://www.citizensinformation.ie/en/social-welfare/irish-social-welfare-system/social-insurance-prsi/class-s-prsi/",
                },
            ],
            "total_liability_estimate": 2922.00,
            "preliminary_tax_paid": preliminary_tax_paid,
            "balance_due": 2922.00 - preliminary_tax_paid,
            "filing_deadline": "31 October",
            "disclaimer": (
                "⚠️  DRAFT ONLY — This document is for review purposes and has NOT been "
                "filed with Revenue. Boombox never submits to ROS. Field references are "
                "indicative; verify against the current Form 11 before filing. Review "
                "with a registered tax adviser (AITI/CTA) before filing."
            ),
            "mock": True,
        }

    gross_income = float(get_ytd_income(tax_year))
    allowable_expenses = float(get_ytd_allowable_expenses(tax_year))
    mileage_deduction = float(get_ytd_mileage_deduction(tax_year))

    position = compute_tax_position(
        gross_income=gross_income,
        allowable_expenses=allowable_expenses,
        mileage_deduction=mileage_deduction,
        tax_year=tax_year,
    )

    rules = load_tax_rules(tax_year)
    deadline = rules["deadlines"]["form11_filing"]["date"]

    lines = _build_lines(position)
    total_liability = Decimal(str(position["total_liability"]))
    prelim_paid = Decimal(str(preliminary_tax_paid))
    balance_due = total_liability - prelim_paid

    # Validate via the Pydantic model, then return floats so the JSON
    # contract matches the frontend's `value: number` typing. Pydantic's
    # mode="json" would serialize Decimals as strings.
    FilingDraft(
        tax_year=tax_year,
        status=FilingStatus.DRAFT,
        lines=lines,
        total_liability_estimate=total_liability,
        preliminary_tax_paid=prelim_paid,
        balance_due=balance_due,
        filing_deadline=deadline,
    )

    return {
        "tax_year": tax_year,
        "status": FilingStatus.DRAFT.value,
        "lines": [
            {
                "panel": line.panel,
                "field_ref": line.field_ref,
                "description": line.description,
                "value": float(line.value),
                "source": line.source,
            }
            for line in lines
        ],
        "total_liability_estimate": float(total_liability),
        "preliminary_tax_paid": float(prelim_paid),
        "balance_due": float(balance_due),
        "filing_deadline": deadline,
        "disclaimer": (
            "⚠️  DRAFT ONLY — This document is for review purposes and has NOT been "
            "filed with Revenue. Boombox never submits to ROS. Field references are "
            "indicative; verify against the current Form 11 before filing. Review "
            "with a registered tax adviser (AITI/CTA) before filing."
        ),
    }
