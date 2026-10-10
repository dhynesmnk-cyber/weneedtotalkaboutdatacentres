#!/usr/bin/env python3
"""
ADCO curated-pack loader.

Scrapers and dataset downloads never write to the database directly. A human reviews the raw
material, curates it into a JSON pack, and this script loads it with validation and an audit
trail. That separation is what keeps the difference between VERIFIED, REPORTED, CLAIMED and GAP
meaningful.

Pack format:

{
  "pack_id": "nsw-portal-mamre-2026-09",
  "prepared_by": "name or handle",
  "prepared_on": "2026-09-18",
  "sources": [ { "id": "SRC_...", "title": "...", "publisher": "...", "url": "...",
                 "doc_type": "primary_planning_portal", "published": "2026-08-25",
                 "credibility": "A", "accessed": "2026-09-18", "notes": "..." } ],
  "rows": {
     "sites":            [ { "id": "SITE_MAMRE_ROAD", "status": "approved", ... } ],
     "applications":     [ { "site_id": "SITE_MAMRE_ROAD", ... } ],
     "power_profile":    [ ... ],
     "metrics":          [ ... ]
  }
}

Rules enforced here:
  * Every row must name a source_id that exists (in the pack or already in the database).
  * Every row must carry fact_status, confidence and as_of_date.
  * Rows keyed by a text primary key are upserted; rows in autoincrement tables are appended
    unless an "id" is supplied, in which case they are upserted.
  * "add_sources" lists extra sources for a row, each a source id or {"id": ..., "quote": ...}:
    the quote is the verbatim extract the source gives for the row, kept in source_refs.quote.
    A quote never replaces one already recorded.
  * {"match": {...}, "set": {...}} updates matched rows. {"match": {...}, "fill": {...}} writes
    only columns that are empty, and never overwrites: where a matched row already holds a
    different value, that value is kept, a warning printed, and the disagreement recorded in
    the pack's ingest_log entry for a human to settle. Gap-filling packs use "fill", because
    at curation time the packs that load earlier have not run and the curator cannot see them.
  * Unknown columns are rejected rather than silently dropped.
  * Every action is written to ingest_log.

Usage:
    python3 scripts/load_pack.py data/packs/example_pack.json
    python3 scripts/load_pack.py data/packs/example_pack.json --dry-run
"""
from __future__ import annotations

import argparse
import json
import os
import sqlite3
import sys
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(ROOT, "exports", "australian_data_centre_observatory.db")

# Columns that must be present on a row before it can be loaded.
PROVENANCE = ("fact_status", "confidence", "as_of_date")
# Pure mapping tables carry no provenance columns and therefore cannot satisfy the
# provenance requirement. An alias is an attribute of an entity row, which IS
# provenance-tracked, so exempting the mapping loses nothing. Keep this list short
# and justify every entry.
PROVENANCE_EXEMPT = {"entity_aliases"}
# engineering_claims is designed to cite MULTIPLE sources, so the base schema gives it
# source_ids (comma-separated) instead of source_id. Honour that rather than forcing a
# single-source shape onto a multi-source row.
SOURCE_COL_OVERRIDE = {"engineering_claims": "source_ids"}
ALLOW_MISSING_SOURCE = False
FORCE_APPEND = False
REQUIRED_BASE = ("source_id",)
REQUIRED_BY_TABLE = {
    "sources": ("title", "publisher", "url", "doc_type", "accessed"),
    "research_gaps": ("pillar", "question", "priority", "status", "opened"),
    "legal_instruments": ("name", "jurisdiction", "instrument_type", "status"),
    "metrics": ("as_of", "scope", "metric_name", "value", "unit"),
    "engineering_claims": ("claim_label", "claim_status", "premise_check", "australia_reality"),
    "community_events": ("event_type", "summary"),
    "modifications": ("mod_case", "title"),
    "lobbying": ("actor_id", "channel", "position"),
    "regulatory_events": ("event_date", "event_type", "summary"),
    "consultancy_profile": ("entity_id",),
    "gov_contracts": ("supplier_name", "agency", "contract_title", "portal"),
    "consultant_role": ("project_slug", "entity_id", "role"),
    "case_handling": ("case_id", "project_slug", "officer_role"),
}
TEXT_PK_TABLES = {"sources", "entities", "sites", "legal_instruments", "community_groups"}
# Tables with a one-row-per-parent UNIQUE constraint: upsert on that column, not on id.
UNIQUE_KEY_TABLES = {"power_profile": "site_id", "water_profile": "site_id",
                     # migration 02: consultancy_profile is keyed on the entity it describes
                     "consultancy_profile": "entity_id"}
# Tables whose uniqueness is COMPOSITE. These are upserted on their composite key by
# composite_unique_targets() below, so packs that write to them are re-runnable. Listed
# here for documentation and so a future schema change is noticed.
COMPOSITE_UNIQUE_TABLES = {"gov_contracts", "consultant_role", "case_handling"}


def unique_targets(conn, table: str) -> list[tuple[str, ...]]:
    """Discover single-column UNIQUE constraints (including UNIQUE PRIMARY KEY) at runtime."""
    out = []
    for row in conn.execute(f"PRAGMA index_list({table})"):
        if not row[2]:  # not unique
            continue
        cols = [c[2] for c in conn.execute(f'PRAGMA index_info("{row[1]}")')]
        if len(cols) == 1:
            out.append((cols[0],))
    return out
ALLOWED_TABLES = {
    "sources", "entities", "entity_aliases", "ownership", "sites", "applications", "land_events",
    "power_profile", "water_profile", "energy_agreements", "renewable_claims", "financial_flows",
    "incentives", "legal_instruments", "instrument_application", "regulatory_events",
    "community_groups", "community_events", "security_records", "metrics", "research_gaps",
    "engineering_claims", "modifications", "lobbying",
    # migration 02: consultancy / advisory layer
    "consultancy_profile", "gov_contracts", "consultant_role", "case_handling",
}


def source_ref(entry) -> tuple[str | None, str | None]:
    """(source id, quote) from an add_sources entry: an id, or {"id": ..., "quote": ...}."""
    if isinstance(entry, dict):
        return entry.get("id"), entry.get("quote")
    return entry, None


def add_source_ref(conn, table: str, rowid, entry, known_sources, errors) -> None:
    sid, quote = source_ref(entry)
    if sid not in known_sources:
        errors.append(f"{table}: add_sources references unknown source {sid}")
        return
    conn.execute("INSERT INTO source_refs (entity_table, entity_rowid, source_id, quote) VALUES (?,?,?,?) "
                 "ON CONFLICT (entity_table, entity_rowid, source_id) "
                 "DO UPDATE SET quote = COALESCE(source_refs.quote, excluded.quote)",
                 (table, str(rowid), sid, quote))


def apply_update(conn, table, row, known_sources, dry_run, errors, kept) -> int:
    """Targeted update of existing rows:
    {"match": {...}, "set": {...}, "fill": {...}, "add_sources": [...]}

    "set" overwrites. "fill" writes a column only where it is empty, and appends to `kept` every
    matched row whose existing value it declined to replace.
    """
    match, upd, fill = row["match"], row.get("set") or {}, row.get("fill") or {}
    cols = columns(conn, table)
    for bad in [k for k in list(match) + list(upd) + list(fill) if k not in cols]:
        errors.append(f"{table}: update references unknown column {bad!r}")
        return 0
    for both in sorted(set(upd) & set(fill)):
        errors.append(f"{table}: {both!r} is in both set and fill for {match}")
        return 0
    where = " AND ".join(f'"{k}"=?' for k in match)
    sel = conn.execute(f"SELECT COUNT(*) FROM {table} WHERE {where}", tuple(match.values())).fetchone()[0]
    if sel == 0:
        errors.append(f"{table}: update matched no rows for {match}")
        return 0
    setcols = [k for k in upd if k not in match]
    if setcols and not dry_run:
        conn.execute(f'UPDATE {table} SET {", ".join(f"{c}=?" for c in setcols)} WHERE {where}',
                     tuple(upd[c] for c in setcols) + tuple(match.values()))
    for col, value in fill.items():
        if col in match:
            continue
        for (existing,) in conn.execute(f'SELECT "{col}" FROM {table} WHERE {where}',
                                        tuple(match.values())):
            if existing not in (None, "") and existing != value:
                kept.append(dict(table=table, match=match, column=col, kept=existing, offered=value))
        if not dry_run:
            conn.execute(f'UPDATE {table} SET "{col}"=? WHERE {where} AND ("{col}" IS NULL OR "{col}"=\'\')',
                         (value, *match.values()))
    for entry in row.get("add_sources", []):
        if source_ref(entry)[0] not in known_sources:
            errors.append(f"{table}: add_sources references unknown source {source_ref(entry)[0]}")
            continue
        if not dry_run:
            ids = [r[0] for r in conn.execute(f'SELECT "id" FROM {table} WHERE {where}', tuple(match.values()))]
            for rid in ids:
                add_source_ref(conn, table, rid, entry, known_sources, errors)
    return sel


# Tables with an autoincrement integer PK and NO unique constraint other than that PK
# are append-only: loading the same pack twice silently doubles their rows. The full
# rebuild (scripts/rebuild_all.py) deletes the database first, so it is always safe;
# re-running a single pack against a live database is not. APPEND_ONLY_TABLES is
# discovered at runtime rather than hardcoded so new tables are caught automatically.
def is_append_only(conn, table: str) -> bool:
    cols = [r[1] for r in conn.execute(f"PRAGMA table_info({table})")]
    if "id" not in cols:
        return False
    if unique_targets(conn, table) or composite_unique_targets(conn, table):
        return False
    if table in TEXT_PK_TABLES or table in UNIQUE_KEY_TABLES:
        return False
    return True


def composite_unique_targets(conn, table: str) -> list[tuple[str, ...]]:
    """Discover multi-column UNIQUE constraints at runtime, so that tables whose
    uniqueness is composite (gov_contracts, consultant_role, case_handling) can be
    upserted idempotently instead of being append-only."""
    out = []
    for row in conn.execute(f"PRAGMA index_list({table})"):
        if not row[2]:  # not unique
            continue
        cols = tuple(c[2] for c in conn.execute(f'PRAGMA index_info("{row[1]}")'))
        if len(cols) > 1:
            out.append(cols)
    return out


def columns(conn: sqlite3.Connection, table: str) -> list[str]:
    return [r[1] for r in conn.execute(f"PRAGMA table_info({table})")]


def load(pack_path: str, dry_run: bool = False, allow_missing_source: bool = False,
         force_append: bool = False) -> int:
    global ALLOW_MISSING_SOURCE, FORCE_APPEND
    ALLOW_MISSING_SOURCE = allow_missing_source
    FORCE_APPEND = force_append
    with open(pack_path, encoding="utf-8") as fh:
        pack = json.load(fh)

    if not os.path.exists(DB_PATH):
        print(f"database not found at {DB_PATH}; run scripts/build_db.py first", file=sys.stderr)
        return 2

    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    run_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    pack_id = pack.get("pack_id") or os.path.basename(pack_path)
    errors: list[str] = []
    warnings: list[str] = []
    counts: dict[str, int] = {}
    kept: list[dict] = []

    # --- sources first, so row-level source_id references resolve -----------------
    known_sources = {r[0] for r in conn.execute("SELECT id FROM sources")}
    for s in pack.get("sources", []):
        sid = s.get("id")
        if not sid:
            errors.append(f"source without id: {s}")
            continue
        s.setdefault("accessed", pack.get("prepared_on", run_at[:10]))
        cols = columns(conn, "sources")
        data = {k: v for k, v in s.items() if k in cols}
        bad = set(s) - set(cols)
        if bad:
            errors.append(f"sources/{sid}: unknown columns {sorted(bad)}")
            continue
        missing = [c for c in ("title", "publisher", "url", "doc_type", "accessed")
                   if data.get(c) in (None, "")]
        if missing:
            errors.append(f"sources/{sid}: missing required fields {missing}")
            continue
        known_sources.add(sid)   # register before the dry-run short-circuit
        if dry_run:
            counts["sources"] = counts.get("sources", 0) + 1
            continue
        conn.execute(
            "INSERT INTO sources (" + ",".join(data) + ") VALUES (" + ",".join("?" * len(data)) + ") "
            "ON CONFLICT(id) DO UPDATE SET " +
            ",".join(f"{k}=excluded.{k}" for k in data if k != "id"),
            tuple(data.values()))
        known_sources.add(sid)
        counts["sources"] = counts.get("sources", 0) + 1

    # --- rows ---------------------------------------------------------------------
    for table, rows in (pack.get("rows") or {}).items():
        if table not in ALLOWED_TABLES:
            errors.append(f"table {table!r} is not loadable from a pack")
            continue
        cols = columns(conn, table)
        colset = set(cols)
        n_ins = n_upd = n_rej = n_skip = 0
        if table == "sources":
            continue  # handled above
        for row in rows:
            if "match" in row and ("set" in row or "fill" in row):
                n_upd += apply_update(conn, table, row, known_sources, dry_run, errors, kept)
                continue
            # {"insert": {...}, "add_sources": [...]} — a plain insert that also registers
            # extra provenance links in source_refs.
            extra_sources = row.get("add_sources") or []
            if "insert" in row:
                row = dict(row["insert"])
            bad = set(row) - colset
            if bad:
                errors.append(f"{table}: unknown columns {sorted(bad)} in row {str(row)[:120]}")
                n_rej += 1
                continue
            if table in PROVENANCE_EXEMPT:
                required = ()
            else:
                base = SOURCE_COL_OVERRIDE.get(table, "source_id")
                required = PROVENANCE + (base,) + REQUIRED_BY_TABLE.get(table, ())
            # A value of 0 or 0.0 is legitimate (a metric can be zero, a stake can be zero).
            # Only None and empty string count as missing.
            missing_prov = [p for p in required if p in colset and row.get(p) in (None, "")]
            if missing_prov:
                errors.append(f"{table}: row missing required field(s) {missing_prov}: {str(row)[:140]}")
                n_rej += 1
                continue
            if table in PROVENANCE_EXEMPT:
                pass  # no source_id requirement
            elif table in SOURCE_COL_OVERRIDE:
                # multi-source row: every cited id must resolve
                cited = [x.strip() for x in str(row.get(SOURCE_COL_OVERRIDE[table]) or "").split(",") if x.strip()]
                bad_src = [x for x in cited if x not in known_sources
                           and not conn.execute("SELECT 1 FROM sources WHERE id=?", (x,)).fetchone()]
                if bad_src:
                    errors.append(f"{table}: source_ids not found {bad_src}: {str(row)[:120]}")
                    n_rej += 1
                    continue
            elif row.get("source_id") not in known_sources:
                if ALLOW_MISSING_SOURCE:
                    # Cross-pack reference: the source exists in the database under another pack.
                    # Only permitted with --allow-missing-source, and the pack order is then load-bearing.
                    if not conn.execute("SELECT 1 FROM sources WHERE id=?", (row["source_id"],)).fetchone():
                        errors.append(f"{table}: source_id {row['source_id']} not in pack AND not in database: "
                                      f"{str(row)[:120]}")
                        n_rej += 1
                        continue
                    warnings.append(f"{table}: source_id {row['source_id']} resolved from the database, "
                                    f"not this pack (load order dependency)")
                else:
                    errors.append(f"{table}: source_id {row['source_id']} not found "
                                  f"(add it to the pack's sources array, or pass "
                                  f"--allow-missing-source if it comes from an earlier pack): "
                                  f"{str(row)[:120]}")
                    n_rej += 1
                    continue
            data = {k: v for k, v in row.items() if k in colset}
            pk = "id" if "id" in colset else None
            ukey = UNIQUE_KEY_TABLES.get(table)
            if not ukey and pk and not data.get(pk):
                # No explicit primary key supplied: look for another single-column UNIQUE
                # constraint that IS supplied, so a partial row updates instead of trying to
                # insert and violating NOT NULL columns it does not carry.
                for (cand,) in unique_targets(conn, table):
                    if cand in data and cand != pk:
                        ukey = cand
                        break
            if (not ukey and is_append_only(conn, table) and not data.get("id")
                    and not FORCE_APPEND):
                # Append-only table (autoincrement PK, no unique key). Loading the same pack
                # twice would silently duplicate rows, so first check whether an IDENTICAL row
                # already exists. Identical -> skip (idempotent). Not identical -> insert, which
                # preserves the normal multi-pack workflow where each pack adds new rows.
                cols_l = list(data)
                probe = " AND ".join(
                    f'"{c}" IS NULL' if data[c] is None else f'"{c}" IS ?' for c in cols_l)
                probe_params = tuple(
                    data[c] for c in cols_l if data[c] is not None)
                try:
                    dup = conn.execute(
                        f"SELECT 1 FROM {table} WHERE {probe} LIMIT 1", probe_params).fetchone()
                except sqlite3.OperationalError:
                    dup = None
                if dup:
                    n_skip += 1
                    continue
            cukey = None
            if not ukey:
                for cand in composite_unique_targets(conn, table):
                    # Every key column must be PRESENT in the row. It may legitimately be
                    # NULL (SQLite treats NULLs as distinct in UNIQUE indexes, but we match
                    # on IS NULL so that re-running a pack updates rather than duplicates).
                    if all(c in data for c in cand):
                        cukey = cand
                        break
            if cukey:
                where = " AND ".join(
                    f'"{c}" IS NULL' if data[c] is None else f'"{c}"=?' for c in cukey)
                params = tuple(data[c] for c in cukey if data[c] is not None)
                exists = conn.execute(f"SELECT 1 FROM {table} WHERE {where}", params).fetchone()
                setcols = [k for k in data if k not in cukey]
                if not dry_run:
                    if setcols:
                        conn.execute(
                            f"INSERT INTO {table} ({','.join(data)}) "
                            f"VALUES ({','.join('?'*len(data))}) "
                            f"ON CONFLICT({','.join(cukey)}) DO UPDATE SET "
                            + ",".join(f"{k}=excluded.{k}" for k in setcols),
                            tuple(data.values()))
                    else:
                        conn.execute(
                            f"INSERT OR IGNORE INTO {table} ({','.join(data)}) "
                            f"VALUES ({','.join('?'*len(data))})",
                            tuple(data.values()))
                n_upd += 1 if exists else 0
                n_ins += 0 if exists else 1
            elif ukey and data.get(ukey):
                exists = conn.execute(f"SELECT 1 FROM {table} WHERE {ukey}=?", (data[ukey],)).fetchone()
                if not dry_run:
                    conn.execute(
                        f"INSERT INTO {table} ({','.join(data)}) VALUES ({','.join('?'*len(data))}) "
                        f"ON CONFLICT({ukey}) DO UPDATE SET " +
                        ",".join(f"{k}=excluded.{k}" for k in data if k != ukey),
                        tuple(data.values()))
                n_upd += 1 if exists else 0
                n_ins += 0 if exists else 1
            elif table in TEXT_PK_TABLES and pk and data.get(pk):
                exists = conn.execute(f"SELECT 1 FROM {table} WHERE id=?", (data[pk],)).fetchone()
                sql = (f"INSERT INTO {table} ({','.join(data)}) VALUES ({','.join('?'*len(data))}) "
                       f"ON CONFLICT(id) DO UPDATE SET " +
                       ",".join(f"{k}=excluded.{k}" for k in data if k != "id"))
                if not dry_run:
                    conn.execute(sql, tuple(data.values()))
                n_upd += 1 if exists else 0
                n_ins += 0 if exists else 1
            elif pk and data.get(pk):
                exists = conn.execute(f"SELECT 1 FROM {table} WHERE id=?", (data[pk],)).fetchone()
                if not dry_run:
                    conn.execute(
                        f"INSERT INTO {table} ({','.join(data)}) VALUES ({','.join('?'*len(data))}) "
                        f"ON CONFLICT(id) DO UPDATE SET " +
                        ",".join(f"{k}=excluded.{k}" for k in data if k != "id"),
                        tuple(data.values()))
                n_upd += 1 if exists else 0
                n_ins += 0 if exists else 1
            else:
                if not dry_run:
                    cur = conn.execute(
                        f"INSERT INTO {table} ({','.join(data)}) VALUES ({','.join('?'*len(data))})",
                        tuple(data.values()))
                    for entry in extra_sources:
                        add_source_ref(conn, table, cur.lastrowid, entry, known_sources, errors)
                n_ins += 1

        counts[table] = counts.get(table, 0) + n_ins + n_upd
        if not dry_run:
            conn.execute("INSERT INTO ingest_log (run_at, pack, table_name, action, rows_affected, detail) "
                         "VALUES (?,?,?,?,?,?)",
                         (run_at, pack_id, table, "insert", n_ins,
                          json.dumps({"updated": n_upd, "rejected": n_rej,
                                      "skipped_identical": n_skip})))

    if errors:
        print(f"{len(errors)} validation error(s):", file=sys.stderr)
        for e in errors[:40]:
            print("  !", e, file=sys.stderr)
        if not dry_run:
            conn.rollback()
            print("\nrolled back: fix the pack and re-run.", file=sys.stderr)
        conn.close()
        return 1

    if not dry_run:
        conn.execute("INSERT INTO ingest_log (run_at, pack, table_name, action, rows_affected, detail) "
                     "VALUES (?,?,?, 'ok', 0, ?)",
                     (run_at, pack_id, "_pack", json.dumps({"counts": counts,
                                                            "prepared_by": pack.get("prepared_by"),
                                                            "prepared_on": pack.get("prepared_on"),
                                                            **({"kept_existing": kept} if kept else {})})))
        conn.commit()
    conn.close()
    for w in warnings:
        print(f"  ~ {w}")
    for k in kept:
        print(f"  ~ {k['table']} {k['match']}: kept {k['column']}={k['kept']!r}; "
              f"the pack offered {k['offered']!r}. A human settles this.")
    verb = "would load" if dry_run else "loaded"
    print(f"{verb} pack {pack_id}: " + ", ".join(f"{k}={v}" for k, v in sorted(counts.items())))
    return 0


def main(argv: list[str]) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("pack", help="path to a curated JSON pack")
    p.add_argument("--dry-run", action="store_true", help="validate without writing")
    p.add_argument("--allow-missing-source", action="store_true",
                   help="permit source_id values that are absent from this pack but already in the database "
                        "(cross-pack references; makes pack load order significant)")
    p.add_argument("--force-append", action="store_true",
                   help="permit appending to autoincrement tables that already hold rows. These tables "
                        "have no unique key, so re-loading a pack DUPLICATES their rows. Prefer "
                        "scripts/rebuild_all.py, which deletes the database first.")
    a = p.parse_args(argv)
    return load(a.pack, a.dry_run, a.allow_missing_source, a.force_append)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
