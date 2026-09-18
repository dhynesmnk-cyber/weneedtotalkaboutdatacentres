import { EVENT_CATEGORIES, type EventCategory } from '@/lib/types';

/**
 * Read the selected timeline tracks out of a URL search param.
 *
 * An absent, empty or unrecognised param means all tracks. That is the honest
 * default: the timeline shows everything until the reader narrows it, and a
 * malformed link should never silently hide events.
 */
export function parseTracks(raw: string | string[] | undefined): EventCategory[] {
  if (!raw) return [...EVENT_CATEGORIES];

  const value = Array.isArray(raw) ? raw.join(',') : raw;
  const valid = new Set<string>(EVENT_CATEGORIES);

  const parsed = value
    .split(',')
    .map((part) => part.trim())
    .filter((part): part is EventCategory => valid.has(part));

  // Preserve the canonical order rather than the order they appeared in the URL,
  // so the timeline legend is stable however the link was built.
  const selected = new Set(parsed);
  const ordered = EVENT_CATEGORIES.filter((c) => selected.has(c));

  return ordered.length ? ordered : [...EVENT_CATEGORIES];
}

/** Serialise a track selection back to a search param value, or null for "all". */
export function serialiseTracks(tracks: EventCategory[]): string | null {
  const selected = new Set(tracks);
  if (selected.size === 0 || selected.size === EVENT_CATEGORIES.length) {
    return null;
  }
  return EVENT_CATEGORIES.filter((c) => selected.has(c)).join(',');
}
