import { resolveLga } from '@/lib/councils';
import {
  FACT_STATUSES,
  SITE_STATUSES,
  type FactStatus,
  type SiteRow,
  type SiteStatus,
} from '@/lib/types';

/**
 * Sorting and filtering for the site index.
 *
 * The state lives in the URL, as the timeline's tracks do, so a sorted and
 * filtered view is a link a reader can share. Everything here is pure: the
 * page reads the params, fetches the sites once, and hands both over.
 */

export const SORT_KEYS = ['name', 'status', 'capacity', 'council'] as const;
export type SortKey = (typeof SORT_KEYS)[number];
export type SortDir = 'asc' | 'desc';

export interface IndexQuery {
  readonly sort: SortKey;
  readonly dir: SortDir;
  readonly status: SiteStatus | null;
  /** A council's displayed name, as `distinctLgas` lists it. */
  readonly council: string | null;
  /** How well the site's record is established. */
  readonly evidence: FactStatus | null;
}

export const DEFAULT_QUERY: IndexQuery = {
  sort: 'name',
  dir: 'asc',
  status: null,
  council: null,
  evidence: null,
};

type Params = Record<string, string | string[] | undefined>;

function one(value: string | string[] | undefined): string | null {
  const v = Array.isArray(value) ? value[0] : value;
  return v === undefined || v.trim() === '' ? null : v.trim();
}

/**
 * Read the query from URL params. Anything unrecognised falls back to the
 * default rather than erroring: a hand-edited or stale link should still show
 * the index, not a failure.
 */
export function parseIndexQuery(params: Params): IndexQuery {
  const sort = one(params.sort);
  const dir = one(params.dir);
  const status = one(params.status);
  const evidence = one(params.evidence);

  return {
    sort: (SORT_KEYS as readonly string[]).includes(sort ?? '')
      ? (sort as SortKey)
      : DEFAULT_QUERY.sort,
    dir: dir === 'desc' ? 'desc' : 'asc',
    status: (SITE_STATUSES as readonly string[]).includes(status ?? '')
      ? (status as SiteStatus)
      : null,
    council: one(params.council),
    evidence: (FACT_STATUSES as readonly string[]).includes(evidence ?? '')
      ? (evidence as FactStatus)
      : null,
  };
}

/** The URL for a query. Defaults are left out so the plain index is `/list`. */
export function indexHref(query: IndexQuery): string {
  const params = new URLSearchParams();
  if (query.sort !== DEFAULT_QUERY.sort) params.set('sort', query.sort);
  if (query.dir !== DEFAULT_QUERY.dir) params.set('dir', query.dir);
  if (query.status) params.set('status', query.status);
  if (query.council) params.set('council', query.council);
  if (query.evidence) params.set('evidence', query.evidence);
  const search = params.toString();
  return search ? `/list?${search}` : '/list';
}

/**
 * Where a column header links: the same column flips direction, a new one
 * starts ascending. Filters are kept.
 */
export function sortHref(query: IndexQuery, key: SortKey): string {
  const dir: SortDir = query.sort === key && query.dir === 'asc' ? 'desc' : 'asc';
  return indexHref({ ...query, sort: key, dir });
}

type SortValue = string | number | null;

function sortValue(
  site: SiteRow,
  key: SortKey,
  councils: ReadonlyMap<string, string>,
): SortValue {
  switch (key) {
    case 'name':
      return site.name;
    case 'status':
      return site.status === null ? null : SITE_STATUSES.indexOf(site.status);
    case 'capacity':
      return Number.isFinite(site.total_capacity_mw) ? site.total_capacity_mw : null;
    case 'council':
      return resolveLga(site.lga, councils)?.display ?? null;
  }
}

function compare(a: SortValue, b: SortValue): number {
  if (typeof a === 'number' && typeof b === 'number') return a - b;
  return String(a).localeCompare(String(b), 'en-AU', { sensitivity: 'base' });
}

/**
 * Filter, then sort.
 *
 * Sites with no value for the sort column always go last, in either
 * direction. A gap is not a small number or an early letter, and sorting it
 * to the top of "largest first" would rank unknowns above known figures.
 * Ties, and the unknowns among themselves, fall back to name.
 */
export function applyIndexQuery(
  sites: readonly SiteRow[],
  query: IndexQuery,
  councils: ReadonlyMap<string, string>,
): SiteRow[] {
  const filtered = sites.filter(
    (site) =>
      (query.status === null || site.status === query.status) &&
      (query.council === null ||
        resolveLga(site.lga, councils)?.display === query.council) &&
      (query.evidence === null || site.fact_status === query.evidence),
  );

  const sign = query.dir === 'asc' ? 1 : -1;
  return filtered
    .map((site) => ({ site, value: sortValue(site, query.sort, councils) }))
    .sort((a, b) => {
      if (a.value === null && b.value !== null) return 1;
      if (b.value === null && a.value !== null) return -1;
      const byValue = a.value === null ? 0 : sign * compare(a.value, b.value);
      return byValue !== 0 ? byValue : compare(a.site.name, b.site.name);
    })
    .map(({ site }) => site);
}
