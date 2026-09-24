import { describe, expect, it } from 'vitest';
import {
  applyIndexQuery,
  DEFAULT_QUERY,
  indexHref,
  parseIndexQuery,
  sortHref,
} from '@/lib/siteIndex';
import { site } from './helpers/site';

const none = new Map<string, string>();

describe('parseIndexQuery', () => {
  it('defaults to name, ascending, unfiltered', () => {
    expect(parseIndexQuery({})).toEqual(DEFAULT_QUERY);
  });

  it('reads a valid query', () => {
    expect(
      parseIndexQuery({ sort: 'capacity', dir: 'desc', status: 'approved', council: 'Penrith' }),
    ).toEqual({
      sort: 'capacity',
      dir: 'desc',
      status: 'approved',
      council: 'Penrith',
      evidence: null,
    });
  });

  it('falls back on anything unrecognised rather than failing', () => {
    expect(
      parseIndexQuery({ sort: 'price', dir: 'sideways', status: 'imagined', evidence: 'rumour' }),
    ).toEqual(DEFAULT_QUERY);
  });

  it('reads an evidence filter', () => {
    expect(parseIndexQuery({ evidence: 'claimed' }).evidence).toBe('claimed');
  });

  it('takes the first of a repeated param and ignores blanks', () => {
    expect(parseIndexQuery({ status: ['lodged', 'approved'], council: '  ' })).toMatchObject({
      status: 'lodged',
      council: null,
    });
  });
});

describe('indexHref and sortHref', () => {
  it('leaves defaults out of the URL', () => {
    expect(indexHref(DEFAULT_QUERY)).toBe('/list');
  });

  it('flips direction on the current column and starts a new one ascending', () => {
    const byCapacity = { ...DEFAULT_QUERY, sort: 'capacity' as const };
    expect(sortHref(byCapacity, 'capacity')).toBe('/list?sort=capacity&dir=desc');
    expect(sortHref({ ...byCapacity, dir: 'desc' }, 'capacity')).toBe('/list?sort=capacity');
    expect(sortHref(byCapacity, 'status')).toBe('/list?sort=status');
  });

  it('keeps filters when the sort changes', () => {
    expect(sortHref({ ...DEFAULT_QUERY, status: 'lodged' }, 'capacity')).toBe(
      '/list?sort=capacity&status=lodged',
    );
  });
});

describe('applyIndexQuery', () => {
  const sites = [
    site('1', { name: 'Charlie', total_capacity_mw: 50, status: 'operating', lga: 'Blacktown' }),
    site('2', { name: 'alpha', total_capacity_mw: null, status: 'rumoured' }),
    site('3', { name: 'Bravo', total_capacity_mw: 300, status: 'approved', lga: 'Blacktown City Council' }),
    site('4', { name: 'Delta', total_capacity_mw: 0, status: null, lga: 'Penrith' }),
  ];
  const names = (rows: { name: string }[]) => rows.map((r) => r.name);

  it('sorts names case-insensitively', () => {
    expect(names(applyIndexQuery(sites, DEFAULT_QUERY, none))).toEqual([
      'alpha',
      'Bravo',
      'Charlie',
      'Delta',
    ]);
  });

  it('puts unknown capacity last in both directions, and treats zero as known', () => {
    const asc = applyIndexQuery(sites, { ...DEFAULT_QUERY, sort: 'capacity' }, none);
    const desc = applyIndexQuery(sites, { ...DEFAULT_QUERY, sort: 'capacity', dir: 'desc' }, none);
    expect(names(asc)).toEqual(['Delta', 'Charlie', 'Bravo', 'alpha']);
    expect(names(desc)).toEqual(['Bravo', 'Charlie', 'Delta', 'alpha']);
  });

  it('sorts status by lifecycle, not alphabetically', () => {
    const rows = applyIndexQuery(sites, { ...DEFAULT_QUERY, sort: 'status' }, none);
    expect(names(rows)).toEqual(['alpha', 'Bravo', 'Charlie', 'Delta']);
  });

  it('filters on evidence, and keeps it in the URL', () => {
    const claimed = [
      site('1', { name: 'A', fact_status: 'claimed' }),
      site('2', { name: 'B', fact_status: 'verified' }),
    ];
    const query = { ...DEFAULT_QUERY, evidence: 'claimed' as const };
    expect(names(applyIndexQuery(claimed, query, none))).toEqual(['A']);
    expect(indexHref(query)).toBe('/list?evidence=claimed');
  });

  it('filters on status', () => {
    const rows = applyIndexQuery(sites, { ...DEFAULT_QUERY, status: 'approved' }, none);
    expect(names(rows)).toEqual(['Bravo']);
  });

  it('filters a council by its approved spelling, matching every recorded spelling', () => {
    const councils = new Map([['Blacktown', 'Blacktown City Council']]);
    const rows = applyIndexQuery(
      sites,
      { ...DEFAULT_QUERY, council: 'Blacktown City Council' },
      councils,
    );
    expect(names(rows)).toEqual(['Bravo', 'Charlie']);
  });

  it('returns nothing, rather than everything, for a council no site has', () => {
    expect(applyIndexQuery(sites, { ...DEFAULT_QUERY, council: 'Nowhere' }, none)).toEqual([]);
  });
});
