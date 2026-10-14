#!/usr/bin/env python3
"""
Site addresses and suburbs from the NSW Planning Portal's own project records.

Every NSW State Significant Development record on the portal carries `field_project_address`,
the address the Department of Planning, Housing and Infrastructure records for the project. The
harvest behind RG-002 archived all 46 data centre SSD records as node JSON with SHA-256
manifests, but scrapers/ingest_nsw_dc.py extracts a fixed field list and never took the address:
42 of the 46 sites showed none. This script takes it, and the suburb the address names.

Rules (no geocoding, no inference, no correction):
  * Address: the portal's string, verbatim except that markup and runs of whitespace are
    removed. A misspelling in the record is the record's, and is kept. Taken only when the string
    names a street or a lot; a string that names the project instead of a place ("78 Lockwood
    Road Data Centre") is left for a human.
  * Suburb: the locality the address names after its last comma, with any parenthetical, "NSW"
    and postcode removed. Taken only where every part of the address that names a locality names
    the same one. An address with no comma gives no suburb: telling street from locality in
    "Augusta Street Blacktown" would be a guess.
  * Never overwrites. The pack uses load_pack.py's "fill", which writes only empty columns and
    reports every existing value that differs from the portal's, for a human to settle.
  * Council: field_local_council_area is not written. Every one of these sites already has a
    council, and comparing spellings is what lga_aliases is for.

Inputs (all archived, offline):
  * data/raw/nsw_planning/nodes/<slug>.json + .meta.json, each verified against its manifest
    (read_nodes in curate_site_coordinates.py).
  * data/packs/*.json - the SSD reference -> site mapping, and the portal pages already
    catalogued as sources. This pack cites the page the coordinates pack registered, so it loads
    after data/packs/site_coordinates.json.

Refuses to write if a node fails its SHA-256 check, an SSD reference maps to more than one site,
or a site's portal page is not catalogued as a source.

Outputs:
  * data/packs/site_portal_fields.json - fills sites.address and sites.suburb, citing each
    project's own portal page. Its "_left" list names every value not taken, and why.

Run:
    python3 scripts/curate_site_portal_fields.py
    python3 scripts/load_pack.py data/packs/site_portal_fields.json --allow-missing-source
"""
from __future__ import annotations

import glob
import html
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from curate_site_coordinates import NODES, PROJECT_URL, first, read_nodes, ssd_to_site  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PACKS = os.path.join(ROOT, "data", "packs")
OUT_PACK = os.path.join(PACKS, "site_portal_fields.json")

STREET = re.compile(r"\b(Road|Rd|Street|St|Drive|Dr|Avenue|Ave|Place|Pl|Close|Crescent|Cres|"
                    r"Way|Lane|Parade|Highway|Hwy|Boulevard|Circuit|Court|Terrace|Lot)\b", re.I)
PROJECT_NAME = re.compile(r"\bdata cent(?:re|er)\b", re.I)
# Joins two addresses: "105 and 113 Hollinsworth Road", "2 & 10 - 22 Kent Road".
JOIN = re.compile(r"\s+(?:and|&)\s+(?=\d|Lot\b)", re.I)
LOCALITY = re.compile(r"[A-Za-z][A-Za-z' -]*[A-Za-z]")


def clean(value: str | None) -> str:
    text = html.unescape(re.sub(r"<[^>]+>", " ", value or ""))
    return re.sub(r"\s+", " ", text).strip()


def locality(address: str) -> tuple[str | None, str]:
    """(the suburb the address names, or None; why not, when None)."""
    names = []
    for part in JOIN.split(re.sub(r"\([^)]*\)", " ", address)):
        if "," not in part:
            continue
        tail = part.rsplit(",", 1)[1]
        tail = re.sub(r"\b(?:NSW|N\.S\.W\.)\b|\b\d{4}\b", " ", tail)
        tail = re.sub(r"\s+", " ", tail).strip()
        # A street type marks a street only as the last word: "Honeycomb Drive" is a street,
        # "Lane Cove West" is a suburb.
        if not LOCALITY.fullmatch(tail) or STREET.fullmatch(tail.split()[-1]):
            return None, f"text after a comma is not a locality: {tail!r}"
        names.append(tail)
    if not names:
        return None, "no comma, so no locality can be told from the street"
    if len({n.lower() for n in names}) > 1:
        return None, f"names more than one locality: {sorted(set(names))}"
    return names[0], ""


def catalogued_portal_sources() -> dict[str, str]:
    """Project page URL -> source id, from every pack except this script's own output."""
    by_url: dict[str, str] = {}
    for path in sorted(glob.glob(os.path.join(PACKS, "*.json"))):
        if os.path.abspath(path) == OUT_PACK:
            continue
        for src in json.load(open(path)).get("sources", []):
            by_url.setdefault(src["url"].rstrip("/"), src["id"])
    return by_url


def main() -> int:
    errors: list[str] = []
    nodes = read_nodes(errors)
    sites = ssd_to_site(errors)
    known = catalogued_portal_sources()

    by_site: dict[str, list[dict]] = {}
    for n in nodes:
        node = json.load(open(os.path.join(NODES, n["slug"] + ".json")))
        n["address"] = clean(first(node, "field_project_address").get("value"))
        site = sites.get(n["case_id"])
        if site is not None:
            by_site.setdefault(site, []).append(n)
            if PROJECT_URL.format(slug=n["slug"]) not in known:
                errors.append(f"{n['case_id']}: its portal page is not catalogued as a source; "
                              "run scripts/curate_site_coordinates.py first")

    if errors:
        print("refusing to write; fix these first:", file=sys.stderr)
        for e in errors:
            print(f"  {e}", file=sys.stderr)
        return 1

    rows, left = [], []
    for site in sorted(by_site):
        ns = sorted(by_site[site], key=lambda r: r["case_id"])
        refs = ", ".join(n["case_id"] for n in ns)
        addresses = {n["address"] for n in ns if n["address"]}
        if len(addresses) != 1:
            why = "no address recorded" if not addresses else f"its SSD records differ: {sorted(addresses)}"
            left.append(dict(site=site, ssd=refs, field="address", reason=why))
            continue
        address = addresses.pop()
        if PROJECT_NAME.search(address) or not STREET.search(address):
            left.append(dict(site=site, ssd=refs, field="address", value=address,
                             reason="names the project, not a street or lot"))
            continue
        fill = {"address": address}
        suburb, why = locality(address)
        if suburb:
            fill["suburb"] = suburb
        else:
            left.append(dict(site=site, ssd=refs, field="suburb", value=address, reason=why))
        rows.append(dict(
            match=dict(id=site),
            fill=fill,
            add_sources=[known[PROJECT_URL.format(slug=ns[0]["slug"])]],
        ))

    pack = {
        "pack_id": "site-portal-fields-nsw-2026-09",
        "prepared_by": "scripts/curate_site_portal_fields.py from data/raw/nsw_planning/nodes/",
        "prepared_on": max(n["fetched"] for ns in by_site.values() for n in ns),
        "_comment": [
            "Fills sites.address with the address the NSW Planning Portal records for each data",
            "centre SSD project (field_project_address), verbatim, and sites.suburb with the locality",
            "that address names. Read from archived, SHA-256-verified node JSON. Uses fill, so no",
            "existing value is overwritten; differences are reported at load for a human to settle.",
            "Each row cites the project's own portal page. _left lists every value not taken.",
        ],
        "sources": [],
        "rows": {"sites": rows},
        "_left": left,
    }
    with open(OUT_PACK, "w") as f:
        json.dump(pack, f, indent=2, ensure_ascii=False)
        f.write("\n")

    n_sub = sum("suburb" in r["fill"] for r in rows)
    print(f"{len(nodes)} SSD records verified; {len(rows)} sites given an address, {n_sub} a suburb; "
          f"{len(left)} values left for a human (see _left).")
    print(f"wrote {os.path.relpath(OUT_PACK, ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
