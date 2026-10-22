#!/usr/bin/env python3
"""
Curate research batch 4, "Whose data, whose rules" (docs/RESEARCH-PLAN.md, story line C3).

C3 asks whether government data stays sovereign and whether its handling is visible. Free records
answer more than the agenda expected:

  1. Every Palantir contract the Commonwealth has published since 2013. AusTender and data.gov.au
     both refuse the research crawler, but the data is licensed CC BY 3.0 AU and the Open
     Contracting Partnership's Data Registry republishes the AusTender feed. That copy was read
     once (data/raw/registers/open_contracting/; the 260 MB file is not committed) and the 30
     Palantir records are committed as an extract. It agrees with the five notices read on
     AusTender itself in September, which this script checks.
  2. The law that decides what can be asked: the Freedom of Information Act 1982 lists the
     Australian Signals Directorate as an exempt agency, so the FOI drafts go to Defence and the
     ACIC, and frame the ASD question around documents Defence itself makes.
  3. The Hosting Certification Framework register (archived in September): Amazon's Australian
     regions are certified; Palantir, which says its Australian platform runs there, is not listed.
  4. WA Police's own privacy impact assessment for its live facial recognition trial names the
     vendor: NEC. Not Palantir.
  5. Coles' statement on ending its Palantir partnership, as three outlets quote it, and its 2026
     notice of meeting, which has no item on Palantir.
  6. The keynote quote: a second transcript agrees with Sherwood's. The recording refused.
  7. Anthropic and the Western Downs Digital Park: Dexus's own stock exchange release. Anthropic
     is the company whose model drafts this research; the hunt log and card carry a disclosure.

Every quote is checked against its archive and the script refuses to write if one is missing.

Run:
    python3 scripts/curate_whose_data.py             # from the committed extract
    python3 scripts/curate_whose_data.py --rescan    # re-derive the extract from the full archive
    python3 scripts/load_pack.py data/packs/whose_data.json --allow-missing-source
"""
from __future__ import annotations

import gzip
import hashlib
import json
import os
import re
import sys
from collections import defaultdict
from datetime import datetime, timezone
from decimal import Decimal
from zoneinfo import ZoneInfo

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "data", "packs", "whose_data.json")
RAW = os.path.join(ROOT, "data", "raw")
OPS = os.path.join(RAW, "operators")
OCP = os.path.join(RAW, "registers", "open_contracting")
FULL = os.path.join(OCP, "austender-full.jsonl.gz")
EXTRACT = os.path.join(OCP, "austender-palantir-extract.json")
NVIDIA_EXTRACT = os.path.join(OCP, "austender-nvidia-extract.json")
TODAY = "2026-10-22"
CANBERRA = ZoneInfo("Australia/Sydney")

SRC_OCDS = "SRC_AUSTENDER_OCDS_202610"
SRC_FOI_ACT = "SRC_FOI_ACT_1982"
SRC_HCF = "SRC_HCF_REGISTER"
SRC_WAPOL = "SRC_WAPOL_OLFR_PIA"
SRC_COLES_ITN = "SRC_ITNEWS_COLES_SEP26"
SRC_COLES_ACS = "SRC_ACS_COLES_SEP26"
SRC_COLES_CD = "SRC_CYBERDAILY_COLES_SEP26"
SRC_COLES_NOM = "SRC_COLES_AGM_NOM_2026"
SRC_DEXUS = "SRC_DEXUS_WDDP_2026"
SRC_SINGJU = "SRC_SINGJU_GTC_TRANSCRIPT"
SRC_SHERWOOD = "SRC_SHERWOOD_GTC_QUOTE"
SRC_WESTRAC = "SRC_PALANTIR_WESTRAC_2022"
SRC_CRIKEY_DEF = "SRC_CRIKEY_DEF_FEB26"
SRC_IRAP = "SRC_PALANTIR_IRAP_NOV25"

# The supplier's ABN on AusTender, and the name filter the extract was cut with.
PALANTIR_ABN = "48144948309"
NAME_FILTER = ("alantir", "ALANTIR", PALANTIR_ABN, "48 144 948 309")
# Notices read in full on AusTender in September (gov_contracts rows 24 to 30) and their values today.
# The copy must agree with every one, or it is not used.
READ_ON_AUSTENDER = {"CN3992202": "696981.39", "CN3996124": "1402122.87", "CN4104368": "7150000.00",
                     "CN4115523": "4135076.99", "CN4218984": "10389894.90"}
AGENCY_ENTITY = {
    "Department of Defence": "ENT_DOD_AU",
    "Australian Criminal Intelligence Commission": "ENT_ACIC",
    "Australian Signals Directorate": "ENT_ASD",
    "Australian Transaction Reports and Analysis Centre": "ENT_AUSTRAC",
    "Department of Veterans' Affairs": None,
}

errors: list[str] = []


def spaceless(text: str) -> str:
    return re.sub(r"\s+", "", text).lower()


def text_of(path: str) -> str:
    return open(path, encoding="utf-8").read()


def in_text(path: str, quote: str, text: str | None = None) -> str:
    if spaceless(quote) not in spaceless(text if text is not None else text_of(path)):
        errors.append(f"{os.path.relpath(path, ROOT)} does not hold {quote[:70]!r}")
    return quote


def quoted(path: str, quote: str) -> str:
    """'pN: quote' from a PDF's page-marked text, refusing a quote the archive does not hold."""
    for m in re.finditer(r"\[\[page (\d+)\]\]\n(.*?)(?=\n\[\[page \d+\]\]|\Z)", text_of(path), re.S):
        if spaceless(quote) in spaceless(m.group(2)):
            return f"p{m.group(1)}: {quote}"
    errors.append(f"{os.path.relpath(path, ROOT)} does not hold {quote[:70]!r}")
    return quote


def absent(path: str, word: str) -> None:
    if re.search(word, text_of(path), re.I):
        errors.append(f"{os.path.relpath(path, ROOT)} now mentions {word!r}; the notes say it does not")


def manifest(path: str) -> dict:
    return json.load(open(path))


def sha_ok(path: str) -> bool:
    return hashlib.sha256(open(path, "rb").read()).hexdigest() == manifest(path + ".meta.json")["sha256"]


def next_data_text(path: str) -> str:
    """The strings of a Next.js page's embedded data: Palantir's newsroom serves its text there."""
    raw = open(path, encoding="utf-8", errors="replace").read()
    m = re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', raw, re.S)
    out: list[str] = []

    def walk(node: object) -> None:
        if isinstance(node, str):
            out.append(node)
        elif isinstance(node, dict):
            for v in node.values():
                walk(v)
        elif isinstance(node, list):
            for v in node:
                walk(v)
    if m:
        walk(json.loads(m.group(1)))
    return "\n".join(out)


def local_date(stamp: str | None) -> str | None:
    """AusTender's feed gives UTC instants; the notices show the Canberra date."""
    if not stamp:
        return None
    return datetime.fromisoformat(stamp.replace("Z", "+00:00")).astimezone(CANBERRA).date().isoformat()


def redacted(record: dict) -> dict:
    """A party's contact point and address can name or locate a person (a contracts officer, a sole
    trader), so neither is committed. Names, roles and business numbers stay."""
    for party in record.get("parties", []):
        party.pop("contactPoint", None)
        party.pop("address", None)
    return record


def cut(full: str) -> tuple[bytes, bytes, list[dict]]:
    """Read the full feed once: the Palantir records, the NVIDIA records (companies only), and the
    AUKUS records, which are counted but not committed because one supplier is a person."""
    palantir, nvidia, aukus = [], [], []
    with gzip.open(full, "rt", encoding="utf-8") as fh:
        for line in fh:
            if any(n in line for n in NAME_FILTER):
                palantir.append(redacted(json.loads(line)))
            low = line.lower()
            if "nvidia" in low:
                nvidia.append(redacted(json.loads(line)))
            if "aukus" in low:
                aukus.append(json.loads(line))

    def dump(recs: list[dict]) -> bytes:
        recs.sort(key=lambda h: h["contracts"][0]["id"])
        return json.dumps(recs, indent=1, sort_keys=True, ensure_ascii=False).encode()
    return dump(palantir), dump(nvidia), aukus


def suppliers(record: dict) -> list[str]:
    return [p["name"] for p in record["parties"] if "supplier" in p.get("roles", [])]


def write_extracts() -> int:
    """Cut the committed extracts from the full feed (run once, after a fresh download)."""
    full_meta = manifest(FULL + ".meta.json")
    if not sha_ok(FULL):
        print(f"{FULL} fails its manifest", file=sys.stderr)
        return 1
    pal, nv, aukus = cut(FULL)
    stamp = datetime.now(timezone.utc).isoformat(timespec="seconds")
    for path, body, what, extra in (
            (EXTRACT, pal, "every record whose line holds 'alantir', 'ALANTIR' or the ABN 48144948309 in either "
                           "form; all are Palantir Technologies Inc. or Palantir Technologies Australia Pty Ltd", {}),
            (NVIDIA_EXTRACT, nv, "every record whose line holds 'nvidia' in any case",
             dict(aukus_records=len(aukus), aukus_suppliers_palantir_or_nvidia=sum(
                 1 for r in aukus if any(re.search("palantir|nvidia", s, re.I) for s in suppliers(r))),
                  aukus_note="records whose line holds 'aukus' in any case: counted here, not committed, because one "
                             "supplier is an individual"))):
        with open(path, "wb") as fh:
            fh.write(body)
        json.dump(dict(derived_from=os.path.relpath(FULL, ROOT), derived_from_sha256=full_meta["sha256"],
                       derived_from_url=full_meta["url"], filter=what,
                       redaction="each party's contactPoint and address removed: they can name or locate a person",
                       records=len(json.loads(body)), derived_utc=stamp, sha256=hashlib.sha256(body).hexdigest(),
                       bytes=len(body), **extra),
                  open(path + ".meta.json", "w"), indent=1)
        print(f"wrote {os.path.relpath(path, ROOT)}: {len(json.loads(body))} records")
    return 0


def main(argv: list[str]) -> int:
    if "--extract" in argv:
        return write_extracts()
    # --- the Commonwealth's Palantir contracts --------------------------------------------------------
    if "--rescan" in argv:
        if not os.path.exists(FULL) or not sha_ok(FULL):
            print(f"{FULL} is missing or fails its manifest", file=sys.stderr)
            return 1
        pal, nv, aukus = cut(FULL)
        for path, body in ((EXTRACT, pal), (NVIDIA_EXTRACT, nv)):
            if hashlib.sha256(body).hexdigest() != manifest(path + ".meta.json")["sha256"]:
                errors.append(f"re-deriving {os.path.basename(path)} from the full feed gives a different file")
        if len(aukus) != manifest(NVIDIA_EXTRACT + ".meta.json")["aukus_records"]:
            errors.append("the full feed's AUKUS records no longer match the count on record")
    for path in (EXTRACT, NVIDIA_EXTRACT):
        if not sha_ok(path):
            errors.append(f"{os.path.basename(path)} fails its manifest")
    records = json.load(open(EXTRACT, encoding="utf-8"))
    if len(records) != 30:
        errors.append(f"the extract holds {len(records)} records, not 30")
    nvidia = json.load(open(NVIDIA_EXTRACT, encoding="utf-8"))
    nv_meta = manifest(NVIDIA_EXTRACT + ".meta.json")
    nvidia_suppliers = sorted({s for r in nvidia for s in suppliers(r)})
    if any(re.search("nvidia", s, re.I) for s in nvidia_suppliers):
        errors.append("a notice now names NVIDIA as its supplier; the notes say none does")
    if nv_meta["aukus_suppliers_palantir_or_nvidia"]:
        errors.append("an AUKUS notice names Palantir or NVIDIA; the notes say none does")

    ledger = []
    for rec in records:
        c = rec["contracts"][0]
        sup = [p for p in rec["parties"] if "supplier" in p.get("roles", [])]
        buy = [p for p in rec["parties"] if "procuringEntity" in p.get("roles", [])]
        if len(sup) != 1 or len(buy) != 1:
            errors.append(f"{c['id']}: expected one supplier and one buyer")
            continue
        abn = next((i["id"] for i in sup[0].get("additionalIdentifiers", []) if i.get("scheme") == "AU-ABN"), None)
        if "palantir technologies" not in sup[0]["name"].lower():
            errors.append(f"{c['id']}: supplier {sup[0]['name']!r} is not Palantir Technologies")
        ledger.append(dict(cn=c["id"], supplier=sup[0]["name"], abn=abn, agency=buy[0]["name"],
                           title=c.get("description"), value=Decimal(c["value"]["amount"]),
                           signed=local_date(c.get("dateSigned")), start=local_date((c.get("period") or {}).get("startDate")),
                           end=local_date((c.get("period") or {}).get("endDate")), status=c.get("status"),
                           method=rec["tender"].get("procurementMethodDetails"),
                           exempt=rec["tender"].get("limitedTenderExempt"),
                           reason=rec["tender"].get("limitedTenderReason"),
                           amendments=len(c.get("amendments") or []),
                           unspsc=sorted({i["classification"]["id"] for i in c.get("items", [])})))
    by_cn = {r["cn"]: r for r in ledger}
    for cn, value in READ_ON_AUSTENDER.items():
        if cn not in by_cn or by_cn[cn]["value"] != Decimal(value):
            errors.append(f"the copy disagrees with the notice read on AusTender: {cn}")
    for r in ledger:
        if r["agency"] not in AGENCY_ENTITY:
            errors.append(f"{r['cn']}: buyer {r['agency']!r} has no entity mapping")
    active = [r for r in ledger if r["status"] != "cancelled"]
    cancelled = [r for r in ledger if r["status"] == "cancelled"]
    if [r["cn"] for r in cancelled] != ["CN2296931"]:
        errors.append("expected exactly one cancelled notice, CN2296931")
    total = sum(r["value"] for r in active)
    by_agency: dict[str, list] = defaultdict(list)
    for r in active:
        by_agency[r["agency"]].append(r)
    parent = [r for r in active if r["abn"] is None]
    asd_parent = [r for r in parent if r["agency"] == "Australian Signals Directorate"]
    limited = [r for r in active if r["method"] == "Limited tender"]
    first = min(active, key=lambda r: r["signed"])
    # Two ASD notices cover the same year: one names the Australian company, one the US parent.
    asd_pair = [by_cn.get("CN3610053"), by_cn.get("CN3652667")]
    if not all(asd_pair) or asd_pair[0]["start"] != asd_pair[1]["start"]:
        errors.append("the two 2019-20 ASD notices no longer share a start date; re-read them")
    if len(asd_parent) != len(by_agency["Australian Signals Directorate"]) - 1:
        errors.append("the notes say every ASD notice but one names the US parent; re-read them")

    # --- the law that decides what can be asked ---------------------------------------------------------
    foi = os.path.join(RAW, "registers", "legislation", "foi-act-1982-C2026C00433.txt")
    foi_s7 = in_text(foi, "The bodies specified in Division 1 of Part I of Schedule 2, and a person holding and "
                          "performing the duties of an office specified in that Division, are to be deemed not to "
                          "be prescribed authorities for the purposes of this Act.")
    foi_sched = in_text(foi, "Part I — Exempt agencies Division 1 Aboriginal Land Councils and Land Trusts Auditor ‑ "
                             "General Australian Secret Intelligence Service Australian Security Intelligence "
                             "Organisation Australian Signals Directorate")
    foi_2a = in_text(foi, "An agency is exempt from the operation of this Act in relation to the following documents: "
                          "(a) a document (an intelligence agency document ) that has originated with, or has been "
                          "received from, any of the following:")
    in_text(foi, "(vii) the Australian Signals Directorate")
    foi_defence = in_text(foi, "Department of Defence, in relation to documents in respect of: (a) the collection, "
                               "reporting or analysis of operational intelligence; or (b) special access programs, "
                               "under which a foreign government provides restricted access to technologies.")
    if not sha_ok(foi[:-4] + ".html"):
        errors.append("the FOI Act archive fails its manifest")

    # --- the certified cloud register -----------------------------------------------------------------
    hcf = os.path.join(RAW, "hcf", "certified-service-providers.20260928125530.html")
    hcf_aws = in_text(hcf, "Amazon Web Services - Cloud Service offering (Australian Regions)")
    absent(hcf, "palantir")

    # --- WA Police's live facial recognition ----------------------------------------------------------
    pia = os.path.join(OPS, "wapolice", "olfr-privacy-impact-assessment")
    if os.path.exists(pia + ".pdf") and not sha_ok(pia + ".pdf"):
        errors.append("the WA Police PIA fails its manifest")
    pia_vendor = quoted(pia + ".txt", "Title Overt Live Facial Recognition (OLFR) Lifecycle Stage Trial proposal "
                                      "Vendor NEC")
    pia_neoface = quoted(pia + ".txt", "Current engagement with NEC is ongoing. If endorsed the technology will be "
                                       "the NEC’s NeoFace Watch technology using the NeoFace M40 algorithm.")
    pia_stored = quoted(pia + ".txt", "Data stored in Australia")
    pia_met = quoted(pia + ".txt", "The proposed trial draws on UK policing models, principally from the "
                                   "Metropolitan Police Service.")
    absent(pia + ".txt", "palantir")

    # --- Coles ------------------------------------------------------------------------------------------
    coles = os.path.join(OPS, "coles")
    itn = os.path.join(coles, "coles-to-end-data-analytics-work-with-palantir-628693.txt")
    acs = os.path.join(coles, "coles-dumps-palantir-after-pressure-campaign.txt")
    cyd = os.path.join(coles, "14146-supermarket-giant-coles-to-cut-ties-with-palantir-in-2027.txt")
    nom = os.path.join(coles, "2026_AGM_Notice_of_Meeting_Web")
    conclude = "Coles and Palantir have agreed to conclude their partnership after three years of collaboration"
    for p in (itn, acs, cyd):
        in_text(p, conclude)
    coles_timing = in_text(itn, "The exact timing is yet to be settled, but the arrangement is not expected to run "
                                "beyond calendar 2027.")
    coles_control = in_text(itn, "The software is deployed within Coles' own environment and is operated and isolated "
                                 "under Coles controls.")
    coles_repurpose = in_text(itn, "Palantir does not control the data, nor can it independently repurpose it")
    getup_itn = in_text(itn, "Advocacy group GetUp! claimed the cessation as a win for a year-long campaign against the "
                             "deal, which gathered 86,000 petition signatures and was pushing for a shareholder vote on "
                             "the partnership at Coles' annual general meeting.")
    getup_email = in_text(acs, "It’s only in the last few weeks, with the shareholder vote around the corner adding yet "
                               "another layer of pressure, that Coles changed tack.")
    coles_cctv = in_text(acs, "Coles also denied that Palantir had access to CCTV, facial recognition or any of its "
                              "crime-prevention measures.")
    getup_westpac = in_text(cyd, "And Palantir still has lucrative contracts with Westpac, Rio Tinto, and a host of "
                                 "government agencies.")
    if os.path.exists(nom + ".pdf") and not sha_ok(nom + ".pdf"):
        errors.append("the Coles notice of meeting fails its manifest")
    nom_items = quoted(nom + ".txt", "Agenda Items 1. Statutory Reports")
    nom_date = quoted(nom + ".txt", "The Coles Group Limited 2026 AGM will be held on Friday 6 November 2026 at 9.30am "
                                    "(AEDT).")
    absent(nom + ".txt", "palantir")

    # --- the keynote quote ------------------------------------------------------------------------------
    sj = os.path.join(OPS, "nvidia_gtc_dc", "transcript-nvidia-ceo-jensen-huangs-keynote-at-gtc-2025.txt")
    sj_event = in_text(sj, "Read the full transcript of NVIDIA CEO Jensen Huang’s keynote speech at NVIDIA GTC 2025 "
                           "Washington, D.C., October 28, 2025.")
    sj_quote = in_text(sj, "We work with Palantir to accelerate everything Palantir does so that we could do data "
                           "processing at a much, much larger scale and more speed")
    sj_tail = in_text(sj, "process that data for our government, for national security, and for enterprises around "
                          "the world")
    keynote_refused = json.load(open(os.path.join(OPS, "nvidia_gtc_dc", "refused.json")))
    if not any("lQHK61IDFH4" in u for u in keynote_refused):
        errors.append("the keynote recording's refusal is not on record")

    # --- WesTrac ----------------------------------------------------------------------------------------
    wt_html = os.path.join(OPS, "palantir", "palantir-continues-expansion-in-australia-with-westrac-partnership.html")
    wt = next_data_text(wt_html)
    wt_deploy = in_text(wt_html, "Palantir and WesTrac announced a partnership to deploy Palantir Foundry across "
                                 "WesTrac’s servicing and rebuild operations centres in Perth, Western Australia.", wt)
    wt_2021 = in_text(wt_html, "WesTrac and Palantir first began collaboration in 2021", wt)
    in_text(wt_html, "PERTH, Australia, Nov. 8, 2022", wt)

    # --- Anthropic and the Western Downs ----------------------------------------------------------------
    dx = os.path.join(OPS, "dexus", "EQS-Adhoc-Dexus-Finance-Pty-Limited-Australian-Data-Centres--Western-Downs-Digit.txt")
    dx_consortium = in_text(dx, "ADC holds a 25% interest in a consortium with Zerra DC and Macquarie Capital "
                                "(Consortium) in connection with the proposed development of a hyperscale data centre "
                                "campus for an Australian subsidiary of Anthropic in the Western Downs region of "
                                "Queensland.")
    dx_lease = in_text(dx, "The Consortium has entered into lease documentation with the Australian subsidiary of "
                           "Anthropic for the delivery of the first stage of the campus, subject to customary approvals.")
    dx_title = in_text(dx, "ASX release 16 September 2026 Australian Data Centres – Western Downs Digital Park")
    dx_dexus = in_text(dx, "Dexus provides the following update in relation to Australian Data Centres (ADC), in which "
                           "Dexus holds an 85% interest.")

    # --- the refusals -----------------------------------------------------------------------------------
    refused = {}
    for d in ("registers/state_tenders", "registers/qld_hansard", "operators/nvidia_gtc_dc", "registers/austender"):
        path = os.path.join(RAW, d, "refused.json")
        if not os.path.exists(path):
            errors.append(f"no refusal recorded at {d}")
            continue
        refused[d] = json.load(open(path))
    if len(refused.get("registers/state_tenders", {})) != 4:
        errors.append("expected four state tender portal refusals (Victoria, South Australia, the ACT, WA)")

    if errors:
        print("refusing to write; fix these first:", file=sys.stderr)
        for e in errors:
            print(f"  {e}", file=sys.stderr)
        return 1

    def archived(path: str) -> str:
        m = manifest(path + ".meta.json")
        return f"sha256 {m['sha256'][:12]}, {m['bytes']:,} bytes"

    def money(v: Decimal) -> str:
        return f"${v:,.2f}"

    full_meta = manifest(EXTRACT + ".meta.json")
    agency_summary = "; ".join(f"{a}: {len(rs)} notices, {money(sum(r['value'] for r in rs))}"
                               for a, rs in sorted(by_agency.items(), key=lambda kv: -sum(r['value'] for r in kv[1])))
    sources = [
        dict(id=SRC_OCDS, title="AusTender contract notices, OCDS feed (Department of Finance), as republished by the "
                                "Open Contracting Partnership's Data Registry",
             publisher="Department of Finance (AusTender); copy held by the Open Contracting Partnership",
             url="https://data.open-contracting.org/en/publication/19", doc_type="primary_government",
             published="2026-10-13", accessed=TODAY, credibility="A",
             notes="The Commonwealth's contract notices from 2007 to October 2026 as the AusTender API publishes them "
                   "(CC BY 3.0 AU), retrieved monthly by the Open Contracting Partnership with minimal transformation; "
                   "this copy was retrieved by the Partnership on 13 October 2026. AusTender's own site and data.gov.au "
                   "both refuse the research crawler (robots.txt), so the full file (260 MB, sha256 "
                   f"{full_meta['derived_from_sha256'][:12]}) was read once and is not committed; the 30 records whose "
                   "supplier is Palantir Technologies, and the records that mention NVIDIA, are, at "
                   "data/raw/registers/open_contracting/ (filter and hash in each manifest; contact points and "
                   "addresses removed, because they can name a person). Checked: the five notices read in full on "
                   "AusTender in September match it value for "
                   "value. Known limits, stated by the Registry: a contract's value and period are its latest after "
                   "amendment, and the feed's counts can differ from the website's. No false matches on the unrelated "
                   "Palantir consultancy."),
        dict(id=SRC_FOI_ACT, title="Freedom of Information Act 1982 (Cth), compilation C2026C00433, 29 September 2026",
             publisher="Federal Register of Legislation (Attorney-General's Department)",
             url=manifest(foi[:-4] + ".html.meta.json")["url"], doc_type="primary_government",
             published="2026-09-29", accessed=TODAY, credibility="A",
             notes="Section 7 and Schedule 2: the Australian Signals Directorate is an exempt agency (Part I, "
                   "Division 1), and any agency is exempt in relation to a document that originated with or was "
                   "received from it (s 7(2A)). The Department of Defence is exempt for documents on operational "
                   "intelligence and special access programs. The ACIC and AUSTRAC are not exempt agencies; AUSTRAC "
                   "intelligence documents are (s 7(2G)). ARCHIVED "
                   f"{TODAY} at data/raw/registers/legislation/ ({archived(foi[:-4] + '.html')})."),
        dict(id=SRC_WAPOL, title="Privacy Impact Assessment: Overt Live Facial Recognition (WA Police Force)",
             publisher="Western Australia Police Force, Technology Portfolio, Innovation",
             url=manifest(pia + ".pdf.meta.json")["url"], doc_type="primary_government", published="2026-05-10",
             accessed=TODAY, credibility="A",
             notes="Dated November 2025 on its cover; version 1.0 of 10 May 2026. Names the vendor as NEC and the "
                   "intended technology as NEC's NeoFace Watch using the NeoFace M40 algorithm, used by the "
                   "Metropolitan Police; states 'Data stored in Australia' and that non-matched biometrics are not "
                   "retained. Does not mention Palantir. Names three police officers, recorded here by role only. "
                   f"ARCHIVED {TODAY} at data/raw/operators/wapolice/ ({archived(pia + '.pdf')}); PDF not committed."),
        dict(id=SRC_COLES_ITN, title="Coles to end data analytics work with Palantir (iTnews, 4 September 2026)",
             publisher="iTnews (nextmedia)",
             url="https://www.itnews.com.au/news/coles-to-end-data-analytics-work-with-palantir-628693",
             doc_type="news", published="2026-09-04", accessed=TODAY, credibility="B",
             notes="Quotes a Coles spokesperson: 'Coles and Palantir have agreed to conclude their partnership after "
                   "three years of collaboration'; timing unsettled but not expected beyond calendar 2027; the "
                   "software runs in Coles' own environment and 'Palantir does not control the data'. Reports GetUp's "
                   "claim of a win after 86,000 signatures. Says the Sydney Morning Herald reported it first. "
                   f"ARCHIVED {TODAY} at data/raw/operators/coles/."),
        dict(id=SRC_COLES_ACS, title="Coles dumps Palantir after pressure campaign (Information Age, ACS, 7 September 2026)",
             publisher="Australian Computer Society, Information Age",
             url="https://ia.acs.org.au/article/2026/coles-dumps-palantir-after-pressure-campaign.html",
             doc_type="news", published="2026-09-07", accessed=TODAY, credibility="B",
             notes="The same Coles statement, Coles' denial that Palantir had access to CCTV or facial recognition, and "
                   "GetUp's email to supporters claiming the decision followed the threat of a shareholder vote. "
                   f"ARCHIVED {TODAY} at data/raw/operators/coles/."),
        dict(id=SRC_COLES_CD, title="Supermarket giant Coles to cut ties with Palantir in 2027 (Cyber Daily, 4 September 2026)",
             publisher="Cyber Daily (Momentum Media)",
             url="https://www.cyberdaily.au/tech/14146-supermarket-giant-coles-to-cut-ties-with-palantir-in-2027",
             doc_type="news", published="2026-09-04", accessed=TODAY, credibility="B",
             notes="The same Coles statement given to Cyber Daily, and GetUp's statement, which asserts that Palantir "
                   "'still has lucrative contracts with Westpac, Rio Tinto, and a host of government agencies' (an "
                   f"advocacy claim, not a record of a Westpac contract). ARCHIVED {TODAY} at data/raw/operators/coles/."),
        dict(id=SRC_COLES_NOM, title="Coles Group 2026 Notice of Annual General Meeting",
             publisher="Coles Group Limited", url=manifest(nom + ".pdf.meta.json")["url"],
             doc_type="primary_company", published="2026-09-15", accessed=TODAY, credibility="A",
             notes="Meeting on 6 November 2026. Five items of business: statutory reports, a director's re-election, "
                   "the remuneration report, and two grants to the Managing Director. None concerns Palantir; the word "
                   f"does not appear. ARCHIVED {TODAY} at data/raw/operators/coles/ ({archived(nom + '.pdf')}); PDF "
                   "not committed."),
        dict(id=SRC_DEXUS, title="Australian Data Centres - Western Downs Digital Park (Dexus ASX release, 16 September 2026)",
             publisher="Dexus (ASX: DXS), distributed by EQS as a regulatory announcement of Dexus Finance Pty Limited",
             url=manifest(dx[:-4] + ".html.meta.json")["url"], doc_type="primary_company", published="2026-09-16",
             accessed=TODAY, credibility="A",
             notes="Dexus's own release, authorised by its General Counsel: Australian Data Centres (85% Dexus) holds "
                   "25% of a consortium with Zerra DC and Macquarie Capital for a hyperscale campus 'for an Australian "
                   "subsidiary of Anthropic in the Western Downs region of Queensland', and the consortium 'has entered "
                   "into lease documentation' for the first stage, 'subject to customary approvals'. Read from the EQS "
                   "copy because ASX's terms limit reuse of its own copies. Anthropic is the company whose model drafts "
                   f"this research: see the RG-012 hunt log. ARCHIVED {TODAY} at data/raw/operators/dexus/."),
        dict(id=SRC_SINGJU, title="Transcript: NVIDIA CEO Jensen Huang's Keynote At GTC 2025 (The Singju Post, 29 October 2025)",
             publisher="The Singju Post", url="https://singjupost.com/transcript-nvidia-ceo-jensen-huangs-keynote-at-gtc-2025/",
             doc_type="other", published="2025-10-29", accessed=TODAY, credibility="C",
             notes="A third-party transcript of the GTC Washington, D.C. keynote of 28 October 2025, independent of "
                   "Sherwood News. Its Palantir passage agrees with Sherwood's, word for word except 'could' for "
                   "'can'. Neither is the recording: YouTube refused the research crawler and its captions are closed "
                   f"to crawlers (data/raw/operators/nvidia_gtc_dc/refused.json). ARCHIVED {TODAY}."),
        dict(id=SRC_WESTRAC, title="Palantir Continues Expansion in Australia with WesTrac Partnership (8 November 2022)",
             publisher="Palantir Technologies",
             url="https://www.palantir.com/newsroom/press-releases/palantir-continues-expansion-in-australia-with-westrac-partnership/",
             doc_type="primary_company", published="2022-11-08", accessed=TODAY, credibility="A",
             notes="Palantir and WesTrac (Caterpillar dealer, Perth) announce Foundry across WesTrac's servicing and "
                   "rebuild operations centres in Perth; collaboration began in 2021 and is to extend to New South "
                   "Wales workshops; describes Rio Tinto as Palantir's 'long-term flagship partnership'. The page "
                   f"serves its text inside embedded page data, read from there. ARCHIVED {TODAY} at "
                   "data/raw/operators/palantir/."),
    ]

    # --- entities ---------------------------------------------------------------------------------------
    austrac = by_agency["Australian Transaction Reports and Analysis Centre"]
    acic = by_agency["Australian Criminal Intelligence Commission"]
    asd = by_agency["Australian Signals Directorate"]
    entities = [
        dict(insert=dict(id="ENT_AUSTRAC", name="Australian Transaction Reports and Analysis Centre (AUSTRAC)",
                         legal_name=None, entity_type="government_agency", domicile="Australia", hq_country="AU",
                         asx_ticker=None, website="austrac.gov.au",
                         notes=f"Australia's financial intelligence agency and anti-money-laundering regulator. Buy-side "
                               f"on {len(austrac)} Palantir notices from 2016 to 2026 worth "
                               f"{money(sum(r['value'] for r in austrac))} at their latest values, the largest a 'Data "
                               f"Analytics capability' (CN3942923, {money(by_cn['CN3942923']['value'])}, to June 2027, "
                               f"amended five times). AUSTRAC intelligence documents are exempt from FOI; its contracts "
                               f"are not.",
                         fact_status="VERIFIED", source_id=SRC_OCDS, confidence="high", as_of_date=TODAY)),
        dict(match=dict(id="ENT_AUSTRAC"), set={},
             add_sources=[dict(id=SRC_OCDS, quote=" | ".join(f"{r['cn']} {r['title']} {money(r['value'])}" for r in austrac))]),
        dict(insert=dict(id="ENT_WESTRAC", name="WesTrac", legal_name=None, entity_type="other",
                         domicile="Australia", hq_country="AU", asx_ticker=None, website="westrac.com.au",
                         notes="Caterpillar equipment dealer headquartered in Perth; Palantir commercial customer since "
                               "2021, with Foundry across its servicing and rebuild operations centres in Perth "
                               "(Palantir release, 8 November 2022). Entity type 'other' - the vocabulary has no "
                               "industrial-services type. RG-088.",
                         fact_status="VERIFIED", source_id=SRC_WESTRAC, confidence="high", as_of_date="2022-11-08")),
        dict(match=dict(id="ENT_WESTRAC"), set={},
             add_sources=[dict(id=SRC_WESTRAC, quote=f"{wt_deploy} | {wt_2021}")]),
        dict(match=dict(id="ENT_COLES"),
             set=dict(fact_status="REPORTED", source_id=SRC_COLES_ITN, confidence="high", as_of_date="2026-09-04",
                      notes="Supermarket chain; Palantir commercial customer since February 2024 (Foundry and AIP for "
                            "rostering, store operations and supply chain across 840+ stores). Investor-day detail (Nov "
                            "2024): executive oversight and workforce management; 24,000 process standards measured in "
                            "15-minute increments. ENDING (RG-095): on 4 September 2026 a Coles spokesperson said 'Coles "
                            "and Palantir have agreed to conclude their partnership after three years of collaboration'; "
                            "the arrangement is not expected to run beyond calendar 2027. Coles gave no other reason, "
                            "said the software runs in its own environment and that 'Palantir does not control the data'. "
                            "GetUp claimed the decision as a campaign win; Coles' 2026 notice of meeting has no item on "
                            "Palantir. Entity type 'other' - the vocabulary has no retail type."),
             add_sources=[dict(id=SRC_COLES_ITN, quote=f"{conclude} | {coles_timing} | {coles_repurpose}"),
                          dict(id=SRC_COLES_NOM, quote=nom_items)]),
        dict(match=dict(id="ENT_PALANTIR_AU"),
             set=dict(as_of_date=TODAY,
                      notes="ABN 48 144 948 309 (as published on AusTender notices). Registered supplier address "
                            "Canberra ACT 2601. LEDGER (RG-086, built 2026-10-22 from the AusTender feed): Palantir "
                            f"is named on {len(active)} Commonwealth notices (not counting one cancelled) from "
                            f"{first['signed'][:4]} to 2026 worth "
                            f"{money(total)} at their latest values ({agency_summary}). This company is named on "
                            f"{len(active) - len(parent)}; the US parent on {len(parent)} ({money(sum(r['value'] for r in parent))}), "
                            "every ASD notice but one among them. Mike Kelly (former defence materiel minister) served "
                            "as Palantir's Australian president 2020-2024 (ABC Four Corners). Paul Rawlins named AU Head "
                            "of Public Sector in Palantir's Nov 2025 IRAP release."),
             add_sources=[dict(id=SRC_OCDS, quote=f"{len(active)} notices; {agency_summary}")]),
        dict(match=dict(id="ENT_ASD"),
             set=dict(as_of_date=TODAY,
                      notes="Commonwealth signals-intelligence agency and cyber security authority. Buy-side on "
                            f"{len(asd)} Palantir notices from 2019 to 2024 worth {money(sum(r['value'] for r in asd))}: "
                            f"yearly software licences and support, all limited tenders, {len(asd_parent)} naming the US "
                            f"parent and {len(asd) - len(asd_parent)} (2019-20) the Australian company, with the same "
                            "start date as a US-parent notice. Sets "
                            "the requirements under which IRAP assessments (including Palantir's PROTECTED-level "
                            "assessment announced 20 Nov 2025) are conducted. EXEMPT FROM FOI: Schedule 2 of the FOI Act "
                            "lists ASD as an exempt agency, and any document originating with it is exempt in any "
                            "agency's hands (s 7(2A)). Crikey reports ASD granted Palantir 'a top security clearance' in "
                            "November 2024 - unverified against any primary record (RG-089)."),
             add_sources=[dict(id=SRC_FOI_ACT, quote=f"{foi_s7} | {foi_sched}"),
                          dict(id=SRC_OCDS, quote=" | ".join(f"{r['cn']} {r['supplier']} {money(r['value'])}" for r in asd))]),
        dict(match=dict(id="ENT_ACIC"),
             set=dict(as_of_date=TODAY,
                      notes=f"National criminal intelligence body. Buy-side on {len(acic)} Palantir notices from 2014 to "
                            f"2025 worth {money(sum(r['value'] for r in acic))}: software licences, maintenance and "
                            "support, the first in 2014. What the platform is used for is not stated on any notice "
                            "(RG-093). Subject to the FOI Act; FOI-004 (docs/requests/) asks what the software supports."),
             add_sources=[dict(id=SRC_OCDS, quote=" | ".join(f"{r['cn']} {r['title']} {money(r['value'])}" for r in acic))]),
        dict(match=dict(id="ENT_ANTHROPIC"),
             set=dict(fact_status="VERIFIED", source_id=SRC_DEXUS, confidence="high", as_of_date="2026-09-16",
                      notes="US AI laboratory. CONFIRMED 2026-10-22 (RG-012) by Dexus's ASX release of 16 September "
                            "2026: a consortium of Zerra DC, Macquarie Capital and Australian Data Centres (85% Dexus) "
                            "'has entered into lease documentation with the Australian subsidiary of Anthropic for the "
                            "delivery of the first stage' of a hyperscale campus in the Western Downs region of "
                            "Queensland, 'subject to customary approvals'. The lodged development application does not "
                            "name Anthropic or Zerra. Earlier reporting of a 5-20 GW Australian build remains unconfirmed. "
                            "Anthropic is the company whose model drafts this research; see the RG-012 hunt log."),
             add_sources=[dict(id=SRC_DEXUS, quote=f"{dx_title} | {dx_lease}")]),
    ]

    sites = [dict(match=dict(id="SITE_WESTERN_DOWNS"), set={},
                  add_sources=[dict(id=SRC_DEXUS, quote=f"{dx_consortium} | {dx_lease}")])]

    # --- the contracts ----------------------------------------------------------------------------------
    contracts, contract_refs = [], []
    for r in sorted(active, key=lambda r: r["signed"]):
        if r["cn"] in READ_ON_AUSTENDER:
            continue  # rows 24 to 30, read in full in September
        extra = []
        if r["amendments"]:
            extra.append(f"amended {r['amendments']} time{'s' if r['amendments'] > 1 else ''}; the value is the latest")
        if r["reason"]:
            extra.append(f"limited tender reason: {r['reason']}")
        elif r["exempt"] == "1":
            extra.append("the feed marks this limited tender as exempt")
        if r["cn"] == "CN3652667":
            extra.append("same start date as CN3610053 (ASD, the Australian company, $678,589.62); the feed does not "
                         "say whether they are one contract re-published or two, so both are kept and neither is "
                         "marked a duplicate")
        contracts.append(dict(insert=dict(
            supplier_entity_id="ENT_PALANTIR_AU" if r["abn"] == PALANTIR_ABN else "ENT_PALANTIR",
            supplier_name=r["supplier"], agency=r["agency"], agency_entity_id=AGENCY_ENTITY[r["agency"]],
            contract_title=f"{r['title']} ({r['cn']})", value_aud=float(r["value"]), value_incl_gst=1,
            portal="AusTender", portal_id=r["cn"], award_published=r["signed"], contract_start=r["start"],
            contract_end=r["end"], method_of_tendering=r["method"], category="UNSPSC " + ", ".join(r["unspsc"]),
            abn=r["abn"], is_duplicate_of=None, duplicate_note=None,
            verification_note="FROM THE AUSTENDER FEED (Open Contracting Partnership copy, retrieved by the Partnership "
                              "13 October 2026); the notice page itself refuses the research crawler and was not read. "
                              + ("; ".join(extra) + "." if extra else ""),
            fact_status="VERIFIED", source_id=SRC_OCDS, confidence="medium", as_of_date="2026-10-13")))
        contract_refs.append(dict(match=dict(portal_id=r["cn"]), set={}, add_sources=[dict(
            id=SRC_OCDS, quote=f"{r['cn']} | {r['supplier']} | {r['agency']} | {r['title']} | {money(r['value'])} | "
                               f"{r['start']} to {r['end']} | {r['method']}")]))
    for cn, rowid in (("CN3992202", 30), ("CN3996124", 29), ("CN4104368", 28), ("CN4115523", 26), ("CN4218984", 25)):
        r = by_cn[cn]
        contract_refs.append(dict(match=dict(id=rowid), set={}, add_sources=[dict(
            id=SRC_OCDS, quote=f"{cn} | {r['supplier']} | {r['agency']} | {r['title']} | {money(r['value'])}")]))

    # --- metrics ----------------------------------------------------------------------------------------
    ledger_note = ("Every Palantir notice in the AusTender feed (RG-086), at each contract's latest value after "
                   "amendment, excluding one cancelled notice (CN2296931, Defence, $1,010,365.99). Includes two ASD "
                   "notices with the same start date that may be one contract re-published ($678,589.62 and "
                   "$682,719.35). Values include GST. Not summed with any state or company figure.")
    metrics = [
        dict(insert=dict(as_of="2026-10-13", scope="Australia - Commonwealth", metric_name="palantir_cth_contract_value_2013_2026",
                         value=float(total), unit="AUD", basis="actual", notes=ledger_note, fact_status="VERIFIED",
                         source_id=SRC_OCDS, confidence="medium", as_of_date="2026-10-13"),
             add_sources=[dict(id=SRC_OCDS, quote=f"{len(active)} notices, {first['cn']} ({first['signed']}) to "
                                                  f"{max(active, key=lambda r: r['signed'])['cn']}; {agency_summary}")]),
        dict(insert=dict(as_of="2026-10-13", scope="Australia - Commonwealth", metric_name="palantir_cth_contract_count_2013_2026",
                         value=float(len(active)), unit="contract notices", basis="actual", notes=ledger_note,
                         fact_status="VERIFIED", source_id=SRC_OCDS, confidence="medium", as_of_date="2026-10-13"),
             add_sources=[dict(id=SRC_OCDS, quote=", ".join(r["cn"] for r in sorted(active, key=lambda r: r["signed"])))]),
        dict(insert=dict(as_of="2026-10-13", scope="Australia - Commonwealth", metric_name="palantir_cth_limited_tender_value_2013_2026",
                         value=float(sum(r["value"] for r in limited)), unit="AUD", basis="actual",
                         notes=f"The {len(limited)} of the {len(active)} notices awarded by limited tender, where one or "
                               "a few suppliers are invited rather than the market. " + ledger_note,
                         fact_status="VERIFIED", source_id=SRC_OCDS, confidence="medium", as_of_date="2026-10-13"),
             add_sources=[dict(id=SRC_OCDS, quote=", ".join(r["cn"] for r in limited))]),
        dict(insert=dict(as_of="2026-10-13", scope="Australia - Commonwealth", metric_name="palantir_cth_us_parent_contract_value",
                         value=float(sum(r["value"] for r in parent)), unit="AUD", basis="actual",
                         notes=f"The {len(parent)} notices naming the US parent, Palantir Technologies Inc., with no "
                               "Australian business number, rather than the Australian company. " + ledger_note,
                         fact_status="VERIFIED", source_id=SRC_OCDS, confidence="medium", as_of_date="2026-10-13"),
             add_sources=[dict(id=SRC_OCDS, quote=" | ".join(f"{r['cn']} {r['agency']}" for r in parent))]),
    ]
    for agency, stem in (("Department of Defence", "defence"), ("Australian Transaction Reports and Analysis Centre", "austrac"),
                         ("Australian Criminal Intelligence Commission", "acic"), ("Australian Signals Directorate", "asd")):
        rs = by_agency[agency]
        metrics.append(dict(
            insert=dict(as_of="2026-10-13", scope="Australia - Commonwealth", metric_name=f"palantir_{stem}_contract_value_2013_2026",
                        value=float(sum(r["value"] for r in rs)), unit="AUD", basis="actual",
                        notes=f"{agency}: {len(rs)} Palantir notices, {min(r['signed'] for r in rs)} to "
                              f"{max(r['signed'] for r in rs)}. " + ledger_note,
                        fact_status="VERIFIED", source_id=SRC_OCDS, confidence="medium", as_of_date="2026-10-13"),
            add_sources=[dict(id=SRC_OCDS, quote=" | ".join(f"{r['cn']} {money(r['value'])}" for r in rs))]))
    defence = by_agency["Department of Defence"]
    metrics += [
        dict(match=dict(id=331),
             set=dict(notes="Crikey's analysis of AusTender: Defence 'has now spent more than $26 million on Palantir "
                            "contracts since 2013'. A floor ('more than'), not an exact total. CHECKED 2026-10-22 "
                            f"(RG-086): the AusTender feed holds {len(defence)} Defence notices with Palantir (not cancelled) from "
                            f"2013 to 2026 worth {money(sum(r['value'] for r in defence))} at their latest values "
                            "(metric palantir_defence_contract_value_2013_2026), plus one cancelled - consistent with "
                            "Crikey's floor."),
             add_sources=[dict(id=SRC_OCDS, quote=" | ".join(f"{r['cn']} {money(r['value'])}" for r in defence))]),
    ]
    for mid in (338, 339):
        metrics.append(dict(match=dict(id=mid), set=dict(notes=(
            "WA Police real-time facial recognition trial (Perth): one mobile van scanned 130,000+ faces in crowded "
            "public spaces in week one; 33 alerts; 19 arrests; two acknowledged false alerts; database ~4,000 people. "
            if mid == 338 else
            "Week-one arrests from the 33 alerts above, including one executed live during the commissioner's media "
            "conference. Two welfare checks; 21 registered sex offenders 'engaged with'. ")
            + "VENDOR NAMED 2026-10-22 (RG-093): WA Police's own privacy impact assessment names NEC and NEC's NeoFace "
              "Watch technology, and states 'Data stored in Australia'. Not a Palantir system."),
            add_sources=[dict(id=SRC_WAPOL, quote=f"{pia_vendor} | {pia_neoface}")]))

    security = [
        dict(match=dict(id=6),
             set=dict(as_of_date=TODAY,
                      notes="Palantir announced IRAP PROTECTED completion under the Information Security Registered "
                            "Assessors Program on 20 Nov 2025, assessed by an independent third-party assessor per ASD "
                            "requirements. Its release states Palantir Platform Australia (PPA) delivers Foundry and AIP "
                            "'hosted in Australian Amazon Web Services (AWS) regions'. sovereign_data_carriage "
                            "deliberately NULL: PPA hosting in Australian AWS regions does not establish that any "
                            "specific Australian deployment (Defence CWD, ASD, ACIC, AUSTRAC) runs on PPA, and IRAP "
                            "PROTECTED is an assessment level, not a sovereignty guarantee (RG-087). CHECKED 2026-10-22: "
                            "the Hosting Certification Framework register lists 'Amazon Web Services - Cloud Service "
                            "offering (Australian Regions)' and does not list Palantir. "
                            f"{len(parent)} of Palantir's Commonwealth notices name the US parent, {len(asd_parent)} of "
                            "them ASD's; ASD is exempt from the FOI Act, so what "
                            "it assessed or cleared cannot be sought from it (RG-089; FOI-003 asks Defence for its own "
                            "records instead). DISCREPANCY: Crikey (17 Feb 2026) states ASD granted Palantir 'a top "
                            "security clearance' in November 2024 - no primary record found; IRAP is not a security "
                            "clearance. The certificate itself was not obtained."),
             add_sources=[dict(id=SRC_HCF, quote=hcf_aws), dict(id=SRC_FOI_ACT, quote=f"{foi_sched} | {foi_2a}")]),
    ]

    # --- the research questions -------------------------------------------------------------------------
    gaps = [
        dict(match=dict(id=86),
             set=dict(status="in_progress", fact_status="VERIFIED", source_id=SRC_OCDS, confidence="medium",
                      as_of_date=TODAY,
                      notes="ADVANCED 2026-10-22 (research batch 4). COMMONWEALTH LEDGER BUILT from the AusTender feed "
                            "(the Open Contracting Partnership's copy; AusTender and data.gov.au refuse the crawler): "
                            f"{len(active)} Palantir notices (not cancelled) from {first['signed']} to 2026 worth {money(total)} "
                            f"at their latest values - {agency_summary}. {len(limited)} were limited tenders "
                            f"({money(sum(r['value'] for r in limited))}); {len(parent)} name the US parent "
                            f"({money(sum(r['value'] for r in parent))}). One more, Defence CN2296931 ($1,010,365.99), "
                            "is cancelled. The feed matches all five notices read on AusTender in September. Defence's "
                            f"{money(sum(r['value'] for r in defence))} is consistent with Crikey's 'more than $26 "
                            "million'. REFUSED: the Victorian, South Australian and ACT portals (HTTP 403) and WA's "
                            "(robots.txt), with buy.nsw from batch 3 (data/raw/registers/); in docs/requests/DOWNLOADS.md. "
                            "Still open: state contracts, and the call-offs under panel SON3490955."),
             add_sources=[dict(id=SRC_OCDS, quote=f"{len(active)} notices; {agency_summary}")]),
        dict(match=dict(id=87),
             set=dict(status="in_progress", as_of_date=TODAY,
                      notes="ADVANCED 2026-10-22 (research batch 4). What the public record holds: Palantir says its "
                            "Australian platform is 'hosted in Australian Amazon Web Services (AWS) regions'; the "
                            "Hosting Certification Framework register lists AWS's Australian regions and not Palantir; "
                            f"{len(parent)} of the Commonwealth's notices name the US parent. No notice says where a deployment "
                            "runs. ASD is exempt from the FOI Act (Schedule 2), so the residency question can be put "
                            "only to Defence: FOI-002 (docs/requests/) asks for the hosting and data-location terms of "
                            "Defence's three current Palantir contracts, framed around location and jurisdiction, not "
                            "capability, with the operational-intelligence exemption in mind."),
             add_sources=[dict(id=SRC_HCF, quote=hcf_aws), dict(id=SRC_FOI_ACT, quote=f"{foi_sched} | {foi_defence}")]),
        dict(match=dict(id=88),
             set=dict(status="in_progress", as_of_date=TODAY,
                      notes="ADVANCED 2026-10-22 (research batch 4). WesTrac VERIFIED from Palantir's own release (8 Nov "
                            "2022; Foundry in its Perth rebuild centres since 2021; ENT_WESTRAC). Coles is ending its "
                            "arrangement (RG-095). Westpac: still only Crikey's report of a Palantir executive's LinkedIn "
                            "post, now joined by GetUp's statement that Palantir 'still has lucrative contracts with "
                            "Westpac' - an advocacy claim, not a record. No Westpac entity until a primary record or a "
                            "second reported source appears. Qantas, Transurban, Nuix and VMO stay out (triage)."),
             add_sources=[dict(id=SRC_WESTRAC, quote=wt_deploy), dict(id=SRC_COLES_CD, quote=getup_westpac)]),
        dict(match=dict(id=89),
             set=dict(status="in_progress", as_of_date=TODAY,
                      notes="WORKED 2026-10-22 (research batch 4). The question cannot be put to ASD: Schedule 2 of the "
                            "FOI Act lists it as an exempt agency, and documents that originated with it are exempt in "
                            "any agency's hands. Not on the public record: no ASD list names Palantir, and the Hosting "
                            "Certification Framework register (which certifies hosting, not software) lists AWS's "
                            "Australian regions but not Palantir. Route now: FOI-003 to Defence for its OWN records of "
                            "any Defence Industry Security Program membership or facility clearance held by Palantir "
                            "Technologies Australia, and of any review of Palantir's IRAP assessment, 2024-2025; and a "
                            "right-of-reply question to Crikey about its source. Both claims stay sourced, neither fact."),
             add_sources=[dict(id=SRC_FOI_ACT, quote=f"{foi_s7} | {foi_sched}"), dict(id=SRC_HCF, quote=hcf_aws)]),
        dict(match=dict(id=90),
             set=dict(status="in_progress", as_of_date=TODAY,
                      notes="WORKED 2026-10-22 (research batch 4). In the AusTender feed (2007 to October 2026) no "
                            f"notice names NVIDIA as supplier: {len(nvidia)} buy NVIDIA products through resellers, none "
                            f"of them AUKUS work. Only {nv_meta['aukus_records']} notices mention AUKUS at all, and "
                            "neither supplier is Palantir or NVIDIA. The "
                            f"{len(active)} Palantir notices are software licences, support, data services and "
                            "analytics. Search summaries found Pillar II awards to other companies only (leads, in the "
                            "hunt log). defence.gov.au did not answer the crawler. Still unevidenced, so still not "
                            "asserted: any Palantir or NVIDIA Pillar II work. Kelly's post-separation conditions: not "
                            "found; the absence stays the working finding."),
             add_sources=[dict(id=SRC_OCDS, quote=" | ".join(
                 f"{r['contracts'][0]['id']} {', '.join(suppliers(r))}: {r['contracts'][0].get('description', '')}"
                 for r in nvidia))]),
        dict(match=dict(id=92),
             set=dict(status="in_progress", as_of_date=TODAY,
                      notes="ADVANCED 2026-10-22 (research batch 4). A second, independent transcript (The Singju Post) "
                            "agrees with Sherwood's: 'We work with Palantir to accelerate everything Palantir does so "
                            "that we could do data processing at a much, much larger scale and more speed ... process "
                            "that data for our government, for national security, and for enterprises around the "
                            "world'. The recording itself REFUSED the crawler (YouTube, HTTP 429; captions closed by "
                            "robots.txt). The quote stays REPORTED; a person can check it at about 1:25:14 of the "
                            "recording (docs/requests/DOWNLOADS.md)."),
             add_sources=[dict(id=SRC_SINGJU, quote=f"{sj_event} | {sj_quote} ... {sj_tail}")]),
        dict(match=dict(id=93),
             set=dict(status="in_progress", as_of_date=TODAY,
                      notes="ADVANCED 2026-10-22 (research batch 4). WA: the live facial recognition trial runs on NEC, "
                            "named in WA Police's own privacy impact assessment (NeoFace Watch, M40 algorithm; 'Data "
                            "stored in Australia'); it does not mention Palantir. COMMONWEALTH: the ledger shows the "
                            f"ACIC has bought Palantir software since 2014 ({len(acic)} notices, "
                            f"{money(sum(r['value'] for r in acic))}) and AUSTRAC since 2016 ({len(austrac)} notices, "
                            f"{money(sum(r['value'] for r in austrac))}); no AFP or Home Affairs notice. What either "
                            "agency runs on it is not stated. State police: the state portals refused (RG-086). FOI-004 "
                            "to the ACIC asks what the software supports. The separation rule stands: no Palantir row "
                            "links to an Australian policing capability without a primary source."),
             add_sources=[dict(id=SRC_WAPOL, quote=f"{pia_vendor} | {pia_stored}"),
                          dict(id=SRC_OCDS, quote=" | ".join(f"{r['cn']} {r['agency']}" for r in acic + austrac))]),
        dict(match=dict(id=95),
             set=dict(status="resolved", resolved_date=TODAY, fact_status="REPORTED", source_id=SRC_COLES_ITN,
                      confidence="high", as_of_date="2026-09-04",
                      notes="RESOLVED 2026-10-22 (research batch 4). Yes: on 4 September 2026 Coles told iTnews, Cyber "
                            "Daily and others that 'Coles and Palantir have agreed to conclude their partnership after "
                            "three years of collaboration'; the arrangement is not expected to run beyond calendar 2027. "
                            "The reason Coles gave is none: the statement praises the software and denies it was used "
                            "for surveillance. The campaign as cause is GetUp's claim (86,000 signatures; a push for a "
                            "shareholder vote). No Coles release or ASX statement was found; Coles' 2026 notice of "
                            "meeting (15 September) has no item on Palantir. REPORTED, not VERIFIED: the statement "
                            "exists as three outlets quote it."),
             add_sources=[dict(id=SRC_COLES_ITN, quote=f"{conclude} | {coles_timing} | {getup_itn}"),
                          dict(id=SRC_COLES_ACS, quote=f"{coles_cctv} | {getup_email}"),
                          dict(id=SRC_COLES_CD, quote=conclude), dict(id=SRC_COLES_NOM, quote=nom_date)]),
        dict(match=dict(id=12),
             set=dict(status="resolved", resolved_date=TODAY, fact_status="VERIFIED", source_id=SRC_DEXUS,
                      confidence="high", as_of_date="2026-09-16",
                      notes="RESOLVED 2026-10-22 (research batch 4). CONFLICT OF INTEREST: Anthropic's model drafts "
                            "this research; the author should read the sources directly. Dexus's ASX release of 16 "
                            "September 2026 confirms the relationship: a consortium of Zerra DC, Macquarie Capital and "
                            "Dexus's Australian Data Centres 'has entered into lease documentation with the Australian "
                            "subsidiary of Anthropic for the delivery of the first stage' of the Western Downs campus, "
                            "'subject to customary approvals'. The development application was obtained in September "
                            "(SRC_WDDP_TPR): it names neither Anthropic nor Zerra. Not public: the lease's term, price "
                            "and capacity, and which approvals remain."),
             add_sources=[dict(id=SRC_DEXUS, quote=f"{dx_consortium} | {dx_lease} | {dx_dexus}")]),
    ]

    pack = {
        "pack_id": "whose-data-2026-10",
        "prepared_by": "scripts/curate_whose_data.py",
        "prepared_on": TODAY,
        "sources": sources,
        "rows": {
            "entities": entities,
            "sites": sites,
            "gov_contracts": contracts + contract_refs,
            "metrics": metrics,
            "security_records": security,
            "research_gaps": gaps,
        },
    }
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(pack, fh, indent=1, ensure_ascii=False)
    print(f"wrote {OUT}: {len(sources)} sources, {len(contracts)} new contract notices "
          f"({len(active)} not cancelled, {money(total)}), "
          f"{sum(len(v) for v in refused.values())} refusals on record")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
