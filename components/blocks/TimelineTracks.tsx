// components/blocks/TimelineTracks.tsx — track selector + rolling window +
// significance filter (C1/C3). Keyboard-operable; the event list below the
// chart is the accessible fallback required by UI.md.

"use client";

import { useMemo, useState } from "react";
import Link from "next/link";
import type { EventCategory, ObservatoryEvent } from "@/lib/types";
import { withinMonths, formatDateAu } from "@/lib/dates";

const CATEGORIES: readonly { key: EventCategory; label: string; cssVar: string }[] = [
  { key: "planning", label: "Planning", cssVar: "--track-planning" },
  { key: "construction", label: "Construction", cssVar: "--track-construction" },
  { key: "media", label: "Media", cssVar: "--track-media" },
  { key: "political", label: "Political", cssVar: "--track-political" },
  { key: "community", label: "Community", cssVar: "--track-community" },
  { key: "financial", label: "Financial", cssVar: "--track-financial" },
];

export default function TimelineTracks({ events }: { events: readonly ObservatoryEvent[] }) {
  const [active, setActive] = useState<Set<EventCategory>>(
    new Set(["planning", "construction", "financial"]),
  );
  const [months, setMonths] = useState(12);
  const [majorOnly, setMajorOnly] = useState(true);

  const toggle = (c: EventCategory) =>
    setActive((prev) => {
      const next = new Set(prev);
      if (next.has(c)) next.delete(c);
      else next.add(c);
      return next;
    });

  const filtered = useMemo(
    () =>
      events
        .filter((e) => active.has(e.category))
        .filter((e) => withinMonths(e.date, months))
        .filter((e) => !majorOnly || e.significance === "major")
        .sort((a, b) => b.date.localeCompare(a.date)),
    [events, active, months, majorOnly],
  );

  // Per-month density buckets for the sparkline strip (C2).
  const density = useMemo(() => {
    const buckets = new Map<string, number>();
    for (const e of filtered) {
      const k = e.date.slice(0, 7);
      buckets.set(k, (buckets.get(k) ?? 0) + 1);
    }
    const max = Math.max(1, ...buckets.values());
    return { buckets, max };
  }, [filtered]);

  return (
    <div className="space-y-4">
      <div role="group" aria-label="Event tracks" className="flex flex-wrap gap-2">
        {CATEGORIES.map((c) => {
          const on = active.has(c.key);
          return (
            <button
              key={c.key}
              type="button"
              aria-pressed={on}
              onClick={() => toggle(c.key)}
              className="inline-flex items-center gap-1.5 rounded-full border px-3 py-1 text-sm font-medium"
              style={{
                borderColor: `var(${c.cssVar})`,
                background: on ? `var(${c.cssVar})` : "transparent",
                color: on ? "#fff" : `var(${c.cssVar})`,
              }}
            >
              <span aria-hidden="true">{on ? "✓" : "○"}</span>
              {c.label}
            </button>
          );
        })}
      </div>

      <div className="flex flex-wrap items-center gap-4 text-sm">
        <label htmlFor="range" className="font-medium">
          Window:
          <select
            id="range"
            value={months}
            onChange={(e) => setMonths(Number(e.target.value))}
            className="ml-2 rounded border px-2 py-1"
            style={{ borderColor: "var(--line)" }}
          >
            <option value={6}>Last 6 months</option>
            <option value={12}>Last 12 months</option>
            <option value={24}>Last 24 months</option>
            <option value={1200}>All time</option>
          </select>
        </label>
        <label className="font-medium">
          <input
            type="checkbox"
            checked={majorOnly}
            onChange={(e) => setMajorOnly(e.target.checked)}
            className="mr-1.5"
          />
          Major events only
        </label>
        <span style={{ color: "var(--ink-500)" }}>{filtered.length} events shown</span>
      </div>

      {/* Density sparkline strip */}
      <div aria-hidden="true" className="flex h-10 items-end gap-px">
        {[...density.buckets.entries()].map(([m, n]) => (
          <div
            key={m}
            title={`${m}: ${n} events`}
            className="w-3 rounded-t"
            style={{ height: `${(n / density.max) * 100}%`, background: "var(--fact-accent)" }}
          />
        ))}
      </div>

      {/* Accessible list fallback (required alternative to the visual timeline) */}
      <ol className="divide-y" style={{ borderColor: "var(--line)" }}>
        {filtered.map((e) => {
          const cat = CATEGORIES.find((c) => c.key === e.category)!;
          return (
            <li key={e.id} className="py-3 flex gap-3 items-baseline">
              <time dateTime={e.date} className="shrink-0 text-xs tabular-nums" style={{ color: "var(--ink-500)" }}>
                {formatDateAu(e.date)}
              </time>
              <span
                className="shrink-0 rounded px-1.5 py-0.5 text-[10px] font-bold uppercase text-white"
                style={{ background: `var(${cat.cssVar})` }}
              >
                {cat.label}
              </span>
              <span className="text-sm">
                <Link href={`/timeline/${e.slug}`} className="font-semibold underline decoration-dotted">
                  {e.title}
                </Link>{" "}
                <span style={{ color: "var(--ink-700)" }}>— {e.summary}</span>
              </span>
            </li>
          );
        })}
        {filtered.length === 0 ? (
          <li className="py-6 text-sm" style={{ color: "var(--ink-700)" }}>
            No events match these filters in this window. Widen the range or turn off
            “major events only” — sparse months are a fact about the news cycle, not a bug.
          </li>
        ) : null}
      </ol>
    </div>
  );
}
