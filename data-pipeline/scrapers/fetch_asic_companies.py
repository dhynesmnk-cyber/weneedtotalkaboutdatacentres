#!/usr/bin/env python3
"""
Extract the companies behind NSW data centre applications from ASIC's Company Dataset.

ASIC publishes its whole company register on data.gov.au as the Company Dataset (CC BY 3.0 AU):
every company's name, ACN, type, status, date of registration and, for a renamed company, each
former name with the date the current one took effect. It holds no directors, shareholders or
addresses, so nothing personal is extracted. This downloads the monthly ZIP (about 80 MB) to a
temporary path, keeps only the rows whose current or former name is in NAMES or starts with one
of PREFIXES, and commits that extract with a manifest. The ZIP itself is not kept.

Archive (data/raw/asic/):
  company_dataset_<yyyymm>_extract.csv            the matching rows, as ASIC publishes them
  company_dataset_<yyyymm>_extract.csv.meta.json  dataset, resource url, ZIP sha256, filter, counts

Usage:
    python3 scrapers/fetch_asic_companies.py                  # download and extract
    python3 scrapers/fetch_asic_companies.py --zip PATH.zip   # extract from a ZIP already fetched
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import os
import re
import sys
import tempfile
import urllib.request
import zipfile
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "data", "raw", "asic")
PACKAGE = "https://data.gov.au/data/api/3/action/package_show?id=asic-companies"
UA = ("ADCO-research/1.0 (Australian Data Centre Observatory; open public-interest research "
      "database; single-threaded polite crawler; stop on request)")

# Applicants on NSW data centre consents and applications, the vehicles around them, and the
# companies their title documents name, spelt as the register spells them (Microsoft's company
# uses the US 'Datacenter'). Matched against current and former names.
NAMES = [
    "ADW Johnson Pty Ltd", "Amazon Australia Company Pty Ltd", "Amazon Commercial Services Pty Ltd",
    "Amazon Corporate Services Pty Ltd", "Arup Australia Pty Ltd", "Arup Pty Ltd",
    "CDC Data Centres Pty Ltd", "Cundall Johnston and Partners Pty Ltd", "Dicker Data Limited",
    "Goodman Property Services (Aust) Pty Ltd", "Greenbox Architecture Pty Ltd",
    "GreenSquareDC Pty Limited", "IFM Real Estate Fiduciary Pty Ltd", "ISPT Pty Ltd",
    "Lehr Consultants International (Australia) Pty Ltd", "Macquarie Data Centres Pty Ltd",
    "Microsoft Datacenter (Australia) Pty Limited", "NBDC Pty Ltd", "NEXTDC Limited",
    "Plan Project Management Pty Ltd", "Project Garden 1 Pty Ltd",
    "STACK Infrastructure Australia Pty Ltd", "Stockland Development Pty Limited",
    "Stockland Trust Management Limited", "WDDP Pty Ltd",
]
PREFIXES = ["AirTrunk", "CKTSME", "EMKC", "Equinix Hyperscale", "HDI SYD", "KNBDC", "NineZero", "Zerra"]


def norm(s: str) -> str:
    s = s.upper().replace("LIMITED", "LTD").replace("PROPRIETARY", "PTY")
    return re.sub(r"\s+", " ", re.sub(r"[^A-Z0-9 ]", " ", s)).strip()


def resource() -> tuple[str, str]:
    """The current ZIP's url and the dataset's last-modified time, from data.gov.au's catalogue."""
    req = urllib.request.Request(PACKAGE, headers={"User-Agent": UA})
    pkg = json.load(urllib.request.urlopen(req, timeout=60))["result"]
    zips = [r for r in pkg["resources"] if (r.get("format") or "").upper() == "ZIP" and "Current" in r["name"]]
    if len(zips) != 1:
        raise SystemExit(f"expected one current ZIP resource, found {len(zips)}")
    return zips[0]["url"], pkg["metadata_modified"]


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--zip", help="a ZIP already downloaded from the url the catalogue gives")
    a = ap.parse_args(argv)

    url, modified = resource()
    path = a.zip
    if not path:
        path = os.path.join(tempfile.mkdtemp(), "company.zip")
        urllib.request.urlretrieve(url, path)  # noqa: S310 - the catalogue's own https url
    digest = hashlib.sha256(open(path, "rb").read()).hexdigest()

    names = {norm(n) for n in NAMES}
    prefixes = [norm(p) for p in PREFIXES]
    z = zipfile.ZipFile(path)
    (member,) = [i for i in z.infolist() if i.filename.upper().endswith(".CSV")]
    yyyymm = re.search(r"(\d{6})", member.filename).group(1)
    rows, header, total = [], None, 0
    with z.open(member) as fh:
        reader = csv.reader(io.TextIOWrapper(fh, encoding="utf-8-sig", newline=""), delimiter="\t")
        header = next(reader)
        for row in reader:
            total += 1
            if len(row) < len(header):
                continue
            seen = {norm(row[0]), norm(row[header.index("Current Name")])}
            if seen & names or any(n.startswith(p) for n in seen for p in prefixes):
                rows.append(row)

    os.makedirs(OUT, exist_ok=True)
    out = os.path.join(OUT, f"company_dataset_{yyyymm}_extract.csv")
    rows.sort(key=lambda r: (r[header.index("ACN")], r[0]))
    with open(out, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(header)
        w.writerows(rows)
    missing = sorted(n for n in names if not any(norm(r[0]) == n or norm(r[header.index("Current Name")]) == n
                                                 for r in rows))
    json.dump(dict(
        dataset="ASIC - Company Dataset (data.gov.au, package asic-companies)", publisher="ASIC",
        licence="Creative Commons Attribution 3.0 Australia", resource_url=url, dataset_modified=modified,
        member=member.filename, zip_sha256=digest, fetched_utc=datetime.now(timezone.utc).isoformat(timespec="seconds"),
        user_agent=UA, rows_in_dataset=total, rows_extracted=len(rows),
        extract_sha256=hashlib.sha256(open(out, "rb").read()).hexdigest(),
        filter=dict(names=NAMES, prefixes=PREFIXES, matched_on="current or former name, case and punctuation folded"),
        names_not_found=missing,
    ), open(out + ".meta.json", "w"), indent=1)
    print(f"{len(rows)} of {total} rows -> {os.path.relpath(out, ROOT)}; not found: {missing or 'none'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
