import { NextResponse, type NextRequest } from 'next/server';
import { completeSignIn } from '@/lib/admin';

export const dynamic = 'force-dynamic';

/** Where the emailed sign-in link lands. Exchanges its one-time code for a session. */
export async function GET(request: NextRequest) {
  const code = request.nextUrl.searchParams.get('code');
  const target = request.nextUrl.clone();
  target.search = '';

  if (code && (await completeSignIn(code))) {
    target.pathname = '/admin';
  } else {
    target.pathname = '/admin/sign-in';
    target.searchParams.set('failed', '1');
  }
  return NextResponse.redirect(target);
}
