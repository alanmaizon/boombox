"""
Income Agent — ingests invoices, categorises, totals YTD, persists to ledger.

Inputs: invoice data (number, client, date, amount, source)
Outputs: structured ingestion confirmation + YTD income summary
Tools: persist_invoice, get_ytd_income_summary, query_income_records
"""

from __future__ import annotations

import os
from pathlib import Path

from google.adk.agents import Agent

from tools.income_tools import (
    get_ytd_income_summary,
    persist_invoice,
    query_income_records,
)

_PROMPT_PATH = Path(__file__).parent / "prompts" / "income_agent.md"
_SYSTEM_PROMPT = _PROMPT_PATH.read_text()


class IncomeAgent(Agent):
    """
    Income Agent — ingests invoices, categorises, totals YTD, persists to ledger.

    Scope:
        Accepts AVASO and third-party invoices. Validates currency (EUR only).
        Persists each record to the ledger. Returns YTD income totals.

    Inputs:
        Invoice fields: invoice_number, source, client_name, invoice_date,
        gross_amount, tax_year, and optionally due_date, payment_date, notes.

    Outputs:
        JSON confirmation with invoice_number, gross_amount, ytd_total.

    Tools:
        persist_invoice, get_ytd_income_summary, query_income_records
    """

    def __init__(self) -> None:
        super().__init__(
            name="IncomeAgent",
            model=os.getenv("BOOMBOX_MODEL", "gemini-2.0-flash"),
            description="Ingests invoices and maintains the income ledger.",
            instruction=_SYSTEM_PROMPT,
            tools=[persist_invoice, get_ytd_income_summary, query_income_records],
        )
