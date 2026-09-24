import type { Metadata } from 'next';
import Link from 'next/link';
import { PrimaryNav } from '@/components/PrimaryNav';
import './globals.css';

export const metadata: Metadata = {
  title: {
    default: 'Australian AI Data Centre Observatory',
    template: '%s · AI Data Centre Observatory',
  },
  description:
    'A public record of Australian AI data centre sites, the entities behind '
    + 'them, and what is known and not known about each.',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en-AU">
      <body className="min-h-screen bg-white">
        <a href="#main" className="skip-link">
          Skip to main content
        </a>

        <header className="border-b border-slate-200">
          <div className="mx-auto max-w-5xl px-4 py-4">
            <Link href="/" className="text-lg font-semibold text-fact-ink">
              Australian AI Data Centre Observatory
            </Link>

            <PrimaryNav />
          </div>
        </header>

        <main id="main" className="mx-auto max-w-5xl px-4 py-8">
          {children}
        </main>

        <footer className="mt-16 border-t border-slate-200">
          <div className="mx-auto max-w-5xl px-4 py-6 text-sm text-slate-600">
            <p>
              Every factual claim on this site references a source record.
              Missing values are marked as gaps, never estimated.
            </p>
            <p className="mt-2">
              <Link href="/how-to-read" className="text-fact-ink underline underline-offset-2">
                How to read this site
              </Link>
            </p>
          </div>
        </footer>
      </body>
    </html>
  );
}
