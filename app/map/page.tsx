import Link from 'next/link';
import { SiteMapLoader } from '@/components/SiteMapLoader';
import { listMappableSites, listSites } from '@/lib/sites';
import { listLgaAliases } from '@/lib/councils';
import { gapsByRecord, listGaps } from '@/lib/evidence';
import type { PopupGaps } from '@/components/MapPointPopup';
import { isConfigured } from '@/lib/supabase/server';
import { NotConnected, NothingRecorded } from '@/components/NotConnected';
import { formatMw, formatSiteStatus } from '@/lib/format';

export const dynamic = 'force-dynamic';

export const metadata = { title: 'Map' };

/**
 * Point map. A single layer, per the v1 non-goal on GIS overlays.
 *
 * The list below the map is not a fallback, it is the accessible equivalent:
 * the same records, reachable by keyboard, and it also states how many sites
 * have no coordinates so their absence from the map is not read as absence
 * from the record.
 */
export default async function MapPage() {
  const [mappable, all, aliases, gaps] = await Promise.all([
    listMappableSites(),
    listSites(),
    listLgaAliases(),
    listGaps('sites'),
  ]);
  const popupGaps = popupGapsFor(mappable, gapsByRecord(gaps));
  const withoutCoords = all.length - mappable.length;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900">Map</h1>
        <p className="mt-2 max-w-2xl text-slate-700">
          Every site with recorded coordinates, as a single point layer.
        </p>
      </div>

      {!isConfigured() ? (
        <NotConnected what="sites" />
      ) : all.length === 0 ? (
        <NothingRecorded what="sites" />
      ) : (
        <>
          <section aria-labelledby="map-heading">
            <h2 id="map-heading" className="sr-only">
              Map of sites with recorded coordinates
            </h2>
            <p className="sr-only">
              The map&rsquo;s points cannot be reached by keyboard. The list of all
              sites below holds the same records.
            </p>
            <SiteMapLoader sites={mappable} aliases={aliases} gaps={popupGaps} />
          </section>

          {withoutCoords > 0 && (
            <p className="rounded border border-gap-edge bg-gap-wash px-3 py-2 text-sm text-gap-ink">
              {withoutCoords} {withoutCoords === 1 ? 'site is' : 'sites are'} not
              shown because no coordinates have been recorded. They appear in the
              list below and in{' '}
              <Link href="/list" className="underline underline-offset-2">
                the full index
              </Link>
              .
            </p>
          )}

          <section aria-labelledby="map-list-heading">
            <h2 id="map-list-heading" className="text-lg font-semibold text-slate-900">
              All sites
            </h2>
            <p className="mt-1 text-sm text-slate-600">
              Every recorded site, including those not on the map. {mappable.length}{' '}
              of {all.length} {all.length === 1 ? 'has' : 'have'} coordinates.
            </p>
            <ul className="mt-3 divide-y divide-slate-200 rounded-lg border border-slate-200">
              {all.map((site) => (
                <li key={site.id} className="px-4 py-3">
                  <Link
                    href={`/sites/${site.id}`}
                    className="font-medium text-fact-ink underline underline-offset-2"
                  >
                    {site.name}
                  </Link>
                  <p className="text-sm text-slate-700">
                    {[
                      site.operator,
                      formatSiteStatus(site.status),
                      formatMw(site.total_capacity_mw),
                      site.lat === null ? 'No coordinates recorded' : null,
                    ]
                      .filter(Boolean)
                      .join(' · ')}
                  </p>
                </li>
              ))}
            </ul>
          </section>
        </>
      )}
    </div>
  );
}

/**
 * The gaps a popup shows, for the sites that can be drawn. Only those cross
 * to the browser: the map has no use for the rest, and every gap sent is
 * page weight.
 */
function popupGapsFor(
  sites: { id: string }[],
  bySite: ReturnType<typeof gapsByRecord>,
): Record<string, PopupGaps> {
  const fields = ['operator', 'status', 'total_capacity_mw', 'lga'] as const;
  const out: Record<string, PopupGaps> = {};
  for (const site of sites) {
    const recorded = bySite.get(site.id);
    if (!recorded) continue;
    const entry: PopupGaps = {};
    for (const field of fields) {
      const gap = recorded.get(field);
      if (gap) entry[field] = gap.reason;
    }
    out[site.id] = entry;
  }
  return out;
}
