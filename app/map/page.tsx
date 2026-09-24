import dynamicImport from 'next/dynamic';
import Link from 'next/link';
import { listMappableSites, listSites } from '@/lib/sites';
import { listLgaAliases } from '@/lib/councils';
import { isConfigured } from '@/lib/supabase/server';
import { NotConnected, NothingRecorded } from '@/components/NotConnected';
import { formatMw, formatSiteStatus } from '@/lib/format';

export const dynamic = 'force-dynamic';

// Leaflet touches window on import, so the map is client-only.
const SiteMap = dynamicImport(
  () => import('@/components/SiteMap').then((m) => m.SiteMap),
  {
    ssr: false,
    loading: () => (
      <div className="h-[28rem] w-full rounded-lg border border-fact-edge bg-fact-wash" />
    ),
  },
);

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
  const [mappable, all, aliases] = await Promise.all([
    listMappableSites(),
    listSites(),
    listLgaAliases(),
  ]);
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
          <SiteMap sites={mappable} aliases={aliases} />

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
              Sites on this map
            </h2>
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
