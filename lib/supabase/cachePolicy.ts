/**
 * How long the site may serve a database response before asking again.
 *
 * Next.js 14 keeps `fetch` responses in its data cache, and supabase-js reads
 * through `fetch`. Left to its defaults it cached every response for a year,
 * whatever the page's `dynamic` setting: a pipeline load, a correction, or a
 * retracted essay reached readers only on the next deploy. Every request now
 * carries an explicit policy instead.
 *
 * The default is five minutes. That bounds how stale a page can be, and lets
 * a burst of readers share one set of queries. A deploy hook can clear the
 * cache at once after a load or an editorial change (app/api/revalidate).
 *
 * RECORD_CACHE_SECONDS overrides it; 0 turns caching off, for local work
 * against a database that is being edited.
 */

export const RECORD_CACHE_TAG = 'record';
export const DEFAULT_RECORD_CACHE_SECONDS = 300;

export type RecordFetchPolicy =
  | { cache: 'no-store' }
  | { next: { revalidate: number; tags: string[] } };

/** Parse the configured lifetime. Anything unreadable falls back to the default. */
export function recordCacheSeconds(raw: string | undefined): number {
  if (raw === undefined || raw.trim() === '') return DEFAULT_RECORD_CACHE_SECONDS;
  const seconds = Number(raw);
  return Number.isInteger(seconds) && seconds >= 0 ? seconds : DEFAULT_RECORD_CACHE_SECONDS;
}

export function recordFetchPolicy(seconds: number): RecordFetchPolicy {
  return seconds === 0
    ? { cache: 'no-store' }
    : { next: { revalidate: seconds, tags: [RECORD_CACHE_TAG] } };
}
