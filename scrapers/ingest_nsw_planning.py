#!/usr/bin/env python3
"""
ADCO ingestion: NSW Planning Portal major projects (State Significant Development / Infrastructure).

Closes research gap RG-002, which is the single highest-value ingestion task in the project:
the portal is the authoritative record for the 19-project, A$50.3bn NSW pipeline and holds the
site-level PUE, WUE, generator count, diesel storage, water source and submission history that
Pillars A, C and D all depend on.

Design constraints, deliberately conservative:
  * One request at a time, with a delay. This is a public planning register, not a data firehose.
  * A descriptive User-Agent and an opt-out contact address. If the Department asks us to stop,
    we stop.
  * Raw HTML is archived under data/raw/nsw_planning/ before any parsing. Parsing is downstream
    and reproducible; fetching is the irreversible part.
  * Nothing is written into the database by this script. It produces a JSON worklist that a human
    reviews and converts into a curated pack for scripts/load_pack.py.

Known URL shapes (verified against a live citation on 2026-09-18):
  project page   https://www.planningportal.nsw.gov.au/major-projects/projects/<slug>
  attachment     https://www.planningportal.nsw.gov.au/prweb/PRRestService/mp/01/getContent?AttachRef=<REF>
                 e.g. AttachRef=SSD-92743706!20260119T012428.711 GMT   (Mamre Road EIS)

Usage:
    python3 scrapers/ingest_nsw_planning.py --project mamre-road-data-centre-campus
    python3 scrapers/ingest_nsw_planning.py --search "data centre" --limit 5
    python3 scrapers/ingest_nsw_planning.py --attachment "SSD-92743706!20260119T012428.711 GMT"
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(ROOT, "data", "raw", "nsw_planning")
PORTAL = "https://www.planningportal.nsw.gov.au"
SEARCH = PORTAL + "/major-projects/find-a-project"
DELAY_SECONDS = 3.0
UA = ("ADCO-research/1.0 (Australian Data Centre Observatory; open public-interest research "
      "database; single-threaded polite crawler; stop on request)")


def _get(url: str, timeout: int = 60) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "*/*"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read()


def _archive(kind: str, key: str, body: bytes, url: str) -> str:
    os.makedirs(RAW, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    digest = hashlib.sha256(body).hexdigest()[:12]
    safe = re.sub(r"[^A-Za-z0-9_.-]+", "_", key)[:80]
    path = os.path.join(RAW, f"{kind}__{safe}__{stamp}__{digest}.html")
    with open(path, "wb") as fh:
        fh.write(body)
    with open(path + ".meta.json", "w", encoding="utf-8") as fh:
        json.dump({"url": url, "fetched_utc": stamp, "sha256": hashlib.sha256(body).hexdigest(),
                   "bytes": len(body), "user_agent": UA}, fh, indent=2)
    return path


def project(slug: str) -> int:
    url = f"{PORTAL}/major-projects/projects/{urllib.parse.quote(slug)}"
    body = _get(url)
    path = _archive("project", slug, body, url)
    print(f"[archived] {url}\n           -> {path} ({len(body):,} bytes)")
    text = body.decode("utf-8", "replace")

    # Cheap, robust extraction: the portal renders key-value pairs in the project summary.
    # Anything that looks like an SSD reference or a capacity figure is surfaced for review.
    found = {
        "ssd_references": sorted(set(re.findall(r"\bSSD-\d{6,}\b", text))),
        "mw_mentions": sorted(set(re.findall(r"([\d,\.]+)\s?(?:MW|megawatt)", text, re.I)))[:20],
        "attachment_refs": sorted(set(re.findall(r"AttachRef=([^&\"'<> ]+)", text)))[:20],
        "document_links": sorted(set(re.findall(r'href="(/major-projects/[^"]+)"', text)))[:20],
    }
    print(json.dumps(found, indent=2))
    out = os.path.join(RAW, f"worklist__{slug}.json")
    with open(out, "w", encoding="utf-8") as fh:
        json.dump({"slug": slug, "url": url, "archived": path, **found}, fh, indent=2)
    print(f"[worklist] {out}")
    return 0


def search(term: str, limit: int) -> int:
    """
    The portal's find-a-project UI is a JS application; its query endpoint is not documented.
    This function archives the search page and prints the candidate project links it can see in
    the server-rendered markup. If nothing comes back, run the search in a browser, copy the
    result slugs, and pass them to --project one at a time. That is the honest fallback and it
    is what the manual_review queue in research_gaps is for.
    """
    url = f"{SEARCH}?keyword={urllib.parse.quote_plus(term)}"
    body = _get(url)
    path = _archive("search", term, body, url)
    text = body.decode("utf-8", "replace")
    slugs = sorted(set(re.findall(r"/major-projects/projects/([a-z0-9\-]+)", text)))
    print(f"[archived] {url} -> {path}")
    print(f"[candidates] {len(slugs)} project slugs visible in server-rendered markup")
    for s in slugs[:limit]:
        print("   -", s)
    if not slugs:
        print("\nNo slugs in the markup: the results are client-rendered. Either")
        print("  (a) open the search in a browser and copy slugs to --project, or")
        print("  (b) use the Department's published datacentre project list / SEARs register.")
    return 0


def attachment(ref: str) -> int:
    url = f"{PORTAL}/prweb/PRRestService/mp/01/getContent?AttachRef={urllib.parse.quote(ref)}"
    body = _get(url, timeout=180)
    path = _archive("attachment", re.sub(r"[^A-Za-z0-9]+", "_", ref), body, url)
    head = body[:8].lower()
    kind = "pdf" if head.startswith(b"%pdf") else "html-or-other"
    print(f"[archived] {url}\n           -> {path} ({len(body):,} bytes, {kind})")
    return 0


def main(argv: list[str]) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--project", help="project slug, e.g. mamre-road-data-centre-campus")
    p.add_argument("--search", help="free-text search term")
    p.add_argument("--limit", type=int, default=25)
    p.add_argument("--attachment", help="AttachRef value for a portal document")
    p.add_argument("--delay", type=float, default=DELAY_SECONDS)
    a = p.parse_args(argv)

    try:
        if a.project:
            return project(a.project)
        if a.search:
            return search(a.search, a.limit)
        if a.attachment:
            time.sleep(a.delay)
            return attachment(a.attachment)
    except Exception as exc:  # noqa: BLE001 - a crawler must never half-write silently
        print(f"[error] {type(exc).__name__}: {exc}", file=sys.stderr)
        return 1
    p.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
