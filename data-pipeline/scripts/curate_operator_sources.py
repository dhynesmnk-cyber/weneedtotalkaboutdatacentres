#!/usr/bin/env python3
"""
Site facts from operators' own pages (batch S4, first pass: NEXTDC and AirTrunk).

An operator's own page is the primary source for facts about its own asset: where the facility is,
how large its site is, and the IT capacity it is built for. scrapers/archive_pages.py archived the
pages read here under data/raw/operators/<group>/, each with a SHA-256 manifest and its visible text.

Every value is an entry in EXTRACTIONS, read by a person, with the passage it comes from. Before
writing, the script checks that the passage is in the page's text (whitespace aside), that a number
the value states is in the passage, and that an address's words appear in the passage in order (a
page may set an address over several lines, so its commas are not compared).

What is taken, and what is not:
  * it_capacity_mw only where the page labels the figure as IT capacity or IT load. A figure given
    as a lower bound ("10MW+", "185+MW") is not a value and is not taken.
  * address only for a site record that is one facility. A record covering several facilities
    (NEXTDC M1/M2/M3, P1/P2) has no single address.
  * campus_area_ha where the page states the site area ("Set on 8.8ha").
  * Nothing about operators or ownership is filled. Where a page says something about who is
    behind another record, it goes into a research question for a human (RG-098).

Uses load_pack.py's "fill": no existing value is overwritten, and a differing one is reported.

Outputs:
  * data/packs/operator_sources.json

Run:
    python3 scripts/curate_operator_sources.py
    python3 scripts/load_pack.py data/packs/operator_sources.json --allow-missing-source
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAGES = os.path.join(ROOT, "data", "raw", "operators")
OUT_PACK = os.path.join(ROOT, "data", "packs", "operator_sources.json")
TODAY = "2026-10-10"

FIELDS = {"it_capacity_mw", "address", "suburb", "campus_area_ha"}
PUBLISHER = {"nextdc": "NEXTDC Limited", "airtrunk": "AirTrunk"}

# (group, page, site, field, value, quote). Read by a person from the archived text.
EXTRACTIONS: list[tuple] = [
    # NEXTDC facility pages: IT capacity as labelled
    ("nextdc", "a1-adelaide", "SITE_NEXTDC_A1", "it_capacity_mw", 5, "5MW IT Capacity"),
    ("nextdc", "c1-canberra", "SITE_NEXTDC_C1", "it_capacity_mw", 4.4, "4.4MW IT Load"),
    ("nextdc", "m4-melbourne", "SITE_NEXTDC_M4", "it_capacity_mw", 150, "150MW IT Capacity"),
    ("nextdc", "s1-sydney", "SITE_NEXTDC_S1", "it_capacity_mw", 16, "16MW IT Capacity"),
    ("nextdc", "s2-sydney", "SITE_NEXTDC_S2", "it_capacity_mw", 30, "30MW IT Capacity"),
    ("nextdc", "s3-sydney", "SITE_NEXTDC_S3", "it_capacity_mw", 80, "80MW IT Capacity"),
    # NEXTDC contact page: the address of each single-facility site
    ("nextdc", "contact", "SITE_NEXTDC_S1", "address", "4 Eden Park Drive, Macquarie Park, NSW, 2113",
     "S1 Sydney 4 Eden Park Drive Macquarie Park, NSW, 2113"),
    ("nextdc", "contact", "SITE_NEXTDC_S2", "address", "6-8 Giffnock Avenue, Macquarie Park, NSW, 2113",
     "S2 Sydney 6-8 Giffnock Avenue Macquarie Park, NSW, 2113"),
    ("nextdc", "contact", "SITE_NEXTDC_S3", "address", "2 Broadcast Way, Artarmon NSW 2064",
     "S3 Sydney 2 Broadcast Way Artarmon NSW 2064"),
    ("nextdc", "contact", "SITE_NEXTDC_C1", "address", "19 Battye Street, Bruce, ACT, 2617",
     "C1 Canberra 19 Battye Street Bruce, ACT, 2617"),
    ("nextdc", "s1-sydney", "SITE_NEXTDC_S1", "suburb", "Macquarie Park", "Located in Macquarie Park,"),
    ("nextdc", "s2-sydney", "SITE_NEXTDC_S2", "suburb", "Macquarie Park", "Located in Macquarie Park,"),
    ("nextdc", "s3-sydney", "SITE_NEXTDC_S3", "suburb", "Artarmon", "Located in Artarmon,"),
    ("nextdc", "c1-canberra", "SITE_NEXTDC_C1", "suburb", "Bruce", "Located in Bruce,"),
    # AirTrunk facility pages: site area. Capacities are given only as lower bounds ("130+MW").
    ("airtrunk", "mel1-melbourne", "SITE_AIRTRUNK_MEL1", "campus_area_ha", 8.8, "Set on 8.8ha"),
    ("airtrunk", "syd1-sydney-west", "SITE_AIRTRUNK_SYD1", "campus_area_ha", 7.4, "Set on 7.4ha"),
    ("airtrunk", "syd2-sydney-north", "SITE_AIRTRUNK_SYD2", "campus_area_ha", 4.2, "Set on 4.2ha"),
    ("airtrunk", "syd3-sydney-west", "SITE_AIRTRUNK_SYD3", "campus_area_ha", 8.3, "Set on 8.3ha"),
    ("airtrunk", "syd2-sydney-north", "SITE_AIRTRUNK_SYD2", "address", "1 Sirius Road",
     "adjacent to AirTrunk’s existing facility at 1 Sirius Road"),
]

# What the AirTrunk SYD2 page says about two other records, put to a human rather than filled.
GAP = dict(
    id=98, pillar="A", priority=4, status="open", opened=TODAY,
    question=("Is AirTrunk SYD2 the same facility as the Lane Cove West Data Centre (SSD-9741, 1 Sirius "
              "Road), and is the Apollo Place Data Centre (SSD-67407231) AirTrunk's?"),
    why_it_matters=("If SYD2 and Lane Cove West are one facility, the record counts it twice; and Apollo "
                    "Place's applicant, EMKC Cubed Management Pty Ltd, is one of the entities RG-064 "
                    "asks to resolve."),
    target_source="AirTrunk's SYD2 page; the NSW Planning Portal records for SSD-9741 and SSD-67407231",
    retrieval_method="manual_review",
    notes=("OPENED 2026-10-10 from AirTrunk's own SYD2 page (archived at "
           "data/raw/operators/airtrunk/syd2-sydney-north.txt). It places SYD2 at 1 Sirius Road, which is "
           "the site of SSD-9741, whose applicant was Greenbox Architecture, and it says Greenbox "
           "Architecture 'delivered' SYD2 in collaboration with AirTrunk. Under 'Apollo Place Data "
           "Centre' it says the development 'has been located adjacent to AirTrunk's existing facility at "
           "1 Sirius Road', that the two 'will form an integrated data centre campus', and that 'The "
           "project is Phase 5 of AirTrunk's investment within the precinct'. Neither record is merged "
           "and no operator is filled: merging records and naming an operator are for a human."),
    fact_status="REPORTED", source_id="SRC_OP_AIRTRUNK_SYD2_SYDNEY_NORTH", confidence="medium",
    as_of_date=TODAY,
)


def normalise(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def words(text: str) -> list[str]:
    return re.findall(r"[A-Za-z0-9-]+", text)


def numbers(text: str) -> set[float]:
    return {float(n.replace(",", "")) for n in re.findall(r"\d[\d,]*(?:\.\d+)?", text)}


def main() -> int:
    errors: list[str] = []
    pages: dict[tuple[str, str], dict] = {}
    for group, page, *_ in EXTRACTIONS:
        if (group, page) in pages:
            continue
        base = os.path.join(PAGES, group, page)
        meta = json.load(open(base + ".html.meta.json"))
        if hashlib.sha256(open(base + ".html", "rb").read()).hexdigest() != meta["sha256"]:
            errors.append(f"{group}/{page}: fails its SHA-256 check")
        pages[(group, page)] = dict(text=normalise(open(base + ".txt", encoding="utf-8").read()), meta=meta)

    fills: dict[str, dict] = {}
    for group, page, site, field, value, quote in EXTRACTIONS:
        where = f"{group}/{page} {site} {field}"
        if field not in FIELDS:
            errors.append(f"{where}: not a field this batch fills")
            continue
        if normalise(quote) not in pages[(group, page)]["text"]:
            errors.append(f"{where}: quote not found: {quote!r}")
            continue
        if isinstance(value, (int, float)) and float(value) not in numbers(quote):
            errors.append(f"{where}: {value} is not a number the quote states")
            continue
        if field in ("address", "suburb") and " ".join(words(str(value))) not in " ".join(words(quote)):
            errors.append(f"{where}: {value!r} is not stated in the quote")
            continue
        entry = fills.setdefault(site, dict(fill={}, refs={}))
        if field in entry["fill"]:
            errors.append(f"{where}: given twice")
            continue
        entry["fill"][field] = value
        entry["refs"].setdefault((group, page), []).append(f"({field}): {normalise(quote)}")

    if errors:
        print("refusing to write; fix these first:", file=sys.stderr)
        for e in errors:
            print(f"  {e}", file=sys.stderr)
        return 1

    def source_id(group: str, page: str) -> str:
        return f"SRC_OP_{group}_{page}".upper().replace("-", "_")

    sources = []
    for (group, page), p in sorted(pages.items()):
        meta = p["meta"]
        sources.append(dict(
            id=source_id(group, page),
            title=f"{PUBLISHER[group]} - {page.replace('-', ' ')} (web page)",
            publisher=PUBLISHER[group],
            url=meta["url"],
            doc_type="primary_company",
            published=None,
            credibility="A",
            accessed=meta["fetched_utc"][:10],
            notes=(f"The operator's own page, read {meta['fetched_utc'][:10]}, SHA-256 {meta['sha256']}, "
                   f"archived at data/raw/operators/{group}/{page}.html with its visible text in .txt. "
                   f"Cited for the facts quoted in source_refs."),
        ))

    rows = []
    for site, entry in sorted(fills.items()):
        rows.append(dict(
            match=dict(id=site),
            fill=entry["fill"],
            add_sources=[dict(id=source_id(g, pg), quote=" | ".join(qs)) for (g, pg), qs in entry["refs"].items()],
        ))

    pack = {
        "pack_id": "operator-sources-2026-10",
        "prepared_by": "scripts/curate_operator_sources.py from data/raw/operators/",
        "prepared_on": TODAY,
        "_comment": [
            "Fills site facts from operators' own pages (batch S4, first pass: NEXTDC and AirTrunk).",
            "Every value was read by a person and is checked against its passage. Uses fill, so no",
            "existing value is overwritten. What the pages say about other records is put to a human",
            "as RG-098, not filled.",
        ],
        "sources": sources,
        "rows": {"sites": rows, "research_gaps": [GAP]},
    }
    with open(OUT_PACK, "w") as f:
        json.dump(pack, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print(f"{len(pages)} pages verified; {sum(len(e['fill']) for e in fills.values())} values for "
          f"{len(rows)} sites; wrote {os.path.relpath(OUT_PACK, ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
