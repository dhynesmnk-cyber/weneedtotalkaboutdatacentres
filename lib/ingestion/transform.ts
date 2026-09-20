/**
 * Pipeline rows in, database rows out. Pure: no I/O, no clock, no randomness.
 *
 * Everything that could put a number in front of a reader that nobody
 * published is decided here, which is why this file is pure and heavily
 * tested. The loader that calls it only moves bytes.
 */

import type { DataGapRow, EntityRow, SiteRow, SourceRow } from '@/lib/types';
import { pipelineUuid } from '@/lib/ingestion/identity';
import {
  mapConfidence,
  mapCredibility,
  mapFactStatus,
  mapSiteStatus,
} from '@/lib/ingestion/vocabulary';

/** A row as the pipeline's SQLite database presents it. */
export type PipelineRow = Record<string, string | number | null>;

export interface TransformedSite {
  site: Omit<SiteRow, 'created_at' | 'updated_at'>;
  gaps: Omit<DataGapRow, 'id' | 'created_at' | 'noted_date'>[];
  citations: DerivedCitation[];
  /** Entity relationships, always proposed. A human confirms them. */
  links: DerivedLink[];
}

export type DerivedCitation = {
  record_type: 'sites' | 'entities';
  record_id: string;
  source_id: string;
  claim: string | null;
};

export type DerivedLink = {
  site_id: string;
  entity_id: string;
  state: 'proposed';
};

/** Rejection carries the row that failed and why, never a silent drop. */
export class RowRejected extends Error {
  constructor(
    readonly table: string,
    readonly pipelineId: string,
    reason: string,
  ) {
    super(`${table} ${pipelineId || '(no id)'} rejected: ${reason}`);
    this.name = 'RowRejected';
  }
}

function text(value: string | number | null | undefined): string | null {
  if (value === null || value === undefined) return null;
  const s = String(value).trim();
  return s === '' ? null : s;
}

function num(value: string | number | null | undefined): number | null {
  if (value === null || value === undefined || value === '') return null;
  const n = typeof value === 'number' ? value : Number(value);
  if (!Number.isFinite(n)) return null;
  return n;
}

function int(value: string | number | null | undefined): number | null {
  const n = num(value);
  return n === null ? null : Math.trunc(n);
}

/**
 * The site fields that are factual claims about the world.
 *
 * A null in one of these earns a data_gaps row. Bookkeeping columns (id, name,
 * the provenance columns, the timestamps) are not claims and are excluded: a
 * missing `pipeline_id` is not a finding about a data centre.
 */
export const SITE_FACTUAL_FIELDS = [
  'operator',
  'lat',
  'lng',
  'lga',
  'status',
  'total_capacity_mw',
  'live_capacity_mw',
  'cooling_type',
  'rack_density_kw',
  'grid_connection',
  'water_usage',
  'proponent',
  'suburb',
  'state',
  'market',
  'address',
  'it_capacity_mw',
  'max_capacity_mw',
  'first_phase_mw',
  'campus_area_ha',
  'gfa_sqm',
  'capital_cost_aud',
  'construction_jobs',
  'operational_jobs',
  'operational_from',
  'target_completion',
  'hcf_certified',
] as const;

export function transformSource(row: PipelineRow): Omit<SourceRow, 'created_at' | 'updated_at'> {
  const pipelineId = text(row.id);
  if (!pipelineId) throw new RowRejected('sources', '', 'no id');

  const title = text(row.title);
  if (!title) throw new RowRejected('sources', pipelineId, 'no title');

  // retrieved_date is not null in the schema. A source whose retrieval date is
  // unknown cannot be cited honestly, so it is rejected rather than back-filled
  // with today's date, which would assert a retrieval that did not happen.
  const retrieved = text(row.accessed);
  if (!retrieved) throw new RowRejected('sources', pipelineId, 'no accessed date');

  return {
    id: pipelineUuid('sources', pipelineId),
    pipeline_id: pipelineId,
    // The pipeline's doc_type is the source type domain docs/SPEC.md left open.
    type: text(row.doc_type) ?? 'unknown',
    title,
    url: text(row.url),
    retrieved_date: retrieved,
    publisher: text(row.publisher),
    credibility: mapCredibility(text(row.credibility)),
  };
}

export function transformEntity(row: PipelineRow): {
  entity: Omit<EntityRow, 'created_at' | 'updated_at'>;
  citations: DerivedCitation[];
} {
  const pipelineId = text(row.id);
  if (!pipelineId) throw new RowRejected('entities', '', 'no id');

  const name = text(row.name);
  if (!name) throw new RowRejected('entities', pipelineId, 'no name');

  const id = pipelineUuid('entities', pipelineId);
  const sourceId = text(row.source_id);

  return {
    entity: {
      id,
      pipeline_id: pipelineId,
      name,
      type: text(row.entity_type),
      // The pipeline has no equivalent of `role`; leaving it null is honest.
      role: null,
      // Never set by an import. See NEVER_POPULATED in vocabulary.ts.
      major_flag: false,
      public_actions_summary: null,
      fact_status: mapFactStatus(text(row.fact_status)),
      confidence: mapConfidence(text(row.confidence)),
      as_of_date: text(row.as_of_date),
    },
    citations: sourceId
      ? [
          {
            record_type: 'entities',
            record_id: id,
            source_id: pipelineUuid('sources', sourceId),
            claim: null,
          },
        ]
      : [],
  };
}

/**
 * A site, plus the gaps, citations and proposed links it implies.
 *
 * Two rules do the real work here:
 *
 *   Every site must carry a source. A site with no source_id is rejected, not
 *   imported uncited, because an uncited record cannot be published and a
 *   record that cannot be published should not be in the fact layer.
 *
 *   Every null factual field earns a gap with reason `unknown`, and only
 *   `unknown`. SPEC.md defines it as "not yet researched, or researched without
 *   result", which is exactly and only what a pipeline null asserts. Reasons
 *   like not_disclosed are claims about the world and need a human and a
 *   source; deriving one here would invent evidence of an event that may never
 *   have happened.
 */
export interface KnownEntity {
  uuid: string;
  name: string;
}

export function transformSite(
  row: PipelineRow,
  entitiesByPipelineId: ReadonlyMap<string, KnownEntity> = new Map(),
): TransformedSite {
  const pipelineId = text(row.id);
  if (!pipelineId) throw new RowRejected('sites', '', 'no id');

  const name = text(row.name);
  if (!name) throw new RowRejected('sites', pipelineId, 'no name');

  const sourceId = text(row.source_id);
  if (!sourceId) {
    throw new RowRejected(
      'sites',
      pipelineId,
      'no source_id; an uncited site cannot be published',
    );
  }

  const id = pipelineUuid('sites', pipelineId);

  // Coordinates are supplied as a pair or not at all (sites_coords_paired).
  // Half a point is not a point, and the map must never receive one.
  const lat = num(row.lat);
  const lng = num(row.lon); // the lon -> lng rename
  const paired = lat !== null && lng !== null;

  const operatorPipelineId = text(row.operator_id);
  const operator = operatorPipelineId
    ? entitiesByPipelineId.get(operatorPipelineId)
    : undefined;

  const site: Omit<SiteRow, 'created_at' | 'updated_at'> = {
    id,
    pipeline_id: pipelineId,
    name,
    // The operator's name is a sourced fact about the site, so it is carried
    // across and rendered. The *link* to the entity record is a derivation,
    // and that waits for a human to confirm it.
    operator: operator?.name ?? null,
    lat: paired ? lat : null,
    lng: paired ? lng : null,
    lga: text(row.lga),
    status: mapSiteStatus(text(row.status)),

    total_capacity_mw: num(row.total_capacity_mw),
    // Never populated. See NEVER_POPULATED in vocabulary.ts.
    live_capacity_mw: null,
    it_capacity_mw: num(row.it_capacity_mw),
    max_capacity_mw: num(row.max_capacity_mw),
    first_phase_mw: num(row.first_phase_mw),

    cooling_type: null,
    rack_density_kw: null,
    grid_connection: null,
    water_usage: null,
    notes: text(row.notes),

    proponent: text(row.proponent),
    suburb: text(row.suburb),
    state: text(row.state),
    market: text(row.market),
    address: text(row.address),
    campus_area_ha: num(row.campus_area_ha),
    gfa_sqm: num(row.gfa_sqm),
    capital_cost_aud: num(row.capital_cost_aud),
    construction_jobs: int(row.construction_jobs),
    operational_jobs: int(row.operational_jobs),
    operational_from: text(row.operational_from),
    target_completion: text(row.target_completion),
    hcf_certified: text(row.hcf_certified),

    fact_status: mapFactStatus(text(row.fact_status)),
    confidence: mapConfidence(text(row.confidence)),
    as_of_date: text(row.as_of_date),
  };

  const gaps = deriveDataGaps('sites', id, site);

  const citations: DerivedCitation[] = [
    {
      record_type: 'sites',
      record_id: id,
      source_id: pipelineUuid('sources', sourceId),
      claim: null,
    },
  ];

  const links: DerivedLink[] = [];
  if (operator) {
    links.push({ site_id: id, entity_id: operator.uuid, state: 'proposed' });
  }

  return { site, gaps, citations, links };
}

/**
 * One gap per null factual field, reason `unknown`.
 *
 * Emitting nothing instead would be worse than it looks: every site page would
 * paint its blanks with UnexplainedBadge, labelling an ordinary unresearched
 * field as a data-quality defect. This derivation adds no information — it
 * states in the schema's vocabulary exactly what a null already asserted.
 */
export function deriveDataGaps(
  recordType: 'sites',
  recordId: string,
  site: Partial<Record<(typeof SITE_FACTUAL_FIELDS)[number], unknown>>,
): Omit<DataGapRow, 'id' | 'created_at' | 'noted_date'>[] {
  return SITE_FACTUAL_FIELDS.filter((field) => {
    const value = site[field];
    return value === null || value === undefined;
  }).map((field) => ({
    record_type: recordType,
    record_id: recordId,
    field_name: field,
    reason: 'unknown' as const,
    source_id: null,
  }));
}

/**
 * Citations from the pipeline's source_refs table.
 *
 * Only refs pointing at tables that exist here are mapped. The rest are
 * returned as skipped so the loader can report them, because a reference
 * dropped silently is indistinguishable from one that was never there.
 */
export function transformSourceRefs(rows: PipelineRow[]): {
  citations: DerivedCitation[];
  skipped: Record<string, number>;
} {
  const citations: DerivedCitation[] = [];
  const skipped: Record<string, number> = {};

  for (const row of rows) {
    const table = text(row.entity_table);
    const rowId = text(row.entity_rowid);
    const sourceId = text(row.source_id);
    if (!table || !rowId || !sourceId) continue;

    if (table !== 'sites' && table !== 'entities') {
      skipped[table] = (skipped[table] ?? 0) + 1;
      continue;
    }

    citations.push({
      record_type: table,
      record_id: pipelineUuid(table, rowId),
      source_id: pipelineUuid('sources', sourceId),
      // source_refs.quote is a verbatim extract, not a field-level assertion.
      // Mapping it onto `claim` would manufacture field-level citation
      // coverage that the research does not actually have.
      claim: null,
    });
  }

  return { citations, skipped };
}
