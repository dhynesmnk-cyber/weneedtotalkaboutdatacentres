/**
 * The four data downloads (/data): sites, entities, sources and the research
 * agenda, as CSV, under CC BY 4.0 (the author's decision of 2026-11-17).
 *
 * The downloads carry what the site already publishes, through the same
 * anon reads and Row Level Security, and nothing more. In particular:
 *   - a blank is never just blank. Every factual site field has a `<field>_gap`
 *     column beside it, saying why it is empty (the gap's reason) when it is;
 *   - each record lists the sources that cite it, by source id, so any row can
 *     be checked against the sources file;
 *   - proposed links, unapproved essays and people's names are not in them,
 *     because the site does not publish them.
 *
 * Pure builders: the routes fetch the rows and pass them in.
 */

import { toCsv, type Cell } from '@/lib/csv';
import type { GapRef } from '@/lib/evidence';
import { SITE_FACTUAL_FIELDS } from '@/lib/ingestion/transform';
import type { EntityRow, ResearchAgendaRow, SiteRow, SourceRow } from '@/lib/types';

export const DATASETS = ['sites', 'entities', 'sources', 'research'] as const;
export type Dataset = (typeof DATASETS)[number];

export const DATA_LICENCE = {
  name: 'Creative Commons Attribution 4.0 International (CC BY 4.0)',
  short: 'CC BY 4.0',
  url: 'https://creativecommons.org/licenses/by/4.0/',
} as const;

const SOURCE_SEPARATOR = '; ';

function sourcesOf(cited: ReadonlyMap<string, readonly string[]>, id: string): string {
  return [...(cited.get(id) ?? [])].sort().join(SOURCE_SEPARATOR);
}

/** Sites: every factual field with its gap reason beside it, then provenance and sources. */
export function sitesCsv(
  sites: readonly SiteRow[],
  gaps: readonly GapRef[],
  cited: ReadonlyMap<string, readonly string[]>,
): string {
  const reasons = new Map<string, string>();
  for (const g of gaps) reasons.set(`${g.record_id}|${g.field_name}`, g.reason);

  const header = [
    'id',
    'record_id',
    'name',
    ...SITE_FACTUAL_FIELDS.flatMap((f) => [f, `${f}_gap`]),
    'notes',
    'fact_status',
    'confidence',
    'as_of_date',
    'sources',
  ];
  const rows = sites.map((s): Cell[] => [
    s.pipeline_id,
    s.id,
    s.name,
    ...SITE_FACTUAL_FIELDS.flatMap((f): Cell[] => {
      const value = s[f] as Cell;
      const empty = value === null || value === undefined || value === '';
      return [value, empty ? (reasons.get(`${s.id}|${f}`) ?? 'unknown') : null];
    }),
    s.notes,
    s.fact_status,
    s.confidence,
    s.as_of_date,
    sourcesOf(cited, s.id),
  ]);
  return toCsv(header, rows);
}

/** Entities: the companies, agencies and bodies the record names, with their sources. */
export function entitiesCsv(entities: readonly EntityRow[], cited: ReadonlyMap<string, readonly string[]>): string {
  const header = ['id', 'record_id', 'name', 'type', 'role', 'public_actions_summary', 'fact_status', 'confidence', 'as_of_date', 'sources'];
  const rows = entities.map((e): Cell[] => [
    e.pipeline_id,
    e.id,
    e.name,
    e.type,
    e.role,
    e.public_actions_summary,
    e.fact_status,
    e.confidence,
    e.as_of_date,
    sourcesOf(cited, e.id),
  ]);
  return toCsv(header, rows);
}

/** Sources: every document the record cites, graded A to D. */
export function sourcesCsv(sources: readonly SourceRow[]): string {
  const header = ['id', 'record_id', 'title', 'publisher', 'type', 'credibility', 'url', 'retrieved_date'];
  const rows = sources.map((s): Cell[] => [
    s.pipeline_id,
    s.id,
    s.title,
    s.publisher,
    s.type,
    s.credibility,
    s.url,
    s.retrieved_date,
  ]);
  return toCsv(header, rows);
}

/** The research agenda: every published open question and how it is to be answered. */
export function researchCsv(
  questions: readonly ResearchAgendaRow[],
  cited: ReadonlyMap<string, readonly string[]>,
): string {
  const header = [
    'id',
    'record_id',
    'status',
    'pillar',
    'priority',
    'question',
    'why_it_matters',
    'target_source',
    'retrieval_method',
    'opened',
    'resolved_date',
    'notes',
    'sources',
  ];
  const rows = questions.map((q): Cell[] => [
    q.pipeline_id,
    q.id,
    q.status,
    q.pillar,
    q.priority,
    q.question,
    q.why_it_matters,
    q.target_source,
    q.retrieval_method,
    q.opened,
    q.resolved_date,
    q.notes,
    sourcesOf(cited, q.id),
  ]);
  return toCsv(header, rows);
}
