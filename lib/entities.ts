import { isRecordId } from '@/lib/ids';
import { facts, isConfigured } from '@/lib/supabase/server';
import type { EntityRow, EventRow, SiteRow } from '@/lib/types';

/** Typed access to facts.entities and the confirmed links that reach them. */

export async function listEntities(options?: {
  majorOnly?: boolean;
}): Promise<EntityRow[]> {
  if (!isConfigured()) return [];

  let query = facts().from('entities').select('*').order('name');
  if (options?.majorOnly) query = query.eq('major_flag', true);

  const { data, error } = await query;
  if (error) throw new Error(`Failed to load entities: ${error.message}`);
  return data ?? [];
}

export async function getEntity(id: string): Promise<EntityRow | null> {
  if (!isConfigured()) return null;
  if (!isRecordId(id)) return null;

  const { data, error } = await facts()
    .from('entities')
    .select('*')
    .eq('id', id)
    .maybeSingle();

  if (error) throw new Error(`Failed to load entity: ${error.message}`);
  return data ?? null;
}

/**
 * Sites and events linked to an entity.
 *
 * Only confirmed links are readable: RLS filters proposed ones out before they
 * reach this code, so there is no state check here to forget. See
 * supabase/migrations/0004_rls.sql.
 */
export async function linkedRecordsForEntity(entityId: string): Promise<{
  sites: SiteRow[];
  events: EventRow[];
}> {
  if (!isConfigured()) return { sites: [], events: [] };

  const { data, error } = await facts()
    .from('links')
    .select('site_id, event_id')
    .eq('entity_id', entityId);

  if (error) throw new Error(`Failed to load entity links: ${error.message}`);

  const siteIds = unique(data?.map((l) => l.site_id));
  const eventIds = unique(data?.map((l) => l.event_id));

  const [sites, events] = await Promise.all([
    siteIds.length ? fetchSitesByIds(siteIds) : Promise.resolve([]),
    eventIds.length ? fetchEventsByIds(eventIds) : Promise.resolve([]),
  ]);

  return { sites, events };
}

/** Entities linked to a site, for the site profile. */
export async function linkedEntitiesForSite(siteId: string): Promise<EntityRow[]> {
  if (!isConfigured()) return [];

  const { data, error } = await facts()
    .from('links')
    .select('entity_id')
    .eq('site_id', siteId);

  if (error) throw new Error(`Failed to load site links: ${error.message}`);

  const entityIds = unique(data?.map((l) => l.entity_id));
  if (!entityIds.length) return [];

  const { data: entities, error: entityError } = await facts()
    .from('entities')
    .select('*')
    .in('id', entityIds)
    .order('name');

  if (entityError) {
    throw new Error(`Failed to load linked entities: ${entityError.message}`);
  }
  return entities ?? [];
}

async function fetchSitesByIds(ids: string[]): Promise<SiteRow[]> {
  const { data, error } = await facts()
    .from('sites')
    .select('*')
    .in('id', ids)
    .order('name');

  if (error) throw new Error(`Failed to load linked sites: ${error.message}`);
  return data ?? [];
}

async function fetchEventsByIds(ids: string[]): Promise<EventRow[]> {
  const { data, error } = await facts()
    .from('events')
    .select('*')
    .in('id', ids)
    .order('date', { ascending: false });

  if (error) throw new Error(`Failed to load linked events: ${error.message}`);
  return data ?? [];
}

function unique(values: (string | null)[] | undefined): string[] {
  return [...new Set((values ?? []).filter((v): v is string => Boolean(v)))];
}
