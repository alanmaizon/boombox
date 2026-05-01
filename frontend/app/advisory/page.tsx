"use client";
import { useState } from "react";
import Link from "next/link";
import { api, AdvisoryResponse } from "@/lib/api";

const eur = (n: number) =>
  new Intl.NumberFormat("en-IE", {
    style: "currency",
    currency: "EUR",
    minimumFractionDigits: 2,
  }).format(n);

type ChatTurn =
  | { role: "user"; question: string }
  | { role: "assistant"; response: AdvisoryResponse }
  | { role: "error"; message: string };

export default function AdvisoryPage() {
  const [taxYear, setTaxYear] = useState<number>(new Date().getFullYear());
  const [question, setQuestion] = useState<string>("");
  const [additionalIncome, setAdditionalIncome] = useState<number>(0);
  const [additionalExpense, setAdditionalExpense] = useState<number>(0);
  const [additionalMileageKm, setAdditionalMileageKm] = useState<number>(0);
  const [reimbursed, setReimbursed] = useState<boolean>(false);
  const [turns, setTurns] = useState<ChatTurn[]>([]);
  const [loading, setLoading] = useState(false);

  const handleAsk = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!question.trim()) return;
    const q = question;
    setTurns((t) => [...t, { role: "user", question: q }]);
    setQuestion("");
    setLoading(true);
    try {
      const data = await api.askAdvisory({
        tax_year: taxYear,
        question: q,
        additional_income: additionalIncome,
        additional_expense: additionalExpense,
        additional_mileage_km: additionalMileageKm,
        mileage_round_trip: true,
        mileage_reimbursed: reimbursed,
      });
      setTurns((t) => [...t, { role: "assistant", response: data }]);
    } catch (err) {
      setTurns((t) => [
        ...t,
        {
          role: "error",
          message: err instanceof Error ? err.message : "Request failed",
        },
      ]);
    }
    setLoading(false);
  };

  return (
    <div className="max-w-5xl mx-auto">
      <div className="mb-6 flex items-center justify-between">
        <h1 className="text-2xl font-normal">Advisory — What-If Scenarios</h1>
        <Link href="/" className="text-black hover:underline">
          ← Back to Dashboard
        </Link>
      </div>

      <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-3 mb-6 text-xs text-yellow-900">
        <strong>⚠️ NOT tax advice.</strong> Each answer is an educational
        simulation based on Finance Act 2025 / Budget 2026 rates. Every numeric
        claim is grounded in published Revenue / Citizens Information sources
        and includes citations. Consult a registered tax adviser (AITI/CTA) for
        advice specific to your situation.
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <aside className="lg:col-span-1 bg-white p-4 rounded-lg shadow border h-fit">
          <h2 className="font-semibold mb-3">Scenario deltas</h2>
          <div className="space-y-3 text-sm">
            <div>
              <label className="block font-medium">Tax Year</label>
              <input
                type="number"
                min={2020}
                max={2100}
                className="mt-1 w-full border rounded p-2"
                value={taxYear}
                onChange={(e) => setTaxYear(Number(e.target.value))}
              />
            </div>
            <div>
              <label className="block font-medium">Additional income (€)</label>
              <input
                type="number"
                step="0.01"
                min={0}
                className="mt-1 w-full border rounded p-2"
                value={additionalIncome}
                onChange={(e) =>
                  setAdditionalIncome(parseFloat(e.target.value) || 0)
                }
              />
            </div>
            <div>
              <label className="block font-medium">
                Additional allowable expense (€)
              </label>
              <input
                type="number"
                step="0.01"
                min={0}
                className="mt-1 w-full border rounded p-2"
                value={additionalExpense}
                onChange={(e) =>
                  setAdditionalExpense(parseFloat(e.target.value) || 0)
                }
              />
            </div>
            <div>
              <label className="block font-medium">
                Additional mileage (one-way km)
              </label>
              <input
                type="number"
                step="0.1"
                min={0}
                className="mt-1 w-full border rounded p-2"
                value={additionalMileageKm}
                onChange={(e) =>
                  setAdditionalMileageKm(parseFloat(e.target.value) || 0)
                }
              />
            </div>
            <label className="flex items-center gap-2">
              <input
                type="checkbox"
                checked={reimbursed}
                onChange={(e) => setReimbursed(e.target.checked)}
              />
              <span>Trip reimbursed by AVASO (≥40 km RT)</span>
            </label>
          </div>
        </aside>

        <section className="lg:col-span-2 bg-white p-4 rounded-lg shadow border flex flex-col min-h-[500px]">
          <div className="flex-1 overflow-auto space-y-4 mb-4">
            {turns.length === 0 && (
              <div className="text-gray-500 text-sm">
                Ask a what-if question. Try: <em>&quot;If I take an extra
                €5,000 contract, what&apos;s my net retention?&quot;</em> Set
                deltas in the sidebar so the simulator can quantify the change.
              </div>
            )}
            {turns.map((t, i) =>
              t.role === "user" ? (
                <div key={i} className="flex justify-end">
                  <div className="bg-blue-600 text-white rounded-lg px-4 py-2 max-w-[80%]">
                    {t.question}
                  </div>
                </div>
              ) : t.role === "error" ? (
                <div key={i} className="bg-red-50 border border-red-300 rounded p-3 text-sm text-red-800">
                  {t.message}
                </div>
              ) : (
                <AssistantTurn key={i} response={t.response} />
              ),
            )}
          </div>

          <form onSubmit={handleAsk} className="border-t pt-3 flex gap-2">
            <input
              type="text"
              placeholder="Ask a what-if question…"
              className="flex-1 border rounded p-2"
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              disabled={loading}
            />
            <button
              type="submit"
              disabled={loading || !question.trim()}
              className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 disabled:bg-gray-400"
            >
              {loading ? "Thinking…" : "Ask"}
            </button>
          </form>
        </section>
      </div>
    </div>
  );
}

function AssistantTurn({ response }: { response: AdvisoryResponse }) {
  return (
    <div className="bg-gray-50 border rounded-lg p-4">
      <p className="text-sm text-gray-900 whitespace-pre-wrap">
        {response.answer}
      </p>

      {(response.delta.total_liability !== 0 ||
        response.delta.net_profit !== 0) && (
        <div className="grid grid-cols-3 gap-3 mt-3 text-xs">
          <Stat
            label="Baseline liability"
            value={eur(response.baseline.total_liability)}
          />
          <Stat
            label="Scenario liability"
            value={eur(response.scenario.total_liability)}
          />
          <Stat
            label="Δ liability"
            value={eur(response.delta.total_liability)}
            accent={response.delta.total_liability > 0 ? "red" : "green"}
          />
        </div>
      )}

      {response.caveats.length > 0 && (
        <div className="mt-3 bg-orange-50 border border-orange-200 rounded p-2 text-xs text-orange-900">
          <strong>Caveats:</strong>
          <ul className="list-disc ml-5 mt-1">
            {response.caveats.map((c, i) => (
              <li key={i}>{c}</li>
            ))}
          </ul>
        </div>
      )}

      <details className="mt-3 text-xs">
        <summary className="cursor-pointer text-gray-600">
          Citations ({response.citations.length})
        </summary>
        <ul className="mt-2 space-y-1">
          {response.citations.map((c, i) => {
            const urlMatch = c.match(/(https?:\/\/\S+)/);
            const url = urlMatch ? urlMatch[1] : null;
            const label = url ? c.replace(url, "").trim().replace(/:$/, "") : c;
            return (
              <li key={i} className="text-gray-700">
                {label}
                {url && (
                  <>
                    {" "}
                    <a
                      href={url}
                      target="_blank"
                      rel="noreferrer"
                      className="text-black hover:underline"
                    >
                      source
                    </a>
                  </>
                )}
              </li>
            );
          })}
        </ul>
      </details>

      <div className="mt-3 text-[11px] text-gray-500 italic">
        {response.disclaimer}
      </div>
    </div>
  );
}

function Stat({
  label,
  value,
  accent,
}: {
  label: string;
  value: string;
  accent?: "red" | "green";
}) {
  const color =
    accent === "red"
      ? "text-red-700"
      : accent === "green"
        ? "text-green-700"
        : "text-gray-900";
  return (
    <div className="bg-white border rounded p-2">
      <div className="text-gray-500">{label}</div>
      <div className={`font-mono font-semibold ${color}`}>{value}</div>
    </div>
  );
}
