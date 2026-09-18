'use client';

import { useRouter, useSearchParams, usePathname } from 'next/navigation';
import { formatEventCategory } from '@/lib/format';
import { serialiseTracks } from '@/lib/timeline';
import { EVENT_CATEGORIES, type EventCategory } from '@/lib/types';

/**
 * Track selector for the timeline.
 *
 * Selection lives in the URL rather than component state, so a combination of
 * tracks is shareable, survives a reload, and works with the back button. Each
 * track is a real checkbox, so keyboard and screen reader support come from the
 * platform rather than from re-implementing it.
 */
export function TimelineTrackSelector({
  selected,
}: {
  selected: EventCategory[];
}) {
  const router = useRouter();
  const pathname = usePathname();
  const searchParams = useSearchParams();

  const selectedSet = new Set(selected);

  function toggle(category: EventCategory) {
    const next = new Set(selectedSet);
    if (next.has(category)) {
      next.delete(category);
    } else {
      next.add(category);
    }

    const params = new URLSearchParams(searchParams.toString());
    const serialised = serialiseTracks([...next]);
    if (serialised === null) {
      params.delete('tracks');
    } else {
      params.set('tracks', serialised);
    }

    const query = params.toString();
    router.push(query ? `${pathname}?${query}` : pathname, { scroll: false });
  }

  function showAll() {
    const params = new URLSearchParams(searchParams.toString());
    params.delete('tracks');
    const query = params.toString();
    router.push(query ? `${pathname}?${query}` : pathname, { scroll: false });
  }

  const allShown = selectedSet.size === EVENT_CATEGORIES.length;

  return (
    <fieldset className="rounded-lg border border-fact-edge bg-fact-wash p-4">
      <legend className="px-1 text-sm font-semibold text-fact-ink">
        Event tracks
      </legend>

      <div className="flex flex-wrap gap-x-5 gap-y-2">
        {EVENT_CATEGORIES.map((category) => (
          <label
            key={category}
            className="flex cursor-pointer items-center gap-2 text-sm"
          >
            <input
              type="checkbox"
              className="h-4 w-4 rounded border-fact-edge text-fact-ink"
              checked={selectedSet.has(category)}
              onChange={() => toggle(category)}
            />
            {formatEventCategory(category)}
          </label>
        ))}
      </div>

      <button
        type="button"
        onClick={showAll}
        disabled={allShown}
        className="mt-3 rounded border border-fact-edge bg-white px-3 py-1 text-sm
                   text-fact-ink disabled:cursor-not-allowed disabled:opacity-50"
      >
        Show all tracks
      </button>
    </fieldset>
  );
}
