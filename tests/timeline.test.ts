import { describe, expect, it } from 'vitest';
import { parseTracks, serialiseTracks } from '@/lib/timeline';
import { groupEventsByYear } from '@/lib/events';
import { EVENT_CATEGORIES, type EventRow } from '@/lib/types';

function event(id: string, date: string): EventRow {
  return {
    id,
    category: 'planning',
    date,
    title: `Event ${id}`,
    summary: null,
    site_id: null,
    created_at: '2026-09-18T00:00:00Z',
    updated_at: '2026-09-18T00:00:00Z',
  };
}

describe('parseTracks', () => {
  it('defaults to every track when the param is absent', () => {
    expect(parseTracks(undefined)).toEqual([...EVENT_CATEGORIES]);
  });

  it('parses a comma separated selection', () => {
    expect(parseTracks('planning,community')).toEqual(['planning', 'community']);
  });

  it('returns tracks in canonical order regardless of URL order', () => {
    expect(parseTracks('community,planning')).toEqual(['planning', 'community']);
  });

  it('ignores unrecognised values rather than failing', () => {
    expect(parseTracks('planning,nonsense')).toEqual(['planning']);
  });

  it('falls back to every track when nothing valid remains', () => {
    // A malformed link must never silently hide events.
    expect(parseTracks('nonsense,rubbish')).toEqual([...EVENT_CATEGORIES]);
    expect(parseTracks('')).toEqual([...EVENT_CATEGORIES]);
  });

  it('tolerates whitespace and repeated array params', () => {
    expect(parseTracks(' planning , media ')).toEqual(['planning', 'media']);
    expect(parseTracks(['planning', 'media'])).toEqual(['planning', 'media']);
  });
});

describe('serialiseTracks', () => {
  it('returns null when everything is selected, keeping the URL clean', () => {
    expect(serialiseTracks([...EVENT_CATEGORIES])).toBeNull();
  });

  it('returns null when nothing is selected, which means all', () => {
    expect(serialiseTracks([])).toBeNull();
  });

  it('round-trips a partial selection', () => {
    const selection = serialiseTracks(['planning', 'financial']);
    expect(selection).toBe('planning,financial');
    expect(parseTracks(selection ?? undefined)).toEqual(['planning', 'financial']);
  });
});

describe('groupEventsByYear', () => {
  it('groups events and orders years newest first', () => {
    const grouped = groupEventsByYear([
      event('a', '2024-03-01'),
      event('b', '2026-01-15'),
      event('c', '2025-07-20'),
    ]);

    expect(grouped.map((g) => g.year)).toEqual([2026, 2025, 2024]);
  });

  it('orders events within a year newest first', () => {
    const grouped = groupEventsByYear([
      event('a', '2026-01-15'),
      event('b', '2026-09-18'),
      event('c', '2026-05-02'),
    ]);

    expect(grouped[0]?.events.map((e) => e.id)).toEqual(['b', 'c', 'a']);
  });

  it('returns nothing for no events', () => {
    expect(groupEventsByYear([])).toEqual([]);
  });

  it('skips an unparseable date rather than bucketing it under NaN', () => {
    const grouped = groupEventsByYear([event('a', 'not-a-date'), event('b', '2026-01-01')]);
    expect(grouped).toHaveLength(1);
    expect(grouped[0]?.year).toBe(2026);
  });
});
