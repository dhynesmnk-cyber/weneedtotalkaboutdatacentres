#!/usr/bin/env python3
"""
The author's second round of decisions on research batch 8 (2026-11-18), and download #34's rest.

The author's answers of 2026-11-18 ("merge and load, 1 yes 2 yes 3 yes"), on the proposals in #47:
  1. #47 is merged and loaded.
  2. The two duplicate source rows are removed from the hosted database (done in one checked
     transaction; the pipeline no longer registers them, so nothing here is needed for it).
  3. Two Northern Territory proposals become site rows, each cited to the NT Government's release of
     22 July 2026 (SRC_NTGOV_BEETALOO_20260722), with no capacity stored:
       SITE_BEETALOO_WEDDELL     Beetaloo Digital at Weddell, pre_lodgement
       SITE_ENERGY_NORTH_ARES    Energy North's Project Ares at Murranji station, pre_lodgement
And the rest of download #34: the author read Amazon Web Services Australia's own major political donor
disclosures on the NSW Electoral Commission's site and pasted the three periods into the session
(RG-069).

Outputs:
  * data/packs/batch8_decisions_2.json

Run:
    python3 scripts/curate_batch8_decisions_2.py
    python3 scripts/load_pack.py data/packs/batch8_decisions_2.json --allow-missing-source
"""
from __future__ import annotations

import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(ROOT, "data", "raw")
OUT_PACK = os.path.join(ROOT, "data", "packs", "batch8_decisions_2.json")
THIS_PACK = "data/packs/batch8_decisions_2.json"
TODAY = "2026-11-18"
DECIDED = f" DECIDED BY THE AUTHOR {TODAY} (research batch 8, second round):"
TAG = f" UPDATED {TODAY} (research batch 8, the author's downloads):"

SRC_NT = "SRC_NTGOV_BEETALOO_20260722"          # registered by curate_batch8_decisions.py
SRC_AWS = "SRC_NSWEC_AWS_DISCLOSURES"

TEXTS = {
    SRC_NT: "operators/ntgov/beetaloo-digital-weddell-22-july-2026.md",
    SRC_AWS: "registers/nsw_electoral_disclosures/aws_major_political_donor_disclosures_author_transcription.txt",
}

QUOTES = {
    SRC_NT: {
        "grant": ("The Finocchiaro CLP Government has granted Beetaloo Digital an exclusive commitment over 185 hectares of "
                  "land at Weddell, about 30km from Darwin."),
        "campuses": "possibly two hyper-scale AI data centre campuses at Weddell",
        "power": "to be powered by up to 2GW of on-site gas-fired power generation",
        "not_to_deal": ("the exclusive right to make plans for the 185ha site while the company progresses the project and "
                        "investigates its feasibility"),
        "ares": ("Energy North’s Project Ares, a one-gigawatt project proposed for Murranji station in the Barkly "
                 "region"),
    },
    SRC_AWS: {
        "p2526": "Reporting Period 2025/2026",
        "d2526": "Political donations made 10,900.00",
        "number": "Disclosure Number 130644 Disclosure Received Date 1/08/2025 Disclosure Type Annual Donation",
        "general": ("Reportable political donations made - General (not made at a fundraisingfunction or venture)Amount $: "
                    "13,250Percentage: 100.0%"),
        "d2425": "Political donations made 13,250.00",
        "p2324": "Reporting Period 2023/2024",
        "d2324": "Political donations made 15,200.00",
    },
}


def normalise(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def pack_list() -> list[str]:
    text = open(os.path.join(ROOT, "scripts", "rebuild_all.py"), encoding="utf-8").read()
    block = text[text.index("PACKS = ["): text.index("]\n", text.index("PACKS = ["))]
    return re.findall(r'"(data/packs/[^"]+\.json)"', block)


def prior_notes(gap_id: int) -> str:
    note = ""
    for rel in pack_list():
        if rel == THIS_PACK:
            break
        path = os.path.join(ROOT, rel)
        if not os.path.exists(path):
            continue
        for r in json.load(open(path, encoding="utf-8")).get("rows", {}).get("research_gaps", []):
            if r.get("id") == gap_id and r.get("notes"):
                note = r["notes"]
            elif r.get("match", {}).get("id") == gap_id and (r.get("set") or {}).get("notes"):
                note = r["set"]["notes"]
    return note


def main() -> int:
    errors: list[str] = []
    texts = {}
    for sid, rel in TEXTS.items():
        path = os.path.join(RAW, rel)
        if not os.path.exists(path):
            errors.append(f"{sid}: archive missing at {rel}")
            continue
        texts[sid] = normalise(open(path, encoding="utf-8", errors="replace").read())
    for sid, quotes in QUOTES.items():
        for label, quote in quotes.items():
            if sid in texts and normalise(quote) not in texts[sid]:
                errors.append(f"{sid}/{label}: quote not found verbatim in the archive")
    # The three-year total the note states, computed from the transcription.
    if SRC_AWS in texts:
        amounts = [float(a.replace(",", "")) for a in re.findall(r"Political donations made ([\d,]+\.\d\d)", texts[SRC_AWS])]
        if amounts != [10900.0, 13250.0, 15200.0]:
            errors.append(f"{SRC_AWS}: amounts {amounts}, the note says 10,900, 13,250 and 15,200")
    if errors:
        print("refusing to write the pack:", file=sys.stderr)
        for e in errors:
            print(f"  {e}", file=sys.stderr)
        return 1

    def q(*refs: tuple[str, str]) -> list[dict]:
        grouped: dict[str, list[str]] = {}
        for sid, label in refs:
            grouped.setdefault(sid, []).append(QUOTES[sid][label])
        return [dict(id=sid, quote=" | ".join(v)) for sid, v in grouped.items()]

    meta = json.load(open(os.path.join(RAW, TEXTS[SRC_AWS] + ".meta.json"), encoding="utf-8"))
    sources = [dict(
        id=SRC_AWS,
        title="Amazon Web Services Australia Pty Ltd: major political donor disclosures, 2023/24 to 2025/26 (NSW Electoral Commission)",
        publisher="NSW Electoral Commission", url=meta["url"], doc_type="primary_regulator", published=None,
        credibility="A", accessed=TODAY,
        notes=("The company's disclosures as major political donor, read on the Electoral Commission's disclosure site by "
               "the author and transcribed into the session (download #34; the crawler is barred by robots.txt). Political "
               "donations made: 2023/24 $15,200; 2024/25 $13,250 (disclosure 130644, an annual donation disclosure received "
               "1 August 2025, all 'General (not made at a fundraising function or venture)'); 2025/26 $10,900. The "
               "transcription gives totals, not recipients. Archived at data/raw/" + TEXTS[SRC_AWS] + " with a manifest "
               f"(SHA-256 {meta['sha256'][:16]}...). RG-069."))]

    sites = [
        dict(id="SITE_BEETALOO_WEDDELL", name="Beetaloo Digital at Weddell", proponent="Beetaloo Digital Pty Ltd",
             state="NT", market="NT", status="pre_lodgement", suburb="Weddell", campus_area_ha=185.0,
             notes=("Added on the author's decision of 2026-11-18 (RG-027), from the NT Government's release of 22 July "
                    "2026: an exclusive 'not to deal' commitment over 185 hectares of land at Weddell, about 30 km from "
                    "Darwin, while the company 'investigates its feasibility', for 'possibly two hyper-scale AI data centre "
                    "campuses', powered by up to 2 GW of on-site gas-fired generation. STATUS pre_lodgement is a recorded "
                    "reading: no planning application has been read. The 185 ha is the land committed, stored as the "
                    "campus area. NO CAPACITY IS STORED: 2 GW is generation, not IT load. The company's claims ($40 "
                    "billion, 5,000 construction jobs, 350 operational jobs) are quoted in the release, not stored. Not "
                    "mapped."),
             fact_status="REPORTED", source_id=SRC_NT, confidence="medium", as_of_date=TODAY),
        dict(match=dict(id="SITE_BEETALOO_WEDDELL"), set={},
             add_sources=q((SRC_NT, "grant"), (SRC_NT, "not_to_deal"), (SRC_NT, "campuses"), (SRC_NT, "power"))),
        dict(id="SITE_ENERGY_NORTH_ARES", name="Energy North Project Ares (Murranji station)", proponent="Energy North",
             state="NT", market="NT", status="pre_lodgement",
             notes=("Added on the author's decision of 2026-11-18 (RG-027), from the NT Government's release of 22 July "
                    "2026, which names 'Energy North's Project Ares, a one-gigawatt project proposed for Murranji station "
                    "in the Barkly region'. That sentence is the whole record: STATUS pre_lodgement is a recorded reading, "
                    "NO CAPACITY IS STORED (the one gigawatt is not labelled IT load), no address, area or proponent "
                    "entity is known, and the row is not mapped. Confidence is low until the proponent's own statement "
                    "or a planning record is read."),
             fact_status="REPORTED", source_id=SRC_NT, confidence="low", as_of_date=TODAY),
        dict(match=dict(id="SITE_ENERGY_NORTH_ARES"), set={}, add_sources=q((SRC_NT, "ares"))),
    ]

    gaps = [
        dict(match=dict(id=27), set=dict(as_of_date=TODAY, notes=(prior_notes(27) + DECIDED + " SITE_BEETALOO_WEDDELL and "
             "SITE_ENERGY_NORTH_ARES added (NT, pre_lodgement, unmapped, no capacity stored), each cited to the NT "
             "Government's release of 22 July 2026. The other proposals this question names are not yet worked.").strip()),
             add_sources=q((SRC_NT, "grant"), (SRC_NT, "ares"))),
        dict(match=dict(id=69), set=dict(as_of_date=TODAY, notes=(prior_notes(69) + TAG + " NSW AMOUNTS, from Amazon Web "
             "Services Australia's own major political donor disclosures, read by the author on the Electoral "
             "Commission's site (download #34, rest): political donations made of $15,200 in 2023/24, $13,250 in 2024/25 "
             "(disclosure 130644, received 1 August 2025, all 'General (not made at a fundraising function or venture)') "
             "and $10,900 in 2025/26: $39,350 over the three periods. The disclosures as read give totals, not "
             "recipients. These are NSW figures and are not added to the Commonwealth ones. No improper conduct is "
             "alleged or implied.").strip()),
             add_sources=q((SRC_AWS, "p2324"), (SRC_AWS, "d2324"), (SRC_AWS, "number"), (SRC_AWS, "general"),
                           (SRC_AWS, "d2425"), (SRC_AWS, "p2526"), (SRC_AWS, "d2526"))),
    ]

    pack = {
        "pack_id": "batch8-decisions-2-2026-11",
        "prepared_by": "scripts/curate_batch8_decisions_2.py, on the author's decisions of 2026-11-18",
        "prepared_on": TODAY,
        "_comment": [
            "The author's second round on batch 8: two NT site rows added, cited to the NT Government's release",
            "of 22 July 2026; the NSW amounts for Amazon Web Services Australia's donations (RG-069).",
            "The duplicate source rows were removed from the hosted database by a checked transaction, recorded",
            "in docs/SUPABASE_SETUP.md; the pipeline no longer registers them.",
        ],
        "sources": sources,
        "rows": {"sites": sites, "research_gaps": gaps},
    }
    with open(OUT_PACK, "w") as f:
        json.dump(pack, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print(f"batch 8 decisions 2: {len(sources)} source, 2 sites added, {len(gaps)} question updates; "
          f"wrote {os.path.relpath(OUT_PACK, ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
