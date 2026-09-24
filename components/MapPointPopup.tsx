import Link from 'next/link';
import { GapBadge, UnexplainedBadge } from '@/components/GapBadge';
import { formatMw, formatSiteStatus } from '@/lib/format';
import type { GapReason, SiteRow } from '@/lib/types';

/** The fields a popup shows, by the name their gaps are recorded under. */
export type PopupGaps = Partial<Record<'operator' | 'status' | 'total_capacity_mw' | 'lga', GapReason>>;

/**
 * Popup contents for a map point: name, operator, status, capacity.
 *
 * Missing values are named rather than blanked, with the same gap badge the
 * site record uses. A popup that silently omits capacity reads as though the
 * site has none.
 */
export function MapPointPopup({
  site,
  council = site.lga,
  gaps = {},
}: {
  site: SiteRow;
  /**
   * The council in its approved spelling, resolved by the caller. Defaults to
   * the recorded value, so a popup rendered without it shows what is stored
   * rather than nothing.
   */
  council?: string | null;
  gaps?: PopupGaps;
}) {
  const status = formatSiteStatus(site.status);
  const capacity = formatMw(site.total_capacity_mw);

  return (
    <div className="min-w-48 text-sm">
      <h3 className="text-base font-semibold text-fact-ink">{site.name}</h3>

      <dl className="mt-2 space-y-1">
        <Row label="Operator" value={site.operator} gap={gaps.operator} />
        <Row label="Status" value={status} gap={gaps.status} />
        <Row label="Capacity" value={capacity} gap={gaps.total_capacity_mw} />
        <Row label="Council" value={council} gap={gaps.lga} />
      </dl>

      {/* `!` because leaflet.css colours every `.leaflet-container a`, which
          outranks a single utility class and turned this link Leaflet blue. */}
      <Link
        href={`/sites/${site.id}`}
        className="mt-3 inline-block font-medium !text-fact-ink underline underline-offset-2"
      >
        Full site record
      </Link>
    </div>
  );
}

function Row({
  label,
  value,
  gap,
}: {
  label: string;
  value: string | null;
  gap: GapReason | undefined;
}) {
  return (
    <div className="flex items-baseline gap-2">
      <dt className="shrink-0 text-slate-600">{label}</dt>
      <dd className="font-medium">
        {value ?? (gap ? <GapBadge reason={gap} /> : <UnexplainedBadge />)}
      </dd>
    </div>
  );
}
