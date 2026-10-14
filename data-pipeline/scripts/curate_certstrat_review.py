#!/usr/bin/env python3
"""
Curate the CertifiedStrategic source review: regrades SRC_CERTSTRAT, withdraws the one claim it
carried that the review could not stand behind, corrects a transcription error, and opens the gap
that replaces it with primary sources.

Why: a review on 2026-10-14 found that one CertifiedStrategic.com article is the sole source for
27 of 93 sites and 25 of the 26 Certified Strategic flags, plus 8 entities, the HCF instrument
row, a security record, 5 metrics and 2 planning applications. The rubric grades by document
class, and the article is an aggregator's directory piece that relays other firms' research, so
it is class C (reports/findings_memo.md, grading table). It was never archived.

What this pack does NOT do: it registers no new source. The review's leads about the framework
(its administering agency, the registration pause, providers absent from this database) came from
search-engine summaries, which sit below grade D (reports/palantir_australia_triage.md). They are
recorded in RG-097 as leads to check, never as facts.

Run:
    python3 scripts/curate_certstrat_review.py
    python3 scripts/load_pack.py data/packs/certstrat_review.json --allow-missing-source
"""
from __future__ import annotations

import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "data", "packs", "certstrat_review.json")
TODAY = "2026-10-14"
SRC = "SRC_CERTSTRAT"

# Re-declared in full because the loader upserts sources. Every field except credibility and the
# appended review note is as the seed registered it; 'accessed' stays the date it was read.
SOURCES = [
    dict(id=SRC, title="Top Data Centres in Australia: 2026 Directory and Market Overview",
         publisher="CertifiedStrategic.com",
         url="https://certifiedstrategic.com/insights/top-data-centres-in-australia-2026-directory-and-market-overview",
         doc_type="market_research", published="2026-03-04", accessed="2026-09-18", credibility="C",
         notes="60 Hosting Certification Framework 'Certified Strategic' facilities across 13 providers; "
               "operator-by-operator site lists; NEXTDC M4 Fishermans Bend 162 MW / A$2bn approval January "
               "2026; CDC Marsden Park 504 MW; Mandala 1,350 MW (2024) to 3,100 MW (2030); CBRE ~1.4 GW "
               "(2025) to ~1.8 GW (2028). REGRADED B to C on 2026-10-14: an aggregator's directory article "
               "that relays other firms' research (the Mandala and CBRE figures above are second-hand), which "
               "is class C under the rubric, as for the GovMarket aggregator. Not archived when read, so what "
               "it said on 18 September 2026 cannot be shown. Rows resting on it are to be re-sourced from "
               "primary records (RG-097)."),
]

LEGAL_UPDATES = [
    dict(match=dict(id="LAW_HCF"),
         set=dict(summary="Certified Strategic is the highest designation and is required for sensitive and "
                          "PROTECTED government workloads. CertifiedStrategic.com stated in March 2026 that 60 "
                          "Certified Strategic facilities and enclaves are operated by 13 providers. Which agency "
                          "administers the framework today is not established from a primary source here: "
                          "releases up to v2.2.0 named the Digital Transformation Agency on the same article's "
                          "authority, and that attribution is withdrawn pending the official register (RG-097).",
                  confidence="low"),
         add_sources=[]),
]

ENTITY_UPDATES = [
    dict(match=dict(id="ENT_DTA"),
         set=dict(notes="Named by CertifiedStrategic.com (March 2026) as administrator of the Hosting "
                        "Certification Framework (Certified Strategic / Certified Assured). That attribution is "
                        "withdrawn: it rests on a grade C aggregator and no primary source for it has been read. "
                        "Which agency administers the framework today is open (RG-097).",
                  confidence="low"),
         add_sources=[]),
]

METRIC_UPDATES = [
    dict(match=dict(metric_name="hcf_certified_strategic_facilities_national", source_id=SRC),
         set=dict(scope="Australia", confidence="low",
                  notes="60 Certified Strategic facilities and enclaves nationally across 13 providers, as "
                        "CertifiedStrategic.com stated it in March 2026, unchanged during the certification "
                        "pause. Not checked against the official register (RG-097). CORRECTED 2026-10-14: "
                        "releases up to v2.2.0 tagged this national count with scope NSW."),
         add_sources=[]),
]

# M4 was the one row graded high on this source alone. The other rows resting on it are already
# medium or lower and stay as they are until RG-097 re-sources them.
SITE_UPDATES = [
    dict(match=dict(id="SITE_NEXTDC_M4"),
         set=dict(confidence="medium",
                  notes="Victorian Government development approval January 2026. Designed for AI, defence and "
                        "sovereign technology workloads; rack densities above 1,000 kW; direct-to-chip liquid "
                        "cooling. Capacity, cost and approval date rest on one grade C aggregator article, to be "
                        "confirmed against NEXTDC's own announcement (RG-097)."),
         add_sources=[]),
]

GAPS = [
    dict(id=97, pillar="A", priority=5, retrieval_method="manual_review", status="open", opened=TODAY,
         question="Replace CertifiedStrategic.com (SRC_CERTSTRAT) with primary records for every row that rests "
                  "on it: the official Hosting Certification Framework register for the Certified Strategic "
                  "flags and the operational sites listed from it, NEXTDC's announcement for M4, and the "
                  "original Mandala and CBRE reports for the four national capacity figures.",
         why_it_matters="One grade C aggregator article, never archived, is the sole source for 27 of the 93 "
                        "sites and for 25 of the 26 Certified Strategic flags, and also supports 8 entities, the "
                        "HCF instrument row, a security record, 5 metrics and 2 planning applications. The "
                        "certified operational sites are the sovereign-hosting layer of the record, and today "
                        "none of them has a primary source, a coordinate or a capacity.",
         target_source="https://www.hostingcertification.gov.au/certified-service-providers (archive with "
                       "SHA-256); NEXTDC ASX announcement on M4 Fishermans Bend (January 2026); Mandala Partners, "
                       "Data Centres as Enabling Infrastructure; CBRE Australian data centre report, August 2025",
         notes="LEADS ONLY, from search-engine summaries read on 2026-10-14 (below grade D, not relied on, and "
               "kept out of every fact row): the framework appears to have moved from the Digital Transformation Agency to the "
               "Department of Home Affairs on 1 May 2023, with registration of new providers and supplementary "
               "assessments paused from 3 November 2025; the register appears to list providers this database "
               "has no flag for (Australian Data Centres at Mitchell and Fyshwick, Cloud Carrier DB1, DigiCo "
               "BNE2 and SYD1, Fujitsu at Western Sydney and Homebush); the publisher's own pages appear to give "
               "60, 61 and 62 certified sites; and press summaries give NEXTDC M4 as 150 MW as well as 162 MW. "
               "Also check whether the article supports ENT_VANTAGE and ENT_AUSTRALIANSUPER at all: both cite "
               "it for European and superannuation holdings that a directory article is unlikely to carry. The "
               "review found the article right where it copied a document directly: its 504 MW for Marsden Park "
               "matches the portal's power consumption, which this database had misfiled until RG-096.",
         fact_status="VERIFIED", confidence="high", as_of_date=TODAY, source_id=SRC),
]


def main() -> int:
    pack = {
        "pack_id": "certstrat-review-2026-10",
        "prepared_by": "scripts/curate_certstrat_review.py",
        "prepared_on": TODAY,
        "sources": SOURCES,
        "rows": {
            "legal_instruments": LEGAL_UPDATES,
            "entities": ENTITY_UPDATES,
            "metrics": METRIC_UPDATES,
            "sites": SITE_UPDATES,
            "research_gaps": GAPS,
        },
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(pack, fh, indent=1)
    print(f"wrote {OUT}: sources={len(SOURCES)} updates="
          f"{len(LEGAL_UPDATES) + len(ENTITY_UPDATES) + len(METRIC_UPDATES) + len(SITE_UPDATES)} gaps={len(GAPS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
