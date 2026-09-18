#!/usr/bin/env python3
"""
Audit the text-extraction yield of every archived PDF.

This exists because a silent extraction failure is the most dangerous class of bug in an evidence
database: it produces confident negative findings from documents that were never actually read. On
18 September 2026 the extractor recovered 9,901 characters from the 1.36 MB NSW Data Centre
Guidelines - 8.2 chars/KB against 46-82 chars/KB for the planning consents - and a keyword search
for "modification" returned zero. The zero was an artefact of the extractor, not a property of the
document. RG-046 had to be re-established from a full renderer.

Run after any harvesting step:
    python3 scripts/extraction_audit.py            # writes reports/extraction_audit.md
"""
from __future__ import annotations

import glob
import json
import os
import sys
import warnings

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
OUT = os.path.join(ROOT, "reports", "extraction_audit.md")

from pdf_text import extract, yield_stats, MIN_CHARS_PER_KB  # noqa: E402


def main() -> int:
    warnings.simplefilter("ignore")
    paths = sorted(glob.glob(os.path.join(ROOT, "data", "raw", "**", "*.pdf"), recursive=True))
    rows = []
    for p in paths:
        canon = ""
        # A pypdf re-extraction (scripts/reextract_consents.py) is the extraction of record where
        # one exists: the dependency-free extractor cannot decrypt AES-encrypted portal PDFs and
        # splits numerals across glyph boundaries. Audit the canonical text, note the fallback.
        meta_p = p + ".meta.json"
        txt_p = os.path.splitext(p)[0] + ".txt"
        if os.path.exists(meta_p) and os.path.exists(txt_p):
            try:
                meta = json.load(open(meta_p))
                if str(meta.get("extractor", "")).startswith("pypdf"):
                    canon = "pypdf"
                    txt = open(txt_p, encoding="utf-8", errors="replace").read()
            except Exception:  # noqa: BLE001
                canon = ""
        if not canon:
            try:
                txt = extract(p, warn=False)
            except Exception as exc:  # noqa: BLE001
                txt = ""
                print(f"  extraction error {os.path.basename(p)}: {exc}", file=sys.stderr)
        rows.append((p, yield_stats(p, len(txt)), canon))
    rows.sort(key=lambda r: r[1]["chars_per_kb"])

    bad = [r for r in rows if not r[1]["reliable"]]
    lines = [
        "# Extraction yield audit", "",
        f"Generated from {len(rows)} archived PDFs. Reliability floor: **{MIN_CHARS_PER_KB} chars/KB**.",
        "",
        "Any document below the floor **cannot support a negative finding**. A keyword that does not appear",
        "in its extracted text may simply not have been extracted. Re-read such documents through a full PDF",
        "renderer before concluding that a term, condition or commitment is absent.",
        "",
        f"**{len(bad)} of {len(rows)} documents are below the floor.**", "",
        "| chars/KB | chars | status | extractor | document | likely cause |",
        "|---|---|---|---|---|---|",
    ]
    for p, st, canon in rows:
        name = os.path.relpath(p, ROOT)
        if st["chars"] == 0:
            cause = "image-only scan, or no extractable content stream"
        elif not st["reliable"]:
            cause = "structured PDF (xref/object streams, CID fonts) this extractor cannot walk"
        else:
            cause = ""
        lines.append(f"| {st['chars_per_kb']:.1f} | {st['chars']:,} | "
                     f"{'**LOW**' if not st['reliable'] else 'ok'} | {canon or 'pdf_text'} | "
                     f"`{name}` | {cause} |")
    lines += [
        "",
        "## Known artefacts",
        "",
        "- The five `hearing_schedule_*.pdf` files and `SSD-10330_political_donation.pdf` are image-only.",
        "  Witness lists were recovered from the transcript appearance formula instead",
        "  (`data/raw/nsw_inquiry/witnesses.json`); the political donation disclosure remains unread and is",
        "  relevant to the inquiry's terms of reference (h)(iv) on lobbying and donations.",
        "- `nsw_data_centre_guidelines_2026.pdf` yields 8.2 chars/KB. Read it through `fetch_page`, which",
        "  renders it completely. RG-046 was established that way, not from this extractor.",
        "- The Endeavour Energy submissions on SSD-73761707 yield 9.1 and 14.7 chars/KB, so they are",
        "  partially extracted. Nothing in the database rests on their contents - they are cited by title only.",
        "- `scripts/pdf_text.py` emits a `LowYieldWarning` at extraction time so this cannot recur silently.",
        "- 2026-09-18: the 20 signed NSW consent PDFs were re-extracted with **pypdf** "
        "(`scripts/reextract_consents.py`), sha256-verified against their fetch manifests; the pypdf text is "
        "the extraction of record and this audit measures it where present. Three failure modes of the "
        "dependency-free extractor were established that day: (1) it cannot decrypt AES-encrypted portal "
        "PDFs - Lane Cove West and Macquarie Park yielded 0 chars; (2) it splits numerals across glyph "
        "boundaries - Glendenning's 235 MW parsed as 23, NEXTDC S4's 294 MW as '2 94' and its 200-hour "
        "generator cap was lost; (3) two-column Schedule 1 layouts (Dicker) separate labels from values. "
        "All three are repaired in the pypdf path; superseded extractions are kept under "
        "`data/raw/nsw_planning/consents/superseded_pdftext/`.",
        "",
        "## Parser false positives already caught",
        "",
        "- `demand_response` matched 17 of 20 consents (2026-09-18 pypdf battery). Every match was the "
        "consent's *definition* of Load Curtailment and a condition **prohibiting** generator use for it. "
        "The correct finding is that no consent requires non-diesel demand response.",
        "- `nox_mass_cap` initially returned 0 because PDF extraction splits `NOx` as `NO x` and spaces out",
        "  punctuation. The hardened pattern returns 2, both verified by reading the condition text.",
        "- The `\\bcdc\\b` entity matcher in the CER analysis over-matched a second corporation, inflating a",
        "  baseline. Fixed by tightening to `\\bcdc group\\b|\\bcdc data\\b` and aggregating duplicate publisher",
        "  rows with an explicit `n_published_rows` audit column.",
        "- Emissions-signature screening for data centre SPVs returned KFC Australia and Saputo Dairy.",
        "  Recorded as RG-028 so the method is not repeated.",
        "",
        "A grep of an extracted document is a **lead**, never a finding. Every negative claim in this",
        "database was confirmed by reading the rendered source.",
    ]
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")
    print(f"wrote {OUT}: {len(rows)} documents, {len(bad)} below the {MIN_CHARS_PER_KB} chars/KB floor")
    for p, st, canon in rows[:8]:
        print(f"  {st['chars_per_kb']:>7.1f} c/KB  {'LOW ' if not st['reliable'] else 'ok  '} "
              f"{(canon or 'pdf_text')[:6]:6s} {os.path.basename(p)[:56]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
