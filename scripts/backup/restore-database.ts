/**
 * Turn a backup export into a reviewable SQL artefact.
 *
 *   npx tsx scripts/backup/restore-database.ts --in .artifacts/backup
 *   npx tsx scripts/backup/restore-database.ts --in .artifacts/backup --curated-only
 *
 * Writes SQL to stdout or to --out. It connects to nothing. A human reads the
 * artefact and applies it, exactly as with the pipeline loader — recovering
 * from a backup is when an unreviewed write does the most damage.
 *
 * In most incidents --curated-only is the right flag. The derived tables come
 * back faster and more trustworthily from `npm run load:pipeline`, which
 * rebuilds them from data-pipeline/ in git; the curated tables have no other
 * copy anywhere and are what this backup exists to protect.
 */

import { readFileSync, writeFileSync, mkdirSync } from 'node:fs';
import { dirname, join } from 'node:path';

import { parseNdjson, verifyManifest, type Manifest } from '@/lib/backup/manifest';
import { buildRestoreSql } from '@/lib/backup/restore-sql';

function arg(flag: string): string | undefined {
  const index = process.argv.indexOf(flag);
  return index === -1 ? undefined : process.argv[index + 1];
}

function main(): void {
  const inDir = arg('--in') ?? '.artifacts/backup';
  const curatedOnly = process.argv.includes('--curated-only');

  const manifest = JSON.parse(readFileSync(join(inDir, 'manifest.json'), 'utf8')) as Manifest;

  const files = new Map<string, string>();
  for (const table of manifest.tables) {
    files.set(table.name, readFileSync(join(inDir, `${table.name}.ndjson`), 'utf8'));
  }

  // Refuse to emit SQL from a damaged export. A restore that silently drops
  // half a table is worse than no restore, because it looks like it worked.
  const problems = verifyManifest(manifest, files);
  if (problems.length > 0) {
    process.stderr.write(
      `Refusing to build a restore from a damaged backup:\n  ${problems.join('\n  ')}\n`,
    );
    process.exit(1);
  }

  const rowsByTable = new Map<string, Record<string, unknown>[]>();
  for (const [name, contents] of files) rowsByTable.set(name, parseNdjson(contents));

  const sql = buildRestoreSql({ manifest, rowsByTable, curatedOnly });

  const out = arg('--out');
  if (out) {
    mkdirSync(dirname(out), { recursive: true });
    writeFileSync(out, sql);
    process.stderr.write(`Wrote ${out} (${sql.length} bytes). Review it, then apply it.\n`);
  } else {
    process.stdout.write(sql);
  }
}

main();
