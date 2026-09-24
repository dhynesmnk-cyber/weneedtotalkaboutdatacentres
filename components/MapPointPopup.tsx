import Link from 'next/link';
import { formatMw, formatSiteStatus } from '@/lib/format';
import type { SiteRow } from '@/lib/types';

/**
 * Popup contents for a map point: name, operator, status, capacity.
 *
 * Missing values are named rather than blanked. A popup that silently omits
 * capacity reads as though the site has none.
 */
export function MapPointPopup({
  site,
  council = site.lga,
}: {
  site: SiteRow;
  /**
   * The council in its approved spelling, resolved by the caller. Defaults to
   * the recorded value, so a popup rendered without it shows what is stored
   * rather than nothing.
   */
  council?: string | null;
}) {
  const status = formatSiteStatus(site.status);
  const capacity = formatMw(site.total_capacity_mw);

  return (
    <div className="min-w-48 text-sm">
      <h3 className="text-base font-semibold text-fact-ink">{site.name}</h3>

      <dl className="mt-2 space-y-1">
        <Row label="Operator" value={site.operator} />
        <Row label="Status" value={status} />
        <Row label="Capacity" value={capacity} />
        <Row label="Council" value={council} />
      </dl>

      <Link
        href={`/sites/${site.id}`}
        className="mt-3 inline-block font-medium text-fact-ink underline underline-offset-2"
      >
        Full site record
      </Link>
    </div>
  );
}

function Row({ label, value }: { label: string; value: string | null }) {
  return (
    <div className="flex gap-2">
      <dt className="shrink-0 text-slate-600">{label}</dt>
      <dd className={value ? 'font-medium' : 'italic text-slate-500'}>
        {value ?? 'Not recorded'}
      </dd>
    </div>
  );
}
