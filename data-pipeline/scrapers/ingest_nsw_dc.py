#!/usr/bin/env python3
"""
ADCO ingestion: NSW Planning Portal — enumerate every data centre major project and harvest
its structured record. Closes RG-002 and feeds RG-023/RG-031.

The portal is a Drupal application. The reliable, documented path is:

  1. GET /major-projects/search?<filters>&page=N     -> project slugs
     Working filter combination as at 2026-09-18:
       field_case_type_value = "State Significant Development"
       combine               = "Data Centre"
     Nine results per page; "No results found" marks the end.
  2. GET /major-projects/projects/<slug>             -> read node/<nid> from drupal-settings-json
  3. GET /node/<nid>?_format=json                    -> structured fields:
       title, field_case_id (SSD-xxxxxxxx), field_case_stage, field_case_type,
       field_date_of_determination_mp, field_decision, field_determination_authority,
       field_development, field_industry, field_local_council_area, field_attachment
  4. Attachments: each entry in field_attachment is a node whose own JSON carries the
     AttachRef; files then download from
       https://majorprojects.planningportal.nsw.gov.au/prweb/PRRestService/mp/01/getContent?AttachRef=<ref>
     Draft conditions and some EPA comment documents return HTTP 401 — assessment material is
     partly access-restricted even where the signed consent is public.

Usage:
    python3 scrapers/ingest_nsw_dc.py --search          # enumerate slugs only
    python3 scrapers/ingest_nsw_dc.py --harvest         # enumerate + fetch every project record
    python3 scrapers/ingest_nsw_dc.py --harvest --limit 10
    python3 scrapers/ingest_nsw_dc.py --attachments SLUG   # list a project's document slugs

Output: data/raw/nsw_planning/dc_project_slugs.json
        exports/nsw_planning/nsw_data_centre_projects.csv
        data/raw/nsw_planning/nodes/<slug>.json  (archived, with a SHA-256 manifest)
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(ROOT, "data", "raw", "nsw_planning")
NODES = os.path.join(RAW, "nodes")
OUT_CSV = os.path.join(ROOT, "exports", "nsw_planning", "nsw_data_centre_projects.csv")
BASE = "https://www.planningportal.nsw.gov.au"
UA = ("ADCO-research/1.0 (Australian Data Centre Observatory; open public-interest research "
      "database; single-threaded polite crawler; stop on request)")
DELAY = 1.6
SEARCH_FILTERS = {"field_case_type_value": "State Significant Development", "combine": "Data Centre"}
FIELDS = ["title", "field_case_id", "field_case_stage", "field_case_type",
          "field_date_of_determination_mp", "field_decision", "field_determination_authority",
          "field_development", "field_industry", "field_local_council_area"]


def get(url: str, timeout: int = 90) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read()


def archive(path: str, body: bytes, url: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as fh:
        fh.write(body)
    with open(path + ".meta.json", "w", encoding="utf-8") as fh:
        json.dump({"url": url, "fetched_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                   "sha256": hashlib.sha256(body).hexdigest(), "bytes": len(body), "user_agent": UA},
                  fh, indent=1)


def enumerate_slugs(max_pages: int = 40) -> list[str]:
    slugs: dict[str, int] = {}
    for pg in range(max_pages):
        params = dict(SEARCH_FILTERS, page=pg)
        url = f"{BASE}/major-projects/search?" + urllib.parse.urlencode(params)
        try:
            html = get(url).decode("utf-8", "replace")
        except (urllib.error.URLError, OSError) as exc:
            print(f"[stop] page {pg}: {exc}", file=sys.stderr)
            break
        found = sorted(set(re.findall(r"/major-projects/projects/([a-z0-9\-]+)", html)))
        if not found or "No results found" in html:
            break
        for s in found:
            slugs.setdefault(s, pg)
        print(f"[search] page {pg}: {len(found)} links ({len(slugs)} unique so far)")
        time.sleep(DELAY)
    os.makedirs(RAW, exist_ok=True)
    with open(os.path.join(RAW, "dc_project_slugs.json"), "w", encoding="utf-8") as fh:
        json.dump(sorted(slugs), fh, indent=1)
    return sorted(slugs)


def node_id(slug: str) -> str | None:
    html = get(f"{BASE}/major-projects/projects/{slug}").decode("utf-8", "replace")
    m = re.search(r'currentPath\\?":\\?"node\\?/(\d+)', html)
    return m.group(1) if m else None


def val(node: dict, key: str) -> str:
    v = node.get(key) or []
    if isinstance(v, list):
        return "; ".join(str(x.get("value", "")).strip() for x in v if isinstance(x, dict) and x.get("value"))
    return str(v)


def describe(slug: str) -> dict | None:
    """Fetch and archive a project's structured record."""
    try:
        html = get(f"{BASE}/major-projects/projects/{slug}").decode("utf-8", "replace")
    except (urllib.error.URLError, OSError) as exc:
        print(f"[miss] {slug}: {exc}", file=sys.stderr)
        return None
    m = re.search(r'currentPath\\?":\\?"node\\?/(\d+)', html)
    if not m:
        print(f"[miss] {slug}: no node id in markup", file=sys.stderr)
        return None
    nid = m.group(1)
    time.sleep(DELAY)
    try:
        raw = get(f"{BASE}/node/{nid}?_format=json")
    except (urllib.error.URLError, OSError) as exc:
        print(f"[miss] {slug}: node json {exc}", file=sys.stderr)
        return None
    archive(os.path.join(NODES, f"{slug}.json"), raw, f"{BASE}/node/{nid}?_format=json")
    try:
        node = json.loads(raw)
    except json.JSONDecodeError as exc:
        print(f"[miss] {slug}: bad json {exc}", file=sys.stderr)
        return None

    # The development description is rendered on the project page, not in the node JSON.
    text = re.sub(r"<script.*?</script>|<style.*?</style>", "", html, flags=re.S)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text)
    dm = re.search(r"(Construction and [Oo]peration[^|]{20,700}?)(?:Attachments & Resources|Current Status|$)", text)
    desc = dm.group(1).strip() if dm else ""
    cap = re.findall(r"(\d+(?:\.\d+)?)\s?(?:MW|megawatt)", desc, re.I)

    rec = {
        "slug": slug,
        "node_id": nid,
        "title": val(node, "title"),
        "case_id": val(node, "field_case_id"),
        "stage": val(node, "field_case_stage"),
        "case_type": val(node, "field_case_type"),
        "decision": val(node, "field_decision"),
        "determination_date": val(node, "field_date_of_determination_mp")[:10],
        "determination_authority": val(node, "field_determination_authority"),
        "development_type": val(node, "field_development"),
        "industry": val(node, "field_industry"),
        "lga": val(node, "field_local_council_area"),
        "mw_mentions_in_description": "; ".join(sorted(set(cap))),
        "description": desc[:700],
        "n_attachments": len(node.get("field_attachment") or []),
    }
    time.sleep(DELAY)
    return rec


MOD_SLUGS = [
    "51-huntingwood-drive-data-centre-mod-2-design-updates",
    "modification-1-51-huntingwood-drive-data-centre-reduced-scale",
    "eastern-creek-data-centre-mod-2-power-consumption-increase",
    "roberts-road-data-centre-mod-1-height-increase",
    "roberts-road-dc-mod-2-additional-back-generators-and-diesel-storage",
    "roberts-road-dc-mod-4-changes-operational-infrastructure",
    "davis-rd-data-centre-mod-1-tree-removal-correction",
    "talavera-road-data-centre-mod-1-expansion",
    "kemps-creek-data-centre-mod-1-data-hall-fit-out",
    "lane-cove-west-data-centre-mod-1-fuel-storage",
    "lane-cove-west-data-centre-mod-2-layout-changes",
    "lane-cove-west-data-centre-mod-3-design-changes",
    "lane-cove-west-data-centre-mod-4-apdc-inclusion",
    "modification-2-lanceley-place-data-centre",
    "mod-3-lanceley-place-data-centre-fire-access-and-switchroom",
    "200-aldington-mod-8-amendments-road-upgrade-works-and-timing",
    "dexus-estate-mod-7-data-centre-site-layout",
]
OUT_MODS = os.path.join(ROOT, "exports", "nsw_planning", "nsw_data_centre_modifications.csv")


def harvest_mods() -> int:
    """Harvest the post-consent modification records.

    These matter more than their administrative framing suggests: a consent's original capacity is
    not its operating capacity. Fuel storage, generator counts, building height and power
    consumption all change by modification, and modifications do not appear in any headline
    pipeline figure.
    """
    os.makedirs(os.path.dirname(OUT_MODS), exist_ok=True)
    rows: list[dict] = []
    for i, s in enumerate(MOD_SLUGS, 1):
        print(f"[{i}/{len(MOD_SLUGS)}] {s}")
        rec = describe(s)
        if rec:
            rows.append(rec)
    if not rows:
        print("nothing harvested", file=sys.stderr)
        return 1
    with open(OUT_MODS, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(sorted(rows, key=lambda r: r["title"]))
    print(f"\nwrote {OUT_MODS} ({len(rows)} modifications)")
    for r in sorted(rows, key=lambda r: r["title"]):
        print(f"  {r['case_id']:16s}{r['stage'][:18]:20s}{r['decision'][:10]:11s}{r['title'][:66]}")
        if r["description"]:
            print(f"      {r['description'][:230]}")
    return 0


def harvest(limit: int | None) -> int:
    slugs = enumerate_slugs()
    if limit:
        slugs = slugs[:limit]
    os.makedirs(os.path.dirname(OUT_CSV), exist_ok=True)
    rows: list[dict] = []
    for i, s in enumerate(slugs, 1):
        print(f"[{i}/{len(slugs)}] {s}")
        rec = describe(s)
        if rec:
            rows.append(rec)
    if not rows:
        print("nothing harvested", file=sys.stderr)
        return 1
    cols = list(rows[0].keys())
    with open(OUT_CSV, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=cols)
        w.writeheader()
        w.writerows(sorted(rows, key=lambda r: (r["lga"], r["title"])))
    print(f"\nwrote {OUT_CSV} ({len(rows)} projects)")

    by_lga: dict[str, int] = {}
    by_stage: dict[str, int] = {}
    for r in rows:
        by_lga[r["lga"]] = by_lga.get(r["lga"], 0) + 1
        by_stage[r["stage"]] = by_stage.get(r["stage"], 0) + 1
    print("\nby LGA:")
    for k, v in sorted(by_lga.items(), key=lambda kv: -kv[1]):
        print(f"   {v:>3}  {k}")
    print("\nby stage:")
    for k, v in sorted(by_stage.items(), key=lambda kv: -kv[1]):
        print(f"   {v:>3}  {k}")
    approved = [r for r in rows if (r["decision"] or "").lower().startswith("approv")]
    print(f"\napproved/consented: {len(approved)}")
    return 0


def attachments(slug: str) -> int:
    nid = node_id(slug)
    if not nid:
        print(f"no node id for {slug}", file=sys.stderr)
        return 1
    node = json.loads(get(f"{BASE}/node/{nid}?_format=json"))
    atts = node.get("field_attachment") or []
    print(f"{slug}: {len(atts)} attachments")
    for a in atts:
        print("   ", a.get("url"))
    return 0


def main(argv: list[str]) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--search", action="store_true", help="enumerate project slugs only")
    p.add_argument("--harvest", action="store_true", help="enumerate + fetch every project record")
    p.add_argument("--limit", type=int, help="cap the number of projects harvested")
    p.add_argument("--attachments", metavar="SLUG", help="list a project's document slugs")
    p.add_argument("--mods", action="store_true", help="harvest the post-consent modification records")
    a = p.parse_args(argv)
    if a.attachments:
        return attachments(a.attachments)
    if a.mods:
        return harvest_mods()
    if a.harvest:
        return harvest(a.limit)
    if a.search:
        slugs = enumerate_slugs()
        print(f"\n{len(slugs)} slugs -> {os.path.join(RAW, 'dc_project_slugs.json')}")
        for s in slugs:
            print("   ", s)
        return 0
    p.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
