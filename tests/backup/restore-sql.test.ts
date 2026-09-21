import { describe, expect, it } from 'vitest';

import { buildManifest, toNdjson } from '@/lib/backup/manifest';
import { arrayLiteral, buildRestoreSql, insertsFor, literal } from '@/lib/backup/restore-sql';
import { tableByName } from '@/lib/backup/tables';

describe('arrayLiteral', () => {
  // editorial.essays carries text[] and uuid[]. The quoted form is used
  // because it coerces to either in assignment context, and because the empty
  // array needs no cast this way.
  it('renders a simple array', () => {
    expect(arrayLiteral(['a', 'b'])).toBe("'{a,b}'");
  });

  it('renders the empty array without a cast', () => {
    expect(arrayLiteral([])).toBe("'{}'");
  });

  it('quotes elements containing a comma or brace', () => {
    expect(arrayLiteral(['a,b'])).toBe('\'{"a,b"}\'');
    expect(arrayLiteral(['{x}'])).toBe('\'{"{x}"}\'');
  });

  it('quotes elements containing whitespace', () => {
    expect(arrayLiteral(['Hills Shire'])).toBe('\'{"Hills Shire"}\'');
  });

  it('escapes backslashes and double quotes', () => {
    expect(arrayLiteral(['a"b'])).toBe('\'{"a\\"b"}\'');
    expect(arrayLiteral(['a\\b'])).toBe('\'{"a\\\\b"}\'');
  });

  it('distinguishes a null element from the string NULL', () => {
    // Unquoted NULL is a null element; the literal text must come back as text.
    expect(arrayLiteral([null])).toBe("'{NULL}'");
    expect(arrayLiteral(['NULL'])).toBe('\'{"NULL"}\'');
  });

  it('quotes the empty string, which is not the same as no element', () => {
    expect(arrayLiteral([''])).toBe('\'{""}\'');
  });
});

describe('literal', () => {
  it('doubles single quotes', () => {
    expect(literal("O'Riordan Street")).toBe("'O''Riordan Street'");
  });

  it('renders an object as jsonb but an array as an array', () => {
    // The distinction lib/ingestion/sql.ts does not need to make and this does.
    expect(literal({ a: 1 })).toBe('\'{"a":1}\'::jsonb');
    expect(literal(['a'])).toBe("'{a}'");
  });

  it('renders null, booleans and numbers bare', () => {
    expect(literal(null)).toBe('null');
    expect(literal(undefined)).toBe('null');
    expect(literal(true)).toBe('true');
    expect(literal(12.5)).toBe('12.5');
  });

  it('refuses a non-finite number rather than emitting NaN', () => {
    expect(() => literal(Number.NaN)).toThrow(/non-finite/);
    expect(() => literal(Number.POSITIVE_INFINITY)).toThrow(/non-finite/);
  });
});

const sites = tableByName('facts.sites')!;
const aliases = tableByName('facts.lga_aliases')!;

describe('insertsFor', () => {
  it('says so rather than emitting an empty insert', () => {
    expect(insertsFor(sites, [])).toBe('-- facts.sites: no rows\n');
  });

  it('upserts on the primary key and never assigns to it', () => {
    const sql = insertsFor(sites, [{ id: 'a', name: 'X' }]);
    expect(sql).toContain('on conflict (id) do update set');
    expect(sql).toContain('name = excluded.name');
    expect(sql).not.toContain('id = excluded.id');
  });

  it('uses a non-id primary key where the table has one', () => {
    const sql = insertsFor(aliases, [{ alias: 'Blacktown', canonical: 'Blacktown City' }]);
    expect(sql).toContain('on conflict (alias) do update set');
    expect(sql).not.toContain('alias = excluded.alias');
  });

  it('batches long tables into several statements', () => {
    const rows = Array.from({ length: 5 }, (_, i) => ({ id: String(i), name: 'n' }));
    const sql = insertsFor(sites, rows, 2);
    expect(sql.match(/insert into facts\.sites/g)).toHaveLength(3);
  });

  it('refuses rows of differing shape rather than emitting broken SQL', () => {
    expect(() => insertsFor(sites, [{ id: 'a', name: 'X' }, { id: 'b' }])).toThrow(
      /different columns/,
    );
  });

  it('is insensitive to key order within a row', () => {
    expect(insertsFor(sites, [{ id: 'a', name: 'X' }])).toBe(
      insertsFor(sites, [{ name: 'X', id: 'a' }]),
    );
  });
});

describe('buildRestoreSql', () => {
  const manifest = buildManifest({
    takenAt: '2026-09-21T00:00:00.000Z',
    sourceHost: 'example.supabase.co',
    tables: [
      { name: 'facts.sites', rows: 1, contents: toNdjson([{ id: 'a', name: 'X' }]) },
      { name: 'editorial.essays', rows: 1, contents: toNdjson([{ id: 'e', title: 'T' }]) },
    ],
  });
  const rowsByTable = new Map([
    ['facts.sites', [{ id: 'a', name: 'X' }]],
    ['editorial.essays', [{ id: 'e', title: 'T' }]],
  ]);

  it('wraps everything in one transaction', () => {
    const sql = buildRestoreSql({ manifest, rowsByTable });
    expect(sql).toContain('begin;');
    expect(sql.trimEnd().endsWith('commit;')).toBe(true);
  });

  it('asserts row counts so a short restore rolls back', () => {
    const sql = buildRestoreSql({ manifest, rowsByTable });
    expect(sql).toMatch(/ROLLED BACK: facts\.sites/);
    expect(sql).toContain('select count(*) into found from editorial.essays;');
  });

  it('restores in foreign key order, not alphabetical order', () => {
    // sources must precede the citations that reference them.
    const wide = buildManifest({
      takenAt: 'now',
      sourceHost: 'h',
      tables: [
        { name: 'facts.citations', rows: 0, contents: '' },
        { name: 'facts.sources', rows: 0, contents: '' },
      ],
    });
    const sql = buildRestoreSql({
      manifest: wide,
      rowsByTable: new Map([
        ['facts.citations', []],
        ['facts.sources', []],
      ]),
    });
    expect(sql.indexOf('facts.sources')).toBeLessThan(sql.indexOf('facts.citations'));
  });

  it('can restore only what cannot be rebuilt from the pipeline', () => {
    const sql = buildRestoreSql({ manifest, rowsByTable, curatedOnly: true });
    expect(sql).toContain('editorial.essays');
    expect(sql).not.toContain('insert into facts.sites');
  });

  it('warns in the artefact that it upserts rather than rewinds', () => {
    // Someone reaching for this during an incident needs to know it will not
    // remove rows created after the backup was taken.
    expect(buildRestoreSql({ manifest, rowsByTable })).toMatch(/does not delete/i);
  });
});
