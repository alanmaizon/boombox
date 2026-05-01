"""
Expense Agent — multimodal receipt ingestion → vendor/date/amount/category/VAT split.

Inputs: expense data from receipt photos, PDFs, emails, or manual entry
Outputs: structured expense record + YTD allowable expenses summary
Tools: persist_expense, get_ytd_expenses_summary, query_expense_records
"""

from __future__ import annotations

import os
from pathlib import Path

from google.adk.agents import Agent

from backend.tools.expense_tools import (
    get_ytd_expenses_summary,
    persist_expense,
    query_expense_records,
)

_PROMPT_PATH = Path(__file__).parent / "prompts" / "expense_agent.md"
_SYSTEM_PROMPT = _PROMPT_PATH.read_text()


class ExpenseAgent(Agent):
    """
    Expense Agent — extracts and persists business expenses.

    Scope:
        Accepts receipts, PDFs, emails, and manual data. Classifies allowable/
        non-allowable per TCA 1997 s.81. Splits VAT where present.

    Inputs:
        vendor, expense_date, amount, category, description, tax_year,
        and optionally vat_amount, receipt_ref, notes.

    Outputs:
        JSON confirmation with vendor, amount, allowable flag, ytd_allowable_total.

    Tools:
        persist_expense, get_ytd_expenses_summary, query_expense_records
    """

    def __init__(self) -> None:
        super().__init__(
            name="ExpenseAgent",
            model=os.getenv("BOOMBOX_MODEL", "gemini-2.0-flash"),
            description="Extracts and persists business expense records.",
            instruction=_SYSTEM_PROMPT,
            tools=[persist_expense, get_ytd_expenses_summary, query_expense_records],
        )
