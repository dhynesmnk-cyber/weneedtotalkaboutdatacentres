import { isRecordId } from '@/lib/ids';
import { facts, isConfigured } from '@/lib/supabase/server';
import { aliasMap, distinctLgas, listLgaAliases, spellingsOf } from '@/lib/councils';
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

  // Filtering on a council has to match every approved spelling of it, not the
  // one the caller happened to name. Asked for `Blacktown City Council` and
  // matching only that, the filter would return 4 sites of 15 and look right.
  if (options?.lga) {
    const spellings = spellingsOf(options.lga, await listLgaAliases());
    query = spellings.length === 1 ? query.eq('lga', options.lga) : query.in('lga', spellings);
  }

  const { data, error } = await query;
  if (error) throw new Error(`Failed to load sites: ${error.message}`);
  return data ?? [];
}

/**
 * Whether a site can be placed on the map.
 *
 * Coordinates are constrained to be supplied together, but both are checked:
 * the map needs both, and this costs nothing. A site without coordinates is
 * not absent from the project, only from the map, and the map page says how
 * many.
 */
export function isMappable(site: SiteRow): boolean {
  return site.lat !== null && site.lng !== null;
}

export async function getSite(id: string): Promise<SiteRow | null> {
  if (!isConfigured()) return null;
  if (!isRecordId(id)) return null;

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

/**
 * The distinct councils represented, for the list page filter.
 *
 * Resolved through the approved aliases, so one council appears once however
 * many ways the source records spell it.
 */
export async function listSiteLgas(): Promise<string[]> {
  const [sites, aliases] = await Promise.all([listSites(), listLgaAliases()]);
  return distinctLgas(sites.map((s) => s.lga), aliasMap(aliases));
}
