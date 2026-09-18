import type { GapReason } from '@/lib/types';

/**
 * Parser for quarterly capacity exports.
 *
 * docs/SPEC.md puts AEMO Generation Information on a manual quarterly parse
 * rather than an automated feed, so this is a pure function over text that a
 * human has already downloaded. It performs no network access and knows nothing
 * about where the file came from.
 *
 * The column mapping is supplied by the caller rather than hard-coded, because
 * this scaffold has not been run against a real AEMO export and guessing that
 * file's headers would be inventing a specification. Configure the mapping once
 * against a real export and pin it in the job that calls this.
 *
 * Three rules follow from the hard rules in CLAUDE.md:
 *   - A row that cannot be parsed is reported, never silently dropped.
 *   - A blank cell becomes a gap with a reason, never a zero.
 *   - A value that fails validation is an error, not a gap. A gap means the
 *     value is absent; a negative capacity means the source is wrong about it.
 */

export interface ColumnMapping {
  name: string;
  operator?: string;
  lga?: string;
  status?: string;
  totalCapacityMw?: string;
  liveCapacityMw?: string;
}

export interface ParsedSite {
  name: string;
  operator: string | null;
  lga: string | null;
  status: string | null;
  totalCapacityMw: number | null;
  liveCapacityMw: number | null;
  /** Fields that were blank in the source, to be written to facts.data_gaps. */
  gaps: { field: string; reason: GapReason }[];
}

export interface RowError {
  /** 1-based line number in the source file, counting the header. */
  line: number;
  message: string;
}

export interface ParseResult {
  sites: ParsedSite[];
  errors: RowError[];
}

/** Maps a mapping key to the database column the gap should be recorded against. */
const GAP_FIELD_NAMES: Record<keyof Omit<ColumnMapping, 'name'>, string> = {
  operator: 'operator',
  lga: 'lga',
  status: 'status',
  totalCapacityMw: 'total_capacity_mw',
  liveCapacityMw: 'live_capacity_mw',
};

export function parseCapacityCsv(
  text: string,
  mapping: ColumnMapping,
): ParseResult {
  const rows = parseCsv(text);
  const sites: ParsedSite[] = [];
  const errors: RowError[] = [];

  if (rows.length === 0) {
    return { sites, errors: [{ line: 0, message: 'File is empty.' }] };
  }

  const header = rows[0] as string[];
  const index = new Map(header.map((h, i) => [h.trim(), i]));

  const nameIndex = index.get(mapping.name);
  if (nameIndex === undefined) {
    return {
      sites,
      errors: [
        { line: 1, message: `Header has no column named "${mapping.name}".` },
      ],
    };
  }

  for (let i = 1; i < rows.length; i += 1) {
    const row = rows[i] as string[];
    const line = i + 1;

    // A trailing newline produces a single empty cell. That is not a row.
    if (row.length === 1 && (row[0] ?? '').trim() === '') continue;

    const name = (row[nameIndex] ?? '').trim();
    if (!name) {
      errors.push({ line, message: 'Row has no site name and was not imported.' });
      continue;
    }

    const gaps: ParsedSite['gaps'] = [];
    const site: ParsedSite = {
      name,
      operator: null,
      lga: null,
      status: null,
      totalCapacityMw: null,
      liveCapacityMw: null,
      gaps,
    };

    let rowFailed = false;

    for (const key of ['operator', 'lga', 'status'] as const) {
      const column = mapping[key];
      if (!column) continue;

      const value = cell(row, index, column);
      if (value === null) {
        gaps.push({ field: GAP_FIELD_NAMES[key], reason: 'unknown' });
      } else {
        site[key] = value;
      }
    }

    for (const key of ['totalCapacityMw', 'liveCapacityMw'] as const) {
      const column = mapping[key];
      if (!column) continue;

      const raw = cell(row, index, column);
      if (raw === null) {
        gaps.push({ field: GAP_FIELD_NAMES[key], reason: 'unknown' });
        continue;
      }

      const parsed = parseNumber(raw);
      if (parsed === null) {
        errors.push({
          line,
          message: `${GAP_FIELD_NAMES[key]} is "${raw}", which is not a number.`,
        });
        rowFailed = true;
        continue;
      }
      if (parsed <= 0) {
        errors.push({
          line,
          message: `${GAP_FIELD_NAMES[key]} is ${parsed}, which is not positive.`,
        });
        rowFailed = true;
        continue;
      }

      site[key] = parsed;
    }

    if (
      site.totalCapacityMw !== null &&
      site.liveCapacityMw !== null &&
      site.liveCapacityMw > site.totalCapacityMw
    ) {
      errors.push({
        line,
        message:
          `Live capacity (${site.liveCapacityMw}) exceeds total capacity ` +
          `(${site.totalCapacityMw}).`,
      });
      rowFailed = true;
    }

    if (!rowFailed) sites.push(site);
  }

  return { sites, errors };
}

function cell(
  row: string[],
  index: Map<string, number>,
  column: string,
): string | null {
  const at = index.get(column);
  if (at === undefined) return null;

  const value = (row[at] ?? '').trim();
  return value === '' ? null : value;
}

/**
 * Parse a numeric cell.
 *
 * Accepts thousands separators and a trailing unit, both of which appear in
 * real exports. Rejects anything else rather than coercing: "n/a", "TBC" and
 * "~50" are not numbers, and treating them as one would fabricate a value.
 */
export function parseNumber(raw: string): number | null {
  const cleaned = raw
    .replace(/,/g, '')
    .replace(/\s*(MW|kW|mw|kw)\s*$/, '')
    .trim();

  if (cleaned === '') return null;
  if (!/^-?\d+(\.\d+)?$/.test(cleaned)) return null;

  const value = Number(cleaned);
  return Number.isFinite(value) ? value : null;
}

/**
 * Minimal RFC 4180 CSV reader: quoted fields, escaped quotes, embedded commas
 * and newlines. Small enough to test exhaustively, which a dependency would not
 * be.
 */
export function parseCsv(text: string): string[][] {
  const rows: string[][] = [];
  let row: string[] = [];
  let field = '';
  let inQuotes = false;

  const source = text.replace(/\r\n/g, '\n').replace(/\r/g, '\n');

  for (let i = 0; i < source.length; i += 1) {
    const char = source[i] as string;

    if (inQuotes) {
      if (char === '"') {
        if (source[i + 1] === '"') {
          field += '"';
          i += 1;
        } else {
          inQuotes = false;
        }
      } else {
        field += char;
      }
      continue;
    }

    if (char === '"') {
      inQuotes = true;
    } else if (char === ',') {
      row.push(field);
      field = '';
    } else if (char === '\n') {
      row.push(field);
      rows.push(row);
      row = [];
      field = '';
    } else {
      field += char;
    }
  }

  // Flush whatever the file ended on, unless it ended cleanly on a newline.
  if (field !== '' || row.length > 0) {
    row.push(field);
    rows.push(row);
  }

  return rows;
}
