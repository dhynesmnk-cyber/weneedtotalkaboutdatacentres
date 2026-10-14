#!/usr/bin/env python3
"""
Curate the CertifiedStrategic source review: regrades SRC_CERTSTRAT, withdraws the one claim it
carried that no primary source supports, corrects a transcription error, counts the HCF register,
and opens the gap for what still rests on the article alone.

Why: a review on 2026-10-14 found that one CertifiedStrategic.com article had been the sole source
for 27 of 93 sites and 25 of the 26 Certified Strategic flags, plus 8 entities, the HCF instrument
row, a security record, 5 metrics and 2 planning applications. The rubric grades by document
class, and the article is an aggregator's directory piece that relays other firms' research, so
it is class C (reports/findings_memo.md, grading table). It was never archived. Batches S3 and S4
have since confirmed every flag against the Commonwealth register (RG-096) and cited operators'
own pages, so no site rests on it alone; the rest is RG-100.

The register (SRC_HCF_REGISTER, archived by curate_hcf_register.py) is counted here, from the
archived page and with that script's own parser, rather than copied from the article. It does not
name its department, so the article's attribution of the framework to the DTA is withdrawn rather
than replaced: the only evidence for Home Affairs is search-engine summaries, which sit below
grade D (reports/palantir_australia_triage.md) and are recorded in RG-100 as leads, never as facts.

Run:
    python3 scripts/curate_certstrat_review.py
    python3 scripts/load_pack.py data/packs/certstrat_review.json --allow-missing-source
"""
from __future__ import annotations

import hashlib
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from curate_hcf_register import ARCHIVE, MATCHES, page_text, register  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "data", "packs", "certstrat_review.json")
TODAY = "2026-10-14"
SRC = "SRC_CERTSTRAT"
REGISTER = "SRC_HCF_REGISTER"
PAUSE = ("The Department will pause the HCF Certification registration of prospective service providers "
         "and HCF Certified providers seeking supplementary assessment effective from 3 November 2025 until "
         "HCF reforms have been completed. HCF Certified providers will not be impacted.")

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
               "it said on 18 September 2026 cannot be shown. Rows resting on it alone are to be re-sourced "
               "from primary records (RG-100)."),
]


def read_register() -> tuple[dict, str]:
    """The archived register's data centre lists, and its capture date. Refuses a failed hash."""
    raw = open(ARCHIVE, "rb").read()
    meta = json.load(open(ARCHIVE + ".meta.json"))
    if hashlib.sha256(raw).hexdigest() != meta["sha256"]:
        raise SystemExit("archived HCF register fails its SHA-256 check")
    errors: list[str] = []
    entries = register(page_text(raw.decode("utf-8")), errors)
    if errors:
        raise SystemExit("cannot read the archived HCF register: " + "; ".join(errors))
    return entries, meta["capture_utc"][:10]


def main() -> int:
    entries, captured = read_register()
    count = {scope: sum(len(e["facilities"]) for es in entries.values() for e in es if e["scope"] == scope)
             for scope in ("facility", "enclave")}
    covered = {(p, f) for p, fs in MATCHES.values() for f in fs}
    unmatched = [f"{p} {', '.join(miss)} ({e['scope']})"
                 for p, es in entries.items() for e in es
                 if (miss := [f for f in e["facilities"] if (p, f) not in covered])]

    legal_updates = [
        dict(match=dict(id="LAW_HCF"),
             set=dict(summary="Certified Strategic is the highest designation and is required for sensitive "
                              "and PROTECTED government workloads. The register lists "
                              f"{count['facility']} Certified Strategic facilities and {count['enclave']} "
                              f"enclaves across {len(entries)} providers (archive of {captured}), and states "
                              "that registration of prospective providers and supplementary assessments are "
                              "paused from 3 November 2025 until the framework's reforms are complete. Which "
                              "agency administers the framework is not established from a primary source "
                              "here: the register names only 'the Department', and releases up to v2.2.0 "
                              "named the Digital Transformation Agency on an aggregator's authority, which is "
                              "withdrawn (RG-100).",
                      confidence="medium"),
             add_sources=[dict(id=REGISTER, quote=PAUSE)]),
    ]

    entity_updates = [
        dict(match=dict(id="ENT_DTA"),
             set=dict(notes="Named by CertifiedStrategic.com (March 2026) as administrator of the Hosting "
                            "Certification Framework (Certified Strategic / Certified Assured). That attribution "
                            "is withdrawn: it rests on a grade C aggregator, and the register itself names only "
                            "'the Department'. Which agency administers the framework today is open (RG-100).",
                      confidence="low"),
             add_sources=[]),
    ]

    metrics = [
        dict(match=dict(metric_name="hcf_certified_strategic_facilities_national", source_id=SRC),
             set=dict(scope="Australia", confidence="low",
                      notes="60 Certified Strategic facilities and enclaves nationally across 13 providers, as "
                            "CertifiedStrategic.com stated it in March 2026. Superseded by "
                            "hcf_certified_strategic_register, counted from the register itself. CORRECTED "
                            "2026-10-14: releases up to v2.2.0 tagged this national count with scope NSW."),
             add_sources=[]),
        dict(as_of=captured, scope="Australia", metric_name="hcf_certified_strategic_register",
             value=float(count["facility"] + count["enclave"]), unit="count", basis="actual",
             notes=f"{count['facility']} Certified Strategic facilities and {count['enclave']} enclaves across "
                   f"{len(entries)} providers on the HCF register's Certified Service Providers page (Internet "
                   f"Archive capture of {captured}), counted from the archived page by "
                   "scripts/curate_certstrat_review.py with curate_hcf_register.py's parser. A facility the "
                   "register names once counts once. Cloud services are listed separately and not counted.",
             fact_status="VERIFIED", confidence="high", as_of_date=captured, source_id=REGISTER),
    ]

    # M4 was the one row graded high on this source alone. Its IT capacity is not changed here:
    # operator_sources.json reports NEXTDC's own page (150 MW) against it for a human to settle.
    sites = [
        dict(match=dict(id="SITE_NEXTDC_M4"),
             set=dict(confidence="medium",
                      notes="Victorian Government development approval January 2026. Designed for AI, defence "
                            "and sovereign technology workloads; rack densities above 1,000 kW; direct-to-chip "
                            "liquid cooling. The 162 MW IT capacity, A$2bn cost and approval date came from a "
                            "grade C aggregator article; NEXTDC's own M4 page gives 150 MW of IT capacity "
                            "(operator_sources pack), and which figure stands is for a human to settle "
                            "(RG-100)."),
             add_sources=[]),
    ]

    gaps = [
        dict(id=100, pillar="A", priority=4, retrieval_method="manual_review", status="open", opened=TODAY,
             question="Replace CertifiedStrategic.com (SRC_CERTSTRAT) for the rows that still rest on it "
                      "alone: four national capacity figures it relays second-hand (Mandala 1,350 MW in 2024 "
                      "and 3,100 MW by 2030; CBRE 1,400 MW in 2025 and 1,800 MW by 2028), eight entity notes, "
                      "the HCF instrument row, a security record and two planning applications; and settle "
                      "NEXTDC M4's IT capacity, 162 MW from the article against 150 MW on NEXTDC's own page.",
             why_it_matters="When reviewed, the article was the sole source for 27 of the 93 sites and 25 of "
                            "the 26 Certified Strategic flags. Batches S3 and S4 have since confirmed every flag "
                            "against the Commonwealth register (RG-096) and cited operators' own pages, so no "
                            "site rests on it alone. What remains is aggregate and descriptive: national "
                            "capacity figures, provider descriptions and the framework's own record. A grade C "
                            "aggregator should not be the only citation for any of them.",
             target_source="Mandala Partners, Data Centres as Enabling Infrastructure; CBRE's Australian data "
                           "centre report, August 2025; each provider's own pages; NEXTDC's M4 page, already "
                           "archived by operator_sources.json; the HCF register, archived by "
                           "curate_hcf_register.py",
             notes="FROM THE ARCHIVED REGISTER (primary, SRC_HCF_REGISTER): it lists data centre facilities "
                   "that match no site record here: " + "; ".join(unmatched) + ". RG-096 matched only "
                   "existing records, so these are candidates for new site rows. LEADS ONLY, from "
                   "search-engine summaries read on 2026-10-14 (below grade D, not relied on, and kept out of "
                   "every fact row): the framework appears to have moved from the Digital Transformation "
                   "Agency to the Department of Home Affairs on 1 May 2023, and the publisher's own pages "
                   "appear to give 60, 61 and 62 certified sites. Also check whether the article supports "
                   "ENT_VANTAGE and ENT_AUSTRALIANSUPER at all: both cite it for European and superannuation "
                   "holdings that a directory article is unlikely to carry. The review found the article "
                   "right where it copied a document directly: its 504 MW for Marsden Park is the IT load in "
                   "the Department's assessment report.",
             fact_status="VERIFIED", confidence="high", as_of_date=TODAY, source_id=SRC),
    ]

    pack = {
        "pack_id": "certstrat-review-2026-10",
        "prepared_by": "scripts/curate_certstrat_review.py",
        "prepared_on": TODAY,
        "sources": SOURCES,
        "rows": {
            "legal_instruments": legal_updates,
            "entities": entity_updates,
            "metrics": metrics,
            "sites": sites,
            "research_gaps": gaps,
        },
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(pack, fh, indent=1)
    print(f"wrote {OUT}: register {count['facility']} facilities + {count['enclave']} enclaves across "
          f"{len(entries)} providers; {len(unmatched)} register lines match no site; gaps={len(gaps)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
