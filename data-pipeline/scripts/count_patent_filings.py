#!/usr/bin/env python3
"""
ADCO analysis: count patent filings per tracked operator, from an IP Australia extract.

This is stage 1 of the patent method in `reports/PATENT_METHOD.md` — the cheap count that either
confirms or overturns the finding there, namely that the Australian operators this project tracks
hold few or no patents because they are infrastructure businesses rather than R&D ones.

INPUT: a delimited extract of IP Australia's applicant table — IPGOD 102 (Patents Applicant
Information), or the equivalent in IP RAPID, the weekly product that superseded IPGOD. Download it
from data.gov.au; this script never fetches anything.

    python3 scripts/count_patent_filings.py --extract data/raw/patents/ipgod_102.csv

THE HARD PART IS NAME MATCHING, NOT COUNTING
--------------------------------------------
"Filings per operator" means deciding that an applicant string denotes one of our entities, and
that is the step where this kind of analysis usually goes wrong. The project has already recorded
what the failure looks like: SRC_GOVMARKET_TCS is graded C precisely because the aggregator
"consolidates 14 spelling variants of the TCS name into one master entity" and its totals are
inflated by a duplicate. Silent consolidation is the defect, not the feature.

So this script refuses to do it. The match table is built from the database — `entities.name`,
`entities.legal_name` and the human-curated `entity_aliases` — and a row counts only on an EXACT
match after conservative normalisation (case, punctuation, and trailing legal-form suffixes such
as PTY LTD or LIMITED). Anything that merely looks similar is reported separately as a **candidate
for human review** and is counted nowhere. Adding it to `entity_aliases` is a human act, exactly as
`lga_aliases` is for councils.

The counts this produces are therefore a **floor**, not a total, and the report says so.

SCHEMA TOLERANCE
----------------
The exact IPGOD column names could not be verified from the authoring environment — every IP
Australia and data.gov.au endpoint was blocked. Rather than hard-code a guess, the script detects
the applicant-name and application-number columns from the header and prints what it chose.
Override with --name-col / --id-col when it guesses wrong.

    python3 scripts/count_patent_filings.py --selftest        # offline, fixture-based
"""
from __future__ import annotations

import argparse
import csv
import os
import re
import sqlite3
import sys
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB = os.path.join(ROOT, "exports", "australian_data_centre_observatory.db")

NAME_COL_HINTS = ["applicant_name", "applicantname", "australian_applicant_name", "app_name",
                  "applicant", "name", "party_name", "owner_name"]
ID_COL_HINTS = ["australian_appl_no", "application_number", "appl_no", "application_no",
                "patent_application_number", "ipa_appl_no", "app_no", "application_id"]

# Trailing legal-form markers. Stripping these lets "NEXTDC Limited" meet "NEXTDC Ltd". It does NOT
# license merging different entities that share a stem - that is what the review list is for.
LEGAL_SUFFIXES = [
    "pty ltd", "pty limited", "pty. ltd.", "proprietary limited", "limited", "ltd", "inc",
    "incorporated", "llc", "l l c", "plc", "corp", "corporation", "co", "company", "gmbh", "sa",
    "nv", "bv", "ag", "kk", "as", "ab", "oy", "srl", "spa", "sarl",
]


def normalise(name: str) -> str:
    s = (name or "").lower()
    s = s.replace("&", " and ")
    s = re.sub(r"[^a-z0-9 ]+", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    changed = True
    while changed:
        changed = False
        for suf in LEGAL_SUFFIXES:
            if s.endswith(" " + suf):
                s = s[: -(len(suf) + 1)].strip()
                changed = True
    return s


def stem(name: str) -> str:
    """First significant word, used only to flag review candidates - never to match."""
    parts = normalise(name).split()
    return parts[0] if parts else ""


def match_table(db_path: str, operators_only: bool) -> tuple[dict[str, str], dict[str, str]]:
    """
    Returns (normalised name -> entity_id, entity_id -> display name), from the database only.
    No name in here was invented by this script.
    """
    con = sqlite3.connect(db_path)
    if operators_only:
        rows = con.execute("""
            SELECT DISTINCT e.id, e.name, e.legal_name FROM entities e
            JOIN sites s ON s.operator_id = e.id OR s.owner_id = e.id OR s.anchor_tenant_id = e.id
        """).fetchall()
    else:
        rows = con.execute("SELECT id, name, legal_name FROM entities").fetchall()

    lookup: dict[str, str] = {}
    display: dict[str, str] = {}
    for eid, name, legal in rows:
        display[eid] = name
        for candidate in (name, legal):
            if candidate:
                # A legal_name field can hold several names; split on the separators used there.
                for part in re.split(r"\s*(?:/| and |;)\s*", candidate):
                    key = normalise(re.sub(r"\(.*?\)", " ", part))
                    if key:
                        lookup.setdefault(key, eid)
    ids = set(display)
    for eid, alias in con.execute("SELECT entity_id, alias FROM entity_aliases"):
        if eid in ids:
            key = normalise(alias)
            if key:
                lookup.setdefault(key, eid)
    con.close()
    return lookup, display


def pick_column(header: list[str], hints: list[str], override: str | None, what: str) -> int:
    norm = [h.strip().lower().replace(" ", "_") for h in header]
    if override:
        want = override.strip().lower().replace(" ", "_")
        if want not in norm:
            raise SystemExit(f"--{what}-col {override!r} not in header: {header}")
        return norm.index(want)
    for hint in hints:
        if hint in norm:
            return norm.index(hint)
    for i, h in enumerate(norm):  # fall back to a substring match
        for hint in hints:
            if hint in h:
                return i
    raise SystemExit(f"could not find a {what} column in header: {header}\n"
                     f"pass --{what}-col explicitly")


def sniff_reader(path: str):
    fh = open(path, encoding="utf-8-sig", errors="replace", newline="")
    sample = fh.read(8192)
    fh.seek(0)
    try:
        dialect = csv.Sniffer().sniff(sample, delimiters=",\t;|")
    except csv.Error:
        dialect = csv.excel
    return fh, csv.reader(fh, dialect)


def count(extract: str, db_path: str, operators_only: bool,
          name_col: str | None, id_col: str | None, out_path: str | None) -> int:
    lookup, display = match_table(db_path, operators_only)
    print(f"match table: {len(lookup)} name forms for {len(display)} entities "
          f"({'site-holding operators' if operators_only else 'all entities'})")

    fh, reader = sniff_reader(extract)
    with fh:
        try:
            header = next(reader)
        except StopIteration:
            raise SystemExit(f"{extract} is empty")
        ni = pick_column(header, NAME_COL_HINTS, name_col, "name")
        ii = pick_column(header, ID_COL_HINTS, id_col, "id")
        print(f"applicant column: {header[ni]!r}   application column: {header[ii]!r}")

        hits: dict[str, set[str]] = defaultdict(set)
        raw_forms: dict[str, set[str]] = defaultdict(set)
        review: dict[str, set[str]] = defaultdict(set)
        stems = {stem(k): eid for k, eid in lookup.items() if stem(k)}
        rows = 0
        for row in reader:
            if len(row) <= max(ni, ii):
                continue
            rows += 1
            raw = row[ni]
            appno = (row[ii] or "").strip()
            key = normalise(raw)
            if not key:
                continue
            eid = lookup.get(key)
            if eid:
                hits[eid].add(appno)
                raw_forms[eid].add(raw.strip())
            elif key.split() and key.split()[0] in stems:
                review[stems[key.split()[0]]].add(raw.strip())

    print(f"\nread {rows:,} applicant rows from {os.path.basename(extract)}\n")
    ordered = sorted(display, key=lambda e: (-len(hits.get(e, ())), display[e].lower()))
    lines = ["# Patent filings per tracked operator", "",
             f"Source extract: `{os.path.basename(extract)}` — {rows:,} applicant rows.",
             "",
             "Counts are **distinct application numbers on an exact name match** after conservative "
             "normalisation, and are a **floor, not a total**. Variant spellings that did not match "
             "exactly are listed for review below and are counted nowhere. Consolidating them is a "
             "human act, recorded in `entity_aliases`.", "",
             "| Entity | Filings (floor) | Matched name forms |", "|---|---:|---|"]
    for eid in ordered:
        n = len(hits.get(eid, ()))
        forms = "; ".join(sorted(raw_forms.get(eid, ()))) or "—"
        print(f"  {n:>5}  {display[eid]}")
        lines.append(f"| {display[eid]} | {n} | {forms} |")

    if review:
        lines += ["", "## Candidates for human review — NOT counted", "",
                  "These share a leading word with a tracked entity but did not match exactly. A "
                  "shared stem is not an identity: confirm each against the register before adding "
                  "it to `entity_aliases`.", ""]
        print("\ncandidates for review (not counted):")
        for eid, forms in sorted(review.items(), key=lambda kv: display.get(kv[0], "")):
            for f in sorted(forms):
                print(f"  ? {f}   (near {display.get(eid, eid)})")
                lines.append(f"- `{f}` — near **{display.get(eid, eid)}**")

    total = sum(len(v) for v in hits.values())
    lines += ["", f"Total matched filings: **{total}** across "
                  f"{sum(1 for e in hits if hits[e])} entities."]
    print(f"\ntotal matched filings: {total}")

    if out_path:
        dest = out_path if os.path.isabs(out_path) else os.path.join(ROOT, out_path)
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        open(dest, "w", encoding="utf-8").write("\n".join(lines) + "\n")
        shown = os.path.relpath(dest, ROOT)
        print(f"wrote {dest if shown.startswith('..') else shown}")
    return 0


# --- validation -------------------------------------------------------------------------------

FIXTURE_HEADER = "australian_appl_no,applicant_name,filing_date\n"
FIXTURE_ROWS = """2019100001,NEXTDC LIMITED,2019-01-04
2019100001,NEXTDC LIMITED,2019-01-04
2020100002,NextDC Ltd.,2020-03-11
2021100003,Nextdc Holdings Pty Ltd,2021-07-02
2021100004,Equinix&nbsp;,2021-08-02
2022100005,Totally Unrelated Widgets Pty Ltd,2022-02-02
2023100006,EQUINIX, INC.,2023-05-05
"""


def selftest() -> int:
    import tempfile
    failures = 0

    def check(name: str, ok: bool, detail: str = "") -> None:
        nonlocal failures
        if ok:
            print(f"[pass] {name}")
        else:
            failures += 1
            print(f"[FAIL] {name}{(' - ' + detail) if detail else ''}")

    check("normalise strips legal suffixes",
          normalise("NEXTDC LIMITED") == normalise("NextDC Ltd.") == "nextdc",
          f"{normalise('NEXTDC LIMITED')!r} vs {normalise('NextDC Ltd.')!r}")
    check("normalise strips stacked suffixes",
          normalise("Foo Pty Ltd") == "foo", f"got {normalise('Foo Pty Ltd')!r}")
    check("normalise does not merge distinct entities",
          normalise("NEXTDC Limited") != normalise("NEXTDC Holdings Pty Ltd"))
    check("normalise folds ampersand and punctuation",
          normalise("A & B, Inc.") == "a and b", f"got {normalise('A & B, Inc.')!r}")

    # Match table must come from the real database, with no invented names.
    if not os.path.exists(DB):
        check("database present for match table", False, f"missing {DB}")
        print(f"\n{'FAILED' if failures else 'ok'}: {failures} failure(s)")
        return 1
    lookup, display = match_table(DB, operators_only=True)
    check("match table built from the database", len(display) > 5 and len(lookup) >= len(display),
          f"{len(display)} entities, {len(lookup)} name forms")
    check("NEXTDC is reachable by its normalised name", "nextdc" in lookup,
          f"sample keys: {sorted(lookup)[:6]}")

    with tempfile.TemporaryDirectory() as td:
        path = os.path.join(td, "ipgod_102.csv")
        open(path, "w", encoding="utf-8").write(FIXTURE_HEADER + FIXTURE_ROWS)
        fh, reader = sniff_reader(path)
        with fh:
            header = next(reader)
            ni = pick_column(header, NAME_COL_HINTS, None, "name")
            ii = pick_column(header, ID_COL_HINTS, None, "id")
        check("detects the applicant column from the header", header[ni] == "applicant_name",
              f"chose {header[ni]!r}")
        check("detects the application-number column", header[ii] == "australian_appl_no",
              f"chose {header[ii]!r}")

        nextdc = [e for e, n in display.items() if n.upper().startswith("NEXTDC")]
        check("NEXTDC resolves to exactly one tracked entity", len(nextdc) == 1, str(nextdc))
        if nextdc:
            seen: set[str] = set()
            review_hit = False
            for line in FIXTURE_ROWS.strip().split("\n"):
                appno, rest = line.split(",", 1)
                name = rest.rsplit(",", 1)[0]
                key = normalise(name)
                if lookup.get(key) == nextdc[0]:
                    seen.add(appno)
                elif key.split() and key.split()[0] == "nextdc":
                    review_hit = True
            check("counts distinct applications, deduplicating repeats", seen == {"2019100001", "2020100002"},
                  f"got {sorted(seen)}")
            check("does NOT silently absorb 'Nextdc Holdings' into NEXTDC", review_hit)

    print(f"\n{'FAILED' if failures else 'ok'}: {failures} failure(s)")
    return 1 if failures else 0


def main(argv: list[str]) -> int:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--extract", help="IPGOD 102 / IP RAPID applicant table (csv/tsv)")
    p.add_argument("--db", default=DB)
    p.add_argument("--all-entities", action="store_true",
                   help="match every entity, not only those holding sites")
    p.add_argument("--name-col")
    p.add_argument("--id-col")
    p.add_argument("--out", help="write a markdown report here")
    p.add_argument("--selftest", action="store_true")
    a = p.parse_args(argv)

    if a.selftest:
        return selftest()
    if a.extract:
        if not os.path.exists(a.extract):
            raise SystemExit(f"no such extract: {a.extract}\n"
                             "Download IPGOD 102 / IP RAPID from data.gov.au first; this script "
                             "never fetches.")
        return count(a.extract, a.db, not a.all_entities, a.name_col, a.id_col, a.out)
    p.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
