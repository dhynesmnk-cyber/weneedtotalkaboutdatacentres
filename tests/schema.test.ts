import { describe, expect, it } from 'vitest';
import { readFileSync, readdirSync } from 'node:fs';
import { join } from 'node:path';
import {
  EVENT_CATEGORIES,
  GAP_REASONS,
  SITE_STATUSES,
  type Database,
} from '@/lib/types';

/**
 * Static checks over supabase/migrations.
 *
 * These are not RLS tests. They read the SQL as text and assert that the
 * policies are declared, which catches a policy deleted or loosened in a diff.
 * They cannot catch a policy that is declared but does not behave as intended —
 * that needs a real Postgres instance, and those tests are the outstanding item
 * recorded in docs/QUALITY.md. Do not read a pass here as proof that the
 * database is secure.
 *
 * The parity checks exist because lib/types.ts is hand-written. Once a Supabase
 * project exists and types are generated, delete them rather than maintaining
 * them alongside a generator.
 */

const MIGRATIONS_DIR = join(__dirname, '..', 'supabase', 'migrations');

const sql = readdirSync(MIGRATIONS_DIR)
  .filter((f) => f.endsWith('.sql'))
  .sort()
  .map((f) => readFileSync(join(MIGRATIONS_DIR, f), 'utf8'))
  .join('\n');

/**
 * The migrations with `--` comments and comment-on strings removed.
 *
 * Needed wherever a test asserts the *absence* of something: the migrations
 * deliberately discuss the old source_ids design in prose, and a bare text
 * search cannot tell an explanation from a column.
 */
const executableSql = sql
  .replace(/^\s*--.*$/gm, '')
  .replace(/comment on [\s\S]*?';/gi, '');

function enumValues(name: string): string[] {
  const match = new RegExp(
    `create type facts\\.${name} as enum \\(([^)]*)\\)`,
    'i',
  ).exec(sql);

  if (!match?.[1]) return [];

  return [...match[1].matchAll(/'([^']+)'/g)].map((m) => m[1] as string);
}

describe('enum parity between SQL and lib/types.ts', () => {
  it('site_status matches', () => {
    expect(enumValues('site_status')).toEqual([...SITE_STATUSES]);
  });

  it('event_category matches', () => {
    expect(enumValues('event_category')).toEqual([...EVENT_CATEGORIES]);
  });

  it('gap_reason matches', () => {
    expect(enumValues('gap_reason')).toEqual([...GAP_REASONS]);
  });

  it('citable_record covers every table a citation may point at', () => {
    expect(enumValues('citable_record')).toEqual([
      'sites',
      'entities',
      'events',
      'case_studies',
      'essays',
    ]);
  });
});

describe('table parity', () => {
  const factTables: (keyof Database['facts']['Tables'])[] = [
    'sources',
    'sites',
    'entities',
    'events',
    'links',
    'citations',
    'data_gaps',
    'council_watchlist',
  ];

  const editorialTables: (keyof Database['editorial']['Tables'])[] = [
    'case_studies',
    'essays',
  ];

  it.each(factTables)('facts.%s is created in a migration', (table) => {
    expect(sql).toContain(`create table facts.${table}`);
  });

  it.each(editorialTables)('editorial.%s is created in a migration', (table) => {
    expect(sql).toContain(`create table editorial.${table}`);
  });

  it('keeps the two layers in separate schemas', () => {
    expect(sql).toContain('create schema if not exists facts');
    expect(sql).toContain('create schema if not exists editorial');

    // Editorial tables must not be created in the facts schema, or the
    // separation is cosmetic.
    for (const table of editorialTables) {
      expect(sql).not.toContain(`create table facts.${table}`);
    }
  });
});

describe('row level security is declared on every table', () => {
  const allTables = [
    'facts.sources',
    'facts.sites',
    'facts.entities',
    'facts.events',
    'facts.links',
    'facts.citations',
    'facts.data_gaps',
    'facts.council_watchlist',
    'editorial.case_studies',
    'editorial.essays',
  ];

  it.each(allTables)('%s has RLS enabled', (table) => {
    expect(sql).toMatch(
      new RegExp(`alter table ${table.replace('.', '\\.')}\\s+enable row level security`),
    );
  });

  it('grants no write access to anon or authenticated', () => {
    // Every grant in the migrations must be a select or a schema usage grant.
    const grants = [...sql.matchAll(/^grant\s+([\s\S]*?);/gim)].map((m) =>
      (m[1] as string).toLowerCase(),
    );

    expect(grants.length).toBeGreaterThan(0);
    for (const grant of grants) {
      expect(grant).not.toMatch(/\binsert\b|\bupdate\b|\bdelete\b|\ball\b/);
    }
  });

  it('declares no policy for insert, update or delete', () => {
    expect(sql).not.toMatch(/create policy[\s\S]*?for\s+(insert|update|delete)/i);
  });
});

describe('the two rules enforced in the database rather than the application', () => {
  it('hides unconfirmed links from public reads', () => {
    const policy = /create policy links_public_read_confirmed_only[\s\S]*?using \(([\s\S]*?)\);/i
      .exec(sql)?.[1];

    expect(policy).toBeDefined();
    expect(policy).toContain("state = 'confirmed'");
  });

  it('hides unapproved editorial records from public reads', () => {
    for (const table of ['case_studies', 'essays']) {
      const policy = new RegExp(
        `create policy ${table}_public_read_approved_only[\\s\\S]*?using \\(([\\s\\S]*?)\\);`,
        'i',
      ).exec(sql)?.[1];

      expect(policy, `${table} policy`).toBeDefined();
      expect(policy).toContain('approved_at is not null');
      expect(policy).toContain('publish_date <= current_date');
    }
  });

  it('requires a named approver on every editorial record that is approved', () => {
    for (const table of ['case_studies', 'essays']) {
      expect(sql).toContain(`constraint ${table}_approval_complete`);
    }
  });

  it('requires a named confirmer on every confirmed link', () => {
    expect(sql).toContain('constraint links_confirmation_complete');
  });

  it('cannot add a council to the watchlist without recording who approved it', () => {
    const table = /create table facts\.council_watchlist \(([\s\S]*?)\n\);/i.exec(sql)?.[1];

    expect(table).toBeDefined();
    expect(table).toMatch(/approved_by\s+text not null/);
    expect(table).toMatch(/approved_at\s+timestamptz not null/);
  });
});

describe('data quality constraints from docs/QUALITY.md', () => {
  it('rejects non-positive capacity', () => {
    expect(sql).toContain('constraint sites_total_capacity_positive');
    expect(sql).toContain('constraint sites_live_capacity_positive');
  });

  it('rejects live capacity above total capacity', () => {
    expect(sql).toContain('constraint sites_live_within_total');
  });

  it('rejects half a coordinate pair', () => {
    expect(sql).toContain('constraint sites_coords_paired');
  });

  it('allows only one gap record per field per record', () => {
    expect(sql).toContain('create unique index data_gaps_unique_field');
  });

  it('has no source_ids column anywhere, since citations is the only path', () => {
    expect(executableSql).not.toMatch(/source_ids/);
  });
});
