#!/usr/bin/env python3
"""
RG-061 and RG-099: the author accepted the findings on 2026-11-15.

RG-061 asked whether NSW consent conditions ever exceed what the proponent's own EIS offered
(the "no ratchet" hypothesis). They do. Three of the twenty archived consent instruments obligate
the applicant to match all operational electricity demand - IT and non-IT - to "a portfolio of
additional, firmed renewable energy supply at all times", contracted through a NSW-based PPA plus
a firming agreement, demonstrated before operation may commence. All three were determined between
23 July and 14 September 2026; none of the sixteen earlier determinations carries it. Each
assessment report records a weaker offer first. The gap stays in_progress: the renewable obligation
is answered, the other performance measures are not tested, and one determined project (Lanceley
Place, SSD-66777221) has no instrument in the archive.

RG-099 asked, for five sites whose capacity rested only on the portal's one-line description,
whether the figure is IT load or total site draw:
  * SITE_ROAD_1        SETTLED as IT load. Its EIS labels it "Power Consumption 34.3 MW (IT Load)"
                       at p35, and pp57-58 corroborate it arithmetically (eight halls at ~4.3 MW,
                       peak PUE 1.4). No value changes.
  * SITE_23_25_WATERLOO SETTLED as total. The description says "total power consumption of 70
                       megawatts"; the row already held it as total. No value changes.
  * SITE_NEXTDC_S7     SETTLED as not IT load (its scoping report calls 612 MW power consumption).
                       Which total stands is RG-097's. The row already holds no figure.
  * SITE_TURNER_RD     CANNOT be settled: withdrawn, so no EIS or assessment report will exist.
  * SITE_ORIORDAN      CANNOT be settled: Prepare EIS, and its two documents disagree (38 vs 45 MW)
                       without labelling either.
For the last two the unlabelled figure is removed from every capacity column, following the
treatment already applied to NEXTDC S7 on 2026-10-14: no figure in any column, the passages quoted
in source_refs, the reason in notes. Clearing it_capacity_mw alone would have left the same
unlabelled number as the row's headline, because headline_mw is
COALESCE(max_capacity_mw, total_capacity_mw, it_capacity_mw).

Deliberately NOT done: Road 1's max_capacity_mw is left at 34.3, not raised to the EIS's ~42 MW.
p54's 42 MW is the electrical infrastructure's design ceiling for *critical IT load*, and
max_capacity_mw is the full-campus-build-out ceiling that headline_mw reads first. Storing an IT-side
design ceiling there would publish 42 MW as this site's headline against other sites' total-power
maxima - the measure-mixing RG-099 exists to prevent. The passage is quoted instead.

Outputs:
  * data/packs/rg061_rg099_decisions.json

Run:
    python3 scripts/curate_rg061_rg099.py
    python3 scripts/load_pack.py data/packs/rg061_rg099_decisions.json
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONSENTS = os.path.join(ROOT, "data", "raw", "nsw_planning", "consents")
DOCS = os.path.join(ROOT, "data", "raw", "nsw_planning", "documents")
NODES = os.path.join(ROOT, "data", "raw", "nsw_planning", "nodes")
OUT_PACK = os.path.join(ROOT, "data", "packs", "rg061_rg099_decisions.json")

TODAY = "2026-11-15"

SRC_CONSENTS = "SRC_NSWPORTAL_CONSENTS"
SRC_REGISTER = "SRC_NSWPORTAL_REGISTER"
SRC_GLEND_ASSESS = "SRC_SSD73761707_ASSESSMENT"
SRC_APOLLO_ASSESS = "SRC_SSD74069708_ASSESSMENT"
SRC_PLUTO_ASSESS = "SRC_SSD69223466_ASSESSMENT"
SRC_S7_SCOPING = "SRC_SSD113934740_SCOPING"
SRC_ORIORDAN_SEARS = "SRC_SSD77274467_SEARS_REQUEST"
SRC_WATERLOO_SEARS = "SRC_SSD91297457_SEARS_REQUEST"
SRC_ROAD1_EIS = "SRC_SSD80814238_EIS"          # created here
SRC_JULIUS_EIS = "SRC_SSD80018208_EIS"
SRC_S5_EIS = "SRC_SSD63168959_EIS"

# The three instruments that carry the obligation, and the sixteen that do not. Read from the
# archive, not typed: the scan below rebuilds this list on every run and refuses if it changes.
FIRMED = {
    "project_pluto_data_centre": ("SSD-69223466", "2026-07-23", "B19/B20"),
    "project_apollo_data_centre_macquarie_park": ("SSD-74069708", "2026-09-02", "B22/B23"),
    "glendenning_road_data_centre": ("SSD-73761707", "2026-09-14", "B20/B21/B22/B23"),
}


def normalise(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def archived(base: str, errors: list[str]) -> str:
    """Archived text, with the document's SHA-256 checked where the PDF is present."""
    meta_path = base + ".pdf.meta.json"
    if not os.path.exists(meta_path):
        errors.append(f"{os.path.basename(base)}: no manifest")
    else:
        meta = json.load(open(meta_path))
        if os.path.exists(base + ".pdf"):
            if hashlib.sha256(open(base + ".pdf", "rb").read()).hexdigest() != meta["sha256"]:
                errors.append(f"{os.path.basename(base)}: fails its SHA-256 check")
    return normalise(open(base + ".txt", encoding="utf-8").read())


def grab(body: str, pattern: str, label: str, errors: list[str]) -> str:
    """A verbatim quote from the archived text. Never retyped, so extraction artefacts are kept."""
    m = re.search(pattern, body, re.I)
    if not m:
        errors.append(f"{label}: quote not found: {pattern[:70]!r}")
        return ""
    return m.group(0).strip()


def node_description(slug: str) -> str:
    j = json.load(open(os.path.join(NODES, slug + ".json")))
    if isinstance(j, list):
        j = j[0]
    return normalise(re.sub(r"<[^>]+>", " ", (j.get("field_project_description") or [{}])[0].get("value") or ""))


def main() -> int:
    errors: list[str] = []

    # ---- the scan: every archived instrument, re-read on every run -------------------------
    instruments = sorted(f for f in os.listdir(CONSENTS) if f.endswith(".txt"))
    firmed, renewable, pue = [], [], []
    for name in instruments:
        body = normalise(open(os.path.join(CONSENTS, name), encoding="utf-8").read())
        stem = name[:-4]
        if re.search(r"firmed renewable", body, re.I):
            firmed.append(stem)
        if re.search(r"renewable", body, re.I):
            renewable.append(stem)
        if re.search(r"\bPUE\b|Power Usage Effectiveness", body, re.I):
            pue.append(stem)
    if len(instruments) != 20:
        errors.append(f"expected 20 archived instruments, found {len(instruments)}; re-read the scan")
    if sorted(firmed) != sorted(FIRMED):
        errors.append(f"the firmed-renewable set changed: {sorted(firmed)}; re-read before writing")
    if len(renewable) != 8 or len(pue) != 7:
        errors.append(f"renewable/PUE counts changed ({len(renewable)}/{len(pue)}); re-read")

    # ---- quotes ---------------------------------------------------------------------------
    glend_consent = archived(os.path.join(CONSENTS, "glendenning_road_data_centre"), errors)
    glend = archived(os.path.join(DOCS, "SSD-73761707_assessment"), errors)
    apollo = archived(os.path.join(DOCS, "SSD-74069708_assessment"), errors)
    pluto = archived(os.path.join(DOCS, "SSD-69223466_assessment"), errors)
    eis = archived(os.path.join(DOCS, "SSD-80814238_eis"), errors)
    scoping = archived(os.path.join(DOCS, "SSD-113934740_scoping"), errors)
    ori_sears = archived(os.path.join(DOCS, "SSD-77274467_sears_request"), errors)
    wat_sears = archived(os.path.join(DOCS, "SSD-91297457_sears_request"), errors)

    q_condition = grab(glend_consent,
                       r"offset all greenhouse gas generation associated with the supply of electricity "
                       r"to the development \(including both non-IT and IT loads\) by demonstrating that "
                       r"all operational electricity demand is matched with a portfolio of additional, "
                       r"firmed renewable energy supply at all times", "Glendenning B20", errors)
    q_ppa = grab(glend_consent,
                 r"entered into a Power Purchase Agreement\(s\) and firming agreement for NSW -based supply "
                 r"within the National Electricity Market", "Glendenning B20(b)", errors)
    q_glend_offer = grab(glend, r"The ESD report additionally noted that further measures to reduce "
                                r"emissions[^.]*zero\.", "Glendenning assessment p55", errors)
    q_glend_imposed = grab(glend, r"the Department recommends conditions requiring that, prior to the "
                                  r"commencement of operation of the development, the Applicant offset all "
                                  r"GHG emissions[^.]*auditing\.", "Glendenning assessment p56", errors)
    q_apollo_offer = grab(apollo, r"the Applicant advised that it has been purchasing 100% renewable "
                                  r"electricity for electricity under their operational control\.",
                          "Apollo assessment p59", errors)
    q_apollo_doubt = grab(apollo, r"the Department considers that emissions outcomes remain materially "
                                  r"dependent[^.]*procurement\.", "Apollo assessment p59", errors)
    q_apollo_epa = grab(apollo, r"recommended consideration of energy efficiency and renewable energy "
                                r"measures, with any commitments to be secured through conditions",
                        "Apollo assessment p33", errors)
    q_pluto_epa = grab(pluto, r"recommended that energy efficiency practices and purchasing of renewable "
                              r"energy certificates be undertaken to reduce Scope 2 greenhouse gas "
                              r"emissions\.", "Pluto assessment p27", errors)
    q_pluto_pv = grab(pluto, r"The proposed PV system will offset 658 MWh/year and save 540 tonnes "
                             r"CO₂-e annually\.", "Pluto assessment p50", errors)
    q_pluto_emissions = grab(pluto, r"The ESD Report estimates the development will generate 467,924 "
                                    r"tonnes CO₂-e annually", "Pluto assessment p50", errors)

    q_road1_label = grab(eis, r"Power Consumption 34\.3 MW \(IT Load\)", "Road 1 EIS p35", errors)
    q_road1_halls = grab(eis, r"Total IT load of 34\.3MW \(evenly distributed at ~4\.3MW per hall\)",
                         "Road 1 EIS p58", errors)
    q_road1_pue = grab(eis, r"The facility is designed with 3MW electrical strings and a peak PUE of 1\.4, "
                            r"providing a total IT load of 34\.3MW\.", "Road 1 EIS p57", errors)
    q_road1_headroom = grab(eis, r"The electrical infrastructure is designed to support a total critical "
                                 r"IT load of approximately 42MW\.", "Road 1 EIS p54", errors)
    q_road1_total = grab(eis, r"The proposed data centre has a total power consumption of 34\.3 megawatts",
                         "Road 1 EIS p11", errors)
    q_s7_power = grab(scoping, r"Power Consumption 612MW", "S7 scoping p27", errors)
    q_s7_site = grab(scoping, r"The expected total site load is approximately 700MW, with infrastructure "
                              r"designed to support up to 875MVA\.", "S7 scoping p35", errors)
    q_ori_sears = grab(ori_sears, r"a 45 megawatt data centre", "O'Riordan SEARs request", errors)

    # RG-017 becomes citable: the S7 scoping report is the public evidence that water agreements
    # are being negotiated and are not published. The requests themselves are drafted, not lodged.
    q_s7_water = grab(scoping, r"Average daily water demand at approximately 70% load is estimated at "
                               r"5\.44 ML/day, with peak demand at full site maturity reaching up to "
                               r"7\.79 ML/day over a 24-hour period\.", "S7 scoping p36", errors)
    q_s7_sydneywater = grab(scoping, r"NEXTDC has commenced engagement with Sydney Water regarding "
                                     r"interim potable water supply for Stage 1, as well as potential "
                                     r"recycled water opportunities, including supply from the St Marys "
                                     r"Advanced Water Treatment Plant\.", "S7 scoping p36", errors)
    q_s7_conexa = grab(scoping, r"Investigations are also underway with coNEXA to identify potential "
                                r"connections to the recycled water main associated with the S4 "
                                r"development\.", "S7 scoping p36", errors)

    # RG-105: found while implementing RG-099. Road 1 and the 1-5 Khartoum Road consent share an
    # address and a lot. Not merged, not assumed: two consents, two figures, one asked question.
    khartoum = archived(os.path.join(CONSENTS, "1_5_khartoum_road_data_centre"), errors)
    q_road1_lot = grab(eis, r"Site Part of Lot 2 Deposited Plan 1043041", "Road 1 EIS glossary", errors)
    q_khartoum_schedule1 = grab(
        khartoum, r"Application Number: SSD-63235720 Applicant: Stockland Development Pty Limited "
                  r"Consent Authority: Minister for Planning and Public Spaces Site: 1-5 Khartoum "
                  r"Road, Macquarie Park Part Lot 2 DP 1043041", "SSD-63235720 Schedule 1", errors)
    for slug in ("road-1-data-centre", "1-5-khartoum-road-data-centre"):
        j = json.load(open(os.path.join(NODES, slug + ".json")))
        if isinstance(j, list):
            j = j[0]
        addr = (j.get("field_project_address") or [{}])[0].get("value")
        if addr != "1-5 Khartoum Road, Macquarie Park":
            errors.append(f"{slug}: portal address changed ({addr!r}); re-read RG-105")

    # ---- free substitutes for the paid title searches (author: no budget yet, 2026-11-15) ----
    # Three archived EISs state land ownership themselves. A $17 NSW title search would confirm
    # the proprietor; these statements are primary, dated and free, and are recorded as what the
    # applicant said, not as a title search.
    julius = archived(os.path.join(DOCS, "SSD-80018208_eis"), errors)
    s5 = archived(os.path.join(DOCS, "SSD-63168959_eis"), errors)
    q_road1_owner = grab(eis, r"Site Name MPark Road 1 Data Centre Land ownership The land is owned by "
                              r"Stockland\. Address 1-5 Khartoum Road, Macquarie Park Legal Description "
                              r"\(Title Particulars\) Part Lot 2 DP 1043041", "Road 1 EIS Table 5", errors)
    q_julius_cover = grab(julius, r"SSD-80018208 ENVIRONMENTAL IMPACT STATEMENT: JULIUS AVENUE DATA "
                                  r"CENTRE 6-8 JULIUS AVENUE, NORTH RYDE LOT 89 DP 1082131 — Prepared by "
                                  r"Willowtree Planning Pty Ltd on behalf of ISPT Pty Ltd JUNE 2025",
                          "Julius Avenue EIS cover", errors)
    q_julius_owner = grab(julius, r"TABLE 6: REGISTERED LANDOWNERS Lot/DP Registered Landowner "
                                  r"89/1082131 ISPT Pty Ltd Landowner’s consent has been obtained from "
                                  r"the above entity\.", "Julius Avenue EIS Table 6", errors)
    q_s5_owner = grab(s5, r"Land Ownership The site is owned by NEXTDC Limited\.",
                      "NEXTDC S5 EIS", errors)

    d_turner = node_description("52-turner-road-data-centre")
    d_ori = node_description("22-oriordan-street-alexandria-data-centre")
    d_wat = node_description("23-25-waterloo-road-data-centre")
    for label, desc, needle in (("Turner", d_turner, "a capacity of 40 MW"),
                                ("O'Riordan", d_ori, "a power capacity of 38 MW"),
                                ("Waterloo", d_wat, "total power consumption of 70 megawatts")):
        if needle not in desc:
            errors.append(f"{label} portal description no longer says {needle!r}; re-read")
    if re.search(r"\bMW\b|megawatt", wat_sears, re.I):
        errors.append("Waterloo's SEARs request now states a capacity figure; re-read it")

    # The EIS source row is created here; its manifest is the provenance.
    eis_meta = json.load(open(os.path.join(DOCS, "SSD-80814238_eis.pdf.meta.json")))

    if errors:
        print("refusing to write; fix these first:", file=sys.stderr)
        for e in errors:
            print(f"  {e}", file=sys.stderr)
        return 1

    # ---- notes ----------------------------------------------------------------------------
    resolved_61 = (
        f"ANSWERED {TODAY} for the renewable-energy obligation; the hypothesis is FALSIFIED. The "
        "'no ratchet' finding does not hold. Three of the 20 archived consent instruments (19 "
        "distinct projects - Davis Road appears twice, original and MOD 1) obligate the Applicant, "
        "before operation may commence and to the Planning Secretary's satisfaction, to offset all "
        "GHG from electricity 'including both non-IT and IT loads' by matching all operational "
        "demand to 'a portfolio of additional, firmed renewable energy supply at all times', with a "
        "Power Purchase Agreement and firming agreement for NSW-based supply within the NEM and a "
        "shortfall framework: Project Pluto SSD-69223466 B19/B20 (determined 23 July 2026), Project "
        "Apollo SSD-74069708 B22/B23 (2 September 2026), Glendenning Road SSD-73761707 B20/B21/B22/B23 "
        "(instrument dated 14 September 2026; the portal's determination field reads 16 September). "
        "None of the 16 earlier determinations in the archive carries it. In each case the "
        "Department's assessment report records a materially weaker offer first and then recommends "
        "the condition anyway: Glendenning p55 offered '100% renewable energy by 2040' against p56's "
        "pre-operation obligation; Apollo p59 said it 'has been purchasing 100% renewable electricity "
        "for electricity under their operational control' and the Department held outcomes "
        "'materially dependent on the successful securing and performance of renewable energy "
        "procurement'; Pluto's EPA advice (p27) went no further than 'purchasing of renewable energy "
        "certificates', while its ESD Report (p50) offered 500 kW of rooftop solar offsetting 658 "
        "MWh/yr and 540 t CO2-e against 467,924 t CO2-e/yr stated - about 0.12% by arithmetic on the "
        "report's own two figures, a derivation and not a quoted fact. WHAT IS NOT RATCHETED: the "
        "numeric targets stay proponent-set (PUE 1.17 Glendenning, 1.4 Pluto); the conditions require "
        "reporting against them, not achieving a Department number. The ratchet is on timing, "
        "additionality, firming, geography and auditing - Glendenning B22 adds continuous IT-vs-total "
        "metering, annual PUE/WUE/CO2-e reporting, alignment with the NSW Guide for Large Emitters "
        "(EPA, 2025), prioritising recycled or non-potable water where available, and three-yearly "
        "revision, and B23 bars operation until the plan is approved. TIMING IS NARROWER THAN '2026': "
        "1-5 Khartoum Road SSD-63235720, determined 11 March 2026, has renewable and PUE language and "
        "no at-all-times obligation, so the change falls between 11 March and 23 July 2026. "
        "CORRECTIONS to this gap's earlier note, which was written against 18 instruments: 20 "
        "instruments for 19 projects; EIGHT consents mention renewable supply (not four) and SEVEN "
        "mention PUE (not five). STILL OPEN, so this gap stays in_progress: no EIS is archived for "
        "any determined project, so the other 16 comparisons run through the assessment report's "
        "summary of the ESD Report; air quality, noise, water and traffic conditions are untested for "
        "a ratchet; the three firmed consents are also the three largest recent approvals, so "
        "'the Department ratchets' and 'it ratchets on the biggest projects' cannot be separated; and "
        "Lanceley Place Artarmon SSD-66777221, approved 11 April 2025, has no instrument in the "
        "archive and no assessment-report attachment on its portal record, so the scan cannot speak "
        "to it. The policy text the conditions refer to ('in accordance with applicable NSW "
        "government policy') has not been located, so the cause of the mid-2026 change is not "
        "established. Full chain with page cites and SHA-256 prefixes: reports/hunts/RG-061.md."
    )

    resolved_99 = (
        f"RESOLVED {TODAY} (author accepted). Three of the five settled from the project's own "
        "document, two cannot be settled from any public document and no longer carry a figure. "
        "SETTLED: SITE_ROAD_1 is IT load - its EIS p35 reads 'Power Consumption 34.3 MW (IT Load)', "
        "p57 'a peak PUE of 1.4, providing a total IT load of 34.3MW' and p58 eight halls at ~4.3 MW "
        "each; the 'total power consumption of 34.3 megawatts' at p11 and the 'megawatt capacity of "
        "34.3' at p63 are the SSD-threshold paragraphs reusing the IT figure. it_capacity_mw 34.3 "
        "confirmed, unchanged. SITE_23_25_WATERLOO is total - the portal description says 'total "
        "power consumption of 70 megawatts', re-read live on 2026-11-16 and unchanged, and its "
        "request for SEARs states no capacity at all; total_capacity_mw 70 confirmed, unchanged. "
        "SITE_NEXTDC_S7 is NOT IT load - its scoping report says 'Power Consumption 612MW' (p27) and "
        "'total power consumption of 612 megawatts' (p40); which total stands (612, the same "
        "report's 'expected total site load is approximately 700MW ... up to 875MVA' at p35, or the "
        "operator's published figure) is RG-097's question, and the row holds no figure. CANNOT BE "
        "SETTLED: SITE_TURNER_RD (SSD-60185233) is WITHDRAWN, last modified 2025-01-04, its five "
        "attachments being SEARs and a withdrawal notice, so no EIS or assessment report will ever "
        "label its 'capacity of 40 MW'; SITE_ORIORDAN (SSD-77274467) is at Prepare EIS and its two "
        "documents disagree - the portal says 'a power capacity of 38 MW', its request for SEARs 'a "
        "45 megawatt data centre' - and neither labels the measure. For both, the unlabelled figure "
        "is removed from it_capacity_mw AND max_capacity_mw, following the treatment applied to "
        "NEXTDC S7 on 2026-10-14: no figure in any capacity column, the passages quoted in "
        "source_refs, the reason in notes. Clearing it_capacity_mw alone would have left the same "
        "unlabelled number as the row's headline, since headline_mw is "
        "COALESCE(max_capacity_mw, total_capacity_mw, it_capacity_mw). NOT DONE, deliberately: Road "
        "1's max_capacity_mw stays 34.3 rather than the EIS p54's 'approximately 42MW', because that "
        "42 MW is the electrical infrastructure's design ceiling for CRITICAL IT LOAD and "
        "max_capacity_mw is the full-campus-build-out ceiling the headline reads first; storing it "
        "would mix measures across sites. The passage is quoted against the row instead. ROUTE "
        "CLOSED: the portal's attachment JSON (<slug>?_format=json) answered 401 for every candidate "
        "on 2026-11-16, so no further document can be archived to settle the remaining two; recorded "
        "in data/raw/nsw_planning/documents/refused.json and not worked around. Full log: "
        "reports/hunts/RG-099.md."
    )

    notes_turner = (
        "CORRECTION: this record was previously entered as 'lodged' from a portal search snippet. "
        "The harvested register shows stage WITHDRAWN, in Camden LGA. The application described 'a "
        "capacity of 40 MW including emergency back-up generators, cooling plant, diesel and lithium "
        "ion battery storage, substation and associated infrastructure'. "
        f"RG-099 CLOSED FOR THIS ROW {TODAY}: the 40 MW is removed from every capacity column. The "
        "portal's description does not say whether it is IT load or total site draw, and because the "
        "application was WITHDRAWN (record last modified 2025-01-04) no EIS or assessment report "
        "will ever be produced to label it. Its five portal attachments are the request for SEARs, "
        "the industry-specific SEARs, a cover letter and a withdrawal notice; the SEARs documents "
        "answered HTTP 401 on 2026-11-16 and are not public. Same treatment as NEXTDC S7: no figure "
        "in any column, the description quoted in source_refs. A capacity for this site would have "
        "to come from the proponent, not the planning record."
    )

    notes_ori = (
        "City of Sydney. Prepare EIS. Alexandria is the inner-Sydney corridor where Equinix SY1 and "
        "noise complaints about generator testing have historically concentrated. "
        f"RG-099 CLOSED FOR THIS ROW {TODAY}: the 38 MW is removed from every capacity column. Two "
        "documents state two different figures and neither labels the measure: the portal "
        "description says 'a power capacity of 38 MW', the request for SEARs 'a 45 megawatt data "
        "centre'. The project has five attachments and no EIS, so nothing public settles it. Same "
        "treatment as NEXTDC S7: no figure in any column, both passages quoted in source_refs. The "
        "38 vs 45 MW discrepancy is itself unexplained and is not resolved by choosing one."
    )

    notes_road1 = (
        "City of Ryde. In Assessment (More Information Required on 2026-11-16). "
        f"RG-099 SETTLED {TODAY}: 34.3 MW is IT LOAD, on the EIS's own label - p35 'Power Consumption "
        "34.3 MW (IT Load)', p57 'designed with 3MW electrical strings and a peak PUE of 1.4, "
        "providing a total IT load of 34.3MW', p58 'Total IT load of 34.3MW (evenly distributed at "
        "~4.3MW per hall)' across eight halls. The 'total power consumption of 34.3 megawatts' at "
        "p11 and 'megawatt capacity of 34.3' at p63 are the SSD-classification paragraphs reusing "
        "the IT figure, not a second measurement. it_capacity_mw 34.3 confirmed and unchanged. NO "
        "total site draw is stated anywhere in the EIS; 34.3 x 1.4 = about 48 MW is a derivation "
        "from the stated peak PUE and is deliberately not stored. max_capacity_mw stays 34.3: p54's "
        "'electrical infrastructure is designed to support a total critical IT load of approximately "
        "42MW' is design headroom expressed as CRITICAL IT LOAD, and max_capacity_mw is the "
        "full-campus-build-out ceiling that headline_mw reads first, so storing 42 there would "
        "publish an IT-side ceiling as this site's headline against other sites' total-power "
        "maxima. The passage is quoted in source_refs instead. The site is within the broader "
        "'MPark' Stockland landholding (EIS p11), on Lot 2 DP 1043041 - a different lot from the "
        "1-5 Khartoum Road consent (SSD-63235720) and from SSD-10467."
    )

    notes_wat = (
        "Macquarie Park. Prepare EIS. RG-099 CONFIRMED 2026-11-15: the portal description labels the "
        "figure explicitly - 'Construction and operation of a data centre with total power "
        "consumption of 70 megawatts at 23-25 Waterloo Road, Macquarie Park' - so 70 MW is total "
        "site draw, not IT load, and total_capacity_mw 70 is correct as recorded. Re-read live on "
        "2026-11-16: description unchanged. The project's request for SEARs states no capacity "
        "figure at all, and its EIS attachment (environmental-impact-statement-14971) answered 401 "
        "on 2026-10-14 and again on 2026-11-16, so no IT load is available. No value changed."
    )

    sources = [dict(
        id=SRC_ROAD1_EIS,
        title=f"{eis_meta.get('label', 'EIS').removesuffix('.pdf')} - SSD-80814238 (Road 1 Data Centre)",
        publisher="Urbis for the proponent (NSW Planning Portal)",
        url=eis_meta["url"],
        doc_type="primary_planning_portal",
        published=None,
        credibility="A",
        accessed=eis_meta["fetched_utc"][:10],
        notes=(f"Environmental impact statement for SSD-80814238, read {TODAY} from the archive at "
               f"data/raw/nsw_planning/documents/ (attachment {eis_meta['attachment_slug']}), "
               f"SHA-256 {eis_meta['sha256']}, {eis_meta['bytes']} bytes, text by "
               f"{eis_meta['extractor']}, {eis_meta.get('pages')} pages with [[page N]] markers. "
               "Cited for the capacity label that settles RG-099 for SITE_ROAD_1: p35 'Power "
               "Consumption 34.3 MW (IT Load)', pp57-58, and the p54 infrastructure headroom."),
    )]

    sites = [
        dict(match=dict(id="SITE_ROAD_1"),
             set=dict(notes=notes_road1, fact_status="VERIFIED", confidence="high",
                      as_of_date=TODAY, source_id=SRC_ROAD1_EIS),
             add_sources=[dict(id=SRC_ROAD1_EIS,
                               quote=" | ".join([f"p35: {q_road1_label}", f"p57: {q_road1_pue}",
                                                 f"p58: {q_road1_halls}", f"p54: {q_road1_headroom}",
                                                 f"p11: {q_road1_total}",
                                                 f"Table 5, p22: {q_road1_owner}"]))]),
        # Free substitute for a paid title search: the EIS states the ownership itself.
        dict(match=dict(id="SITE_JULIUS_AVE"),
             set=dict(notes=(
                 "City of Ryde. In Assessment. Julius Avenue is in the Macquarie Park corridor. "
                 f"LAND OWNERSHIP READ FROM THE EIS {TODAY} (free substitute for a paid NSW title "
                 "search, which the author has no budget for yet): the cover page states the "
                 "statement was 'Prepared by Willowtree Planning Pty Ltd on behalf of ISPT Pty Ltd' "
                 "for '6-8 JULIUS AVENUE, NORTH RYDE LOT 89 DP 1082131', and Table 6 'REGISTERED "
                 "LANDOWNERS' gives Lot/DP 89/1082131, Registered Landowner 'ISPT Pty Ltd', with "
                 "'Landowner's consent has been obtained from the above entity'. This is the "
                 "applicant's own statement of title, not a title search, and it is recorded as "
                 "such. owner_id is deliberately NOT set: the only ISPT entity in the record is "
                 "ENT_ISPT ('ISPT (Core Fund)'), and whether ISPT Pty Ltd is that fund's trustee or "
                 "a different vehicle is the reconciliation RG-005 is already asking about for "
                 "Mamre Road. One artefact noted: a single running header in the EIS reads '269 Lane "
                 "Cove Road, Macquarie Park' (the NEXTDC S5 address) against 628 mentions of Julius; "
                 "the cover page and Table 6 agree on Lot 89 DP 1082131, so the header is treated as "
                 "a template artefact, not as a second site."),
                 as_of_date=TODAY),
             add_sources=[dict(id=SRC_JULIUS_EIS,
                               quote=" | ".join([f"cover, p1: {q_julius_cover}",
                                                 f"Table 6, p33: {q_julius_owner}"]))]),
        dict(match=dict(id="SITE_NEXTDC_S5"),
             set=dict(owner_id="ENT_NEXTDC", as_of_date=TODAY,
                      notes=("269 Lane Cove Road, Macquarie Park. LAND OWNERSHIP READ FROM THE EIS "
                             f"{TODAY} (free substitute for a paid title search): 'Land Ownership "
                             "The site is owned by NEXTDC Limited.' owner_id set to ENT_NEXTDC, the "
                             "listed company (ASX: NXT). The EIS is already cited on this row by the "
                             "ssd_documents pack for its capacity and GFA, and the loader keeps one "
                             "quote per row and source (first writer wins), so the ownership "
                             "sentence is recorded here verbatim rather than as a second quote "
                             "against the same source.")),
             add_sources=[dict(id=SRC_S5_EIS, quote=q_s5_owner)]),
        dict(match=dict(id="SITE_23_25_WATERLOO"),
             set=dict(notes=notes_wat, as_of_date=TODAY),
             add_sources=[dict(id=SRC_REGISTER, quote=d_wat)]),
        dict(match=dict(id="SITE_TURNER_RD"),
             set=dict(it_capacity_mw=None, max_capacity_mw=None, notes=notes_turner,
                      fact_status="VERIFIED", confidence="high", as_of_date=TODAY,
                      source_id=SRC_REGISTER),
             add_sources=[dict(id=SRC_REGISTER, quote=d_turner)]),
        dict(match=dict(id="SITE_ORIORDAN"),
             set=dict(it_capacity_mw=None, max_capacity_mw=None, notes=notes_ori,
                      fact_status="VERIFIED", confidence="high", as_of_date=TODAY,
                      source_id=SRC_REGISTER),
             add_sources=[dict(id=SRC_REGISTER, quote=d_ori),
                          dict(id=SRC_ORIORDAN_SEARS, quote=q_ori_sears)]),
    ]

    gaps = [
        dict(match=dict(id=17),
             set=dict(notes=(
                 f"CITED {TODAY}, so the question is now publishable. What is public: NEXTDC S7's "
                 "scoping report (SSD-113934740, p36) states average daily water demand at about 70% "
                 "load of 5.44 ML/day and peak demand at full site maturity up to 7.79 ML/day, that "
                 "NEXTDC 'has commenced engagement with Sydney Water regarding interim potable water "
                 "supply for Stage 1, as well as potential recycled water opportunities, including "
                 "supply from the St Marys Advanced Water Treatment Plant', and that investigations "
                 "are underway with coNEXA to connect to the recycled water main associated with the "
                 "S4 development. What is NOT public: any agreement, allocation, trade waste consent "
                 "or capacity statement from the utilities themselves. Seventeen of the "
                 "observatory's NSW sites sit in the one Eastern Creek - Kemps Creek - Horsley Park "
                 "- Glendenning - Marsden Park corridor. RG-062 established that none of the 20 "
                 "archived consents requires recycled water; they impose a duty to prioritise "
                 "non-potable supply 'where available', and whether it is available is a utility "
                 "fact. Four requests are DRAFTED and NOT LODGED (author deferred lodging on "
                 f"{TODAY}): docs/requests/GIPA-004-sydney-water.md ($30), "
                 "FOI-005-melbourne-water.md ($34.50, also answers RG-080), "
                 "FOI-006-yarra-valley-south-east-water.md (two applications) and "
                 "RTI-001-unitywater.md ($59.60, not waivable). Nothing here is inferred from a "
                 "draft request; the question stays open until documents are released."),
                 fact_status="VERIFIED", confidence="high", as_of_date=TODAY,
                 source_id=SRC_S7_SCOPING),
             add_sources=[dict(id=SRC_S7_SCOPING, quote=" | ".join([
                 f"p36: {q_s7_water}", f"p36: {q_s7_sydneywater}", f"p36: {q_s7_conexa}"]))]),
        dict(id=105, pillar="A", priority=3, retrieval_method="manual_review", status="open",
             opened=TODAY,
             question=("Are Road 1 (SSD-80814238, SITE_ROAD_1) and 1-5 Khartoum Road "
                       "(SSD-63235720, SITE_KHARTOUM) two buildings on one Stockland M_Park campus, "
                       "or one project recorded twice? Both portal records give the address as "
                       "'1-5 Khartoum Road, Macquarie Park' and both sit on Lot 2 DP 1043041."),
             why_it_matters=("RG-084 removed one duplicate Macquarie Park row on exactly this kind "
                             "of evidence. Two rows sharing an address and a lot inflate the "
                             "campus count and any capacity summed across them: SSD-63235720 is "
                             "approved at 76.4 MW maximum power consumption and SSD-80814238 is in "
                             "assessment at 34.3 MW IT load. If they are stages of one campus the "
                             "figures must not be added as if they were separate sites; if they "
                             "are separate buildings the shared address needs distinguishing."),
             target_source=("Both projects' EIS and assessment reports on the NSW Planning Portal "
                            "(site plans, staging, lot and DP references); Stockland's M_Park "
                            "project pages and ASX announcements; the signed SSD-63235720 consent's "
                            "site description and any modification"),
             notes=(f"OPENED {TODAY} while implementing RG-099. NOT merged and NOT assumed to be "
                    "one project: they are two consents with different applicants' documents, "
                    "different figures and different stages (SSD-63235720 approved 11 March 2026; "
                    "SSD-80814238 in Assessment, More Information Required). The Road 1 EIS "
                    "glossary defines its Site as 'Part of Lot 2 Deposited Plan 1043041' and p11 "
                    "places it 'within the broader MPark Stockland landholding'; the SSD-63235720 "
                    "consent's Schedule 1 gives '1-5 Khartoum Road, Macquarie Park Part Lot 2 DP "
                    "1043041'. The portal's site name for SSD-63235720 is 'M_Park'. Both rows "
                    "keep their own figures and their own status until a document settles it. "
                    "Note the address fill in data/packs/site_portal_fields.json gives both rows "
                    "the same address, which is what surfaced this."),
             fact_status="VERIFIED", confidence="high", as_of_date=TODAY, source_id=SRC_ROAD1_EIS),
        # add_sources is only honoured on append-only inserts (loader defect 6): attach RG-105's
        # quotes with a follow-up match/set.
        dict(match=dict(id=105), set={}, add_sources=[
            dict(id=SRC_ROAD1_EIS, quote=" | ".join([q_road1_lot, f"Table 5, p22: {q_road1_owner}"])),
            dict(id=SRC_CONSENTS, quote=q_khartoum_schedule1),
        ]),
        dict(match=dict(id=61),
             set=dict(status="in_progress", notes=resolved_61, fact_status="VERIFIED",
                      confidence="high", as_of_date=TODAY, source_id=SRC_CONSENTS),
             add_sources=[
                 dict(id=SRC_CONSENTS, quote=" | ".join([
                     "SSD-73761707 B20: " + q_condition,
                     "SSD-73761707 B20(b): " + q_ppa,
                     "SSD-69223466 B19 and SSD-74069708 B22 carry the same wording; the other 16 "
                     "determinations in the archive carry none",
                 ])),
                 dict(id=SRC_GLEND_ASSESS, quote=f"p55: {q_glend_offer} | p56: {q_glend_imposed}"),
                 dict(id=SRC_APOLLO_ASSESS, quote=(f"p33: {q_apollo_epa} | p59: {q_apollo_offer} | "
                                                   f"p59: {q_apollo_doubt}")),
                 dict(id=SRC_PLUTO_ASSESS, quote=(f"p27: {q_pluto_epa} | p50: {q_pluto_emissions} | "
                                                  f"p50: {q_pluto_pv}")),
             ]),
        dict(match=dict(id=99),
             set=dict(status="resolved", resolved_date=TODAY, notes=resolved_99,
                      fact_status="VERIFIED", confidence="high", as_of_date=TODAY,
                      source_id=SRC_ROAD1_EIS),
             add_sources=[
                 dict(id=SRC_ROAD1_EIS, quote=f"p35: {q_road1_label} | p58: {q_road1_halls}"),
                 dict(id=SRC_REGISTER, quote=" | ".join([d_wat, d_turner, d_ori])),
                 dict(id=SRC_ORIORDAN_SEARS, quote=q_ori_sears),
                 dict(id=SRC_WATERLOO_SEARS, quote=("read in full " + TODAY + ": no MW or capacity "
                                                    "figure anywhere in the request")),
                 dict(id=SRC_S7_SCOPING, quote=f"p27: {q_s7_power} | p35: {q_s7_site}"),
             ]),
    ]

    pack = {
        "pack_id": "rg061-rg099-decisions-2026-11",
        "prepared_by": "scripts/curate_rg061_rg099.py from data/raw/nsw_planning/",
        "prepared_on": TODAY,
        "_comment": [
            "Author accepted the RG-061 and RG-099 findings on 2026-11-15.",
            "RG-061: the no-ratchet hypothesis is falsified for the renewable obligation; the gap",
            "stays in_progress because the other performance measures are untested and one",
            "determined project has no archived instrument.",
            "RG-099: resolved. Road 1 confirmed as IT load and Waterloo as total (no value change);",
            "S7 already held no figure; Turner (withdrawn) and O'Riordan (pre-EIS, 38 vs 45 MW)",
            "lose the unlabelled figure from every capacity column, as NEXTDC S7 did on 2026-10-14.",
            "Road 1's max_capacity_mw is deliberately NOT raised to the EIS's ~42 MW: that is an",
            "IT-side design ceiling and max_capacity_mw is the headline build-out ceiling.",
            "Every quote is extracted verbatim from the archived text and checked before writing.",
            "Free substitutes for the paid title searches (no budget yet): three archived EISs",
            "state land ownership themselves - Road 1 (Stockland), Julius Avenue (ISPT Pty Ltd,",
            "Lot 89 DP 1082131) and NEXTDC S5 (NEXTDC Limited, owner_id set). Recorded as the",
            "applicant's statement of title, not as a title search.",
            "Also: RG-017 becomes citable (the S7 scoping report is the public evidence that water",
            "agreements are being negotiated and are not published; four requests drafted, not",
            "lodged), and RG-105 opens on the address and lot Road 1 shares with SSD-63235720.",
        ],
        "sources": sources,
        "rows": {"sites": sites, "research_gaps": gaps},
    }
    with open(OUT_PACK, "w") as f:
        json.dump(pack, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print(f"RG-061 answered (renewable obligation, gap stays open); RG-099 resolved: "
          f"Road 1 IT load confirmed, Waterloo total confirmed, Turner and O'Riordan capacity "
          f"cleared; RG-017 cited; RG-105 opened; wrote {os.path.relpath(OUT_PACK, ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
