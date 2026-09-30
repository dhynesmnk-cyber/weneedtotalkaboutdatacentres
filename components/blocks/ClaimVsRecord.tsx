// components/blocks/ClaimVsRecord.tsx — the core narrative device (D3): a
// common perception stated plainly, then the dated record(s) that support or
// contradict it. Claim card uses editorial styling; record card is fact layer.

import Link from "next/link";
import type { ClaimVsRecordPair } from "@/lib/types";
import { formatDateAu } from "@/lib/dates";

const RECORD_HREF: Record<ClaimVsRecordPair["recordTable"], string> = {
  sites: "/sites",
  entities: "/entities",
  events: "/timeline",
  case_studies: "/case-studies",
  essays: "/essays",
};

export default function ClaimVsRecord({ pairs }: { pairs: readonly ClaimVsRecordPair[] }) {
  return (
    <section aria-labelledby="cvr-heading" className="space-y-4">
      <h2 id="cvr-heading" className="text-xl font-bold">
        What people say vs what the records show
      </h2>
      <div className="grid gap-4 md:grid-cols-2">
        {pairs.map((p, i) => (
          <div key={i} className="rounded-lg border p-4" style={{ borderColor: "var(--line)", background: "var(--card)" }}>
            <p className="text-xs font-bold uppercase tracking-wide" style={{ color: "var(--editorial-accent)" }}>
              The claim
            </p>
            <blockquote className="mt-1 text-base italic" style={{ color: "var(--ink-900)" }}>
              {p.claim}
            </blockquote>
            <div className="mt-3 border-t pt-3" style={{ borderColor: "var(--line)" }}>
              <p className="text-xs font-bold uppercase tracking-wide" style={{ color: "var(--fact-accent)" }}>
                The record ({formatDateAu(p.recordDate)})
              </p>
              <p className="mt-1 text-sm" style={{ color: "var(--ink-700)" }}>
                {p.recordSummary}
              </p>
              <Link href={`${RECORD_HREF[p.recordTable]}/${p.recordId}`} className="mt-2 inline-block text-sm font-medium underline">
                Open underlying record →
              </Link>
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}
