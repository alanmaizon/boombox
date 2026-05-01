export default function Home() {
  return (
    <div className="max-w-4xl mx-auto">
      <h1 className="text-3xl font-bold mb-2">Boombox</h1>
      <p className="text-gray-600 mb-8">
        Irish sole-trader tax operations — income, expenses, mileage,
        calculations.
      </p>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
        <a
          href="/income"
          className="block p-6 border rounded-lg hover:bg-gray-50 transition-colors"
        >
          <h2 className="text-xl font-semibold mb-2">💰 Income</h2>
          <p className="text-gray-600 text-sm">
            Record invoices, view YTD income totals
          </p>
        </a>
        <a
          href="/expenses"
          className="block p-6 border rounded-lg hover:bg-gray-50 transition-colors"
        >
          <h2 className="text-xl font-semibold mb-2">🧾 Expenses</h2>
          <p className="text-gray-600 text-sm">
            Log receipts, categorise, track deductible spend
          </p>
        </a>
        <a
          href="/mileage"
          className="block p-6 border rounded-lg hover:bg-gray-50 transition-colors"
        >
          <h2 className="text-xl font-semibold mb-2">🚗 Mileage</h2>
          <p className="text-gray-600 text-sm">
            Record trips, separate reimbursed vs deductible
          </p>
        </a>
        <a
          href="/calculate"
          className="block p-6 border rounded-lg hover:bg-gray-50 transition-colors"
        >
          <h2 className="text-xl font-semibold mb-2">🧮 Calculate</h2>
          <p className="text-gray-600 text-sm">
            Income Tax + USC + PRSI estimate
          </p>
        </a>
        <a
          href="/filing"
          className="block p-6 border rounded-lg hover:bg-gray-50 transition-colors"
        >
          <h2 className="text-xl font-semibold mb-2">📄 Filing</h2>
          <p className="text-gray-600 text-sm">
            Draft Form 11 line items for review
          </p>
        </a>
        <a
          href="/advisory"
          className="block p-6 border rounded-lg hover:bg-gray-50 transition-colors"
        >
          <h2 className="text-xl font-semibold mb-2">💡 Advisory</h2>
          <p className="text-gray-600 text-sm">
            What-if scenarios with cited sources
          </p>
        </a>
      </div>

      <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 text-sm text-yellow-800">
        <strong>⚠️ Important:</strong> Boombox is an educational and
        organisational tool. All tax estimates are indicative only, based on
        Finance Act 2025 / Budget 2026 rates. They do not constitute tax advice.
        Always consult a registered tax adviser (AITI/CTA) before making
        financial or filing decisions. Boombox never files anything with Revenue
        on your behalf.
      </div>
    </div>
  );
}
