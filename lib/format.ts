import type {
  ConfidenceLevel,
  EventCategory,
  FactStatus,
  GapReason,
  ResearchStatus,
  SiteStatus,
} from '@/lib/types';

/**
 * Presentation helpers. Australian English throughout, per CLAUDE.md.
 *
 * Every formatter takes a nullable input and returns null for a missing value,
 * so callers must decide what to render in its place. There is no default
 * em dash here: a missing value is a gap, and a GapBadge states why.
 */

const AU_DATE = new Intl.DateTimeFormat('en-AU', {
  day: 'numeric',
  month: 'long',
  year: 'numeric',
  timeZone: 'UTC',
});

const AU_MONTH = new Intl.DateTimeFormat('en-AU', {
  month: 'long',
  year: 'numeric',
  timeZone: 'UTC',
});

const AUD = new Intl.NumberFormat('en-AU', {
  style: 'currency',
  currency: 'AUD',
  maximumFractionDigits: 0,
});

/** "18 September 2026". Date-only strings are read as UTC to avoid drift. */
export function formatDate(value: string | null | undefined): string | null {
  const date = parseDate(value);
  return date ? AU_DATE.format(date) : null;
}

/** "September 2026". */
export function formatMonth(value: string | null | undefined): string | null {
  const date = parseDate(value);
  return date ? AU_MONTH.format(date) : null;
}

/** "$1,200,000". Rounded to whole dollars; these are never precise to the cent. */
export function formatAud(value: number | null | undefined): string | null {
  if (!Number.isFinite(value)) return null;
  return AUD.format(value as number);
}

/** "$1.2 billion" for headline figures where full precision is noise. */
export function formatAudCompact(value: number | null | undefined): string | null {
  if (!Number.isFinite(value)) return null;
  const n = value as number;

  const billion = 1_000_000_000;
  const million = 1_000_000;

  if (Math.abs(n) >= billion) {
    return `$${trimZero(n / billion)} billion`;
  }
  if (Math.abs(n) >= million) {
    return `$${trimZero(n / million)} million`;
  }
  return formatAud(n);
}

/** "150 MW". */
export function formatMw(value: number | null | undefined): string | null {
  if (!Number.isFinite(value)) return null;
  return `${trimZero(value as number)} MW`;
}

/** "8.5%". */
export function formatPct(value: number | null | undefined): string | null {
  if (!Number.isFinite(value)) return null;
  return `${trimZero(value as number)}%`;
}

/** "22.4 ML" for annual water usage, given a figure in megalitres. */
export function formatMegalitres(value: number | null | undefined): string | null {
  if (!Number.isFinite(value)) return null;
  return `${trimZero(value as number)} ML`;
}

const SITE_STATUS_LABELS: Record<SiteStatus, string> = {
  rumoured: 'Rumoured',
  pre_lodgement: 'Pre-lodgement',
  proposed: 'Proposed',
  lodged: 'Lodged',
  approved: 'Approved',
  under_construction: 'Under construction',
  operating: 'Operating',
  stalled: 'Stalled',
  refused: 'Refused',
  withdrawn: 'Withdrawn',
  cancelled: 'Cancelled',
};

/**
 * Reader-facing wording for how well established a claim is.
 *
 * A "claimed" figure is a proponent's assertion that nobody has independently
 * confirmed. Rendering it identically to a figure parsed from a planning
 * consent is the failure this project exists to correct, so the wording says
 * who is doing the asserting.
 */
const FACT_STATUS_LABELS: Record<FactStatus, string> = {
  gap: 'No value established',
  claimed: 'Claimed by proponent',
  reported: 'Reported by a secondary source',
  verified: 'Verified against a primary source',
};

export function formatFactStatus(value: FactStatus | null | undefined): string | null {
  return value ? FACT_STATUS_LABELS[value] : null;
}

const CONFIDENCE_LABELS: Record<ConfidenceLevel, string> = {
  low: 'Low confidence',
  medium: 'Medium confidence',
  high: 'High confidence',
};

export function formatConfidence(
  value: ConfidenceLevel | null | undefined,
): string | null {
  return value ? CONFIDENCE_LABELS[value] : null;
}

export function formatSiteStatus(value: SiteStatus | null | undefined): string | null {
  return value ? SITE_STATUS_LABELS[value] : null;
}

const EVENT_CATEGORY_LABELS: Record<EventCategory, string> = {
  planning: 'Planning',
  construction: 'Construction',
  media: 'Media',
  political: 'Political',
  community: 'Community',
  financial: 'Financial',
};

export function formatEventCategory(value: EventCategory): string {
  return EVENT_CATEGORY_LABELS[value];
}

/**
 * Reader-facing wording for a gap reason, per docs/UI.md "Gap presentation".
 * A badge always says why a value is missing, never just that it is.
 */
const GAP_REASON_LABELS: Record<GapReason, string> = {
  unknown: 'Not yet researched',
  not_disclosed: 'Not disclosed',
  not_applicable: 'Not applicable',
  withheld: 'Withheld in source',
};

export function formatGapReason(value: GapReason): string {
  return GAP_REASON_LABELS[value];
}

/**
 * Reader-facing wording for where a research question stands. "Won't fix" is
 * the curator's shorthand; a reader needs to know the question was closed
 * without an answer, not that something was broken.
 */
const RESEARCH_STATUS_LABELS: Record<ResearchStatus, string> = {
  in_progress: 'In progress',
  open: 'Open',
  blocked: 'Blocked',
  resolved: 'Resolved',
  wont_fix: 'Closed without an answer',
};

export function formatResearchStatus(value: ResearchStatus): string {
  return RESEARCH_STATUS_LABELS[value];
}

/** The research's five lines of enquiry, as data-pipeline/README.md names them. */
const PILLAR_LABELS: Record<string, string> = {
  A: 'Physical infrastructure',
  B: 'Capital and control',
  C: 'Regulatory framework',
  D: 'Community impact',
  E: 'Engineering critique',
};

export function formatPillar(value: string | null | undefined): string | null {
  if (!value) return null;
  return PILLAR_LABELS[value] ?? value;
}

/**
 * How a question is to be answered, in words. An unrecognised method is shown
 * as recorded rather than hidden, so a new one in the pipeline is visible.
 */
const RETRIEVAL_METHOD_LABELS: Record<string, string> = {
  scrape_portal: 'Reading a public register or portal',
  foi_request: 'Freedom of information request',
  asic_search: 'Company register search (ASIC)',
  dataset_download: 'Downloading a published dataset',
  manual_review: 'Reading the documents',
  regulator_request: 'Request to a regulator',
  interview: 'Interview',
  not_retrievable: 'Not obtainable from a public source',
};

export function formatRetrievalMethod(value: string | null | undefined): string | null {
  if (!value) return null;
  return RETRIEVAL_METHOD_LABELS[value] ?? value;
}

/** Priority as the curator graded it: 5 is the most urgent (migration 0009). */
const PRIORITY_LABELS: Record<number, string> = {
  5: 'Most urgent',
  4: 'High priority',
  3: 'Medium priority',
  2: 'Low priority',
  1: 'Lowest priority',
};

export function formatPriority(value: number | null | undefined): string | null {
  if (value === null || value === undefined) return null;
  return PRIORITY_LABELS[value] ?? null;
}

/**
 * Fields whose reader-facing name is not their column name. `lga` is a
 * planning term most readers do not know, and title-casing it gives "Lga";
 * the rest of the site already calls it the council.
 */
const FIELD_LABELS: Record<string, string> = {
  lga: 'Council',
};

/** "total_capacity_mw" becomes "Total capacity". Units live in the value. */
export function formatFieldName(field: string): string {
  const label = FIELD_LABELS[field];
  if (label) return label;

  const withoutUnit = field
    .replace(/_mw$/, '')
    .replace(/_kw$/, '')
    .replace(/_aud$/, '')
    .replace(/_pct$/, '');

  const words = withoutUnit.split('_').filter(Boolean);
  if (words.length === 0) return field;

  const [first, ...rest] = words as [string, ...string[]];
  return [first.charAt(0).toUpperCase() + first.slice(1), ...rest].join(' ');
}

function parseDate(value: string | null | undefined): Date | null {
  if (!value) return null;
  // Date-only strings are treated as UTC midnight so that a date never shifts
  // by a day depending on where the reader is.
  const iso = /^\d{4}-\d{2}-\d{2}$/.test(value) ? `${value}T00:00:00Z` : value;
  const date = new Date(iso);
  return Number.isNaN(date.getTime()) ? null : date;
}

function trimZero(value: number): string {
  const rounded = Math.round(value * 10) / 10;
  return rounded.toLocaleString('en-AU', { maximumFractionDigits: 1 });
}
