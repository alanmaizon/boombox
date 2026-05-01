"use client";
import { useState, useEffect } from "react";
import { api, MileageRecordPayload } from "@/lib/api";
import Link from "next/link";

export default function MileagePage() {
  const [taxYear, setTaxYear] = useState(new Date().getFullYear());
  const [summary, setSummary] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState<MileageRecordPayload>({
    trip_date: "", origin: "", destination: "", distance_km: 0, tax_year: new Date().getFullYear(), round_trip: true, reimbursed_by_client: false
  });

  const loadSummary = async () => {
    setLoading(true);
    try {
      const data = await api.getMileageSummary(taxYear);
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
      await api.recordMileage(formData);
      alert("Mileage recorded successfully!");
      loadSummary();
    } catch (e) {
      alert("Error recording mileage");
    }
  };

  return (
    <div className="max-w-4xl mx-auto">
      <div className="mb-6 flex items-center justify-between">
        <h1 className="text-2xl font-normal">Mileage</h1>
        <Link href="/" className="text-black hover:underline">← Back to Dashboard</Link>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        <div className="card">
          <h2 className="text-lg font-normal mb-4">Record Trip</h2>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div><label className="form-label">Date</label>
            <input type="date" required className="form-input" onChange={e => setFormData({...formData, trip_date: e.target.value})} /></div>
            <div className="flex gap-4">
              <div className="w-1/2"><label className="form-label">Origin</label>
              <input type="text" required className="form-input" onChange={e => setFormData({...formData, origin: e.target.value})} /></div>
              <div className="w-1/2"><label className="form-label">Destination</label>
              <input type="text" required className="form-input" onChange={e => setFormData({...formData, destination: e.target.value})} /></div>
            </div>
            <div><label className="form-label">Distance (km)</label>
            <input type="number" step="0.1" required className="form-input" onChange={e => setFormData({...formData, distance_km: parseFloat(e.target.value)})} /></div>
            
            <div className="flex items-center gap-4 mt-4">
              <label className="flex items-center space-x-2">
                <input type="checkbox" checked={formData.round_trip} onChange={e => setFormData({...formData, round_trip: e.target.checked})} className="rounded text-black" />
                <span className="text-sm">Round Trip</span>
              </label>
              <label className="flex items-center space-x-2">
                <input type="checkbox" checked={formData.reimbursed_by_client} onChange={e => setFormData({...formData, reimbursed_by_client: e.target.checked})} className="rounded text-black" />
                <span className="text-sm">Reimbursed by Client</span>
              </label>
            </div>

            <button type="submit" className="w-full btn-primary">Submit Mileage</button>
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
