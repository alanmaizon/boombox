"""
Advisory Agent — answers what-if questions by simulating against Irish tax rules.

Every claim includes a source citation. Never makes unsupported assertions.

Inputs: WhatIfQuery (question + optional income/expense/mileage deltas)
Outputs: AdvisoryResponse with cited sources and disclaimer
Tools: compute_tax_position, get_ytd_income_summary, get_ytd_expenses_summary
"""

from __future__ import annotations

import os
from pathlib import Path

from google.adk.agents import Agent

from tools.advisory_tools import simulate_what_if
from tools.expense_tools import get_ytd_expenses_summary
from tools.income_tools import get_ytd_income_summary
from tools.tax_tools import compute_tax_position

_PROMPT_PATH = Path(__file__).parent / "prompts" / "advisory_agent.md"
_SYSTEM_PROMPT = _PROMPT_PATH.read_text()


class AdvisoryAgent(Agent):
    """
    Advisory Agent — what-if scenario simulation with mandatory citations.

    Scope:
        Simulates changes to income, expenses, and mileage. Flags VAT thresholds.
        Every numeric claim includes a source URL or statute reference.

    Inputs:
        WhatIfQuery — question plus optional deltas for income, expenses, mileage.

    Outputs:
        AdvisoryResponse with answer, citations list, caveats, and disclaimer.

    Tools:
        compute_tax_position, get_ytd_income_summary, get_ytd_expenses_summary
    """

    def __init__(self) -> None:
        super().__init__(
            name="AdvisoryAgent",
            model=os.getenv("BOOMBOX_MODEL", "gemini-2.0-flash"),
            description="Answers what-if tax questions with mandatory citations.",
            instruction=_SYSTEM_PROMPT,
            tools=[
                simulate_what_if,
                compute_tax_position,
                get_ytd_income_summary,
                get_ytd_expenses_summary,
            ],
        )
