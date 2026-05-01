import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Boombox — Irish Sole Trader Tax Operations",
  description:
    "Educational tax-operations tool for Irish sole traders. Not tax advice.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>
        <header className="bg-yellow-50 border-b border-yellow-200 px-4 py-3">
          <p className="text-sm text-yellow-800 font-medium text-center">
            ⚠️ <strong>Disclaimer:</strong> Boombox is an educational and
            organisational tool. It does <strong>not</strong> provide tax advice
            and does <strong>not</strong> file anything with Revenue. Always
            consult a registered tax adviser (AITI/CTA) for complex matters.
          </p>
        </header>
        <main className="min-h-screen p-8">{children}</main>
        <footer className="border-t px-4 py-4 text-center text-xs text-gray-500">
          Boombox — educational tool only. Not tax advice. Finance Act 2025 / Budget 2026.
        </footer>
      </body>
    </html>
  );
}
