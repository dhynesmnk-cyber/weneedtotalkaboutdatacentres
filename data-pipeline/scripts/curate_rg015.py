#!/usr/bin/env python3
"""
Curate the RG-015 pack: the NSW Legislative Council Inquiry into Data Centres record.

Downloaded and archived on 2026-09-18 from files.parliament.nsw.gov.au (SHA-256 manifests in
data/raw/nsw_inquiry/):
  * Terms of reference (updated 5 August 2026)
  * Five CORRECTED/UNCORRECTED hearing transcripts: 1 May, 8 May, 22 May, 29 May, 2 July 2026
    (1,121,548 characters of testimony in total)
  * Five hearing schedules (image-only PDFs; no extractable text - witnesses recovered from the
    transcript appearance formula instead, see data/raw/nsw_inquiry/witnesses.json)

The submissions list at parliament.nsw.gov.au returns HTTP 403 to non-browser clients, so the
~120 submissions themselves are NOT yet harvested. That residual is RG-041.

Run:
    python3 scripts/curate_rg015.py
    python3 scripts/load_pack.py data/packs/rg015_inquiry_record.json --dry-run --allow-missing-source
"""
from __future__ import annotations

import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "data", "packs", "rg015_inquiry_record.json")
TODAY = "2026-09-18"
F = "https://files.parliament.nsw.gov.au/fileapi/ParlFiles/GetArtifact?serverRelativeUrl="

SOURCES = [
    dict(id="SRC_INQ_TOR",
         title="Terms of reference - PAWC - Data centres (updated 5 August 2026)",
         publisher="NSW Legislative Council Public Accountability and Works Committee",
         url=F + "%2Flcdocs%2Finquiries%2F3169%2FTerms%20of%20reference%20-%20PAWC%20-%20Data%20centres"
               "%20-%20Updated%205%20August%202026.pdf",
         doc_type="primary_government", published="2026-08-05", credibility="A", accessed=TODAY,
         notes="Self-referred 29 January 2026; committee to report by 3 November 2026. Chair Abigail Boyd MLC "
               "(The Greens). Eleven terms of reference spanning scale and clustering, the planning framework "
               "including SSD classification and fast-track mechanisms such as the Investment Delivery "
               "Authority, electricity demand and grid impacts including on-site back-up generation, water "
               "usage and cooling, local environmental and community impacts including heat, land use and "
               "housing, economic and distributional outcomes INCLUDING (g)(iii) 'the extent of public "
               "subsidies, concessions or state directed facilitation provided to the sector', governance and "
               "transparency including conflicts of interest in accelerated approval frameworks and the impact "
               "of lobbying and donations, workforce considerations, and lessons from other jurisdictions."),
    dict(id="SRC_INQ_T_0501", title="Transcript - CORRECTED - PAWC - Data Centres - 1 May 2026",
         publisher="NSW Legislative Council Public Accountability and Works Committee",
         url=F + "%2Flcdocs%2Ftranscripts%2F3731%2FTranscript%20-%20CORRECTED%20-%20PAWC%20-%20Data%20Centres"
               "%20-%201%20May%202026.pdf",
         doc_type="primary_government", published="2026-05-01", credibility="A", accessed=TODAY,
         notes="Jubilee Room, Parliament House. Witnesses: Ms Belinda Dennett (CEO, Data Centres Australia); "
               "Ms Claire Pullen (Group CEO, Australian Writers' Guild); Mr Devjeet Matta (Research Officer, "
               "Protocol Policy Lab)."),
    dict(id="SRC_INQ_T_0508", title="Transcript - CORRECTED - PAWC - Data Centres - 8 May 2026",
         publisher="NSW Legislative Council Public Accountability and Works Committee",
         url=F + "%2Flcdocs%2Ftranscripts%2F3732%2FTranscript%20-%20CORRECTED%20-%20PAWC%20-%20Data%20Centres"
               "%20-%208%20May%202026.pdf",
         doc_type="primary_government", published="2026-05-08", credibility="A", accessed=TODAY,
         notes="Macquarie Room. Witnesses: Dr Bronwyn Cumbo (UTS); Professor Kurt Iveson (University of "
               "Sydney); Dr Riki Scanlan (postdoctoral researcher); Mr Andrew Sjoquist (CEO, WinDC); Dr Rob "
               "Nicholls (Centre for AI, Trust and Governance, University of Sydney); Professor Deanna "
               "D'Alessandro (Director, Net Zero Institute, University of Sydney); Mr Jeremy Gill (Head of "
               "Policy, Committee for Sydney); Ms Rochelle Flood (Deputy Mayor, Lane Cove Council)."),
    dict(id="SRC_INQ_T_0522", title="Transcript - CORRECTED - PAWC - Data Centres - 22 May 2026",
         publisher="NSW Legislative Council Public Accountability and Works Committee",
         url=F + "%2Flcdocs%2Ftranscripts%2F3733%2FTranscript%20-%20CORRECTED%20-%20PAWC%20-%20Data%20Centres"
               "%20-%2022%20May%202026.pdf",
         doc_type="primary_government", published="2026-05-22", credibility="A", accessed=TODAY,
         notes="Macquarie Room; the largest hearing (15 witnesses, 360,257 characters). Witnesses include Mr "
               "Jason Krstanoski (Executive General Manager Network, Transgrid); Mr Darren Cleary (Managing "
               "Director, Sydney Water) and Mr Paul Higham (Head of Business); Ms Maryanne Graham (Executive "
               "General Manager Corporate Affairs, Stakeholder Engagement and Environment); Ms Danielle "
               "Francis (Manager Customer and Policy, Water Services Association of Australia); Ms Jaqueline "
               "Mills (Nature Conservation Council of NSW); Ms Solaye Snider and Dr Simon Bradshaw (Greenpeace "
               "Australia Pacific); Mr Gavin Melvin (Executive Director Policy and Strategy, Urban Development "
               "Institute of Australia); Mr Dan Hunter (CEO, Business NSW) and Mr David Borger; Mr Peter "
               "Ephraums (Lane Cove Responsible Planning Group); Mr Tom Edwards (Research and Policy Officer, "
               "Unions NSW); Mr David Eyre (CEO, UNSW Institute for Industrial Decarbonisation); Professor "
               "Nicholas Ekins-Daukes (Head of School of Photovoltaic and Renewable Energy Engineering, UNSW); "
               "Mr Simon Draper PSM (Secretary, Premier's Department); Mr Tom Gellibrand (Chief Executive, "
               "Infrastructure NSW); Mr Alexander Hoysted (Carbon Zero Initiative)."),
    dict(id="SRC_INQ_T_0529", title="Transcript - CORRECTED - PAWC - Data Centres - 29 May 2026",
         publisher="NSW Legislative Council Public Accountability and Works Committee",
         url=F + "%2Flcdocs%2Ftranscripts%2F3806%2FTranscript%20-%20CORRECTED%20-%20PAWC%20-%20Data%20Centres"
               "%20%E2%80%93%2029%20May%202026.pdf",
         doc_type="primary_government", published="2026-05-29", credibility="A", accessed=TODAY,
         notes="Macquarie Room. Witnesses: Mr Colin Crisafulli (General Manager Future Grid and Asset "
               "Management, Endeavour Energy); Ms Fatima Bazzi (Group Executive Customer, Ausgrid) and Ms Annie "
               "Pearson; Mr Martin Kennedy (General Manager Market Operations and Grid, Clean Energy Council); "
               "Ms Wendy Black (Executive Director Policy, Business Council of Australia); Dr Sue Keay "
               "(Director, UNSW AI Institute); Ms Elizabeth Whitelock (CEO, Australian Information Industry "
               "Association); Mr Glenn Hughes (General Manager, Sydmec); Ms Emma Bacon (Executive Director, "
               "Sweltering Cities)."),
    dict(id="SRC_INQ_T_0702", title="Transcript - UNCORRECTED - PAWC - Data Centres in NSW - 2 July 2026",
         publisher="NSW Legislative Council Public Accountability and Works Committee",
         url=F + "%2Flcdocs%2Ftranscripts%2F3815%2FTranscript%20-%20UNCORRECTED%20-%20PAWC%20-%20Data%20Centres"
               "%20in%20NSW%20%E2%80%93%202%20July%202026%20-%20Copy.pdf",
         doc_type="primary_government", published="2026-07-02", credibility="A", accessed=TODAY,
         notes="Macquarie Room, UNCORRECTED copy. Witnesses: Professor David Reilly (School of Physics, "
               "University of Sydney); Professor Thomas Ohki (Professor of Practice of Quantum Technologies); "
               "Ms Kylie Hargreaves (Deputy Chair, Regional Development Australia Sydney); Professor Penelope "
               "Crossley (Professor of Law, University of Sydney)."),
]

ENTITIES = [
    dict(id="ENT_PAWC", name="NSW Legislative Council Public Accountability and Works Committee",
         entity_type="government_agency", domicile="Australia", hq_country="AU",
         notes="The committee running the Inquiry into Data Centres. Chair Abigail Boyd MLC (The Greens). "
               "Members: Hon Mark Buttigieg MLC (ALP), Hon Scott Farlow MLC (Liberal, substituting for Hon "
               "Damien Tudehope MLC from 30 March 2026), Hon Taylor Martin MLC (Independent, substituting for "
               "Hon Mark Latham MLC from 6 May 2026), Hon Jacqui Munro MLC (Liberal, substituting for Hon Sarah "
               "Mitchell MLC from 1 February 2026), Hon Peter Primrose MLC (ALP), Hon Emily Suvaal MLC (ALP, "
               "substituting for Hon Dr Sarah Kaine MLC from 26 March 2026). Report due 3 November 2026. Note "
               "this is a different body from the entity already recorded as ENT_NSWLC.",
         fact_status="VERIFIED", confidence="high", as_of_date=TODAY, source_id="SRC_INQ_TOR"),
    dict(id="ENT_UDIA", name="Urban Development Institute of Australia (NSW)", entity_type="industry_body",
         domicile="Australia", hq_country="AU",
         notes="Gave evidence on 22 May 2026 through Mr Gavin Melvin, Executive Director Policy and Strategy. "
               "The housing-sector voice in the inquiry, and the source of the strongest quantified evidence "
               "that data centre water demand competes with housing delivery.",
         fact_status="VERIFIED", confidence="high", as_of_date=TODAY, source_id="SRC_INQ_T_0522"),
    dict(id="ENT_UNIONS_NSW", name="Unions NSW", entity_type="industry_body", domicile="Australia",
         hq_country="AU",
         notes="Gave evidence on 22 May 2026 through Mr Tom Edwards, Research and Policy Officer, with Mr "
               "Con Tsiaoulas also appearing. Recommends local content quotas and apprentice quotas for data "
               "centres and their associated renewable energy, at no less than the standards set by the "
               "Renewable Energy Sector Board, plus training, work health and safety and industrial standards.",
         fact_status="VERIFIED", confidence="high", as_of_date=TODAY, source_id="SRC_INQ_T_0522"),
    dict(id="ENT_BUSINESS_NSW", name="Business NSW", entity_type="industry_body", domicile="Australia",
         hq_country="AU",
         notes="Gave evidence on 22 May 2026 through Mr Dan Hunter (CEO) and Mr David Borger. Cited the Oxford "
               "Economics phantom demand research alongside Data Centres Australia.",
         fact_status="VERIFIED", confidence="high", as_of_date=TODAY, source_id="SRC_INQ_T_0522"),
    dict(id="ENT_PREMIERS_DEPT", name="NSW Premier's Department", entity_type="government_agency",
         domicile="Australia", hq_country="AU",
         notes="Secretary Mr Simon Draper PSM gave evidence on 22 May 2026. The department made NO submission to "
               "the inquiry despite an invitation, and despite budget estimates evidence that a government "
               "submission was expected.",
         fact_status="VERIFIED", confidence="high", as_of_date=TODAY, source_id="SRC_INQ_T_0522"),
    dict(id="ENT_INFRA_NSW", name="Infrastructure NSW", entity_type="government_agency", domicile="Australia",
         hq_country="AU",
         notes="Chief Executive Mr Tom Gellibrand gave evidence on 22 May 2026. Publisher of the NSW Data Centre "
               "Guidelines.",
         fact_status="VERIFIED", confidence="high", as_of_date=TODAY, source_id="SRC_INQ_T_0522"),
    dict(id="ENT_LCRPG", name="Lane Cove Responsible Planning Group", entity_type="community_group",
         domicile="Australia", hq_country="AU",
         notes="Mr Peter Ephraums gave evidence on 22 May 2026. Community planning group in the Lane Cove / "
               "lower north shore corridor where an operating data centre sits 350 m from homes and the NSW "
               "Government has IDA-endorsed a further project at 16-20 Mars Road.",
         fact_status="VERIFIED", confidence="high", as_of_date=TODAY, source_id="SRC_INQ_T_0522"),
    dict(id="ENT_LANE_COVE_COUNCIL", name="Lane Cove Council", entity_type="council", domicile="Australia",
         hq_country="AU",
         notes="Deputy Mayor Ms Rochelle Flood gave evidence on 8 May 2026. Lane Cove LGA contains five data "
               "centre SSD records, one approved with four modifications including a fuel storage modification, "
               "one withdrawn, and one at Prepare EIS.",
         fact_status="VERIFIED", confidence="high", as_of_date=TODAY, source_id="SRC_INQ_T_0508"),
    dict(id="ENT_SWELTERING", name="Sweltering Cities", entity_type="community_group", domicile="Australia",
         hq_country="AU",
         notes="Executive Director Ms Emma Bacon gave evidence on 29 May 2026. Urban heat advocacy organisation, "
               "relevant to the cumulative microclimate impact Blacktown City Council raised in its objection to "
               "SSD-73761707.",
         fact_status="VERIFIED", confidence="high", as_of_date=TODAY, source_id="SRC_INQ_T_0529"),
    dict(id="ENT_ENDEAVOUR", name="Endeavour Energy", entity_type="network_business", domicile="Australia",
         hq_country="AU",
         notes="Distribution network service provider for parts of Greater Sydney including the Blacktown LGA "
               "where the 235 MW Glendenning Road data centre was consented; it submitted standard DA conditions "
               "on that application. General Manager Future Grid and Asset Management Mr Colin Crisafulli and "
               "others gave evidence on 29 May 2026.",
         fact_status="VERIFIED", confidence="high", as_of_date=TODAY, source_id="SRC_INQ_T_0529"),
    dict(id="ENT_IPART2", name="IPART", entity_type="regulator", domicile="Australia", hq_country="AU",
         notes="Data Centres Australia told the committee on 1 May 2026 that IPART 'dismissed' Sydney Water's "
               "projection that data centres could use 25 per cent of Sydney's water by 2035 as 'unverifiable'. "
               "That characterisation of IPART's position has NOT been checked against IPART's own "
               "determination and is recorded as a claim - research gap RG-042. Separately, the UDIA told the "
               "committee that Sydney Water's IPART determination funds it for 100,000 fewer homes over five "
               "years than the National Housing Accord target requires.",
         fact_status="REPORTED", confidence="low", as_of_date=TODAY, source_id="SRC_INQ_T_0501"),
    dict(id="ENT_CARBONZERO", name="Carbon Zero Initiative", entity_type="other", domicile="Australia",
         hq_country="AU",
         notes="Not-for-profit focused on decarbonisation; Partner and Strategy Lead Mr Alexander Hoysted gave "
               "evidence on 22 May 2026. States that in February 2026 it convened a public principles process at "
               "the intersection of digital and energy infrastructure.",
         fact_status="VERIFIED", confidence="medium", as_of_date=TODAY, source_id="SRC_INQ_T_0522"),
    dict(id="ENT_WINDC", name="WinDC", entity_type="industry_body", domicile="Australia", hq_country="AU",
         notes="CEO Mr Andrew Sjoquist gave evidence on 8 May 2026.",
         fact_status="VERIFIED", confidence="medium", as_of_date=TODAY, source_id="SRC_INQ_T_0508"),
]

METRICS = [
    dict(as_of="2026-05", scope="Australia", metric_name="dca_member_share_of_operational_capacity",
         value=86.0, unit="%", basis="actual",
         notes="Belinda Dennett, CEO of Data Centres Australia, under parliamentary privilege: 'Our members "
               "represent 86 per cent of operational data centre capacity across the country.' DCA launched on "
               "28 November 2025 and grew out of five data centre operators that began meeting about two and a "
               "half years earlier.",
         fact_status="VERIFIED", confidence="high", as_of_date=TODAY, source_id="SRC_INQ_T_0501"),
    dict(as_of="2030", scope="Australia", metric_name="dc_operator_energy_infrastructure_payments", value=10.3,
         unit="AUD bn", basis="forecast_central",
         notes="Claimed by Data Centres Australia: operators will pay $10.3 billion in energy infrastructure to "
               "2030. Asserted alongside the claim that the national electricity rules require all large load "
               "users including data centres to pay 100 per cent of connection costs and augmentations.",
         fact_status="CLAIMED", confidence="medium", as_of_date=TODAY, source_id="SRC_INQ_T_0501"),
    dict(as_of="2030", scope="Australia", metric_name="dc_excess_capacity_available_for_public_use", value=1.1,
         unit="AUD bn", basis="forecast_central",
         notes="Data Centres Australia: of the $10.3 billion, $1.1 billion is excess capacity available for "
               "public use. This is the industry's own version of the 'no net cost to consumers' principle and "
               "should be tested against network business capital plans.",
         fact_status="CLAIMED", confidence="medium", as_of_date=TODAY, source_id="SRC_INQ_T_0501"),
    dict(as_of="2026", scope="Australia", metric_name="dc_share_of_national_water_use_dca_claim", value=0.04,
         unit="%", basis="estimate",
         notes="Data Centres Australia, citing the ABS water accounts: data centre water use is 0.04 per cent of "
               "Australia's water use and less than 1 per cent of Sydney's. Directly contradicts Sydney Water's "
               "projection of up to 25 per cent of Greater Sydney drinking water demand by 2035. The two are "
               "probably measuring different things - current measured use against a ten-year forward "
               "projection based on applications received - but the gap is four orders of magnitude in framing "
               "and the committee put it to both parties.",
         fact_status="CLAIMED", confidence="medium", as_of_date=TODAY, source_id="SRC_INQ_T_0501"),
    dict(as_of="2026", scope="Australia", metric_name="dc_share_of_water_use_dca_estimate", value=1.9,
         unit="%", basis="estimate",
         notes="Figure attributed to Data Centres Australia by the Chair when putting the discrepancy to Sydney "
               "Water's Managing Director on 22 May 2026: 'DCA say that they estimate 1.9 per cent of water will "
               "be used for data centres, which is very different to your 25 per cent.' Note this is a second, "
               "different DCA water figure from the 0.04 per cent / less than 1 per cent given on 1 May.",
         fact_status="REPORTED", confidence="medium", as_of_date=TODAY, source_id="SRC_INQ_T_0522"),
    dict(as_of="2026-05", scope="Sydney", metric_name="sydney_water_stands_by_25pct", value=25.0, unit="%",
         basis="forecast_high",
         notes="Darren Cleary, Managing Director of Sydney Water, under questioning: 'We do [stand by the 25 per "
               "cent forecast demand], and we acknowledge the uncertainty.' He added that the current "
               "applications alone represent water demand 'the equivalent of a new suburb connecting to our "
               "system', that the ten-year figure could be 20, 10 or 5 per cent, and that Sydney Water removes "
               "obviously duplicative or entirely speculative applications but otherwise forecasts on "
               "applications actually received. On phantom demand specifically: water applications are less "
               "likely to be phantom than energy applications because by the time a proponent applies for water "
               "it has typically already secured its energy connection, so its project is more mature.",
         fact_status="VERIFIED", confidence="high", as_of_date=TODAY, source_id="SRC_INQ_T_0522"),
    dict(as_of="2026-05", scope="Sydney", metric_name="medium_dc_water_demand_equivalent_homes", value=9000,
         unit="homes", basis="estimate",
         notes="UDIA: a medium-sized data centre using around five megalitres per day has a water demand broadly "
               "equivalent to around 9,000 homes.",
         fact_status="VERIFIED", confidence="high", as_of_date=TODAY, source_id="SRC_INQ_T_0522"),
    dict(as_of="2026-05", scope="South-west Sydney", metric_name="housing_lots_constrained_water_sewer",
         value=121000, unit="lots", basis="actual",
         notes="UDIA: the Department of Planning's Urban Development Program identifies around 121,000 housing "
               "lots still to be created across three south-west Sydney growth areas, constrained by a lack of "
               "water and sewer infrastructure.",
         fact_status="VERIFIED", confidence="high", as_of_date=TODAY, source_id="SRC_INQ_T_0522"),
    dict(as_of="2026-05", scope="Sydney", metric_name="dwellings_blocked_by_water_servicing_pct", value=62.0,
         unit="%", basis="actual",
         notes="UDIA survey work representing more than 36,000 planned dwellings found 22,400 of them - 62 per "
               "cent - unable to proceed because of a lack of committed water or wastewater infrastructure. This "
               "is the strongest quantified evidence in the inquiry record that data centre water demand "
               "competes directly with housing delivery.",
         fact_status="VERIFIED", confidence="high", as_of_date=TODAY, source_id="SRC_INQ_T_0522"),
    dict(as_of="2026-05", scope="Sydney", metric_name="sydney_water_funding_shortfall_vs_housing_accord",
         value=100000, unit="homes", basis="estimate",
         notes="UDIA: Sydney Water's IPART determination means it is funded for 100,000 fewer homes in its "
               "servicing area over the next five years than the National Housing Accord target requires Sydney "
               "to deliver.",
         fact_status="REPORTED", confidence="medium", as_of_date=TODAY, source_id="SRC_INQ_T_0522"),
    dict(as_of="2026-05", scope="NSW", metric_name="transgrid_enquiries_vs_formal_applications_gw", value=6.0,
         unit="GW", basis="pipeline",
         notes="Transgrid's submission, put to it by the Chair: more than 10 GW of connection inquiries from data "
               "centres, with approximately 6 GW progressing to formal applications. Jason Krstanoski confirmed "
               "the 10 GW is the inquiry stage and the 6 GW is where proponents are paying money and progressing "
               "through technical assessments.",
         fact_status="VERIFIED", confidence="high", as_of_date=TODAY, source_id="SRC_INQ_T_0522"),
    dict(as_of="2026-05", scope="NSW", metric_name="transgrid_committed_data_centre_connections", value=0,
         unit="count", basis="actual",
         notes="Jason Krstanoski, Executive General Manager Network, Transgrid, on 22 May 2026: 'We are very "
               "close but we haven't had a data centre actually commit yet. We're on the eve of that now.' As at "
               "that date NO data centre had committed to a transmission connection on Transgrid's network, "
               "against 10 GW of inquiries and 6 GW of formal applications. This is the single hardest "
               "quantification of phantom demand in the Australian record and it comes from the network business "
               "itself.",
         fact_status="VERIFIED", confidence="high", as_of_date=TODAY, source_id="SRC_INQ_T_0522"),
    dict(as_of="2026-05", scope="NSW", metric_name="inquiry_witnesses", value=37, unit="count", basis="actual",
         notes="Distinct witnesses across five hearings (1, 8, 22, 29 May and 2 July 2026), recovered from the "
               "transcript appearance formula. 15 appeared on 22 May alone, including Sydney Water, Transgrid, "
               "WSAA, UDIA, Business NSW, Unions NSW, the Nature Conservation Council, Greenpeace, the Premier's "
               "Department and Infrastructure NSW.",
         fact_status="VERIFIED", confidence="high", as_of_date=TODAY, source_id="SRC_INQ_T_0522"),
]

REG_EVENTS = [
    dict(event_date="2026-05-01", regulator_id="ENT_PAWC", instrument_id="LAW_NSW_INQUIRY",
         event_type="hearing",
         summary="First public hearing, Jubilee Room. Data Centres Australia gave evidence that operators pay "
                 "100 per cent of connection and augmentation costs, will pay $10.3 billion in energy "
                 "infrastructure to 2030 with $1.1 billion of that excess capacity available for public use, do "
                 "not receive subsidies or tax incentives, and that the widely repeated 25 per cent Sydney water "
                 "figure is 'not based in fact' and was dismissed by IPART as unverifiable.",
         notes="Also: Australian Writers' Guild on copyright and AI training; Protocol Policy Lab on tax "
               "incentives in other jurisdictions and their risks.",
         fact_status="VERIFIED", confidence="high", as_of_date=TODAY, source_id="SRC_INQ_T_0501"),
    dict(event_date="2026-05-08", regulator_id="ENT_PAWC", instrument_id="LAW_NSW_INQUIRY",
         event_type="hearing",
         summary="Second hearing. Academic and community evidence: UTS, University of Sydney (urban geography, "
                 "AI trust and governance, Net Zero Institute), WinDC, Committee for Sydney, and Lane Cove "
                 "Council's Deputy Mayor. A committee member proposed that community benefit sharing could be "
                 "funded through a shift in land tax classification for data centres; the witness had done no "
                 "analysis of the land tax implication and cautioned that market equality within zones would "
                 "need to be considered.",
         notes="This is the only point in the record where a land tax change is floated, and it is floated by a "
               "committee member as a revenue-raising mechanism for community benefit - the opposite direction "
               "from a concession.",
         fact_status="VERIFIED", confidence="high", as_of_date=TODAY, source_id="SRC_INQ_T_0508"),
    dict(event_date="2026-05-22", regulator_id="ENT_PAWC", instrument_id="LAW_NSW_INQUIRY",
         event_type="hearing",
         summary="Largest hearing, 15 witnesses. Transgrid confirmed 10 GW of inquiries and 6 GW of formal "
                 "applications but no committed data centre connection. Sydney Water's Managing Director stood "
                 "by the 25 per cent projection while acknowledging uncertainty. UDIA quantified the collision "
                 "with housing delivery. Unions NSW recommended local content and apprentice quotas at no less "
                 "than Renewable Energy Sector Board standards. The Premier's Department appeared without having "
                 "made a submission.",
         fact_status="VERIFIED", confidence="high", as_of_date=TODAY, source_id="SRC_INQ_T_0522"),
    dict(event_date="2026-05-22", regulator_id="ENT_PAWC", instrument_id="LAW_NSW_INQUIRY",
         event_type="other",
         summary="GOVERNANCE FINDING. The Chair recorded that the Premier's Department made no submission to the "
                 "inquiry despite an invitation, and that budget estimates evidence had indicated a government "
                 "submission was expected. Secretary Simon Draper PSM said the department thought appearing in "
                 "person would be more effective; the Chair replied 'It's not.' Ms Jacqui Munro MLC established "
                 "that the department had not prepared a submission and sought permission to make one. Sydney "
                 "Water also made no submission, which the Chair described as perplexing given it was invited to "
                 "appear.",
         notes="Directly relevant to terms of reference (h)(i)-(iv) on governance, transparency and "
               "accountability. The two bodies holding the most material data on water demand and government "
               "coordination gave oral evidence only, with no written submission on the public record.",
         fact_status="VERIFIED", confidence="high", as_of_date=TODAY, source_id="SRC_INQ_T_0522"),
    dict(event_date="2026-05-29", regulator_id="ENT_PAWC", instrument_id="LAW_NSW_INQUIRY",
         event_type="hearing",
         summary="Networks and industry hearing: Endeavour Energy, Ausgrid, Clean Energy Council, Business "
                 "Council of Australia, UNSW AI Institute, Australian Information Industry Association, Sydmec "
                 "and Sweltering Cities. Discussion included cross-subsidisation risk, stranded assets and "
                 "inefficient utilisation of allocated capacity, and the proposition that excess network "
                 "capacity gives data centres potential to absorb infrastructure costs and therefore reduce "
                 "household bills.",
         fact_status="VERIFIED", confidence="high", as_of_date=TODAY, source_id="SRC_INQ_T_0529"),
    dict(event_date="2026-07-02", regulator_id="ENT_PAWC", instrument_id="LAW_NSW_INQUIRY",
         event_type="hearing",
         summary="Final hearing (uncorrected transcript): University of Sydney physics and quantum technologies, "
               "Regional Development Australia Sydney, and a professor of law. Regional siting and the "
               "sovereign-capability framing featured.",
         fact_status="VERIFIED", confidence="high", as_of_date=TODAY, source_id="SRC_INQ_T_0702"),
    dict(event_date="2026-11-03", regulator_id="ENT_PAWC", instrument_id="LAW_NSW_INQUIRY",
         event_type="review_announced",
         summary="The committee is required to report by 3 November 2026.",
         notes="This is the next major scheduled event in the Australian data centre policy calendar, alongside "
               "the ECMC's September 2026 consideration of National Electricity Rule changes and the "
               "Commonwealth legislation flagged for early 2027.",
         fact_status="VERIFIED", confidence="high", as_of_date=TODAY, source_id="SRC_INQ_TOR"),
]

CLAIMS = [
    dict(claimant_id="ENT_DATA_CENTRES_AU", claim_date="2026-05-01", claim_scope="national",
         claim_type="other",
         claim_text="Data centre operators pay their way. The national electricity rules require all large load "
                    "users, including data centres, to pay 100 per cent of connection costs and augmentations to "
                    "the network. Data centre operators will pay $10.3 billion in energy infrastructure to 2030, "
                    "and $1.1 billion of that is excess capacity available for public use. Data centre operators "
                    "do not receive subsidies or tax incentives.",
         instrument_relied_on="National Electricity Rules connection and augmentation cost allocation",
         lgc_surrender_evidence="n/a",
         verification_status="PARTIALLY_VERIFIED",
         verification_note="The 'pay 100 per cent of connection and augmentation costs' limb is corroborated "
                           "independently: Transgrid's 26 August 2026 position states that where new large users "
                           "drive network investment beyond their physical connection, costs will be borne by the "
                           "proponents rather than existing consumers, and the Network Capacity Allocation Policy "
                           "makes capacity conditional on committing to fund augmentation. The $10.3bn and "
                           "$1.1bn figures are industry forecasts and are NOT verified. The 'no subsidies or tax "
                           "incentives' limb is consistent with this database's own finding that no cash "
                           "concession has been located, but it does not address non-cash state support, which "
                           "IS documented: the 75-day NSW fast track, Investment Delivery Authority endorsement, "
                           "a NSW approvals authority for projects above A$1bn, and Victoria's three-month fast "
                           "track. Given on 1 May 2026, six months before the IDA Round 2 and after Round 1.",
         fact_status="CLAIMED", confidence="high", as_of_date=TODAY, source_id="SRC_INQ_T_0501"),
    dict(claimant_id="ENT_DATA_CENTRES_AU", claim_date="2026-05-01", claim_scope="national",
         claim_type="other",
         claim_text="There is significant misinformation around water use in the public debate. The ABS water "
                    "accounts show that data centre water use is 0.04 per cent of Australia's water use, and "
                    "less than 1 per cent of Sydney's water use. The 25 per cent of Sydney's water by 2035 that "
                    "has been widely repeated in the media and in submissions to this inquiry is not based in "
                    "fact. It was dismissed by IPART - the independent pricing regulator - as being "
                    "unverifiable, and it should be dismissed.",
         instrument_relied_on="ABS water accounts",
         verification_status="CONTRADICTED",
         verification_note="Contradicted on three grounds from the same inquiry record. (1) Sydney Water's "
                           "Managing Director Darren Cleary was asked directly on 22 May 2026 whether he stood "
                           "by the 25 per cent forecast and answered 'We do, and we acknowledge the uncertainty', "
                           "adding that current applications alone represent demand equivalent to a new suburb "
                           "connecting to the system. The utility that holds the applications stands by the "
                           "figure. (2) The claim conflates current measured use with a ten-year forward "
                           "projection: the ABS water accounts describe present consumption, Sydney Water's "
                           "figure describes demand from applications received. (3) The characterisation of "
                           "IPART's position as dismissing the figure is unverified and is being checked against "
                           "IPART's own determination (RG-042). Note also that DCA gave two different figures on "
                           "two different days - 0.04 per cent of national use and less than 1 per cent of "
                           "Sydney's on 1 May, and 1.9 per cent as attributed by the Chair on 22 May.",
         fact_status="CLAIMED", confidence="high", as_of_date=TODAY, source_id="SRC_INQ_T_0501"),
    dict(claimant_id="ENT_SYDNEYWATER", claim_date="2026-05-22", claim_scope="national",
         claim_type="other",
         claim_text="Data centre water demand could reach 25 per cent of Greater Sydney demand over ten years; "
                    "there will not be a cross-subsidy to the consumer, and if a recycled water facility is "
                    "developed that cost will be borne by the proponents.",
         instrument_relied_on="applications received",
         verification_status="PARTIALLY_VERIFIED",
         verification_note="The Managing Director stood by the projection under questioning while conceding the "
                           "ten-year figure could be 20, 10 or 5 per cent, and explained the method: forecasts "
                           "are based on applications actually received, with obviously duplicative or entirely "
                           "speculative applications removed. He also gave the committee a reason to trust water "
                           "applications more than energy applications: by the time a proponent applies for water "
                           "it has typically already secured its energy connection, so its project is more "
                           "mature. The no-cross-subsidy commitment is consistent with the IPART water pricing "
                           "review commissioned on 17 August 2026 and with NSW Guideline Principle 2, but is a "
                           "statement of intent rather than an enforceable obligation.",
         fact_status="VERIFIED", confidence="high", as_of_date=TODAY, source_id="SRC_INQ_T_0522"),
]

GAPS = [
    dict(id=41, pillar="C", priority=4, retrieval_method="scrape_portal", status="open", opened=TODAY,
         question="Harvest the ~120 submissions to the NSW Legislative Council Inquiry into Data Centres and "
                  "code them by organisation type, position and the specific assertions each makes about "
                  "subsidies, water, jobs and emissions.",
         why_it_matters="The five hearing transcripts are now archived and mined, but the written submissions "
                        "are the larger body of evidence and include the Greenpeace submission already used in "
                        "this database. They are the best free route to closing RG-007, because industry and "
                        "union submissions lobby for or against concessions and so disclose whether they exist.",
         target_source="https://www.parliament.nsw.gov.au/parliamentary-business/committees/"
                       "inquiry-submission-details?committeeInquiryId=3169 - returns HTTP 403 to non-browser "
                       "clients. Individual submission PDFs ARE downloadable from "
                       "files.parliament.nsw.gov.au/fileapi/ParlFiles/GetArtifact?serverRelativeUrl=/lcdocs/"
                       "submissions/<id>/<name>.pdf, as demonstrated by Greenpeace's submission No 120 at "
                       "/lcdocs/submissions/95082/. The blocker is enumerating the list, not fetching the files.",
         notes="Route options: fetch the list through a browser-capable client; probe sequential submission ids "
               "in the 95000-95200 range; or use the hearing schedules, which name organisations. The hearing "
               "schedule PDFs are image-only and yielded no text, so witness lists were recovered from the "
               "transcript appearance formula instead.",
         fact_status="VERIFIED", confidence="high", as_of_date=TODAY, source_id="SRC_INQ_T_0522"),
    dict(id=42, pillar="D", priority=4, retrieval_method="dataset_download", status="open", opened=TODAY,
         question="Obtain IPART's actual position on Sydney Water's 25 per cent data centre water projection, "
                  "and the ABS water accounts figure Data Centres Australia relies on.",
         why_it_matters="Two directly opposed accounts of the same regulator's position are now on the public "
                        "record. DCA says IPART dismissed the 25 per cent figure as unverifiable; Sydney Water's "
                        "Managing Director stands by it. The Observatory currently holds Sydney Water's "
                        "projection as REPORTED/high and DCA's rebuttal as CLAIMED. Whichever way IPART's "
                        "determination reads, one of the two must be reclassified - and this is the single most "
                        "contested number in the whole Australian water debate.",
         target_source="IPART's Sydney Water pricing determination and any related issues paper; the IPART water "
                       "pricing review for data centres commissioned on 17 August 2026; ABS Water Account "
                       "Australia publications",
         fact_status="VERIFIED", confidence="high", as_of_date=TODAY, source_id="SRC_INQ_T_0501"),
    dict(id=43, pillar="B", priority=4, retrieval_method="manual_review", status="open", opened=TODAY,
         question="Test Data Centres Australia's $10.3bn energy infrastructure payment and $1.1bn excess "
                  "capacity figures against network business capital plans and AER prudence assessments.",
         why_it_matters="These are the industry's headline numbers for the 'no net cost to consumers' claim and "
                        "they appear in the inquiry record under parliamentary privilege. Transgrid's own "
                        "published position supports the cost-allocation principle but not the quantum. Either "
                        "the figures reconcile to augmentation commitments under signed connection agreements, "
                        "or they are a projection of a pipeline in which, on Transgrid's evidence of 22 May 2026, "
                        "no data centre had yet committed.",
         target_source="Transgrid, Ausgrid and Endeavour Energy capital expenditure plans; AER regulatory "
                       "proposals and determinations; connection agreement disclosures",
         fact_status="VERIFIED", confidence="high", as_of_date=TODAY, source_id="SRC_INQ_T_0501"),
    dict(id=44, pillar="E", priority=3, retrieval_method="manual_review", status="open", opened=TODAY,
         question="Assess Unions NSW's proposal for local content and apprentice quotas at no less than "
                  "Renewable Energy Sector Board standards, and its warning that a market-based renewable "
                  "funding mechanism would be opaque and would prevent tracking local content.",
         why_it_matters="This is the only quantified workforce-conditionality proposal in the Australian record "
                        "and it maps directly onto the 'conditional equity and utility' replacement the project "
                        "brief proposes. The RESB precedent also means it is already implemented policy in an "
                        "adjacent sector, so the feasibility objection is weak. The opacity warning is a direct "
                        "critique of the NSW Guidelines' PPA portfolio approach and of the proposed REGO "
                        "certificate scheme.",
         target_source="Renewable Energy Sector Board local content requirements; Unions NSW submission to the "
                       "inquiry; NSW Data Centre Guidelines Principle 6",
         fact_status="VERIFIED", confidence="high", as_of_date=TODAY, source_id="SRC_INQ_T_0522"),
]

GAP_UPDATES = [
    dict(match=dict(id=15),
         set=dict(status="in_progress",
                  notes="Substantially advanced 2026-09-18. The terms of reference and all five hearing "
                        "transcripts (1 May, 8 May, 22 May, 29 May, 2 July 2026; 1,121,548 characters) are "
                        "downloaded, archived with SHA-256 manifests, text-extracted with scripts/pdf_text.py "
                        "and mined. 37 witnesses identified. The committee reports by 3 November 2026. RESIDUAL: "
                        "the ~120 written submissions are not harvested because the submissions index page "
                        "returns HTTP 403 to non-browser clients, although individual submission PDFs are "
                        "downloadable from files.parliament.nsw.gov.au - see RG-041. Also note RG-007's "
                        "expectation that the inquiry would settle the tax concession question is only partly "
                        "met: the record contains a firm industry denial under privilege and a committee member "
                        "floating land tax as a REVENUE-RAISING mechanism for community benefit sharing, but no "
                        "revenue officer gave evidence, so the FOI route remains necessary.",
                  fact_status="VERIFIED", confidence="high", as_of_date=TODAY, source_id="SRC_INQ_T_0522"),
         add_sources=["SRC_INQ_TOR", "SRC_INQ_T_0501", "SRC_INQ_T_0508", "SRC_INQ_T_0522",
                      "SRC_INQ_T_0529", "SRC_INQ_T_0702"]),
    dict(match=dict(id=7),
         set=dict(notes="STRATEGY DRAFTED 2026-09-18, not yet lodged - see reports/RG007_foi_strategy.md. Five "
                        "request templates are written for Revenue NSW, NSW DPHI/Investment NSW, SRO Victoria, "
                        "Queensland Revenue Office and Commonwealth Treasury/FIRB, framed to seek policy "
                        "instruments and aggregate counts rather than named taxpayer assessments. UPDATED after "
                        "mining the inquiry record: the hoped-for free answer did NOT materialise. No revenue "
                        "officer gave evidence. What the record does contain is (a) a firm denial under "
                        "parliamentary privilege from Data Centres Australia's CEO on 1 May 2026 that operators "
                        "'do not receive subsidies or tax incentives', and (b) a committee member proposing on "
                        "8 May 2026 that land tax classification be shifted to FUND community benefit sharing - "
                        "the opposite of a concession, with the witness conceding no analysis had been done. The "
                        "terms of reference (g)(iii) expressly requires the committee to examine 'the extent of "
                        "public subsidies, concessions or state directed facilitation provided to the sector', "
                        "and the committee reports by 3 November 2026, so a finding may arrive without FOI. The "
                        "FOI route remains the only way to obtain primary revenue-office records. Free routes "
                        "still worth working first: the VPA register, budget papers, consultation submissions "
                        "and RG-041 (the inquiry's written submissions).",
                  fact_status="VERIFIED", confidence="high", as_of_date=TODAY, source_id="SRC_INQ_T_0501"),
         add_sources=["SRC_INQ_T_0501", "SRC_INQ_T_0508", "SRC_INQ_TOR"]),
]

COMMUNITY_EVENTS = [
    dict(event_date="2026-05-08", locality="Lane Cove", state="NSW", event_type="political_intervention",
         group_id="GRP_LANECOVE", actor="Ms Rochelle Flood, Deputy Mayor, Lane Cove Council", severity=3,
         summary="Lane Cove Council's Deputy Mayor gave evidence to the inquiry on 8 May 2026. The same LGA "
                 "contains five data centre SSD records and a resident population reporting an operating "
                 "facility 350 m from homes.",
         fact_status="VERIFIED", confidence="high", as_of_date=TODAY, source_id="SRC_INQ_T_0508"),
    dict(event_date="2026-05-22", locality="Lane Cove", state="NSW", event_type="political_intervention",
         group_id="GRP_LANECOVE", actor="Mr Peter Ephraums, Lane Cove Responsible Planning Group", severity=3,
         summary="A community planning group gave evidence directly to the inquiry alongside Sydney Water, "
                 "Transgrid, the Premier's Department and Infrastructure NSW.",
         fact_status="VERIFIED", confidence="high", as_of_date=TODAY, source_id="SRC_INQ_T_0522"),
    dict(event_date="2026-05-22", locality="NSW", state="NSW", event_type="political_intervention",
         group_id="GRP_GREENPEACE",
         actor="Ms Solaye Snider and Dr Simon Bradshaw, Greenpeace Australia Pacific; Ms Jaqueline Mills, "
               "Nature Conservation Council of NSW", severity=3,
         summary="Both environmental organisations gave oral evidence on 22 May 2026 in addition to their written "
                 "submissions, in the same session as the water utilities and networks.",
         fact_status="VERIFIED", confidence="high", as_of_date=TODAY, source_id="SRC_INQ_T_0522"),
    dict(event_date="2026-05-29", locality="NSW", state="NSW", event_type="political_intervention",
         actor="Ms Emma Bacon, Executive Director, Sweltering Cities", severity=3,
         summary="Urban heat advocacy evidence on 29 May 2026, relevant to the cumulative microclimate impact "
                 "Blacktown City Council raised in its objection to the 235 MW Glendenning Road consent and to "
                 "the Greater Sydney Heat Smart City Plan 2025-2030.",
         fact_status="VERIFIED", confidence="high", as_of_date=TODAY, source_id="SRC_INQ_T_0529"),
]


def main() -> int:
    pack = {
        "pack_id": "rg015-inquiry-record-2026-09",
        "prepared_by": "scripts/curate_rg015.py (curated from transcripts read 2026-09-18)",
        "prepared_on": TODAY,
        "sources": SOURCES,
        "rows": {
            "entities": ENTITIES,
            "metrics": METRICS,
            "regulatory_events": REG_EVENTS,
            "renewable_claims": CLAIMS,
            "community_events": COMMUNITY_EVENTS,
            "research_gaps": GAPS + GAP_UPDATES,
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
