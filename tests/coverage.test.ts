import { describe, expect, it } from 'vitest';
import { siteCoverage, statusCounts, SITE_COVERAGE_FIELDS } from '@/lib/coverage';
import { gapsByRecord } from '@/lib/evidence';
import { gap, site } from './helpers/site';

const only = (field: string) => SITE_COVERAGE_FIELDS.filter((f) => f.field === field);

describe('siteCoverage', () => {
  it('counts values, gaps by reason, and unexplained blanks separately', () => {
    const sites = [
      site('a', { operator: 'Operator A' }),
      site('b'),
      site('c'),
      site('d'),
    ];
    const gaps = [gap('b', 'operator', 'unknown'), gap('c', 'operator', 'not_disclosed')];

    const [operator] = siteCoverage(sites, gaps, only('operator'));
    expect(operator).toMatchObject({
      field: 'operator',
      known: 1,
      unexplained: 1,
      total: 4,
      gaps: { unknown: 1, not_disclosed: 1, not_applicable: 0, withheld: 0 },
    });
  });

  it('counts a field holding both a value and a gap as known, as the site page does', () => {
    const [operator] = siteCoverage(
      [site('a', { operator: 'Operator A' })],
      [gap('a', 'operator')],
      only('operator'),
    );
    expect(operator?.known).toBe(1);
    expect(operator?.gaps.unknown).toBe(0);
  });

  it('never counts a gap recorded against a different field', () => {
    const [operator] = siteCoverage([site('a')], [gap('a', 'proponent')], only('operator'));
    expect(operator?.unexplained).toBe(1);
  });

  it('treats coordinates as one field, known only when both halves are present', () => {
    const [coords] = siteCoverage(
      [site('a', { lat: -33.8, lng: 151.2 }), site('b'), site('c')],
      [gap('b', 'lat')],
      only('lat'),
    );
    expect(coords).toMatchObject({ label: 'Coordinates', known: 1, unexplained: 1 });
    expect(coords?.gaps.unknown).toBe(1);
  });

  it('treats zero as a value, not a gap', () => {
    const [capacity] = siteCoverage(
      [site('a', { total_capacity_mw: 0 })],
      [],
      only('total_capacity_mw'),
    );
    expect(capacity?.known).toBe(1);
  });

  it('does not count a stored "unknown" as recorded, nor as an unexplained blank', () => {
    const [hcf] = siteCoverage(
      [
        site('a', { hcf_certified: 'certified_strategic' }),
        site('b', { hcf_certified: 'unknown' }),
        site('c'),
      ],
      [gap('c', 'hcf_certified')],
      only('hcf_certified'),
    );
    expect(hcf).toMatchObject({ known: 1, unexplained: 0 });
    expect(hcf?.gaps.unknown).toBe(2);
  });

  it('adds up to the number of sites for every field', () => {
    const sites = [site('a', { status: 'operating' }), site('b')];
    for (const f of siteCoverage(sites, [gap('b', 'status')])) {
      const gaps = Object.values(f.gaps).reduce((sum, n) => sum + n, 0);
      expect(f.known + gaps + f.unexplained).toBe(sites.length);
    }
  });
});

describe('statusCounts', () => {
  it('lists statuses in lifecycle order, not by size, with no status last', () => {
    const counts = statusCounts([
      site('a', { status: 'operating' }),
      site('b', { status: 'operating' }),
      site('c', { status: 'rumoured' }),
      site('d'),
      site('e', { status: 'approved' }),
    ]);
    expect(counts).toEqual([
      { status: 'rumoured', count: 1 },
      { status: 'approved', count: 1 },
      { status: 'operating', count: 2 },
      { status: null, count: 1 },
    ]);
  });
});

describe('gapsByRecord', () => {
  it('groups gaps by record and then by field', () => {
    const grouped = gapsByRecord([gap('a', 'operator'), gap('a', 'lga'), gap('b', 'lga')]);
    expect([...grouped.keys()]).toEqual(['a', 'b']);
    expect([...grouped.get('a')!.keys()]).toEqual(['operator', 'lga']);
  });
});
