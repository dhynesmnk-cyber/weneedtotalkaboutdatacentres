import { describe, expect, it } from 'vitest';
import { citationCoverage, gapsByField, resolveField } from '@/lib/evidence';
import type { CitationWithSource, DataGapRow } from '@/lib/types';

function gap(field: string, reason: DataGapRow['reason'] = 'unknown'): DataGapRow {
  return {
    id: `gap-${field}`,
    record_type: 'sites',
    record_id: 'site-1',
    field_name: field,
    reason,
    noted_date: '2026-09-18',
    source_id: null,
    created_at: '2026-09-18T00:00:00Z',
  };
}

function citation(claim: string | null): CitationWithSource {
  return {
    id: `cite-${claim ?? 'none'}`,
    source_id: 'source-1',
    record_type: 'sites',
    record_id: 'site-1',
    claim,
    created_at: '2026-09-18T00:00:00Z',
    source: null,
  };
}

describe('resolveField', () => {
  const gaps = gapsByField([gap('water_usage', 'not_disclosed')]);

  it('reports a present value', () => {
    const result = resolveField('operator', 'NEXTDC', gaps);
    expect(result.value).toBe('NEXTDC');
    expect(result.gap).toBeNull();
    expect(result.unexplained).toBe(false);
  });

  it('reports a stated gap with its reason', () => {
    const result = resolveField('water_usage', null, gaps);
    expect(result.value).toBeNull();
    expect(result.gap).toBe('not_disclosed');
    expect(result.unexplained).toBe(false);
  });

  it('flags a blank with no recorded gap as unexplained', () => {
    const result = resolveField('cooling_type', null, gaps);
    expect(result.gap).toBeNull();
    expect(result.unexplained).toBe(true);
  });

  it('treats an empty string as absent, not as a value', () => {
    expect(resolveField('operator', '', gaps).unexplained).toBe(true);
  });

  it('treats undefined the same as null', () => {
    expect(resolveField('operator', undefined, gaps).unexplained).toBe(true);
  });

  it('prefers the recorded value when a gap also exists for that field', () => {
    // A field that has both is a data defect, but showing the value is the
    // safer of the two: it is checkable against the sources.
    const result = resolveField('water_usage', '22.4 ML', gaps);
    expect(result.value).toBe('22.4 ML');
    expect(result.unexplained).toBe(false);
  });

  it('does not treat zero as absent', () => {
    const result = resolveField('water_usage', 0, gaps);
    expect(result.value).toBe(0);
    expect(result.unexplained).toBe(false);
  });
});

describe('gapsByField', () => {
  it('keys gaps by field name', () => {
    const map = gapsByField([gap('operator'), gap('lga', 'withheld')]);
    expect(map.get('lga')?.reason).toBe('withheld');
    expect(map.size).toBe(2);
  });

  it('returns an empty map for no gaps', () => {
    expect(gapsByField([]).size).toBe(0);
  });
});

describe('citationCoverage', () => {
  const gaps = gapsByField([]);

  it('counts a populated field as cited when a citation names it', () => {
    const fields = [
      resolveField('operator', 'NEXTDC', gaps),
      resolveField('status', 'proposed', gaps),
    ];

    const coverage = citationCoverage(fields, [
      citation('operator'),
      citation('status'),
    ]);

    expect(coverage).toEqual({ cited: 2, total: 2, uncited: [] });
  });

  it('names the populated fields that no citation supports', () => {
    const fields = [
      resolveField('operator', 'NEXTDC', gaps),
      resolveField('status', 'proposed', gaps),
    ];

    const coverage = citationCoverage(fields, [citation('operator')]);

    expect(coverage.cited).toBe(1);
    expect(coverage.uncited).toEqual(['status']);
  });

  it('does not count gaps against coverage', () => {
    const fields = [
      resolveField('operator', 'NEXTDC', gaps),
      resolveField('water_usage', null, gaps),
    ];

    const coverage = citationCoverage(fields, [citation('operator')]);

    expect(coverage.total).toBe(1);
    expect(coverage.uncited).toEqual([]);
  });

  it('ignores citations with no named claim when attributing coverage', () => {
    const fields = [resolveField('operator', 'NEXTDC', gaps)];
    const coverage = citationCoverage(fields, [citation(null)]);

    expect(coverage.cited).toBe(0);
    expect(coverage.uncited).toEqual(['operator']);
  });
});
