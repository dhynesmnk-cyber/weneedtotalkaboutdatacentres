/**
 * Where the map's base tiles come from.
 *
 * OpenStreetMap's own tile servers are the default because they need no
 * account, but their usage policy is for light use and they are not a
 * production tile service. Before launch set MAP_TILE_URL (a Leaflet URL
 * template) and MAP_TILE_ATTRIBUTION to a provider chosen for it; the
 * attribution is whatever that provider's terms require.
 *
 * Read on the server at request time, not inlined at build, so a provider can
 * be changed in the host's environment without a rebuild.
 */

export interface MapTiles {
  readonly url: string;
  readonly attribution: string;
}

export const OSM_TILES: MapTiles = {
  url: 'https://tile.openstreetmap.org/{z}/{x}/{y}.png',
  attribution:
    '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
};

export function mapTiles(env: Record<string, string | undefined> = process.env): MapTiles {
  const url = env['MAP_TILE_URL']?.trim();
  if (!url) return OSM_TILES;
  // A provider without attribution would breach most tile licences, so a URL
  // alone is not accepted silently.
  const attribution = env['MAP_TILE_ATTRIBUTION']?.trim();
  if (!attribution) {
    throw new Error('MAP_TILE_URL is set without MAP_TILE_ATTRIBUTION. Set both.');
  }
  return { url, attribution };
}
