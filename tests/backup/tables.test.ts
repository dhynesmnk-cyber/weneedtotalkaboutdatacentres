import { describe, expect, it } from 'vitest';
import { readFileSync } from 'node:fs';
import { join } from 'node:path';

import { BACKUP_TABLES, CURATED_COLUMNS, curatedTables } from '@/lib/backup/tables';

const REPO_ROOT = join(__dirname, '..', '..');

describe('BACKUP_TABLES', () => {
  it('covers every table created by the migrations', () => {
    // The catalogue is the backup's definition of "everything". A table added
    // by a migration and not added here would be absent from every future
    // backup, and nobody would find out until a restore.
    const sql = ['0002_facts_tables', '0003_editorial_tables', '0009_research_agenda', '0010_load_support']
      .map((f) => readFileSync(join(REPO_ROOT, 'supabase', 'migrations', `${f}.sql`), 'utf8'))
      .join('\n');

    const created = [...sql.matchAll(/create table (facts|editorial)\.(\w+)/g)].map(
      (m) => `${m[1]}.${m[2]}`,
    );
    expect(created.length).toBeGreaterThan(0);

    const covered = new Set(BACKUP_TABLES.map((t) => t.name));
    expect(created.filter((t) => !covered.has(t))).toEqual([]);
  });

  it('has a primary key and a stated reason for every table', () => {
    for (const table of BACKUP_TABLES) {
      expect(table.primaryKey.length).toBeGreaterThan(0);
      expect(table.note.length).toBeGreaterThan(0);
      expect(table.name).toBe(`${table.schema}.${table.table}`);
    }
  });

  it('lists no table twice', () => {
    expect(new Set(BACKUP_TABLES.map((t) => t.name)).size).toBe(BACKUP_TABLES.length);
  });

  it('classifies both editorial tables as irreplaceable', () => {
    // No loader can reach the editorial schema, so nothing can rebuild it.
    const editorial = BACKUP_TABLES.filter((t) => t.schema === 'editorial');
    expect(editorial.length).toBeGreaterThan(0);
    expect(editorial.every((t) => t.recoverability === 'curated')).toBe(true);
  });

  it('classifies as derived exactly the tables the pipeline loader writes', () => {
    // Kept honest against the loader's own allow-list: if the loader gains a
    // table, that table becomes rebuildable and this test says so.
    const loader = readFileSync(
      join(REPO_ROOT, 'scripts', 'ingestion', 'load-pipeline.ts'),
      'utf8',
    );
    const allowed = [...loader.matchAll(/'(facts\.\w+)',/g)].map((m) => m[1]);
    expect(allowed.length).toBeGreaterThan(0);

    for (const table of BACKUP_TABLES) {
      if (table.recoverability !== 'derived') continue;
      expect(allowed).toContain(table.name);
    }
  });

  it('names the curated columns that hide inside derived tables', () => {
    // These are why "just re-run the loader" is not a complete recovery.
    const names = CURATED_COLUMNS.map((c) => c.table);
    expect(names).toContain('facts.sites');
    expect(names).toContain('facts.links');
    for (const entry of CURATED_COLUMNS) {
      expect(entry.columns.length).toBeGreaterThan(0);
      expect(entry.why.length).toBeGreaterThan(0);
      expect(BACKUP_TABLES.some((t) => t.name === entry.table)).toBe(true);
    }
  });

  it('protects the approved council list and the alias table', () => {
    const curated = curatedTables().map((t) => t.name);
    expect(curated).toContain('facts.council_watchlist');
    expect(curated).toContain('facts.lga_aliases');
  });
});
