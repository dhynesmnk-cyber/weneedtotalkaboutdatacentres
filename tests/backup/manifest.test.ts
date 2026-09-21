import { describe, expect, it } from 'vitest';

import {
  buildManifest,
  digestOf,
  parseNdjson,
  summarise,
  toNdjson,
  verifyManifest,
  type Manifest,
} from '@/lib/backup/manifest';

describe('toNdjson', () => {
  it('writes one row per line and ends with a newline', () => {
    expect(toNdjson([{ a: 1 }, { a: 2 }])).toBe('{"a":1}\n{"a":2}\n');
  });

  it('writes nothing at all for no rows', () => {
    expect(toNdjson([])).toBe('');
  });

  it('sorts keys, so column order cannot change the digest', () => {
    // PostgREST does not promise a column order. If it varied, every weekly
    // backup would differ from the last and the digest would stop meaning
    // "the data changed".
    expect(toNdjson([{ b: 1, a: 2 }])).toBe(toNdjson([{ a: 2, b: 1 }]));
  });

  it('round-trips through parseNdjson', () => {
    const rows = [{ id: 'x', tags: ['a', 'b'], meta: { k: 1 }, empty: null }];
    expect(parseNdjson(toNdjson(rows))).toEqual(rows);
  });
});

describe('parseNdjson', () => {
  it('ignores blank lines', () => {
    expect(parseNdjson('{"a":1}\n\n{"a":2}\n')).toHaveLength(2);
  });

  it('names the line that is malformed', () => {
    expect(() => parseNdjson('{"a":1}\nnot json\n')).toThrow(/Line 2/);
  });
});

const sample = () =>
  buildManifest({
    takenAt: '2026-09-21T00:00:00.000Z',
    sourceHost: 'example.supabase.co',
    tables: [
      { name: 'facts.sites', rows: 2, contents: toNdjson([{ id: 1 }, { id: 2 }]) },
      { name: 'editorial.essays', rows: 1, contents: toNdjson([{ id: 3 }]) },
    ],
  });

describe('buildManifest', () => {
  it('separates curated rows from derived ones', () => {
    const manifest = sample();
    // sites is rebuildable from data-pipeline/; an essay is not rebuildable at all.
    expect(manifest.totals.derivedRows).toBe(2);
    expect(manifest.totals.curatedRows).toBe(1);
    expect(manifest.totals.rows).toBe(3);
  });

  it('refuses a table that is not in the catalogue', () => {
    expect(() =>
      buildManifest({
        takenAt: 'now',
        sourceHost: 'h',
        tables: [{ name: 'facts.invented', rows: 0, contents: '' }],
      }),
    ).toThrow(/not in BACKUP_TABLES/);
  });

  it('records the digest of the bytes written', () => {
    const manifest = sample();
    const sites = manifest.tables.find((t) => t.name === 'facts.sites');
    expect(sites?.digest).toBe(digestOf(toNdjson([{ id: 1 }, { id: 2 }])));
  });
});

describe('verifyManifest', () => {
  const files = () =>
    new Map([
      ['facts.sites', toNdjson([{ id: 1 }, { id: 2 }])],
      ['editorial.essays', toNdjson([{ id: 3 }])],
    ]);

  it('passes a sound export', () => {
    expect(verifyManifest(sample(), files())).toEqual([]);
  });

  it('catches a truncated file', () => {
    const damaged = files();
    damaged.set('facts.sites', toNdjson([{ id: 1 }]));
    const problems = verifyManifest(sample(), damaged);
    expect(problems.join(' ')).toMatch(/facts\.sites.*digest mismatch/);
  });

  it('catches a missing file', () => {
    const damaged = files();
    damaged.delete('editorial.essays');
    expect(verifyManifest(sample(), damaged).join(' ')).toMatch(/missing from the export/);
  });

  it('catches a file nobody recorded', () => {
    const extra = files();
    extra.set('facts.links', toNdjson([{ id: 9 }]));
    expect(verifyManifest(sample(), extra).join(' ')).toMatch(/absent from the manifest/);
  });

  it('reports every problem, not just the first', () => {
    const damaged = new Map([['facts.sites', toNdjson([{ id: 1 }])]]);
    // One damaged table and one missing one: a restore needs to know both.
    expect(verifyManifest(sample(), damaged).length).toBeGreaterThan(1);
  });

  it('rejects a manifest written by a different version', () => {
    const stale = { ...sample(), manifestVersion: 'observatory-backup/0' } as Manifest;
    expect(verifyManifest(stale, files()).join(' ')).toMatch(/Manifest version/);
  });
});

describe('summarise', () => {
  it('marks the irreplaceable tables', () => {
    const text = summarise(sample());
    expect(text).toMatch(/\* editorial\.essays/);
    expect(text).toMatch(/irreplaceable/);
    expect(text).toMatch(/rebuildable from data-pipeline/);
  });
});
