import { ImageResponse } from 'next/og';
import { SITE_NAME, SITE_STRAPLINE } from '@/lib/site';

export const alt = `${SITE_NAME}: ${SITE_STRAPLINE}`;
export const size = { width: 1200, height: 630 };
export const contentType = 'image/png';

/**
 * The image shown when a page is shared. It carries the masthead and the
 * strapline and no figures, so it cannot go stale or be quoted as a finding.
 */
export default function OpenGraphImage() {
  return new ImageResponse(
    (
      <div
        style={{
          width: '100%',
          height: '100%',
          display: 'flex',
          flexDirection: 'column',
          justifyContent: 'space-between',
          padding: '72px 80px',
          background: '#ffffff',
          color: '#0f172a',
        }}
      >
        <div style={{ display: 'flex', gap: 16, alignItems: 'center' }}>
          <div style={{ width: 18, height: 18, borderRadius: 9, background: '#24405e' }} />
          <div style={{ fontSize: 26, letterSpacing: 4, textTransform: 'uppercase', color: '#24405e' }}>
            The record
          </div>
          <div style={{ width: 18, height: 18, borderRadius: 9, background: '#7a4413', marginLeft: 24 }} />
          <div style={{ fontSize: 26, letterSpacing: 4, textTransform: 'uppercase', color: '#7a4413' }}>
            Analysis
          </div>
        </div>
        <div style={{ display: 'flex', flexDirection: 'column' }}>
          <div style={{ fontSize: 84, fontWeight: 700, lineHeight: 1.05, letterSpacing: -2 }}>{SITE_NAME}</div>
          <div style={{ fontSize: 36, marginTop: 24, color: '#334155' }}>{SITE_STRAPLINE}</div>
        </div>
        <div style={{ fontSize: 24, color: '#475569' }}>
          Every claim sourced. Every gap marked. Argument kept apart from the record.
        </div>
      </div>
    ),
    size,
  );
}
