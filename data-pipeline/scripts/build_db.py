#!/usr/bin/env python3
"""
ADCO build script.

  python3 scripts/build_db.py            -> builds exports/australian_data_centre_observatory.db
                                           writes CSV exports and a validation report

Idempotent: deletes and rebuilds the SQLite file from schema + seed each run.
"""
import csv
import json
import os
import sqlite3
import sys
from datetime import date

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from data.seed_data import (  # noqa: E402
    SOURCES, ENTITIES, OWNERSHIP, SITES, APPLICATIONS, LAND_EVENTS, POWER, WATER,
    ENERGY_AGREEMENTS, RENEWABLE_CLAIMS, FLOWS, INCENTIVES, INSTRUMENTS,
    INSTRUMENT_APPLICATION, REG_EVENTS, COMMUNITY_EVENTS, COMMUNITY_GROUPS,
    SECURITY, METRICS, GAPS, ENGINEERING, ACCESSED,
)

DB_PATH = os.path.join(ROOT, "exports", "australian_data_centre_observatory.db")
# All schema files are applied in filename order: 01_schema.sql is the base,
# 02_consultants.sql and any later NN_*.sql are additive migrations.
SCHEMA_DIR = os.path.join(ROOT, "schema")
SCHEMA_FILES = sorted(
    os.path.join(SCHEMA_DIR, f) for f in os.listdir(SCHEMA_DIR)
    if f.endswith(".sql")
) if os.path.isdir(SCHEMA_DIR) else []
SCHEMA = SCHEMA_FILES[0] if SCHEMA_FILES else os.path.join(SCHEMA_DIR, "01_schema.sql")
CSV_DIR = os.path.join(ROOT, "exports", "csv")
REPORT = os.path.join(ROOT, "reports", "build_report.md")

PROVENANCE_COLS = ("fact_status", "confidence", "as_of_date")

# table -> (seed list, primary key column name or None for autoincrement)
TABLES = [
    ("sources", SOURCES, "id"),
    ("entities", ENTITIES, "id"),
    ("ownership", OWNERSHIP, None),
    ("sites", SITES, "id"),
    ("applications", APPLICATIONS, None),
    ("land_events", LAND_EVENTS, None),
    ("power_profile", POWER, None),
    ("water_profile", WATER, None),
    ("energy_agreements", ENERGY_AGREEMENTS, None),
    ("renewable_claims", RENEWABLE_CLAIMS, None),
    ("financial_flows", FLOWS, None),
    ("incentives", INCENTIVES, None),
    ("legal_instruments", INSTRUMENTS, "id"),
    ("instrument_application", INSTRUMENT_APPLICATION, None),
    ("regulatory_events", REG_EVENTS, None),
    ("community_groups", COMMUNITY_GROUPS, "id"),
    ("community_events", COMMUNITY_EVENTS, None),
    ("security_records", SECURITY, None),
    ("metrics", METRICS, None),
    ("engineering_claims", ENGINEERING, None),
]


def columns_of(conn, table):
    return [r[1] for r in conn.execute(f"PRAGMA table_info({table})")]


def build():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    os.makedirs(CSV_DIR, exist_ok=True)
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)

    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    for schema_file in SCHEMA_FILES:
        with open(schema_file, encoding="utf-8") as fh:
            conn.executescript(fh.read())
        print(f"  schema: {os.path.basename(schema_file)}")

    inserted = {}
    problems = []

    for table, rows, pk in TABLES:
        cols = columns_of(conn, table)
        colset = set(cols)
        n = 0
        for row in rows:
            unknown = set(row) - colset
            if unknown:
                problems.append(f"{table}: unknown column(s) {sorted(unknown)} -> row keys {list(row)[:3]}")
                continue
            missing_required = [c for c in cols
                                if c not in row and c not in ("id",) and not c.startswith("_")]
            data = {k: v for k, v in row.items() if k in colset}
            if table == "sources":
                data.setdefault("accessed", ACCESSED)
            if "as_of_date" in colset and not data.get("as_of_date"):
                data["as_of_date"] = ACCESSED
            placeholders = ",".join("?" for _ in data)
            collist = ",".join(data.keys())
            try:
                conn.execute(f"INSERT INTO {table} ({collist}) VALUES ({placeholders})",
                             tuple(data.values()))
                n += 1
            except sqlite3.Error as exc:
                problems.append(f"{table}: {exc} :: {json.dumps({k: str(v)[:80] for k, v in data.items()})[:400]}")
        inserted[table] = n

    # research_gaps has a different shape (tuples)
    for i, (pillar, code, question, why, target, method, priority) in enumerate(GAPS, start=1):
        conn.execute(
            "INSERT INTO research_gaps (id, pillar, question, why_it_matters, target_source, "
            "retrieval_method, priority, status, opened) VALUES (?,?,?,?,?,?,?,?,?)",
            (i, pillar, question, why, target, method, priority, "open", "2026-09-18"))
    inserted["research_gaps"] = len(GAPS)

    # ------------------------------------------------------------------
    # source_refs: normalised provenance for every row that cites a source
    # ------------------------------------------------------------------
    refs = 0
    for table, rows, pk in TABLES:
        if table == "sources":
            continue
        # Re-read rowids in insertion order so the link table is accurate.
        idcol = "id" if "id" in columns_of(conn, table) else None
        if idcol:
            rowids = [r[0] for r in conn.execute(f'SELECT "{idcol}" FROM {table} ORDER BY rowid')]
        else:  # pragma: no cover - every table has an id column in this schema
            rowids = list(range(1, len(rows) + 1))
        for idx, row in enumerate(rows):
            sid = row.get("source_id")
            if not sid or idx >= len(rowids):
                continue
            try:
                conn.execute(
                    "INSERT OR IGNORE INTO source_refs (entity_table, entity_rowid, source_id) "
                    "VALUES (?,?,?)", (table, rowids[idx], sid))
                refs += 1
            except sqlite3.Error as exc:
                problems.append(f"source_refs {table}: {exc}")
    inserted["source_refs"] = refs

    conn.commit()

    # ------------------------------------------------------------------
    # Integrity checks
    # ------------------------------------------------------------------
    fk_violations = list(conn.execute("PRAGMA foreign_key_check"))
    for v in fk_violations:
        problems.append(f"FK violation: {v}")

    conn.execute("ANALYZE")
    conn.commit()

    # ------------------------------------------------------------------
    # CSV exports
    # ------------------------------------------------------------------
    tables = [r[0] for r in conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name")]
    views = [r[0] for r in conn.execute(
        "SELECT name FROM sqlite_master WHERE type='view' ORDER BY name")]

    # NOTE: this export contains SEED ROWS ONLY, because it runs before the curated
    # packs are loaded. scripts/export_csv.py is the authoritative export and runs
    # last in rebuild_all.py, overwriting these files and verifying them against the
    # database. Do not rely on the CSVs written here.
    for t in tables + views:
        cur = conn.execute(f'SELECT * FROM "{t}"')
        cols = [d[0] for d in cur.description]
        rows = cur.fetchall()
        with open(os.path.join(CSV_DIR, f"{t}.csv"), "w", newline="", encoding="utf-8") as fh:
            w = csv.writer(fh)
            w.writerow(cols)
            w.writerows(rows)

    # ------------------------------------------------------------------
    # Build report
    # ------------------------------------------------------------------
    total = sum(v for k, v in inserted.items() if k != "source_refs")
    lines = [
        "# ADCO build report",
        "",
        f"Generated: {date.today().isoformat()} (data as at 2026-09-18)",
        "",
        f"- Database: `exports/australian_data_centre_observatory.db`",
        f"- Tables: {len(tables)}  |  Views: {len(views)}  |  Rows inserted: {total}",
        f"- Source references linked: {refs}",
        f"- Sources catalogued: {inserted['sources']}",
        f"- Integrity problems: {len(problems)}",
        "",
        "## Row counts",
        "",
        "| Table | Rows |",
        "|---|---|",
    ]
    for k, v in inserted.items():
        lines.append(f"| {k} | {v} |")

    lines += ["", "## Verification ledger (fact_status x confidence)", "",
              "| Table | fact_status | confidence | rows |", "|---|---|---|---|"]
    for tbl, fs, cf, n in conn.execute("SELECT * FROM v_verification_ledger ORDER BY tbl, fact_status"):
        lines.append(f"| {tbl} | {fs} | {cf} | {n} |")

    lines += ["", "## Unverified / claimed material that must not be published as fact", ""]
    for tbl, fs, n in conn.execute(
            "SELECT 'sites', fact_status, COUNT(*) FROM sites WHERE fact_status IN ('CLAIMED','GAP') GROUP BY 2 "
            "UNION ALL SELECT 'entities', fact_status, COUNT(*) FROM entities WHERE fact_status IN ('CLAIMED','GAP') GROUP BY 2 "
            "UNION ALL SELECT 'incentives', fact_status, COUNT(*) FROM incentives WHERE fact_status IN ('CLAIMED','GAP') GROUP BY 2 "
            "UNION ALL SELECT 'renewable_claims', fact_status, COUNT(*) FROM renewable_claims GROUP BY 2 "
            "UNION ALL SELECT 'metrics', fact_status, COUNT(*) FROM metrics WHERE confidence='low' GROUP BY 2"):
        lines.append(f"- {tbl}: {fs} = {n}")

    lines += ["", "## Pipeline by state (v_pipeline_by_state)", "",
              "| State | Market | Status | Sites | MW | Capex A$bn |", "|---|---|---|---|---|---|"]
    for r in conn.execute("SELECT * FROM v_pipeline_by_state"):
        lines.append("| " + " | ".join(str(x) for x in r) + " |")

    lines += ["", "## Problems", ""]
    lines += [f"- {p}" for p in problems] if problems else ["None."]

    lines += ["", "## Open research gaps (priority order)", "",
              "| ID | Pillar | Priority | Method | Question |", "|---|---|---|---|---|"]
    for gid, pillar, q, _why, _t, method, prio in [
            (i, g[0], g[2], g[3], g[4], g[5], g[6]) for i, g in enumerate(GAPS, start=1)]:
        lines.append(f"| RG-{gid:03d} | {pillar} | {prio} | {method} | {q[:150]} |")

    with open(REPORT, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")

    # JSON dump of the database for the offline viewer
    dump = {}
    for t in tables + views:
        cur = conn.execute(f'SELECT * FROM "{t}"')
        cols = [d[0] for d in cur.description]
        dump[t] = [dict(zip(cols, r)) for r in cur.fetchall()]
    with open(os.path.join(ROOT, "viewer", "db.json"), "w", encoding="utf-8") as fh:
        json.dump(dump, fh, indent=1, default=str)

    conn.close()

    print(f"built {DB_PATH}")
    print(f"rows: {total}  refs: {refs}  problems: {len(problems)}")
    for p in problems[:20]:
        print("  !", p)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(build())
