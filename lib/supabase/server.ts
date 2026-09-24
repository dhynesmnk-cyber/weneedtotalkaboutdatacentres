import { createClient, type SupabaseClient } from '@supabase/supabase-js';
import type { Database } from '@/lib/types';
import { recordCacheSeconds, recordFetchPolicy } from '@/lib/supabase/cachePolicy';

/**
 * The only place a Supabase client is constructed.
 *
 * This client uses the anon key, so every read goes through Row Level Security:
 * unconfirmed links and unapproved editorial records are invisible to it by
 * construction, not by remembering to filter. The service role key is never
 * imported here — it belongs to ingestion jobs and edge functions alone.
 *
 * Both schemas must be listed under "Exposed schemas" in the Supabase project's
 * API settings, since neither is `public`. See docs/DEPLOYMENT.md.
 */

let cached: SupabaseClient<Database, 'facts'> | null = null;

/**
 * Read an environment variable at runtime.
 *
 * The indexed access matters. Next.js inlines a literal
 * `process.env.NEXT_PUBLIC_FOO` into the bundle at build time, so a placeholder
 * supplied to CI would be baked in and the app would believe it is configured
 * when it is not. A computed key is left alone and reads the real value at
 * request time. This module is server-only, so `process.env` is fully
 * populated here.
 */
function readOptionalEnv(name: string): string | undefined {
  return process.env[name];
}

function readEnv(name: string): string {
  const value = readOptionalEnv(name);
  if (!value) {
    throw new Error(
      `${name} is not set. Copy .env.example to .env.local and fill it in.`,
    );
  }
  return value;
}

function recordFetch(): typeof fetch {
  const policy = recordFetchPolicy(recordCacheSeconds(readOptionalEnv('RECORD_CACHE_SECONDS')));
  return (input, init) => fetch(input, { ...init, ...policy });
}

export function getClient(): SupabaseClient<Database, 'facts'> {
  if (cached) return cached;

  cached = createClient<Database, 'facts'>(
    readEnv('NEXT_PUBLIC_SUPABASE_URL'),
    readEnv('NEXT_PUBLIC_SUPABASE_ANON_KEY'),
    {
      db: { schema: 'facts' },
      auth: { persistSession: false },
      // Every read carries an explicit cache policy; see cachePolicy.ts for
      // why the default was a year.
      global: { fetch: recordFetch() },
    },
  );

  return cached;
}

/** The facts schema. Sourced records only. */
export function facts() {
  return getClient();
}

/** The editorial schema. Published analysis and essays only. */
export function editorial() {
  return getClient().schema('editorial');
}

/**
 * Whether the app is configured to reach a database at all.
 *
 * The scaffold has no Supabase project yet, and pages use this to render an
 * honest "not connected" state rather than crashing or, worse, showing
 * placeholder data that could be mistaken for findings.
 */
export function isConfigured(): boolean {
  return Boolean(
    readOptionalEnv('NEXT_PUBLIC_SUPABASE_URL') &&
      readOptionalEnv('NEXT_PUBLIC_SUPABASE_ANON_KEY'),
  );
}
