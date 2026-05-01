const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL ?? "http://localhost:8000";

export type IncomeIngestionPayload = {
  invoice_number: string;
  source: "AVASO" | "OTHER";
  client_name: string;
  invoice_date: string;
  gross_amount: number;
  tax_year: number;
  due_date?: string;
  payment_date?: string;
};

export type ExpenseIngestionPayload = {
  vendor: string;
  expense_date: string;
  amount: number;
  category: string;
  description: string;
  tax_year: number;
  vat_amount?: number;
  receipt_ref?: string;
};

export type MileageRecordPayload = {
  trip_date: string;
  origin: string;
  destination: string;
  distance_km: number;
  tax_year: number;
  round_trip?: boolean;
  reimbursed_by_client?: boolean;
};

export type TaxCalcPayload = {
  gross_income: number;
  allowable_expenses: number;
  mileage_deduction: number;
  tax_year: number;
};

async function apiPost<T>(path: string, body: unknown): Promise<T> {
  const res = await fetch(`${BACKEND_URL}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error((err as { detail: string }).detail ?? res.statusText);
  }
  return res.json() as Promise<T>;
}

async function apiGet<T>(path: string): Promise<T> {
  const res = await fetch(`${BACKEND_URL}${path}`);
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error((err as { detail: string }).detail ?? res.statusText);
  }
  return res.json() as Promise<T>;
}

export const api = {
  ingestInvoice: (payload: IncomeIngestionPayload) =>
    apiPost("/income/ingest", payload),

  getIncomeSummary: (taxYear: number) =>
    apiGet(`/income/summary?tax_year=${taxYear}`),

  ingestExpense: (payload: ExpenseIngestionPayload) =>
    apiPost("/expenses/ingest", payload),

  getExpensesSummary: (taxYear: number) =>
    apiGet(`/expenses/summary?tax_year=${taxYear}`),

  recordMileage: (payload: MileageRecordPayload) =>
    apiPost("/mileage/record", payload),

  getMileageSummary: (taxYear: number) =>
    apiGet(`/mileage/summary?tax_year=${taxYear}`),

  calculateTax: (payload: TaxCalcPayload) =>
    apiPost("/tax/calculate", payload),

  getHealth: () => apiGet("/health"),
};
