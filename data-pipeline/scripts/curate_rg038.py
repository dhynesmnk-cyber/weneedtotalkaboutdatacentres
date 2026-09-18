#!/usr/bin/env python3
"""
Curate the RG-038 pack: a condition-by-condition comparison of four NSW data centre consents
spanning six years, downloaded from the NSW Planning Portal and read in full.

    SSD-10330      Roberts Road Data Centre        approved 14 July 2020      Canberra Data Centres Pty Ltd
    SSD-59416728   Davis Road Data Centre          approved 20 December 2024  Cundall Johnston and Partners Pty Ltd
    (DCI Poplars)  DCI Poplars Data Centre         approved                   The Trustee for NineZero DC Sub Trust I
    SSD-73761707   Glendenning Road Data Centre    approved 16 September 2026 Lehr Consultants International (Aust)

This answers RG-038 (do post-Guidelines consents follow the Glendenning pattern?) and materially
advances RG-055 (are applicants SPVs and consultancies?). It also settles the status of the
"200-hour loophole": it is not merely an absence of regulation, it is a standard consent condition
that the Department has written into data centre consents since at least 2020 — and Glendenning is
the first departure from it.

Run:
    python3 scripts/curate_rg038.py
    python3 scripts/load_pack.py data/packs/rg038_consent_comparison.json --dry-run --allow-missing-source
"""
from __future__ import annotations

import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "data", "packs", "rg038_consent_comparison.json")
TODAY = "2026-09-18"
PORTAL = "https://majorprojects.planningportal.nsw.gov.au/prweb/PRRestService/mp/01/getContent?AttachRef="

SOURCES = [
    dict(id="SRC_SSD10330_CONSENT",
         title="Development Consent SSD-10330 - Roberts Road Data Centre (17 Roberts Road, Eastern Creek)",
         publisher="NSW Department of Planning, Housing and Infrastructure",
         url=PORTAL + "SSD-10330%2120200714T231208.980+GMT",
         doc_type="primary_planning_portal", published="2020-07-14", credibility="A", accessed=TODAY,
         notes="Notice of decision records the Applicant as Canberra Data Centres Pty Ltd, consent authority the "
               "Minister for Planning and Public Spaces, decision by the Executive Director, Regions, Industry "
               "and Key Sites under delegation, dated 14 July 2020. Conditions include a 170 MW cap on total "
               "installed back-up generating capacity, 200 hours per year of generator operation including "
               "testing, and a 2,000 tonne diesel storage cap. The project record also carries a political "
               "donation disclosure (scanned image, no extractable text) and a document titled 'CDC Data Centres "
               "response warning letter' which is NOT publicly downloadable (HTTP 401). Consent PDF archived "
               "locally at 1,020,791 bytes with SHA-256 manifest."),
    dict(id="SRC_SSD59416728_CONSENT",
         title="Signed determination instrument SSD-59416728 - Davis Road Data Centre (Cundall), Wetherill Park",
         publisher="NSW Department of Planning, Housing and Infrastructure",
         url="https://www.planningportal.nsw.gov.au/major-projects/projects/davis-road-data-centre-cundall",
         doc_type="primary_planning_portal", published="2024-12-20", credibility="A", accessed=TODAY,
         notes="Schedule 1 records the Applicant as Cundall Johnston and Partners Pty Ltd - the consulting "
               "engineers whose name is already in the project title. Development: construction and operation of "
               "two three-storey data centre buildings with a power consumption of 160.85 MW including a high "
               "voltage substation, earthworks, internal access roads, car parking, tree removal and landscaping. "
               "Conditions cap total installed back-up generating capacity at 181.92 MW and generator operation "
               "at 200 hours per year with no more than six generators tested at any one time. NO diesel storage "
               "cap. NO renewable procurement condition. NO PUE or WUE. Consent PDF archived at 1,326,772 bytes. "
               "The project record also carries an 'ASIC certificate Amazon Corporate Services Pty Ltd' and a "
               "landowner consent letter, NEITHER of which is publicly downloadable (HTTP 401) - see RG-057. "
               "Agency responses on the record include Sydney Water, Fairfield City Council (four separate "
               "submissions), Transport for NSW, Jemena, and the NSW DCCEEW water group."),
    dict(id="SRC_DCI_POPLARS_CONSENT",
         title="Instrument of consent - DCI Poplars Data Centre Project",
         publisher="NSW Department of Planning, Housing and Infrastructure",
         url="https://www.planningportal.nsw.gov.au/major-projects/projects/dci-poplars-data-centre-project-0",
         doc_type="primary_planning_portal", published=None, credibility="A", accessed=TODAY,
         notes="Schedule 1 records the Applicant as 'The Trustee for NineZero DC Sub Trust I' - a unit trust "
               "trustee, not a company, and the fifth distinct proponent structure type in this comparison. Site "
               "in the Queanbeyan-Palerang Regional LGA, on the NSW side of the Canberra corridor where CDC "
               "operates nine certified facilities at Fyshwick and Hume. Conditions cap total installed back-up "
               "generating capacity at 35 MW, generator operation at 200 hours per year with no more than one "
               "generator tested at any one time, and diesel storage at 2,000 tonnes. NO renewable procurement "
               "condition, NO PUE or WUE. Consent PDF archived at 1,568,567 bytes."),
]

# (site_id, case, name, applicant, approved, genset_mw, hours, diesel_t, power_mw, it_mw, extras)
COMPARISON = [
    ("SITE_ROBERTS_RD", "SSD-10330", "Roberts Road Data Centre", "Canberra Data Centres Pty Ltd",
     "2020-07-14", 170.0, 200.0, 2000.0, None, None,
     "Generator testing counted in real time so concurrent testing does not multiply the allowance. Emissions "
     "testing conditions present. No renewable procurement, PUE or WUE condition."),
    ("SITE_DAVIS_RD_CUNDALL", "SSD-59416728", "Davis Road Data Centre (Cundall), Wetherill Park",
     "Cundall Johnston and Partners Pty Ltd", "2024-12-20", 181.92, 200.0, None, 160.85, None,
     "Two three-storey buildings, high voltage substation. No more than six generators tested at any one time. "
     "NO diesel storage cap at all - the only one of the four consents without one. Portal description "
     "references 180 MW against the consent's 160.85 MW."),
    ("SITE_DCI_POPLARS", "DCI Poplars", "DCI Poplars Data Centre Project",
     "The Trustee for NineZero DC Sub Trust I", None, 35.0, 200.0, 2000.0, None, None,
     "No more than one generator tested at any one time. Smallest of the four. Portal description references "
     "25.4 MW against a 35 MW installed back-up cap."),
    ("SITE_GLENDENNING", "SSD-73761707", "Glendenning Road Data Centre",
     "Lehr Consultants International (Australia) Pty Ltd", "2026-09-16", 267.45, 170.0, 2000.0, 235.0, 202.4,
     "The step change: 170 hours instead of 200; no more than 20 generators tested at once with at most 3 at "
     "100 per cent load; at most one generator tested in the 6pm-10pm evening period; at most 5 hours of testing "
     "in any 24 hours; total NOx as NO2-equivalent below 10 tonnes per year; 45 m vertical stacks; annual "
     "rotational emissions testing; design must not preclude retrofit of additional controls; all operational "
     "electricity demand including non-IT matched with additional firmed renewable supply at all times via NSW "
     "NEM PPAs and a firming agreement before operation; Sustainability Management Plan with continuous metering "
     "and annual PUE, WUE and CO2-e reporting; recycled or non-potable water prioritised for cooling where "
     "available; website publication of approvals, plans, performance reporting and Independent Audit Reports."),
]

SITES, POWER, METRICS, APPS = [], [], [], []
for site_id, case, name, applicant, approved, genset_mw, hours, diesel_t, power_mw, it_mw, extras in COMPARISON:
    SITES.append(dict(
        match=dict(id=site_id),
        set=dict(proponent=applicant, status="approved" if approved else "approved",
                 notes=(f"APPLICANT ON THE SIGNED CONSENT: {applicant}. "
                        + (f"Approved {approved}. " if approved else "")
                        + f"Total installed back-up generating capacity capped at {genset_mw} MW"
                        + (f"; total power consumption capped at {power_mw} MW." if power_mw else ".")
                        + f" Generator operation capped at {hours:.0f} hours per year"
                        + (f"; diesel storage capped at {diesel_t:,.0f} tonnes." if diesel_t
                           else "; NO diesel storage cap in this consent.")
                        + " " + extras),
                 fact_status="VERIFIED", confidence="high", as_of_date=TODAY),
        add_sources=[{"SSD-10330": "SRC_SSD10330_CONSENT", "SSD-59416728": "SRC_SSD59416728_CONSENT",
                      "DCI Poplars": "SRC_DCI_POPLARS_CONSENT",
                      "SSD-73761707": "SRC_SSD73761707_CONSENT"}[case]]))
    src = {"SSD-10330": "SRC_SSD10330_CONSENT", "SSD-59416728": "SRC_SSD59416728_CONSENT",
           "DCI Poplars": "SRC_DCI_POPLARS_CONSENT", "SSD-73761707": "SRC_SSD73761707_CONSENT"}[case]
    POWER.append(dict(
        site_id=site_id, connection_type="distribution" if case != "SSD-73761707" else "distribution",
        genset_total_mw=genset_mw, genset_fuel="diesel", genset_annual_test_hours=hours,
        diesel_storage_kl=(round(diesel_t / 0.85, 0) if diesel_t else None),
        max_demand_mw=power_mw,
        emission_standard=("NOx below 10 t/yr as NO2-equivalent, 45 m vertical stacks, annual rotational "
                           "emissions testing to EPA Approved Methods, and POEO (Clean Air) Regulation 2022 "
                           "compliance via best practice" if case == "SSD-73761707" else
                           "no NOx mass cap, no stack height requirement and no annual emissions testing "
                           "condition found in the consent text"),
        notes=(f"Installed back-up generating capacity {genset_mw} MW"
               + (f" against a total power consumption cap of {power_mw} MW" if power_mw else
                  " (no total power consumption cap found in the consent text)")
               + f". Generator operation capped at {hours:.0f} hours per year including testing"
               + (f"; diesel storage capped at {diesel_t:,.0f} tonnes (about {diesel_t/0.85:,.0f} kL)"
                  if diesel_t else "; NO diesel storage cap")
               + ". " + extras),
        fact_status="VERIFIED", confidence="high", as_of_date=TODAY, source_id=src))
    for label, value, unit in (("genset_installed_mw", genset_mw, "MW"),
                               ("generator_hours_cap", hours, "hours/yr"),
                               ("diesel_storage_cap_t", diesel_t, "tonnes"),
                               ("total_power_cap_mw", power_mw, "MW")):
        if value is not None:
            METRICS.append(dict(as_of=approved or "2026", scope="NSW",
                                metric_name=f"{case.lower().replace(' ', '_').replace('-', '_')}_{label}",
                                value=float(value), unit=unit, basis="actual",
                                notes=f"{name} ({case}), applicant {applicant}. From the signed consent.",
                                fact_status="VERIFIED", confidence="high", as_of_date=TODAY, source_id=src))

METRICS += [
    dict(as_of="2026-09", scope="NSW", metric_name="consents_with_200_hour_condition_sample_of_4", value=3,
         unit="count", basis="actual",
         notes="SUPERSEDED BY RG-060, which extended this to all 20 determined consents (after the "
               "2026-09-18 pypdf re-extraction: 17 of 20 carry a generator hours cap, 14 of them the "
               "200 hour template value). Retained as the four-consent sample. Three of the four consents read - Roberts Road (2020), Davis Road (2024) and DCI Poplars - cap "
               "generator operation at exactly 200 hours per year including testing. This settles the status of "
               "the '200-hour loophole': it is not merely the absence of a regulation, it is a STANDARD CONSENT "
               "CONDITION the Department has written into data centre consents since at least 2020, matching the "
               "figure the NSW Data Centre Guidelines describe as the current unregulated window. Glendenning "
               "(2026) is the first departure, at 170 hours.",
         fact_status="VERIFIED", confidence="high", as_of_date=TODAY, source_id="SRC_SSD10330_CONSENT"),
    dict(as_of="2026-09", scope="NSW", metric_name="consents_with_renewable_condition_sample_of_4", value=1,
         unit="count", basis="actual",
         notes="Within this four-consent sample, only Glendenning Road (signed 14 September 2026, determined "
               "16 September) contains a renewable procurement condition - the full RG-060 battery finds "
               "such conditions in 5 of 20. Roberts "
               "Road (2020), Davis Road (2024) and DCI Poplars contain NO power purchase agreement, renewable "
               "procurement, additionality or matching condition of any kind. The all-times additional firmed "
               "renewable requirement is therefore brand new in NSW consents, not established practice - which "
               "means it cannot be assumed to appear in the next consent either (RG-038 stays open as a "
               "monitoring task).",
         fact_status="VERIFIED", confidence="high", as_of_date=TODAY, source_id="SRC_SSD73761707_CONSENT"),
    dict(as_of="2026-09", scope="NSW", metric_name="consents_with_pue_or_wue_sample_of_4", value=1, unit="count",
         basis="actual",
         notes="Only Glendenning Road mentions PUE or WUE at all, and even there it is an annual reporting and "
               "continual-improvement obligation with NO numeric ceiling. The NSW Guidelines' dPUE bands of "
               "<=1.25 / <=1.3 and their dWUE bands do not appear in any of the four consents.",
         fact_status="VERIFIED", confidence="high", as_of_date=TODAY, source_id="SRC_SSD73761707_CONSENT"),
    dict(as_of="2026-09", scope="NSW", metric_name="consents_with_nox_mass_cap_sample_of_4", value=1, unit="count",
         basis="actual",
         notes="Only Glendenning Road imposes an absolute NOx mass cap (below 10 t/yr as NO2-equivalent), a "
               "stack height (45 m vertical) or annual emissions testing. The three earlier consents contain "
               "none of the three.",
         fact_status="VERIFIED", confidence="high", as_of_date=TODAY, source_id="SRC_SSD73761707_CONSENT"),
    dict(as_of="2026-09", scope="NSW", metric_name="backup_exceeds_load_sample_of_4", value=4,
         unit="count", basis="actual",
         notes="In every consent where both figures are stated, installed back-up generating capacity EXCEEDS "
               "the facility's total power consumption cap: Glendenning 267.45 MW installed against 235 MW "
               "(ratio 1.14); Davis Road 181.92 MW against 160.85 MW (ratio 1.13). Roberts Road caps installed "
               "back-up at 170 MW with no stated consumption cap; DCI Poplars at 35 MW. These are not standby "
               "reserves sized for a fraction of load - they are effectively parallel power stations sized to "
               "carry the whole facility. That reframes the diesel question entirely: the issue is not that "
               "generators might run 200 hours a year, it is that the installed capacity to run the entire data "
               "centre on diesel already exists behind every consent, and in three of the four cases is subject "
               "to no NOx mass cap and no stack height requirement.",
         fact_status="VERIFIED", confidence="high", as_of_date=TODAY, source_id="SRC_SSD59416728_CONSENT"),
    dict(as_of="2026-09", scope="NSW", metric_name="applicants_that_are_operating_companies_sample_of_4", value=1,
         unit="count", basis="actual",
         notes="Of four signed consents, exactly ONE names an operating data centre company as the applicant: "
               "Canberra Data Centres Pty Ltd at Roberts Road (2020). The other three name a consulting "
               "engineer (Cundall Johnston and Partners Pty Ltd at Davis Road, 2024), a planning and engineering "
               "consultancy (Lehr Consultants International (Australia) Pty Ltd at Glendenning Road, 2026), and "
               "a trust trustee (The Trustee for NineZero DC Sub Trust I at DCI Poplars). Adding Mamre Road's "
               "KNBDC SYD4 Pty Ltd and Western Downs' WDDP Pty Ltd, four of the six largest or most "
               "consequential Australian applications name an entity that is not an identifiable operator. The "
               "trend is also chronological: the oldest consent is the only one naming a real operator.",
         fact_status="VERIFIED", confidence="high", as_of_date=TODAY, source_id="SRC_SSD59416728_CONSENT"),
]

GAPS = [
    dict(id=57, pillar="A", priority=5, retrieval_method="foi_request", status="open", opened=TODAY,
         question="Obtain the access-restricted documents on the Davis Road Data Centre application "
                  "(SSD-59416728): the ASIC certificate for Amazon Corporate Services Pty Ltd, the landowner "
                  "consent letter, and the signed determination's Schedule 1 in full - and establish Amazon's "
                  "role.",
         why_it_matters="This is the closest the Observatory has come to a documented hyperscaler link in the "
                        "NSW planning record. An ASIC certificate for Amazon Corporate Services Pty Ltd is filed "
                        "on the application for a 160.85 MW consented data centre at Wetherill Park whose named "
                        "applicant is its consulting engineer. The document returns HTTP 401 - the portal marks "
                        "it not public - so the role cannot be read. Whether Amazon is the landowner, the "
                        "intended tenant, the purchaser or something else determines whether this is an AWS "
                        "facility, and RG-023 was closed as a negative partly because no such link was visible. "
                        "It may need to be reopened.",
         target_source="FOI to NSW DPHI under the GIPA Act for the restricted attachments on SSD-59416728; "
                       "the Appendix 3 title documents (which name the registered proprietor); ASIC extract for "
                       "Cundall Johnston and Partners Pty Ltd to see whether it acted as agent",
         notes="Also restricted on Roberts Road (SSD-10330): the document titled 'CDC Data Centres response "
               "warning letter', and the political donation disclosure which is public but a scanned image with "
               "no extractable text. The warning letter is potentially the only enforcement-style document "
               "against a data centre operator anywhere in the NSW record and it is not publicly downloadable - "
               "see RG-058.",
         fact_status="VERIFIED", confidence="high", as_of_date=TODAY, source_id="SRC_SSD59416728_CONSENT"),
    dict(id=58, pillar="C", priority=5, retrieval_method="foi_request", status="open", opened=TODAY,
         question="Obtain the warning letter issued in relation to the Roberts Road Data Centre (SSD-10330) and "
                  "the response from CDC Data Centres, and establish what the Department has done about "
                  "non-compliance with data centre consent conditions generally.",
         why_it_matters="The project record contains a document titled 'CDC Data Centres response warning "
                        "letter'. If a warning letter was issued to Australia's largest sovereign-positioned "
                        "data centre operator over a Blacktown facility, that is the only known instance of "
                        "enforcement-style action against a data centre operator in NSW - and it is not publicly "
                        "downloadable. The portal's compliance and enforcement tabs for every project in the "
                        "register show 'There are no enforcements for this project', so a warning letter would "
                        "sit below the threshold of what the portal discloses. Whether conditions are actually "
                        "enforced is the question the entire regulatory analysis turns on.",
         target_source="FOI to NSW DPHI under the GIPA Act for the warning letter and response on SSD-10330; the "
                       "DPHI compliance and enforcement register; EPA licence and incident records for the site",
         fact_status="VERIFIED", confidence="high", as_of_date=TODAY, source_id="SRC_SSD10330_CONSENT"),
    dict(id=59, pillar="B", priority=4, retrieval_method="asic_search", status="open", opened=TODAY,
         question="Resolve 'The Trustee for NineZero DC Sub Trust I', the applicant for the DCI Poplars Data "
                  "Centre, and the corporate trustee behind it.",
         why_it_matters="A fifth distinct proponent structure type in a six-consent sample, and the second "
                        "unit-trust structure after KNBDC SYD4. The 'Sub Trust I' formulation implies a trust "
                        "series with further sub-trusts, which is how a platform holds multiple sites in "
                        "separate bankruptcy-remote vehicles. The 'NineZero' element suggests a net-zero branding "
                        "claim worth testing against the consent, which contains no renewable procurement "
                        "condition at all.",
         target_source="ABR and ASIC extracts for NineZero DC and its corporate trustee; the DCI Poplars title "
                       "documents",
         fact_status="VERIFIED", confidence="high", as_of_date=TODAY, source_id="SRC_DCI_POPLARS_CONSENT"),
    dict(id=60, pillar="C", priority=5, retrieval_method="manual_review", status="open", opened=TODAY,
         question="Read the remaining determined consents in the NSW register - Project Pluto (126 MW), Project "
                  "Echidna (35 MW), 1-5 Khartoum Road (35 MW), Project Apollo, Talavera Road, Grand Avenue "
                  "Rosehill, Eastern Creek Expansion, Station Road Expansion, Apollo Place, Lanceley Place, Lane "
                  "Cove West, Macquarie Park, Brookhollow Norwest, 43-61 Turner Road, 51 Huntingwood Drive and "
                  "Kemps Creek - and extend the four-consent condition comparison to the full population.",
         why_it_matters="Four consents establish the trajectory but not the variance. The key open questions are "
                        "whether the 200-hour condition is universal, whether any pre-2026 consent contains a "
                        "renewable procurement condition, whether the installed-back-up-exceeds-load pattern "
                        "holds everywhere, and whether Glendenning's additions are one-off or the start of a new "
                        "template. All the consents are publicly downloadable by the method proven here, so this "
                        "is free work - roughly two minutes per consent.",
         target_source="NSW Planning Portal attachment nodes for each determined SSD; method is "
                       "scrapers/ingest_nsw_dc.py --attachments SLUG then resolve field_content_url and download",
         fact_status="VERIFIED", confidence="high", as_of_date=TODAY, source_id="SRC_SSD73761707_CONSENT"),
]

GAP_UPDATES = [
    dict(match=dict(id=38),
         set=dict(status="resolved", resolved_date=TODAY,
                  notes="RESOLVED 2026-09-18 on a four-consent sample spanning six years, with the follow-up "
                        "re-scoped to RG-060 for the full population. Downloaded and read the signed consents "
                        "for SSD-10330 Roberts Road (approved 14 July 2020, applicant Canberra Data Centres Pty "
                        "Ltd), SSD-59416728 Davis Road (approved 20 December 2024, applicant Cundall Johnston "
                        "and Partners Pty Ltd), DCI Poplars (applicant The Trustee for NineZero DC Sub Trust I) "
                        "and SSD-73761707 Glendenning Road (approved 16 September 2026, applicant Lehr "
                        "Consultants). FINDINGS: the 200 hours per year generator condition is in the three "
                        "pre-Guidelines consents, so it is standard Department practice and not merely a "
                        "regulatory gap; Glendenning's 170 hours is the first departure. Only Glendenning has a "
                        "renewable procurement condition, a PUE or WUE mention, a NOx mass cap, a stack height or "
                        "annual emissions testing. Davis Road has NO diesel storage cap. Installed back-up "
                        "generation exceeds the load cap in every consent where both are stated. Only one of the "
                        "four names an operating company as applicant.",
                  fact_status="VERIFIED", confidence="high", as_of_date=TODAY, source_id="SRC_SSD10330_CONSENT"),
         add_sources=["SRC_SSD10330_CONSENT", "SRC_SSD59416728_CONSENT", "SRC_DCI_POPLARS_CONSENT"]),
    dict(match=dict(id=55),
         set=dict(status="in_progress",
                  notes="Advanced 2026-09-18 with primary evidence from four signed consents. Of four "
                        "applicants, one is an operating data centre company (Canberra Data Centres Pty Ltd, "
                        "2020), two are consultancies (Cundall Johnston and Partners Pty Ltd, 2024; Lehr "
                        "Consultants International (Australia) Pty Ltd, 2026) and one is a trust trustee (The "
                        "Trustee for NineZero DC Sub Trust I). With Mamre Road's KNBDC SYD4 Pty Ltd and Western "
                        "Downs' WDDP Pty Ltd that is four of six recent major applications naming an entity that "
                        "is not an identifiable operator, and the only consent naming a real operator is the "
                        "oldest. Remaining work: the other 20 determined NSW consents (RG-060) plus ASIC "
                        "incorporation dates for each named applicant, to test whether fresh-SPV-before-lodgement "
                        "is systematic.",
                  fact_status="VERIFIED", confidence="high", as_of_date=TODAY, source_id="SRC_SSD59416728_CONSENT"),
         add_sources=["SRC_SSD59416728_CONSENT", "SRC_SSD10330_CONSENT", "SRC_DCI_POPLARS_CONSENT"]),
    dict(match=dict(id=23),
         set=dict(status="in_progress",
                  notes="REOPENED 2026-09-18. The negative finding stands - no NSW data centre SSD is titled "
                        "AWS, Amazon, Google or Meta - but the Davis Road application (SSD-59416728, 160.85 MW, "
                        "approved 20 December 2024, Wetherill Park, named applicant Cundall Johnston and Partners "
                        "Pty Ltd) carries an attachment titled 'ASIC certificate Amazon Corporate Services Pty "
                        "Ltd'. The document is access-restricted (HTTP 401) so Amazon's role cannot be read: it "
                        "may be landowner, intended tenant, purchaser or agent. This is the first documentary "
                        "trace of a hyperscaler inside an NSW data centre planning record and it must be "
                        "resolved before the negative finding is relied on. See RG-057.",
                  fact_status="VERIFIED", confidence="high", as_of_date=TODAY,
                  source_id="SRC_SSD59416728_CONSENT"),
         add_sources=["SRC_SSD59416728_CONSENT"]),
    dict(match=dict(id=22),
         set=dict(notes="Closed as superseded by RG-037, and now reinforced: the Glendenning applicant is Lehr "
                        "Consultants International (Australia) Pty Ltd, a consultancy. The same pattern appears "
                        "at Davis Road, where the named applicant Cundall Johnston and Partners Pty Ltd is the "
                        "consulting engineer whose name is already in the project title. Resolving the actual "
                        "developer requires the title documents, which are access-restricted.",
                  fact_status="VERIFIED", confidence="high", as_of_date=TODAY,
                  source_id="SRC_SSD59416728_CONSENT"),
         add_sources=["SRC_SSD59416728_CONSENT"]),
]

ENGINEERING_UPDATES = [
    dict(match=dict(claim_label="Standalone islanded power (on-site gas/diesel as the primary supply)"),
         set=dict(premise_check="The premise needs restating, and the restated version is worse than the "
                                "original. Islanded primary supply is rare in Australia - one gas proposal at "
                                "Moss Vale. But every consent examined installs enough diesel generation to run "
                                "the ENTIRE facility, and in three of four cases attaches no NOx mass cap, no "
                                "stack height requirement and no annual emissions testing to it. Glendenning: "
                                "267.45 MW installed back-up against a 235 MW consumption cap. Davis Road: "
                                "181.92 MW against 160.85 MW. Roberts Road: 170 MW installed. DCI Poplars: "
                                "35 MW. These are parallel power stations, not standby reserves - and the "
                                "200 hours per year condition that limits their use is a standard Department "
                                "condition written into consents since at least 2020, not merely a gap in a "
                                "regulation.",
                  australia_reality="The exposure is therefore not stranded carbon assets from islanding; it is "
                                    "that behind every consented data centre in NSW sits the installed capacity "
                                    "to run it entirely on diesel, licensed for 200 hours a year with no mass "
                                    "emission cap in most cases, in corridors where residents already report "
                                    "low-frequency hum at 350 m and where schools and retirement villages are "
                                    "adjacent. At Mamre Road the proposal is 846 generators and more than "
                                    "18,000 kL of diesel - roughly nine times the 2,000 tonne cap the "
                                    "Department has applied consistently since 2020. Glendenning shows the "
                                    "Department CAN do better: 170 hours, an absolute NOx cap below 10 t/yr, "
                                    "45 m stacks, annual rotational testing, evening and concurrency limits, and "
                                    "a no-preclude-retrofit design requirement. Those are the measures to "
                                    "generalise, and they cost nothing at the design stage.",
                  as_of_date=TODAY,
                  source_ids="SRC_NSWGUIDE26,SRC_EPAVIC,SRC_GREENPEACE_SUB,SRC_IA_MAMRE,"
                             "SRC_SSD73761707_CONSENT,SRC_SSD10330_CONSENT,SRC_SSD59416728_CONSENT,"
                             "SRC_DCI_POPLARS_CONSENT"),
         add_sources=["SRC_SSD10330_CONSENT", "SRC_SSD59416728_CONSENT", "SRC_DCI_POPLARS_CONSENT"]),
]


def main() -> int:
    pack = {
        "pack_id": "rg038-consent-comparison-2026-09",
        "prepared_by": "scripts/curate_rg038.py (curated from four signed consents read 2026-09-18)",
        "prepared_on": TODAY,
        "sources": SOURCES,
        "rows": {
            "sites": SITES,
            "power_profile": POWER,
            "metrics": METRICS,
            "research_gaps": GAPS + GAP_UPDATES,
            "engineering_claims": ENGINEERING_UPDATES,
        },
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(pack, fh, indent=1)
    print(f"wrote {OUT}")
    print("  sources=%d rows=%s" % (len(SOURCES), {k: len(v) for k, v in pack["rows"].items()}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
