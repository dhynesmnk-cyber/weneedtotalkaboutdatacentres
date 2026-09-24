import Link from 'next/link';
import { listSites } from '@/lib/sites';
import { listGaps } from '@/lib/evidence';
import { lastLoadedAt, siteCoverage } from '@/lib/coverage';
import { isConfigured } from '@/lib/supabase/server';
import { formatFieldName, formatGapReason } from '@/lib/format';
import { GAP_REASONS, type GapReason } from '@/lib/types';
import { NotConnected, NothingRecorded } from '@/components/NotConnected';
import { DateStamp } from '@/components/DateStamp';

export const dynamic = 'force-dynamic';
export const metadata = { title: 'Coverage' };

/**
 * What is known for every site field.
 *
 * The gaps are a finding, so this page publishes them as one: for each field,
 * how many sites hold a value, how many carry a gap and why, and how many
 * have neither. It is a table first because there are too many fields for a
 * chart to carry, and the numbers are what a reader will quote.
 *
 * A gap reason column appears only once some gap carries that reason, so the
 * table does not fill with columns of zeroes. The "no explanation" column is
 * always shown: its being zero is itself the claim that every blank is
 * accounted for.
 */
export default async function CoveragePage() {
  const [sites, gaps, loadedAt] = await Promise.all([
    listSites(),
    listGaps('sites'),
    lastLoadedAt(),
  ]);
  const rows = siteCoverage(sites, gaps);
  const reasons: GapReason[] = GAP_REASONS.filter((r) => rows.some((row) => row.gaps[r] > 0));

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-bold text-slate-900">Coverage</h1>
        <p className="mt-2 max-w-2xl text-slate-700">
          For every field the observatory records about a site: how many sites
          hold a sourced value, how many carry a gap and why, and how many have
          neither. A blank with no stated reason is a defect in the record and
          is counted separately.
        </p>
        <DateStamp dataAsOfDate={loadedAt} className="mt-2" />
      </div>

      {!isConfigured() ? (
        <NotConnected what="sites" />
      ) : sites.length === 0 ? (
        <NothingRecorded what="sites" />
      ) : (
        // Focusable so the table can be scrolled by keyboard at narrow widths:
        // it holds no links, so nothing inside it would otherwise take focus.
        <div
          className="overflow-x-auto"
          tabIndex={0}
          role="region"
          aria-label="Coverage by field"
        >
          <table className="w-full border-collapse text-sm">
            <caption className="mb-3 text-left text-slate-700">
              {sites.length} sites. Each row adds up to {sites.length}.
            </caption>
            <thead>
              <tr className="border-b border-slate-300 text-left align-bottom">
                <th scope="col" className="py-2 pr-4 font-semibold">Field</th>
                <th scope="col" className="py-2 pr-4 text-right font-semibold">Recorded</th>
                <th scope="col" className="hidden py-2 pr-4 font-semibold sm:table-cell">
                  <span className="sr-only">Share recorded</span>
                </th>
                {reasons.map((reason) => (
                  <th key={reason} scope="col" className="py-2 pr-4 text-right font-semibold">
                    {formatGapReason(reason)}
                  </th>
                ))}
                <th scope="col" className="py-2 text-right font-semibold">No explanation</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((row) => (
                <tr key={row.field} className="border-b border-slate-200">
                  <th scope="row" className="py-2 pr-4 text-left font-medium">
                    {row.label ?? formatFieldName(row.field)}
                  </th>
                  <td className="py-2 pr-4 text-right tabular-nums">{row.known}</td>
                  <td className="hidden w-40 py-2 pr-4 sm:table-cell">
                    <div aria-hidden="true" className="h-2 w-full rounded-full bg-fact-edge/60">
                      {row.known > 0 && (
                        <div
                          className="h-2 rounded-full bg-fact-ink"
                          style={{
                            width: `max(${((row.known / row.total) * 100).toFixed(1)}%, 0.5rem)`,
                          }}
                        />
                      )}
                    </div>
                  </td>
                  {reasons.map((reason) => (
                    <td key={reason} className="py-2 pr-4 text-right tabular-nums text-gap-ink">
                      {row.gaps[reason]}
                    </td>
                  ))}
                  <td
                    data-unexplained={row.unexplained > 0 ? '' : undefined}
                    className={`py-2 text-right tabular-nums ${
                      row.unexplained > 0 ? 'font-semibold text-red-800' : 'text-slate-600'
                    }`}
                  >
                    {row.unexplained}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      <p className="text-sm text-slate-700">
        Each site&rsquo;s record page shows its values with their sources. Browse
        the sites in{' '}
        <Link href="/list" className="text-fact-ink underline underline-offset-2">
          the full index
        </Link>
        .
      </p>
    </div>
  );
}
