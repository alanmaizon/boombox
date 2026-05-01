"""
Calculator Agent — runs Income Tax + USC + PRSI computation against current
Irish bands. Pure function over the YTD ledger; deterministic.

Inputs: tax_year (reads YTD totals from storage)
Outputs: full TaxPosition with itemised bands and source citations
Tools: compute_tax_position, get_ytd_income_summary, get_ytd_expenses_summary,
       get_ytd_mileage_summary
"""

from __future__ import annotations

import os
from pathlib import Path

from google.adk.agents import Agent

from backend.tools.expense_tools import get_ytd_expenses_summary
from backend.tools.income_tools import get_ytd_income_summary
from backend.tools.mileage_tools import get_ytd_mileage_summary
from backend.tools.tax_tools import compute_tax_position

_PROMPT_PATH = Path(__file__).parent / "prompts" / "calculator_agent.md"
_SYSTEM_PROMPT = _PROMPT_PATH.read_text()


class CalculatorAgent(Agent):
    """
    Calculator Agent — deterministic Income Tax + USC + PRSI computation.

    Scope:
        Reads YTD totals from income, expense, and mileage tools, then runs
        a full tax position calculation against irish_tax_rules.json bands.

    Inputs:
        tax_year — all other inputs are fetched via tool calls.

    Outputs:
        TaxPosition JSON with per-band breakdown and source citations.

    Tools:
        compute_tax_position, get_ytd_income_summary, get_ytd_expenses_summary,
        get_ytd_mileage_summary
    """

    def __init__(self) -> None:
        super().__init__(
            name="CalculatorAgent",
            model=os.getenv("BOOMBOX_MODEL", "gemini-2.0-flash"),
            description="Computes Income Tax, USC, and PRSI for a given tax year.",
            instruction=_SYSTEM_PROMPT,
            tools=[
                compute_tax_position,
                get_ytd_income_summary,
                get_ytd_expenses_summary,
                get_ytd_mileage_summary,
            ],
        )
