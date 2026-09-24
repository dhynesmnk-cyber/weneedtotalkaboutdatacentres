import Link from 'next/link';
import { Suspense } from 'react';
import { TimelineTrackSelector } from '@/components/TimelineTrackSelector';
import { parseTracks } from '@/lib/timeline';
import { NotConnected, NothingRecorded } from '@/components/NotConnected';
import { StatTile } from '@/components/StatTile';
import { StatusBreakdown } from '@/components/StatusBreakdown';
import { DateStamp } from '@/components/DateStamp';
import { groupEventsByYear, listEvents } from '@/lib/events';
import { listSites } from '@/lib/sites';
import { listGaps } from '@/lib/evidence';
import { lastLoadedAt, siteCoverage, statusCounts } from '@/lib/coverage';
import { isConfigured } from '@/lib/supabase/server';
import { formatDate, formatEventCategory } from '@/lib/format';
import type { EventRow } from '@/lib/types';

export const dynamic = 'force-dynamic';

/** The fields the headline tiles report, in the order they are shown. */
const HEADLINE_FIELDS = [
  { field: 'operator', label: 'Operator recorded' },
  { field: 'lga', label: 'Council recorded' },
  { field: 'total_capacity_mw', label: 'Total capacity recorded' },
  { field: 'lat', label: 'Coordinates recorded' },
] as const;

/**
 * Home: what the record holds, then the timeline.
 *
 * The page leads with the state of the record because that is the finding a
 * first-time reader most needs: how much of what is said about these sites
 * has been established from a source. Every number is a count of rows. The
 * timeline follows, on combinable tracks whose selection lives in the URL so
 * "planning and community events only" can be shared as a link.
 */
export default async function HomePage({
  searchParams,
}: {
  searchParams: { tracks?: string };
}) {
  const tracks = parseTracks(searchParams.tracks);
  const [sites, gaps, loadedAt, events] = await Promise.all([
    listSites(),
    listGaps('sites'),
    lastLoadedAt(),
    listEvents({ categories: tracks, limit: 200 }),
  ]);
  const coverage = new Map(siteCoverage(sites, gaps).map((c) => [c.field, c]));
  const byYear = groupEventsByYear(events);

  return (
    <div className="space-y-12">
      <div>
        <h1 className="text-2xl font-bold text-slate-900">What is on the record</h1>
        <p className="mt-2 max-w-2xl text-slate-700">
          The observatory tracks data centre sites in Australia. Each figure
          below counts what the record holds: a value drawn from a source, or a
          gap with a stated reason. Nothing is estimated.
        </p>
        <DateStamp dataAsOfDate={loadedAt} className="mt-2" />
      </div>

      {!isConfigured() ? (
        <NotConnected what="sites or events" />
      ) : (
        <>
          <section aria-labelledby="summary-heading" className="space-y-6">
            <h2 id="summary-heading" className="sr-only">
              Record summary
            </h2>

            {sites.length === 0 ? (
              <NothingRecorded what="sites" />
            ) : (
              <>
                <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-5">
                  <StatTile label="Sites tracked" value={sites.length} />
                  {HEADLINE_FIELDS.map(({ field, label }) => (
                    <StatTile
                      key={field}
                      label={label}
                      value={coverage.get(field)?.known ?? 0}
                      total={sites.length}
                    />
                  ))}
                </div>
                <p className="text-sm">
                  <Link href="/coverage" className="text-fact-ink underline underline-offset-2">
                    What is known for every field
                  </Link>
                </p>

                <section aria-labelledby="status-heading">
                  <h3 id="status-heading" className="text-lg font-semibold text-slate-900">
                    Sites by status
                  </h3>
                  <p className="mt-1 text-sm text-slate-600">
                    In order from first report to operation, then sites that
                    left the pipeline.
                  </p>
                  <div className="mt-3 max-w-2xl">
                    <StatusBreakdown counts={statusCounts(sites)} />
                  </div>
                </section>
              </>
            )}
          </section>

          <section aria-labelledby="timeline-heading" className="space-y-6">
            <div>
              <h2 id="timeline-heading" className="text-xl font-bold text-slate-900">
                Timeline
              </h2>
              <p className="mt-2 max-w-2xl text-slate-700">
                Planning, construction, media, political, community and
                financial events, on combinable tracks. Every entry is dated and
                sourced.
              </p>
            </div>

            <Suspense fallback={null}>
              <TimelineTrackSelector selected={tracks} />
            </Suspense>

            {byYear.length === 0 ? (
              <NothingRecorded what="events" />
            ) : (
              <ol className="space-y-10">
                {byYear.map(({ year, events: yearEvents }) => (
                  <li key={year}>
                    <h3 className="sticky top-0 bg-white py-2 text-lg font-semibold text-slate-900">
                      {year}
                    </h3>
                    <ul className="mt-2 space-y-4 border-l-2 border-fact-edge pl-5">
                      {yearEvents.map((event) => (
                        <TimelineEntry key={event.id} event={event} />
                      ))}
                    </ul>
                  </li>
                ))}
              </ol>
            )}
          </section>
        </>
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

      <h4 className="mt-1 font-medium text-slate-900">{event.title}</h4>
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
