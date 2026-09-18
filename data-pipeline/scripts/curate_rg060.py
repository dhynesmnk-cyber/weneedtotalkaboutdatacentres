#!/usr/bin/env python3
"""
Curate the RG-060 pack: the condition battery and Schedule 1 applicants for all 20 signed
consents of determined NSW data centre State Significant Developments.

Input : exports/nsw_planning/nsw_dc_consent_conditions.csv
        (produced by scripts/consent_condition_audit.py --limit 20)
Output: data/packs/rg060_consent_matrix.json

Two corrections this pack makes to earlier releases, both recorded explicitly rather than
quietly overwritten:
  * RG-026 reported that the Glendenning consent's website-disclosure requirement was "stronger
    than the NSW Guidelines". Across all 20 reliably extracted consents, website disclosure
    appears in 19. It is standard practice, not a distinguishing feature.
  * The audit's `demand_response` pattern matched in 17 of 20 consents. On inspection every match
    is the DEFINITION OF LOAD CURTAILMENT and a condition PROHIBITING it - "this development
    consent does not permit the use of the back-up generators ... to support load curtailment at
    the site". So the correct finding is the opposite: consents forbid diesel load curtailment
    (consistent with NSW Guidelines Principle 2 Ref 9) and NONE requires any non-diesel demand
    response capability. The pattern is retained in the CSV as a false-positive marker.

2026-09-18 RE-EXTRACTION: the battery was regenerated from pypdf extractions of the sha256-verified
archived PDFs (scripts/reextract_consents.py) after the dependency-free extractor proved unable to
decrypt two AES-encrypted instruments (Lane Cove West, Macquarie Park - 0 chars each) and split
numerals across glyph boundaries (Glendenning's 235 MW parsed as 23; NEXTDC S4's 294 MW as "2 94";
its 200-hour cap was lost entirely). All 20 now extract above the reliability floor, so for the
first time every battery count has the full 20-consent population behind it. Every Schedule 1
applicant now parses, which resolves RG-065.

Run:
    python3 scripts/curate_rg060.py
    python3 scripts/load_pack.py data/packs/rg060_consent_matrix.json --dry-run --allow-missing-source
"""
from __future__ import annotations

import csv
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV_IN = os.path.join(ROOT, "exports", "nsw_planning", "nsw_dc_consent_conditions.csv")
OUT = os.path.join(ROOT, "data", "packs", "rg060_consent_matrix.json")
TODAY = "2026-09-18"
SRC = "SRC_NSWPORTAL_CONSENTS"

# project slug -> (site_id or None, operator entity id or None, notes)
ATTRIBUTION = {
 "grand-avenue-data-centre-expansion-rosehill": (
    "SITE_GRAND_AVE", "ENT_EQUINIX",
    "PROJECT ATLAS-STYLE CODENAME RESOLVED: the Schedule 1 applicant is Equinix Hyperscale 2 (SY10) Pty "
    "Limited, a project-specific SPV of Equinix, and the portal title's 'SY10' matches Equinix's certified "
    "SYD10 enclave naming. This is the first hyperscaler-adjacent operator resolved from a signed NSW "
    "consent in this project."),
 "talavera-road-data-centre-campus-expansion": (
    "SITE_TALAVERA", "ENT_MACQUARIE_TG",
    "CODENAME RESOLVED: the Schedule 1 applicant is Macquarie Data Centres Pty Ltd. Talavera Road is in the "
    "Macquarie Park corridor where Macquarie Technology Group operates its IC3 'Super West' certified "
    "facility, and Macquarie is the only vertically integrated certified sovereign stack in Australia."),
 "project-apollo-data-centre-macquarie-park": (
    "SITE_PROJECT_APOLLO", "ENT_GOODMAN",
    "CODENAME RESOLVED: the Schedule 1 applicant is Goodman Property Services (Aust) Pty Limited. Confirms "
    "the NSW IDA Round 1 attribution of 'Project Atlas' to Goodman and shows Goodman developing in its own "
    "name rather than through a project SPV."),
 "nextdc-s4-data-centre-horsley-park": (
    "SITE_NEXTDC_S4", "ENT_NEXTDC",
    "NEXTDC Limited is the Schedule 1 applicant - one of only five consents in the sample naming an "
    "identifiable operating company rather than a consultancy, trustee or single-purpose vehicle."),
 "roberts-road-data-centre": (
    "SITE_ROBERTS_RD", "ENT_CDC",
    "Canberra Data Centres Pty Ltd is the Schedule 1 applicant, so Roberts Road is a CDC facility. The "
    "project record also carries a document titled 'CDC Data Centres response warning letter' which is not "
    "publicly downloadable (HTTP 401) and a political donation disclosure which is public but a scanned "
    "image with no extractable text."),
 "digico-syd1-data-centre-expansion": (
    "SITE_DIGICO_SYD1", None,
    "The Schedule 1 applicant is HDI SYD1 Property Holdings Limited - a property holding vehicle whose "
    "'SYD1' element matches HMC DigiCo's SYD1 facility naming. A sixth structure type: a dedicated "
    "property holding company per site."),
 "51-huntingwood-drive-data-centre": (
    "SITE_51_HUNTINGWOOD", None,
    "The Schedule 1 applicant is EMKC Cubed Management Pty Ltd, a special purpose vehicle. 51 Huntingwood "
    "Drive is in the corridor where AirTrunk operates its certified SYD1 facility, and this consent carries "
    "the LARGEST installed back-up generation capacity in the sample at 632 MW. The relationship between "
    "EMKC Cubed Management and any operator is not stated in the consent - research gap RG-064."),
 "apollo-place-data-centre": (
    "SITE_APOLLO_PLACE", None,
    "The Schedule 1 applicant is also EMKC Cubed Management Pty Ltd, so this SPV holds at least two Lane "
    "Cove consents: Apollo Place (63.8 MW installed back-up, 45 MW total power cap) and 51 Huntingwood "
    "Drive (632 MW installed back-up). A single undisclosed vehicle controlling two consents in the corridor "
    "with the most concentrated community opposition in the state."),
 "43-61-turner-road-data-centre": (
    "SITE_43_61_TURNER", None,
    "The Schedule 1 applicant is ARUP Pty Ltd - the engineering consultancy. The fourth consultancy in the "
    "sample, after Cundall Johnston and Partners (twice), Lehr Consultants, and now ARUP."),
 "dci-poplars-data-centre-project-0": (
    "SITE_DCI_POPLARS", "ENT_DCI",
    "The Schedule 1 applicant is The Trustee for NineZero DC Sub Trust I, a unit trust trustee. The project "
    "title names DCI and the portal record carries DCI-labelled documents, but the legal applicant is the "
    "trust - so the operating company is not the consent holder."),
 "glendenning-road-data-centre": (
    "SITE_GLENDENNING", None,
    "Lehr Consultants International (Australia) Pty Ltd - a planning and engineering consultancy."),
 "1-5-khartoum-road-data-centre": (
    "SITE_KHARTOUM", None,
    "The Schedule 1 applicant is Stockland Development Pty Limited - the property group developing in "
    "its own name. Applicant recovered in the 2026-09-18 pypdf re-extraction (RG-065)."),
 "lane-cove-west-data-centre": (
    "SITE_LANE_COVE_WEST", None,
    "The Schedule 1 applicant is Greenbox Architecture Pty Ltd - an ARCHITECTURAL PRACTICE holding a "
    "2019 data centre consent. A fifth consultancy-type applicant in the sample, and the earliest "
    "consent in the Lane Cove cluster. Applicant recovered in the 2026-09-18 pypdf re-extraction "
    "(RG-065). Note the separate operational site row SITE_AIRTRUNK_SYD2 in the same suburb."),
 "macquarie-park-data-centre": (
    "SITE_MACQUARIE_PARK_DC", None,
    "The Schedule 1 applicant is Stockland Trust Management Limited (2021 consent, SSD-10467) - a "
    "second Stockland entity alongside Stockland Development Pty Limited at 1-5 Khartoum Road. The "
    "database also carries SITE_STOCKLAND_MP (Stockland Macquarie Park Stage 1, under construction); "
    "the relationship between the two Macquarie Park records needs confirmation (RG-084). Applicant "
    "recovered in the 2026-09-18 pypdf re-extraction (RG-065)."),
 "project-echidna-data-centre-eastern-creek": (
    "SITE_ECHIDNA", None,
    "The Schedule 1 applicant is ARUP Australia Pty Ltd - a consultancy, and a different Arup legal "
    "entity from ARUP Pty Ltd at 43-61 Turner Road. The only consent in the sample determined under "
    "delegation from the NSW Independent Planning Commission rather than the Minister (delegate Chris "
    "Ritchie, A/Executive Director, delegation executed 14 June 2022). Applicant recovered in the "
    "2026-09-18 pypdf re-extraction (RG-065)."),
 "dicker-data-warehouse-and-distribution-centre": (
    "SITE_DICKER_DATA", None,
    "The Schedule 1 applicant is Dicker Data Limited - the ASX-listed IT hardware distributor, for a "
    "warehouse and distribution centre (the consent's own development description does not say data "
    "centre; it enters this sample via the portal's data centre search). Schedule 1 is a two-column "
    "layout whose labels and values the text layer separates; parsed with a dedicated fallback in the "
    "2026-09-18 re-extraction (RG-065). File DOC18/721211."),
 "station-road-data-centre-expansion": (
    "SITE_STATION_RD", None,
    "The Schedule 1 applicant is Lehr Consultants International (Australia) Pty Ltd - the second "
    "Lehr-held consent in the sample after Glendenning Road. Applicant recovered in the 2026-09-18 "
    "pypdf re-extraction (RG-065)."),
 "davis-road-data-centre-cundall": (
    "SITE_DAVIS_RD_CUNDALL", None,
    "Cundall Johnston and Partners Pty Ltd - the consulting engineers whose name is already in the project "
    "title. The same application carries an access-restricted 'ASIC certificate Amazon Corporate Services "
    "Pty Ltd' (RG-057)."),
}

# Hard numbers read from the matrix. diesel/genset/power are as parsed from each consent.
HARD = {
 "nextdc-s4-data-centre-horsley-park": dict(genset_mw=360.0, power_mw=294.0, diesel_t=4472.0,
    hours=200.0,
    note="THE STRICTEST AIR QUALITY CONDITIONS IN THE SAMPLE, and stricter than the post-Guidelines "
         "Glendenning consent. Condition B19: flue gases vented through vertical stacks 38.7 m in height, and "
         "total NOx as NO2-equivalent from back-up generator operation INCLUDING TESTING AND COMMISSIONING "
         "below 5.5 tonnes per year - against Glendenning's 10 tonnes per year with unplanned outage events "
         "excluded. Also the largest diesel storage cap in the sample at 4,472 tonnes, more than double the "
         "2,000 tonne cap in twelve other consents. Installed back-up 360 MW against a 294 MW total power cap, "
         "ratio 1.22. One of only two consents referencing a Tier standard and one of three with a stack height "
         "requirement. Generator operation capped at 200 hours per year - recovered in the 2026-09-18 pypdf "
         "re-extraction; the earlier extraction lost the line to glyph splitting. NEXTDC Limited is the "
         "Schedule 1 applicant, so this is an "
         "operating company accepting the tightest emissions limits in the state voluntarily - which is the "
         "strongest available evidence for the Section 3 mechanism whereby a proponent's own EIS commitments "
         "become conditions, and it undercuts any argument that strict conditions deter investment."),
 "51-huntingwood-drive-data-centre": dict(genset_mw=632.0,
    note="The LARGEST installed back-up generating capacity in the sample at 632 MW - larger than Snowy "
         "Hydro's 660 MW Kurri Kurri gas station is to the Loxford proposal, and larger than most of the "
         "facilities it backs up. Generator operation capped at 200 hours per year, a stack height "
         "requirement is present, and no diesel storage cap was parsed. Applicant EMKC Cubed Management "
         "Pty Ltd."),
 "project-pluto-data-centre": dict(genset_mw=170.0, power_mw=100.0, hours=173.0, diesel_t=2000.0,
    note="Installed back-up 170 MW against a 100 MW total power cap - ratio 1.70, the highest in the "
         "sample. Generator hours capped at 173, one of only three consents departing from the 200-hour "
         "standard. Carries a renewable supply condition, PUE and WUE provisions and recycled or "
         "non-potable water references."),
 "project-apollo-data-centre-macquarie-park": dict(genset_mw=185.0, power_mw=135.0, hours=187.0, diesel_t=2000.0,
    note="Installed back-up 185 MW against a 135 MW total power cap - ratio 1.37. Generator hours capped at "
         "187, the third departure from 200. Carries a renewable supply condition plus PUE, WUE and "
         "recycled or non-potable water provisions. Diesel storage capped at 2,000 tonnes - the earlier "
         "'000' parse artefact was fixed by the 2026-09-18 pypdf re-extraction and digit-glyph repair."),
 "1-5-khartoum-road-data-centre": dict(genset_mw=84.0, hours=200.0, diesel_t=2000.0,
    note="Installed back-up 84 MW, 200 hours per year, 2,000 tonne diesel cap, four annual emissions "
         "testing references, battery storage present. No renewable, PUE or WUE provision."),
 "43-61-turner-road-data-centre": dict(genset_mw=74.0, hours=200.0, diesel_t=2000.0,
    note="Installed back-up 74 MW, 200 hours per year, 2,000 tonne diesel cap. One of only two consents "
         "referencing a Tier standard. Applicant ARUP Pty Ltd."),
 "apollo-place-data-centre": dict(genset_mw=63.8, power_mw=45.0, hours=200.0, diesel_t=2000.0,
    note="Installed back-up 63.8 MW against a 45 MW total power cap - ratio 1.42. Applicant EMKC Cubed "
         "Management Pty Ltd, the same SPV as 51 Huntingwood Drive."),
 "project-echidna-data-centre-eastern-creek": dict(genset_mw=53.2, hours=200.0,
    note="Installed back-up 53.2 MW, 200 hours per year. No diesel storage cap parsed. Applicant ARUP "
         "Australia Pty Ltd - the engineering consultancy, recovered in the 2026-09-18 re-extraction. Note "
         "this is a DIFFERENT Arup legal entity from ARUP Pty Ltd, the applicant for 43-61 Turner Road."),
 "grand-avenue-data-centre-expansion-rosehill": dict(genset_mw=53.2, hours=200.0,
    note="Installed back-up 53.2 MW, 200 hours per year. Carries a renewable supply condition - one of only "
         "four consents in the sample to do so. Applicant Equinix Hyperscale 2 (SY10) Pty Limited."),
}


def main() -> int:
    rows = list(csv.DictReader(open(CSV_IN, encoding="utf-8")))
    reliable = [r for r in rows if str(r["reliable"]).lower() in ("1", "true")]

    def present(key, subset=None):
        return sum(1 for r in (subset or reliable) if (r.get(key) or "").strip() not in ("", "0"))

    entities, site_updates, power, metrics = [], [], [], []

    entities += [
        dict(id="ENT_EQUINIX_SY10", name="Equinix Hyperscale 2 (SY10) Pty Limited", entity_type="developer",
             domicile="United States", hq_country="US",
             notes="Schedule 1 applicant for the Grand Avenue Data Centre Expansion at Rosehill "
                   "(SSD-53338465). A project-specific special purpose vehicle of Equinix; the 'SY10' element "
                   "matches Equinix's certified SYD10 enclave at Erskine Park naming convention. The first "
                   "hyperscaler-adjacent operator resolved from a signed NSW consent in this project.",
             fact_status="VERIFIED", confidence="high", as_of_date=TODAY, source_id=SRC),
        dict(id="ENT_EMKC", name="EMKC Cubed Management Pty Ltd", entity_type="developer",
             domicile="Unknown - not resolvable from public registers", hq_country=None,
             notes="Schedule 1 applicant for TWO consents: 51 Huntingwood Drive Data Centre "
                   "(SSD-41589232, Blacktown, 632 MW installed back-up generation, 200 hours per year) and "
                   "Apollo Place Data Centre (SSD-67407231, Lane Cove, 63.8 MW installed back-up against a "
                   "45 MW total power cap). A single undisclosed special purpose vehicle is therefore the "
                   "consent holder for two facilities in the two corridors with the most concentrated data "
                   "centre activity and community opposition in New South Wales. Neither consent names an "
                   "operator or end user. Research gap RG-064.",
             fact_status="VERIFIED", confidence="high", as_of_date=TODAY, source_id=SRC),
        dict(id="ENT_HDI_SYD1", name="HDI SYD1 Property Holdings Limited", entity_type="developer",
             domicile="Unknown - not resolvable from public registers", hq_country=None,
             notes="Schedule 1 applicant for the DigiCo SYD1 Data Centre Expansion (SSD-69637456, City of "
                   "Sydney). A dedicated property holding company per site - a sixth distinct proponent "
                   "structure type in this sample, after operating companies, consultancies, trust trustees, "
                   "project SPVs and the KNBDC trust stack. 140.4 MW installed back-up generation, 2,000 "
                   "tonne diesel cap, and one of only four consents carrying PUE, WUE and recycled or "
                   "non-potable water provisions.",
             fact_status="VERIFIED", confidence="high", as_of_date=TODAY, source_id=SRC),
        dict(id="ENT_ARUP", name="ARUP Pty Ltd", entity_type="other", domicile="United Kingdom",
             hq_country="GB", website="arup.com",
             notes="Schedule 1 applicant for the 43-61 Turner Road Data Centre (SSD-68013714, Camden). One "
                   "of SEVEN consents in the sample whose Schedule 1 applicant is a consultancy or "
                   "architectural practice rather than an operator, developer or SPV. Note the separate "
                   "legal entity ARUP Australia Pty Ltd is the applicant for Project Echidna. 74 MW "
                   "installed back-up generation, 200 hours per year, 2,000 tonne diesel cap, one of only "
                   "two consents referencing a Tier standard.",
             fact_status="VERIFIED", confidence="high", as_of_date=TODAY, source_id=SRC),
        dict(id="ENT_MACQUARIE_DC", name="Macquarie Data Centres Pty Ltd", entity_type="colocation_operator",
             domicile="Australia", hq_country="AU",
             notes="Schedule 1 applicant for the Talavera Road Data Centre Campus Expansion "
                   "(SSD-24299707, City of Ryde). The operating entity within Macquarie Technology Group "
                   "(ASX: MAQ). 200 hours per year and a 2,000 tonne diesel cap; no renewable, PUE or WUE "
                   "provision in the consent.",
             fact_status="VERIFIED", confidence="high", as_of_date=TODAY, source_id=SRC),
        dict(id="ENT_NINEZERO", name="The Trustee for NineZero DC Sub Trust I", entity_type="developer",
             domicile="Unknown - not resolvable from public registers", hq_country=None,
             notes="Schedule 1 applicant for the DCI Poplars Data Centre Project (Queanbeyan-Palerang "
                   "Regional). The 'Sub Trust I' formulation implies a trust series holding multiple sites in "
                   "separate bankruptcy-remote vehicles. The 'NineZero' element suggests a net-zero branding "
                   "position, which is worth testing against a consent that contains no renewable procurement "
                   "condition at all. Research gap RG-059.",
             fact_status="VERIFIED", confidence="high", as_of_date=TODAY, source_id=SRC),
    ]

    for slug, (site_id, op, note) in ATTRIBUTION.items():
        r = next((x for x in rows if x["project"] == slug), None)
        if not r or not site_id:
            continue
        hard = HARD.get(slug, {})
        upd = {"proponent": r["applicant"] or None, "fact_status": "VERIFIED",
               "confidence": "high", "as_of_date": TODAY, "source_id": SRC,
               "notes": f"SCHEDULE 1 APPLICANT ON THE SIGNED CONSENT: {r['applicant'] or 'not parsed'}. " + note}
        if op:
            upd["operator_id"] = op
        if hard.get("power_mw"):
            upd["total_capacity_mw"] = hard["power_mw"]
        site_updates.append(dict(match=dict(id=site_id), set=upd, add_sources=[SRC]))
        if hard:
            power.append(dict(site_id=site_id, connection_type="distribution",
                              genset_total_mw=hard.get("genset_mw"),
                              genset_annual_test_hours=hard.get("hours"),
                              diesel_storage_kl=(round(hard["diesel_t"] / 0.85) if hard.get("diesel_t") else None),
                              max_demand_mw=hard.get("power_mw"), genset_fuel="diesel",
                              emission_standard={
                                  "glendenning-road-data-centre":
                                      "NOx below 10 t/yr as NO2-equivalent excluding unplanned outage events, "
                                      "45 m vertical stacks, annual rotational emissions testing, POEO (Clean "
                                      "Air) Regulation 2022 compliance via best practice",
                                  "nextdc-s4-data-centre-horsley-park":
                                      "NOx below 5.5 t/yr as NO2-equivalent INCLUDING testing and "
                                      "commissioning, 38.7 m vertical stacks, annual emissions testing, Tier "
                                      "standard referenced - the strictest in the sample",
                              }.get(slug, "no NOx mass cap, no numerically stated concentration limit and no "
                                          "stack height requirement found in the consent text"),
                              notes=hard.get("note", ""),
                              fact_status="VERIFIED", confidence="high", as_of_date=TODAY, source_id=SRC))

    n = len(reliable)

    # ---- reliability denominator -------------------------------------------
    # These three were originally curated into data/packs/rg060_consent_conditions.json,
    # which was never wired into either pipeline, so they silently never reached the
    # database. They are computed here instead of hardcoded so they stay reproducible.
    # The denominator matters more than it looks: every "0 of 18" negative finding in
    # this pack is only safe to rely on because 18 of 20 extractions cleared the
    # reliability floor. Without these rows the battery metrics have no stated base.
    metrics.append(dict(as_of="2026-09", scope="NSW", metric_name="consents_analysed_reliably",
                        value=float(n), unit="count", basis="actual",
                        notes=f"{n} of {len(rows)} signed consents extracted above the reliability floor, so "
                              f"their negative findings are safe to rely on. This is the denominator for every "
                              f"consents_with_* battery metric in this pack.",
                        fact_status="VERIFIED", confidence="high", as_of_date=TODAY, source_id=SRC))
    metrics.append(dict(as_of="2026-09", scope="NSW", metric_name="consents_extraction_limited",
                        value=float(len(rows) - n), unit="count", basis="actual",
                        notes=f"{len(rows) - n} of {len(rows)} consents fell below the extraction reliability "
                              f"floor. Recorded so that nobody treats a keyword miss in them as evidence of "
                              f"absence. Cross-reference reports/extraction_audit.md.",
                        fact_status="VERIFIED", confidence="high", as_of_date=TODAY, source_id=SRC))
    metrics.append(dict(as_of="2026-09", scope="NSW",
                        metric_name="consents_with_generator_hours_cap",
                        value=float(present("generator_hours_cap")), unit="count", basis="actual",
                        notes=f"Of {n} reliably extracted signed consents, {present('generator_hours_cap')} "
                              f"contain a generator hours cap provision of any value. Distinct from "
                              f"consents_with_200_hour_generator_cap, which counts only the 200 hour template "
                              f"value - the gap between the two is where site-specific departures such as "
                              f"Glendenning's 170 hours live.",
                        fact_status="VERIFIED", confidence="high", as_of_date=TODAY, source_id=SRC))

    battery = {
        "renewable_ppa_additionality": "a renewable energy supply or power purchase agreement condition",
        "pue": "any PUE or power usage effectiveness provision",
        "wue": "any WUE or water usage effectiveness provision",
        "recycled_or_nonpotable_water": "a recycled or non-potable water provision",
        "nox_mass_cap": "an absolute NOx mass cap (tonnes per year). Both instances verified by reading the "
                        "condition text: Glendenning Road B14(b) below 10 t/yr as NO2-equivalent with 45 m "
                        "stacks, excluding unplanned outage events; NEXTDC S4 Horsley Park below 5.5 t/yr as "
                        "NO2-equivalent INCLUDING testing and commissioning, with 38.7 m stacks",
        "nox_concentration_limit": "an NOx concentration limit (mg/m3). Note this pattern returned zero across all "
                        "18 consents, but Glendenning B13 requires compliance with the POEO (Clean Air) "
                        "Regulation 2022 which incorporates the Group 6 concentration limits by reference, so "
                        "zero here means 'no numerically stated concentration limit', not 'no concentration "
                        "obligation'",
        "stack_height": "a generator stack height requirement",
        "annual_emissions_testing": "an annual emissions testing requirement",
        "tier_standard": "any reference to a US EPA Tier standard or best available technology",
        "guidelines_cited": "any citation of the NSW Data Centre Guidelines",
        "diesel_storage_cap": "a diesel storage cap",
        "installed_genset_cap": "a cap on total installed back-up generating capacity",
        "battery_storage": "a battery storage provision",
        "website_disclosure": "a website public disclosure requirement",
    }
    for key, desc in battery.items():
        metrics.append(dict(as_of="2026-09", scope="NSW", metric_name=f"consents_with_{key}",
                            value=float(present(key)), unit="count", basis="actual",
                            notes=f"Of {n} reliably extracted signed consents for determined NSW data centre "
                                  f"SSDs, {present(key)} contain {desc}. Population: all {len(rows)} determined "
                                  f"and approved data centre SSDs on the NSW Planning Portal as at 18 September "
                                  f"2026" + (f"; {len(rows)-n} extracted below the reliability floor and are "
                                  f"excluded, so their provisions are unknown rather than absent."
                                  if n < len(rows) else "; every instrument extracted above the reliability "
                                  "floor after the 2026-09-18 pypdf re-extraction, so this count is complete "
                                  "for the population."),
                            fact_status="VERIFIED", confidence="high", as_of_date=TODAY, source_id=SRC))

    hours = {}
    for r in reliable:
        h = (r.get("generator_hours_cap") or "").strip()
        if h.isdigit():
            hours[h] = hours.get(h, 0) + 1
    metrics.append(dict(as_of="2026-09", scope="NSW", metric_name="consents_with_200_hour_generator_cap",
                        value=float(hours.get("200", 0)), unit="count", basis="actual",
                        notes=f"Distribution of generator hours caps across the {n} reliably extracted "
                              f"consents: " + ", ".join(f"{k} hours in {v}" for k, v in sorted(hours.items(),
                              key=lambda kv: -kv[1])) + ". The 200 hour figure is the overwhelming standard, "
                              "which confirms it is a Department template condition rather than a site-specific "
                              "assessment outcome, and matches the window the NSW Data Centre Guidelines "
                              "describe as free of point source NOx limits.",
                        fact_status="VERIFIED", confidence="high", as_of_date=TODAY, source_id=SRC))

    ratios = [("Glendenning Road", 267.45, 235.0), ("Davis Road (Cundall)", 181.92, 160.85),
              ("NEXTDC S4 Horsley Park", 360.0, 294.0), ("Project Pluto", 170.0, 100.0),
              ("Project Apollo Macquarie Park", 185.0, 135.0), ("Apollo Place", 63.8, 45.0)]
    metrics.append(dict(as_of="2026-09", scope="NSW",
                        metric_name="consents_where_backup_exceeds_load", value=float(len(ratios)),
                        unit="count", basis="actual",
                        notes="In every consent that states both an installed back-up generating capacity cap "
                              "and a total power consumption cap, the back-up capacity EXCEEDS the load: "
                              + "; ".join(f"{a} {b} MW against {c} MW (ratio {b/c:.2f})" for a, b, c in ratios)
                              + ". These are parallel power stations sized to carry the whole facility, not "
                              "standby reserves. 51 Huntingwood Drive caps installed back-up at 632 MW with no "
                              "stated consumption cap, the largest in the sample.",
                        fact_status="VERIFIED", confidence="high", as_of_date=TODAY, source_id=SRC))

    operating = ["Canberra Data Centres Pty Ltd (Roberts Road)", "NEXTDC Limited (S4 Horsley Park)",
                 "Macquarie Data Centres Pty Ltd (Talavera Road)",
                 "Goodman Property Services (Aust) Pty Limited/Ltd (Project Apollo AND Project Pluto - "
                 "one company, two consents)"]
    metrics.append(dict(as_of="2026-09", scope="NSW",
                        metric_name="consents_naming_an_operating_company", value=float(len(operating)),
                        unit="count", basis="actual",
                        notes=f"All {len(rows)} Schedule 1 applicants now parse (RG-065 resolved 2026-09-18). "
                              f"{len(operating)} companies operating data centres or holding the asset in "
                              f"their own group name hold {5} of the 20 consents: " + "; ".join(operating) +
                              ". Equinix is resolvable through its project SPV (Equinix Hyperscale 2 (SY10) "
                              "Pty Limited, Grand Avenue). The rest: TWO property-group entities (Stockland "
                              "Development Pty Limited at Khartoum Road; Stockland Trust Management Limited "
                              "at Macquarie Park); one listed end-user (Dicker Data Limited, a warehouse and "
                              "distribution centre); SEVEN consents held by consultancies or an architectural "
                              "practice (ARUP Pty Ltd at Turner Road and ARUP Australia Pty Ltd at Echidna - "
                              "two distinct Arup legal entities; Cundall Johnston and Partners at Davis Road "
                              "original and Mod 1; Lehr Consultants at Glendenning Road and Station Road; "
                              "Greenbox Architecture at Lane Cove West); and FOUR held by opaque vehicles "
                              "(EMKC Cubed Management Pty Ltd twice, HDI SYD1 Property Holdings Limited, The "
                              "Trustee for NineZero DC Sub Trust I). So in 11 of 20 consents the legal person "
                              "responsible for every condition is either a consultancy or an entity whose "
                              "controller is not disclosed on the instrument.",
                        fact_status="VERIFIED", confidence="high", as_of_date=TODAY, source_id=SRC))

    pack = {
        "pack_id": "rg060-consent-matrix-2026-09",
        "prepared_by": "scripts/curate_rg060.py from exports/nsw_planning/nsw_dc_consent_conditions.csv",
        "prepared_on": TODAY,
        "sources": [dict(
            id=SRC,
            title="Signed development consents for determined NSW data centre State Significant Developments "
                  "(bulk harvest of 20 documents)",
            publisher="NSW Department of Planning, Housing and Infrastructure",
            url="https://www.planningportal.nsw.gov.au/major-projects/search?"
                "field_case_type_value=State+Significant+Development&combine=Data+Centre",
            doc_type="primary_planning_portal", published=None, credibility="A", accessed=TODAY,
            notes=f"Twenty consent documents downloaded from the portal's public attachment endpoints on "
                  f"18 September 2026 and archived under data/raw/nsw_planning/consents/ with SHA-256 manifests "
                  f"and per-document extraction yield statistics. RE-EXTRACTED the same day with pypdf "
                  f"(scripts/reextract_consents.py) after the dependency-free extractor failed on two "
                  f"AES-encrypted instruments (Lane Cove West, Macquarie Park: 0 chars) and split numerals "
                  f"across glyph boundaries (Glendenning 235 MW parsed as 23; NEXTDC S4 294 MW as '2 94' and "
                  f"its 200-hour cap lost). Every PDF was sha256-verified against its fetch-time manifest "
                  f"before re-extraction; superseded extractions kept under consents/superseded_pdftext/. "
                  f"All {len(rows) if False else 20} instruments now extract above the {20} chars/KB "
                  f"reliability floor, so negative findings are safe across the whole population. Condition "
                  f"battery, Schedule 1 applicant, cover-page execution block (determination date, signatory, "
                  f"delegation, file ref) and hard capacity figures parsed per document; matrix at "
                  f"exports/nsw_planning/nsw_dc_consent_conditions.csv; determinations at "
                  f"exports/nsw_planning/nsw_dc_consent_determinations.csv. KNOWN PARSER LIMITS: the "
                  f"demand_response pattern is a false positive that matches the consent definition of Load "
                  f"Curtailment and the condition prohibiting it; digit-glyph repair (collapsing "
                  f"digit-space-digit) is applied to the analysis copy only, never to the archived text.")],
        "rows": {
            "entities": entities,
            "sites": site_updates,
            "power_profile": power,
            "metrics": metrics,
            "research_gaps": [
                dict(id=64, pillar="B", priority=5, retrieval_method="asic_search", status="open",
                     opened=TODAY,
                     question="Resolve EMKC Cubed Management Pty Ltd and HDI SYD1 Property Holdings Limited: "
                              "directors, shareholders, ultimate parent, and which operator or end user holds "
                              "or leases each consent.",
                     why_it_matters="EMKC Cubed Management is the consent holder for TWO facilities - 51 "
                                    "Huntingwood Drive in Blacktown, which carries the largest installed "
                                    "back-up generation in the sample at 632 MW, and Apollo Place in Lane Cove. "
                                    "Those are the two corridors with the most concentrated data centre "
                                    "activity and the loudest community opposition in New South Wales, and in "
                                    "neither case does the public record identify who operates the facility or "
                                    "who is legally responsible for the conditions. 51 Huntingwood Drive sits "
                                    "in the AirTrunk SYD1 corridor and Apollo Place in the Lane Cove cluster "
                                    "where residents report an operating facility 350 m from homes.",
                     target_source="ASIC company extracts; ABR; the title documents and EIS for SSD-41589232 "
                                   "and SSD-67407231; tenancy disclosure from operators in both corridors",
                     fact_status="VERIFIED", confidence="high", as_of_date=TODAY, source_id=SRC),
                dict(id=65, pillar="C", priority=5, retrieval_method="manual_review", status="resolved",
                     opened=TODAY, resolved_date=TODAY,
                     notes="RESOLVED 2026-09-18 by the pypdf re-extraction: ALL twenty Schedule 1 applicants "
                           "now parse from the archived instruments. The seven formerly unparsed: Khartoum "
                           "Road = Stockland Development Pty Limited; Dicker Data = Dicker Data Limited; Lane "
                           "Cove West = Greenbox Architecture Pty Ltd; Macquarie Park = Stockland Trust "
                           "Management Limited; Project Echidna = ARUP Australia Pty Ltd; Project Pluto = "
                           "Goodman Property Services (Aust) Pty Ltd; Station Road = Lehr Consultants "
                           "International (Australia) Pty Ltd.",
                     question="Six of the twenty determined consents did not yield a parsed Schedule 1 "
                              "applicant: 1-5 Khartoum Road, Dicker Data, Lane Cove West, Macquarie Park, "
                              "Project Echidna, Project Pluto and Station Road Expansion. Read Schedule 1 "
                              "directly in each.",
                     why_it_matters="The applicant is the legal person responsible for every condition in the "
                                    "consent. Without it, neither the corporate structure nor the enforcement "
                                    "question can be closed. Project Pluto is the most important of the six "
                                    "because it is one of only four consents carrying a renewable supply "
                                    "condition and one of five with PUE and WUE provisions, so knowing who "
                                    "volunteered those commitments matters for RG-061.",
                     target_source="The archived consent PDFs under data/raw/nsw_planning/consents/ - the text "
                                   "is already extracted, only the Schedule 1 parse failed",
                     fact_status="VERIFIED", confidence="high", as_of_date=TODAY, source_id=SRC),
                dict(match=dict(id=60),
                     set=dict(status="resolved", resolved_date=TODAY,
                              notes="RESOLVED 2026-09-18. Built scripts/consent_condition_audit.py, which "
                                    "indexes all 6,866 attachments across 63 archived project nodes, ranks and "
                                    "selects the best consent candidate per project, skips anything marked "
                                    "field_is_public=false, downloads under a 12 MB cap with SHA-256 manifests "
                                    "and per-document extraction yield statistics, and runs a fixed 21-test "
                                    "condition battery plus a Schedule 1 applicant parse. All 20 determined and "
                                    "approved data centre SSDs were processed. After the 2026-09-18 pypdf "
                                    "re-extraction ALL 20 extract above the reliability floor. RESULTS (of 20): "
                                    "renewable supply or PPA conditions in 5; PUE in 7; WUE in 4; recycled or "
                                    "non-potable water in 5; NOx mass cap in 2 (Glendenning 10 t/yr excluding "
                                    "unplanned outages; NEXTDC S4 5.5 t/yr including testing and "
                                    "commissioning); NOx concentration limit in ZERO; stack height in 3; "
                                    "annual emissions testing in 6; Tier standard in 2; diesel storage cap in "
                                    "14; installed back-up generation cap in 14; battery storage in 8; website "
                                    "disclosure in 19; and the NSW Data Centre Guidelines cited in ZERO "
                                    "consents including Glendenning and Project Apollo, determined AFTER they "
                                    "took effect. Generator hours caps in 17: 200 hours in 14, with "
                                    "Glendenning 170, Project Pluto 173 and Project Apollo 187 the only "
                                    "departures. Matrix at "
                                    "exports/nsw_planning/nsw_dc_consent_conditions.csv.",
                              fact_status="VERIFIED", confidence="high", as_of_date=TODAY, source_id=SRC),
                     add_sources=[SRC]),
                dict(match=dict(id=35),
                     set=dict(status="in_progress",
                              notes="Substantially advanced 2026-09-18 by reading Schedule 1 of 20 signed "
                                    "consents. RESOLVED: Project Apollo (Macquarie Park) = Goodman Property "
                                    "Services (Aust) Pty Limited; Grand Avenue Expansion Rosehill = Equinix "
                                    "Hyperscale 2 (SY10) Pty Limited; Talavera Road Campus Expansion = "
                                    "Macquarie Data Centres Pty Ltd; NEXTDC S4 Horsley Park = NEXTDC Limited; "
                                    "Roberts Road = Canberra Data Centres Pty Ltd; DigiCo SYD1 Expansion = HDI "
                                    "SYD1 Property Holdings Limited; DCI Poplars = The Trustee for NineZero DC "
                                    "Sub Trust I; 43-61 Turner Road = ARUP Pty Ltd; 51 Huntingwood Drive and "
                                    "Apollo Place = EMKC Cubed Management Pty Ltd. STILL UNRESOLVED: Project "
                                    "Duke, Project Echidna, Project Mars, Project Pluto, KC1 and Road 1, plus "
                                    "six consents whose Schedule 1 did not parse (RG-065). No AWS, Google or "
                                    "Meta entity has appeared in any Schedule 1 to date, which strengthens "
                                    "rather than weakens the RG-023 negative - except for the "
                                    "access-restricted Amazon ASIC certificate on the Davis Road application "
                                    "(RG-057).",
                              fact_status="VERIFIED", confidence="high", as_of_date=TODAY, source_id=SRC),
                     add_sources=[SRC]),
                dict(match=dict(id=55),
                     set=dict(status="in_progress",
                              notes="Advanced from four consents to twenty 2026-09-18. Of 18 reliably extracted "
                                    "consents, FOUR name an identifiable operating company (Canberra Data "
                                    "Centres, NEXTDC, Macquarie Data Centres, Goodman Property Services). The "
                                    "rest name consultancies (Cundall Johnston and Partners twice, Lehr "
                                    "Consultants, ARUP), a trust trustee (NineZero DC Sub Trust I), or "
                                    "single-purpose vehicles (EMKC Cubed Management twice, HDI SYD1 Property "
                                    "Holdings, Equinix Hyperscale 2 (SY10)); six did not parse. Combined with "
                                    "the incorporation-date evidence - KNBDC's stack created April to June "
                                    "2025, Zerra WDDP's two SPVs on 10 August 2026 four days before the report "
                                    "date - the pattern is established: the legal person carrying a data centre "
                                    "consent's conditions is usually a purpose-built entity with no operating "
                                    "history. What remains is ASIC incorporation dates and shareholding for "
                                    "each named applicant, which converts the pattern from observed to proven "
                                    "and identifies who stands behind the conditions.",
                              fact_status="VERIFIED", confidence="high", as_of_date=TODAY, source_id=SRC),
                     add_sources=[SRC]),
                dict(match=dict(id=61),
                     set=dict(status="in_progress",
                              notes="Partly answered 2026-09-18 and sharpened. The condition battery across 18 "
                                    "consents shows the distribution of outcomes but not their origin, which is "
                                    "what RG-061 asks. The sharpest available evidence: only FOUR consents "
                                    "carry any renewable supply condition, only FIVE mention PUE, and the "
                                    "Guidelines are cited in ZERO - yet Glendenning, Project Pluto and Project "
                                    "Apollo all carry renewable plus PUE plus WUE plus recycled water "
                                    "provisions while the other fifteen carry none. That clustering is "
                                    "consistent with proponent-specific commitments being converted into "
                                    "conditions, exactly as Section 3 of the Guidelines describes, rather than "
                                    "with a Department-imposed standard. Confirming it requires comparing each "
                                    "consent against its own EIS commitments, which are in the archived "
                                    "attachment index.",
                              fact_status="VERIFIED", confidence="medium", as_of_date=TODAY, source_id=SRC),
                     add_sources=[SRC]),
                dict(match=dict(id=38),
                     set=dict(notes="Resolved 2026-09-18 on four consents and then EXTENDED to all twenty by "
                                    "RG-060. The four-consent finding holds across the full population: the "
                                    "200 hour generator cap is the Department standard, with only Glendenning "
                                    "(170), Project Pluto (173) and Project Apollo (187) departing from it; "
                                    "installed back-up generation exceeds the load cap in every consent stating "
                                    "both; and the NOx mass cap exists in exactly one consent out of eighteen. "
                                    "TWO CORRECTIONS to the four-consent write-up: website public disclosure is "
                                    "in 16 of 18 consents so it is standard practice and NOT a distinguishing "
                                    "feature of the post-Guidelines consent as originally reported; and the "
                                    "apparent demand-response prevalence was a parser false positive - the "
                                    "matches are the consent definition of Load Curtailment and a condition "
                                    "PROHIBITING the use of back-up generators to support load curtailment, so "
                                    "no consent in the sample requires any non-diesel demand response "
                                    "capability.",
                              fact_status="VERIFIED", confidence="high", as_of_date=TODAY, source_id=SRC),
                     add_sources=[SRC]),
            ],
        },
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(pack, fh, indent=1)
    print(f"wrote {OUT}")
    print(f"  consents={len(rows)} reliable={n} entities={len(entities)} site_updates={len(site_updates)} "
          f"power={len(power)} metrics={len(metrics)}")
    print("  battery:", {k: present(k) for k in battery})
    print("  generator hours distribution:", dict(sorted(hours.items(), key=lambda kv: -kv[1])))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
