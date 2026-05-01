"""
Pydantic schemas for Boombox — income, expenses, mileage, and tax position.

All monetary amounts are in EUR. Dates follow ISO 8601 (YYYY-MM-DD).
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, field_validator


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------


class ExpenseCategory(str, Enum):
    TRAVEL = "TRAVEL"
    EQUIPMENT = "EQUIPMENT"
    SOFTWARE = "SOFTWARE"
    PHONE = "PHONE"
    HOME_OFFICE = "HOME_OFFICE"
    PROFESSIONAL_FEES = "PROFESSIONAL_FEES"
    TRAINING = "TRAINING"
    MARKETING = "MARKETING"
    BANK_CHARGES = "BANK_CHARGES"
    CLOTHING = "CLOTHING"
    FOOD = "FOOD"
    MILEAGE = "MILEAGE"
    OTHER = "OTHER"


class IncomeSource(str, Enum):
    AVASO = "AVASO"
    OTHER = "OTHER"


class FilingStatus(str, Enum):
    DRAFT = "DRAFT"
    READY = "READY"
    SUBMITTED = "SUBMITTED"


# ---------------------------------------------------------------------------
# Income
# ---------------------------------------------------------------------------


class InvoiceItem(BaseModel):
    """A single line item on an invoice."""

    description: str
    quantity: Decimal = Field(gt=0)
    unit_price: Decimal = Field(ge=0)
    amount: Decimal = Field(ge=0)


class IncomeRecord(BaseModel):
    """A single income record (invoice or payment received)."""

    id: Optional[int] = None
    invoice_number: str
    source: IncomeSource = IncomeSource.OTHER
    client_name: str
    invoice_date: date
    due_date: Optional[date] = None
    payment_date: Optional[date] = None
    line_items: list[InvoiceItem] = Field(default_factory=list)
    gross_amount: Decimal = Field(ge=0, description="Total invoice amount before any deductions (EUR)")
    currency: str = Field(default="EUR", max_length=3)
    notes: Optional[str] = None
    tax_year: int

    @field_validator("currency")
    @classmethod
    def currency_uppercase(cls, v: str) -> str:
        return v.upper()

    @field_validator("tax_year")
    @classmethod
    def tax_year_range(cls, v: int) -> int:
        if not (2020 <= v <= 2100):
            raise ValueError("tax_year must be between 2020 and 2100")
        return v


# ---------------------------------------------------------------------------
# Expenses
# ---------------------------------------------------------------------------


class ExpenseRecord(BaseModel):
    """A single expense record."""

    id: Optional[int] = None
    vendor: str
    expense_date: date
    amount: Decimal = Field(ge=0, description="Gross amount paid (EUR)")
    vat_amount: Decimal = Field(default=Decimal("0"), ge=0, description="VAT portion, if applicable (EUR)")
    net_amount: Decimal = Field(ge=0, description="Amount excluding VAT (EUR)")
    category: ExpenseCategory
    description: str
    receipt_ref: Optional[str] = Field(default=None, description="Reference to stored receipt (Drive URL or local path)")
    allowable: bool = Field(default=True, description="Is this expense tax-deductible?")
    notes: Optional[str] = None
    tax_year: int

    @field_validator("tax_year")
    @classmethod
    def tax_year_range(cls, v: int) -> int:
        if not (2020 <= v <= 2100):
            raise ValueError("tax_year must be between 2020 and 2100")
        return v


# ---------------------------------------------------------------------------
# Mileage
# ---------------------------------------------------------------------------


class MileageRecord(BaseModel):
    """A single mileage record for a business trip."""

    id: Optional[int] = None
    trip_date: date
    origin: str
    destination: str
    round_trip: bool = True
    distance_km: Decimal = Field(gt=0, description="One-way distance in km")
    round_trip_km: Decimal = Field(ge=0, description="Total round-trip distance in km")
    reimbursed_by_client: bool = Field(
        default=False,
        description="True if AVASO reimbursed this trip (≥40km round trip at €0.44/km)",
    )
    reimbursed_amount: Decimal = Field(default=Decimal("0"), ge=0)
    deductible_amount: Decimal = Field(
        default=Decimal("0"),
        ge=0,
        description="Owner-deductible portion (non-reimbursed business mileage)",
    )
    notes: Optional[str] = None
    tax_year: int

    @field_validator("tax_year")
    @classmethod
    def tax_year_range(cls, v: int) -> int:
        if not (2020 <= v <= 2100):
            raise ValueError("tax_year must be between 2020 and 2100")
        return v


# ---------------------------------------------------------------------------
# Tax Position
# ---------------------------------------------------------------------------


class TaxBandResult(BaseModel):
    """Result for a single tax band computation."""

    label: str
    taxable_in_band: Decimal
    rate: Decimal
    tax: Decimal
    source: str


class IncomeTaxResult(BaseModel):
    """Itemised Income Tax computation."""

    gross_income: Decimal
    allowable_expenses: Decimal
    net_profit: Decimal
    bands: list[TaxBandResult]
    gross_tax: Decimal
    personal_credit: Decimal
    earned_income_credit: Decimal
    total_credits: Decimal
    net_income_tax: Decimal
    source: str = "https://www.revenue.ie/en/personal-tax-credits-reliefs-and-exemptions/tax-relief-charts/index.aspx"


class USCResult(BaseModel):
    """Itemised USC computation."""

    reckonable_income: Decimal
    bands: list[TaxBandResult]
    total_usc: Decimal
    source: str = "https://www.revenue.ie/en/jobs-and-pensions/usc/index.aspx"


class PRSIResult(BaseModel):
    """Itemised PRSI computation."""

    reckonable_income: Decimal
    rate: Decimal
    total_prsi: Decimal
    source: str = "https://www.citizensinformation.ie/en/social-welfare/irish-social-welfare-system/social-insurance-prsi/class-s-prsi/"


class TaxPosition(BaseModel):
    """Full YTD tax position for a self-assessed sole trader."""

    tax_year: int
    ytd_income: Decimal
    ytd_expenses: Decimal
    ytd_mileage_deduction: Decimal
    net_profit: Decimal
    income_tax: IncomeTaxResult
    usc: USCResult
    prsi: PRSIResult
    total_liability: Decimal
    disclaimer: str = (
        "⚠️  This is an educational estimate only and does NOT constitute tax advice. "
        "Figures are indicative and based on vendored rate data. "
        "Always consult a registered tax adviser (AITI/CTA) for your personal circumstances "
        "before making any financial or filing decisions."
    )


# ---------------------------------------------------------------------------
# Filing
# ---------------------------------------------------------------------------


class Form11DraftLine(BaseModel):
    """A single line item in a draft Form 11."""

    panel: str
    field_ref: str
    description: str
    value: Decimal
    source: Optional[str] = None


class FilingDraft(BaseModel):
    """A draft set of Form 11 line items for review."""

    tax_year: int
    status: FilingStatus = FilingStatus.DRAFT
    lines: list[Form11DraftLine]
    total_liability_estimate: Decimal
    preliminary_tax_paid: Decimal = Decimal("0")
    balance_due: Decimal
    filing_deadline: str = "31 October"
    disclaimer: str = (
        "⚠️  DRAFT ONLY — This document is for review purposes and has NOT been filed with Revenue. "
        "Boombox never submits to ROS. Review with a registered tax adviser before filing."
    )


# ---------------------------------------------------------------------------
# Advisory
# ---------------------------------------------------------------------------


class WhatIfQuery(BaseModel):
    """A what-if scenario query for the Advisory Agent."""

    question: str
    additional_income: Optional[Decimal] = Decimal("0")
    additional_expense: Optional[Decimal] = Decimal("0")
    additional_mileage_km: Optional[Decimal] = Decimal("0")
    context: Optional[str] = None


class AdvisoryResponse(BaseModel):
    """Advisory Agent response — always includes citations and disclaimer."""

    question: str
    answer: str
    citations: list[str]
    caveats: list[str] = Field(default_factory=list)
    disclaimer: str = (
        "⚠️  This is NOT tax advice. It is an educational simulation based on published Irish tax rules. "
        "Consult a registered tax adviser (AITI/CTA) for advice specific to your situation."
    )
