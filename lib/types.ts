/**
 * Database types.
 *
 * Hand-written for now and kept in step with supabase/migrations by the tests in
 * tests/schema.test.ts, which parse the SQL and compare. Once a Supabase project
 * exists these should be replaced by `supabase gen types typescript`, and that
 * test deleted rather than maintained alongside a generator.
 */

export type SiteStatus =
  | 'proposed'
  | 'approved'
  | 'under_construction'
  | 'operating'
  | 'stalled'
  | 'withdrawn';

export type EventCategory =
  | 'planning'
  | 'construction'
  | 'media'
  | 'political'
  | 'community'
  | 'financial';

export type GapReason =
  | 'unknown'
  | 'not_disclosed'
  | 'not_applicable'
  | 'withheld';

export type LinkState = 'proposed' | 'confirmed';

export type CitableRecord =
  | 'sites'
  | 'entities'
  | 'events'
  | 'case_studies'
  | 'essays';

export type SourceRow = {
  id: string;
  type: string;
  title: string;
  url: string | null;
  retrieved_date: string;
  publisher: string | null;
  created_at: string;
  updated_at: string;
};

/** Every field bar id and name is nullable. A null is a gap, not an oversight. */
export type SiteRow = {
  id: string;
  name: string;
  operator: string | null;
  lat: number | null;
  lng: number | null;
  lga: string | null;
  status: SiteStatus | null;
  total_capacity_mw: number | null;
  live_capacity_mw: number | null;
  cooling_type: string | null;
  rack_density_kw: number | null;
  grid_connection: string | null;
  water_usage: number | null;
  notes: string | null;
  created_at: string;
  updated_at: string;
};

export type EntityRow = {
  id: string;
  name: string;
  type: string | null;
  role: string | null;
  major_flag: boolean;
  public_actions_summary: string | null;
  created_at: string;
  updated_at: string;
};

export type EventRow = {
  id: string;
  category: EventCategory;
  date: string;
  title: string;
  summary: string | null;
  site_id: string | null;
  created_at: string;
  updated_at: string;
};

export type LinkRow = {
  id: string;
  site_id: string | null;
  entity_id: string | null;
  event_id: string | null;
  state: LinkState;
  confirmed_by: string | null;
  confirmed_at: string | null;
  created_at: string;
};

export type CitationRow = {
  id: string;
  source_id: string;
  record_type: CitableRecord;
  record_id: string;
  claim: string | null;
  created_at: string;
};

export type DataGapRow = {
  id: string;
  record_type: CitableRecord;
  record_id: string;
  field_name: string;
  reason: GapReason;
  noted_date: string;
  source_id: string | null;
  created_at: string;
};

export type CouncilWatchlistRow = {
  id: string;
  lga: string;
  state: string;
  approved_by: string;
  approved_at: string;
  notes: string | null;
  created_at: string;
};

export type CaseStudyRow = {
  id: string;
  title: string;
  publish_date: string | null;
  data_as_of_date: string;
  site_id: string | null;
  metrics: CaseStudyMetrics;
  narrative: string | null;
  approved_by: string | null;
  approved_at: string | null;
  created_at: string;
  updated_at: string;
};

/**
 * Financial metrics for a case study. Every one is optional: a missing figure is
 * recorded in data_gaps, never estimated. See docs/SPEC.md.
 */
export type CaseStudyMetrics = {
  total_capex_aud?: number;
  annual_revenue_aud?: number;
  annual_opex_aud?: number;
  development_yield_pct?: number;
  stabilised_cap_rate_pct?: number;
  power_cost_per_kw?: number;
};

export type EssayRow = {
  id: string;
  title: string;
  publish_date: string | null;
  youtube_id: string | null;
  body: string | null;
  tags: string[];
  related_ids: string[];
  approved_by: string | null;
  approved_at: string | null;
  created_at: string;
  updated_at: string;
};

type Table<R> = {
  Row: R;
  Insert: Partial<R>;
  Update: Partial<R>;
  Relationships: [];
};

export interface Database {
  facts: {
    Tables: {
      sources: Table<SourceRow>;
      sites: Table<SiteRow>;
      entities: Table<EntityRow>;
      events: Table<EventRow>;
      links: Table<LinkRow>;
      citations: Table<CitationRow>;
      data_gaps: Table<DataGapRow>;
      council_watchlist: Table<CouncilWatchlistRow>;
    };
    Views: Record<string, never>;
    Functions: Record<string, never>;
    Enums: {
      site_status: SiteStatus;
      event_category: EventCategory;
      gap_reason: GapReason;
      link_state: LinkState;
      citable_record: CitableRecord;
    };
    CompositeTypes: Record<string, never>;
  };
  editorial: {
    Tables: {
      case_studies: Table<CaseStudyRow>;
      essays: Table<EssayRow>;
    };
    Views: Record<string, never>;
    Functions: Record<string, never>;
    Enums: Record<string, never>;
    CompositeTypes: Record<string, never>;
  };
}

/** A site with its gaps and citations resolved, ready to render. */
export interface SiteWithEvidence {
  site: SiteRow;
  gaps: DataGapRow[];
  citations: CitationWithSource[];
}

export interface CitationWithSource extends CitationRow {
  source: SourceRow | null;
}

export const SITE_STATUSES: readonly SiteStatus[] = [
  'proposed',
  'approved',
  'under_construction',
  'operating',
  'stalled',
  'withdrawn',
] as const;

export const EVENT_CATEGORIES: readonly EventCategory[] = [
  'planning',
  'construction',
  'media',
  'political',
  'community',
  'financial',
] as const;

export const GAP_REASONS: readonly GapReason[] = [
  'unknown',
  'not_disclosed',
  'not_applicable',
  'withheld',
] as const;
