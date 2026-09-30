// lib/dates.ts
// Everything is dated (UI.md principle). Publish date and data-as-of date are
// always shown together; PSAs expire automatically.

export const formatDateAu = (iso: string): string =>
  new Date(`${iso}T00:00:00`).toLocaleDateString("en-AU", {
    day: "numeric",
    month: "long",
    year: "numeric",
  });

export const formatMonthAu = (yyyyMm: string): string => {
  const [y, m] = yyyyMm.split("-").map(Number);
  return new Date(y, m - 1, 1).toLocaleDateString("en-AU", {
    month: "long",
    year: "numeric",
  });
};

/** Rolling window test used by the timeline default (C1: last 12 months). */
export function withinMonths(iso: string, months: number, now: Date = new Date()): boolean {
  const then = new Date(`${iso}T00:00:00`);
  const cutoff = new Date(now);
  cutoff.setMonth(cutoff.getMonth() - months);
  return then >= cutoff && then <= now;
}

/** PSA expiry check (M5): an expired notice must never render as current. */
export function isExpired(expiryIso: string | undefined, now: Date = new Date()): boolean {
  if (!expiryIso) return false;
  return new Date(`${expiryIso}T23:59:59`) < now;
}

/** Correction SLA helper (QUALITY.md): publish → resolve duration in days. */
export function daysBetween(startIso: string, endIso: string): number {
  const a = new Date(`${startIso}T00:00:00`).getTime();
  const b = new Date(`${endIso}T00:00:00`).getTime();
  return Math.round((b - a) / 86_400_000);
}
