// components/blocks/AreaSearch.tsx — "Check your area" (Epic B1). Client
// component over the locality dataset; conservative matching, honest
// out-of-coverage messaging, keyboard accessible combobox pattern.

"use client";

import { useMemo, useState } from "react";
import Link from "next/link";
import type { Locality } from "@/lib/types";
import { searchLocalities, groupByLga } from "@/lib/search";

export default function AreaSearch({ localities }: { localities: readonly Locality[] }) {
  const [query, setQuery] = useState("");
  const result = useMemo(() => searchLocalities(localities, query), [localities, query]);
  const groups = useMemo(() => [...groupByLga(result.localities).values()], [result]);

  return (
    <div className="rounded-lg border p-4" style={{ borderColor: "var(--line)", background: "var(--card)" }}>
      <label htmlFor="area-search" className="block text-sm font-semibold">
        Check your area — enter your suburb or postcode
      </label>
      <input
        id="area-search"
        type="search"
        role="combobox"
        aria-expanded={result.localities.length > 0}
        aria-controls="area-results"
        autoComplete="off"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder="e.g. 2150 or Illustra West"
        className="mt-2 w-full rounded-md border px-3 py-2 text-sm"
        style={{ borderColor: "var(--line)" }}
      />
      <div id="area-results" aria-live="polite" className="mt-3 space-y-3">
        {query && result.outOfCoverage ? (
          <p className="text-sm" style={{ color: "var(--ink-700)" }}>
            We have no locality records for “{query}” yet. Our v1 list covers approved
            council areas plus a national postcode mapping — if a site were proposed
            near you, it would appear on the timeline first. You can browse the{" "}
            <Link href="/timeline" className="underline">full timeline</Link>.
          </p>
        ) : null}
        {groups.map((lgas) => {
          const lga = lgas[0];
          return (
            <div key={lga.lgaCode}>
              <Link
                href={`/areas/${lga.lgaCode}`}
                className="text-sm font-bold underline decoration-dotted"
                style={{ color: "var(--fact-accent)" }}
              >
                {lga.lgaName} →
              </Link>
              <ul className="mt-1 flex flex-wrap gap-2 text-xs" style={{ color: "var(--ink-700)" }}>
                {lgas.map((l) => (
                  <li key={`${l.name}-${l.postcode}`} className="rounded border px-2 py-0.5" style={{ borderColor: "var(--line)" }}>
                    {l.name} {l.postcode}
                  </li>
                ))}
              </ul>
            </div>
          );
        })}
      </div>
    </div>
  );
}
