#!/usr/bin/env python3
"""
Curate the status pack: records progress on RG-007, RG-013 and RG-023 and links the FOI strategy.

Run:
    python3 scripts/curate_status.py
    python3 scripts/load_pack.py data/packs/status_updates.json --allow-missing-source
"""
from __future__ import annotations

import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "data", "packs", "status_updates.json")
TODAY = "2026-09-18"

SOURCES = [
    dict(id="SRC_GIPA_IPC",
         title="Fact sheet - Your right to access government information (GIPA Act application fee and "
               "processing charges)",
         publisher="NSW Information and Privacy Commission",
         url="https://www.ipc.nsw.gov.au/resources/fact-sheet-your-right-access-government-information",
         doc_type="primary_government", published=None, credibility="A", accessed=TODAY,
         notes="Confirms the $30 standard application fee for a formal GIPA access application, that the "
               "application is invalid until the fee is paid, and that processing charges apply at $30 per "
               "hour with a possible 50% reduction for some applicants."),
    dict(id="SRC_VIC_FOI",
         title="Freedom of information: Victorian Government (Freedom of Information Act 1982)",
         publisher="Victorian Government",
         url="https://www.schools.vic.gov.au/freedom-information-victorian-government",
         doc_type="primary_government", published=None, credibility="A", accessed=TODAY,
         notes="The FOI Act 1982 (Vic) gives a right to apply for access to documents held by Victorian "
               "government agencies and ministers; applications go to the specific agency."),
]

GAP_UPDATES = [
    dict(match=dict(id=7),
         set=dict(status="in_progress",
                  retrieval_method="foi_request",
                  notes="STRATEGY DRAFTED 2026-09-18, not yet lodged - see reports/RG007_foi_strategy.md. Five "
                        "request templates are written for Revenue NSW, NSW DPHI/Investment NSW, SRO Victoria, "
                        "Queensland Revenue Office and Commonwealth Treasury/FIRB. All are framed to seek "
                        "policy instruments, determinations, guidelines and aggregate counts rather than "
                        "individual taxpayer assessments, because a request naming a taxpayer will be refused "
                        "on confidentiality grounds and would waste the attempt. NSW fee $30 per request under "
                        "the GIPA Act with processing at $30/hour. Four free parallel routes are identified "
                        "that should be worked FIRST: (1) the published NSW Voluntary Planning Agreements "
                        "register; (2) state budget papers and Treasurer's determinations searched for 'data "
                        "centre' 2019-20 to 2026-27; (3) submissions to the NSW Data Centre Consultation Paper "
                        "(March 2026), where industry and unions lobby for or against concessions and so "
                        "disclose whether they exist; (4) the NSW Legislative Council data centres inquiry "
                        "submissions and the 29 May 2026 hearing transcripts, where a direct question to a "
                        "revenue officer in public is the fastest possible answer. Route 4 may resolve this "
                        "before any FOI is decided. A documented negative is recorded as incentive_type "
                        "'none_found' with fact_status VERIFIED and is treated as a publishable finding that "
                        "settles Pillar B in the sector's favour.",
                  fact_status="VERIFIED", confidence="high", as_of_date=TODAY, source_id="SRC_GIPA_IPC"),
         add_sources=["SRC_GIPA_IPC", "SRC_VIC_FOI"]),
    dict(match=dict(id=13),
         set=dict(status="in_progress",
                  notes="Advanced again 2026-09-18. The complete NSW data centre SSD register (46 records) "
                        "contains NO project titled AWS, Amazon, Google or Meta; Microsoft appears only through "
                        "its proponent entity Microsoft Datacentre (Australia) Pty Ltd on Kemps Creek "
                        "SSD-10101987 (approved, operating) and Honeman Close SSD-58601963 (in Assessment, "
                        "description references 96 MW). Conclusion: hyperscaler footprints CANNOT be mapped "
                        "from NSW planning titles. The sector's convention is codenames - Project Duke, Atlas, "
                        "Echidna, Apollo, Pluto, Mars, KC1, Road 1 - and the NSW Government's own IDA release "
                        "confirms it (Goodman's 'Project Atlas', Stockland's 'Project A'), with one endorsed "
                        "project withheld entirely for commercial sensitivity. Remaining routes are ASIC "
                        "resolution of the codename SPVs (RG-035), landlord tenancy disclosure, and Victorian "
                        "and Queensland registers. AWS and Google remain entirely unresolved.",
                  fact_status="VERIFIED", confidence="high", as_of_date=TODAY,
                  source_id="SRC_NSWPORTAL_REGISTER"),
         add_sources=["SRC_NSWPORTAL_REGISTER"]),
    dict(match=dict(id=15),
         set=dict(priority=5,
                  notes="Priority RAISED from 4 to 5 on 2026-09-18. The inquiry record is now the most "
                        "promising free route to closing RG-007: a question put to a revenue officer in the "
                        "29 May 2026 public hearings, or a submission from an industry body or union, would "
                        "settle whether payroll tax or land tax concessions exist without waiting 8-12 weeks "
                        "for an FOI decision. Approximately 120+ submissions are freely downloadable and the "
                        "terms of reference were updated 5 August 2026.",
                  fact_status="VERIFIED", confidence="high", as_of_date=TODAY, source_id="SRC_NSWINQ"),
         add_sources=[]),
    dict(match=dict(id=23),
         set=dict(status="resolved", resolved_date=TODAY,
                  notes="RESOLVED as a negative finding on 2026-09-18, and re-scoped to RG-035 for the "
                        "constructive work. The question 'can AWS and Google sites be mapped from NSW planning "
                        "records?' is answered: no. All 46 data centre SSD records were harvested and none is "
                        "titled AWS, Amazon, Google or Meta. The remaining work - resolving codename SPVs via "
                        "ASIC and the title documents attached to each application - is RG-035.",
                  fact_status="VERIFIED", confidence="high", as_of_date=TODAY,
                  source_id="SRC_NSWPORTAL_REGISTER"),
         add_sources=["SRC_NSWPORTAL_REGISTER"]),
    dict(match=dict(id=10),
         set=dict(notes="Unchanged in substance, but note the interaction with the NSW register harvest: the "
                        "reported ~1 GW WA facility could not be located in any NSW record because WA is a "
                        "different jurisdiction operating the Wholesale Electricity Market. AEMO records 15 "
                        "operational data centre sites across the South West Interconnected System. The WA "
                        "route is the WA Planning Commission's development application register and Western "
                        "Power connection data, not the NSW portal.",
                  fact_status="REPORTED", confidence="medium", as_of_date=TODAY,
                  source_id="SRC_NSWPORTAL_REGISTER"),
         add_sources=[]),
]

INCENTIVE_UPDATES = [
    dict(match=dict(jurisdiction="All", incentive_type="alleged"),
         set=dict(notes="AUDIT REQUIRED - strategy now drafted. The industry body Data Centres Australia "
                        "asserts that data centres pay all standard taxes and receive no special concessions. "
                        "No primary revenue-office evidence either way has been located. Five FOI request "
                        "templates are drafted at reports/RG007_foi_strategy.md, framed to seek policy "
                        "instruments and aggregate counts rather than named taxpayer assessments so that they "
                        "are arguably releasable. Four free parallel routes are identified that should be "
                        "worked first, of which the NSW Legislative Council inquiry record is the most "
                        "promising. A documented negative will be recorded as incentive_type 'none_found' with "
                        "fact_status VERIFIED and published as a finding that settles the question in the "
                        "sector's favour.",
                  fact_status="GAP", confidence="low", as_of_date=TODAY, source_id="SRC_GIPA_IPC"),
         add_sources=["SRC_GIPA_IPC"]),
]


def main() -> int:
    pack = {
        "pack_id": "status-updates-2026-09",
        "prepared_by": "scripts/curate_status.py",
        "prepared_on": TODAY,
        "sources": SOURCES,
        "rows": {
            "research_gaps": GAP_UPDATES,
            "incentives": INCENTIVE_UPDATES,
        },
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(pack, fh, indent=1)
    print(f"wrote {OUT}: gap_updates={len(GAP_UPDATES)} incentive_updates={len(INCENTIVE_UPDATES)} "
          f"sources={len(SOURCES)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
