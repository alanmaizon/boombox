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

export type IncomeSummaryResponse = {
  tax_year: number;
  total_income: number;
  record_count: number;
  disclaimer?: string;
  mock?: boolean;
};

export type ExpensesSummaryResponse = {
  tax_year: number;
  total_allowable_expenses: number;
  record_count: number;
  disclaimer?: string;
  mock?: boolean;
};

export type MileageSummaryResponse = {
  tax_year: number;
  total_deductible_mileage: number;
  record_count: number;
  disclaimer?: string;
  mock?: boolean;
};

export type FilingDraftPayload = {
  tax_year: number;
  preliminary_tax_paid?: number;
};

export type Form11Line = {
  panel: string;
  field_ref: string;
  description: string;
  value: number;
  source?: string | null;
};

export type FilingDraftResponse = {
  tax_year: number;
  status: string;
  lines: Form11Line[];
  total_liability_estimate: number;
  preliminary_tax_paid: number;
  balance_due: number;
  filing_deadline: string;
  disclaimer: string;
  mock?: boolean;
};

export type AdvisoryQueryPayload = {
  tax_year: number;
  question: string;
  additional_income?: number;
  additional_expense?: number;
  additional_mileage_km?: number;
  mileage_round_trip?: boolean;
  mileage_reimbursed?: boolean;
};

export type AdvisoryFigures = {
  total_liability: number;
  net_profit: number;
  ytd_income?: number;
  ytd_expenses?: number;
  ytd_mileage_deduction?: number;
};

export type AdvisoryResponse = {
  question: string;
  answer: string;
  citations: string[];
  caveats: string[];
  baseline: AdvisoryFigures;
  scenario: AdvisoryFigures;
  delta: {
    total_liability: number;
    net_profit: number;
    net_retention?: number;
  };
  disclaimer: string;
  mock?: boolean;
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
    apiGet<IncomeSummaryResponse>(`/income/summary?tax_year=${taxYear}`),

  ingestExpense: (payload: ExpenseIngestionPayload) =>
    apiPost("/expenses/ingest", payload),

  getExpensesSummary: (taxYear: number) =>
    apiGet<ExpensesSummaryResponse>(`/expenses/summary?tax_year=${taxYear}`),

  recordMileage: (payload: MileageRecordPayload) =>
    apiPost("/mileage/record", payload),

  getMileageSummary: (taxYear: number) =>
    apiGet<MileageSummaryResponse>(`/mileage/summary?tax_year=${taxYear}`),

  calculateTax: (payload: TaxCalcPayload) =>
    apiPost("/tax/calculate", payload),

  draftFiling: (payload: FilingDraftPayload) =>
    apiPost<FilingDraftResponse>("/filing/draft", payload),

  askAdvisory: (payload: AdvisoryQueryPayload) =>
    apiPost<AdvisoryResponse>("/advisory/ask", payload),

  getHealth: () => apiGet("/health"),
};
