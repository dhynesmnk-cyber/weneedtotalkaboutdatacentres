import { describe, expect, it } from 'vitest';
import {
  formatAud,
  formatAudCompact,
  formatDate,
  formatFieldName,
  formatGapReason,
  formatMegalitres,
  formatMw,
  formatPct,
  formatSiteStatus,
} from '@/lib/format';

/**
 * Australian English and Australian conventions throughout, per CLAUDE.md.
 *
 * Every formatter returns null for a missing value rather than an em dash, so
 * that the caller has to decide what to show. A formatter that quietly renders
 * "—" would let a gap slip onto the page without a stated reason.
 */

describe('formatDate', () => {
  it('uses day month year', () => {
    expect(formatDate('2026-09-18')).toBe('18 September 2026');
  });

  it('does not shift the day across time zones', () => {
    // A date-only string read as local time can land on the previous day west
    // of UTC. This must stay stable wherever it runs.
    expect(formatDate('2026-01-01')).toBe('1 January 2026');
    expect(formatDate('2026-12-31')).toBe('31 December 2026');
  });

  it('returns null for missing or invalid input', () => {
    expect(formatDate(null)).toBeNull();
    expect(formatDate(undefined)).toBeNull();
    expect(formatDate('')).toBeNull();
    expect(formatDate('not a date')).toBeNull();
  });
});

describe('currency', () => {
  it('formats whole dollars', () => {
    expect(formatAud(1_200_000)).toBe('$1,200,000');
  });

  it('formats billions compactly', () => {
    expect(formatAudCompact(31_900_000_000)).toBe('$31.9 billion');
  });

  it('formats millions compactly', () => {
    expect(formatAudCompact(415_000_000)).toBe('$415 million');
  });

  it('falls back to full figures below a million', () => {
    expect(formatAudCompact(5_000)).toBe('$5,000');
  });

  it('returns null rather than $0 for a missing figure', () => {
    expect(formatAud(null)).toBeNull();
    expect(formatAudCompact(undefined)).toBeNull();
  });

  it('formats a genuine zero, which is not the same as missing', () => {
    expect(formatAud(0)).toBe('$0');
  });
});

describe('units', () => {
  it('formats megawatts', () => {
    expect(formatMw(550)).toBe('550 MW');
    expect(formatMw(1200)).toBe('1,200 MW');
  });

  it('formats megalitres', () => {
    expect(formatMegalitres(22.4)).toBe('22.4 ML');
  });

  it('formats percentages', () => {
    expect(formatPct(8.5)).toBe('8.5%');
  });

  it('returns null for missing values', () => {
    expect(formatMw(null)).toBeNull();
    expect(formatPct(null)).toBeNull();
    expect(formatMegalitres(null)).toBeNull();
  });
});

describe('labels', () => {
  it('renders site statuses in sentence case', () => {
    expect(formatSiteStatus('under_construction')).toBe('Under construction');
    expect(formatSiteStatus('stalled')).toBe('Stalled');
  });

  it('returns null for an absent status', () => {
    expect(formatSiteStatus(null)).toBeNull();
  });

  it('gives every gap reason reader-facing wording', () => {
    expect(formatGapReason('unknown')).toBe('Not yet researched');
    expect(formatGapReason('not_disclosed')).toBe('Not disclosed');
    expect(formatGapReason('not_applicable')).toBe('Not applicable');
    expect(formatGapReason('withheld')).toBe('Withheld in source');
  });
});

describe('formatFieldName', () => {
  it('strips unit suffixes, which belong with the value', () => {
    expect(formatFieldName('total_capacity_mw')).toBe('Total capacity');
    expect(formatFieldName('rack_density_kw')).toBe('Rack density');
    expect(formatFieldName('total_capex_aud')).toBe('Total capex');
    expect(formatFieldName('development_yield_pct')).toBe('Development yield');
  });

  it('handles single-word fields', () => {
    expect(formatFieldName('operator')).toBe('Operator');
  });

  it('returns the input unchanged when there is nothing to format', () => {
    expect(formatFieldName('')).toBe('');
  });
});
