"""
Mileage Agent — trip data in, deductible mileage out.

Separates AVASO-reimbursed trips (≥40km round trip at €0.44/km) from
owner-deductible portions.

Inputs: trip data (date, origin, destination, distance, reimbursed flag)
Outputs: reimbursed and deductible amounts with source citations
Tools: compute_mileage, persist_mileage_trip, get_ytd_mileage_summary
"""

from __future__ import annotations

import os
from pathlib import Path

from google.adk.agents import Agent

from backend.tools.mileage_tools import (
    compute_mileage,
    get_ytd_mileage_summary,
    persist_mileage_trip,
)

_PROMPT_PATH = Path(__file__).parent / "prompts" / "mileage_agent.md"
_SYSTEM_PROMPT = _PROMPT_PATH.read_text()


class MileageAgent(Agent):
    """
    Mileage Agent — records trips, separates reimbursed from deductible mileage.

    Scope:
        AVASO-reimbursed trips: round trips ≥ 40 km at €0.44/km.
        Owner-deductible trips: civil service rates from irish_tax_rules.json.

    Inputs:
        trip_date, origin, destination, distance_km, tax_year,
        round_trip (default True), reimbursed_by_client (default False).

    Outputs:
        JSON with round_trip_km, reimbursed_amount, deductible_amount.

    Tools:
        compute_mileage, persist_mileage_trip, get_ytd_mileage_summary
    """

    def __init__(self) -> None:
        super().__init__(
            name="MileageAgent",
            model=os.getenv("BOOMBOX_MODEL", "gemini-2.0-flash"),
            description="Records business trips and computes deductible mileage.",
            instruction=_SYSTEM_PROMPT,
            tools=[compute_mileage, persist_mileage_trip, get_ytd_mileage_summary],
        )
