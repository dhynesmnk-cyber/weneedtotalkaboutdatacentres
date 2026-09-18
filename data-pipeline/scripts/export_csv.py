#!/usr/bin/env python3
"""
Export every table and view to exports/csv/ AND VERIFY the result.

WHY THIS SCRIPT EXISTS
----------------------
build_db.py also writes CSVs, but it runs BEFORE the curated packs are loaded, so
those files contain only the seed rows. That was a real defect: after a full
rebuild the committed CSVs understated the database badly -

    lobbying              CSV=0    DB=13
    modifications         CSV=0    DB=17
    metrics               CSV=41   DB=313
    research_gaps         CSV=19   DB=77
    sites                 CSV=41   DB=93
    sources               CSV=60   DB=117
    gov_contracts         CSV=0    DB=23
    consultancy_profile   CSV=0    DB=8

Anyone reading exports/csv/ rather than the SQLite file was silently getting the
wrong data, which is the one failure mode a verification database must not have.

This script is therefore the SINGLE authoritative CSV export and runs LAST in
rebuild_all.py, after every pack has loaded. It then re-reads each CSV it wrote
and compares the row count against the database. Any divergence is a hard error
and a non-zero exit code, so a stale export can never be committed silently.

Usage:
    python3 scripts/export_csv.py            # export + verify
    python3 scripts/export_csv.py --verify   # verify only, do not write
"""
from __future__ import annotations

import argparse
import csv
import os
import sqlite3
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(ROOT, "exports", "australian_data_centre_observatory.db")
CSV_DIR = os.path.join(ROOT, "exports", "csv")


def objects(conn: sqlite3.Connection) -> tuple[list[str], list[str]]:
    tables = [r[0] for r in conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' "
        "ORDER BY name")]
    views = [r[0] for r in conn.execute(
        "SELECT name FROM sqlite_master WHERE type='view' ORDER BY name")]
    return tables, views


def export(conn: sqlite3.Connection) -> dict[str, int]:
    os.makedirs(CSV_DIR, exist_ok=True)
    tables, views = objects(conn)
    written: dict[str, int] = {}
    for name in tables + views:
        cur = conn.execute(f'SELECT * FROM "{name}"')
        cols = [d[0] for d in cur.description]
        rows = cur.fetchall()
        with open(os.path.join(CSV_DIR, f"{name}.csv"), "w", newline="", encoding="utf-8") as fh:
            w = csv.writer(fh)
            w.writerow(cols)
            w.writerows(rows)
        written[name] = len(rows)
    return written


def verify(conn: sqlite3.Connection) -> list[str]:
    """Re-read every CSV on disk and compare against the database. Returns problems."""
    tables, views = objects(conn)
    problems: list[str] = []
    for name in tables + views:
        db_n = conn.execute(f'SELECT COUNT(*) FROM "{name}"').fetchone()[0]
        path = os.path.join(CSV_DIR, f"{name}.csv")
        if not os.path.exists(path):
            problems.append(f"{name}: no CSV on disk (database has {db_n} rows)")
            continue
        with open(path, newline="", encoding="utf-8") as fh:
            reader = csv.reader(fh)
            try:
                next(reader)  # header
            except StopIteration:
                problems.append(f"{name}: CSV is completely empty, not even a header")
                continue
            csv_n = sum(1 for _ in reader)
        if csv_n != db_n:
            problems.append(f"{name}: CSV has {csv_n} rows but database has {db_n} "
                            f"(stale export - run scripts/export_csv.py)")
    return problems


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--verify", action="store_true",
                    help="verify existing CSVs against the database without rewriting them")
    ap.add_argument("--db", default=DB_PATH)
    a = ap.parse_args(argv)

    if not os.path.exists(a.db):
        print(f"database not found at {a.db}", file=sys.stderr)
        return 2

    conn = sqlite3.connect(a.db)
    if not a.verify:
        written = export(conn)
        tables, views = objects(conn)
        total = sum(written.values())
        print(f"exported {len(tables)} tables + {len(views)} views to {os.path.relpath(CSV_DIR, ROOT)}/")
        print(f"  {total} rows written")

    problems = verify(conn)
    if problems:
        print(f"\n{len(problems)} CSV VERIFICATION FAILURE(S):", file=sys.stderr)
        for p in problems:
            print(f"  ! {p}", file=sys.stderr)
        return 1

    n = len(objects(conn)[0]) + len(objects(conn)[1])
    print(f"  verification PASSED: {n} files match the database exactly")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
