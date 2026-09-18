import type { Metadata } from 'next';
import Link from 'next/link';
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

const NAV = [
  { href: '/', label: 'Timeline' },
  { href: '/essays', label: 'Essays' },
  { href: '/map', label: 'Map' },
  { href: '/list', label: 'Sites and entities' },
] as const;

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

            <nav aria-label="Primary" className="mt-3">
              <ul className="flex flex-wrap gap-x-5 gap-y-1 text-sm">
                {NAV.map((item) => (
                  <li key={item.href}>
                    <Link
                      href={item.href}
                      className="rounded text-slate-700 underline-offset-4 hover:underline"
                    >
                      {item.label}
                    </Link>
                  </li>
                ))}
              </ul>
            </nav>
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
          </div>
        </footer>
      </body>
    </html>
  );
}
