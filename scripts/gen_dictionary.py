#!/usr/bin/env python3
"""Generate reports/DATA_DICTIONARY.md from the live database schema + curated descriptions."""
from __future__ import annotations

import os
import sqlite3
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB = os.path.join(ROOT, "exports", "australian_data_centre_observatory.db")
OUT = os.path.join(ROOT, "reports", "DATA_DICTIONARY.md")

DESC = {
 "sources": "Provenance root. Every factual row points here. Graded A–D by document class, not reputation.",
 "source_refs": "Normalised many-to-many link from any table row to a source, with an optional verbatim quote. "
                "`entity_table` + `entity_rowid` identify the row; for text-PK tables `entity_rowid` holds the "
                "text id (e.g. `SITE_MAMRE_ROAD`), otherwise the integer rowid.",
 "entities": "Companies, funds, agencies, councils, community groups and utilities. `domicile` is the country of "
             "ultimate control, which is the field that matters for sovereignty analysis — it is not the same as "
             "where the entity trades.",
 "entity_aliases": "Trading names, SPVs and former names, so that scraped records can be resolved to a canonical entity.",
 "ownership": "The control chain. One row per holder per period; `effective_to IS NULL` means current. Carries the "
              "FIRB flag and outcome. This is Pillar B's core table.",
 "sites": "Physical facilities and proposals. Three capacity fields are stored separately and must never be summed: "
          "`it_capacity_mw` (critical load), `total_capacity_mw` (with cooling overhead), `max_capacity_mw` (full "
          "campus build-out). `market` records NEM / WEM / NT because the regulatory regime differs.",
 "applications": "Planning and approval pathways, including the outcome and the conditions imposed. Distinguishes "
                 "state-significant, local council, fast-track and non-planning approvals (grid, water, licence).",
 "land_events": "Land acquisition, option, rezoning and leasehold events. Where the domestic retirement capital "
                "shows up in this sector.",
 "power_profile": "Engineering and grid reality per site: connection type and point, NCA status, who funds "
                  "augmentation, PUE, demand flexibility, storage, synchronous condenser flag, on-site gas, "
                  "generator count and fuel, diesel inventory, emission standard, EPA licence, Safeguard exposure.",
 "water_profile": "Cooling technology, water source, supply agreement status, annual volume, WUE, potable "
                  "dependency and drought response. The S7 row is the canonical case study in infrastructure "
                  "sequencing failure.",
 "energy_agreements": "PPAs, vPPAs, green tariffs, firming, gas, network and water agreements. `additionality` is "
                      "the load-bearing field: a PPA against an existing asset is not new generation.",
 "renewable_claims": "The audit table. A claim is `VERIFIED` only when contracted instruments satisfy an "
                     "additionality test AND reconcile to Clean Energy Regulator certificate surrender and NGERS "
                     "emissions data. Nothing meets that bar yet — RG-009 is the blocker.",
 "financial_flows": "Money moving: equity, acquisitions, debt, capital raises, land purchases and capex "
                    "commitments, with a `foreign_control` flag.",
 "incentives": "The subsidy register. Covers cash concessions AND in-kind support (fast-tracking, approvals "
               "authorities, co-funded infrastructure), because in Australia the latter is what actually exists. "
               "`conditionality_score` is 0–5; `domestic_compute_allocation` records whether sovereign compute is "
               "reserved.",
 "legal_instruments": "Acts, regulations, rules, determinations, bills, policies, guidelines, strategies, codes and "
                      "inquiries. `binding` is the field that separates the Commonwealth Expectations (0) from the "
                      "Clean Air Regulation (1).",
 "instrument_application": "How an instrument actually bites on a named site or entity, and whether they comply. "
                           "This is where an exemption or an adverse finding is recorded.",
 "regulatory_events": "Dated regulator actions: additional information requests, adverse findings, licence "
                      "conditions, hearings, rule change requests, determinations, fast-track grants.",
 "community_groups": "Register of campaign organisations. Only five are recorded; RG-016 expands it.",
 "community_events": "Dated friction: objections, protests, petitions, council deferrals and rejections, "
                     "litigation, political interventions, school and institution objections, benefit agreements. "
                     "`severity` 1–5, where 5 is a formal council objection.",
 "security_records": "FIRB, SOCI Act, Critical Infrastructure Register, CIRMP, Hosting Certification Framework and "
                     "related regimes, with the ultimate controller and any conditions.",
 "metrics": "Time series of system-level figures. `basis` is mandatory discipline: actual / pipeline / signed / "
            "enquiry / forecast. Enquiry and signed figures are never summed.",
 "research_gaps": "The ingestion backlog and the list of things we do not know. Each row names the target source "
                  "and the retrieval method. This is the project's work queue.",
 "engineering_claims": "Pillar E. Each proposition from the brief is tested against Australian evidence, given a "
                       "verdict, and — where it fails — replaced with a specification anchored to an existing "
                       "policy instrument, plus the residual gap that policy still leaves.",
 "ingest_log": "Audit trail of every curated pack load: what was inserted, updated and rejected.",
}

VIEW_DESC = {
 "v_pipeline_by_state": "Sites, capacity and capex by state / market / status.",
 "v_site_full": "One row per site with operator, owner, tenant, power profile and water profile joined.",
 "v_site_dossier": "Publication-ready site summary with primary source and counts of applications, community "
                   "events, regulatory events and applicable instruments.",
 "v_foreign_control": "Operators and their current holders, with domicile and FIRB flag.",
 "v_incentive_register": "Every recorded incentive, subsidy or fast-track benefit with its conditions.",
 "v_renewable_audit": "Claims joined to claimant and site, ordered by verification status.",
 "v_community_friction": "Community events joined to site and group, newest first.",
 "v_verification_ledger": "Row counts by table / fact_status / confidence. The health check.",
}

VOCABS = {
 "fact_status": ["VERIFIED", "REPORTED", "CLAIMED", "GAP"],
 "confidence": ["high", "medium", "low"],
 "sites.status": ["operational", "under_construction", "approved", "lodged", "pre_lodgement",
                  "refused", "withdrawn", "cancelled", "rumoured"],
 "sites.market": ["NEM", "WEM", "NT", "Multi"],
 "power_profile.connection_type": ["transmission", "distribution", "behind_the_meter_gas",
                                   "behind_the_meter_diesel", "islanded", "hybrid", "tbd"],
 "water_profile.cooling_technology": ["air_cooled", "closed_loop_water", "adiabatic", "evaporative",
                                      "direct_to_chip_liquid", "immersion", "hybrid", "tbd"],
 "water_profile.water_source": ["potable_mains", "recycled_water", "closed_loop_no_makeup",
                                "bore_groundwater", "rainwater", "sea_water", "mixed", "tbd"],
 "renewable_claims.verification_status": ["VERIFIED", "PARTIALLY_VERIFIED", "UNVERIFIED",
                                          "CONTRADICTED", "NOT_ASSESSED"],
 "energy_agreements.additionality": ["new_build_pre_fid", "new_build_post_fid", "expansion_existing",
                                     "existing_asset", "unknown"],
 "incentives.incentive_type": ["payroll_tax_exemption", "land_tax_exemption", "stamp_duty_relief",
                               "leasehold_land_concession", "grant", "tax_increment",
                               "rate_concession", "fast_track_approval", "co_funded_infrastructure",
                               "equity_stake", "guarantee", "offtake_commitment", "other",
                               "alleged", "none_found"],
 "metrics.basis": ["actual", "forecast_low", "forecast_central", "forecast_high", "pipeline",
                   "signed", "enquiry", "estimate"],
 "engineering_claims.claim_status": ["SOUND", "PARTLY_SOUND", "UNSOUND_AS_STATED",
                                     "ALREADY_MANDATED", "FACTUALLY_WRONG_PREMISE"],
 "sources.credibility": ["A", "B", "C", "D"],
}


def main() -> int:
    if not os.path.exists(DB):
        print("run scripts/build_db.py first", file=sys.stderr)
        return 2
    conn = sqlite3.connect(DB)
    tables = [r[0] for r in conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name")]
    views = [r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='view' ORDER BY name")]
    ddl = {r[0]: r[1] for r in conn.execute(
        "SELECT name, sql FROM sqlite_master WHERE sql IS NOT NULL")}

    out = ["# ADCO data dictionary", "",
           "Schema v1.0.0 · generated from the live database by `scripts/gen_dictionary.py`.",
           "",
           f"{len(tables)} tables, {len(views)} views. Conventions: power in **MW**, water in **kL/yr**, money in",
           "**AUD (REAL)**, dates **ISO-8601** (`YYYY-MM-DD`, or `YYYY-MM` where the day is unknown).",
           "",
           "Every factual table carries the four provenance columns `fact_status`, `confidence`, `as_of_date`",
           "and `source_id` (FK → `sources`). `source_refs` provides the normalised link plus an optional",
           "verbatim quote.",
           "",
           "---", ""]

    for t in tables + views:
        n = conn.execute(f'SELECT COUNT(*) FROM "{t}"').fetchone()[0]
        kind = "view" if t in views else "table"
        out.append(f"## `{t}` ({kind}, {n} rows)")
        out.append("")
        out.append((VIEW_DESC if kind == "view" else DESC).get(t, "_No description recorded._"))
        out.append("")
        if kind == "view":
            sql = ddl.get(t, "")
            out.append("<details><summary>definition</summary>\n\n```sql\n" + sql.strip() + "\n```\n\n</details>\n")
            continue
        out.append("| Column | Type | Constraints |")
        out.append("|---|---|---|")
        for row in conn.execute(f"PRAGMA table_info({t})"):
            cid, name, ctype, notnull, dflt, pk = row
            cons = []
            if pk:
                cons.append("**PK**")
            if notnull:
                cons.append("NOT NULL")
            if dflt is not None:
                cons.append(f"default `{dflt}`")
            fks = conn.execute(f"PRAGMA foreign_key_list({t})")
            for fk in fks:
                if fk[3] == name:
                    cons.append(f"→ `{fk[2]}.{fk[4]}`")
            out.append(f"| `{name}` | {ctype or 'TEXT'} | {' '.join(cons)} |")
        out.append("")

    out += ["---", "", "## Controlled vocabularies", ""]
    for k, v in VOCABS.items():
        out.append(f"- **{k}**: " + " · ".join(f"`{x}`" for x in v))
    out += ["", "---", "",
            "## Provenance semantics", "",
            "| `fact_status` | Meaning | Publishable as fact? |", "|---|---|---|",
            "| `VERIFIED` | Primary document read directly | Yes |",
            "| `REPORTED` | Credible secondary reporting of a primary fact | Yes, with attribution |",
            "| `CLAIMED` | Proponent or industry assertion, unconfirmed | No — attribute as a claim |",
            "| `GAP` | Known unknown, tracked in `research_gaps` | No |", "",
            "| Source credibility | Definition |", "|---|---|",
            "| A | Primary government, regulator, legislation, planning portal, first-party company document, "
            "major broadcaster or wire |",
            "| B | Established trade press, law firm analysis, think tank, market research |",
            "| C | Single-source, social, community or aggregator |",
            "| D | Unusable — never admitted |", ""]

    with open(OUT, "w", encoding="utf-8") as fh:
        fh.write("\n".join(out) + "\n")
    print(f"wrote {OUT} ({len(out)} lines)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
