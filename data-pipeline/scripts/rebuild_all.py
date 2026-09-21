#!/usr/bin/env python3
"""
Portable pipeline driver — use this if `make` is not available.

    python3 scripts/rebuild_all.py            # build -> verify -> curate -> load packs -> docs
    python3 scripts/rebuild_all.py --fetch    # also re-download the CER datasets first

Every step is idempotent. The build wipes and recreates the database from the seed, then the
curated verification packs are re-applied, so the committed database is always reproducible from
`schema/ + data/seed_data.py + scripts/curate_*.py + data/packs/ + data/raw/`.

PACK ORDER IS LOAD-BEARING. `rg013_hyperscaler_sites.json` cites SRC_CER_NGERS, which is
registered by `cer_verification.json`. The loader refuses cross-pack source references unless
`--allow-missing-source` is passed, so a pack that depends on an earlier one must be listed
after it and carry that flag.
"""
from __future__ import annotations

import subprocess
import sys
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PY = sys.executable
CER_YEARS = "2019-20,2020-21,2021-22,2022-23,2023-24,2024-25"

# (pack path, extra flags)
PACKS = [
    ("data/packs/cer_verification.json", []),
    ("data/packs/rg013_hyperscaler_sites.json", ["--allow-missing-source"]),
    ("data/packs/rg002_nsw_ssd_register.json", ["--allow-missing-source"]),
    ("data/packs/rg026_consent_conditions.json", ["--allow-missing-source"]),
    ("data/packs/rg015_inquiry_record.json", ["--allow-missing-source"]),
    ("data/packs/rg034_consent_modifications.json", ["--allow-missing-source"]),
    ("data/packs/rg003_vic_qld.json", ["--allow-missing-source"]),
    ("data/packs/rg049_western_downs.json", ["--allow-missing-source"]),
    ("data/packs/rg038_consent_comparison.json", ["--allow-missing-source"]),
    ("data/packs/rg046_guidelines_scope.json", ["--allow-missing-source"]),
    ("data/packs/rg060_consent_matrix.json", ["--allow-missing-source"]),
    ("data/packs/airtrunk_bca_influence.json", ["--allow-missing-source"]),
    ("data/packs/consultants_layer.json", ["--allow-missing-source"]),
    ("data/packs/rg079_determinations.json", ["--allow-missing-source"]),
    ("data/packs/status_updates.json", ["--allow-missing-source"]),
]


def run(*args: str) -> None:
    print(f"\n$ {' '.join(args)}")
    r = subprocess.run(args, cwd=ROOT)
    if r.returncode != 0:
        print(f"step failed with exit {r.returncode}", file=sys.stderr)
        sys.exit(r.returncode)


def main(argv: list[str]) -> int:
    # Fail fast if a pack or curation script is wired into only one of the two drivers.
    run(PY, "scripts/check_packs.py")
    # Offline parser fixtures for the AusTender scraper. Mirrors the Makefile's check-austender:
    # a check only one driver runs is the drift check_packs.py exists to catch.
    run(PY, "scrapers/ingest_austender.py", "--selftest")
    # Planted-topic recovery test for the patent topic model. Same reasoning: both drivers or
    # neither. Does not touch the database - analyse_patents.py only ever writes a report.
    run(PY, "scripts/analyse_patents.py", "--selftest")

    if "--fetch" in argv:
        run(PY, "scrapers/ingest_cer.py", "--check")
        run(PY, "scrapers/ingest_cer.py", "--years", CER_YEARS)
        run(PY, "scrapers/ingest_cer.py", "--registers")
        # AusTender is NOT in --fetch: it has never been run against the live site, so its first
        # run is a human review step, not part of an unattended rebuild. See `make fetch-austender`.

    run(PY, "scripts/build_db.py")
    run(PY, "scripts/analyse_cer.py")
    run(PY, "scripts/curate_rg013.py")
    run(PY, "scripts/curate_rg002.py")
    run(PY, "scripts/curate_rg026.py")
    run(PY, "scripts/curate_rg015.py")
    run(PY, "scripts/curate_rg034.py")
    run(PY, "scripts/curate_rg003.py")
    run(PY, "scripts/curate_rg049.py")
    run(PY, "scripts/curate_rg038.py")
    run(PY, "scripts/curate_rg046.py")
    run(PY, "scripts/curate_rg060.py")
    run(PY, "scripts/curate_rg079.py")
    run(PY, "scripts/curate_airtrunk_bca.py")
    run(PY, "scripts/curate_consultants.py")
    run(PY, "scripts/curate_status.py")
    for pack, flags in PACKS:
        run(PY, "scripts/load_pack.py", pack, *flags)
    run(PY, "scripts/extraction_audit.py")
    run(PY, "scripts/gen_dictionary.py")
    # CSV export runs LAST and verifies itself. build_db.py also writes CSVs, but it
    # runs before the packs load, so those files hold seed rows only. This is the
    # authoritative export; it fails the build if any CSV diverges from the database.
    run(PY, "scripts/export_csv.py")
    # Post-load documentation: build_db.py wrote build_report.md and viewer/db.json at SEED
    # stage; finalize regenerates both from the loaded database. Must run after every pack.
    run(PY, "scripts/finalize_docs.py")
    run(PY, "scripts/query.py", "unverified")
    print("\npipeline complete.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
