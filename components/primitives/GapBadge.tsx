// components/primitives/GapBadge.tsx — explicit missing-data marker.
// Hard rule: a gap badge is better than a blank or a guess. Never colour-only:
// the badge carries text and an icon glyph so it reads without colour vision.

import type { GapFlag } from "@/lib/types";
import { gapLabel } from "@/lib/gap";

export default function GapBadge({ gap, label }: { gap: GapFlag; label?: string }) {
  const full = gapLabel(gap);
  return (
    <span
      role="note"
      aria-label={`Data gap: ${full}`}
      title={full}
      className="inline-flex items-center gap-1 rounded-full border px-2 py-0.5 text-xs font-medium"
      style={{ borderColor: "var(--line)", color: "var(--ink-700)", background: "#f1efe9" }}
    >
      <span aria-hidden="true">◌</span>
      {label ?? "No verified figure"}
    </span>
  );
}
