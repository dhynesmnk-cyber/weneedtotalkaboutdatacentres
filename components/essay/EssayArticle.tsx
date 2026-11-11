import { DateStamp } from '@/components/DateStamp';
import { FactOpinionDivider } from '@/components/FactOpinionDivider';
import { SourcePanel } from '@/components/SourcePanel';
import { EssayBody, type CitationIndex } from '@/components/essay/EssayBody';
import { slugify } from '@/lib/editorial/markdown';
import { sourcesInOrder, splitAtOpinion } from '@/lib/editorial/rules';
import { sections } from '@/lib/editorial/text';
import { youtubeEmbedUrl } from '@/lib/editorial/youtube';
import type { CitationWithSource, EssayRow, SourceRow } from '@/lib/types';

export type ArticlePiece = Pick<
  EssayRow,
  'title' | 'standfirst' | 'kind' | 'body' | 'publish_date' | 'data_as_of_date' | 'conflict' | 'youtube_id' | 'proposal_no'
>;

const KIND_LABEL: Record<EssayRow['kind'], string> = {
  essay: 'Essay',
  position: 'Where we stand',
  proposal: 'What if…?',
};

/**
 * The numbering readers see, and the source panel that goes with it.
 *
 * Sources are numbered by first citation in the text, so the panel reads in
 * the order the argument meets them. An id the record does not hold gets no
 * number, and is shown as [?] where it is cited, never silently dropped.
 */
export function citationModel(body: string, sources: readonly SourceRow[]) {
  const byPipelineId = new Map(sources.filter((s) => s.pipeline_id).map((s) => [s.pipeline_id!, s]));
  const index: CitationIndex = {};
  const panel: CitationWithSource[] = [];
  for (const id of sourcesInOrder(body)) {
    const source = byPipelineId.get(id);
    if (!source) continue;
    const n = panel.length + 1;
    index[id] = { n, title: source.title };
    panel.push({
      id: `cite-${id}`,
      source_id: source.id,
      record_type: 'essays',
      record_id: '',
      claim: null,
      created_at: source.created_at,
      source,
    });
  }
  return { index, panel };
}

/**
 * An essay, position or proposal as a reader sees it. The public page and the
 * editor's preview both render this, so what is approved is what is shown.
 *
 * The record comes first, in the fact layer's colours; the divider; then the
 * argument, in the editorial layer's. The divider is drawn by the structure
 * of the text (the "Our view" heading), not by the writer remembering to add it.
 */
export function EssayArticle({
  piece,
  sources,
  footer,
  compact = false,
}: {
  piece: ArticlePiece;
  /** The sources the body cites, in any order. */
  sources: readonly SourceRow[];
  footer?: React.ReactNode;
  /**
   * One column, no side navigation: for a narrow container such as the
   * editor's preview pane, where the wide-screen layout would be squeezed.
   */
  compact?: boolean;
}) {
  const body = piece.body ?? '';
  const { index, panel } = citationModel(body, sources);
  const { record, opinion, heading } = splitAtOpinion(body);
  const recordSections = sections(record).sections.map((s) => s.heading);
  const embedUrl = youtubeEmbedUrl(piece.youtube_id);
  const kicker =
    piece.kind === 'proposal' && piece.proposal_no
      ? `${KIND_LABEL.proposal} · Proposal ${piece.proposal_no}`
      : KIND_LABEL[piece.kind];

  return (
    <article className="essay">
      <header className="max-w-4xl">
        <p className="kicker text-editorial-ink">Analysis · {kicker}</p>
        <h1 className="mt-3 font-serif text-display font-semibold text-slate-900">{piece.title}</h1>
        {piece.standfirst && <p className="standfirst mt-5 font-serif">{piece.standfirst}</p>}
        <DateStamp publishDate={piece.publish_date} dataAsOfDate={piece.data_as_of_date} className="mt-5" />
      </header>

      {piece.conflict && (
        <aside
          aria-labelledby="disclosure-heading"
          className="mt-6 max-w-measure rounded-lg border border-slate-300 bg-slate-50 p-4 text-sm text-slate-800"
        >
          <h2 id="disclosure-heading" className="kicker text-slate-700">
            Disclosure
          </h2>
          <p className="mt-2">{piece.conflict}</p>
        </aside>
      )}

      {embedUrl && (
        <div className="mt-8 aspect-video w-full max-w-4xl overflow-hidden rounded-lg border border-slate-200">
          <iframe
            src={embedUrl}
            title={`Video essay: ${piece.title}`}
            className="h-full w-full"
            allow="accelerometer; clipboard-write; encrypted-media; picture-in-picture"
            allowFullScreen
          />
        </div>
      )}

      <div className={compact ? 'mt-10' : 'mt-10 lg:grid lg:grid-cols-[minmax(0,68ch)_minmax(0,1fr)] lg:gap-16'}>
        <div>
          {record.trim() && (
            <div className="essay-body essay-record">
              <EssayBody markdown={record} citations={index} />
            </div>
          )}

          {heading && (
            <>
              <FactOpinionDivider
                label="Our view begins here"
                description="What follows is argument: the authors’ interpretation of the record above, not a sourced finding."
              />
              <div className="essay-body essay-opinion">
                <h2 id={slugify(heading)}>{heading}</h2>
                <EssayBody markdown={opinion ?? ''} citations={index} />
              </div>
            </>
          )}
        </div>

        {!compact && (recordSections.length > 1 || heading) && (
          <nav aria-label="In this piece" className="hidden lg:block" data-print-hidden>
            <div className="sticky top-6 border-l border-slate-200 pl-5 text-sm">
              <p className="kicker text-slate-600">In this piece</p>
              <ol className="mt-3 space-y-2">
                {recordSections.map((h) => (
                  <li key={h}>
                    <a href={`#${slugify(h)}`} className="text-slate-700 hover:text-slate-900 hover:underline">
                      {h}
                    </a>
                  </li>
                ))}
                {heading && (
                  <li>
                    <a href={`#${slugify(heading)}`} className="text-editorial-ink hover:underline">
                      {heading}
                    </a>
                  </li>
                )}
                <li>
                  <a href="#sources" className="text-fact-ink hover:underline">
                    Sources ({panel.length})
                  </a>
                </li>
              </ol>
            </div>
          </nav>
        )}
      </div>

      <div className="mt-12 max-w-measure space-y-6">
        <SourcePanel id="sources" citations={panel} title={`Sources cited (${panel.length})`} />
        {footer}
      </div>
    </article>
  );
}
