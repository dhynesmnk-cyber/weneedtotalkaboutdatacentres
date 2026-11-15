import Link from 'next/link';
import type { Metadata } from 'next';
import { PageHeader } from '@/components/PageHeader';
import { SITE_NAME } from '@/lib/site';

export const metadata: Metadata = {
  title: 'About',
  description: 'What this site is, how it is made, and who makes it.',
};

/**
 * About the site: what it is, how its two layers are made, and the
 * disclosure every reader should have. Static, and deliberately free of
 * figures: a number here would be a claim without a source panel.
 */
export default function AboutPage() {
  return (
    <div className="space-y-10">
      <PageHeader layer="record" kicker="About this site" title={`About ${SITE_NAME}`}>
        <p>
          A public record of Australia&rsquo;s AI data centres, the companies and money
          behind them, and what is and is not known about each, with a separate layer of
          essays that argue from that record.
        </p>
      </PageHeader>

      <section aria-labelledby="layers-heading" className="max-w-measure space-y-4 text-slate-800">
        <h2 id="layers-heading" className="font-serif text-2xl font-semibold text-slate-900">
          Two layers, kept apart
        </h2>
        <p>
          <strong className="font-semibold text-fact-ink">The record</strong> is sourced
          facts: sites, operators, capacity, councils, events, money. Every fact links to the
          document it comes from, and every missing value says why it is missing. Nothing is
          estimated to fill a gap, and no sample data is ever shown in place of the real
          thing.
        </p>
        <p>
          <strong className="font-semibold text-editorial-ink">The analysis</strong> is
          argument: essays, a statement of where we stand, and proposals for how Australia could do this differently. Each piece shows the
          record it rests on first, then marks where the argument begins.
        </p>
        <p>
          <Link href="/how-to-read" className="link">
            How to read this site
          </Link>{' '}
          explains the badges, grades and dates in detail.
        </p>
      </section>

      <section aria-labelledby="made-heading" className="max-w-measure space-y-4 text-slate-800">
        <h2 id="made-heading" className="font-serif text-2xl font-semibold text-slate-900">
          How it is made
        </h2>
        <p>
          The research is gathered and graded in a separate research database, checked, and
          only then loaded here. The questions still open, and how each is to be answered,
          are listed on{' '}
          <Link href="/research" className="link">
            Open questions
          </Link>
          .
        </p>
        <p>
          Essays are drafted with the help of an AI model, from cited research notes, and then
          read, edited and approved by the site&rsquo;s author. No piece is published until the
          author approves it, and the site&rsquo;s database records who approved which text and
          when. Software checks that every factual sentence carries a citation and that
          opinion stays below the divider; it cannot judge an argument, which is the
          author&rsquo;s job.
        </p>
        <p>
          People appear on this site only in their public roles, as shown by a primary record.
        </p>
      </section>

      <section
        aria-labelledby="disclosure-heading"
        className="max-w-measure rounded-lg border border-slate-300 bg-slate-50 p-5 text-slate-800"
      >
        <h2 id="disclosure-heading" className="kicker text-slate-700">
          Disclosure
        </h2>
        <p className="mt-3">
          The AI model used to draft essays and research notes here is Claude, made by
          Anthropic. Anthropic is a frontier AI company, and is itself a subject of this
          site&rsquo;s research. Any piece that touches Anthropic says so above its text, and
          its sources should be read directly.
        </p>
      </section>
    </div>
  );
}
