#!/usr/bin/env python3
"""
Pipeline consistency check: every curated pack and every curation script must be wired
into BOTH build drivers (scripts/rebuild_all.py and the Makefile).

This exists because the pipeline has drifted twice already: rg060_consent_conditions.json was
generated but wired into neither driver (three curated metrics silently never reached the
database), and curate_consultants.py was missing from the Makefile's verify target while
present in rebuild_all.py. A pack or script that only one driver knows about is a pack that
silently stops being regenerated - or silently stops being loaded.

Checks:
  1. every data/packs/*.json (excluding EXAMPLE_pack.json and retired/) is listed in
     rebuild_all.py's PACKS and in the Makefile's PACKS / PACKS_ALLOW_MISSING;
  2. every scripts/curate_*.py is run by rebuild_all.py and by the Makefile's verify recipe;
  3. both drivers list the packs in the SAME relative order (load order is load-bearing for
     cross-pack source references).

Exit 1 on any drift. Run: python3 scripts/check_packs.py
"""
from __future__ import annotations

import glob
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXCLUDED_PACKS = {"EXAMPLE_pack.json"}


def rebuild_packs() -> list[str]:
    src = open(os.path.join(ROOT, "scripts", "rebuild_all.py"), encoding="utf-8").read()
    return re.findall(r'\("(data/packs/[^"]+\.json)"', src)


def rebuild_curates() -> list[str]:
    src = open(os.path.join(ROOT, "scripts", "rebuild_all.py"), encoding="utf-8").read()
    return re.findall(r'run\(PY, "scripts/(curate_[^"]+\.py)"\)', src)


def makefile_packs() -> list[str]:
    src = open(os.path.join(ROOT, "Makefile"), encoding="utf-8").read()
    out = []
    for var in ("PACKS", "PACKS_ALLOW_MISSING"):
        m = re.search(rf"^{var} = (.*?)(?=\n\S|\Z)", src, re.S | re.M)
        if not m:
            continue
        out += re.findall(r"(data/packs/[^\s\\]+\.json)", m.group(1))
    return out


def makefile_curates() -> list[str]:
    src = open(os.path.join(ROOT, "Makefile"), encoding="utf-8").read()
    return re.findall(r"\$\(PY\) scripts/(curate_[^ \t\n]+\.py)", src)


def main() -> int:
    problems: list[str] = []
    on_disk = sorted(os.path.basename(p) for p in glob.glob(os.path.join(ROOT, "data", "packs", "*.json"))
                     if os.path.basename(p) not in EXCLUDED_PACKS)
    rp, mp = rebuild_packs(), makefile_packs()
    rp_b = [os.path.basename(p) for p in rp]
    mp_b = [os.path.basename(p) for p in mp]

    for name in on_disk:
        if name not in rp_b:
            problems.append(f"pack data/packs/{name} is NOT wired into scripts/rebuild_all.py PACKS")
        if name not in mp_b:
            problems.append(f"pack data/packs/{name} is NOT wired into the Makefile pack lists")
    for name in rp_b:
        if name not in on_disk:
            problems.append(f"rebuild_all.py lists data/packs/{name} which is not on disk")
    for name in mp_b:
        if name not in on_disk:
            problems.append(f"Makefile lists data/packs/{name} which is not on disk")

    # relative order of the common packs must agree (load order carries source dependencies)
    common_r = [n for n in rp_b if n in mp_b]
    common_m = [n for n in mp_b if n in rp_b]
    if common_r != common_m:
        problems.append("pack ORDER differs between rebuild_all.py and the Makefile: "
                        f"{common_r} vs {common_m}")

    curates = sorted(os.path.basename(p) for p in glob.glob(os.path.join(ROOT, "scripts", "curate_*.py")))
    rc, mc = rebuild_curates(), makefile_curates()
    for name in curates:
        if name not in rc:
            problems.append(f"scripts/{name} is NOT run by scripts/rebuild_all.py")
        if name not in mc:
            problems.append(f"scripts/{name} is NOT run by the Makefile verify target")

    if problems:
        print("PACK/PIPELINE CONSISTENCY: FAIL")
        for p in problems:
            print("  -", p)
        return 1
    print(f"PACK/PIPELINE CONSISTENCY: OK - {len(on_disk)} packs wired into both drivers in the "
          f"same order; {len(curates)} curation scripts run by both.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
