#!/usr/bin/env python3
"""
Curate research batch 2, "Your super, your savings" and "The OpenAI deal" (docs/RESEARCH-PLAN.md,
story lines M2 and M5).

M2 asks whose money is in Australian data centres. Four free records answer part of it:

  1. Super funds' portfolio holdings disclosures. Cbus, HESTA and Hostplus publish a file per
     investment option, twice a year; each was archived by scrapers/archive_pages.py under
     data/raw/superannuation/. AustralianSuper, UniSuper, Australian Retirement Trust, CSC and the
     Future Fund refused the research crawler, and Aware Super's robots.txt excludes its files;
     every refusal is in that folder's refused.json and none was worked around.
  2. NEXTDC's FY26 annual report, which lists the substantial holders the ASX was told about.
  3. NEXTDC's releases on who funds its build (La Caisse's hybrid commitment, bank debt).
  4. The Future Fund's December 2025 holdings file, archived in September by the Palantir thread.

M5 asks what NEXTDC and OpenAI agreed for S7. NEXTDC's own release of 5 December 2025 is the
only primary statement read: a memorandum of understanding. Every NEXTDC report since is checked
below for the word OpenAI, and the script refuses to write if one now carries it, because the notes
say none does.

Every quote is checked against its archive and the script refuses to write a pack if one is
missing. A fund's holding is recorded as the fund reports it, for the option the file covers;
nothing is summed across options or funds.

Run:
    python3 scripts/curate_super_and_openai.py
    python3 scripts/load_pack.py data/packs/super_and_openai.json --allow-missing-source
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "data", "packs", "super_and_openai.json")
RAW = os.path.join(ROOT, "data", "raw")
SUPER = os.path.join(RAW, "superannuation")
NXT = os.path.join(RAW, "operators", "nextdc")
FF = os.path.join(RAW, "futurefund", "futurefund_pir_2025-12-31.csv")
ASX_LIST = os.path.join(RAW, "asx", "nxt", "announcements.do.txt")
EIS = os.path.join(RAW, "nsw_planning", "documents", "SSD-92743706_eis.txt")
TODAY = "2026-10-22"

SRC_CBUS = "SRC_CBUS_PHD_202606"
SRC_HESTA = "SRC_HESTA_PHD_202606"
SRC_HOSTPLUS = "SRC_HOSTPLUS_PHD_202606"
SRC_MOU = "SRC_NXT_OPENAI_MOU_2025"
SRC_AR = "SRC_NXT_FY26_ANNUAL_REPORT"
SRC_FY26 = "SRC_NXT_FY26_PRESENTATION"
SRC_1H26 = "SRC_NXT_1H26_PRESENTATION"
SRC_HYBRID = "SRC_NXT_HYBRID_LA_CAISSE"
SRC_LIQUIDITY = "SRC_NXT_LIQUIDITY_MAY26"
SRC_ASX = "SRC_ASX_NXT_ANNOUNCEMENTS_2025"
SRC_FF = "SRC_FF_PIR_DEC25"

errors: list[str] = []


def spaceless(text: str) -> str:
    return re.sub(r"\s+", "", text).lower()


def text_of(path: str) -> str:
    return open(path, encoding="utf-8").read()


def verified(path: str) -> bytes:
    """The archived bytes, refused if they no longer match the manifest's SHA-256."""
    raw = open(path, "rb").read()
    meta = json.load(open(path + ".meta.json"))
    if hashlib.sha256(raw).hexdigest() != meta["sha256"]:
        errors.append(f"{os.path.relpath(path, ROOT)} fails its SHA-256 check")
    return raw


def in_text(path: str, quote: str) -> str:
    if spaceless(quote) not in spaceless(text_of(path)):
        errors.append(f"{os.path.relpath(path, ROOT)} does not hold {quote[:70]!r}")
    return quote


def quoted(path: str, quote: str) -> str:
    """'pN: quote' from a PDF's page-marked text, refusing a quote the archive does not hold."""
    for m in re.finditer(r"\[\[page (\d+)\]\]\n(.*?)(?=\n\[\[page \d+\]\]|\Z)", text_of(path), re.S):
        if spaceless(quote) in spaceless(m.group(2)):
            return f"p{m.group(1)}: {quote}"
    errors.append(f"{os.path.relpath(path, ROOT)} does not hold {quote[:70]!r}")
    return quote


def csv_line(path: str, line: str) -> str:
    """A line of a holdings file, verbatim. The file is checked against its manifest first."""
    # Hostplus's file carries a few Windows-1252 bytes in names; the lines quoted here are plain ASCII.
    lines = verified(path).decode("utf-8-sig", errors="replace").splitlines()
    if line not in lines:
        errors.append(f"{os.path.relpath(path, ROOT)} has no line {line[:70]!r}")
    return line


def absent(path: str, pattern: str) -> None:
    if re.search(pattern, text_of(path), re.I):
        errors.append(f"{os.path.relpath(path, ROOT)} now matches {pattern!r}; the notes say it does not")


def manifest(path: str) -> dict:
    return json.load(open(path + ".meta.json"))


def main() -> int:
    # --- the super funds' own files ----------------------------------------------------------------
    cbus_csv = os.path.join(SUPER, "cbus", "super-growth.csv")
    cbus_page = os.path.join(SUPER, "cbus", "cbus-investment-holdings.txt")
    cbus_head = csv_line(cbus_csv, "Portfolio Holdings Information for Investment Option: Growth Accumulation "
                                   "Option - Assets - 30 June 2026,,,,,,,,,,,,,")
    cbus_shares = csv_line(cbus_csv, "Listed equities,04,NEXTDC LTD,,,,,B5LMKP4,,,, 23629033.32,344511305.86,0.4048 %")
    cbus_notes = csv_line(cbus_csv, "Fixed income internal,02,,,,NEXTDC LTD CALLABLE MEDIUM TERM NOTE VARIABLE,,,,,,, "
                                    "18587879.90,0.0218 %")
    cbus_stack = csv_line(cbus_csv, "Fixed income internal (PRIVATE DEBT),02,,,,STACK INFRASTRUCTURE AUSTRALIA "
                                    "(PALMERS ROAD) PTY LTD,,,,,,,,")
    cbus_private = csv_line(cbus_csv, "Fixed income internal,02,,,,PRIVATE DEBT,,,,,,,961424965.53,1.1297 %")
    in_text(cbus_page, "We are required to publish where each investment option invests for 31 December and 30 June "
                       "every year across super, transition to retirement and retirement.")
    cbus_date = in_text(cbus_page, "The information published below is for 30 June 2026.")
    cbus_option = in_text(cbus_page, "Growth (MySuper)")

    hesta_csv = os.path.join(SUPER, "hesta", "Balanced-Growth-super-assets.csv")
    hesta_page = os.path.join(SUPER, "hesta", "portfolio-holdings.txt")
    hesta_shares = csv_line(hesta_csv, "30/06/2026,Balanced Growth,Listed Equity,,NEXTDC Ltd,5042709.981097,"
                                       "73522711.524395,0.00092264,,,,AU000000NXT8")
    in_text(hesta_page, "Holdings calculated as at 30 June 2026.")

    hostplus_csv = os.path.join(SUPER, "hostplus", "Balanced.csv")
    hostplus_page = os.path.join(SUPER, "hostplus", "investment-holdings-by-investment-option.txt")
    hostplus_shares = csv_line(hostplus_csv, 'NEXTDC LTD,AU000000NXT8,"7,485,373.95","109,136,752",0.11%')
    csv_line(hostplus_csv, "HC Balanced - Class A Option,,,,")
    # The file carries no date of its own; the page that links it does.
    hostplus_date = in_text(hostplus_page, "Investment holdings by investment option As at 30 June 2026")

    ff_nxt_eq = csv_line(FF, 'Listed Equity,,,,NextDC Ltd.,,,B5LMKP4,,"6,289,407","78,806,270",0.03%,')
    ff_nxt_prop = csv_line(FF, 'Listed Property,,,,NextDC Ltd.,,,B5LMKP4,,"529,664","6,636,690",0.00%,')
    ff_cdc = csv_line(FF, "Unlisted Infrastructure,Internally,,,CDC,,,,29%,,,,")
    ff_nvda = csv_line(FF, 'Listed Equity,,,,NVIDIA Corp.,,,2379504,,"7,534,692","2,107,250,593",0.78%,')
    csv_line(FF, "Reporting Date: ,31/12/2025,,,,,,,,,,,")

    # --- NEXTDC's own record -----------------------------------------------------------------------
    ar = os.path.join(NXT, "FY26_Annual_Report_Appendix_4E.txt")
    holders_basis = quoted(ar, "Substantial holders in the Company based on ASX lodgements up until 20 August 2026")
    holders = quoted(ar, "State Street Corporation 79,701,811 10.48 % AustralianSuper Pty Ltd 54,446,234 8.49 % "
                         "BlackRock Group 40,226,111 6.27 % Vanguard Group 38,639,037 6.02 %")
    ar_partners = quoted(ar, "the Group continues to evaluate capital partnership structures across its development "
                             "portfolio, including S4 and S7")
    ar_s7_entity = quoted(ar, "NEXTDC S7 Holdings Pty Ltd Body corporate - 100 % Australia")

    fy26 = os.path.join(NXT, "NEXTDC_FY26_Results_Presentation.txt")
    fy26_s7 = quoted(fy26, "S7 SYDNEY Total power planned ~550MW+1 Initial capacity TBD Status Design & Town Planning")
    fy26_jvco = quoted(fy26, "The Company continues its evaluation of partnering with third party capital through a "
                             "JVCo structure for S4, S7 and M5")

    h1 = os.path.join(NXT, "1H26_Results_Presentation.txt")
    h1_fast = quoted(h1, "S7 granted fast track status under the NSW Government’s Investment Delivery Authority "
                         "(IDA) program")
    h1_adviser = quoted(h1, "Barrenjoey has been appointed as Lead Financial Adviser to support these programs")

    mou = os.path.join(NXT, "building-the-next-generation-of-sovereign-ai-infrastructure-in-australia.txt")
    mou_agreed = in_text(mou, "confirms that it has agreed a Memorandum of Understanding (“MoU”) with OpenAI, enabling "
                              "Australia to become a regional infrastructure partner under the Open AI for Countries "
                              "program.")
    mou_scope = in_text(mou, "Through the MoU, OpenAI and NEXTDC will collaborate on the planning, development and "
                             "operation of a next-generation hyperscale AI campus and large-scale GPU supercluster at "
                             "NEXTDC’s S7 site in Eastern Creek, Sydney.")
    mou_timing = in_text(mou, "Subject to securing necessary approvals, the first phase of the S7 project is expected to "
                              "be delivered in the second half of calendar 2027.")
    # The release states no price, term, capacity commitment or stake. Checked, so the notes stay true.
    for word in (r"\$\s?\d", r"\bA\$", r"\bMW\b", r"offtake", r"equity", r"\bterm\b", r"price"):
        mou_body = text_of(mou)
        start = mou_body.find("TL;DR")
        end = mou_body.find("Authorised for release", start)
        if re.search(word, mou_body[start:end], re.I):
            errors.append(f"the MoU release now matches {word!r}; the notes say it states no such term")

    hybrid = os.path.join(NXT, "a1.0-billion-hybrid-securities-offer-and-la-caisse-commitment.txt")
    hybrid_commit = in_text(hybrid, "The Hybrid Securities Offer is supported by a A$1.0 billion binding commitment from "
                                    "La Caisse, a global investment group based in Québec, Canada")
    hybrid_debt = in_text(hybrid, "There are no equity conversion features associated with the Hybrid Securities.")
    liquidity = os.path.join(NXT, "nextdc-bolsters-liquidity-to-a8.4-billion-to-accelerate-ai-infrastructure-rollou.txt")
    liq_caisse = in_text(liquidity, "expanded its hybrid securities program, supported by A$1.7 billion in binding "
                                    "commitments from La Caisse")
    liq_banks = in_text(liquidity, "A$1.8 billion in new senior debt commitments from a syndicate of domestic and "
                                   "international banks")

    s7_page = os.path.join(NXT, "s7-sydney.txt")
    s7_size = in_text(s7_page, "Planned for Eastern Creek, S7 Sydney is a future 550MW+ hyperscale data centre")

    asx_letter = in_text(ASX_LIST, "12/12/2025 3:57 pm Response to ASX Compliance Letter")
    in_text(ASX_LIST, "05/12/2025 1:28 pm NEXTDC joins OpenAI for Australia as Infrastructure Partner")

    # Every NEXTDC report read since the release. None names OpenAI; if one ever does, re-read it.
    silent = ["1H26_Results_Announcement.txt", "1H26_Results_Presentation.txt", "1H26_Reports_and_Accounts.txt",
              "record-contracted-growth-and-a2.2bn-capital-plan-to-scale-ai-ready-infrastructur.txt",
              "a1.0-billion-hybrid-securities-offer-and-la-caisse-commitment.txt",
              "nextdc-bolsters-liquidity-to-a8.4-billion-to-accelerate-ai-infrastructure-rollou.txt",
              "FY26_Results_Announcement.txt", "NEXTDC_FY26_Results_Presentation.txt",
              "FY26_Annual_Report_Appendix_4E.txt", "s7-sydney.txt"]
    for name in silent:
        absent(os.path.join(NXT, name), r"open\s*ai")

    # --- Mamre Road: the site is one lot ----------------------------------------------------------
    eis_site = quoted(EIS, "The site is legally described as Lot 10 Deposited Plan (DP) 1280592 and is located at 706 "
                           "-752 Mamre Road, Kemps Creek")
    eis_area = quoted(EIS, "comprises a total area of approximately 522,477m² (52.2ha)")
    eis_roads = quoted(EIS, "internal roads connecting to adjacent developments (Yiribana Logistics Estate, Gibb Group, "
                            "and Frasers Pr operty Industrial sites)")

    # --- refusals the notes rely on ----------------------------------------------------------------
    refused = {}
    for fund in ("futurefund", "csc", "australiansuper", "unisuper", "art", "aware"):
        path = os.path.join(SUPER, fund, "refused.json")
        if not os.path.exists(path):
            errors.append(f"no refusal recorded for {fund}")
            continue
        refused[fund] = json.load(open(path))

    if errors:
        print("refusing to write; fix these first:", file=sys.stderr)
        for e in errors:
            print(f"  {e}", file=sys.stderr)
        return 1

    def phd(fund_id, fund, option, csv_path, page_path, publisher):
        m, p = manifest(csv_path), manifest(page_path.replace(".txt", ".html"))
        return dict(id=fund_id, title=f"{fund} portfolio holdings disclosure, {option} option, 30 June 2026",
                    publisher=publisher, url=m["url"], doc_type="primary_company", published="2026-06-30",
                    accessed=TODAY, credibility="A",
                    notes=f"Every asset the option held at 30 June 2026, as the fund publishes it twice a year. "
                          f"ARCHIVED {TODAY} at data/raw/superannuation/ with SHA-256 manifests: the file "
                          f"(sha256 {m['sha256'][:12]}, {m['bytes']:,} bytes) and the page that links it "
                          f"({p['url']}, sha256 {p['sha256'][:12]}), which gives the date. One option only: "
                          f"the fund's other options hold their own amounts, which are not added here.")

    sources = [
        phd(SRC_CBUS, "Cbus", "Growth (MySuper)", cbus_csv, cbus_page, "Cbus Super"),
        phd(SRC_HESTA, "HESTA", "Balanced Growth", hesta_csv, hesta_page, "HESTA"),
        phd(SRC_HOSTPLUS, "Hostplus", "Balanced", hostplus_csv, hostplus_page, "Hostplus"),
        dict(id=SRC_MOU, title="NEXTDC to Join OpenAI in Australia as an Infrastructure Partner (ASX announcement, "
                               "5 December 2025)",
             publisher="NEXTDC Limited", url=manifest(mou.replace(".txt", ".html"))["url"],
             doc_type="primary_company", published="2025-12-05", accessed=TODAY, credibility="A",
             notes="NEXTDC's own copy of its 1:28 pm ASX announcement of 5 December 2025 (the ASX lists it as "
                   "'NEXTDC joins OpenAI for Australia as Infrastructure Partner'). It confirms a Memorandum of "
                   "Understanding with OpenAI under the OpenAI for Countries program, to collaborate on planning, "
                   "development and operation of an AI campus at S7, first phase expected in the second half of "
                   "2027 subject to approvals. It states no price, contract term, capacity commitment or stake. "
                   f"ARCHIVED {TODAY} at data/raw/operators/nextdc/ with a SHA-256 manifest."),
        dict(id=SRC_AR, title="NEXTDC FY26 Annual Report and Appendix 4E", publisher="NEXTDC Limited",
             url=manifest(ar.replace(".txt", ".pdf"))["url"], doc_type="primary_company", published="2026-08-27",
             accessed=TODAY, credibility="A",
             notes="Lodged with the ASX on 27 August 2026. Shareholder information lists the substantial holders "
                   "based on ASX lodgements up to 20 August 2026; the list of subsidiaries at 30 June 2026 includes "
                   "NEXTDC S7 Holdings Pty Ltd, S7 Holdings MidCo and two S7 trusts, all 100% owned. The report "
                   f"does not mention OpenAI. ARCHIVED {TODAY} (PDF not committed; text and manifest are)."),
        dict(id=SRC_FY26, title="NEXTDC FY26 Results Presentation", publisher="NEXTDC Limited",
             url=manifest(fy26.replace(".txt", ".pdf"))["url"], doc_type="primary_company", published="2026-08-27",
             accessed=TODAY, credibility="A",
             notes="S7 Sydney: total power planned about 550 MW, initial capacity 'TBD', status design and town "
                   "planning; NEXTDC continues to evaluate third-party capital through a joint venture company for "
                   f"S4, S7 and M5. Does not mention OpenAI. ARCHIVED {TODAY} (PDF not committed)."),
        dict(id=SRC_1H26, title="NEXTDC 1H26 Results Presentation", publisher="NEXTDC Limited",
             url=manifest(h1.replace(".txt", ".pdf"))["url"], doc_type="primary_company", published="2026-02-25",
             accessed=TODAY, credibility="A",
             notes="Half year to 31 December 2025, the half in which the OpenAI memorandum was announced. Says S7 "
                   "was granted fast-track status under the NSW Investment Delivery Authority, and that Barrenjoey "
                   "was appointed lead financial adviser for the joint venture funding of S4 and S7. Does not "
                   f"mention OpenAI. ARCHIVED {TODAY} (PDF not committed)."),
        dict(id=SRC_HYBRID, title="A$1.0 billion Hybrid Securities Offer and La Caisse Commitment",
             publisher="NEXTDC Limited", url=manifest(hybrid.replace(".txt", ".html"))["url"],
             doc_type="primary_company", published="2026-04-06", accessed=TODAY, credibility="A",
             notes="Subordinated 100-year hybrid securities, classified as debt, with no equity conversion; a "
                   "A$1.0bn binding commitment from La Caisse, 'a global investment group based in Québec, Canada'. "
                   f"ARCHIVED {TODAY} at data/raw/operators/nextdc/."),
        dict(id=SRC_LIQUIDITY, title="NEXTDC bolsters liquidity to A$8.4 billion to accelerate AI infrastructure "
                                     "rollout",
             publisher="NEXTDC Limited", url=manifest(liquidity.replace(".txt", ".html"))["url"],
             doc_type="primary_company", published="2026-05-08", accessed=TODAY, credibility="A",
             notes="A$1.8bn of new senior debt from domestic and international banks; a A$1.5bn entitlement offer; "
                   "hybrid securities supported by A$1.7bn of binding commitments from La Caisse; A$750m of "
                   f"subordinated wholesale notes. ARCHIVED {TODAY} at data/raw/operators/nextdc/."),
        dict(id=SRC_ASX, title="ASX company announcements, NEXTDC Limited (NXT), released in 2025",
             publisher="ASX", url=manifest(ASX_LIST.replace(".txt", ".html"))["url"], doc_type="primary_regulator",
             published="2025-12-31", accessed=TODAY, credibility="A",
             notes="The exchange's own list of NEXTDC's 2025 announcements, with dates, times and headlines. Lists "
                   "'Response to ASX Compliance Letter' at 3:57 pm on 12 December 2025, a week after the OpenAI "
                   "announcement. The documents themselves sit behind ASX's terms of use, which limit free use to "
                   "private investors, so none was opened; a person must read the compliance letter response "
                   f"(docs/requests/DOWNLOADS.md). The list page ARCHIVED {TODAY} at data/raw/asx/nxt/."),
        # Re-declared in full because the loader upserts sources; the notes gain the archive line.
        dict(id="SRC_NEXTDC_S7", title="S7 Sydney Data Centre - In Planning", publisher="NEXTDC",
             url="https://www.nextdc.com/data-centres/sydney-data-centres/s7-sydney", doc_type="primary_company",
             published="2026", accessed=TODAY, credibility="A",
             notes="Planned for Eastern Creek; described by the proponent as a 550 MW+ hyperscale facility. "
                   f"ARCHIVED {TODAY} at data/raw/operators/nextdc/s7-sydney with a SHA-256 manifest; the page as "
                   "archived does not mention OpenAI."),
    ]

    entities = [
        dict(insert=dict(id="ENT_LA_CAISSE", name="La Caisse", entity_type="investor", domicile="Canada",
                         hq_country="CA",
                         notes="Described by NEXTDC as 'a global investment group based in Québec, Canada'. "
                               "Committed A$1.0bn to NEXTDC's subordinated hybrid securities on 6 April 2026; by 8 "
                               "May 2026 NEXTDC described A$1.7bn of binding commitments from La Caisse. The "
                               "securities are classified as debt and carry no equity conversion. Its final "
                               "allocation is not stated in any record read.",
                         fact_status="VERIFIED", confidence="high", as_of_date=TODAY, source_id=SRC_HYBRID)),
        # The loader registers add_sources only on an update, so the citations follow the insert.
        dict(match=dict(id="ENT_LA_CAISSE"), set={},
             add_sources=[dict(id=SRC_HYBRID, quote=hybrid_commit), dict(id=SRC_LIQUIDITY, quote=liq_caisse)]),
        dict(match=dict(id="ENT_AUSTRALIANSUPER"),
             set=dict(legal_name="AustralianSuper Pty Ltd", fact_status="VERIFIED", source_id=SRC_AR,
                      confidence="high", as_of_date=TODAY,
                      notes="A substantial holder of NEXTDC: 54,446,234 shares, 8.49% of issued shares, in the "
                            "substantial holders NEXTDC's FY26 annual report lists from ASX lodgements up to 20 "
                            "August 2026; the second largest after State Street Corporation. Its own portfolio "
                            "holdings disclosure could not be read: australiansuper.com refused the research "
                            "crawler on 22 October 2026 (RG-004). CORRECTED 2026-10-22: this was a placeholder "
                            "citing CertifiedStrategic.com (RG-100); it now rests on NEXTDC's annual report."),
             add_sources=[dict(id=SRC_AR, quote=holders)]),
    ]

    ownership = [
        dict(insert=dict(
                 holder_id="ENT_AUSTRALIANSUPER", target_id="ENT_NEXTDC", stake_pct=8.49, instrument="equity",
                 event="substantial holding, as last lodged with the ASX",
                 notes="NEXTDC's FY26 annual report lists four substantial holders from ASX lodgements up to 20 August "
                       "2026: State Street Corporation 79,701,811 shares (10.48%), AustralianSuper Pty Ltd 54,446,234 "
                       "(8.49%), BlackRock Group 40,226,111 (6.27%) and Vanguard Group 38,639,037 (6.02%). Each "
                       "percentage is of the shares on issue when that holder last lodged, so they do not share one "
                       "base. Only AustralianSuper is recorded as a row: the others are not yet entities here.",
                 fact_status="VERIFIED", source_id=SRC_AR, confidence="high", as_of_date="2026-08-20"),
             add_sources=[dict(id=SRC_AR, quote=f"{holders_basis} | {holders}")]),
        dict(insert=dict(
                 holder_id="ENT_LA_CAISSE", target_id="ENT_NEXTDC", instrument="debt",
                 event="binding commitment to subordinated hybrid securities",
                 notes="A$1.0bn binding commitment announced 6 April 2026; NEXTDC described A$1.7bn of binding "
                       "commitments from La Caisse on 8 May 2026. The hybrids rank below all NEXTDC's other debt, are "
                       "classified as debt and carry no equity conversion. La Caisse's final allocation 'may be less "
                       "than its commitment' and is not stated in any record read, so no amount is recorded.",
                 fact_status="VERIFIED", source_id=SRC_HYBRID, confidence="high", as_of_date="2026-05-08"),
             add_sources=[dict(id=SRC_HYBRID, quote=f"{hybrid_commit} | {hybrid_debt}"),
                          dict(id=SRC_LIQUIDITY, quote=liq_caisse)]),
        dict(match=dict(id=6),
             set=dict(notes="CDC's own release (18 February 2025) gives the Future Fund 34.55% after it took up "
                            "10.46% from CSC's sale. The Future Fund's Periodic Investment Report at 31 December "
                            "2025 lists CDC among its internally managed unlisted infrastructure at '29%' ownership. "
                            "Neither record explains the difference. The Future Fund Board also manages other "
                            "Commonwealth funds, whose reports would show whether they hold the rest; futurefund.gov.au "
                            "refused the research crawler on 22 October 2026 (RG-094). Both figures are kept; "
                            "neither is chosen."),
             add_sources=[dict(id=SRC_FF, quote=ff_cdc)]),
    ]

    def metric(name, value, unit, as_of, src, quote, notes):
        return dict(insert=dict(as_of=as_of, scope="Australia", metric_name=name, value=value, unit=unit,
                                basis="actual", notes=notes, fact_status="VERIFIED", source_id=src,
                                confidence="high", as_of_date=as_of),
                    add_sources=[dict(id=src, quote=quote)])

    one_option = ("One investment option only, as the fund's file reports it; the fund's other options hold their "
                  "own amounts and nothing is added across them.")
    metrics = [
        metric("cbus_growth_mysuper_nextdc_shares_holding", 344511305.86, "AUD", "2026-06-30", SRC_CBUS,
               f"{cbus_head} | {cbus_shares} | {cbus_option} | {cbus_date}",
               f"Cbus Growth (MySuper): 23,629,033.32 NEXTDC shares worth A$344,511,305.86, 0.4048% of the option. "
               f"{one_option}"),
        metric("cbus_growth_mysuper_nextdc_notes_holding", 18587879.90, "AUD", "2026-06-30", SRC_CBUS,
               f"{cbus_head} | {cbus_notes}",
               "Cbus Growth (MySuper): NEXTDC callable medium term notes, a loan to NEXTDC, worth A$18,587,879.90. "
               "The same file lists STACK Infrastructure Australia (Palmers Road) Pty Ltd among the borrowers in "
               "its private debt, with no amount of its own: private debt is reported as one total of "
               f"A$961,424,965.53. {one_option}"),
        metric("hesta_balanced_growth_nextdc_shares_holding", 73522711.524395, "AUD", "2026-06-30", SRC_HESTA,
               hesta_shares,
               f"HESTA Balanced Growth: 5,042,709.98 NEXTDC shares worth A$73,522,711.52. {one_option}"),
        metric("hostplus_balanced_nextdc_shares_holding", 109136752.0, "AUD", "2026-06-30", SRC_HOSTPLUS,
               f"{hostplus_shares} | {hostplus_date}",
               f"Hostplus Balanced: 7,485,373.95 NEXTDC shares worth A$109,136,752, 0.11% of the option. The file "
               f"carries no date; the page that links it says 'As at 30 June 2026'. {one_option}"),
        metric("futurefund_nextdc_listed_equity_holding", 78806270.0, "AUD", "2025-12-31", SRC_FF, ff_nxt_eq,
               "Future Fund: 6,289,407 NEXTDC shares worth A$78,806,270 held as listed equity. The same report "
               "lists a further 529,664 shares (A$6,636,690) under listed property, kept as its own row."),
        metric("futurefund_nextdc_listed_property_holding", 6636690.0, "AUD", "2025-12-31", SRC_FF, ff_nxt_prop,
               "Future Fund: 529,664 NEXTDC shares worth A$6,636,690 held under listed property."),
        metric("futurefund_cdc_ownership_pct", 29.0, "%", "2025-12-31", SRC_FF, ff_cdc,
               "The Future Fund's report gives its ownership of CDC as '29%' and no value. CDC's February 2025 "
               "release gives the Future Fund 34.55% (ownership row 6). The difference is unexplained (RG-094)."),
        metric("futurefund_nvidia_holding", 2107250593.0, "AUD", "2025-12-31", SRC_FF, ff_nvda,
               "Future Fund: 7,534,692 NVIDIA shares worth A$2,107,250,593, 0.78% of the fund (RG-094)."),
    ]

    flows = [
        dict(match=dict(id=9),
             set=dict(notes="Capital Brief reports a A$7.6bn S7 build with OpenAI as partner. NEXTDC's own ASX "
                            "release of the same day describes a Memorandum of Understanding with OpenAI to "
                            "collaborate on planning, development and operation, and states no dollar figure, "
                            "capacity commitment, contract term or price; the A$7.6bn is Capital Brief's. No NEXTDC "
                            "report read since mentions OpenAI (RG-014). CORRECTED 2026-10-22: earlier notes spoke of "
                            "'the OpenAI offtake'; no record read describes one."),
             add_sources=[dict(id=SRC_MOU, quote=f"{mou_agreed} | {mou_scope}")]),
    ]

    gaps = [
        dict(match=dict(id=4),
             set=dict(status="in_progress", as_of_date=TODAY,
                      notes="ADVANCED 2026-10-22 (research batch 2). Read from the funds' own files at 30 June 2026, "
                            "one option each: Cbus Growth (MySuper) holds NEXTDC shares worth A$344.5m and NEXTDC "
                            "notes worth A$18.6m, and lists STACK Infrastructure Australia (Palmers Road) Pty Ltd "
                            "among its private-debt borrowers; HESTA Balanced Growth holds NEXTDC shares worth "
                            "A$73.5m; Hostplus Balanced holds NEXTDC shares worth A$109.1m. All three put billions "
                            "with IFM Investors, whose real estate trustee holds the Mamre Road land (RG-005). "
                            "NEXTDC's FY26 annual report names AustralianSuper Pty Ltd a substantial holder with "
                            "8.49%. The Future Fund's December 2025 report holds NEXTDC shares (A$85.4m across two "
                            "lines) and CDC at '29%'. REFUSED, never worked around: australiansuper.com (robots.txt refused, "
                            "read as disallow-all), csc.gov.au (HTTP 403), unisuper.com.au and "
                            "australianretirementtrust.com.au (bot-check pages), Aware Super (robots.txt disallows its "
                            "files) and futurefund.gov.au (data/raw/superannuation/*/refused.json). Those files are "
                            "in docs/requests/DOWNLOADS.md for a person to download. Not yet looked for: debt "
                            "facilities and platform stakes beyond what the files show."),
             add_sources=[dict(id=SRC_CBUS, quote=cbus_shares), dict(id=SRC_HESTA, quote=hesta_shares),
                          dict(id=SRC_HOSTPLUS, quote=hostplus_shares), dict(id=SRC_AR, quote=holders)]),
        dict(match=dict(id=94),
             set=dict(status="in_progress", as_of_date=TODAY,
                      notes="Archive every CSV pulled under data/raw/futurefund/ with SHA-256 manifests, as done for "
                            "the December-2025 Future Fund PIR. ADVANCED 2026-10-22: the archived December 2025 "
                            "report also holds NVIDIA (7,534,692 shares, A$2.107bn, 0.78% of the fund) and lists "
                            "CDC at '29%', where CDC's own release gives the Future Fund 34.55%. BLOCKED: "
                            "futurefund.gov.au now refuses the research crawler (its robots.txt is refused, so read "
                            "as disallow-all), including the December 2025 file it served on 2026-09-21. The June "
                            "2025 report and the other funds' reports are in docs/requests/DOWNLOADS.md for a person "
                            "to download."),
             add_sources=[dict(id=SRC_FF, quote=f"{ff_nvda} | {ff_cdc}")]),
        dict(match=dict(id=5),
             set=dict(status="in_progress", as_of_date=TODAY,
                      notes="ADVANCED 2026-10-22. The title search filed with the Mamre Road EIS (16 December 2025) "
                            "shows Lot 10 DP 1280592 at Kemps Creek registered to ISPT Pty Limited, and ASIC's "
                            "register shows ISPT Pty Ltd (ACN 064 041 283) has been named IFM Real Estate Fiduciary "
                            "Pty Ltd since 24 November 2025, which reconciles the 'ISPT' and 'IFM' accounts for that "
                            "lot. The search carries a caveat by KNBDC SYD4 Pty Ltd (now AirTrunk SYD4). The EIS "
                            "describes the whole site, 706-752 Mamre Road, as Lot 10 DP 1280592 of about 52.2 ha, "
                            "so Lot 10 is the site; it plans road connections to the neighbouring GPT, Gibb Group "
                            "and Frasers estates. Still open: the fund vehicle, the sale price and the conditions "
                            "precedent. The NSW Valuer General's free sales data would give a price; its site "
                            "refused the research crawler (docs/requests/DOWNLOADS.md)."),
             add_sources=[dict(id="SRC_SSD92743706_EIS", quote=f"{eis_site} | {eis_area} | {eis_roads}")]),
        dict(match=dict(id=14),
             set=dict(status="in_progress", as_of_date=TODAY,
                      notes="ADVANCED 2026-10-22 (research batch 2). The only primary statement read is NEXTDC's "
                            "own ASX release of 5 December 2025: a Memorandum of Understanding with OpenAI under "
                            "OpenAI for Countries, to collaborate on planning, development and operation of an AI "
                            "campus at S7, first phase expected in the second half of 2027 subject to approvals. It "
                            "states no offtake term, capacity, price, funding or stake. A week later, on 12 December "
                            "2025, NEXTDC lodged a 'Response to ASX Compliance Letter'; it sits behind ASX's terms "
                            "of use and has not been read. No NEXTDC report since mentions OpenAI: the 1H26 results "
                            "announcement, presentation and accounts, the April and May 2026 funding releases, the "
                            "FY26 results announcement, presentation and annual report, and the S7 page as archived "
                            "on 2026-10-22. The FY26 presentation lists S7's initial capacity as 'TBD' and says "
                            "NEXTDC is evaluating third-party capital through a joint venture company for S4, S7 and "
                            "M5; the annual report lists NEXTDC S7 Holdings Pty Ltd and related S7 entities, 100% "
                            "owned at 30 June 2026. openai.com refused the research crawler. HUMAN DECISION: "
                            "SITE_NEXTDC_S7 records OpenAI as anchor tenant on news reports; NEXTDC's own record "
                            "calls OpenAI an infrastructure partner under a memorandum and has not named it since."),
             add_sources=[dict(id=SRC_MOU, quote=f"{mou_agreed} | {mou_timing}"),
                          dict(id=SRC_FY26, quote=f"{fy26_s7} | {fy26_jvco}"),
                          dict(id=SRC_AR, quote=f"{ar_partners} | {ar_s7_entity}"),
                          dict(id=SRC_1H26, quote=f"{h1_fast} | {h1_adviser}"),
                          dict(id=SRC_ASX, quote=asx_letter),
                          dict(id="SRC_NEXTDC_S7", quote=s7_size)]),
    ]

    pack = {
        "pack_id": "super-and-openai-2026-10",
        "prepared_by": "scripts/curate_super_and_openai.py",
        "prepared_on": TODAY,
        "sources": sources,
        "rows": {
            "entities": entities,
            "ownership": ownership,
            "metrics": metrics,
            "financial_flows": flows,
            "research_gaps": gaps,
        },
    }
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(pack, fh, indent=1, ensure_ascii=False)
    print(f"wrote {OUT}: {len(sources)} sources, {len(metrics)} metrics, {len(ownership)} ownership rows; "
          f"{len(refused)} funds refused, {len(silent)} NEXTDC documents checked for OpenAI")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
