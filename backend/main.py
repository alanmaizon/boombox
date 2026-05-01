"""
Boombox backend — FastAPI entry point.

Endpoints:
    POST /income/ingest       — persist an invoice
    GET  /income/summary      — YTD income summary
    POST /expenses/ingest     — persist an expense
    GET  /expenses/summary    — YTD expense summary
    POST /mileage/record      — persist a mileage trip
    GET  /mileage/summary     — YTD mileage summary
    POST /tax/calculate       — compute full tax position
    GET  /health              — health check

Mock mode: set BOOMBOX_MOCK=true for keyless demo responses.

⚠️  Disclaimer: Boombox is an educational and organisational tool.
It does NOT provide tax advice and does NOT file anything with Revenue.
Always consult a registered tax adviser for complex matters.
"""

from __future__ import annotations

import os
from decimal import Decimal
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from backend.storage import init_db
from backend.tools.expense_tools import get_ytd_expenses_summary, persist_expense
from backend.tools.income_tools import get_ytd_income_summary, persist_invoice
from backend.tools.mileage_tools import get_ytd_mileage_summary, persist_mileage_trip
from backend.tools.tax_tools import compute_tax_position

_MOCK = os.getenv("BOOMBOX_MOCK", "false").lower() == "true"

_DISCLAIMER = (
    "⚠️  Boombox is an educational and organisational tool. "
    "It does NOT provide tax advice and does NOT file anything with Revenue. "
    "Always consult a registered tax adviser (AITI/CTA) for complex matters."
)

app = FastAPI(
    title="Boombox",
    description="Irish sole-trader tax operations — income, expenses, mileage, calculations.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("BOOMBOX_CORS_ORIGINS", "http://localhost:3000").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup() -> None:
    if not _MOCK:
        init_db()


# ---------------------------------------------------------------------------
# Request / response models
# ---------------------------------------------------------------------------


class InvoiceRequest(BaseModel):
    invoice_number: str
    source: str = "OTHER"
    client_name: str
    invoice_date: str
    gross_amount: float = Field(gt=0)
    tax_year: int
    due_date: str | None = None
    payment_date: str | None = None


class ExpenseRequest(BaseModel):
    vendor: str
    expense_date: str
    amount: float = Field(gt=0)
    category: str
    description: str
    tax_year: int
    vat_amount: float = 0.0
    receipt_ref: str | None = None


class MileageRequest(BaseModel):
    trip_date: str
    origin: str
    destination: str
    distance_km: float = Field(gt=0)
    tax_year: int
    round_trip: bool = True
    reimbursed_by_client: bool = False


class TaxCalcRequest(BaseModel):
    gross_income: float = Field(ge=0)
    allowable_expenses: float = Field(ge=0)
    mileage_deduction: float = Field(ge=0)
    tax_year: int


# ---------------------------------------------------------------------------
# Health
# ---------------------------------------------------------------------------


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "mock_mode": str(_MOCK)}


# ---------------------------------------------------------------------------
# Income
# ---------------------------------------------------------------------------


@app.post("/income/ingest")
def ingest_invoice(req: InvoiceRequest) -> dict[str, Any]:
    """Persist an invoice to the income ledger."""
    try:
        result = persist_invoice(
            invoice_number=req.invoice_number,
            source=req.source,
            client_name=req.client_name,
            invoice_date=req.invoice_date,
            gross_amount=req.gross_amount,
            tax_year=req.tax_year,
            due_date=req.due_date,
            payment_date=req.payment_date,
        )
        return {**result, "disclaimer": _DISCLAIMER}
    except Exception as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@app.get("/income/summary")
def income_summary(tax_year: int) -> dict[str, Any]:
    """Return YTD income summary for a given tax year."""
    return {**get_ytd_income_summary(tax_year), "disclaimer": _DISCLAIMER}


# ---------------------------------------------------------------------------
# Expenses
# ---------------------------------------------------------------------------


@app.post("/expenses/ingest")
def ingest_expense(req: ExpenseRequest) -> dict[str, Any]:
    """Persist an expense record to the ledger."""
    try:
        result = persist_expense(
            vendor=req.vendor,
            expense_date=req.expense_date,
            amount=req.amount,
            category=req.category,
            description=req.description,
            tax_year=req.tax_year,
            vat_amount=req.vat_amount,
            receipt_ref=req.receipt_ref,
        )
        return {**result, "disclaimer": _DISCLAIMER}
    except Exception as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@app.get("/expenses/summary")
def expenses_summary(tax_year: int) -> dict[str, Any]:
    """Return YTD allowable expenses summary for a given tax year."""
    return {**get_ytd_expenses_summary(tax_year), "disclaimer": _DISCLAIMER}


# ---------------------------------------------------------------------------
# Mileage
# ---------------------------------------------------------------------------


@app.post("/mileage/record")
def record_mileage(req: MileageRequest) -> dict[str, Any]:
    """Persist a mileage trip to the ledger."""
    try:
        result = persist_mileage_trip(
            trip_date=req.trip_date,
            origin=req.origin,
            destination=req.destination,
            distance_km=req.distance_km,
            tax_year=req.tax_year,
            round_trip=req.round_trip,
            reimbursed_by_client=req.reimbursed_by_client,
        )
        return {**result, "disclaimer": _DISCLAIMER}
    except Exception as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@app.get("/mileage/summary")
def mileage_summary(tax_year: int) -> dict[str, Any]:
    """Return YTD mileage deduction summary for a given tax year."""
    return {**get_ytd_mileage_summary(tax_year), "disclaimer": _DISCLAIMER}


# ---------------------------------------------------------------------------
# Tax calculation
# ---------------------------------------------------------------------------


@app.post("/tax/calculate")
def calculate_tax(req: TaxCalcRequest) -> dict[str, Any]:
    """Compute full Income Tax + USC + PRSI position."""
    try:
        result = compute_tax_position(
            gross_income=req.gross_income,
            allowable_expenses=req.allowable_expenses,
            mileage_deduction=req.mileage_deduction,
            tax_year=req.tax_year,
        )
        return result
    except FileNotFoundError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
