import Link from 'next/link';
import { EvidenceBadge, EVIDENCE_MEANING } from '@/components/EvidenceBadge';
import { GapBadge, UnexplainedBadge } from '@/components/GapBadge';
import { EditorialBlock, FactBlock, FactOpinionDivider } from '@/components/FactOpinionDivider';
import { FACT_STATUSES, GAP_REASONS, type GapReason } from '@/lib/types';

export const metadata = { title: 'How to read this site' };

// docs/SPEC.md's definitions, in reader-facing words.
const GAP_MEANING: Record<GapReason, string> = {
  unknown: 'Not yet researched, or researched without finding a source.',
  not_disclosed: 'Asked for or publicly sought, and the holder did not provide it.',
  not_applicable: 'The field does not apply to this site.',
  withheld: 'The figure exists but is redacted or commercial-in-confidence in the source.',
};

/**
 * How to read the site: the two layers, what each badge means, and where the
 * facts come from.
 *
 * Static on purpose. It describes conventions, not data, so it can be read
 * without a database and cited from anywhere. The badges are the real
 * components, so the key cannot drift from what the rest of the site shows.
 */
export default function HowToReadPage() {
  return (
    <div className="max-w-3xl space-y-12">
      <div>
        <h1 className="text-2xl font-bold text-slate-900">How to read this site</h1>
        <p className="mt-2 text-slate-700">
          The observatory keeps two things apart: a public record of Australian data
          centre sites, and analysis of what that record shows. This page explains how
          to tell them apart, and how much weight each fact on the record can bear.
        </p>
      </div>

      <section aria-labelledby="layers-heading" className="space-y-4">
        <h2 id="layers-heading" className="text-xl font-bold text-slate-900">
          Two layers: the record and the analysis
        </h2>
        <FactBlock>
          <p className="py-2 text-slate-800">
            <strong className="text-fact-ink">The record</strong> is shown on a cool
            blue edge like this one. It holds what a source says about each site: status,
            operator, capacity, council, and so on. Every fact links to the source it came
            from, and anything not found is marked as a gap, never estimated. You will find
            it on the{' '}
            <Link href="/list" className="text-fact-ink underline underline-offset-2">
              site index
            </Link>
            , the{' '}
            <Link href="/map" className="text-fact-ink underline underline-offset-2">
              map
            </Link>{' '}
            and each site&rsquo;s own page.
          </p>
        </FactBlock>
        <FactOpinionDivider />
        <EditorialBlock>
          <p className="py-2 text-slate-800">
            <strong className="text-editorial-ink">The analysis</strong> is shown on a warm
            edge like this one, below a divider that says analysis begins. It is argument
            and interpretation: essays and case studies that draw on the record, cite the
            sources they rely on, and are published with a date. Read it as a point of
            view, not as a finding. It lives under{' '}
            <Link href="/essays" className="text-editorial-ink underline underline-offset-2">
              Essays
            </Link>
            .
          </p>
        </EditorialBlock>
      </section>

      <section aria-labelledby="evidence-heading" className="space-y-4">
        <h2 id="evidence-heading" className="text-xl font-bold text-slate-900">
          How well each record is established
        </h2>
        <p className="text-slate-700">
          A figure a developer announces and a figure read in a signed planning consent
          are not the same kind of fact. Each site record says which kind it rests on.
        </p>
        <dl className="divide-y divide-slate-200 rounded-lg border border-slate-200">
          {FACT_STATUSES.map((status) => (
            <div key={status} className="flex flex-col gap-2 px-4 py-3 sm:flex-row sm:items-baseline sm:gap-4">
              <dt className="w-72 shrink-0">
                <EvidenceBadge status={status} />
              </dt>
              <dd className="text-sm text-slate-700">{EVIDENCE_MEANING[status]}</dd>
            </div>
          ))}
        </dl>
        <p className="text-sm text-slate-700">
          A claimed record is never presented as verified. You can list the sites that
          rest only on a claim from the{' '}
          <Link
            href="/list?evidence=claimed"
            className="text-fact-ink underline underline-offset-2"
          >
            site index
          </Link>
          .
        </p>
      </section>

      <section aria-labelledby="gaps-heading" className="space-y-4">
        <h2 id="gaps-heading" className="text-xl font-bold text-slate-900">
          Missing values are findings
        </h2>
        <p className="text-slate-700">
          When a value is missing, the site says why rather than leaving a blank or
          filling in a guess. That a developer has not published its water use is itself
          something worth knowing.
        </p>
        <dl className="divide-y divide-slate-200 rounded-lg border border-slate-200">
          {GAP_REASONS.map((reason) => (
            <div key={reason} className="flex flex-col gap-2 px-4 py-3 sm:flex-row sm:items-baseline sm:gap-4">
              <dt className="w-56 shrink-0">
                <GapBadge reason={reason} />
              </dt>
              <dd className="text-sm text-slate-700">{GAP_MEANING[reason]}</dd>
            </div>
          ))}
          <div className="flex flex-col gap-2 px-4 py-3 sm:flex-row sm:items-baseline sm:gap-4">
            <dt className="w-56 shrink-0">
              <UnexplainedBadge />
            </dt>
            <dd className="text-sm text-slate-700">
              A blank with no stated reason. That is a fault in the record, not a finding,
              and it is shown so it cannot hide.
            </dd>
          </div>
        </dl>
        <p className="text-sm text-slate-700">
          <Link href="/coverage" className="text-fact-ink underline underline-offset-2">
            What&rsquo;s known
          </Link>{' '}
          counts every value and every gap, field by field.
        </p>
      </section>

      <section aria-labelledby="sources-heading" className="space-y-3">
        <h2 id="sources-heading" className="text-xl font-bold text-slate-900">
          Sources and their grades
        </h2>
        <p className="text-slate-700">
          Every site page lists its sources, with the date each was retrieved. Sources are
          graded A to D by the kind of document they are, not by whether they turned out
          to be right: an excellent law firm analysis is still a secondary source.
        </p>
        <ul className="list-disc space-y-1 pl-6 text-sm text-slate-700">
          <li>
            <strong>A</strong>: mostly primary documents, such as government and regulator
            publications, planning records, legislation and companies&rsquo; own releases.
          </li>
          <li>
            <strong>B</strong>: mostly secondary sources, such as news reporting, law firm
            and academic analysis, and research.
          </li>
          <li>
            <strong>C</strong> and <strong>D</strong>: lower-weight material, such as
            industry marketing, market research and community posts.
          </li>
        </ul>
      </section>

      <section aria-labelledby="dates-heading" className="space-y-3">
        <h2 id="dates-heading" className="text-xl font-bold text-slate-900">Dates</h2>
        <ul className="list-disc space-y-1 pl-6 text-sm text-slate-700">
          <li>
            <strong>Data as at</strong> says when figures were current. On a site&rsquo;s
            page it is the date that site&rsquo;s research was last checked; on the home
            page, the date the whole record was last loaded onto this site.
          </li>
          <li>
            <strong>Retrieved</strong> beside a source is when that document was read.
          </li>
          <li>
            <strong>Published</strong> on analysis is when it was published. Analysis also
            says when the data it relies on was current, which may be earlier.
          </li>
        </ul>
      </section>
    </div>
  );
}
