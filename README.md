# Boombox

> Irish sole-trader tax operations — income, expenses, mileage, calculations.  
> Google Cloud Rapid Agent Hackathon submission.

**⚠️ Disclaimer:** Boombox is an educational and organisational tool. It does **not** provide tax advice and does **not** file anything with Revenue. Always consult a registered tax adviser (AITI/CTA) for complex matters.

---

## What it does

Boombox is a multi-agent system (Google ADK) that handles:

1. **Income ingestion** — record AVASO invoices and other income
2. **Expense tracking** — log receipts with category, VAT split, allowability
3. **Mileage computation** — separate AVASO-reimbursed from owner-deductible trips
4. **Tax estimation** — Income Tax + USC + PRSI against Finance Act 2025 rates
5. **Filing preparation** — draft Form 11 line items for review (DRAFT ONLY)
6. **Advisory Q&A** — what-if scenarios with cited Revenue.ie / statute sources

---

## Quick start

### Local (mock mode, no API keys required)

```bash
BOOMBOX_MOCK=true docker compose up --build
```

Open [http://localhost:3000](http://localhost:3000).

### Local (live mode)

Copy `.env.example` to `.env` and fill in your API keys:

```bash
cp .env.example .env
docker compose up --build
```

### Backend only

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

API docs at [http://localhost:8000/docs](http://localhost:8000/docs).

---

## Build commands

| Command | Description |
|---|---|
| `docker compose up --build` | Full stack locally |
| `cd backend && pytest` | Backend tests |
| `cd frontend && npm test` | Frontend unit tests |
| `cd tests/e2e && node demo.mjs` | E2E demo flow |
| `bash deploy/cloud-run-backend.sh` | Deploy backend to Cloud Run |
| `bash deploy/cloud-run-frontend.sh` | Deploy frontend to Cloud Run |

---

## Architecture

See [docs/architecture.md](docs/architecture.md) for the full multi-agent topology.

### Agent topology

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

---

## Tax data

All rates sourced from **Finance Act 2025 / Budget 2026**. Single source of truth: `backend/data/irish_tax_rules.json`.

Sources: Revenue.ie, Citizens Information, Irish Statute Book (TCA 1997).

Rate updates require a PR with source citations — never hardcoded in code.

---

## Development notes

- **Python:** type hints everywhere, `ruff` + `black`, `pytest`
- **TypeScript:** strict mode, ESLint + Prettier
- **Mock mode:** `BOOMBOX_MOCK=true` stubs all tool and MCP calls
- **Privacy:** notes/receipt content stripped from DB writes; never logged in production
- **No real data in tests** — all fixtures use synthetic values

---

## Disclaimer (full text)

> ⚠️ Boombox is an educational and organisational tool. All tax estimates are indicative only, based on Finance Act 2025 / Budget 2026 rates. They do not constitute tax advice and should not be used as the basis for financial or filing decisions. Always consult a registered tax adviser (AITI Chartered Tax Adviser / CTA) for advice specific to your situation. Boombox never submits anything to Revenue on your behalf — all outputs are drafts for review only.

