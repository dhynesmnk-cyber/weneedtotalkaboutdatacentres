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
  id = 'sources',
}: {
  citations: CitationWithSource[];
  title?: string;
  /**
   * Anchor for the panel. Each entry is `${id}-${n}`, which is what an inline
   * citation in an essay links to. Two panels on one page need distinct ids.
   */
  id?: string;
}) {
  return (
    <section
      id={id}
      aria-labelledby={`${id}-heading`}
      className="scroll-mt-6 rounded-lg border border-fact-edge bg-fact-wash p-4"
    >
      <h2
        id={`${id}-heading`}
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
            <li
              key={citation.id}
              id={`${id}-${index + 1}`}
              className="scroll-mt-6 rounded text-sm target:bg-white target:ring-2 target:ring-fact-ink"
            >
              <span className="mr-1 font-mono text-xs text-slate-600">
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

/** One citation as a reader sees it: title, publisher, retrieval date and grade. */
export function SourceLine({ citation }: { citation: CitationWithSource }) {
  const { source, claim } = citation;

  if (!source) {
    return (
      <span className="text-defect-ink">
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
          className="font-medium link"
          rel="noopener noreferrer"
          target="_blank"
        >
          {source.title}
          <span className="sr-only"> (opens in a new tab)</span>
        </a>
      ) : (
        <span className="font-medium">{source.title}</span>
      )}
      {source.publisher && <span className="text-slate-700">, {source.publisher}</span>}
      {retrieved && (
        <span className="text-slate-600"> (retrieved {retrieved})</span>
      )}
      {source.credibility && (
        <>
          {' '}
          <a
            href="/how-to-read#sources-heading"
            className="whitespace-nowrap rounded border border-fact-edge bg-white px-1.5 text-xs font-medium text-fact-ink no-underline"
            title="Sources are graded A to D by the kind of document they are"
          >
            Grade {source.credibility}
          </a>
        </>
      )}
    </span>
  );
}
