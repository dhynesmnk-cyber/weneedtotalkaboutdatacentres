// components/primitives/StatCard.tsx — value + as-of + gap footnote. The home
// briefing block (A1) and rollups (E1) compose these; they never render raw
// numbers without provenance context.

import type { Field } from "@/lib/types";
import FieldValue from "./FieldValue";
import GapBadge from "./GapBadge";

export default function StatCard({
  label,
  field,
  unit,
  asOf,
  href,
}: {
  label: string;
  field: Field<number | string>;
  unit?: string;
  asOf?: string;
  href?: string;
}) {
  const body = (
    <div className="rounded-lg border p-4" style={{ borderColor: "var(--line)", background: "var(--card)" }}>
      <p className="text-xs font-semibold uppercase tracking-wide" style={{ color: "var(--ink-500)" }}>
        {label}
      </p>
      <p className="mt-1 text-2xl font-bold" style={{ color: "var(--ink-900)" }}>
        <FieldValue
          field={field}
          render={(v) => (typeof v === "number" ? new Intl.NumberFormat("en-AU").format(v) : String(v))}
        />
        {field.kind === "value" && unit ? <span className="ml-1 text-base font-medium">{unit}</span> : null}
      </p>
      {field.kind === "gap" ? <div className="mt-1"><GapBadge gap={field.gap} /></div> : null}
      {asOf ? (
        <p className="mt-1 text-xs" style={{ color: "var(--ink-500)" }}>
          as of <time dateTime={asOf}>{asOf}</time>
        </p>
      ) : null}
      {href ? <p className="mt-1 text-xs underline">See underlying records →</p> : null}
    </div>
  );
  return href ? <a href={href}>{body}</a> : body;
}
