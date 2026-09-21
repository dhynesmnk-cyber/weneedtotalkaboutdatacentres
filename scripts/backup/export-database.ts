/**
 * Export every table in both schemas to newline-delimited JSON.
 *
 *   npm run backup:export -- --out .artifacts/backup
 *   npm run backup:verify -- --out .artifacts/backup
 *
 * Reads over PostgREST with the service role key, which bypasses Row Level
 * Security. That is the point: proposed links and unapproved editorial records
 * are invisible to the public API, and they are exactly the rows a backup must
 * not miss. A backup taken with the anon key would look complete and quietly
 * omit them. The key needs the grant in migration 0012.
 *
 * HTTPS rather than pg_dump, because the Postgres wire protocol is unreachable
 * from an agent session and from some CI networks (see docs/SUPABASE_SETUP.md),
 * and a backup that only runs on one person's laptop is a backup that stops
 * running.
 *
 * This writes files. It never writes to the database.
 */

import { mkdirSync, readFileSync, writeFileSync } from 'node:fs';
import { join } from 'node:path';

import { readTable, readTableNames } from '@/lib/backup/fetch';
import {
  buildManifest,
  summarise,
  toNdjson,
  verifyManifest,
  type Manifest,
} from '@/lib/backup/manifest';
import { BACKUP_TABLES } from '@/lib/backup/tables';

function readEnv(name: string): string {
  const value = process.env[name];
  if (!value) throw new Error(`${name} is not set.`);
  return value;
}

function arg(flag: string): string | undefined {
  const index = process.argv.indexOf(flag);
  return index === -1 ? undefined : process.argv[index + 1];
}

function readExport(outDir: string, manifest: Manifest): Map<string, string> {
  const files = new Map<string, string>();
  for (const table of manifest.tables) {
    files.set(table.name, readFileSync(join(outDir, `${table.name}.ndjson`), 'utf8'));
  }
  return files;
}

function verifyOnly(outDir: string): void {
  const manifest = JSON.parse(readFileSync(join(outDir, 'manifest.json'), 'utf8')) as Manifest;
  const problems = verifyManifest(manifest, readExport(outDir, manifest));
  if (problems.length > 0) {
    process.stderr.write(`Backup is damaged:\n  ${problems.join('\n  ')}\n`);
    process.exit(1);
  }
  process.stdout.write(summarise(manifest) + '\n');
}

async function main(): Promise<void> {
  const outDir = arg('--out') ?? '.artifacts/backup';

  if (process.argv.includes('--verify')) {
    verifyOnly(outDir);
    return;
  }

  const baseUrl = readEnv('NEXT_PUBLIC_SUPABASE_URL');
  const apiKey = readEnv('SUPABASE_SERVICE_ROLE_KEY');
  const options = { baseUrl, apiKey, fetch: globalThis.fetch as never };

  // Secondary check: does the database hold a table the catalogue omits?
  //
  // Advisory on purpose. The primary check is tests/backup/tables.test.ts,
  // which compares the catalogue against the migrations in CI and so catches
  // the mistake before it can reach a backup. This one reads an endpoint
  // Supabase restricts to the service role and may withdraw, and a backup that
  // refuses to run because a sanity check could not be performed is a backup
  // that stops running. So it warns when it cannot look, and fails only when
  // it looks and finds something.
  const known = new Set(BACKUP_TABLES.map((t) => t.name));
  try {
    const live = [
      ...(await readTableNames('facts', options)),
      ...(await readTableNames('editorial', options)),
    ];
    const uncovered = live.filter((t) => !known.has(t));
    if (uncovered.length > 0) {
      throw new Error(
        `The database has tables this backup does not cover: ${uncovered.join(', ')}.\n` +
          'Add them to lib/backup/tables.ts with a recoverability classification.',
      );
    }
  } catch (error) {
    const message = (error as Error).message;
    if (message.startsWith('The database has tables')) throw error;
    process.stderr.write(`  (could not list tables to cross-check: ${message})\n`);
  }

  mkdirSync(outDir, { recursive: true });

  const written: { name: string; rows: number; contents: string }[] = [];
  for (const table of BACKUP_TABLES) {
    const rows = await readTable(table, options);
    const contents = toNdjson(rows);
    writeFileSync(join(outDir, `${table.name}.ndjson`), contents);
    written.push({ name: table.name, rows: rows.length, contents });
    process.stderr.write(`  ${table.name.padEnd(26)} ${String(rows.length).padStart(6)}\n`);
  }

  const manifest = buildManifest({
    takenAt: new Date().toISOString(),
    sourceHost: new URL(baseUrl).host,
    tables: written,
  });
  writeFileSync(join(outDir, 'manifest.json'), JSON.stringify(manifest, null, 2) + '\n');

  // Verify what was just written rather than trusting that writing worked.
  const problems = verifyManifest(manifest, readExport(outDir, manifest));
  if (problems.length > 0) {
    throw new Error(`The export does not match its own manifest:\n  ${problems.join('\n  ')}`);
  }

  process.stdout.write(summarise(manifest) + '\n');
}

main().catch((error: unknown) => {
  process.stderr.write(`${(error as Error).message}\n`);
  process.exit(1);
});
