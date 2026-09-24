'use client';

import dynamic from 'next/dynamic';

/**
 * Loads SiteMap in the browser only.
 *
 * Leaflet touches `window` on import, so it must never run on the server. In
 * the App Router `ssr: false` is only honoured when `next/dynamic` is called
 * from a client component: called from a server page it is silently ignored,
 * Leaflet is evaluated during the server render, and the map page returns a
 * 500. That is why this wrapper exists rather than the dynamic import living
 * in app/map/page.tsx.
 */
export const SiteMapLoader = dynamic(
  () => import('@/components/SiteMap').then((m) => m.SiteMap),
  {
    ssr: false,
    loading: () => (
      <div className="h-[28rem] w-full rounded-lg border border-fact-edge bg-fact-wash" />
    ),
  },
);
