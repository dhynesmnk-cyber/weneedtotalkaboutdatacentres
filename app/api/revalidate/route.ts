import { timingSafeEqual } from 'node:crypto';
import { revalidateTag } from 'next/cache';
import { RECORD_CACHE_TAG } from '@/lib/supabase/cachePolicy';

export const dynamic = 'force-dynamic';

/**
 * Clear the cached database reads, so the next reader sees the current record.
 *
 * Reads are cached for a few minutes (lib/supabase/cachePolicy.ts). Call this
 * after applying a pipeline load, or after approving or retracting editorial,
 * so the change is live at once rather than when the cache expires:
 *
 *   curl -X POST -H "Authorization: Bearer $REVALIDATE_SECRET" \
 *     https://<site>/api/revalidate
 *
 * It only clears a cache: it cannot change or publish anything. It is still
 * behind a secret, because an open endpoint would let anyone force every
 * page to re-query the database. With no REVALIDATE_SECRET set it does not
 * exist.
 */
export async function POST(request: Request): Promise<Response> {
  const secret = process.env['REVALIDATE_SECRET'];
  if (!secret) return new Response('Not found', { status: 404 });

  const header = request.headers.get('authorization') ?? '';
  const given = Buffer.from(header.replace(/^Bearer\s+/i, ''));
  const expected = Buffer.from(secret);
  if (given.length !== expected.length || !timingSafeEqual(given, expected)) {
    return new Response('Unauthorised', { status: 401 });
  }

  revalidateTag(RECORD_CACHE_TAG);
  return Response.json({ revalidated: RECORD_CACHE_TAG, at: new Date().toISOString() });
}
