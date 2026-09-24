#!/usr/bin/env python3
"""
Site coordinates from the NSW Planning Portal's own project records.

Every NSW State Significant Development record on the portal carries a location point,
`field_coordinates`, which the Department of Planning, Housing and Infrastructure records for
the project. The harvest behind RG-002 archived all 46 data centre SSD records as node JSON
with SHA-256 manifests, but scrapers/ingest_nsw_dc.py extracts a fixed field list and never
took the point. This script takes it. No geocoding, no inference: each coordinate is the
department's recorded point for the project, read from an archived primary record.

What the point is, and is not: it is the location the planning record gives for the project,
typically a point on the land concerned. It is not a surveyed building footprint. It is
recorded with method `planning_portal_point` so that it is never mistaken for one.

Inputs (all archived, offline):
  * data/raw/nsw_planning/nodes/<slug>.json + .meta.json - the portal node and its fetch
    manifest (url, fetched_utc, sha256). Every node read is verified against its manifest.
  * data/packs/*.json - the SSD reference -> site mapping, as the packs that created the NSW
    SSD sites recorded it. Curation runs before packs load, so the database cannot be used.

Refuses to write anything if:
  * a node fails its SHA-256 check;
  * an SSD reference maps to more than one site, or a site has two points further apart than
    MAX_SPLIT_KM;
  * a point lies outside NSW.

Outputs:
  * data/packs/site_coordinates.json - sets sites.lat/lon, cites each project's own portal
    page (registering the pages not already catalogued), for scripts/load_pack.py.
  * data/inputs/site_coordinates.csv - the same points in the RG-001 input format
    (site_id,lat,lon,method,source_id), so scripts/cable_proximity.py can run.

Run:
    python3 scripts/curate_site_coordinates.py
    python3 scripts/load_pack.py data/packs/site_coordinates.json --allow-missing-source
"""
from __future__ import annotations

import csv
import glob
import hashlib
import json
import math
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NODES = os.path.join(ROOT, "data", "raw", "nsw_planning", "nodes")
PACKS = os.path.join(ROOT, "data", "packs")
OUT_PACK = os.path.join(PACKS, "site_coordinates.json")
OUT_CSV = os.path.join(ROOT, "data", "inputs", "site_coordinates.csv")

PROJECT_URL = "https://www.planningportal.nsw.gov.au/major-projects/projects/{slug}"
METHOD = "planning_portal_point"
SSD = "State Significant Development"

# NSW's extent, generously. A point outside it is a bad record, not a site.
NSW_LAT = (-37.6, -28.1)
NSW_LON = (140.9, 153.7)
# Two SSD applications for one site must place it in the same spot.
MAX_SPLIT_KM = 0.5


def km(a: tuple[float, float], b: tuple[float, float]) -> float:
    la1, lo1, la2, lo2 = map(math.radians, (a[0], a[1], b[0], b[1]))
    h = math.sin((la2 - la1) / 2) ** 2 + math.cos(la1) * math.cos(la2) * math.sin((lo2 - lo1) / 2) ** 2
    return 12742 * math.asin(math.sqrt(h))


def first(node: dict, field: str):
    values = node.get(field) or [{}]
    return values[0]


def read_nodes(errors: list[str]) -> list[dict]:
    """Every archived SSD node with its point, verified against its manifest."""
    out = []
    for path in sorted(glob.glob(os.path.join(NODES, "*.json"))):
        if path.endswith(".meta.json"):
            continue
        slug = os.path.basename(path)[: -len(".json")]
        meta_path = path + ".meta.json"
        if not os.path.exists(meta_path):
            errors.append(f"{slug}: no fetch manifest")
            continue
        raw = open(path, "rb").read()
        meta = json.load(open(meta_path))
        if hashlib.sha256(raw).hexdigest() != meta["sha256"]:
            errors.append(f"{slug}: SHA-256 does not match its manifest")
            continue
        node = json.loads(raw)
        if first(node, "field_case_type").get("value") != SSD:
            continue  # modifications and attachments: the parent SSD record carries the point
        point = first(node, "field_coordinates")
        out.append(dict(
            slug=slug,
            case_id=first(node, "field_case_id").get("value"),
            title=first(node, "title").get("value"),
            lat=point.get("lat"),
            lon=point.get("lon"),
            wkt=point.get("value"),
            node_url=meta["url"],
            fetched=meta["fetched_utc"][:10],
            sha256=meta["sha256"],
        ))
    return out


def ssd_to_site(errors: list[str]) -> dict[str, str]:
    """SSD reference -> site id, from every pack except this script's own output."""
    mapping: dict[str, set[str]] = {}
    for path in sorted(glob.glob(os.path.join(PACKS, "*.json"))):
        if os.path.abspath(path) == OUT_PACK:
            continue
        for app in json.load(open(path)).get("rows", {}).get("applications", []):
            ref = app.get("reference") or (app.get("set") or {}).get("reference")
            site = app.get("site_id") or (app.get("match") or {}).get("site_id")
            if ref and site:
                mapping.setdefault(ref.strip(), set()).add(site)
    for ref, sites in mapping.items():
        if len(sites) > 1:
            errors.append(f"{ref} maps to more than one site: {sorted(sites)}")
    return {ref: next(iter(sites)) for ref, sites in mapping.items() if len(sites) == 1}


def catalogued_portal_sources() -> dict[str, str]:
    """Project page URL -> source id, for pages an earlier pack already registered."""
    by_url = {}
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

    points: dict[str, list[dict]] = {}
    unmatched = []
    for n in nodes:
        if n["lat"] is None or n["lon"] is None:
            errors.append(f"{n['case_id']}: SSD record has no point")
            continue
        if not (NSW_LAT[0] < n["lat"] < NSW_LAT[1] and NSW_LON[0] < n["lon"] < NSW_LON[1]):
            errors.append(f"{n['case_id']}: point {n['lat']},{n['lon']} lies outside NSW")
            continue
        site = sites.get(n["case_id"])
        if site is None:
            unmatched.append(n["case_id"])
            continue
        points.setdefault(site, []).append(n)

    for site, ns in points.items():
        spread = max((km((a["lat"], a["lon"]), (b["lat"], b["lon"])) for a in ns for b in ns), default=0)
        if spread > MAX_SPLIT_KM:
            errors.append(f"{site}: its SSD records place it {spread:.2f} km apart")

    if errors:
        print("refusing to write; fix these first:", file=sys.stderr)
        for e in errors:
            print(f"  {e}", file=sys.stderr)
        return 1

    new_sources, rows, csv_rows = [], [], []
    for site in sorted(points):
        # One point per site: the earliest-numbered SSD record, so the choice is stable.
        n = sorted(points[site], key=lambda r: r["case_id"])[0]
        url = PROJECT_URL.format(slug=n["slug"])
        source_id = known.get(url)
        if source_id is None:
            source_id = "SRC_NSWPORTAL_" + n["case_id"].replace("-", "").upper()
            new_sources.append(dict(
                id=source_id,
                title=f"{n['title']} ({n['case_id']}) - NSW Planning Portal major project record",
                publisher="NSW Department of Planning, Housing and Infrastructure",
                url=url,
                doc_type="primary_planning_portal",
                published=None,
                credibility="A",
                accessed=n["fetched"],
                notes=(f"Project record read as node JSON from {n['node_url']}, fetched {n['fetched']}, "
                       f"SHA-256 {n['sha256']}, archived at data/raw/nsw_planning/nodes/{n['slug']}.json. "
                       f"Cited for the project's recorded location: field_coordinates {n['wkt']}."),
            ))
            known[url] = source_id
        rows.append(dict(
            match=dict(id=site),
            set=dict(lat=n["lat"], lon=n["lon"]),
            add_sources=[source_id],
        ))
        csv_rows.append(dict(site_id=site, lat=n["lat"], lon=n["lon"], method=METHOD, source_id=source_id))

    pack = {
        "pack_id": "site-coordinates-nsw-portal-2026-09",
        "prepared_by": "scripts/curate_site_coordinates.py from data/raw/nsw_planning/nodes/",
        "prepared_on": max(n["fetched"] for ns in points.values() for n in ns),
        "_comment": [
            "Sets sites.lat/lon to the location point the NSW Planning Portal records for each data",
            f"centre State Significant Development project (method {METHOD}). Read from archived,",
            "SHA-256-verified node JSON; nothing is geocoded or inferred. The point is the planning",
            "record's location for the project, not a surveyed building footprint.",
        ],
        "sources": new_sources,
        "rows": {"sites": rows},
    }
    with open(OUT_PACK, "w") as f:
        json.dump(pack, f, indent=2, ensure_ascii=False)
        f.write("\n")

    with open(OUT_CSV, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["site_id", "lat", "lon", "method", "source_id"])
        w.writeheader()
        w.writerows(csv_rows)

    print(f"{len(nodes)} SSD records verified; {len(rows)} sites located; "
          f"{len(new_sources)} project pages newly catalogued; "
          f"{len(unmatched)} records match no site{': ' + ', '.join(unmatched) if unmatched else ''}.")
    print(f"wrote {os.path.relpath(OUT_PACK, ROOT)} and {os.path.relpath(OUT_CSV, ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
