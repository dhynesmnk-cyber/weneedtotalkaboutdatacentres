// components/primitives/SourcePanel.tsx — citations for the current record.
// Hard rule: every factual claim references a source record; the panel makes
// that one tap away on any page.

import type { SourceRecord } from "@/lib/types";

export default function SourcePanel({ sources }: { sources: readonly SourceRecord[] }) {
  if (sources.length === 0) {
    return (
      <aside className="layer-fact rounded-md border p-3 text-sm" style={{ borderColor: "var(--line)", color: "var(--ink-700)" }}>
        No source records attached to this view yet. Where sources are missing we
        show gap flags rather than guesses.
      </aside>
    );
  }
  return (
    <aside aria-label="Sources" className="layer-fact rounded-md border p-4" style={{ borderColor: "var(--line)", background: "var(--card)" }}>
      <h2 className="text-sm font-bold uppercase tracking-wide" style={{ color: "var(--fact-accent)" }}>
        Sources ({sources.length})
      </h2>
      <ol className="mt-2 space-y-2 text-sm">
        {sources.map((s, i) => (
          <li key={s.id}>
            <span aria-hidden="true">[{i + 1}]</span>{" "}
            <a href={s.url} className="underline decoration-dotted underline-offset-2 hover:no-underline" style={{ color: "var(--ink-900)" }}>
              {s.title}
            </a>
            <span className="block text-xs" style={{ color: "var(--ink-500)" }}>
              {s.publisher} · retrieved {s.retrievedDate} · type: {s.type}
            </span>
          </li>
        ))}
      </ol>
    </aside>
  );
}
