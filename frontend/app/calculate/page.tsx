"use client";
import { useState } from "react";
import { api, TaxCalcPayload } from "@/lib/api";
import Link from "next/link";

export default function CalculatePage() {
  const [formData, setFormData] = useState<TaxCalcPayload>({
    gross_income: 0, allowable_expenses: 0, mileage_deduction: 0, tax_year: new Date().getFullYear()
  });
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  const handleCalculate = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      const data = await api.calculateTax(formData);
      setResult(data);
    } catch (e) {
      alert("Error calculating tax");
    }
    setLoading(false);
  };

  const autoFillFromSummary = async () => {
    setLoading(true);
    try {
      const [income, expenses, mileage] = await Promise.all([
        api.getIncomeSummary(formData.tax_year).catch(() => null),
        api.getExpensesSummary(formData.tax_year).catch(() => null),
        api.getMileageSummary(formData.tax_year).catch(() => null),
      ]);
      setFormData(prev => ({
        ...prev,
        gross_income: income?.total_income ?? 0,
        allowable_expenses: expenses?.total_allowable_expenses ?? 0,
        mileage_deduction: mileage?.total_deductible_mileage ?? 0,
      }));
    } catch (e) {
      console.error(e);
    }
    setLoading(false);
  };

  return (
    <div className="max-w-4xl mx-auto">
      <div className="mb-6 flex items-center justify-between">
        <h1 className="text-2xl font-normal">Calculate Tax</h1>
        <Link href="/" className="text-black hover:underline">← Back to Dashboard</Link>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        <div className="card">
          <div className="card-header flex justify-between items-center">
            <h2 className="text-lg font-semibold text-slate-800">Inputs</h2>
            <button type="button" onClick={autoFillFromSummary} className="btn-secondary">Auto-fill from YTD</button>
          </div>
          <form onSubmit={handleCalculate} className="space-y-4">
            <div><label className="form-label">Tax Year</label>
            <input type="number" required className="form-input" value={formData.tax_year} onChange={e => setFormData({...formData, tax_year: Number(e.target.value)})} /></div>
            <div><label className="form-label">Gross Income (€)</label>
            <input type="number" step="0.01" required className="form-input" value={formData.gross_income} onChange={e => setFormData({...formData, gross_income: parseFloat(e.target.value)})} /></div>
            <div><label className="form-label">Allowable Expenses (€)</label>
            <input type="number" step="0.01" required className="form-input" value={formData.allowable_expenses} onChange={e => setFormData({...formData, allowable_expenses: parseFloat(e.target.value)})} /></div>
            <div><label className="form-label">Mileage Deduction (€)</label>
            <input type="number" step="0.01" required className="form-input" value={formData.mileage_deduction} onChange={e => setFormData({...formData, mileage_deduction: parseFloat(e.target.value)})} /></div>
            
            <button type="submit" disabled={loading} className="w-full btn-primary mt-6">
              {loading ? "Calculating..." : "Calculate Estimate"}
            </button>
          </form>
        </div>

        <div className="card">
          <h2 className="text-lg font-normal mb-4">Results</h2>
          {result ? (
            <div className="bg-gray-50 p-4 rounded text-sm overflow-auto max-h-[500px]">
              <pre>{JSON.stringify(result, null, 2)}</pre>
            </div>
          ) : <p className="text-gray-500">Run a calculation to see estimates.</p>}
        </div>
      </div>
    </div>
  );
}
