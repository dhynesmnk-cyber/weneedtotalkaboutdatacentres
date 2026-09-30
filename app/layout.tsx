// app/layout.tsx — site chrome: skip link, primary nav (fact layer),
// editorial section clearly separated, footer with methodology links.
import type { Metadata } from "next";
import "./globals.css";
import Link from "next/link";
import { dataSourceLabel } from "@/lib/db";

export const metadata: Metadata = {
  title: {
    default: "Australian AI Data Centre Observatory",
    template: "%s | AI Data Centre Observatory",
  },
  description:
    "A public data observatory tracking Australian AI data centres — sites, events, capacity and finances — with every figure linked to its source.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en-AU">
      <body className="font-sans antialiased" style={{ background: "var(--paper)" }}>
        <a href="#main" className="skip-link">
          Skip to main content
        </a>
        <header className="border-b" style={{ borderColor: "var(--line)", background: "var(--card)" }}>
          <div className="mx-auto max-w-6xl px-4 py-3 flex flex-wrap items-center gap-x-6 gap-y-2">
            <Link href="/" className="text-lg font-bold" style={{ color: "var(--fact-accent)" }}>
              AI Data Centre Observatory
            </Link>
            <nav aria-label="Primary" className="flex gap-5 text-sm font-medium" style={{ color: "var(--ink-700)" }}>
              <Link href="/timeline">Timeline</Link>
              <Link href="/map">Map</Link>
              <Link href="/sites">Sites</Link>
              <Link href="/check-your-area">Check your area</Link>
              <Link href="/about">About &amp; method</Link>
            </nav>
            <span className="ml-auto text-xs uppercase tracking-wide" style={{ color: "var(--editorial-accent)" }}>
              <Link href="/essays">Video essays (opinion)</Link>
            </span>
          </div>
        </header>
        <main id="main" className="mx-auto max-w-6xl px-4 py-8">
          {children}
        </main>
        <footer className="border-t mt-16" style={{ borderColor: "var(--line)" }}>
          <div className="mx-auto max-w-6xl px-4 py-6 text-sm flex flex-wrap gap-x-6 gap-y-2" style={{ color: "var(--ink-500)" }}>
            <span>Data source: {dataSourceLabel()}</span>
            <Link href="/about#method">Methodology</Link>
            <Link href="/about#corrections">Corrections</Link>
            <Link href="/about#gaps">How we handle missing data</Link>
            <span className="ml-auto">Public data, dated records, cited sources.</span>
          </div>
        </footer>
      </body>
    </html>
  );
}
