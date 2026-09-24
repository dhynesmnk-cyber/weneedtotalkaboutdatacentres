'use client';

import { MapContainer, TileLayer, CircleMarker, Popup } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import { MapPointPopup } from '@/components/MapPointPopup';
import { aliasMap, resolveLga } from '@/lib/councils';
import type { LgaAliasRow, SiteRow } from '@/lib/types';

/**
 * Single point layer over Australia.
 *
 * Leaflet with raster tiles and CircleMarker rather than image pins: no WebGL,
 * no marker icon assets to fetch, and a shape whose colour can carry status
 * without a sprite sheet. No GIS overlays — that is a v1 non-goal in
 * docs/SPEC.md, and this component deliberately has no layer control to grow
 * one into.
 *
 * The map is not the only way to reach this data. Its points are SVG paths
 * that cannot take keyboard focus, so the map page renders a list of the
 * same sites alongside it as the accessible path. The map is deliberately
 * not hidden from assistive technology: its zoom controls are focusable, and
 * hiding focusable controls is itself an accessibility failure.
 *
 * Browser only. Import it through SiteMapLoader, never directly from a server
 * component.
 */

// Continental Australia, including Tasmania.
const AUSTRALIA_CENTRE: [number, number] = [-27.5, 134];
const DEFAULT_ZOOM = 4;

export function SiteMap({
  sites,
  aliases = [],
}: {
  sites: SiteRow[];
  /**
   * Approved council equivalences. Passed as rows rather than a Map because
   * this is a client component and the props cross a serialisation boundary.
   */
  aliases?: LgaAliasRow[];
}) {
  const councils = aliasMap(aliases);

  return (
    <MapContainer
      center={AUSTRALIA_CENTRE}
      zoom={DEFAULT_ZOOM}
      scrollWheelZoom={false}
      className="h-[28rem] w-full rounded-lg border border-fact-edge"
    >
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        url="https://tile.openstreetmap.org/{z}/{x}/{y}.png"
      />

      {sites.map((site) =>
        site.lat !== null && site.lng !== null ? (
          <CircleMarker
            key={site.id}
            center={[site.lat, site.lng]}
            radius={7}
            pathOptions={{
              color: '#24405e',
              fillColor: '#24405e',
              fillOpacity: 0.7,
              weight: 2,
            }}
          >
            <Popup>
              <MapPointPopup site={site} council={resolveLga(site.lga, councils)?.display ?? null} />
            </Popup>
          </CircleMarker>
        ) : null,
      )}
    </MapContainer>
  );
}
