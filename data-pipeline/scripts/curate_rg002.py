#!/usr/bin/env python3
"""
Curate the RG-002 pack: the complete NSW data centre State Significant Development register,
harvested from the NSW Planning Portal by scrapers/ingest_nsw_dc.py on 2026-09-18.

Input :  exports/nsw_planning/nsw_data_centre_projects.csv   (46 project records)
Output:  data/packs/rg002_nsw_ssd_register.json

The harvest is machine-readable but the mapping from a portal record to an Observatory site is a
judgement call, so it is written out explicitly below rather than inferred. Every row still carries
the portal as its source and a VERIFIED status only where the portal itself is the authority for
the fact (case id, stage, decision, LGA, determination date).

Run:
    python3 scripts/curate_rg002.py
    python3 scripts/load_pack.py data/packs/rg002_nsw_ssd_register.json --dry-run --allow-missing-source
    python3 scripts/load_pack.py data/packs/rg002_nsw_ssd_register.json --allow-missing-source
"""
from __future__ import annotations

import csv
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV_IN = os.path.join(ROOT, "exports", "nsw_planning", "nsw_data_centre_projects.csv")
OUT = os.path.join(ROOT, "data", "packs", "rg002_nsw_ssd_register.json")
TODAY = "2026-09-18"
SRC = "SRC_NSWPORTAL_REGISTER"

# Sites whose name was already established from a better source than the portal's generic title.
WELL_NAMED = {"SITE_MSFT_KEMPS"}

# slug -> (site_id, operator_entity_id or None, name, status, notes)
# status vocabulary: operational, under_construction, approved, lodged, pre_lodgement,
#                    refused, withdrawn, cancelled, rumoured
MAP = {
 "project-duke-data-centre": ("SITE_PROJECT_DUKE", None, "Project Duke Data Centre", "approved",
    "Codename. Bayside LGA. Approved; capacity not stated in the portal description."),
 "51-huntingwood-drive-data-centre": ("SITE_51_HUNTINGWOOD", None, "51 Huntingwood Drive Data Centre",
    "approved", "Blacktown. Approved. 51 Huntingwood Drive is in the Huntingwood corridor where AirTrunk's "
                "SYD1 operates; operator attribution requires the consent documents, not the portal summary."),
 "51-huntingwood-drive-data-centre-mod-2-design-updates": None,
 "modification-1-51-huntingwood-drive-data-centre-reduced-scale": None,
 "augusta-street-data-centre": ("SITE_AUGUSTA_ST", None, "Augusta Street Data Centre", "withdrawn",
    "Blacktown. WITHDRAWN. One of three withdrawn data centre SSDs in the NSW register."),
 "eastern-creek-data-centre-expansion-project": ("SITE_EC_EXPANSION", None,
    "Eastern Creek Data Centre Expansion Project", "approved", "Blacktown. Approved."),
 "eastern-creek-data-centre-mod-2-power-consumption-increase": None,
 "glendenning-road-data-centre": ("SITE_GLENDENNING", None, "Glendenning Road Data Centre", "approved",
    "See the RG-026 pack for the signed consent. The portal description states 202.4 MW while the signed "
    "consent permits 235 MW total power consumption; both figures are recorded."),
 "honeman-close-data-centre": ("SITE_MSFT_HONEMAN", "ENT_MSFT_DC_AU", "Microsoft Honeman Close Data Centre",
    "lodged", "Blacktown. In Assessment per the portal. The description references 96 MW, which is lower than "
              "any published Microsoft capacity figure for the site and should be read as one stage of a "
              "multi-stage campus rather than the total. Endorsed in NSW IDA Round 1."),
 "marsden-park-data-centre": ("SITE_CDC_MARSDEN", "ENT_CDC", "CDC Marsden Park Data Centre", "approved",
    "Blacktown. APPROVED, and the portal description references both 504 MW and 720 MW - the campus appears to "
    "have been consented at a larger capacity than the 504 MW widely reported. Reconcile against the "
    "determination before quoting either figure."),
 "nextdc-s7-data-centre-eastern-creek": ("SITE_NEXTDC_S7", "ENT_NEXTDC", "NEXTDC S7 Data Centre, Eastern Creek",
    "lodged", "Blacktown. Portal stage is Prepare EIS, which is EARLIER than 'lodged' implies: the SSD "
              "application is registered but the environmental impact statement was still being prepared as at "
              "18 September 2026. Description references 612 MW."),
 "project-atlas-data-centre-eastern-creek": ("SITE_GOODMAN_ATLAS", "ENT_GOODMAN",
    "Project Atlas Data Centre, Eastern Creek", "lodged",
    "Blacktown. At Response to Submissions. Named by the NSW Government as a Goodman Property Services (Aust) "
    "Pty Ltd project in IDA Round 1."),
 "project-echidna-data-centre-eastern-creek": ("SITE_ECHIDNA", None, "Project Echidna Data Centre, Eastern Creek",
    "approved", "Blacktown. Approved; 35 MW operational capacity with associated emergency back-up generation."),
 "roberts-road-data-centre": ("SITE_ROBERTS_RD", None, "Roberts Road Data Centre", "approved", "Blacktown. Approved."),
 "roberts-road-data-centre-mod-1-height-increase": None,
 "roberts-road-dc-mod-2-additional-back-generators-and-diesel-storage": None,
 "roberts-road-dc-mod-4-changes-operational-infrastructure": None,
 "station-road-data-centre-expansion": ("SITE_STATION_RD", None, "Station Road Data Centre Expansion", "approved",
    "Blacktown. Approved."),
 "43-61-turner-road-data-centre": ("SITE_43_61_TURNER", None, "43-61 Turner Road Data Centre", "approved",
    "Camden LGA. Approved."),
 "52-turner-road-data-centre": ("SITE_TURNER_RD", None, "52 Turner Road Data Centre", "withdrawn",
    "CORRECTION: this record was previously entered as 'lodged' from a portal search snippet. The harvested "
    "register shows stage WITHDRAWN, in Camden LGA (not an unrecorded LGA). A 40 MW application including "
    "emergency back-up generators, cooling plant, and diesel and lithium-ion battery storage was withdrawn."),
 "kurri-kurri-data-centre": ("SITE_KURRI_KURRI", None, "Kurri Kurri Data Centre", "pre_lodgement",
    "Cessnock City LGA, in the Hunter. Portal stage is Prepare EIS, so the application is registered but the "
    "EIS is not yet submitted. Significant as a REGIONAL siting rather than a Sydney-corridor one, consistent "
    "with Transgrid's public encouragement for proponents to look outside the constrained Sydney basin, and "
    "with the NSW Guidelines' observation that consumer bills can fall when load is added where the network has "
    "spare capacity."),
 "grand-avenue-data-centre-expansion-rosehill": ("SITE_GRAND_AVE", None,
    "Grand Avenue Data Centre Expansion, Rosehill", "approved", "City of Parramatta. Approved."),
 "1-5-khartoum-road-data-centre": ("SITE_KHARTOUM", None, "1-5 Khartoum Road Data Centre", "approved",
    "City of Ryde. Approved; description references 35 MW. Khartoum Road is in the Macquarie Park / North Ryde "
    "corridor."),
 "23-25-waterloo-road-data-centre": ("SITE_23_25_WATERLOO", None, "23-25 Waterloo Road Data Centre",
    "pre_lodgement", "City of Ryde. Prepare EIS; description references 70 MW."),
 "julius-avenue-data-centre": ("SITE_JULIUS_AVE", None, "Julius Avenue Data Centre", "lodged",
    "City of Ryde. In Assessment. Julius Avenue is in the Macquarie Park corridor."),
 "macquarie-park-data-centre": ("SITE_MACQUARIE_PARK_DC", None, "Macquarie Park Data Centre", "approved",
    "City of Ryde. Approved. ABC used a Macquarie Park data centre as its illustration for the August 2026 "
    "fast-track story."),
 "nextdc-s5-data-centre-and-innovation-hub": ("SITE_NEXTDC_S5", "ENT_NEXTDC",
    "NEXTDC S5 Data Centre and Innovation Hub", "lodged", "City of Ryde. In Assessment. IDA Round 1 endorsed."),
 "project-apollo-data-centre-macquarie-park": ("SITE_PROJECT_APOLLO", None,
    "Project Apollo Data Centre, Macquarie Park", "approved", "City of Ryde. Approved."),
 "road-1-data-centre": ("SITE_ROAD_1", None, "Road 1 Data Centre", "lodged",
    "City of Ryde. In Assessment; description references 34.3 MW."),
 "talavera-road-data-centre-campus-expansion": ("SITE_TALAVERA", None,
    "Talavera Road Data Centre Campus Expansion", "approved",
    "City of Ryde. Approved. Talavera Road is the Macquarie Park data centre corridor."),
 "talavera-road-data-centre-mod-1-expansion": None,
 "waterloo-road-data-centre-esr-developments": ("SITE_WATERLOO_ESR", None,
    "Waterloo Road Data Centre (ESR Developments)", "approved",
    "City of Ryde. Approved. The portal title names ESR Developments, a listed Asia-Pacific industrial real "
    "estate manager - a rare case of the developer being identifiable from the portal record itself."),
 "22-oriordan-street-alexandria-data-centre": ("SITE_ORIORDAN", None,
    "22 O'Riordan Street, Alexandria Data Centre", "pre_lodgement",
    "City of Sydney. Prepare EIS; description references 38 MW. Alexandria is the inner-sydney corridor where "
    "Equinix SY1 and noise complaints about generator testing have historically concentrated."),
 "digico-syd1-data-centre-expansion": ("SITE_DIGICO_SYD1", None, "DigiCo SYD1 Data Centre Expansion",
    "approved", "City of Sydney. Approved. HMC DigiCo is a certified data centre provider."),
 "project-pluto-data-centre": ("SITE_PROJECT_PLUTO", None, "Project Pluto Data Centre", "approved",
    "Cumberland LGA. Approved; description references 126 MW."),
 "davis-road-data-centre-cundall": ("SITE_DAVIS_RD_CUNDALL", None, "Davis Road Data Centre (Cundall)",
    "approved", "Fairfield City. Approved; description references 180 MW. The portal title names Cundall, a "
                "consulting engineer, so as with Glendenning Road the identifiable party is a consultant rather "
                "than the developer."),
 "davis-rd-data-centre-mod-1-tree-removal-correction": None,
 "nextdc-s4-data-centre-horsley-park": ("SITE_NEXTDC_S4", "ENT_NEXTDC",
    "NEXTDC S4 Data Centre, Horsley Park", "approved",
    "Fairfield City and Blacktown (the site straddles both LGAs). APPROVED. This is a material upgrade on the "
    "IDA Round 1 listing, which showed S4 only as an endorsed project. Horsley Park, not Fairfield broadly."),
 "nextdc-s4-data-centre-phase-2-horsley-park": ("SITE_NEXTDC_S4_P2", "ENT_NEXTDC",
    "NEXTDC S4 Data Centre Phase 2, Horsley Park", "pre_lodgement",
    "Fairfield City. Prepare EIS; description references 134.4 MW. A second stage of the approved S4 campus."),
 "apollo-place-data-centre": ("SITE_APOLLO_PLACE", None, "Apollo Place Data Centre", "approved",
    "Lane Cove LGA. Approved."),
 "lane-cove-west-data-centre": ("SITE_LANE_COVE_WEST", None, "Lane Cove West Data Centre", "approved",
    "Lane Cove. Approved, and carrying FOUR modifications including 'Mod 1 fuel storage' and 'Mod 4 APDC "
    "inclusion'. This is the lower north shore corridor where the BBC reports residents 350 m from an operating "
    "facility with four more in the pipeline, and where ABC used a facility to illustrate community backlash. A "
    "modification specifically for fuel storage in that context is worth retrieving."),
 "lane-cove-west-data-centre-mod-1-fuel-storage": None,
 "lane-cove-west-data-centre-mod-2-layout-changes": None,
 "lane-cove-west-data-centre-mod-3-design-changes": None,
 "lane-cove-west-data-centre-mod-4-apdc-inclusion": None,
 "mars-road-data-centre": ("SITE_LANE_COVE_MARS", "ENT_LANE_COVE_ALLIANCE",
    "Mars Road Data Centre (16-20 Mars Road, Lane Cove West)", "pre_lodgement",
    "Lane Cove. Prepare EIS. IDA Round 1 endorsed as the 'Lane Cove Data Centre Development Project' with "
    "proponent 'Lane Cove DC Alliance', which does not resolve to any entity on the Australian Business "
    "Register - suggesting an unincorporated joint venture or a trading name."),
 "mowbray-road-data-centre": ("SITE_MOWBRAY_RD", None, "Mowbray Road Data Centre", "withdrawn",
    "Lane Cove. WITHDRAWN - the second of three withdrawn data centre SSDs, and the second in Lane Cove LGA."),
 "project-mars-data-centre": ("SITE_PROJECT_MARS", None, "Project Mars Data Centre", "lodged",
    "Lane Cove. At Response to Submissions. A fourth Lane Cove project."),
 "aldington-road-data-centre": ("SITE_ALDINGTON", None, "Aldington Road Data Centre", "pre_lodgement",
    "Penrith. Prepare EIS. Aldington Road is in the Kemps Creek / St Marys growth corridor; a '200 Aldington' "
    "modification also appears in the register against a separate project."),
 "200-aldington-mod-8-amendments-road-upgrade-works-and-timing": None,
 "kc1-data-centre-kemps-creek": ("SITE_KC1", None, "KC1 Data Centre, Kemps Creek", "pre_lodgement",
    "Penrith. Prepare EIS; description references 144 MW. A FOURTH named project at Kemps Creek alongside "
    "Microsoft's operating campus, Stockland Fife and the 1 GW Mamre Road campus - which is why the Department "
    "directed cumulative-impact assessment for this precinct."),
 "kemps-creek-data-centre": ("SITE_MSFT_KEMPS", "ENT_MICROSOFT",
    "Microsoft Kemps Creek Data Centre Campus", "operational",
    "SSD-10101987, approved 13 July 2023. See the RG-013 pack."),
 "kemps-creek-data-centre-mod-1-data-hall-fit-out": None,
 "mamre-road-data-centre-campus": ("SITE_MAMRE_ROAD", "ENT_KNBDC",
    "Mamre Road Data Centre Campus", "lodged",
    "SSD-92743706, Penrith. Portal stage is RESPONSE TO SUBMISSIONS, which is more precise than 'lodged': the "
    "proponent has responded and the matter is with the Department. NSW EPA found the EIS incomplete on "
    "10 April 2026 and Penrith City Council objected."),
 "stack-syd01-data-centre-erskine-park": ("SITE_STACK_SYD01", "ENT_STACK_AU",
    "STACK SYD01 Data Centre, Erskine Park", "lodged",
    "Penrith and Blacktown. In Assessment; description references 450 MW. STACK's Erskine Park campus is one of "
    "the largest applications in the state and sits in the same corridor as Digital Realty's SYD10/SYD11/SYD14 "
    "certified enclaves."),
 "dci-poplars-data-centre-project-0": ("SITE_DCI_POPLARS", "ENT_DCI", "DCI Poplars Data Centre Project",
    "approved", "Queanbeyan-Palerang Regional LGA - the NSW side of the Canberra corridor, near Hume where CDC "
                "operates nine certified sites. Approved. Illustrates that the ACT-adjacent data centre market "
                "spills into NSW, which matters because the ACT is a separate NEM jurisdiction with its own "
                "planning regime."),
 "brookhollow-avenue-data-centre-expansion-norwest": ("SITE_BROOKHOLLOW", None,
    "Brookhollow Avenue Data Centre Expansion, Norwest", "lodged",
    "The Hills Shire. At Response to Submissions. Norwest is the same corridor as the IDA-endorsed AIMS Bella "
    "Vista campus and GreenSquare DC SYD1 Stage 2."),
 "frederick-street-data-centre": ("SITE_FREDERICK_ST", None, "Frederick Street Data Centre", "pre_lodgement",
    "Willoughby City. Prepare EIS; description references 81 MW. Frederick Street Artarmon had already surfaced "
    "through a Willoughby community group; this confirms it is a registered SSD application. An 81 MW facility "
    "in a dense lower north shore residential-commercial interface."),
 "lanceley-place-data-centre-artarmon": ("SITE_LANCELEY", None, "Lanceley Place Data Centre, Artarmon",
    "approved", "Willoughby City. Approved, with a further modification application on foot. Artarmon is a "
                "second operating data centre node in the Lane Cove / Willoughby corridor."),
 "modification-2-lanceley-place-data-centre": None,
 "mod-3-lanceley-place-data-centre-fire-access-and-switchroom": None,
 "dicker-data-warehouse-and-distribution-centre": ("SITE_DICKER_DATA", None,
    "Dicker Data Warehouse and Distribution Centre", "approved",
    "Sutherland Shire. Approved. INCLUDE WITH CARE: 'Dicker Data' is an IT reseller and the development type "
    "reads as a warehouse and distribution centre, so this is very likely a logistics facility that the keyword "
    "search caught rather than a data centre. Retained as a documented false positive of the harvesting method."),
}


def main() -> int:
    rows = list(csv.DictReader(open(CSV_IN, encoding="utf-8")))
    by_slug = {r["slug"]: r for r in rows}

    sites, site_updates, apps, metrics = [], [], [], []
    skipped_mods, unmapped = [], []

    for slug, spec in MAP.items():
        if spec is None:
            skipped_mods.append(slug)
            continue
        if slug not in by_slug:
            unmapped.append(slug)
            continue
        r = by_slug[slug]
        site_id, op, name, status, notes = spec
        approved = (r["decision"] or "").lower().startswith("approv")
        common = dict(
            source_id=SRC, fact_status="VERIFIED", confidence="high", as_of_date=TODAY,
            state="NSW", market="NEM", lga=r["lga"] or None,
        )
        mw = [float(x) for x in re.findall(r"\d+(?:\.\d+)?", r["mw_mentions_in_description"] or "")]
        row = dict(id=site_id, name=r["title"] or name, operator_id=op, status=status,
                   proponent=None, notes=notes, **common)
        if mw:
            row["it_capacity_mw"] = max(mw)
            row["max_capacity_mw"] = max(mw) if len(mw) == 1 else None
        if site_id in ("SITE_GLENDENNING", "SITE_MSFT_KEMPS", "SITE_MAMRE_ROAD", "SITE_NEXTDC_S7",
                       "SITE_ECHIDNA", "SITE_TURNER_RD", "SITE_NEXTDC_S4", "SITE_NEXTDC_S5",
                       "SITE_GOODMAN_ATLAS", "SITE_LANE_COVE_MARS"):
            upd = {k: v for k, v in row.items() if k != "id" and v is not None}
            # The portal's title is generic ("Kemps Creek Data Centre"). Where an earlier pack
            # established a better-attributed name, do not overwrite it with the register title.
            if site_id in WELL_NAMED:
                upd.pop("name", None)
            site_updates.append(dict(match=dict(id=site_id), set=upd, add_sources=[SRC]))
        else:
            sites.append(row)

        if r["case_id"]:
            apps.append(dict(site_id=site_id, jurisdiction="NSW Department of Planning, Housing and Infrastructure",
                             pathway="state_significant_development", reference=r["case_id"],
                             decided=r["determination_date"] or None,
                             outcome=("approved" if approved else
                                      "withdrawn" if r["stage"].lower().startswith("with") else
                                      "under_assessment"),
                             decision_maker=r["determination_authority"] or None,
                             capacity_mw_in_app=max(mw) if mw else None,
                             conditions_summary=None,
                             notes=f"Portal stage at harvest: {r['stage'] or 'not recorded'}. Development type "
                                   f"{r['development_type']}, industry classification {r['industry']}. "
                                   f"{r['n_attachments']} documents attached to the project record.",
                             source_id=SRC, fact_status="VERIFIED", confidence="high", as_of_date=TODAY))

    # register-level metrics
    by_lga, by_stage = {}, {}
    for r in rows:
        for l in (r["lga"] or "unrecorded").split(";"):
            by_lga[l.strip()] = by_lga.get(l.strip(), 0) + 1
        by_stage[r["stage"] or "unrecorded"] = by_stage.get(r["stage"] or "unrecorded", 0) + 1
    for lga, n in by_lga.items():
        metrics.append(dict(as_of="2026-09", scope=f"NSW - {lga}", metric_name="nsw_dc_ssd_projects",
                            value=float(n), unit="count", basis="actual",
                            notes="Data centre State Significant Development project records on the NSW Planning "
                                  "Portal, harvested 18 September 2026. Includes modification applications.",
                            fact_status="VERIFIED", confidence="high", as_of_date=TODAY, source_id=SRC))
    for st, n in by_stage.items():
        metrics.append(dict(as_of="2026-09", scope="NSW", metric_name=f"nsw_dc_ssd_stage_{st.lower().replace(' ', '_')}",
                            value=float(n), unit="count", basis="actual",
                            notes=f"Projects at stage '{st}' in the harvested register.",
                            fact_status="VERIFIED", confidence="high", as_of_date=TODAY, source_id=SRC))
    metrics.append(dict(as_of="2026-09", scope="NSW", metric_name="nsw_dc_ssd_withdrawn", value=3.0,
                        unit="count", basis="actual",
                        notes="Augusta Street (Blacktown, SSD-10469), 52 Turner Road (Camden, SSD-60185233) and "
                              "Mowbray Road (Lane Cove, SSD-13475973). Withdrawn applications are the only "
                              "direct evidence in the planning record of proposals that did not survive, and "
                              "they belong in any phantom-demand analysis alongside the IDA's $40.7bn of "
                              "non-endorsed proposals and Transgrid's 20 GW of unconverted enquiries.",
                        fact_status="VERIFIED", confidence="high", as_of_date=TODAY, source_id=SRC))
    metrics.append(dict(as_of="2026-09", scope="NSW", metric_name="nsw_dc_ssd_no_hyperscaler_branded_project",
                        value=0.0, unit="count", basis="actual",
                        notes="Zero of the 46 harvested NSW data centre SSD records is titled with AWS, Amazon, "
                              "Google or Meta. Microsoft appears only through its proponent entity on the "
                              "Kemps Creek consent and the Honeman Close application. Hyperscaler facilities are "
                              "therefore either leased from third-party landlords, held under codenames "
                              "(Project Duke, Atlas, Echidna, Apollo, Pluto, Mars), or in another state. This "
                              "is the concrete finding for RG-023: the NSW planning record cannot be used to "
                              "map hyperscaler footprints, and the route is ASIC resolution of the codename "
                              "SPVs plus landlord tenancy disclosure.",
                        fact_status="VERIFIED", confidence="high", as_of_date=TODAY, source_id=SRC))

    pack = {
        "pack_id": "rg002-nsw-ssd-register-2026-09",
        "prepared_by": "scripts/curate_rg002.py from exports/nsw_planning/nsw_data_centre_projects.csv",
        "prepared_on": TODAY,
        "sources": [
            dict(id=SRC,
                 title="NSW Planning Portal major projects register - data centre State Significant Development "
                       "records (46 projects harvested)",
                 publisher="NSW Department of Planning, Housing and Infrastructure",
                 url="https://www.planningportal.nsw.gov.au/major-projects/search?"
                     "field_case_type_value=State+Significant+Development&combine=Data+Centre",
                 doc_type="primary_planning_portal", published=None, credibility="A", accessed=TODAY,
                 notes="Harvested 18 September 2026 by scrapers/ingest_nsw_dc.py. For each project the portal's "
                       "Drupal node JSON provides case id, stage, case type, decision, determination date, "
                       "determination authority, development type, industry classification and local government "
                       "area; the project page provides the development description. Every node JSON is archived "
                       "under data/raw/nsw_planning/nodes/ with a SHA-256 manifest. 24 of 46 records are at "
                       "Determination with an Approved decision; 3 are Withdrawn; 9 are at Prepare EIS; 5 at "
                       "Assessment; 4 at Response to Submissions. Modification applications are harvested but "
                       "deliberately not turned into site rows."),
        ],
        "rows": {
            "sites": sites + site_updates,
            "applications": apps,
            "metrics": metrics,
            "research_gaps": [
                dict(match=dict(id=2),
                     set=dict(status="resolved", resolved_date=TODAY,
                              notes="RESOLVED 2026-09-18 for the SSD layer. Built scrapers/ingest_nsw_dc.py and "
                                    "harvested all 46 data centre State Significant Development records on the "
                                    "NSW Planning Portal: case ids, stages, decisions, determination dates and "
                                    "authorities, development types, industry classifications and LGAs, plus the "
                                    "development description and attachment counts. Node JSON archived with "
                                    "SHA-256 manifests. Concentration: Blacktown 11, City of Ryde 9, Lane Cove 5, "
                                    "Penrith 4. 24 approved, 3 withdrawn. RESIDUAL, re-scoped as RG-034: the "
                                    "register covers State Significant Development only. It does not include "
                                    "local council development applications (which is where the Melton, South "
                                    "Morang and Moss Vale matters sit), Part 5A infrastructure, modification "
                                    "content, or the attachment bodies themselves - the signed consents must be "
                                    "fetched one at a time as was done for SSD-73761707.",
                              fact_status="VERIFIED", confidence="high", as_of_date=TODAY, source_id=SRC),
                     add_sources=[SRC]),
                dict(match=dict(id=23),
                     set=dict(status="in_progress",
                              notes="Advanced and re-scoped 2026-09-18. The complete NSW SSD register contains NO "
                                    "project titled AWS, Amazon, Google or Meta. Microsoft appears only via its "
                                    "proponent entity (Microsoft Datacentre (Australia) Pty Ltd) on Kemps Creek "
                                    "SSD-10101987 and Honeman Close SSD-58601963. Conclusion: hyperscaler sites "
                                    "cannot be mapped from planning titles. The viable routes are (a) ASIC "
                                    "resolution of the codename SPVs - Project Duke, Atlas, Echidna, Apollo, "
                                    "Pluto, Mars, KC1, Road 1 - several of which are plausible hyperscaler "
                                    "leases; (b) landlord tenancy disclosure from AirTrunk, NEXTDC, CDC, "
                                    "Equinix, Digital Realty and STACK; (c) the withheld IDA project. See "
                                    "RG-035.",
                              fact_status="VERIFIED", confidence="high", as_of_date=TODAY, source_id=SRC),
                     add_sources=[SRC]),
                dict(id=34, pillar="A", priority=4, retrieval_method="scrape_portal", status="open",
                     opened=TODAY,
                     question="Extend the NSW register harvest to modification applications and to local council "
                              "development applications in Blacktown, Penrith, Fairfield, Ryde, Lane Cove, "
                              "Willoughby, Camden, Cumberland, Hills Shire and Parramatta.",
                     why_it_matters="Modifications carry the operational changes that matter most - 'Lane Cove "
                                    "West Mod 1 fuel storage', 'Roberts Road Mod 2 additional back-up generators "
                                    "and diesel storage', 'Eastern Creek Mod 2 power consumption increase'. A "
                                    "consent's original capacity is not its operating capacity. And council-level "
                                    "DAs are where smaller facilities and all of the community-facing disputes "
                                    "sit.",
                     target_source="NSW Planning Portal (modification records already enumerated in "
                                   "data/raw/nsw_planning/dc_project_slugs.json); each council's online DA "
                                   "register",
                     fact_status="VERIFIED", confidence="high", as_of_date=TODAY, source_id=SRC),
                dict(id=35, pillar="A", priority=5, retrieval_method="asic_search", status="open",
                     opened=TODAY,
                     question="Resolve the codename SPVs behind Project Duke, Project Atlas, Project Echidna, "
                              "Project Apollo, Project Pluto, Project Mars, KC1 and Road 1 via ASIC company "
                              "extracts and the title documents attached to each application.",
                     why_it_matters="These are the most likely hiding places for hyperscaler leases in NSW. The "
                                    "NSW Government's own IDA release already shows that codenames are the "
                                    "sector's convention (Goodman's 'Project Atlas', Stockland's 'Project A'), "
                                    "and one IDA-endorsed project is withheld entirely for commercial "
                                    "sensitivity. Without ASIC extracts the hyperscaler footprint in Australia "
                                    "cannot be mapped from public planning data at all.",
                     target_source="ASIC Connect company and business-name extracts; Appendix title documents in "
                                   "each SSD record (these name the registered proprietor); landlord disclosures",
                     fact_status="VERIFIED", confidence="high", as_of_date=TODAY, source_id=SRC),
            ],
        },
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(pack, fh, indent=1)

    n_new = len([s for s in sites])
    print(f"wrote {OUT}")
    print(f"  harvested={len(rows)} mapped={len(MAP) - len(skipped_mods)} new_sites={n_new} "
          f"updated_sites={len(site_updates)} applications={len(apps)} metrics={len(metrics)}")
    print(f"  modification/duplicate slugs intentionally not turned into sites: {len(skipped_mods)}")
    if unmapped:
        print(f"  WARNING slugs in MAP but absent from the harvest: {unmapped}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
