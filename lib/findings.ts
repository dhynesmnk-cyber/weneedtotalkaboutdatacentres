import { resolveLga } from '@/lib/councils';
import { FACT_STATUSES, type FactStatus, type SiteRow } from '@/lib/types';

/**
 * Findings the home page states about the record.
 *
 * Each is a count or a single value read straight off the loaded sites, and
 * the page links every one to the records it comes from, so a reader can
 * check it. Nothing is summed across sites: capacity figures measure
 * different things (docs/PIPELINE_MAPPING.md), and adding them would state a
 * total no source gives.
 */

export interface LargestCapacity {
  readonly site: Pick<SiteRow, 'id' | 'name'>;
  readonly mw: number;
  /** How many sites have a total capacity at all: the field it is largest in. */
  readonly of: number;
}

/** The largest recorded total capacity, or null if none is recorded. */
export function largestCapacity(sites: readonly SiteRow[]): LargestCapacity | null {
  const withCapacity = sites.filter((s) => Number.isFinite(s.total_capacity_mw));
  if (withCapacity.length === 0) return null;
  const top = withCapacity.reduce((a, b) =>
    (b.total_capacity_mw as number) > (a.total_capacity_mw as number) ? b : a,
  );
  return {
    site: { id: top.id, name: top.name },
    mw: top.total_capacity_mw as number,
    of: withCapacity.length,
  };
}

export interface TopCouncil {
  readonly council: string;
  readonly count: number;
  /** The next council's count, so "more than any other" is checkable. */
  readonly runnerUp: number;
}

/**
 * The council with the most sites, counted in its approved spelling.
 *
 * Null when two councils tie for first: "the most sites" would then name one
 * of them arbitrarily, which is a claim the record does not make. A site whose
 * council cell names two councils is not counted for either.
 */
export function topCouncil(
  sites: readonly SiteRow[],
  councils: ReadonlyMap<string, string>,
): TopCouncil | null {
  const counts = new Map<string, number>();
  for (const site of sites) {
    const name = resolveLga(site.lga, councils)?.display;
    if (!name || name.includes(';')) continue;
    counts.set(name, (counts.get(name) ?? 0) + 1);
  }
  const ranked = [...counts].sort((a, b) => b[1] - a[1]);
  const [first, second] = ranked;
  if (!first) return null;
  if (second && second[1] === first[1]) return null;
  return { council: first[0], count: first[1], runnerUp: second?.[1] ?? 0 };
}

/** Sites by how well their record is established, strongest first. */
export function evidenceCounts(
  sites: readonly SiteRow[],
): { status: FactStatus | null; count: number }[] {
  const counts = new Map<FactStatus | null, number>();
  for (const site of sites) {
    counts.set(site.fact_status, (counts.get(site.fact_status) ?? 0) + 1);
  }
  const ordered: { status: FactStatus | null; count: number }[] = FACT_STATUSES.filter((s) =>
    counts.has(s),
  ).map((s) => ({ status: s, count: counts.get(s)! }));
  const unrated = counts.get(null);
  if (unrated) ordered.push({ status: null, count: unrated });
  return ordered;
}
