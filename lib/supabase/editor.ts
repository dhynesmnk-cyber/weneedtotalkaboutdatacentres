import { createServerClient, type SetAllCookies } from '@supabase/ssr';
import type { SupabaseClient } from '@supabase/supabase-js';
import { cookies } from 'next/headers';
import type { NextRequest, NextResponse } from 'next/server';
import type { Database } from '@/lib/types';
import { siteUrl } from '@/lib/site';

/**
 * The editor's database client: the signed-in editor's session, from cookies.
 *
 * It uses the anon key like the public client, so it can do nothing the
 * signed-in user may not: every read and write goes through row level
 * security, and the database decides who is an editor (editorial.is_editor(),
 * migration 0014). The service role key is never used here, and there is no
 * browser client at all; the session lives in httpOnly cookies the page's
 * JavaScript cannot read.
 *
 * Reads are never cached. The public client caches records for minutes
 * (cachePolicy.ts); an editor must see the draft as it is now.
 */

function env(name: string): string | undefined {
  return process.env[name];
}

export function isAuthConfigured(): boolean {
  return Boolean(env('NEXT_PUBLIC_SUPABASE_URL') && env('NEXT_PUBLIC_SUPABASE_ANON_KEY'));
}

export function editorCookieOptions() {
  return {
    httpOnly: true,
    sameSite: 'lax' as const,
    path: '/',
    secure: siteUrl().protocol === 'https:',
  };
}

const noStore: typeof fetch = (input, init) => fetch(input, { ...init, cache: 'no-store' });

/**
 * The editorial-schema client type the public client also uses. @supabase/ssr
 * 0.5 passes its generics in the order older supabase-js releases took, which
 * the installed release reads differently (every write typed as never). The
 * object at run time is the same SupabaseClient either way.
 */
export type EditorClient = SupabaseClient<Database, 'editorial'>;

/** For server components, server actions and route handlers. */
export function editorClient(): EditorClient {
  const store = cookies();
  const client = createServerClient<Database, 'editorial'>(
    env('NEXT_PUBLIC_SUPABASE_URL') ?? '',
    env('NEXT_PUBLIC_SUPABASE_ANON_KEY') ?? '',
    {
      db: { schema: 'editorial' },
      cookieOptions: editorCookieOptions(),
      global: { fetch: noStore },
      cookies: {
        getAll: () => store.getAll(),
        setAll: ((list) => {
          try {
            for (const { name, value, options } of list) store.set(name, value, options);
          } catch {
            // A server component cannot set cookies. The middleware refreshes
            // the session on every /admin request, so nothing is lost.
          }
        }) satisfies SetAllCookies,
      },
    },
  );
  return client as unknown as EditorClient;
}

/**
 * For middleware: refresh the session cookies on the way through. Returns the
 * signed-in user's email, or null.
 */
export async function refreshEditorSession(
  request: NextRequest,
  respond: () => NextResponse,
): Promise<{ email: string | null; response: NextResponse }> {
  let response = respond();
  if (!isAuthConfigured()) return { email: null, response };

  const supabase = createServerClient<Database, 'editorial'>(
    env('NEXT_PUBLIC_SUPABASE_URL')!,
    env('NEXT_PUBLIC_SUPABASE_ANON_KEY')!,
    {
      db: { schema: 'editorial' },
      cookieOptions: editorCookieOptions(),
      global: { fetch: noStore },
      cookies: {
        getAll: () => request.cookies.getAll(),
        setAll: ((list) => {
          for (const { name, value } of list) request.cookies.set(name, value);
          response = respond();
          for (const { name, value, options } of list) response.cookies.set(name, value, options);
        }) satisfies SetAllCookies,
      },
    },
  );

  const { data } = await supabase.auth.getUser();
  return { email: data.user?.email ?? null, response };
}
