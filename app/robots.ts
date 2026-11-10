import type { MetadataRoute } from 'next';
import { siteUrl } from '@/lib/site';

export default function robots(): MetadataRoute.Robots {
  return {
    // The editor's pages are private. They also refuse anyone who is not the
    // editor; this only keeps them out of search results.
    rules: [{ userAgent: '*', allow: '/', disallow: '/admin' }],
    sitemap: new URL('/sitemap.xml', siteUrl()).toString(),
  };
}
