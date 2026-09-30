// lib/types.ts
// Typed domain model mirroring the Supabase schema (docs/SPEC.md).
// The database is the source of truth; these types describe rows only.
// Australian English in all user-facing strings.

/** Explicit missing-data marker. Never infer or fabricate values. */
export type GapReason =
  | "not_published" // source has not published the value
  | "not_tracked" // outside our approved ingestion scope
  | "pending_verification" // candidate value awaiting human verification
  | "conflicting_sources"; // sources disagree; unresolved

export interface GapFlag {
  readonly reason: GapReason;
  /** Optional human note, e.g. "council refused to release submission counts". */
  readonly note?: string;
}

/** A field that may be unknown — render with GapBadge, never blank. */
export type Field<T> =
  | { readonly kind: "value"; readonly value: T }
  | { readonly kind: "gap"; readonly gap: GapFlag };

export type SiteStatus =
  | "proposed"
  | "approved"
  | "under_construction"
  | "live"
  | "stalled"
  | "cancelled";

export type EventCategory =
  | "planning"
  | "construction"
  | "media"
  | "political"
  | "community"
  | "financial";

export type EntityType =
  | "operator"
  | "investor"
  | "developer"
  | "government"
  | "community_group"
  | "utility";

export interface SourceRecord {
  readonly id: number;
  readonly type: "news" | "council" | "aemo" | "asx" | "company" | "government" | "other";
  readonly title: string;
  readonly url: string;
  readonly retrievedDate: string; // ISO date
  readonly publisher: string;
}

export interface Citation {
  readonly recordTable: "sites" | "entities" | "events" | "case_studies" | "essays";
  readonly recordId: number;
  readonly sourceId: number;
  readonly claimSummary?: string;
}

export interface Site {
  readonly id: number;
  readonly slug: string; // stable deep link (migration M3)
  readonly name: string;
  readonly operator: Field<string>;
  readonly lat: number;
  readonly lng: number;
  readonly lgaCode: string;
  readonly lgaName: string;
  readonly status: Field<SiteStatus>;
  readonly totalCapacityMW: Field<number>;
  readonly liveCapacityMW: Field<number>;
  readonly coolingType: Field<string>;
  readonly rackDensityKW: Field<number>;
  readonly gridConnection: Field<string>;
  readonly waterUsage: Field<string>;
  readonly notes?: string;
}

export interface Entity {
  readonly id: number;
  readonly slug: string;
  readonly name: string;
  readonly type: EntityType;
  readonly role: string;
  readonly majorFlag: boolean;
  readonly publicActionsSummary?: string;
}

export interface ObservatoryEvent {
  readonly id: number;
  readonly slug: string;
  readonly category: EventCategory;
  readonly date: string; // ISO date — every event is dated
  readonly title: string;
  readonly summary: string;
  readonly siteId?: number;
  readonly entityIds: readonly number[];
  readonly sourceIds: readonly number[];
  readonly significance: "major" | "notable" | "routine";
}

export interface FinancialMetrics {
  readonly totalCapexAUD: Field<number>;
  readonly annualRevenueAUD: Field<number>;
  readonly annualOpexAUD: Field<number>;
  readonly developmentYieldPct: Field<number>;
  readonly stabilisedCapRatePct: Field<number>;
  readonly powerCostPerKW: Field<number>;
}

export interface CaseStudy {
  readonly id: number;
  readonly slug: string;
  readonly title: string;
  readonly publishDate: string;
  readonly dataAsOfDate: string;
  readonly siteId?: number;
  readonly metrics: FinancialMetrics;
  readonly narrative: string;
  readonly sourceIds: readonly number[];
}

export interface Essay {
  readonly id: number;
  readonly slug: string;
  readonly title: string;
  readonly publishDate: string;
  readonly youtubeId?: string;
  readonly body: string;
  readonly tags: readonly string[];
  readonly relatedRecordIds: readonly Citation[];
  /** Editorial layer — clearly separated from fact layer in UI and data. */
  readonly layer: "editorial";
}

export interface Locality {
  readonly name: string;
  readonly postcode: string;
  readonly lgaCode: string;
  readonly lgaName: string;
  readonly lat: number;
  readonly lng: number;
  readonly sourceId: number; // every row carries a source (M1)
  readonly asOfDate: string;
}

export interface RollupRow {
  readonly state: string;
  readonly status: SiteStatus;
  readonly siteCount: number;
  readonly totalCapacityMW: Field<number>; // gap if any member is unknown
}

export interface DigestItem {
  readonly eventId?: number;
  readonly essayId?: number;
  readonly headline: string;
  readonly summary: string;
}

export interface Digest {
  readonly id: number;
  readonly slug: string;
  readonly month: string; // YYYY-MM
  readonly publishDate: string;
  readonly dataAsOfDate: string;
  readonly items: readonly DigestItem[];
  readonly psaTag: boolean;
  readonly expiryDate?: string; // PSAs expire automatically
  readonly approvedBy: string; // always a human (CLAUDE.md hard rule)
}

/** Perception-claim vs evidence-record pairing (core narrative device). */
export interface ClaimVsRecordPair {
  readonly claim: string;
  readonly claimSourceId: number;
  readonly recordSummary: string;
  readonly recordTable: Citation["recordTable"];
  readonly recordId: number;
  readonly recordDate: string;
}
