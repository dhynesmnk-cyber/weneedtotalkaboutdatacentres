import { facts, isConfigured } from '@/lib/supabase/server';
import type { EventCategory, EventRow } from '@/lib/types';

/** Typed access to facts.events, which drives the timeline. */

export async function listEvents(options?: {
  categories?: EventCategory[];
  siteId?: string;
  limit?: number;
}): Promise<EventRow[]> {
  if (!isConfigured()) return [];

  let query = facts().from('events').select('*').order('date', { ascending: false });

  if (options?.categories?.length) {
    query = query.in('category', options.categories);
  }
  if (options?.siteId) {
    query = query.eq('site_id', options.siteId);
  }
  if (options?.limit) {
    query = query.limit(options.limit);
  }

  const { data, error } = await query;
  if (error) throw new Error(`Failed to load events: ${error.message}`);
  return data ?? [];
}

export async function listEventsForSite(siteId: string): Promise<EventRow[]> {
  return listEvents({ siteId });
}

/**
 * Group events by year for timeline rendering.
 *
 * Returns years newest first, each with its events in date order, so the
 * timeline reads from the present backwards.
 */
export function groupEventsByYear(
  events: EventRow[],
): { year: number; events: EventRow[] }[] {
  const byYear = new Map<number, EventRow[]>();

  for (const event of events) {
    const year = Number(event.date.slice(0, 4));
    if (!Number.isFinite(year)) continue;

    const bucket = byYear.get(year);
    if (bucket) {
      bucket.push(event);
    } else {
      byYear.set(year, [event]);
    }
  }

  return [...byYear.entries()]
    .sort((a, b) => b[0] - a[0])
    .map(([year, yearEvents]) => ({
      year,
      events: [...yearEvents].sort((a, b) => b.date.localeCompare(a.date)),
    }));
}
