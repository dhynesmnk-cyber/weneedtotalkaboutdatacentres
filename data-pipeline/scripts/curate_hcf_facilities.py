#!/usr/bin/env python3
"""
The HCF register's facilities that had no site record (RG-096 follow-up, author-approved).

curate_hcf_register.py matched 26 existing site records to the Commonwealth's Certified Service
Providers register. Reading the whole register, not just the lines those records match, showed
13 further certified facilities and enclaves with no row at all. This script adds the ones an
operator's own page can place, and puts the rest to a human.

Added here (8), each on a grade-A page archived for this batch under data/raw/operators/:
  ADC Mitchell and ADC Fyshwick (ACT), NEXTDC B1 Brisbane and B2 Brisbane (QLD),
  Fujitsu Western Sydney and Homebush Bay (NSW), Polaris at Springfield Central (QLD),
  Macquarie IC3 East at Macquarie Park (NSW).

Held, not invented (5): Cloud Carrier DB1; DigiCo BNE2, ADL1 and SYD1; Vocus TransACT House
Dickson. The register gives a provider and a facility name and nothing else - no jurisdiction,
no address, no status - and sites.state and sites.status are NOT NULL. digico and cloudcarrier
refused the crawler's robots.txt check and are recorded in refused.json; Vocus's own data centre
page sells connectivity into other people's facilities and names none of its own. RG-101 carries
the register's own lines for all five so the next pass starts from evidence, not from a guess.

What is taken, and what is not:
  * it_capacity_mw only where the page labels the figure IT Capacity or IT Load, as in
    curate_operator_sources.py. Lower bounds ("over 14,500m2") are not values.
  * Technical space is not gross floor area, so it is quoted, not stored in gfa_sqm.
  * Fujitsu's 90 MW is a 2020 end-state for the whole Western Sydney campus, not a current
    capacity: quoted in the notes and in source_refs, not stored.
  * hcf_certified is NOT set here. curate_hcf_register.py fills it from the register with the
    register's own line quoted, which is the document that makes the claim.
  * Nothing is inferred about the five held facilities, and no existing row's status is changed:
    what Macquarie's own page says about IC3 Super West contradicts a grade-C seed value and goes
    to a human as RG-104, with the page quoted against the row.

Every quote is checked against the archived page (whitespace aside) and every page against its
SHA-256 manifest before anything is written. Two sources are copied verbatim out of the packs
that register them, so this pack can cite them without depending on load order.

Outputs:
  * data/packs/hcf_facilities.json

Run:
    python3 scripts/curate_hcf_facilities.py
    python3 scripts/load_pack.py data/packs/hcf_facilities.json --allow-missing-source
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys

import curate_hcf_register as hcf

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAGES = os.path.join(ROOT, "data", "raw", "operators")
OUT_PACK = os.path.join(ROOT, "data", "packs", "hcf_facilities.json")
TODAY = "2026-11-15"

SRC_REGISTER = "SRC_HCF_REGISTER"
SRC_FY26 = "SRC_NXT_FY26_PRESENTATION"

# (group, page) -> publisher, published date (None for an undated page).
PUBLISHER = {
    ("adc", "index"): ("Australian Data Centres", None),
    ("adc", "locations"): ("Australian Data Centres", None),
    ("polaris", "index"): ("Polaris Data Centre", None),
    ("fujitsu", "fujitsu-expands-australian-data-centre-footprint"): ("Fujitsu Australia Limited", "2020-09-30"),
    ("nextdc", "b1-brisbane"): ("NEXTDC Limited", None),
    ("nextdc", "b2-brisbane"): ("NEXTDC Limited", None),
    ("macquarie", "ic3-east"): ("Macquarie Data Centres Pty Ltd", None),
    ("macquarie", "ic3-super-west"): ("Macquarie Data Centres Pty Ltd", None),
}


def source_id(group: str, page: str) -> str:
    return f"SRC_OP_{group}_{page}".upper().replace("-", "_")


# Quotes read by a person from the archived text. Keys are used in the rows below.
QUOTES: dict[tuple[str, str], dict[str, str]] = {
    ("adc", "index"): {
        "both": "More than 10 years continuous operation at Mitchell and Fyshwick in Canberra ACT, "
                "with available capacity and options to grow.",
        "hcf": "HCF certified Strategic; all key personnel are Australian Citizen's with Government Clearance",
        "since": "Continuous Canberra operations since 2014.",
    },
    ("adc", "locations"): {
        "operational": "Operational – Canberra (Mitchell, Fyshwick)",
    },
    ("polaris", "index"): {
        "largest": "Polaris Data Centre is Queensland’s largest, 100% Australian owned data centre",
        "owner": "Polaris is 100% owned by the Springfield City Group, a 100% Queensland-owned business.",
        "where": "Located in Springfield, 25km from Brisbane’s CBD and 19km from Amberly Airbase.",
        "address": "11 Mary Mackenroth Lane Springfield Central QLD 4300",
        "size": "in Queensland with over 14,500m 2 over 5 levels, with over 7,000m 2 of raised technical floor space",
    },
    ("fujitsu", "fujitsu-expands-australian-data-centre-footprint"): {
        "six": "Fujitsu’s six data centre facilities are located in: Homebush Bay, Western Sydney, and North "
               "Ryde in New South Wales; Noble Park in Victoria; Eight Mile Plains in Queensland; and Malaga "
               "in Western Australia.",
        "90mw": "providing a combined total capacity of 90 megawatts at the Western Sydney data centre campus",
    },
    ("nextdc", "b1-brisbane"): {
        "intro": "Located in Brisbane's CBD, B1 Brisbane is a 2.25MW data centre designed and built to Uptime "
                 "Institute Tier III standards",
        "it": "2.25MW IT Capacity",
        "size": "B1 Brisbane CBD | 1,650m² | 2.25MW",
    },
    ("nextdc", "b2-brisbane"): {
        "intro": "Located in Fortitude Valley on the fringe of the Brisbane CBD, B2 Brisbane is a 12MW Tier IV "
                 "certified data centre",
        "it": "12MW IT Capacity",
        "size": "B2 Fortitude Valley | 6,000m² | 12MW",
    },
    ("macquarie", "ic3-east"): {
        "it": "12MW IT Load",
        "size": "11,700m 2 Technical space",
        "what": "IC3 is a next-generation, Tier III colocation data centre in Macquarie Park",
    },
    ("macquarie", "ic3-super-west"): {
        "it": "47MW IT Load",
        "status": "IC3 Super West is currently under construction with the entire end-state power secured.",
    },
}

FY26_QUOTE = ("B2 BRISBANE Total power planned 12MW Built capacity 6MW built, 2MW in progress "
              "Status Operational")

# The register's own lines for the facilities this batch does NOT create rows for.
HELD = [
    ("Cloud Carrier", "DB1", "facility", "Cloud Carrier – DB1"),
    ("DigiCo", "BNE2", "facility", "DigiCo – BNE2"),
    ("DigiCo", "ADL1", "enclave", "DigiCo – ADL1 and SYD1"),
    ("DigiCo", "SYD1", "enclave", "DigiCo – ADL1 and SYD1"),
    ("Vocus", "TransACT House Dickson", "enclave", "Vocus - TransACT House Dickson"),
]

ENTITIES = [
    dict(id="ENT_AUSTRALIAN_DC", name="Australian Data Centres", entity_type="colocation_operator",
         domicile="Australia", hq_country="Australia", website="https://www.ausdatacentre.com.au/",
         notes="Australian-owned colocation and build-to-suit provider. Its own page: 'Continuous "
               "Canberra operations since 2014' and 'More than 10 years continuous operation at "
               "Mitchell and Fyshwick in Canberra ACT'. The page also describes 'Strategic "
               "development of a 300MW+ AI-optimised Melbourne campus in accelerated planning', "
               "which is a lead for a future site record, not a fact recorded here.",
         fact_status="VERIFIED", source_id=source_id("adc", "index"), confidence="high", as_of_date=TODAY),
    dict(id="ENT_POLARIS_DC", name="Polaris Data Centre", entity_type="colocation_operator",
         domicile="Australia", hq_country="Australia", website="https://www.polarisdatacentre.com.au/",
         notes="Operator of the Polaris facility at Springfield Central, Queensland, on its own "
               "page. The Commonwealth HCF register names Springfield Real Estate Sales Pty Ltd as "
               "the certified service provider for Polaris Data Centre; how that entity relates to "
               "the Springfield City Group that owns the facility is not stated on the page "
               "(RG-103).",
         fact_status="VERIFIED", source_id=source_id("polaris", "index"), confidence="high", as_of_date=TODAY),
    dict(id="ENT_SPRINGFIELD_CITY_GROUP", name="Springfield City Group", entity_type="developer",
         domicile="Australia", hq_country="Australia",
         notes="Polaris Data Centre's own page: 'Polaris is 100% owned by the Springfield City "
               "Group, a 100% Queensland-owned business.' Recorded as the facility's owner.",
         fact_status="VERIFIED", source_id=source_id("polaris", "index"), confidence="high", as_of_date=TODAY),
]

ADC_NOTE = (
    "Australian Data Centres' own page: 'More than 10 years continuous operation at Mitchell and "
    "Fyshwick in Canberra ACT'; its locations page lists 'Operational – Canberra (Mitchell, "
    "Fyshwick)'. The Commonwealth HCF register lists {scope} (quoted on this row). Neither page "
    "states an address, a site area or a capacity, so none is recorded - RG-103."
)

SITES = [
    dict(id="SITE_ADC_MITCHELL", name="ADC Mitchell (Australian Data Centres)",
         operator_id="ENT_AUSTRALIAN_DC", suburb="Mitchell", state="ACT", market="NEM",
         status="operational",
         notes=ADC_NOTE.format(scope="ADC Mitchell as a Certified Strategic Facility") +
               " The operator also describes a 300MW+ AI-optimised Melbourne campus in accelerated "
               "planning; that is a separate, unlocated proposal and is not recorded as a site.",
         fact_status="VERIFIED", source_id=source_id("adc", "index"), confidence="high", as_of_date=TODAY,
         refs=[(("adc", "index"), "both"), (("adc", "index"), "since"), (("adc", "locations"), "operational")]),
    dict(id="SITE_ADC_FYSHWICK", name="ADC Fyshwick (Australian Data Centres)",
         operator_id="ENT_AUSTRALIAN_DC", suburb="Fyshwick", state="ACT", market="NEM",
         status="operational",
         notes=ADC_NOTE.format(scope="ADC Fyshwick as a Certified Strategic Enclave") +
               " A different provider's facilities in the same suburb: CDC's Fyshwick F1 and F2 are "
               "recorded under SITE_CDC_CANBERRA and are not this facility.",
         fact_status="VERIFIED", source_id=source_id("adc", "index"), confidence="high", as_of_date=TODAY,
         refs=[(("adc", "index"), "both"), (("adc", "locations"), "operational")]),
    dict(id="SITE_NEXTDC_B1", name="NEXTDC B1 Brisbane", operator_id="ENT_NEXTDC",
         suburb="Brisbane CBD", state="QLD", market="NEM", status="operational", it_capacity_mw=2.25,
         notes="NEXTDC's own B1 page: 'Located in Brisbane's CBD, B1 Brisbane is a 2.25MW data centre "
               "designed and built to Uptime Institute Tier III standards', labelled '2.25MW IT "
               "Capacity'; its portfolio table gives 1,650m² of technical space (not gross floor "
               "area, so no area field is filled). The HCF register lists Brisbane 1 as a Certified "
               "Strategic Enclave. No street address is published on the page - RG-103.",
         fact_status="VERIFIED", source_id=source_id("nextdc", "b1-brisbane"), confidence="high",
         as_of_date=TODAY,
         refs=[(("nextdc", "b1-brisbane"), "intro"), (("nextdc", "b1-brisbane"), "it"),
               (("nextdc", "b1-brisbane"), "size")]),
    dict(id="SITE_NEXTDC_B2", name="NEXTDC B2 Brisbane", operator_id="ENT_NEXTDC",
         suburb="Fortitude Valley", state="QLD", market="NEM", status="operational", it_capacity_mw=12.0,
         notes="NEXTDC's own B2 page: 'Located in Fortitude Valley on the fringe of the Brisbane CBD, "
               "B2 Brisbane is a 12MW Tier IV certified data centre', labelled '12MW IT Capacity', "
               "6,000m² in its portfolio table. The 12 MW recorded here is the facility's IT "
               "capacity as the operator states it, not delivered capacity: NEXTDC's FY26 results "
               "presentation (27 August 2026) reports 'Built capacity 6MW built, 2MW in progress' "
               "against 'Total power planned 12MW'. The HCF register lists Brisbane 2 as a Certified "
               "Strategic Enclave. No street address is published on the page - RG-103.",
         fact_status="VERIFIED", source_id=source_id("nextdc", "b2-brisbane"), confidence="high",
         as_of_date=TODAY,
         refs=[(("nextdc", "b2-brisbane"), "intro"), (("nextdc", "b2-brisbane"), "it"),
               (("nextdc", "b2-brisbane"), "size")],
         extra_refs=[(SRC_FY26, FY26_QUOTE)]),
    dict(id="SITE_FUJITSU_WSYD", name="Fujitsu Western Sydney Data Centre", operator_id="ENT_FUJITSU_AU",
         state="NSW", market="NEM", status="operational",
         notes="Fujitsu's own release of 30 September 2020 lists its six Australian facilities: "
               "'Homebush Bay, Western Sydney, and North Ryde in New South Wales; Noble Park in "
               "Victoria; Eight Mile Plains in Queensland; and Malaga in Western Australia'. The "
               "same release says further expansion phases would provide 'a combined total capacity "
               "of 90 megawatts at the Western Sydney data centre campus' - a 2020 end-state figure "
               "for the campus, not a current capacity, so no capacity field is filled (RG-103). "
               "The HCF register lists Western Sydney as a Certified Strategic Enclave. The release "
               "gives no suburb or street address for the campus.",
         fact_status="REPORTED", source_id=source_id("fujitsu", "fujitsu-expands-australian-data-centre-footprint"),
         confidence="medium", as_of_date="2020-09-30",
         refs=[(("fujitsu", "fujitsu-expands-australian-data-centre-footprint"), "six"),
               (("fujitsu", "fujitsu-expands-australian-data-centre-footprint"), "90mw")]),
    dict(id="SITE_FUJITSU_HOMEBUSH", name="Fujitsu Homebush Bay Data Centre", operator_id="ENT_FUJITSU_AU",
         suburb="Homebush Bay", state="NSW", market="NEM", status="operational",
         notes="The HCF register names this facility 'Homebush'. Fujitsu's own release of 30 "
               "September 2020 names 'Homebush Bay' among its six Australian facilities and lists no "
               "other Homebush facility; the two names are read as the same facility, which is why "
               "this row is REPORTED at medium confidence rather than VERIFIED. No address, area or "
               "capacity is stated - RG-103.",
         fact_status="REPORTED", source_id=source_id("fujitsu", "fujitsu-expands-australian-data-centre-footprint"),
         confidence="medium", as_of_date="2020-09-30",
         refs=[(("fujitsu", "fujitsu-expands-australian-data-centre-footprint"), "six")]),
    dict(id="SITE_POLARIS", name="Polaris Data Centre (Springfield Central)", operator_id="ENT_POLARIS_DC",
         owner_id="ENT_SPRINGFIELD_CITY_GROUP", suburb="Springfield Central", state="QLD", market="NEM",
         address="11 Mary Mackenroth Lane, Springfield Central QLD 4300", status="operational",
         notes="Polaris's own page: 'Queensland’s largest, 100% Australian owned data centre', "
               "'Located in Springfield, 25km from Brisbane’s CBD', address in its footer. It "
               "describes 'over 14,500m2 over 5 levels, with over 7,000m2 of raised technical floor "
               "space': both are lower bounds and technical space is not gross floor area, so no "
               "area field is filled. No capacity is published. The HCF register certifies Polaris "
               "Data Centre as a Strategic Enclave under Springfield Real Estate Sales Pty Ltd; the "
               "page says the facility is 100% owned by the Springfield City Group. How those "
               "entities relate, and which one operates the facility, is RG-103.",
         fact_status="VERIFIED", source_id=source_id("polaris", "index"), confidence="high", as_of_date=TODAY,
         refs=[(("polaris", "index"), "largest"), (("polaris", "index"), "owner"),
               (("polaris", "index"), "where"), (("polaris", "index"), "address"),
               (("polaris", "index"), "size")]),
    dict(id="SITE_MACQ_IC3E", name="Macquarie IC3 East (Macquarie Park)", operator_id="ENT_MACQUARIE_TG",
         suburb="Macquarie Park", state="NSW", market="NEM", status="operational", it_capacity_mw=12.0,
         notes="Macquarie Data Centres' own IC3 East page gives '12MW IT Load' and '11,700m2 "
               "Technical space' (technical space, not gross floor area, so no area field is "
               "filled), within what it calls its 65MW Macquarie Park campus. The HCF register "
               "lists IC3e as a Certified Strategic Enclave alongside IC1, IC2 and IC3. The "
               "campus's other building, IC3 Super West, is a separate facility and the subject of "
               "RG-104; this row is not a second record of it.",
         fact_status="VERIFIED", source_id=source_id("macquarie", "ic3-east"), confidence="high",
         as_of_date=TODAY,
         refs=[(("macquarie", "ic3-east"), "it"), (("macquarie", "ic3-east"), "size"),
               (("macquarie", "ic3-east"), "what")]),
]

# The ids this pack creates, so curate_hcf_register.py can tell a new row from a confirmation.
NEW_SITE_IDS = [s["id"] for s in SITES]

GAP_101 = dict(
    id=101, pillar="C", priority=3, retrieval_method="manual_review", status="open", opened=TODAY,
    question=("Where are the five HCF-certified facilities that still have no site record - Cloud "
              "Carrier DB1; DigiCo BNE2, ADL1 and SYD1; and Vocus TransACT House Dickson - who "
              "operates them, and what are their status and capacity?"),
    why_it_matters=("The register is the Commonwealth's own list of facilities cleared to host "
                    "government data. Five of its entries are missing from the observatory, so "
                    "the certified estate is under-counted and the sovereign-hosting map has "
                    "holes in exactly the providers that are hardest to see."),
    target_source=("Operators' own facility pages (cloudcarrier.com, digi-co.com.au, vocus.com.au); "
                   "ABR/ASIC for the operating entities; the HCF register itself"),
    notes="",  # filled in main() from the register's own lines and the recorded refusals
    fact_status="VERIFIED", source_id=SRC_REGISTER, confidence="high", as_of_date=TODAY,
)

GAP_103 = dict(
    id=103, pillar="A", priority=3, retrieval_method="manual_review", status="open", opened=TODAY,
    question=("Addresses, site areas and capacities for the eight facilities added from the HCF "
              "register (ADC Mitchell and Fyshwick, NEXTDC B1 and B2, Fujitsu Western Sydney and "
              "Homebush Bay, Polaris, Macquarie IC3 East), and which legal entity operates Polaris?"),
    why_it_matters=("These rows exist because the Commonwealth certifies them, not because a "
                    "planning record places them. Without an address they cannot be mapped, "
                    "matched to a consent, or checked for double-counting against the rows that "
                    "came from the planning portal."),
    target_source=("Operators' facility and contact pages; ABR/ASIC for Springfield Real Estate "
                   "Sales Pty Ltd and the Springfield City Group; NSW/QLD/ACT planning registers"),
    notes=(f"OPENED {TODAY}. What the archived pages do and do not state: Australian Data Centres "
           "names Mitchell and Fyshwick and says both are operational, but publishes no address, "
           "area or capacity for either. NEXTDC's B1 and B2 pages give IT capacity (2.25 MW, 12 MW) "
           "and technical space (1,650 m², 6,000 m²) but no street address; B2's delivered capacity "
           "(6 MW built, 2 MW in progress) is from its FY26 presentation, not its facility page. "
           "Fujitsu's only archived document is a 30 September 2020 release: it places Western "
           "Sydney and Homebush Bay in NSW and gives a 90 MW end-state for the Western Sydney "
           "campus, which is six years old and is not a current capacity. Polaris publishes an "
           "address and lower-bound areas ('over 14,500m2', 'over 7,000m2') but no capacity, and "
           "its owner (Springfield City Group) is not the entity the register certifies "
           "(Springfield Real Estate Sales Pty Ltd). Macquarie's IC3 East page gives 12 MW IT load "
           "and 11,700 m² of technical space. No lower bound and no technical-space figure has "
           "been stored as a value."),
    fact_status="VERIFIED", source_id=SRC_REGISTER, confidence="high", as_of_date=TODAY,
)

GAP_104 = dict(
    id=104, pillar="A", priority=3, retrieval_method="manual_review", status="open", opened=TODAY,
    question=("Is SITE_MACQ_IC3 - recorded as 'IC3 Super West', operational, from a grade-C "
              "directory - the register's certified 'IC3', when Macquarie's own page says IC3 "
              "Super West is under construction with 47 MW of IT load?"),
    why_it_matters=("A facility recorded as operational that its operator says is still being "
                    "built inflates the operating estate, and the register's IC3 and IC3e entries "
                    "cannot be assigned to buildings until it is settled. Macquarie Park is the "
                    "cluster where the record has already double-counted once (RG-084)."),
    target_source=("Macquarie Data Centres' IC3 Super West and IC3 East pages (archived); the HCF "
                   "register; Macquarie Technology Group's ASX announcements"),
    notes=(f"OPENED {TODAY}. Macquarie's own IC3 Super West page, read for this batch, says 'IC3 "
           "Super West is currently under construction with the entire end-state power secured', "
           "gives '47MW IT Load' and lists the facility as 'Coming Soon'. SITE_MACQ_IC3 is named "
           "'IC3 Super West (Macquarie Park)' and recorded operational on SRC_CERTSTRAT, a grade-C "
           "directory. The register lists 'IC1, IC2, IC3 and IC3e' as Certified Strategic "
           "Enclaves; IC3 East is operational at 12 MW IT load and is added by this batch as "
           "SITE_MACQ_IC3E. Which building each register name denotes, and whether a facility "
           "under construction can hold Strategic certification, is for a human. NO VALUE IS "
           "CHANGED HERE: the page is quoted against the existing row so the contradiction is on "
           "the record, not resolved by an agent."),
    fact_status="REPORTED", source_id=source_id("macquarie", "ic3-super-west"), confidence="medium",
    as_of_date=TODAY,
)


def normalise(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def words(text: str) -> list[str]:
    return re.findall(r"[A-Za-z0-9-]+", text)


def numbers(text: str) -> set[float]:
    return {float(n.replace(",", "")) for n in re.findall(r"\d[\d,]*(?:\.\d+)?", text)}


def source_from_pack(pack_name: str, sid: str, errors: list[str]) -> dict | None:
    """A source definition copied verbatim from the pack that registers it, so this pack can
    cite it without a load-order dependency. Never a second, divergent definition."""
    path = os.path.join(ROOT, "data", "packs", pack_name)
    if not os.path.exists(path):
        errors.append(f"{pack_name}: not found; cannot cite {sid}")
        return None
    for s in json.load(open(path, encoding="utf-8")).get("sources", []):
        if s.get("id") == sid:
            return s
    errors.append(f"{pack_name}: does not register {sid}")
    return None


def main() -> int:
    errors: list[str] = []
    pages: dict[tuple[str, str], dict] = {}
    for (group, page), (publisher, published) in sorted(PUBLISHER.items()):
        base = os.path.join(PAGES, group, page)
        meta_path = base + ".html.meta.json"
        if not os.path.exists(meta_path):
            errors.append(f"{group}/{page}: not archived")
            continue
        meta = json.load(open(meta_path))
        if hashlib.sha256(open(base + ".html", "rb").read()).hexdigest() != meta["sha256"]:
            errors.append(f"{group}/{page}: fails its SHA-256 check")
        pages[(group, page)] = dict(text=normalise(open(base + ".txt", encoding="utf-8").read()),
                                    meta=meta, publisher=publisher, published=published)

    for key, quotes in QUOTES.items():
        if key not in pages:
            continue
        for label, quote in quotes.items():
            if normalise(quote) not in pages[key]["text"]:
                errors.append(f"{key[0]}/{key[1]} {label}: quote not found: {quote[:70]!r}")

    fy26_text_path = os.path.join(PAGES, "nextdc", "NEXTDC_FY26_Results_Presentation.txt")
    if normalise(FY26_QUOTE) not in normalise(open(fy26_text_path, encoding="utf-8").read()):
        errors.append("FY26 presentation: the B2 built-capacity quote is not in the archived text")

    # The register lines quoted in RG-101 must be the register's own words, read from the archive
    # through the same parser curate_hcf_register.py uses (which also checks its SHA-256).
    raw_register = open(hcf.ARCHIVE, "rb").read()
    register_meta = json.load(open(hcf.ARCHIVE + ".meta.json"))
    if hashlib.sha256(raw_register).hexdigest() != register_meta["sha256"]:
        errors.append("archived HCF register fails its SHA-256 check")
    entries = hcf.register(hcf.page_text(raw_register.decode("utf-8")), errors)
    listed = {e["line"]: e for lines in entries.values() for e in lines}
    for provider, facility, scope, line in HELD:
        e = listed.get(line)
        if e is None:
            errors.append(f"register line for {provider} {facility} is not in the register: {line!r}")
        elif e["scope"] != scope or facility not in e["facilities"]:
            errors.append(f"{provider} {facility}: register says {e['scope']}, {e['facilities']}")
    for site in SITES:
        if site["id"] not in hcf.MATCHES:
            errors.append(f"{site['id']}: not in curate_hcf_register.py MATCHES, so the register "
                          f"would never certify it")
    if hcf.CREATED_HERE != set(NEW_SITE_IDS):
        errors.append("curate_hcf_register.py CREATED_HERE and this pack's rows disagree: "
                      f"{sorted(hcf.CREATED_HERE ^ set(NEW_SITE_IDS))}")

    rows = []
    quote_rows = []
    for site in SITES:
        row = {k: v for k, v in site.items() if k not in ("refs", "extra_refs")}
        refs: dict[tuple[str, str], list[str]] = {}
        for key, label in site["refs"]:
            refs.setdefault(key, []).append(QUOTES[key][label])
        add_sources = [dict(id=source_id(g, p), quote=" | ".join(qs)) for (g, p), qs in refs.items()]
        add_sources += [dict(id=sid, quote=q) for sid, q in site.get("extra_refs", [])]
        # A capacity must be a number its own quote states, and an address must be in its quote.
        for key, label in site["refs"]:
            q = QUOTES[key][label]
            if "it_capacity_mw" in row and label == "it":
                if float(row["it_capacity_mw"]) not in numbers(q):
                    errors.append(f"{row['id']}: {row['it_capacity_mw']} is not stated in {q!r}")
            if "address" in row and label == "address":
                if " ".join(words(row["address"])) not in " ".join(words(q)):
                    errors.append(f"{row['id']}: the address is not stated in {q!r}")
        # NB: the loader only honours add_sources on append-only inserts. A sites row has a text
        # primary key, so its quotes are attached by a follow-up match/set, which is the pattern
        # every other pack uses (see PROJECT-REVIEW.md, loader defect 6).
        rows.append(row)
        quote_rows.append(dict(match=dict(id=row["id"]), set={}, add_sources=add_sources))

    if errors:
        print("refusing to write; fix these first:", file=sys.stderr)
        for e in errors:
            print(f"  {e}", file=sys.stderr)
        return 1

    sources = []
    for (group, page), p in sorted(pages.items()):
        meta = p["meta"]
        sources.append(dict(
            id=source_id(group, page),
            title=f"{p['publisher']} - {page.replace('-', ' ')} (web page)",
            publisher=p["publisher"], url=meta["url"], doc_type="primary_company",
            published=p["published"], credibility="A", accessed=meta["fetched_utc"][:10],
            notes=(f"The operator's own page, read {meta['fetched_utc'][:10]}, SHA-256 "
                   f"{meta['sha256']}, archived at data/raw/operators/{group}/{page}.html with its "
                   f"visible text in .txt. Cited for the facts quoted in source_refs."),
        ))
    for pack_name, sid in (("hcf_register.json", SRC_REGISTER), ("super_and_openai.json", SRC_FY26)):
        s = source_from_pack(pack_name, sid, errors)
        if s:
            sources.append(s)

    refusals = []
    for group in ("digico", "cloudcarrier"):
        path = os.path.join(PAGES, group, "refused.json")
        if os.path.exists(path):
            for url, rec in json.load(open(path, encoding="utf-8")).items():
                refusals.append(f"{url} - {rec['how']} ({rec['checked_utc'][:10]})")
    held_lines = "; ".join(f"{provider} - {facility} ({scope}), register line '{line}'"
                           for provider, facility, scope, line in HELD)
    GAP_101["notes"] = (
        f"OPENED {TODAY} from the Commonwealth register (SRC_HCF_REGISTER). The register gives a "
        f"provider and a facility name and nothing else - no jurisdiction, address, status or "
        f"capacity - and sites.state and sites.status are required, so no row has been invented "
        f"for these five: {held_lines}. Attempts to place them: "
        + ("; ".join(refusals) if refusals else "no fetch attempted")
        + ". Both refusals are recorded in data/raw/operators/<group>/refused.json and were not "
          "worked around. Vocus's own wholesale data centre page was archived "
          "(data/raw/operators/vocus/data-centres.txt): it sells connectivity into more than 150 "
          "data centres and names none of its own facilities, so it does not place TransACT House. "
          "DigiCo SYD1 needs care: SITE_DIGICO_SYD1 already records the SYD1 EXPANSION project "
          "from a NSW consent, while the register certifies an enclave in the existing facility. "
          "A new row must distinguish the two before it is created, or the record repeats the "
          "double-count RG-084 removed. Eight other register facilities were placed from "
          "operators' own pages and are added by this pack; their missing fields are RG-103."
    )

    # The IC3 Super West page goes against the existing row as evidence, changing no value.
    sites_updates = [dict(
        match=dict(id="SITE_MACQ_IC3"), set={},
        add_sources=[dict(id=source_id("macquarie", "ic3-super-west"),
                          quote=f"{QUOTES[('macquarie', 'ic3-super-west')]['status']} | "
                                f"{QUOTES[('macquarie', 'ic3-super-west')]['it']}")],
    )]

    pack = {
        "pack_id": "hcf-facilities-2026-11",
        "prepared_by": "scripts/curate_hcf_facilities.py from data/raw/operators/",
        "prepared_on": TODAY,
        "_comment": [
            "Adds the HCF register's facilities that had no site record, where an operator's own",
            "page places them: ADC Mitchell and Fyshwick, NEXTDC B1 and B2, Fujitsu Western Sydney",
            "and Homebush Bay, Polaris, Macquarie IC3 East. hcf_certified is left to",
            "hcf_register.json, which loads next and fills it with the register's line quoted.",
            "Five facilities are held as RG-101 rather than guessed at; missing fields on the new",
            "rows are RG-103; the IC3 Super West contradiction is RG-104 and changes no value.",
        ],
        "sources": sources,
        "rows": {"entities": ENTITIES, "sites": rows + quote_rows + sites_updates,
                 "research_gaps": [GAP_101, GAP_103, GAP_104]},
    }
    with open(OUT_PACK, "w") as f:
        json.dump(pack, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print(f"{len(pages)} operator pages verified; {len(rows)} facilities added, "
          f"{len(HELD)} held as RG-101; wrote {os.path.relpath(OUT_PACK, ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
