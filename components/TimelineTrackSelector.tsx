'use client';

import { useEffect, useState, useTransition } from 'react';
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
 *
 * The boxes change as soon as they are pressed. The URL, and so the events,
 * follow once the server has answered; until then a status line says the
 * timeline is updating. Without that the box would sit unchanged through the
 * round trip, which reads as a control that did not work.
 *
 * At least one track is always selected. An empty selection has no honest
 * meaning here: the URL treats "no tracks" as "all tracks" (see parseTracks),
 * so unticking the last box used to tick all six again. The last selected box
 * is disabled instead, and says why.
 */
export function TimelineTrackSelector({
  selected,
}: {
  selected: EventCategory[];
}) {
  const router = useRouter();
  const pathname = usePathname();
  const searchParams = useSearchParams();
  const [isPending, startTransition] = useTransition();

  // What the reader has pressed, ahead of the server. Re-synced whenever the
  // URL-derived selection changes, including by back and forward.
  const [shown, setShown] = useState<ReadonlySet<EventCategory>>(new Set(selected));
  const selectedKey = selected.join(',');
  useEffect(() => {
    setShown(new Set(selectedKey.split(',') as EventCategory[]));
  }, [selectedKey]);

  function navigate(next: ReadonlySet<EventCategory>) {
    setShown(next);
    const params = new URLSearchParams(searchParams.toString());
    const serialised = serialiseTracks([...next]);
    if (serialised === null) {
      params.delete('tracks');
    } else {
      params.set('tracks', serialised);
    }
    const query = params.toString();
    startTransition(() => {
      router.push(query ? `${pathname}?${query}` : pathname, { scroll: false });
    });
  }

  function toggle(category: EventCategory) {
    const next = new Set(shown);
    if (next.has(category)) {
      if (next.size === 1) return;
      next.delete(category);
    } else {
      next.add(category);
    }
    navigate(next);
  }

  const allShown = shown.size === EVENT_CATEGORIES.length;

  return (
    <fieldset
      className="rounded-lg border border-fact-edge bg-fact-wash p-4"
      aria-describedby="tracks-hint"
    >
      <legend className="px-1 text-sm font-semibold text-fact-ink">
        Event tracks
      </legend>

      <div className="flex flex-wrap gap-x-5 gap-y-2">
        {EVENT_CATEGORIES.map((category) => {
          const checked = shown.has(category);
          const onlyOne = checked && shown.size === 1;
          return (
            <label
              key={category}
              className={`flex items-center gap-2 text-sm ${
                onlyOne ? 'cursor-not-allowed' : 'cursor-pointer'
              }`}
            >
              <input
                type="checkbox"
                className="h-4 w-4 rounded border-fact-edge text-fact-ink"
                checked={checked}
                disabled={onlyOne}
                onChange={() => toggle(category)}
              />
              {formatEventCategory(category)}
            </label>
          );
        })}
      </div>

      <div className="mt-3 flex flex-wrap items-center gap-x-4 gap-y-2">
        <button
          type="button"
          onClick={() => navigate(new Set(EVENT_CATEGORIES))}
          disabled={allShown}
          className="rounded border border-fact-edge bg-white px-3 py-1 text-sm
                     text-fact-ink disabled:cursor-not-allowed disabled:opacity-50"
        >
          Show all tracks
        </button>
        <p id="tracks-hint" className="text-xs text-slate-600">
          At least one track is always shown.
        </p>
        <p role="status" className="text-xs font-medium text-fact-ink">
          {isPending ? 'Updating the timeline…' : ''}
        </p>
      </div>
    </fieldset>
  );
}
