#!/usr/bin/env python3
"""
The author's decisions on research batch 8, and the downloads the author brought back (2026-11-18).

The author's answers of 2026-11-18 ("merge and load, 1 yes 2 yes 3 yes"), on the proposals in batch 8:
  1. RG-076 and RG-090 close as resolved-negative.
  2. RG-013's remainder (AWS and Google) and RG-102 (Macquarie Park's end user) close as not
     retrievable at zero spend (wont_fix).
  3. Three modification rows are reclassified from the reports read in batch 8's second pass.

The downloads (docs/requests/DOWNLOADS.md), each archived under data/raw with a manifest:
  * #30 Budget Paper No. 1, 2026-27 (RG-007): its tax expenditure statement never mentions data
    centres; the only fiscal mention is Sydney Water's "full cost recovery" servicing strategy.
  * #31 AEMO's NEM Registration and Exemption List (RG-018): a Firmus company is registered to
    provide ancillary services as a load; another ran a 20 MW ancillary service load at St Leonards,
    Tasmania, until 2023; CDC is an intending participant; NEXTDC's backup generators are exempt,
    with zero export.
  * #32 The NT Government's release of 22 July 2026 (RG-027): Beetaloo Digital's exclusive
    commitment over 185 ha at Weddell, and a second proposal it names. New site rows are PROPOSED.
  * #34, part (RG-069): the NSW Electoral Commission's stakeholder register (no amounts) lists one
    data centre company as a major political donor; the amounts come from the AEC's free bulk
    returns, fetched by the crawler.

Outputs:
  * data/packs/batch8_decisions.json

Run:
    python3 scripts/curate_batch8_decisions.py
    python3 scripts/load_pack.py data/packs/batch8_decisions.json --allow-missing-source
"""
from __future__ import annotations

import csv
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(ROOT, "data", "raw")
OUT_PACK = os.path.join(ROOT, "data", "packs", "batch8_decisions.json")
THIS_PACK = "data/packs/batch8_decisions.json"
TODAY = "2026-11-18"
DECIDED = f" DECIDED BY THE AUTHOR {TODAY} (research batch 8):"
TAG = f" UPDATED {TODAY} (research batch 8, the author's downloads):"

SRC_BP1 = "SRC_NSW_BP1_2026_27"
SRC_AEMO = "SRC_AEMO_NEM_REG_LIST_202611"
SRC_NT = "SRC_NTGOV_BEETALOO_20260722"
SRC_NSWEC = "SRC_NSWEC_STAKEHOLDERS_202611"
SRC_AEC = "SRC_AEC_TRANSPARENCY_2025"

TEXTS = {
    SRC_BP1: "registers/nsw_budget/2026-27_Budget_Paper_No.01_-_Budget_Statement.md",
    SRC_AEMO: "registers/aemo/nem_registration_list_data_centre_rows.csv",
    SRC_NT: "operators/ntgov/beetaloo-digital-weddell-22-july-2026.md",
    SRC_NSWEC: "registers/nsw_electoral_disclosures/stakeholders_data_centre_rows.csv",
    SRC_AEC: "registers/aec_transparency/data_centre_companies_2020-21_to_2024-25.csv",
}

QUOTES = {
    SRC_BP1: {
        "itemised": "Tax expenditure measures and concessions that have an impact over $1 million are itemised in a table.",
        "total": ("In 2026-27, total tax expenditures and concessions provided by the NSW Government are estimated at "
                  "$16.8 billion"),
        "sydney_water": ("Sydney Water’s strategy for servicing data centres focuses on enabling timely and reliable "
                         "connections to support economic growth while protecting broader customer outcomes."),
        "cost_recovery": "This approach is supported by principles of full cost recovery",
        "investment": "Significant drivers of this improvement included investment in data centres",
    },
    SRC_AEMO: {
        "firmus": ("Registered Participants=Firmus Infrastructure Pty Ltd | ABN / CAN=24 655 510 151 | Demand Response "
                   "Service Provider - Ancillary Service Load=1"),
        "st_leonards": ("Registered Participant=Firmus Grid Pty Ltd | ABN=31 638 040 534 | Category of Participant=Market "
                        "Customer - Scheduled Load | Facility=St Leonards Facility | Units=1 | Region=TAS1 | Type=Ancillary "
                        "Service Load | Capacity=20 | Time=2023-02-07 00:00:00"),
        "cdc": "Registered Participants=CDC Data Centres Pty Ltd | ABN / CAN=125 710 394 | Intending=1",
        "nextdc": "Company=NEXTDC Limited | ABN=35 143 582 521 | System=M1 - Melbourne, Unit 1",
        "zero": "The combined export of the generating units or generating systems at the parent connection point is expected to be zero MWh.",
    },
    SRC_NT: {
        "grant": ("The Finocchiaro CLP Government has granted Beetaloo Digital an exclusive commitment over 185 hectares of "
                  "land at Weddell, about 30km from Darwin."),
        "power": ("Beetaloo Digital is proposing a hyperscale computing infrastructure project for AI, cloud computing and "
                  "large-scale data processing, to be powered by up to 2GW of on-site gas-fired power generation."),
        "campuses": "possibly two hyper-scale AI data centre campuses at Weddell",
        "not_to_deal": ("Under the \"not to deal\" arrangement, the Government commits to give Beetaloo Digital the exclusive "
                        "right to make plans for the 185ha site while the company progresses the project and investigates "
                        "its feasibility."),
        "ares": ("Energy North’s Project Ares, a one-gigawatt project proposed for Murranji station in the Barkly "
                 "region"),
        "dozen": "As many as a dozen data centre developers are eyeing the region",
    },
    SRC_NSWEC: {
        "aws": "AMAZON WEB SERVICES AUSTRALIA PTY LTD,Major Political Donor - Entity",
    },
    SRC_AEC: {
        "cdc_2425": ("recipient return (Detailed Receipts),2024-25,CDC Data Centres,CDC Data centres,Australian Labor Party "
                     "(ALP),Other Receipt,,10000"),
        "airtrunk": ("recipient return (Detailed Receipts),2024-25,AirTrunk,AirTrunk Operating Pty Ltd,Business Council of "
                     "Australia,Other Receipt,,104500"),
    },
}

NEW_SOURCES = [
    (SRC_BP1, "NSW Budget 2026-27, Budget Paper No. 1: Budget Statement", "NSW Treasury", "2026-06-01",
     "primary_government", "A",
     "Appendix C is the State's statement of revenue forgone through tax expenditures and concessions ($16.8 billion "
     "in 2026-27), itemising those over $1 million: it never mentions data centres (checked by the curation script). "
     "Data centres appear only as a driver of business investment and in Sydney Water's servicing strategy, 'supported "
     "by principles of full cost recovery'. Saved by the author as Markdown from the published PDF (download #30); "
     "the crawler is barred by robots.txt. RG-007."),
    (SRC_AEMO, "AEMO NEM Registration and Exemption List (as downloaded 2026-11-18): rows naming data centre operators",
     "Australian Energy Market Operator", None, "primary_regulator", "A",
     "The extract of the list's rows that name data centre operators, from the spreadsheet the author downloaded "
     "(download #31; AEMO's site answered the crawler with HTTP 403). The spreadsheet is not committed; its SHA-256 "
     "is in the extract's manifest. RG-018."),
    (SRC_NT, "Finocchiaro CLP Government supporting proposed Beetaloo Digital Pty Ltd integrated energy and data centre "
             "development (NT Government media release, 22 July 2026)",
     "Northern Territory Government", "2026-07-22", "primary_government", "A",
     "The NT Government grants Beetaloo Digital a 'not to deal' exclusive commitment over 185 ha at Weddell, about 30 km "
     "from Darwin, for possibly two hyperscale AI campuses powered by up to 2 GW of on-site gas generation; the "
     "company's own claims ($40 billion, 5,000 construction jobs) are quoted, not stored. Names a second proposal, "
     "Energy North's Project Ares (1 GW, Murranji station, Barkly). Saved by the author (download #32); the media "
     "advisers' names and mobile numbers are redacted from the archived copy. RG-027."),
    (SRC_NSWEC, "NSW Electoral Commission stakeholder register (export, 2026-11-18): data centre entities among major "
                "political donors",
     "NSW Electoral Commission", None, "primary_regulator", "A",
     "The author's export of the register (download #34, part) lists 2,368 stakeholders and gives no amounts. One data "
     "centre company is among the 276 major political donor entities: Amazon Web Services Australia. Only matching "
     "entity rows are committed; the full register names private individuals. RG-069."),
    (SRC_AEC, "AEC Transparency Register, annual returns (bulk download): rows naming data centre companies, 2020-21 to "
              "2024-25",
     "Australian Electoral Commission", None, "primary_regulator", "A",
     "Fetched by the crawler from the AEC's free bulk download (its robots.txt allows it). The extract keeps both sides: "
     "the donor's return (Donations Made) and the recipient's (Detailed Receipts), which must not be added together, "
     "since one payment can appear in both. A recipient's 'Other Receipt' is not a donation, and receipts by the "
     "Business Council of Australia are a lobby group's, not a party's. The zip is not committed (it names private "
     "donors); its SHA-256 is in the manifest. RG-069."),
]


def normalise(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def pack_list() -> list[str]:
    text = open(os.path.join(ROOT, "scripts", "rebuild_all.py"), encoding="utf-8").read()
    block = text[text.index("PACKS = ["): text.index("]\n", text.index("PACKS = ["))]
    return re.findall(r'"(data/packs/[^"]+\.json)"', block)


def prior_notes(gap_id: int) -> str:
    note = ""
    for rel in pack_list():
        if rel == THIS_PACK:
            break
        path = os.path.join(ROOT, rel)
        if not os.path.exists(path):
            continue
        for r in json.load(open(path, encoding="utf-8")).get("rows", {}).get("research_gaps", []):
            if r.get("id") == gap_id and r.get("notes"):
                note = r["notes"]
            elif r.get("match", {}).get("id") == gap_id and (r.get("set") or {}).get("notes"):
                note = r["set"]["notes"]
    return note


def aec_totals() -> dict:
    """Party-side figures by company, 2020-21 to 2024-25, from the extract (BCA receipts kept apart)."""
    t: dict = {}
    for r in csv.DictReader(open(os.path.join(RAW, TEXTS[SRC_AEC]), encoding="utf-8")):
        bca = "Business Council" in r["counterparty"]
        key = (r["company_group"], r["return_side"].split(" ")[0], "BCA" if bca else "party")
        t[key] = t.get(key, 0.0) + float(r["value_aud"] or 0)
    return t


def main() -> int:
    errors: list[str] = []
    texts = {}
    for sid, rel in TEXTS.items():
        path = os.path.join(RAW, rel)
        if not os.path.exists(path):
            errors.append(f"{sid}: archive missing at {rel}")
            continue
        texts[sid] = normalise(open(path, encoding="utf-8", errors="replace").read())
    for sid, quotes in QUOTES.items():
        for label, quote in quotes.items():
            if sid in texts and normalise(quote) not in texts[sid]:
                errors.append(f"{sid}/{label}: quote not found verbatim in the archive")
    # The absence the note states: no data centre in the tax expenditure appendix (Appendix C to the end).
    if SRC_BP1 in texts:
        appendix = texts[SRC_BP1][texts[SRC_BP1].index("C. Tax expenditures and concessional charges"):]
        if re.search(r"data cent", appendix, re.I):
            errors.append(f"{SRC_BP1}: the note says Appendix C never mentions data centres, but it does")
    # The figures the RG-069 note states, computed from the extract.
    tot = aec_totals()
    expect = {("Amazon", "donor", "party"): 523945, ("Macquarie Technology Group", "donor", "party"): 316324,
              ("CDC Data Centres", "recipient", "party"): 27900, ("AirTrunk", "recipient", "BCA"): 104500}
    for k, v in expect.items():
        if round(tot.get(k, 0)) != v:
            errors.append(f"{SRC_AEC}: {k} totals {round(tot.get(k, 0))}, the note says {v}")
    if errors:
        print("refusing to write the pack:", file=sys.stderr)
        for e in errors:
            print(f"  {e}", file=sys.stderr)
        return 1

    def q(*refs: tuple[str, str]) -> list[dict]:
        grouped: dict[str, list[str]] = {}
        for sid, label in refs:
            grouped.setdefault(sid, []).append(QUOTES[sid][label])
        return [dict(id=sid, quote=" | ".join(v)) for sid, v in grouped.items()]

    sources = []
    for sid, title, publisher, published, doc_type, cred, notes in NEW_SOURCES:
        meta = json.load(open(os.path.join(RAW, TEXTS[sid] + ".meta.json"), encoding="utf-8"))
        sources.append(dict(id=sid, title=title, publisher=publisher, url=meta["url"], doc_type=doc_type,
                            published=published, credibility=cred, accessed=TODAY,
                            notes=notes + f" Archived {TODAY} at data/raw/{TEXTS[sid]} with a manifest "
                                          f"(SHA-256 {meta['sha256'][:16]}...)."))

    def gap(gap_id: int, tag: str, text: str, refs: list[tuple[str, str]], status: str | None = None,
            resolved: bool = False, source_id: str | None = None) -> list[dict]:
        upd = dict(notes=(prior_notes(gap_id) + tag + " " + text).strip(), as_of_date=TODAY)
        if status:
            upd["status"] = status
        if resolved:
            upd["resolved_date"] = TODAY
        if source_id:
            upd.update(source_id=source_id, fact_status="VERIFIED", confidence="high")
        return [dict(match=dict(id=gap_id), set=upd, add_sources=q(*refs) if refs else [])]

    gaps: list[dict] = []
    # ---- The author's decisions --------------------------------------------------------------
    gaps += gap(76, DECIDED, "Closed as resolved-negative: no Australian site, application or announcement for "
                "TCS or HyperVault was found in two passes. Re-open on any HyperVault announcement for Australia.", [],
                status="resolved", resolved=True)
    gaps += gap(90, DECIDED, "Closed as resolved-negative: nothing read places Palantir or NVIDIA in AUKUS Pillar II "
                "work. Closing records the absence, not a denial. Re-open on a primary record of an award.", [],
                status="resolved", resolved=True)
    gaps += gap(13, DECIDED, "The remainder (AWS's and Google's site-level footprints) is closed as not retrievable "
                "at zero spend. Re-open if a planning record, a landowner document or the operator names a site.", [],
                status="wont_fix")
    gaps += gap(102, DECIDED, "Closed as not retrievable at zero spend: no record names the end user. Re-open on "
                "the operator's or Stockland's own statement.", [], status="wont_fix")
    gaps += gap(34, DECIDED, "The three modification rows are reclassified as proposed: SSD-9741-Mod-4 to "
                "fuel_storage_increase (materiality 5), SSD-66777221-Mod-2 to generator_increase (5), SSD-9741-Mod-3 "
                "to generator_increase (4). Council development applications remain.", [], status="in_progress")
    mods = [
        dict(match=dict(mod_case="SSD-9741-Mod-4"), set=dict(change_type="fuel_storage_increase", materiality=5,
                                                              as_of_date=TODAY)),
        dict(match=dict(mod_case="SSD-66777221-Mod-2"), set=dict(change_type="generator_increase", materiality=5,
                                                                  as_of_date=TODAY)),
        dict(match=dict(mod_case="SSD-9741-Mod-3"), set=dict(change_type="generator_increase", materiality=4,
                                                              as_of_date=TODAY)),
    ]

    # ---- The author's downloads ---------------------------------------------------------------
    gaps += gap(7, TAG, (
        "NSW PART, from the State's own statement (download #30). Budget Paper No. 1 for 2026-27 estimates "
        "'$16.8 billion' of tax expenditures and concessions and itemises every one over $1 million: its Appendix C "
        "never mentions data centres. Data centres appear elsewhere only as a driver of business investment and in "
        "Sydney Water's strategy for 'servicing data centres', which 'is supported by principles of full cost "
        "recovery'. So no data-centre concession of $1 million or more is in the NSW statement; a firm-level grant "
        "below that line, or one made outside the tax system, is not excluded (GIPA-002, not lodged). Other states "
        "remain."),
        [(SRC_BP1, "total"), (SRC_BP1, "itemised"), (SRC_BP1, "investment"), (SRC_BP1, "sydney_water"),
         (SRC_BP1, "cost_recovery")], status="in_progress")
    gaps += gap(18, TAG, (
        "RESOLVED, as far as AEMO's registration list answers it (download #31). A data centre company is "
        "registered to provide ancillary services: 'Firmus Infrastructure Pty Ltd' holds the category 'Demand "
        "Response Service Provider - Ancillary Service Load'. An earlier Firmus company ran the 'St Leonards "
        "Facility' in Tasmania as a 20 MW 'Ancillary Service Load' until its registration ceased on 7 February "
        "2023. CDC Data Centres Pty Ltd is registered only as 'Intending'. NEXTDC's backup generators at seven sites "
        "(M1, M2, M3, B1, B2, S1 and S3) are exempt from registration as small generating systems whose 'combined "
        "export ... is expected to be zero MWh'. No data centre is registered for system strength. Registration is "
        "not dispatch: whether the Firmus load is enabled for FCAS would show in AEMO's ancillary services data."),
        [(SRC_AEMO, "firmus"), (SRC_AEMO, "st_leonards"), (SRC_AEMO, "cdc"), (SRC_AEMO, "nextdc"),
         (SRC_AEMO, "zero")], status="resolved", resolved=True, source_id=SRC_AEMO)
    gaps += gap(27, TAG, (
        "BEETALOO, from the NT Government's own release of 22 July 2026 (download #32): 'The Finocchiaro CLP "
        "Government has granted Beetaloo Digital an exclusive commitment over 185 hectares of land at Weddell, "
        "about 30km from Darwin', a 'not to deal' arrangement giving the company 'the exclusive right to make "
        "plans for the 185ha site' while it 'investigates its feasibility'; the project is 'possibly two "
        "hyper-scale AI data centre campuses', 'powered by up to 2GW of on-site gas-fired power generation'. The 2 "
        "GW is generation, not IT load, and is not stored as a capacity. The release also names 'Energy North's "
        "Project Ares, a one-gigawatt project proposed for Murranji station in the Barkly region', and says 'As "
        "many as a dozen data centre developers are eyeing the region'. PROPOSED to the author: new site rows for "
        "Beetaloo Digital at Weddell (NT, pre-lodgement, no capacity) and Energy North's Project Ares at Murranji "
        "station (NT, proposed, no capacity), each cited to this release. Not made by this pack."),
        [(SRC_NT, "grant"), (SRC_NT, "not_to_deal"), (SRC_NT, "campuses"), (SRC_NT, "power"), (SRC_NT, "ares"),
         (SRC_NT, "dozen")], status="in_progress")
    gaps += gap(69, TAG, (
        "NSW: the Electoral Commission's stakeholder register (the author's export, download #34 in part) lists "
        "276 major political donor entities and gives no amounts; one is a data centre company, 'AMAZON WEB "
        "SERVICES AUSTRALIA PTY LTD'. CDC, AirTrunk, NEXTDC, Equinix, Goodman and Stockland are not on it. "
        "COMMONWEALTH, with amounts, from the AEC's free bulk returns (fetched by the crawler), 2020-21 to 2024-25, "
        "by side of the return (the two sides are not added): Amazon's own returns disclose $523,945 of donations "
        "made to Labor and Liberal branches; Macquarie Technology Group's own returns $316,324 to parties; the "
        "Labor Party's returns record $27,900 from 'CDC Data centres' as 'Other Receipt', not as donations "
        "(2022-23 to 2024-25). Most of what the other companies paid went to the Business Council of Australia, a "
        "lobby group, as 'Other Receipt' or 'Subscription' (AirTrunk $104,500 in 2024-25), not to a party. "
        "STILL OPEN: the NSW amounts, which sit on each major political donor's own disclosure on the Electoral "
        "Commission's site (download #34, rest: Amazon Web Services Australia's disclosures). No improper conduct "
        "is alleged or implied."),
        [(SRC_NSWEC, "aws"), (SRC_AEC, "cdc_2425"), (SRC_AEC, "airtrunk")], status="in_progress")

    pack = {
        "pack_id": "batch8-decisions-2026-11",
        "prepared_by": "scripts/curate_batch8_decisions.py from data/raw/ (the author's downloads of 2026-11-18)",
        "prepared_on": TODAY,
        "_comment": [
            "The author's decisions of 2026-11-18 on batch 8's proposals: RG-076 and RG-090 resolved-negative;",
            "RG-013's remainder and RG-102 wont_fix; three modification rows reclassified.",
            "The author's downloads #30, #31, #32 and #34 (part), and the AEC's bulk returns. New site rows for",
            "the NT proposals are PROPOSED in RG-027's note and not made here.",
        ],
        "sources": sources,
        "rows": {"research_gaps": gaps, "modifications": mods},
    }
    with open(OUT_PACK, "w") as f:
        json.dump(pack, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print(f"batch 8 decisions: {len(sources)} sources, {len(gaps)} question updates, {len(mods)} modification rows "
          f"reclassified; wrote {os.path.relpath(OUT_PACK, ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
