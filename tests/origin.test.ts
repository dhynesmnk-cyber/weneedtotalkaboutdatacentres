import { describe, expect, it } from 'vitest';
import { requestOrigin } from '@/lib/origin';

const h = (o: Record<string, string>) => ({ get: (n: string) => o[n] ?? null });

describe('requestOrigin', () => {
  it('uses the host the request arrived at', () => {
    expect(requestOrigin(h({ host: '127.0.0.1:3000' }), 'http://localhost:3000')).toBe('http://127.0.0.1:3000');
  });

  it('prefers the forwarded host and scheme behind a proxy', () => {
    expect(
      requestOrigin(h({ host: 'internal:8080', 'x-forwarded-host': 'preview--site.netlify.app', 'x-forwarded-proto': 'https' }), 'http://x'),
    ).toBe('https://preview--site.netlify.app');
  });

  it('falls back when the host header is missing or malformed', () => {
    expect(requestOrigin(h({}), 'https://example.org')).toBe('https://example.org');
    expect(requestOrigin(h({ host: 'evil.example/path?x' }), 'https://example.org')).toBe('https://example.org');
  });
});
