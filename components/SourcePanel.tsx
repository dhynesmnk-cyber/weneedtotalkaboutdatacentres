import { formatDate } from '@/lib/format';
import type { CitationWithSource } from '@/lib/types';

/**
 * Citations for the current record.
 *
 * Every factual claim carries a citation, and the panel is where a reader
 * checks one. Where a citation names the specific claim it supports, that claim
 * is shown, because a record with six sources and six claims is only auditable
 * when the reader can tell which supports which.
 */
export function SourcePanel({
  citations,
  title = 'Sources',
}: {
  citations: CitationWithSource[];
  title?: string;
}) {
  return (
    <section
      aria-labelledby="source-panel-heading"
      className="rounded-lg border border-fact-edge bg-fact-wash p-4"
    >
      <h2
        id="source-panel-heading"
        className="text-sm font-semibold uppercase tracking-wide text-fact-ink"
      >
        {title}
      </h2>

      {citations.length === 0 ? (
        <p className="mt-2 text-sm text-slate-700">
          No sources recorded for this record yet. Nothing here should be treated
          as verified until they are.
        </p>
      ) : (
        <ol className="mt-3 space-y-3">
          {citations.map((citation, index) => (
            <li key={citation.id} className="text-sm">
              <span className="mr-1 font-mono text-xs text-slate-500">
                [{index + 1}]
              </span>
              <SourceLine citation={citation} />
            </li>
          ))}
        </ol>
      )}
    </section>
  );
}

function SourceLine({ citation }: { citation: CitationWithSource }) {
  const { source, claim } = citation;

  if (!source) {
    return (
      <span className="text-red-800">
        Citation points at a source record that could not be loaded.
      </span>
    );
  }

  const retrieved = formatDate(source.retrieved_date);

  return (
    <span>
      {claim && <span className="text-slate-700">On {claim}: </span>}
      {source.url ? (
        <a
          href={source.url}
          className="font-medium text-fact-ink underline underline-offset-2"
          rel="noopener noreferrer"
          target="_blank"
        >
          {source.title}
        </a>
      ) : (
        <span className="font-medium">{source.title}</span>
      )}
      {source.publisher && <span className="text-slate-700">, {source.publisher}</span>}
      {retrieved && (
        <span className="text-slate-600"> (retrieved {retrieved})</span>
      )}
    </span>
  );
}
