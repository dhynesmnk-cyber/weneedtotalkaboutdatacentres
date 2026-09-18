#!/usr/bin/env python3
"""
ADCO query console.

    python3 scripts/query.py --list                     # show preset queries
    python3 scripts/query.py pipeline                   # run one
    python3 scripts/query.py --sql "SELECT ..."          # run arbitrary SQL
    python3 scripts/query.py --csv pipeline              # CSV to stdout
    python3 scripts/query.py dossier SITE_MAMRE_ROAD     # full evidence dossier for a site
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import sqlite3
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(ROOT, "exports", "australian_data_centre_observatory.db")

PRESETS: dict[str, str] = {
 "pipeline": """
   SELECT s.state, s.status, COUNT(*) AS n,
          ROUND(SUM(COALESCE(s.max_capacity_mw,s.total_capacity_mw,s.it_capacity_mw,0)),0) AS mw,
          ROUND(SUM(COALESCE(s.capital_cost_aud,0))/1e9,2) AS capex_aud_bn
     FROM sites s GROUP BY s.state, s.status ORDER BY s.state, mw DESC""",

 "biggest": """
   SELECT s.id, s.name, s.state, s.status,
          COALESCE(s.max_capacity_mw,s.total_capacity_mw,s.it_capacity_mw) AS mw,
          s.capital_cost_aud, s.fact_status, s.confidence
     FROM sites s ORDER BY mw DESC NULLS LAST LIMIT 20""",

 "diesel": """
   SELECT s.name, s.state, s.status, p.genset_count, p.genset_total_mw, p.diesel_storage_kl,
          p.onsite_gas_mw, p.emission_standard, s.fact_status
     FROM sites s JOIN power_profile p ON p.site_id=s.id
    WHERE COALESCE(p.genset_count,0)>0 OR COALESCE(p.onsite_gas_mw,0)>0
       OR COALESCE(p.genset_total_mw,0)>0 OR COALESCE(p.diesel_storage_kl,0)>0
    ORDER BY COALESCE(p.diesel_storage_kl,0) DESC""",

 "water": """
   SELECT s.name, s.state, w.cooling_technology, w.water_source, w.annual_water_kl, w.wue_design,
          w.supply_agreement_status, s.fact_status, w.notes
     FROM sites s JOIN water_profile w ON w.site_id=s.id""",

 "control": """
   SELECT e.name AS operator, h.name AS controller, h.domicile, o.stake_pct, o.instrument,
          o.effective_from, o.firb_reviewed, o.fact_status
     FROM entities e JOIN ownership o ON o.target_id=e.id JOIN entities h ON h.id=o.holder_id
    WHERE o.effective_to IS NULL ORDER BY e.name, o.stake_pct DESC""",

 "money": """
   SELECT f.flow_date, f.flow_type, f.from_entity_id AS from_, f.to_entity_id AS to_,
          f.amount_aud, f.foreign_control, f.fact_status, f.notes
     FROM financial_flows f ORDER BY f.flow_date DESC""",

 "incentives": """SELECT * FROM v_incentive_register""",

 "law": """
   SELECT id, name, jurisdiction, instrument_type, status,
          CASE binding WHEN 1 THEN 'binding' ELSE 'non-binding' END AS force, made
     FROM legal_instruments ORDER BY jurisdiction, made DESC""",

 "loopholes": """
   SELECT i.name AS instrument, a.site_id, a.entity_id, a.compliance_status, a.obligation, a.evidence
     FROM instrument_application a JOIN legal_instruments i ON i.id=a.instrument_id
    WHERE a.compliance_status IN ('non_compliant','partially_compliant','exemption_granted',
                                        'exemption_sought','unknown','not_assessed')""",

 "friction": """
   SELECT event_date, state, locality, event_type, actor, severity, summary
     FROM community_events ORDER BY severity DESC, event_date DESC""",

 "claims": """SELECT * FROM v_renewable_audit""",

 "gaps": """
   SELECT printf('RG-%03d',id) AS gap, pillar, priority, retrieval_method, status, question
     FROM research_gaps ORDER BY priority DESC, pillar, id""",

 "metrics": """
   SELECT as_of, scope, metric_name, value, unit, basis, confidence, fact_status
     FROM metrics ORDER BY scope, metric_name""",

 "unverified": """
   SELECT 'sites' t, id, name, fact_status, confidence FROM sites WHERE fact_status IN ('CLAIMED','GAP')
   UNION ALL SELECT 'entities', id, name, fact_status, confidence FROM entities WHERE fact_status IN ('CLAIMED','GAP')
   UNION ALL SELECT 'metrics', CAST(id AS TEXT), metric_name, fact_status, confidence
             FROM metrics WHERE fact_status IN ('CLAIMED','GAP') OR confidence='low'
   UNION ALL SELECT 'incentives', CAST(id AS TEXT), incentive_type, fact_status, confidence
             FROM incentives WHERE fact_status IN ('CLAIMED','GAP')""",

 "dossier_all": """SELECT * FROM v_site_dossier ORDER BY headline_mw DESC NULLS LAST""",

 "drift": """
   SELECT parent_case, site, lga, mod_case, change_type, decision, determination_date,
          materiality, what_changed
     FROM v_consent_drift
    WHERE materiality >= 4 OR determination_date >= '2026-08-01'
    ORDER BY determination_date DESC""",

 "mods": """
   SELECT m.change_type, COUNT(*) n,
          SUM(CASE WHEN m.decision LIKE 'Approv%' THEN 1 ELSE 0 END) approved,
          SUM(CASE WHEN m.materiality>=4 THEN 1 ELSE 0 END) material
     FROM modifications m GROUP BY m.change_type ORDER BY material DESC, n DESC""",

 # ---- consultancy / advisory layer (schema migration 02) ----
 "consultants": """
   SELECT e.name AS firm, cp.firm_type, cp.role_in_pipeline, cp.peak_body_member,
          cp.also_an_operator AS is_operator, cp.operator_vehicle,
          cp.au_public_sector_exposure_aud AS exposure_aud, cp.exposure_source_tier,
          cp.fact_status, cp.confidence
     FROM consultancy_profile cp JOIN entities e ON e.id = cp.entity_id
    ORDER BY cp.au_public_sector_exposure_aud DESC NULLS LAST""",

 "contracts": """
   SELECT g.agency, g.contract_title, g.value_aud, g.portal, g.portal_id,
          g.method_of_tendering, g.contract_start, g.contract_end,
          CASE WHEN g.is_duplicate_of IS NULL THEN '' ELSE 'DUPLICATE of #' || g.is_duplicate_of END AS dup,
          g.fact_status
     FROM gov_contracts g ORDER BY g.value_aud DESC""",

 "spend": """
   SELECT firm, agency, records, distinct_contracts,
          distinct_value_aud, gross_value_aud, double_counted_aud
     FROM v_consultant_spend_totals""",

 "reconcile": """
   SELECT firm, enumerated_records, enumerated_distinct,
          enumerated_gross_aud, enumerated_distinct_aud,
          published_portfolio_aud, deduplicated_portfolio_aud, deduplicated_contract_count
     FROM v_contract_reconciliation""",

 "duplicates": """
   SELECT g.id, g.agency, g.contract_title, g.value_aud, g.portal, g.portal_id,
          g.is_duplicate_of, g.duplicate_note
     FROM gov_contracts g WHERE g.is_duplicate_of IS NOT NULL""",

 "applicants": """
   SELECT project_slug, case_id, named_applicant, firm_type,
          true_proponent, proponent_known, fact_status
     FROM v_applicant_vs_proponent ORDER BY proponent_known, project_slug""",

 "officers": """
   SELECT officer_name, officer_role, cases, earliest_decision, latest_decision, delegations_used
     FROM v_case_officer_load""",

 "influence2": """
   SELECT firm, peak_body_member, on_peak_body_board, also_an_operator, operator_vehicle,
          au_public_sector_exposure_aud, exposure_source_tier, channel, recipient,
          event_date, instrument, lobbying_fact_status
     FROM v_consultant_influence""",
}


def dossier(conn: sqlite3.Connection, site_id: str) -> None:
    def dump(title: str, sql: str, params: tuple = ()) -> None:
        cur = conn.execute(sql, params)
        cols = [d[0] for d in cur.description]
        rows = cur.fetchall()
        print(f"\n=== {title} ({len(rows)}) ===")
        if not rows:
            print("  (none)")
            return
        for r in rows:
            print("  " + "-" * 70)
            for c, v in zip(cols, r):
                if v not in (None, ""):
                    print(f"  {c:24s} {v}")

    dump("SITE", "SELECT * FROM sites WHERE id=?", (site_id,))
    dump("APPLICATIONS", "SELECT * FROM applications WHERE site_id=?", (site_id,))
    dump("POWER PROFILE", "SELECT * FROM power_profile WHERE site_id=?", (site_id,))
    dump("WATER PROFILE", "SELECT * FROM water_profile WHERE site_id=?", (site_id,))
    dump("LAND EVENTS", "SELECT * FROM land_events WHERE site_id=?", (site_id,))
    dump("INSTRUMENTS APPLIED", """SELECT i.name, a.applies_from, a.obligation, a.compliance_status, a.evidence
                                   FROM instrument_application a JOIN legal_instruments i ON i.id=a.instrument_id
                                   WHERE a.site_id=?""", (site_id,))
    dump("REGULATORY EVENTS", "SELECT * FROM regulatory_events WHERE site_id=?", (site_id,))
    dump("COMMUNITY EVENTS", "SELECT * FROM community_events WHERE site_id=?", (site_id,))
    dump("RENEWABLE CLAIMS", "SELECT * FROM renewable_claims WHERE site_id=?", (site_id,))
    dump("FINANCIAL FLOWS", "SELECT * FROM financial_flows WHERE site_id=?", (site_id,))
    dump("SECURITY", "SELECT * FROM security_records WHERE site_id=?", (site_id,))
    dump("SOURCES CITED", """SELECT DISTINCT s.id, s.title, s.publisher, s.url, s.doc_type, s.credibility
                             FROM sources s JOIN source_refs r ON r.source_id=s.id
                             WHERE r.entity_table='sites' AND r.entity_rowid=?""", (site_id,))


def tabulate(cols: list[str], rows: list[tuple]) -> str:
    rows = [[("" if v is None else (json.dumps(v) if isinstance(v, (dict, list)) else str(v))) for v in r] for r in rows]
    widths = [len(c) for c in cols]
    for r in rows:
        for i, v in enumerate(r):
            widths[i] = max(widths[i], min(len(v), 60))
    def line(vals):
        return "  ".join(v[:60].ljust(widths[i]) for i, v in enumerate(vals))
    out = [line(cols), "  ".join("-" * w for w in widths)]
    out += [line(r) for r in rows]
    return "\n".join(out)


def main(argv: list[str]) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("preset", nargs="?", help="name of a preset query")
    p.add_argument("preset_arg", nargs="?", help="argument for the preset (e.g. SITE_x for `dossier`)")
    p.add_argument("--sql", help="arbitrary SELECT statement")
    p.add_argument("--csv", action="store_true", help="emit CSV instead of an aligned table")
    p.add_argument("--dossier", metavar="SITE_ID", help="print the full evidence dossier for a site")
    p.add_argument("--list", action="store_true", help="list presets")
    p.add_argument("--db", default=DB_PATH)
    a = p.parse_args(argv)

    if a.list:
        for k, v in PRESETS.items():
            first = " ".join(v.split())[:100]
            print(f"  {k:14s} {first}")
        return 0

    if not os.path.exists(a.db):
        print(f"no database at {a.db}; run scripts/build_db.py", file=sys.stderr)
        return 2

    conn = sqlite3.connect(a.db)
    conn.execute("PRAGMA foreign_keys=ON")

    target = a.dossier or (a.preset_arg if a.preset == "dossier" else None)
    if target:
        if not conn.execute("SELECT 1 FROM sites WHERE id=?", (target,)).fetchone():
            ids = [r[0] for r in conn.execute("SELECT id FROM sites ORDER BY id")]
            print(f"no site with id {target!r}. valid ids:\n  " + "\n  ".join(ids), file=sys.stderr)
            return 2
        dossier(conn, target)
        return 0

    sql = a.sql or (PRESETS.get(a.preset or "") if a.preset else None)
    if a.preset == "dossier" and not sql:
        print("usage: query.py dossier SITE_x", file=sys.stderr)
        return 2
    if not sql:
        print("nothing to run. try --list", file=sys.stderr)
        return 2

    cur = conn.execute(sql)
    cols = [d[0] for d in cur.description]
    rows = cur.fetchall()
    if a.csv:
        w = csv.writer(sys.stdout)
        w.writerow(cols)
        w.writerows(rows)
    else:
        print(tabulate(cols, rows))
        print(f"\n{len(rows)} row(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
