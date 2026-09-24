import Link from 'next/link';
import { aliasMap, distinctLgas, listLgaAliases, resolveLga } from '@/lib/councils';
import { listSites } from '@/lib/sites';
import { listEntities } from '@/lib/entities';
import { gapsByRecord, listGaps } from '@/lib/evidence';
import { statusCounts } from '@/lib/coverage';
import {
  applyIndexQuery,
  DEFAULT_QUERY,
  indexHref,
  parseIndexQuery,
  sortHref,
  type IndexQuery,
  type SortKey,
} from '@/lib/siteIndex';
import { isConfigured } from '@/lib/supabase/server';
import { NotConnected, NothingRecorded } from '@/components/NotConnected';
import { GapBadge, UnexplainedBadge } from '@/components/GapBadge';
import { formatMw, formatSiteStatus } from '@/lib/format';
import type { DataGapRow } from '@/lib/types';

export const dynamic = 'force-dynamic';
export const metadata = { title: 'Sites and entities' };

const COLUMNS: { key: SortKey; label: string }[] = [
  { key: 'name', label: 'Name' },
  { key: 'status', label: 'Status' },
  { key: 'capacity', label: 'Capacity' },
  { key: 'council', label: 'Council' },
];

/**
 * Sortable, filterable index of sites, and the major entities.
 *
 * Sort and filters live in the URL and the filter is a plain GET form, so the
 * index works, and can be shared, without JavaScript. Missing values show the
 * same gap badge as the site record, so the index never says less about why
 * something is blank than the record does.
 */
export default async function ListPage({
  searchParams,
}: {
  searchParams: Record<string, string | string[] | undefined>;
}) {
  const query = parseIndexQuery(searchParams);
  const [sites, gaps, entities, aliases] = await Promise.all([
    listSites(),
    listGaps('sites'),
    listEntities({ majorOnly: true }),
    listLgaAliases(),
  ]);
  // Council names are shown in the spelling a human approved, so one council
  // reads as one council. The stored value is untouched; the site record page
  // shows it, and facts.lga_aliases is published so a reader can check every
  // equivalence and who approved it.
  const councils = aliasMap(aliases);
  const gapsBySite = gapsByRecord(gaps);
  const rows = applyIndexQuery(sites, query, councils);
  const filtered = query.status !== null || query.council !== null;

  return (
    <div className="space-y-10">
      <div>
        <h1 className="text-2xl font-bold text-slate-900">Sites and entities</h1>
        <p className="mt-2 max-w-2xl text-slate-700">
          The full index. Entity profiles are published only for entities flagged
          as major by public prominence.
        </p>
      </div>

      {!isConfigured() ? (
        <NotConnected what="sites or entities" />
      ) : (
        <>
          <section aria-labelledby="sites-heading" className="space-y-4">
            <h2 id="sites-heading" className="text-lg font-semibold text-slate-900">
              Sites
            </h2>

            {sites.length === 0 ? (
              <NothingRecorded what="sites" />
            ) : (
              <>
                <FilterForm
                  query={query}
                  statuses={statusCounts(sites).flatMap((c) => (c.status ? [c.status] : []))}
                  councils={distinctLgas(
                    sites.map((s) => s.lga),
                    councils,
                  )}
                />

                <p className="text-sm text-slate-700" role="status">
                  {filtered
                    ? `${rows.length} of ${sites.length} sites match.`
                    : `${sites.length} sites.`}{' '}
                  {filtered && (
                    <Link
                      href={indexHref({ ...DEFAULT_QUERY, sort: query.sort, dir: query.dir })}
                      className="text-fact-ink underline underline-offset-2"
                    >
                      Clear filters
                    </Link>
                  )}
                </p>

                {rows.length > 0 && (
                  <div
                    className="overflow-x-auto"
                    tabIndex={0}
                    role="region"
                    aria-label="Sites"
                  >
                    <table className="w-full border-collapse text-sm">
                      <caption className="sr-only">
                        Data centre sites with operator, status, capacity and
                        council. Sortable by the column headings. Council names
                        are shown in their approved spelling; each site&rsquo;s
                        record page shows the spelling as recorded.
                      </caption>
                      <thead>
                        <tr className="border-b border-slate-300 text-left">
                          <SortHeader column={COLUMNS[0]!} query={query} />
                          <th scope="col" className="py-2 pr-4 font-semibold">
                            Operator
                          </th>
                          {COLUMNS.slice(1).map((column) => (
                            <SortHeader key={column.key} column={column} query={query} />
                          ))}
                        </tr>
                      </thead>
                      <tbody>
                        {rows.map((site) => {
                          const siteGaps = gapsBySite.get(site.id);
                          return (
                            <tr key={site.id} className="border-b border-slate-200">
                              <th scope="row" className="py-2 pr-4 text-left font-medium">
                                <Link
                                  href={`/sites/${site.id}`}
                                  className="text-fact-ink underline underline-offset-2"
                                >
                                  {site.name}
                                </Link>
                              </th>
                              <Cell value={site.operator} gap={siteGaps?.get('operator')} />
                              <Cell
                                value={formatSiteStatus(site.status)}
                                gap={siteGaps?.get('status')}
                              />
                              <Cell
                                value={formatMw(site.total_capacity_mw)}
                                gap={siteGaps?.get('total_capacity_mw')}
                              />
                              <Cell
                                value={resolveLga(site.lga, councils)?.display ?? null}
                                gap={siteGaps?.get('lga')}
                                last
                              />
                            </tr>
                          );
                        })}
                      </tbody>
                    </table>
                  </div>
                )}
              </>
            )}
          </section>

          <section aria-labelledby="entities-heading">
            <h2 id="entities-heading" className="text-lg font-semibold text-slate-900">
              Major entities
            </h2>

            {entities.length === 0 ? (
              <div className="mt-3">
                <NothingRecorded what="major entities" />
              </div>
            ) : (
              <ul className="mt-3 divide-y divide-slate-200 rounded-lg border border-slate-200">
                {entities.map((entity) => (
                  <li key={entity.id} className="px-4 py-3">
                    <Link
                      href={`/entities/${entity.id}`}
                      className="font-medium text-fact-ink underline underline-offset-2"
                    >
                      {entity.name}
                    </Link>
                    <p className="text-sm text-slate-700">
                      {[entity.type, entity.role].filter(Boolean).join(' · ') ||
                        'No type or role recorded'}
                    </p>
                  </li>
                ))}
              </ul>
            )}
          </section>
        </>
      )}
    </div>
  );
}

function FilterForm({
  query,
  statuses,
  councils,
}: {
  query: IndexQuery;
  statuses: NonNullable<IndexQuery['status']>[];
  councils: string[];
}) {
  const select =
    'mt-1 block w-full rounded border border-slate-300 bg-white px-2 py-1 text-sm sm:w-56';

  return (
    <form
      method="get"
      action="/list"
      className="flex flex-col gap-3 rounded-lg border border-fact-edge bg-fact-wash p-4 sm:flex-row sm:items-end"
    >
      {/* Carry the sort through a filter change. Defaults are left out of the URL. */}
      {query.sort !== DEFAULT_QUERY.sort && <input type="hidden" name="sort" value={query.sort} />}
      {query.dir !== DEFAULT_QUERY.dir && <input type="hidden" name="dir" value={query.dir} />}

      <label className="text-sm font-medium text-fact-ink">
        Status
        <select name="status" defaultValue={query.status ?? ''} className={select}>
          <option value="">Any status</option>
          {statuses.map((status) => (
            <option key={status} value={status}>
              {formatSiteStatus(status)}
            </option>
          ))}
        </select>
      </label>

      <label className="text-sm font-medium text-fact-ink">
        Council
        <select name="council" defaultValue={query.council ?? ''} className={select}>
          <option value="">Any council</option>
          {/* A council from a stale link is kept as an option, so the form
              shows the filter that is actually applied. */}
          {query.council && !councils.includes(query.council) && (
            <option value={query.council}>{query.council}</option>
          )}
          {councils.map((council) => (
            <option key={council} value={council}>
              {council}
            </option>
          ))}
        </select>
      </label>

      <button
        type="submit"
        className="rounded border border-fact-edge bg-white px-3 py-1 text-sm font-medium text-fact-ink"
      >
        Apply filters
      </button>
    </form>
  );
}

function SortHeader({
  column,
  query,
}: {
  column: { key: SortKey; label: string };
  query: IndexQuery;
}) {
  const active = query.sort === column.key;
  const sort = active ? (query.dir === 'asc' ? 'ascending' : 'descending') : 'none';

  return (
    <th scope="col" aria-sort={sort} className="py-2 pr-4 font-semibold">
      <Link
        href={sortHref(query, column.key)}
        className="inline-flex items-center gap-1 text-slate-900 underline-offset-4 hover:underline"
      >
        {column.label}
        <span className="sr-only">
          {active
            ? `, sorted ${sort}. Select to sort ${query.dir === 'asc' ? 'descending' : 'ascending'}`
            : ', select to sort'}
        </span>
        <span aria-hidden="true" className={active ? 'text-fact-ink' : 'text-slate-500'}>
          {active ? (query.dir === 'asc' ? '▲' : '▼') : '↕'}
        </span>
      </Link>
    </th>
  );
}

function Cell({
  value,
  gap,
  last = false,
}: {
  value: string | null;
  gap: DataGapRow | undefined;
  last?: boolean;
}) {
  return (
    <td className={last ? 'py-2' : 'py-2 pr-4'}>
      {value !== null ? value : gap ? <GapBadge reason={gap.reason} /> : <UnexplainedBadge />}
    </td>
  );
}
