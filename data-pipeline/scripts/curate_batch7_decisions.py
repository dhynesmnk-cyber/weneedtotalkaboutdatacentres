#!/usr/bin/env python3
"""
Research batch 7: the author's decisions of 2026-11-18 on what the batch found.

Batch 7 (scripts/curate_batch7.py) answered several questions whose answers implied a change to a
site row, and proposed each change in the question's note rather than making it. The author
decided them on 2026-11-18 ("1 yes 2 yes 3 yes 4 yes 5 yes 6 don't know"):

  1. RG-098 YES. AirTrunk's own SYD2 page makes SYD2 the facility the Lane Cove West consent
     (SSD-9741) approved. SITE_AIRTRUNK_SYD2, a seed row resting on a grade-C directory, is retired
     from data/seed_data.py; SITE_LANE_COVE_WEST, the consent row (VERIFIED, mapped, carrying its
     application and three modifications), becomes the SYD2 record: AirTrunk is its operator, its
     status is operational, and the HCF register's SYD2 certification now matches it
     (curate_hcf_register.py). Apollo Place's operator is AirTrunk, REPORTED on AirTrunk's page.
     The seed row's other claims (a 20-100 MW band, noise reports) rested on CertifiedStrategic.com
     and are not carried.
  2. RG-102 YES. SITE_MACQUARIE_PARK_DC reads operational, on the Department's March 2026 report.
  3. RG-024 YES. SITE_MSFT_KEMPS loses it_capacity_mw: its only primary source calls 190 MW an
     "operational capacity", not IT load. Area and floor area are cited to the report.
  4. RG-071 and RG-027 YES. Two rows are added from the operators' own pages, with no capacity
     stored: AirTrunk MEL2 (VIC; status pre_lodgement, the earliest stage the vocabulary has, as a
     recorded reading) and Firmus Wesley Vale (TAS; status lodged, on the development application
     its own page links). Neither is mapped.
  5. RG-001 and RG-082 closed as wont_fix by the author.
  6. RG-104 "don't know": stays open, with what would settle it.

Outputs:
  * data/packs/batch7_decisions.json

Run:
    python3 scripts/curate_batch7_decisions.py
    python3 scripts/load_pack.py data/packs/batch7_decisions.json --allow-missing-source
"""
from __future__ import annotations

import importlib.util
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(ROOT, "data", "raw")
OUT_PACK = os.path.join(ROOT, "data", "packs", "batch7_decisions.json")
THIS_PACK = "data/packs/batch7_decisions.json"
TODAY = "2026-11-18"
DECIDED = f" DECIDED BY THE AUTHOR {TODAY} (research batch 7):"

SRC_SYD2 = "SRC_OP_AIRTRUNK_SYD2_SYDNEY_NORTH"
SRC_KHARTOUM = "SRC_SSD63235720_ASSESSMENT"
SRC_KEMPS = "SRC_SSD10101987_ASSESSMENT"
SRC_MEL2 = "SRC_OP_AIRTRUNK_MEL2"
SRC_FIRMUS_WV = "SRC_OP_FIRMUS_WESLEY_VALE"

TEXTS = {
    SRC_SYD2: "operators/airtrunk/syd2-sydney-north.txt",
    SRC_KHARTOUM: "nsw_planning/documents/SSD-63235720_assessment.txt",
    SRC_KEMPS: "nsw_planning/documents/SSD-10101987_assessment.txt",
    SRC_MEL2: "operators/airtrunk/mel2-melbourne.txt",
    SRC_FIRMUS_WV: "operators/firmus/wesley-vale-ai-factory-project.txt",
}
QUOTES = {
    SRC_SYD2: {
        "greenbox": ("Through close collaboration with AirTrunk and specialist consultants, Greenbox "
                     "Architecture delivered a future‑ready data centre environment"),
        "existing": ("The Apollo Place data centre has been located adjacent to AirTrunk’s existing "
                     "facility at 1 Sirius Road."),
        "phase5": "The project is Phase 5 of AirTrunk’s investment within the precinct.",
        "campus": ("AirTrunk SYD2 is one of Australia’s largest hyperscale data centre campuses, "
                   "delivering high‑performance digital infrastructure at scale."),
        "area": "Set on 4.2ha",
    },
    SRC_KHARTOUM: {
        "existing": "an existing data centre adjoining to the west at 11 - 17 Khartoum Road (SSD - 10467)",
        "operational": ("including one operational data centre, one under - construction data centre, "
                        "and one data centre currently under assessment"),
    },
    SRC_KEMPS: {
        "capacity": ("two data storage buildings with an operational capacity of 190 Megawatts (MW)"),
        "area": "The site is approximately 14.43 hectares (ha) in area",
        "gfa": "The development has a gross floor area (GFA) of 60,943 m2",
    },
    SRC_MEL2: {
        "location": "Strategically located in Melbourne’s North-West",
        "capacity": "A hyperscale campus with multiple diverse buildings and a total capacity of 354+MW",
        "size": ("Set on 8.070 ha with 45,578sqm of gross floor area and up to 32 technical data halls "
                 "spanning 42,240m 2"),
    },
    SRC_FIRMUS_WV: {
        "site": "Firmus plans to build a new AI Factory project at 226 Mill Road, Wesley Vale",
        "stages": ("an initial stage of approximately 26 MW, growing to maximum approximately 52 MW of "
                   "capacity (23 MW critical IT load, growing to maximum of approximately 46 WM)."),
        "da": "Download Development Application",
        "generators": "The facility will have 40 backup generators",
    },
}


def normalise(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def pack_list() -> list[str]:
    text = open(os.path.join(ROOT, "scripts", "rebuild_all.py"), encoding="utf-8").read()
    block = text[text.index("PACKS = ["): text.index("]\n", text.index("PACKS = ["))]
    return re.findall(r'"(data/packs/[^"]+\.json)"', block)


def seed_sites() -> dict[str, dict]:
    spec = importlib.util.spec_from_file_location("seed_data", os.path.join(ROOT, "data", "seed_data.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)  # type: ignore[union-attr]
    return {s["id"]: s for s in mod.SITES}


def prior(table: str, key: str, value, column: str, seed: dict | None = None) -> str:
    """The value the last earlier pack wrote for one column, else the seed's, so it is extended."""
    out = (seed or {}).get(value, {}).get(column) or ""
    for rel in pack_list():
        if rel == THIS_PACK:
            break
        path = os.path.join(ROOT, rel)
        if not os.path.exists(path):
            continue
        for r in json.load(open(path, encoding="utf-8")).get("rows", {}).get(table, []):
            if r.get(key) == value and r.get(column):
                out = r[column]
            elif (r.get("match") or {}).get(key) == value and (r.get("set") or {}).get(column):
                out = r["set"][column]
    return out


def main() -> int:
    errors: list[str] = []
    texts = {sid: normalise(open(os.path.join(RAW, rel), encoding="utf-8").read()) for sid, rel in TEXTS.items()}
    for sid, quotes in QUOTES.items():
        for label, q in quotes.items():
            if normalise(q) not in texts[sid]:
                errors.append(f"{sid}/{label}: quote not found verbatim in the archive")
    seed = seed_sites()
    if "SITE_AIRTRUNK_SYD2" in seed:
        errors.append("SITE_AIRTRUNK_SYD2 is still in data/seed_data.py: retire it before this pack")
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

    def site_note(site_id: str, text: str) -> str:
        return (prior("sites", "id", site_id, "notes", seed) + DECIDED + " " + text).strip()

    def gap_note(gap_id: int, text: str) -> str:
        return (prior("research_gaps", "id", gap_id, "notes") + DECIDED + " " + text).strip()

    sites = [
        dict(match=dict(id="SITE_LANE_COVE_WEST"),
             set=dict(name="AirTrunk SYD2 (Lane Cove West Data Centre)", operator_id="ENT_AIRTRUNK",
                      status="operational",
                      notes=site_note("SITE_LANE_COVE_WEST", (
                          "RG-098: this consent's facility is AirTrunk SYD2. AirTrunk's own SYD2 page "
                          "credits Greenbox Architecture, this consent's applicant, with delivering it "
                          "'in collaboration with AirTrunk', dates it from 2019, places it at 1 Sirius "
                          "Road, and calls it 'one of Australia's largest hyperscale data centre "
                          "campuses'; it calls the 1 Sirius Road facility 'existing'. The separate seed "
                          "row SITE_AIRTRUNK_SYD2 is retired and its HCF certification (the register's "
                          "'AirTrunk Australia - SYD1, SYD2 and MEL1') now matches this row. Its other "
                          "claims rested on CertifiedStrategic.com and are not carried. Site area stays "
                          "the consent's 3.59 ha; AirTrunk's 'Set on 4.2ha' is quoted, not stored, as "
                          "the campus may include later phases. No capacity is stored: AirTrunk gives "
                          "only a lower bound ('120+MW').")),
                      as_of_date=TODAY),
             add_sources=q((SRC_SYD2, "greenbox"), (SRC_SYD2, "existing"), (SRC_SYD2, "campus"),
                           (SRC_SYD2, "area"))),
        dict(match=dict(id="SITE_APOLLO_PLACE"),
             set=dict(operator_id="ENT_AIRTRUNK",
                      notes=site_note("SITE_APOLLO_PLACE", (
                          "RG-098: operator AirTrunk, REPORTED on AirTrunk's own SYD2 page, which says "
                          "this development 'has been located adjacent to AirTrunk's existing facility at "
                          "1 Sirius Road' and 'is Phase 5 of AirTrunk's investment within the precinct'. "
                          "The consent's applicant (EMKC Cubed Management) is unchanged.")),
                      as_of_date=TODAY),
             add_sources=q((SRC_SYD2, "existing"), (SRC_SYD2, "phase5"))),
        dict(match=dict(id="SITE_MACQUARIE_PARK_DC"),
             set=dict(status="operational",
                      notes=site_note("SITE_MACQUARIE_PARK_DC", (
                          "RG-102: status operational (it read approved). The Department's March 2026 "
                          "report on the neighbouring SSD-63235720 describes 'an existing data centre "
                          "adjoining to the west at 11-17 Khartoum Road (SSD-10467)' and counts it among "
                          "'one operational data centre'. Its end user is still unnamed.")),
                      as_of_date=TODAY),
             add_sources=q((SRC_KHARTOUM, "existing"), (SRC_KHARTOUM, "operational"))),
        dict(match=dict(id="SITE_MSFT_KEMPS"),
             set=dict(it_capacity_mw=None,
                      notes=site_note("SITE_MSFT_KEMPS", (
                          "RG-024: it_capacity_mw is cleared. The only primary source, the Department's "
                          "assessment report, describes 'two data storage buildings with an operational "
                          "capacity of 190 Megawatts (MW)', which is not labelled IT load, so no capacity "
                          "column holds it (the RG-099 rule). The report confirms the site area (14.43 ha) "
                          "and floor area (60,943 m2) the row holds.")),
                      as_of_date=TODAY),
             add_sources=q((SRC_KEMPS, "capacity"), (SRC_KEMPS, "area"), (SRC_KEMPS, "gfa"))),
        dict(id="SITE_AIRTRUNK_MEL2", name="AirTrunk MEL2 (Melbourne North-West)", operator_id="ENT_AIRTRUNK",
             state="VIC", market="NEM", status="pre_lodgement", campus_area_ha=8.07, gfa_sqm=45578.0,
             hcf_certified="unknown",
             notes=("Added on the author's decision of 2026-11-18 (RG-071), from AirTrunk's own MEL2 page: "
                    "'Strategically located in Melbourne's North-West', 'Set on 8.070 ha with 45,578sqm of "
                    "gross floor area'. STATUS IS A RECORDED READING: the page gives no status and no planning "
                    "record has been read, so the row takes pre_lodgement, the earliest stage the vocabulary "
                    "has; a planning record will move it. NO CAPACITY IS STORED: 'a total capacity of 354+MW' "
                    "is a lower bound. No address or suburb is published (directories say Tullamarine: a "
                    "lead), so the row is not mapped."),
             fact_status="REPORTED", source_id=SRC_MEL2, confidence="low", as_of_date=TODAY),
        dict(match=dict(id="SITE_AIRTRUNK_MEL2"), set={},
             add_sources=q((SRC_MEL2, "location"), (SRC_MEL2, "size"), (SRC_MEL2, "capacity"))),
        dict(id="SITE_FIRMUS_WESLEY_VALE", name="Firmus Wesley Vale AI Factory", operator_id="ENT_FIRMUS",
             state="TAS", market="NEM", status="lodged", address="226 Mill Road, Wesley Vale",
             suburb="Wesley Vale", hcf_certified="unknown",
             notes=("Added on the author's decision of 2026-11-18 (RG-027), from Firmus's own project page: "
                    "'a new AI Factory project at 226 Mill Road, Wesley Vale', on part of the former pulp mill "
                    "landholding, with 40 backup generators. STATUS lodged rests on the development "
                    "application the page links; the council record has not been read. NO CAPACITY IS "
                    "STORED until it is: the page gives 'an initial stage of approximately 26 MW, growing to "
                    "maximum approximately 52 MW of capacity (23 MW critical IT load, growing to maximum of "
                    "approximately 46 WM)' (sic). Not mapped."),
             fact_status="REPORTED", source_id=SRC_FIRMUS_WV, confidence="medium", as_of_date=TODAY),
        dict(match=dict(id="SITE_FIRMUS_WESLEY_VALE"), set={},
             add_sources=q((SRC_FIRMUS_WV, "site"), (SRC_FIRMUS_WV, "da"), (SRC_FIRMUS_WV, "stages"),
                           (SRC_FIRMUS_WV, "generators"))),
    ]

    gaps = [
        dict(match=dict(id=98), set=dict(status="resolved", resolved_date=TODAY, as_of_date=TODAY,
             notes=gap_note(98, "Both proposals accepted: SITE_LANE_COVE_WEST is now the SYD2 record "
                                "(operator AirTrunk, operational; SITE_AIRTRUNK_SYD2 retired), and Apollo "
                                "Place's operator is AirTrunk, REPORTED."))),
        dict(match=dict(id=102), set=dict(status="in_progress", as_of_date=TODAY,
             notes=gap_note(102, "Status set to operational. The end user stays unnamed, so the "
                                 "question stays open for it."))),
        dict(match=dict(id=24), set=dict(status="resolved", resolved_date=TODAY, as_of_date=TODAY,
             notes=gap_note(24, "it_capacity_mw cleared on SITE_MSFT_KEMPS; area and floor area "
                                "confirmed from the assessment report. No primary source read states an "
                                "IT load for the campus."))),
        dict(match=dict(id=71), set=dict(status="resolved", resolved_date=TODAY, as_of_date=TODAY,
             notes=gap_note(71, "SITE_AIRTRUNK_MEL2 added (VIC, pre_lodgement as a recorded reading, "
                                "unmapped, no capacity stored)."))),
        dict(match=dict(id=27), set=dict(status="in_progress", as_of_date=TODAY,
             notes=gap_note(27, "SITE_FIRMUS_WESLEY_VALE added (TAS, lodged, unmapped, no capacity "
                                "stored). The other proposals this question names are not yet worked."))),
        dict(match=dict(id=1), set=dict(status="wont_fix", resolved_date=TODAY, as_of_date=TODAY,
             notes=gap_note(1, "Closed as wont_fix: distance analysis is left for after v1, which has no "
                               "GIS overlays."))),
        dict(match=dict(id=82), set=dict(status="wont_fix", resolved_date=TODAY, as_of_date=TODAY,
             notes=gap_note(82, "Closed as wont_fix: a schema task for the engineering backlog, not a "
                                "research question."))),
        dict(match=dict(id=104), set=dict(as_of_date=TODAY,
             notes=gap_note(104, "The author cannot say which building the register's 'IC3' is. It stays "
                                 "open. What would settle it: Macquarie Data Centres naming the certified "
                                 "building, or the Hosting Certification Framework's certificate scope. "
                                 "No value changes."))),
    ]

    pack = {
        "pack_id": "batch7-decisions-2026-11",
        "prepared_by": "scripts/curate_batch7_decisions.py, on the author's decisions of 2026-11-18",
        "prepared_on": TODAY,
        "_comment": [
            "The author's decisions on batch 7's proposals: SYD2 merged into the Lane Cove West consent row",
            "(the seed row is retired from seed_data.py), Apollo Place operator AirTrunk, Macquarie Park",
            "operational, Kemps Creek's unlabelled 190 MW cleared, MEL2 and Wesley Vale added without",
            "capacity, RG-001 and RG-082 closed, RG-104 left open. Loads after batch7_open_questions.json,",
            "whose notes it extends.",
        ],
        "sources": [],
        "rows": {"sites": sites, "research_gaps": gaps},
    }
    with open(OUT_PACK, "w") as f:
        json.dump(pack, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print(f"batch 7 decisions: {len(sites)} site rows, {len(gaps)} questions; wrote {os.path.relpath(OUT_PACK, ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
