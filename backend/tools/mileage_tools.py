"""
Mileage tools — record trips, compute reimbursed and owner-deductible portions.

AVASO policy: trips with round-trip distance ≥ 40 km are reimbursed at €0.44/km.
The reimbursed portion is NOT tax-deductible by the owner (it is employer-paid).
Owner can deduct non-reimbursed business mileage at civil service rates.
"""

from __future__ import annotations

import os
from datetime import date
from decimal import Decimal, ROUND_HALF_UP
from typing import Any

from backend.models import MileageRecord
from backend.storage import get_mileage_records, get_ytd_mileage_deduction, persist_mileage_record
from backend.tools.tax_data import load_tax_rules

_MOCK = os.getenv("BOOMBOX_MOCK", "false").lower() == "true"


def _civil_service_rate(km: Decimal, rules: dict) -> Decimal:
    """
    Compute the Revenue-approved civil service mileage deduction for ``km`` km.

    Bands from data/irish_tax_rules.json (mileage.rates).
    Source: https://www.revenue.ie/en/personal-tax-credits-reliefs-and-exemptions/travel/motor-travel-rates/index.aspx
    """
    bands = rules["mileage"]["rates"]
    remaining = km
    total = Decimal("0")
    accumulated = Decimal("0")

    for band in bands:
        lower = Decimal(str(band["lower_km"]))
        upper = Decimal(str(band["upper_km"])) if band["upper_km"] is not None else None
        rate = Decimal(str(band["rate_per_km"]))

        band_size = (upper - lower) if upper is not None else remaining
        in_band = min(remaining, band_size - max(Decimal("0"), accumulated - lower))

        start_in_band = max(Decimal("0"), accumulated - lower) if accumulated > lower else Decimal("0")
        avail = band_size - start_in_band if upper else remaining

        in_band = min(remaining, avail)
        if in_band <= 0:
            accumulated += Decimal("0")
            continue

        total += (in_band * rate).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        remaining -= in_band
        accumulated += in_band

        if remaining <= 0:
            break

    return total


def compute_mileage(
    distance_km: float,
    round_trip: bool,
    reimbursed_by_client: bool,
    tax_year: int,
) -> dict[str, Any]:
    """
    Compute reimbursed amount and owner-deductible mileage.

    Args:
        distance_km: One-way distance in km.
        round_trip: Whether this is a return trip.
        reimbursed_by_client: True if AVASO reimburses this trip.
        tax_year: Tax year for rate lookup.

    Returns:
        A dict with ``round_trip_km``, ``reimbursed_amount``, ``deductible_amount``.
    """
    rules = load_tax_rules(tax_year)
    avaso_rate = Decimal(str(rules["mileage"]["avaso_rate_per_km"]))
    min_rt_km = Decimal(str(rules["mileage"]["avaso_minimum_round_trip_km"]))

    rt_km = Decimal(str(distance_km)) * (2 if round_trip else 1)

    reimbursed_amount = Decimal("0")
    deductible_amount = Decimal("0")

    if reimbursed_by_client and rt_km >= min_rt_km:
        reimbursed_amount = (rt_km * avaso_rate).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    else:
        # Owner-deductible portion uses civil service rates
        deductible_amount = _civil_service_rate(rt_km, rules)

    return {
        "round_trip_km": float(rt_km),
        "reimbursed_amount": float(reimbursed_amount),
        "deductible_amount": float(deductible_amount),
        "source": rules["mileage"]["source"],
    }


def persist_mileage_trip(
    trip_date: str,
    origin: str,
    destination: str,
    distance_km: float,
    tax_year: int,
    round_trip: bool = True,
    reimbursed_by_client: bool = False,
    notes: str | None = None,
) -> dict[str, Any]:
    """
    Record a mileage trip and persist it to the ledger.

    Args:
        trip_date: ISO 8601 date string (YYYY-MM-DD).
        origin: Starting location.
        destination: Ending location.
        distance_km: One-way distance in km.
        tax_year: Tax year this trip belongs to.
        round_trip: Whether this is a return trip (default True).
        reimbursed_by_client: True if AVASO reimburses this trip.
        notes: Optional notes.

    Returns:
        A dict with ``id``, ``round_trip_km``, ``reimbursed_amount``, ``deductible_amount``.
    """
    if _MOCK:
        return {
            "id": 1,
            "round_trip_km": distance_km * 2 if round_trip else distance_km,
            "reimbursed_amount": distance_km * 2 * 0.44 if reimbursed_by_client else 0.0,
            "deductible_amount": 0.0,
            "mock": True,
        }

    computed = compute_mileage(distance_km, round_trip, reimbursed_by_client, tax_year)
    rt_km = Decimal(str(computed["round_trip_km"]))
    reimbursed = Decimal(str(computed["reimbursed_amount"]))
    deductible = Decimal(str(computed["deductible_amount"]))

    record = MileageRecord(
        trip_date=date.fromisoformat(trip_date),
        origin=origin,
        destination=destination,
        round_trip=round_trip,
        distance_km=Decimal(str(distance_km)),
        round_trip_km=rt_km,
        reimbursed_by_client=reimbursed_by_client,
        reimbursed_amount=reimbursed,
        deductible_amount=deductible,
        notes=notes,
        tax_year=tax_year,
    )

    row = {
        "trip_date": record.trip_date,
        "origin": record.origin,
        "destination": record.destination,
        "round_trip": record.round_trip,
        "distance_km": record.distance_km,
        "round_trip_km": record.round_trip_km,
        "reimbursed_by_client": record.reimbursed_by_client,
        "reimbursed_amount": record.reimbursed_amount,
        "deductible_amount": record.deductible_amount,
        "notes": None,
        "tax_year": record.tax_year,
    }
    new_id = persist_mileage_record(row)
    return {
        "id": new_id,
        "round_trip_km": float(rt_km),
        "reimbursed_amount": float(reimbursed),
        "deductible_amount": float(deductible),
    }


def get_ytd_mileage_summary(tax_year: int) -> dict[str, Any]:
    """
    Query year-to-date mileage deduction total for a given tax year.

    Args:
        tax_year: The tax year to query.

    Returns:
        A dict with ``tax_year``, ``total_deductible_mileage``, ``record_count``.
    """
    if _MOCK:
        return {"tax_year": tax_year, "total_deductible_mileage": 180.00, "record_count": 6, "mock": True}

    records = get_mileage_records(tax_year)
    total = get_ytd_mileage_deduction(tax_year)
    return {
        "tax_year": tax_year,
        "total_deductible_mileage": float(total),
        "record_count": len(records),
    }
