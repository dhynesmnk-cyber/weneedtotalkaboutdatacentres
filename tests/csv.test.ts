import { describe, expect, it } from 'vitest';
import { csvCell, csvFileName, guardFormula, toCsv } from '@/lib/csv';
import { entitiesCsv, researchCsv, sitesCsv, sourcesCsv } from '@/lib/dataExport';
import type { EntityRow, ResearchAgendaRow, SiteRow, SourceRow } from '@/lib/types';

describe('csvCell', () => {
  it('quotes commas, quotes and line breaks, and doubles quotes', () => {
    expect(csvCell('Kurri Kurri, Hart Road')).toBe('"Kurri Kurri, Hart Road"');
    expect(csvCell('the "phantom" demand')).toBe('"the ""phantom"" demand"');
    expect(csvCell('line one\nline two')).toBe('"line one\nline two"');
  });

  it('writes numbers as numbers, and a null as an empty field', () => {
    expect(csvCell(-33.875)).toBe('-33.875');
    expect(csvCell(0)).toBe('0');
    expect(csvCell(null)).toBe('');
    expect(csvCell(undefined)).toBe('');
    expect(csvCell(Number.NaN)).toBe('');
  });
});

describe('the formula-injection guard', () => {
  it('prefixes text a spreadsheet would run as a formula', () => {
    expect(guardFormula('=HYPERLINK("http://example.com")')).toBe(`'=HYPERLINK("http://example.com")`);
    expect(guardFormula('+61 2 0000 0000')).toBe(`'+61 2 0000 0000`);
    expect(guardFormula('-1 site')).toBe(`'-1 site`);
    expect(guardFormula('@SUM(A1)')).toBe(`'@SUM(A1)`);
    expect(guardFormula('\tcmd')).toBe(`'\tcmd`);
  });

  it('leaves ordinary text alone', () => {
    expect(guardFormula('NEXTDC S7')).toBe('NEXTDC S7');
  });

  it('guards inside a quoted field too', () => {
    expect(csvCell('=1+1, then more')).toBe(`"'=1+1, then more"`);
  });
});

describe('toCsv', () => {
  it('starts with a byte order mark and ends every line with CRLF', () => {
    expect(toCsv(['a', 'b'], [[1, 'x'], [null, 'y']])).toBe('﻿a,b\r\n1,x\r\n,y\r\n');
  });
});

describe('csvFileName', () => {
  it('names the dataset and the date of the load', () => {
    expect(csvFileName('sites', '2026-11-17T04:08:00Z')).toBe('datacentres-sites-2026-11-17.csv');
    expect(csvFileName('sites', null)).toBe('datacentres-sites-undated.csv');
  });
});

// A site row with every column, empty unless given.
function site(overrides: Partial<SiteRow>): SiteRow {
  const empty = Object.fromEntries(
    [
      'operator', 'lat', 'lng', 'lga', 'status', 'total_capacity_mw', 'live_capacity_mw', 'cooling_type',
      'rack_density_kw', 'grid_connection', 'water_usage', 'notes', 'fact_status', 'confidence', 'as_of_date',
      'pipeline_id', 'proponent', 'suburb', 'state', 'market', 'address', 'it_capacity_mw', 'max_capacity_mw',
      'first_phase_mw', 'campus_area_ha', 'gfa_sqm', 'capital_cost_aud', 'construction_jobs', 'operational_jobs',
      'operational_from', 'target_completion', 'hcf_certified',
    ].map((k) => [k, null]),
  );
  return { id: 'uuid-1', name: 'Test site', created_at: '', updated_at: '', ...empty, ...overrides } as SiteRow;
}

function parse(csv: string): string[][] {
  // Enough for these fixtures: no quoted commas in the cells read back.
  return csv.replace(/^﻿/, '').trimEnd().split('\r\n').map((l) => l.split(','));
}

describe('sitesCsv', () => {
  const csv = sitesCsv(
    [site({ pipeline_id: 'SITE_A', it_capacity_mw: 34.3, state: 'NSW' })],
    [
      { record_id: 'uuid-1', field_name: 'live_capacity_mw', reason: 'not_applicable' },
      { record_id: 'uuid-1', field_name: 'operator', reason: 'unknown' },
    ],
    new Map([['uuid-1', ['SRC_B', 'SRC_A']]]),
  );
  const [header, row] = parse(csv) as [string[], string[]];
  const col = (name: string) => row[header.indexOf(name)];

  it('puts a gap column beside every factual field', () => {
    expect(header.indexOf('it_capacity_mw_gap')).toBe(header.indexOf('it_capacity_mw') + 1);
    expect(header.filter((h) => h.endsWith('_gap')).length).toBeGreaterThan(20);
  });

  it('says why an empty value is empty, and nothing beside a value', () => {
    expect(col('live_capacity_mw')).toBe('');
    expect(col('live_capacity_mw_gap')).toBe('not_applicable');
    expect(col('operator_gap')).toBe('unknown');
    expect(col('it_capacity_mw')).toBe('34.3');
    expect(col('it_capacity_mw_gap')).toBe('');
  });

  it('never leaves a blank unexplained', () => {
    // No gap row for cooling_type: the derived default is the only reason a load may give.
    expect(col('cooling_type_gap')).toBe('unknown');
  });

  it('lists the sources by id, sorted', () => {
    expect(col('id')).toBe('SITE_A');
    expect(col('sources')).toBe('SRC_A; SRC_B');
  });
});

describe('the other files', () => {
  it('carry their ids, sources and grades', () => {
    const entity = { id: 'e1', pipeline_id: 'ENT_X', name: '[Founder and CEO, AirTrunk]', type: 'other', role: null, major_flag: false, public_actions_summary: null, fact_status: 'verified', confidence: 'high', as_of_date: null, created_at: '', updated_at: '' } as EntityRow;
    expect(entitiesCsv([entity], new Map([['e1', ['SRC_A']]]))).toContain('ENT_X,e1,"[Founder and CEO, AirTrunk]",other');

    const source = { id: 's1', pipeline_id: 'SRC_A', title: 'A report', publisher: 'A body', type: 'primary_government', credibility: 'A', url: 'https://example.org', retrieved_date: '2026-11-17', created_at: '', updated_at: '' } as SourceRow;
    expect(sourcesCsv([source])).toContain('SRC_A,s1,A report,A body,primary_government,A,https://example.org,2026-11-17');

    const question = { id: 'q1', pipeline_id: 'RG-101', status: 'in_progress', pillar: 'C', priority: 3, question: 'Where are they?', why_it_matters: null, target_source: null, retrieval_method: 'manual_review', opened: '2026-11-15', resolved_date: null, notes: null, fact_status: 'verified', confidence: 'high', as_of_date: null, created_at: '', updated_at: '' } as ResearchAgendaRow;
    expect(researchCsv([question], new Map([['q1', ['SRC_A']]]))).toContain('RG-101,q1,in_progress,C,3,Where are they?');
  });
});
