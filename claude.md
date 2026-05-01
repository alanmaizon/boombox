# Boombox: Project Handoff & Roadmap

## Welcome, Claude!
You are picking up **Boombox**, an educational and organisational tax-operations tool for Irish sole-traders. This codebase was rapidly scaffolded recently, but the user has **plenty of compute** and **over a month of runway**. 

**Your directive:** Do not take shortcuts. Write comprehensive tests, deep reasoning loops, robust error handling, and high-quality production-ready code. 

## Project Architecture
- **Backend:** Python / FastAPI / SQLAlchemy (SQLite for dev, moving to PostgreSQL for prod).
- **Agents:** Built using `google-adk` (Google Agent Development Kit). A `CoordinatorAgent` routes tasks to specialist agents (`IncomeAgent`, `ExpenseAgent`, `MileageAgent`, `CalculatorAgent`, `FilingAgent`, `AdvisoryAgent`).
- **Frontend:** Next.js 14 (App Router) / React / Tailwind CSS.
- **Infrastructure:** Docker Compose (frontend and backend containers).

## Current State
1. **Infrastructure:** Docker containers are configured, building successfully, and talking to each other.
2. **Backend:** 
   - Core API endpoints (`/income`, `/expenses`, `/mileage`, `/tax/calculate`) are functional.
   - Database schema and persistence are working.
   - `API_KEY` mapping to `GEMINI_API_KEY` for the `google-adk` agents is configured.
   - 45/45 Backend tests are passing (we recently fixed import issues and test DB teardowns).
3. **Frontend:** 
   - Basic CRUD UI is built and connected to the backend for Income, Expenses, Mileage, and Tax Calculation.
   - **`/advisory`** and **`/filing`** are currently just placeholder pages.
   - Model structure is in place in `lib/api.ts`.

## Final Expected Result (The Goal)
We want to evolve Boombox from a basic CRUD app into a **fully functional, agent-driven tax assistant**. 

### 1. Agent & API Wiring (Immediate Next Steps)
- **Expose Agent Endpoints:** FastAPI currently lacks routes for the multi-agent system. You need to expose the `CoordinatorAgent` (or specific `AdvisoryAgent` / `FilingAgent`) via WebSocket or REST endpoints in `main.py` so the frontend can communicate with them.
- **Advisory UI:** Build out `frontend/app/advisory/page.tsx` as a rich chat interface where the user can ask "What-if" scenarios (e.g., "What if I buy a laptop for €2000?"). The agent must respond with citations using the `irish_tax_rules.json`.
- **Filing UI (Form 11):** Build out `frontend/app/filing/page.tsx` to interface with the `FilingAgent` to generate a draft **Form 11** based on the YTD SQLite data. 

### 2. MCP Integration (Model Context Protocol)
- There are stubs for MCP clients (`mcp_clients.py` and `test_mcp_mock.py`) for Gmail, Google Drive, Google Sheets, and Google Calendar. 
- **Goal:** Wire these MCP tools into the `google-adk` agents so the system can autonomously ingest receipts from Gmail/Drive or sync important tax deadlines to the user's Calendar.

### 3. Production Hardening
- **Database Migration:** Implement the transition from SQLite (dev) to PostgreSQL (prod) as outlined in `docs/decisions/ADR-002-sqlite-dev-postgresql-prod.md`.
- **Authentication:** The app currently has no auth. Implement a secure authentication mechanism.
- **E2E Testing:** Playwright is installed (`tests/e2e/demo.mjs`). Expand this to cover full end-to-end user journeys (logging an invoice -> checking calculate -> generating a Form 11).

## Operating Guidelines for Claude
- You have the time and compute. **Think deeply.**
- If you need to refactor a file, do it robustly.
- Maintain the strict separation of concerns (Tools vs Agents vs FastAPI Routers).
- Always ensure `pytest` and `npm run build` succeed after your changes.
- Ensure the disclaimer (Boombox is not tax advice) remains prominent across agent outputs and UIs.