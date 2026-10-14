import Link from 'next/link';
import { lastLoadedAt } from '@/lib/coverage';
import {
  groupResearchAgenda,
  listResearchAgenda,
  researchPillars,
  type ResearchQuestion,
} from '@/lib/researchAgenda';
import { isConfigured } from '@/lib/supabase/server';
import {
  formatDate,
  formatPillar,
  formatPriority,
  formatResearchStatus,
  formatRetrievalMethod,
} from '@/lib/format';
import { NotConnected, NothingRecorded } from '@/components/NotConnected';
import { DateStamp } from '@/components/DateStamp';
import { SourceLine } from '@/components/SourcePanel';

export const dynamic = 'force-dynamic';
export const metadata = { title: 'Open questions' };

/**
 * The research agenda: what the observatory has not yet established, why it
 * matters, and how it means to find out.
 *
 * Published because an observatory that shows what it has not established is
 * more honest than one that shows only what it has (docs/SPEC.md). A question
 * is part of the record, not the analysis: it states what is missing, and the
 * sources it cites are the evidence that the question is real.
 *
 * Who is working a question is not shown, and is not in the table (0009).
 */
export default async function ResearchPage({
  searchParams,
}: {
  searchParams: Record<string, string | string[] | undefined>;
}) {
  const [all, loadedAt] = await Promise.all([listResearchAgenda(), lastLoadedAt()]);
  const pillars = researchPillars(all);
  const requested = typeof searchParams.pillar === 'string' ? searchParams.pillar : null;
  const pillar = requested && pillars.includes(requested) ? requested : null;
  const questions = pillar ? all.filter((q) => q.pillar === pillar) : all;
  const groups = groupResearchAgenda(questions);

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-bold text-slate-900">Open questions</h1>
        <p className="mt-2 max-w-2xl text-slate-700">
          What the observatory has not yet established, why each question
          matters, and how it is to be answered. A question is not a finding:
          it says what is missing. The sources under each one show that the
          question is a real one.
        </p>
        <p className="mt-2 max-w-2xl text-slate-700">
          A question is different from a gap. A gap is one missing value on one
          site, and{' '}
          <Link href="/coverage" className="text-fact-ink underline underline-offset-2">
            What&rsquo;s known
          </Link>{' '}
          counts them field by field. A question is a line of enquiry, and may
          bear on many sites or on none.
        </p>
        <DateStamp dataAsOfDate={loadedAt} className="mt-2" />
      </div>

      {!isConfigured() ? (
        <NotConnected what="research questions" />
      ) : all.length === 0 ? (
        <NothingRecorded what="research questions" />
      ) : (
        <>
          <nav aria-label="Filter by line of enquiry">
            <ul className="flex flex-wrap gap-2 text-sm">
              <li>
                <PillarLink pillar={null} current={pillar} count={all.length} />
              </li>
              {pillars.map((p) => (
                <li key={p}>
                  <PillarLink
                    pillar={p}
                    current={pillar}
                    count={all.filter((q) => q.pillar === p).length}
                  />
                </li>
              ))}
            </ul>
          </nav>

          <p className="text-sm text-slate-700">
            {questions.length} {questions.length === 1 ? 'question' : 'questions'}
            {pillar && <> on {formatPillar(pillar)?.toLowerCase()}</>}:{' '}
            {groups
              .map((g) => `${g.questions.length} ${formatResearchStatus(g.status).toLowerCase()}`)
              .join(', ')}
            .
          </p>

          {groups.map((group) => (
            <section key={group.status} aria-labelledby={`status-${group.status}`}>
              <h2
                id={`status-${group.status}`}
                className="text-lg font-semibold text-slate-900"
              >
                {formatResearchStatus(group.status)}{' '}
                <span className="font-normal text-slate-600">({group.questions.length})</span>
              </h2>
              <ol className="mt-3 space-y-4">
                {group.questions.map((q) => (
                  <li key={q.id}>
                    <Question question={q} />
                  </li>
                ))}
              </ol>
            </section>
          ))}
        </>
      )}
    </div>
  );
}

function PillarLink({
  pillar,
  current,
  count,
}: {
  pillar: string | null;
  current: string | null;
  count: number;
}) {
  const selected = pillar === current;
  return (
    <Link
      href={pillar ? `/research?pillar=${pillar}` : '/research'}
      aria-current={selected ? 'page' : undefined}
      className={`inline-block rounded border px-2 py-1 ${
        selected
          ? 'border-fact-ink bg-fact-wash font-semibold text-fact-ink'
          : 'border-slate-300 text-slate-700 hover:border-fact-edge'
      }`}
    >
      {pillar ? formatPillar(pillar) : 'All'}{' '}
      <span className="text-slate-600">({count})</span>
    </Link>
  );
}

function Question({ question: q }: { question: ResearchQuestion }) {
  const opened = formatDate(q.opened);
  const resolved = formatDate(q.resolved_date);
  const method = formatRetrievalMethod(q.retrieval_method);
  const meta = [
    formatPillar(q.pillar),
    formatPriority(q.priority),
  ].filter((m): m is string => !!m);

  return (
    <article
      aria-labelledby={`q-${q.id}`}
      className="rounded-lg border border-slate-200 border-l-4 border-l-fact-edge px-4 py-3"
    >
      <div className="flex flex-wrap items-baseline gap-x-3 gap-y-1 text-sm text-slate-600">
        <span className="rounded border border-fact-edge bg-fact-wash px-2 py-0.5 font-mono text-xs font-medium text-fact-ink">
          {q.pipeline_id}
        </span>
        {meta.map((m) => (
          <span key={m}>{m}</span>
        ))}
        {opened && (
          <span>
            Opened <time dateTime={q.opened ?? undefined}>{opened}</time>
          </span>
        )}
        {resolved && (
          <span>
            {q.status === 'resolved' ? 'Resolved' : 'Closed'}{' '}
            <time dateTime={q.resolved_date ?? undefined}>{resolved}</time>
          </span>
        )}
      </div>

      <h3 id={`q-${q.id}`} className="mt-2 font-medium text-slate-900">
        {q.question}
      </h3>

      <dl className="mt-2 space-y-2 text-sm">
        {q.why_it_matters && (
          <div>
            <dt className="font-medium text-slate-600">Why it matters</dt>
            <dd className="text-slate-800">{q.why_it_matters}</dd>
          </div>
        )}
        {(method || q.target_source) && (
          <div>
            <dt className="font-medium text-slate-600">How it is to be answered</dt>
            <dd className="text-slate-800">
              {method}
              {method && q.target_source && ': '}
              {q.target_source}
            </dd>
          </div>
        )}
      </dl>

      {q.notes && (
        <details className="mt-2 text-sm">
          <summary className="cursor-pointer text-fact-ink">Research notes</summary>
          <p className="mt-1 whitespace-pre-line text-slate-800">{q.notes}</p>
        </details>
      )}

      <details className="mt-2 text-sm">
        <summary className="cursor-pointer text-fact-ink">
          Sources ({q.citations.length})
        </summary>
        <ol className="mt-2 space-y-2">
          {q.citations.map((citation, index) => (
            <li key={citation.id}>
              <span className="mr-1 font-mono text-xs text-slate-600">[{index + 1}]</span>
              <SourceLine citation={citation} />
            </li>
          ))}
        </ol>
      </details>
    </article>
  );
}
