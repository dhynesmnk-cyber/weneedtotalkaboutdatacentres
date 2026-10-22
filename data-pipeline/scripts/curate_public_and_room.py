#!/usr/bin/env python3
"""
Curate research batch 3, "What the public gives" and "Who is in the room" (docs/RESEARCH-PLAN.md,
story lines M3 and M4).

M3 asks whether data centres pay their own way. Free records answer more than the agenda expected:

  1. The signed NSW consents (archived in September under data/raw/nsw_planning/consents/) carry
     their own contribution conditions: what each developer must pay its council and the State
     before building starts. Recorded per consent, as each consent states it.
  2. Penrith Council's planning agreement with Microsoft, archived by scrapers/archive_pages.py
     under data/raw/councils/penrith/. The signed copy is a scan with no text, so the amount comes
     from the draft agreement and the explanatory note published beside it.
  3. The industry's grid-payment figure, traced from the inquiry transcript to the report it came
     from (Mandala, commissioned by four operators). The report's text is checked where the archive
     exists; it is a commercial report, so only its manifest is committed.
  4. The 2025-26 NSW Budget's Investment Delivery Authority, and the public servants' own evidence
     to the inquiry on what that support is and is not.

M4 asks who is in the room:

  5. The Business Council of Australia's member list, now served in full on its own page.
  6. The phantom-demand research briefing everyone cited, whose own page says who commissioned it.
  7. The ministers' diaries, the NSW lobbyist register, AusTender and buy.nsw all refused the
     crawler; each refusal is in a refused.json under data/raw/ and none was worked around.

Every quote is checked against its archive and the script refuses to write if one is missing.
Nothing is summed across consents: each contribution is recorded as its own consent states it.

Run:
    python3 scripts/curate_public_and_room.py
    python3 scripts/load_pack.py data/packs/public_and_room.json --allow-missing-source
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "data", "packs", "public_and_room.json")
RAW = os.path.join(ROOT, "data", "raw")
CONSENTS = os.path.join(RAW, "nsw_planning", "consents")
PENRITH = os.path.join(RAW, "councils", "penrith")
INQ = os.path.join(RAW, "nsw_inquiry", "text")
OPS = os.path.join(RAW, "operators")
MANDALA = os.path.join(OPS, "mandala", "Data-Centres-as-Enabling-Infrastructure")
TODAY = "2026-10-22"

SRC_CONSENTS = "SRC_NSWPORTAL_CONSENTS"
SRC_VPA_PAGE = "SRC_PENRITH_VPA"
SRC_VPA_NOTE = "SRC_PENRITH_VPA_NOTE"
SRC_VPA_DRAFT = "SRC_PENRITH_VPA_DRAFT"
SRC_MANDALA = "SRC_MANDALA_DCEI_2025"
SRC_OXEC = "SRC_OXEC_PHANTOM_2025"
SRC_GUIDE = "SRC_NSWGUIDE26"
SRC_BCA = "SRC_BCA_MEMBERS_202610"
SRC_IDA_BUDGET = "SRC_NSW_IDA_BUDGET_2025"
SRC_FIRB = "SRC_FIRB_QR_2026Q1"
SRC_DIARIES = "SRC_NSW_DIARIES_2026"
T0501, T0522, T0529 = "SRC_INQ_T_0501", "SRC_INQ_T_0522", "SRC_INQ_T_0529"

errors: list[str] = []


def spaceless(text: str) -> str:
    return re.sub(r"\s+", "", text).lower()


def text_of(path: str) -> str:
    return open(path, encoding="utf-8").read()


def in_text(path: str, quote: str) -> str:
    if spaceless(quote) not in spaceless(text_of(path)):
        errors.append(f"{os.path.relpath(path, ROOT)} does not hold {quote[:70]!r}")
    return quote


def quoted(path: str, quote: str) -> str:
    """'pN: quote' from a PDF's page-marked text, refusing a quote the archive does not hold."""
    for m in re.finditer(r"\[\[page (\d+)\]\]\n(.*?)(?=\n\[\[page \d+\]\]|\Z)", text_of(path), re.S):
        if spaceless(quote) in spaceless(m.group(2)):
            return f"p{m.group(1)}: {quote}"
    errors.append(f"{os.path.relpath(path, ROOT)} does not hold {quote[:70]!r}")
    return quote


def manifest(path: str) -> dict:
    return json.load(open(path))


def verified_pdf(base: str) -> None:
    """A PDF that is archived here must still match its manifest."""
    if os.path.exists(base + ".pdf"):
        raw = open(base + ".pdf", "rb").read()
        if hashlib.sha256(raw).hexdigest() != manifest(base + ".pdf.meta.json")["sha256"]:
            errors.append(f"{os.path.relpath(base, ROOT)}.pdf fails its SHA-256 check")


def consent(name: str) -> str:
    return os.path.join(CONSENTS, f"{name}.txt")


# (case, consent file, LGA scope, metric stem, kind, amount, the condition's own words). Read from
# every archived consent; the classification of all twenty is in CONTRIBUTION_NOTES below.
CONTRIBUTIONS = [
    ("SSD-9741", "lane_cove_west_data_centre", "NSW - Lane Cove", "local", 1426876.00,
     "a contribution under section 7.11 of the EP&A Act of $1,426,876"),
    ("SSD-53338465", "grand_avenue_data_centre_expansion_rosehill", "NSW - City of Parramatta", "local", 314528.57,
     "a contribution under section 7.11 of the EP&A Act of $314,528.57"),
    ("SSD-53338465", "grand_avenue_data_centre_expansion_rosehill", "NSW - City of Parramatta", "hpc", 234724.80,
     "Total housing and productivity contribution $234,724.80"),
    ("SSD-59416728", "davis_road_data_centre_cundall", "NSW - Fairfield City", "hpc", 625174.00,
     "Total housing and productivity contribution $625,174.00"),
    ("SSD-67407231", "apollo_place_data_centre", "NSW - Lane Cove", "local", 546544.60,
     "a contribution under section 7.11 of the EP&A Act of $546,544.60"),
    ("SSD-67407231", "apollo_place_data_centre", "NSW - Lane Cove", "hpc", 151287.31,
     "Total housing and productivity contribution $151,287.31"),
    ("SSD-68013714", "43_61_turner_road_data_centre", "NSW - Camden", "local", 8597094.07,
     "Note: At the date of this consent, the relevant monetary contribution is approximately $8,597,094.07."),
    ("SSD-69637456", "digico_syd1_data_centre_expansion", "NSW - City of Sydney", "hpc", 3568.10,
     "Total housing and productivity contribution $3,568.10"),
    ("SSD-63741210", "nextdc_s4_data_centre_horsley_park", "NSW - Fairfield City", "hpc", 1000607.00,
     "Total housing and productivity contribution $1,000,607.00"),
    ("SSD-63235720", "1_5_khartoum_road_data_centre", "NSW - City of Ryde", "local", 776297.24,
     "Total contribution amount $776,297.24"),
    ("SSD-63235720", "1_5_khartoum_road_data_centre", "NSW - City of Ryde", "hpc", 315192.70,
     "Total housing and productivity contribution $315,192.70"),
    ("SSD-69223466", "project_pluto_data_centre", "NSW - Cumberland", "local", 4506237.24,
     "a payment of a levy of $4,506,237.24"),
    ("SSD-69223466", "project_pluto_data_centre", "NSW - Cumberland", "hpc", 478501.83,
     "Total housing and productivity contribution $478,501.83"),
    ("SSD-74069708", "project_apollo_data_centre_macquarie_park", "NSW - City of Ryde", "local", 437586.24,
     "Total contribution amount $437,586.24"),
    ("SSD-74069708", "project_apollo_data_centre_macquarie_park", "NSW - City of Ryde", "hpc", 471542.50,
     "Total housing and productivity contribution $471,542.50"),
    ("SSD-73761707", "glendenning_road_data_centre", "NSW - Blacktown", "hpc", 816286.25,
     "Total housing and productivity contribution $816,286.25"),
]
# Consents whose local contribution is a rate, not an amount, and the condition that sets it.
RATE_ONLY = [
    ("SSD-59416728", "davis_road_data_centre_cundall",
     "a payment of a levy of 1 % of the proposed cost of carrying out the development must be paid to Council "
     "under section 7.12 of the EP&A Act"),
    ("SSD-63741210", "nextdc_s4_data_centre_horsley_park",
     "a payment of a levy of 1% of the proposed cost of carrying out the development"),
]
CONTRIBUTION_NOTES = (
    "Read on 2026-10-22 from the 20 signed consents archived on 2026-09-18 (SRC_NSWPORTAL_CONSENTS). Each "
    "condition requires payment before the first construction certificate, indexed from the consent date. "
    "Local contributions under s7.11 or s7.12 of the EP&A Act go to the council under its contributions plan; "
    "the housing and productivity contribution (HPC) goes to the State under the HPC Order 2024 and applies "
    "only to consents determined after it commenced. Davis Road and NEXTDC S4 set a local levy of 1% of the "
    "cost of development with no dollar figure; 1-5 Khartoum Road must also enter a planning agreement on the "
    "terms of an offer dated 24 November 2024. Microsoft's Kemps Creek campus pays through a planning agreement "
    "with Penrith Council (metric penrith_msft_vpa_contribution_draft). No contribution condition was found in "
    "the consents for 51 Huntingwood Drive, DCI Poplars, Project Echidna, Station Road, Talavera Road, "
    "Macquarie Park, Roberts Road or Glendenning Road's local component. Amounts are not summed: they are set "
    "at different dates under different plans."
)


def main() -> int:
    # --- contributions in the consents ------------------------------------------------------------
    contribution_rows = []
    for case, f, scope, kind, amount, q in CONTRIBUTIONS:
        quote = in_text(consent(f), q)
        what = ("local infrastructure contribution to the council" if kind == "local"
                else "housing and productivity contribution to the State")
        contribution_rows.append(dict(
            insert=dict(as_of=TODAY, scope=scope,
                        metric_name=f"{case.lower().replace('-', '')}_{'local_contribution' if kind == 'local' else 'housing_productivity_contribution'}",
                        value=amount, unit="AUD", basis="actual",
                        notes=f"{case}: the {what} its signed consent requires before construction, as stated in "
                              f"the consent (indexed from the consent date). " + CONTRIBUTION_NOTES,
                        fact_status="VERIFIED", source_id=SRC_CONSENTS, confidence="high", as_of_date=TODAY),
            add_sources=[dict(id=SRC_CONSENTS, quote=f"{case}: {quote}")]))
    rates = [f"{case}: {in_text(consent(f), q)}" for case, f, q in RATE_ONLY]
    khartoum_pa = in_text(consent("1_5_khartoum_road_data_centre"),
                          "the Applicant must enter into a PA with the Council in accordance with")

    # --- Penrith's planning agreement with Microsoft ----------------------------------------------
    note_base = os.path.join(PENRITH, "Explanatory_Note_1")
    draft_base = os.path.join(PENRITH, "Penrith_City_Council_VPA_-_3_February_2022_FINAL301930683.1_1")
    exec_base = os.path.join(PENRITH, "Executed_Voluntary_Planning_Agreement_-_Microsoft_Datacenter")
    page = os.path.join(PENRITH, "vpa-microsoft-datacenter.txt")
    for b in (note_base, draft_base, exec_base):
        verified_pdf(b)
    vpa_amount = quoted(note_base + ".txt", "The Planning Agreement requires the Developer to pay the monetary "
                                            "contribution of $8,423,505.96 before the issue of the first "
                                            "construction certificate for the proposed development.")
    vpa_no_plan = quoted(note_base + ".txt", "There is no s.7.11 Contributions Plan applying to the Subject Land.")
    vpa_draft = quoted(draft_base + ".txt", "The Developer will pay to Council a monetary contribution of "
                                            "$8,423,505.96 or an amount calculated in accordance with the "
                                            "following formula, whichever is the greater")
    vpa_executed = in_text(page, "At Council's Ordinary Meeting of 29 May 2023, Council endorsed the VPA for "
                                 "execution. The VPA was executed on 7 June 2023.")
    if spaceless(text_of(exec_base + ".txt")).replace("[[page", "").strip("0123456789]"):
        errors.append("the executed VPA now has text; read its amount instead of the draft's")

    # --- the industry's grid figure and the report behind it --------------------------------------
    dca_claim = in_text(os.path.join(INQ, "transcript_2026-05-01.txt"),
                        "Data centre operators will pay $10.3 billion in energy infrastructure to 2030, and $1.1 "
                        "billion of that is excess capacity available for public use. Data centre operators do "
                        "not receive subsidies or tax incentives.")
    # Mandala's report is commercial, so only its manifest is committed. Its quotes are written here with
    # their pages, and checked against the text wherever the archive exists, so every machine builds
    # the same pack.
    mandala = dict(
        totals="p6: Data centres have invested $3.1 billion in grid infrastructure since 2020, with a further $7.2 "
               "billion forecast by 2030. This includes $1.1 billion of excess capacity for communities and other "
               "industries.",
        excess_past="p22: Between 2020 and 2025, $500 million (or 15 per cent of total investment) represented excess "
                    "capacity.",
        government="p22: By comparison, the Australian Government has committed $10.3 billion of funding for vital grid "
                   "electricity infrastructure to 2030.",
        data="p21: Source: Data from select data centre operators; Expert interviews; Mandala analysis.",
        commissioned="p2: The analysis in this report was commissioned for Data Centres Australia by AirTrunk, Amazon "
                     "Web Services, CDC, and NEXTDC and prepared by Mandala.",
    )
    if os.path.exists(MANDALA + ".txt"):
        verified_pdf(MANDALA)
        for key, q in mandala.items():
            page, body = q.split(": ", 1)
            if quoted(MANDALA + ".txt", body) != q:
                errors.append(f"Mandala's report does not hold the {key} quote on {page}")
        if len(re.findall(r"10\.3 billion", text_of(MANDALA + ".txt"))) != 1:
            errors.append("Mandala's report now uses '$10.3 billion' more than once; re-read it")
    else:
        print("note: the Mandala archive is not on this machine; its quotes are carried as written", file=sys.stderr)
    causer = in_text(os.path.join(INQ, "transcript_2026-05-29.txt"),
                     "in New South Wales, the customer who caused network costs pays for them.")
    # The transcript has a stray dash character before "until", so the sentence is quoted in two parts.
    no_commit = " ... ".join(in_text(os.path.join(INQ, "transcript_2026-05-22.txt"), q) for q in (
        "we don't invest in new equipment, new assets, long lead items or anything",
        "until we have that full commitment."))

    # --- what the public gives instead of cash ------------------------------------------------------
    t0522 = os.path.join(INQ, "transcript_2026-05-22.txt")
    not_financial = in_text(t0522, "The one thing that we don't contemplate is government participation "
                                   "financially.")
    ida_team = in_text(t0522, "There is a team that supports the Investment Delivery Authority in terms of "
                              "assessing applications and progressing facilitation and support for those endorsed "
                              "projects, and the team that does that sits within my team in the Premier's "
                              "Department.")
    no_minister = in_text(t0522, "There is no Minister for data centres.")
    met_dca = in_text(t0522, "met with Data Centres Australia and talked to them about the consultation paper")
    direct_reps = in_text(t0522, "it's also apparent that a lot of those organisations have made direct "
                                 "representations to different people in government.")
    budget_page = os.path.join(OPS, "nswgov", "investment-delivery-authority-to-turbocharge-business-investment-nsw.txt")
    ida_budget = in_text(budget_page, "The Minns Labor Government is investing $17.7 million in the 2025-26 Budget "
                                      "to establish and support the work of an Investment Delivery Authority.")
    ida_taskforce = in_text(budget_page, "A multi-agency Investment Taskforce, in Investment NSW under the Premier’s "
                                         "Department, will support the Authority’s work.")
    guide = os.path.join(OPS, "nswgov", "id0073_nsw-data-centre_guidelines.txt")
    verified_pdf(os.path.join(OPS, "nswgov", "id0073_nsw-data-centre_guidelines"))
    concierge = quoted(guide, "Creating a concierge function within DPHI, working with the planning assessment "
                              "team, that understands data centre technologies and needs")
    guide_oe = quoted(guide, "Oxford Economics, which prepared AEMO’s forecast on data centres, estimates 6 in "
                             "every 7 megawatts (MW) of data centre connection requests are phantom demand.")
    guide_oe_ref = quoted(guide, "Oxford Economics, Estimating Data Centre ‘Phantom Demand’, Oxford Economics, 2025.")

    # --- FIRB ---------------------------------------------------------------------------------------
    firb = os.path.join(OPS, "firb_files", "quarterly-report-jan-mar-2026")
    verified_pdf(firb)
    firb_suppressed = quoted(firb + ".txt", "Any data that may enable the identification of a particular person or "
                                            "organisation has been suppressed to preserve confidentiality.")
    if re.search(r"data cent", text_of(firb + ".txt"), re.I):
        errors.append("the FIRB quarterly report now mentions data centres; the notes say it does not")

    # --- who commissioned the phantom-demand briefing ------------------------------------------------
    oe = os.path.join(OPS, "oxfordeconomics", "estimating-data-centre-phantom-demand.txt")
    oe_aws = in_text(oe, "This research briefing was commissioned by AWS. The analysis and findings are Oxford "
                         "Economics.")
    oe_aemo = in_text(oe, "In response, AEMO commissioned Oxford Economics to develop independent forecasts of "
                          "electricity consumption by data centres in Australia.")
    oe_six = in_text(oe, "6 in every 7 MWs of connection requests are estimated to be ‘phantom demand’.")
    bca_sub = os.path.join(RAW, "nsw_inquiry", "submissions", "BCA_116.txt")
    bca_cites = in_text(bca_sub, "Oxford Economics, Surging Data Centre Connection Requests Drive Phantom Demand")
    in_text(oe, "Surging data centre connection requests drive phantom demand for power")
    dca_cites = in_text(t0522, "Data Centres Australia and the Business Council of Australia have both cited Oxford "
                               "Economics phantom demandresearch")

    # --- the BCA's members ----------------------------------------------------------------------------
    bca = os.path.join(OPS, "bca", "membership.txt")
    bca_lines = [ln.strip() for ln in text_of(bca).splitlines()]
    members_at = max(i for i, ln in enumerate(bca_lines) if ln.startswith("*********"))
    members = []
    for ln in bca_lines[members_at + 1:]:
        if re.search(r"\.(com|au|org|net|tech|technology|healthcare|edu|gov)\b|^www\.|/", ln) and " " not in ln:
            continue
        if not ln or re.search(r"Join|Contact|Membership|©|Privacy|Subscribe|Newsroom", ln):
            if members and not ln:
                continue
            break
        members.append(ln)
    if len(members) != 130:
        errors.append(f"the BCA page now lists {len(members)} members, not 130; re-read it")
    member_set = set(members)
    # BCA member name -> the database entity it is, and why that entity is in the database.
    BCA_MATCHES = [
        ("AirTrunk", "ENT_AIRTRUNK", "data centre operator"),
        ("Amazon", "ENT_AWS", "hyperscaler; the BCA lists it as 'Amazon'"),
        ("Google", "ENT_GOOGLE", "hyperscaler"),
        ("Microsoft", "ENT_MICROSOFT", "hyperscaler"),
        ("Meta", "ENT_META", "hyperscaler"),
        ("Blackstone", "ENT_BLACKSTONE", "majority owner of AirTrunk"),
        ("Goodman", "ENT_GOODMAN", "applicant for three NSW data centre consents"),
        ("Stockland", "ENT_STOCKLAND", "applicant for two NSW data centre consents"),
        ("TransGrid", "ENT_TRANSGRID", "the transmission network data centres connect to"),
        ("Endeavour Energy", "ENT_ENDEAVOUR", "the distribution network for western Sydney's data centres"),
        ("Fujitsu", "ENT_FUJITSU_AU", "data centre operator"),
        ("Telstra", "ENT_TELSTRA", "telecommunications carrier"),
        ("Origin Energy", "ENT_ORIGIN", "electricity retailer and generator"),
        ("Tata Consultancy Services", "ENT_TCS", "partner in the HyperVault data centre venture"),
    ]
    for name, _, _ in BCA_MATCHES:
        if name not in member_set:
            errors.append(f"the BCA page no longer lists {name!r}")
    for absent in ("NEXTDC", "CDC", "Equinix", "Macquarie Technology Group", "Data Centres Australia"):
        if any(absent.lower() in m.lower() for m in members):
            errors.append(f"the BCA page now lists {absent!r}; the notes say it does not")
    bca_line = lambda name: in_text(bca, name)  # noqa: E731
    india_forum = in_text(os.path.join(OPS, "bca", "about.txt"), "Australia-India CEO Forum")

    # --- the diaries are published, and closed to crawlers --------------------------------------------
    diaries_page = os.path.join(OPS, "nswgov", "2026-ministers-diary-disclosures.txt")
    diaries = in_text(diaries_page, "Minister for Planning and Public Spaces")
    refused = {}
    for d in ("registers/nsw_ministers_diaries", "registers/nsw_lobbyists", "registers/austender",
              "registers/buynsw"):
        path = os.path.join(RAW, d, "refused.json")
        if not os.path.exists(path):
            errors.append(f"no refusal recorded at {d}")
            continue
        refused[d] = json.load(open(path))
    if len(refused.get("registers/nsw_ministers_diaries", {})) != 30:
        errors.append("expected 30 ministers' diary refusals")

    if errors:
        print("refusing to write; fix these first:", file=sys.stderr)
        for e in errors:
            print(f"  {e}", file=sys.stderr)
        return 1

    def archived(base: str, ext: str = ".pdf") -> str:
        m = manifest(base + ext + ".meta.json")
        return f"sha256 {m['sha256'][:12]}, {m['bytes']:,} bytes"

    sources = [
        dict(id=SRC_VPA_NOTE, title="Explanatory Note - Draft Planning Agreement, Penrith City Council and Microsoft "
                                    "Datacenters (Australia) Pty Limited",
             publisher="Penrith City Council and Microsoft (prepared jointly)",
             url=manifest(note_base + ".pdf.meta.json")["url"], doc_type="primary_government", published="2023-03-09",
             accessed=TODAY, credibility="A",
             notes="Published with the draft agreement for notification (9 March to 6 April 2023). States the "
                   "$8,423,505.96 monetary contribution, payable before the first construction certificate, for "
                   "land, embellishment and public works, calculated by the Mamre Road East Precinct s7.11 rates "
                   f"because no contributions plan applied to the land. ARCHIVED {TODAY} at "
                   f"data/raw/councils/penrith/ ({archived(note_base)}); PDF not committed, text is."),
        dict(id=SRC_VPA_DRAFT, title="Planning Agreement, Penrith City Council and Microsoft (draft notified 2023, "
                                     "file dated 3 February 2022)",
             publisher="Penrith City Council", url=manifest(draft_base + ".pdf.meta.json")["url"],
             doc_type="primary_government", published="2022-02-03", accessed=TODAY, credibility="A",
             notes="Clause 6.1: $8,423,505.96 or that amount indexed by CPI, whichever is greater. The council "
                   "publishes the executed agreement (signed 7 June 2023) beside it, but the executed copy is a "
                   "scan with no text, so whether its figure is the same has not been read. ARCHIVED "
                   f"{TODAY} ({archived(draft_base)}); the executed copy too ({archived(exec_base)}), its text "
                   "empty."),
        dict(id=SRC_VPA_PAGE, title="Voluntary Planning Agreement - Microsoft Datacenter (Your Say Penrith)",
             publisher="Penrith City Council", url="https://yoursaypenrith.com.au/vpa-microsoft-datacenter",
             doc_type="primary_government", published="2023-06-07", accessed=TODAY, credibility="A",
             notes="Voluntary Planning Agreement between Penrith City Council and Microsoft Datacenter (Australia) "
                   "Pty Ltd for Lot 2 DP 1271142, 769 Mamre Road, Kemps Creek, within the approved industrial "
                   "estate 'The Yards' at 657-769 Mamre Road. Publicly notified 9 March to 6 April 2023; endorsed by "
                   "Council at its Ordinary Meeting of 29 May 2023; executed 7 June 2023. Purpose: to collect "
                   "monetary contributions for the future development of a data centre, to support delivery of "
                   "infrastructure including open space and landscaping embellishment within the Mamre Road "
                   f"Precinct. ARCHIVED {TODAY} at data/raw/councils/penrith/ with the three documents it links "
                   "(SRC_PENRITH_VPA_NOTE, SRC_PENRITH_VPA_DRAFT; the executed copy is a scan)."),
        dict(id=SRC_OXEC, title="Estimating Data Centre 'Phantom Demand' (research briefing, 21 November 2025)",
             publisher="Oxford Economics Australia",
             url=manifest(os.path.join(OPS, "oxfordeconomics", "estimating-data-centre-phantom-demand.html.meta.json"))["url"],
             doc_type="market_research", published="2025-11-21", accessed=TODAY, credibility="B",
             notes="Subtitled 'Surging data centre connection requests drive phantom demand for power'. Finds 6 in "
                   "every 7 MW of the 44 GW of connection requests AEMO received are 'phantom demand'. The page says "
                   "AEMO separately commissioned Oxford Economics to forecast data centre electricity use, and that "
                   "'This research briefing was commissioned by AWS.' Cited by the BCA (Submission No 116, under its "
                   "subtitle), Data Centres Australia and the NSW Data Centre Guidelines. ARCHIVED "
                   f"{TODAY} at data/raw/operators/oxfordeconomics/."),
        dict(id=SRC_BCA, title="Business Council of Australia - Membership (Our Members)",
             publisher="Business Council of Australia", url="https://www.bca.com.au/membership/",
             doc_type="industry_body", published=None, accessed=TODAY, credibility="A",
             notes="The BCA's own member directory, served in full to the research crawler on 2026-10-22 (it returned "
                   "a challenge page in September): 130 members, each with its web address. Its data-centre-related "
                   "members: AirTrunk, Amazon, Google, Microsoft, Meta, Blackstone, Goodman, Stockland, TransGrid, "
                   "Endeavour Energy, Fujitsu, Telstra, Origin Energy and Tata Consultancy Services. Not listed: "
                   "NEXTDC, CDC, Equinix, Macquarie Technology Group or Data Centres Australia. ARCHIVED "
                   f"{TODAY} at data/raw/operators/bca/ with the about page."),
        dict(id=SRC_IDA_BUDGET, title="Investment Delivery Authority to turbocharge business investment in NSW "
                                      "(ministerial media release, 23 June 2025)",
             publisher="NSW Government - the Premier, Treasurer, Minister for Innovation, Science and Technology, "
                       "Minister for Planning and Public Spaces",
             url="https://www.nsw.gov.au/ministerial-releases/investment-delivery-authority-to-turbocharge-business-investment-nsw",
             doc_type="primary_government", published="2025-06-23", accessed=TODAY, credibility="A",
             notes="$17.7 million in the 2025-26 Budget to establish and support the Investment Delivery Authority; "
                   "about 30 large projects a year; projects over $1 billion; a multi-agency Investment Taskforce in "
                   f"Investment NSW under the Premier's Department. ARCHIVED {TODAY} at data/raw/operators/nswgov/."),
        dict(id=SRC_FIRB, title="Quarterly report on foreign investment - 1 January to 31 March 2026",
             publisher="Australian Government, The Treasury (Foreign Investment)",
             url=manifest(firb + ".pdf.meta.json")["url"], doc_type="primary_government", published="2026-05-29",
             accessed=TODAY, credibility="A",
             notes="311 commercial proposals approved in the quarter, 97 of them with conditions. Reports by sector "
                   "and source country only; 'Any data that may enable the identification of a particular person "
                   "or organisation has been suppressed'. Does not mention data centres. ARCHIVED "
                   f"{TODAY} ({archived(firb)}); PDF not committed."),
        dict(id=SRC_DIARIES, title="2026 ministers' diary disclosures (NSW Cabinet Office index page)",
             publisher="NSW Government - The Cabinet Office",
             url="https://www.nsw.gov.au/departments-and-agencies/cabinet-office/access-to-information/ministers-diary-disclosures/2026-ministers-diary-disclosures",
             doc_type="primary_government", published="2026-07", accessed=TODAY, credibility="A",
             notes="Lists each minister's quarterly diary disclosure for 2026. The disclosures themselves sit under "
                   "/sites/default/files/noindex/, which nsw.gov.au's robots.txt closes to crawlers; the 30 for the "
                   "Premier, Treasurer and the Planning, Energy and Industry ministers from January 2025 to June 2026 "
                   "were not fetched (data/raw/registers/nsw_ministers_diaries/refused.json; docs/requests/"
                   f"DOWNLOADS.md). The index pages for 2025 and 2026 ARCHIVED {TODAY}."),
        # Re-declared in full because the loader upserts sources; the notes gain the archive line and the
        # finding about the research it cites.
        dict(id=SRC_GUIDE, title="NSW Data Centre Guidelines",
             publisher="NSW Government (Infrastructure NSW / DPHI)",
             url="https://www.infrastructure.nsw.gov.au/media/4jlictae/id0073_nsw-data-centre_guidelines.pdf",
             doc_type="primary_government", published="2026-08-17", accessed=TODAY, credibility="A",
             notes="Six principles, 17 numbered performance measures. Primary source for dPUE/dWUE limits, Group 6 "
                   "diesel limits, 25% demand-flexibility requirement, PPA additionality criteria. Footnote 4 cites "
                   "'Oxford Economics, Estimating Data Centre Phantom Demand, Oxford Economics, 2025', introduced as "
                   "the work of the firm 'which prepared AEMO's forecast'; that briefing's own page says it was "
                   f"commissioned by AWS (SRC_OXEC_PHANTOM_2025). ARCHIVED {TODAY} at data/raw/operators/nswgov/ "
                   "with a SHA-256 manifest (an earlier copy is at data/raw/nsw_planning/)."),
    ]

    metrics = contribution_rows + [
        dict(insert=dict(as_of="2023-06-07", scope="NSW - Penrith", metric_name="penrith_msft_vpa_contribution_draft",
                         value=8423505.96, unit="AUD", basis="actual",
                         notes="The monetary contribution in the draft planning agreement between Penrith City Council "
                               "and Microsoft for 769 Mamre Road, Kemps Creek, and in its explanatory note: payable "
                               "before the first construction certificate, indexed by CPI. The agreement was executed "
                               "on 7 June 2023; the executed copy the council publishes is a scan with no text, so "
                               "its amount has not been read (RG-025).",
                         fact_status="VERIFIED", source_id=SRC_VPA_NOTE, confidence="medium", as_of_date=TODAY),
             add_sources=[dict(id=SRC_VPA_NOTE, quote=f"{vpa_amount} | {vpa_no_plan}"),
                          dict(id=SRC_VPA_DRAFT, quote=vpa_draft), dict(id=SRC_VPA_PAGE, quote=vpa_executed)]),
        dict(insert=dict(as_of="2025-06-23", scope="NSW", metric_name="nsw_ida_budget_2025_26", value=17.7,
                         unit="AUD m", basis="actual",
                         notes="2025-26 NSW Budget funding to establish and support the Investment Delivery "
                               "Authority, whose Round 1 endorsed 15 data centre projects (SRC_NSW_IDA). Not a "
                               "data-centre-only figure: the Authority takes projects over $1 billion in any sector.",
                         fact_status="VERIFIED", source_id=SRC_IDA_BUDGET, confidence="high", as_of_date="2025-06-23"),
             add_sources=[dict(id=SRC_IDA_BUDGET, quote=f"{ida_budget} | {ida_taskforce}")]),
    ]
    for name, value, quote, note in [
        ("dc_grid_investment_2020_2025_mandala", 3.1, mandala["totals"],
         "What data centres invested in grid infrastructure from 2020 to 2025, per the report Data Centres "
         "Australia's members commissioned. Built from 'data from select data centre operators', so CLAIMED."),
        ("dc_grid_investment_forecast_2025_2030_mandala", 7.2, mandala["totals"],
         "The same report's forecast for 2025 to 2030, of which $1.1bn is described as excess capacity for "
         "public use. CLAIMED: operator-supplied data and a forecast."),
        ("dc_grid_excess_capacity_2020_2025_mandala", 0.5, mandala["excess_past"],
         "The report's figure for excess capacity built 2020 to 2025, 15 per cent of the $3.1bn."),
    ]:
        metrics.append(dict(
            insert=dict(as_of="2025-11", scope="Australia", metric_name=name, value=value, unit="AUD bn",
                        basis="estimate" if "forecast" in name else "actual", notes=note, fact_status="CLAIMED",
                        source_id=SRC_MANDALA, confidence="medium", as_of_date="2025-11"),
            add_sources=[dict(id=SRC_MANDALA, quote=f"{quote} | {mandala['data']}")]))
    # Corrections to rows earlier packs wrote.
    metrics += [
        dict(match=dict(id=211),
             set=dict(notes="Claimed by Data Centres Australia to the NSW inquiry on 1 May 2026: operators will pay "
                            "$10.3 billion in energy infrastructure to 2030. TRACED 2026-10-22 (RG-043): the report "
                            "behind the industry's figures (Mandala, commissioned for Data Centres Australia by "
                            "AirTrunk, AWS, CDC and NEXTDC) gives $3.1bn invested 2020-2025 and $7.2bn forecast "
                            "2025-2030, which together make $10.3bn; the only '$10.3 billion' the report itself "
                            "states is the Australian Government's grid funding to 2030. Its figures come from 'data "
                            "from select data centre operators'.")),
        dict(match=dict(id=212),
             set=dict(notes="Data Centres Australia: of the $10.3 billion, $1.1 billion is excess capacity available "
                            "for public use. TRACED 2026-10-22 (RG-043): in the Mandala report the $1.1bn is the "
                            "excess within the $7.2bn forecast for 2025-2030; it puts the excess built 2020-2025 at "
                            "$0.5bn. Neither figure has been tested against network capital plans.")),
        dict(match=dict(id=26),
             set=dict(notes="The NSW Data Centre Guidelines: 'Oxford Economics, which prepared AEMO's forecast on data "
                            "centres, estimates 6 in every 7 megawatts (MW) of data centre connection requests are "
                            "phantom demand', citing Oxford Economics' briefing 'Estimating Data Centre Phantom "
                            "Demand' (2025). CORRECTED 2026-10-22 (RG-078): that briefing's own page says it 'was "
                            "commissioned by AWS'; AEMO's forecast was a separate engagement."),
             add_sources=[dict(id=SRC_OXEC, quote=f"{oe_six} | {oe_aws}")]),
    ]
    for mid, what in [(290, "AEMO received around 44 GW of connection requests linked to data centre proposals in 2025"),
                      (291, "of the 44 GW of requests, about 6 GW of project capacity is expected to proceed"),
                      (292, "only 2.8 GW of actual electricity draw once facilities reach maturity, described as '15 "
                            "times lower than what is sometimes reported'")]:
        metrics.append(dict(match=dict(id=mid),
                            set=dict(notes=f"Oxford Economics, as cited in BCA Submission No 116: {what}. CORRECTED "
                                           "2026-10-22 (RG-078): earlier notes called this research 'for the BCA'; the "
                                           "briefing's own page says it 'was commissioned by AWS'."),
                            add_sources=[dict(id=SRC_OXEC, quote=oe_aws)]))

    lobbying = [
        dict(match=dict(id=6),
             set=dict(actor_id="ENT_AWS", source_id=SRC_OXEC, fact_status="VERIFIED", as_of_date=TODAY,
                      recipient="Public policy debate; cited by the BCA (Submission No 116), Data Centres Australia "
                                "and the NSW Data Centre Guidelines",
                      notes="CORRECTED 2026-10-22 (RG-078): this row named the BCA as the commissioner. The briefing's "
                            "own page says 'This research briefing was commissioned by AWS. The analysis and findings "
                            "are Oxford Economics.' AEMO separately commissioned Oxford Economics to forecast data "
                            "centre electricity use; the Guidelines introduce the firm by that engagement and cite the "
                            "AWS-commissioned briefing. The finding itself is that most requested capacity will never "
                            "be drawn, which still stands as Oxford Economics' analysis."),
             add_sources=[dict(id=SRC_OXEC, quote=f"{oe_aws} | {oe_aemo}"), dict(id=SRC_GUIDE, quote=guide_oe_ref),
                          dict(id=T0522, quote=dca_cites)]),
        dict(match=dict(id=11),
             set=dict(source_id=SRC_BCA, fact_status="VERIFIED", confidence="high", as_of_date=TODAY,
                      outcome="Current: listed on the BCA's own member directory, read 2026-10-22.",
                      notes="CONFIRMED 2026-10-22 from the BCA's own page (RG-067), replacing the Wikipedia list this "
                            "row first relied on. The page also lists the Australia-India CEO Forum among the BCA's "
                            "initiatives. No improper conduct is alleged or implied."),
             add_sources=[dict(id=SRC_BCA, quote=bca_line("Tata Consultancy Services"))]),
        dict(match=dict(id=2),
             set=dict(outcome="Current: listed on the BCA's own member directory, read 2026-10-22, which lists no other "
                              "data centre operator except Fujitsu; NEXTDC, CDC and Equinix are not members."),
             add_sources=[dict(id=SRC_BCA, quote=bca_line("AirTrunk"))]),
        dict(insert=dict(actor_id="ENT_DATA_CENTRES_AU", person=None, channel="ministerial_meeting",
                         recipient="Secretary, NSW Premier's Department", event_date=None,
                         instrument="Meeting on the NSW Data Centre Consultation Paper (date not stated)",
                         position="Input on the NSW Data Centre Consultation Paper.",
                         outcome="Recorded only because the Secretary told the inquiry on 22 May 2026 that he was "
                                 "there; no diary entry or register record has been read.",
                         aligned_with_outcome=None, disclosed=1,
                         notes="Sworn evidence, not a register entry: the Secretary of the Premier's Department said he "
                               "'met with Data Centres Australia and talked to them about the consultation paper'. "
                               "The channel value is the closest the schema has; the recipient is a public servant, "
                               "not a minister. The same session heard the Chief Executive of Infrastructure NSW say "
                               "'a lot of those organisations have made direct representations to different people "
                               "in government'. RG-070.",
                         fact_status="VERIFIED", source_id=T0522, confidence="high", as_of_date="2026-05-22"),
             add_sources=[dict(id=T0522, quote=f"{met_dca} | {direct_reps}")]),
    ]
    for name, ent, why in BCA_MATCHES:
        if ent in ("ENT_AIRTRUNK", "ENT_TCS"):
            continue  # rows 2 and 11 above
        lobbying.append(dict(
            insert=dict(actor_id=ent, person=None, channel="peak_body_membership",
                        recipient="Business Council of Australia", event_date=None,
                        instrument="BCA member directory, read 2026-10-22",
                        position=f"Membership of the peak body representing more than 120 chief executives; in this "
                                 f"database as: {why}.",
                        outcome="Current as at 2026-10-22.", aligned_with_outcome=None, disclosed=1,
                        notes="From the BCA's own member list (RG-067). Membership is not a lobbying record and no "
                              "improper conduct is alleged or implied; it records who sits inside the body that "
                              "submitted to the NSW inquiry (Submission No 116) and gave evidence on 29 May 2026.",
                        fact_status="VERIFIED", source_id=SRC_BCA, confidence="high", as_of_date=TODAY),
            add_sources=[dict(id=SRC_BCA, quote=bca_line(name))]))

    incentives = [
        dict(match=dict(id=7),
             set=dict(notes="RECORD THIS AS A CONTRIBUTION, NOT A SUBSIDY - money flows from the developer to the "
                            "council. READ 2026-10-22 (RG-025): the draft agreement and its explanatory note set the "
                            "contribution at $8,423,505.96 (indexed by CPI), payable before the first construction "
                            "certificate, because no s7.11 contributions plan applied to the land. The executed copy "
                            "the council publishes is a scan; its amount has not been read, so amount_aud stays empty "
                            "and the figure is metric penrith_msft_vpa_contribution_draft. Every other determined NSW "
                            "data centre consent sets its contributions in its own conditions (RG-025 notes)."),
             add_sources=[dict(id=SRC_VPA_NOTE, quote=vpa_amount)]),
        dict(match=dict(id=6),
             set=dict(notes="THIS IS THE SUBSIDY THAT IS ACTUALLY DOCUMENTED IN AUSTRALIA: state-facilitated "
                            "coordination and endorsement, publicly named, with a published rejection rate. It is not a "
                            "tax concession. Funded with $17.7 million in the 2025-26 NSW Budget, with a multi-agency "
                            "Investment Taskforce in Investment NSW (SRC_NSW_IDA_BUDGET_2025). The Secretary of the "
                            "Premier's Department told the inquiry on 22 May 2026: 'The one thing that we don't "
                            "contemplate is government participation financially.' Read with the NSW Data Centre "
                            "Guidelines' 75-day pathway and concierge (row 9) and the Penrith VPA (row 7), which runs "
                            "money the other way."),
             add_sources=[dict(id=SRC_IDA_BUDGET, quote=ida_budget), dict(id=T0522, quote=not_financial)]),
        dict(match=dict(id=9), set={},
             add_sources=[dict(id=T0522, quote=ida_team), dict(id=SRC_GUIDE, quote=concierge)]),
        dict(match=dict(id=5),
             set=dict(notes="AUDIT REQUIRED - still no primary revenue-office evidence either way. ADVANCED 2026-10-22 "
                            "(RG-007): on the public record, Data Centres Australia told the inquiry 'Data centre "
                            "operators do not receive subsidies or tax incentives' and the BCA's submission said the "
                            "same; the Secretary of the Premier's Department said government does not 'contemplate' "
                            "participating financially. Neither is a revenue office's record. The GIPA application to "
                            "Revenue NSW (docs/requests/GIPA-002-revenue-nsw.md) asks for instruments and aggregate "
                            "counts, never a named taxpayer. A documented negative will be recorded as 'none_found'."),
             add_sources=[dict(id=T0501, quote=dca_claim), dict(id=T0522, quote=not_financial)]),
    ]

    contrib_summary = "; ".join(f"{c[0]} {c[3]} ${c[4]:,.2f}" for c in CONTRIBUTIONS)
    gaps = [
        dict(match=dict(id=25),
             set=dict(status="in_progress", as_of_date=TODAY,
                      notes="ADVANCED 2026-10-22 (research batch 3). PENRITH VPA: the draft agreement and its "
                            "explanatory note set Microsoft's contribution at $8,423,505.96, indexed by CPI and payable "
                            "before the first construction certificate, calculated by the Mamre Road East Precinct "
                            "rates because no contributions plan applied; executed 7 June 2023, but the executed copy "
                            "is a scan whose amount has not been read. SURVEY: the 20 signed SSD consents archived in "
                            "September carry their own contribution conditions - " + contrib_summary + ". Davis Road "
                            "and NEXTDC S4 set a 1% levy with no amount; Khartoum Road must also enter a planning "
                            "agreement. Not covered: consents determined by councils rather than the State, and "
                            "whether any contribution has been paid."),
             add_sources=[dict(id=SRC_VPA_NOTE, quote=vpa_amount), dict(id=SRC_CONSENTS, quote=" | ".join(rates)),
                          dict(id=SRC_VPA_DRAFT, quote=vpa_draft)]),
        dict(match=dict(id=7),
             set=dict(status="in_progress", as_of_date=TODAY,
                      notes="ADVANCED 2026-10-22 (research batch 3). The free routes give the sector's and the "
                            "government's word, not a revenue office's: Data Centres Australia told the inquiry 'Data "
                            "centre operators do not receive subsidies or tax incentives' (1 May 2026); the BCA's "
                            "Submission No 116 says operators 'pay full taxes with no concessions'; the Secretary of "
                            "the Premier's Department said 'The one thing that we don't contemplate is government "
                            "participation financially' (22 May 2026). What the State does give is in kind: the IDA "
                            "($17.7m in the 2025-26 Budget) and the Guidelines' concierge. No witness from Revenue "
                            "NSW appeared. GIPA-002 to the Department of Customer Service (which holds Revenue NSW's "
                            "records) is drafted from reports/RG007_foi_strategy.md; the Victorian, Queensland and "
                            "Commonwealth templates stay in that file."),
             add_sources=[dict(id=T0501, quote=dca_claim), dict(id=T0522, quote=not_financial)]),
        dict(match=dict(id=6),
             set=dict(status="in_progress", as_of_date=TODAY,
                      notes="WORKED 2026-10-22 (research batch 3). The free route is closed by design: the FIRB "
                            "quarterly report for January to March 2026 reports 311 approved commercial proposals, 97 "
                            "with conditions, by sector and source country only, and suppresses 'Any data that may "
                            "enable the identification of a particular person or organisation'; it does not mention "
                            "data centres. FOI-001 to the Treasury is drafted (docs/requests/FOI-001-treasury-firb.md): "
                            "no application fee, a 30-day decision period, and it asks for decisions and conditions on "
                            "data centre acquisitions since 2020, expecting exemptions it can then challenge."),
             add_sources=[dict(id=SRC_FIRB, quote=firb_suppressed)]),
        dict(match=dict(id=63),
             set=dict(status="in_progress", as_of_date=TODAY,
                      notes="ADVANCED 2026-10-22 (research batch 3). What is public: the 2025-26 Budget gave the "
                            "Investment Delivery Authority $17.7 million, supported by a multi-agency Investment "
                            "Taskforce in Investment NSW; a Deputy Secretary told the inquiry that the team supporting "
                            "the IDA 'sits within my team in the Premier's Department'; the Guidelines commit to a "
                            "concierge function within DPHI and dedicated post-consent staff. Headcount and cost of the "
                            "DPHI concierge are not published, and no record read offers councils or community groups "
                            "the same service. Next: DPHI's annual report and budget estimates."),
             add_sources=[dict(id=SRC_IDA_BUDGET, quote=f"{ida_budget} | {ida_taskforce}"),
                          dict(id=T0522, quote=ida_team), dict(id=SRC_GUIDE, quote=concierge)]),
        dict(match=dict(id=70),
             set=dict(status="in_progress", as_of_date=TODAY,
                      notes="WORKED 2026-10-22 (research batch 3). REFUSED, never worked around: the NSW lobbyist "
                            "register's robots.txt closes the whole site; the ministers' quarterly diary disclosures "
                            "sit in a folder nsw.gov.au's robots.txt closes (30 files for the Premier, Treasurer and "
                            "the Planning, Energy and Industry ministers, January 2025 to June 2026, recorded in "
                            "data/raw/registers/); the Commonwealth register is a JavaScript application with no "
                            "content without a browser. All are in docs/requests/DOWNLOADS.md. On the public record "
                            "instead: the Secretary of the Premier's Department told the inquiry he 'met with Data "
                            "Centres Australia' about the consultation paper, and the Chief Executive of "
                            "Infrastructure NSW said 'a lot of those organisations have made direct representations "
                            "to different people in government' (22 May 2026). 'There is no Minister for data "
                            "centres.'"),
             add_sources=[dict(id=T0522, quote=f"{met_dca} | {direct_reps} | {no_minister}"),
                          dict(id=SRC_DIARIES, quote=diaries)]),
        dict(match=dict(id=67),
             set=dict(status="resolved", resolved_date=TODAY, fact_status="VERIFIED", confidence="high",
                      as_of_date=TODAY,
                      notes="RESOLVED 2026-10-22 (research batch 3). The BCA's own member directory now serves in full "
                            "to the research crawler: 130 members. Cross-referenced against this database: AirTrunk, "
                            "Amazon, Google, Microsoft, Meta, Blackstone (AirTrunk's owner), Goodman and Stockland "
                            "(NSW data centre applicants), TransGrid and Endeavour Energy (the networks data centres "
                            "connect to), Fujitsu, Telstra, Origin Energy and Tata Consultancy Services are members; "
                            "each is a lobbying row (peak_body_membership). NEXTDC, CDC, Equinix, Macquarie "
                            "Technology Group and Data Centres Australia are not. The big four accounting firms and "
                            "several of the law firms that act on data centre deals are members too. Membership is "
                            "not lobbying and no improper conduct is implied. The 'member-driven or board-driven' "
                            "half of the question is not answerable from public records."),
             add_sources=[dict(id=SRC_BCA, quote=" | ".join(bca_line(n) for n, _, _ in BCA_MATCHES[:8]))]),
        dict(match=dict(id=78),
             set=dict(status="resolved", resolved_date=TODAY, fact_status="VERIFIED", confidence="high",
                      as_of_date=TODAY,
                      notes="RESOLVED 2026-10-22 (research batch 3). Oxford Economics' own page for the briefing "
                            "'Estimating Data Centre Phantom Demand' (21 November 2025; subtitle 'Surging data centre "
                            "connection requests drive phantom demand for power', the title the BCA cites) ends: "
                            "'This research briefing was commissioned by AWS. The analysis and findings are Oxford "
                            "Economics.' The same page says AEMO separately commissioned Oxford Economics to forecast "
                            "data centre electricity use. So the briefing cited by the BCA, by Data Centres Australia "
                            "and in the NSW Data Centre Guidelines - which introduce the firm as the one 'which "
                            "prepared AEMO's forecast' - was commissioned by Amazon Web Services. Who paid is not "
                            "stated beyond 'commissioned'. CORRECTED: lobbying row 6 and metrics 26 and 290-292 had "
                            "attributed it to the BCA or AEMO."),
             add_sources=[dict(id=SRC_OXEC, quote=f"{oe_aws} | {oe_aemo}"), dict(id=SRC_GUIDE, quote=guide_oe),
                          dict(id="SRC_BCA_SUB116", quote=bca_cites)]),
        dict(match=dict(id=43),
             set=dict(status="in_progress", as_of_date=TODAY,
                      notes="ADVANCED 2026-10-22 (research batch 3). Traced to source: Data Centres Australia told "
                            "the inquiry operators 'will pay $10.3 billion in energy infrastructure to 2030, and $1.1 "
                            "billion of that is excess capacity'. The report behind the industry's figures (Mandala, "
                            "commissioned for Data Centres Australia by AirTrunk, AWS, CDC and NEXTDC) gives $3.1bn "
                            "invested 2020-2025 and $7.2bn forecast to 2030, built from 'data from select data centre "
                            "operators'; the two make $10.3bn, and the only '$10.3 billion' the report states is the "
                            "Australian Government's grid funding. Its $1.1bn excess is within the forecast, with "
                            "$0.5bn before. The networks told the inquiry the principle holds - Ausgrid: 'the customer "
                            "who caused network costs pays for them'; Transgrid invests only on 'full commitment' and "
                            "had no data centre commitment on 22 May 2026 - but none put a total on it. Still to "
                            "test: the quantum against Transgrid, Ausgrid and Endeavour capital plans and AER "
                            "determinations (aer.gov.au did not answer)."),
             add_sources=[dict(id=T0529, quote=causer), dict(id=T0522, quote=no_commit),
                          dict(id=SRC_MANDALA, quote=f"{mandala['totals']} | {mandala['government']} | "
                                                     f"{mandala['data']}")]),
        dict(match=dict(id=77),
             set=dict(as_of_date=TODAY,
                      notes="Roles CONFIRMED from Austrade's own site and Forum releases. ADVANCED 2026-10-22: the BCA's "
                            "own site lists the Australia-India CEO Forum among its initiatives, and its member "
                            "directory lists Tata Consultancy Services. Register and diary checks are blocked: the NSW "
                            "lobbyist register and the ministers' diaries are closed to crawlers and the Commonwealth "
                            "register needs a browser (RG-070; docs/requests/DOWNLOADS.md). Pairs with RG-070."),
             add_sources=[dict(id=SRC_BCA, quote=f"{india_forum} | {bca_line('Tata Consultancy Services')}")]),
        dict(match=dict(id=74),
             set=dict(as_of_date=TODAY,
                      notes="ADVANCED 2026-09-18. All 20 Schedule 1 applicants now parse (RG-065): SEVEN consents are "
                            "held by consultancies or an architectural practice - ARUP Pty Ltd (Turner Road), ARUP "
                            "Australia Pty Ltd (Echidna), Cundall Johnston and Partners (Davis Road consent AND Mod 1), "
                            "Lehr Consultants (Glendenning Road, Station Road), Greenbox Architecture (Lane Cove West). "
                            "Cross-referenced against the tracked gov_contracts table: NONE of these firms appears. "
                            "BLOCKED 2026-10-22: AusTender and buy.nsw both refuse the research crawler (their "
                            "robots.txt is refused, read as disallow-all; data/raw/registers/), so contracts cannot be "
                            "pulled by agency here; the NSW Data Centre Guidelines name no consultant author. In "
                            "docs/requests/DOWNLOADS.md for a person."),
             add_sources=[dict(id=SRC_GUIDE, quote=concierge)]),
    ]

    pack = {
        "pack_id": "public-and-room-2026-10",
        "prepared_by": "scripts/curate_public_and_room.py",
        "prepared_on": TODAY,
        "sources": sources,
        "rows": {
            "metrics": metrics,
            "lobbying": lobbying,
            "incentives": incentives,
            "research_gaps": gaps,
        },
    }
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(pack, fh, indent=1, ensure_ascii=False)
    print(f"wrote {OUT}: {len(sources)} sources, {len(contribution_rows)} consent contributions, "
          f"{len(members)} BCA members ({len(BCA_MATCHES)} in the database), "
          f"{sum(len(v) for v in refused.values())} refusals on record")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
