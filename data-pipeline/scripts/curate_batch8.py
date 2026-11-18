#!/usr/bin/env python3
"""
Research batch 8, first pass (2026-11-18): the questions the agent can settle from free records,
under the author's zero-spend decision of 2026-11-18 (docs/PUBLICATION-PLAN.md, Decisions).

What this pass settles, from documents already archived or read from the planning portal today:
  * RG-062 RESOLVED (negative). No consent or modification read relies on the Guidelines'
    definition of recycled water; the closest usage (rainwater tanks under "Recycled water and
    reuse" at DigiCo SYD1) predates the Guidelines.
  * RG-075 RESOLVED. Every peer review opened is by a different firm from the author, and every
    one was commissioned by the applicant or its planner. The acoustic reviews did no remodelling.
  * RG-073 ADVANCED. The firm behind the acoustic and air quality report of each determined
    consent, read from the reports' own cover and document-control pages, not from filenames.
  * RG-061 ADVANCED. Generator-hour caps and the 2,000-tonne diesel cap, counted across the 20
    archived consents by this script (the counts are computed, not typed), and the EPA's own
    reason for the 200-hour cap.
  * RG-008 BLOCKED on download #28, after a first pass: which sites the EPA said need a licence.
  * Zero spend: the questions that wait on a fee-bearing state request are set to `blocked`,
    naming the request; the four waiting on free Commonwealth FOI requests are set to `blocked`
    until the author lodges them and a reply comes; the paid-search questions say so.
  * RG-076 and RG-090 are PROPOSED to the author for closing as resolved-negative. This pack
    closes neither.

Outputs:
  * data/packs/batch8_open_questions.json

Run:
    python3 scripts/curate_batch8.py
    python3 scripts/load_pack.py data/packs/batch8_open_questions.json --allow-missing-source
"""
from __future__ import annotations

import glob
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(ROOT, "data", "raw")
DOCS = os.path.join(RAW, "nsw_planning", "documents")
CONSENTS = os.path.join(RAW, "nsw_planning", "consents")
PACKS_DIR = os.path.join(ROOT, "data", "packs")
OUT_PACK = os.path.join(PACKS_DIR, "batch8_open_questions.json")
THIS_PACK = "data/packs/batch8_open_questions.json"
TODAY = "2026-11-18"
TAG = f" UPDATED {TODAY} (research batch 8):"

# Existing sources this pack cites.
SRC_GUIDE = "SRC_NSWGUIDE26"
SRC_CONSENTS = "SRC_NSWPORTAL_CONSENTS"
SRC_RR = "SRC_SSD10330_ASSESSMENT"
SRC_RR_MOD2 = "SRC_SSD10330_MOD2_ASSESSMENT"
SRC_MPDC = "SRC_SSD10467_ASSESSMENT"
SRC_KHARTOUM = "SRC_SSD63235720_ASSESSMENT"
SRC_HUNTINGWOOD = "SRC_SSD41589232_ASSESSMENT"
SRC_S4 = "SRC_SSD63741210_ASSESSMENT"
SRC_S5 = "SRC_SSD63168959_EIS"
SRC_MARSDEN = "SRC_SSD70889211_ASSESSMENT"
SRC_GLEN = "SRC_SSD73761707_ASSESSMENT"
SRC_GRAND = "SRC_SSD53338465_ASSESSMENT"
SRC_PLUTO = "SRC_SSD69223466_ASSESSMENT"
SRC_APOLLO = "SRC_SSD74069708_ASSESSMENT"
SRC_DAVIS = "SRC_SSD59416728_ASSESSMENT"
SRC_APOLLO_PL = "SRC_SSD67407231_ASSESSMENT"
SRC_ECHIDNA = "SRC_SSD47320208_ASSESSMENT"
SRC_EC = "SRC_SSD21342738_ASSESSMENT"
SRC_TALAVERA = "SRC_SSD24299707_ASSESSMENT"
SRC_STATION = "SRC_SSD33781208_ASSESSMENT"
SRC_KEMPS = "SRC_SSD10101987_ASSESSMENT"
SRC_DIGICO = "SRC_SSD69637456_ASSESSMENT"
SRC_LCW = "SRC_SSD9741_ASSESSMENT"
SRC_DICKER = "SRC_SSD8662_ASSESSMENT"
# New sources, read from the planning portal today.
SRC_PR_DIGICO = "SRC_SSD69637456_ACOUSTIC_PEER_REVIEW"
SRC_PR_LCW = "SRC_SSD9741_MOD3_ACOUSTIC_PEER_REVIEW"
SRC_PR_RR4 = "SRC_SSD10330_MOD4_GHG_REVIEW"
SRC_TECH = "SRC_NSWPORTAL_TECH_REPORTS"
SRC_GHG_ATLAS = "SRC_SSD101067971_GHG_REVIEW"
SRC_GHG_RR2 = "SRC_SSD10330_MOD2_GHG_REVIEW"

TEXTS = {
    SRC_GUIDE: "operators/nswgov/id0073_nsw-data-centre_guidelines.txt",
    SRC_RR: "nsw_planning/documents/SSD-10330_assessment.txt",
    SRC_RR_MOD2: "nsw_planning/documents/SSD-10330-Mod-2_mod_assessment.txt",
    SRC_MPDC: "nsw_planning/documents/SSD-10467_assessment.txt",
    SRC_KHARTOUM: "nsw_planning/documents/SSD-63235720_assessment.txt",
    SRC_HUNTINGWOOD: "nsw_planning/documents/SSD-41589232_assessment.txt",
    SRC_S4: "nsw_planning/documents/SSD-63741210_assessment.txt",
    SRC_S5: "nsw_planning/documents/SSD-63168959_eis.txt",
    SRC_MARSDEN: "nsw_planning/documents/SSD-70889211_assessment.txt",
    SRC_GLEN: "nsw_planning/documents/SSD-73761707_assessment.txt",
    SRC_GRAND: "nsw_planning/documents/SSD-53338465_assessment.txt",
    SRC_PLUTO: "nsw_planning/documents/SSD-69223466_assessment.txt",
    SRC_APOLLO: "nsw_planning/documents/SSD-74069708_assessment.txt",
    SRC_DAVIS: "nsw_planning/documents/SSD-59416728_assessment.txt",
    SRC_APOLLO_PL: "nsw_planning/documents/SSD-67407231_assessment.txt",
    SRC_ECHIDNA: "nsw_planning/documents/SSD-47320208_assessment.txt",
    SRC_EC: "nsw_planning/documents/SSD-21342738_assessment.txt",
    SRC_TALAVERA: "nsw_planning/documents/SSD-24299707_assessment.txt",
    SRC_STATION: "nsw_planning/documents/SSD-33781208_assessment.txt",
    SRC_KEMPS: "nsw_planning/documents/SSD-10101987_assessment.txt",
    SRC_DIGICO: "nsw_planning/documents/SSD-69637456_assessment.txt",
    SRC_LCW: "nsw_planning/documents/SSD-9741_assessment.txt",
    SRC_DICKER: "nsw_planning/documents/SSD-8662_assessment.txt",
    SRC_PR_DIGICO: "nsw_planning/documents/SSD-69637456_acoustic_peer_review.txt",
    SRC_PR_LCW: "nsw_planning/documents/SSD-9741-Mod-3_acoustic_peer_review.txt",
    SRC_PR_RR4: "nsw_planning/documents/SSD-10330-Mod-4_ghg_peer_review.txt",
    SRC_GHG_ATLAS: "nsw_planning/documents/SSD-101067971_ghg_review.txt",
    SRC_GHG_RR2: "nsw_planning/documents/SSD-10330-Mod-2_ghg_review.txt",
}

# Quotes from one consent instrument each. They are cited as SRC_NSWPORTAL_CONSENTS, the bulk
# harvest the 20 instruments belong to, and checked against the named instrument.
CONSENT_QUOTES = {
    "digico_rain": ("digico_syd1_data_centre_expansion.txt",
                    "Recycled water and reuse, through: o Use of 2x5000L existing rainwater tanks"),
    "water_review": ("glendenning_road_data_centre.txt",
                     "review of available water servicing arrangements, in consultation with the relevant "
                     "water service provider, to identify any alternative"),
    "pluto_hours": ("project_pluto_data_centre.txt", "exceed 173 hours per year"),
    "apollo_hours": ("project_apollo_data_centre_macquarie_park.txt", "exceed 187 hours per year"),
    "glen_hours": ("glendenning_road_data_centre.txt", "does not exceed 170 hours per year"),
    "khartoum_72": ("1_5_khartoum_road_data_centre.txt",
                    "Total generator testing time is limited to 72 hours per year"),
    "khartoum_200": ("1_5_khartoum_road_data_centre.txt", "does not exceed 200 hours per year"),
    "rr_diesel": ("roberts_road_data_centre.txt", "does not exceed 2,000 tonnes"),
}

# Every quote is checked verbatim (whitespace normalised) against the archived text before writing.
QUOTES = {
    SRC_GUIDE: {
        "recycled": ("Recycled water includes that provided by recycled water networks or on-site water "
                     "treatment, such as from captured stormwater."),
        "hours": ("Current regulations allow data centres to use generators for up to 200 hours a year "
                  "without being subject to any point source emission limits for oxides of nitrogen"),
    },
    SRC_RR: {
        "no_epl": ("The EPA also confirmed the testing regime proposed by the Applicant would not constitute "
                   "a scheduled activity under the POEO Act and therefore the development would not require "
                   "an EPL."),
    },
    SRC_RR_MOD2: {
        "epl": ("will require an environment protection licence issued by the NSW Environment Protection "
                "Authority (EPA) under section 42"),
        "diesel": ("The EPA advised t he development would require an environment protection licence under "
                   "Schedule 1 of the Protection of the Environment Operations Act 1997 (POEO Act) for "
                   "Chemical Storage (diesel fuel)."),
    },
    SRC_MPDC: {
        "cap": ("To ensure an EPL is not required, the EPA recommended a condition be imposed restricting the "
                "use and/or testing of any back-up generators installed at the site to a maximum of 200 hours "
                "per year."),
    },
    SRC_KHARTOUM: {
        "authority": ("the EPA provided no further comments on the development as an EPL is not required for "
                      "the site and therefore the EPA does not consider itself to be the appropriate regulatory "
                      "authority for air emissions associated with the development"),
    },
    SRC_HUNTINGWOOD: {
        "epl": ("an Environment Protection Licence (EPL) will need to be applied for and issued by the "
                "Environment Protection Authority (EPA) under the Protection of the Environment Operations "
                "Act 1997"),
    },
    SRC_S4: {
        "epl": ("The EPA advised the development would require an EPL for the quantity of diesel storage on "
                "the site above the thresholds of the POEO Act."),
    },
    SRC_MARSDEN: {
        "epl": ("The EPA advised the development would require an EPL for the quantity of diesel storage on "
                "the site above the thresholds of the POEO Act."),
    },
    SRC_S5: {
        "trigger": "below the 2,000-tonne trigger for petroleum products storage for which an EPL would be required",
    },
    SRC_GLEN: {
        "first": ("Noted based on the information provided, the development would require an Environment "
                  "Protection Licence (EPL)"),
        "below": ("The EPA noted the Applicant had confirmed the total diesel storage capacity of the site would "
                  "be below 2,000 tonnes and, consequently, the development would not require an EPL under the "
                  "POEO Act."),
        "guidelines": ("The Department has considered the Guidelines as a relevant consideration under section "
                       "4.15 of the EP&A Act."),
    },
    SRC_GRAND: {
        "stay": "recommended conditions to ensure the development would stay under the triggers for an EPL",
    },
    SRC_PLUTO: {
        "below": ("recommended consent conditions to ensure diesel storage and generator testing remain below "
                  "POEO Act thresholds and noted the Applicant must apply for an EPL if limits are exceeded"),
    },
    SRC_APOLLO: {
        "appear": ("The EPA advised that the proposal does not appear to require an Environment Protection "
                   "Licence under the POEO Act."),
        "guidelines": ("The Department has considered the Guidelines as a relevant consideration under section "
                       "4.15 of the EP&A Act."),
        "offer": "Routine generator testing of up to 187 hours per year is required",
        "revised": "the generator operating regime has been revised to remain below 200 hours per year",
    },
    SRC_EC: {"no_epl": "subject to conditions, an Environment Protection Licence (EPL) is not required"},
    SRC_TALAVERA: {"no_epl": "subject to conditions, an Environment Protection Licence (EPL) is not required"},
    SRC_STATION: {"no_epl": "subject to conditions, an Environment Protection Licence (EPL) is not required",
                  "lci": "SSDA Acoustic Assessment Report prepared by LCI Consultants"},
    SRC_KEMPS: {"no_epl": "subject to conditions, an Environmental Protection Licence (EPL) is not required"},
    SRC_DIGICO: {"no_epl": "The EPA noted the development does not require an environment protection licence"},
    SRC_LCW: {"no_epl": "Therefore, an Environment Protection Licence (EPL) is not required."},
    SRC_DICKER: {"no_epl": "therefore an Environment Protection Licence (EPL) is not required"},
    SRC_DAVIS: {
        "no_epl": ("The EPA did not provide any comments, noting the development would not require an "
                   "Environment Protection Licence (EPL) under the Protection of the Environment Operations Act "
                   "1997 (POEO Act)."),
    },
    SRC_APOLLO_PL: {
        "no_epl": "Advised the proposal does not trigger Schedule 1 of the POEO Act and does not require an EPL.",
    },
    SRC_ECHIDNA: {
        "no_epl": ("The EPA advised it had no comments on the development as the development does not constitute "
                   "a scheduled activity under Schedule 1 of the Protection of the Environment Operations Act 1997 "
                   "(POEO Act)."),
    },
    SRC_PR_DIGICO: {
        "engaged": ("Renzo Tonin & Associates (RTA) was engaged by Patch Planning, on behalf of HDI SYD1 Property "
                    "Holdings Pty Limited (DigiCo) to peer review the noise and vibration impact assessment (NVIA) "
                    "report undertaken by Pulse White Noise Acoustics (PWNA)"),
        "no_model": "The peer review process did not involve any detailed modelling checks or remodelling by RTA.",
        "revisions": "conducting reviews or partial reviews of eight revisions of the NVIA",
    },
    SRC_PR_LCW: {
        "engaged": ("Renzo Tonin & Associates (RTA) was engaged by EMKC Cubed Management (EMKC) to undertake an "
                    "independent review of the Noise Impact Assessment (NIA) prepared by Pulse White Noise "
                    "Acoustics (PWNA) for the Proposed S4.55 Modification Application for the AirTrunk SYD2 "
                    "Datacentre"),
        "no_model": "The peer review process did not involve any detailed modelling checks or remodelling by RTA.",
        "revisions": "conducting seven reviews of the NIA",
    },
    SRC_PR_RR4: {
        "engaged": ("Zephyr Environmental Pty Ltd (Zephyr) has been engaged by Canberra Data Centres (CDC) to "
                    "perform an independent review of the Greenhouse Gas (GHG) Assessment Report"),
        "author": "Revision 05, SLR Consulting, 16 July 2026",
        "mandatory": ("For projects with Scope 1 and 2 emissions exceeding 100,000 tCO 2-e per year at any time "
                      "over the operational life of the project, mitigation assessments must be verified by an "
                      "independent expert review."),
        "kit": "is expected to involve the addition of 24 new diesel generators and 32 new chillers",
        "threshold": "the Scope 1 & 2 emissions exceed 25,000 tCO2-e per year",
        "satisfactory": "CDC’s offset strategy for the Eastern Creek modification is considered satisfactory",
    },
    SRC_GHG_ATLAS: {
        "engaged": ("Zephyr Environmental Pty Ltd (Zephyr) has been engaged by LCI Consultants (LCI ), on behalf of "
                    "Goodman Property Services (Aust) Pty Ltd (Goodman Property Services) to perform an independent "
                    "review of the Greenhouse Gas (GHG) Assessment Report"),
        "author": "The Assessment Report has been prepared by LCI on behalf of Goodman Property Services",
        "conflict": ("No actual or perceived conflicts of interest have come to my attention, and I have not been "
                     "employed by the proponent within the last five years."),
        "adequate": "the mitigation strategy laid out for the proposed development is considered adequate",
    },
    SRC_GHG_RR2: {
        "engaged": ("Zephyr Environmental Pty Ltd (Zephyr) has been engaged by Urbis, on behalf of Canberra Data "
                    "Centres (CDC) to perform an independent review of the Greenhouse Gas (GHG) Assessment Report"),
        "author": "The GHG Assessment Report has been prepared by SLR Consulting Australia on behalf of CDC",
        "conflict": ("No actual or perceived conflicts of interest have come to my attention, and I have not been "
                     "employed by the proponent within the last five years."),
        "satisfactory": "CDC’s offset strategy for the Eastern Creek modification is considered satisfactory",
    },
}

# The firm named on each report's own cover or document-control page (RG-073). Each entry is
# (case, kind, firm, quote); the quote is checked against the report's archived text. Reports whose
# pages name no firm are left out and listed in the note as unread, never guessed.
AUTHORS: list[tuple[str, str, str, str]] = [
    ("SSD-63235720", "noise_assessment", "Arup Australia", "Arup Australia Pty Ltd | ABN 76 625 912 665"),
    ("SSD-63235720", "air_quality_report", "Arup Australia", "Arup Australia Pty Ltd | ABN 76 625 912 665"),
    ("SSD-68013714", "noise_assessment", "Arup", "Arup Pty Limited | ABN 18 000 966 165"),
    ("SSD-68013714", "air_quality_report", "Arup", "Arup Pty Ltd (Arup) was"),
    ("SSD-41589232", "noise_assessment", "Pulse White Noise Acoustics",
     "PREPARED BY: Pulse White Noise Acoustics Pty Ltd"),
    ("SSD-41589232", "air_quality_report", "Northstar Air Quality",
     "This document has been prepared for EMKC3 by: Northstar Air Quality Pty Ltd"),
    ("SSD-67407231", "noise_assessment", "Renzo Tonin & Associates",
     "carried out in accordance with the Renzo Tonin & Associates Quality Assurance System"),
    ("SSD-67407231", "air_quality_report", "Northstar Air Quality",
     "prepared for EMKC Cubed Management Pty Ltd by: Northstar Air Quality Pty Ltd"),
    ("SSD-59416728", "noise_assessment", "Cundall",
     "© Cundall Johnston & Partners PTY Ltd (“Cundall”) owns the copyright in this report"),
    ("SSD-59416728", "air_quality_report", "Cundall",
     "© Cundall Johnston & Partners LLP (“Cundall”) owns the copyright in this report"),
    ("SSD-64287712", "noise_assessment", "SLR Consulting", "Prepared by: SLR Consulting Australia"),
    ("SSD-64287712", "air_quality_report", "SLR Consulting", "Prepared by: SLR Consulting Australia Pty Ltd"),
    ("SSD-69637456", "noise_assessment", "Pulse White Noise Acoustics",
     "PREPARED BY: Pulse White Noise Acoustics Pty Ltd"),
    ("SSD-69637456", "air_quality_report", "Northstar Air Quality",
     "prepared for HDI SYD1 Property Holdings Pty Limited by: Northstar Air Quality Pty Ltd"),
    ("SSD-73761707", "noise_assessment", "Pulse White Noise Acoustics",
     "PREPARED BY: Pulse White Noise Acoustics Pty Ltd"),
    ("SSD-73761707", "air_quality_report", "Northstar Air Quality",
     "prepared for LCI Consultants by: Northstar Air Quality Pty Ltd"),
    ("SSD-53338465", "noise_assessment", "Arup Australia", "Arup Australia Pty Ltd | ABN 76 625 912 665"),
    ("SSD-53338465", "air_quality_report", "Arup Australia", "Arup Australia Pty Ltd | ABN 76 625 912 665"),
    ("SSD-9741", "noise_assessment", "Arup", "Arup Pty Ltd ABN 18 000 966 165"),
    ("SSD-9741", "air_quality_report", "Arup", "Arup Pty Ltd ABN 18 000 966 165"),
    ("SSD-10467", "noise_assessment", "AECOM", "Prepared by AECOM Australia Pty Ltd"),
    ("SSD-10467", "air_quality_report", "AECOM", "Prepared by AECOM Australia Pty Ltd"),
    ("SSD-63741210", "noise_assessment", "Aurecon", "Document prepared by: Aurecon Australasia Pty Ltd"),
    ("SSD-63741210", "air_quality_report", "Northstar Air Quality",
     "prepared for Aurecon Group Pty Ltd on behalf of NEXTDC Ltd by: Northstar Air Quality Pty Ltd"),
    ("SSD-74069708", "noise_assessment", "SLR Consulting", "Prepared by: SLR Consulting Australia"),
    ("SSD-74069708", "air_quality_report", "SLR Consulting", "Prepared by: SLR Consulting Australia"),
    ("SSD-47320208", "noise_assessment", "Arup Australia", "Arup Australia Pty Ltd | ABN 76 625 912 665"),
    ("SSD-69223466", "noise_assessment", "SLR Consulting", "Prepared by: SLR Consulting Australia"),
    ("SSD-69223466", "air_quality_report", "Northstar Air Quality",
     "prepared for Goodman Property Services (Aust.) Pty Ltd by: Northstar Air Quality Pty Ltd"),
    ("SSD-10330", "noise_assessment", "SLR Consulting", "PREPARED BY SLR Consulting Australia Pty Ltd"),
    ("SSD-10330", "air_quality_report", "SLR Consulting", "PREPARED BY SLR Consulting Australia Pty Ltd"),
    ("SSD-33781208", "noise_assessment", "Pulse White Noise Acoustics",
     "PREPARED BY: Pulse White Noise Acoustics Pty Ltd"),
    ("SSD-33781208", "air_quality_report", "Benbow Environmental",
     "The copyright for this report and accompanying notes is held by Benbow Environmental."),
    ("SSD-24299707", "noise_assessment", "Renzo Tonin & Associates",
     "This Noise and Vibration Report has been prepared by Renzo Tonin & Associates (Renzo Tonin)"),
    ("SSD-24299707", "air_quality_report", "SLR Consulting", "PREPARED BY SLR Consulting Australia Pty Ltd"),
]

NEW_SOURCES = [
    (SRC_PR_DIGICO,
     "DigiCo SYD1 Data Centre Expansion - Peer review of Noise and Vibration Impact Assessment (SSD-69637456)",
     "Renzo Tonin & Associates, for the applicant (NSW Planning Portal)", "2025-09-01",
     "A two-page letter. The applicant's planner, on behalf of HDI SYD1 Property Holdings (DigiCo), engaged "
     "Renzo Tonin & Associates to peer review Pulse White Noise Acoustics' noise and vibration assessment, "
     "over eight revisions; the letter says the review 'did not involve any detailed modelling checks or "
     "remodelling'. RG-075."),
    (SRC_PR_LCW,
     "Acoustic Assessment AirTrunk SYD2 Datacentre, 1 Sirius Rd, Lane Cove West - Peer Review (SSD-9741-Mod-3)",
     "Renzo Tonin & Associates, for the applicant (NSW Planning Portal)", "2023-07-18",
     "A two-page letter. EMKC Cubed Management engaged Renzo Tonin & Associates to review Pulse White Noise "
     "Acoustics' noise impact assessment for the Mod 3 application 'for the AirTrunk SYD2 Datacentre', over "
     "seven reviews; no remodelling. A primary record tying the applicant of record to AirTrunk's SYD2 "
     "(RG-064, a lead on the relationship, not on ownership). RG-075."),
    (SRC_PR_RR4,
     "Independent review for a data centre in accordance with the NSW EPA's Guide for Large Emitters "
     "(Roberts Road Data Centre Mod 4, SSD-10330-Mod-4)",
     "Zephyr Environmental, for the applicant (NSW Planning Portal)", "2026-07-30",
     "The independent expert review of SLR Consulting's greenhouse gas assessment for Roberts Road Mod 4, "
     "engaged by CDC, as section 4.7 of the EPA's Guide for Large Emitters requires. The modification adds "
     "24 diesel generators and 32 chillers and is expected to exceed 25,000 tonnes CO2-e a year of Scope 1 "
     "and 2 emissions. The letter is headed 'RESTRICTED' but the portal publishes it as public. RG-075."),
    (SRC_GHG_ATLAS,
     "Project Atlas - Independent Reviewer Report for a data centre in accordance with the NSW EPA's Guide for "
     "Large Emitters (SSD-101067971)",
     "Zephyr Environmental, for the applicant (NSW Planning Portal)", "2026-03-23",
     "The independent expert review of the Project Atlas greenhouse gas assessment. The assessment 'has been "
     "prepared by LCI on behalf of Goodman Property Services', and the reviewer was 'engaged by LCI Consultants "
     "(LCI), on behalf of Goodman Property Services': the author of the report engaged its reviewer. The reviewer "
     "states no actual or perceived conflict of interest and finds the mitigation strategy 'adequate'. RG-075."),
    (SRC_GHG_RR2,
     "Eastern Creek Data Centre - Independent Reviewer Report for a data centre in accordance with the NSW EPA's "
     "Guide for Large Emitters (Roberts Road Mod 2, SSD-10330-Mod-2)",
     "Zephyr Environmental, for the applicant (NSW Planning Portal)", "2025-11-25",
     "The independent expert review of SLR Consulting's greenhouse gas assessment for Roberts Road Mod 2, "
     "engaged by the planning consultant Urbis on behalf of CDC. It states no actual or perceived conflict of "
     "interest and finds CDC's offset strategy 'satisfactory'. RG-075."),
]


def normalise(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def pack_list() -> list[str]:
    """The packs rebuild_all.py loads, in order, read from its PACKS list."""
    text = open(os.path.join(ROOT, "scripts", "rebuild_all.py"), encoding="utf-8").read()
    block = text[text.index("PACKS = ["): text.index("]\n", text.index("PACKS = ["))]
    return re.findall(r'"(data/packs/[^"]+\.json)"', block)


def prior_notes(gap_id: int) -> str:
    """The note the last earlier pack wrote for a question, so this pass extends it."""
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


def consent_counts() -> dict:
    """Generator-hour caps and diesel caps across the archived consent instruments, computed."""
    hours: dict[str, list[str]] = {}
    diesel: list[str] = []
    for path in sorted(glob.glob(os.path.join(CONSENTS, "*.txt"))):
        name = os.path.basename(path)[:-4]
        text = normalise(open(path, encoding="utf-8", errors="replace").read())
        caps = sorted(set(re.findall(r"exceed (\d+) hours", text)))
        if caps:
            hours[name] = caps
        if "does not exceed 2,000 tonnes" in text:
            diesel.append(name)
    return dict(instruments=len(glob.glob(os.path.join(CONSENTS, "*.txt"))), hours=hours, diesel=diesel)


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
    for label, (fname, quote) in CONSENT_QUOTES.items():
        text = normalise(open(os.path.join(CONSENTS, fname), encoding="utf-8", errors="replace").read())
        if normalise(quote) not in text:
            errors.append(f"consent/{label}: quote not found verbatim in {fname}")
    for case, kind, firm, quote in AUTHORS:
        path = os.path.join(DOCS, f"{case}_{kind}.txt")
        if not os.path.exists(path):
            errors.append(f"{case}_{kind}: report not archived")
        elif normalise(quote) not in normalise(open(path, encoding="utf-8", errors="replace").read()):
            errors.append(f"{case}_{kind}: the firm's name ({firm}) not found as quoted")

    # The counts the notes state, computed from the instruments; a drift refuses the pack.
    counts = consent_counts()
    at_200 = sorted(n for n, c in counts["hours"].items() if c == ["200"])
    lower = {n: c for n, c in counts["hours"].items() if c != ["200"]}
    expect = dict(instruments=20, at_200=15, diesel=13,
                  lower={"glendenning_road_data_centre": ["170"], "project_pluto_data_centre": ["173"],
                         "project_apollo_data_centre_macquarie_park": ["187"]})
    if counts["instruments"] != expect["instruments"]:
        errors.append(f"consents: {counts['instruments']} instruments, the note says {expect['instruments']}")
    if len(at_200) != expect["at_200"]:
        errors.append(f"consents: {len(at_200)} capped at 200 hours, the note says {expect['at_200']}")
    if lower != expect["lower"]:
        errors.append(f"consents: lower caps {lower}, the note says {expect['lower']}")
    if len(counts["diesel"]) != expect["diesel"]:
        errors.append(f"consents: {len(counts['diesel'])} capped at 2,000 tonnes, the note says {expect['diesel']}")
    if errors:
        print("refusing to write the pack:", file=sys.stderr)
        for e in errors:
            print(f"  {e}", file=sys.stderr)
        return 1

    def q(*refs: tuple[str, str]) -> list[dict]:
        grouped: dict[str, list[str]] = {}
        for sid, label in refs:
            quote = CONSENT_QUOTES[label][1] if sid == SRC_CONSENTS else QUOTES[sid][label]
            grouped.setdefault(sid, []).append(quote)
        return [dict(id=sid, quote=" | ".join(v)) for sid, v in grouped.items()]

    sources = []
    for sid, title, publisher, published, notes in NEW_SOURCES:
        meta = json.load(open(os.path.join(RAW, TEXTS[sid].replace(".txt", ".pdf.meta.json")), encoding="utf-8"))
        sources.append(dict(
            id=sid, title=title, publisher=publisher, url=meta["url"], doc_type="primary_planning_portal",
            published=published, credibility="A", accessed=TODAY,
            notes=(notes + f" Read {TODAY} from the NSW Planning Portal ({meta['label']}), SHA-256 "
                   f"{meta['sha256']}, {meta['pages']} pages, text by {meta['extractor']}, archived at "
                   f"data/raw/{TEXTS[sid]} with its manifest; personal contact details are redacted from the "
                   "text and the PDF is not committed.")))

    if AUTHORS:
        lines = []
        for case, kind, firm, _ in AUTHORS:
            meta = json.load(open(os.path.join(DOCS, f"{case}_{kind}.pdf.meta.json"), encoding="utf-8"))
            lines.append(f"{case} {kind.replace('_', ' ')}: {firm} ({meta['attachment_slug']}, SHA-256 "
                         f"{meta['sha256'][:16]}...)")
        sources.append(dict(
            id=SRC_TECH,
            title=("Acoustic and air quality assessments for determined NSW data centre consents "
                   f"(bulk read of {len(AUTHORS)} reports)"),
            publisher="Prepared for the applicants (NSW Planning Portal)",
            url="https://www.planningportal.nsw.gov.au/major-projects",
            doc_type="primary_planning_portal", published=None, credibility="A", accessed=TODAY,
            notes=("One noise or acoustic report and one air quality report per determined data centre "
                   "consent, read from the planning portal on " + TODAY + " for the firm that prepared each, "
                   "taken from the report's own cover or document-control page, not from its filename. "
                   "Each is archived at data/raw/nsw_planning/documents/<case>_<kind>.txt with a manifest "
                   "holding its URL and full SHA-256; personal names in document-control tables are not "
                   "recorded here. " + "; ".join(lines) + ". RG-073.")))

    def gap(gap_id: int, text: str, refs: list[tuple[str, str]], status: str | None = None,
            resolved: bool = False, source_id: str | None = None) -> list[dict]:
        upd = dict(notes=(prior_notes(gap_id) + TAG + " " + text).strip(), as_of_date=TODAY)
        if status:
            upd["status"] = status
        if resolved:
            upd["resolved_date"] = TODAY
        if source_id:
            upd.update(source_id=source_id, fact_status="VERIFIED", confidence="high")
        return [dict(match=dict(id=gap_id), set=upd, add_sources=q(*refs) if refs else [])]

    gaps: list[dict] = []

    # ---- Water -------------------------------------------------------------------------------
    gaps += gap(62, (
        "RESOLVED (negative). The NSW Data Centre Guidelines define the term: 'Recycled water includes that "
        "provided by recycled water networks or on-site water treatment, such as from captured stormwater.' "
        "Read against all 20 archived consent instruments and the modification reports read in batch 7, no "
        "consent or modification cites that definition or relies on it to meet a recycled-water expectation. "
        "Only two assessment reports mention the Guidelines (Glendenning Road and Project Apollo, both after "
        "their release on 17 August 2026); each says 'The Department has considered the Guidelines as a "
        "relevant consideration under section 4.15 of the EP&A Act' and lists the related conditions as "
        "renewable power purchase, retrofit capability, PUE and WUE monitoring through a Sustainability "
        "Management Plan, and amenity; recycled water is not among them. The closest usage predates the "
        "Guidelines: the DigiCo SYD1 consent (December 2025) lists, under 'Recycled water and reuse, through:', "
        "the 'Use of 2x5000L existing rainwater tanks', rainwater counted as recycled water, which is the "
        "reading the later definition allows. The three consents decided since July 2026 (Project Pluto, "
        "Project Apollo, Glendenning Road) instead require a 'review of available water servicing "
        "arrangements, in consultation with the relevant water service provider, to identify any "
        "alternative non-potable or recycled water supply options'. Re-open if a Sustainability Management "
        "Plan approved under one of them relies on the definition."),
        [(SRC_GUIDE, "recycled"), (SRC_CONSENTS, "digico_rain"), (SRC_CONSENTS, "water_review"),
         (SRC_GLEN, "guidelines"), (SRC_APOLLO, "guidelines")],
        status="resolved", resolved=True, source_id=SRC_GUIDE)

    # ---- Generators, diesel and licences ------------------------------------------------------
    hours_note = (
        f"GENERATOR HOURS AND DIESEL, counted by this pack's script across the {counts['instruments']} archived "
        f"consent instruments (18 data centre consents; the Davis Road Mod 1 instrument and the Dicker Data "
        f"warehouse carry no generator cap). {len(at_200)} cap generator operation at 200 hours a year; the "
        "three decided since July 2026 set lower caps: Project Pluto 'exceed 173 hours per year', Project "
        "Apollo 187 and Glendenning Road 170. Project Apollo's cap is the applicant's own figure, not a "
        "tightening: its report says 'Routine generator testing of up to 187 hours per year is required', and "
        "that 'In response to EPA advice' the applicant said 'the generator operating regime has been revised "
        "to remain below 200 hours per year'. 200 hours is the "
        "line in the Guidelines: 'Current regulations allow data centres to use generators for up to 200 hours "
        "a year without being subject to any point source emission limits for oxides of nitrogen'. The EPA's "
        "own reason for the cap is on the record at Macquarie Park: 'To ensure an EPL is not required, the "
        "EPA recommended a condition be imposed restricting the use and/or testing of any back-up generators "
        "installed at the site to a maximum of 200 hours per year.' At 1-5 Khartoum Road the consent "
        "condition is 200 hours while its own mitigation table says 'Total generator testing time is limited "
        f"to 72 hours per year': the condition does not lock in the offer. {len(counts['diesel'])} of the "
        "instruments say diesel storage 'does not exceed 2,000 tonnes', the licensing line for petroleum "
        "storage (RG-008). So on generator hours there is no ratchet below the 200-hour line except in the "
        "three newest consents, and in one of those the cap is exactly the applicant's offer.")
    gaps += gap(61, hours_note,
                [(SRC_GUIDE, "hours"), (SRC_MPDC, "cap"), (SRC_CONSENTS, "pluto_hours"),
                 (SRC_CONSENTS, "apollo_hours"), (SRC_CONSENTS, "glen_hours"), (SRC_CONSENTS, "khartoum_72"),
                 (SRC_CONSENTS, "khartoum_200"), (SRC_CONSENTS, "rr_diesel"), (SRC_APOLLO, "offer"),
                 (SRC_APOLLO, "revised")], status="in_progress")
    gaps += gap(8, (
        "FIRST PASS, from the Department's reports, which record the EPA's advice on each application. The "
        "licences themselves are not yet read. LICENCE REQUIRED, per the reports: 51 Huntingwood Drive "
        "(SSD-41589232: an EPL 'will need to be applied for and issued'); NEXTDC S4 Horsley Park "
        "(SSD-63741210) and Marsden Park (SSD-70889211), each: 'The EPA advised the development would require "
        "an EPL for the quantity of diesel storage on the site above the thresholds of the POEO Act'; and "
        "Roberts Road as modified by Mod 2 ('will require an environment protection licence ... under section "
        "42', 'for Chemical Storage (diesel fuel)'). NOT REQUIRED, per the reports: Roberts "
        "Road as first approved, Kemps Creek, Macquarie Park, Eastern Creek, Talavera Road, Station Road, "
        "Grand Avenue, Davis Road, Project Echidna, 1-5 Khartoum Road, Apollo Place, Project Pluto, DigiCo "
        "SYD1, Project Apollo ('does not appear to require'), Lane Cove West, the Dicker Data warehouse, and "
        "Glendenning Road, where the EPA first 'Noted ... the development would require' a licence and then "
        "accepted the applicant's confirmation that diesel 'would be below 2,000 tonnes'. HOW THE LINE IS "
        "HELD: at Grand Avenue the EPA 'recommended conditions to ensure the development would stay under the "
        "triggers for an EPL'; at Project Pluto, conditions 'to ensure diesel storage and generator testing "
        "remain below POEO Act thresholds'; the NEXTDC S5 EIS states the diesel line as 'the 2,000-tonne "
        "trigger for petroleum products storage for which an EPL would be required'. WHAT FOLLOWS: at 1-5 "
        "Khartoum Road the report records that 'the EPA does not consider itself to be the appropriate "
        "regulatory authority for air emissions associated with the development' because no licence is "
        "required. For most sites there is no licence whose conditions this question could extract; their "
        "generator and air terms are consent conditions (RG-061). BLOCKED on download #28: the EPA's public "
        "register is now an interactive application the crawler cannot read; a person can search it for the "
        "four sites above and save each licence."),
        [(SRC_HUNTINGWOOD, "epl"), (SRC_S4, "epl"), (SRC_MARSDEN, "epl"), (SRC_RR_MOD2, "epl"),
         (SRC_RR_MOD2, "diesel"), (SRC_RR, "no_epl"), (SRC_GLEN, "first"), (SRC_GLEN, "below"),
         (SRC_GRAND, "stay"), (SRC_PLUTO, "below"), (SRC_APOLLO, "appear"), (SRC_DAVIS, "no_epl"),
         (SRC_APOLLO_PL, "no_epl"), (SRC_ECHIDNA, "no_epl"), (SRC_S5, "trigger"), (SRC_KHARTOUM, "authority"),
         (SRC_MPDC, "cap"), (SRC_EC, "no_epl"), (SRC_TALAVERA, "no_epl"), (SRC_STATION, "no_epl"),
         (SRC_KEMPS, "no_epl"), (SRC_DIGICO, "no_epl"), (SRC_LCW, "no_epl"), (SRC_DICKER, "no_epl")],
        status="blocked")

    # ---- Who checks the consultants ------------------------------------------------------------
    gaps += gap(75, (
        "RESOLVED for the documents on the public record. Six of the 63 projects in the attachment index carry "
        "a review document by title: two acoustic peer reviews (DigiCo SYD1; Lane Cove West Mod 3); an acoustic "
        "and an air quality 'review statement' on 51 Huntingwood Drive Mod 1, a withdrawn modification (the "
        "acoustic one answered 401, not public; refusal recorded); and three greenhouse gas reviews (Project Atlas; Roberts Road Mods 2 and 4). "
        "OPENED: at DigiCo SYD1, 'Renzo Tonin & Associates (RTA) was engaged by Patch Planning, on behalf of "
        "HDI SYD1 Property Holdings Pty Limited (DigiCo) to peer review the noise and vibration impact "
        "assessment (NVIA) report undertaken by Pulse White Noise Acoustics (PWNA)', across 'reviews or partial "
        "reviews of eight revisions'. At Lane Cove West Mod 3 the same reviewer 'was engaged by EMKC Cubed "
        "Management (EMKC) to undertake an independent review of the Noise Impact Assessment (NIA) prepared by "
        "Pulse White Noise Acoustics (PWNA)', in 'seven reviews of the NIA'. Both letters say 'The peer review "
        "process did not involve any detailed modelling checks or remodelling by RTA.' At Roberts Road Mod 4, "
        "'Zephyr Environmental Pty Ltd (Zephyr) has been engaged by Canberra Data Centres (CDC) to perform an "
        "independent review' of SLR Consulting's greenhouse gas report ('Revision 05, SLR Consulting, 16 July "
        "2026'); under the EPA's Guide for Large Emitters, above 100,000 tonnes a year 'mitigation assessments "
        "must be verified by an independent expert review'. All three greenhouse reviews are by the same firm, "
        "Zephyr Environmental: Roberts Road Mod 2 ('engaged by Urbis, on behalf of Canberra Data Centres (CDC)', "
        "reviewing SLR's report) and Project Atlas, where 'The Assessment Report has been prepared by LCI on "
        "behalf of Goodman Property Services' and the reviewer 'has been engaged by LCI Consultants (LCI ), on "
        "behalf of Goodman Property Services': there the author of the report engaged its reviewer. The Mod 2 "
        "and Atlas letters each say 'No actual or perceived conflicts of interest have come to my attention, and "
        "I have not been employed by the proponent within the last five years'; the Mod 4 letter, written after "
        "the Mod 2 engagement for the same proponent, carries no such statement. Each review found the work "
        "'adequate' or 'satisfactory'. ANSWER: in every review opened the reviewer is a different firm from the "
        "author, so no firm was found reviewing its own work; every review was engaged by the applicant, its "
        "planner or the report's author, none by the Department; the acoustic reviews checked by comment and "
        "meeting, not by re-running the model. The greenhouse reviews follow the EPA's rule; nothing read "
        "requires the acoustic ones."),
        [(SRC_PR_DIGICO, "engaged"), (SRC_PR_DIGICO, "no_model"), (SRC_PR_DIGICO, "revisions"),
         (SRC_PR_LCW, "engaged"), (SRC_PR_LCW, "no_model"), (SRC_PR_LCW, "revisions"),
         (SRC_PR_RR4, "engaged"), (SRC_PR_RR4, "author"), (SRC_PR_RR4, "mandatory"),
         (SRC_PR_RR4, "satisfactory"), (SRC_GHG_ATLAS, "engaged"), (SRC_GHG_ATLAS, "author"),
         (SRC_GHG_ATLAS, "conflict"), (SRC_GHG_ATLAS, "adequate"), (SRC_GHG_RR2, "engaged"),
         (SRC_GHG_RR2, "author"), (SRC_GHG_RR2, "conflict"), (SRC_GHG_RR2, "satisfactory")],
        status="resolved", resolved=True, source_id=SRC_PR_DIGICO)
    if AUTHORS:
        firms: dict[str, list[str]] = {}
        for case, kind, firm, _ in AUTHORS:
            firms.setdefault(firm, []).append(f"{case} {'noise' if kind.startswith('noise') else 'air'}")
        tally = "; ".join(f"{f}: {len(v)} ({', '.join(v)})" for f, v in
                          sorted(firms.items(), key=lambda kv: (-len(kv[1]), kv[0])))
        gaps += gap(73, (
            f"ACOUSTIC AND AIR QUALITY DONE: {len(AUTHORS)} reports opened, one noise and one air quality "
            "report per determined consent where the portal publishes them, each firm read from the report's own "
            f"cover or document-control page (source {SRC_TECH}). By firm: {tally}. WHERE A CONSULTANCY HOLDS "
            "THE CONSENT (applicants per RG-074), it wrote its own evidence in three of the six: Turner Road "
            "(applicant ARUP Pty Ltd; both reports by Arup Pty Limited), Project Echidna (applicant ARUP Australia; "
            "the noise report by Arup Australia; its air quality report is over the crawler's 120 MB limit) and Davis Road (applicant "
            "Cundall; both reports by Cundall). Lehr's two consents used other firms, each report written for its "
            "own practice, LCI Consultants; Lane Cove West's are by Arup. THE DEPARTMENT'S OWN RECORD can name the client as "
            "the author: its Station Road report lists the 'SSDA Acoustic Assessment Report prepared by LCI "
            "Consultants' (Issue 9), while the issue read here (Issue 8) names Pulse White Noise Acoustics as "
            "author and LCI Consultants as client. Not read: Project Echidna's air quality report, "
            "larger than the crawler's 120 MB limit (recorded; a person can save it). Where an earlier version "
            "of a report answered 401, a later published version was read instead. Still open: the other disciplines (traffic, flooding, heritage, "
            "hazards, greenhouse gas)."),
            [(SRC_STATION, "lci")], status="in_progress")
    gaps += gap(64, (
        "A primary record now ties the applicant of record to AirTrunk's site: the Lane Cove West Mod 3 peer "
        "review says its reviewer 'was engaged by EMKC Cubed Management (EMKC)' to review the noise assessment "
        "'for the AirTrunk SYD2 Datacentre'. That is the relationship, not the ownership. BLOCKED at zero spend: "
        "the landowner's consent letters on Apollo Place and 51 Huntingwood Drive are items 7 and 8 of "
        "GIPA-001, which carries the $30 GIPA fee and is not lodged (author's decision, 2026-11-18); directors "
        "and shareholders need paid extracts, which are not bought (RG-081)."),
        [(SRC_PR_LCW, "engaged")], status="blocked")

    # ---- Zero spend: fee-bearing state requests not lodged -------------------------------------
    for gid, what, paid in (
        (21, "the landowners' consent letters on the Mamre Road application (items 2 to 4)",
         "; directors and shareholders also need a paid ASIC extract"),
        (35, "the landowner's consent letters on Project Duke and Project Mars (items 11 to 13)", ""),
        (37, "Glendenning Road's owner's consent letter (item 1)", "; a paid title search is the other route"),
        (57, "the Davis Road landowner's consent letter and the ASIC certificate for Amazon Corporate Services "
             "(items 5 and 6)", ""),
        (59, "the landowners' consent letters on DCI Poplars and the Eastern Creek expansion (items 9 and 10)", ""),
    ):
        gaps += gap(gid, (
            f"BLOCKED at zero spend: what is left needs {what} of GIPA-001, which carries the $30 GIPA "
            f"application fee and is not lodged, by the author's decision of 2026-11-18{paid}, not bought. The "
            "free routes already tried are in the notes above and the hunt log."), [], status="blocked")
    gaps += gap(58, (
        "BLOCKED at zero spend: the warning letters and the operator's response are restricted on the portal "
        "and are asked for in GIPA-003, which carries the $30 GIPA fee and is not lodged (author's decision, "
        "2026-11-18)."), [], status="blocked")
    gaps += gap(17, (
        "BLOCKED at zero spend: the water agreements are asked for in GIPA-004 ($30), FOI-005 ($34.50), FOI-006 "
        "(two applications) and RTI-001 ($59.60), none lodged by the author's decision of 2026-11-18. Free "
        "substitutes read: the consents' own water conditions (RG-062, resolved today) and Melbourne Water's "
        "public reports (RG-080)."), [], status="blocked")

    # ---- Free Commonwealth requests: waiting on the author's lodgement --------------------------
    for gid, req, agency in ((6, "FOI-001", "the Treasury"), (87, "FOI-002", "Defence"),
                             (89, "FOI-003", "Defence"), (93, "FOI-004", "the ACIC")):
        gaps += gap(gid, (
            f"BLOCKED on {req} to {agency}: drafted, free to lodge (no application fee under the Commonwealth "
            "FOI Act; it asks for any processing charge to be waived, and is narrowed or withdrawn rather than "
            "paid if one is levied). The author lodges it; the reply comes in through a pack."), [],
            status="blocked")

    # ---- Paid searches: deferred, saying so -----------------------------------------------------
    for gid in (36, 50, 52, 81):
        gaps += gap(gid, (
            "DEFERRED under zero spend (author's decision, 2026-11-18): the remaining facts need paid ASIC "
            "extracts, which are not bought. Free substitutes used: ASIC's free register of names, dates and "
            "former names (above). The question stays open, saying why."), [])

    # ---- Proposals to the author: closures this pack does not make -----------------------------
    gaps += gap(76, (
        "PROPOSED TO THE AUTHOR for closing as resolved-negative: two passes (2026-09-18, 2026-11-18) found no "
        "Australian site, application or announcement for TCS or HyperVault; the absence is the finding. Not "
        "closed by this pack."), [])
    gaps += gap(90, (
        "PROPOSED TO THE AUTHOR for closing as resolved-negative: the Commonwealth's Palantir notices are "
        "software, support and data services, none a Pillar II award; defence.gov.au has twice refused the "
        "crawler; nothing read places Palantir or NVIDIA in Pillar II work. Closing records the absence, not "
        "a denial. Not closed by this pack."), [])

    pack = {
        "pack_id": "batch8-open-questions-2026-11",
        "prepared_by": "scripts/curate_batch8.py from data/raw/ (archived and read 2026-11-18)",
        "prepared_on": TODAY,
        "_comment": [
            "Research batch 8, first pass, under the author's zero-spend decision of 2026-11-18.",
            "Resolves RG-062 and RG-075; advances RG-061 and RG-073; RG-008 is blocked on download #28.",
            "Fee-blocked and FOI-waiting questions are set to blocked, naming the request; paid-search",
            "questions stay open, saying so. RG-076 and RG-090 are PROPOSED for closing; this pack closes",
            "neither. Counts in the notes are computed from the consent instruments, and a drift refuses",
            "the pack.",
        ],
        "sources": sources,
        "rows": {"research_gaps": gaps},
    }
    with open(OUT_PACK, "w") as f:
        json.dump(pack, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print(f"batch 8: {len(sources)} sources, {len(gaps)} question updates; "
          f"wrote {os.path.relpath(OUT_PACK, ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
