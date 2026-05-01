"use client";
import { useState } from "react";
import Link from "next/link";
import { api, FilingDraftResponse } from "@/lib/api";

const eur = (n: number) =>
  new Intl.NumberFormat("en-IE", {
    style: "currency",
    currency: "EUR",
    minimumFractionDigits: 2,
  }).format(n);

export default function FilingPage() {
  const [taxYear, setTaxYear] = useState<number>(new Date().getFullYear());
  const [preliminaryTaxPaid, setPreliminaryTaxPaid] = useState<number>(0);
  const [draft, setDraft] = useState<FilingDraftResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleDraft = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setDraft(null);
    try {
      const data = await api.draftFiling({
        tax_year: taxYear,
        preliminary_tax_paid: preliminaryTaxPaid,
      });
      setDraft(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to draft Form 11");
    }
    setLoading(false);
  };

  const groupedByPanel = draft?.lines.reduce<Record<string, typeof draft.lines>>(
    (acc, line) => {
      (acc[line.panel] ||= []).push(line);
      return acc;
    },
    {},
  );

  return (
    <div className="max-w-5xl mx-auto">
      <div className="mb-6 flex items-center justify-between">
        <h1 className="text-2xl font-normal">Filing — Draft Form 11</h1>
        <Link href="/" className="text-black hover:underline">
          ← Back to Dashboard
        </Link>
      </div>

      <div className="bg-red-50 border-2 border-red-300 rounded-lg p-4 mb-6 text-sm text-red-900">
        <strong>⚠️ DRAFT ONLY:</strong> Boombox <strong>never</strong> submits to
        ROS or files anything with Revenue. Field references are indicative —
        verify against the current Form 11 before filing. Always review with a
        registered tax adviser (AITI/CTA).
      </div>

      <form
        onSubmit={handleDraft}
        className="bg-white p-6 rounded-lg shadow border mb-6 grid grid-cols-1 md:grid-cols-3 gap-4 items-end"
      >
        <div>
          <label className="block text-sm font-medium">Tax Year</label>
          <input
            type="number"
            required
            min={2020}
            max={2100}
            className="mt-1 w-full border rounded p-2"
            value={taxYear}
            onChange={(e) => setTaxYear(Number(e.target.value))}
          />
        </div>
        <div>
          <label className="block text-sm font-medium">
            Preliminary Tax Paid (€)
          </label>
          <input
            type="number"
            step="0.01"
            min={0}
            className="mt-1 w-full border rounded p-2"
            value={preliminaryTaxPaid}
            onChange={(e) =>
              setPreliminaryTaxPaid(parseFloat(e.target.value) || 0)
            }
          />
        </div>
        <button
          type="submit"
          disabled={loading}
          className="bg-blue-600 text-white py-2 rounded hover:bg-blue-700 disabled:bg-gray-400"
        >
          {loading ? "Drafting…" : "Generate Draft Form 11"}
        </button>
      </form>

      {error && (
        <div className="bg-red-50 border border-red-300 rounded p-3 mb-4 text-sm text-red-800">
          {error}
        </div>
      )}

      {draft && (
        <div className="bg-white p-6 rounded-lg shadow border">
          <div className="flex flex-wrap gap-4 items-center justify-between mb-4">
            <div>
              <span className="inline-block bg-yellow-200 text-yellow-900 text-xs font-bold px-2 py-1 rounded mr-2">
                {draft.status}
              </span>
              <span className="text-sm text-gray-600">
                Tax year {draft.tax_year} · Filing deadline:{" "}
                <strong>{draft.filing_deadline}</strong>
              </span>
            </div>
            <div className="text-right">
              <div className="text-xs text-gray-500">Total liability estimate</div>
              <div className="text-2xl font-bold">
                {eur(draft.total_liability_estimate)}
              </div>
              <div className="text-sm text-gray-700">
                Preliminary paid: {eur(draft.preliminary_tax_paid)} · Balance
                due: <strong>{eur(draft.balance_due)}</strong>
              </div>
            </div>
          </div>

          {groupedByPanel &&
            Object.entries(groupedByPanel).map(([panel, lines]) => (
              <div key={panel} className="mb-4">
                <h3 className="font-semibold text-gray-800 border-b pb-1 mb-2">
                  {panel}
                </h3>
                <table className="w-full text-sm">
                  <thead>
                    <tr className="text-left text-gray-500">
                      <th className="py-1 w-20">Field</th>
                      <th className="py-1">Description</th>
                      <th className="py-1 text-right w-32">Value</th>
                      <th className="py-1 w-24">Source</th>
                    </tr>
                  </thead>
                  <tbody>
                    {lines.map((line, i) => (
                      <tr key={i} className="border-t">
                        <td className="py-2 font-mono text-xs">
                          {line.field_ref}
                        </td>
                        <td className="py-2">{line.description}</td>
                        <td className="py-2 text-right font-mono">
                          {eur(line.value)}
                        </td>
                        <td className="py-2">
                          {line.source && (
                            <a
                              href={line.source}
                              target="_blank"
                              rel="noreferrer"
                              className="text-black hover:underline text-xs"
                            >
                              ref
                            </a>
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ))}

          <div className="mt-6 bg-yellow-50 border border-yellow-200 rounded p-3 text-xs text-yellow-900">
            {draft.disclaimer}
          </div>
        </div>
      )}
    </div>
  );
}
