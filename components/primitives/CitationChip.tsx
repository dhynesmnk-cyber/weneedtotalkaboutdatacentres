// components/primitives/CitationChip.tsx — "cite this record" snippet (E2).
// Click copies a stable, dated citation with the site's deep link.

"use client";

export default function CitationChip({
  slug,
  title,
  dataAsOf,
}: {
  slug: string;
  title: string;
  dataAsOf?: string;
}) {
  const cite = `"${title}", Australian AI Data Centre Observatory, record /sites/${slug}${
    dataAsOf ? `, data as of ${dataAsOf}` : ""
  } (accessed ${new Date().toLocaleDateString("en-AU")}).`;

  return (
    <button
      type="button"
      className="rounded-full border px-2.5 py-1 text-xs font-medium"
      style={{ borderColor: "var(--line)", color: "var(--ink-700)" }}
      onClick={async () => {
        await navigator.clipboard.writeText(cite);
        alert("Citation copied to clipboard.");
      }}
      title={cite}
    >
      ⧉ Cite this record
    </button>
  );
}
