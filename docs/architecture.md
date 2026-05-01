# Boombox — Architecture

## Overview

Boombox is a multi-agent Irish sole-trader tax-operations system built on Google ADK.
It handles income ingestion, expense tracking, mileage computation, tax estimation,
filing preparation, and advisory what-if analysis.

## Multi-Agent Topology

```
                    CoordinatorAgent (root)
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
   IncomeAgent        ExpenseAgent        MileageAgent
        │                   │                   │
        └───────────┬───────┴───────────────────┘
                    │
              CalculatorAgent
                    │
            ┌───────┴───────┐
            │               │
       FilingAgent   AdvisoryAgent
```

### Agent descriptions

| Agent | File | Responsibility |
|---|---|---|
| CoordinatorAgent | `agents/coordinator_agent.py` | Root router; dispatches to specialists |
| IncomeAgent | `agents/income_agent.py` | Invoice ingestion, YTD income totals |
| ExpenseAgent | `agents/expense_agent.py` | Receipt extraction, allowability, VAT split |
| MileageAgent | `agents/mileage_agent.py` | Trip recording, reimbursed vs deductible |
| CalculatorAgent | `agents/calculator_agent.py` | Income Tax + USC + PRSI computation |
| FilingAgent | `agents/filing_agent.py` | Draft Form 11 line items (never files) |
| AdvisoryAgent | `agents/advisory_agent.py` | What-if simulation with citations |

## Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.11, FastAPI, Google ADK |
| Frontend | Next.js 14, TypeScript, Tailwind CSS |
| Storage (dev) | SQLite |
| Storage (prod) | PostgreSQL via Cloud SQL |
| Deploy | Google Cloud Run |
| MCP | Gmail, Google Drive, Google Sheets, Google Calendar |

## Data flow

1. User submits income/expense/mileage via API or UI
2. CoordinatorAgent routes to the appropriate specialist agent
3. Specialist agent calls tools (pure functions where possible)
4. Tools read rates from `data/irish_tax_rules.json` — never hardcoded
5. Results are persisted to SQLite/PostgreSQL via `storage.py`
6. CalculatorAgent computes tax position on demand
7. FilingAgent maps position to Form 11 fields (DRAFT ONLY)
8. AdvisoryAgent simulates what-if scenarios with citations

## Privacy

- Receipt content and notes are never logged to stdout in production
- Notes fields are stripped before DB write (privacy-first design)
- No real financial data appears in tests, fixtures, or commits
- Encryption at rest required for PostgreSQL production deployment

## Mock mode

Set `BOOMBOX_MOCK=true` to run with all tools and MCP calls stubbed.
Used for CI, e2e tests, and keyless demos.
