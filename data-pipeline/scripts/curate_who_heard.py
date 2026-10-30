#!/usr/bin/env python3
"""
Curate research batch 5, "Who gets heard" and "Did anyone check?" (docs/RESEARCH-PLAN.md, story lines
C1 and C2).

C1 asks whether locals and councils have their say. The parliamentary record of who was heard is
closed to the crawler (NSW Parliament and the Senate refuse it), so this batch reads the record the
planning system keeps instead:

  1. The council submissions on NSW data centre applications in Blacktown, Penrith, Fairfield, Ryde
     and The Hills, fetched from the NSW Planning Portal one at a time (scripts in the hunt logs).
  2. Every assessment report already archived for a determined NSW data centre, read for who could
     decide the case and what happened to the council's objection. The portal tells the public that
     a council objection makes the Independent Planning Commission the consent authority; a
     delegation of 18 August 2026 lets a departmental Director decide data centre cases whatever
     the council says, and Project Apollo was approved that way.

C2 asks whether anyone checks:

  3. The political donation disclosures in the NSW record: three in 46 projects. Talavera Road's
     sent its case to the Commission. Roberts Road's is an image-only scan, read here (OCR for the
     print, by eye for the handwriting; transcription committed, residential address left out); the
     Department's report said a delegate could decide only if no disclosure had been made, and
     that no reportable donation had been made by the applicant. Mamre Road's is restricted.
  4. The two warning letters in the record (Roberts Road and Station Road): both restricted.
  5. Who decided Talavera Road: the Commission's own statement of reasons names its panel.

Every quote is checked against its archive and the script refuses to write if one is missing. No
improper conduct is alleged or implied by any row; where the record does not explain itself, the
row says so and the question goes to the GIPA draft.

Run:
    python3 scripts/curate_who_heard.py
    python3 scripts/load_pack.py data/packs/who_heard.json --allow-missing-source
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "data", "packs", "who_heard.json")
NSWP = os.path.join(ROOT, "data", "raw", "nsw_planning")
DOCS = os.path.join(NSWP, "documents")
ATT = os.path.join(NSWP, "attachments")
SUBS = os.path.join(NSWP, "council_submissions")
IPC = os.path.join(NSWP, "ipc")
TODAY = "2026-10-30"

SRC_DON_10330 = "SRC_SSD10330_DONATION"
SRC_DON_24299707 = "SRC_SSD24299707_DONATION"
SRC_IPC_SOR = "SRC_IPC_TALAVERA_SOR"
SRC_REFERRAL = "SRC_DPE_TALAVERA_REFERRAL"
SRC_PORTAL_RULES = "SRC_NSWPORTAL_DETERMINE_DA"
SRC_SUBS = "SRC_NSWPORTAL_COUNCIL_SUBS"
SRC_GUIDE = "SRC_NSWGUIDE26"


def ar(case: str) -> str:
    """The assessment report source the ssd_documents pack registered for a case."""
    return f"SRC_{case.replace('-', '')}_ASSESSMENT"


errors: list[str] = []


def spaceless(text: str) -> str:
    return re.sub(r"\s+", "", text).lower()


def text_of(path: str) -> str:
    return open(path, encoding="utf-8").read()


def in_text(path: str, quote: str) -> str:
    if spaceless(quote) not in spaceless(text_of(path)):
        errors.append(f"{os.path.relpath(path, ROOT)} does not hold {quote[:70]!r}")
    return quote


def manifest(path: str) -> dict:
    return json.load(open(path))


def sha_ok(path: str) -> bool:
    """A PDF that is archived here must still match its manifest (PDFs are not committed)."""
    return (not os.path.exists(path)
            or hashlib.sha256(open(path, "rb").read()).hexdigest() == manifest(path + ".meta.json")["sha256"])


def report(case: str) -> str:
    return os.path.join(DOCS, f"{case}_assessment.txt")


def sub(case: str) -> str:
    (name,) = [f for f in os.listdir(SUBS) if f.startswith(case + "__") and f.endswith(".txt")]
    return os.path.join(SUBS, name)


# Determined NSW data centres whose council objected, and what the assessment report says became of
# the objection. (case, site, council, outcome, the report's own words). Read from every assessment
# report archived under data/raw/nsw_planning/documents/; the cases where the council did not object
# are listed in the RG-040 hunt log.
OBJECTIONS = [
    ("SSD-21342738", "SITE_EC_EXPANSION", "Blacktown City Council", "lodged outside the exhibition period",
     "Council objected to the development, howev er Council’s submission was received outside the exhibition period."),
    ("SSD-33781208", "SITE_STATION_RD", "Blacktown City Council", "withdrawn",
     "While Council originally objected to the SSD application, it formally withdrew its objection to the "
     "development on 6 October 2022."),
    ("SSD-41589232", "SITE_51_HUNTINGWOOD", "Blacktown City Council", "lodged out of time, then withdrawn",
     "While Council originally objected to the SSD application, the objection was not made within 28 day exhibition "
     "period in accordance with Schedule 1 of the EP&A Act. Further, Council also subsequently withdrew its "
     "objection to the development on 10 August 2023."),
    ("SSD-47320208", "SITE_ECHIDNA", "Blacktown City Council", "withdrawn",
     "While Council originally objected to the SSD application, Council advised the Department in writing on 19 "
     "March 2024 that it has withdrawn its objection to the development."),
    ("SSD-70889211", "SITE_CDC_MARSDEN", "Blacktown City Council", "withdrawn",
     "Council originally objected to the SSD application, Council advised the Department in writing on 9 September "
     "2025 that it has withdrawn its objection to the development."),
    ("SSD-73761707", "SITE_GLENDENNING", "Blacktown City Council", "resolved",
     "Council initially objected to the development but later advised in writing to the Department that its "
     "objection has been resolved."),
    ("SSD-74069708", "SITE_PROJECT_APOLLO", "City of Ryde Council", "maintained; decided by a departmental Director",
     "Council maintained its objection"),
]


def main() -> int:
    # --- what the public is told ------------------------------------------------------------------------
    rules = os.path.join(NSWP, "portal_rules", "determine-da.txt")
    rule_ipc = in_text(rules, "The IPC is generally the consent authority for an SSD application where the applicant "
                              "is not a public authority (or acting on behalf of one), and one or more of the "
                              "following applies:")
    rule_council = in_text(rules, "the local council has lodged an objection")
    rule_donation = in_text(rules, "the applicant has made a reportable political donation.")
    rule_updated = in_text(rules, "Last updated: 09/04/2026")

    # --- the delegation of 18 August 2026 ---------------------------------------------------------------
    apollo = report("SSD-74069708")
    deleg_2026 = in_text(apollo, "On 18 August 2026 , the Minister delegated the functions to determine SSD "
                                 "applications for relevant resource, ener gy or data centre projects to the "
                                 "Director, Industry Assessments where:")
    deleg_2026_terms = in_text(apollo, "there are less than 15 unique public submissions by way of objection, and • a "
                                       "reportable political disclosure statement has not been made by the Applicant.")
    apollo_obj = in_text(apollo, "During the exhibition period, the Department received one objection from City of "
                                 "Ryde Council (Council) and no submissions from the public.")
    apollo_kept = in_text(apollo, "Council maintained its objection, advising that:")
    apollo_deleg = in_text(apollo, "Accordingly, the application can be determined by the A/Director, Industry "
                                   "Assessments, under delegation.")
    # The framework came out the day before the delegation; the regulatory_events note says so.
    in_text(apollo, "On 17 August 2026, the NSW Government released the NSW Data Centre Policy Framework")
    glen = report("SSD-73761707")
    glen_deleg = in_text(glen, "On 18 August 2026 , the Minister delegated the functions to determine SSD "
                               "applications to the Director, Industry Assessments where:")
    deleg_2022 = in_text(report("SSD-41589232"), "the relevant local council has not made a submission by way of "
                                                 "objection under the mandatory requirements for community "
                                                 "participation listed under Schedule 1 of the EP&A Act.")
    ryde_apollo = in_text(sub("SSD-74069708"), "Council is not supportive of the development in its")
    ryde_s5 = in_text(sub("SSD-63168959"), "In short, Council strongly objects to the development as submitted.")
    btown_glen = in_text(sub("SSD-73761707"), "we object to the proposal in its current form")
    objection_quotes = {case: in_text(report(case), words) for case, _, _, _, words in OBJECTIONS}

    # --- Talavera Road: a disclosure, an objection, and the Commission ---------------------------------
    don_t = os.path.join(ATT, "SSD-24299707_political_donation")
    if not sha_ok(don_t + ".pdf"):
        errors.append("the Talavera Road disclosure fails its manifest")
    t_who = in_text(don_t + ".txt", "Macquarie Data Centres Pty Ltd (ABN 11 612 259 391)")
    t_donor = in_text(don_t + ".txt", "Macquarie Telecom Pty Ltd (21082930916)")
    t_penrith = in_text(don_t + ".txt", "NSW Division - Penrith SEC 12/11/2020 $2000")
    t_epping = in_text(don_t + ".txt", "NSW Division - Epping SEC 18/06/2021 $1500")
    t_ryde = in_text(don_t + ".txt", "23/10/2021Jerome Laxale City of Ryde West Ward Campaign Group $1980")
    t_signed = in_text(don_t + ".txt", "28 February 2022")
    sor = os.path.join(IPC, "statement-of-reasons-for-decision-talavera-road-ssd-24299707")
    referral = os.path.join(IPC, "referral-letter-redacted")
    for b in (sor, referral):
        if not sha_ok(b + ".pdf"):
            errors.append(f"{os.path.basename(b)} fails its manifest")
    sor_why = in_text(sor + ".txt", "an objection was received from the City of Ryde Council and a company connected "
                                    "to the Applicant disclosed a reportable political donation.")
    sor_panel = in_text(sor + ".txt", "Commissioners Ms Juliet Grant (Chair) and Dr Bronwyn Evans AM were appointed to "
                                      "constitute the Commission Panel in making the final decision.")
    sor_date = in_text(sor + ".txt", "Statement of Reasons for Decision Ms Juliet Grant (Chair) Dr Bronwyn Evans AM 19 "
                                     "January 2024")
    ref_rule = in_text(referral + ".txt", "In accordance with clause 8A of the former State Environmental Planning "
                                          "Policy (State and Regional Development) 2011 and section 4.5 of the "
                                          "Environmental Planning and Assessment Act 1979 , the Independent Planning "
                                          "Commission is the declared consent authority for this development, as:")
    ref_donation = in_text(referral + ".txt", "a company connected to Macquarie Data Centres Pty Ltd (the Applicant) "
                                              "has made reportable political donations in the two-year period prior to "
                                              "the application being made.")
    portal_blank = "[Name of Commissioner]"  # the portal copy's signature block (RG-085's question)

    # --- Roberts Road: the disclosure and the report -----------------------------------------------------
    don_r = os.path.join(ATT, "SSD-10330_political_donation")
    if not sha_ok(don_r + ".pdf"):
        errors.append("the Roberts Road disclosure fails its manifest")
    if text_of(don_r + ".txt").strip():
        errors.append("the Roberts Road disclosure now has extractable text; read it instead of the transcription")
    tr = don_r + ".transcription.txt"
    if manifest(don_r + ".pdf.meta.json")["sha256"] not in text_of(tr):
        errors.append("the transcription does not name the scan it was read from")
    r_discloser = in_text(tr, "Name of person making this disclosure: Gregory David Boorer (Director & CEO)")
    r_ref = in_text(tr, "Planning application reference: SSD10330")
    r_applicant = in_text(tr, "You are the APPLICANT: YES (circled)")
    r_recipient = in_text(tr, "Name of party or person for whose benefit the donation was made: The Liberal Party of "
                              "Australia - NSW Division, ABN 68 324 857 904")
    r_date = in_text(tr, "Date donation made: 18 June 2018")
    r_amount = in_text(tr, "Amount/value of donation: $7,500")
    r_signed = in_text(tr, "Signature(s) and Date: [signature] 2 December 2019")
    if re.search(r"\d+ [A-Z][a-z]+ (street|road|avenue)|ACT 26\d\d", text_of(tr), re.I):
        errors.append("the transcription now holds an address; leave it out")
    r_meta = manifest(don_r + ".pdf.meta.json")
    rr = report("SSD-10330")
    rr_deleg = in_text(rr, "On 9 March 2020, the Minister delegated the functions to determine SSD applications to "
                           "the Executive Director, Regions, Industry and Key Sites where:")
    rr_cond = in_text(rr, "a political disclosure statement has not been made.")
    rr_none = in_text(rr, "No reportable political donations were made by the Applicant in the last two years and no "
                          "reportable political donations were made by any persons who lodged a submission.")
    rr_so = in_text(rr, "Accordingly, the application can be determined by the Executive Director , Regions, Industry "
                        "and Key Sites under delegation.")
    rr_consent = in_text(os.path.join(ATT, "SSD-10330_roberts_consent.txt"),
                         "As delegate of the Minister for Planning and Public Spaces under delegation executed on 9 "
                         "March 2020, I approve the")

    # --- what is locked ---------------------------------------------------------------------------------
    locked = json.load(open(os.path.join(ATT, "restricted.json")))
    for slug in ("cdc-data-centres-response-warning-letter", "warning-letter-29052024",
                 "political-donations-disclosure-mamre-road-data-centre"):
        if slug not in locked:
            errors.append(f"no refusal recorded for {slug}")
    sub_locked = json.load(open(os.path.join(SUBS, "restricted.json")))
    sub_files = sorted(f for f in os.listdir(SUBS) if f.endswith(".txt"))
    for f in sub_files:
        if not sha_ok(os.path.join(SUBS, f[:-4] + ".pdf")):
            errors.append(f"{f} fails its manifest")
    if len(sub_files) != 18 or len(sub_locked) != 4:
        errors.append(f"expected 18 council submissions read and 4 restricted, found {len(sub_files)} and {len(sub_locked)}")

    if errors:
        print("refusing to write; fix these first:", file=sys.stderr)
        for e in errors:
            print(f"  {e}", file=sys.stderr)
        return 1

    def archived(path: str) -> str:
        m = manifest(path + ".meta.json")
        return f"sha256 {m['sha256'][:12]}, {m['bytes']:,} bytes"

    sources = [
        dict(id=SRC_DON_10330, title="Political donations disclosure statement, SSD-10330 Roberts Road Data Centre "
                                     "(signed 2 December 2019)",
             publisher="NSW Planning Portal (filed by the applicant, Canberra Data Centres Pty Ltd)",
             url=r_meta["url"], doc_type="primary_planning_portal", published="2019-12-05",
             accessed=TODAY, credibility="A",
             notes="A statutory disclosure under s147 (now s10.4) of the EP&A Act, filed in the project's EIS folder. "
                   "Image-only scan with no extractable text: read on 2026-10-30 by OCR for the print and by eye for "
                   "the handwriting, transcription committed beside it (data/raw/nsw_planning/attachments/"
                   "SSD-10330_political_donation.transcription.txt) with the donor's residential address left out. "
                   "Declares one donation: $7,500 to the Liberal Party of Australia - NSW Division on 18 June 2018, by "
                   "the company's director and chief executive, who ticked 'applicant'. Handwriting: check against "
                   f"the image. ARCHIVED 2026-09-18 ({archived(don_r + '.pdf')}); PDF not committed."),
        dict(id=SRC_DON_24299707, title="Political donations disclosure statement, SSD-24299707 Talavera Road Data "
                                        "Centre Campus Expansion (28 February 2022)",
             publisher="NSW Planning Portal (filed by the applicant, Macquarie Data Centres Pty Ltd)",
             url=manifest(don_t + ".pdf.meta.json")["url"], doc_type="primary_planning_portal",
             published="2022-03-01", accessed="2026-10-22", credibility="A",
             notes="Filed by Macquarie Data Centres Pty Ltd. Three donations by Macquarie Telecom Pty Ltd: $2,000 to "
                   "the Liberal Party NSW Division (Penrith SEC) on 12/11/2020, $1,500 to the Liberal Party NSW "
                   "Division (Epping SEC) on 18/06/2021, and $1,980 to a City of Ryde West Ward campaign group on "
                   "23/10/2021. Typed; text extracted. ARCHIVED 2026-10-22 at data/raw/nsw_planning/attachments/ "
                   f"({archived(don_t + '.pdf')}); PDF not committed."),
        dict(id=SRC_IPC_SOR, title="Statement of Reasons for Decision, Talavera Road Data Centre Campus Extension "
                                   "SSD-24299707 (19 January 2024)",
             publisher="Independent Planning Commission NSW",
             url=manifest(sor + ".pdf.meta.json")["url"], doc_type="primary_regulator", published="2024-01-19",
             accessed="2026-10-22", credibility="A",
             notes="The Commission was the consent authority 'because an objection was received from the City of Ryde "
                   "Council and a company connected to the Applicant disclosed a reportable political donation'. "
                   "Names the panel: two Commissioners, a Chair and a member. Approved with conditions. The "
                   "consent the planning portal publishes carries '[Name of Commissioner]' placeholders. ARCHIVED "
                   f"2026-10-22 at data/raw/nsw_planning/ipc/ ({archived(sor + '.pdf')}); PDF not committed."),
        dict(id=SRC_REFERRAL, title="Referral for determination of State significant development application, "
                                    "Talavera Road (SSD-24299707) (27 November 2023)",
             publisher="NSW Department of Planning and Environment",
             url=manifest(referral + ".pdf.meta.json")["url"], doc_type="primary_government", published="2023-11-27",
             accessed="2026-10-22", credibility="A",
             notes="The Department to the Commission's Chair: under clause 8A of the former State Environmental "
                   "Planning Policy (State and Regional Development) 2011 and s4.5 of the EP&A Act the Commission is "
                   "the declared consent authority because the council objected and 'a company connected to "
                   "Macquarie Data Centres Pty Ltd (the Applicant) has made reportable political donations in the "
                   "two-year period prior to the application being made'. Published by the Commission, redacted. "
                   f"ARCHIVED 2026-10-22 at data/raw/nsw_planning/ipc/ ({archived(referral + '.pdf')})."),
        dict(id=SRC_PORTAL_RULES, title="Determine DA - State significant development process (NSW Planning Portal)",
             publisher="NSW Department of Planning, Housing and Infrastructure",
             url="https://www.planningportal.nsw.gov.au/major-projects/assessment/state-significant-development/ssd-process/determine-da",
             doc_type="primary_government", published="2026-04-09", accessed="2026-10-22", credibility="A",
             notes="The public explanation of who decides an SSD application, last updated 9 April 2026: the "
                   "Commission 'is generally the consent authority' where the local council has lodged an objection, "
                   "50 or more public objections are received, or the applicant has made a reportable political "
                   "donation; the Minister and the Commission can delegate decisions to Department officers. ARCHIVED "
                   "2026-10-22 at data/raw/nsw_planning/portal_rules/."),
        dict(id=SRC_SUBS, title="Council submissions on NSW data centre State Significant Development applications "
                                "(Blacktown, Penrith, Fairfield, Ryde, The Hills)",
             publisher="NSW Planning Portal (the councils' own letters)",
             url="https://www.planningportal.nsw.gov.au/major-projects", doc_type="primary_planning_portal",
             published=None, accessed="2026-10-22", credibility="A",
             notes=f"Each council's main submission on {len(sub_files) + len(sub_locked)} data centre applications in the "
                   f"five councils RG-040 names, fetched one at a time through the portal's JSON: {len(sub_files)} "
                   f"read ({len(sub_files) - 2} with text, two scans read by OCR), {len(sub_locked)} restricted "
                   "(data/raw/nsw_planning/council_submissions/restricted.json). Ryde's letters are cover letters; "
                   "their attachments were not fetched. Personal contact details redacted. ARCHIVED 2026-10-22; PDFs "
                   "not committed, text is."),
    ]

    lobbying = [
        dict(match=dict(id=10),
             set=dict(actor_id="ENT_CDC",
                      person="Director and Chief Executive Officer, Canberra Data Centres (named in the statutory "
                             "disclosure; recorded here by role)",
                      recipient="Liberal Party of Australia - NSW Division", event_date="2018-06-18",
                      instrument="Political donations disclosure statement filed with SSD-10330 (Roberts Road Data "
                                 "Centre), signed 2 December 2019",
                      position="A reportable political donation of $7,500, disclosed with the Roberts Road application "
                               "as the law requires.",
                      outcome="The application was determined on 14 July 2020 by the Department's Executive "
                              "Director under a delegation that applied where 'a political disclosure statement has "
                              "not been made'; the assessment report states that no reportable political donations "
                              "were made by the Applicant in the last two years. Why the disclosure did not change "
                              "who decided is not on the record (GIPA-003).",
                      aligned_with_outcome=None, disclosed=1,
                      notes="READ 2026-10-30 (RG-069). This row was a placeholder parked under AirTrunk; it is now "
                            "attributed to CDC, whose company is the applicant. The disclosure is a scan: the print was "
                            "read by OCR and the handwriting by eye, and should be checked against the image. Lawful "
                            "donations, lawfully disclosed. No improper conduct by anyone is alleged or implied.",
                      fact_status="VERIFIED", source_id=SRC_DON_10330, confidence="medium", as_of_date=TODAY),
             add_sources=[dict(id=SRC_DON_10330, quote=f"{r_discloser} | {r_ref} | {r_applicant} | {r_recipient} | "
                                                       f"{r_date} | {r_amount} | {r_signed}"),
                          dict(id=ar("SSD-10330"), quote=f"{rr_cond} | {rr_none}")]),
    ]
    for recipient, date, amount, quote in (
            ("Liberal Party of Australia - NSW Division (Penrith SEC)", "2020-11-12", "$2,000", t_penrith),
            ("Liberal Party of Australia - NSW Division (Epping SEC)", "2021-06-18", "$1,500", t_epping),
            ("A City of Ryde West Ward council election campaign group (named in the disclosure)", "2021-10-23",
             "$1,980", t_ryde)):
        lobbying.append(dict(
            insert=dict(actor_id="ENT_MACQUARIE_TG", person=None, channel="political_donation", recipient=recipient,
                        event_date=date,
                        instrument="Political donations disclosure statement filed with SSD-24299707 (Talavera Road), "
                                   "28 February 2022",
                        position=f"A reportable political donation of {amount} by Macquarie Telecom Pty Ltd, a company "
                                 f"connected to the applicant Macquarie Data Centres, to {recipient}.",
                        outcome="With the City of Ryde's objection, the disclosure made the Independent Planning "
                                "Commission the consent authority; it approved the expansion on 19 January 2024.",
                        aligned_with_outcome=None, disclosed=1,
                        notes="From the applicant's own disclosure (RG-069). The Talavera Road site is in the City of "
                              "Ryde. Lawful donations, lawfully disclosed; no improper conduct is alleged or implied.",
                        fact_status="VERIFIED", source_id=SRC_DON_24299707, confidence="high", as_of_date=TODAY),
            add_sources=[dict(id=SRC_DON_24299707, quote=f"{t_who} | {t_donor} | {quote} | {t_signed}"),
                         dict(id=SRC_IPC_SOR, quote=sor_why)]))

    regulatory = [
        dict(insert=dict(event_date="2026-08-18", regulator_id="ENT_NSW_DPHI", instrument_id=None, site_id=None,
                         entity_id=None, event_type="other",
                         summary="The Minister for Planning delegated the determination of SSD applications 'for "
                                 "relevant resource, energy or data centre projects' to the Director, Industry "
                                 "Assessments, where fewer than 15 unique public submissions object and the applicant "
                                 "has made no reportable political disclosure statement. Unlike the 2020 and 2022 "
                                 "delegations, its conditions as the assessment reports quote them say nothing about "
                                 "the local council objecting.",
                         outcome="Used for Project Apollo (approved 2 September 2026 while the City of Ryde maintained "
                                 "its objection) and Glendenning Road (16 September 2026, after Blacktown advised its "
                                 "objection was resolved).",
                         notes="The delegation instrument itself has not been read; this rests on the Department's own "
                               "assessment reports. The day before, 17 August 2026, the NSW Data Centre Policy Framework "
                               "and Guidelines were released. The planning portal page last updated 9 April 2026 still "
                               "says a council objection generally makes the Commission the consent authority; how the "
                               "Commission's role was removed for these cases is not on the record read (RG-040; "
                               "GIPA-003 asks for the instrument).",
                         fact_status="VERIFIED", source_id=ar("SSD-74069708"), confidence="high", as_of_date=TODAY),
             add_sources=[dict(id=ar("SSD-74069708"), quote=f"{deleg_2026} {deleg_2026_terms}"),
                          dict(id=ar("SSD-73761707"), quote=glen_deleg),
                          dict(id=ar("SSD-41589232"), quote=deleg_2022),
                          dict(id=SRC_PORTAL_RULES, quote=f"{rule_ipc} {rule_council} | {rule_updated}")]),
        dict(insert=dict(event_date="2026-09-02", regulator_id="ENT_NSW_DPHI", instrument_id=None,
                         site_id="SITE_PROJECT_APOLLO", entity_id=None, event_type="determination",
                         summary="Project Apollo Data Centre, Macquarie Park (SSD-74069708) approved by the A/Director, "
                                 "Industry Assessments under the 18 August 2026 delegation. The City of Ryde objected "
                                 "during exhibition and maintained its objection after the Submissions Report.",
                         outcome="Approved by a departmental officer over a standing council objection.",
                         notes="The only determined NSW data centre read where a local council's objection stood at "
                               "decision and the Commission did not decide (RG-040).",
                         fact_status="VERIFIED", source_id=ar("SSD-74069708"), confidence="high", as_of_date=TODAY),
             add_sources=[dict(id=ar("SSD-74069708"), quote=f"{apollo_obj} | {apollo_kept} | {apollo_deleg}"),
                          dict(id=SRC_SUBS, quote=ryde_apollo)]),
        dict(insert=dict(event_date="2024-01-19", regulator_id=None, instrument_id=None, site_id="SITE_TALAVERA",
                         entity_id=None, event_type="determination",
                         summary="Talavera Road Data Centre Campus Expansion (SSD-24299707) approved by the Independent "
                                 "Planning Commission, a two-Commissioner panel, because the City of Ryde objected and a "
                                 "company connected to the applicant disclosed reportable political donations.",
                         outcome="Approved with conditions.",
                         notes="RG-085: the consent the planning portal publishes leaves the Commissioners' names as "
                               f"'{portal_blank}'; the Commission's own statement of reasons names the panel.",
                         fact_status="VERIFIED", source_id=SRC_IPC_SOR, confidence="high", as_of_date=TODAY),
             add_sources=[dict(id=SRC_IPC_SOR, quote=f"{sor_why} | {sor_panel}"),
                          dict(id=SRC_REFERRAL, quote=f"{ref_rule} | {ref_donation}")]),
        dict(insert=dict(event_date="2020-07-14", regulator_id="ENT_NSW_DPHI", instrument_id=None,
                         site_id="SITE_ROBERTS_RD", entity_id="ENT_CDC", event_type="determination",
                         summary="Roberts Road Data Centre (SSD-10330) approved by the Executive Director, Regions, "
                                 "Industry and Key Sites under the 9 March 2020 delegation, which applied where 'a "
                                 "political disclosure statement has not been made'. The assessment report states no "
                                 "reportable political donations were made by the Applicant in the last two years.",
                         outcome="Approved under delegation.",
                         notes="The project record holds a political donations disclosure statement signed 2 December "
                               "2019 and filed with the EIS, declaring a $7,500 donation on 18 June 2018 (lobbying row "
                               "10). The record read does not say why it did not change who decided. No improper conduct "
                               "is alleged or implied; GIPA-003 asks the Department (RG-069).",
                         fact_status="VERIFIED", source_id=ar("SSD-10330"), confidence="high", as_of_date=TODAY),
             add_sources=[dict(id=ar("SSD-10330"), quote=f"{rr_deleg} {rr_cond} | {rr_none} | {rr_so}"),
                          dict(id="SRC_SSD10330_CONSENT", quote=rr_consent),
                          dict(id=SRC_DON_10330, quote=f"{r_amount} | {r_date} | {r_signed}")]),
        dict(match=dict(id=13),
             set=dict(notes="Recorded as objection_upheld=False in substance - the objection did not prevent approval. "
                            "CORRECTED 2026-10-30 (RG-040): the assessment report says Council 'later advised in "
                            "writing to the Department that its objection has been resolved' before the decision. "
                            "Kept in regulatory_events as well as community_events because it is a formal statutory "
                            "submission, not a community campaign."),
             add_sources=[dict(id=ar("SSD-73761707"), quote=objection_quotes["SSD-73761707"])]),
    ]

    community = [
        dict(match=dict(id=15),
             set=dict(outcome="Resolved before decision: the assessment report says Council 'later advised in writing "
                              "to the Department that its objection has been resolved'. Consent issued 16 September 2026 "
                              "by the Minister's delegate."),
             add_sources=[dict(id=ar("SSD-73761707"), quote=objection_quotes["SSD-73761707"]),
                          dict(id=SRC_SUBS, quote=btown_glen)]),
        dict(insert=dict(event_date="2024-09-24", site_id="SITE_NEXTDC_S5", group_id=None, locality="Macquarie Park",
                         state="NSW", event_type="council_rejection", actor="City of Ryde Council",
                         summary="The City of Ryde's submission on the NEXTDC S5 Data Centre and Innovation Hub EIS "
                                 "(SSD-63168959): 'In short, Council strongly objects to the development as "
                                 "submitted.'",
                         severity=None, outcome="Pending: the application had not been determined when read.",
                         notes="Council submission read from the planning portal (RG-040). Under the 18 August 2026 "
                               "delegation, a council objection no longer stops a departmental officer deciding a data "
                               "centre case (regulatory_events).",
                         fact_status="VERIFIED", source_id=SRC_SUBS, confidence="high", as_of_date=TODAY),
             add_sources=[dict(id=SRC_SUBS, quote=ryde_s5)]),
    ]
    for case, site, council, outcome, words in OBJECTIONS:
        if case == "SSD-73761707":
            continue  # community_events row 15, updated above
        community.append(dict(
            insert=dict(event_date=None, site_id=site, group_id=None, locality=None, state="NSW",
                        event_type="council_rejection", actor=council,
                        summary=f"{council} objected to the data centre application {case}. The Department's "
                                f"assessment report: '{words}'",
                        severity=None, outcome=f"Objection {outcome}.",
                        notes="From the Department's own assessment report (RG-040). Event date not stated in the "
                              "report; the council's letter is in the planning record.",
                        fact_status="VERIFIED", source_id=ar(case), confidence="high", as_of_date=TODAY),
            add_sources=[dict(id=ar(case), quote=objection_quotes[case])]))

    outcome_line = "; ".join(f"{c} {o}" for c, _, _, o, _ in OBJECTIONS)
    gaps = [
        dict(match=dict(id=40),
             set=dict(status="in_progress", as_of_date=TODAY,
                      notes=f"ADVANCED 2026-10-30 (research batch 5). Each council's main submission was fetched for "
                            f"{len(sub_files) + len(sub_locked)} data centre applications in Blacktown, Penrith, "
                            f"Fairfield, Ryde and The Hills: {len(sub_files)} read, {len(sub_locked)} restricted "
                            "(Honeman Close, Macquarie Park, Mamre Road, NEXTDC S4). Ryde's are cover letters whose "
                            "attachments were not fetched. Keyword screen of grounds, not a coding: hunt log. "
                            "OUTCOMES, from every archived assessment report of a determined data centre: the local "
                            f"council objected in eight cases - {outcome_line}; SSD-24299707 stood and the Independent "
                            "Planning Commission decided. Delegations of 2020 and 2022 let a departmental officer decide "
                            "only where the council had not objected; the delegation of 18 August 2026 for data centre "
                            "projects drops that condition, and Project Apollo was approved under it while Ryde's "
                            "objection stood. Ryde 'strongly objects' to NEXTDC S5, undetermined."),
             add_sources=[dict(id=ar("SSD-74069708"), quote=f"{deleg_2026} | {apollo_kept}"),
                          dict(id=SRC_SUBS, quote=f"{btown_glen} | {ryde_s5} | {ryde_apollo}")]),
        dict(match=dict(id=66),
             set=dict(status="in_progress", as_of_date=TODAY,
                      notes="BLOCKED 2026-10-30 (research batch 5). aph.gov.au's robots.txt refuses the research "
                            "crawler, so pages 2 to 6 of the submission list and the submissions themselves were not "
                            "fetched (data/raw/registers/aph/refused.json). The first 20, indexed in September, stand. "
                            "In docs/requests/DOWNLOADS.md for a person.")),
        dict(match=dict(id=15),
             set=dict(as_of_date=TODAY,
                      notes="BLOCKED 2026-10-30 (research batch 5): parliament.nsw.gov.au's robots.txt now refuses the "
                            "research crawler for the inquiry pages and the submission files alike (data/raw/registers/"
                            "nsw_parliament/refused.json). The five hearing transcripts archived in September stand. "
                            "Some submitters publish their own submissions (the Climate Council, the Committee for "
                            "Sydney); the full list needs a person (docs/requests/DOWNLOADS.md). The report was due by "
                            "30 September 2026.")),
        dict(match=dict(id=41),
             set=dict(status="in_progress", as_of_date=TODAY,
                      notes="BLOCKED 2026-10-30 (research batch 5): the submission files at /lcdocs/submissions/ are "
                            "now refused by parliament.nsw.gov.au's robots.txt, as the list page was, so neither "
                            "enumerating nor fetching is open to the crawler. Probing sequential ids was not tried. "
                            "In docs/requests/DOWNLOADS.md for a person.")),
        dict(match=dict(id=48),
             set=dict(as_of_date=TODAY,
                      notes="BLOCKED 2026-10-30 (research batch 5): planning.vic.gov.au's robots.txt refuses the "
                            "research crawler (read as disallow-all), so the Development Facilitation Program's "
                            "decisions were not read. In docs/requests/DOWNLOADS.md.")),
        dict(match=dict(id=56),
             set=dict(as_of_date=TODAY,
                      notes="Supersedes RG-047. BLOCKED 2026-10-30 (research batch 5): planning.vic.gov.au refuses the "
                            "crawler; Maribyrnong's register allows it but is a search application with no listing to "
                            "read. In docs/requests/DOWNLOADS.md.")),
        dict(match=dict(id=11),
             set=dict(as_of_date=TODAY,
                      notes="Partly advanced 2026-09-18: The Guardian (26 July 2026) identifies Syncline Energy as the "
                            "proponent of the Plumpton 'Victorian AI hub', and SITE_MELTON_SYNCLINE is REPORTED/medium. "
                            "2026-10-30 (research batch 5): Melton's and Whittlesea's registers allow the crawler but "
                            "are search applications; planning.vic.gov.au refuses it. Still outstanding: the Melton "
                            "application reference and capacity, and the South Morang approval. In DOWNLOADS.md.")),
        dict(match=dict(id=58),
             set=dict(status="in_progress", as_of_date=TODAY,
                      notes="WORKED 2026-10-30 (research batch 5). Two warning letters are in the NSW data centre "
                            "record: 'CDC Data Centres response warning letter' on Roberts Road (SSD-10330) and a "
                            "warning letter of 29 May 2024, with a Department email about it, on Station Road "
                            "(SSD-33781208). All three are restricted on the portal (data/raw/nsw_planning/attachments/"
                            "restricted.json), as is a 'scanned signed letter' on Roberts Road. GIPA-003 to the "
                            "Department asks for the letters, the responses and the compliance record for data centre "
                            "consents (docs/requests/)."),
             add_sources=[dict(id=SRC_SUBS, quote="Station Road (SSD-33781208): " + objection_quotes["SSD-33781208"])]),
        dict(match=dict(id=39),
             set=dict(as_of_date=TODAY,
                      notes="WORKED 2026-10-30 (research batch 5). The consent requires the Applicant to publish its "
                            "approved plans, monitoring and audit reports on 'its website'. The Applicant is Lehr "
                            "Consultants International (Australia) Pty Ltd; no website for it was found, and "
                            "lehr.com.au belongs to an unrelated recruitment firm. The operator is still not "
                            "established (RG-037). Test again once the operator is known or operation begins.")),
        dict(match=dict(id=69),
             set=dict(status="in_progress", fact_status="VERIFIED", source_id=SRC_DON_10330, confidence="medium",
                      as_of_date=TODAY,
                      notes="ADVANCED 2026-10-30 (research batch 5). SURVEY: the attachment index of 6,866 documents "
                            "across the NSW data centre records holds three donation disclosures. ROBERTS ROAD "
                            "(SSD-10330): image-only, read by OCR and by eye - the company's director and chief "
                            "executive, as applicant, declared $7,500 to the Liberal Party of Australia - NSW Division "
                            "on 18 June 2018 (signed 2 December 2019, filed with the EIS). The Department's assessment "
                            "report says the delegation applied where 'a political disclosure statement has not been "
                            "made' and that no reportable political donations were made by the Applicant in the last "
                            "two years; a delegate decided it. Why the disclosure did not change who decided is not on "
                            "the record. TALAVERA ROAD (SSD-24299707): Macquarie Telecom gave $2,000 and $1,500 to the "
                            "Liberal Party NSW Division and $1,980 to a City of Ryde West Ward campaign group in "
                            "2020-21; with Ryde's objection, that made the Commission the consent authority. MAMRE "
                            "ROAD (SSD-92743706): restricted. Next: the NSW Electoral Commission's disclosure register "
                            "(not yet tried) and GIPA-003. No improper conduct is alleged or implied."),
             add_sources=[dict(id=SRC_DON_10330, quote=f"{r_recipient} | {r_date} | {r_amount}"),
                          dict(id=ar("SSD-10330"), quote=f"{rr_cond} | {rr_none}"),
                          dict(id=SRC_DON_24299707, quote=f"{t_penrith} | {t_epping} | {t_ryde}")]),
        dict(match=dict(id=85),
             set=dict(status="resolved", resolved_date=TODAY, fact_status="VERIFIED", source_id=SRC_IPC_SOR,
                      confidence="high", as_of_date=TODAY,
                      notes="RESOLVED 2026-10-30 (research batch 5). The Commission's own Statement of Reasons for "
                            "Decision (19 January 2024) names the panel of two Commissioners, a Chair and a member, and "
                            "says the Commission was the consent authority because Ryde objected and a company "
                            "connected to the applicant disclosed a reportable political donation. The Department's "
                            "referral letter of 27 November 2023 gives the same grounds under clause 8A of the former "
                            "State and Regional Development SEPP. The consent copy on the planning portal still shows "
                            f"'{portal_blank}' placeholders: the gap is in the portal's copy, not in the decision."),
             add_sources=[dict(id=SRC_IPC_SOR, quote=f"{sor_date} | {sor_panel} | {sor_why}"),
                          dict(id=SRC_REFERRAL, quote=ref_donation)]),
        dict(match=dict(id=16),
             set=dict(as_of_date=TODAY,
                      notes="NOT WORKED in batch 5. The plan sources community opposition only from planning, council "
                            "or parliamentary records, never social media. The council submissions read for RG-040 are "
                            "councils', not groups'; the parliamentary submissions where groups appear are closed to "
                            "the crawler (RG-015, RG-041, RG-066). The register waits on those downloads.")),
    ]

    pack = {
        "pack_id": "who-heard-2026-10",
        "prepared_by": "scripts/curate_who_heard.py",
        "prepared_on": TODAY,
        "sources": sources,
        "rows": {
            "lobbying": lobbying,
            "regulatory_events": regulatory,
            "community_events": community,
            "research_gaps": gaps,
        },
    }
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(pack, fh, indent=1, ensure_ascii=False)
    print(f"wrote {OUT}: {len(sources)} sources, {len(sub_files)} council submissions read, "
          f"{len(OBJECTIONS)} council objections traced to their outcome")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
