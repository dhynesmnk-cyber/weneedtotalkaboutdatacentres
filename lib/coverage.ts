import { facts, isConfigured } from '@/lib/supabase/server';
import type { GapRef } from '@/lib/evidence';
import {
  GAP_REASONS,
  SITE_STATUSES,
  type GapReason,
  type SiteRow,
  type SiteStatus,
} from '@/lib/types';

/**
 * How much of the record is actually known.
 *
 * Every figure here is a count of rows that exist: sites with a value in a
 * field, and gaps with a stated reason. Nothing is estimated, and a field with
 * neither a value nor a gap is counted as unexplained rather than folded into
 * either, because that is a data quality defect under docs/QUALITY.md and
 * hiding it inside another number would be the same fault the gap badge
 * exists to prevent.
 */

export interface CoverageField {
  /** The field name as `facts.data_gaps.field_name` records it. */
  readonly field: string;
  /** Overrides formatFieldName where the column name is not the reader's. */
  readonly label?: string;
  readonly present: (site: SiteRow) => boolean;
  /**
   * True where the stored value itself says the answer is not known. Such a
   * site is neither recorded nor unexplained: it is counted as an `unknown`
   * gap, the only reason a derived gap may give (CLAUDE.md).
   */
  readonly statesUnknown?: (site: SiteRow) => boolean;
}

const has =
  (key: keyof SiteRow) =>
  (site: SiteRow): boolean => {
    const value = site[key];
    return value !== null && value !== undefined && value !== '';
  };

/**
 * The site fields a reader would expect to be researched, in reading order:
 * who and where, then how big, then how it runs, then when.
 *
 * Notes and the provenance columns are left out: they describe the record
 * rather than the site. Coordinates are one entry, not two, because the
 * schema constrains lat and lng to be supplied together; the gap is recorded
 * against `lat`.
 */
export const SITE_COVERAGE_FIELDS: readonly CoverageField[] = [
  { field: 'status', present: has('status') },
  { field: 'operator', present: has('operator') },
  { field: 'proponent', present: has('proponent') },
  { field: 'lga', present: has('lga') },
  { field: 'suburb', present: has('suburb') },
  { field: 'state', present: has('state') },
  { field: 'address', present: has('address') },
  {
    field: 'lat',
    label: 'Coordinates',
    present: (s) => s.lat !== null && s.lng !== null,
  },
  { field: 'total_capacity_mw', present: has('total_capacity_mw') },
  { field: 'it_capacity_mw', label: 'IT capacity', present: has('it_capacity_mw') },
  { field: 'max_capacity_mw', label: 'Maximum capacity', present: has('max_capacity_mw') },
  { field: 'first_phase_mw', label: 'First phase capacity', present: has('first_phase_mw') },
  { field: 'live_capacity_mw', present: has('live_capacity_mw') },
  { field: 'cooling_type', present: has('cooling_type') },
  { field: 'rack_density_kw', present: has('rack_density_kw') },
  { field: 'grid_connection', present: has('grid_connection') },
  { field: 'water_usage', present: has('water_usage') },
  {
    field: 'hcf_certified',
    label: 'HCF certification',
    // The column stores "unknown" as a value (migration 0008): not knowing
    // whether a site is certified. Counting it as recorded would overstate
    // what the record holds.
    present: (s) => has('hcf_certified')(s) && s.hcf_certified !== 'unknown',
    statesUnknown: (s) => s.hcf_certified === 'unknown',
  },
  { field: 'campus_area_ha', label: 'Campus area', present: has('campus_area_ha') },
  { field: 'gfa_sqm', label: 'Gross floor area', present: has('gfa_sqm') },
  { field: 'capital_cost_aud', present: has('capital_cost_aud') },
  { field: 'construction_jobs', present: has('construction_jobs') },
  { field: 'operational_jobs', present: has('operational_jobs') },
  { field: 'operational_from', present: has('operational_from') },
  { field: 'target_completion', present: has('target_completion') },
];

export interface FieldCoverage {
  readonly field: string;
  readonly label?: string;
  /** Sites with a value. */
  readonly known: number;
  /** Sites with no value and a recorded gap, by the gap's reason. */
  readonly gaps: Readonly<Record<GapReason, number>>;
  /** Sites with neither a value nor a gap. A defect, counted on its own. */
  readonly unexplained: number;
  readonly total: number;
}

/**
 * Coverage of each field across a set of sites.
 *
 * A site holding both a value and a gap for the same field counts as known,
 * which is how the site page resolves it too (see resolveField).
 */
export function siteCoverage(
  sites: readonly SiteRow[],
  gaps: readonly GapRef[],
  fields: readonly CoverageField[] = SITE_COVERAGE_FIELDS,
): FieldCoverage[] {
  const gapFor = new Map<string, GapReason>();
  for (const gap of gaps) gapFor.set(`${gap.record_id}\u0000${gap.field_name}`, gap.reason);

  return fields.map(({ field, label, present, statesUnknown }) => {
    const byReason = Object.fromEntries(GAP_REASONS.map((r) => [r, 0])) as Record<
      GapReason,
      number
    >;
    let known = 0;
    let unexplained = 0;

    for (const site of sites) {
      if (present(site)) {
        known += 1;
        continue;
      }
      if (statesUnknown?.(site)) {
        byReason.unknown += 1;
        continue;
      }
      const reason = gapFor.get(`${site.id}\u0000${field}`);
      if (reason) byReason[reason] += 1;
      else unexplained += 1;
    }

    return { field, label, known, gaps: byReason, unexplained, total: sites.length };
  });
}

export interface StatusCount {
  /** Null for sites with no status recorded. */
  readonly status: SiteStatus | null;
  readonly count: number;
}

/**
 * Sites per status, in lifecycle order rather than by size, because status is
 * a sequence: a reader scans it as a pipeline from rumour to operation. Only
 * statuses that occur are listed. Sites with no status come last.
 */
export function statusCounts(sites: readonly SiteRow[]): StatusCount[] {
  const counts = new Map<SiteStatus | null, number>();
  for (const site of sites) counts.set(site.status, (counts.get(site.status) ?? 0) + 1);

  const ordered: StatusCount[] = SITE_STATUSES.filter((s) => counts.has(s)).map((s) => ({
    status: s,
    count: counts.get(s)!,
  }));
  const missing = counts.get(null);
  if (missing) ordered.push({ status: null, count: missing });
  return ordered;
}

/**
 * When the record was last loaded from the curation pipeline.
 *
 * This is the date the whole summary is "as at". It is the load, not the
 * research: sources inside it carry their own retrieval dates.
 */
export async function lastLoadedAt(): Promise<string | null> {
  if (!isConfigured()) return null;

  const { data, error } = await facts()
    .from('ingest_runs')
    .select('run_at')
    .order('run_at', { ascending: false })
    .limit(1)
    .maybeSingle();

  if (error) throw new Error(`Failed to load the last ingest run: ${error.message}`);
  return data?.run_at ?? null;
}
