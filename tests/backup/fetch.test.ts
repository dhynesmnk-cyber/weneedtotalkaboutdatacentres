import { describe, expect, it } from 'vitest';

import { pageRequest, readTable, readTableNames, type FetchLike } from '@/lib/backup/fetch';
import { tableByName } from '@/lib/backup/tables';

const sites = tableByName('facts.sites')!;
const aliases = tableByName('facts.lga_aliases')!;

/**
 * A PostgREST that holds `total` rows and honours the Range header, including
 * the row cap that makes paging necessary in the first place.
 */
function fakePostgrest(total: number, options: { cap?: number } = {}): {
  fetch: FetchLike;
  ranges: string[];
} {
  const cap = options.cap ?? Infinity;
  const ranges: string[] = [];

  const fetch: FetchLike = async (_url, init) => {
    const range = init.headers.Range ?? '0-';
    ranges.push(range);
    const [fromText, toText] = range.split('-');
    const from = Number(fromText);
    const to = Math.min(Number(toText), from + cap - 1);
    const page: Record<string, unknown>[] = [];
    for (let i = from; i <= to && i < total; i += 1) page.push({ id: String(i) });
    return {
      ok: page.length === total && from === 0,
      status: 206,
      json: async () => page,
      text: async () => '',
    };
  };

  return { fetch, ranges };
}

describe('pageRequest', () => {
  it('orders by the primary key so exports are byte-stable', () => {
    const { url } = pageRequest(sites, { baseUrl: 'https://x.co', apiKey: 'k', offset: 0, pageSize: 1000 });
    expect(url).toContain('order=id.asc');
  });

  it('orders by a non-id primary key where the table has one', () => {
    const { url } = pageRequest(aliases, { baseUrl: 'https://x.co', apiKey: 'k', offset: 0, pageSize: 10 });
    expect(url).toContain('order=alias.asc');
  });

  it('asks for the right schema, which is never public', () => {
    const facts = pageRequest(sites, { baseUrl: 'https://x.co', apiKey: 'k', offset: 0, pageSize: 10 });
    expect(facts.headers['Accept-Profile']).toBe('facts');
    const essays = pageRequest(tableByName('editorial.essays')!, {
      baseUrl: 'https://x.co',
      apiKey: 'k',
      offset: 0,
      pageSize: 10,
    });
    expect(essays.headers['Accept-Profile']).toBe('editorial');
  });

  it('builds an inclusive range from the offset and page size', () => {
    const first = pageRequest(sites, { baseUrl: 'https://x.co', apiKey: 'k', offset: 0, pageSize: 1000 });
    expect(first.headers.Range).toBe('0-999');
    const second = pageRequest(sites, { baseUrl: 'https://x.co', apiKey: 'k', offset: 1000, pageSize: 1000 });
    expect(second.headers.Range).toBe('1000-1999');
  });

  it('tolerates a base url with a trailing slash', () => {
    const { url } = pageRequest(sites, { baseUrl: 'https://x.co/', apiKey: 'k', offset: 0, pageSize: 1 });
    expect(url).toContain('https://x.co/rest/v1/sites');
    expect(url).not.toContain('//rest');
  });
});

describe('readTable', () => {
  const read = (total: number, pageSize: number, cap?: number) => {
    const fake = fakePostgrest(total, { cap });
    return readTable(sites, {
      baseUrl: 'https://x.co',
      apiKey: 'k',
      pageSize,
      fetch: fake.fetch,
    }).then((rows) => ({ rows, ranges: fake.ranges }));
  };

  it('returns a single short page without asking again', async () => {
    const { rows, ranges } = await read(5, 1000);
    expect(rows).toHaveLength(5);
    expect(ranges).toHaveLength(1);
  });

  it('pages past the row cap rather than stopping at it', async () => {
    // facts.data_gaps holds 1885 rows against a cap of 1000. Stopping at the
    // first page would lose 885 rows and still look like a successful backup.
    const { rows } = await read(1885, 1000);
    expect(rows).toHaveLength(1885);
    expect(rows[0]).toEqual({ id: '0' });
    expect(rows[1884]).toEqual({ id: '1884' });
  });

  it('asks once more when the row count is an exact multiple of the page size', async () => {
    // The boundary case: a full last page is indistinguishable from a page
    // with more behind it, so it must be followed by an empty request.
    const { rows, ranges } = await read(2000, 1000);
    expect(rows).toHaveLength(2000);
    expect(ranges).toEqual(['0-999', '1000-1999', '2000-2999']);
  });

  it('returns nothing for an empty table', async () => {
    const { rows } = await read(0, 1000);
    expect(rows).toEqual([]);
  });

  it('never returns a duplicate row across pages', async () => {
    const { rows } = await read(2500, 1000);
    expect(new Set(rows.map((r) => r.id)).size).toBe(2500);
  });

  it('throws with the server message rather than writing a truncated backup', async () => {
    const failing: FetchLike = async () => ({
      ok: false,
      status: 403,
      json: async () => [],
      text: async () => '{"code":"42501","message":"permission denied for schema facts"}',
    });
    await expect(
      readTable(sites, { baseUrl: 'https://x.co', apiKey: 'k', fetch: failing }),
    ).rejects.toThrow(/42501|permission denied/);
  });

  it('treats 206 Partial Content as success', async () => {
    // `ok` is false for 206 in the Fetch specification, but it is the normal
    // answer to a Range header and must not abort the export.
    const partial: FetchLike = async () => ({
      ok: false,
      status: 206,
      json: async () => [{ id: '1' }],
      text: async () => '',
    });
    await expect(
      readTable(sites, { baseUrl: 'https://x.co', apiKey: 'k', pageSize: 10, fetch: partial }),
    ).resolves.toHaveLength(1);
  });

  it('refuses a response that is not an array of rows', async () => {
    const odd: FetchLike = async () => ({
      ok: true,
      status: 200,
      json: async () => ({ message: 'nope' }),
      text: async () => '',
    });
    await expect(
      readTable(sites, { baseUrl: 'https://x.co', apiKey: 'k', fetch: odd }),
    ).rejects.toThrow(/expected an array/);
  });
});

describe('readTableNames', () => {
  it('prefixes the schema onto each table it finds', async () => {
    const fetch: FetchLike = async () => ({
      ok: true,
      status: 200,
      json: async () => ({ definitions: { sites: {}, sources: {} } }),
      text: async () => '',
    });
    await expect(readTableNames('facts', { baseUrl: 'https://x.co', apiKey: 'k', fetch })).resolves.toEqual([
      'facts.sites',
      'facts.sources',
    ]);
  });

  it('returns nothing rather than throwing when a schema exposes no tables', async () => {
    const fetch: FetchLike = async () => ({
      ok: true,
      status: 200,
      json: async () => ({}),
      text: async () => '',
    });
    await expect(readTableNames('editorial', { baseUrl: 'https://x.co', apiKey: 'k', fetch })).resolves.toEqual(
      [],
    );
  });
});
