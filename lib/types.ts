/**
 * Database types.
 *
 * Hand-written for now and kept in step with supabase/migrations by the tests in
 * tests/schema.test.ts, which parse the SQL and compare. Once a Supabase project
 * exists these should be replaced by `supabase gen types typescript`, and that
 * test deleted rather than maintained alongside a generator.
 */

export type SiteStatus =
  | 'rumoured'
  | 'pre_lodgement'
  | 'proposed'
  | 'lodged'
  | 'approved'
  | 'under_construction'
  | 'operating'
  | 'stalled'
  | 'refused'
  | 'withdrawn'
  | 'cancelled';

/** How well established a claim is. Ordered weakest to strongest. */
export type FactStatus = 'gap' | 'claimed' | 'reported' | 'verified';

/** Curator confidence, which is not the same thing as fact status. */
export type ConfidenceLevel = 'low' | 'medium' | 'high';

/** Source grading, A strongest. */
export type SourceCredibility = 'A' | 'B' | 'C' | 'D';

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
  | 'essays'
  | 'research_agenda';

/** The pipeline's states for a research question, carried across unrenamed (0013). */
export type ResearchStatus = 'open' | 'in_progress' | 'blocked' | 'resolved' | 'wont_fix';

export type SourceRow = {
  id: string;
  type: string;
  title: string;
  url: string | null;
  retrieved_date: string;
  publisher: string | null;
  credibility: SourceCredibility | null;
  pipeline_id: string | null;
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

  // 0006: provenance. These describe the strength of a claim that is already
  // cited; they are not a second citation mechanism.
  fact_status: FactStatus | null;
  confidence: ConfidenceLevel | null;
  as_of_date: string | null;

  // 0007: origin in the curation pipeline, null for hand-entered rows.
  pipeline_id: string | null;

  // 0008: the fields the research actually carries. The four capacity figures
  // measure different things and are never aggregated; see
  // docs/PIPELINE_MAPPING.md.
  proponent: string | null;
  suburb: string | null;
  state: string | null;
  market: string | null;
  address: string | null;
  it_capacity_mw: number | null;
  max_capacity_mw: number | null;
  first_phase_mw: number | null;
  campus_area_ha: number | null;
  gfa_sqm: number | null;
  capital_cost_aud: number | null;
  construction_jobs: number | null;
  operational_jobs: number | null;
  /** Text, not a date: sources say "H2 2026" and coercing that invents precision. */
  operational_from: string | null;
  target_completion: string | null;
  /** A status with an "unknown" value, not a boolean. */
  hcf_certified: string | null;

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
  fact_status: FactStatus | null;
  confidence: ConfidenceLevel | null;
  as_of_date: string | null;
  pipeline_id: string | null;
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

/** What an editorial piece is: an essay, the position page, or a policy proposal. */
export type PieceKind = 'essay' | 'position' | 'proposal';

export const PIECE_KINDS: readonly PieceKind[] = ['essay', 'position', 'proposal'] as const;

export type EssayRow = {
  id: string;
  title: string;
  publish_date: string | null;
  youtube_id: string | null;
  /** Markdown. Sources are cited inline as [SRC_ID]; see supabase/migrations/0016. */
  body: string | null;
  tags: string[];
  related_ids: string[];
  approved_by: string | null;
  approved_at: string | null;
  created_at: string;
  updated_at: string;
  kind: PieceKind;
  slug: string | null;
  standfirst: string | null;
  data_as_of_date: string | null;
  conflict: string | null;
  named_parties: string[];
  story_cards: string[];
  proposal_no: number | null;
  source_file: string | null;
  source_sha256: string | null;
  edited_in_admin_at: string | null;
  last_edited_by: string | null;
};

/** The allow-list of editors (0014). Never read through the API. */
export type EditorRow = {
  email: string;
  added_by: string;
  added_at: string;
};

/** One approval or retraction, as logged by the approval functions (0017). */
export type ApprovalRow = {
  id: string;
  record_type: 'essays';
  record_id: string;
  action: 'approve' | 'retract';
  actor_email: string;
  reason: string | null;
  body_sha256: string | null;
  at: string;
};

/** An earlier version of an essay's text (0015). */
export type EssayRevisionRow = {
  id: string;
  essay_id: string;
  title: string;
  standfirst: string | null;
  body: string | null;
  edited_by: string | null;
  edited_at: string;
  saved_at: string;
};

/**
 * An open research question. NOT a field-level gap: see DataGapRow for those.
 * A question may span many records or none.
 */
export type ResearchAgendaRow = {
  id: string;
  pipeline_id: string | null;
  pillar: string | null;
  question: string;
  why_it_matters: string | null;
  target_source: string | null;
  retrieval_method: string | null;
  priority: number | null;
  status: ResearchStatus;
  opened: string | null;
  resolved_date: string | null;
  notes: string | null;
  fact_status: FactStatus | null;
  confidence: ConfidenceLevel | null;
  as_of_date: string | null;
  created_at: string;
  updated_at: string;
};

/** Human-approved council name equivalences. The loader never writes here. */
export type LgaAliasRow = {
  alias: string;
  canonical: string;
  approved_by: string;
  approved_at: string;
  note: string | null;
};

/** One row per load of the curation pipeline into this database. */
export type IngestRunRow = {
  id: string;
  run_at: string;
  source_system: string;
  source_digest: string;
  loader_version: string;
  rows_by_table: Record<string, number>;
  notes: string | null;
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
      research_agenda: Table<ResearchAgendaRow>;
      lga_aliases: Table<LgaAliasRow>;
      ingest_runs: Table<IngestRunRow>;
    };
    Views: Record<string, never>;
    Functions: Record<string, never>;
    Enums: {
      site_status: SiteStatus;
      event_category: EventCategory;
      gap_reason: GapReason;
      link_state: LinkState;
      citable_record: CitableRecord;
      fact_status: FactStatus;
      confidence_level: ConfidenceLevel;
      source_credibility: SourceCredibility;
    };
    CompositeTypes: Record<string, never>;
  };
  editorial: {
    Tables: {
      case_studies: Table<CaseStudyRow>;
      essays: Table<EssayRow>;
      editors: Table<EditorRow>;
      approvals: Table<ApprovalRow>;
      essay_revisions: Table<EssayRevisionRow>;
    };
    Views: Record<string, never>;
    Functions: {
      is_editor: {
        Args: Record<string, never>;
        Returns: boolean;
      };
      approve_essay: {
        Args: {
          p_id: string;
          p_publish_date: string;
          p_expected_updated_at: string;
          p_legal_ack?: boolean;
        };
        Returns: EssayRow;
      };
      retract_essay: {
        Args: { p_id: string; p_reason: string };
        Returns: EssayRow;
      };
    };
    Enums: {
      piece_kind: PieceKind;
    };
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
  'rumoured',
  'pre_lodgement',
  'proposed',
  'lodged',
  'approved',
  'under_construction',
  'operating',
  'stalled',
  'refused',
  'withdrawn',
  'cancelled',
] as const;

export const EVENT_CATEGORIES: readonly EventCategory[] = [
  'planning',
  'construction',
  'media',
  'political',
  'community',
  'financial',
] as const;

/** Strongest first: the order a reader should meet them in. */
export const FACT_STATUSES: readonly FactStatus[] = [
  'verified',
  'reported',
  'claimed',
  'gap',
] as const;

/** Lifecycle order: what is being worked on first, what is closed last. */
export const RESEARCH_STATUSES: readonly ResearchStatus[] = [
  'in_progress',
  'open',
  'blocked',
  'resolved',
  'wont_fix',
] as const;

export const GAP_REASONS: readonly GapReason[] = [
  'unknown',
  'not_disclosed',
  'not_applicable',
  'withheld',
] as const;
