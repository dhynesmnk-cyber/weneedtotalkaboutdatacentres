import Link from 'next/link';
import { formatDate, formatEventCategory } from '@/lib/format';
import type { EventCategory, EventRow } from '@/lib/types';

/**
 * Track colours, written out in full so Tailwind can see every class.
 * Values come from lib/design/tokens.ts (UX-PLAN G2).
 */
const TRACK_CHIP: Record<EventCategory, string> = {
  planning: 'bg-track-planning-wash text-track-planning-ink',
  construction: 'bg-track-construction-wash text-track-construction-ink',
  media: 'bg-track-media-wash text-track-media-ink',
  political: 'bg-track-political-wash text-track-political-ink',
  community: 'bg-track-community-wash text-track-community-ink',
  financial: 'bg-track-financial-wash text-track-financial-ink',
};

const TRACK_DOT: Record<EventCategory, string> = {
  planning: 'bg-track-planning-ink',
  construction: 'bg-track-construction-ink',
  media: 'bg-track-media-ink',
  political: 'bg-track-political-ink',
  community: 'bg-track-community-ink',
  financial: 'bg-track-financial-ink',
};

/** The event's track, named in words and coloured by track. */
export function TrackChip({ category }: { category: EventCategory }) {
  return (
    <span
      className={`rounded px-2 py-0.5 text-xs font-semibold ${TRACK_CHIP[category] ?? 'bg-fact-wash text-fact-ink'}`}
    >
      {formatEventCategory(category)}
    </span>
  );
}

/**
 * One dated event. The same markup on the timeline, a site record and an
 * entity record, so an event reads the same wherever it is met.
 *
 * - `timeline`: a point on the year line, with a marker in the track colour.
 * - `card`: a bordered item in a list on a record page.
 */
export function EventItem({
  event,
  variant = 'card',
  showSummary = true,
  showSiteLink = false,
  titleAs: Title = 'p',
}: {
  event: EventRow;
  variant?: 'timeline' | 'card';
  showSummary?: boolean;
  showSiteLink?: boolean;
  /** A heading where events sit under a heading of their own, as on the timeline. */
  titleAs?: 'p' | 'h3' | 'h4';
}) {
  const body = (
    <>
      <div className="flex flex-wrap items-baseline gap-x-3 gap-y-1">
        <TrackChip category={event.category} />
        <time dateTime={event.date} className="text-sm text-slate-600">
          {formatDate(event.date)}
        </time>
      </div>
      <Title className="mt-1 font-medium text-slate-900">{event.title}</Title>
      {showSummary && event.summary && (
        <p className="mt-1 text-sm text-slate-700">{event.summary}</p>
      )}
      {showSiteLink && event.site_id && (
        <Link href={`/sites/${event.site_id}`} className="link mt-1 inline-block text-sm">
          Related site
        </Link>
      )}
    </>
  );

  if (variant === 'timeline') {
    return (
      <li className="relative">
        <span
          aria-hidden="true"
          className={`absolute -left-[1.6rem] top-2 h-2.5 w-2.5 rounded-full ${TRACK_DOT[event.category] ?? 'bg-fact-ink'}`}
        />
        {body}
      </li>
    );
  }

  return <li className="rounded border border-slate-200 px-4 py-3">{body}</li>;
}
