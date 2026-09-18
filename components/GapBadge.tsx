import { formatGapReason } from '@/lib/format';
import type { GapReason } from '@/lib/types';

/**
 * Explicit missing data marker.
 *
 * A gap badge always states why a value is missing, never merely that it is.
 * "Not disclosed" and "not yet researched" are different findings, and the
 * difference is often the story. See docs/UI.md "Gap presentation".
 */
export function GapBadge({
  reason,
  sourceHref,
}: {
  reason: GapReason;
  sourceHref?: string | undefined;
}) {
  const label = formatGapReason(reason);

  const badge = (
    <span
      className="inline-flex items-center gap-1 rounded border border-gap-edge
                 bg-gap-wash px-2 py-0.5 text-sm font-medium text-gap-ink"
    >
      <span aria-hidden="true">◌</span>
      {label}
    </span>
  );

  if (!sourceHref) return badge;

  return (
    <a
      href={sourceHref}
      className="rounded underline decoration-gap-edge underline-offset-2"
      aria-label={`${label}. View the source for this gap.`}
    >
      {badge}
    </a>
  );
}

/**
 * A field with no value and no recorded gap.
 *
 * This is a data quality defect under docs/QUALITY.md, not a gap, and it is
 * shown as one so that a missing gap record cannot hide as a deliberate
 * omission.
 */
export function UnexplainedBadge() {
  return (
    <span
      className="inline-flex items-center gap-1 rounded border border-red-300
                 bg-red-50 px-2 py-0.5 text-sm font-medium text-red-800"
      title="No value and no recorded gap. This is a data quality defect."
    >
      <span aria-hidden="true">!</span>
      No value recorded
    </span>
  );
}
