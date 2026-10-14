#!/usr/bin/env python3
"""
Curate the CertifiedStrategic source review: regrades SRC_CERTSTRAT, withdraws the claims it carried
that no primary source supports, corrects a transcription error, counts the HCF register, re-sources
what primary records now reach, and keeps the gap for the rest.

Why: a review on 2026-10-14 found that one CertifiedStrategic.com article had been the sole source
for 27 of 93 sites and 25 of the 26 Certified Strategic flags, plus 8 entities, the HCF instrument
row, a security record, 5 metrics and 2 planning applications. The rubric grades by document
class, and the article is an aggregator's directory piece that relays other firms' research, so
it is class C (reports/findings_memo.md, grading table). Batches S3 and S4 have since confirmed
every flag against the Commonwealth register (RG-096) and cited operators' own pages, so no site
rests on it alone; the rest is RG-100.

RG-100, worked 2026-10-14. The article is archived (data/raw/operators/certifiedstrategic/), in the
version last modified 2026-10-02; what it said when read on 2026-09-18 cannot be shown. Read
against our rows: it names the DTA as the framework's administrator, gives M4 as 162 MW and A$2bn,
Marsden Park as 504 MW and November 2025, and relays Mandala and CBRE figures; it does not mention
Vantage, AustralianSuper, AirTrunk SYD3 or Stockland, all four of which cited it. The register
(SRC_HCF_REGISTER) now supports the provider counts in five entity notes and the Macquarie record,
which this script derives from the archived page with curate_hcf_register.py's parser. Mandala's
November 2025 report, which the article names for the 1,350 MW and 3,100 MW figures, is archived
and does not state them.

The register does not name its department, so the DTA attribution is withdrawn rather than
replaced: the only evidence for Home Affairs is search-engine summaries, which sit below grade D
(reports/palantir_australia_triage.md) and are recorded in RG-100 as leads, never as facts.

Run:
    python3 scripts/curate_certstrat_review.py
    python3 scripts/load_pack.py data/packs/certstrat_review.json --allow-missing-source
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from curate_hcf_register import ARCHIVE, ENCLAVE, FACILITY, MATCHES, page_text, register  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "data", "packs", "certstrat_review.json")
ARTICLE = os.path.join(ROOT, "data", "raw", "operators", "certifiedstrategic",
                       "top-data-centres-in-australia-2026-directory-and-market-overview.html")
MANDALA = os.path.join(ROOT, "data", "raw", "operators", "mandala", "Data-Centres-as-Enabling-Infrastructure")
TODAY = "2026-10-14"
SRC = "SRC_CERTSTRAT"
REGISTER = "SRC_HCF_REGISTER"
MANDALA_SRC = "SRC_MANDALA_DCEI_2025"
PAUSE = ("The Department will pause the HCF Certification registration of prospective service providers "
         "and HCF Certified providers seeking supplementary assessment effective from 3 November 2025 until "
         "HCF reforms have been completed. HCF Certified providers will not be impacted.")
HIGHEST = ("Strategic Certification enclave and facility providers represents the highest level of assurance "
           "to Australian Government customers and offers the most secure storage solutions for government "
           "held data.")
CLOUD = "Service Provider and Certified Strategic Service:"

# Entities whose HCF facts the register states, by the provider name the register uses.
REGISTER_PROVIDER = {
    "ENT_EQUINIX": "Equinix Australia",
    "ENT_DIGITALREALTY": "Digital Realty",
    "ENT_MACQUARIE_TG": "Macquarie Technology Group",
    "ENT_DCI": "DCI Data Centers",
    "ENT_TELSTRA": "Telstra",
}


def verified(path: str, ext: str) -> bytes:
    """An archived file, refused if it fails the SHA-256 its manifest records."""
    raw = open(path + ext, "rb").read()
    if hashlib.sha256(raw).hexdigest() != json.load(open(path + ext + ".meta.json"))["sha256"]:
        raise SystemExit(f"{os.path.relpath(path + ext, ROOT)} fails its SHA-256 check")
    return raw


def read_register() -> tuple[dict, list[str], str]:
    """The archived register's data centre lists, its cloud service providers, and its capture date."""
    raw = verified(ARCHIVE[: -len(".html")], ".html")
    meta = json.load(open(ARCHIVE + ".meta.json"))
    lines = page_text(raw.decode("utf-8"))
    errors: list[str] = []
    entries = register(lines, errors)
    if errors:
        raise SystemExit("cannot read the archived HCF register: " + "; ".join(errors))
    start = lines.index(CLOUD) + 1
    cloud = []
    for line in lines[start:]:
        if line.startswith("If the Service Provider"):
            break
        cloud.append(line)
    return entries, cloud, meta["capture_utc"][:10]


def article_body() -> tuple[str, str]:
    """The archived article's text and last-modified date, from its schema.org NewsArticle."""
    raw = verified(ARTICLE[: -len(".html")], ".html").decode("utf-8")
    for block in re.findall(r'<script type="application/ld\+json">(.*?)</script>', raw, re.S):
        data = json.loads(block)
        if data.get("@type") == "NewsArticle":
            return data["articleBody"], data["dateModified"][:10]
    raise SystemExit("archived article has no NewsArticle body")


def main() -> int:
    entries, cloud, captured = read_register()
    body, modified = article_body()
    # Checks the notes below rely on. Each refuses rather than writes a claim the archive does not hold.
    for absent in ("Vantage", "AustralianSuper", "SYD3", "Stockland"):
        if absent in body:
            raise SystemExit(f"the archived article mentions {absent}; revise the notes that say it does not")
    for stated in ("Digital Transformation Agency", "162MW", "504MW Marsden Park", "1,350MW", "3,100MW",
                   "groundbreaking October 2024"):
        if stated not in body:
            raise SystemExit(f"the archived article no longer states {stated!r}; revise the notes")
    # Only the Mandala manifest is committed (a commercial report), so the check runs where the
    # archive is held and the manifest's hash is what a fresh clone can compare a download against.
    if os.path.exists(MANDALA + ".pdf"):
        verified(MANDALA, ".pdf")
        if re.search(r"1,?350\s*MW|3,?100\s*MW", open(MANDALA + ".txt", encoding="utf-8").read()):
            raise SystemExit("Mandala's November 2025 report states the figures after all; revise RG-100")

    count = {scope: sum(len(e["facilities"]) for es in entries.values() for e in es if e["scope"] == scope)
             for scope in ("facility", "enclave")}
    covered = {(p, f) for p, fs in MATCHES.values() for f in fs}
    unmatched = [f"{p} {', '.join(miss)} ({e['scope']})"
                 for p, es in entries.items() for e in es
                 if (miss := [f for f in e["facilities"] if (p, f) not in covered])]
    cloud_providers = {re.split(r"\s+[–-]\s+", line, maxsplit=1)[0].strip(): line for line in cloud}
    both = sorted(set(entries) & set(cloud_providers))
    if both != ["Macquarie Technology Group"]:
        raise SystemExit(f"providers on both the data centre and cloud lists are now {both}; revise record 4")

    def register_quote(provider: str) -> str:
        lines = [f"{FACILITY if e['scope'] == 'facility' else ENCLAVE} {e['line']}" for e in entries[provider]]
        if provider in cloud_providers:
            lines.append(f"{CLOUD} {cloud_providers[provider]}")
        return " | ".join(lines)

    sources = [
        # Re-declared in full because the loader upserts sources. Every field except credibility and
        # the appended notes is as the seed registered it; 'accessed' stays the date it was read.
        dict(id=SRC, title="Top Data Centres in Australia: 2026 Directory and Market Overview",
             publisher="CertifiedStrategic.com",
             url="https://certifiedstrategic.com/insights/top-data-centres-in-australia-2026-directory-and-market-overview",
             doc_type="market_research", published="2026-03-04", accessed="2026-09-18", credibility="C",
             notes="60 Hosting Certification Framework 'Certified Strategic' facilities across 13 providers; "
                   "operator-by-operator site lists; NEXTDC M4 Fishermans Bend 162 MW / A$2bn approval January "
                   "2026; CDC Marsden Park 504 MW; Mandala 1,350 MW (2024) to 3,100 MW (2030); CBRE ~1.4 GW "
                   "(2025) to ~1.8 GW (2028). REGRADED B to C on 2026-10-14: an aggregator's directory article "
                   "that relays other firms' research (the Mandala and CBRE figures above are second-hand), "
                   "which is class C under the rubric, as for the GovMarket aggregator. Not archived when read "
                   "on 2026-09-18. ARCHIVED 2026-10-14 in the version last modified "
                   f"{modified}, at data/raw/operators/certifiedstrategic/ with a SHA-256 manifest; that "
                   "version gives 62 sites, 21 facilities and 41 enclaves across 14 providers, matching the "
                   "register, and does not mention Vantage, AustralianSuper, AirTrunk SYD3 or Stockland. Rows "
                   "resting on it alone are to be re-sourced from primary records (RG-100)."),
        dict(id=MANDALA_SRC, title="Data Centres as Enabling Infrastructure",
             publisher="Mandala, for Data Centres Australia",
             url="https://mandalapartners.com/uploads/Data-Centres-as-Enabling-Infrastructure.pdf",
             doc_type="market_research", published="2025-11", accessed=TODAY, credibility="B",
             notes="November 2025; commissioned for Data Centres Australia by AirTrunk, Amazon Web Services, "
                   "CDC and NEXTDC, and prepared by Mandala. Archived 2026-10-14 at "
                   "data/raw/operators/mandala/ with a SHA-256 manifest; the PDF and its text are not "
                   "committed (a commercial report). CertifiedStrategic.com names it as the source of the "
                   "1,350 MW (2024) and 3,100 MW (2030) deployable capacity figures; its text states neither, "
                   "and it cites Mandala's October 2024 report, Empowering Australia's Digital Future, for the "
                   "earlier analysis. Cited by RG-100 for that finding, not for any figure."),
    ]

    legal_updates = [
        dict(match=dict(id="LAW_HCF"),
             set=dict(summary="Certified Strategic is the framework's highest level: the register calls it "
                              "'the highest level of assurance to Australian Government customers'. "
                              "CertifiedStrategic.com adds that it is required for sensitive and PROTECTED "
                              "workloads, which no primary source here states. The register lists "
                              f"{count['facility']} Certified Strategic facilities and {count['enclave']} "
                              f"enclaves across {len(entries)} providers (archive of {captured}), and states "
                              "that registration of prospective providers and supplementary assessments are "
                              "paused from 3 November 2025 until the framework's reforms are complete. Which "
                              "agency administers the framework is not established from a primary source "
                              "here: the register names only 'the Department', and releases up to v2.2.0 "
                              "named the Digital Transformation Agency on an aggregator's authority, which is "
                              "withdrawn (RG-100).",
                      confidence="medium"),
             add_sources=[dict(id=REGISTER, quote=f"{HIGHEST} | {PAUSE}")]),
    ]

    entity_updates = [
        dict(match=dict(id="ENT_DTA"),
             set=dict(notes="Named by CertifiedStrategic.com (March 2026) as administrator of the Hosting "
                            "Certification Framework (Certified Strategic / Certified Assured). That attribution "
                            "is withdrawn: it rests on a grade C aggregator, and the register itself names only "
                            "'the Department'. Which agency administers the framework today is open (RG-100).",
                      confidence="low"),
             add_sources=[]),
        dict(match=dict(id="ENT_MACQUARIE_TG"),
             set=dict(notes="Six HCF Certified Strategic sites: enclaves IC1, IC2, IC3 and IC3e in Sydney and "
                            "facilities IC4 and IC5 at Fairbairn (ACT), plus a certified Government Cloud Service; "
                            "the only provider the register lists for both data centres and a cloud service. "
                            "CORRECTED 2026-10-14: releases up to v2.2.0 said five sites, omitting IC3e."),
             add_sources=[dict(id=REGISTER, quote=register_quote("Macquarie Technology Group"))]),
        # Neither entity is mentioned by the article they cited. The claims are withdrawn from the
        # notes, not re-sourced: the primary release is not reachable from here (RG-100).
        dict(match=dict(id="ENT_VANTAGE"),
             set=dict(notes="Placeholder: Australian sites not yet mapped in this release. Releases up to v2.2.0 "
                            "also said AustralianSuper holds a significant minority stake in Vantage Data "
                            "Centers' European business (2023), citing CertifiedStrategic.com, whose archived "
                            "article does not mention Vantage. That claim is withdrawn until a primary source "
                            "is read (RG-100)."),
             add_sources=[]),
        dict(match=dict(id="ENT_AUSTRALIANSUPER"),
             set=dict(notes="Placeholder: domestic superannuation exposure to data centres not yet traced. See "
                            "research_gaps RG-004. Releases up to v2.2.0 also claimed exposure via Vantage's "
                            "European business and reported 2024 commitments, citing CertifiedStrategic.com, "
                            "whose archived article mentions neither; withdrawn until a primary source is read "
                            "(RG-100)."),
             add_sources=[]),
    ] + [
        dict(match=dict(id=entity), set={}, add_sources=[dict(id=REGISTER, quote=register_quote(provider))])
        for entity, provider in sorted(REGISTER_PROVIDER.items()) if entity != "ENT_MACQUARIE_TG"
    ]

    security_updates = [
        dict(match=dict(subject_entity_id="ENT_MACQUARIE_TG", regime="hosting_certification_framework"),
             set=dict(status="The only provider the HCF register lists for both certified data centre "
                             "facilities and a certified cloud service (a Government Cloud Service offering)",
                      notes=f"Derived from the register (archive of {captured}) by "
                            "scripts/curate_certstrat_review.py: of the "
                            f"{len(entries)} data centre providers and {len(cloud_providers)} cloud service "
                            "providers it lists, Macquarie Technology Group is the one on both. "
                            "CertifiedStrategic.com calls this 'the only vertically integrated certified "
                            "sovereign stack'.",
                      fact_status="VERIFIED", confidence="high", as_of_date=captured, source_id=REGISTER),
             add_sources=[dict(id=REGISTER, quote=register_quote("Macquarie Technology Group"))]),
    ]

    metrics = [
        dict(match=dict(metric_name="hcf_certified_strategic_facilities_national", source_id=SRC),
             set=dict(scope="Australia", confidence="low",
                      notes="60 Certified Strategic facilities and enclaves nationally across 13 providers, as "
                            "CertifiedStrategic.com stated it in March 2026; its version of "
                            f"{modified} gives 62 across 14. Superseded by hcf_certified_strategic_register, "
                            "counted from the register itself. CORRECTED 2026-10-14: releases up to v2.2.0 "
                            "tagged this national count with scope NSW."),
             add_sources=[]),
        dict(as_of=captured, scope="Australia", metric_name="hcf_certified_strategic_register",
             value=float(count["facility"] + count["enclave"]), unit="count", basis="actual",
             notes=f"{count['facility']} Certified Strategic facilities and {count['enclave']} enclaves across "
                   f"{len(entries)} providers on the HCF register's Certified Service Providers page (Internet "
                   f"Archive capture of {captured}), counted from the archived page by "
                   "scripts/curate_certstrat_review.py with curate_hcf_register.py's parser. A facility the "
                   "register names once counts once. Cloud services are listed separately and not counted.",
             fact_status="VERIFIED", confidence="high", as_of_date=captured, source_id=REGISTER),
    ] + [
        dict(match=dict(metric_name=name, as_of=as_of, source_id=SRC),
             set=dict(confidence="low", notes=note), add_sources=[])
        for name, as_of, note in (
            ("deployable_capacity", "2024",
             "Relayed by CertifiedStrategic.com from Mandala's 'Data Centres as Enabling Infrastructure' "
             "(November 2025), whose text does not state it (RG-100)."),
            ("deployable_capacity", "2030",
             "Relayed by CertifiedStrategic.com from Mandala's 'Data Centres as Enabling Infrastructure' "
             "(November 2025), whose text does not state it; nor the >A$26bn investment (RG-100)."),
            ("live_capacity", "2025",
             "Relayed by CertifiedStrategic.com from CBRE's August 2025 research, which has not been read "
             "here (RG-100)."),
            ("live_capacity", "2028",
             "Relayed by CertifiedStrategic.com from CBRE's August 2025 research, which has not been read "
             "here; demand outpaces supply by 0.7-1.7 GW on the same account (RG-100)."),
        )
    ]

    # M4 was the one row graded high on this source alone. Its IT capacity is not changed here:
    # operator_sources.json reports NEXTDC's own page (150 MW) against it for a human to settle.
    m4_page = "M4 Melbourne is targeting 150MW of IT capacity. Currently In Planning"
    sites = [
        dict(match=dict(id="SITE_NEXTDC_M4"),
             set=dict(confidence="medium",
                      notes="Victorian Government development approval January 2026. Designed for AI, defence "
                            "and sovereign technology workloads; rack densities above 1,000 kW; direct-to-chip "
                            "liquid cooling. The 162 MW IT capacity, A$2bn cost and approval date came from a "
                            "grade C aggregator article. NEXTDC's own M4 page gives 150 MW of IT capacity and "
                            "calls the facility 'Currently In Planning' (operator_sources pack); which capacity "
                            "stands is for a human to settle (RG-100)."),
             add_sources=[]),
        # The article does not mention either site; each already cites a better source, which now
        # becomes its primary one.
        dict(match=dict(id="SITE_AIRTRUNK_SYD3"), set=dict(source_id="SRC_OP_AIRTRUNK_SYD3_SYDNEY_WEST"),
             add_sources=[]),
        dict(match=dict(id="SITE_STOCKLAND_MP"), set=dict(source_id="SRC_NSW_IDA"), add_sources=[]),
    ]

    applications = [
        # A duplicate of the portal register's own row for SSD-70889211, now cited to it. Matched on
        # its month-only decision date because the loader never sets a column it matches on.
        dict(match=dict(site_id="SITE_CDC_MARSDEN", decided="2025-11"),
             set=dict(notes="NSW planning approval November 2025, as the portal register records it "
                            "(SSD-70889211, determined 27 November 2025); the Department's assessment report "
                            "gives 504 MW as the IT load of a 720 MW maximum power capacity. Duplicates the "
                            "register's own application row; first recorded from CertifiedStrategic.com, which "
                            "adds an October 2024 ground-breaking that no primary source here confirms.",
                      fact_status="VERIFIED", confidence="high", source_id="SRC_NSWPORTAL_REGISTER"),
             add_sources=["SRC_NSWPORTAL_REGISTER",
                          dict(id="SRC_SSD70889211_ASSESSMENT",
                               quote="Maximum power capacity • 720 MW (504 MW IT load)")]),
        dict(match=dict(site_id="SITE_NEXTDC_M4", source_id=SRC),
             set=dict(notes="Described by CertifiedStrategic.com as a January 2026 Victorian Government "
                            "development approval for 162 MW and A$2bn; no primary record of the approval has "
                            "been read. NEXTDC's own page gives 150 MW of IT capacity and calls M4 'Currently In "
                            "Planning' (RG-100)."),
             add_sources=[dict(id="SRC_OP_NEXTDC_M4_MELBOURNE", quote=m4_page)]),
    ]

    gaps = [
        dict(id=100, pillar="A", priority=4, retrieval_method="manual_review", status="in_progress",
             opened=TODAY,
             question="Replace CertifiedStrategic.com (SRC_CERTSTRAT) for what still rests on it alone: four "
                      "national capacity figures it relays second-hand (deployable 1,350 MW in 2024 and 3,100 MW "
                      "by 2030, attributed to Mandala; live 1,400 MW in 2025 and 1,800 MW by 2028, attributed to "
                      "CBRE), the locations and descriptions in five provider notes that the register does "
                      "not state, the framework's PROTECTED "
                      "requirement, M4's approval date and cost, and a primary source or removal for "
                      "ENT_VANTAGE and ENT_AUSTRALIANSUPER; and settle NEXTDC M4's IT capacity, 162 MW from "
                      "the article against 150 MW on NEXTDC's own page.",
             why_it_matters="When reviewed, the article was the sole source for 27 of the 93 sites and 25 of "
                            "the 26 Certified Strategic flags. Batches S3 and S4 confirmed every flag against "
                            "the Commonwealth register (RG-096) and cited operators' own pages, so no site "
                            "rests on it alone. What remains is aggregate and descriptive, and two of its "
                            "citations proved not to be in it at all.",
             target_source="Mandala Partners, Empowering Australia's Digital Future (October 2024); CBRE, AI "
                           "Adoption Drives Australia's Data Centre Investment and Demand (August 2025); "
                           "NEXTDC's ASX announcement and the Victorian Government's record of the M4 approval; "
                           "the DigitalBridge/Vantage release on AustralianSuper's 2023 investment",
             notes="ADVANCED 2026-10-14. Archived and read the article itself (version of "
                   f"{modified}): it does not mention Vantage, AustralianSuper, AirTrunk SYD3 or Stockland, so "
                   "the two entities' claims are withdrawn and the two sites now take their better sources as "
                   "primary. Re-sourced to the register: the provider counts in the Equinix, Digital Realty, "
                   "Macquarie (now six sites, adding IC3e), DCI and Telstra notes, the framework's 'highest "
                   "level of assurance' wording, and the Macquarie security record, which is derived from the "
                   "register and now VERIFIED. Marsden Park's application row now cites the portal and its "
                   "assessment report. The Mandala report the article names (Data Centres as Enabling "
                   "Infrastructure, November 2025, archived) does not state 1,350 MW or 3,100 MW; it points to "
                   "Mandala's October 2024 report, which this environment cannot fetch because the host's "
                   "robots.txt refuses it, as does CDC's copy. CBRE answers 403. FROM THE ARCHIVED REGISTER "
                   "(primary, SRC_HCF_REGISTER): it lists data centre facilities that match no site record "
                   "here: " + "; ".join(unmatched) + ". RG-096 matched only existing records, so these are "
                   "candidates for new site rows. LEADS ONLY, from search-engine summaries read on 2026-10-14 "
                   "(below grade D, not relied on, and kept out of every fact row): the framework appears to "
                   "have moved from the Digital Transformation Agency to the Department of Home Affairs on 1 "
                   "May 2023; the 1,350 MW and 3,100 MW figures appear to come from Mandala's October 2024 "
                   "report; and AustralianSuper appears to have announced a EUR 1.5bn minority investment in "
                   "Vantage Data Centers' EMEA platform on 11 September 2023.",
             fact_status="VERIFIED", confidence="high", as_of_date=TODAY, source_id=SRC),
        # The loader registers add_sources only on an update, so the Mandala citation follows the insert.
        dict(match=dict(id=100), set={},
             add_sources=[dict(id=MANDALA_SRC, quote=(
                 "The centrality of data centres to our digital infrastructure and their economic benefits "
                 "across the economy were detailed in a previous report, Empowering Australia’s Digital "
                 "Future, released in October 2024."))]),
    ]

    pack = {
        "pack_id": "certstrat-review-2026-10",
        "prepared_by": "scripts/curate_certstrat_review.py",
        "prepared_on": TODAY,
        "sources": sources,
        "rows": {
            "legal_instruments": legal_updates,
            "entities": entity_updates,
            "security_records": security_updates,
            "metrics": metrics,
            "sites": sites,
            "applications": applications,
            "research_gaps": gaps,
        },
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(pack, fh, indent=1)
    print(f"wrote {OUT}: register {count['facility']} facilities + {count['enclave']} enclaves across "
          f"{len(entries)} providers; {len(unmatched)} register lines match no site; article of {modified}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
