/**
 * The manifest that travels with an export.
 *
 * An untested backup is a rumour. The manifest is what turns a directory of
 * JSON into something a restore can be checked against: it records how many
 * rows each table had at export time and the digest of the bytes written, so a
 * truncated upload or a half-finished export is caught before anyone relies on
 * it rather than during the incident it was meant to cover.
 *
 * Pure, so it is testable without a database or a filesystem.
 */

import { createHash } from 'node:crypto';

import { BACKUP_TABLES, type Recoverability } from '@/lib/backup/tables';

export const MANIFEST_VERSION = 'observatory-backup/1';

export interface TableManifest {
  readonly name: string;
  readonly rows: number;
  readonly recoverability: Recoverability;
  /** SHA-256 of the exported file's bytes. */
  readonly digest: string;
  readonly bytes: number;
}

export interface Manifest {
  readonly manifestVersion: string;
  readonly takenAt: string;
  /** The project the export came from. Host only — never a key. */
  readonly sourceHost: string;
  readonly tables: readonly TableManifest[];
  readonly totals: {
    readonly rows: number;
    readonly curatedRows: number;
    readonly derivedRows: number;
    readonly bytes: number;
  };
}

export function digestOf(contents: string): string {
  return createHash('sha256').update(contents, 'utf8').digest('hex');
}

/**
 * Serialise rows as newline-delimited JSON.
 *
 * NDJSON rather than one big array so that a partial file is still readable up
 * to the point it stops, and so a diff between two weeks shows the rows that
 * changed rather than re-indenting the whole table.
 *
 * Keys are sorted so the digest depends on the data and not on the order
 * PostgREST happened to return columns in. Without this, two identical exports
 * a week apart could produce different digests and every backup would look
 * like a change.
 */
export function toNdjson(rows: readonly Record<string, unknown>[]): string {
  return rows.map((row) => JSON.stringify(sortKeys(row))).join('\n') + (rows.length > 0 ? '\n' : '');
}

export function parseNdjson(contents: string): Record<string, unknown>[] {
  return contents
    .split('\n')
    .filter((line) => line.trim() !== '')
    .map((line, index) => {
      try {
        return JSON.parse(line) as Record<string, unknown>;
      } catch (error) {
        throw new Error(`Line ${index + 1} is not valid JSON: ${(error as Error).message}`);
      }
    });
}

function sortKeys(row: Record<string, unknown>): Record<string, unknown> {
  const sorted: Record<string, unknown> = {};
  for (const key of Object.keys(row).sort()) sorted[key] = row[key];
  return sorted;
}

export function buildManifest(input: {
  takenAt: string;
  sourceHost: string;
  tables: readonly { name: string; rows: number; contents: string }[];
}): Manifest {
  const tables: TableManifest[] = input.tables.map((t) => {
    const definition = BACKUP_TABLES.find((d) => d.name === t.name);
    if (!definition) {
      throw new Error(`${t.name} is not in BACKUP_TABLES. Add it there before exporting it.`);
    }
    return {
      name: t.name,
      rows: t.rows,
      recoverability: definition.recoverability,
      digest: digestOf(t.contents),
      bytes: Buffer.byteLength(t.contents, 'utf8'),
    };
  });

  const sum = (predicate: (t: TableManifest) => boolean) =>
    tables.filter(predicate).reduce((total, t) => total + t.rows, 0);

  return {
    manifestVersion: MANIFEST_VERSION,
    takenAt: input.takenAt,
    sourceHost: input.sourceHost,
    tables,
    totals: {
      rows: sum(() => true),
      curatedRows: sum((t) => t.recoverability === 'curated'),
      derivedRows: sum((t) => t.recoverability === 'derived'),
      bytes: tables.reduce((total, t) => total + t.bytes, 0),
    },
  };
}

/**
 * Check an export against its own manifest.
 *
 * Returns every problem rather than throwing on the first, because during a
 * restore you want to know whether one table is damaged or all of them.
 */
export function verifyManifest(
  manifest: Manifest,
  files: ReadonlyMap<string, string>,
): string[] {
  const problems: string[] = [];

  if (manifest.manifestVersion !== MANIFEST_VERSION) {
    problems.push(
      `Manifest version is ${manifest.manifestVersion}, this tool writes ${MANIFEST_VERSION}.`,
    );
  }

  for (const table of manifest.tables) {
    const contents = files.get(table.name);
    if (contents === undefined) {
      problems.push(`${table.name}: named in the manifest but missing from the export.`);
      continue;
    }
    const digest = digestOf(contents);
    if (digest !== table.digest) {
      problems.push(
        `${table.name}: digest mismatch. The manifest says ${table.digest.slice(0, 12)}, ` +
          `the file is ${digest.slice(0, 12)}. The export is damaged.`,
      );
    }
    const rows = parseNdjson(contents).length;
    if (rows !== table.rows) {
      problems.push(`${table.name}: manifest says ${table.rows} rows, the file holds ${rows}.`);
    }
  }

  for (const name of files.keys()) {
    if (!manifest.tables.some((t) => t.name === name)) {
      problems.push(`${name}: present in the export but absent from the manifest.`);
    }
  }

  return problems;
}

/** A short human summary, for the workflow log and the job summary. */
export function summarise(manifest: Manifest): string {
  const lines = [
    `Backup ${manifest.takenAt} from ${manifest.sourceHost}`,
    `${manifest.totals.rows} rows, ${(manifest.totals.bytes / 1024).toFixed(1)} KiB`,
    `${manifest.totals.curatedRows} curated (irreplaceable), ` +
      `${manifest.totals.derivedRows} derived (rebuildable from data-pipeline/)`,
    '',
  ];
  for (const table of manifest.tables) {
    const mark = table.recoverability === 'curated' ? '*' : ' ';
    lines.push(`  ${mark} ${table.name.padEnd(26)} ${String(table.rows).padStart(6)}`);
  }
  lines.push('', '* irreplaceable: no upstream copy exists outside this backup.');
  return lines.join('\n');
}
