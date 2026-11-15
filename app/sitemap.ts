import type { MetadataRoute } from 'next';
import { listEssays } from '@/lib/editorial';
import { listEntities } from '@/lib/entities';
import { listSites } from '@/lib/sites';
import { isConfigured } from '@/lib/supabase/server';
import { siteUrl } from '@/lib/site';

export const dynamic = 'force-dynamic';

const STATIC_ROUTES = ['/', '/map', '/list', '/coverage', '/research', '/essays', '/how-to-read'];

/**
 * Every public page. Records come from the database through the same RLS the
 * pages use, so an unpublished essay or a minor entity cannot appear here.
 * If the database is unreachable the sitemap still lists the fixed pages.
 */
export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
  const base = siteUrl();
  const at = (path: string) => new URL(path, base).toString();
  const entries: MetadataRoute.Sitemap = STATIC_ROUTES.map((path) => ({ url: at(path) }));

  if (!isConfigured()) return entries;

  try {
    const [sites, entities, essays] = await Promise.all([
      listSites(),
      listEntities({ majorOnly: true }),
      listEssays(),
    ]);
    for (const site of sites) entries.push({ url: at(`/sites/${site.id}`) });
    for (const entity of entities) entries.push({ url: at(`/entities/${entity.id}`) });
    for (const essay of essays) {
      entries.push({
        url: at(`/essays/${essay.id}`),
        ...(essay.publish_date ? { lastModified: essay.publish_date } : {}),
      });
    }
  } catch {
    // A sitemap with the fixed pages beats a failed request.
  }

  return entries;
}
