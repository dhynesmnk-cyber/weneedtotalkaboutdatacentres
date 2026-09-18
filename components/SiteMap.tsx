'use client';

import { MapContainer, TileLayer, CircleMarker, Popup } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import { MapPointPopup } from '@/components/MapPointPopup';
import type { SiteRow } from '@/lib/types';

/**
 * Single point layer over Australia.
 *
 * Leaflet with raster tiles and CircleMarker rather than image pins: no WebGL,
 * no marker icon assets to fetch, and a shape whose colour can carry status
 * without a sprite sheet. No GIS overlays — that is a v1 non-goal in
 * docs/SPEC.md, and this component deliberately has no layer control to grow
 * one into.
 *
 * The map is not the only way to reach this data. The map page renders a
 * keyboard-navigable list of the same sites alongside it.
 */

// Continental Australia, including Tasmania.
const AUSTRALIA_CENTRE: [number, number] = [-27.5, 134];
const DEFAULT_ZOOM = 4;

export function SiteMap({ sites }: { sites: SiteRow[] }) {
  return (
    <MapContainer
      center={AUSTRALIA_CENTRE}
      zoom={DEFAULT_ZOOM}
      scrollWheelZoom={false}
      className="h-[28rem] w-full rounded-lg border border-fact-edge"
      // The map is decorative relative to the list beside it; the list is the
      // accessible path to the same records.
      aria-hidden="true"
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
              <MapPointPopup site={site} />
            </Popup>
          </CircleMarker>
        ) : null,
      )}
    </MapContainer>
  );
}
