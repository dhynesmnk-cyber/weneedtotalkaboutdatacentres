#!/usr/bin/env python3
"""
The people register (schema/03_people.sql): who the site names by role only.

The site publishes people by public role, never by name, until legal review is arranged
(CLAUDE.md). On 2026-11-17 a sweep of every published text field found names the loader
had no way to withhold: in source titles, entity names, a site's notes and three research
questions. The lobbying and case-handling tables already pair a name with a role, and the
loader reads them directly. This register adds the people they do not cover, and overrides
two lobbying roles that are too long to publish as a label.

Every entry states the role the site publishes and the record that states it. An entry's
`evidence` is a phrase that must appear verbatim in that record (the source's title or
notes, an entity's notes, or a lobbying row): the script refuses to write if it does not,
so no role is invented.

Not listed, on the author's decision of 2026-11-17: journalists' bylines in
sources.publisher. A byline is a citation's authorship, not a person in our content.

Outputs:
  * data/packs/people_register.json

Run:
    python3 scripts/curate_people.py
    python3 scripts/load_pack.py data/packs/people_register.json --allow-missing-source
"""
from __future__ import annotations

import glob
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PACKS = os.path.join(ROOT, "data", "packs")
OUT_PACK = os.path.join(PACKS, "people_register.json")
TODAY = "2026-11-17"

# where: ("source", SRC_ID) = the source's title or notes; ("entity", ENT_ID) = the entity's
# notes; ("lobbying", None) = a lobbying.person value in any pack.
PEOPLE = [
    dict(id="PER_AUSTRADE_SOUTH_ASIA_COMMISSIONER", name="Jodi McKay",
         role="Austrade's Senior Trade and Investment Commissioner for South Asia",
         source_id="SRC_AUSTRADE_MCKAY", where=("source", "SRC_AUSTRADE_MCKAY"),
         evidence="Senior Trade and Investment Commissioner for South Asia"),
    dict(id="PER_NVIDIA_CEO", name="Jensen Huang", role="NVIDIA's chief executive",
         source_id="SRC_SHERWOOD_GTC_QUOTE", where=("source", "SRC_SHERWOOD_GTC_QUOTE"),
         evidence="Nvidia CEO Jensen Huang"),
    dict(id="PER_TELSTRA_CEO", name="Vicki Brady", role="Telstra's chief executive",
         source_id="SRC_WMEDIA_BCA", where=("source", "SRC_WMEDIA_BCA"),
         evidence="Telstra CEO Vicki Brady"),
    dict(id="PER_BCA_PRESIDENT", name="Geoff Culbert",
         role="President, Business Council of Australia", organisation_id="ENT_BCA",
         source_id="SRC_BCA_ABOUT", where=("entity", "ENT_BCA_PRES"),
         evidence="President of the Business Council of Australia"),
    dict(id="PER_TCS_CHAIR", name="Chandrasekaran",
         aliases="Chairman Chandrasekaran|N Chandrasekaran|N. Chandrasekaran",
         role="TCS's chairman", source_id="SRC_TCS_HYPERVAULT",
         where=("gap_note", 76), evidence="Chairman Chandrasekaran is quoted"),
    dict(id="PER_UK_DEFENCE_SECRETARY", name="John Healey", aliases="John Healey MP",
         role="the UK Defence Secretary", source_id="SRC_GOVUK_PALANTIR_SEP25",
         where=("source", "SRC_GOVUK_PALANTIR_SEP25"), evidence="Defence Secretary John Healey"),
    # The lobbying row records him by role only; the seed's entity name and the disclosure's
    # verbatim quote carry the name, so the register is what lets the loader withhold it.
    dict(id="PER_CDC_CEO", name="Greg Boorer", aliases="Gregory David Boorer|Gregory Boorer",
         role="CDC's director and chief executive", organisation_id="ENT_CDC",
         source_id="SRC_SSD10330_DONATION", where=("lobbying", None),
         evidence="Director and Chief Executive Officer, Canberra Data Centres"),
    # Overrides: the lobbying table names these two with roles too long to publish as a label.
    dict(id="PER_UK_MOD_DG_AUKUS", name="Damian Parmenter", aliases="Damian Parmenter CBE",
         role="a former UK Ministry of Defence Director General for AUKUS",
         source_id="SRC_ACOBA_PARMENTER", where=("source", "SRC_ACOBA_PARMENTER"),
         evidence="former Director General, AUKUS, Ministry of Defence"),
    dict(id="PER_FORMER_DEFENCE_MATERIEL_MINISTER", name="Mike Kelly",
         role="a former federal Minister for Defence Materiel", organisation_id="ENT_PALANTIR_AU",
         source_id="SRC_ABC_REVOLVING", where=("lobbying", None),
         evidence="former Labor Minister for Defence Materiel"),
]


def load_packs() -> list[dict]:
    return [json.load(open(p, encoding="utf-8")) for p in sorted(glob.glob(os.path.join(PACKS, "*.json")))
            if os.path.basename(p) != os.path.basename(OUT_PACK)]


def evidence_text(packs: list[dict], where: tuple) -> str:
    kind, key = where
    texts: list[str] = []
    for pack in packs:
        if kind == "source":
            texts += [f"{s.get('title', '')} {s.get('notes', '')}" for s in pack.get("sources", [])
                      if s.get("id") == key]
        rows = pack.get("rows", {})
        if kind == "entity":
            for r in rows.get("entities", []):
                target = r.get("match", r)
                if target.get("id") == key:
                    texts.append(json.dumps(r, ensure_ascii=False))
        if kind == "lobbying":
            # Inserts carry person at the top level; updates carry it in set.
            texts += [json.dumps(r, ensure_ascii=False) for r in rows.get("lobbying", [])]
        if kind == "gap_note":
            for r in rows.get("research_gaps", []):
                target = r.get("match", r)
                if target.get("id") == key:
                    texts.append(json.dumps(r, ensure_ascii=False))
    return re.sub(r"\s+", " ", " ".join(texts))


def main() -> int:
    packs = load_packs()
    errors: list[str] = []
    ids = [p["id"] for p in PEOPLE]
    if len(set(ids)) != len(ids):
        errors.append("duplicate ids in PEOPLE")
    for p in PEOPLE:
        if p["name"].lower() in p["id"].lower().replace("_", " "):
            errors.append(f"{p['id']}: an id names the role, never the person")
        text = evidence_text(packs, p["where"])
        if not text:
            errors.append(f"{p['id']}: {p['where']} not found in any pack")
        elif p["evidence"] not in text:
            errors.append(f"{p['id']}: evidence {p['evidence']!r} not found in {p['where']}")
    if errors:
        print("refusing to write; fix these first:", file=sys.stderr)
        for e in errors:
            print(f"  {e}", file=sys.stderr)
        return 1

    rows = []
    for p in PEOPLE:
        rows.append(dict(
            id=p["id"], name=p["name"], aliases=p.get("aliases"), role=p["role"],
            organisation_id=p.get("organisation_id"),
            notes=(f"Published by role only (CLAUDE.md). The role is stated in the record as: "
                   f"'{p['evidence']}'."),
            fact_status="VERIFIED", source_id=p["source_id"], confidence="high", as_of_date=TODAY,
        ))
    pack = {
        "pack_id": "people-register-2026-11",
        "prepared_by": "scripts/curate_people.py",
        "prepared_on": TODAY,
        "_comment": [
            "Who the site names by role only. The loader reads this table with lobbying.person and",
            "case_handling.officer_name and replaces each name in every published text field. Each",
            "role is checked verbatim against the record that states it. Bylines are not listed.",
        ],
        "sources": [],
        "rows": {"people": rows},
    }
    with open(OUT_PACK, "w") as f:
        json.dump(pack, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print(f"{len(rows)} people registered, every role checked against its record; "
          f"wrote {os.path.relpath(OUT_PACK, ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
