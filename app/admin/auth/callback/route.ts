import { NextResponse, type NextRequest } from 'next/server';
import { completeSignIn } from '@/lib/admin';
import { requestOrigin } from '@/lib/origin';

export const dynamic = 'force-dynamic';

/** Where the emailed sign-in link lands. Exchanges its one-time code for a session. */
export async function GET(request: NextRequest) {
  const code = request.nextUrl.searchParams.get('code');
  // Back to the host the link was opened on, where the session cookie is set.
  const origin = requestOrigin(request.headers, request.nextUrl.origin);

  const target =
    code && (await completeSignIn(code))
      ? new URL('/admin', origin)
      : new URL('/admin/sign-in?failed=1', origin);
  return NextResponse.redirect(target);
}
