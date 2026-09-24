import { facts, isConfigured } from '@/lib/supabase/server';
import type {
  CitableRecord,
  CitationWithSource,
  DataGapRow,
  GapReason,
} from '@/lib/types';

/**
 * Evidence access: citations and gaps.
 *
 * These are the two things that make a record publishable. A factual field with
 * neither a citation nor a gap is a defect, and `evidenceFor` surfaces that
 * rather than letting it render as an ordinary blank.
 */

/** Citations for one record, with the source joined. */
export async function citationsFor(
  recordType: CitableRecord,
  recordId: string,
): Promise<CitationWithSource[]> {
  if (!isConfigured()) return [];

  const { data, error } = await facts()
    .from('citations')
    .select('*, source:sources(*)')
    .eq('record_type', recordType)
    .eq('record_id', recordId);

  if (error) throw new Error(`Failed to load citations: ${error.message}`);
  return (data ?? []) as unknown as CitationWithSource[];
}

/** Recorded gaps for one record. */
export async function gapsFor(
  recordType: CitableRecord,
  recordId: string,
): Promise<DataGapRow[]> {
  if (!isConfigured()) return [];

  const { data, error } = await facts()
    .from('data_gaps')
    .select('*')
    .eq('record_type', recordType)
    .eq('record_id', recordId);

  if (error) throw new Error(`Failed to load gaps: ${error.message}`);
  return data ?? [];
}

/**
 * PostgREST returns at most this many rows per request. Supabase's default
 * "Max rows" setting is 1000, and a request past it is truncated without an
 * error, so anything that can exceed it has to page.
 */
const PAGE_SIZE = 1000;

/**
 * The part of a gap that pages listing many records use: which record, which
 * field, and why. A full row is more than twice the size, and the site gaps
 * alone are 1885 rows.
 */
export type GapRef = Pick<DataGapRow, 'record_id' | 'field_name' | 'reason'>;

/**
 * Every recorded gap for one kind of record.
 *
 * Paged, because the site gaps alone already number more than one response
 * can carry: an unpaged read would return the first 1000 and every count
 * built on it would be quietly wrong.
 */
export async function listGaps(recordType: CitableRecord): Promise<GapRef[]> {
  if (!isConfigured()) return [];

  const rows: GapRef[] = [];
  for (let from = 0; ; from += PAGE_SIZE) {
    const { data, error } = await facts()
      .from('data_gaps')
      .select('record_id, field_name, reason')
      .eq('record_type', recordType)
      .order('id')
      .range(from, from + PAGE_SIZE - 1);

    if (error) throw new Error(`Failed to load gaps: ${error.message}`);
    // Ordered by id so the pages are stable; PostgREST orders by a column
    // it does not return, so the id costs nothing on the wire.
    rows.push(...(data ?? []));
    if (!data || data.length < PAGE_SIZE) return rows;
  }
}

/** Gaps grouped by record, then by field, for rendering many records at once. */
export function gapsByRecord<G extends GapRef>(
  gaps: readonly G[],
): Map<string, Map<string, G>> {
  const byRecord = new Map<string, G[]>();
  for (const gap of gaps) {
    const list = byRecord.get(gap.record_id);
    if (list) list.push(gap);
    else byRecord.set(gap.record_id, [gap]);
  }
  return new Map([...byRecord].map(([id, list]) => [id, gapsByField(list)]));
}

/** Gaps keyed by field name, for rendering a badge beside the field it concerns. */
export function gapsByField<G extends Pick<DataGapRow, 'field_name'>>(
  gaps: readonly G[],
): Map<string, G> {
  const byField = new Map<string, G>();
  for (const gap of gaps) {
    byField.set(gap.field_name, gap);
  }
  return byField;
}

export interface FieldEvidence<T> {
  field: string;
  value: T | null;
  gap: GapReason | null;
  /**
   * True when the field has neither a value nor a recorded gap. This is a data
   * quality defect under docs/QUALITY.md, not a gap, and the UI says so.
   */
  unexplained: boolean;
}

/**
 * Resolve a field into one of three states: a value, a stated gap, or an
 * unexplained blank.
 *
 * The third state exists so that a missing gap record is visible rather than
 * indistinguishable from a deliberate one.
 */
export function resolveField<T>(
  field: string,
  value: T | null | undefined,
  gaps: Map<string, Pick<DataGapRow, 'reason'>>,
): FieldEvidence<T> {
  const present = value !== null && value !== undefined && value !== '';
  const gap = gaps.get(field);

  return {
    field,
    value: present ? (value as T) : null,
    gap: gap?.reason ?? null,
    unexplained: !present && !gap,
  };
}

/** Citation coverage for a record, as measured by docs/QUALITY.md. */
export function citationCoverage(
  fields: FieldEvidence<unknown>[],
  citations: CitationWithSource[],
): { cited: number; total: number; uncited: string[] } {
  const populated = fields.filter((f) => f.value !== null);
  const claims = new Set(
    citations.map((c) => c.claim).filter((c): c is string => Boolean(c)),
  );

  const uncited = populated
    .filter((f) => !claims.has(f.field))
    .map((f) => f.field);

  return {
    cited: populated.length - uncited.length,
    total: populated.length,
    uncited,
  };
}
