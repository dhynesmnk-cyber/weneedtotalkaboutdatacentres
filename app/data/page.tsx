import Link from 'next/link';
import type { Metadata } from 'next';
import { PageHeader } from '@/components/PageHeader';
import { lastLoadedAt } from '@/lib/coverage';
import { DATA_LICENCE } from '@/lib/dataExport';
import { formatDate } from '@/lib/format';
import { SITE_NAME, siteUrl } from '@/lib/site';
import { isConfigured } from '@/lib/supabase/server';

export const dynamic = 'force-dynamic';

export const metadata: Metadata = {
  title: 'Download the data',
  description: 'The record as CSV: sites, entities, sources and open questions, under CC BY 4.0.',
};

const FILES = [
  {
    file: 'sites.csv',
    title: 'Sites',
    holds:
      'Every data centre site in the record: operator, council, status, the four capacity figures, cost, jobs and dates. Each factual column has a column beside it ending in _gap, which says why the value is empty when it is.',
  },
  {
    file: 'entities.csv',
    title: 'Entities',
    holds: 'The companies, agencies, funds and bodies the record names, with their type and role.',
  },
  {
    file: 'sources.csv',
    title: 'Sources',
    holds:
      'Every document the record cites, with its publisher, type, link, the date it was read, and its credibility grade from A to D.',
  },
  {
    file: 'research.csv',
    title: 'Open questions',
    holds:
      'The research agenda: every published question the record has not yet answered, its status, and how it is to be answered.',
  },
] as const;

/**
 * The data downloads: the record as CSV, for journalists and researchers
 * (docs/DELIVERY-PLAN.md, decision 1), under CC BY 4.0 (the author's decision
 * of 2026-11-17). The files carry what the site publishes and nothing more.
 */
export default async function DataPage() {
  const asOf = isConfigured() ? await lastLoadedAt() : null;
  const asOfText = formatDate(asOf) ?? 'not yet loaded';
  const base = siteUrl().origin;

  return (
    <div className="space-y-10">
      <PageHeader layer="record" kicker="The record · Data" title="Download the data">
        <p>
          The record behind every page of this site, as four CSV files. Each row says which
          sources it rests on, and each empty value says why it is empty.
        </p>
        <p className="text-sm text-slate-600">Record as at {asOfText}.</p>
      </PageHeader>

      <section aria-labelledby="files-heading" className="max-w-measure space-y-4 text-slate-800">
        <h2 id="files-heading" className="font-serif text-2xl font-semibold text-slate-900">
          The files
        </h2>
        <ul className="space-y-4">
          {FILES.map((f) => (
            <li key={f.file}>
              <a href={`/data/${f.file}`} className="link font-semibold" download>
                {f.title} ({f.file})
              </a>
              <p className="mt-1">{f.holds}</p>
            </li>
          ))}
        </ul>
        <p>
          The <code>id</code> column is the record&rsquo;s own identifier, such as{' '}
          <code>SITE_MAMRE_ROAD</code> or <code>SRC_NSWGUIDE26</code>. The <code>sources</code>{' '}
          column lists the ids of the sources that back a row, so every row can be checked
          against <code>sources.csv</code> and from there against the document itself.
        </p>
      </section>

      <section aria-labelledby="licence-heading" className="max-w-measure space-y-4 text-slate-800">
        <h2 id="licence-heading" className="font-serif text-2xl font-semibold text-slate-900">
          Licence and how to credit it
        </h2>
        <p>
          The data is published under the{' '}
          <a href={DATA_LICENCE.url} className="link" rel="license noopener noreferrer" target="_blank">
            {DATA_LICENCE.name}
          </a>{' '}
          licence. You may copy, adapt and republish it, including commercially, as long as you
          credit it.
        </p>
        <p>Credit it as:</p>
        <blockquote className="border-l-4 border-slate-300 pl-4 text-slate-700">
          {SITE_NAME}, data as at {asOfText}, {DATA_LICENCE.short}, {base}/data
        </blockquote>
        <p>
          The licence covers this compilation. The documents the sources point to belong to
          their publishers and keep their own terms.
        </p>
      </section>

      <section aria-labelledby="reading-heading" className="max-w-measure space-y-4 text-slate-800">
        <h2 id="reading-heading" className="font-serif text-2xl font-semibold text-slate-900">
          Reading it correctly
        </h2>
        <ul className="list-disc space-y-2 pl-6">
          <li>
            <strong className="font-semibold">An empty value is not a zero.</strong> Read the
            matching <code>_gap</code> column: <code>unknown</code> means no source states it.
            Any other reason was given by a person, with a source.
          </li>
          <li>
            <strong className="font-semibold">The four capacity figures measure different things</strong>{' '}
            and are never added together. IT capacity is a design rating; live capacity is what is
            energised.
          </li>
          <li>
            <strong className="font-semibold">Grades and statuses</strong> are explained on{' '}
            <Link href="/how-to-read" className="link">
              How to read this site
            </Link>
            .
          </li>
        </ul>
      </section>

      <section aria-labelledby="absent-heading" className="max-w-measure space-y-4 text-slate-800">
        <h2 id="absent-heading" className="font-serif text-2xl font-semibold text-slate-900">
          What is not in the files
        </h2>
        <ul className="list-disc space-y-2 pl-6">
          <li>
            <strong className="font-semibold">Proposed links</strong> between sites and companies
            that no person has yet confirmed.
          </li>
          <li>
            <strong className="font-semibold">Essays</strong>, which are argument and not record.
          </li>
          <li>
            <strong className="font-semibold">People&rsquo;s names.</strong> Until legal review is
            arranged, people appear by public role only, in the files as on the site.
          </li>
        </ul>
      </section>
    </div>
  );
}
