#!/usr/bin/env python3
"""
Site figures from each NSW SSD project's own planning document (batch S2).

scrapers/fetch_ssd_documents.py archived one document per data centre SSD project under
data/raw/nsw_planning/documents/: the Department's assessment report where the project is
determined, otherwise the applicant's EIS, scoping report or request for SEARs. This script
carries the figures those documents state onto the site record.

Every value is an entry in EXTRACTIONS, read by a person from the archived text, with the page and
the passage it comes from. The script checks each one before writing anything:
  * the quote appears, verbatim up to whitespace, on the page cited;
  * the number in the value appears in the quote (after the quote's own unit: "$1.29 billion"
    reads as 1,290,000,000, "60,943 m2" as 60,943), so a slip in transcription is caught.

Figures are those of the development the application seeks, as the document states them. For an
expansion, a site total that includes existing buildings is not taken, and the development's share
is never computed from one. Site area is the application's site, as stated.

Which column a figure belongs in is decided by what the document says it is, never by its size:
  it_capacity_mw     the document calls it IT load, critical IT load or IT capacity
  total_capacity_mw  total power consumption, power consumption, or maximum power or site demand
  max_capacity_mw    the ultimate, full build-out or maximum of a campus built in stages
  first_phase_mw     the first stage's capacity, when the document states one (the quote says
                     whether it is IT or total)
  capital_cost_aud   the capital investment value (CIV), the planning system's own cost figure,
                     or the estimated development cost an application form states; never a range
  gfa_sqm, campus_area_ha, construction_jobs, operational_jobs   as the document states them
  proponent          the applicant the document names, unless it is a consultancy acting for one
A figure the document does not define ("a capacity of 35 MW") is left out: live_capacity_mw is
never filled, and no capacity column is filled from another.

Cooling, water and grid connection are stated in many of these documents, but the loader does not
carry those fields to the site yet (a decision outside this batch), so they are not extracted here.

Uses load_pack.py's "fill": no existing value is overwritten, and a differing one is reported.
Each row cites its document, with the passage quoted in source_refs.

Refuses to write if a document fails its SHA-256 check, a quote is not on its page, a value is not
in its quote, a field is not one listed above, or a case maps to no site.

Outputs:
  * data/packs/ssd_documents.json

Run:
    python3 scripts/curate_ssd_documents.py
    python3 scripts/load_pack.py data/packs/ssd_documents.json --allow-missing-source
"""
from __future__ import annotations

import glob
import hashlib
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from curate_site_coordinates import ssd_to_site  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS = os.path.join(ROOT, "data", "raw", "nsw_planning", "documents")
OUT_PACK = os.path.join(ROOT, "data", "packs", "ssd_documents.json")
TODAY = "2026-10-10"

FIELDS = {"it_capacity_mw", "total_capacity_mw", "max_capacity_mw", "first_phase_mw",
          "capital_cost_aud", "gfa_sqm", "campus_area_ha", "construction_jobs",
          "operational_jobs", "proponent"}
KIND_PUBLISHER = {
    "assessment": "NSW Department of Planning, Housing and Infrastructure",
    "eis": "Prepared for the applicant; published on the NSW Planning Portal",
    "scoping": "Prepared for the applicant; published on the NSW Planning Portal",
    "sears_request": "Prepared for the applicant; published on the NSW Planning Portal",
}

# Unit conversions an entry may declare as a sixth element: the quote states the figure in another
# unit, and the value is that figure converted. Arithmetic only.
CONVERSIONS = {"sqm_to_ha": 1 / 10_000, "gw_to_mw": 1_000}

# (SSD case, field, value, page, quote[, conversion]). Read by a person from the archived text.
EXTRACTIONS: list[tuple] = [
    # Kemps Creek Data Centre (Microsoft), assessment report
    ("SSD-10101987", "capital_cost_aud", 1298942449, 17, "Capital investment value $1,298,942,449.00"),
    ("SSD-10101987", "construction_jobs", 300, 17,
     "Employment 300 full-time equivalent construction jobs and 79 operational jobs"),
    ("SSD-10101987", "operational_jobs", 79, 17,
     "Employment 300 full-time equivalent construction jobs and 79 operational jobs"),
    ("SSD-10101987", "gfa_sqm", 60943, 16, "The development has a gross floor area (GFA) of 60,943 m2"),
    ("SSD-10101987", "campus_area_ha", 14.43, 16, "The site is approximately 14.43 hectares (ha) in area"),
    # Roberts Road Data Centre (CDC), assessment report
    ("SSD-10330", "capital_cost_aud", 291465000, 17, "Capital investment value (CIV) $291,465,000"),
    ("SSD-10330", "construction_jobs", 448, 17, "Employment 448 construction jobs and 10 operational jobs"),
    ("SSD-10330", "operational_jobs", 10, 17, "Employment 448 construction jobs and 10 operational jobs"),
    ("SSD-10330", "gfa_sqm", 42222, 15, "The expansion would have a total GFA of approximately 42,222 m2"),
    ("SSD-10330", "campus_area_ha", 14.52, 15, "Site area 14.52 ha"),
    # Macquarie Park Data Centre (Stockland), assessment report
    ("SSD-10467", "capital_cost_aud", 263600000, 5,
     "has a capital investment value (CIV) of approximately $263.6 millio n"),
    ("SSD-10467", "construction_jobs", 400, 5,
     "would generate up to 400 construction jobs and 50 full-time equivalent operational jobs"),
    ("SSD-10467", "operational_jobs", 50, 5,
     "would generate up to 400 construction jobs and 50 full-time equivalent operational jobs"),
    ("SSD-10467", "gfa_sqm", 12069, 17, "Gross floor area (GFA) 12,069 m2"),
    ("SSD-10467", "campus_area_ha", 1.296, 17, "Site area 1.296 ha"),
    # Lane Cove data centre, 3-4 Apollo Place and 87-91 Mars Road: the request for SEARs form
    ("SSD-108835458", "capital_cost_aud", 1000000000, 1,
     "Estimated Development Cost (excl GST) AUD1,000,000,000.00"),
    ("SSD-108835458", "operational_jobs", 50, 1, "Indicative Operation Jobs 50 Indicative Construction Jobs 1,000"),
    ("SSD-108835458", "construction_jobs", 1000, 1, "Indicative Operation Jobs 50 Indicative Construction Jobs 1,000"),
    ("SSD-108835458", "gfa_sqm", 13801, 1, "Gross Floor Area (GFA) sqm 13,801"),
    ("SSD-108835458", "campus_area_ha", 1.5044, 2, "Site Area sqm 15,044", "sqm_to_ha"),
    # NEXTDC S4 Phase 2, Horsley Park: scoping report
    ("SSD-108864209", "construction_jobs", 1100, 18,
     "approximately 1,100 full- time equivalent c onstruction jobs and approximately 217 full- time operational jobs"),
    ("SSD-108864209", "operational_jobs", 217, 18,
     "approximately 1,100 full- time equivalent c onstruction jobs and approximately 217 full- time operational jobs"),
    ("SSD-108864209", "campus_area_ha", 21.33, 6, "The site has a total area of 21.33 hectares."),
    # Aldington Road, Kemps Creek: scoping report; Table 1 compares the earlier proposal (first
    # column) with the amended one (second), and only the amended figures are taken.
    ("SSD-112059740", "campus_area_ha", 30, 8,
     "Description 90 Aldington Road Data Centre Amended Proposal Site Area Approximately 20ha Approximately 30ha"),
    ("SSD-112059740", "it_capacity_mw", 360, 8,
     "Description 90 Aldington Road Data Centre Amended Proposal Site Area Approximately 20ha Approximately 30ha "
     "Site Developable Area Approximately 10ha Approximately 14ha Height 27 metres 36 metres MegaWatt IT Load (Max) "
     "245 MW 360 MW MegaWatt IT Load (Min) 226 MW 342 MW"),
    # NEXTDC S7, Eastern Creek: scoping report. Its total power is left out: the report states a
    # "total power consumption of 612 megawatts" (p40) and an "expected total site load of
    # approximately 700MW" (p35).
    ("SSD-113934740", "capital_cost_aud", 7154563995, 27, "Expected Capital Investment Value $7,154,563,995 .00"),
    ("SSD-113934740", "construction_jobs", 2000, 27, "Construction: Approximately 2,000 FTE construction roles"),
    ("SSD-113934740", "operational_jobs", 425, 28, "Operation: Approximately 425 FTE roles"),
    ("SSD-113934740", "gfa_sqm", 174411, 26, "The proposal provides an approximate total GFA of 174,411 m²"),
    ("SSD-113934740", "campus_area_ha", 38.5734, 8, "has a total area of approximately 385,734m2", "sqm_to_ha"),
    # Kurri Kurri Data Centre, Loxford: scoping report
    ("SSD-128819490", "construction_jobs", 500, 33,
     "Employment Generation 500 construction jobs and 250 full-time operational jobs"),
    ("SSD-128819490", "operational_jobs", 250, 33,
     "Employment Generation 500 construction jobs and 250 full-time operational jobs"),
    ("SSD-128819490", "gfa_sqm", 44220, 29, "Total GFA – 44,220 m2"),
    ("SSD-128819490", "campus_area_ha", 20.91, 8, "with a total area of 20.91 hectares"),
    ("SSD-128819490", "total_capacity_mw", 540, 9, "A total power consumption of 540 MW"),
    # KC1, Kemps Creek: scoping report
    ("SSD-133677993", "total_capacity_mw", 144, 7, "anticipated to have a total power consumption of approximately 144 MW"),
    ("SSD-133677993", "campus_area_ha", 88.4, 8, "has an approximate combined area of 88.4ha across four (4) lots"),
    # 12 Frederick Street: scoping report. Site area left out: 1.82 ha on p5, 1.859 ha on p11.
    ("SSD-139545990", "gfa_sqm", 16634, 18, "Gross Floor Area (GFA) 16,634 sqm"),
    ("SSD-139545990", "total_capacity_mw", 81, 4, "a data centre that has a maximum power demand of 81 megawatts (MW)"),
    # Project Atlas (Goodman), 10 Roberts Road, Eastern Creek: EIS
    ("SSD-101067971", "capital_cost_aud", 5536389811, 15, "Estimated Development Cost $5,536,389,811 AUD"),
    ("SSD-101067971", "construction_jobs", 2323, 15,
     "Employment Generation Construction 2,323 full-time equivalent jobs Operational 162 full-time equivalent jobs"),
    ("SSD-101067971", "operational_jobs", 162, 15,
     "Employment Generation Construction 2,323 full-time equivalent jobs Operational 162 full-time equivalent jobs"),
    ("SSD-101067971", "total_capacity_mw", 348, 13,
     "a Data Centre that has a total power consumption of more than 15 megawatts (348MW)"),
    ("SSD-101067971", "gfa_sqm", 99130, 14, "Total GFA: 99,130m2"),
    ("SSD-101067971", "campus_area_ha", 16.8574, 14, "Total site area = 168,574m2", "sqm_to_ha"),
    # Eastern Creek Data Centre Expansion (DCI): assessment report; the development's own figures
    ("SSD-21342738", "capital_cost_aud", 330311108, 14, "Capital investment value (CIV) $330,311,108"),
    ("SSD-21342738", "construction_jobs", 150, 14, "Employment 150 construction jobs and 76 additional operational jobs"),
    ("SSD-21342738", "operational_jobs", 76, 14, "Employment 150 construction jobs and 76 additional operational jobs"),
    ("SSD-21342738", "gfa_sqm", 13210, 13, "Gross floor area (GFA) 13,210 m2"),
    ("SSD-21342738", "total_capacity_mw", 32, 13, "Power consumption 32 megawatts (MW)"),
    ("SSD-21342738", "campus_area_ha", 4.094, 13, "Site area 40,940 m2", "sqm_to_ha"),
    # Talavera Road Data Centre Campus Expansion: assessment report; the development's own figures
    # (Table 2 on p24 also gives the site's existing 28 MW and combined 66 MW, which are not taken)
    ("SSD-24299707", "capital_cost_aud", 332032973, 22, "Capital investment value (CIV) $332,032,973"),
    ("SSD-24299707", "construction_jobs", 610, 22, "Employment 610 construction jobs and 20 additional operational jobs"),
    ("SSD-24299707", "operational_jobs", 20, 22, "Employment 610 construction jobs and 20 additional operational jobs"),
    ("SSD-24299707", "gfa_sqm", 16142, 21, "Gross floor area (GFA) 16,142 m2"),
    ("SSD-24299707", "total_capacity_mw", 38, 21, "Power consumption 38 megawatts (MW)"),
    ("SSD-24299707", "campus_area_ha", 2.0094, 21, "Site area 20,094 m2", "sqm_to_ha"),
    # Station Road Data Centre Expansion, Seven Hills: assessment report; the development's own figures
    ("SSD-33781208", "capital_cost_aud", 167632802, 15, "Capital investment value (CIV) $167,632,802"),
    ("SSD-33781208", "construction_jobs", 250, 15, "Employment 250 construction jobs and 32 additional operational jobs"),
    ("SSD-33781208", "operational_jobs", 32, 15, "Employment 250 construction jobs and 32 additional operational jobs"),
    ("SSD-33781208", "gfa_sqm", 8076, 14, "Gross floor area (GFA) 8,076 m2"),
    ("SSD-33781208", "total_capacity_mw", 19.2, 14, "Power consumption 19.2 MW"),
    ("SSD-33781208", "campus_area_ha", 2.57, 14, "Site area 2.57 ha"),
    # 51 Huntingwood Drive Data Centre: assessment report
    ("SSD-41589232", "capital_cost_aud", 1074990484, 16, "Capital investment value $1,074,990,484.00"),
    ("SSD-41589232", "construction_jobs", 1333, 16,
     "Employment 1,333 full-time equivalent construction jobs and 276 operational jobs"),
    ("SSD-41589232", "operational_jobs", 276, 16,
     "Employment 1,333 full-time equivalent construction jobs and 276 operational jobs"),
    ("SSD-41589232", "gfa_sqm", 122546, 15, "Gross floor area (GFA) 122,546 m2"),
    ("SSD-41589232", "total_capacity_mw", 400, 15, "Power Consumption 400 MW"),
    ("SSD-41589232", "campus_area_ha", 9, 15, "Site area 9 hectares"),
    # Project Echidna, Eastern Creek: assessment report
    ("SSD-47320208", "capital_cost_aud", 380267448, 17, "Capital Investment Value $380,267,448"),
    ("SSD-47320208", "construction_jobs", 100, 17,
     "Employment 100 full-time equivalent construction jobs and 50 full-time operational jobs"),
    ("SSD-47320208", "operational_jobs", 50, 17,
     "Employment 100 full-time equivalent construction jobs and 50 full-time operational jobs"),
    ("SSD-47320208", "gfa_sqm", 9225, 16, "Gross Floor Area (GFA) 9,225 m2"),
    ("SSD-47320208", "total_capacity_mw", 35.2, 16, "Power Consumption 35.2 MW"),
    # Grand Avenue Data Centre Expansion, Rosehill: assessment report. Its 31.2 MW is an
    # "operational capacity", which the report does not define, so it is not taken.
    ("SSD-53338465", "capital_cost_aud", 293360197, 14, "Capital Investment Value $ 293,360,197"),
    ("SSD-53338465", "construction_jobs", 250, 14,
     "Employment 250 full-time equivalent construction jobs and 36 operational jobs"),
    ("SSD-53338465", "operational_jobs", 36, 14,
     "Employment 250 full-time equivalent construction jobs and 36 operational jobs"),
    ("SSD-53338465", "gfa_sqm", 14856, 13, "Gross Floor Area (GFA) 14,856 m2"),
    ("SSD-53338465", "campus_area_ha", 1.9, 13, "Site area 1.9 ha"),
    # Davis Road Data Centre (Cundall), Wetherill Park: assessment report. Its 160 MW is an
    # undefined "operational capacity" and is not taken.
    ("SSD-59416728", "capital_cost_aud", 1597338256, 15, "Estimated development cost $1,597,338,256"),
    ("SSD-59416728", "construction_jobs", 556, 15,
     "Employment 556 full-time equivalent construction jobs and 73 operational jobs"),
    ("SSD-59416728", "operational_jobs", 73, 15,
     "Employment 556 full-time equivalent construction jobs and 73 operational jobs"),
    ("SSD-59416728", "gfa_sqm", 39568, 14, "Total GFA of 39,568 m2"),
    ("SSD-59416728", "campus_area_ha", 10.54, 14, "Site area 10.54 ha"),
    # Honeman Close Data Centre (Microsoft), Huntingwood: EIS
    ("SSD-58601963", "capital_cost_aud", 1263226278.52, 12,
     "The proposal has a capital investment value (CIV) of $1,263,226,278.52 exc. GST"),
    ("SSD-58601963", "total_capacity_mw", 96, 38, "Total power consumption capacity up to 96 MW"),
    ("SSD-58601963", "construction_jobs", 250, 39,
     "Employment Generation Up to 250 construction jobs, and 74 operational full-time employees."),
    ("SSD-58601963", "operational_jobs", 74, 39,
     "Employment Generation Up to 250 construction jobs, and 74 operational full-time employees."),
    # NEXTDC S5 Data Centre and Innovation Hub, Macquarie Park: EIS. Its IT load is stated only per
    # data hall (p63), and no total is computed from them.
    ("SSD-63168959", "total_capacity_mw", 90, 49, "Power Consumption 90 megawatts"),
    ("SSD-63168959", "gfa_sqm", 46935, 13, "total gross floor area (GFA) of 46,935m2"),
    # 1-5 Khartoum Road Data Centre: assessment report, which splits the site's power into total
    # and IT load
    ("SSD-63235720", "total_capacity_mw", 76.4, 12, "Maximum power capacity 76.4 MW (51.4 MW IT Load)"),
    ("SSD-63235720", "it_capacity_mw", 51.4, 12, "Maximum power capacity 76.4 MW (51.4 MW IT Load)"),
    ("SSD-63235720", "gfa_sqm", 19434, 12, "Gross floor area (GFA) 19,434 m 2"),
    ("SSD-63235720", "capital_cost_aud", 718259656, 13, "Estimated development cost $718,259 ,656"),
    ("SSD-63235720", "construction_jobs", 250, 13,
     "Employment 250 full - time equivalent construction jobs and 50 operational jobs"),
    ("SSD-63235720", "operational_jobs", 50, 13,
     "Employment 250 full - time equivalent construction jobs and 50 operational jobs"),
    # NEXTDC S4 Data Centre, Horsley Park: assessment report; Table 10 compares the original
    # development (first column) with the amended one (second), and only the amended is taken.
    ("SSD-63741210", "capital_cost_aud", 3177382221, 17, "Estimated development cost $3,177,382,221"),
    ("SSD-63741210", "construction_jobs", 1111, 17,
     "Employment 411 full-time operational jobs and 1,111 construction jobs"),
    ("SSD-63741210", "operational_jobs", 411, 17,
     "Employment 411 full-time operational jobs and 1,111 construction jobs"),
    ("SSD-63741210", "total_capacity_mw", 294, 82,
     "Aspect Original Development in EIS Amended Development Site Area 8.206 ha 8.206 ha (site) plus land within "
     "HV route (1.1617 ha) and land within the TransGrid Sydney West Substation site (approximately 43.09 ha) "
     "Land Use Activity Data centre with ancillary office and café Data centre with ancillary office and café "
     "Power Consumption 232 megawatts 294 megawatts"),
    ("SSD-63741210", "campus_area_ha", 8.206, 82,
     "Aspect Original Development in EIS Amended Development Site Area 8.206 ha 8.206 ha (site)"),
    # DCI Poplars Data Centre Project, Jerrabomberra: assessment report. IT capacity is stated per
    # stage; the first stage's is taken as first-phase capacity, and no total is computed.
    ("SSD-64287712", "total_capacity_mw", 25.4, 4, "The facility would have a total power consumption of 25.4 megawatts (MW)"),
    ("SSD-64287712", "first_phase_mw", 8, 12, "Stage 1 – Two data halls with 8 MW IT capacity"),
    ("SSD-64287712", "campus_area_ha", 4.0532, 12, "Site area 40,532 m2", "sqm_to_ha"),
    ("SSD-64287712", "gfa_sqm", 5826, 12, "Gross floor area (GFA) 5,826 m2"),
    ("SSD-64287712", "construction_jobs", 125, 13, "Employment 125 construction jobs and 24 operational jobs"),
    ("SSD-64287712", "operational_jobs", 24, 13, "Employment 125 construction jobs and 24 operational jobs"),
    ("SSD-64287712", "capital_cost_aud", 278781168, 13, "Estimated development cost $278,781,168"),
    # Apollo Place Data Centre, Lane Cove West: assessment report
    ("SSD-67407231", "total_capacity_mw", 45, 13, "Total power consumption of 45 megawatts (MW), with IT load of 41 MW"),
    ("SSD-67407231", "it_capacity_mw", 41, 13, "Total power consumption of 45 megawatts (MW), with IT load of 41 MW"),
    ("SSD-67407231", "gfa_sqm", 9328, 13, "Gross floor area (GFA) 9,328 m 2"),
    ("SSD-67407231", "campus_area_ha", 4.4842, 13, "Site area Consolidated site – 44,842 m 2", "sqm_to_ha"),
    ("SSD-67407231", "construction_jobs", 380, 14,
     "Employment 380 full-time equivalent construction jobs and 44 operational jobs"),
    ("SSD-67407231", "operational_jobs", 44, 14,
     "Employment 380 full-time equivalent construction jobs and 44 operational jobs"),
    ("SSD-67407231", "capital_cost_aud", 288398501, 14, "Estimated Development Cost $288,398,501"),
    # 43-61 Turner Road Data Centre, Gregory Hills: assessment report
    ("SSD-68013714", "total_capacity_mw", 61.7, 11, "Maximum power consumption 61.7 MW (53 MW IT Load)"),
    ("SSD-68013714", "it_capacity_mw", 53, 11, "Maximum power consumption 61.7 MW (53 MW IT Load)"),
    ("SSD-68013714", "campus_area_ha", 9.74, 11, "Site area 9.74 ha"),
    ("SSD-68013714", "gfa_sqm", 14941, 11, "Total GFA of 14,941 m2"),
    ("SSD-68013714", "construction_jobs", 100, 12,
     "Employment 100 full-time equivalent construction jobs and 50 operational jobs"),
    ("SSD-68013714", "operational_jobs", 50, 12,
     "Employment 100 full-time equivalent construction jobs and 50 operational jobs"),
    ("SSD-68013714", "capital_cost_aud", 800000000, 12, "Estimated Development Cost $800,000,000"),
    # Project Pluto, Guildford West: assessment report
    ("SSD-69223466", "total_capacity_mw", 100, 12, "Total power consumption of 100 MW with an IT Load of 68 MW"),
    ("SSD-69223466", "it_capacity_mw", 68, 12, "Total power consumption of 100 MW with an IT Load of 68 MW"),
    ("SSD-69223466", "campus_area_ha", 7.171, 12, "site area 71,710 m2", "sqm_to_ha"),
    ("SSD-69223466", "gfa_sqm", 29444, 12, "Gross floor area (GFA) 29,444 m2"),
    ("SSD-69223466", "construction_jobs", 467, 13,
     "Employment 467 full-time equivalent construction jobs and 60 operational jobs"),
    ("SSD-69223466", "operational_jobs", 60, 13,
     "Employment 467 full-time equivalent construction jobs and 60 operational jobs"),
    ("SSD-69223466", "capital_cost_aud", 1114474328, 13, "Estimated Development Cost $1,114,474,328"),
    # DigiCo SYD1 Data Centre Expansion, Ultimo: assessment report. Its 45 operational jobs are
    # existing jobs retained, not jobs the development creates, so they are not taken.
    ("SSD-69637456", "total_capacity_mw", 120, 13, "Total power consumption of 120 MW (88 MW IT load)"),
    ("SSD-69637456", "it_capacity_mw", 88, 13, "Total power consumption of 120 MW (88 MW IT load)"),
    ("SSD-69637456", "campus_area_ha", 1.1, 13, "Site area 1.1 ha"),
    ("SSD-69637456", "construction_jobs", 80, 14,
     "Employment 80 full-time equivalent construction jobs and retention of 45 operational jobs"),
    ("SSD-69637456", "capital_cost_aud", 605593980, 14, "Estimated development cost (EDC) $605,593,980.00"),
    # CDC Marsden Park (105 and 113 Hollinsworth Road): assessment report
    ("SSD-70889211", "total_capacity_mw", 720, 12, "Maximum power capacity • 720 MW (504 MW IT load)"),
    ("SSD-70889211", "it_capacity_mw", 504, 12, "Maximum power capacity • 720 MW (504 MW IT load)"),
    ("SSD-70889211", "campus_area_ha", 20.91, 12, "Site area 20.91 hectares"),
    ("SSD-70889211", "gfa_sqm", 279650, 12, "Gross floor area (GFA) 279,650 m2"),
    ("SSD-70889211", "construction_jobs", 220, 13,
     "Employment 220 full-time equivalent construction jobs and 265 operational jobs"),
    ("SSD-70889211", "operational_jobs", 265, 13,
     "Employment 220 full-time equivalent construction jobs and 265 operational jobs"),
    ("SSD-70889211", "capital_cost_aud", 3113226273, 13, "Estimated development cost $3,113,226,273"),
    # Project Duke, Mascot: assessment report; Table 7 compares the original development with the
    # amended one, and only the amended site area is taken.
    ("SSD-71368959", "total_capacity_mw", 120, 13,
     "Total power consumption of 120 megawatts (MW), with IT load of up to 85 MW"),
    ("SSD-71368959", "it_capacity_mw", 85, 13,
     "Total power consumption of 120 megawatts (MW), with IT load of up to 85 MW"),
    ("SSD-71368959", "construction_jobs", 600, 14,
     "Employment 600 full - time equivalent construction jobs and 30 operational jobs"),
    ("SSD-71368959", "operational_jobs", 30, 14,
     "Employment 600 full - time equivalent construction jobs and 30 operational jobs"),
    ("SSD-71368959", "capital_cost_aud", 1177672175, 14, "Estimated Development Cost $ 1,1 7 7,672,175"),
    ("SSD-71368959", "campus_area_ha", 2.2923, 62,
     "Aspect Original Development in EIS Amended Development Site area 20,760 m 2 ( 2 Kent Road, 10 - 22 Kent Road) "
     "22,923 m 2 (2 Kent Road, 10 - 22 Kent Road and 685 Gardeners Road)", "sqm_to_ha"),
    # Glendenning Road Data Centre: assessment report
    ("SSD-73761707", "total_capacity_mw", 235, 13, "Maximum power capacity • 235 MW (IT load of 193.6 MW)"),
    ("SSD-73761707", "it_capacity_mw", 193.6, 13, "Maximum power capacity • 235 MW (IT load of 193.6 MW)"),
    ("SSD-73761707", "gfa_sqm", 50233, 13, "Total GFA of 50,233 m 2"),
    ("SSD-73761707", "campus_area_ha", 10.44, 13, "Site area 10.44 hect"),
    ("SSD-73761707", "construction_jobs", 1076, 15,
     "Employment 1,076 full - time equivalent construction jobs and 106 operational jobs"),
    ("SSD-73761707", "operational_jobs", 106, 15,
     "Employment 1,076 full - time equivalent construction jobs and 106 operational jobs"),
    ("SSD-73761707", "capital_cost_aud", 2168267746, 15, "Estimated development cost $2,168,267,746"),
    # Project Apollo, Macquarie Park (4-10 Talavera Road): assessment report
    ("SSD-74069708", "total_capacity_mw", 135, 13, "Total power consumption of up to 135 megawatts (MW)"),
    ("SSD-74069708", "campus_area_ha", 2.319, 13, "Site area 23,190 m2", "sqm_to_ha"),
    ("SSD-74069708", "construction_jobs", 400, 15,
     "Employment 400 full-time equivalent construction jobs and 60 operational jobs"),
    ("SSD-74069708", "operational_jobs", 60, 15,
     "Employment 400 full-time equivalent construction jobs and 60 operational jobs"),
    ("SSD-74069708", "capital_cost_aud", 1365463075, 15, "Estimated development cost $1,365,463,075"),
    # 22 O'Riordan Street, Alexandria: the request for SEARs form
    ("SSD-77274467", "capital_cost_aud", 2000000000, 1, "Estimated Development Cost (excl GST) AUD2,000,000,000.00"),
    ("SSD-77274467", "operational_jobs", 100, 1, "Indicative Operation Jobs 100 Indicative Construction Jobs 220"),
    ("SSD-77274467", "construction_jobs", 220, 1, "Indicative Operation Jobs 100 Indicative Construction Jobs 220"),
    ("SSD-77274467", "gfa_sqm", 20970, 1, "Gross Floor Area (GFA) sqm 20,970"),
    ("SSD-77274467", "campus_area_ha", 0.7436, 2, "Site Area sqm 7,436", "sqm_to_ha"),
    # Julius Avenue Data Centre, North Ryde: EIS. Its construction jobs ("4,963.49 FTE") are a
    # calculated fraction, not a count, and are not taken.
    ("SSD-80018208", "it_capacity_mw", 115.2, 80,
     "The IT load for the Proposal is 115.2 MW and the total power consumption for the Proposal is 169 MW."),
    ("SSD-80018208", "total_capacity_mw", 169, 80,
     "The IT load for the Proposal is 115.2 MW and the total power consumption for the Proposal is 169 MW."),
    ("SSD-80018208", "capital_cost_aud", 1582669210, 80, "The Proposal as an EDC of $1,582,669,210 (exc. GST)."),
    ("SSD-80018208", "operational_jobs", 50, 80, "the operational jobs for the Proposal is 50"),
    ("SSD-80018208", "campus_area_ha", 2.863, 27, "Site area 2.863ha"),
    # Brookhollow Avenue Data Centre Expansion, Norwest: EIS. Its total is stated only in MVA,
    # which is not MW and is not converted; operational jobs are stated only for one stage.
    ("SSD-81928961", "it_capacity_mw", 96, 24,
     "the proposed development has an IT load of 96 MW and a total power consumption of 120 MVA"),
    ("SSD-81928961", "gfa_sqm", 16191, 20, "Gross Floor Area (GFA) of 16,191m2"),
    ("SSD-81928961", "capital_cost_aud", 1248408516, 49, "Estimated Development Cost $1,248,408,516 (excl. GST)"),
    ("SSD-81928961", "construction_jobs", 555, 50, "Construction Jobs: 555"),
    # Dicker Data, 238 Captain Cook Drive, Kurnell: assessment report (a warehouse and distribution
    # centre with a data centre; the jobs are the whole development's)
    ("SSD-8662", "capital_cost_aud", 77186968, 15, "Capital investment value • $77,186,968"),
    ("SSD-8662", "construction_jobs", 350, 15, "Employment • 350 construction jobs and 257 operational jobs"),
    ("SSD-8662", "operational_jobs", 257, 15, "Employment • 350 construction jobs and 257 operational jobs"),
    # Lane Cove West Data Centre (1 Sirius Road): assessment report
    ("SSD-9741", "capital_cost_aud", 196852378, 16, "Capital investment value (CIV) $196,852,378"),
    ("SSD-9741", "construction_jobs", 320, 16, "Employment 320 construction jobs and 100 operational jobs"),
    ("SSD-9741", "operational_jobs", 100, 16, "Employment 320 construction jobs and 100 operational jobs"),
    ("SSD-9741", "campus_area_ha", 3.59, 14, "Site area 3.59 ha"),
    ("SSD-9741", "gfa_sqm", 32429, 15, "The data centre would have a total GFA of 32,429 m 2"),
    # Mowbray Road Data Centre (withdrawn): scoping report. Operational jobs are given only as a
    # lower bound ("exceed approximately 50") and are not taken.
    ("SSD-13475973", "campus_area_ha", 1.757, 9, "Site Area 1.757 ha"),
    ("SSD-13475973", "construction_jobs", 300, 13,
     "Construction jobs are expected to be in the order of approximately 300"),
    # Road 1 Data Centre, Macquarie Park: the request for SEARs form
    ("SSD-80814238", "capital_cost_aud", 300000000, 1, "Estimated Development Cost (excl GST) AUD300,000,000.00"),
    ("SSD-80814238", "operational_jobs", 50, 1, "Indicative Operation Jobs 50 Indicative Construction Jobs 200"),
    ("SSD-80814238", "construction_jobs", 200, 1, "Indicative Operation Jobs 50 Indicative Construction Jobs 200"),
    ("SSD-80814238", "gfa_sqm", 13920, 1, "Gross Floor Area (GFA) sqm 13,920"),
    ("SSD-80814238", "campus_area_ha", 0.8093, 2, "Site Area sqm 8,093", "sqm_to_ha"),
    # STACK SYD01, Erskine Park: the request for SEARs form
    ("SSD-82211208", "capital_cost_aud", 650000000, 1, "Estimated Development Cost (excl GST) AUD650,000,000.00"),
    ("SSD-82211208", "operational_jobs", 100, 1, "Indicative Operation Jobs 100 Indicative Construction Jobs 800"),
    ("SSD-82211208", "construction_jobs", 800, 1, "Indicative Operation Jobs 100 Indicative Construction Jobs 800"),
    ("SSD-82211208", "gfa_sqm", 82020, 1, "Gross Floor Area (GFA) sqm 82,020"),
    ("SSD-82211208", "campus_area_ha", 7.7243, 2, "Site Area sqm 77,243", "sqm_to_ha"),
    # 23-25 Waterloo Road, Macquarie Park: the request for SEARs form
    ("SSD-91297457", "capital_cost_aud", 700000000, 1, "Estimated Development Cost (excl GST) AUD700,000,000.00"),
    ("SSD-91297457", "operational_jobs", 50, 1, "Indicative Operation Jobs 50 Indicative Construction Jobs 3,400"),
    ("SSD-91297457", "construction_jobs", 3400, 1, "Indicative Operation Jobs 50 Indicative Construction Jobs 3,400"),
    ("SSD-91297457", "gfa_sqm", 23375, 1, "Gross Floor Area (GFA) sqm 23,375"),
    ("SSD-91297457", "campus_area_ha", 1.12, 2, "Site Area sqm 11,200", "sqm_to_ha"),
    # Mamre Road Data Centre Campus, Kemps Creek: EIS. Its construction jobs are stated twice and
    # differ (10,059 on p120, 10,056 on p56), so neither is taken.
    ("SSD-92743706", "it_capacity_mw", 1040, 120,
     "The IT load for the proposal is 1.04-GW and the total power consumption for the proposal is 1.2-GW.", "gw_to_mw"),
    ("SSD-92743706", "total_capacity_mw", 1200, 120,
     "The IT load for the proposal is 1.04-GW and the total power consumption for the proposal is 1.2-GW.", "gw_to_mw"),
    ("SSD-92743706", "operational_jobs", 800, 120, "the operational jobs for the proposal is 800"),
    ("SSD-92743706", "capital_cost_aud", 8999802659.81, 56, "EDC $8,999,802,659.81"),
    ("SSD-92743706", "campus_area_ha", 52, 40, "Site Area 52 hectares"),

    # Proponents: the applicant each document names, verbatim, for sites with none recorded.
    # Not taken where the applicant is a consultancy acting for an unnamed client: ARUP (Mowbray
    # Road, SSD-13475973), Lehr Consultants (Honeman Close, SSD-58601963) and Greenbox
    # Architecture (23-25 Waterloo Road, SSD-91297457).
    ("SSD-108864209", "proponent", "NEXTDC Ltd", 5,
     "This Scoping Report has been prepared on behalf of NEXTDC Ltd (the Applicant)"),
    ("SSD-112059740", "proponent", "Stockland Development Pty Limited", 5,
     "prepared by Urbis on behalf of Stockland Development Pty Limited (the Applicant)"),
    ("SSD-113934740", "proponent", "NEXTDC", 7,
     "This Scoping Report has been prepared on behalf of NEXTDC (the Applicant)"),
    ("SSD-133677993", "proponent", "CDC Data Centres Pty Ltd", 7,
     "on behalf of CDC Data Centres Pty Ltd (the Proponent)"),
    ("SSD-139545990", "proponent", "Gateway Capital", 4,
     "This Scoping Report has been prepared on behalf of Gateway Capital (the Applicant)"),
    ("SSD-21342738", "proponent", "NineZero DC Sub TC I Pty Ltd", 5,
     "NineZero DC Sub TC I Pty Ltd trading as DCI Data Centers (the Applicant)"),
    ("SSD-69223466", "proponent", "Goodman Property Services (Aust) Pty Ltd", 4,
     "Goodman Property Services (Aust) Pty Ltd (the Applicant)"),
    ("SSD-70889211", "proponent", "Canberra Data Centres (CDC) Pty Ltd", 8,
     "Canberra Data Centres (CDC) Pty Ltd (the Applicant)"),
    ("SSD-71368959", "proponent", "Goodman Property Services (Aust) Pty Limited", 4,
     "Goodman Property Services (Aust) Pty Limited (the Applicant)"),
    ("SSD-80018208", "proponent", "ISPT Pty Ltd", 20, "on behalf of ISPT Pty Ltd (the Proponent)"),
    ("SSD-81928961", "proponent", "Project Garden 1 Pty Ltd as trustee for the Norwest Property Trust", 1,
     "On behalf of Project Garden 1 Pty Ltd as trustee for the Norwest Property Trust"),
    ("SSD-77274467", "proponent", "The Trustee for M9 Property Trust", 1,
     "Company Name The Trustee for M9 Property Trust ABN 26226031748"),
    ("SSD-80814238", "proponent", "STOCKLAND DEVELOPMENT PTY LIMITED", 1,
     "Company Name STOCKLAND DEVELOPMENT PTY LIMITED ABN 71000064835"),
    ("SSD-82211208", "proponent", "STACK INFRASTRUCTURE AUSTRALIA PTY LTD", 1,
     "Company Name STACK INFRASTRUCTURE AUSTRALIA PTY LTD ABN 78650472236"),
]


# The batch's research question: opened here and left in progress, with what was done and what was
# deliberately not taken, so the next pass starts from the record rather than from scratch.
GAP = dict(
    id=97, pillar="A", priority=4, status="in_progress", opened=TODAY,
    question=("What does each NSW State Significant Development data centre project's own planning "
              "document state about its cost, jobs, floor and site area, power and applicant?"),
    why_it_matters=("These are the figures a reader expects for every site, and the planning record "
                    "states most of them; before this batch the site record carried few."),
    target_source="NSW Planning Portal: each project's assessment report, EIS, scoping report or SEARs request",
    retrieval_method="manual_review",
    notes=("ADVANCED 2026-10-10 (batch S2). One document per project archived under "
           "data/raw/nsw_planning/documents/ by scrapers/fetch_ssd_documents.py, and every value read "
           "by a person and checked against its page and quote (scripts/curate_ssd_documents.py). "
           "Deliberately not taken, each for a stated reason: NEXTDC S7 total power (612 MW stated as "
           "total power consumption, ~700 MW as expected site load); 12 Frederick Street site area "
           "(1.82 ha and 1.859 ha); Mamre Road construction jobs (10,059 and 10,056); Julius Avenue "
           "construction jobs (a calculated 4,963.49 FTE); undefined 'operational capacity' figures "
           "(Kemps Creek 190 MW, Grand Avenue 31.2 MW, Davis Road 160 MW); DigiCo SYD1's 45 retained "
           "jobs; Brookhollow's total (120 MVA, not MW) and stage-only operational jobs; Mowbray Road's "
           "operational jobs (a lower bound); IT capacity stated only per hall or stage (NEXTDC S5, "
           "DCI Poplars, which gets first-phase capacity only); site totals that include existing "
           "buildings. No public project document found: Augusta Street (SSD-10469), 52 Turner Road "
           "(SSD-60185233), Lanceley Place (SSD-66777221), Waterloo Road ESR (SSD-59516710), Project "
           "Mars (SSD-82052708, EIS not public). Cooling, water and grid connection are stated in many "
           "of these documents but not extracted, because the loader does not carry those fields to "
           "the site."),
    fact_status="VERIFIED", source_id="SRC_NSWPORTAL_REGISTER", confidence="high", as_of_date=TODAY,
)


def normalise(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def pages(text: str) -> dict[int, str]:
    out = {}
    for m in re.finditer(r"\[\[page (\d+)\]\]\n(.*?)(?=\n\[\[page \d+\]\]|\Z)", text, re.S):
        out[int(m.group(1))] = normalise(m.group(2))
    return out


MULTIPLIER = {"billion": 1e9, "bn": 1e9, "b": 1e9, "million": 1e6, "m": 1e6}


def readings(quote: str) -> set[float]:
    """Every number the quote states, with any money multiplier applied.

    PDF text often splits a word or number with a space ("$263.6 millio n", "14.5 2 hectares").
    The quote must still match the page exactly; only this reading of it also tries the quote
    with spaces removed, so the figure the document states is recognised.
    """
    out = set()
    for text in (quote, quote.replace(" ", "")):
        for m in re.finditer(r"(\d[\d,]*(?:\.\d+)?)\s*(billion|bn|million|m\b|b\b)?", text, re.I):
            n = float(m.group(1).replace(",", ""))
            out.add(n)
            if m.group(2):
                out.add(round(n * MULTIPLIER[m.group(2).lower()], 2))
    return out


def documents(errors: list[str]) -> dict[str, dict]:
    """SSD case -> {kind, text pages, meta} for every archived document."""
    out = {}
    for meta_path in sorted(glob.glob(os.path.join(DOCS, "*.pdf.meta.json"))):
        base = meta_path[: -len(".pdf.meta.json")]
        case, kind = os.path.basename(base).split("_", 1)
        meta = json.load(open(meta_path))
        if os.path.exists(base + ".pdf"):
            if hashlib.sha256(open(base + ".pdf", "rb").read()).hexdigest() != meta["sha256"]:
                errors.append(f"{case}: {kind} fails its SHA-256 check")
                continue
        out[case] = dict(kind=kind, pages=pages(open(base + ".txt", encoding="utf-8").read()),
                         meta=meta)
    return out


def main() -> int:
    errors: list[str] = []
    docs = documents(errors)
    sites = ssd_to_site(errors)

    fills: dict[str, dict] = {}
    for case, field, value, page, quote, *conversion in EXTRACTIONS:
        where = f"{case} {field}"
        factor = CONVERSIONS[conversion[0]] if conversion else 1
        if field not in FIELDS:
            errors.append(f"{where}: not a field this batch fills")
            continue
        doc = docs.get(case)
        if doc is None:
            errors.append(f"{where}: no archived document")
            continue
        if normalise(quote) not in doc["pages"].get(page, ""):
            errors.append(f"{where}: quote not found on page {page}: {quote!r}")
            continue
        if field != "proponent" and not any(abs(r * factor - float(value)) < 1e-6
                                            for r in readings(quote)):
            errors.append(f"{where}: {value} is not a number the quote states")
            continue
        if field == "proponent" and normalise(str(value)) not in normalise(quote):
            errors.append(f"{where}: {value!r} is not named in the quote")
            continue
        site = sites.get(case)
        if site is None:
            errors.append(f"{where}: maps to no site")
            continue
        entry = fills.setdefault(case, dict(site=site, fill={}, quotes=[]))
        if field in entry["fill"]:
            errors.append(f"{where}: given twice")
            continue
        entry["fill"][field] = value
        unit = f", {conversion[0].replace('_', ' ')}" if conversion else ""
        entry["quotes"].append(f"p{page} ({field}{unit}): {normalise(quote)}")

    if errors:
        print("refusing to write; fix these first:", file=sys.stderr)
        for e in errors:
            print(f"  {e}", file=sys.stderr)
        return 1

    sources, rows = [], []
    for case, entry in sorted(fills.items()):
        doc = docs[case]
        meta = doc["meta"]
        source_id = f"SRC_{case.replace('-', '')}_{doc['kind'].upper()}"
        sources.append(dict(
            id=source_id,
            title=f"{(meta.get('label') or doc['kind']).removesuffix('.pdf')} - {case} "
                  f"({meta['project_slug'].replace('-', ' ')})",
            publisher=KIND_PUBLISHER[doc["kind"]],
            url=meta["url"],
            doc_type="primary_planning_portal",
            published=None,
            credibility="A",
            accessed=meta["fetched_utc"][:10],
            notes=(f"{meta.get('folder') or ''} document for {case}, read {meta['fetched_utc'][:10]} from the "
                   f"NSW Planning Portal (attachment {meta['attachment_slug']}), SHA-256 {meta['sha256']}, "
                   f"{meta['bytes']} bytes, text by {meta['extractor']}, archived at "
                   f"data/raw/nsw_planning/documents/. Cited for the figures quoted in source_refs."),
        ))
        rows.append(dict(
            match=dict(id=entry["site"]),
            fill=entry["fill"],
            add_sources=[dict(id=source_id, quote=" | ".join(entry["quotes"]))],
        ))

    pack = {
        "pack_id": "ssd-documents-2026-10",
        "prepared_by": "scripts/curate_ssd_documents.py from data/raw/nsw_planning/documents/",
        "prepared_on": TODAY,
        "_comment": [
            "Fills site figures from each NSW SSD project's assessment report, EIS, scoping report",
            "or SEARs request (batch S2). Every value was read by a person and is checked against",
            "its page and quote. Uses fill, so no existing value is overwritten; differences are",
            "reported at load for a human to settle. Each row cites its document with the passages",
            "quoted.",
        ],
        "sources": sources,
        "rows": {"sites": rows, "research_gaps": [GAP]},
    }
    with open(OUT_PACK, "w") as f:
        json.dump(pack, f, indent=2, ensure_ascii=False)
        f.write("\n")
    n = sum(len(e["fill"]) for e in fills.values())
    print(f"{len(docs)} documents verified; {n} values for {len(rows)} sites; "
          f"wrote {os.path.relpath(OUT_PACK, ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
