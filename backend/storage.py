"""
Storage layer for Boombox — SQLite for development, PostgreSQL for production.

Uses SQLAlchemy Core (not ORM) to keep things explicit and testable.
"""

from __future__ import annotations

import os
from contextlib import contextmanager
from decimal import Decimal
from typing import Generator

import sqlalchemy as sa
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Connection

# ---------------------------------------------------------------------------
# Engine setup
# ---------------------------------------------------------------------------

_DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./boombox.db")
_engine = create_engine(_DATABASE_URL, connect_args={"check_same_thread": False} if "sqlite" in _DATABASE_URL else {})

# ---------------------------------------------------------------------------
# Schema
# ---------------------------------------------------------------------------

metadata = sa.MetaData()

income_records = sa.Table(
    "income_records",
    metadata,
    sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
    sa.Column("invoice_number", sa.String(64), nullable=False, unique=True),
    sa.Column("source", sa.String(32), nullable=False),
    sa.Column("client_name", sa.String(255), nullable=False),
    sa.Column("invoice_date", sa.Date, nullable=False),
    sa.Column("due_date", sa.Date),
    sa.Column("payment_date", sa.Date),
    sa.Column("gross_amount", sa.Numeric(12, 2), nullable=False),
    sa.Column("currency", sa.String(3), nullable=False, default="EUR"),
    sa.Column("notes", sa.Text),
    sa.Column("tax_year", sa.Integer, nullable=False),
    sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
)

expense_records = sa.Table(
    "expense_records",
    metadata,
    sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
    sa.Column("vendor", sa.String(255), nullable=False),
    sa.Column("expense_date", sa.Date, nullable=False),
    sa.Column("amount", sa.Numeric(12, 2), nullable=False),
    sa.Column("vat_amount", sa.Numeric(12, 2), nullable=False, default=0),
    sa.Column("net_amount", sa.Numeric(12, 2), nullable=False),
    sa.Column("category", sa.String(32), nullable=False),
    sa.Column("description", sa.Text, nullable=False),
    sa.Column("receipt_ref", sa.String(512)),
    sa.Column("allowable", sa.Boolean, nullable=False, default=True),
    sa.Column("notes", sa.Text),
    sa.Column("tax_year", sa.Integer, nullable=False),
    sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
)

mileage_records = sa.Table(
    "mileage_records",
    metadata,
    sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
    sa.Column("trip_date", sa.Date, nullable=False),
    sa.Column("origin", sa.String(255), nullable=False),
    sa.Column("destination", sa.String(255), nullable=False),
    sa.Column("round_trip", sa.Boolean, nullable=False, default=True),
    sa.Column("distance_km", sa.Numeric(10, 2), nullable=False),
    sa.Column("round_trip_km", sa.Numeric(10, 2), nullable=False),
    sa.Column("reimbursed_by_client", sa.Boolean, nullable=False, default=False),
    sa.Column("reimbursed_amount", sa.Numeric(10, 2), nullable=False, default=0),
    sa.Column("deductible_amount", sa.Numeric(10, 2), nullable=False, default=0),
    sa.Column("notes", sa.Text),
    sa.Column("tax_year", sa.Integer, nullable=False),
    sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
)


def init_db() -> None:
    """Create all tables if they don't exist."""
    metadata.create_all(_engine)


# ---------------------------------------------------------------------------
# Connection context manager
# ---------------------------------------------------------------------------


@contextmanager
def get_connection() -> Generator[Connection, None, None]:
    with _engine.connect() as conn:
        yield conn
        conn.commit()


# ---------------------------------------------------------------------------
# Income persistence
# ---------------------------------------------------------------------------


def persist_income_record(record: dict) -> int:
    """Insert an income record. Returns the new row id."""
    with get_connection() as conn:
        result = conn.execute(income_records.insert().values(**record))
        return result.inserted_primary_key[0]


def get_income_records(tax_year: int) -> list[dict]:
    """Return all income records for a given tax year."""
    with get_connection() as conn:
        rows = conn.execute(
            income_records.select().where(income_records.c.tax_year == tax_year)
        ).fetchall()
        return [dict(row._mapping) for row in rows]


def get_ytd_income(tax_year: int) -> Decimal:
    """Sum gross_amount for the given tax year."""
    with get_connection() as conn:
        result = conn.execute(
            sa.select(sa.func.coalesce(sa.func.sum(income_records.c.gross_amount), 0)).where(
                income_records.c.tax_year == tax_year
            )
        ).scalar()
        return Decimal(str(result))


# ---------------------------------------------------------------------------
# Expense persistence
# ---------------------------------------------------------------------------


def persist_expense_record(record: dict) -> int:
    """Insert an expense record. Returns the new row id."""
    with get_connection() as conn:
        result = conn.execute(expense_records.insert().values(**record))
        return result.inserted_primary_key[0]


def get_expense_records(tax_year: int) -> list[dict]:
    """Return all expense records for a given tax year."""
    with get_connection() as conn:
        rows = conn.execute(
            expense_records.select().where(expense_records.c.tax_year == tax_year)
        ).fetchall()
        return [dict(row._mapping) for row in rows]


def get_ytd_allowable_expenses(tax_year: int) -> Decimal:
    """Sum net_amount for allowable expenses in the given tax year."""
    with get_connection() as conn:
        result = conn.execute(
            sa.select(
                sa.func.coalesce(sa.func.sum(expense_records.c.net_amount), 0)
            ).where(
                sa.and_(
                    expense_records.c.tax_year == tax_year,
                    expense_records.c.allowable == True,  # noqa: E712
                )
            )
        ).scalar()
        return Decimal(str(result))


# ---------------------------------------------------------------------------
# Mileage persistence
# ---------------------------------------------------------------------------


def persist_mileage_record(record: dict) -> int:
    """Insert a mileage record. Returns the new row id."""
    with get_connection() as conn:
        result = conn.execute(mileage_records.insert().values(**record))
        return result.inserted_primary_key[0]


def get_mileage_records(tax_year: int) -> list[dict]:
    """Return all mileage records for a given tax year."""
    with get_connection() as conn:
        rows = conn.execute(
            mileage_records.select().where(mileage_records.c.tax_year == tax_year)
        ).fetchall()
        return [dict(row._mapping) for row in rows]


def get_ytd_mileage_deduction(tax_year: int) -> Decimal:
    """Sum deductible_amount for non-reimbursed mileage in the given tax year."""
    with get_connection() as conn:
        result = conn.execute(
            sa.select(
                sa.func.coalesce(sa.func.sum(mileage_records.c.deductible_amount), 0)
            ).where(
                sa.and_(
                    mileage_records.c.tax_year == tax_year,
                    mileage_records.c.reimbursed_by_client == False,  # noqa: E712
                )
            )
        ).scalar()
        return Decimal(str(result))
