"use client";
import { useState, useEffect } from "react";
import { api, ExpenseIngestionPayload } from "@/lib/api";
import Link from "next/link";

export default function ExpensesPage() {
  const [taxYear, setTaxYear] = useState(new Date().getFullYear());
  const [summary, setSummary] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState<ExpenseIngestionPayload>({
    vendor: "", expense_date: "", amount: 0, category: "OFFICE_SUPPLIES", description: "", tax_year: new Date().getFullYear(), vat_amount: 0
  });

  const loadSummary = async () => {
    setLoading(true);
    try {
      const data = await api.getExpensesSummary(taxYear);
      setSummary(data);
    } catch (e) {
      console.error(e);
    }
    setLoading(false);
  };

  useEffect(() => { loadSummary(); }, [taxYear]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await api.ingestExpense(formData);
      alert("Expense recorded successfully!");
      loadSummary();
    } catch (e) {
      alert("Error recording expense");
    }
  };

  return (
    <div className="max-w-4xl mx-auto">
      <div className="mb-6 flex items-center justify-between">
        <h1 className="text-2xl font-normal">Expenses</h1>
        <Link href="/" className="text-black hover:underline">← Back to Dashboard</Link>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        <div className="card">
          <h2 className="text-lg font-normal mb-4">Log Expense</h2>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div><label className="form-label">Vendor</label>
            <input type="text" required className="form-input" onChange={e => setFormData({...formData, vendor: e.target.value})} /></div>
            <div><label className="form-label">Date</label>
            <input type="date" required className="form-input" onChange={e => setFormData({...formData, expense_date: e.target.value})} /></div>
            <div><label className="form-label">Gross Amount (€)</label>
            <input type="number" step="0.01" required className="form-input" onChange={e => setFormData({...formData, amount: parseFloat(e.target.value)})} /></div>
            <div><label className="form-label">Description</label>
            <input type="text" required className="form-input" onChange={e => setFormData({...formData, description: e.target.value})} /></div>
            <div><label className="form-label">Category</label>
            <select className="form-input" onChange={e => setFormData({...formData, category: e.target.value})}>
              <option value="OFFICE_SUPPLIES">Office Supplies</option>
              <option value="SOFTWARE_SUBSCRIPTIONS">Software</option>
              <option value="TRAVEL">Travel</option>
              <option value="MEALS">Meals</option>
              <option value="OTHER">Other</option>
            </select></div>
            <button type="submit" className="w-full btn-primary">Submit Expense</button>
          </form>
        </div>

        <div className="card">
          <h2 className="text-lg font-normal mb-4">YTD Summary</h2>
          <div className="mb-4">
            <label className="form-label">Tax Year</label>
            <input type="number" value={taxYear} onChange={e => setTaxYear(Number(e.target.value))} className="form-input" />
          </div>
          {loading ? <p>Loading...</p> : summary ? (
            <div className="bg-gray-50 p-6 text-xs overflow-auto font-mono text-gray-600">
              <pre>{JSON.stringify(summary, null, 2)}</pre>
            </div>
          ) : <p className="text-gray-500">No data found.</p>}
        </div>
      </div>
    </div>
  );
}
