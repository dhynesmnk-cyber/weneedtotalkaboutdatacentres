#!/usr/bin/env python3
"""
The gap worklist: every site field the public record shows as "Not yet researched", sorted by
the source most likely to answer it.

The site's coverage page (/coverage) counts, field by field, how many sites hold a value and how
many carry a gap. This script produces the same count from the research database and turns each
gap into a row of work: which site, which field, which batch of sources to try first, whether
the document is already archived here, and which research questions (RG items) bear on it.

Batches are organised by source, not by cell, because one document closes many cells:

  S1  archived NSW Planning Portal project records (data/raw/nsw_planning/nodes/), offline
  S2  NSW State Significant Development documents: EIS, consent, SEARs
  S3  the Commonwealth Hosting Certification Framework register
  S4  operator primary sources: ASX releases, facility pages, annual reports; geocoding
  S5  development application records of councils approved in docs/SPEC.md
  S6  state planning registers outside NSW
  S7  ASIC extracts, and the fields almost nobody publishes (live capacity, water, grid)
  LOADER  the value is already in the pipeline but the loader does not carry it to the site

A batch is a suggestion about where to look first, not a finding. Nothing here is a value, and
nothing here closes a gap: gaps close only through a curated pack citing a source.

Two populations need different sources:
  P  sites with an archived NSW State Significant Development portal record
  O  every other site

What the fields mean, and how they map from this database onto the site's columns, mirrors
SITE_COVERAGE_FIELDS in lib/coverage.ts and transformSite in lib/ingestion/transform.ts. In
particular `hcf_certified = 'unknown'` counts as a gap, `live_capacity_mw` has no column here
and is never filled from `it_capacity_mw`, and the four "how it runs" fields are always null on
the site today, whatever the pipeline holds.

Read-only: the database is opened with mode=ro, and archived documents are only read (the portal
records verified against their SHA-256 manifests). Output is deterministic, so a re-run with no
change in the data leaves the reports byte-identical.

Refuses to write if a portal record fails its SHA-256 check, a mapped column is missing from the
schema, or the total differs from --expect.

Outputs:
  * reports/gap_worklist.csv - one row per site x missing field
  * reports/gap_worklist.md  - counts per field (laid out as /coverage is), per batch, per site

Run:
    python3 scripts/gap_worklist.py
    python3 scripts/gap_worklist.py --expect 1777   # the total /coverage shows
"""
from __future__ import annotations

import argparse
import csv
import glob
import json
import os
import re
import sqlite3
import sys
from collections import Counter, defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from curate_site_coordinates import first, read_nodes  # noqa: E402  (SHA-256-verified reader)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB = os.path.join(ROOT, "exports", "australian_data_centre_observatory.db")
NODES = os.path.join(ROOT, "data", "raw", "nsw_planning", "nodes")
CONSENTS = os.path.join(ROOT, "data", "raw", "nsw_planning", "consents")
OUT_CSV = os.path.join(ROOT, "reports", "gap_worklist.csv")
OUT_MD = os.path.join(ROOT, "reports", "gap_worklist.md")

# (site field, label as /coverage shows it, column(s) here or None where the site's value is
# always null). Order is /coverage's order.
FIELDS: list[tuple[str, str, tuple[str, ...] | None]] = [
    ("status", "Status", ("status",)),
    ("operator", "Operator", ("operator_id",)),
    ("proponent", "Proponent", ("proponent",)),
    ("lga", "Council", ("lga",)),
    ("suburb", "Suburb", ("suburb",)),
    ("state", "State", ("state",)),
    ("address", "Address", ("address",)),
    ("lat", "Coordinates", ("lat", "lon")),
    ("total_capacity_mw", "Total capacity", ("total_capacity_mw",)),
    ("it_capacity_mw", "IT capacity", ("it_capacity_mw",)),
    ("max_capacity_mw", "Maximum capacity", ("max_capacity_mw",)),
    ("first_phase_mw", "First phase capacity", ("first_phase_mw",)),
    ("live_capacity_mw", "Live capacity", None),
    ("cooling_type", "Cooling type", None),
    ("rack_density_kw", "Rack density", None),
    ("grid_connection", "Grid connection", None),
    ("water_usage", "Water usage", None),
    ("hcf_certified", "HCF certification", ("hcf_certified",)),
    ("campus_area_ha", "Campus area", ("campus_area_ha",)),
    ("gfa_sqm", "Gross floor area", ("gfa_sqm",)),
    ("capital_cost_aud", "Capital cost", ("capital_cost_aud",)),
    ("construction_jobs", "Construction jobs", ("construction_jobs",)),
    ("operational_jobs", "Operational jobs", ("operational_jobs",)),
    ("operational_from", "Operational from", ("operational_from",)),
    ("target_completion", "Target completion", ("target_completion",)),
]

# The pipeline columns that already hold a value for a field the loader leaves null
# (lib/ingestion/transform.ts). Whether each is a plain rename is a human decision; until it is
# made, these cells are marked LOADER so that nobody researches them a second time.
IN_PIPELINE = {
    "cooling_type": ("water_profile", "cooling_technology"),
    "grid_connection": ("power_profile", "connection_type"),
    "water_usage": ("water_profile", "annual_water_kl"),
}
EMPTY_VALUES = (None, "", "tbd", "unknown")

# Councils drafted in docs/COUNCIL_CANDIDATES.md. S5 applies only once one is approved.
COUNCIL_CANDIDATES = ("Blacktown", "Penrith", "Ryde", "Latrobe", "Wyndham", "Melton",
                      "Moorabool", "Hume", "Western Downs", "Ipswich", "Goyder", "Gosnells")

BATCHES = {
    "S1": "Archived NSW portal project records (offline)",
    "S2": "NSW SSD documents: EIS, consent, SEARs",
    "S3": "Hosting Certification Framework register",
    "S4": "Operator primary sources; geocoding",
    "S5": "Approved councils' development application records",
    "S6": "State planning registers outside NSW",
    "S7": "ASIC extracts; rarely published fields",
    "LOADER": "In the pipeline, not loaded to the site",
}
# Research questions already open against each batch's sources.
BATCH_RGS = {
    "S2": (34, 37, 53, 73),
    "S4": (13, 24, 71, 91),
    "S5": (34,),
    "S6": (3, 10, 11, 27, 48, 51, 56),
    "S7": (17, 21, 35, 36, 52, 59, 64, 81),
}


def batch_for(field: str, pop: str, state: str | None, council: str | None,
              has_node: bool) -> tuple[str, str]:
    """(first batch, fallback batch) for one missing field. A routing rule, not a finding."""
    elsewhere = "S6" if state not in ("NSW", None) else ("S5" if council else "S4")
    if field == "hcf_certified":
        return "S3", ""
    if field == "live_capacity_mw":
        return "S7", ""
    if pop == "P":
        if field in ("address", "suburb", "lga", "lat") and has_node:
            return "S1", "S2"
        if field in ("operator", "proponent"):
            return "S2", "S7"
        if field in ("grid_connection", "water_usage", "cooling_type", "rack_density_kw"):
            return "S2", "S7"
        if field in ("operational_from", "target_completion"):
            return "S2", "S4"
        return "S2", ""
    # Population O: the operator's own documents first, then planning records.
    if field in ("grid_connection", "water_usage"):
        return "S7", "S4"
    if field in ("cooling_type", "rack_density_kw"):
        return "S4", "S7"
    if field in ("operator", "proponent"):
        return "S4", "S7" if elsewhere == "S4" else elsewhere
    if field in ("campus_area_ha", "gfa_sqm", "capital_cost_aud", "construction_jobs",
                 "operational_jobs"):
        return (elsewhere, "S4") if elsewhere != "S4" else ("S4", "")
    return "S4", "" if elsewhere == "S4" else elsewhere


def missing(row: sqlite3.Row, cols: tuple[str, ...] | None, field: str) -> bool:
    if cols is None:
        return True
    if field == "hcf_certified":
        return row["hcf_certified"] in (None, "", "unknown")
    return any(row[c] is None or row[c] == "" for c in cols)


def consent_cases() -> set[str]:
    """SSD references with an archived consent text (data/raw/nsw_planning/consents/)."""
    cases = set()
    for meta in glob.glob(os.path.join(CONSENTS, "*.pdf.meta.json")):
        txt = meta[: -len(".pdf.meta.json")] + ".txt"
        m = re.search(r"AttachRef=([A-Z]+-\d+)", json.load(open(meta)).get("url", ""))
        if m and os.path.exists(txt):
            cases.add(m.group(1))
    return cases


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--expect", type=int, help="fail unless the total gap count equals this")
    args = ap.parse_args()

    errors: list[str] = []
    nodes = {n["case_id"]: n for n in read_nodes(errors)}
    addressed = set()
    for case_id, n in nodes.items():
        node = json.load(open(os.path.join(NODES, n["slug"] + ".json")))
        if first(node, "field_project_address").get("value"):
            addressed.add(case_id)
    consents = consent_cases()

    db = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
    db.row_factory = sqlite3.Row
    columns = {r["name"] for r in db.execute("pragma table_info(sites)")}
    for field, _, cols in FIELDS:
        for c in cols or ():
            if c not in columns:
                errors.append(f"sites.{c} (for {field}) is not in the schema")

    if errors:
        print("refusing to write; fix these first:", file=sys.stderr)
        for e in errors:
            print(f"  {e}", file=sys.stderr)
        return 1

    entities = {r["id"] for r in db.execute("select id from entities")}
    refs: dict[str, list[str]] = defaultdict(list)
    for r in db.execute("select site_id, reference from applications where reference is not null"):
        refs[r["site_id"]].append(r["reference"].strip())
    in_pipeline: dict[str, set[str]] = defaultdict(set)
    for field, (table, col) in IN_PIPELINE.items():
        for r in db.execute(f"select site_id, {col} as v from {table}"):
            if r["v"] not in EMPTY_VALUES:
                in_pipeline[r["site_id"]].add(field)
    rgs = list(db.execute(
        "select id, status, coalesce(question,'')||' '||coalesce(why_it_matters,'')||' '||"
        "coalesce(target_source,'')||' '||coalesce(notes,'') as text from research_gaps"))
    open_rgs = {r["id"] for r in rgs if r["status"] != "resolved"}

    sites = list(db.execute(
        "select s.*, so.doc_type as src_type, so.credibility as src_grade "
        "from sites s left join sources so on so.id = s.source_id order by s.name, s.id"))

    rows = []
    for s in sites:
        site_refs = refs.get(s["id"], [])
        has_node = any(ref in nodes for ref in site_refs)
        pop = "P" if has_node else "O"
        council = next((c for c in COUNCIL_CANDIDATES if c.lower() in (s["lga"] or "").lower()),
                       None)
        # Questions that name this site, by its id or one of its application references.
        tokens = [s["id"], *site_refs]
        site_rgs = sorted(r["id"] for r in rgs if r["id"] in open_rgs
                          and any(re.search(rf"\b{re.escape(t)}\b", r["text"]) for t in tokens))
        for field, label, cols in FIELDS:
            if field == "operator":
                gap = s["operator_id"] is None or s["operator_id"] not in entities
            else:
                gap = missing(s, cols, field)
            if not gap:
                continue
            notes = []
            if field in in_pipeline[s["id"]]:
                batch, fallback, bucket = "LOADER", "", "in pipeline"
                table, col = IN_PIPELINE[field]
                notes.append(f"{table}.{col} holds a value; the loader does not map it")
            else:
                batch, fallback = batch_for(field, pop, s["state"], council, has_node)
                bucket = "archived" if batch == "S1" else "research"
            if field == "live_capacity_mw":
                notes.append("never filled from it_capacity_mw")
            if field == "hcf_certified" and s["hcf_certified"] == "unknown":
                notes.append("stored as the string 'unknown'")
            if s["state"] == "Multi":
                notes.append("fleet record, not a single site")
            archived = []
            if has_node:
                archived.append("portal record")
            if any(ref in consents for ref in site_refs):
                archived.append("consent text")
            rows.append(dict(
                site_id=s["id"], site=s["name"], state=s["state"] or "", status=s["status"],
                fact_status=s["fact_status"], source_type=s["src_type"] or "",
                source_grade=s["src_grade"] or "", population=pop, field=field, label=label,
                batch=batch, fallback=fallback, bucket=bucket,
                council_candidate=council or "",
                archived="; ".join(archived),
                site_rgs=" ".join(f"RG-{i:03d}" for i in site_rgs),
                batch_rgs=" ".join(f"RG-{i:03d}" for i in BATCH_RGS.get(batch, ()) if i in open_rgs),
                note="; ".join(notes),
            ))

    total = len(rows)
    if args.expect is not None and total != args.expect:
        print(f"refusing to write: {total} gaps, expected {args.expect}. The database and the "
              "site disagree; find out why before working from either.", file=sys.stderr)
        return 1

    with open(OUT_CSV, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]) if rows else ["site_id"])
        w.writeheader()
        w.writerows(rows)

    by_field = Counter(r["field"] for r in rows)
    by_batch = Counter(r["batch"] for r in rows)
    by_field_batch = Counter((r["field"], r["batch"]) for r in rows)
    batch_order = [b for b in BATCHES if by_batch[b]]
    pops = Counter(("P" if any(ref in nodes for ref in refs.get(s["id"], [])) else "O")
                   for s in sites)

    md = [
        "# Gap worklist",
        "",
        "Generated by `scripts/gap_worklist.py` from `exports/australian_data_centre_observatory.db`",
        "(read-only). Every row is a site field the public record shows as \"Not yet researched\".",
        "A batch is where to look first, not a finding. Gaps close only through a curated pack",
        "citing a source. The full list is `reports/gap_worklist.csv`.",
        "",
        f"**{total} gaps across {len(sites)} sites and {len(FIELDS)} fields** "
        f"({len(sites) * len(FIELDS)} values). Population P (archived NSW SSD portal record): "
        f"{pops['P']} sites; population O (all others): {pops['O']} sites.",
        "",
        "## Batches",
        "",
        "| Batch | Source | Gaps | Open questions already on it |",
        "|---|---|---:|---|",
    ]
    for b in batch_order:
        rg = " ".join(f"RG-{i:03d}" for i in BATCH_RGS.get(b, ()) if i in open_rgs)
        md.append(f"| {b} | {BATCHES[b]} | {by_batch[b]} | {rg} |")
    md += [
        "",
        "## By field",
        "",
        "Laid out as the coverage page is, so the two can be compared row by row.",
        "",
        "| Field | Recorded | Not yet researched | " + " | ".join(batch_order) + " |",
        "|---|---:|---:|" + "---:|" * len(batch_order),
    ]
    for field, label, _ in FIELDS:
        cells = [str(by_field_batch[(field, b)] or "") for b in batch_order]
        md.append(f"| {label} | {len(sites) - by_field[field]} | {by_field[field]} | "
                  + " | ".join(cells) + " |")
    md.append(f"| **Total** | | **{total}** | "
              + " | ".join(f"**{by_batch[b]}**" for b in batch_order) + " |")

    per_site: dict[str, list[dict]] = defaultdict(list)
    for r in rows:
        per_site[r["site_id"]].append(r)
    md += [
        "",
        "## By site",
        "",
        "Most gaps first. Archived: documents already in `data/raw/` for this site.",
        "",
        "| Site | State | Pop. | Evidence | Gaps | Archived | Questions naming it |",
        "|---|---|---|---|---:|---|---|",
    ]
    for site_id, rs in sorted(per_site.items(), key=lambda kv: (-len(kv[1]), kv[1][0]["site"])):
        r = rs[0]
        md.append(f"| {r['site']} | {r['state']} | {r['population']} | {r['fact_status']} | "
                  f"{len(rs)} | {r['archived']} | {r['site_rgs']} |")
    md.append("")

    with open(OUT_MD, "w") as f:
        f.write("\n".join(md))

    print(f"{len(nodes)} SSD portal records verified; {len(sites)} sites; {total} gaps "
          f"({', '.join(f'{b} {by_batch[b]}' for b in batch_order)}).")
    print(f"wrote {os.path.relpath(OUT_CSV, ROOT)} and {os.path.relpath(OUT_MD, ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
