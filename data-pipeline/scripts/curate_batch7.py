#!/usr/bin/env python3
"""
Research batch 7, first pass (2026-11-18): the open questions the agent can work from free
sources (docs/PUBLICATION-PLAN.md, Part 3, tracks A and R), at the author's direction of
2026-11-18 ("do all the open questions").

What this pass settles, from documents already archived or archived today:
  * RG-105 RESOLVED. Road 1 (SSD-80814238) and 1-5 Khartoum Road (SSD-63235720) are two
    buildings, not one project recorded twice: the Department's SSD-63235720 report calls Road 1
    "a separate data centre development by the Applicant on the site", directly south. Both rows
    stay.
  * RG-044 RESOLVED. Unions NSW asked the inquiry to require local content no less than the
    Renewable Energy Sector Board's; the Guidelines only encourage local content, and none of the
    20 archived consents mentions it.
  * RG-025 Penrith part SETTLED. The executed planning agreement is a scan; OCR of it, checked
    against the page image, shows clause 6.1 keeps the draft's $8,423,505.96 (or that amount
    indexed by CPI, whichever is greater), payable before the first construction certificate.
    The question stays open for the survey (whether any contribution has been paid).
  * RG-088 Westpac now has two reported sources quoting the bank, the threshold the question set:
    ENT_WESTPAC is added, REPORTED.
  * RG-098, RG-102, RG-024, RG-071: the answer is in hand, and a change to a site row would
    follow from it. Those changes are the author's: this pack records the evidence and the
    proposed change in the note and changes no site value.
  * RG-039 BLOCKED on RG-037 (the operator is not established, so there is no website to test).
  * RG-010, RG-051, RG-054, RG-076, RG-090, RG-091, RG-101, RG-103, RG-106: what was tried today,
    what refused, and what the leads are. Search summaries are leads, never facts.

Outputs:
  * data/packs/batch7_open_questions.json

Run:
    python3 scripts/curate_batch7.py
    python3 scripts/load_pack.py data/packs/batch7_open_questions.json --allow-missing-source
"""
from __future__ import annotations

import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(ROOT, "data", "raw")
PACKS_DIR = os.path.join(ROOT, "data", "packs")
OUT_PACK = os.path.join(PACKS_DIR, "batch7_open_questions.json")
THIS_PACK = "data/packs/batch7_open_questions.json"
TODAY = "2026-11-18"
TAG = f" UPDATED {TODAY} (research batch 7):"

# Existing sources this pack cites.
SRC_SYD2 = "SRC_OP_AIRTRUNK_SYD2_SYDNEY_NORTH"
SRC_KHARTOUM = "SRC_SSD63235720_ASSESSMENT"
SRC_ROAD1 = "SRC_SSD80814238_EIS"
SRC_MPDC = "SRC_SSD10467_ASSESSMENT"
SRC_KEMPS = "SRC_SSD10101987_ASSESSMENT"
SRC_INQ22 = "SRC_INQ_T_0522"
SRC_GUIDE = "SRC_NSWGUIDE26"
SRC_VPA = "SRC_PENRITH_VPA"
# New sources, archived today.
SRC_IA_WESTPAC = "SRC_ACS_WESTPAC_NOV26"
SRC_CD_WESTPAC = "SRC_CYBERDAILY_WESTPAC_NOV26"
SRC_CD_PETITION = "SRC_CYBERDAILY_WESTPAC_OCT26"
SRC_MEL2 = "SRC_OP_AIRTRUNK_MEL2"
SRC_NVIDIA_AU = "SRC_NVIDIA_AU_DSX_20260909"
SRC_RR_MOD2 = "SRC_SSD10330_MOD2_ASSESSMENT"
SRC_EC_MOD2 = "SRC_SSD21342738_MOD2_ASSESSMENT"
SRC_LCW_MOD1 = "SRC_SSD9741_MOD1_ASSESSMENT"
SRC_TAL_MOD1 = "SRC_SSD24299707_MOD1_ASSESSMENT"
SRC_RR_MOD4 = "SRC_SSD10330_MOD4_REPORT"
SRC_MODS = "SRC_NSWPORTAL_MODS"
SRC_OCDS = "SRC_AUSTENDER_OCDS_202610"
SRC_FIRMUS_WV = "SRC_OP_FIRMUS_WESLEY_VALE"

TEXTS = {
    SRC_SYD2: "operators/airtrunk/syd2-sydney-north.txt",
    SRC_KHARTOUM: "nsw_planning/documents/SSD-63235720_assessment.txt",
    SRC_ROAD1: "nsw_planning/documents/SSD-80814238_eis.txt",
    SRC_MPDC: "nsw_planning/documents/SSD-10467_assessment.txt",
    SRC_KEMPS: "nsw_planning/documents/SSD-10101987_assessment.txt",
    SRC_INQ22: "nsw_inquiry/text/transcript_2026-05-22.txt",
    SRC_GUIDE: "operators/nswgov/id0073_nsw-data-centre_guidelines.txt",
    SRC_VPA: "councils/penrith/Executed_Voluntary_Planning_Agreement_-_Microsoft_Datacenter.ocr.txt",
    SRC_IA_WESTPAC: "operators/westpac/westpac-reportedly-dumping-palantir-after-public-pressure.txt",
    SRC_CD_WESTPAC: "operators/westpac/14407-westpac-ditches-palantir-following-activist-push.txt",
    SRC_CD_PETITION: "operators/westpac/14313-westpac-silent-on-petition-calling-on-bank-to-cut-ties-with-palantir.txt",
    SRC_MEL2: "operators/airtrunk/mel2-melbourne.txt",
    SRC_NVIDIA_AU: ("operators/nvidia/nvidia-expands-ai-infrastructure-capacity-in-partnership-with-"
                    "australias-data-ce.txt"),
    SRC_RR_MOD2: "nsw_planning/documents/SSD-10330-Mod-2_mod_assessment.txt",
    SRC_EC_MOD2: "nsw_planning/documents/SSD-21342738-Mod-2_mod_assessment.txt",
    SRC_LCW_MOD1: "nsw_planning/documents/SSD-9741-Mod-1_mod_assessment.txt",
    SRC_TAL_MOD1: "nsw_planning/documents/SSD-24299707-Mod-1_mod_assessment.txt",
    SRC_RR_MOD4: "nsw_planning/documents/SSD-10330-Mod-4_mod_report.txt",
    SRC_MODS: "nsw_planning/nodes/eastern-creek-data-centre-mod-2-power-consumption-increase.json",
    SRC_OCDS: "registers/open_contracting/austender-tcs-extract.json",
    SRC_FIRMUS_WV: "operators/firmus/wesley-vale-ai-factory-project.txt",
}

# Every quote is checked verbatim (whitespace normalised) against the archived text before writing.
QUOTES = {
    SRC_SYD2: {
        "greenbox": ("Through close collaboration with AirTrunk and specialist consultants, Greenbox "
                     "Architecture delivered a future‑ready data centre environment that balances "
                     "efficiency, resilience and architectural coherence."),
        "date": "Date: 2019 – ongoing",
        "apollo": ("The Apollo Place data centre has been located adjacent to AirTrunk’s existing "
                   "facility at 1 Sirius Road."),
        "phase5": "The project is Phase 5 of AirTrunk’s investment within the precinct.",
    },
    SRC_KHARTOUM: {
        "separate": ("A State significant development (SSD) application for a separate data centre "
                     "development by the Applicant on the site being the Khartoum Road Data Centre "
                     "Building H (SSD - 80814238) is currently under assessment with the Department ."),
        "south": ("The proposed development is located directly south of the subject development and "
                  "i nvolves a 34.3 MW data centre"),
        "existing": "an existing data centre adjoining to the west at 11 - 17 Khartoum Road (SSD - 10467)",
        "operational": ("including one operational data centre, one under - construction data centre, "
                        "and one data centre currently under assessment"),
    },
    SRC_ROAD1: {
        "single": "Staging The project will be constructed in a single stage.",
        "beside": ("adjacent to the existing double storey concrete carparking structure, where a new "
                   "data centre is proposed under SSD-63235720"),
        "area": "Site Area 8,096m2",
    },
    SRC_MPDC: {
        "lessee": ("The Applicant has been approached by a data centre operator (th e lessee) who is "
                   "seeking to expand its operations within the Sydney region."),
        "operated": "The development would be constructed by the Applicant and operated by the lessee.",
    },
    SRC_KEMPS: {
        "capacity": ("Construction and operation of a data centre including two data storage buildings "
                     "with an operational capacity of 190 Megawatts (MW)"),
        "area": "The site is approximately 14.43 hectares (ha) in area",
        "gfa": "The development has a gross floor area (GFA) of 60,943 m2",
    },
    SRC_INQ22: {
        "proposal": ("Our recommendation is to require local content no less than that set by the "
                     "Renewable Energy Sector Board, both for data centres and the associated renewable "
                     "energy."),
        "opaque": ("I think there's a risk if there's a market mechanism of it being opaque a nd us not "
                   "being able to really track the localcontent that then goes into that renewable "
                   "energy."),
    },
    SRC_GUIDE: {
        "pm16": ("Data centres are encouraged to prioritise use of local content where possible and "
                 "engage with NSW Government on opportunities to support local supply chains."),
    },
    SRC_VPA: {
        "61a": ("The Developer will pay to Council a monetary contribution of $8,423,505.96 or an "
                "amount calculated in accordance with the following formula, whichever is the "
                "greater:"),
        "61b": ("The Monetary Contribution must be paid to Council prior to the issue of the first "
                "Construction Certificate for the Development, or if no such certificate is required, "
                "prior to the commencement of any work comprising the Development."),
    },
    SRC_IA_WESTPAC: {
        "uses": ("The bank uses a Palantir platform in its cybersecurity and regulatory compliance work, "
                 "but the US firm \"does not have access to Westpac customer data\", the spokesperson "
                 "told Information Age ."),
        "neither": ("A spokesperson for Westpac would not confirm or deny the bank had decided to not "
                    "renew its contract with Palantir, when contacted for comment."),
        "date": "By Tom Williams on Nov 05 2026",
    },
    SRC_CD_WESTPAC: {
        "uses": ("Westpac currently uses Palantir software in its financial markets compliance and cyber "
                 "security; however, in a statement to media, a spokesman for the bank confirmed that "
                 "customer data was not accessible to Palantir."),
        "ends": "Westpac has said it will not renew its contract with Palantir.",
        "date": "Thu, 05 Nov 2026",
    },
    SRC_CD_PETITION: {
        "date": "Fri, 16 Oct 2026",
    },
    SRC_MEL2: {
        "location": "Strategically located in Melbourne’s North-West",
        "capacity": "A hyperscale campus with multiple diverse buildings and a total capacity of 354+MW",
        "size": ("Set on 8.070 ha with 45,578sqm of gross floor area and up to 32 technical data halls "
                 "spanning 42,240m 2"),
    },
    SRC_NVIDIA_AU: {
        "partners": ("NVIDIA is collaborating with Australian NVIDIA Cloud Partners and AI infrastructure "
                     "partners including Firmus, Sharon AI, IREN, ResetData, Megaport, CDC, NEXTDC and "
                     "AirTrunk to expand land, power and shell capacity designed to host multiple "
                     "generations of NVIDIA DSX compute infrastructure."),
        "target": ("Firmus, Sharon AI, IREN, Megaport, ResetData, CDC, NEXTDC and AirTrunk to Deliver Up "
                   "to 2-Gigawatt Buildout by 2027"),
        "date": "September 9, 2026",
    },
    SRC_EC_MOD2: {
        "power": ("The modification seeks to improve operational efficiency through an increase in the "
                  "power consumption of the development from 32 MW to 63 MW."),
        "before": ("27 x 2.65 MW generators • Up to 545,000 litres (L) of additional fuel storage"),
        "after": "52 x 1.8 MW generators • Up to 782,000 L of additional fuel storage",
    },
    SRC_MODS: {
        "ec_desc": ("The modification seeks approval for an increase in the overall power consumption of "
                    "the development (to 70.2 megawatts)"),
    },
    SRC_RR_MOD2: {
        "gens": "the installation of 24 additional generators and the relocation of four approved units",
        "diesel": ("Diesel fuel storage capacity 1,914,000 litres ( 1,627 tonnes ) within the footprint "
                   "of the SSD 2,403,600 litres ( 2, 043 tonnes ) within the footprint of the SSD"),
    },
    SRC_RR_MOD4: {
        "proposal": ("Modify the total number of back -up diesel generators approved under SSD -10330 "
                     "from 72 generators to 96 generators."),
        "history": ("Modification of the total number of back -up, diesel generators approved under SSD "
                    "-10330 from 48 generators to 72 generators."),
    },
    SRC_LCW_MOD1: {
        "tanks": ("relocation of 80 diesel fuel storage tanks from t he external plant platforms to 16 "
                  "steel tanks located internally on Level 1, with a total storage capacity of 1,952 "
                  "kilolitres (kL)"),
        "gens": "replacement of 80 MV generators with 116 LV generators",
    },
    SRC_TAL_MOD1: {
        "capacity": ("an increase in capacity from 38 megawatts (MW) to 47 MW including associated "
                     "increases in plant and equipment."),
        "gens": ("The proposed modification application includes an additional four diesel generators "
                 "on site to the previously approved."),
    },
    SRC_FIRMUS_WV: {
        "site": ("Firmus plans to build a new AI Factory project at 226 Mill Road, Wesley Vale — on part of "
                 "the former Wesley Vale Pulp Mill landholding"),
        "stages": ("The Wesley Vale site is being delivered in two stages: an initial stage of approximately "
                   "26 MW, growing to maximum approximately 52 MW of capacity (23 MW critical IT load, "
                   "growing to maximum of approximately 46 WM)."),
        "generators": "The facility will have 40 backup generators, but they are not used for everyday power.",
        "water": "Average annual water used for cooling the facility — sourced from on-site rainwater.",
    },
    SRC_OCDS: {
        "rba1": "Provision of and Implementation of a Core Banking Solution",
        "rba2": ("RFP for provision of System Integration for IT infrastructure and Continuing Managed "
                 "Services"),
        "rba3": "Professional services for cloud build capability",
        "rba4": "CoreMod System Integrator for Application Migrations",
    },
}

NEW_SOURCES = [
    (SRC_IA_WESTPAC, "Westpac reportedly dumping Palantir after public pressure (Information Age, ACS, 5 November 2026)",
     "Australian Computer Society, Information Age", "2026-11-05", "news", "B",
     "Quotes a Westpac spokesperson: the bank uses a Palantir platform in cybersecurity and regulatory "
     "compliance work, Palantir 'does not have access to Westpac customer data', and the spokesperson "
     "would neither confirm nor deny non-renewal. Reports, citing Capital Brief, a seven-figure contract "
     "expected to expire without renewal within 18 months."),
    (SRC_CD_WESTPAC, "Westpac ditches Palantir following activist push (Cyber Daily, 5 November 2026)",
     "Cyber Daily (Momentum Media)", "2026-11-05", "news", "B",
     "Says Westpac 'has said it will not renew its contract with Palantir', that Westpac uses Palantir "
     "software in financial markets compliance and cyber security, and that a bank spokesman confirmed "
     "customer data was not accessible to Palantir. Its account of non-renewal conflicts with Information "
     "Age's, where the spokesperson would neither confirm nor deny it; both are recorded."),
    (SRC_CD_PETITION, "Westpac silent on petition calling on bank to cut ties with Palantir (Cyber Daily, 16 October 2026)",
     "Cyber Daily (Momentum Media)", "2026-10-16", "news", "B",
     "Earlier report of the campaign against Westpac's Palantir contract. Archived for the sequence; no "
     "value rests on it alone."),
    (SRC_MEL2, "MEL2 Melbourne (AirTrunk facility page)", "AirTrunk", None, "primary_company", "A",
     "The operator's own page: 'Strategically located in Melbourne's North-West'; 'a total capacity of "
     "354+MW' (a lower bound, not stored as a value); 'Set on 8.070 ha with 45,578sqm of gross floor "
     "area and up to 32 technical data halls'. No street address, suburb or status is given."),
    (SRC_FIRMUS_WV, "Wesley Vale AI Factory Project (Firmus project page)", "Firmus", None, "primary_company", "A",
     "The developer's own project page: 226 Mill Road, Wesley Vale, on part of the former pulp mill "
     "landholding; two stages, about 26 MW initially to about 52 MW maximum, with critical IT load of "
     "23 MW growing to 'approximately 46 WM' (sic); 40 backup generators; 448 kL a year of cooling water "
     "from on-site rainwater; links its development application. No status beyond the application."),
    (SRC_NVIDIA_AU, "NVIDIA Expands AI Infrastructure Capacity in Partnership With Australia's Data Center Ecosystem (NVIDIA Newsroom, 9 September 2026)",
     "NVIDIA", "2026-09-09", "primary_company", "A",
     "Names eight Australian partners (Firmus, Sharon AI, IREN, Megaport, ResetData, CDC, NEXTDC, "
     "AirTrunk) for 'Up to 2-Gigawatt Buildout by 2027' of NVIDIA DSX AI factories. Names no site, "
     "address or capacity per site."),
]


MOD_DOCS = [
    (SRC_RR_MOD2, "Modification 2 of Roberts Road Data Centre (SSD-10330-Mod-2) - Assessment Report",
     "NSW Department of Planning, Housing and Infrastructure", "2026-03-06"),
    (SRC_EC_MOD2, "Eastern Creek Data Centre Expansion (SSD-21342738-Mod-2) - Assessment Report",
     "NSW Department of Planning, Housing and Infrastructure", "2026-08-05"),
    (SRC_LCW_MOD1, "Lane Cove West Data Centre (SSD-9741-Mod-1) - Assessment Report",
     "NSW Department of Planning, Industry and Environment", "2020-04-14"),
    (SRC_TAL_MOD1, "Talavera Road Data Centre Campus Expansion (SSD-24299707-Mod-1) - Assessment Report",
     "NSW Department of Planning, Housing and Infrastructure", "2024-12-19"),
    (SRC_RR_MOD4, "Modification Report - Roberts Road Data Centre (SSD-10330 Mod 4)",
     "Prepared for the applicant (NSW Planning Portal)", None),
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


def manifest_url(rel_txt: str) -> str:
    base = os.path.join(RAW, rel_txt)
    for ext in (".html.meta.json", ".pdf.meta.json"):
        meta = re.sub(r"\.(ocr\.)?txt$", "", base) + ext
        if os.path.exists(meta):
            return json.load(open(meta, encoding="utf-8"))["url"]
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
        for label, q in quotes.items():
            if sid in texts and normalise(q) not in texts[sid]:
                errors.append(f"{sid}/{label}: quote not found verbatim in the archive")
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
        sources.append(dict(id=sid, title=title, publisher=publisher, url=manifest_url(TEXTS[sid]),
                            doc_type=doc_type, published=published, credibility=cred, accessed=TODAY,
                            notes=notes + f" ARCHIVED {TODAY} at data/raw/{os.path.dirname(TEXTS[sid])}/ "
                                          "with a SHA-256 manifest."))

    for sid, title, publisher, published in MOD_DOCS:
        meta = json.load(open(os.path.join(RAW, TEXTS[sid].replace(".txt", ".pdf.meta.json")),
                              encoding="utf-8"))
        sources.append(dict(
            id=sid, title=title, publisher=publisher, url=meta["url"], doc_type="primary_planning_portal",
            published=published, credibility="A", accessed=TODAY,
            notes=(f"Read {TODAY} from the NSW Planning Portal ({meta['label']}), SHA-256 {meta['sha256']}, "
                   f"{meta['pages']} pages, text by {meta['extractor']}, archived at "
                   f"data/raw/{TEXTS[sid].replace('.txt', '')}.txt with its manifest; the PDF is not "
                   "committed (re-fetch it from the manifest's url and check the hash). RG-045.")))

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
    gaps += gap(105, (
        "RESOLVED: two buildings, not one project recorded twice. The Department's assessment report "
        "for SSD-63235720 (March 2026) says 'A State significant development (SSD) application for a "
        "separate data centre development by the Applicant on the site being the Khartoum Road Data "
        "Centre Building H (SSD-80814238) is currently under assessment', 'located directly south of "
        "the subject development' at 34.3 MW. The Road 1 EIS gives its own 8,096 m2 site, 'adjacent to "
        "the existing double storey concrete carparking structure, where a new data centre is proposed "
        "under SSD-63235720', built 'in a single stage'. Both rows stay, with their own figures; they "
        "may be counted as separate sites. The shared portal address remains, and Road 1's EIS calls its "
        "address 'Part 1-5 Khartoum Road'."),
        [(SRC_KHARTOUM, "separate"), (SRC_KHARTOUM, "south"), (SRC_ROAD1, "beside"), (SRC_ROAD1, "area"),
         (SRC_ROAD1, "single")], status="resolved", resolved=True, source_id=SRC_KHARTOUM)
    gaps += gap(44, (
        "RESOLVED. The proposal, in the corrected transcript of 22 May 2026, from Unions NSW's research "
        "and policy officer (by role): 'Our recommendation is to require local content no less than "
        "that set by the Renewable Energy Sector Board, both for data centres and the associated "
        "renewable energy', and, of a market-based renewable funding model, 'a risk ... of it being "
        "opaque' so local content could not be tracked. Assessed against what was adopted: the NSW Data "
        "Centre Guidelines (August 2026), performance measure 16, say only that data centres 'are "
        "encouraged to prioritise use of local content where possible'; apprenticeship targets appear "
        "as things developers 'could' adopt with unions. None of the 20 archived consent instruments "
        "mentions local content. So the proposal was not adopted as a requirement, in the guidelines or "
        "in any consent read. Whether a market mechanism would be opaque is a prediction the record "
        "cannot test."),
        [(SRC_INQ22, "proposal"), (SRC_INQ22, "opaque"), (SRC_GUIDE, "pm16")],
        status="resolved", resolved=True, source_id=SRC_INQ22)
    gaps += gap(25, (
        "PENRITH PART SETTLED (download #12 needed no download: the scan was re-fetched, its SHA-256 "
        "matched the archive, and it was read by OCR and checked against the page image). Clause 6.1(a) "
        "of the EXECUTED agreement keeps the draft's figure: 'The Developer will pay to Council a "
        "monetary contribution of $8,423,505.96 or an amount calculated in accordance with the "
        "following formula, whichever is the greater' (the formula indexes it by CPI), and 6.1(b) "
        "makes it payable 'prior to the issue of the first Construction Certificate'. STILL OPEN: "
        "whether any contribution in the survey has been paid, and contributions on council-determined "
        "consents."),
        [(SRC_VPA, "61a"), (SRC_VPA, "61b")], status="in_progress")
    gaps += gap(88, (
        "WESTPAC: the threshold this question set (a second reported source) is met. Two outlets "
        "quote the bank on 5 November 2026. Information Age: 'The bank uses a Palantir platform in its "
        "cybersecurity and regulatory compliance work, but the US firm \"does not have access to "
        "Westpac customer data\"', and the spokesperson 'would not confirm or deny' non-renewal. Cyber "
        "Daily: 'Westpac currently uses Palantir software in its financial markets compliance and "
        "cyber security' and 'Westpac has said it will not renew its contract'. ENT_WESTPAC is added "
        "(REPORTED). Whether Westpac will renew is disputed between the two reports, and recorded as "
        "such. The contract's value ('a seven-figure sum', via Capital Brief) is not stored."),
        [(SRC_IA_WESTPAC, "uses"), (SRC_IA_WESTPAC, "neither"), (SRC_CD_WESTPAC, "uses"),
         (SRC_CD_WESTPAC, "ends")], status="in_progress")
    gaps += gap(98, (
        "ANSWERED FROM THE OPERATOR'S OWN PAGE; THE RECORD CHANGE IS THE AUTHOR'S. AirTrunk's SYD2 page "
        "credits Greenbox Architecture, SSD-9741's applicant, with delivering SYD2 'in collaboration "
        "with AirTrunk', dates it '2019 - ongoing' (SSD-9741 was determined on 15 November 2019, and its "
        "report described a client with 'two data centres in Melbourne and western Sydney'), places it "
        "at 1 Sirius Road and links to the planning portal; and says the Apollo Place data centre "
        "(SSD-67407231) 'has been located adjacent to AirTrunk's existing facility at 1 Sirius Road' "
        "and 'is Phase 5 of AirTrunk's investment within the precinct'. PROPOSED for the author: (1) "
        "SITE_LANE_COVE_WEST is the consent for the facility SITE_AIRTRUNK_SYD2 records, so the two are "
        "one site, as RG-084 found for Macquarie Park; (2) SITE_APOLLO_PLACE's operator is AirTrunk, "
        "REPORTED on the operator's own statement. Neither change is made by this pack."),
        [(SRC_SYD2, "greenbox"), (SRC_SYD2, "date"), (SRC_SYD2, "apollo"), (SRC_SYD2, "phase5")],
        status="in_progress")
    gaps += gap(102, (
        "CONSTRUCTION ANSWERED, END USER NOT. The Department's March 2026 report on the neighbouring "
        "SSD-63235720 describes 'an existing data centre adjoining to the west at 11-17 Khartoum Road "
        "(SSD-10467)' and lists, among adjoining sites, 'one operational data centre, one under-"
        "construction data centre, and one data centre currently under assessment'. So SSD-10467 was "
        "built and operating by March 2026. Its own 2021 report says only that 'The Applicant has been "
        "approached by a data centre operator (the lessee)' who would operate it: one of the nine "
        "unnamed operators (RG-055). PROPOSED for the author: SITE_MACQUARIE_PARK_DC status `approved` "
        "-> `operational`, REPORTED on the Department's description. Not made by this pack."),
        [(SRC_KHARTOUM, "existing"), (SRC_KHARTOUM, "operational"), (SRC_MPDC, "lessee"),
         (SRC_MPDC, "operated")], status="in_progress")
    gaps += gap(24, (
        "PRIMARY SOURCE READ: the Department's assessment report for SSD-10101987 (July 2023) confirms "
        "'The site is approximately 14.43 hectares (ha) in area' and 'a gross floor area (GFA) of "
        "60,943 m2', matching the row. But its capacity is 'two data storage buildings with an "
        "operational capacity of 190 Megawatts (MW)': the measure is not labelled IT load, and the row "
        "stores 190 in it_capacity_mw. That is the mislabelling RG-099 removed elsewhere. PROPOSED for "
        "the author: clear it_capacity_mw on SITE_MSFT_KEMPS (no column holds an unlabelled figure; "
        "the passage is quoted), and cite the report for the area and GFA. Not made by this pack. "
        "Whether the campus is operating, and at what IT load, still needs Microsoft's own statement."),
        [(SRC_KEMPS, "capacity"), (SRC_KEMPS, "area"), (SRC_KEMPS, "gfa")], status="in_progress")
    gaps += gap(71, (
        "AirTrunk's own MEL2 page archived: 'Strategically located in Melbourne's North-West', 'a total "
        "capacity of 354+MW' (a lower bound, so no capacity value), 'Set on 8.070 ha with 45,578sqm of "
        "gross floor area and up to 32 technical data halls'. It gives no address, suburb or status, so "
        "no row is invented: sites.status has no 'unknown'. Directory listings and a trade photo "
        "caption say Tullamarine; those are leads, not records. PROPOSED for the author: a row "
        "SITE_AIRTRUNK_MEL2 (VIC, unmapped) only if the author accepts a status reading."),
        [(SRC_MEL2, "location"), (SRC_MEL2, "capacity"), (SRC_MEL2, "size")], status="in_progress")
    gaps += gap(39, (
        "BLOCKED on RG-037. The test needs the operator's website, and the operator of Glendenning Road "
        "is not established; the applicant has no website. Unblocks when RG-037 names the operator or "
        "operation begins."), [], status="blocked")
    gaps += gap(91, (
        "NVIDIA's own release of 9 September 2026 names eight Australian partners (Firmus, Sharon AI, "
        "IREN, Megaport, ResetData, CDC, NEXTDC, AirTrunk) for 'Up to 2-Gigawatt Buildout by 2027' of "
        "DSX AI factories, and names no site. Mapping onto the register needs each partner's own site "
        "statement. Firmus's 'Project Southgate' is reported in Tasmania, Victoria, NSW, WA and the ACT "
        "(leads)."), [(SRC_NVIDIA_AU, "partners"), (SRC_NVIDIA_AU, "target")], status="in_progress")
    gaps += gap(76, (
        "Searched: TCS's own releases on HyperVault describe Indian campuses (Telangana) and a TPG "
        "investment; no Australian site, application or announcement was found. The absence is the "
        "working finding. Proposed to the author for closing as resolved-negative."), [])
    gaps += gap(90, (
        "Tried again: defence.gov.au reset the connection on the Pillar II news page (recorded). Search "
        "summaries name Pillar II awards to BAE Systems Australia, L3Harris and Mission Systems, not "
        "Palantir or NVIDIA (leads). Still unevidenced, still not asserted."), [])
    gaps += gap(54, (
        "Tried: statedevelopment.qld.gov.au's list of prescribed projects refuses the robots check "
        "(recorded in data/raw/qld_western_downs/qld_prescribed/refused.json). Search summaries found no "
        "declaration for the Western Downs Digital Park (a lead, not a record). Needs a person to read "
        "the list (DOWNLOADS.md)."), [])
    gaps += gap(10, (
        "LEAD (not a record): Gingerah Energy's 'Project Meridien', an off-grid data centre of up to "
        "1 GW in the Kimberley near Broome, reported as referred under the EPBC Act in October 2026. "
        "energy-storage.news and DatacenterDynamics refused the crawler (recorded). The EPBC referral "
        "on the federal public portal is the primary record to read (DOWNLOADS.md)."), [])
    gaps += gap(51, (
        "LEAD (not a record): the reported ten-storey proposal is at Swanbank, about 6 km west of "
        "Ipswich, by Northern Concept Swanb Pty Ltd, reportedly code-assessable, with Ipswich City "
        "Council asking for more information. DatacenterDynamics and PlanningAlerts refused the crawler "
        "(recorded). Ipswich City Council's development application record is the primary source "
        "(DOWNLOADS.md)."), [])
    gaps += gap(101, (
        "Cloud Carrier's site still refuses the robots check (HTTP 403 on robots.txt). LEAD (not a "
        "record): directories place DB1 at Moss Vale NSW. The NSW Planning Portal or Wingecarribee "
        "Council's records would place it; wsc.nsw.gov.au refused (HTTP 403)."), [])
    gaps += gap(103, (
        "DigiCo's site now answers its robots check (open), but every location page returned HTTP 403 "
        "to the crawler (recorded in data/raw/operators/digico/refused.json). Its sitemap lists "
        "location pages for ADL1, ADL2, SYD1, BNE, BNE1, BNE2, BNE3 and TSV1. ADL1's and BNE2's "
        "addresses need a person to read those pages (DOWNLOADS.md)."), [])
    gaps += gap(106, (
        "DigiCo's location pages for TSV1, ADL2, BNE1 and BNE (and a separate BNE3 page) exist but "
        "refused the crawler (HTTP 403). LEADS (not records): directories give TSV1 as iseek's North "
        "Queensland Regional Data Centre at Garbutt, Townsville; BNE3 at Woolloongabba; BNE1 at "
        "Brisbane Airport's Export Park. The DigiCo pages would settle them (DOWNLOADS.md)."), [])

    gaps += gap(45, (
        "RESOLVED from the Department's assessment reports (and, for Mod 4, the applicant's "
        "modification report), all read today. EASTERN CREEK Mod 2 (approved 5 August 2026): power "
        "consumption 'from 32 MW to 63 MW'; back-up generators from '27 x 2.65 MW' to '52 x 1.8 MW'; "
        "additional fuel storage from 'Up to 545,000 litres' to 'Up to 782,000 L'. The portal's own "
        "one-line description says 'to 70.2 megawatts'; the report's 63 MW is the assessed figure and "
        "the conflict is recorded, not resolved. ROBERTS ROAD Mod 2 (approved 6 March 2026): 'the "
        "installation of 24 additional generators and the relocation of four approved units' (48 to 72 "
        "under SSD-10330, per the Mod 4 report); diesel storage from 1,914,000 litres (1,627 t) to "
        "2,403,600 litres (2,043 t) within the SSD footprint. ROBERTS ROAD Mod 4 (NOT determined; the "
        "applicant's proposal): generators 'from 72 generators to 96 generators'. LANE COVE WEST Mod 1 "
        "(approved 14 April 2020): 'replacement of 80 MV generators with 116 LV generators', and 80 "
        "external diesel tanks relocated to 16 internal tanks 'with a total storage capacity of 1,952 "
        "kilolitres'. TALAVERA ROAD Mod 1 (approved 19 December 2024): 'an increase in capacity from 38 "
        "megawatts (MW) to 47 MW', and 'an additional four diesel generators'. No site capacity column "
        "is changed: the assessed figures are total power consumption, quoted here and on the "
        "modification rows."),
        [(SRC_EC_MOD2, "power"), (SRC_EC_MOD2, "before"), (SRC_EC_MOD2, "after"), (SRC_MODS, "ec_desc"),
         (SRC_RR_MOD2, "gens"), (SRC_RR_MOD2, "diesel"), (SRC_RR_MOD4, "proposal"), (SRC_RR_MOD4, "history"),
         (SRC_LCW_MOD1, "gens"), (SRC_LCW_MOD1, "tanks"), (SRC_TAL_MOD1, "capacity"), (SRC_TAL_MOD1, "gens")],
        status="resolved", resolved=True, source_id=SRC_EC_MOD2)
    gaps += gap(34, (
        "The quantum RG-034 left open is answered by RG-045 from the five modification reports, read "
        "today: Eastern Creek 32 MW to 63 MW, Roberts Road 48 to 72 generators (96 proposed), Lane Cove "
        "West 116 smaller generators and 1,952 kL of internal fuel storage, Talavera Road 38 MW to 47 "
        "MW. Local council development applications remain out of scope."), [(SRC_TAL_MOD1, "capacity")])
    gaps += gap(72, (
        "COMMONWEALTH PART SETTLED from the portal of record's data: the same AusTender feed file read "
        "in October (re-fetched today; SHA-256 matched) holds 7 notices whose supplier is Tata "
        "Consultancy Services, $41,416,192.60 at their latest values: the Reserve Bank of Australia "
        "four (a core banking solution, $13,600,000; IT infrastructure system integration and managed "
        "services, $10,285,017.60; cloud build capability, $1,976,040; 'CoreMod' application "
        "migrations, $14,021,150), Defence one (industry benchmarking, $1,087,625), Finance one "
        "(Digital Marketplace panel, $311,080), Prime Minister and Cabinet one (ICT contractor "
        "services, $135,280). Extract, redacted of contact points, at data/raw/registers/"
        "open_contracting/austender-tcs-extract.json. STILL OPEN: the NSW records, whose portal of "
        "record is buy.nsw, which refused the crawler (download #11)."),
        [(SRC_OCDS, "rba1"), (SRC_OCDS, "rba2"), (SRC_OCDS, "rba3"), (SRC_OCDS, "rba4")], status="in_progress")
    gaps += gap(83, (
        "NARROWED: neither the 'Office 365 Environment Setup for MoG GSS' award nor any OneStream "
        "award is in the Commonwealth's AusTender feed (searched today across every record), so none is "
        "a Commonwealth notice. That leaves the NSW portal of record, buy.nsw, as GovMarket's "
        "attribution says; buy.nsw refused the crawler, so the attribution stays at low confidence "
        "until a person reads it (download #11)."), [], status="in_progress")
    gaps += gap(27, (
        "WESLEY VALE placed from the developer's own page (Firmus, archived today): 'a new AI Factory "
        "project at 226 Mill Road, Wesley Vale', in two stages, 'an initial stage of approximately 26 MW, "
        "growing to maximum approximately 52 MW of capacity (23 MW critical IT load, growing to maximum of "
        "approximately 46 WM)' (sic), with 40 backup generators and cooling water from on-site rainwater. "
        "Leads (not records): trade reports of a Latrobe Council application and a December 2026 deadline "
        "for a major project proposal. PROPOSED for the author: a row SITE_FIRMUS_WESLEY_VALE (TAS, "
        "status `lodged` on the page's linked development application), with the stated maxima quoted "
        "rather than stored until the council record is read. The other proposals this question names "
        "are not yet worked."),
        [(SRC_FIRMUS_WV, "site"), (SRC_FIRMUS_WV, "stages"), (SRC_FIRMUS_WV, "generators")], status="in_progress")
    gaps += gap(42, (
        "Tried: IPART's own submission to the NSW inquiry and its review page for a data centre water "
        "pricing framework; ipart.nsw.gov.au closed the connection without answering (recorded here, "
        "not worked around). LEADS (not records): search summaries say IPART's submission reports Sydney "
        "Water's estimate of data centre water needs of up to 250 ML a day by 2035, that IPART made no "
        "allowance for data centres in its 2025 Sydney Water determination, and that the Government has "
        "asked IPART to review water pricing for data centres. Needs a person to download the "
        "submission (DOWNLOADS.md)."), [])
    gaps += gap(18, (
        "Searched: no record found of any Australian data centre registered with AEMO to provide "
        "frequency control ancillary services; demand-response aggregators report registrations without "
        "naming sites (leads). AEMO's registration lists are the primary record to check next."), [])
    gaps += gap(1, (
        "PROPOSED FOR CLOSING (wont_fix, author's decision): computing distances to cable landings is "
        "analysis the v1 rule against GIS overlays leaves for later (docs/PUBLICATION-PLAN.md, Part 3)."), [])
    gaps += gap(82, (
        "PROPOSED FOR CLOSING (wont_fix, author's decision): a schema change, not a research question; "
        "it moves to the engineering backlog. consultancy_profile.firm_type remains the workaround."), [])
    mods = [
        dict(match=dict(mod_case="SSD-21342738-Mod-2"), set={},
             add_sources=q((SRC_EC_MOD2, "power"), (SRC_EC_MOD2, "before"), (SRC_EC_MOD2, "after"))),
        dict(match=dict(mod_case="SSD-10330-Mod-2"), set={},
             add_sources=q((SRC_RR_MOD2, "gens"), (SRC_RR_MOD2, "diesel"))),
        dict(match=dict(mod_case="SSD-10330-Mod-4"), set={}, add_sources=q((SRC_RR_MOD4, "proposal"))),
        dict(match=dict(mod_case="SSD-9741-Mod-1"), set={},
             add_sources=q((SRC_LCW_MOD1, "gens"), (SRC_LCW_MOD1, "tanks"))),
        dict(match=dict(mod_case="SSD-24299707-Mod-1"), set={},
             add_sources=q((SRC_TAL_MOD1, "capacity"), (SRC_TAL_MOD1, "gens"))),
    ]

    entities = [
        dict(id="ENT_WESTPAC", name="Westpac", legal_name="Westpac Banking Corporation",
             entity_type="other", domicile="Australia", hq_country="AU", asx_ticker="WBC",
             website="westpac.com.au",
             notes=("Bank. Palantir customer, REPORTED: on 5 November 2026 two outlets quoted the bank "
                    "saying it uses Palantir software in compliance and cyber security work and that "
                    "Palantir cannot access customer data. Whether it will renew is disputed between "
                    "the reports (RG-088). Entity type 'other': the vocabulary has no bank type."),
             fact_status="REPORTED", source_id=SRC_IA_WESTPAC, confidence="medium", as_of_date=TODAY),
        dict(match=dict(id="ENT_WESTPAC"), set={},
             add_sources=q((SRC_IA_WESTPAC, "uses"), (SRC_CD_WESTPAC, "uses"), (SRC_CD_WESTPAC, "ends"))),
    ]

    pack = {
        "pack_id": "batch7-open-questions-2026-11",
        "prepared_by": "scripts/curate_batch7.py from data/raw/ (archived and read 2026-11-18)",
        "prepared_on": TODAY,
        "_comment": [
            "Research batch 7, first pass, at the author's direction to work every open question.",
            "Resolves RG-105 and RG-044; settles RG-025's Penrith part; adds ENT_WESTPAC (RG-088).",
            "RG-098, RG-102, RG-024 and RG-071 carry PROPOSED site changes for the author; this pack",
            "changes no site value. RG-039 is blocked on RG-037. Refusals are recorded, not worked",
            "around; search summaries are leads, never values.",
        ],
        "sources": sources,
        "rows": {"entities": entities, "research_gaps": gaps, "modifications": mods},
    }
    with open(OUT_PACK, "w") as f:
        json.dump(pack, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print(f"batch 7: {len(sources)} sources, {len(gaps)} questions updated, {len(mods)} modifications "
          "quoted, ENT_WESTPAC added; "
          f"wrote {os.path.relpath(OUT_PACK, ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
