import { describe, expect, it } from 'vitest';
import { ariaCurrent, isCurrent, NAV_GROUPS } from '@/lib/nav';

describe('navigation', () => {
  it('keeps the record and the analysis in separate groups', () => {
    const record = NAV_GROUPS.find((g) => g.id === 'record')?.items.map((i) => i.href);
    const analysis = NAV_GROUPS.find((g) => g.id === 'analysis')?.items.map((i) => i.href);
    expect(record).toEqual(['/map', '/list', '/coverage', '/research']);
    expect(analysis).toEqual(['/essays']);
  });

  it('marks the overview only on the home page', () => {
    expect(isCurrent('/', '/')).toBe(true);
    expect(isCurrent('/', '/map')).toBe(false);
  });

  it('marks the index as the location on a site or entity record', () => {
    expect(ariaCurrent('/list', '/list')).toBe('page');
    expect(ariaCurrent('/list', '/sites/abc')).toBe('location');
    expect(ariaCurrent('/list', '/entities/abc')).toBe('location');
  });

  it('places case studies under the analysis, not the record', () => {
    expect(ariaCurrent('/essays', '/case-studies/abc')).toBe('location');
    expect(ariaCurrent('/list', '/case-studies/abc')).toBeUndefined();
  });

  it('does not match a path that merely shares a prefix', () => {
    expect(isCurrent('/map', '/mapping')).toBe(false);
  });
});
