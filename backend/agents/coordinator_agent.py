"""
Coordinator Agent — root agent that routes user requests to specialist agents.

This is the top-level entry point for the multi-agent system.

Topology:
    Coordinator → IncomeAgent | ExpenseAgent | MileageAgent
                → CalculatorAgent → FilingAgent | AdvisoryAgent
"""

from __future__ import annotations

import os
from pathlib import Path

from google.adk.agents import Agent

from agents.advisory_agent import AdvisoryAgent
from agents.calculator_agent import CalculatorAgent
from agents.expense_agent import ExpenseAgent
from agents.filing_agent import FilingAgent
from agents.income_agent import IncomeAgent
from agents.mileage_agent import MileageAgent

_PROMPT_PATH = Path(__file__).parent / "prompts" / "coordinator_agent.md"
_SYSTEM_PROMPT = _PROMPT_PATH.read_text()


class CoordinatorAgent(Agent):
    """
    Coordinator Agent — root of the multi-agent topology.

    Scope:
        Routes income, expense, mileage, calculation, filing, and advisory
        requests to the appropriate specialist agent. Aggregates responses.

    Inputs:
        Any natural-language request from the user.

    Outputs:
        Aggregated response from the relevant specialist agent(s), with disclaimer.

    Sub-agents:
        IncomeAgent, ExpenseAgent, MileageAgent, CalculatorAgent,
        FilingAgent, AdvisoryAgent
    """

    def __init__(self) -> None:
        super().__init__(
            name="CoordinatorAgent",
            model=os.getenv("BOOMBOX_MODEL", "gemini-2.0-flash"),
            description="Root coordinator — routes requests to specialist agents.",
            instruction=_SYSTEM_PROMPT,
            sub_agents=[
                IncomeAgent(),
                ExpenseAgent(),
                MileageAgent(),
                CalculatorAgent(),
                FilingAgent(),
                AdvisoryAgent(),
            ],
        )
