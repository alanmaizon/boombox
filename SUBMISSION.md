# Boombox — Hackathon Submission

**Competition:** Google Cloud Rapid Agent Hackathon  
**Deadline:** 11 June 2026  
**Team:** Alan Maizon  

---

## What was built

Boombox is a multi-agent Irish sole-trader tax-operations system.

### MCPs integrated

| MCP | Purpose | Status |
|---|---|---|
| Gmail | Parse income from invoice emails | Stubbed (mock mode) / live with env vars |
| Google Drive | Store receipt files | Stubbed (mock mode) / live with env vars |
| Google Sheets | Export expense ledger | Stubbed (mock mode) / live with env vars |
| Google Calendar | Create filing deadline reminders | Stubbed (mock mode) / live with env vars |

### ADK patterns used

- `Agent` with `tools` (all specialist agents)
- `Agent` with `sub_agents` (CoordinatorAgent)
- Tool decorators and pure-function tool design
- Mock mode for keyless demo (`BOOMBOX_MOCK=true`)

---

## Demo checklist

1. ☐ Receipt photo → expense extraction → categorisation → ledger entry
2. ☐ Invoice import (mock AVASO invoice): income recorded, YTD total updated
3. ☐ Mileage entry: Enniskerry → Rathdrum, AVASO-reimbursed portion separated
4. ☐ Tax calculation: YTD position with Income Tax + USC + PRSI estimate
5. ☐ MCP integration: at least one of Gmail / Drive / Sheets / Calendar live
6. ☐ Advisory Agent: what-if question with cited sources

---

## How to run the demo

```bash
# Mock mode (no API keys required)
BOOMBOX_MOCK=true docker compose up --build
```

Open [http://localhost:3000](http://localhost:3000) and walk through the demo steps.

---

## Demo video

_Link to be added before submission._

---

## Disclaimer

⚠️ Boombox is an educational and organisational tool. It does NOT provide tax advice
and does NOT file anything with Revenue. Always consult a registered tax adviser.
