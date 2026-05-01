"""
Expense tools — ingest expenses (receipts, PDFs, manual entries), query YTD totals.
"""

from __future__ import annotations

import os
from datetime import date
from decimal import Decimal
from typing import Any

from backend.models import ExpenseCategory, ExpenseRecord
from backend.storage import get_expense_records, get_ytd_allowable_expenses, persist_expense_record

_MOCK = os.getenv("BOOMBOX_MOCK", "false").lower() == "true"

# Categories that are NEVER allowable per Irish tax rules.
_DISALLOWABLE_CATEGORIES = {ExpenseCategory.CLOTHING, ExpenseCategory.FOOD}


def persist_expense(
    vendor: str,
    expense_date: str,
    amount: float,
    category: str,
    description: str,
    tax_year: int,
    vat_amount: float = 0.0,
    receipt_ref: str | None = None,
    notes: str | None = None,
) -> dict[str, Any]:
    """
    Persist an expense record.

    Args:
        vendor: Supplier / vendor name.
        expense_date: ISO 8601 date string (YYYY-MM-DD).
        amount: Gross amount paid in EUR.
        category: Expense category code (see ExpenseCategory enum).
        description: Brief description of the expense.
        tax_year: Tax year this expense belongs to.
        vat_amount: VAT portion of the amount, if applicable.
        receipt_ref: Optional reference to stored receipt (Drive URL or local path).
        notes: Optional free-text notes (never logged in production).

    Returns:
        A dict with ``id``, ``vendor``, ``amount``, and ``allowable``.
    """
    if _MOCK:
        return {"id": 1, "vendor": vendor, "amount": amount, "allowable": True, "mock": True}

    cat = ExpenseCategory(category)
    allowable = cat not in _DISALLOWABLE_CATEGORIES
    net = Decimal(str(amount)) - Decimal(str(vat_amount))

    record = ExpenseRecord(
        vendor=vendor,
        expense_date=date.fromisoformat(expense_date),
        amount=Decimal(str(amount)),
        vat_amount=Decimal(str(vat_amount)),
        net_amount=net,
        category=cat,
        description=description,
        receipt_ref=receipt_ref,
        allowable=allowable,
        notes=notes,
        tax_year=tax_year,
    )

    row = {
        "vendor": record.vendor,
        "expense_date": record.expense_date,
        "amount": record.amount,
        "vat_amount": record.vat_amount,
        "net_amount": record.net_amount,
        "category": record.category.value,
        "description": record.description,
        "receipt_ref": record.receipt_ref,
        "allowable": record.allowable,
        "notes": None,  # never persist raw notes to production DB
        "tax_year": record.tax_year,
    }
    new_id = persist_expense_record(row)
    return {"id": new_id, "vendor": vendor, "amount": amount, "allowable": allowable}


def get_ytd_expenses_summary(tax_year: int) -> dict[str, Any]:
    """
    Query year-to-date allowable expenses total for a given tax year.

    Args:
        tax_year: The tax year to query.

    Returns:
        A dict with ``tax_year``, ``total_allowable_expenses``, ``record_count``.
    """
    if _MOCK:
        return {"tax_year": tax_year, "total_allowable_expenses": 3200.00, "record_count": 12, "mock": True}

    records = get_expense_records(tax_year)
    total = get_ytd_allowable_expenses(tax_year)
    return {
        "tax_year": tax_year,
        "total_allowable_expenses": float(total),
        "record_count": len(records),
    }


def query_expense_records(tax_year: int) -> list[dict[str, Any]]:
    """
    Return all expense records for the given tax year.

    Args:
        tax_year: The tax year to query.

    Returns:
        List of expense record dicts.
    """
    if _MOCK:
        return [
            {
                "id": 1,
                "vendor": "Eir",
                "expense_date": "2025-01-10",
                "amount": 49.99,
                "vat_amount": 9.57,
                "net_amount": 40.42,
                "category": "PHONE",
                "allowable": True,
                "tax_year": tax_year,
                "mock": True,
            }
        ]

    return get_expense_records(tax_year)
