#!/usr/bin/env python3
"""
Draft proposals for stronger gap reasons, for a human to accept or strike.

A derived gap only ever says `unknown` ("not yet researched, or researched without finding a
source"). Some of those gaps are not unknown at all: they are fields that cannot apply to the site
as its own record describes it. A proposed data centre cannot hold a hosting certification or have
energised capacity, and a withdrawn one will never open. Saying "Not yet researched" for those
misleads a reader about how much research is outstanding.

But `not_applicable` is a claim about the world (CLAUDE.md): only a human may record it, with a
source. So this script records nothing. It reads the research database (mode=ro) and writes a list
of proposals, each naming the site, the field, the proposed reason, the rule behind it, and the
source the site's status rests on, which is the evidence the human would cite.

The rules are deliberately few, and each depends only on the site's recorded status:

  hcf_certified      not operating                      certification is of an operating facility
  live_capacity_mw   not operating or being built       nothing is energised
  operational_from   withdrawn, refused or cancelled    it will never open
  target_completion  withdrawn, refused or cancelled    it will never be completed
  target_completion  operating                          it is complete

A proposal is only as good as the status it rests on, so the status source is listed beside each.

Outputs:
  * reports/gap_reason_proposals.csv - one row per proposal
How a human records one: docs/QUALITY.md, "Recording a stronger gap reason".

Run:
    python3 scripts/propose_gap_reasons.py
"""
from __future__ import annotations

import csv
import os
import sqlite3
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB = os.path.join(ROOT, "exports", "australian_data_centre_observatory.db")
OUT = os.path.join(ROOT, "reports", "gap_reason_proposals.csv")

NOT_BUILT = ("rumoured", "pre_lodgement", "lodged", "approved", "withdrawn", "refused", "cancelled")
NOT_OPERATING = NOT_BUILT + ("under_construction",)
ENDED = ("withdrawn", "refused", "cancelled")

# (field, column holding it or None if the site's value is always null, statuses, basis)
RULES = [
    ("hcf_certified", "hcf_certified", NOT_OPERATING,
     "HCF certifies operating facilities; a site that is {status} is not one yet"),
    ("live_capacity_mw", None, NOT_BUILT,
     "live capacity is what is energised; a site that is {status} has none"),
    ("operational_from", "operational_from", ENDED,
     "the site is {status}, so it will not open"),
    ("target_completion", "target_completion", ENDED,
     "the site is {status}, so it will not be completed"),
    ("target_completion", "target_completion", ("operational",),
     "the site is operating; a target completion applies to sites not yet built"),
]


def main() -> int:
    db = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
    db.row_factory = sqlite3.Row
    sites = list(db.execute(
        "select s.*, so.title as src_title, so.credibility as src_grade "
        "from sites s left join sources so on so.id = s.source_id order by s.name, s.id"))

    rows = []
    for s in sites:
        for field, col, statuses, basis in RULES:
            if s["status"] not in statuses:
                continue
            value = s[col] if col else None
            if value not in (None, "", "unknown"):
                continue  # recorded: nothing to explain
            rows.append(dict(
                site_id=s["id"], site=s["name"], status=s["status"], field=field,
                proposed_reason="not_applicable",
                basis=basis.format(status=s["status"].replace("_", " ")),
                status_source_id=s["source_id"] or "",
                status_source=s["src_title"] or "", status_source_grade=s["src_grade"] or "",
                status_fact_status=s["fact_status"] or "",
            ))

    with open(OUT, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]) if rows else ["site_id"])
        w.writeheader()
        w.writerows(rows)
    by_field: dict[str, int] = {}
    for r in rows:
        by_field[r["field"]] = by_field.get(r["field"], 0) + 1
    print(f"{len(rows)} proposals for a human ({', '.join(f'{k} {v}' for k, v in by_field.items())}); "
          f"wrote {os.path.relpath(OUT, ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
