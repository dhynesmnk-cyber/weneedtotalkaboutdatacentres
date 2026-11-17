#!/usr/bin/env python3
"""
RG-101 third pass: DigiCo's own statutory documents place three of the five held facilities.

curate_hcf_facilities.py held five HCF register facilities because the register gives a provider
and a facility name and nothing else, while sites.state and sites.status are NOT NULL. Three of
the five are DigiCo's: BNE2 (a certified facility) and ADL1 and SYD1 (a certified enclave). On
2026-11-16 every route to DigiCo's own documents was refused: digi-co.com.au refuses the robots
check, and ASX served a bot-check page in place of both announcement PDFs (recorded in
data/raw/asx/dgt/refused.json, not worked around).

On 2026-11-17 the author supplied the documents, downloaded by hand in a browser:
  * the ASX release of 15 October 2026, "DGT Executes Long-term 71MW Contract at SYD1";
  * the AGM 2026 Presentation of 11 November 2026;
  * the Annual Report 2026, released 25 September 2026.

What the author approved (plan of 2026-11-17), and what this pack does:
  * SYD1 is a MATCH, not a new row. The release says the SYD1 Expansion "involves the adaptive
    reuse of an established data centre asset with ... State Significant Development Approval in
    place" and that works "are being delivered within an operating data centre"; the Annual
    Report says "SYD1 granted 'Strategic Certification' status under the ... Hosting
    Certification Framework". So the register's SYD1 enclave and SITE_DIGICO_SYD1 (the consent
    for the expansion) are one facility. curate_hcf_register.py now matches it.
  * ADL1 and BNE2 become rows, placed by the Annual Report's own portfolio list ("Adelaide 1
    (ADL1)", "Brisbane 2 (BNE2)", among seven Australian properties) and its goodwill note
    ("DigiCo Queensland and South Australia (formerly iseek)"). The status `operational` is a
    reading, not a per-facility statement, and is recorded as one: fact_status REPORTED, ADL1 at
    medium confidence (the AGM deck calls its project a brownfield expansion of an existing
    facility), BNE2 at low confidence (only the portfolio list and the register's certification).
  * DigiCo Infrastructure REIT becomes an entity, operator of all three, and owner of SYD1 by
    the 18 December 2024 acquisition the Annual Report records.
  * DigiCo's other four Australian properties (TSV1, ADL2, BNE, BNE1) have no row and are not
    given one: RG-106 asks where they are.

What is quoted and NOT stored:
  * "SYD1 is 100% contracted across 88MW of total capacity": not labelled IT load. The row's
    88 MW IT and 120 MW total come from the consent and are not touched (the RG-099 lesson).
  * The 71 MW tenant is "a global technology firm": anchor_tenant_id stays empty.
  * ADL1's "additional 15MW of IT Capacity (up from 8MW)": ambiguous between today's capacity and
    an earlier plan, so no capacity is stored for ADL1.
  * The Annual Report's FY25 "$1,937.0 million relating to the acquisition of the SYD1 data
    centre campus" is property, plant and equipment acquired, not a stated price, so
    transaction_value_aud stays empty.

SITE_DIGICO_SYD1's status is set to `under_construction` on the author's decision of 2026-11-17
(it had read `approved`, from the consent): the AGM deck says "20MW Project completed; 52MW
expansion is DigiCo's priority development", and the release says a "Fixed price lump sum D&C
Contract executed for the SYD1 52MW capacity expansion". Its 88 MW IT and 120 MW total, from the
consent, are not touched.

Neither the PDFs nor their full text are committed (ASX's terms limit free use of its documents to
private investors). Each document has a manifest (.pdf.meta.json: ASX URL, SHA-256, pages,
extraction yield, how it was obtained) and a file of verbatim excerpts (.excerpts.txt), each
checked against the full extraction when it was written. This script checks every quote against
those excerpts and refuses to write if one is missing.

Outputs:
  * data/packs/rg101_digico.json

Run:
    python3 scripts/curate_rg101_digico.py
    python3 scripts/load_pack.py data/packs/rg101_digico.json --allow-missing-source
"""
from __future__ import annotations

import json
import os
import re
import sys

import curate_hcf_register as hcf

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DGT = os.path.join(ROOT, "data", "raw", "asx", "dgt")
PACKS = os.path.join(ROOT, "data", "packs")
OUT_PACK = os.path.join(PACKS, "rg101_digico.json")
TODAY = "2026-11-17"

SRC_RELEASE = "SRC_DGT_SYD1_71MW_20261015"
SRC_AGM = "SRC_DGT_AGM_20261111"
SRC_AR = "SRC_DGT_AR_2026"
SRC_REGISTER = hcf.SOURCE_ID

DOCS = {
    SRC_RELEASE: ("DGT_Executes_Longterm_71MW_Contract_at_SYD1",
                  "DigiCo Infrastructure REIT - DGT Executes Long-term 71MW Contract at SYD1 (ASX release)"),
    SRC_AGM: ("AGM_2026_Presentation", "DigiCo Infrastructure REIT - AGM 2026 Presentation"),
    SRC_AR: ("Annual_Report_2026", "DigiCo Infrastructure REIT - Annual Report 2026"),
}

# Verbatim passages, each checked against the document's .excerpts.txt before anything is written.
QUOTES: dict[str, dict[str, str]] = {
    SRC_RELEASE: {
        "issuer": "HMC Digital Infrastructure Ltd (ACN 682 024 924) and Equity Trustees Limited (ACN 004 "
                  "031 298; AFSL 240975) as responsible entity for the HMC Digital Infrastructure Trust "
                  "(ARSN 682 160 578)",
        "total": "SYD1 is 100% contracted across 88MW of total capacity",
        "dc": "Fixed price lump sum D&C Contract executed for the SYD1 52MW capacity expansion",
        "tenant": "it has executed a 15-year2 contract for 71MW of capacity at SYD1 with a global "
                  "technology firm, with investment grade credit support.",
        "colo": "The remaining 17MW of SYD1 capacity is leased to co-location customers",
        "first10": "The first 10MW of the SYD1 Expansion is expected to be energised and income producing "
                   "in late Q4 FY27, with the balance delivered progressively over FY28, aligned to "
                   "customer requirements.",
        "reuse": "the SYD1 Expansion, which involves the adaptive reuse of an established data centre "
                 "asset with approved grid capacity and water access and State Significant Development "
                 "Approval in place.",
        "operating": "Works are being delivered within an operating data centre, with uptime maintained "
                     "for existing customers throughout",
    },
    SRC_AGM: {
        "syd1": "SYD1 88MW Project accelerated – 20MW Project completed; 52MW expansion is DigiCo’s "
                "priority development",
        "adl1": "ADL1 Project ▪ Brownfield expansion project to deliver additional 15MW of IT Capacity "
                "(up from 8MW) ▪ In advanced customer discussions",
    },
    SRC_AR: {
        "progress": "ADL1 is also progressing, supported by advanced customer discussions.",
        "portfolio": "Portfolio Australia Sydney 1 (SYD1) Townsville 1 (TSV1) Adelaide 2 (ADL2) Brisbane 1 "
                     "(BNE1) Brisbane 2 (BNE2) Brisbane (BNE)1 Adelaide 1 (ADL1)",
        "renamed": "BNE has been renamed (previously was BNE3).",
        "count": "Number of Properties 5 7 12",
        "billing": "Billing IT Capacity 44MW 41MW 85MW",
        "hcf": "SYD1 granted ‘Strategic Certification’ status under the Australian Government’s Hosting "
               "Certification Framework (HCF) by the Department of Home Affairs",
        "ppe": "FY25: $1,937.0 million relating to the acquisition of the SYD1 data centre campus",
        "cgu": "DigiCo Queensland and South Australia (formerly iseek)",
        "acq": "On 18 December 2024, the Stapled Group acquired 100% of HDI SYD1 Holdings Pty Limited "
               "(Global Switch), which was accounted for as an asset acquisition",
    },
}

# The rows this pack creates or places, for curate_hcf_register.py to certify after it loads.
PLACED = {"SITE_DIGICO_SYD1", "SITE_DIGICO_ADL1", "SITE_DIGICO_BNE2"}
STILL_HELD = ["Cloud Carrier DB1", "Vocus TransACT House Dickson"]

ENTITY = dict(
    id="ENT_DIGICO_REIT", name="DigiCo Infrastructure REIT",
    legal_name=("HMC Digital Infrastructure Ltd (ACN 682 024 924) stapled with the HMC Digital "
                "Infrastructure Trust (ARSN 682 160 578), responsible entity Equity Trustees Limited"),
    entity_type="colocation_operator", domicile="Australia", hq_country="Australia", asx_ticker="DGT",
    website="https://www.digi-co.com.au/",
    notes=("ASX-listed owner, operator and developer of data centres (ASX: DGT), managed within HMC "
           "Capital's group, whose letterhead and contact details its releases carry. Its Annual Report "
           "2026 lists seven Australian properties - Sydney 1 (SYD1), Townsville 1 (TSV1), Adelaide 1 "
           "(ADL1), Adelaide 2 (ADL2), Brisbane 1 (BNE1), Brisbane 2 (BNE2) and Brisbane (BNE, "
           "previously BNE3) - with 41 MW of billing IT capacity in Australia at 30 June 2026, and a "
           "goodwill unit called 'DigiCo Queensland and South Australia (formerly iseek)'. Its own "
           "website refuses the crawler's robots check (RG-101); everything here is from its ASX "
           "documents, supplied by the author. People named in those documents appear here by role "
           "only."),
    fact_status="VERIFIED", source_id=SRC_RELEASE, confidence="high", as_of_date=TODAY,
)

NEW_SITES = [
    dict(id="SITE_DIGICO_ADL1", name="DigiCo ADL1 (Adelaide 1)", operator_id="ENT_DIGICO_REIT",
         state="SA", market="NEM", status="operational",
         notes=("Placed by DigiCo's own Annual Report 2026, which lists 'Adelaide 1 (ADL1)' among its "
                "seven Australian properties, with 41 MW of billing IT capacity across them, and a "
                "goodwill unit 'DigiCo Queensland and South Australia (formerly iseek)'. STATUS IS A "
                "READING, NOT A STATEMENT: no document read says 'ADL1 is operational' in those words. "
                "It rests on the AGM 2026 deck's 'Brownfield expansion project to deliver additional "
                "15MW of IT Capacity (up from 8MW)', which describes an existing facility, and on its "
                "place in a portfolio that is billing. NO CAPACITY IS STORED: '(up from 8MW)' can be "
                "read as today's capacity or as an earlier plan for the expansion, and the documents do "
                "not settle which. No address, suburb or area is published in them - RG-103. The "
                "Commonwealth HCF register certifies 'DigiCo - ADL1 and SYD1' as a Strategic Enclave "
                "(quoted on this row by curate_hcf_register.py)."),
         fact_status="REPORTED", source_id=SRC_AR, confidence="medium", as_of_date="2026-06-30",
         refs=[(SRC_AR, "portfolio"), (SRC_AR, "count"), (SRC_AR, "billing"), (SRC_AR, "cgu"),
               (SRC_AR, "progress"), (SRC_AGM, "adl1")]),
    dict(id="SITE_DIGICO_BNE2", name="DigiCo BNE2 (Brisbane 2)", operator_id="ENT_DIGICO_REIT",
         state="QLD", market="NEM", status="operational",
         notes=("Placed by DigiCo's own Annual Report 2026, which lists 'Brisbane 2 (BNE2)' among its "
                "seven Australian properties, with 41 MW of billing IT capacity across them, and a "
                "goodwill unit 'DigiCo Queensland and South Australia (formerly iseek)'. STATUS IS A "
                "READING, AT LOW CONFIDENCE: nothing read says anything about BNE2 except its name in "
                "that list and the Commonwealth HCF register's certification of 'DigiCo - BNE2' as a "
                "Strategic Facility (quoted on this row by curate_hcf_register.py). A certified facility "
                "in a billing portfolio is read as operating; a document that says so, or says "
                "otherwise, replaces this reading. No address, suburb, area or capacity is published - "
                "RG-103. Not to be confused with NEXTDC B2 Brisbane (SITE_NEXTDC_B2), a different "
                "operator's facility the register lists as 'Brisbane 2' under NEXTDC."),
         fact_status="REPORTED", source_id=SRC_AR, confidence="low", as_of_date="2026-06-30",
         refs=[(SRC_AR, "portfolio"), (SRC_AR, "count"), (SRC_AR, "billing"), (SRC_AR, "cgu")]),
]

SYD1_REFS = [(SRC_RELEASE, "reuse"), (SRC_RELEASE, "operating"), (SRC_RELEASE, "dc"), (SRC_RELEASE, "total"),
             (SRC_RELEASE, "tenant"), (SRC_RELEASE, "colo"), (SRC_RELEASE, "first10"),
             (SRC_AGM, "syd1"), (SRC_AR, "hcf"), (SRC_AR, "acq")]

SYD1_NOTE = (
    " UPDATED 2026-11-17 (RG-101, author-approved): this row is the operating SYD1 facility as well "
    "as the consent for its expansion. DigiCo's release of 15 October 2026 says the SYD1 Expansion "
    "'involves the adaptive reuse of an established data centre asset with ... State Significant "
    "Development Approval in place' and that works 'are being delivered within an operating data "
    "centre'; its Annual Report 2026 says SYD1 holds 'Strategic Certification' under the Hosting "
    "Certification Framework. DigiCo's Stapled Group acquired 100% of 'HDI SYD1 Holdings Pty Limited "
    "(Global Switch)' on 18 December 2024 - a different company from the consent's applicant, HDI "
    "SYD1 Property Holdings Limited. QUOTED, NOT STORED: 'SYD1 is 100% contracted across 88MW of "
    "total capacity' (not labelled IT load; the 88 MW IT and 120 MW total here come from the "
    "consent), and a 15-year contract for 71 MW 'with a global technology firm' that DigiCo does not "
    "name, so the tenant stays a gap. STATUS SET TO under_construction ON THE AUTHOR'S DECISION OF "
    "2026-11-17 (it read approved, from the consent): the AGM 2026 deck says '20MW Project completed; "
    "52MW expansion is DigiCo's priority development', and the release says a 'Fixed price lump sum "
    "D&C Contract executed for the SYD1 52MW capacity expansion'."
)

OWNERSHIP = dict(
    holder_id="ENT_DIGICO_REIT", target_id="ENT_GLOBALSWITCH", stake_pct=100.0, instrument="equity",
    effective_from="2024-12-18", event="acquisition",
    notes=("DigiCo's Annual Report 2026: 'On 18 December 2024, the Stapled Group acquired 100% of HDI "
           "SYD1 Holdings Pty Limited (Global Switch), which was accounted for as an asset "
           "acquisition'. The target is recorded against ENT_GLOBALSWITCH because the report itself "
           "names the acquired company 'Global Switch'; the legal entity it names is HDI SYD1 "
           "Holdings Pty Limited, which the record does not otherwise hold. No price is stored: the "
           "report's FY25 '$1,937.0 million relating to the acquisition of the SYD1 data centre "
           "campus' is property, plant and equipment acquired, not a stated consideration."),
    fact_status="VERIFIED", source_id=SRC_AR, confidence="high", as_of_date="2026-06-30",
)

GAP_106 = dict(
    id=106, pillar="A", priority=4, retrieval_method="manual_review", status="open", opened=TODAY,
    question=("Where are DigiCo's four other Australian properties - Townsville 1 (TSV1), Adelaide 2 "
              "(ADL2), Brisbane 1 (BNE1) and Brisbane (BNE, previously BNE3) - and does the record "
              "already hold any of them under another name?"),
    why_it_matters=("DigiCo's Annual Report lists seven Australian properties and the record now holds "
                    "three. The other four are operating facilities of an ASX-listed operator that "
                    "calls itself 'an emerging sovereign digital infrastructure platform', and the "
                    "Queensland and South Australian ones came from iseek, so they may sit in the "
                    "record under an older name."),
    target_source=("DigiCo's ASX announcements and annual reports; iseek's archived facility pages; "
                   "Queensland and South Australian planning registers"),
    notes=(f"OPENED {TODAY} from DigiCo's Annual Report 2026, whose Australian portfolio lists "
           "'Sydney 1 (SYD1) Townsville 1 (TSV1) Adelaide 2 (ADL2) Brisbane 1 (BNE1) Brisbane 2 "
           "(BNE2) Brisbane (BNE)1 Adelaide 1 (ADL1)', footnoted 'BNE has been renamed (previously "
           "was BNE3).' SYD1, ADL1 and BNE2 are recorded (RG-101). The other four are NOT given rows: "
           "the report names them and nothing else - no address, status or capacity - and none of "
           "them is on the HCF register. No existing row is named for iseek or DigiCo."),
    fact_status="VERIFIED", source_id=SRC_AR, confidence="high", as_of_date=TODAY,
)


def normalise(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def pack_row(pack_name: str, table: str, key: str, value, errors: list[str]) -> dict | None:
    """A row as an earlier pack writes it, so a note can be extended rather than replaced."""
    path = os.path.join(PACKS, pack_name)
    if not os.path.exists(path):
        errors.append(f"{pack_name}: not found")
        return None
    for r in json.load(open(path, encoding="utf-8")).get("rows", {}).get(table, []):
        target = r.get("match", r)
        if target.get(key) == value:
            return r
    errors.append(f"{pack_name}: no {table} row with {key}={value!r}")
    return None


def main() -> int:
    errors: list[str] = []
    manifests: dict[str, dict] = {}
    for sid, (slug, _title) in DOCS.items():
        meta_path = os.path.join(DGT, slug + ".pdf.meta.json")
        excerpts_path = os.path.join(DGT, slug + ".excerpts.txt")
        if not (os.path.exists(meta_path) and os.path.exists(excerpts_path)):
            errors.append(f"{slug}: manifest or excerpts missing")
            continue
        meta = json.load(open(meta_path, encoding="utf-8"))
        excerpts = open(excerpts_path, encoding="utf-8").read()
        if meta["sha256"] not in excerpts:
            errors.append(f"{slug}: the excerpts do not name the manifest's SHA-256")
        body = [ln for ln in excerpts.splitlines() if ln and not ln.startswith("#")]
        for ln in body:
            m = re.match(r"p(\d+) \| ", ln)
            if not m or not 1 <= int(m.group(1)) <= meta["pages"]:
                errors.append(f"{slug}: malformed excerpt line {ln[:60]!r}")
        text = normalise(" ".join(re.sub(r"^p\d+ \| ", "", ln) for ln in body))
        for label, quote in QUOTES[sid].items():
            if normalise(quote) not in text:
                errors.append(f"{slug} {label}: quote not in the excerpts: {quote[:70]!r}")
        manifests[sid] = meta

    # The register must list each placed facility exactly where curate_hcf_register.py will look.
    missing = PLACED - set(hcf.MATCHES)
    if missing:
        errors.append(f"not in curate_hcf_register.py MATCHES: {sorted(missing)}")
    if hcf.PLACED_BY_RG101 != PLACED:
        errors.append("curate_hcf_register.py PLACED_BY_RG101 and this pack disagree: "
                      f"{sorted(hcf.PLACED_BY_RG101 ^ PLACED)}")

    syd1 = pack_row("rg060_consent_matrix.json", "sites", "id", "SITE_DIGICO_SYD1", errors)
    gap103 = pack_row("hcf_facilities.json", "research_gaps", "id", 103, errors)
    gap101 = pack_row("hcf_facilities.json", "research_gaps", "id", 101, errors)

    if errors:
        print("refusing to write; fix these first:", file=sys.stderr)
        for e in errors:
            print(f"  {e}", file=sys.stderr)
        return 1

    def quotes(refs: list[tuple[str, str]]) -> list[dict]:
        grouped: dict[str, list[str]] = {}
        for sid, label in refs:
            grouped.setdefault(sid, []).append(QUOTES[sid][label])
        return [dict(id=sid, quote=" | ".join(qs)) for sid, qs in grouped.items()]

    sources = []
    for sid, (slug, title) in DOCS.items():
        meta = manifests[sid]
        sources.append(dict(
            id=sid, title=title, publisher="DigiCo Infrastructure REIT (ASX: DGT)", url=meta["url"],
            doc_type="primary_company", published=meta["published"], credibility="A", accessed=TODAY,
            notes=(f"The issuer's own statutory disclosure to ASX, {meta['pages']} pages, SHA-256 "
                   f"{meta['sha256']}. The crawler was refused it (data/raw/asx/dgt/refused.json); the "
                   f"author downloaded it in a browser and supplied it on {TODAY}. PDF and full text not "
                   f"committed (ASX's terms): the manifest is data/raw/asx/dgt/{slug}.pdf.meta.json and "
                   f"the cited passages are verbatim in {slug}.excerpts.txt."),
        ))

    sites = []
    for site in NEW_SITES:
        row = {k: v for k, v in site.items() if k != "refs"}
        sites.append(row)
        # The loader drops add_sources on a keyed insert, so quotes go on a follow-up match.
        sites.append(dict(match=dict(id=row["id"]), set={}, add_sources=quotes(site["refs"])))
    sites.append(dict(
        match=dict(id="SITE_DIGICO_SYD1"),
        set=dict(notes=syd1["set"]["notes"] + SYD1_NOTE, status="under_construction"),
        fill=dict(operator_id="ENT_DIGICO_REIT", owner_id="ENT_DIGICO_REIT"),
        add_sources=quotes(SYD1_REFS),
    ))

    gaps = [
        dict(match=dict(id=101), set=dict(
            status="in_progress",
            notes=gap101["notes"] + (
                f" UPDATED {TODAY} (third pass, author-approved): THREE OF THE FIVE PLACED from "
                "DigiCo's own ASX documents, which the crawler was refused and the author supplied. "
                "SYD1 is SITE_DIGICO_SYD1 - the expansion is 'the adaptive reuse of an established "
                "data centre asset' and the Annual Report records SYD1's Strategic Certification - so "
                "it is a match, not a new row. ADL1 and BNE2 are added as SITE_DIGICO_ADL1 (SA) and "
                "SITE_DIGICO_BNE2 (QLD) from the Annual Report's portfolio list, with status "
                "`operational` recorded as a reading (REPORTED; ADL1 medium, BNE2 low confidence) and "
                "no capacity stored. STILL HELD: " + " and ".join(STILL_HELD) + ", whose every route "
                "is refused (cloudcarrier.com and environment.act.gov.au refuse the robots check) or "
                "silent (Vocus's own page names none of its facilities). Decided by the author on "
                f"{TODAY}: SITE_DIGICO_SYD1 now reads `under_construction` (it read `approved`, from the "
                "consent), on DigiCo's own words that the first 20 MW project is complete and the 52 MW "
                "expansion is under a fixed-price construction contract. DigiCo's other four "
                "Australian properties are RG-106.")),
            add_sources=quotes([(SRC_AR, "portfolio"), (SRC_AR, "hcf"), (SRC_RELEASE, "reuse")])),
        dict(match=dict(id=103), set=dict(notes=gap103["notes"] + (
            f" UPDATED {TODAY}: SITE_DIGICO_ADL1 and SITE_DIGICO_BNE2 join this question. DigiCo's "
            "Annual Report and AGM deck name them and nothing more: no address, suburb, area or "
            "current capacity. ADL1's 'additional 15MW of IT Capacity (up from 8MW)' is quoted on the "
            "row, not stored.")),
            add_sources=quotes([(SRC_AGM, "adl1")])),
        GAP_106,
    ]

    pack = {
        "pack_id": "rg101-digico-2026-11",
        "prepared_by": "scripts/curate_rg101_digico.py from data/raw/asx/dgt/ (supplied by the author)",
        "prepared_on": TODAY,
        "_comment": [
            "RG-101 third pass. DigiCo's ASX documents, supplied by the author after ASX refused the",
            "crawler, place three of the five held HCF facilities: SYD1 matches SITE_DIGICO_SYD1;",
            "ADL1 and BNE2 become rows whose status is a recorded reading. Loads after",
            "hcf_facilities.json (whose RG-101 and RG-103 notes it extends) and before",
            "hcf_register.json, which certifies all three from the register's own lines.",
        ],
        "sources": sources,
        "rows": {
            "entities": [ENTITY],
            "sites": sites,
            "ownership": [OWNERSHIP],
            "research_gaps": gaps,
        },
    }
    # The entity's quote, attached after its insert for the same loader reason as the sites.
    pack["rows"]["entities"].append(dict(match=dict(id="ENT_DIGICO_REIT"), set={},
                                         add_sources=quotes([(SRC_RELEASE, "issuer"), (SRC_AR, "cgu")])))
    with open(OUT_PACK, "w") as f:
        json.dump(pack, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print(f"{len(DOCS)} DigiCo documents verified against their excerpts; SYD1 matched, "
          f"{len(NEW_SITES)} facilities added, {len(STILL_HELD)} still held; "
          f"wrote {os.path.relpath(OUT_PACK, ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
