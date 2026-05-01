#!/usr/bin/env node
/**
 * Boombox E2E demo flow — runs the full demo sequence in mock mode.
 *
 * Usage: BOOMBOX_MOCK=true node tests/e2e/demo.mjs
 *
 * Demonstrates:
 *   1. Invoice ingestion (AVASO)
 *   2. Expense recording
 *   3. Mileage trip (Enniskerry → Rathdrum)
 *   4. Tax calculation (YTD position)
 *   5. Advisory what-if query
 */

const BASE_URL = process.env.BOOMBOX_API_URL ?? "http://localhost:8000";
const TAX_YEAR = 2025;

async function post(path, body) {
  const res = await fetch(`${BASE_URL}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(`POST ${path} failed: ${err.detail ?? res.statusText}`);
  }
  return res.json();
}

async function get(path) {
  const res = await fetch(`${BASE_URL}${path}`);
  if (!res.ok) throw new Error(`GET ${path} failed: ${res.statusText}`);
  return res.json();
}

function step(n, label) {
  console.log(`\n── Step ${n}: ${label} ──`);
}

async function main() {
  console.log("🎬  Boombox Demo — mock mode");
  console.log("⚠️  Educational tool only. Not tax advice.\n");

  // Health check
  const health = await get("/health");
  console.log("Health:", health);

  // Step 1: Ingest AVASO invoice
  step(1, "Invoice ingestion (AVASO)");
  const invoice = await post("/income/ingest", {
    invoice_number: "AVASO-2025-001",
    source: "AVASO",
    client_name: "AVASO Technology Solutions",
    invoice_date: "2025-01-31",
    gross_amount: 7000.0,
    tax_year: TAX_YEAR,
  });
  console.log("Invoice result:", invoice);

  // Step 2: Record an expense
  step(2, "Expense recording (broadband)");
  const expense = await post("/expenses/ingest", {
    vendor: "Eir",
    expense_date: "2025-01-10",
    amount: 49.99,
    category: "PHONE",
    description: "Monthly broadband — business proportion",
    tax_year: TAX_YEAR,
    vat_amount: 9.57,
  });
  console.log("Expense result:", expense);

  // Step 3: Mileage — Enniskerry to Rathdrum
  step(3, "Mileage: Enniskerry → Rathdrum (AVASO-reimbursed)");
  const mileage = await post("/mileage/record", {
    trip_date: "2025-01-15",
    origin: "Enniskerry, Co. Wicklow",
    destination: "Rathdrum, Co. Wicklow",
    distance_km: 65.0,
    tax_year: TAX_YEAR,
    round_trip: true,
    reimbursed_by_client: true,
  });
  console.log("Mileage result:", mileage);

  // Step 4: Tax calculation
  step(4, "Tax calculation (YTD position)");
  const taxResult = await post("/tax/calculate", {
    gross_income: 42000.0,
    allowable_expenses: 3200.0,
    mileage_deduction: 500.0,
    tax_year: TAX_YEAR,
  });
  console.log("Tax position:");
  console.log("  Net profit:      €" + taxResult.net_profit);
  console.log("  Total liability: €" + taxResult.total_liability);
  console.log("  Disclaimer:", taxResult.disclaimer?.slice(0, 80) + "...");

  // Step 5: Summaries
  step(5, "YTD summaries");
  const [incomeSummary, expenseSummary, mileageSummary] = await Promise.all([
    get(`/income/summary?tax_year=${TAX_YEAR}`),
    get(`/expenses/summary?tax_year=${TAX_YEAR}`),
    get(`/mileage/summary?tax_year=${TAX_YEAR}`),
  ]);
  console.log("Income YTD:  €" + incomeSummary.total_income);
  console.log("Expenses YTD: €" + expenseSummary.total_allowable_expenses);
  console.log("Mileage YTD: €" + mileageSummary.total_deductible_mileage);

  console.log("\n✅  Demo complete.\n");
  console.log("⚠️  All outputs are educational estimates only. Not tax advice.");
}

main().catch((err) => {
  console.error("Demo failed:", err.message);
  process.exit(1);
});
