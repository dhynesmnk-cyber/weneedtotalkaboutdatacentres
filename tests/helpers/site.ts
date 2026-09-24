import type { DataGapRow, GapReason, SiteRow } from '@/lib/types';

/**
 * A site with every nullable field empty, for tests to fill in only what they
 * are about. The name is illustrative; no test asserts anything about a real
 * site.
 */
export function site(id: string, fields: Partial<SiteRow> = {}): SiteRow {
  return {
    id,
    name: `Site ${id}`,
    operator: null,
    lat: null,
    lng: null,
    lga: null,
    status: null,
    total_capacity_mw: null,
    live_capacity_mw: null,
    cooling_type: null,
    rack_density_kw: null,
    grid_connection: null,
    water_usage: null,
    notes: null,
    fact_status: null,
    confidence: null,
    as_of_date: null,
    pipeline_id: null,
    proponent: null,
    suburb: null,
    state: null,
    market: null,
    address: null,
    it_capacity_mw: null,
    max_capacity_mw: null,
    first_phase_mw: null,
    campus_area_ha: null,
    gfa_sqm: null,
    capital_cost_aud: null,
    construction_jobs: null,
    operational_jobs: null,
    operational_from: null,
    target_completion: null,
    hcf_certified: null,
    created_at: '2026-09-01T00:00:00Z',
    updated_at: '2026-09-01T00:00:00Z',
    ...fields,
  };
}

export function gap(recordId: string, field: string, reason: GapReason = 'unknown'): DataGapRow {
  return {
    id: `${recordId}-${field}`,
    record_type: 'sites',
    record_id: recordId,
    field_name: field,
    reason,
    noted_date: '2026-09-01',
    source_id: null,
    created_at: '2026-09-01T00:00:00Z',
  };
}
