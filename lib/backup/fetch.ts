/**
 * Reading every row of a table out of PostgREST.
 *
 * Separated from the export script so the paging can be tested without a
 * database. Paging is the part most likely to be quietly wrong: PostgREST caps
 * a response at `max_rows` — 1000 on this project — and returns the first page
 * with a 200 or 206 and no indication that anything was left behind. A backup
 * that silently stopped at 1000 rows would look successful every week and
 * would be missing nearly half of facts.data_gaps.
 */

import type { BackupTable } from '@/lib/backup/tables';

/** The subset of `fetch` this module needs, so a test can supply its own. */
export type FetchLike = (
  url: string,
  init: { headers: Record<string, string> },
) => Promise<{
  ok: boolean;
  status: number;
  json: () => Promise<unknown>;
  text: () => Promise<string>;
}>;

export interface ReadOptions {
  readonly baseUrl: string;
  readonly apiKey: string;
  readonly pageSize?: number;
  readonly fetch: FetchLike;
}

/**
 * A page request's URL and headers.
 *
 * Rows are ordered by primary key so that two exports of unchanged data
 * produce byte-identical files. PostgREST promises no order otherwise, and
 * without this every weekly backup would differ from the last and the digest
 * would stop meaning "the data changed". It also makes paging coherent: an
 * unordered offset scan can return the same row twice and miss another.
 */
export function pageRequest(
  table: BackupTable,
  options: { baseUrl: string; apiKey: string; offset: number; pageSize: number },
): { url: string; headers: Record<string, string> } {
  const order = table.primaryKey.map((c) => `${c}.asc`).join(',');
  return {
    url: `${options.baseUrl.replace(/\/$/, '')}/rest/v1/${table.table}?select=*&order=${order}`,
    headers: {
      apikey: options.apiKey,
      Authorization: `Bearer ${options.apiKey}`,
      'Accept-Profile': table.schema,
      Range: `${options.offset}-${options.offset + options.pageSize - 1}`,
      'Range-Unit': 'items',
    },
  };
}

export async function readTable(
  table: BackupTable,
  options: ReadOptions,
): Promise<Record<string, unknown>[]> {
  const pageSize = options.pageSize ?? 1000;
  const rows: Record<string, unknown>[] = [];

  for (let offset = 0; ; offset += pageSize) {
    const { url, headers } = pageRequest(table, {
      baseUrl: options.baseUrl,
      apiKey: options.apiKey,
      offset,
      pageSize,
    });

    const response = await options.fetch(url, { headers });

    // 206 Partial Content is the normal answer to a Range header and is not an
    // error, but `ok` is false for it in the Fetch specification.
    if (!response.ok && response.status !== 206) {
      throw new Error(`${table.name}: HTTP ${response.status} ${await response.text()}`);
    }

    const page = (await response.json()) as Record<string, unknown>[];
    if (!Array.isArray(page)) {
      throw new Error(`${table.name}: expected an array of rows, got ${typeof page}.`);
    }

    rows.push(...page);

    // A short page is the last page. A full one might be, so ask again: the
    // cost is one empty request per table whose row count is an exact multiple
    // of the page size, and the alternative is losing rows in that case.
    if (page.length < pageSize) return rows;
  }
}

/**
 * The tables PostgREST will serve, from the OpenAPI description it publishes.
 *
 * Used to fail an export when the database holds a table the backup catalogue
 * does not list. Note that this sees only what the calling key may read, so it
 * is a secondary check; tests/backup/tables.test.ts compares the catalogue
 * against the migrations themselves and catches the same mistake in CI, before
 * it can reach a backup at all.
 */
export async function readTableNames(
  schema: string,
  options: Omit<ReadOptions, 'pageSize'>,
): Promise<string[]> {
  const response = await options.fetch(`${options.baseUrl.replace(/\/$/, '')}/rest/v1/`, {
    headers: {
      apikey: options.apiKey,
      Authorization: `Bearer ${options.apiKey}`,
      'Accept-Profile': schema,
    },
  });
  if (!response.ok) {
    throw new Error(`Could not read the ${schema} schema description: HTTP ${response.status}`);
  }
  const document = (await response.json()) as { definitions?: Record<string, unknown> };
  return Object.keys(document.definitions ?? {}).map((t) => `${schema}.${t}`);
}
