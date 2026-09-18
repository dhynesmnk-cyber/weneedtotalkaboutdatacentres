import { describe, expect, it } from 'vitest';
import {
  parseCapacityCsv,
  parseCsv,
  parseNumber,
  type ColumnMapping,
} from '@/scripts/ingestion/parse-capacity-csv';

const mapping: ColumnMapping = {
  name: 'Station',
  operator: 'Owner',
  lga: 'Council',
  status: 'Status',
  totalCapacityMw: 'Capacity (MW)',
  liveCapacityMw: 'Live (MW)',
};

const header = 'Station,Owner,Council,Status,Capacity (MW),Live (MW)';

describe('parseCsv', () => {
  it('reads a simple file', () => {
    expect(parseCsv('a,b\n1,2')).toEqual([
      ['a', 'b'],
      ['1', '2'],
    ]);
  });

  it('handles quoted fields containing commas', () => {
    expect(parseCsv('a,b\n"Smith, John",2')).toEqual([
      ['a', 'b'],
      ['Smith, John', '2'],
    ]);
  });

  it('handles escaped quotes', () => {
    expect(parseCsv('a\n"He said ""no"""')).toEqual([['a'], ['He said "no"']]);
  });

  it('handles newlines inside quoted fields', () => {
    expect(parseCsv('a,b\n"line one\nline two",2')).toEqual([
      ['a', 'b'],
      ['line one\nline two', '2'],
    ]);
  });

  it('normalises Windows line endings', () => {
    expect(parseCsv('a,b\r\n1,2')).toEqual([
      ['a', 'b'],
      ['1', '2'],
    ]);
  });

  it('does not invent a row for a trailing newline', () => {
    expect(parseCsv('a,b\n1,2\n')).toEqual([
      ['a', 'b'],
      ['1', '2'],
    ]);
  });
});

describe('parseNumber', () => {
  it('parses plain numbers', () => {
    expect(parseNumber('150')).toBe(150);
    expect(parseNumber('150.5')).toBe(150.5);
  });

  it('strips thousands separators', () => {
    expect(parseNumber('1,200')).toBe(1200);
  });

  it('strips a trailing unit', () => {
    expect(parseNumber('550 MW')).toBe(550);
  });

  it('rejects approximations rather than coercing them', () => {
    expect(parseNumber('~50')).toBeNull();
    expect(parseNumber('up to 200')).toBeNull();
    expect(parseNumber('50-100')).toBeNull();
  });

  it('rejects placeholder text that would otherwise become a number', () => {
    expect(parseNumber('n/a')).toBeNull();
    expect(parseNumber('TBC')).toBeNull();
    expect(parseNumber('-')).toBeNull();
  });

  it('returns null for an empty cell rather than zero', () => {
    expect(parseNumber('')).toBeNull();
    expect(parseNumber('   ')).toBeNull();
  });
});

describe('parseCapacityCsv', () => {
  it('parses a complete row', () => {
    const csv = `${header}\nEastern Creek,NEXTDC,Blacktown,proposed,550,100`;
    const { sites, errors } = parseCapacityCsv(csv, mapping);

    expect(errors).toEqual([]);
    expect(sites).toHaveLength(1);
    expect(sites[0]).toMatchObject({
      name: 'Eastern Creek',
      operator: 'NEXTDC',
      lga: 'Blacktown',
      status: 'proposed',
      totalCapacityMw: 550,
      liveCapacityMw: 100,
      gaps: [],
    });
  });

  it('records a blank cell as a gap rather than a zero', () => {
    const csv = `${header}\nMorwell,Keppel,Latrobe,proposed,,`;
    const { sites, errors } = parseCapacityCsv(csv, mapping);

    expect(errors).toEqual([]);
    expect(sites[0]?.totalCapacityMw).toBeNull();
    expect(sites[0]?.liveCapacityMw).toBeNull();
    expect(sites[0]?.gaps).toEqual([
      { field: 'total_capacity_mw', reason: 'unknown' },
      { field: 'live_capacity_mw', reason: 'unknown' },
    ]);
  });

  it('reports an unparseable number as an error and drops the row', () => {
    const csv = `${header}\nSomewhere,Operator,Council,proposed,about 400,50`;
    const { sites, errors } = parseCapacityCsv(csv, mapping);

    expect(sites).toHaveLength(0);
    expect(errors).toHaveLength(1);
    expect(errors[0]?.line).toBe(2);
    expect(errors[0]?.message).toContain('not a number');
  });

  it('rejects a non-positive capacity, which is an error and not a gap', () => {
    const csv = `${header}\nSomewhere,Operator,Council,proposed,0,0`;
    const { sites, errors } = parseCapacityCsv(csv, mapping);

    expect(sites).toHaveLength(0);
    expect(errors.some((e) => e.message.includes('not positive'))).toBe(true);
  });

  it('rejects live capacity exceeding total capacity', () => {
    const csv = `${header}\nSomewhere,Operator,Council,proposed,100,150`;
    const { sites, errors } = parseCapacityCsv(csv, mapping);

    expect(sites).toHaveLength(0);
    expect(errors[0]?.message).toContain('exceeds total capacity');
  });

  it('reports a nameless row rather than importing it', () => {
    const csv = `${header}\n,Operator,Council,proposed,100,50`;
    const { sites, errors } = parseCapacityCsv(csv, mapping);

    expect(sites).toHaveLength(0);
    expect(errors[0]?.message).toContain('no site name');
  });

  it('keeps good rows when a later row fails', () => {
    const csv =
      `${header}\n` +
      'Good Site,Operator,Council,proposed,100,50\n' +
      'Bad Site,Operator,Council,proposed,nonsense,50';

    const { sites, errors } = parseCapacityCsv(csv, mapping);

    expect(sites).toHaveLength(1);
    expect(sites[0]?.name).toBe('Good Site');
    expect(errors).toHaveLength(1);
    expect(errors[0]?.line).toBe(3);
  });

  it('fails loudly when the name column is absent from the header', () => {
    const { sites, errors } = parseCapacityCsv('Wrong,Headers\n1,2', mapping);

    expect(sites).toHaveLength(0);
    expect(errors[0]?.message).toContain('no column named "Station"');
  });

  it('reports an empty file', () => {
    expect(parseCapacityCsv('', mapping).errors[0]?.message).toBe('File is empty.');
  });

  it('ignores unmapped optional columns without inventing gaps for them', () => {
    const minimal: ColumnMapping = { name: 'Station' };
    const { sites } = parseCapacityCsv('Station\nSomewhere', minimal);

    expect(sites[0]?.gaps).toEqual([]);
    expect(sites[0]?.name).toBe('Somewhere');
  });
});
