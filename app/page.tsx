import Link from 'next/link';
import { Suspense } from 'react';
import { TimelineTrackSelector } from '@/components/TimelineTrackSelector';
import { parseTracks } from '@/lib/timeline';
import { NotConnected, NothingRecorded } from '@/components/NotConnected';
import { StatTile } from '@/components/StatTile';
import { StatusBreakdown } from '@/components/StatusBreakdown';
import { DateStamp } from '@/components/DateStamp';
import { EvidenceBadge } from '@/components/EvidenceBadge';
import { groupEventsByYear, listEvents } from '@/lib/events';
import { listSites } from '@/lib/sites';
import { listGaps } from '@/lib/evidence';
import { aliasMap, listLgaAliases } from '@/lib/councils';
import { lastLoadedAt, siteCoverage, statusCounts } from '@/lib/coverage';
import { evidenceCounts, largestCapacity, topCouncil } from '@/lib/findings';
import { DEFAULT_QUERY, indexHref } from '@/lib/siteIndex';
import { isConfigured } from '@/lib/supabase/server';
import { formatDate, formatEventCategory, formatMw } from '@/lib/format';
import { EVENT_CATEGORIES, type EventRow } from '@/lib/types';

export const dynamic = 'force-dynamic';

/** The fields the completeness tiles report, in the order they are shown. */
const HEADLINE_FIELDS = [
  { field: 'operator', label: 'Operator recorded' },
  { field: 'lga', label: 'Council recorded' },
  { field: 'total_capacity_mw', label: 'Total capacity recorded' },
  { field: 'lat', label: 'Coordinates recorded' },
] as const;

const link = 'text-fact-ink underline underline-offset-2';

/**
 * Home: the front door.
 *
 * A first-time reader meets, in order: what the site is, the two ways to read
 * it (the record and the analysis, kept apart), a few findings from the
 * record, how complete the record is, and the timeline once it has events.
 *
 * Everything the page says about the world is a count or value read off the
 * record and linked to where it can be checked. The premise describes what
 * the site does, not the industry, because a claim about the industry would
 * need a source like any other.
 */
export default async function HomePage({
  searchParams,
}: {
  searchParams: { tracks?: string };
}) {
  const tracks = parseTracks(searchParams.tracks);
  const [sites, gaps, loadedAt, events, anyEvents, aliases] = await Promise.all([
    listSites(),
    listGaps('sites'),
    lastLoadedAt(),
    listEvents({ categories: tracks, limit: 200 }),
    listEvents({ categories: [...EVENT_CATEGORIES], limit: 1 }),
    listLgaAliases(),
  ]);
  const coverage = new Map(siteCoverage(sites, gaps).map((c) => [c.field, c]));
  const byYear = groupEventsByYear(events);
  const largest = largestCapacity(sites);
  const council = topCouncil(sites, aliasMap(aliases));
  const evidence = new Map(evidenceCounts(sites).map((e) => [e.status, e.count]));

  return (
    <div className="space-y-14">
      <div>
        <h1 className="text-3xl font-bold text-slate-900">
          Australia&rsquo;s data centres, on the record
        </h1>
        <p className="mt-3 max-w-2xl text-lg text-slate-700">
          This observatory tracks proposed and operating data centres in Australia,
          including those built for AI. For each site it records what the public record
          shows, from planning documents, regulators and company statements, and marks
          plainly what has not been published. Analysis and argument are kept separate,
          and labelled as such.
        </p>
        <p className="mt-3 text-sm">
          <Link href="/how-to-read" className={link}>
            How to read this site
          </Link>
        </p>
      </div>

      <section aria-labelledby="layers-heading">
        <h2 id="layers-heading" className="sr-only">
          Two ways to read this site
        </h2>
        <div className="grid gap-4 md:grid-cols-2">
          <div className="rounded-lg border-l-4 border-fact-edge bg-fact-wash p-5">
            <p className="text-xs font-semibold uppercase tracking-wide text-fact-ink">
              The record
            </p>
            <p className="mt-2 text-slate-800">
              Sourced facts about each site: status, operator, capacity, council. Every
              fact links to its source, and every gap says why it is a gap.
            </p>
            <p className="mt-3 flex flex-wrap gap-x-4 gap-y-1 text-sm">
              <Link href="/list" className={link}>
                Browse the sites
              </Link>
              <Link href="/map" className={link}>
                See the map
              </Link>
              <Link href="/coverage" className={link}>
                What&rsquo;s known
              </Link>
            </p>
          </div>
          <div className="rounded-lg border-l-4 border-editorial-edge bg-editorial-wash p-5">
            <p className="text-xs font-semibold uppercase tracking-wide text-editorial-ink">
              The analysis
            </p>
            <p className="mt-2 text-slate-800">
              Essays and case studies that argue from the record. They are a point of view,
              dated and sourced, and always marked where analysis begins.
            </p>
            <p className="mt-3 text-sm">
              <Link href="/essays" className="text-editorial-ink underline underline-offset-2">
                Read the analysis
              </Link>
            </p>
          </div>
        </div>
      </section>

      {!isConfigured() ? (
        <NotConnected what="sites or events" />
      ) : sites.length === 0 ? (
        <NothingRecorded what="sites" />
      ) : (
        <>
          <section aria-labelledby="findings-heading" className="space-y-4">
            <div>
              <h2 id="findings-heading" className="text-xl font-bold text-slate-900">
                From the record
              </h2>
              <DateStamp dataAsOfDate={loadedAt} className="mt-1" />
            </div>
            <ul className="space-y-3">
              {largest && (
                <Finding>
                  <Link href={`/sites/${largest.site.id}`} className={link}>
                    {largest.site.name}
                  </Link>{' '}
                  has the largest total capacity on the record: {formatMw(largest.mw)}. Only{' '}
                  {largest.of} of {sites.length} sites have a published total capacity.
                </Finding>
              )}
              {council && (
                <Finding>
                  <Link
                    href={indexHref({ ...DEFAULT_QUERY, council: council.council })}
                    className={link}
                  >
                    {council.council}
                  </Link>{' '}
                  has more sites than any other council: {council.count} of {sites.length}.
                </Finding>
              )}
              {(evidence.get('claimed') ?? 0) > 0 && (
                <Finding>
                  <Link
                    href={indexHref({ ...DEFAULT_QUERY, evidence: 'claimed' })}
                    className={link}
                  >
                    {evidence.get('claimed')} sites
                  </Link>{' '}
                  rest only on a developer&rsquo;s or industry body&rsquo;s own statement,
                  which no one has independently confirmed.{' '}
                  <span className="whitespace-nowrap">
                    <EvidenceBadge status="claimed" size="sm" />
                  </span>
                </Finding>
              )}
              {(evidence.get('verified') ?? 0) > 0 && (
                <Finding>
                  <Link
                    href={indexHref({ ...DEFAULT_QUERY, evidence: 'verified' })}
                    className={link}
                  >
                    {evidence.get('verified')} sites
                  </Link>{' '}
                  are verified against a primary document, such as a planning record or a
                  regulator.{' '}
                  <span className="whitespace-nowrap">
                    <EvidenceBadge status="verified" size="sm" />
                  </span>
                </Finding>
              )}
            </ul>
          </section>

          <section aria-labelledby="summary-heading" className="space-y-6">
            <div>
              <h2 id="summary-heading" className="text-xl font-bold text-slate-900">
                How complete the record is
              </h2>
              <p className="mt-1 max-w-2xl text-sm text-slate-700">
                A missing figure is shown as a gap, never estimated. When a developer has
                not published something, that absence is itself a finding.
              </p>
            </div>
            <div className="grid grid-cols-2 gap-3 lg:grid-cols-5">
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
              <Link href="/coverage" className={link}>
                What is known for every field
              </Link>
            </p>

            <section aria-labelledby="status-heading">
              <h3 id="status-heading" className="text-lg font-semibold text-slate-900">
                Sites by status
              </h3>
              <p className="mt-1 text-sm text-slate-600">
                In order from first report to operation, then sites that left the pipeline.
              </p>
              <div className="mt-3 max-w-2xl">
                <StatusBreakdown counts={statusCounts(sites)} />
              </div>
            </section>
          </section>

          <section aria-labelledby="timeline-heading" className="space-y-6">
            <div>
              <h2 id="timeline-heading" className="text-xl font-bold text-slate-900">
                Timeline
              </h2>
              <p className="mt-2 max-w-2xl text-slate-700">
                Planning, construction, media, political, community and financial events,
                on combinable tracks. Every entry is dated and sourced.
              </p>
            </div>

            {anyEvents.length === 0 ? (
              // No controls for a timeline with nothing on it: six working
              // checkboxes over an empty list read as a broken page.
              <p className="text-sm text-slate-700">
                No events have been recorded yet. They will appear here as they are
                added.
              </p>
            ) : (
              <>
                <Suspense fallback={null}>
                  <TimelineTrackSelector selected={tracks} />
                </Suspense>

                {byYear.length === 0 ? (
                  <NothingRecorded what="events on these tracks" />
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
              </>
            )}
          </section>
        </>
      )}
    </div>
  );
}

function Finding({ children }: { children: React.ReactNode }) {
  return (
    <li className="max-w-3xl rounded-lg border-l-4 border-fact-edge bg-fact-wash/40 py-2 pl-4 pr-3 text-slate-800">
      {children}
    </li>
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
