import { NextResponse, type NextRequest } from 'next/server';
import { refreshEditorSession } from '@/lib/supabase/editor';

/**
 * The editor's pages: refresh the sign-in session, and send anyone not signed
 * in to the sign-in page.
 *
 * This is an early turn-away, not the lock. Whether a signed-in person may
 * edit is decided by the database (editorial.is_editor()), which every admin
 * page asks before showing anything, and row level security refuses every
 * write that is not the editor's.
 */
export async function middleware(request: NextRequest) {
  const { email, response } = await refreshEditorSession(request, () =>
    NextResponse.next({ request }),
  );

  const path = request.nextUrl.pathname;
  const open = path === '/admin/sign-in' || path.startsWith('/admin/auth/');

  let result = response;
  if (!open && !email) {
    const url = request.nextUrl.clone();
    url.pathname = '/admin/sign-in';
    url.search = '';
    result = NextResponse.redirect(url);
    for (const cookie of response.cookies.getAll()) result.cookies.set(cookie);
  }

  result.headers.set('Cache-Control', 'private, no-store');
  result.headers.set('X-Robots-Tag', 'noindex, nofollow');
  return result;
}

export const config = {
  matcher: ['/admin/:path*'],
};
