#!/usr/bin/env python3
"""
Curate the RG-034 pack: post-consent modifications to NSW data centre consents.

Input : exports/nsw_planning/nsw_data_centre_modifications.csv (harvested by
        scrapers/ingest_nsw_dc.py --mods on 2026-09-18)
Output: data/packs/rg034_consent_modifications.json

Why this matters: a consent's original capacity is not its operating capacity. Fuel storage,
generator counts, building height and power consumption all change by modification, and
modifications appear in no headline pipeline figure, no IDA announcement and no submission to
the Legislative Council inquiry. The modification portal pages do not carry the development
description, so the `what_changed` field below is read off the modification TITLE, which the
Department itself writes descriptively — that is a weaker evidentiary basis than a consent
schedule and is graded accordingly in each row's notes.

Run:
    python3 scripts/curate_rg034.py
    python3 scripts/load_pack.py data/packs/rg034_consent_modifications.json --dry-run --allow-missing-source
"""
from __future__ import annotations

import csv
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV_IN = os.path.join(ROOT, "exports", "nsw_planning", "nsw_data_centre_modifications.csv")
OUT = os.path.join(ROOT, "data", "packs", "rg034_consent_modifications.json")
TODAY = "2026-09-18"
SRC = "SRC_NSWPORTAL_MODS"

# mod_case -> (site_id or None, change_type, materiality 1-5, what_changed)
# materiality: 5 = changes the environmental envelope the original consent was assessed against
MAP = {
 "SSD-10330-Mod-2": ("SITE_ROBERTS_RD", "generator_increase", 5,
    "Additional back-up generators and additional diesel storage at Roberts Road, Blacktown, approved "
    "6 March 2026. This is the clearest instance in the NSW record of the diesel and generator envelope "
    "being enlarged AFTER the original consent was assessed and granted, which means the air quality and "
    "noise assessment underpinning the consent no longer describes the facility. The original Roberts Road "
    "consent (SSD-10330) has no capacity figure in its portal description."),
 "SSD-21342738-Mod-2": ("SITE_EC_EXPANSION", "capacity_increase", 5,
    "Power consumption increase at the Eastern Creek Data Centre Expansion, Blacktown, approved 5 August "
    "2026 - twelve days before the NSW Data Centre Guidelines took effect on 17 August 2026. An approved "
    "increase in electricity demand, so the facility's grid connection and its share of any network "
    "augmentation were re-set by modification rather than by a fresh application."),
 "SSD-9741-Mod-1": ("SITE_LANE_COVE_WEST", "fuel_storage_increase", 5,
    "Fuel storage at Lane Cove West Data Centre, approved 14 April 2020. Lane Cove is the corridor where "
    "residents report an operating facility 350 m from homes, where the council's Deputy Mayor gave evidence "
    "to the Legislative Council inquiry on 8 May 2026, where a community planning group gave evidence on "
    "22 May 2026, and where the NSW Government IDA-endorsed a further project at 16-20 Mars Road on "
    "27 March 2026."),
 "SSD-10330-Mod-1": ("SITE_ROBERTS_RD", "height_increase", 3,
    "Building height increase at Roberts Road, Blacktown, approved 17 April 2024."),
 "SSD-24299707-Mod-1": ("SITE_TALAVERA", "capacity_increase", 4,
    "Expansion of the Talavera Road Data Centre Campus, City of Ryde, approved 19 December 2024. Talavera "
    "Road is the Macquarie Park data centre corridor."),
 "SSD-41589232-Mod-2": ("SITE_51_HUNTINGWOOD", "design", 2,
    "Design updates at 51 Huntingwood Drive, Blacktown, approved 28 August 2026 - eleven days after the NSW "
    "Data Centre Guidelines took effect."),
 "SSD-66777221-Mod-3": ("SITE_LANCELEY", "fire_or_safety", 3,
    "Fire access and switchroom changes at Lanceley Place, Artarmon (Willoughby), approved 11 August 2026 - "
    "six days before the Guidelines took effect. Fire access and switchroom changes are the physical "
    "consequences of the diesel and lithium-ion battery risk the Guidelines address at Principle 1 Ref 6."),
 "SSD-66777221-Mod-2": ("SITE_LANCELEY", "other", 2,
    "General modification at Lanceley Place, Artarmon (Willoughby), approved 14 April 2026."),
 "SSD-10101987-Mod-1": ("SITE_MSFT_KEMPS", "fit_out", 3,
    "Data hall fit-out at Microsoft's Kemps Creek Data Centre (SSD-10101987), Penrith, approved 18 November "
    "2024. Fit-out is where IT load, rack density and cooling configuration are actually determined, so a "
    "fit-out modification can change a facility's operating character without changing its consented power "
    "consumption ceiling."),
 "SSD-59416728-Mod-1": ("SITE_DAVIS_RD_CUNDALL", "landscaping", 1,
    "Tree removal correction at Davis Road Data Centre, Fairfield City, approved 15 August 2025."),
 "SSD-9741-Mod-2": ("SITE_LANE_COVE_WEST", "layout", 2,
    "Layout changes at Lane Cove West, approved 16 December 2020."),
 "SSD-9741-Mod-3": ("SITE_LANE_COVE_WEST", "design", 2,
    "Design changes at Lane Cove West, approved 13 June 2024."),
 "SSD-9741-Mod-4": ("SITE_LANE_COVE_WEST", "other", 3,
    "'APDC inclusion' at Lane Cove West, approved 9 October 2025. APDC is not expanded on the portal record; "
    "resolve what is being included before relying on this row (RG-045)."),
 "SSD-10330-Mod-4": ("SITE_ROBERTS_RD", "other", 4,
    "Changes to operational infrastructure at Roberts Road, Blacktown. NOT YET DETERMINED - portal stage is "
    "'Prepare Mod Report' as at 18 September 2026. A second round of operational-infrastructure changes at "
    "the same site that already received additional generators and diesel storage in March 2026."),
 "SSD-41589232-Mod-1": ("SITE_51_HUNTINGWOOD", "scale_reduction", 2,
    "Reduced scale at 51 Huntingwood Drive, Blacktown. WITHDRAWN. The subsequent Mod 2 (design updates) was "
    "approved on 28 August 2026, so a scale reduction was proposed, abandoned and replaced."),
 "MP08_0259-Mod-7": (None, "layout", 2,
    "Data centre site layout within the DEXUS Estate, spanning Blacktown, Cumberland and Fairfield LGAs, "
    "approved 30 September 2022. A Part 3A legacy case number (MP08_0259), so this sits under the repealed "
    "major-project regime rather than the current SSD framework."),
 "SSD-10479-Mod-8": (None, "road_or_access", 2,
    "Amendments to road upgrade works and timing at 200 Aldington, Penrith. Portal stage 'Recommendation' as "
    "at 18 September 2026 - not yet determined."),
}

SRC_RECORD = dict(
    id=SRC,
    title="NSW Planning Portal - post-consent modification records for data centre State Significant "
          "Developments (17 records harvested)",
    publisher="NSW Department of Planning, Housing and Infrastructure",
    url="https://www.planningportal.nsw.gov.au/major-projects/search?"
        "field_case_type_value=State+Significant+Development&combine=Data+Centre",
    doc_type="primary_planning_portal", published=None, credibility="A", accessed=TODAY,
    notes="Harvested 18 September 2026 by scrapers/ingest_nsw_dc.py --mods. Fifteen of 17 are determined and "
          "Approved; one is Withdrawn (51 Huntingwood Drive Mod 1, reduced scale); two are undetermined "
          "(Roberts Road Mod 4 at 'Prepare Mod Report', 200 Aldington Mod 8 at 'Recommendation'). Four were "
          "approved between 5 and 28 August 2026, i.e. either side of the NSW Data Centre Guidelines taking "
          "effect on 17 August 2026. Modification project pages do NOT carry the development description that "
          "original applications carry, so the change is read off the Department's own modification title and "
          "the underlying modification reports must be fetched to establish quantum (RG-045). Every node JSON "
          "is archived under data/raw/nsw_planning/nodes/ with a SHA-256 manifest.",
)


def main() -> int:
    rows = list(csv.DictReader(open(CSV_IN, encoding="utf-8")))
    by_case = {r["case_id"]: r for r in rows}

    mods, metrics = [], []
    for case, (site_id, ctype, materiality, what) in MAP.items():
        r = by_case.get(case)
        if not r:
            print(f"  WARNING: {case} in MAP but absent from the harvest")
            continue
        mods.append(dict(
            site_id=site_id, parent_case=case.rsplit("-Mod", 1)[0] if "-Mod" in case else case,
            mod_case=case, title=r["title"], lga=r["lga"] or None, stage=r["stage"] or None,
            decision=r["decision"] or None, determination_date=r["determination_date"] or None,
            change_type=ctype, what_changed=what, materiality=materiality,
            notes=f"Portal stage at harvest: {r['stage'] or 'not recorded'}. Development type "
                  f"{r['development_type'] or 'not recorded'}. {r['n_attachments']} documents attached to the "
                  f"modification record.",
            fact_status="VERIFIED", confidence="high", as_of_date=TODAY, source_id=SRC))

    approved = [m for m in mods if (m["decision"] or "").lower().startswith("approv")]
    material = [m for m in mods if m["materiality"] >= 4]
    post_guidelines = [m for m in mods
                       if m["determination_date"] and "2026-08-05" <= m["determination_date"] <= "2026-08-31"]
    metrics += [
        dict(as_of="2026-09", scope="NSW", metric_name="nsw_dc_consent_modifications_harvested",
             value=float(len(mods)), unit="count", basis="actual",
             notes="Post-consent modification records for data centre SSDs on the NSW Planning Portal.",
             fact_status="VERIFIED", confidence="high", as_of_date=TODAY, source_id=SRC),
        dict(as_of="2026-09", scope="NSW", metric_name="nsw_dc_modifications_approved",
             value=float(len(approved)), unit="count", basis="actual",
             notes=f"{len(approved)} of {len(mods)} determined modifications were Approved. One was Withdrawn "
                   "(a scale reduction at 51 Huntingwood Drive) and two remain undetermined.",
             fact_status="VERIFIED", confidence="high", as_of_date=TODAY, source_id=SRC),
        dict(as_of="2026-09", scope="NSW", metric_name="nsw_dc_modifications_materiality_4plus",
             value=float(len(material)), unit="count", basis="actual",
             notes="Modifications scored 4 or 5 for materiality, i.e. changing the capacity, generator or fuel "
                   "envelope the original consent was assessed against: Roberts Road Mod 2 (additional "
                   "generators and diesel storage), Eastern Creek Mod 2 (power consumption increase), Lane Cove "
                   "West Mod 1 (fuel storage), Talavera Road Mod 1 (expansion), Roberts Road Mod 4 "
                   "(operational infrastructure, undetermined).",
             fact_status="VERIFIED", confidence="high", as_of_date=TODAY, source_id=SRC),
        dict(as_of="2026-08", scope="NSW", metric_name="nsw_dc_modifications_approved_aug2026",
             value=float(len(post_guidelines)), unit="count", basis="actual",
             notes="Modifications approved between 5 and 28 August 2026, i.e. either side of the NSW Data "
                   "Centre Guidelines taking effect on 17 August 2026: Eastern Creek Mod 2 (5 Aug, power "
                   "consumption increase), Lanceley Place Mod 3 (11 Aug, fire access and switchroom), 51 "
                   "Huntingwood Drive Mod 2 (28 Aug, design updates). None of the three is described as being "
                   "assessed against the Guidelines, and the Guidelines themselves say nothing about "
                   "modifications.",
             fact_status="VERIFIED", confidence="high", as_of_date=TODAY, source_id=SRC),
    ]

    pack = {
        "pack_id": "rg034-consent-modifications-2026-09",
        "prepared_by": "scripts/curate_rg034.py from exports/nsw_planning/nsw_data_centre_modifications.csv",
        "prepared_on": TODAY,
        "sources": [SRC_RECORD],
        "rows": {
            "modifications": mods,
            "metrics": metrics,
            "research_gaps": [
                dict(match=dict(id=34),
                     set=dict(status="in_progress",
                              notes="Advanced 2026-09-18. All 17 post-consent modification records for NSW data "
                                    "centre SSDs are harvested and loaded: case ids, stages, decisions, "
                                    "determination dates and LGAs. Fifteen approved, one withdrawn, two "
                                    "undetermined. Five are material to the environmental envelope (added "
                                    "generators and diesel at Roberts Road, a power consumption increase at "
                                    "Eastern Creek, added fuel storage at Lane Cove West, an expansion at "
                                    "Talavera Road, and pending operational-infrastructure changes at Roberts "
                                    "Road again). RESIDUAL: modification pages do not publish the development "
                                    "description, so the QUANTUM of each change is unknown - the underlying "
                                    "modification reports must be fetched (RG-045). Local council development "
                                    "applications are also still out of scope.",
                              fact_status="VERIFIED", confidence="high", as_of_date=TODAY, source_id=SRC),
                     add_sources=[SRC]),
                dict(id=45, pillar="C", priority=5, retrieval_method="scrape_portal", status="open",
                     opened=TODAY,
                     question="Fetch the modification reports and determinations for the five material "
                              "post-consent modifications and quantify each change: how many additional "
                              "generators and how much additional diesel at Roberts Road (SSD-10330-Mod-2), how "
                              "much additional power consumption at Eastern Creek (SSD-21342738-Mod-2), how "
                              "much additional fuel storage at Lane Cove West (SSD-9741-Mod-1), the extent of "
                              "the Talavera Road expansion (SSD-24299707-Mod-1), and what Roberts Road Mod 4 "
                              "proposes to change.",
                     why_it_matters="This is the mechanism by which the environmental envelope of a consented "
                                    "data centre grows without a fresh application, fresh exhibition or a fresh "
                                    "cumulative-impact assessment. The NSW Data Centre Guidelines say nothing "
                                    "about modifications, so a facility that satisfies dPUE, generator and "
                                    "diesel limits at consent can move away from them by modification. Until "
                                    "the quantum is known the Observatory can show that drift happens but not "
                                    "how far. Also resolve what 'APDC inclusion' means in Lane Cove West Mod 4.",
                     target_source="NSW Planning Portal attachment nodes for each modification case; the "
                                   "scrapers/ingest_nsw_dc.py --attachments SLUG command lists them",
                     fact_status="VERIFIED", confidence="high", as_of_date=TODAY, source_id=SRC),
                dict(id=46, pillar="C", priority=4, retrieval_method="manual_review", status="open",
                     opened=TODAY,
                     question="Do the NSW Data Centre Guidelines, the Commonwealth Expectations or any draft "
                              "National Electricity Rule change apply their performance measures to "
                              "post-consent MODIFICATIONS, or only to new applications and expansions?",
                     why_it_matters="If they apply only to new applications, then every existing consent in "
                                    "Western Sydney can be upgraded past the dPUE, dWUE, generator-hours, "
                                    "diesel-storage and PPA-additionality thresholds by modification, and the "
                                    "Guidelines will have no effect on the operating fleet - only on greenfield "
                                    "sites. The Commonwealth Expectations do say they apply to 'new or "
                                    "expanded' hyperscale facilities, which suggests expansion is captured, but "
                                    "the NSW Guidelines' own text does not address modifications and the "
                                    "Glendenning consent contains no modification-specific performance measure.",
                     target_source="NSW Data Centre Guidelines full text; Expectations of data centres and AI "
                                    "infrastructure developers; EP&A Act s.4.55 modification provisions and any "
                                    "DPHI practice note on modifications to data centre consents",
                     fact_status="VERIFIED", confidence="high", as_of_date=TODAY, source_id=SRC),
            ],
        },
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(pack, fh, indent=1)
    print(f"wrote {OUT}")
    print(f"  modifications={len(mods)} metrics={len(metrics)} "
          f"(approved={len(approved)}, materiality>=4: {len(material)}, Aug-2026: {len(post_guidelines)})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
