#!/usr/bin/env python3
"""
RG-001: compute straight-line distance from every mapped site to its nearest submarine cable
landing station.

This module is deliberately split into (a) a computation that is exact and testable, and (b) two
input files that must be populated from citable sources before anything is written to the database.
Fabricating coordinates would poison the one field the project brief explicitly asks for, so the
tool ships ready and the data stays empty until it is sourced.

INPUTS
  data/inputs/cable_landing_stations.csv
      name,system,location,state,lat,lon,source_id
      Populate from TeleGeography's Submarine Cable Map landing-point pages
      (https://www.submarinecablemap.com/country/australia), which list systems and landing
      points. Every row needs a source_id that exists in the sources table.

  data/inputs/site_coordinates.csv
      site_id,lat,lon,method,source_id
      method ∈ {geocoded_address, lga_centroid, suburb_centroid, proponent_map, precise}
      Populate by geocoding the `address` column where present, else falling back to suburb.
      Record the method on every row: an LGA centroid is not a site coordinate and must not be
      presented as one.

OUTPUT
  exports/cable_proximity.csv      one row per site, nearest three landing stations
  --write                          also emits a curated pack for scripts/load_pack.py that sets
                                   sites.nearest_cable_ls_km, nearest_cable_ls_name and
                                   proximity_note

USAGE
  python3 scripts/cable_proximity.py --template      # write the two empty input templates
  python3 scripts/cable_proximity.py                 # compute from populated inputs
  python3 scripts/cable_proximity.py --write         # compute and emit a loadable pack

The haversine great-circle distance is the right measure here: cable landing proximity is about
terrestrial backhaul length and latency, and straight-line km is the standard first-order proxy.
It is NOT a route distance and must be labelled as straight-line wherever it is published.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import os
import sqlite3
import sys
from datetime import date

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB = os.path.join(ROOT, "exports", "australian_data_centre_observatory.db")
IN_DIR = os.path.join(ROOT, "data", "inputs")
OUT_CSV = os.path.join(ROOT, "exports", "cable_proximity.csv")
OUT_PACK = os.path.join(ROOT, "data", "packs", "rg001_cable_proximity.json")

LANDING_HEADERS = ["name", "system", "location", "state", "lat", "lon", "source_id"]
SITE_HEADERS = ["site_id", "lat", "lon", "method", "source_id"]
EARTH_R_KM = 6371.0088


def haversine_km(a: tuple[float, float], b: tuple[float, float]) -> float:
    lat1, lon1 = math.radians(a[0]), math.radians(a[1])
    lat2, lon2 = math.radians(b[0]), math.radians(b[1])
    dlat, dlon = lat2 - lat1, lon2 - lon1
    h = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    return 2 * EARTH_R_KM * math.asin(math.sqrt(h))


def write_templates() -> int:
    os.makedirs(IN_DIR, exist_ok=True)
    p1 = os.path.join(IN_DIR, "cable_landing_stations.csv")
    p2 = os.path.join(IN_DIR, "site_coordinates.csv")
    if not os.path.exists(p1):
        with open(p1, "w", newline="", encoding="utf-8") as fh:
            w = csv.writer(fh)
            w.writerow(LANDING_HEADERS)
            # The leading "#" is what load_inputs() skips on, so the example never
            # reaches the computation. It sits on the first real column rather than in
            # an extra cell of its own, so the example still has one value per header
            # and shows the true column order.
            w.writerow(["# example - delete before use: Perth CLS", "INDIGO-West", "Perth",
                        "WA", "-31.9", "115.8", "SRC_CABLEMAP"])
        print(f"wrote template {p1}")
    if not os.path.exists(p2):
        with open(p2, "w", newline="", encoding="utf-8") as fh:
            w = csv.writer(fh)
            w.writerow(SITE_HEADERS)
            # Same here: "#" on site_id keeps the row inert, and the row carries exactly
            # five values so the columns line up with the header above it.
            w.writerow(["# example - delete before use: SITE_MSFT_KEMPS", "-33.72", "150.80",
                        "geocoded_address", "SRC_NSWPORTAL_KC"])
        print(f"wrote template {p2}")
    print("\nPopulate both files from citable sources, then re-run without --template.")
    print("Rows whose source_id is not in the sources table will be rejected by load_pack.py.")
    return 0


def load_inputs() -> tuple[list[dict], list[dict]]:
    landings, sites = [], []
    for path, out, headers in ((os.path.join(IN_DIR, "cable_landing_stations.csv"), landings, LANDING_HEADERS),
                               (os.path.join(IN_DIR, "site_coordinates.csv"), sites, SITE_HEADERS)):
        if not os.path.exists(path):
            print(f"missing input: {path} (run with --template to create it)", file=sys.stderr)
            continue
        for row in csv.DictReader(open(path, encoding="utf-8-sig", newline="")):
            if not row.get(headers[0]) or str(row[headers[0]]).startswith("#"):
                continue
            try:
                row["lat"] = float(row["lat"])
                row["lon"] = float(row["lon"])
            except (KeyError, TypeError, ValueError):
                print(f"  skipping row with bad coordinates: {row}", file=sys.stderr)
                continue
            out.append(row)
    return landings, sites


def compute(write_pack: bool) -> int:
    landings, sites = load_inputs()
    if not landings or not sites:
        print(f"\nnothing to compute: {len(landings)} landing stations, {len(sites)} site coordinates.",
              file=sys.stderr)
        print("This is the expected state until the two input files are populated. See RG-001.", file=sys.stderr)
        return 1

    if not os.path.exists(DB):
        print("database not found; run scripts/build_db.py first", file=sys.stderr)
        return 2
    conn = sqlite3.connect(DB)
    known = {r[0] for r in conn.execute("SELECT id FROM sites")}

    os.makedirs(os.path.dirname(OUT_CSV), exist_ok=True)
    rows, updates = [], []
    for s in sites:
        if s["site_id"] not in known:
            print(f"  WARNING {s['site_id']} is not in the sites table", file=sys.stderr)
            continue
        ranked = sorted(((haversine_km((s["lat"], s["lon"]), (l["lat"], l["lon"])), l) for l in landings),
                        key=lambda x: x[0])
        if not ranked:
            continue
        d, near = ranked[0]
        rows.append({
            "site_id": s["site_id"], "site_lat": s["lat"], "site_lon": s["lon"],
            "geocode_method": s["method"],
            "nearest_ls": near["name"], "nearest_system": near["system"],
            "nearest_location": near["location"], "nearest_state": near["state"],
            "nearest_km": round(d, 1),
            "second_ls": ranked[1][1]["name"] if len(ranked) > 1 else "",
            "second_km": round(ranked[1][0], 1) if len(ranked) > 1 else "",
            "third_ls": ranked[2][1]["name"] if len(ranked) > 2 else "",
            "third_km": round(ranked[2][0], 1) if len(ranked) > 2 else "",
            "n_landing_stations_considered": len(landings),
            "landing_source_id": near["source_id"], "site_source_id": s["source_id"],
        })
        updates.append(dict(
            match=dict(id=s["site_id"]),
            set=dict(nearest_cable_ls_km=round(d, 1),
                     nearest_cable_ls_name=f"{near['name']} ({near['system']}, {near['location']} {near['state']})",
                     proximity_note=f"Straight-line great-circle distance, not route distance. Site coordinate "
                                    f"method: {s['method']}. Nearest three landing stations: "
                                    + "; ".join(f"{r[1]['name']} {r[0]:.0f} km" for r in ranked[:3])
                                    + f". Computed {date.today().isoformat()} by scripts/cable_proximity.py.",
                     lat=s["lat"], lon=s["lon"],
                     as_of_date=str(date.today())),
            add_sources=[near["source_id"], s["source_id"]]))

    with open(OUT_CSV, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(sorted(rows, key=lambda r: r["nearest_km"]))
    print(f"wrote {OUT_CSV} ({len(rows)} sites against {len(landings)} landing stations)")
    for r in sorted(rows, key=lambda r: r["nearest_km"])[:15]:
        print(f"  {r['site_id']:26s} {r['nearest_km']:>7.1f} km  {r['nearest_ls']} ({r['nearest_system']})"
              f"  [{r['geocode_method']}]")

    if write_pack:
        pack = {
            "pack_id": "rg001-cable-proximity",
            "prepared_by": "scripts/cable_proximity.py",
            "prepared_on": str(date.today()),
            "sources": [],
            "rows": {"sites": updates},
        }
        with open(OUT_PACK, "w", encoding="utf-8") as fh:
            json.dump(pack, fh, indent=1)
        print(f"wrote {OUT_PACK} ({len(updates)} site updates)")
        print("Load with: python3 scripts/load_pack.py data/packs/rg001_cable_proximity.json "
              "--allow-missing-source")
    return 0


def main(argv: list[str]) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--template", action="store_true", help="write the two empty input templates")
    p.add_argument("--write", action="store_true", help="also emit a loadable curated pack")
    a = p.parse_args(argv)
    if a.template:
        return write_templates()
    return compute(a.write)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
