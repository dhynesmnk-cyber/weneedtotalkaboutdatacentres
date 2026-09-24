import Link from 'next/link';
import type { StatusCount } from '@/lib/coverage';
import { formatSiteStatus } from '@/lib/format';
import { indexHref, DEFAULT_QUERY } from '@/lib/siteIndex';

/**
 * Sites per status, as a single-series bar list.
 *
 * One hue, because status here is one measure (a count) across ordered
 * categories, not several series. Every bar carries its number as text, and
 * the list is ordered by lifecycle, so the bars are a reading aid over a list
 * that stands on its own; they are hidden from assistive technology.
 * Each status links to the index filtered to it.
 */
export function StatusBreakdown({ counts }: { counts: StatusCount[] }) {
  const max = Math.max(1, ...counts.map((c) => c.count));

  return (
    <ul className="space-y-2">
      {counts.map(({ status, count }) => {
        const label = formatSiteStatus(status) ?? 'No status recorded';
        return (
          <li
            key={status ?? 'none'}
            className="grid grid-cols-[9rem_1fr_2.5rem] items-center gap-3 text-sm sm:grid-cols-[11rem_1fr_3rem]"
          >
            {status ? (
              <Link
                href={indexHref({ ...DEFAULT_QUERY, status })}
                className="text-fact-ink underline underline-offset-2"
              >
                {label}
              </Link>
            ) : (
              <span className="italic text-slate-600">{label}</span>
            )}
            <span aria-hidden="true" className="h-3">
              <span
                className="block h-3 rounded-r bg-fact-ink"
                style={{ width: `${((count / max) * 100).toFixed(1)}%` }}
              />
            </span>
            <span className="text-right tabular-nums text-slate-900">{count}</span>
          </li>
        );
      })}
    </ul>
  );
}
