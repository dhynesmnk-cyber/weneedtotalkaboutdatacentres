import Link from 'next/link';
import { Suspense } from 'react';
import { TimelineTrackSelector } from '@/components/TimelineTrackSelector';
import { parseTracks } from '@/lib/timeline';
import { NotConnected, NothingRecorded } from '@/components/NotConnected';
import { groupEventsByYear, listEvents } from '@/lib/events';
import { isConfigured } from '@/lib/supabase/server';
import { formatDate, formatEventCategory } from '@/lib/format';
import type { EventRow } from '@/lib/types';

export const dynamic = 'force-dynamic';

/**
 * Home and timeline. The first entry point in docs/SPEC.md's priority order.
 *
 * Tracks are combinable and the selection lives in the URL, so a reader can
 * share "planning and community events only" as a link.
 */
export default async function TimelinePage({
  searchParams,
}: {
  searchParams: { tracks?: string };
}) {
  const tracks = parseTracks(searchParams.tracks);
  const events = await listEvents({ categories: tracks, limit: 200 });
  const byYear = groupEventsByYear(events);

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-bold text-slate-900">Timeline</h1>
        <p className="mt-2 max-w-2xl text-slate-700">
          Planning, construction, media, political, community and financial
          events, on combinable tracks. Every entry is dated and sourced.
        </p>
      </div>

      <Suspense fallback={null}>
        <TimelineTrackSelector selected={tracks} />
      </Suspense>

      {!isConfigured() ? (
        <NotConnected what="events" />
      ) : byYear.length === 0 ? (
        <NothingRecorded what="events" />
      ) : (
        <ol className="space-y-10">
          {byYear.map(({ year, events: yearEvents }) => (
            <li key={year}>
              <h2 className="sticky top-0 bg-white py-2 text-lg font-semibold text-slate-900">
                {year}
              </h2>
              <ul className="mt-2 space-y-4 border-l-2 border-fact-edge pl-5">
                {yearEvents.map((event) => (
                  <TimelineEntry key={event.id} event={event} />
                ))}
              </ul>
            </li>
          ))}
        </ol>
      )}
    </div>
  );
}

function TimelineEntry({ event }: { event: EventRow }) {
  return (
    <li className="relative">
      <span
        aria-hidden="true"
        className="absolute -left-[1.6rem] top-2 h-2.5 w-2.5 rounded-full bg-fact-ink"
      />
      <div className="flex flex-wrap items-baseline gap-x-3">
        <span className="rounded border border-fact-edge bg-fact-wash px-2 py-0.5 text-xs font-medium text-fact-ink">
          {formatEventCategory(event.category)}
        </span>
        <time dateTime={event.date} className="text-sm text-slate-600">
          {formatDate(event.date)}
        </time>
      </div>

      <h3 className="mt-1 font-medium text-slate-900">{event.title}</h3>
      {event.summary && (
        <p className="mt-1 text-sm text-slate-700">{event.summary}</p>
      )}
      {event.site_id && (
        <Link
          href={`/sites/${event.site_id}`}
          className="mt-1 inline-block text-sm text-fact-ink underline underline-offset-2"
        >
          Related site
        </Link>
      )}
    </li>
  );
}
