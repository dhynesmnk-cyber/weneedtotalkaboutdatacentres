#!/usr/bin/env python3
"""
RG-084: the two Stockland Macquarie Park records are one project (author-approved merge).

The database carried two rows for one consent:
  * SITE_MACQUARIE_PARK_DC - created from the NSW Planning Portal register (rg002), applicant
    recovered from the signed consent (rg060), VERIFIED against SSD-10467; and
  * SITE_STOCKLAND_MP - a seed row from a grade-C market directory, CLAIMED/low, "Stockland
    Macquarie Park Stage 1", under construction, A$264m, reported to be for AWS.

The signed consent and the Department's assessment show they are the same development: the
assessment's capital investment value is approximately $263.6 million (the seed row said A$264m)
and it "presents as a five-storey warehouse building" (the seed row said five-storey). The author
approved the merge on 2026-11-15.

How a merge is done here: the loader has no delete, and the database is rebuilt from the seed on
every run, so the duplicate is removed at its source (data/seed_data.py) and every pack that
referenced it is repointed. This pack carries what the retired row knew onto the surviving row,
and resolves RG-084 with the evidence.

What is carried, and what is not:
  * The consent's site is 11-17 Khartoum Road AND 33-39 Talavera Road (Lot 1 DP 633221). The
    surviving row named only the Khartoum Road frontage; the address is corrected here.
  * status stays "approved" - the consent's own state. The retired row's "under construction",
    its AWS end-user and its September 2026 north-zone start are NOT adopted: they were cited to
    CertifiedStrategic.com, whose archived article does not mention Stockland at all (checked
    here, and by curate_certstrat_review.py). They are recorded as unconfirmed claims and put to
    a human as RG-102. No capacity is invented: neither row had one.
  * The neighbouring Stockland consent (SSD-63235720, Stockland Development Pty Limited, 1-5
    Khartoum Road, Part Lot 2 DP 1043041) is a DIFFERENT consent on a different lot and stays a
    separate row (SITE_KHARTOUM). It is quoted here so the boundary of the merge is on the record.

Loads LAST: rg060 and rg079 write this row's notes and open RG-084, and this pack settles both.

Outputs:
  * data/packs/rg084_macquarie_park_merge.json

Run:
    python3 scripts/curate_rg084.py
    python3 scripts/load_pack.py data/packs/rg084_macquarie_park_merge.json --allow-missing-source
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONSENTS = os.path.join(ROOT, "data", "raw", "nsw_planning", "consents")
DOCS = os.path.join(ROOT, "data", "raw", "nsw_planning", "documents")
CERTSTRAT = os.path.join(ROOT, "data", "raw", "operators", "certifiedstrategic",
                         "top-data-centres-in-australia-2026-directory-and-market-overview.txt")
IDA = os.path.join(ROOT, "data", "raw", "operators", "nswgov",
                   "data-centre-investment-sustainable-development")
OUT_PACK = os.path.join(ROOT, "data", "packs", "rg084_macquarie_park_merge.json")

TODAY = "2026-11-15"
SRC_CONSENTS = "SRC_NSWPORTAL_CONSENTS"
SRC_ASSESSMENT = "SRC_SSD10467_ASSESSMENT"
SRC_PORTAL = "SRC_NSWPORTAL_SSD10467"

SITE = "SITE_MACQUARIE_PARK_DC"
RETIRED = "SITE_STOCKLAND_MP"

ADDRESS = "11-17 Khartoum Road and 33-39 Talavera Road, Macquarie Park (Lot 1 DP 633221)"

# Every quote is checked against the archived text before anything is written.
Q_SCHEDULE1 = ("Application Number: SSD-10467 Applicant: Stockland Trust Management Limited "
               "Consent Authority: Minister for Planning and Public Spaces Site: 11-17 Khartoum "
               "Road and 33-39 Talavera Road, Macquarie Park (Lot 1 DP 633221)")
Q_CIV = "a capital investment value (CIV) of approximately $263.6 millio n"
Q_FORM = "presents as a five-storey warehouse building, surrounded by an access road and landscaped areas."
Q_NEIGHBOUR = ("Application Number: SSD-63235720 Applicant: Stockland Development Pty Limited "
               "Consent Authority: Minister for Planning and Public Spaces Site: 1-5 Khartoum "
               "Road, Macquarie Park Part Lot 2 DP 1043041")
Q_IDA_PROJECTA = "Stockland Project A City of Ryde"
Q_IDA_WITHHELD = "**NB: One IDA endorsed data centre not listed due to commercial sensitivities**"

NOTES = (
    "SCHEDULE 1 APPLICANT ON THE SIGNED CONSENT: Stockland Trust Management Limited (SSD-10467, "
    "determined 28 May 2021) - a second Stockland entity alongside Stockland Development Pty "
    "Limited at 1-5 Khartoum Road (SSD-63235720, a different lot, still a separate record). "
    "Applicant recovered in the 2026-09-18 pypdf re-extraction (RG-065). "
    f"MERGED {TODAY} (RG-084, approved by the author): the former {RETIRED} row ('Stockland "
    "Macquarie Park Stage 1 data centre') described this same consent and has been retired; what "
    "it held is carried here. The consent's site is 11-17 Khartoum Road AND 33-39 Talavera Road, "
    "Lot 1 DP 633221 - the address previously recorded named only the Khartoum Road frontage. "
    "The Department's assessment gives a CIV of approximately $263.6 million (the retired row "
    "said A$264m) and describes a development that 'presents as a five-storey warehouse "
    "building' (the retired row said five-storey). Status stays 'approved', which is what the "
    "consent records. NOT adopted from the retired row: 'under construction', an AWS end-user "
    "and a north-zone start in September 2026. Those were seeded from CertifiedStrategic.com, "
    "whose archived article does not mention Stockland at all, so no archived source states "
    "them; they are unconfirmed claims, kept here as claims and put to a human as RG-102. "
    "No IT capacity is recorded: the retired row had none and no capacity has been read from "
    "this consent."
)

RESOLVED_84 = (
    f"RESOLVED {TODAY}: one project, one consent, one record. The signed SSD-10467 consent names "
    "Stockland Trust Management Limited as applicant and the site as 11-17 Khartoum Road and "
    "33-39 Talavera Road, Macquarie Park (Lot 1 DP 633221). The Department's assessment gives a "
    "CIV of approximately $263.6 million and a development that 'presents as a five-storey "
    f"warehouse building'; the retired {RETIRED} row described a five-storey Macquarie Park data "
    "centre at A$264m. Same site, same scale, same proponent group: the two rows were one "
    "project recorded twice, not two stages. The author approved the merge on 2026-11-15. "
    f"{RETIRED} is removed from data/seed_data.py and every pack referencing it repointed; "
    f"{SITE} survives, with the address corrected to include the Talavera Road frontage and the "
    "retired row's unsourced claims (AWS end-user, under-construction status, September 2026 "
    "start) recorded as claims under RG-102 rather than adopted. NOT merged: SSD-63235720 "
    "(Stockland Development Pty Limited, 1-5 Khartoum Road, Part Lot 2 DP 1043041, 76.4 MW "
    "maximum power consumption) is a separate consent on a separate lot and remains "
    "SITE_KHARTOUM; the Talavera Road campus expansion (SSD-24299707, Macquarie Data Centres) "
    "and the Goodman consent at 4-10 Talavera Road are also separate records."
)

GAP_102 = dict(
    id=102, pillar="A", priority=3, retrieval_method="manual_review", status="open", opened=TODAY,
    question=("Who is the end user of the Macquarie Park Data Centre (SSD-10467, Stockland Trust "
              "Management Limited, 11-17 Khartoum Road and 33-39 Talavera Road), and has "
              "construction started? The retired SITE_STOCKLAND_MP row reported AWS and a "
              "north-zone start in September 2026; no archived source states either."),
    why_it_matters=("An anchor hyperscaler tenancy and a construction start change both the "
                    "Sydney north-zone pipeline and who the NSW approvals are actually for. "
                    "These claims entered the record from a grade-C directory that does not "
                    "mention the project, so they are the weakest provenance in the Macquarie "
                    "Park cluster and survived a merge only as claims."),
    target_source=("Stockland project pages and ASX announcements; the NSW Planning Portal "
                   "record for SSD-10467 (staging plan, construction certificate, any "
                   "modification); AWS Australian infrastructure announcements"),
    notes=(f"OPENED {TODAY} by the RG-084 merge. The seed row cited SRC_CERTSTRAT for 'A$264m', "
           "'for AWS' and 'a north-zone start in September 2026'. The archived article "
           "(data/raw/operators/certifiedstrategic/) does not contain the word 'Stockland' - "
           "checked by this script and by curate_certstrat_review.py - so the citation never "
           "supported the claim. The consent itself records approval, not construction. Nothing "
           "here has been read that names an end user or a start date. Until one is, the "
           "surviving row keeps status 'approved' and no anchor tenant. One lead, no more: the "
           "NSW IDA release of 27 March 2026 lists 'Stockland Project A City of Ryde' (recorded "
           "separately as SITE_STOCKLAND_PROJA) and states '**NB: One IDA endorsed data centre "
           "not listed due to commercial sensitivities**'. Whether the withheld project is this "
           "one is unknown and is not assumed."),
    fact_status="REPORTED", source_id=SRC_PORTAL, confidence="low", as_of_date=TODAY,
    add_sources=[dict(id="SRC_NSW_IDA", quote=f"{Q_IDA_PROJECTA} | {Q_IDA_WITHHELD}")],
)


def normalise(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def archived(base: str, errors: list[str]) -> str:
    """The archived text, with the document's SHA-256 checked where the document is committed."""
    meta_path = base + ".pdf.meta.json"
    if os.path.exists(meta_path):
        meta = json.load(open(meta_path))
        if os.path.exists(base + ".pdf"):
            if hashlib.sha256(open(base + ".pdf", "rb").read()).hexdigest() != meta["sha256"]:
                errors.append(f"{os.path.basename(base)}: fails its SHA-256 check")
    else:
        errors.append(f"{os.path.basename(base)}: no manifest")
    return normalise(open(base + ".txt", encoding="utf-8").read())


def main() -> int:
    errors: list[str] = []
    consent = archived(os.path.join(CONSENTS, "macquarie_park_data_centre"), errors)
    neighbour = archived(os.path.join(CONSENTS, "1_5_khartoum_road_data_centre"), errors)
    assessment = archived(os.path.join(DOCS, "SSD-10467_assessment"), errors)

    for label, body, quote in (("SSD-10467 consent", consent, Q_SCHEDULE1),
                               ("SSD-10467 assessment", assessment, Q_CIV),
                               ("SSD-10467 assessment", assessment, Q_FORM),
                               ("SSD-63235720 consent", neighbour, Q_NEIGHBOUR)):
        if quote not in body:
            errors.append(f"{label}: quote not found: {quote[:80]!r}")

    # The notes say the directory never mentioned this project. If that changes, re-read it.
    directory = normalise(open(CERTSTRAT, encoding="utf-8").read())
    if "Stockland" in directory:
        errors.append("the archived CertifiedStrategic article now mentions Stockland; "
                      "re-read it before claiming the AWS/start-date claims are unsourced")

    # The IDA lead quoted in RG-102.
    ida_meta = json.load(open(IDA + ".html.meta.json"))
    if hashlib.sha256(open(IDA + ".html", "rb").read()).hexdigest() != ida_meta["sha256"]:
        errors.append("NSW IDA release: fails its SHA-256 check")
    ida = normalise(open(IDA + ".txt", encoding="utf-8").read())
    for q in (Q_IDA_PROJECTA, Q_IDA_WITHHELD):
        if q not in ida:
            errors.append(f"NSW IDA release: quote not found: {q[:60]!r}")

    # The address must be the consent's own words, not a paraphrase of them.
    if " ".join(re.findall(r"[A-Za-z0-9-]+", ADDRESS)) not in " ".join(re.findall(r"[A-Za-z0-9-]+", Q_SCHEDULE1)):
        errors.append("the address is not stated in the consent's Schedule 1 quote")

    if errors:
        print("refusing to write; fix these first:", file=sys.stderr)
        for e in errors:
            print(f"  {e}", file=sys.stderr)
        return 1

    sites = [dict(
        match=dict(id=SITE),
        set=dict(address=ADDRESS, notes=NOTES, fact_status="VERIFIED", confidence="high",
                 as_of_date=TODAY, source_id=SRC_CONSENTS),
        add_sources=[dict(id=SRC_CONSENTS, quote=Q_SCHEDULE1),
                     dict(id=SRC_ASSESSMENT, quote=f"{Q_CIV} | {Q_FORM}")],
    )]

    gaps = [
        dict(match=dict(id=84),
             set=dict(status="resolved", resolved_date=TODAY, notes=RESOLVED_84,
                      fact_status="VERIFIED", confidence="high", as_of_date=TODAY,
                      source_id=SRC_CONSENTS),
             add_sources=[dict(id=SRC_CONSENTS, quote=f"{Q_SCHEDULE1} | {Q_NEIGHBOUR}"),
                          dict(id=SRC_ASSESSMENT, quote=f"{Q_CIV} | {Q_FORM}")]),
        {k: v for k, v in GAP_102.items() if k != "add_sources"},
        # add_sources is only honoured on append-only inserts, and research_gaps has an integer
        # primary key: attach the quote with a follow-up match/set (loader defect 6).
        dict(match=dict(id=102), set={}, add_sources=GAP_102["add_sources"]),
    ]

    pack = {
        "pack_id": "rg084-macquarie-park-merge-2026-11",
        "prepared_by": "scripts/curate_rg084.py from data/raw/nsw_planning/",
        "prepared_on": TODAY,
        "_comment": [
            "Author-approved merge of SITE_STOCKLAND_MP into SITE_MACQUARIE_PARK_DC (RG-084).",
            "The duplicate is deleted at its source in data/seed_data.py; this pack carries its",
            "content onto the surviving row, corrects the address from the consent's Schedule 1,",
            "and keeps the directory's AWS / under-construction / September-2026 claims as",
            "unconfirmed claims (RG-102) rather than adopting them. Loads last.",
        ],
        "sources": [],
        "rows": {"sites": sites, "research_gaps": gaps},
    }
    with open(OUT_PACK, "w") as f:
        json.dump(pack, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print(f"RG-084 resolved: {RETIRED} merged into {SITE}; address corrected; "
          f"RG-102 opened; wrote {os.path.relpath(OUT_PACK, ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
