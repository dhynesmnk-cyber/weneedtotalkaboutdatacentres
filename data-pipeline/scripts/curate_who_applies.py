#!/usr/bin/env python3
"""
Curate research batch 1, "Who is really applying?" (docs/RESEARCH-PLAN.md, story line M1).

Three free records, read together, answer much of what the agenda had marked as needing paid
searches:

  1. ASIC's Company Dataset (scrapers/fetch_asic_companies.py): every applicant company's
     registration date and every name it has carried, with the date each change took effect.
  2. The title searches two applicants filed with their applications
     (scrapers/fetch_ownership_documents.py): who is registered as owning the land.
  3. The Department's own assessment reports, already archived by batch S2: what each one says
     about who the applicant is acting for.

Every quote below is checked against the archive it comes from, and the script refuses to write a
pack if any is missing. Nothing is inferred: where a record names a company, the company is
named; where it only implies one, the implication stays a question in the research agenda.
Naming an operator against a site, or merging records, remains a human decision (RG-098).

Run:
    python3 scripts/curate_who_applies.py
    python3 scripts/load_pack.py data/packs/who_applies.json --allow-missing-source
"""
from __future__ import annotations

import csv
import hashlib
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "data", "packs", "who_applies.json")
RAW = os.path.join(ROOT, "data", "raw")
ASIC = os.path.join(RAW, "asic", "company_dataset_202610_extract.csv")
DOCS = os.path.join(RAW, "nsw_planning", "documents")
OWNERSHIP = os.path.join(RAW, "nsw_planning", "ownership")
IDA = os.path.join(RAW, "operators", "nswgov", "data-centre-investment-sustainable-development.txt")
AIRTRUNK_SYD2 = os.path.join(RAW, "operators", "airtrunk", "syd2-sydney-north.txt")
TODAY = "2026-10-22"
SRC_ASIC = "SRC_ASIC_COMPANIES_202610"
SRC_DAVIS_TITLE = "SRC_SSD59416728_TITLE"
SRC_MAMRE_TITLE = "SRC_SSD92743706_TITLE"

errors: list[str] = []


def spaceless(text: str) -> str:
    """Lower case with all whitespace removed: some reports are letter-spaced in extraction."""
    return re.sub(r"\s+", "", text).lower()


def verified_text(path: str) -> str:
    return open(path, encoding="utf-8").read()


def page_of(path: str, quote: str) -> int | None:
    """The page an archived text carries the quote on, or None."""
    text = verified_text(path)
    for m in re.finditer(r"\[\[page (\d+)\]\]\n(.*?)(?=\n\[\[page \d+\]\]|\Z)", text, re.S):
        if spaceless(quote) in spaceless(m.group(2)):
            return int(m.group(1))
    return None


def quoted(path: str, quote: str) -> str:
    """'pN: quote', refusing a quote the archive does not hold."""
    page = page_of(path, quote)
    if page is None:
        errors.append(f"{os.path.relpath(path, ROOT)} does not hold {quote[:70]!r}")
        return quote
    return f"p{page}: {quote}"


def in_text(path: str, quote: str) -> str:
    if spaceless(quote) not in spaceless(verified_text(path)):
        errors.append(f"{os.path.relpath(path, ROOT)} does not hold {quote[:70]!r}")
    return quote


# --- ASIC -----------------------------------------------------------------------------------------

def asic_rows() -> list[list[str]]:
    raw = open(ASIC, "rb").read()
    meta = json.load(open(ASIC + ".meta.json"))
    if hashlib.sha256(raw).hexdigest() != meta["extract_sha256"]:
        raise SystemExit("the ASIC extract fails its SHA-256 check")
    return list(csv.reader(raw.decode("utf-8").splitlines()))


ROWS = asic_rows()
HEAD, BODY = ROWS[0], ROWS[1:]
COL = {k: i for i, k in enumerate(HEAD)}


def asic(name: str) -> str:
    """The register's line for a company name, current or former, verbatim as the quote."""
    hits = [r for r in BODY if r[0].upper() == name.upper()]
    if len(hits) != 1:
        errors.append(f"ASIC extract holds {len(hits)} rows named {name!r}")
        return name
    return ",".join(hits[0])


def registered(name: str) -> str:
    """The registration date of the company now or once named so, as ASIC gives it."""
    hits = [r for r in BODY if r[0].upper() == name.upper()]
    return hits[0][COL["Date of Registration"]] if len(hits) == 1 else "?"


def renamed(former: str, current: str, since: str) -> str:
    """Check the register records the change, and return its line."""
    line = asic(former)
    cells = line.split(",")
    if cells[COL["Current Name"]].upper() != current.upper() or cells[COL["Current Name Start Date"]] != since:
        errors.append(f"ASIC does not record {former} -> {current} from {since}")
    return line


# --- the Department's descriptions of applicants (batch S2 archives) ------------------------------

def report(case: str) -> str:
    return os.path.join(DOCS, f"{case}_assessment.txt")


# (case, site, applicant, the Department's sentence). Each says the applicant stands in for an
# operator the report does not name. Read 2026-10-21 from every determined data centre consent
# with an archived assessment report; the classification of all 22 is in METRIC_NOTES.
UNNAMED = [
    ("SSD-9741", "SITE_LANE_COVE_WEST", "Greenbox Architecture Pty Ltd",
     "Greenbox acts on behalf of an existing data centre operator (the client) which currently operates two "
     "data centres in Melbourne and western Sydney."),
    ("SSD-10467", "SITE_MACQUARIE_PARK_DC", "Stockland Trust Management Limited",
     "The Applicant has been approached by a data centre operator (the lessee) who is seeking to expand its "
     "operations within the Sydney region."),
    ("SSD-33781208", "SITE_STATION_RD", "Lehr Consultants International (Australia) Pty Ltd",
     "It acts on behalf of a multinational data centre operator which is seeking to expand its operations "
     "within the Sydney region."),
    ("SSD-10101987", "SITE_MSFT_KEMPS", "Arup Pty Ltd",
     "has been approached by a data centre operator (the end user) who is seeking to expand its operations "
     "within Western Sydney."),
    ("SSD-41589232", "SITE_51_HUNTINGWOOD", "EMKC Cubed Management Pty Ltd",
     "The Applicant was approached by a data centre operator who is seeking to expand its operations within "
     "Western Sydney."),
    ("SSD-47320208", "SITE_ECHIDNA", "ARUP Australia Pty Ltd",
     "It acts on behalf of a multinational data centre operation which is seeking to expand its operations "
     "within the Sydney region."),
    ("SSD-59416728", "SITE_DAVIS_RD_CUNDALL", "Cundall Johnston and Partners Pty Ltd",
     "It acts on behalf of a global data centre operator which is seeking to expand its operations within the "
     "Sydney region."),
    ("SSD-67407231", "SITE_APOLLO_PLACE", "EMKC Cubed Management Pty Ltd",
     "has been approached by a data centre operator (the end user) who is seeking to expand its operations "
     "within the Lane Cove West Business Park."),
    ("SSD-68013714", "SITE_43_61_TURNER", "ARUP Pty Ltd",
     "It acts on behalf of a multinational data centre operation which is seeking to expand its operations "
     "within the Sydney region."),
]
METRIC_NOTES = (
    "Of the 22 determined NSW data centre State Significant Development consents whose Department assessment "
    "report is archived (batch S2; the Dicker Data warehouse is excluded as not a data centre), 9 describe the "
    "applicant as acting for, or approached by, a data centre operator the report does not name: Lane Cove "
    "West (SSD-9741, Greenbox Architecture), Macquarie Park (SSD-10467, Stockland Trust Management), Station "
    "Road (SSD-33781208, Lehr), Kemps Creek (SSD-10101987, Arup; the end user is identified only by 'the asset "
    "numbers SYD05, 06 & 07'), 51 Huntingwood Drive (SSD-41589232, EMKC Cubed Management), Project Echidna "
    "(SSD-47320208, ARUP Australia), Davis Road (SSD-59416728, Cundall), Apollo Place (SSD-67407231, EMKC "
    "Cubed Management) and 43-61 Turner Road (SSD-68013714, ARUP). One more names a consultancy applicant "
    "without mentioning an operator at all (Glendenning Road, SSD-73761707, Lehr). Four name a property "
    "developer that builds for tenants it does not name (Goodman for Project Pluto, Project Duke and Project "
    "Apollo; Stockland for 1-5 Khartoum Road). Eight name the operator itself: CDC (Roberts Road, Marsden "
    "Park), NineZero (the Eastern Creek expansion, and DCI Poplars, 'trading as DCI Data Centers'), Macquarie Data Centres (Talavera "
    "Road), Equinix (Grand Avenue), NEXTDC (S4) and HDI SYD1, which the report calls DigiCo (SYD1). So 14 of "
    "22 consents went to an applicant that is not the operator. Read 2026-10-21 by "
    "scripts/curate_who_applies.py; each of the nine is quoted in this row's source references.")

# --- registration dates for RG-055 ----------------------------------------------------------------

# Consent applicant (as the Department names it) -> the register name it is filed under, and the
# consent's determination date. Trusts are not companies and are not on the register.
APPLICANTS = [
    ("SSD-9741", "Greenbox Architecture Pty Ltd", "GREENBOX ARCHITECTURE PTY LTD", "2019-11-15"),
    ("SSD-10330", "Canberra Data Centres Pty Ltd", "CDC DATA CENTRES PTY LTD", "2020-07-14"),
    ("SSD-10467", "Stockland Trust Management Limited", "STOCKLAND TRUST MANAGEMENT LIMITED", "2021-05-28"),
    ("SSD-33781208", "Lehr Consultants International (Australia) Pty Ltd",
     "LEHR CONSULTANTS INTERNATIONAL (AUSTRALIA) PTY LTD", "2022-12-16"),
    ("SSD-10101987", "Arup Pty Ltd", "ARUP PTY LIMITED", "2023-07-13"),
    ("SSD-21342738", "NineZero DC Sub TC I Pty Ltd", "NINEZERO DC SUB TC I PTY LTD", "2023-09-01"),
    ("SSD-41589232", "EMKC Cubed Management Pty Ltd", "EMKC CUBED MANAGEMENT PTY LTD", "2023-09-15"),
    ("SSD-24299707", "Macquarie Data Centres Pty Ltd", "MACQUARIE DATA CENTRES PTY LTD", "2024-01-19"),
    ("SSD-47320208", "ARUP Australia Pty Ltd", "ARUP AUSTRALIA PTY LTD", "2024-04-05"),
    ("SSD-53338465", "Equinix Hyperscale 2 (SY10) Pty Limited", "EQUINIX HYPERSCALE 2 (SY10) PTY LIMITED",
     "2024-12-16"),
    ("SSD-59416728", "Cundall Johnston and Partners Pty Ltd", "CUNDALL JOHNSTON AND PARTNERS PTY. LIMITED",
     "2024-12-20"),
    ("SSD-67407231", "EMKC Cubed Management Pty Ltd", "EMKC CUBED MANAGEMENT PTY LTD", "2025-10-09"),
    ("SSD-68013714", "ARUP Pty Ltd", "ARUP PTY LIMITED", "2025-11-21"),
    ("SSD-70889211", "CDC Data Centres Pty Ltd", "CDC DATA CENTRES PTY LTD", "2025-11-27"),
    ("SSD-71368959", "Goodman Property Services (Aust) Pty Limited",
     "GOODMAN PROPERTY SERVICES (AUST) PTY LIMITED", "2025-12-22"),
    ("SSD-69637456", "HDI SYD1 Property Holdings Limited", "HDI SYD1 PROPERTY HOLDINGS PTY LIMITED", "2025-12-23"),
    ("SSD-63741210", "NEXTDC Limited", "NEXTDC LIMITED", "2025-12-24"),
    ("SSD-63235720", "Stockland Development Pty Limited", "STOCKLAND DEVELOPMENT PTY LIMITED", "2026-03-11"),
    ("SSD-69223466", "Goodman Property Services (Aust) Pty Ltd", "GOODMAN PROPERTY SERVICES (AUST) PTY LIMITED",
     "2026-07-23"),
    ("SSD-74069708", "Goodman Property Services (Aust) Pty Limited",
     "GOODMAN PROPERTY SERVICES (AUST) PTY LIMITED", "2026-09-02"),
    ("SSD-73761707", "Lehr Consultants International (Australia) Pty Ltd",
     "LEHR CONSULTANTS INTERNATIONAL (AUSTRALIA) PTY LTD", "2026-09-16"),
]


def years_before(registered_dmy: str, decided_iso: str) -> float:
    d, m, y = (int(x) for x in registered_dmy.split("/"))
    yy, mm, dd = (int(x) for x in decided_iso.split("-"))
    return round((yy + (mm - 1) / 12 + dd / 365) - (y + (m - 1) / 12 + d / 365), 1)


def main() -> int:
    # Name changes the notes rely on. Each refuses if the register does not record it.
    knbdc_syd4 = renamed("KNBDC SYD4 PTY LTD", "AIRTRUNK SYD4 PTY LTD", "16/06/2026")
    for former, current in [("KNBDC SYD4 HOLD PTY LTD", "AIRTRUNK SYD4 HOLD PTY LTD"),
                            ("KNBDC SYD4 INTERMEDIATE HOLD PTY LTD", "AIRTRUNK SYD4 INTERMEDIATE HOLD PTY LTD"),
                            ("KNBDC SYD4 FINANCING HOLDCO PTY LTD", "AIRTRUNK SYD4 FINANCING HOLDCO PTY LTD")]:
        renamed(former, current, "16/06/2026")
    renamed("KNBDC SYD4 FINCO PTY LTD", "AIRTRUNK SYD4 FINCO PTY LTD", "17/06/2026")
    renamed("KNBDC MEL3 PTY LTD", "AIRTRUNK MEL3 PTY LTD", "16/06/2026")
    renamed("KNBDC MEL EXP PTY LTD", "AIRTRUNK MEL EXP PTY LTD", "05/08/2026")
    renamed("KNBDC AUSTRALIA PTY LTD", "AIRTRUNK MEL1 PTY LTD", "22/01/2026")
    knbdc_dev = asic("KNBDC AU DEVELOPMENT PTY LTD")
    emkc = renamed("EMKC CUBED MANAGEMENT PTY LTD", "CKTSME MANAGEMENT PTY LTD", "03/06/2025")
    hdi = renamed("GLOBAL SWITCH PROPERTY (AUSTRALIA) PTY LIMITED", "HDI SYD1 PROPERTY HOLDINGS PTY LIMITED",
                  "12/05/2025")
    ispt = renamed("ISPT PTY LTD", "IFM REAL ESTATE FIDUCIARY PTY LTD", "24/11/2025")
    agp_manager = renamed("AGP DC MANAGER AUSTRALIA PTY LTD", "ZERRA WDDP MANAGER AUSTRALIA PTY LTD", "13/08/2026")
    agp_invest = renamed("AGPDC INVESTMENTS AUSTRALIA PTY LTD", "ZERRA INVESTMENTS AUSTRALIA PTY LTD", "20/01/2026")
    wddp = asic("WDDP PTY LTD")
    wddp_holdco = asic("ZERRA WDDP HOLDCO PTY LTD")
    amazon_au = asic("AMAZON AUSTRALIA COMPANY PTY LTD")
    ninezero_tc = asic("NINEZERO DC SUB TC I PTY LTD")
    msft = asic("MICROSOFT DATACENTER (AUSTRALIA) PTY LIMITED")
    if registered("WDDP PTY LTD") != "28/07/2026" or registered("AMAZON AUSTRALIA COMPANY PTY LTD") != "14/11/2022":
        errors.append("a registration date the notes rely on has changed")
    six = [r[0] for r in BODY if r[0].startswith("EMKC CUBED") and r[COL["Current Name"]].startswith("CKTSME")]
    if len(set(six)) != 6:
        errors.append(f"expected six EMKC Cubed companies renamed CKTSME, found {sorted(set(six))}")

    # Title searches filed with the applications.
    davis_title = os.path.join(OWNERSHIP, "SSD-59416728__appendix-3-title-documents-310.txt")
    mamre_title = os.path.join(OWNERSHIP, "SSD-92743706__appendix-3-title-documents-388.txt")
    davis_owner = in_text(davis_title, "FIRST SCHEDULE -------------- AMAZON AUSTRALIA COMPANY PTY LTD (TZ AS707242)")
    in_text(davis_title, "SEARCH DATE TIME EDITION NO DATE ----------- ---- ---------- ---- 12/10/2023 10:40 AM 37 "
                         "9/12/2022")
    mamre_owner = in_text(mamre_title, "FIRST SCHEDULE -------------- ISPT PTY LIMITED")
    mamre_caveat = in_text(mamre_title, "AV293179 CAVEAT BY KNBDC SYD4 PTY LTD")
    in_text(mamre_title, "LOT 10 IN DEPOSITED PLAN 1280592 AT KEMPS CREEK")
    in_text(IDA, "KNBDC SYD4 Pty Ltd")
    phase5 = in_text(AIRTRUNK_SYD2, "The project is Phase 5 of AirTrunk’s investment within the precinct")

    unnamed_refs = [dict(id=f"SRC_{case.replace('-', '')}_ASSESSMENT", quote=quoted(report(case), q))
                    for case, _, _, q in UNNAMED]
    healey = quoted(report("SSD-41589232"), "including the Huntingwood Data Centre located nearby to the site at "
                                            "24 Healey Circuit, Huntingwood")
    asset_numbers = quoted(report("SSD-10101987"), "The proposed development has been identified by the end user "
                                                   "with the asset numbers SYD05, 06 & 07.")
    digico = quoted(report("SSD-69637456"), "HDI SYD1 Property Holdings Limited (DigiCo) (the Applicant)")
    dci = quoted(report("SSD-64287712"), "The Trustee for NineZero DC Sub Trust I, trading as DCI Data Centers")

    # RG-055: how long each consent's applicant had existed when the consent was determined.
    ages = []
    for case, applicant, register_name, decided in APPLICANTS:
        reg = registered(register_name)
        if reg == "?":
            errors.append(f"no register row for {register_name}")
            continue
        ages.append((case, applicant, reg, decided, years_before(reg, decided)))
    under_three = [a for a in ages if a[4] < 3]

    if errors:
        print("refusing to write; fix these first:", file=sys.stderr)
        for e in errors:
            print(f"  {e}", file=sys.stderr)
        return 1

    # Each title source points at the document itself, not the project page: another curation
    # (curate_site_coordinates.py) adopts any registered project-page source as that project's own.
    sources = [
        dict(id=SRC_ASIC, title="ASIC Company Dataset, October 2026 release: extract of the companies behind NSW "
                               "data centre applications",
             publisher="Australian Securities and Investments Commission (data.gov.au)",
             url="https://data.gov.au/data/dataset/asic-companies", doc_type="primary_regulator",
             published="2026-10", accessed="2026-10-21", credibility="A",
             notes="ASIC's whole company register, published monthly under CC BY 3.0 AU: each company's name, ACN, "
                   "type, status and registration date, and for a renamed company each former name with the date "
                   "the current one took effect. No directors, shareholders or addresses. Downloaded 2026-10-21 "
                   "(ZIP SHA-256 in the manifest) and filtered by scrapers/fetch_asic_companies.py to 185 rows, "
                   "committed at data/raw/asic/company_dataset_202610_extract.csv. Names only: who owns a "
                   "company needs a paid extract (docs/requests/PAID-SEARCHES.md)."),
        dict(id=SRC_DAVIS_TITLE, title="Title search, Lot 1 DP 864615, 3 Davis Road, Wetherill Park (Appendix 3 "
                                       "to SSD-59416728)",
             publisher="NSW Land Registry Services, via the applicant's information broker; published on the NSW "
                       "Planning Portal",
             url=json.load(open(os.path.join(OWNERSHIP, "SSD-59416728__appendix-3-title-documents-310.pdf.meta.json")))["url"],
             doc_type="primary_planning_portal", published="2023-10-12", accessed="2026-10-21", credibility="A",
             notes="Searched 12 October 2023. First Schedule (registered proprietor): Amazon Australia Company "
                   "Pty Ltd, by transfer AS707242; current edition dated 9 December 2022; a lease of Warehouse 1 to "
                   "Northline Pty Ltd expiring 30 November 2024. Archived by "
                   "scrapers/fetch_ownership_documents.py at data/raw/nsw_planning/ownership/."),
        dict(id=SRC_MAMRE_TITLE, title="Title search, Lot 10 DP 1280592, Kemps Creek (Appendix 3 to SSD-92743706)",
             publisher="NSW Land Registry Services, via the applicant's information broker; published on the NSW "
                       "Planning Portal",
             url=json.load(open(os.path.join(OWNERSHIP, "SSD-92743706__appendix-3-title-documents-388.pdf.meta.json")))["url"],
             doc_type="primary_planning_portal", published="2025-12-16", accessed="2026-10-21", credibility="A",
             notes="Searched 16 December 2025. First Schedule (registered proprietor): ISPT Pty Limited. Second "
                   "Schedule item 3: caveat AV293179 by KNBDC SYD4 Pty Ltd, marked as not on the current edition of "
                   "the certificate of title. Covers Lot 10 only. Archived by scrapers/fetch_ownership_documents.py "
                   "at data/raw/nsw_planning/ownership/."),
        # Re-declared in full because the loader upserts sources; only the notes gain the archive line.
        dict(id="SRC_NSW_IDA", title="NSW Government backs data centre investment, sets course for sustainable "
                                     "development (ministerial media release, 27 March 2026)",
             publisher="NSW Government - Treasurer, Minister for Industry and Trade, Minister for Planning and "
                       "Public Spaces",
             url="https://www.nsw.gov.au/ministerial-releases/data-centre-investment-sustainable-development",
             doc_type="primary_government", published="2026-03-27", accessed="2026-09-18", credibility="A",
             notes="Names the proponent, project and local government area for all 15 data centre projects endorsed "
                   "in Round 1 of the Investment Delivery Authority (IDA), collectively worth $51.9bn. Also records "
                   "that the IDA did NOT endorse around $40.7bn of data centre and technology proposals considered "
                   "premature or overly speculative; that 90 data centres are operating in NSW; that data centre "
                   "investment has grown 65% per year on average over three years; that data centres are 12% of all "
                   "non-residential building investment in NSW; that eight data centre projects worth more than "
                   "$10bn were approved in the past year including the biggest in the Southern Hemisphere; and that "
                   "one further endorsed project is withheld for commercial sensitivity. This is the authoritative "
                   "proponent list for the NSW pipeline. ARCHIVED 2026-10-21 at data/raw/operators/nswgov/ with a "
                   "SHA-256 manifest."),
    ]

    entities = [
        dict(insert=dict(id="ENT_AMAZON_AU_CO", name="Amazon Australia Company Pty Ltd",
                         legal_name="AMAZON AUSTRALIA COMPANY PTY LTD", entity_type="other",
                         domicile="Unknown - not resolvable from public registers",
                         notes="Registered proprietor of Lot 1 DP 864615, 3 Davis Road, Wetherill Park, the site of "
                               "the Davis Road Data Centre (SSD-59416728), in the title search the applicant filed "
                               "(searched 12 October 2023; transfer AS707242; current edition dated 9 December "
                               "2022). ASIC registered the company (ACN 663 812 468) on 14 November 2022. Which "
                               "Amazon business stands behind it is not stated in any public document read; the "
                               "application's ASIC certificate for Amazon Corporate Services Pty Ltd is "
                               "restricted (RG-057).",
                         fact_status="VERIFIED", confidence="high", as_of_date=TODAY, source_id=SRC_DAVIS_TITLE)),
        # The loader registers add_sources only on an update, so the citations follow the insert.
        dict(match=dict(id="ENT_AMAZON_AU_CO"), set={},
             add_sources=[dict(id=SRC_DAVIS_TITLE, quote=davis_owner), dict(id=SRC_ASIC, quote=amazon_au)]),
        dict(match=dict(id="ENT_KNBDC"),
             set=dict(notes="The proponent structure behind the Mamre Road Data Centre Campus, which the NSW "
                            "Investment Delivery Authority's Round 1 list (27 March 2026) names as KNBDC SYD4 Pty "
                            "Ltd. ASIC's register shows KNBDC SYD4 Pty Ltd (ACN 687 904 963, registered 10 June "
                            "2025) has been named AirTrunk SYD4 Pty Ltd since 16 June 2026, and its Hold, "
                            "Intermediate Hold, FinCo and Financing Holdco companies took AirTrunk SYD4 names the "
                            "same week. The KNBDC MEL1 and MEL3 companies, three of the five Melbourne expansion "
                            "companies and KNBDC Australia Pty Ltd now carry AirTrunk names too. KNBDC AU "
                            "Development Pty Ltd (ACN 687 116 098), KNBDC AU Financing Holdco Pty Ltd (ACN 685 936 "
                            "074) and two Melbourne expansion finance companies keep their KNBDC names. The "
                            "SYD4 trustee company is NBDC Pty Ltd (ACN 606 821 452, registered 1 July 2015). The "
                            "Mamre Road title search (16 December 2025) carries a caveat by KNBDC SYD4 Pty Ltd over "
                            "land registered to ISPT Pty Limited. The register gives names and dates, not owners: "
                            "who owns these companies needs a paid ASIC extract (RG-036). CORRECTED 2026-10-22: "
                            "earlier notes called the AirTrunk link an unverified inference from the site code; the "
                            "register now records the AirTrunk name against the same company.",
                      confidence="high", as_of_date=TODAY),
             add_sources=[dict(id=SRC_ASIC, quote=f"{knbdc_syd4} | {knbdc_dev}"),
                          dict(id=SRC_MAMRE_TITLE, quote=mamre_caveat)]),
        dict(match=dict(id="ENT_EMKC"),
             set=dict(legal_name="CKTSME MANAGEMENT PTY LTD",
                      notes="Schedule 1 applicant for two consents: 51 Huntingwood Drive Data Centre (SSD-41589232, "
                            "Blacktown, 632 MW installed back-up generation, 200 hours per year) and Apollo Place "
                            "Data Centre (SSD-67407231, Lane Cove, 63.8 MW installed back-up against a 45 MW total "
                            "power cap). In both, the Department's assessment report says the applicant was "
                            "approached by a data centre operator it does not name. For Apollo Place, AirTrunk's own "
                            "SYD2 page calls the project 'Phase 5 of AirTrunk's investment within the precinct' "
                            "(RG-098). ASIC's register shows EMKC Cubed Management Pty Ltd (ACN 650 102 640, "
                            "registered 11 May 2021) has been named CKTSME Management Pty Ltd since 3 June 2025, "
                            "four months before the Apollo Place consent was determined in its former name; six "
                            "EMKC Cubed companies took CKTSME names between 30 May and 3 June 2025. Research gaps RG-064 and RG-081.",
                      as_of_date=TODAY),
             add_sources=[dict(id=SRC_ASIC, quote=emkc)]),
        dict(match=dict(id="ENT_HDI_SYD1"),
             set=dict(legal_name="HDI SYD1 PROPERTY HOLDINGS PTY LIMITED",
                      notes="Schedule 1 applicant for the DigiCo SYD1 Data Centre Expansion (SSD-69637456, City of "
                            "Sydney), which the Department's assessment report calls 'HDI SYD1 Property Holdings "
                            "Limited (DigiCo)'. ASIC's register shows the four HDI SYD1 companies carried Global "
                            "Switch names until 12 May 2025: HDI SYD1 Property Holdings Pty Limited (ACN 094 051 779, "
                            "registered 7 August 2000) was Global Switch Property (Australia) Pty Limited. The consent's 'Limited' and the register's 'Pty Limited' differ. 140.4 MW "
                            "installed back-up generation, 2,000 tonne diesel cap, and one of only four consents "
                            "carrying PUE, WUE and recycled or non-potable water provisions. CORRECTED 2026-10-22: "
                            "earlier notes called this a sixth, distinct proponent structure; the register shows it "
                            "is the company once named Global Switch Property (Australia).",
                      as_of_date=TODAY),
             add_sources=[dict(id=SRC_ASIC, quote=hdi), dict(id="SRC_SSD69637456_ASSESSMENT", quote=digico)]),
        dict(match=dict(id="ENT_WDDP"),
             set=dict(legal_name="WDDP PTY LTD",
                      notes="The instructing party and proponent named on the Western Downs Digital Park Town "
                            "Planning Report (Urbis, 14 August 2026, Report V4). ASIC's register lists WDDP Pty Ltd "
                            "(ACN 700 788 058), registered 28 July 2026, 17 days before the report's date. The "
                            "words 'Zerra' and 'AGP' appear nowhere in the lodged document; the Zerra WDDP companies "
                            "share the project acronym (ENT_ZERRA). Who owns WDDP Pty Ltd needs a paid ASIC extract "
                            "(RG-052). CORRECTED 2026-10-22: earlier notes said an ABR name search did not return "
                            "WDDP Pty Ltd; ASIC's register does.",
                      as_of_date=TODAY),
             add_sources=[dict(id=SRC_ASIC, quote=wddp)]),
        dict(match=dict(id="ENT_ZERRA"),
             set=dict(domicile="Unknown; the Australian group is registered in NSW 2000 (Sydney CBD). ASIC's register "
                               "shows two of its companies once carried AGP names; where AGP is based is not "
                               "established from a primary record.",
                      notes="Australian corporate stack, all NSW 2000 (ABR, 18 September 2026; ASIC, October 2026): "
                            "Zerra WDDP Manager Australia Pty Ltd (ACN 684 250 584, registered 5 February 2025; former "
                            "names AGP DC Manager Australia Pty Ltd and Zerra DC Manager Australia Pty Ltd; current "
                            "name from 13 August 2026, the day before the Western Downs report's date); Zerra "
                            "Investments Australia Pty Ltd (ACN 686 366 254, registered 17 April 2025; former name "
                            "AGPDC Investments Australia Pty Ltd; current name from 20 January 2026); Zerra DC Operator (Australia) "
                            "Pty Ltd (25 November 2025, business name 'Zerra DC'); Zerra Operator FinCo Pty Ltd "
                            "(5 August 2026); and Zerra WDDP Asset Manager, Zerra WDDP Investments AU and Zerra WDDP "
                            "Holdco Pty Ltd (all 10 August 2026). 'Zerra' and 'AGP' appear nowhere in the lodged Town "
                            "Planning Report, whose named instructing party is WDDP Pty Ltd. The 'Singapore-based' "
                            "description rests on trade press only (RG-050).",
                      as_of_date=TODAY),
             add_sources=[dict(id=SRC_ASIC, quote=f"{agp_manager} | {agp_invest} | {wddp_holdco}")]),
        dict(match=dict(id="ENT_ZERRA_PARENT"), set={}, add_sources=[dict(id=SRC_ASIC, quote=agp_manager)]),
        dict(match=dict(id="ENT_NINEZERO"),
             set=dict(notes="Schedule 1 applicant for the DCI Poplars Data Centre Project (Queanbeyan-Palerang "
                            "Regional), which the Department's assessment report describes as 'The Trustee for "
                            "NineZero DC Sub Trust I, trading as DCI Data Centers'. A trust is not on ASIC's "
                            "register. The register holds NineZero DC Sub TC I Pty Ltd (ACN 607 631 845, registered "
                            "13 August 2015), which the portal names as proponent of the Eastern Creek Data Centre "
                            "Expansion (SSD-21342738); no public document read says it is the trustee of Sub Trust "
                            "I. The landowner's consent letters on both applications are restricted (RG-059).",
                      as_of_date=TODAY),
             add_sources=[dict(id="SRC_SSD64287712_ASSESSMENT", quote=dci), dict(id=SRC_ASIC, quote=ninezero_tc)]),
        dict(match=dict(id="ENT_MSFT_DC_AU"),
             set=dict(legal_name="MICROSOFT DATACENTER (AUSTRALIA) PTY LIMITED"),
             add_sources=[dict(id=SRC_ASIC, quote=msft)]),
    ]

    sites = [
        dict(match=dict(id="SITE_MAMRE_ROAD"),
             set=dict(proponent="KNBDC SYD4 Pty Ltd (per NSW IDA Round 1), named AirTrunk SYD4 Pty Ltd on ASIC's "
                                "register since 16 June 2026 (ACN 687 904 963); the ABR-resolved structure is The "
                                "Trustee for KNBDC SYD4 Hold Trust / Land Trust / Intermediate Hold Trust, trustee "
                                "NBDC Pty Ltd, above KNBDC AU Development Pty Ltd and KNBDC AU Financing Holdco Pty "
                                "Ltd",
                      notes="NSW Planning Portal: 'Construction and operation of a data centre campus with a power "
                            "capacity of 1 GW including six four-storey data centre buildings'. Proposal documents "
                            "put power capacity at 1.2 GW. Six buildings, 728 cooling units, 846 diesel back-up "
                            "generators, >18,000 kL diesel storage, lithium-ion batteries, ~22.4 million litres of "
                            "water per year. Land held by IFM Investors (listed by ISPT as 'Summit'); AirTrunk "
                            "reported as prospective buyer conditional on approval of the 1 GW application. The "
                            "proponent company, KNBDC SYD4 Pty Ltd, was registered on 10 June 2025 and has been "
                            "named AirTrunk SYD4 Pty Ltd since 16 June 2026 (ASIC). The title search filed with the "
                            "EIS (16 December 2025) shows Lot 10 DP 1280592 registered to ISPT Pty Limited, the "
                            "company ASIC has named IFM Real Estate Fiduciary Pty Ltd since 24 November 2025, with a "
                            "caveat by KNBDC SYD4 Pty Ltd. EIS by Willowtree Planning, the same consultancy that "
                            "appears on the Glendenning Road pre-application documents. First Australian project "
                            "above 1 GW. CORRECTED 2026-10-22: earlier notes said the proponent's sponsor was not "
                            "publicly identified anywhere."),
             add_sources=[dict(id=SRC_MAMRE_TITLE, quote=f"{mamre_owner} | {mamre_caveat}"),
                          dict(id=SRC_ASIC, quote=f"{knbdc_syd4} | {ispt}")]),
        dict(match=dict(id="SITE_DAVIS_RD_CUNDALL"),
             set=dict(notes="SCHEDULE 1 APPLICANT ON THE SIGNED CONSENT: Cundall Johnston and Partners Pty Ltd, the "
                            "consulting engineers whose name is already in the project title. The Department's "
                            "assessment report says Cundall 'acts on behalf of a global data centre operator' it does "
                            "not name. The title search the applicant filed (12 October 2023) shows the land, Lot 1 "
                            "DP 864615, registered to Amazon Australia Company Pty Ltd, a company ASIC registered on "
                            "14 November 2022. The same application carries an access-restricted 'ASIC certificate "
                            "Amazon Corporate Services Pty Ltd' and a restricted landowner's consent letter "
                            "(RG-057)."),
             add_sources=[dict(id=SRC_DAVIS_TITLE, quote=davis_owner)]),
        dict(match=dict(id="SITE_APOLLO_PLACE"),
             set=dict(notes="SCHEDULE 1 APPLICANT ON THE SIGNED CONSENT: EMKC Cubed Management Pty Ltd, which also "
                            "holds the 51 Huntingwood Drive consent in Blacktown. The Department's assessment report "
                            "says the applicant 'has been approached by a data centre operator (the end user)' that "
                            "operates the co-located Lane Cove West Data Centre. AirTrunk's own SYD2 page calls "
                            "Apollo Place 'Phase 5 of AirTrunk's investment within the precinct' (RG-098). ASIC's "
                            "register shows EMKC Cubed Management Pty Ltd had been named CKTSME Management Pty Ltd "
                            "since 3 June 2025, four months before the consent was determined on 9 October 2025. "
                            "CORRECTED 2026-10-22: earlier notes placed 51 Huntingwood Drive in Lane Cove."),
             add_sources=[dict(id="SRC_OP_AIRTRUNK_SYD2_SYDNEY_NORTH", quote=phase5),
                          dict(id=SRC_ASIC, quote=emkc)]),
        dict(match=dict(id="SITE_51_HUNTINGWOOD"),
             set=dict(notes="SCHEDULE 1 APPLICANT ON THE SIGNED CONSENT: EMKC Cubed Management Pty Ltd, named CKTSME "
                            "Management Pty Ltd on ASIC's register since 3 June 2025. The Department's assessment "
                            "report says the applicant 'was approached by a data centre operator' whose assets include "
                            "'the Huntingwood Data Centre located nearby to the site at 24 Healey Circuit, "
                            "Huntingwood'; it does not name the operator. This consent carries the largest installed "
                            "back-up generation capacity in the sample at 632 MW (RG-064)."),
             add_sources=[dict(id="SRC_SSD41589232_ASSESSMENT", quote=healey)]),
    ]

    land_events = [
        dict(match=dict(site_id="SITE_MAMRE_ROAD", event_type="option"),
             set=dict(notes="ISPT lists the property as 'Summit', masterplanned for 245,000 sqm. Reported value of "
                            "the wider AirTrunk commitment exceeds A$5bn. The title search filed with the EIS (16 "
                            "December 2025) shows Lot 10 DP 1280592 registered to ISPT Pty Limited, named IFM Real "
                            "Estate Fiduciary Pty Ltd on ASIC's register since 24 November 2025, with a caveat by "
                            "KNBDC SYD4 Pty Ltd, the company named AirTrunk SYD4 Pty Ltd since 16 June 2026. A "
                            "caveat records a claimed interest in land; the search does not say what the interest "
                            "is, so the option itself still rests on the media report (RG-005)."),
             add_sources=[dict(id=SRC_MAMRE_TITLE, quote=f"{mamre_owner} | {mamre_caveat}")]),
    ]

    for ref in unnamed_refs:
        if ref["id"] == "SRC_SSD10101987_ASSESSMENT":
            ref["quote"] = f"{ref['quote']} | {asset_numbers}"
    metrics = [
        dict(insert=dict(as_of="2026-10", scope="NSW", metric_name="nsw_dc_consents_applicant_acts_for_unnamed_operator",
                         value=float(len(UNNAMED)), unit="count", basis="actual", notes=METRIC_NOTES,
                         fact_status="VERIFIED", confidence="high", as_of_date=TODAY,
                         source_id=unnamed_refs[0]["id"]),
             add_sources=unnamed_refs),
    ]

    age_line = "; ".join(f"{a[1]} {a[2]} for {a[0]} ({a[4]} years)" for a in ages)
    young = ", ".join(f"{a[1]} ({a[0]}, {a[4]} years)" for a in under_three)
    gaps = [
        dict(match=dict(id=55),
             set=dict(status="resolved", resolved_date=TODAY, fact_status="VERIFIED", confidence="high",
                      as_of_date=TODAY,
                      notes="RESOLVED 2026-10-22 from ASIC's Company Dataset (SRC_ASIC_COMPANIES_202610), with a "
                            "correction. Registration dates for the companies holding the 21 determined consents "
                            "whose applicant is a company (trusts are not on the register), and how long each had "
                            "existed when its consent was determined: " + age_line + ". " + (f"Only one was under three years old: {young}" if len(under_three) == 1 else
                                   f"Only {len(under_three)} were under three years old: {young}") + ". So the claim in this question's earlier "
                            "notes, that the legal person carrying a consent is usually a purpose-built entity with "
                            "no operating history, does not hold: most consent holders are long-established "
                            "consultancies, developers and operators. The pattern the assessment reports show is "
                            "different: in 9 of 22 consents an established consultancy or developer applies for an "
                            "operator the report does not name (metric "
                            "nsw_dc_consents_applicant_acts_for_unnamed_operator). Fresh vehicles do appear in the "
                            "newest and largest proposals, which are not yet determined: KNBDC SYD4 Pty Ltd (Mamre "
                            "Road, registered 10 June 2025, now AirTrunk SYD4), WDDP Pty Ltd (Western Downs, 28 July "
                            "2026) and Project Garden 1 Pty Ltd (Brookhollow Avenue, 3 February 2025)."),
             add_sources=[SRC_ASIC]),
        dict(match=dict(id=21),
             set=dict(status="in_progress", as_of_date=TODAY,
                      notes="ADVANCED 2026-10-22. ASIC's register shows KNBDC SYD4 Pty Ltd (ACN 687 904 963, "
                            "registered 10 June 2025) has been named AirTrunk SYD4 Pty Ltd since 16 June 2026, as "
                            "have its Hold, Intermediate Hold, FinCo and Financing Holdco companies, so the AirTrunk "
                            "link this question asked about is now on a primary record. The title search filed with "
                            "the EIS shows Lot 10 DP 1280592 registered to ISPT Pty Limited (named IFM Real Estate "
                            "Fiduciary Pty Ltd since 24 November 2025) with a caveat by KNBDC SYD4 Pty Ltd. The "
                            "landowner's consent letters from IFM, GPT and Gibb Group are restricted on the portal. "
                            "Still open: shareholders, directors and ultimate parent, which need a paid ASIC extract "
                            "(docs/requests/PAID-SEARCHES.md), and what interest the caveat protects. Earlier: the ABR "
                            "resolves the trust stack (Hold, Land and Intermediate Hold trusts, trustee NBDC Pty "
                            "Ltd)."),
             add_sources=[dict(id=SRC_ASIC, quote=knbdc_syd4), dict(id=SRC_MAMRE_TITLE, quote=mamre_caveat)]),
        dict(match=dict(id=36),
             set=dict(status="in_progress", as_of_date=TODAY,
                      notes="ADVANCED 2026-10-22. ASIC's register names, dates and former names for the whole stack: "
                            "the KNBDC SYD4, MEL1 and MEL3 companies and three of five Melbourne expansion companies "
                            "now carry AirTrunk names; KNBDC AU Development Pty Ltd, KNBDC AU Financing Holdco Pty "
                            "Ltd and two Melbourne expansion finance companies keep theirs; NBDC Pty "
                            "Ltd was registered on 1 July 2015. Directors, shareholders and registered charges still "
                            "need paid extracts; the first to buy is AirTrunk SYD4 Pty Ltd "
                            "(docs/requests/PAID-SEARCHES.md). Supersedes the ownership half of RG-021."),
             add_sources=[SRC_ASIC]),
        dict(match=dict(id=35),
             set=dict(as_of_date=TODAY,
                      notes="ADVANCED 2026-10-22. Applicants now on the record: Project Apollo, Project Pluto and "
                            "Project Duke = Goodman Property Services (Aust) Pty Limited (the Duke assessment report "
                            "and the portal); KC1 = CDC Data Centres Pty Ltd (its scoping report); Road 1 = Stockland "
                            "Development Pty Limited (the portal and its EIS); Grand Avenue = Equinix Hyperscale 2 "
                            "(SY10); Talavera Road = Macquarie Data Centres; NEXTDC S4 = NEXTDC; Roberts Road = "
                            "Canberra Data Centres; DigiCo SYD1 = HDI SYD1 Property Holdings (formerly Global Switch "
                            "Property (Australia)); DCI Poplars = the NineZero trust trading as DCI Data Centers; "
                            "43-61 Turner Road = ARUP; 51 Huntingwood Drive and Apollo Place = EMKC Cubed Management "
                            "(now CKTSME Management). STILL UNRESOLVED: Project Echidna, whose applicant ARUP Australia "
                            "'acts on behalf of a multinational data centre operation' the assessment report does not "
                            "name; and Project Mars, whose portal record names no applicant and whose owner's consent "
                            "letter is restricted. The landowner's consent letters on Project Duke and Project Mars "
                            "are restricted too; they are in the drafted GIPA request (docs/requests/)."),
             add_sources=[SRC_ASIC]),
        dict(match=dict(id=37),
             set=dict(status="in_progress", as_of_date=TODAY,
                      notes="WORKED 2026-10-21. The owner's consent letter (owners-consent-6713) answers 401: "
                            "restricted. The Appendix 03 title documents are a ZIP of 20 scanned plans and land "
                            "dealings with no machine-readable text and no current title search, so the registered "
                            "proprietor of Lot 2 DP 1137162 is not established. The assessment report calls the "
                            "applicant, Lehr, 'an engineering and design consultancy' and does not mention an "
                            "operator at all. Next: a paid NSW title search for Lot 2 DP 1137162, and the GIPA "
                            "request for the consent letter (docs/requests/). Earlier: the portal attachment list is "
                            "reachable via the node JSON; draft conditions and EPA comments also answered 401."),
             add_sources=[]),
        dict(match=dict(id=50),
             set=dict(as_of_date=TODAY,
                      notes="ADVANCED 2026-10-22. ASIC's register gives the AGP link a primary record: a former name "
                            "of Zerra WDDP Manager Australia Pty Ltd (registered 5 February 2025) is AGP DC Manager "
                            "Australia Pty Ltd, and a former name of Zerra Investments Australia Pty Ltd (registered "
                            "17 April 2025) is AGPDC Investments Australia Pty Ltd. Where AGP is based, and who owns the Australian companies, still need "
                            "paid extracts. Earlier: the ABR resolves six Zerra entities, all NSW 2000; the lodged "
                            "application names WDDP Pty Ltd and never mentions Zerra or AGP."),
             add_sources=[dict(id=SRC_ASIC, quote=f"{agp_manager} | {agp_invest}")]),
        dict(match=dict(id=52),
             set=dict(status="in_progress", as_of_date=TODAY,
                      notes="ADVANCED 2026-10-22. ASIC's register: WDDP Pty Ltd (ACN 700 788 058) registered 28 July "
                            "2026, 17 days before the Town Planning Report's date; Zerra WDDP Manager Australia renamed "
                            "to its current name on 13 August 2026, the day before; Zerra WDDP Asset Manager, Zerra "
                            "WDDP Investments AU and Zerra WDDP Holdco all registered 10 August 2026. Directors, "
                            "shareholders and ultimate parent still need paid extracts, first WDDP Pty Ltd "
                            "(docs/requests/PAID-SEARCHES.md)."),
             add_sources=[dict(id=SRC_ASIC, quote=f"{wddp} | {wddp_holdco}")]),
        dict(match=dict(id=57),
             set=dict(status="in_progress", as_of_date=TODAY,
                      notes="ADVANCED 2026-10-22. The title search the applicant filed (searched 12 October 2023) "
                            "shows the land, Lot 1 DP 864615, registered to Amazon Australia Company Pty Ltd, which "
                            "ASIC registered on 14 November 2022; the title's current edition is dated 9 December "
                            "2022. The Department's assessment report says Cundall 'acts on behalf of a global data "
                            "centre operator' it does not name. The ASIC certificate for Amazon Corporate Services "
                            "Pty Ltd and the landowner's consent letter both answer 401, and are in the drafted GIPA "
                            "request (docs/requests/GIPA-001-ownership-documents.md). Amazon's role as landowner is "
                            "now on a primary record; its role as operator is not. Also restricted on Roberts Road "
                            "(SSD-10330): the CDC response to a warning letter (RG-058)."),
             add_sources=[dict(id=SRC_DAVIS_TITLE, quote=davis_owner)]),
        dict(match=dict(id=59),
             set=dict(status="in_progress", as_of_date=TODAY,
                      notes="ADVANCED 2026-10-22. The DCI Poplars assessment report calls the applicant 'The Trustee "
                            "for NineZero DC Sub Trust I, trading as DCI Data Centers'. ASIC's register holds "
                            "NineZero DC Sub TC I Pty Ltd (registered 13 August 2015) and Sub TC II (11 April 2017), "
                            "and the portal names Sub TC I as proponent of the Eastern Creek Data Centre Expansion; "
                            "no public document read says Sub TC I is the trustee of Sub Trust I. The landowner's "
                            "consent letters on both applications answer 401 and are in the drafted GIPA request."),
             add_sources=[dict(id="SRC_SSD64287712_ASSESSMENT", quote=dci), dict(id=SRC_ASIC, quote=ninezero_tc)]),
        dict(match=dict(id=64),
             set=dict(status="in_progress", as_of_date=TODAY,
                      notes="ADVANCED 2026-10-22. EMKC Cubed Management Pty Ltd has been named CKTSME Management Pty "
                            "Ltd on ASIC's register since 3 June 2025. In both its consents the assessment report says "
                            "it was approached by a data centre operator it does not name; for Apollo Place, "
                            "AirTrunk's own SYD2 page calls the project 'Phase 5 of AirTrunk's investment within the "
                            "precinct' (RG-098), and for 51 Huntingwood Drive the operator's assets include 'the "
                            "Huntingwood Data Centre ... at 24 Healey Circuit, Huntingwood'. HDI SYD1 Property "
                            "Holdings was named Global Switch Property (Australia) until 12 May 2025, and the Department "
                            "calls it DigiCo. The landowner's consent letters on Apollo Place and 51 Huntingwood "
                            "Drive answer 401 and are in the drafted GIPA request. Still open: shareholders and "
                            "directors (paid extracts), and which operator holds the 51 Huntingwood consent."),
             add_sources=[dict(id=SRC_ASIC, quote=f"{emkc} | {hdi}"),
                          dict(id="SRC_SSD41589232_ASSESSMENT", quote=healey)]),
        dict(match=dict(id=81),
             set=dict(status="in_progress", as_of_date=TODAY,
                      notes="ADVANCED 2026-10-22 (with RG-064 and RG-059). ASIC's register gives names, dates and "
                            "former names: EMKC Cubed Management is now CKTSME Management (3 June 2025); HDI SYD1 "
                            "Property Holdings was Global Switch Property (Australia) (renamed 12 May 2025); NineZero "
                            "DC Sub TC I Pty Ltd exists (13 August 2015). Beneficial ownership still needs paid "
                            "extracts. Note EMKC holds TWO consents and 'HDI SYD1' is a per-site holding company, so "
                            "the structures are site-specific."),
             add_sources=[SRC_ASIC]),
        dict(match=dict(id=5),
             set=dict(status="in_progress", as_of_date=TODAY,
                      notes="ADVANCED 2026-10-22. The title search filed with the Mamre Road EIS (16 December 2025) "
                            "shows Lot 10 DP 1280592 at Kemps Creek registered to ISPT Pty Limited, and ASIC's "
                            "register shows ISPT Pty Ltd (ACN 064 041 283) has been named IFM Real Estate Fiduciary "
                            "Pty Ltd since 24 November 2025, which reconciles the 'ISPT' and 'IFM' accounts for that "
                            "lot. The search carries a caveat by KNBDC SYD4 Pty Ltd (now AirTrunk SYD4). Still open: "
                            "whether Lot 10 is the whole 706-752 Mamre Road site, the fund vehicle, the sale price "
                            "and the conditions precedent."),
             add_sources=[dict(id=SRC_MAMRE_TITLE, quote=mamre_owner), dict(id=SRC_ASIC, quote=ispt)]),
    ]

    pack = {
        "pack_id": "who-applies-2026-10",
        "prepared_by": "scripts/curate_who_applies.py",
        "prepared_on": TODAY,
        "sources": sources,
        "rows": {
            "entities": entities,
            "sites": sites,
            "land_events": land_events,
            "metrics": metrics,
            "research_gaps": gaps,
        },
    }
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(pack, fh, indent=1)
    print(f"wrote {OUT}: {len(UNNAMED)} consents with an unnamed operator; {len(ages)} applicant ages, "
          f"{len(under_three)} under three years")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
