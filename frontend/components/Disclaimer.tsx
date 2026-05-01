interface DisclaimerProps {
  variant?: "banner" | "inline";
}

export function Disclaimer({ variant = "inline" }: DisclaimerProps) {
  if (variant === "banner") {
    return (
      <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 text-sm text-yellow-800 mb-6">
        <p>
          <strong>⚠️ Not tax advice.</strong> Boombox is an educational and
          organisational tool. All estimates are indicative only, based on
          Finance Act 2025 / Budget 2026 rates. Always consult a registered tax
          adviser (AITI/CTA) before making financial or filing decisions.
          Boombox never files anything with Revenue on your behalf.
        </p>
      </div>
    );
  }

  return (
    <p className="text-xs text-gray-500 mt-2">
      ⚠️ Educational estimate only. Not tax advice. Consult a registered tax
      adviser (AITI/CTA).
    </p>
  );
}
