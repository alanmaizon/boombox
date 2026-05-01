"""
Income tools — ingest invoices, query YTD income.

All tools are pure functions where possible; side-effect tools are named
with a verb indicating the side effect (persist_invoice).
"""

from __future__ import annotations

import os
from datetime import date
from decimal import Decimal
from typing import Any

from backend.models import IncomeRecord, IncomeSource
from backend.storage import get_income_records, get_ytd_income, persist_income_record

_MOCK = os.getenv("BOOMBOX_MOCK", "false").lower() == "true"


def persist_invoice(
    invoice_number: str,
    source: str,
    client_name: str,
    invoice_date: str,
    gross_amount: float,
    tax_year: int,
    due_date: str | None = None,
    payment_date: str | None = None,
    notes: str | None = None,
) -> dict[str, Any]:
    """
    Persist an invoice to the ledger.

    Args:
        invoice_number: Unique invoice reference (e.g. "AVASO-2025-001").
        source: Income source — "AVASO" or "OTHER".
        client_name: Name of the client / payer.
        invoice_date: ISO 8601 date string (YYYY-MM-DD).
        gross_amount: Total invoice amount in EUR.
        tax_year: Tax year this income belongs to.
        due_date: Optional ISO 8601 due date string.
        payment_date: Optional ISO 8601 payment received date.
        notes: Optional free-text notes (never logged in production).

    Returns:
        A dict with ``id``, ``invoice_number``, and ``gross_amount``.
    """
    if _MOCK:
        return {"id": 1, "invoice_number": invoice_number, "gross_amount": gross_amount, "mock": True}

    record = IncomeRecord(
        invoice_number=invoice_number,
        source=IncomeSource(source),
        client_name=client_name,
        invoice_date=date.fromisoformat(invoice_date),
        due_date=date.fromisoformat(due_date) if due_date else None,
        payment_date=date.fromisoformat(payment_date) if payment_date else None,
        gross_amount=Decimal(str(gross_amount)),
        tax_year=tax_year,
        notes=notes,
    )

    row = {
        "invoice_number": record.invoice_number,
        "source": record.source.value,
        "client_name": record.client_name,
        "invoice_date": record.invoice_date,
        "due_date": record.due_date,
        "payment_date": record.payment_date,
        "gross_amount": record.gross_amount,
        "currency": record.currency,
        "notes": None,  # never persist raw notes to production DB
        "tax_year": record.tax_year,
    }
    new_id = persist_income_record(row)
    return {"id": new_id, "invoice_number": invoice_number, "gross_amount": gross_amount}


def get_ytd_income_summary(tax_year: int) -> dict[str, Any]:
    """
    Query year-to-date income total and record count for a given tax year.

    Args:
        tax_year: The tax year to query (e.g. 2025).

    Returns:
        A dict with ``tax_year``, ``total_income``, ``record_count``.
    """
    if _MOCK:
        return {"tax_year": tax_year, "total_income": 28000.00, "record_count": 4, "mock": True}

    records = get_income_records(tax_year)
    total = get_ytd_income(tax_year)
    return {
        "tax_year": tax_year,
        "total_income": float(total),
        "record_count": len(records),
    }


def query_income_records(tax_year: int) -> list[dict[str, Any]]:
    """
    Return all income records for the given tax year.

    Args:
        tax_year: The tax year to query.

    Returns:
        List of income record dicts (id, invoice_number, source, client_name,
        invoice_date, gross_amount).
    """
    if _MOCK:
        return [
            {
                "id": 1,
                "invoice_number": "AVASO-2025-001",
                "source": "AVASO",
                "client_name": "AVASO Technology Solutions",
                "invoice_date": "2025-01-31",
                "gross_amount": 7000.00,
                "tax_year": tax_year,
                "mock": True,
            }
        ]

    return get_income_records(tax_year)
