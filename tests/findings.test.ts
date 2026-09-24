import { describe, expect, it } from 'vitest';
import { evidenceCounts, largestCapacity, topCouncil } from '@/lib/findings';
import { site } from './helpers/site';

describe('largestCapacity', () => {
  it('names the largest recorded total capacity and how many sites have one', () => {
    const result = largestCapacity([
      site('a', { name: 'Small', total_capacity_mw: 45 }),
      site('b', { name: 'Big', total_capacity_mw: 3240 }),
      site('c', { name: 'Unknown' }),
    ]);
    expect(result).toEqual({ site: { id: 'b', name: 'Big' }, mw: 3240, of: 2 });
  });

  it('says nothing when no capacity is recorded', () => {
    expect(largestCapacity([site('a')])).toBeNull();
  });
});

describe('topCouncil', () => {
  const aliases = new Map([['Blacktown', 'Blacktown City Council']]);

  it('counts a council in its approved spelling, across every recorded spelling', () => {
    const result = topCouncil(
      [
        site('1', { lga: 'Blacktown' }),
        site('2', { lga: 'Blacktown City Council' }),
        site('3', { lga: 'Penrith' }),
      ],
      aliases,
    );
    expect(result).toEqual({ council: 'Blacktown City Council', count: 2, runnerUp: 1 });
  });

  it('names no council when two tie for first', () => {
    expect(topCouncil([site('1', { lga: 'Ryde' }), site('2', { lga: 'Penrith' })], aliases)).toBeNull();
  });

  it('does not count a cell naming two councils for either', () => {
    const result = topCouncil(
      [site('1', { lga: 'Penrith; Blacktown' }), site('2', { lga: 'Ryde' })],
      aliases,
    );
    expect(result).toEqual({ council: 'Ryde', count: 1, runnerUp: 0 });
  });
});

describe('evidenceCounts', () => {
  it('orders strongest first, with unrated sites last', () => {
    expect(
      evidenceCounts([
        site('1', { fact_status: 'claimed' }),
        site('2', { fact_status: 'verified' }),
        site('3', { fact_status: 'verified' }),
        site('4'),
      ]),
    ).toEqual([
      { status: 'verified', count: 2 },
      { status: 'claimed', count: 1 },
      { status: null, count: 1 },
    ]);
  });
});
