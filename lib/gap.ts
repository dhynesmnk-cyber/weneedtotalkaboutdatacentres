// lib/gap.ts
// Gap-flag helpers. Hard rule: never infer or fabricate values; a gap badge is
// always better than a blank or a guess.

import type { Field, GapFlag, GapReason } from "./types";

export const value = <T>(v: T): Field<T> => ({ kind: "value", value: v });

export const gap = (reason: GapReason, note?: string): Field<never> => ({
  kind: "gap",
  gap: note ? { reason, note } : { reason },
});

export const isGap = (f: Field<unknown>): boolean => f.kind === "gap";

/** User-facing wording for each gap reason (Australian English). */
export const GAP_LABELS: Record<GapReason, string> = {
  not_published: "Not published by the source",
  not_tracked: "Outside our tracking scope",
  pending_verification: "Awaiting verification",
  conflicting_sources: "Sources disagree",
};

export const gapLabel = (g: GapFlag): string =>
  g.note ? `${GAP_LABELS[g.reason]} — ${g.note}` : GAP_LABELS[g.reason];

/** Render helper: format a Field<number> with unit, or return null so the
 * caller must render a GapBadge. Components must never show a bare blank. */
export function formatNumberField(
  f: Field<number>,
  unit: string,
  formatter: Intl.NumberFormat = new Intl.NumberFormat("en-AU"),
): string | null {
  if (f.kind === "gap") return null;
  return `${formatter.format(f.value)} ${unit}`.trim();
}
