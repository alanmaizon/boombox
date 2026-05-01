"use client";
import { useState, useEffect } from "react";
import { api, IncomeIngestionPayload } from "@/lib/api";
import Link from "next/link";

export default function IncomePage() {
  const [taxYear, setTaxYear] = useState(new Date().getFullYear());
  const [summary, setSummary] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState<IncomeIngestionPayload>({
    invoice_number: "", source: "OTHER", client_name: "", invoice_date: "", gross_amount: 0, tax_year: new Date().getFullYear()
  });

  const loadSummary = async () => {
    setLoading(true);
    try {
      const data = await api.getIncomeSummary(taxYear);
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
      await api.ingestInvoice(formData);
      alert("Invoice recorded successfully!");
      loadSummary();
    } catch (e) {
      alert("Error recording invoice");
    }
  };

  return (
    <div className="max-w-4xl mx-auto">
      <div className="mb-6 flex items-center justify-between">
        <h1 className="text-2xl font-normal">Income</h1>
        <Link href="/" className="text-black hover:underline">← Back to Dashboard</Link>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        <div className="card">
          <h2 className="text-lg font-normal mb-4">Record Invoice</h2>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div><label className="form-label">Invoice Number</label>
            <input type="text" required className="form-input" onChange={e => setFormData({...formData, invoice_number: e.target.value})} /></div>
            <div><label className="form-label">Client Name</label>
            <input type="text" required className="form-input" onChange={e => setFormData({...formData, client_name: e.target.value})} /></div>
            <div><label className="form-label">Invoice Date</label>
            <input type="date" required className="form-input" onChange={e => setFormData({...formData, invoice_date: e.target.value})} /></div>
            <div><label className="form-label">Gross Amount (€)</label>
            <input type="number" step="0.01" required className="form-input" onChange={e => setFormData({...formData, gross_amount: parseFloat(e.target.value)})} /></div>
            <div><label className="form-label">Source</label>
            <select className="form-input" onChange={e => setFormData({...formData, source: e.target.value as any})}>
              <option value="OTHER">Other</option>
              <option value="AVASO">Avaso</option>
            </select></div>
            <button type="submit" className="w-full btn-primary">Submit Invoice</button>
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
