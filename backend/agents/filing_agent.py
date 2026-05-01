"""
Filing Agent — drafts Form 11 line items, generates preliminary tax estimate,
flags 31 October deadline, drafts quarterly position.

NEVER submits to ROS. DRAFT ONLY.

Inputs: TaxPosition from CalculatorAgent
Outputs: FilingDraft with Form 11 panel mappings and disclaimer
Tools: compute_tax_position, get_ytd_income_summary, get_ytd_expenses_summary
"""

from __future__ import annotations

import os
from pathlib import Path

from google.adk.agents import Agent

from backend.tools.expense_tools import get_ytd_expenses_summary
from backend.tools.income_tools import get_ytd_income_summary
from backend.tools.tax_tools import compute_tax_position

_PROMPT_PATH = Path(__file__).parent / "prompts" / "filing_agent.md"
_SYSTEM_PROMPT = _PROMPT_PATH.read_text()


class FilingAgent(Agent):
    """
    Filing Agent — produces draft Form 11 line items for review.

    Scope:
        Maps TaxPosition figures to Form 11 panel/field references.
        Flags 31 October deadline and preliminary tax requirements.
        DRAFT ONLY — never submits to ROS or Revenue.

    Inputs:
        tax_year — fetches TaxPosition via compute_tax_position.

    Outputs:
        FilingDraft JSON with panel mappings, liability estimate, and disclaimer.

    Tools:
        compute_tax_position, get_ytd_income_summary, get_ytd_expenses_summary
    """

    def __init__(self) -> None:
        super().__init__(
            name="FilingAgent",
            model=os.getenv("BOOMBOX_MODEL", "gemini-2.0-flash"),
            description="Drafts Form 11 line items for review. NEVER files with Revenue.",
            instruction=_SYSTEM_PROMPT,
            tools=[compute_tax_position, get_ytd_income_summary, get_ytd_expenses_summary],
        )
