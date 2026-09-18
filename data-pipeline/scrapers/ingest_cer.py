#!/usr/bin/env python3
"""
ADCO ingestion: Clean Energy Regulator datasets (RG-009).

The CER moved from cleanenergyregulator.gov.au to cer.gov.au. Every dataset below has a
"Raw data in CSV format" sibling link whose slug ends in `-0`; the sibling without the suffix
is the XLSX. That pattern is stable across all years tested on 2026-09-18.

Datasets and what each one proves:

  1. corporate        NGER corporate emissions and energy, per controlling corporation, per year.
                      Scope 1, scope 2 (location-based) and net energy consumed. This is the
                      authoritative test of whether an operator's emissions are falling while it
                      advertises "100% renewable". Published for 2019-20 .. 2024-25.
  2. market_s2        Market-based scope 2 emissions by controlling corporation. Only published
                      for 2023-24 and 2024-25. This is the ONLY place a voluntary renewable
                      procurement claim becomes visible in statutory data: the gap between
                      location-based and market-based scope 2 is the claim, in tonnes.
  3. transfer         Reporting transfer certificate holders (small; context only).
  4. shortfall        LGC certificate shortfall register: liable entity, assessment year, LGC
                      liability, LGCs accepted for surrender, remaining shortfall, shortfall
                      charge. Proves who under-surrendered. Note: data centres are NOT liable
                      entities - retailers are - so absence from this register is itself a
                      finding about what "100% renewable" can and cannot mean.
  5. lret             Large-scale renewable energy supply data: accredited power stations,
                      committed projects, probable projects. The pipeline's FID status is how
                      additionality is tested (NSW Principle 3 requires projects that had NOT
                      reached FID at the time of contracting).
  6. safeguard        Safeguard Mechanism baselines and covered emissions per facility.

Usage:
    python3 scrapers/ingest_cer.py --check
    python3 scrapers/ingest_cer.py --years 2019-20,2020-21,2021-22,2022-23,2023-24,2024-25
    python3 scrapers/ingest_cer.py --registers
    python3 scrapers/ingest_cer.py --url KEY=URL          # ad hoc fetch

Then:  python3 scripts/analyse_cer.py                    # the actual verification
"""
from __future__ import annotations

import argparse
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
RAW = os.path.join(ROOT, "data", "raw", "cer")
BASE = "https://cer.gov.au"
DELAY = 2.0
UA = ("ADCO-research/1.0 (Australian Data Centre Observatory; open public-interest research "
      "database; single-threaded polite crawler; stop on request)")

CORP_YEARS = ["2019-20", "2020-21", "2021-22", "2022-23", "2023-24", "2024-25"]
MARKET_S2_YEARS = ["2023-24", "2024-25"]  # not published before 2023-24

DOC_SLUGS = {
    ("corporate", "{y}"): "greenhouse-and-energy-information-registered-corporation-{y}-0",
    ("transfer", "{y}"): "greenhouse-and-energy-information-reporting-transfer-certificate-holder-{y}-0",
    ("market_s2", "{y}"): "market-based-scope-2-emissions-information-registered-corporation-{y}-0",
}

REGISTERS = {
    "shortfall": "lgc-certificate-shortfall-register-0",
    "shortfall_stc": "stc-certificate-shortfall-register-0",
    "lret_lgc_accredited": "total-lgcs-and-capacity-accredited-power-stations-2026-0",
}

LANDING_PAGES = {
    "corporate_index": f"{BASE}/markets/reports-and-data/nger-reporting-data-and-registers",
    "corporate_2024_25": f"{BASE}/markets/reports-and-data/nger-reporting-data-and-registers/"
                         f"corporate-emissions-and-energy-data-2024-25",
    "highlights_2024_25": f"{BASE}/markets/reports-and-data/nger-reporting-data-and-registers/"
                          f"2024-25-published-data-highlights",
    "lret_index": f"{BASE}/markets/reports-and-data/large-scale-renewable-energy-data",
    "shortfall_index": f"{BASE}/markets/reports-and-data/certificate-shortfall-register",
    "safeguard_index": f"{BASE}/markets/reports-and-data/safeguard-data/2024-25-baselines-and-emissions-data",
}


def fetch(url: str, timeout: int = 120) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read()


def sniff_ext(body: bytes) -> str:
    head = body[:256].lower()
    if head.startswith(b"%pdf"):
        return ".pdf"
    if head.startswith(b"pk\x03\x04"):
        return ".xlsx"
    if head.startswith(b"\xd0\xcf\x11\xe0"):
        return ".xls"
    if b"," in body[:512] and (b"\r\n" in body[:2048] or b"\n" in body[:2048]):
        return ".csv"
    if head.lstrip().startswith(b"<"):
        return ".html"
    return ".bin"


def save(kind: str, name: str, body: bytes, url: str) -> str:
    dest_dir = os.path.join(RAW, kind)
    os.makedirs(dest_dir, exist_ok=True)
    ext = sniff_ext(body)
    safe = re.sub(r"[^A-Za-z0-9_.-]+", "_", name)[:110]
    path = os.path.join(dest_dir, safe + ext)
    with open(path, "wb") as fh:
        fh.write(body)
    with open(path + ".meta.json", "w", encoding="utf-8") as fh:
        json.dump({"url": url, "fetched_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                   "sha256": hashlib.sha256(body).hexdigest(), "bytes": len(body),
                   "user_agent": UA, "kind": kind}, fh, indent=2)
    print(f"[saved] {kind}/{safe}{ext}  ({len(body):,} bytes)")
    return path


def resolve_lret_links() -> list[tuple[str, str]]:
    """
    The LRET supply tables (approved / committed / probable power stations) change slug each
    month, so discover them from the live page rather than hard-coding.
    """
    try:
        html = fetch(LANDING_PAGES["lret_index"]).decode("utf-8", "replace")
    except (urllib.error.URLError, OSError) as exc:
        print(f"[warn] could not read LRET index: {exc}", file=sys.stderr)
        return []
    slugs = sorted(set(re.findall(r"/document/([a-z0-9\-]+)", html)))
    want = [s for s in slugs if re.search(r"(approved|committed|probable|accredited|lgc)", s)
            and s.endswith("-0")]
    return [("lret", s) for s in want]


def resolve_safeguard_links() -> list[tuple[str, str]]:
    try:
        html = fetch(LANDING_PAGES["safeguard_index"]).decode("utf-8", "replace")
    except (urllib.error.URLError, OSError) as exc:
        print(f"[warn] could not read Safeguard index: {exc}", file=sys.stderr)
        return []
    slugs = sorted(set(re.findall(r"/document/([a-z0-9\-]+)", html)))
    return [("safeguard", s) for s in slugs if s.endswith("-0")]


def get_doc(kind: str, slug: str) -> None:
    url = f"{BASE}/document/{slug}"
    try:
        save(kind, slug, fetch(url), url)
    except urllib.error.HTTPError as exc:
        print(f"[miss] {kind}/{slug}: HTTP {exc.code}", file=sys.stderr)
    except (urllib.error.URLError, OSError) as exc:
        print(f"[miss] {kind}/{slug}: {exc}", file=sys.stderr)
    time.sleep(DELAY)


def do_years(years: list[str]) -> int:
    for y in years:
        get_doc("corporate", DOC_SLUGS[("corporate", "{y}")].format(y=y))
        get_doc("transfer", DOC_SLUGS[("transfer", "{y}")].format(y=y))
        if y in MARKET_S2_YEARS:
            get_doc("market_s2", DOC_SLUGS[("market_s2", "{y}")].format(y=y))
    return 0


def do_registers() -> int:
    for kind, slug in REGISTERS.items():
        get_doc(kind.split("_")[0], slug)
    for kind, slug in resolve_lret_links():
        get_doc(kind, slug)
    for kind, slug in resolve_safeguard_links():
        get_doc(kind, slug)
    return 0


def check() -> int:
    ok = True
    for name, url in LANDING_PAGES.items():
        try:
            body = fetch(url)
            print(f"[reachable] {name}: {url} ({len(body):,} bytes)")
        except Exception as exc:  # noqa: BLE001
            ok = False
            print(f"[FAILED]    {name}: {exc}")
        time.sleep(1.0)
    print(f"\nCSV slugs resolve under {BASE}/document/<slug> where <slug> ends in '-0'.")
    print(f"Corporate years available: {', '.join(CORP_YEARS)}")
    print(f"Market-based scope 2 years: {', '.join(MARKET_S2_YEARS)} (not published earlier)")
    return 0 if ok else 1


def main(argv: list[str]) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--check", action="store_true")
    p.add_argument("--years", help="comma-separated NGER years, e.g. 2019-20,2024-25")
    p.add_argument("--registers", action="store_true", help="fetch shortfall, LRET and Safeguard datasets")
    p.add_argument("--url", action="append", default=[], metavar="KIND=URL")
    a = p.parse_args(argv)
    os.makedirs(RAW, exist_ok=True)

    if a.url:
        for spec in a.url:
            kind, _, url = spec.partition("=")
            if not url:
                print(f"bad --url {spec!r}", file=sys.stderr)
                return 2
            save(kind, os.path.basename(urllib.parse.urlparse(url).path) or "dataset", fetch(url), url)
        return 0
    if a.check:
        return check()
    if a.years:
        return do_years([y.strip() for y in a.years.split(",") if y.strip()])
    if a.registers:
        return do_registers()
    p.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
