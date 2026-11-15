/**
 * The origin a request actually arrived at, from its forwarded headers.
 *
 * Sign-in sets its session cookie on the host the reader is using. A redirect
 * built from anything else (a configured SITE_URL, or the address the server
 * happens to listen on) can land the reader on a different host, where that
 * cookie is not sent and they appear signed out. Deploy previews make this
 * routine: each has its own address.
 */
export function requestOrigin(headers: { get(name: string): string | null }, fallback: string): string {
  const host = headers.get('x-forwarded-host') ?? headers.get('host');
  if (!host || !/^[A-Za-z0-9.-]+(:\d+)?$/.test(host)) return fallback;
  const proto = (headers.get('x-forwarded-proto') ?? '').split(',')[0]!.trim();
  const scheme = proto === 'http' || proto === 'https' ? proto : new URL(fallback).protocol.replace(':', '');
  return `${scheme}://${host}`;
}
