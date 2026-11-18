#!/usr/bin/env python3
"""
Research batch 8, second pass (2026-11-18): the questions left for free sources after the first pass
(docs/PUBLICATION-PLAN.md, "Batch 8, first pass"), under the author's zero-spend decision.

What this pass settles, from documents archived today:
  * RG-034, modification half: all 17 modification records on the NSW data centre files are now read
    (five in batch 7, eleven today; the withdrawn 51 Huntingwood Mod 1 is restricted). Three changes
    the record had typed as minor add generators or diesel: Lane Cove West Mod 4 (diesel 1,651 t to
    1,966.9 t, "below the storage limit of 2,000 t"), Lanceley Place Mod 2 (30 to 42 generators) and
    Lane Cove West Mod 3 (116 to 121). Their reclassification is PROPOSED to the author.
  * RG-019 RESOLVED. Transgrid's System Strength Project puts two synchronous condensers at the Kemps
    Creek 500 kV substation, energised from early 2028; none serves a data centre corridor today.
  * RG-018, RG-043: Transgrid's own page on data centres, "more than 10 GW" of enquiries within 12 km
    of Sydney West, capacity "largely exhausted", large users to "play their role" in system strength.
    AEMO's registration list refused the crawler (download #31).
  * RG-100: the October 2024 Mandala report, in the copy AirTrunk publishes, states the 1,350 MW and
    3,100 MW figures; the two metrics are re-sourced to it from the second-hand article.
  * RG-068, RG-080: the free substitutes read and found silent; both set to `blocked` on their
    unlodged requests.
  * RG-007, RG-027, RG-063, RG-069: the free primary record refused; each becomes a download.
  * RG-013 (the AWS and Google remainder) and RG-102 (the end user) are PROPOSED to the author as not
    retrievable at zero spend. This pack closes neither.

Outputs:
  * data/packs/batch8b_open_questions.json

Run:
    python3 scripts/curate_batch8b.py
    python3 scripts/load_pack.py data/packs/batch8b_open_questions.json --allow-missing-source
"""
from __future__ import annotations

import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(ROOT, "data", "raw")
PACKS_DIR = os.path.join(ROOT, "data", "packs")
OUT_PACK = os.path.join(PACKS_DIR, "batch8b_open_questions.json")
THIS_PACK = "data/packs/batch8b_open_questions.json"
TODAY = "2026-11-18"
TAG = f" UPDATED {TODAY} (research batch 8, second pass):"

DOCS = "nsw_planning/documents"
# The eleven modification records read today: (source id, archived text, title, published).
MODS = {
    "SRC_SSD9741_MOD4_ASSESSMENT": (f"{DOCS}/SSD-9741-Mod-4_mod_assessment.txt",
                                    "Modification 4 of Lane Cove West Data Centre (SSD-9741-Mod-4) - Assessment Report",
                                    "2025-10-01"),
    "SRC_SSD66777221_MOD2_ASSESSMENT": (f"{DOCS}/SSD-66777221-Mod-2_mod_assessment.txt",
                                        "Modification 2 of Lanceley Place Data Centre (SSD-66777221-Mod-2) - Assessment Report",
                                        "2026-04-01"),
    "SRC_SSD9741_MOD3_ASSESSMENT": (f"{DOCS}/SSD-9741-Mod-3_mod_assessment.txt",
                                    "Modification 3 of Lane Cove West Data Centre (SSD-9741-Mod-3) - Assessment Report",
                                    "2024-06-01"),
    "SRC_SSD9741_MOD2_ASSESSMENT": (f"{DOCS}/SSD-9741-Mod-2_mod_assessment.txt",
                                    "Lane Cove Data Centre Modification 2 (SSD-9741-Mod-2) - Modification Assessment",
                                    "2020-12-01"),
    "SRC_SSD41589232_MOD2_ASSESSMENT": (f"{DOCS}/SSD-41589232-Mod-2_mod_assessment.txt",
                                        "Modification 2 of 51 Huntingwood Drive Data Centre (SSD-41589232-Mod-2) - Assessment Report",
                                        "2026-08-01"),
    "SRC_MP080259_MOD7_ASSESSMENT": (f"{DOCS}/MP08_0259-Mod-7_mod_assessment.txt",
                                     "Greystanes Employment Lands - Dexus Estate Modification 7 (MP08_0259-Mod-7) - Modification Assessment",
                                     "2022-09-01"),
    "SRC_SSD10101987_MOD1_ASSESSMENT": (f"{DOCS}/SSD-10101987-Mod-1_mod_assessment.txt",
                                        "Modification 1 of the Kemps Creek Data Centre (SSD-10101987-Mod-1) - Assessment Report",
                                        "2024-11-01"),
    "SRC_SSD10330_MOD1_ASSESSMENT": (f"{DOCS}/SSD-10330-Mod-1_mod_assessment.txt",
                                     "Modification 1 of the Roberts Road Data Centre (SSD-10330-Mod-1) - Assessment Report",
                                     "2024-04-01"),
    "SRC_SSD59416728_MOD1_ASSESSMENT": (f"{DOCS}/SSD-59416728-Mod-1_mod_assessment.txt",
                                        "Modification 1 of Davis Road Data Centre (Cundall) (SSD-59416728-MOD-1) - Assessment Report",
                                        "2025-08-01"),
    "SRC_SSD66777221_MOD3_ASSESSMENT": (f"{DOCS}/SSD-66777221-Mod-3_mod_assessment.txt",
                                        "Modification 3 of Lanceley Place Data Centre (SSD-66777221-Mod-3) - Assessment Report",
                                        "2026-08-01"),
    "SRC_SSD10479_MOD8_REPORT": (f"{DOCS}/SSD-10479-Mod-8_mod_report.txt",
                                 "200 Aldington Road Industrial Estate (SSD-10479) - Section 4.55(1A) Modification Application Report",
                                 "2026-08-21"),
}
# Registered earlier (2026-09-18); this pass first registered a duplicate under its own id (fixed 2026-11-18).
SRC_TG_DC = "SRC_TRANSGRIDCAP"
SRC_TG_SS = "SRC_TRANSGRID_SYSTEM_STRENGTH"
SRC_TG_FAQ = "SRC_TRANSGRID_SYSTEM_STRENGTH_FAQ"
SRC_MANDALA24 = "SRC_MANDALA_EADF_2024"
SRC_MW_AR = "SRC_MELBOURNE_WATER_AR_2025"

TEXTS = {sid: v[0] for sid, v in MODS.items()}
TEXTS.update({
    SRC_TG_DC: "operators/transgrid/data-centres-and-electricity-capacity-in-nsw.txt",
    SRC_TG_SS: "operators/transgrid/system-strength-project.txt",
    SRC_TG_FAQ: "operators/transgrid/system_strength_project_faq.txt",
    SRC_MANDALA24: "reports_third_party/mandala/Empowering-Australias-Digital-Future-Report.txt",
    SRC_MW_AR: "registers/melbourne_water/downloads.txt",
})

QUOTES = {
    "SRC_SSD9741_MOD4_ASSESSMENT": {
        "diesel": ("The proposed modification seeks to increase diesel storage capacity from 1,651 t to 1966.9 t, "
                   "below the storage limit of 2,000 t specified in condition A6(c)."),
        "batteries": "increase the quantity of lithium-ion batteries from 55 t (as modified by the approved FSS) to 308 t",
        "monitoring": ("the Department has recommended new conditions requiring detailed monitoring and reporting of "
                       "generator use"),
        "posted": "the Department made the modification application publicly available on the Department’s website on 9 July 2025",
        "delegate": "the A/Team Leader, Industry Assessments, may determine the application under delegation",
        "route": "pursuant to section 4.55(1A)",
    },
    "SRC_SSD66777221_MOD2_ASSESSMENT": {
        "before": "30 x 2.8 MW / 3.5 MVA generators",
        "after": "42 x 2.82 MW / 3.6 MVA generators",
        "diesel": ("The electrical generation changes increase both the number and capacity of diesel generators, with "
                   "associated increases in diesel storage."),
        "approved": "The approved development included 170,000 kg of lithium-ion batteries and 895,000 L of diesel",
        "posted": "the Department made the modification application publicly available on the Department’s website on 27 January 2026",
        "route": "pursuant to section 4.55(1A)",
    },
    "SRC_SSD9741_MOD3_ASSESSMENT": {
        "before": "116 transformers / generators",
        "after": "121 transformers / generators",
        "exhibited": "publicly exhibited the modification from 21 February 2023 until 6 March 2023",
        "capacity": "138 MW • No change",
    },
    "SRC_SSD9741_MOD2_ASSESSMENT": {
        "route": "pursuant to section 4.55(2)",
        "exhibited": ("A total of seven submissions were received on the modification application during the "
                      "exhibition period"),
    },
    "SRC_SSD41589232_MOD2_ASSESSMENT": {
        "gens": "316 back-up diesel generators (No change)",
        "lodged": "The application was lodged on 12 June 2026 by AW Edwards Pty Ltd pursuant to section 4.55(1A)",
        "capacity": "a total capacity of 400 megawatts (MW)",
    },
    "SRC_MP080259_MOD7_ASSESSMENT": {
        "diesel": "the gantry structure would accommodate the storage of 1,288,600 L of diesel",
        "exhibited": "The modification application was not exhibited, however, was notified to Council and made publicly available",
    },
    "SRC_SSD10101987_MOD1_ASSESSMENT": {
        "purpose": "to allow for fit-out works to occur prior to operations commencing at the site",
    },
    "SRC_SSD10330_MOD1_ASSESSMENT": {
        "purpose": "increase the building height from three storeys to four storeys",
    },
    "SRC_SSD59416728_MOD1_ASSESSMENT": {
        "purpose": "to amend the number of existing trees to be removed by the development",
    },
    "SRC_SSD66777221_MOD3_ASSESSMENT": {
        "purpose": ("to facilitate architectural modifications to the switch room and reinstatement of an existing fire "
                    "brigade crossover"),
    },
    "SRC_SSD10479_MOD8_REPORT": {
        "purpose": "seeks to amend the configuration of Intersection 4",
    },
    SRC_TG_DC: {
        "exhausted": "Capacity to connect to the transmission network in the Sydney basin is largely exhausted",
        "enquiries": "data centre connection enquiries totaling more than 10 GW within a 12 km radius of Sydney West",
        "nca": "network capacity is only allocated upon signature of a Network Connection Agreement (NCA)",
        "threshold": "an inverter-based load greater than or equal to 30 MW or 30 MVA",
        "role": ("Require large users, such as data centres, to play their role in maintaining system security, "
                 "strength and reliability during the energy transition."),
        "cost": "Households and businesses should not bear the cost or risk associated with this growth.",
    },
    SRC_TG_SS: {
        "five": "fast-track the deployment of synchronous condensers at five strategic locations on Transgrid’s network",
        "kemps": "including Kemps Creek (Western Sydney)",
    },
    SRC_TG_FAQ: {
        "site": "Kemps Creek 500kV substation, off Gurner Avenue, West Hoxton in Western Sydney",
        "timing": ("Progressive energisation of synchronous condensers at the five sites is expected from early 2028 to "
                   "early 2029."),
        "two": "two smaller synchronous condensers at each of the five sites",
    },
    SRC_MANDALA24: {
        "capacity": ("data centre deployable capacity in Australia is projected to more than double from 1,350 megawatts "
                     "(MW) in 2024 to 3,100 MW by 2030"),
        "commissioned": ("The analysis in this report was commissioned by AirTrunk, Amazon Web Services, CDC, Microsoft, "
                         "and NEXTDC and prepared by Mandala."),
    },
    SRC_MW_AR: {
        "title": "Melbourne Water Annual Report 2024-25",
    },
}

NEW_SOURCES = [
    (SRC_TG_SS, "System Strength Project (Transgrid project page)", "Transgrid", None, "primary_company", "A",
     "Transgrid's page for the synchronous condensers it is deploying at five substations, including Kemps "
     "Creek (Western Sydney), directed by the NSW Government as a Priority Network Infrastructure Project. RG-019."),
    (SRC_TG_FAQ, "System Strength Project - frequently asked questions (Transgrid)", "Transgrid", None,
     "primary_company", "A",
     "Places the Western Sydney installation at the Kemps Creek 500 kV substation, off Gurner Avenue, West Hoxton: "
     "two smaller synchronous condensers at each of five sites, construction from mid-2026, progressive "
     "energisation early 2028 to early 2029. Names no data centre. RG-019."),
    (SRC_MANDALA24, "Empowering Australia's Digital Future - Data Centres: Essential digital infrastructure "
                    "underpinning everyday life (Mandala, October 2024)",
     "Mandala, commissioned by AirTrunk, Amazon Web Services, CDC, Microsoft and NEXTDC", "2024-10-01",
     "market_research", "B",
     "The report CertifiedStrategic.com relayed. It states deployable capacity of 1,350 MW in 2024 and 3,100 MW "
     "by 2030 in its own words; an industry-commissioned projection, so REPORTED, not verified. Read from the copy "
     "AirTrunk, one of the commissioning operators, publishes on its own site; Mandala's own host refused the "
     "crawler earlier (RG-100)."),
    (SRC_MW_AR, "Melbourne Water Annual Report 2024-25", "Melbourne Water", "2025-08-29", "primary_government", "A",
     "Read for RG-080 as the free substitute for FOI-005: its text does not mention data centres or Tata "
     "Consultancy Services. The PDF (about 70 MB) is not committed; re-fetch it from the manifest's URL."),
]


def normalise(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def pack_list() -> list[str]:
    text = open(os.path.join(ROOT, "scripts", "rebuild_all.py"), encoding="utf-8").read()
    block = text[text.index("PACKS = ["): text.index("]\n", text.index("PACKS = ["))]
    return re.findall(r'"(data/packs/[^"]+\.json)"', block)


def prior_notes(table: str, key: str, value) -> str:
    """The note the last earlier pack wrote for a row, so this pass extends it."""
    note = ""
    for rel in pack_list():
        if rel == THIS_PACK:
            break
        path = os.path.join(ROOT, rel)
        if not os.path.exists(path):
            continue
        for r in json.load(open(path, encoding="utf-8")).get("rows", {}).get(table, []):
            if r.get(key) == value and r.get("notes"):
                note = r["notes"]
            elif r.get("match", {}).get(key) == value and (r.get("set") or {}).get("notes"):
                note = r["set"]["notes"]
    return note


def manifest(rel_txt: str) -> dict:
    base = re.sub(r"\.txt$", "", os.path.join(RAW, rel_txt))
    for ext in (".pdf.meta.json", ".html.meta.json"):
        if os.path.exists(base + ext):
            return json.load(open(base + ext, encoding="utf-8"))
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
    # The absences the notes state, checked rather than typed.
    if SRC_MW_AR in texts:
        mw = texts[SRC_MW_AR].lower()
        for term in ("data centre", "data center", "tata consultancy"):
            if term in mw:
                errors.append(f"{SRC_MW_AR}: the note says the report does not mention '{term}', but it does")
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
    for sid, (rel, title, published) in MODS.items():
        meta = manifest(rel)
        sources.append(dict(
            id=sid, title=title, publisher="NSW Department of Planning, Housing and Infrastructure (NSW Planning Portal)"
            if "REPORT" not in sid else "Prepared for the applicant (NSW Planning Portal)",
            url=meta["url"], doc_type="primary_planning_portal", published=published, credibility="A",
            accessed=TODAY,
            notes=(f"Read {TODAY} from the NSW Planning Portal ({meta['label']}), SHA-256 {meta['sha256']}, "
                   f"{meta['pages']} pages, text by {meta['extractor']}, archived at data/raw/{rel} with its "
                   "manifest; the PDF is not committed. Published month as printed on the report. RG-034.")))
    for sid, title, publisher, published, doc_type, cred, notes in NEW_SOURCES:
        meta = manifest(TEXTS[sid])
        sources.append(dict(id=sid, title=title, publisher=publisher, url=meta["url"], doc_type=doc_type,
                            published=published, credibility=cred, accessed=TODAY,
                            notes=notes + f" ARCHIVED {TODAY} at data/raw/{os.path.dirname(TEXTS[sid])}/ with a "
                                          f"SHA-256 manifest ({meta['sha256'][:16]}...)."))

    def gap(gap_id: int, text: str, refs: list[tuple[str, str]], status: str | None = None,
            resolved: bool = False, source_id: str | None = None) -> list[dict]:
        upd = dict(notes=(prior_notes("research_gaps", "id", gap_id) + TAG + " " + text).strip(), as_of_date=TODAY)
        if status:
            upd["status"] = status
        if resolved:
            upd["resolved_date"] = TODAY
        if source_id:
            upd.update(source_id=source_id, fact_status="VERIFIED", confidence="high")
        return [dict(match=dict(id=gap_id), set=upd, add_sources=q(*refs) if refs else [])]

    gaps: list[dict] = []
    gaps += gap(34, (
        "MODIFICATION HALF DONE: all 17 modification records on the NSW data centre files are read (five in batch "
        "7; ten assessment reports and one modification report today; the withdrawn 51 Huntingwood Mod 1 report "
        "answered 401). Beyond batch 7's five, three more add generators or diesel. LANE COVE WEST MOD 4 (October "
        "2025, section 4.55(1A), decided by an A/Team Leader, posted on 9 July 2025, not exhibited): 'The proposed "
        "modification seeks to increase diesel storage capacity from 1,651 t to 1966.9 t, below the storage limit "
        "of 2,000 t specified in condition A6(c)', and lithium-ion batteries from 55 t to 308 t; the Department "
        "added conditions 'requiring detailed monitoring and reporting of generator use'. LANCELEY PLACE MOD 2 "
        "(April 2026, section 4.55(1A), posted 27 January 2026): from '30 x 2.8 MW / 3.5 MVA generators' to '42 x "
        "2.82 MW / 3.6 MVA generators', 'with associated increases in diesel storage' above the approved 895,000 "
        "L. LANE COVE WEST MOD 3 (June 2024, section 4.55(2), exhibited 21 February to 6 March 2023): from '116 "
        "transformers / generators' to '121'. The rest change no generator or diesel quantity: Lane Cove West Mod 2 "
        "(office use; section 4.55(2), exhibited, seven submissions), 51 Huntingwood Mod 2 ('316 back-up diesel "
        "generators (No change)'; lodged by a builder, AW Edwards Pty Ltd), Dexus Estate Mod 7 (layout; restates "
        "1,288,600 L of diesel; not exhibited), Kemps Creek Mod 1 (fit-out before operation), Roberts Road Mod 1 "
        "(height), Davis Road Mod 1 (trees), Lanceley Place Mod 3 (switch room), 200 Aldington Mod 8 (an "
        "intersection). PROPOSED to the author: reclassify SSD-9741-Mod-4 (change_type other -> "
        "fuel_storage_increase, materiality 3 -> 5), SSD-66777221-Mod-2 (other -> generator_increase, 2 -> 5) and "
        "SSD-9741-Mod-3 (design -> generator_increase, 2 -> 4). Not made by this pack. STILL OPEN: council "
        "development applications, for the approved council list only (docs/SPEC.md)."),
        [("SRC_SSD9741_MOD4_ASSESSMENT", "diesel"), ("SRC_SSD9741_MOD4_ASSESSMENT", "monitoring"),
         ("SRC_SSD66777221_MOD2_ASSESSMENT", "before"), ("SRC_SSD66777221_MOD2_ASSESSMENT", "after"),
         ("SRC_SSD66777221_MOD2_ASSESSMENT", "diesel"), ("SRC_SSD9741_MOD3_ASSESSMENT", "before"),
         ("SRC_SSD9741_MOD3_ASSESSMENT", "after"), ("SRC_SSD41589232_MOD2_ASSESSMENT", "gens")],
        status="in_progress")
    gaps += gap(19, (
        "RESOLVED. One exists in plan, none in service. Transgrid's System Strength Project, directed by the NSW "
        "Government, will 'fast-track the deployment of synchronous condensers at five strategic locations', "
        "'including Kemps Creek (Western Sydney)': two smaller machines at the 'Kemps Creek 500kV substation, off "
        "Gurner Avenue, West Hoxton in Western Sydney', the substation of the Kemps Creek - Mamre Road data centre "
        "corridor. 'Progressive energisation of synchronous condensers at the five sites is expected from early "
        "2028 to early 2029.' Neither Transgrid document names a data centre; the condensers serve the network, "
        "not a customer. Re-open if a data centre's own connection includes one."),
        [(SRC_TG_SS, "five"), (SRC_TG_SS, "kemps"), (SRC_TG_FAQ, "site"), (SRC_TG_FAQ, "timing"),
         (SRC_TG_FAQ, "two")], status="resolved", resolved=True, source_id=SRC_TG_FAQ)
    gaps += gap(18, (
        "The network owner's position, on its own page: Transgrid is working on frameworks to 'Require large "
        "users, such as data centres, to play their role in maintaining system security, strength and reliability "
        "during the energy transition' - a requirement it is seeking, not one in force. The primary record of what any site provides is AEMO's NEM Registration and Exemption List; AEMO's "
        "registration page answered the crawler with HTTP 403 (recorded). BLOCKED on download #31."),
        [(SRC_TG_DC, "role")], status="blocked")
    gaps += gap(43, (
        "Transgrid's own page states the principle and the constraint, not a total: 'Households and businesses "
        "should not bear the cost or risk associated with this growth'; capacity in the Sydney basin is 'largely "
        "exhausted'; since late 2024 it has received 'data centre connection enquiries totaling more than 10 GW "
        "within a 12 km radius of Sydney West'; capacity is allocated only on a signed connection agreement, for "
        "loads of 30 MW or more. It puts no dollar figure on what data centres pay. The AER's register closed the "
        "connection again today (recorded). The quantum test against the networks' capital plans stays open."),
        [(SRC_TG_DC, "cost"), (SRC_TG_DC, "exhausted"), (SRC_TG_DC, "enquiries"), (SRC_TG_DC, "nca"),
         (SRC_TG_DC, "threshold")], status="in_progress")
    gaps += gap(100, (
        "The two Mandala figures now rest on Mandala: the October 2024 report says 'data centre deployable "
        "capacity in Australia is projected to more than double from 1,350 megawatts (MW) in 2024 to 3,100 MW by "
        "2030', and that it 'was commissioned by AirTrunk, Amazon Web Services, CDC, Microsoft, and NEXTDC'. Read "
        "from the copy AirTrunk publishes; Mandala's own host had refused. The two metrics are re-sourced to it "
        "(REPORTED, medium: an industry-commissioned projection). STILL ON CertifiedStrategic.com alone: the two "
        "CBRE figures (CBRE answered 403) and the national count of certified facilities."),
        [(SRC_MANDALA24, "capacity"), (SRC_MANDALA24, "commissioned")], status="in_progress")
    gaps += gap(68, (
        "Free substitutes read, all silent: the Lane Cove West (AirTrunk SYD2) consent and its four modification "
        "reports, and the Apollo Place consent and assessment, mention 'recycled' only for construction waste, "
        "never for water; AirTrunk's April 2025 paper on cooling resources names no Australian site and no "
        "recycled-water supply. No record read shows an AirTrunk site holding a recycled-water agreement. The "
        "utility's own record is the only place one would appear: BLOCKED at zero spend on GIPA-004 (Sydney Water, "
        "$30, not lodged) and FOI-005 (Melbourne Water, $34.50, not lodged)."), [], status="blocked")
    gaps += gap(80, (
        "Free substitute read: Melbourne Water's Annual Report 2024-25 does not mention data centres or Tata "
        "Consultancy Services (checked by this pack's script). Its published tenders were not reached. BLOCKED at "
        "zero spend on FOI-005 ($34.50, not lodged)."), [(SRC_MW_AR, "title")], status="blocked")
    gaps += gap(7, (
        "The free substitute is refused: the 2026-27 Budget Paper No. 1, which carries the tax expenditure "
        "statement (Appendix C), sits under a path nsw.gov.au's robots.txt disallows; the older budget.nsw.gov.au "
        "links now redirect. Recorded; BLOCKED on download #30 (and GIPA-002, not lodged)."), [], status="blocked")
    gaps += gap(63, (
        "The Department's 2024-25 annual report is published only through the National Library's viewer, which "
        "served a bot-check page in place of the document (recorded). BLOCKED on download #33."), [],
        status="blocked")
    gaps += gap(69, (
        "The NSW Electoral Commission's disclosure site disallows every crawler in its robots.txt (recorded). "
        "BLOCKED on download #34 (and GIPA-003, not lodged)."), [], status="blocked")
    gaps += gap(27, (
        "BEETALOO: the Territory Coordinator's release on Beetaloo Digital's Weddell site refused the crawler "
        "(its robots.txt could not be read; recorded). LEADS (search summaries, not records): a 12-month exclusive "
        "land commitment over 185 ha at Weddell, south of Darwin, granted on 22 July 2026, with up to 2 GW of "
        "on-site gas generation. Download #32 would put it on the record."), [])
    gaps += gap(91, (
        "Sharon AI's June 2026 release on its NVIDIA collaboration is on a newswire whose robots.txt refused the "
        "crawler. LEADS (search summaries): 72 MW of new Australian capacity, with no city, state or host facility "
        "named. No partner statement read today places a DSX build on a site."), [])
    gaps += gap(102, (
        "One more free search (Stockland's releases and the trade press): no record names the end user. A "
        "directory's 'believed to be' a cloud provider is speculation, not a record. PROPOSED TO THE AUTHOR as not "
        "retrievable at zero spend; the question would re-open on an operator's or Stockland's own statement. "
        "Not closed by this pack."), [])
    gaps += gap(13, (
        "PROPOSED TO THE AUTHOR: close the remainder (AWS's and Google's site-level footprints) as not retrievable "
        "at zero spend. The free routes are worked: planning registers name codename companies and consultancies, "
        "not hyperscalers (RG-035, RG-055); the landowner documents are restricted (GIPA-001, not lodged). Not "
        "closed by this pack."), [])

    # The modification rows: each gains its report and the quotes that describe it. Values are unchanged;
    # the three reclassifications are proposed in RG-034.
    mods = []
    for case, sid, labels in (
        ("SSD-9741-Mod-4", "SRC_SSD9741_MOD4_ASSESSMENT", ["diesel", "batteries", "monitoring", "posted", "delegate"]),
        ("SSD-66777221-Mod-2", "SRC_SSD66777221_MOD2_ASSESSMENT", ["before", "after", "diesel", "approved", "posted"]),
        ("SSD-9741-Mod-3", "SRC_SSD9741_MOD3_ASSESSMENT", ["before", "after", "exhibited", "capacity"]),
        ("SSD-9741-Mod-2", "SRC_SSD9741_MOD2_ASSESSMENT", ["route", "exhibited"]),
        ("SSD-41589232-Mod-2", "SRC_SSD41589232_MOD2_ASSESSMENT", ["gens", "lodged", "capacity"]),
        ("MP08_0259-Mod-7", "SRC_MP080259_MOD7_ASSESSMENT", ["diesel", "exhibited"]),
        ("SSD-10101987-Mod-1", "SRC_SSD10101987_MOD1_ASSESSMENT", ["purpose"]),
        ("SSD-10330-Mod-1", "SRC_SSD10330_MOD1_ASSESSMENT", ["purpose"]),
        ("SSD-59416728-Mod-1", "SRC_SSD59416728_MOD1_ASSESSMENT", ["purpose"]),
        ("SSD-66777221-Mod-3", "SRC_SSD66777221_MOD3_ASSESSMENT", ["purpose"]),
        ("SSD-10479-Mod-8", "SRC_SSD10479_MOD8_REPORT", ["purpose"]),
    ):
        mods.append(dict(match=dict(mod_case=case), set={}, add_sources=q(*[(sid, lab) for lab in labels])))

    metrics = []
    for as_of in ("2024", "2030"):
        match = dict(as_of=as_of, scope="Australia", metric_name="deployable_capacity")
        metrics.append(dict(match=match, set=dict(
            source_id=SRC_MANDALA24, fact_status="REPORTED", confidence="medium", as_of_date=TODAY,
            notes=("Stated by Mandala's October 2024 report, commissioned by AirTrunk, AWS, CDC, Microsoft and "
                   "NEXTDC: an industry-commissioned projection, REPORTED (re-sourced " + TODAY + ", RG-100). "
                   "Earlier: relayed by CertifiedStrategic.com from Mandala's November 2025 report, whose text "
                   "does not state it; the figure is the October 2024 report's.")),
            add_sources=q((SRC_MANDALA24, "capacity"))))

    pack = {
        "pack_id": "batch8b-open-questions-2026-11",
        "prepared_by": "scripts/curate_batch8b.py from data/raw/ (archived and read 2026-11-18)",
        "prepared_on": TODAY,
        "_comment": [
            "Research batch 8, second pass, under the author's zero-spend decision of 2026-11-18.",
            "Resolves RG-019; reads the 11 remaining modification records (RG-034); re-sources the two",
            "Mandala capacity metrics (RG-100). RG-007, 018, 063, 068, 069 and 080 are blocked on a named",
            "download or unlodged request. RG-013 and RG-102 are PROPOSED for closing, and three",
            "modification reclassifications are PROPOSED; this pack makes none of them.",
        ],
        "sources": sources,
        "rows": {"research_gaps": gaps, "modifications": mods, "metrics": metrics},
    }
    with open(OUT_PACK, "w") as f:
        json.dump(pack, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print(f"batch 8b: {len(sources)} sources, {len(gaps)} question updates, {len(mods)} modifications quoted, "
          f"{len(metrics)} metrics re-sourced; wrote {os.path.relpath(OUT_PACK, ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
