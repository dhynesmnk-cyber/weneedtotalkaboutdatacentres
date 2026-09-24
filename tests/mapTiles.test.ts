import { describe, expect, it } from 'vitest';
import { mapTiles, OSM_TILES } from '@/lib/mapTiles';

describe('mapTiles', () => {
  it('defaults to OpenStreetMap', () => {
    expect(mapTiles({})).toEqual(OSM_TILES);
    expect(mapTiles({ MAP_TILE_URL: ' ' })).toEqual(OSM_TILES);
  });

  it('uses a configured provider with its attribution', () => {
    expect(
      mapTiles({ MAP_TILE_URL: 'https://tiles.example/{z}/{x}/{y}.png', MAP_TILE_ATTRIBUTION: '© Example' }),
    ).toEqual({ url: 'https://tiles.example/{z}/{x}/{y}.png', attribution: '© Example' });
  });

  it('refuses a provider with no attribution rather than dropping the credit', () => {
    expect(() => mapTiles({ MAP_TILE_URL: 'https://tiles.example/{z}/{x}/{y}.png' })).toThrow(
      /MAP_TILE_ATTRIBUTION/,
    );
  });
});
