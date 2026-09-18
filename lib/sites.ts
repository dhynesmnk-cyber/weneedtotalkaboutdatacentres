import { facts, isConfigured } from '@/lib/supabase/server';
import { citationsFor, gapsFor } from '@/lib/evidence';
import type { SiteRow, SiteStatus, SiteWithEvidence } from '@/lib/types';

/** Typed access to facts.sites. No raw SQL reaches a component. */

export async function listSites(options?: {
  status?: SiteStatus;
  lga?: string;
}): Promise<SiteRow[]> {
  if (!isConfigured()) return [];

  let query = facts().from('sites').select('*').order('name');

  if (options?.status) query = query.eq('status', options.status);
  if (options?.lga) query = query.eq('lga', options.lga);

  const { data, error } = await query;
  if (error) throw new Error(`Failed to load sites: ${error.message}`);
  return data ?? [];
}

/**
 * Sites that can be placed on the map.
 *
 * Coordinates are constrained to be supplied together, so filtering on lat
 * alone is sufficient. A site without coordinates is not absent from the
 * project, only from the map, and the map page says how many.
 */
export async function listMappableSites(): Promise<SiteRow[]> {
  if (!isConfigured()) return [];

  const { data, error } = await facts()
    .from('sites')
    .select('*')
    .not('lat', 'is', null)
    .order('name');

  if (error) throw new Error(`Failed to load mappable sites: ${error.message}`);
  return data ?? [];
}

export async function getSite(id: string): Promise<SiteRow | null> {
  if (!isConfigured()) return null;

  const { data, error } = await facts()
    .from('sites')
    .select('*')
    .eq('id', id)
    .maybeSingle();

  if (error) throw new Error(`Failed to load site: ${error.message}`);
  return data ?? null;
}

/** A site with its gaps and citations, which is the only form worth publishing. */
export async function getSiteWithEvidence(
  id: string,
): Promise<SiteWithEvidence | null> {
  const site = await getSite(id);
  if (!site) return null;

  const [gaps, citations] = await Promise.all([
    gapsFor('sites', id),
    citationsFor('sites', id),
  ]);

  return { site, gaps, citations };
}

/** The distinct local government areas represented, for the list page filter. */
export async function listSiteLgas(): Promise<string[]> {
  const sites = await listSites();
  const lgas = new Set(
    sites.map((s) => s.lga).filter((l): l is string => Boolean(l)),
  );
  return [...lgas].sort((a, b) => a.localeCompare(b, 'en-AU'));
}
