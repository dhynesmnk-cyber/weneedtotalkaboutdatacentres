// lib/search.ts
// Suburb / postcode search (Epic B1). v1 uses a curated locality table (M1) —
// no geocoding vendor dependency. Matching is deliberately conservative: we
// return what the data supports and surface honest "no coverage" messaging
// rather than guessing.

import type { Locality } from "./types";

export interface SearchResult {
  readonly localities: Locality[];
  /** True when the query looks valid but our locality list has no match —
   * the UI must explain coverage, not show a bare empty box. */
  readonly outOfCoverage: boolean;
}

const normalise = (s: string): string =>
  s
    .toLowerCase()
    .replace(/\s+/g, " ")
    .trim();

const isPostcode = (s: string): boolean => /^\d{4}$/.test(s.trim());

/**
 * Search localities by exact postcode or name prefix (multi-word aware).
 * Results ranked: exact > prefix > substring; postcode matches first.
 */
export function searchLocalities(
  localities: readonly Locality[],
  query: string,
  limit = 10,
): SearchResult {
  const q = normalise(query);
  if (!q) return { localities: [], outOfCoverage: false };

  const scored: { l: Locality; score: number }[] = [];
  for (const loc of localities) {
    const name = normalise(loc.name);
    if (isPostcode(q)) {
      if (loc.postcode === q.trim()) scored.push({ l: loc, score: 100 });
      else if (loc.postcode.startsWith(q.trim())) scored.push({ l: loc, score: 60 });
      continue;
    }
    if (name === q) scored.push({ l: loc, score: 95 });
    else if (name.startsWith(`${q} `) || name.startsWith(q)) scored.push({ l: loc, score: 70 });
    else if (name.includes(q)) scored.push({ l: loc, score: 40 });
    else if (normalise(loc.lgaName).includes(q)) scored.push({ l: loc, score: 30 });
  }

  scored.sort((a, b) => b.score - a.score || a.l.name.localeCompare(b.l.name));
  const hits = scored.slice(0, limit).map((s) => s.l);
  return { localities: hits, outOfCoverage: hits.length === 0 };
}

/** Group results by LGA so the area view (B2) can render one card per LGA. */
export function groupByLga(localities: readonly Locality[]): Map<string, Locality[]> {
  const map = new Map<string, Locality[]>();
  for (const loc of localities) {
    const arr = map.get(loc.lgaCode) ?? [];
    arr.push(loc);
    map.set(loc.lgaCode, arr);
  }
  return map;
}
