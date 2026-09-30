// components/primitives/FactOpinionDivider.tsx — visual and semantic boundary
// between the verified fact layer and the editorial layer (hard rule).

export default function FactOpinionDivider() {
  return (
    <div role="separator" aria-label="End of verified facts; opinion content below" className="my-8">
      <div className="flex items-center gap-3">
        <span className="h-px flex-1" style={{ background: "var(--editorial-accent)" }} />
        <span
          className="rounded-full border px-3 py-1 text-xs font-bold uppercase tracking-wide"
          style={{ borderColor: "var(--editorial-accent)", color: "var(--editorial-accent)" }}
        >
          Opinion &amp; analysis begins — clearly separated from data
        </span>
        <span className="h-px flex-1" style={{ background: "var(--editorial-accent)" }} />
      </div>
    </div>
  );
}
