// lib/rollups.ts
// National/state capacity rollups (Epic E1). Aggregation logic lives here for
// display formatting; in production the totals come from the Postgres view
// v_rollup_capacity_by_status_state (migration M2) so the database stays the
// single source of truth. These functions are pure and unit-tested.

import type { Field, RollupRow, SiteStatus } from "./types";
import { gap, value } from "./gap";

export const STATUS_ORDER: readonly SiteStatus[] = [
  "proposed",
  "approved",
  "under_construction",
  "live",
  "stalled",
  "cancelled",
];

export const STATUS_LABELS: Record<SiteStatus, string> = {
  proposed: "Proposed",
  approved: "Approved",
  under_construction: "Under construction",
  live: "Live",
  stalled: "Stalled",
  cancelled: "Cancelled",
};

/**
 * Sum MW across a status group. If ANY member is unknown, the total is a gap —
 * we never silently drop unknowns to make a total look complete.
 */
export function sumCapacity(members: readonly Field<number>[]): Field<number> {
  let total = 0;
  for (const m of members) {
    if (m.kind === "gap") {
      return gap("pending_verification", "one or more site capacities are unverified");
    }
    if (!Number.isFinite(m.value) || m.value < 0) {
      // Validation rule (QUALITY.md): capacity must be numeric and positive.
      return gap("conflicting_sources", "invalid capacity value encountered");
    }
    total += m.value;
  }
  return value(total);
}

/** Group sites into rollup rows by state and status. */
export function buildRollups(
  sites: readonly {
    state: string;
    status: Field<SiteStatus>;
    totalCapacityMW: Field<number>;
  }[],
): RollupRow[] {
  const rows: RollupRow[] = [];
  const states = [...new Set(sites.map((s) => s.state))].sort();
  for (const state of states) {
    for (const status of STATUS_ORDER) {
      const members = sites.filter(
        (s) => s.state === state && s.status.kind === "value" && s.status.value === status,
      );
      if (members.length === 0) continue;
      rows.push({
        state,
        status,
        siteCount: members.length,
        totalCapacityMW: sumCapacity(members.map((m) => m.totalCapacityMW)),
      });
    }
  }
  return rows;
}

/** Reconciliation helper used in CI (Epic E acceptance): the view totals must
 * equal row-level sums computed independently. Returns list of mismatches. */
export function reconcile(
  viewRows: readonly RollupRow[],
  computedRows: readonly RollupRow[],
): string[] {
  const problems: string[] = [];
  const key = (r: RollupRow) => `${r.state}/${r.status}`;
  const viewMap = new Map(viewRows.map((r) => [key(r), r]));
  const compMap = new Map(computedRows.map((r) => [key(r), r]));
  for (const k of new Set([...viewMap.keys(), ...compMap.keys()])) {
    const a = viewMap.get(k);
    const b = compMap.get(k);
    if (!a || !b) {
      problems.push(`${k}: present in only one side`);
      continue;
    }
    if (a.siteCount !== b.siteCount) problems.push(`${k}: count ${a.siteCount} != ${b.siteCount}`);
    if (a.totalCapacityMW.kind === "value" && b.totalCapacityMW.kind === "value") {
      if (a.totalCapacityMW.value !== b.totalCapacityMW.value)
        problems.push(`${k}: MW mismatch`);
    } else if (a.totalCapacityMW.kind !== b.totalCapacityMW.kind) {
      problems.push(`${k}: gap flag disagreement`);
    }
  }
  return problems;
}
