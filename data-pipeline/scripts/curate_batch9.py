#!/usr/bin/env python3
"""
Research batch 9 (2026-11-18): the remaining questions the agent can move on free sources, at the
author's direction ("continue with the remaining research questions"), under zero spend.

What this pass settles, from documents archived today:
  * RG-053 RESOLVED. The Western Downs application's appendices, re-fetched (SHA-256 matches the
    September manifest) and read: the title search, traffic, water, fire safety, air quality and
    economic benefit appendices. The application contradicts itself on IT capacity (2,160 MW in the
    planning report; ~1,440 MW in two appendices), ongoing jobs (~430 FTE against ~1,400) and back-up
    generators (20 in the air quality assessment; 8 per building in the fire strategy). Two changes
    to SITE_WESTERN_DOWNS are PROPOSED (capital cost, IT capacity). The record's lot plan, DY516, was
    a transcription error for DY316 and is corrected at its source (curate_rg049.py).
  * RG-104: Macquarie's own reporting (February and August 2026) says IC3 SuperWest was still being
    fitted out; SITE_MACQ_IC3's status change is PROPOSED.
  * RG-043: Transgrid's letter of 20 August 2026 to data centre applicants: augmentation costs fall
    on the proponent; about 1.5 GW signed; up to 2 GW more by augmentation.
  * RG-007: Queensland's tax expenditure statement, like NSW's, never mentions data centres;
    Victoria's budget paper refused the crawler (download #35).
  * RG-069 RESOLVED: the planning portal holds three donation disclosures on data centre
    applications, all now read or recorded as restricted; the NSW and Commonwealth amounts are in.
  * RG-100: a note on what remains, and a proposal to the author.

Outputs:
  * data/packs/batch9_open_questions.json

Run:
    python3 scripts/curate_batch9.py
    python3 scripts/load_pack.py data/packs/batch9_open_questions.json --allow-missing-source
"""
from __future__ import annotations

import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(ROOT, "data", "raw")
OUT_PACK = os.path.join(ROOT, "data", "packs", "batch9_open_questions.json")
THIS_PACK = "data/packs/batch9_open_questions.json"
TODAY = "2026-11-18"
TAG = f" UPDATED {TODAY} (research batch 9):"

SRC_WD = "SRC_WD_COUNCIL_DA"                       # existing: the lodged application
SRC_QLD = "SRC_QLD_BP2_2026_27"
SRC_TG = "SRC_TRANSGRID_SYDNEY_BASIN_20260820"
SRC_MAQ_REL = "SRC_MAQ_FY26_RESULTS_RELEASE"
SRC_MAQ_PRES = "SRC_MAQ_FY26_RESULTS_PRESENTATION"
SRC_MAQ_HY = "SRC_MAQ_HY26_BRIEFING"
SRC_MAQ_TOP = "SRC_MAQ_IC3SW_TOPPING_OUT"

TEXTS = {
    SRC_WD: "qld_western_downs/wdrc_6393206_1.appendices_excerpts.txt",
    SRC_QLD: "registers/qld_budget/2026-27-budget-bp2-budget-strategy-outlook.txt",
    SRC_TG: "operators/transgrid/20260820-sydney-basin-network-capacity-update.txt",
    SRC_MAQ_REL: "asx/maq/0738k2n30w6slp.excerpts.txt",
    SRC_MAQ_PRES: "asx/maq/0738k7f9vrp2mb.excerpts.txt",
    SRC_MAQ_HY: "operators/macquarie/Half-Year-Management-Briefing-to-Analysts.txt",
    SRC_MAQ_TOP: "operators/macquarie/treasurer-tops-out-macquarie-data-centres-newest-47mw-ai-and-cloud-data-centre.txt",
}

QUOTES = {
    SRC_WD: {
        "owner": "WAMBO CATTLE COMPANY PTY LIMITED A.C.N. 058 718 326",
        "lot": "LOT 125 CROWN PLAN DY316",
        "tia_capacity": "an ultimate capacity of 1,440 MW, delivered in 4 x 360 MW stages",
        "tia_staff": ("Nominal data centre staffing rate: 0.3 FTE per MW, resulting in approximately 430 FTE at the "
                      "ultimate 1,440 MW build"),
        "no_town_water": ("There is no reticulated (town) water network in the vicinity of the site, the nearest "
                          "reticulated water infrastructure being approximately 15 km away."),
        "no_cooling_water": "There is no anticipated continuous water demand for equipment cooling",
        "op_water": ("Operational phase (one building, irrigation included in non-potable): approximately 16.5 kL/day "
                     "total"),
        "con_water": "peak water demand during construction is expected to exceed 300 kL/day",
        "fire_gens": "Generator Enclosures (8 per building)",
        "fire_diesel": "Diesel 186,336 Litre",
        "aq_gens": ("Five (5) 2.2MW diesel generators will be installed in each data hall, totaling 20 generators with "
                    "a combined generation capacity of 44 MW."),
        "aq_use": ("The diesel generators are proposed to provide backup power for network rooms and lift safety "
                   "services only."),
        "aq_testing": "a total of 50 operational hours per year for testing across all four data halls",
        "eba_capacity": "Total data centre IT load capacity of ~1.44 GW.",
        "eba_cost": "A total construction cost of $14.5B excluding GST ($16B including GST).",
        "eba_jobs": "~1,400+ ongoing jobs to operate and maintain the campus post construction",
    },
    SRC_QLD: {
        "tes": ("This Tax Expenditure Statement (TES) details revenue forgone as a result of Queensland Government "
                "decisions relating to the provision of tax exemptions or concessions."),
    },
    SRC_TG: {
        "enquiries": ("Connection enquiries representing more than 20 GW of data centre load, about double NSW’s "
                      "current peak demand, have been lodged with Transgrid."),
        "signed": ("Transgrid has signed connection agreements with data centres representing approximately 1.5 GW of "
                   "demand in Western Sydney"),
        "unable": ("Transgrid is unable to offer capacity to any prospective connection applicants in this region "
                   "unless the appropriate network augmentation is undertaken with the connection"),
        "unlock": ("augmentation of the transmission network could unlock up to 2 GW of additional capacity for data "
                   "centre connections across the Sydney basin"),
        "borne": ("the costs of those augmentations will be borne by the data centre proponent creating that need "
                  "rather than electricity consumers more broadly"),
    },
    SRC_MAQ_REL: {
        "on_track": "IC3 SuperWest construction remains on track and on budget.",
        "revenue": "assuming IC3 SuperWest Phase 1 revenue commences in 2H FY27",
    },
    SRC_MAQ_PRES: {
        "fitout": ("Construction of IC3 SuperWest core and shell is complete, with the mechanical and electrical fit "
                   "out progressing on time and on budget."),
        "once": "Once completed, IC3 SuperWest, located in Macquarie Park, will add an additional 47MW.",
        "campus": ("IC3SW has design capacity of 47MW, increasing Macquarie Park Data Centre Campus’ capacity to 65MW "
                   "(including IC2 and IC3 East)."),
    },
    SRC_MAQ_TOP: {
        "open": "IC3 Super West is on track to open in Sydney’s north zone in September 2026",
        "phase1": ("Phase 1 of the build is a ~$350 million investment and will deliver the complete core and shell "
                   "with 6MW IT load fitted out."),
    },
    SRC_MAQ_HY: {
        "names": ("Macquarie Park Data Centre Campus: IC2, IC3 East and IC3 SuperWest (expected to be completed by "
                  "September 2026)"),
    },
}

NEW_SOURCES = [
    (SRC_QLD, "Queensland Budget 2026-27, Budget Paper No. 2: Budget Strategy and Outlook", "Queensland Treasury",
     None, "primary_government", "A",
     "Appendix B is the State's tax expenditure statement. The paper never mentions data centres (checked by the "
     "curation script). RG-007."),
    (SRC_TG, "Update on network capacity and connection pathway for data centres in the Sydney basin (Transgrid "
             "letter to data centre applicants, 20 August 2026)", "Transgrid", "2026-08-20", "primary_company", "A",
     "Sent to all data centre proponents at once: more than 20 GW of data centre enquiries lodged; about 1.5 GW of "
     "signed agreements in Western Sydney fit the existing network; no further capacity without augmentation, which "
     "could unlock up to 2 GW; augmentation costs 'borne by the data centre proponent creating that need rather "
     "than electricity consumers more broadly'. RG-043."),
    (SRC_MAQ_REL, "Macquarie Technology delivers twelve consecutive years of EBITDA growth (ASX release, 26 August "
                  "2026)", "Macquarie Technology Group", "2026-08-26", "primary_company", "A",
     "The full-year results release. Archived as a manifest and verbatim excerpts only (ASX's terms); the PDF is not "
     "committed. RG-104."),
    (SRC_MAQ_PRES, "Macquarie Technology Group Full Year Results 2026 (ASX presentation, 26 August 2026)",
     "Macquarie Technology Group", "2026-08-26", "primary_company", "A",
     "The full-year results presentation: IC3 SuperWest's core and shell complete and its fit-out under way; 'Once "
     "completed' it adds 47 MW. Manifest and verbatim excerpts only (ASX's terms). RG-104."),
    (SRC_MAQ_HY, "Macquarie Technology Group Half Year Results 1H2026: management briefing to analysts (26 February 2026)",
     "Macquarie Technology Group", "2026-02-26", "primary_company", "A",
     "The company's own list of its Macquarie Park campus: IC2, IC3 East and IC3 SuperWest, the last 'expected to "
     "be completed by September 2026'. RG-104."),
    (SRC_MAQ_TOP, "Treasurer 'Tops Out' Macquarie Data Centres' newest 47MW AI and cloud data centre",
     "Macquarie Data Centres", "2025-12-03", "primary_company", "A",
     "The operator's post on the topping out of IC3 Super West by the NSW Treasurer (named in the post; recorded "
     "here by role): the external structure complete, opening scheduled for September 2026, and Phase 1 a ~$350 "
     "million investment delivering the core and shell with 6 MW of IT load fitted out. RG-104."),
]


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


def manifest(rel_txt: str) -> dict:
    base = os.path.join(RAW, rel_txt)
    for cand in (base + ".meta.json", re.sub(r"\.(excerpts\.)?txt$", "", base) + ".pdf.meta.json",
                 re.sub(r"\.txt$", "", base) + ".html.meta.json"):
        if os.path.exists(cand):
            return json.load(open(cand, encoding="utf-8"))
    raise FileNotFoundError(base)


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
    if SRC_QLD in texts and re.search(r"data cent", texts[SRC_QLD], re.I):
        errors.append(f"{SRC_QLD}: the note says the paper never mentions data centres, but it does")
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

    sources = []
    for sid, title, publisher, published, doc_type, cred, notes in NEW_SOURCES:
        meta = manifest(TEXTS[sid])
        sources.append(dict(id=sid, title=title, publisher=publisher, url=meta["url"], doc_type=doc_type,
                            published=published, credibility=cred, accessed=TODAY,
                            notes=notes + f" Archived {TODAY} at data/raw/{TEXTS[sid]} with a manifest "
                                          f"(SHA-256 {meta['sha256'][:16]}...)."))

    def gap(gap_id: int, text: str, refs: list[tuple[str, str]], status: str | None = None,
            resolved: bool = False) -> list[dict]:
        upd = dict(notes=(prior_notes(gap_id) + TAG + " " + text).strip(), as_of_date=TODAY)
        if status:
            upd["status"] = status
        if resolved:
            upd["resolved_date"] = TODAY
        return [dict(match=dict(id=gap_id), set=upd, add_sources=q(*refs) if refs else [])]

    gaps: list[dict] = []
    gaps += gap(53, (
        "RESOLVED. The lodged application was re-fetched (its SHA-256 matches the September manifest) and its "
        "appendices read as text; the pages cited are archived as excerpts. TITLE (Appendix B): registered owner "
        "'WAMBO CATTLE COMPANY PTY LIMITED A.C.N. 058 718 326', 'LOT 125 CROWN PLAN DY316' (the record had DY516, a "
        "transcription error, corrected at its source). WATER (Infrastructure Services Report): 'There is no "
        "reticulated (town) water network in the vicinity of the site', so supply is on site; 'There is no "
        "anticipated continuous water demand for equipment cooling'; construction peaks above 300 kL/day; one "
        "building in operation about 16.5 kL/day. BACK-UP POWER: the air quality assessment says 'Five (5) 2.2MW "
        "diesel generators will be installed in each data hall, totaling 20 generators with a combined generation "
        "capacity of 44 MW', for 'network rooms and lift safety services only', tested 50 hours a year in all; the "
        "fire safety strategy says 'Generator Enclosures (8 per building)' and lists 186,336 litres of diesel. "
        "THE APPLICATION CONTRADICTS ITSELF. IT capacity: the planning report gives approximately 2,160 MW; the "
        "traffic assessment 'an ultimate capacity of 1,440 MW, delivered in 4 x 360 MW stages', and the economic "
        "assessment 'Total data centre IT load capacity of ~1.44 GW.' Ongoing jobs: the traffic assessment "
        "'approximately 430 FTE at the ultimate 1,440 MW build'; the economic assessment '~1,400+ ongoing jobs'. "
        "Cost: the economic assessment gives '$14.5B excluding GST ($16B including GST)'; the record's A$31.9bn "
        "came in with the ABC's report (SRC_ABC_WD), not from the application. The ABC's 1.44 GW of IT capacity "
        "and 2.16 GW of total peak, as the seed row summarised it, read like the appendices; the planning report "
        "calls 2,160 MW the IT load and 3,240 MVA the total. PROPOSED to the author: SITE_WESTERN_DOWNS "
        "capital_cost_aud A$31.9bn (press) -> A$14.5bn excluding GST (the application's own figure); "
        "it_capacity_mw either kept at 2,160 (the planning report, which the row cites) with the conflict noted, "
        "or cleared until the applicant says which figure stands. Neither change is made by this pack."),
        [(SRC_WD, "owner"), (SRC_WD, "lot"), (SRC_WD, "no_town_water"), (SRC_WD, "no_cooling_water"),
         (SRC_WD, "con_water"), (SRC_WD, "op_water"), (SRC_WD, "aq_gens"), (SRC_WD, "aq_use"), (SRC_WD, "aq_testing"),
         (SRC_WD, "fire_gens"), (SRC_WD, "fire_diesel"), (SRC_WD, "tia_capacity"), (SRC_WD, "tia_staff"),
         (SRC_WD, "eba_capacity"), (SRC_WD, "eba_jobs"), (SRC_WD, "eba_cost")],
        status="resolved", resolved=True)
    gaps += gap(104, (
        "Macquarie's own reporting settles the status, not the certificate. February 2026: 'Macquarie Park Data "
        "Centre Campus: IC2, IC3 East and IC3 SuperWest (expected to be completed by September 2026)'. 26 August "
        "2026: 'Construction of IC3 SuperWest core and shell is complete, with the mechanical and electrical fit out "
        "progressing on time and on budget', 'Once completed, IC3 SuperWest ... will add an additional 47MW', and "
        "the results assume 'IC3 SuperWest Phase 1 revenue commences in 2H FY27'. So IC3 SuperWest was not "
        "operating at the end of August 2026. Its first phase is smaller than the building: at the topping out "
        "(3 December 2025) the operator said 'Phase 1 of the build is a ~$350 million investment and will deliver "
        "the complete core and shell with 6MW IT load fitted out'. The company's own names for the campus are "
        "IC2, IC3 East and IC3 SuperWest. PROPOSED to the author: SITE_MACQ_IC3 status operational -> under_construction, cited to the "
        "August 2026 results. Which building the register's 'IC3' certifies remains for Macquarie or the "
        "certificate to say."),
        [(SRC_MAQ_TOP, "open"), (SRC_MAQ_TOP, "phase1"), (SRC_MAQ_HY, "names"), (SRC_MAQ_PRES, "fitout"),
         (SRC_MAQ_PRES, "once"), (SRC_MAQ_PRES, "campus"), (SRC_MAQ_REL, "on_track"), (SRC_MAQ_REL, "revenue")],
        status="in_progress")
    gaps += gap(43, (
        "Transgrid's letter to all data centre applicants of 20 August 2026 settles who pays for new capacity, not "
        "how much: about 1.5 GW of signed agreements in Western Sydney fit the existing network; beyond that "
        "'Transgrid is unable to offer capacity ... unless the appropriate network augmentation is undertaken with "
        "the connection'; augmentation 'could unlock up to 2 GW'; and 'the costs of those augmentations will be "
        "borne by the data centre proponent creating that need rather than electricity consumers more broadly'. "
        "Enquiries exceed 20 GW. No dollar figure is given, so the $10.3bn claim is still untested against the "
        "networks' own numbers."),
        [(SRC_TG, "signed"), (SRC_TG, "unable"), (SRC_TG, "unlock"), (SRC_TG, "borne"), (SRC_TG, "enquiries")],
        status="in_progress")
    gaps += gap(7, (
        "QUEENSLAND: the 2026-27 Budget Strategy and Outlook carries the State's tax expenditure statement and "
        "never mentions data centres (checked by this pack's script). VICTORIA: Budget Paper No. 5 is hosted where "
        "the crawler's robots check fails (recorded); download #35. Still unread: WA, SA, Tasmania, the ACT and "
        "the NT."), [(SRC_QLD, "tes")], status="in_progress")
    gaps += gap(69, (
        "RESOLVED. The survey of the planning record is complete: the NSW data centre attachment index holds three "
        "political donation disclosures (Roberts Road and Talavera Road, both read; Mamre Road, restricted and in "
        "GIPA-003, not lodged). The NSW Electoral Commission's register (Amazon Web Services Australia, $39,350 over "
        "2023/24 to 2025/26) and the AEC's Commonwealth returns are recorded above. The recipients of Amazon Web "
        "Services Australia's NSW donations are not in what was read; re-open if the author reads them."), [],
        status="resolved", resolved=True)
    gaps += gap(100, (
        "What rests on CertifiedStrategic.com alone is now the two CBRE figures (live capacity 1,400 MW in 2025 and "
        "1,800 MW by 2028), with CBRE's site refusing the crawler. The national count of certified facilities also "
        "still cites it, but that metric is already at low confidence and marked superseded by the count taken "
        "from the register itself (hcf_certified_strategic_register); the Mandala figures are re-sourced. PROPOSED to the author: keep the two CBRE metrics at low confidence as reported "
        "second-hand, or retire them."), [])

    pack = {
        "pack_id": "batch9-open-questions-2026-11",
        "prepared_by": "scripts/curate_batch9.py from data/raw/ (archived and read 2026-11-18)",
        "prepared_on": TODAY,
        "_comment": [
            "Research batch 9: the Western Downs appendices (RG-053, resolved), Macquarie's own reporting on IC3",
            "SuperWest (RG-104), Transgrid's letter to applicants (RG-043), Queensland's tax expenditure statement",
            "(RG-007), and RG-069 closed on the planning record. Changes to SITE_WESTERN_DOWNS and SITE_MACQ_IC3",
            "are PROPOSED in the notes; this pack changes no site value.",
        ],
        "sources": sources,
        "rows": {"research_gaps": gaps},
    }
    with open(OUT_PACK, "w") as f:
        json.dump(pack, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print(f"batch 9: {len(sources)} sources, {len(gaps)} question updates; wrote {os.path.relpath(OUT_PACK, ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
