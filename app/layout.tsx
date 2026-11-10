import type { Metadata, Viewport } from 'next';
import Link from 'next/link';
import { PrimaryNav } from '@/components/PrimaryNav';
import { SITE_DESCRIPTION, SITE_NAME, SITE_STRAPLINE, siteUrl } from '@/lib/site';
import { mono, sans, serif } from './fonts';
import './globals.css';

export const metadata: Metadata = {
  metadataBase: siteUrl(),
  title: {
    default: SITE_NAME,
    template: `%s · ${SITE_NAME}`,
  },
  description: SITE_DESCRIPTION,
  openGraph: {
    siteName: SITE_NAME,
    locale: 'en_AU',
    type: 'website',
  },
};

export const viewport: Viewport = {
  themeColor: [
    { media: '(prefers-color-scheme: light)', color: '#ffffff' },
    { media: '(prefers-color-scheme: dark)', color: '#0d1420' },
  ],
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en-AU" className={`${serif.variable} ${sans.variable} ${mono.variable}`}>
      <body className="min-h-screen">
        <a href="#main" className="skip-link">
          Skip to main content
        </a>

        <header data-site-header className="border-b border-slate-200">
          <div className="mx-auto max-w-6xl px-4 pb-3 pt-5">
            <Link href="/" className="group inline-block rounded">
              <span className="block font-serif text-2xl font-semibold leading-tight tracking-tight text-slate-900 group-hover:underline group-hover:decoration-2 group-hover:underline-offset-4 sm:text-3xl">
                {SITE_NAME}
              </span>
              <span className="mt-1 block text-sm text-slate-600">{SITE_STRAPLINE}</span>
            </Link>
            <div className="mt-4 border-t border-slate-200 pt-3">
              <PrimaryNav />
            </div>
          </div>
        </header>

        <main id="main" className="mx-auto max-w-6xl px-4 py-8 md:py-10">
          {children}
        </main>

        <footer data-site-footer className="mt-16 border-t border-slate-200">
          <div className="mx-auto grid max-w-6xl gap-6 px-4 py-8 text-sm text-slate-700 md:grid-cols-[2fr_1fr]">
            <div>
              <p className="font-serif text-lg font-semibold text-slate-900">{SITE_NAME}</p>
              <p className="mt-2 max-w-xl">
                Every factual claim on this site references a source record.
                Missing values are marked as gaps, never estimated. Essays are
                argument, kept apart from the record and labelled as such.
              </p>
            </div>
            <nav aria-label="About this site">
              <ul className="space-y-2">
                <li>
                  <Link href="/how-to-read" className="link">
                    How to read this site
                  </Link>
                </li>
                <li>
                  <Link href="/coverage" className="link">
                    What the record holds
                  </Link>
                </li>
                <li>
                  <Link href="/research" className="link">
                    What it does not yet know
                  </Link>
                </li>
              </ul>
            </nav>
          </div>
        </footer>
      </body>
    </html>
  );
}
