#!/usr/bin/env python3
"""
Curator for the CONSULTANCY / ADVISORY layer (v2.0.0).

Builds data/packs/consultants_layer.json from:
  * primary procurement notices read on 2026-09-18 (buy.nsw CAN-100812)
  * the GovMarket aggregator supplier record for Tata Consultancy Services
    (the provenance of the figures supplied to the project - recorded as
    REPORTED, not VERIFIED, because it is a commercial aggregator)
  * TCS's own press release on HyperVault / TPG
  * the 20 signed NSW consents already in data/raw/nsw_planning/consents/
  * the 63 NSW planning portal node records already in data/raw/nsw_planning/nodes/

Verification discipline applied here:
  - A figure is VERIFIED only if it was read in a primary government or
    first-party document during this session.
  - A figure taken from GovMarket is REPORTED and names GovMarket as the source.
  - A figure supplied to the project by a user and not yet traced is CLAIMED.
  - Anything that could not be read is GAP.

Run: python3 scripts/curate_consultants.py
"""
from __future__ import annotations

import csv
import glob
import json
import os
import re
from collections import Counter, defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "data", "packs", "consultants_layer.json")
CONSENTS = os.path.join(ROOT, "data", "raw", "nsw_planning", "consents")
NODES = os.path.join(ROOT, "data", "raw", "nsw_planning", "nodes")
ATTACH = os.path.join(ROOT, "exports", "nsw_planning", "nsw_dc_attachment_index.csv")
AS_OF = "2026-09-18"

# ---------------------------------------------------------------------------
# SOURCES
# ---------------------------------------------------------------------------
SOURCES = [
    {
        "id": "SRC_BUYNsw_CAN100812",
        "title": "CW2307478 - Transport Equip Centre of Excellence, Contract Award Notice CAN-100812",
        "publisher": "NSW Government (buy.nsw / eTendering)",
        "url": "https://buy.nsw.gov.au/notices/6BD465F8-5DCF-4433-A0495C518C94EE38",
        "doc_type": "primary_government",
        "published": "2025-07-17",
        "accessed": AS_OF,
        "credibility": "A",
        "notes": (
            "PRIMARY SOURCE, read in full. Agency Transport for NSW. Type CAN, Class 1, Category "
            "'Information and technology'. Description 'Transport Equip Centre of Excellence - "
            "Maintain and Operate Services'. Estimated amount payable inc GST $118,312,700.00. "
            "METHOD OF TENDERING: DIRECT NEGOTIATION. EFFECTIVE DATE 29-MAR-2018. CONTRACT END DATE "
            "30-JUN-2027. PUBLISH DATE 17-JUL-2025. Display until 30-Jun-2027. Supplier TATA "
            "Consultancy Services LTd, ABN 28109981777, ACN 109981777, 76 Berry Street North Sydney "
            "NSW 2060, flagged 'NSW-based business'. Heightened modern slavery due diligence "
            "procurement: No. Agency piggyback clause: No. Assessment criteria listed as Methodology, "
            "Price, Experience, Organisational capacity. Provisions for varying the amount payable: "
            "'Not applicable'. Provisions for renegotiation: 'Not applicable'. Other private sector "
            "entities involved in, with an interest in or benefiting from this contract: 'Not "
            "applicable'. Agency contact Dave Grosvenor, tss.contractdisclosures@transport.nsw.gov.au. "
            "Amendments: 'No amendments have been made to this disclosure'. "
            "THIS NOTICE IS DECISIVE ON TWO POINTS. First, the contract was effective 29 March 2018 "
            "and runs to 30 June 2027 - a 9 year 3 month term - so it is not a July 2025 award. "
            "Second, it was obtained by direct negotiation, not competitive tender."
        ),
    },
    {
        "id": "SRC_GOVMARKET_TCS",
        "title": "Tata Consultancy Services - Government Contracts & Awards (supplier portfolio record)",
        "publisher": "GovMarket (govmarket.com.au) - commercial procurement aggregator",
        "url": "https://govmarket.com.au/supplier/tata-consultancy-services",
        "doc_type": "market_research",
        "published": None,
        "accessed": AS_OF,
        "credibility": "C",
        "notes": (
            "AGGREGATOR, NOT A PRIMARY PORTAL. GovMarket states that it pulls 'tenders and awarded "
            "contracts from government portals around the clock' - AusTender, NSW eTendering, QLD "
            "QTenders, VIC Buying for Victoria, SA/WA/TAS/NT/ACT Tenders, TenderLink, VendorPanel, "
            "Gateway - and is a subscription product ($49.99/month solo). It self-describes its "
            "supplier summary as an 'AI summary - inferred from awarded contracts'. "
            "It consolidates 14 spelling variants of the TCS name into one master entity. "
            "Headline figures as read: total portfolio $352,735,957.18; contracts won 65; latest win "
            "Oct 2025; buyer concentration 79% from Transport for NSW; 2 contracts flagged expiring. "
            "Top 5 buyers: Transport for NSW $278.9M (79%, 15 contracts); Reserve Bank of Australia "
            "$39.9M (11%, 4 contracts); Insurance and Care NSW (icare) $8.5M (2%, 2 contracts); "
            "Department of Customer Service $6.6M (2%, 3 contracts); Melbourne Water $5.3M (1%, 27 "
            "contracts). 20 of the 65 contracts are listed publicly; 45 sit behind the paywall. "
            "Credibility C: the individual figures are plausible and the one tested against a primary "
            "notice ($118,312,700 for the Transport Equipment Centre of Excellence) matched exactly, "
            "but the TOTALS are the aggregator's own arithmetic and are demonstrably inflated by at "
            "least one duplicate record. Every row sourced here is REPORTED, never VERIFIED."
        ),
    },
    {
        "id": "SRC_GOVMARKET_TECOE",
        "title": "Contract record: Operation and Maintenance of Transport Equipment Centre of Excellence",
        "publisher": "GovMarket (govmarket.com.au)",
        "url": "https://govmarket.com.au/contract/operation-and-maintenance-of-transport-equipment-centre-of-excellence-by-tata-consultancy-services",
        "doc_type": "market_research",
        "published": None,
        "accessed": AS_OF,
        "credibility": "C",
        "notes": (
            "READ IN FULL, AND IT CONTRADICTS THE AGGREGATOR'S OWN SUPPLIER LISTING. The supplier "
            "listing dates this contract '29 July 2025'; this record states 'Awarded 29 Mar 2018' and "
            "'9y 3mo term - 92% elapsed', expiring Wed 30 June 2027, value $118,312,700.00, agency "
            "Transport for NSW, category Transport & Logistics. Those dates and that value are "
            "identical to primary notice CAN-100812. It also states 'Larger than 98% of TATA "
            "Consultancy's contracts - ~531x their median win' and, for the buyer relationship, '15 "
            "contracts together, $278.9M awarded, since 2024'. "
            "This is the record that establishes the DOUBLE COUNT: the same $118,312,700 contract "
            "appears twice in the 65-contract / $352.7M portfolio, once sourced from each portal."
        ),
    },
    {
        "id": "SRC_TCS_HYPERVAULT",
        "title": "TCS Secures $1Bn Investment from TPG to Accelerate AI Data Center Business HyperVault",
        "publisher": "Tata Consultancy Services (first-party press release, Mumbai)",
        "url": "https://www.tcs.com/who-we-are/newsroom/press-release/tcs-secures-1bn-investment-from-tpg-accelerate-ai-data-center-business-hypervault",
        "doc_type": "primary_company",
        "published": "2025-11-20",
        "accessed": AS_OF,
        "credibility": "A",
        "notes": (
            "FIRST-PARTY, read in full. Sub-headline: 'HyperVault aims to establish AI data centers "
            "with capacity in excess of a GW and address the growing need for AI-ready data centers'. "
            "Strategic partnership with TPG to support the growth of TCS's AI data center business "
            "HyperVault. Combined commitment up to Rs 18,000 crore over the next few years; TPG to "
            "invest up to Rs 8,820 crore for a final shareholding between 27.5% and 49%, with TCS "
            "retaining majority. TPG's investment is facilitated through TPG Rise Climate and its "
            "Global South Initiative (a strategy launched in partnership with ALTÉRRA) and through "
            "TPG's Asia Real Estate business. Chairman N. Chandrasekaran is quoted on building 'large "
            "GW-scale AI data centers in India'; Jim Coulter (Executive Chairman, TPG; Managing "
            "Partner, TPG Rise Climate) describes data centers as 'a multifaceted asset class' sitting "
            "'at the intersection of green energy infrastructure, technology and real estate'. "
            "HyperVault 'will deliver secure, reliable, large-scale AI-ready infrastructure for "
            "hyperscalers and AI-driven organizations' and 'purpose-built, liquid-cooled data centers "
            "with high rack densities'. States India has about 1.5 GW of data centre capacity expected "
            "to exceed 10 GW by 2030, and that India's data centre market has attracted nearly $94 "
            "billion since 2019. TCS advised by AZB & Partners (legal) and Deloitte Touche Tohmatsu "
            "India LLP (tax); TPG advised by Cyril Amarchand Mangaldas and Latham & Watkins (legal) and "
            "Price Waterhouse & Co. LLP (tax). Subject to conditions precedent and statutory approvals. "
            "TCS profile: BSE 532540, NSE TCS; over 590,000 employees across 55 countries and 202 "
            "service delivery centers; consolidated revenues over US$30bn for FY ended 31 March 2025; "
            "title partner of the TCS Sydney Marathon. "
            "AUSTRALIA IS NOT MENTIONED ANYWHERE IN THIS RELEASE. The build is India-scoped."
        ),
    },
    {
        "id": "SRC_WIKI_BCA_MEMBERS",
        "title": "Business Council of Australia - membership list (as at April 2025)",
        "publisher": "Wikipedia",
        "url": "https://en.wikipedia.org/wiki/Business_Council_of_Australia",
        "doc_type": "other",
        "published": None,
        "accessed": AS_OF,
        "credibility": "C",
        "notes": (
            "SECONDARY. Used only to corroborate a membership claim that the BCA's own /about/ page "
            "could not be re-read this session (it returns a challenge page - see RG-067). The list as "
            "at April 2025 includes Accenture and Tata Consultancy Services among others (Adamantem, "
            "Telstra, TPG Capital, TransGrid, Transurban, Uber, UBS ...). Note that this list places "
            "TPG CAPITAL - the HyperVault investor - in the same peak body as TCS, its investee. "
            "Independently corroborated for TCS by a TCS-hosted LinkedIn post stating 'TCS is a member "
            "of Business Council of Australia and Australia-India CEO Forum'. The BCA's own SRC_BCA_ABOUT "
            "record already in the database notes Accenture among the membership logos. Membership of "
            "both firms is therefore REPORTED from two directions but not confirmed on the BCA's own "
            "current page; graded medium confidence pending RG-067."
        ),
    },
    {
        "id": "SRC_AUSTRADE_MCKAY",
        "title": "Jodi McKay - Australia's Senior Trade and Investment Commissioner for South Asia",
        "publisher": "Austrade (Australian Trade and Investment Commission)",
        "url": "https://www.austrade.gov.au/en/about-austrade/our-team/our-trade-commissioners/jodi-mckay",
        "doc_type": "primary_government",
        "published": None,
        "accessed": AS_OF,
        "credibility": "A",
        "notes": (
            "PRIMARY. Austrade confirms Jodi McKay is Australia's Senior Trade and Investment "
            "Commissioner for South Asia, based in Mumbai. McKay was Leader of the Opposition in the "
            "NSW Parliament and a NSW Cabinet Minister. Her public profiles also describe her as "
            "Director of the Australia-India CEO Forum, and she posts in that capacity about meetings "
            "with 'Australia-India CEO Forum member Tata Consultancy Services'. A separate "
            "Australia-India CEO Forum release records that the Australia India Women's Leadership "
            "Forum 'will be co-chaired by Tata Consultancy Services'. Recorded because it places a "
            "serving Commonwealth trade commissioner and a former NSW Opposition Leader in a "
            "government-convened forum whose member and co-chair is a firm holding substantial "
            "Australian government IT contracts. No improper conduct is alleged or implied; this is "
            "an access map, and it is the kind of overlap the Observatory records rather than leaves "
            "implicit."
        ),
    },
    {
        "id": "SRC_CONSENT_APPLICANTS",
        "title": "Schedule 1 applicant extraction across 20 signed NSW data centre development consents",
        "publisher": "Australian Data Centre Observatory (derived from NSW DPHI signed consents)",
        "url": "https://www.planningportal.nsw.gov.au/major-projects",
        "doc_type": "primary_planning_portal",
        "published": None,
        "accessed": AS_OF,
        "credibility": "A",
        "notes": (
            "DERIVED FROM PRIMARY DOCUMENTS. The Schedule 1 'Applicant' field was parsed from the 20 "
            "signed consent instruments archived at data/raw/nsw_planning/consents/*.txt. 13 of 20 "
            "parsed cleanly; 7 did not because the PDF text extraction splits the label from the value "
            "across lines (RG-065). This pack records what was actually read. "
            "THE MATERIAL FINDING: in 4 of the 13 parsed consents the named Applicant is a CONSULTANCY "
            "or engineering firm rather than the operator - ARUP Pty Ltd (43-61 Turner Road), Cundall "
            "Johnston and Partners Pty Ltd (Davis Road, twice), Lehr Consultants International "
            "(Australia) Pty Ltd (Glendenning Road SSD-73761707, the 235 MW consent that is the "
            "Observatory's most-read instrument). A further 3 name opaque single-purpose vehicles whose "
            "beneficial ownership is not disclosed on the face of the consent: EMKC Cubed Management Pty "
            "Ltd (two consents), HDI SYD1 Property Holdings Limited, and The Trustee for NineZero DC Sub "
            "Trust I. Only 5 of 13 name an identifiable operator: NEXTDC Limited, Goodman Property "
            "Services (Aust) Pty Limited, Canberra Data Centres Pty Ltd, Macquarie Data Centres Pty Ltd, "
            "Equinix Hyperscale 2 (SY10) Pty Limited."
        ),
    },
    {
        "id": "SRC_CONSENT_DELEGATIONS",
        "title": "Delegate signatory, ministerial delegation date and decision date across 20 signed NSW data centre consents",
        "publisher": "Australian Data Centre Observatory (derived from NSW DPHI signed consents)",
        "url": "https://www.planningportal.nsw.gov.au/major-projects",
        "doc_type": "primary_planning_portal",
        "published": None,
        "accessed": AS_OF,
        "credibility": "A",
        "notes": (
            "DERIVED FROM PRIMARY DOCUMENTS. Each consent opens 'As delegate of the Minister for "
            "Planning and Public Spaces under delegation executed on [date], I approve the Development "
            "Application referred to in Schedule 1'. Both the delegation date and the signatory were "
            "extracted. "
            "DELEGATION DATES: 9 March 2022 (11 consents, in three OCR variants), 9 March 2020 (1), "
            "18 AUGUST 2026 (2 - Glendenning Road SSD-73761707 and Project Apollo Macquarie Park), not "
            "parsed (6). "
            "THE 18 AUGUST 2026 DELEGATION IS THE SIGNIFICANT ONE: the NSW Data Centre Guidelines were "
            "published 17 August 2026. A fresh ministerial delegation was executed the following day, "
            "and the two consents issued under it are the first two post-Guidelines decisions in the "
            "sample. Glendenning Road was signed 14 September 2026 by Joanna Bakopanos, A/Director "
            "Industry Assessments, file EF 24/10658. Project Apollo Macquarie Park was signed 2 "
            "September 2026 by Bakopanos acting. Project Pluto was signed 23 July 2026 by Bakopanos "
            "under the older 2022 delegation. "
            "SIGNATORIES PARSED: Joanna Bakopanos (4-5, including one as 'Bakopanos Acting'), Chris "
            "Ritchie (2, plus 2 as 'Ritchie Executive'), Sargeant Executive (1, Roberts Road, 14 July "
            "2020). 10 not parsed. Note the database elsewhere records Glendenning as determined 16 "
            "September 2026; the instrument itself is signed 14 September 2026, and the 16th is "
            "presumed to be the portal publication date. Both are recorded rather than reconciled by "
            "assumption."
        ),
    },
    {
        "id": "SRC_PORTAL_PLANNERS",
        "title": "Case officer (Planner) assignments across 63 NSW data centre planning portal project records",
        "publisher": "NSW Department of Planning, Housing and Infrastructure - planning portal node records",
        "url": "https://www.planningportal.nsw.gov.au/major-projects",
        "doc_type": "primary_planning_portal",
        "published": None,
        "accessed": AS_OF,
        "credibility": "A",
        "notes": (
            "PRIMARY, machine-readable. The field_party_role field on every one of the 63 archived "
            "project node records is 'Planner', and field_party_first_name / field_party_last_name name "
            "the officer. These are the NSW assessment officers, NOT external consultants - an "
            "important distinction, and the reason this data goes into case_handling rather than "
            "consultant_role. "
            "CASELOAD: Shaun Williams 25 of 63 (40%); Patrick Copas 16 (25%); Jeffrey Peng 7 (11%); "
            "Dave Auster 5 (8%); Catriona Shirley 3 (5%); Joanna Bakopanos 2 (3%); David Schwebel, "
            "Chloe Dunlop, Pamela Morales, Thomas Bertwistle and Rasmus Altenkamp 1 each (2%). "
            "Two officers account for 41 of 63 records, 65% of the NSW data centre pipeline. "
            "The portal publishes these names, so this is disclosed accountability rather than a leak."
        ),
    },
    {
        "id": "SRC_ATTACHMENT_CONSULTANTS",
        "title": "Technical appendix authorship signals across 6,866 NSW data centre consent attachments",
        "publisher": "Australian Data Centre Observatory (derived from NSW DPHI attachment index)",
        "url": "https://www.planningportal.nsw.gov.au/major-projects",
        "doc_type": "primary_planning_portal",
        "published": None,
        "accessed": AS_OF,
        "credibility": "B",
        "notes": (
            "DERIVED, FILENAME-LEVEL EVIDENCE ONLY. Attachment filenames were searched for consultancy "
            "names and technical disciplines. Filenames name the author in a minority of cases, so this "
            "is a floor and not a census - RG-073 exists to do it properly by opening the documents. "
            "NAMED FIRMS FOUND: Arup (10 attachments - CFD modelling advice at 1-5 Khartoum Road, and "
            "'appendix-c7-arup-technical-note' x7 at Apollo Place); Aurecon (2 - 'plant and equipment "
            "systems report', Mamre Road campus); WSP (1 - Dicker data warehouse); Renzo Tonin (1 - "
            "'appendix-3-renzo-tonin-response-acoustic-queries', Talavera Road mod 1); Acoustic Logic "
            "(implied, Stack SYD01 Erskine Park); Cundall ('bcs-advice-davis-road-data-centre-cundall'). "
            "DISCIPLINE VOLUMES: acoustic/noise 181 attachments across 17 projects, water 218, "
            "bushfire/heritage 205, traffic/transport 126, geotechnical 56, biodiversity 38, "
            "contamination 13. "
            "PEER REVIEW EXISTS AND IS RARE BUT REAL: 'a14-acoustic-peer-review' (DigiCo SYD1 "
            "expansion), 'peer-review-acoustic-assessment' (Lane Cove West mod 3), "
            "'appendix-b4-acoustic-review-statement' x2 (51 Huntingwood Drive mod 1). Three projects "
            "out of 63 carry an identifiable independent peer review of the acoustic evidence. "
            "REGULATOR DIALOGUE IS VISIBLE IN THE FILENAMES: 'a3-acoustic-response-dphi-scoping-report-"
            "comments' x6 (KC1 Kemps Creek) and 'acoustic-logic-rfi-response-epa-comments' (Stack "
            "SYD01) show consultants responding directly to DPHI SEARS scoping and to EPA comments. "
            "That is the mechanism by which the technical evidence base for a consent is actually set."
        ),
    },
]

# ---------------------------------------------------------------------------
# ENTITIES
# ---------------------------------------------------------------------------
ENTITIES = [
    {
        "id": "ENT_TCS",
        "name": "Tata Consultancy Services Limited",
        "legal_name": "TATA Consultancy Services LTd (Australian branch, ABN 28 109 981 777)",
        "entity_type": "vendor",
        "domicile": "India",
        "hq_country": "IN",
        "website": "tcs.com",
        "notes": (
            "Systems integrator and consultancy. BSE 532540 / NSE TCS. Over 590,000 employees across 55 "
            "countries and 202 service delivery centers; consolidated revenues over US$30bn for the "
            "financial year ended 31 March 2025. Australian operations at 76 Berry Street, North Sydney "
            "NSW 2060, registered ABN 28109981777 / ACN 109981777, and flagged 'NSW-based business' on "
            "the NSW procurement portal, where it self-identifies as supplying IT consultants, cloud "
            "products and support, end user computing, infrastructure and network, MANAGED AND OUTSOURCED "
            "SERVICES, software licensing and support, solution design and development, and "
            "telecommunications (supplier profile 75727, last updated 29 June 2021). Title partner of the "
            "TCS Sydney Marathon. "
            "RELEVANCE TO THIS OBSERVATORY IS THREEFOLD AND UNUSUAL. (1) It is a member of the Business "
            "Council of Australia - the same peak body whose board carries AirTrunk's founder and which "
            "made Submission No 116 to the NSW data centre inquiry. (2) It holds a substantial portfolio "
            "of Australian taxpayer-funded IT contracts, including to agencies that are themselves "
            "actors in this database (Melbourne Water). (3) From 20 November 2025 it is a DATA CENTRE "
            "OPERATOR in its own right through HyperVault, a JV with TPG targeting more than a GW of "
            "liquid-cooled AI capacity for hyperscalers - so it sits on both sides of the sector it is "
            "politically represented in. The HyperVault build is India-scoped; no Australian facility is "
            "announced (RG-076)."
        ),
        "fact_status": "VERIFIED",
        "source_id": "SRC_BUYNsw_CAN100812",
        "confidence": "high",
        "as_of_date": AS_OF,
    },
    {
        "id": "ENT_TCS_HYPERVAULT",
        "name": "HyperVault (TCS AI data centre business)",
        "entity_type": "developer",
        "domicile": "India",
        "hq_country": "IN",
        "notes": (
            "TCS's AI data centre business, announced as a strategic partnership with TPG on 20 November "
            "2025. Target: AI data centres with capacity in excess of a GW, purpose-built and "
            "liquid-cooled, with high rack densities, serving hyperscalers, AI companies, private "
            "enterprises and the public sector. Combined commitment up to Rs 18,000 crore (about "
            "US$2.1bn) over the next few years, funded by equity from TCS and TPG plus debt; TPG to "
            "invest up to Rs 8,820 crore for a final shareholding between 27.5% and 49%, leaving TCS "
            "with the majority. TPG's participation runs through TPG Rise Climate and its Global South "
            "Initiative (launched in partnership with ALTÉRRA) and through TPG's Asia Real Estate "
            "business. Subject to conditions precedent and statutory approvals as at announcement. "
            "Chairman N. Chandrasekaran frames it as building 'large GW-scale AI data centers in India' "
            "and as a step towards making TCS 'the largest AI-led technology services company'. "
            "Recorded in this database because it establishes that a BCA member holding Australian "
            "government IT contracts is also now a hyperscale data centre developer - a convergence the "
            "sector's own peak-body submissions do not disclose. AUSTRALIAN FOOTPRINT: NONE ANNOUNCED."
        ),
        "fact_status": "VERIFIED",
        "source_id": "SRC_TCS_HYPERVAULT",
        "confidence": "high",
        "as_of_date": AS_OF,
    },
    {
        "id": "ENT_TPG",
        "name": "TPG (TPG Capital / TPG Rise Climate)",
        "entity_type": "pe_firm",
        "domicile": "United States",
        "hq_country": "US",
        "website": "tpg.com",
        "notes": (
            "Global alternative asset manager. Investing up to Rs 8,820 crore in TCS's HyperVault for a "
            "final stake of 27.5-49%, through TPG Rise Climate and its Global South Initiative (a "
            "strategy launched in partnership with ALTÉRRA) and through TPG's Asia Real Estate business. "
            "Jim Coulter is Executive Chairman of TPG and a Managing Partner of TPG Rise Climate. TPG "
            "describes data centers as 'a multifaceted asset class' sitting 'at the intersection of green "
            "energy infrastructure, technology and real estate'. "
            "RECORDED FOR TWO REASONS. First, it is the capital behind a new entrant to the hyperscale "
            "data centre market. Second, TPG Capital appears on the Business Council of Australia's "
            "membership list alongside Tata Consultancy Services - so investor and investee are both "
            "members of the same Australian peak body. That is the same structural pattern the "
            "Observatory already records for Blackstone/CPP and AirTrunk: private capital and its "
            "portfolio company inside one room, in a body that submits to parliamentary inquiries about "
            "the sector they are building."
        ),
        "fact_status": "VERIFIED",
        "source_id": "SRC_TCS_HYPERVAULT",
        "confidence": "high",
        "as_of_date": AS_OF,
    },
    {
        "id": "ENT_CUNDALL",
        "name": "Cundall Johnston and Partners Pty Ltd",
        "entity_type": "other",
        "hq_country": "AU",
        "notes": (
            "Engineering consultancy (building services, sustainability, acoustics). Named as the "
            "SCHEDULE 1 APPLICANT on two NSW data centre consents: the Davis Road Data Centre "
            "(SSD-59416728) and the Davis Road Data Centre Mod 1 tree removal correction. An attachment "
            "on the Davis Road project is titled 'bcs-advice-davis-road-data-centre-cundall', indicating "
            "Cundall also authored technical advice on the same project it is the named applicant for. "
            "This is the clearest instance in the sample of a consultancy being the consent holder of "
            "record rather than the operator. Typed 'other' pending a schema change to add a "
            "'consultancy' entity_type (RG-081)."
        ),
        "fact_status": "VERIFIED",
        "source_id": "SRC_CONSENT_APPLICANTS",
        "confidence": "high",
        "as_of_date": AS_OF,
    },
    {
        "id": "ENT_AURECON",
        "name": "Aurecon",
        "entity_type": "other",
        "hq_country": "AU",
        "notes": (
            "Engineering and advisory firm. Named in an attachment filename on the Mamre Road Data Centre "
            "Campus - the largest project in the NSW register at 321 archived attachments - as the author "
            "of 'appendix-d5-plant-and-equipment-systems-report-aurecon'. That appendix is the one that "
            "would specify cooling plant and back-up generation, i.e. the two things the NSW Data Centre "
            "Guidelines of 17 August 2026 regulate most tightly through dPUE and dWUE bands, recycled-water "
            "requirements and generator hour caps. Evidence tier: filename only (RG-073)."
        ),
        "fact_status": "REPORTED", "source_id": "SRC_ATTACHMENT_CONSULTANTS",
        "confidence": "medium", "as_of_date": AS_OF,
    },
    {
        "id": "ENT_WSP",
        "name": "WSP",
        "entity_type": "other",
        "hq_country": "AU",
        "notes": (
            "Global engineering consultancy. Appears once in the attachment index as 'wsp-letter' on the "
            "Dicker data warehouse and distribution centre project. Low evidentiary weight; recorded so "
            "the firm is in the database for future cross-referencing against the regulator-contract "
            "question in RG-074. Evidence tier: filename only (RG-073)."
        ),
        "fact_status": "REPORTED", "source_id": "SRC_ATTACHMENT_CONSULTANTS",
        "confidence": "low", "as_of_date": AS_OF,
    },
    {
        "id": "ENT_RENZO_TONIN",
        "name": "Renzo Tonin Acoustics",
        "entity_type": "other",
        "hq_country": "AU",
        "notes": (
            "Acoustic consultancy. Named in the attachment filename "
            "'appendix-3-renzo-tonin-response-acoustic-queries-22' on the Talavera Road Data Centre "
            "mod 1 expansion - a Macquarie Data Centres campus. Recorded because acoustic evidence is the "
            "single most common technical discipline in the NSW data centre record (181 acoustic and noise "
            "attachments across 17 projects) and is the evidence base for the amenity conditions the "
            "Observatory tracks in Pillar D, yet almost none of its authors are identifiable from the "
            "public index. Evidence tier: filename only (RG-073)."
        ),
        "fact_status": "REPORTED", "source_id": "SRC_ATTACHMENT_CONSULTANTS",
        "confidence": "medium", "as_of_date": AS_OF,
    },
    {
        "id": "ENT_PEER_REVIEW_UNKNOWN",
        "name": "Independent acoustic peer reviewer (identity not established)",
        "entity_type": "other",
        "notes": (
            "PLACEHOLDER ENTITY, deliberately named as unknown. Three NSW data centre projects carry an "
            "identifiable independent peer review of their acoustic evidence - DigiCo SYD1 expansion "
            "('a14-acoustic-peer-review-15'), Lane Cove West mod 3 ('peer-review-acoustic-assessment-25') "
            "and 51 Huntingwood Drive mod 1 ('appendix-b4-acoustic-review-statement-47' and '-48') - but "
            "the reviewing firm is not named in any filename. This entity exists so those three peer "
            "reviews can be recorded as consultant_role rows with fact_status GAP rather than dropped. "
            "Establishing who performs peer review, and whether any firm reviews its own work, is RG-075."
        ),
        "fact_status": "GAP", "source_id": "SRC_ATTACHMENT_CONSULTANTS",
        "confidence": "low", "as_of_date": AS_OF,
    },
    {
        "id": "ENT_GOVMARKET",
        "name": "GovMarket (govmarket.com.au)",
        "entity_type": "other",
        "hq_country": "AU",
        "website": "govmarket.com.au",
        "notes": (
            "Commercial procurement intelligence aggregator and the ACTUAL PROVENANCE of the TCS figures "
            "supplied to this project. Scrapes AusTender, all state portals and TenderLink; claims 1.3 "
            "million historical contracts; subscription $49.99/month solo, $199/month team. Publishes "
            "AI-generated supplier summaries explicitly labelled 'AI summary - inferred from awarded "
            "contracts'. "
            "Recorded as an entity because it is a source in the verification chain and its method has "
            "a measurable defect: it consolidates 14 name variants into one master supplier but does NOT "
            "de-duplicate the same contract when two portals publish it, which inflates portfolio totals "
            "and contract counts. Any figure cited from GovMarket in public debate should be traced to a "
            "portal notice before use. The Observatory's own rule is that aggregator output is REPORTED "
            "at credibility C and never VERIFIED."
        ),
        "fact_status": "VERIFIED",
        "source_id": "SRC_GOVMARKET_TCS",
        "confidence": "high",
        "as_of_date": AS_OF,
    },
    {
        "id": "ENT_TFNSW",
        "name": "Transport for NSW",
        "entity_type": "government_agency",
        "hq_country": "AU",
        "notes": (
            "NSW State government transport agency. The single largest buyer in the tracked TCS "
            "portfolio: $278.9M across 15 records per GovMarket, of which $118.3M is ONE contract - the "
            "Transport Equipment Centre of Excellence, directly negotiated, effective 29 March 2018 to "
            "30 June 2027. Contract disclosure contact tss.contractdisclosures@transport.nsw.gov.au; "
            "address L4/36-46 George Street, Burwood NSW 2134. "
            "Relevant to this Observatory as the largest single instance of an NSW agency holding a "
            "long-duration sole-sourced technology operation contract, which is the pattern the "
            "consultancy layer exists to make visible."
        ),
        "fact_status": "VERIFIED",
        "source_id": "SRC_BUYNsw_CAN100812",
        "confidence": "high",
        "as_of_date": AS_OF,
    },
    {
        "id": "ENT_RBA",
        "name": "Reserve Bank of Australia",
        "entity_type": "government_agency",
        "hq_country": "AU",
        "notes": (
            "Australia's central bank. Second largest buyer in the tracked TCS portfolio at $39.9M across "
            "4 contracts, including CoreMod System Integration for Application Migrations ($14M, "
            "published 30 July 2025) and Professional Services for Cloud Build Capability ($2M, 1 June "
            "2025, flagged as expiring within two months of the aggregator snapshot). "
            "Relevant to the Observatory because CoreMod is a legacy modernisation and cloud migration "
            "programme at the central bank - i.e. demand-side compute and cloud footprint - and because "
            "the RBA is a Commonwealth agency whose own infrastructure decisions bear on national "
            "compute capacity."
        ),
        "fact_status": "REPORTED",
        "source_id": "SRC_GOVMARKET_TCS",
        "confidence": "medium",
        "as_of_date": AS_OF,
    },
    {
        "id": "ENT_MELB_WATER",
        "name": "Melbourne Water",
        "entity_type": "utility",
        "hq_country": "AU",
        "notes": (
            "Victorian statutory water authority - the metropolitan water and drainage authority for "
            "Melbourne, and the relevant recycled-water and stormwater authority for data centre sites in "
            "that market. In the tracked TCS portfolio it is the most CONTRACT-FRAGMENTED buyer: $5.3M "
            "across 27 separate contracts, the highest contract count of any buyer at an average of "
            "about $196k each, covering Citrix upgrades, SolarWinds implementation and support, "
            "Microsoft 365 OneDrive and SharePoint Level 2 infrastructure support, disaster recovery "
            "infrastructure build phase 2, GIS consulting, cyber security project management, network "
            "zone model refinement, and end-of-life hardware replacement. "
            "Doubly relevant here. Melbourne Water is BOTH a TCS client and a water authority whose "
            "counterparts are central to this Observatory's water findings: the NSW Data Centre "
            "Guidelines of 17 August 2026 require 100% recycled water for water-intensive cooling, and "
            "the BCA's Submission No 116 claims recycled water already supplies 55% of AirTrunk's total "
            "water use - a claim the Observatory could not verify and logged as RG-068. Whether any TCS "
            "engagement at Melbourne Water touches recycled-water supply planning for data centres is "
            "open (RG-080)."
        ),
        "fact_status": "REPORTED",
        "source_id": "SRC_GOVMARKET_TCS",
        "confidence": "medium",
        "as_of_date": AS_OF,
    },
    {
        "id": "ENT_ICARE",
        "name": "Insurance and Care NSW (icare)",
        "entity_type": "government_agency",
        "hq_country": "AU",
        "notes": (
            "NSW workers compensation and insurance scheme. Third largest buyer in the tracked TCS "
            "portfolio at $8.5M across 2 contracts. The individual contracts sit behind the aggregator "
            "paywall, so their scope is unknown - recorded as a GAP rather than described."
        ),
        "fact_status": "REPORTED",
        "source_id": "SRC_GOVMARKET_TCS",
        "confidence": "medium",
        "as_of_date": AS_OF,
    },
    {
        "id": "ENT_NSW_DCS",
        "name": "Department of Customer Service (NSW)",
        "entity_type": "government_agency",
        "hq_country": "AU",
        "notes": (
            "NSW Department of Customer Service, which runs Government Shared Services. Fourth largest "
            "buyer in the tracked TCS portfolio at $6.6M across 3 contracts, including 'Office 365 "
            "Environment Setup for MoG GSS' ($189k, published 5 May 2025). NOTE A DISCREPANCY: the "
            "aggregator attributes the O365 contract to the NSW Department of Customer Service, but the "
            "contract title 'MoG GSS' (Machinery of Government, Government Shared Services) and its "
            "publication pattern are consistent with a Commonwealth award, and it was supplied to this "
            "project as 'NSW Department of Customer Service'. The portal of record was not resolved this "
            "session; the attribution is carried as REPORTED at low confidence and flagged for RG-072."
        ),
        "fact_status": "REPORTED",
        "source_id": "SRC_GOVMARKET_TCS",
        "confidence": "low",
        "as_of_date": AS_OF,
    },
    {
        "id": "ENT_AIIA_FORUM",
        "name": "Australia-India CEO Forum",
        "entity_type": "industry_body",
        "hq_country": "AU",
        "notes": (
            "Bilateral government-convened business forum. TCS is a member. The Forum's Director is Jodi "
            "McKay, who is also Australia's Senior Trade and Investment Commissioner for South Asia "
            "(Austrade, Mumbai) and a former NSW Leader of the Opposition and Cabinet Minister. The "
            "Australia India Women's Leadership Forum 'will be co-chaired by Tata Consultancy Services' "
            "per a Forum release. Recorded as an access channel distinct from the BCA: a bilateral "
            "trade body in which a firm holding Australian government IT contracts is a member and a "
            "co-chair, alongside a serving Commonwealth trade commissioner."
        ),
        "fact_status": "REPORTED",
        "source_id": "SRC_AUSTRADE_MCKAY",
        "confidence": "medium",
        "as_of_date": AS_OF,
    },
]

ENTITY_ALIASES = [
    {"entity_id": "ENT_TCS", "alias": "TATA Consultancy Services LTd"},
    {"entity_id": "ENT_TCS", "alias": "Tata Consultancy Services Ltd"},
    {"entity_id": "ENT_TCS", "alias": "TATA CONSULTANCY SERVICES LIMITED"},
    {"entity_id": "ENT_TCS", "alias": "Tata Consultancy Services"},
    {"entity_id": "ENT_TCS", "alias": "TCS"},
    {"entity_id": "ENT_TCS", "alias": "TaTa Consultancy Services Limited"},
    {"entity_id": "ENT_TCS_HYPERVAULT", "alias": "HyperVault"},
    {"entity_id": "ENT_TPG", "alias": "TPG Capital"},
    {"entity_id": "ENT_TPG", "alias": "TPG Rise Climate"},
    {"entity_id": "ENT_TFNSW", "alias": "TfNSW"},
    {"entity_id": "ENT_MELB_WATER", "alias": "Melbourne Water Corporation"},
]

OWNERSHIP = [
    {
        "holder_id": "ENT_TCS", "target_id": "ENT_TCS_HYPERVAULT", "stake_pct": 51.0,
        "instrument": "joint_venture",
        "effective_from": "2025-11-20",
        "event": "HyperVault JV formation with TPG (announced)",
        "notes": ("Instrument is joint_venture per the schema enum; TCS holds the majority. Announced 20 November 2025 as subject to conditions precedent "
                  "and statutory approvals, so the holding is announced rather than completed. TCS states "
                  "HyperVault is funded through a mix of equity from TCS and TPG, and debt."),
        "fact_status": "VERIFIED", "source_id": "SRC_TCS_HYPERVAULT",
        "confidence": "high", "as_of_date": AS_OF,
    },
    {
        "holder_id": "ENT_TPG", "target_id": "ENT_TCS_HYPERVAULT", "stake_pct": 49.0,
        "instrument": "joint_venture",
        "effective_from": "2025-11-20",
        "event": "HyperVault JV formation (announced); TPG to invest up to Rs 8,820 crore of a combined "
                 "commitment of up to Rs 18,000 crore",
        "notes": ("Instrument is joint_venture; the stake range is recorded in stake_pct at its UPPER BOUND. The of the announced range is release gives 27.5-49% and fixes no number. TPG participates through TPG Rise Climate "
                  "and its Global South Initiative (launched in partnership with ALTERRA) and through TPG "
                  "Asia Real Estate. Deal advisers: TCS by AZB & Partners and Deloitte Touche Tohmatsu "
                  "India LLP; TPG by Cyril Amarchand Mangaldas, Latham & Watkins and Price Waterhouse & Co. "
                  "LLP - four of the six being firms that also appear in Australian public procurement."),
        "fact_status": "VERIFIED", "source_id": "SRC_TCS_HYPERVAULT",
        "confidence": "high", "as_of_date": AS_OF,
    },
]

# ---------------------------------------------------------------------------
# GOV CONTRACTS
# ---------------------------------------------------------------------------
# Every row below was read on the GovMarket supplier page on 2026-09-18.
# fact_status REPORTED = aggregator-sourced. The one contract independently
# confirmed against a primary portal notice is VERIFIED and says so.
GM = "SRC_GOVMARKET_TCS"

CONTRACTS = [
    # --- the contract that matters, with its duplicate ---
    dict(supplier="TATA Consultancy Services LTd", agency="Transport for NSW",
         title="CW2307478 - Transport Equip Centre of Excellence (Maintain and Operate Services)",
         value=118312700.00, gst=1, portal="buy.nsw", portal_id="CAN-100812",
         published="2025-07-17", start="2018-03-29", end="2027-06-30",
         method="Direct negotiation", category="Information and technology",
         abn="28109981777",
         src="SRC_BUYNsw_CAN100812",
         vnote=("VERIFIED AGAINST THE PRIMARY NOTICE, read in full. Value inc GST $118,312,700.00; "
                "effective 29-Mar-2018; contract end 30-Jun-2027; published 17-Jul-2025; METHOD OF "
                "TENDERING 'Direct negotiation'; supplier ABN 28109981777 / ACN 109981777 at 76 Berry "
                "Street North Sydney; heightened modern slavery due diligence 'No'; piggyback clause "
                "'No'; variation, renegotiation and other-beneficiary provisions all 'Not applicable'; "
                "'No amendments have been made to this disclosure'. "
                "TERM IS 9 YEARS 3 MONTHS. This is one continuous sole-sourced engagement, not a 2025 "
                "award, and not a new project."),
         status="VERIFIED", conf="high"),
    dict(supplier="TATA Consultancy Services LTd", agency="Transport for NSW",
         title="Operation and Maintenance of Transport Equipment Centre of Excellence",
         value=118312700.00, gst=1, portal="aggregator", portal_id="govmarket/tecoe",
         published="2025-07-29", start="2018-03-29", end="2027-06-30",
         method="Direct negotiation", category="Transport & Logistics",
         dup=True,
         dupnote=("DUPLICATE OF CAN-100812. Identical value to the cent ($118,312,700.00), identical "
                  "award date (GovMarket's own contract record states 'Awarded 29 Mar 2018 - 9y 3mo "
                  "term - 92% elapsed'), identical expiry (Wed 30 June 2027). The supplier listing dates "
                  "it '29 July 2025' while the contract record dates it '29 Mar 2018' - the aggregator "
                  "is internally inconsistent about its own record. This single duplicate inflates the "
                  "published portfolio by $118,312,700 and the contract count by one."),
         vnote=("Excluded from all Observatory totals. Retained as a row precisely so the inflation is "
                "auditable rather than silently corrected. Sourced to the aggregator page because that is "
                "where the SECOND listing of this contract was directly observed; the fact_status is "
                "VERIFIED because the duplication itself was proven by comparing it against primary notice "
                "CAN-100812 - identical value to the cent, identical 29 March 2018 award date, identical "
                "30 June 2027 expiry. What is verified is the duplication, not a new fact about spend."),
         status="VERIFIED", conf="high"),
    # --- TfNSW, other ---
    dict(supplier="TATA CONSULTANCY SERVICES LIMITED", agency="Transport for NSW",
         title="Professional Services Provided to Transport for NSW", value=1100000.0, gst=1,
         portal="aggregator", portal_id="govmarket/tfnsw-ps-2025", published="2025-07-01",
         category="Consultancy & Legal", status="REPORTED", conf="medium"),
    dict(supplier="TATA Consultancy Services LTd", agency="Transport for NSW",
         title="Defect Fix Services for OneStream Solution", value=1100000.0, gst=1,
         portal="aggregator", portal_id="govmarket/onestream-defect", published="2024-12-19",
         category="IT & Software", status="REPORTED", conf="medium"),
    dict(supplier="TATA Consultancy Services Ltd", agency="Transport for NSW",
         title="Professional Services for OneStream Solution", value=350000.0, gst=1,
         portal="aggregator", portal_id="govmarket/onestream-ps", published="2024-12-18",
         category="IT & Software", status="REPORTED", conf="medium"),
    dict(supplier="TATA Consultancy Services LTd", agency="Transport for NSW",
         title="Professional Services for OneStream Solution (second award)", value=285000.0, gst=1,
         portal="aggregator", portal_id="govmarket/onestream-ps2", published="2024-12-17",
         category="IT & Software", status="REPORTED", conf="medium",
         vnote=("Three OneStream awards on three consecutive days in December 2024 totalling "
                "$1,735,000. The user-supplied brief described these as 'multiple contracts totalling "
                "roughly AUD $1.7 million', which matches. Whether three same-title awards on "
                "consecutive days are three scopes or one scope split across notices is unresolved "
                "(RG-072).")),
    dict(supplier="Tata Consultancy Services", agency="Transport for NSW",
         title="Azure EiPaaS Platform Services", value=829000.0, gst=1,
         portal="aggregator", portal_id="govmarket/azure-eipaas", published="2024-08-20",
         category="IT & Software", status="REPORTED", conf="medium"),
    dict(supplier="Tata Consultancy Services", agency="Transport for NSW",
         title="SAP Fiori Forms Delivery Services", value=570000.0, gst=1,
         portal="aggregator", portal_id="govmarket/sap-fiori", published="2024-07-29",
         category="IT & Software", status="REPORTED", conf="medium"),
    # --- RBA ---
    dict(supplier="Tata Consultancy Services Limited", agency="Reserve Bank of Australia",
         title="CoreMod System Integration for Application Migrations", value=14000000.0, gst=1,
         portal="aggregator", portal_id="govmarket/rba-coremod", published="2025-07-30",
         category="IT & Software", status="REPORTED", conf="medium",
         vnote=("Second largest single award in the portfolio. The user-supplied brief dated this "
                "'July 2025'; the aggregator dates publication 30 July 2025. AusTender record of primary "
                "not yet read (RG-072).")),
    dict(supplier="Tata Consultancy Services", agency="Reserve Bank of Australia",
         title="Professional Services for Cloud Build Capability", value=2000000.0, gst=1,
         portal="aggregator", portal_id="govmarket/rba-cloud", published="2025-06-01",
         category="IT & Software", status="REPORTED", conf="medium",
         vnote="Flagged by the aggregator as expiring within two months of the snapshot - i.e. a live recompete."),
    # --- other agencies ---
    dict(supplier="Tata Consultancy Services", agency="Department of Defence",
         title="Industry Benchmarking Services", value=1100000.0, gst=1,
         portal="aggregator", portal_id="govmarket/defence-benchmark", published="2025-05-05",
         category="Consultancy & Legal", status="REPORTED", conf="medium"),
    dict(supplier="Tata Consultancy Services", agency="Department of Customer Service",
         title="Office 365 Environment Setup for MoG GSS", value=189000.0, gst=1,
         portal="aggregator", portal_id="govmarket/o365-mog", published="2025-05-05",
         category="IT & Software", status="REPORTED", conf="low",
         vnote=("AGENCY ATTRIBUTION UNRESOLVED. GovMarket attributes this to the NSW Department of "
                "Customer Service; 'MoG GSS' denotes Machinery-of-Government change affecting Government "
                "Shared Services, and the award pattern is consistent with a Commonwealth publication. "
                "Carried at low confidence; resolve via RG-072.")),
    dict(supplier="Tata Consultancy Services", agency="Department of the Prime Minister and Cabinet",
         title="ICT Contractor Services", value=135000.0, gst=1,
         portal="aggregator", portal_id="govmarket/pmc-ict", published="2025-02-16",
         category="IT & Software", status="REPORTED", conf="medium",
         vnote=("Notable because PM&C now houses the Office of AI, which is the Commonwealth body "
                "coordinating data centre policy and which flagged national AI Standard legislation for "
                "early 2027.")),
    dict(supplier="Tata Consultancy Services", agency="NSW Electoral Commission",
         title="Software Licensing", value=239000.0, gst=1,
         portal="aggregator", portal_id="govmarket/nswec-lic", published=None,
         category="IT & Software", status="REPORTED", conf="medium",
         vnote="Flagged by the aggregator as expiring within four months of the snapshot."),
    # --- Melbourne Water, the 27-contract tail (all publicly listed ones) ---
    dict(supplier="Tata Consultancy Services", agency="Melbourne Water",
         title="M365 OneDrive and SharePoint Platform Level 2 Infrastructure Support",
         value=192000.0, gst=1, portal="aggregator", portal_id="govmarket/mw-m365",
         published="2024-11-30", category="IT & Software", status="REPORTED", conf="medium"),
    dict(supplier="Tata Consultancy Services", agency="Melbourne Water",
         title="SolarWinds Phase 2 Implementation", value=157000.0, gst=1,
         portal="aggregator", portal_id="govmarket/mw-solarwinds2", published="2024-11-24",
         category="IT & Software", status="REPORTED", conf="medium"),
    dict(supplier="Tata Consultancy Services", agency="Melbourne Water",
         title="Project Manager for Network Zone Model Refinement Project", value=135000.0, gst=1,
         portal="aggregator", portal_id="govmarket/mw-netzone", published="2024-11-05",
         category="IT & Software", status="REPORTED", conf="medium"),
    dict(supplier="Tata Consultancy Services", agency="Melbourne Water",
         title="Project Manager Services for Cyber Security Initiatives", value=140000.0, gst=1,
         portal="aggregator", portal_id="govmarket/mw-cyberpm", published="2024-11-03",
         category="IT & Software", status="REPORTED", conf="medium"),
    dict(supplier="Tata Consultancy Services", agency="Melbourne Water",
         title="DR Infra Build - Phase 2", value=289000.0, gst=1,
         portal="aggregator", portal_id="govmarket/mw-dr2", published="2024-10-22",
         category="IT & Software", status="REPORTED", conf="medium",
         vnote=("Disaster recovery infrastructure build. Recorded because DR architecture is a "
                "data-centre-adjacent scope: it implies secondary site capacity.")),
    dict(supplier="Tata Consultancy Services", agency="Melbourne Water",
         title="Citrix Upgrade", value=209000.0, gst=1,
         portal="aggregator", portal_id="govmarket/mw-citrix", published="2024-10-08",
         category="IT & Software", status="REPORTED", conf="medium"),
    dict(supplier="Tata Consultancy Services", agency="Melbourne Water",
         title="SolarWinds and ServiceNow Tools Support", value=370000.0, gst=1,
         portal="aggregator", portal_id="govmarket/mw-solarwinds-sn", published="2024-08-31",
         category="IT & Software", status="REPORTED", conf="medium"),
    dict(supplier="Tata Consultancy Services", agency="Melbourne Water",
         title="End-of-Life Hardware Replacement", value=105000.0, gst=1,
         portal="aggregator", portal_id="govmarket/mw-eol", published="2024-07-04",
         category="IT & Software", status="REPORTED", conf="medium"),
    dict(supplier="Tata Consultancy Services", agency="Melbourne Water",
         title="GIS Consultant T&M Engagement", value=197000.0, gst=1,
         portal="aggregator", portal_id="govmarket/mw-gis", published="2024-06-30",
         category="Consultancy & Legal", status="REPORTED", conf="medium",
         vnote="Time-and-materials. The only engagement in the visible set explicitly priced by time."),
]

# Buyer aggregates exactly as published by the aggregator, recorded separately so
# that the inflated headline is auditable and never silently laundered.
BUYER_AGGREGATES = [
    ("Transport for NSW", 278900000.0, 15, 79),
    ("Reserve Bank of Australia", 39900000.0, 4, 11),
    ("Insurance and Care NSW (icare)", 8500000.0, 2, 2),
    ("Department of Customer Service", 6600000.0, 3, 2),
    ("Melbourne Water", 5300000.0, 27, 1),
]

# ---------------------------------------------------------------------------
# CONSULTANCY PROFILES
# ---------------------------------------------------------------------------
PROFILES = [
    dict(entity_id="ENT_TCS", firm_type="systems_integrator",
         role_in_pipeline="government_contractor", peak_body_member="BCA",
         on_peak_body_board=0, also_an_operator=1,
         operator_vehicle="HyperVault - JV with TPG, >1 GW liquid-cooled AI capacity (India)",
         exposure=234423257.18, exposure_as_of="2026-09-18",
         exposure_tier="aggregator",
         offshore=("Over 590,000 employees across 55 countries and 202 service delivery centers "
                   "(TCS's own figures), which is the delivery model the user brief characterises as "
                   "'offshore-heavy'. The Australian entity is registered at 76 Berry Street, North "
                   "Sydney and flagged 'NSW-based business' on the NSW portal. The onshore/offshore "
                   "SPLIT for these specific contracts is not disclosed on any notice read; asserting "
                   "it would be unsupported (RG-072)."),
         notes=("THE CENTRAL CASE IN THIS LAYER, and the reason the layer exists. TCS is simultaneously "
                "(a) a member of the Business Council of Australia - the peak body whose board includes "
                "AirTrunk's founder and which made Submission No 116 to the NSW data centre inquiry "
                "arguing that operators 'pay full taxes with no concessions'; (b) a holder of at least "
                "$234.4M in distinct Australian taxpayer-funded contracts (the widely quoted $352.7M "
                "figure double-counts one $118.3M contract); and (c) from 20 November 2025 a hyperscale "
                "DATA CENTRE OPERATOR through HyperVault, backed by TPG - itself a BCA member. "
                "A firm that is politically represented in the room where data centre policy is "
                "negotiated, is paid by the agencies affected by that policy, and is building the "
                "infrastructure the policy governs, is a structural conflict of position rather than "
                "any allegation of misconduct. Nothing here suggests impropriety. It does mean the BCA's "
                "'no concessions' submission was made by a body whose membership includes both a data "
                "centre operator and a data centre developer. "
                "EXPOSURE FIGURE: $234,423,257.18 is the Observatory's de-duplicated figure, being the "
                "aggregator's published $352,735,957.18 less the one confirmed $118,312,700 duplicate. "
                "45 of the 65 records are paywalled, so further duplicates cannot be excluded and this "
                "figure is a CEILING on distinct spend, not a floor."),
         status="VERIFIED", conf="high"),
    dict(entity_id="ENT_ARUP", firm_type="engineering",
         role_in_pipeline="named_applicant", peak_body_member=None,
         on_peak_body_board=0, also_an_operator=0,
         notes=("Global engineering consultancy. Appears in this database in TWO distinct capacities, "
                "which is the point of separating consultant_role from entities. (1) NAMED APPLICANT: "
                "Schedule 1 of the consent for 43-61 Turner Road Data Centre (SSD-68013714, Camden) "
                "names ARUP Pty Ltd as the Applicant - the consent holder of record is the engineering "
                "consultancy, not the operator. That consent carries 74 MW of installed back-up "
                "generation, a 200 hour per year cap, a 2,000 tonne diesel cap, and is one of only two "
                "in the sample referencing a Tier standard. (2) TECHNICAL AUTHOR: Arup authored the CFD "
                "modelling advice attached to a DIFFERENT project, 1-5 Khartoum Road Data Centre "
                "('attachment-c-arup-summary-advice-cfd-modelling', plus two variants and an RFI "
                "response 'response-rficfd17dec2025-final'), and seven numbered technical notes at "
                "Apollo Place Data Centre ('appendix-c7-arup-technical-note' 206-212). "
                "CFD modelling is the evidence that determines thermal plume dispersion and heat "
                "rejection impact on neighbouring residences - it is the technical basis for the "
                "community-amenity conditions this Observatory tracks in Pillar D. That a firm can be "
                "the consent holder on one project and the CFD author on another is not a conflict in "
                "itself, but it does mean the same organisation appears on both the proponent and "
                "evidence sides of the NSW pipeline. Whether Arup ever peer-reviews its own CFD output "
                "on a given project is open (RG-075)."),
         status="VERIFIED", conf="high"),
    dict(entity_id="ENT_LEHR", firm_type="planning_consultant",
         role_in_pipeline="named_applicant", peak_body_member=None,
         on_peak_body_board=0, also_an_operator=0,
         notes=("Planning, engineering and environment consultancy. THE MOST CONSEQUENTIAL NAMED "
                "APPLICANT IN THE SAMPLE: Schedule 1 of the signed Development Consent SSD-73761707 for "
                "the 235 MW Glendenning Road Data Centre names Lehr Consultants International (Australia) "
                "Pty Ltd as the Applicant, with the Minister for Planning and Public Spaces as Consent "
                "Authority. Lehr is also named as the proponent in the NSW Investment Delivery Authority "
                "Round 1 release. ABR search returns 'LEHR CONSULTANTS INTERNA...' at ABN 92 124 107 973 "
                "among 20 matches. "
                "This matters because Glendenning is the Observatory's benchmark post-Guidelines consent: "
                "all-times additional firmed renewable matching, NOx under 10 tonnes per year excluding "
                "outages, 45 metre stacks, a 170 hour generator cap (the first departure from the "
                "Department's 200 hour template), and 267.45 MW of installed back-up against a 235 MW "
                "load cap. The instrument that imposes those conditions names an acoustics and planning "
                "consultancy as the applicant, so the operator is not identifiable from the face of the "
                "consent. Signed 14 September 2026 by Joanna Bakopanos, A/Director Industry Assessments, "
                "as delegate of the Minister under a delegation executed 18 August 2026 - one day after "
                "the Guidelines were published."),
         status="VERIFIED", conf="high"),
    dict(entity_id="ENT_CUNDALL", firm_type="engineering",
         role_in_pipeline="named_applicant", peak_body_member=None,
         on_peak_body_board=0, also_an_operator=0,
         notes=("Building services and sustainability engineering consultancy. Named as the Schedule 1 "
                "APPLICANT on TWO consents: Davis Road Data Centre (SSD-59416728) and Davis Road Data "
                "Centre Mod 1 (tree removal correction). An attachment on the Davis Road project is "
                "titled 'bcs-advice-davis-road-data-centre-cundall', so Cundall appears both as the "
                "named applicant and as the author of technical advice on the same project. "
                "Cundall's discipline - building services, HVAC, sustainability - is directly the "
                "domain of the dPUE and dWUE bands the NSW Guidelines now impose (dPUE at or below "
                "1.25/1.3 with water-use bands), which makes its appearance as consent holder notable "
                "rather than incidental."),
         status="VERIFIED", conf="high"),
    dict(entity_id="ENT_EMKC", firm_type=None, role_in_pipeline="named_applicant",
         peak_body_member=None, on_peak_body_board=0, also_an_operator=0,
         notes=("Opaque special purpose vehicle and the named Schedule 1 APPLICANT on TWO consents: "
                "51 Huntingwood Drive Data Centre (SSD-41589232, Blacktown, 632 MW of installed back-up "
                "generation, 200 hour per year cap) and Apollo Place Data Centre (SSD-67407231, Lane "
                "Cove, 63.8 MW installed back-up against a 45 MW total power cap). One undisclosed SPV "
                "is therefore the consent holder for two facilities in the two corridors with the most "
                "concentrated data centre development in NSW. Beneficial ownership unresolved - RG-064, extended by RG-081. "
                "The 'EMKC' prefix is not a recognisable Australian operator brand, and Apollo Place "
                "carries seven Arup technical notes as appendices, so the consultancy relationship is "
                "visible even where the ownership is not."),
         status="VERIFIED", conf="medium"),
    dict(entity_id="ENT_HDI_SYD1", firm_type=None, role_in_pipeline="named_applicant",
         peak_body_member=None, on_peak_body_board=0, also_an_operator=0,
         notes=("Dedicated per-site property holding company and the named Schedule 1 APPLICANT for the "
                "DigiCo SYD1 Data Centre Expansion (SSD-69637456, City of Sydney) - 140.4 MW of "
                "installed back-up generation, a 2,000 tonne diesel cap, and one of only four consents "
                "carrying that combination. The 'DigiCo' project name and the 'HDI SYD1 Property "
                "Holdings' applicant name do not match, so the operator behind the vehicle is not "
                "identifiable from the consent. This project also carries the sample's clearest "
                "independent check: an attachment titled 'a14-acoustic-peer-review'. Ownership "
                "unresolved - RG-064."),
         status="VERIFIED", conf="medium"),
    dict(entity_id="ENT_NINEZERO", firm_type=None, role_in_pipeline="named_applicant",
         peak_body_member=None, on_peak_body_board=0, also_an_operator=0,
         notes=("Trust trustee and the named Schedule 1 APPLICANT for the DCI Poplars Data Centre "
                "Project (Queanbeyan-Palerang Regional). The 'Sub Trust I' formulation implies a trust "
                "series holding multiple sites in separate bankruptcy-remote vehicles - a standard "
                "structured-finance pattern, and the same architecture the Observatory tracks for the "
                "KNBDC trust stack. The 'NineZero' element suggests a net-zero branding position, which "
                "is worth testing against a consent that contains NO renewable procurement condition at "
                "all (RG-059). Ownership unresolved - RG-064, extended by RG-081."),
         status="VERIFIED", conf="medium"),
    dict(entity_id="ENT_TPG", firm_type="economic_consulting", role_in_pipeline="operator_advisor",
         peak_body_member="BCA", on_peak_body_board=0, also_an_operator=1,
         operator_vehicle="HyperVault (27.5-49% stake, with TCS)",
         notes=("Recorded in the consultancy layer because TPG is a BCA member and, through HyperVault, "
                "a data centre developer. The firm_type value is a poor fit - the schema's enum has no "
                "'investor' option for this table and TPG is already correctly typed as pe_firm in "
                "entities; the profile row exists to carry the peak_body_member and also_an_operator "
                "flags. See RG-082 for the enum fix."),
         status="REPORTED", conf="medium"),
]

# ---------------------------------------------------------------------------
# CONSULTANT ROLES (from consents + attachments)
# ---------------------------------------------------------------------------
ROLES = []
NAMED_APPLICANTS = {
    "43_61_turner_road_data_centre": ("ENT_ARUP", "ARUP Pty Ltd", "SSD-68013714", None),
    "51_huntingwood_drive_data_centre": ("ENT_EMKC", "EMKC Cubed Management Pty Ltd", "SSD-41589232", None),
    "apollo_place_data_centre": ("ENT_EMKC", "EMKC Cubed Management Pty Ltd", "SSD-67407231", None),
    "davis_rd_data_centre_mod_1_tree_removal_corr": ("ENT_CUNDALL", "Cundall Johnston and Partners Pty Ltd", None, None),
    "davis_road_data_centre_cundall": ("ENT_CUNDALL", "Cundall Johnston and Partners Pty Ltd", "SSD-59416728", None),
    "digico_syd1_data_centre_expansion": ("ENT_HDI_SYD1", "HDI SYD1 Property Holdings Limited", "SSD-69637456", None),
    "glendenning_road_data_centre": ("ENT_LEHR", "Lehr Consultants International (Australia) Pty Ltd", "SSD-73761707", None),
    "dci_poplars_data_centre_project_0": ("ENT_NINEZERO", "The Trustee for NineZero DC Sub Trust I", None, None),
    "grand_avenue_data_centre_expansion_rosehill": ("ENT_EQUINIX_SY10", "Equinix Hyperscale 2 (SY10) Pty Limited", None, "Equinix"),
    "nextdc_s4_data_centre_horsley_park": ("ENT_NEXTDC", "NEXTDC Limited", None, "NEXTDC"),
    "project_apollo_data_centre_macquarie_park": ("ENT_GOODMAN", "Goodman Property Services (Aust) Pty Limited", None, "Goodman"),
    "roberts_road_data_centre": ("ENT_CDC", "Canberra Data Centres Pty Ltd", "SSD-10330", "CDC"),
    "talavera_road_data_centre_campus_expansion": ("ENT_MACQUARIE_DC", "Macquarie Data Centres Pty Ltd", None, "Macquarie Data Centres"),
}
for slug, (eid, name, case, proponent) in NAMED_APPLICANTS.items():
    is_consult = eid in ("ENT_ARUP", "ENT_LEHR", "ENT_CUNDALL")
    is_spv = eid in ("ENT_EMKC", "ENT_HDI_SYD1", "ENT_NINEZERO")
    ROLES.append(dict(
        project_slug=slug.replace("_", "-"), case_id=case, entity_id=eid,
        role="named_applicant",
        evidence_document=f"Schedule 1, signed Development Consent ({slug}.txt)",
        is_named_applicant=1,
        true_proponent=proponent,
        proponent_known=1 if proponent else 0,
        notes=(
            f"Schedule 1 of the signed consent names {name} as the Applicant. "
            + ("The named applicant is a CONSULTANCY, so the operator is not identifiable from the face "
               "of the consent." if is_consult else
               "The named applicant is an opaque single-purpose vehicle or trust trustee whose beneficial "
               "ownership is not disclosed on the consent (RG-064 / RG-081)." if is_spv else
               "The named applicant is the identifiable operator.")
        ),
        fact_status="VERIFIED", source_id="SRC_CONSENT_APPLICANTS",
        confidence="high" if proponent or is_consult else "medium", as_of_date=AS_OF,
    ))

# Technical authorship inferred from attachment filenames (evidence tier: filename).
ATTACH_ROLES = [
    ("1-5-khartoum-road-data-centre", "ENT_ARUP", "cfd_modelling",
     "attachment-c-arup-summary-advice-cfd-modelling-7; attachmentc-arupsummaryadviceoncfdmodelling-14; -15; response-rficfd17dec2025-final-2",
     "CFD (computational fluid dynamics) modelling advice, plus a December 2025 RFI response. CFD is the "
     "evidence base for thermal plume dispersion and heat rejection impact on neighbouring land uses."),
    ("apollo-place-data-centre", "ENT_ARUP", "other",
     "appendix-c7-arup-technical-note-206 through -212 (7 notes)",
     "Seven sequentially numbered Arup technical notes as EIS appendices on the project whose Schedule 1 "
     "applicant is the EMKC Cubed Management SPV."),
    ("mamre-road-data-centre-campus", "ENT_AURECON", "other",
     "appendix-d5-plant-and-equipment-systems-report-aurecon; -0",
     "Plant and equipment systems report. This is the appendix that would specify cooling plant and "
     "back-up generation - the two things the NSW Guidelines now regulate most tightly. Mamre Road is the "
     "largest campus in the NSW register at 321 archived attachments."),
    ("dicker-data-warehouse-and-distribution-centre", "ENT_WSP", "other", "wsp-letter",
     "Single WSP letter. Low evidentiary weight; recorded for completeness."),
    ("talavera-road-data-centre-mod-1-expansion", "ENT_RENZO_TONIN", "acoustic_consultant",
     "appendix-3-renzo-tonin-response-acoustic-queries-22",
     "Renzo Tonin Acoustics responding to acoustic queries on a Macquarie Data Centres campus expansion."),
    ("davis-road-data-centre-cundall", "ENT_CUNDALL", "other",
     "bcs-advice-davis-road-data-centrecundall-8",
     "Technical advice authored on the same project for which Cundall is the Schedule 1 named applicant."),
    # peer reviews - recorded as a distinct role because independent checking is the control
    ("digico-syd1-data-centre-expansion", "ENT_PEER_REVIEW_UNKNOWN", "peer_reviewer",
     "a14-acoustic-peer-review-15",
     "INDEPENDENT PEER REVIEW of the acoustic assessment. One of only three identifiable peer reviews "
     "across 63 projects. The reviewing firm is not named in the filename."),
    ("lane-cove-west-data-centre-mod-3-design-changes", "ENT_PEER_REVIEW_UNKNOWN", "peer_reviewer",
     "peer-review-acoustic-assessment-25 (alongside appendix-d9-acoustic-assessment-105/-106 and appendix-4-acoustic-assessment-24)",
     "Peer review of the acoustic assessment, on a project carrying three separate acoustic assessments."),
    ("modification-1-51-huntingwood-drive-data-centre-reduced-scale", "ENT_PEER_REVIEW_UNKNOWN", "peer_reviewer",
     "appendix-b4-acoustic-review-statement-47; -48",
     "Two acoustic review statements on the modification that REDUCED the scale of the 632 MW-back-up "
     "Huntingwood Drive facility."),
]
for slug, eid, role, doc, note in ATTACH_ROLES:
    ROLES.append(dict(
        project_slug=slug, case_id=None, entity_id=eid, role=role,
        evidence_document=doc, is_named_applicant=0, proponent_known=0,
        notes=note + (" Evidence tier: ATTACHMENT FILENAME only - the document itself was not opened, so "
                      "authorship is inferred from the filename and graded accordingly (RG-073)."
                      if role != "peer_reviewer" else
                      " Evidence tier: ATTACHMENT FILENAME only (RG-073)."),
        fact_status="REPORTED", source_id="SRC_ATTACHMENT_CONSULTANTS",
        confidence="medium", as_of_date=AS_OF,
    ))

# ---------------------------------------------------------------------------
# CASE HANDLING : planners and delegate signatories
# ---------------------------------------------------------------------------
PLANNER_FILE = os.path.join(ROOT, "data", "raw", "nsw_planning", "planner_assignments.json")
CASE_HANDLING = []
if os.path.exists(PLANNER_FILE):
    for slug, (nm, case, site) in json.load(open(PLANNER_FILE)).items():
        CASE_HANDLING.append(dict(
            case_id=case or f"(unparsed){slug}", project_slug=slug,
            officer_name=nm, officer_role="case_planner", acting=0,
            notes=("Named as 'Planner' in field_party_role on the NSW planning portal node record. These "
                   "are NSW assessment officers, not external consultants."),
            fact_status="VERIFIED", source_id="SRC_PORTAL_PLANNERS",
            confidence="high", as_of_date=AS_OF,
        ))

SIGNATORIES = [
    ("glendenning-road-data-centre", "SSD-73761707", "Joanna Bakopanos", "acting_director", 1,
     "Minister for Planning and Public Spaces", "2026-08-18", "2026-09-14", "EF 24/10658",
     "Signed 'Joanna Bakopanos, A/Director, Industry Assessments, Sydney, 14 September 2026'. The "
     "instrument recites approval 'As delegate of the Minister for Planning and Public Spaces under "
     "delegation executed on 18 August 2026' - ONE DAY AFTER the NSW Data Centre Guidelines were "
     "published on 17 August 2026. This is the Observatory's benchmark post-Guidelines consent. Note "
     "the database elsewhere records the determination as 16 September 2026; the instrument is signed "
     "14 September, and the 16th is presumed to be portal publication. Both are kept."),
    ("project-apollo-data-centre-macquarie-park", "(unparsed)", "Joanna Bakopanos", "acting_director", 1,
     "Minister for Planning and Public Spaces", "2026-08-18", "2026-09-02", None,
     "Second of only two consents in the sample issued under the 18 August 2026 delegation, and therefore "
     "the second post-Guidelines decision. Signed by Bakopanos acting. Schedule 1 applicant is Goodman "
     "Property Services (Aust) Pty Limited."),
    ("project-pluto-data-centre", "(unparsed)", "Joanna Bakopanos", "delegate_signatory", 0,
     "Minister for Planning and Public Spaces", "2022-03-09", "2026-07-23", None,
     "Decided 23 July 2026 but under the 9 March 2022 delegation - i.e. BEFORE the Guidelines and before "
     "the fresh delegation. Useful as the control case: a mid-2026 decision made on pre-Guidelines "
     "instrumentation."),
    ("roberts-road-data-centre", "SSD-10330", "Sargeant", "delegate_signatory", 0,
     "Minister for Planning and Public Spaces", "2020-03-09", "2020-07-14", None,
     "Oldest decision in the sample. This is the project record that also carries the only political "
     "donation disclosure found anywhere in the 63-project register (RG-069)."),
]
for slug, case, nm, role, acting, ca, dele, dec, fileref, note in SIGNATORIES:
    CASE_HANDLING.append(dict(
        case_id=case, project_slug=slug, officer_name=nm, officer_role=role, acting=acting,
        consent_authority=ca, delegation_date=dele, decision_date=dec, file_reference=fileref,
        notes=note, fact_status="VERIFIED", source_id="SRC_CONSENT_DELEGATIONS",
        confidence="high", as_of_date=AS_OF,
    ))
for slug, nm in [("51-huntingwood-drive-data-centre", "Chris Ritchie"),
                 ("station-road-data-centre-expansion", "Chris Ritchie"),
                 ("digico-syd1-data-centre-expansion", "Chris Ritchie"),
                 ("nextdc-s4-data-centre-horsley-park", "Chris Ritchie")]:
    CASE_HANDLING.append(dict(
        case_id="(unparsed)", project_slug=slug, officer_name=nm,
        officer_role="delegate_signatory", acting=0,
        consent_authority="Minister for Planning and Public Spaces",
        delegation_date="2022-03-09",
        notes=("Signatory name recovered from the consent text; the surrounding title line extracted as "
               "'Ritchie Executive' on two records, so the exact office title was not cleanly parsed. "
               "Recorded at medium confidence rather than inferred."),
        fact_status="REPORTED", source_id="SRC_CONSENT_DELEGATIONS",
        confidence="medium", as_of_date=AS_OF,
    ))

# ---------------------------------------------------------------------------
# LOBBYING / INFLUENCE
# ---------------------------------------------------------------------------
LOBBYING = [
    dict(actor_id="ENT_TCS", channel="peak_body_membership",
         recipient="Business Council of Australia", event_date="2025-04",
         instrument="BCA membership list (as at April 2025)",
         position=("Membership of Australia's principal general business peak body - the same body whose "
                   "board includes AirTrunk founder and CEO Robin Khuda alongside the CEOs of Telstra, "
                   "Commonwealth Bank, Wesfarmers, Google Australia and New Zealand and BHP Australia, "
                   "and which made Submission No 116 to the NSW Legislative Council inquiry into data "
                   "centres on 2 April 2026."),
         outcome=("Current as at the April 2025 membership list. Corroborated by a TCS-hosted LinkedIn "
                  "post stating 'TCS is a member of Business Council of Australia and Australia-India "
                  "CEO Forum'. The BCA's own /about/ page could not be re-read this session (challenge "
                  "page, RG-067), so membership is REPORTED from two secondary directions rather than "
                  "confirmed first-hand. ACCENTURE ALSO APPEARS ON THE SAME LIST, so at least two global "
                  "systems integrators sit inside the peak body that submitted to the data centre inquiry."),
         notes=("This is the row that connects the consultancy layer to the influence layer already in the "
                "database. Its significance is compositional: the BCA's Submission No 116 asserted that "
                "'datacentre operators in Australia pay full taxes with no concessions' and asked "
                "government to 'recalibrate ... community narratives'. That submission was made by a body "
                "whose membership includes data centre operators (AirTrunk, on the board), data centre "
                "developers (TPG via HyperVault), the hyperscalers, and the systems integrators who hold "
                "the government's own technology contracts. No improper conduct is alleged or implied. "
                "What the Observatory records is that the same organisation speaks for the operator, the "
                "investor and the supplier at once, and that the inquiry received one submission from it."),
         fact_status="REPORTED", source_id="SRC_WIKI_BCA_MEMBERS",
         confidence="medium", as_of_date=AS_OF, disclosed=1),
    dict(actor_id="ENT_TCS", channel="industry_forum",
         recipient="Australia-India CEO Forum", event_date="2026",
         instrument="Forum membership; co-chair of the Australia India Women's Leadership Forum",
         position=("TCS is a member of the government-convened Australia-India CEO Forum and co-chairs its "
                   "Women's Leadership Forum. The Forum's Director is Jodi McKay, who is concurrently "
                   "Australia's Senior Trade and Investment Commissioner for South Asia at Austrade "
                   "(Mumbai) and a former NSW Leader of the Opposition and Cabinet Minister. McKay has "
                   "posted in that capacity about meeting 'Australia-India CEO Forum member Tata "
                   "Consultancy Services' and about TCS's Mumbai facility."),
         outcome=("Ongoing. A second access channel distinct from the BCA, and one that runs through a "
                  "serving Commonwealth trade commissioner rather than a domestic peak body."),
         notes=("Recorded as an access map. A firm holding at least $234.4M in Australian government IT "
                "contracts - including to the Department of the Prime Minister and Cabinet, which now "
                "houses the Office of AI - is a member of, and co-chairs a programme of, a bilateral forum "
                "directed by a serving Commonwealth trade commissioner who previously led the opposition "
                "in the state where most of those contracts sit. This is entirely lawful and entirely "
                "normal in trade promotion. It belongs in the database because the Senate inquiry's terms "
                "of reference cover 'deals between Government and global AI companies', and because the "
                "Observatory's method is to map access rather than assume its absence."),
         fact_status="REPORTED", source_id="SRC_AUSTRADE_MCKAY",
         confidence="medium", as_of_date=AS_OF, disclosed=1),
    dict(actor_id="ENT_TCS", channel="other",
         recipient="Australian data centre policy debate (position, not advocacy)",
         event_date="2025-11-20",
         instrument="HyperVault / TPG strategic partnership announcement",
         position=("By becoming a hyperscale data centre developer, TCS moved from being a supplier to "
                   "government into the class of entity whose interests the NSW Data Centre Guidelines, "
                   "the Commonwealth Expectations and the two parliamentary inquiries are actually about. "
                   "TPG - its JV partner - is itself a BCA member. TPG's Jim Coulter frames data centers "
                   "as an asset class at 'the intersection of green energy infrastructure, technology and "
                   "real estate'."),
         outcome=("Announced, subject to conditions precedent and statutory approvals. India-scoped: "
                  "Chandrasekaran is quoted on building 'GW-scale AI data centers in India'. No Australian "
                  "HyperVault facility is announced (RG-075)."),
         notes=("Recorded under channel 'other' because it is a market position rather than an act of "
                "advocacy, and because the lobbying table's enum has no value for 'became a regulated "
                "party'. The analytical point stands on its own: as at 18 September 2026 the BCA's "
                "membership includes at least one firm that is simultaneously a government IT contractor, "
                "a peak-body member, and a data centre developer. Whether HyperVault ever seeks Australian "
                "consent is the question that would convert this from a structural observation into a "
                "live conflict, and it is the highest-value forward-looking item in this layer."),
         fact_status="VERIFIED", source_id="SRC_TCS_HYPERVAULT",
         confidence="high", as_of_date=AS_OF, disclosed=1),
]

# ---------------------------------------------------------------------------
# METRICS
# ---------------------------------------------------------------------------
METRICS = []
def M(scope, name, value, unit, status, src, conf, note=None, as_of="2026-09-18"):
    METRICS.append(dict(scope=scope, metric_name=name, value=value, unit=unit, as_of=as_of,
                        notes=note, fact_status=status, source_id=src, confidence=conf,
                        as_of_date=as_of))

M("national", "TCS Australian public sector contract portfolio - published aggregator total",
  352735957.18, "AUD", "REPORTED", GM, "medium",
  "GovMarket published figure: 'Total portfolio $352,735,957.18', 'Contracts won 65'. This is the number "
  "in public circulation and the number supplied to this project. It is INFLATED - see the de-duplicated "
  "metric below.")
M("national", "TCS Australian public sector contract portfolio - Observatory de-duplicated total",
  234423257.18, "AUD", "VERIFIED", "SRC_GOVMARKET_TECOE", "high",
  "$352,735,957.18 less ONE confirmed duplicate of $118,312,700 (the Transport Equipment Centre of "
  "Excellence, published on both buy.nsw as CAN-100812 and in the aggregator's own contract record with "
  "identical value, identical 29 March 2018 award date and identical 30 June 2027 expiry). 45 of 65 "
  "records are paywalled so further duplicates cannot be excluded: this is a CEILING on distinct spend, "
  "not a floor. The overstatement is $118,312,700, or 50.5% of the corrected figure.")
M("national", "TCS distinct Australian public contracts", 64, "count", "VERIFIED",
  "SRC_GOVMARKET_TECOE", "high",
  "65 published less one confirmed duplicate.")
M("national", "TCS portfolio share attributable to a single nine-year sole-sourced contract",
  50.5, "percent of corrected total", "VERIFIED", "SRC_BUYNsw_CAN100812", "high",
  "$118,312,700 of $234,423,257. Half of the tracked Australian public-sector exposure to this firm is "
  "one directly negotiated contract running 29 March 2018 to 30 June 2027.")
M("national", "Transport Equipment Centre of Excellence contract term", 9.25, "years", "VERIFIED",
  "SRC_BUYNsw_CAN100812", "high",
  "29 March 2018 to 30 June 2027. GovMarket's own contract record states '9y 3mo term - 92% elapsed'. "
  "Method of tendering: direct negotiation.")
M("national", "TCS median Australian government contract win (implied)", 222810.0, "AUD", "REPORTED",
  "SRC_GOVMARKET_TECOE", "low",
  "DERIVED, NOT PUBLISHED. The aggregator states the $118.3M contract is '~531x their median win', which "
  "implies a median of about $222,810. Recorded as a derived estimate at low confidence because it is "
  "arithmetic performed on the aggregator's own characterisation.")
M("national", "TCS contracts with Melbourne Water", 27, "count", "REPORTED", GM, "medium",
  "$5.3M across 27 contracts - the highest contract count of any buyer, at an average of about $196k. "
  "Nine of the 27 are individually visible and sum to $1,794,000 (average $199,333, against a published "
  "average of $196,296), leaving 18 records and $3,506,000 behind the paywall. Consistent with a panel or standing-offer drawdown rather than 27 separate "
  "competitions.")
M("NSW", "Share of NSW data centre planning records handled by the two most-assigned officers",
  65.1, "percent", "VERIFIED", "SRC_PORTAL_PLANNERS", "high",
  "Shaun Williams 25 of 63 (39.7%) and Patrick Copas 16 of 63 (25.4%), together 41 of 63. Eleven named "
  "officers in total across the 63 records. Published on the portal, so this is disclosed accountability.")
M("NSW", "NSW data centre consents issued under a delegation executed after the Guidelines",
  2, "count", "VERIFIED", "SRC_CONSENT_DELEGATIONS", "high",
  "Glendenning Road SSD-73761707 (signed 14 September 2026) and Project Apollo Macquarie Park (signed "
  "2 September 2026), both under a ministerial delegation executed 18 August 2026 - one day after the "
  "NSW Data Centre Guidelines were published on 17 August 2026. Eleven further consents were issued under "
  "a 9 March 2022 delegation and one under 9 March 2020.")
M("NSW", "NSW data centre consents where the Schedule 1 applicant is a consultancy",
  4, "count", "VERIFIED", "SRC_CONSENT_APPLICANTS", "high",
  "ARUP Pty Ltd (43-61 Turner Road); Cundall Johnston and Partners Pty Ltd (Davis Road and its Mod 1); "
  "Lehr Consultants International (Australia) Pty Ltd (Glendenning Road SSD-73761707, 235 MW). Of 13 "
  "consents whose Schedule 1 applicant parsed.")
M("NSW", "NSW data centre consents where the Schedule 1 applicant is an opaque SPV or trust trustee",
  4, "count", "VERIFIED", "SRC_CONSENT_APPLICANTS", "high",
  "EMKC Cubed Management Pty Ltd (two consents: 51 Huntingwood Drive SSD-41589232 with 632 MW installed "
  "back-up, and Apollo Place SSD-67407231); HDI SYD1 Property Holdings Limited (DigiCo SYD1 expansion "
  "SSD-69637456); The Trustee for NineZero DC Sub Trust I (DCI Poplars). Beneficial ownership unresolved "
  "in all four (RG-064).")
M("NSW", "NSW data centre consents where the Schedule 1 applicant is the identifiable operator",
  5, "count", "VERIFIED", "SRC_CONSENT_APPLICANTS", "high",
  "Five, and they are: NEXTDC Limited; Goodman Property Services (Aust) Pty Limited; Canberra Data Centres "
  "Pty Ltd; Macquarie Data Centres Pty Ltd; Equinix Hyperscale 2 (SY10) Pty Limited. The 13 parsed consents "
  "therefore divide 4 consultancy applicants + 4 opaque SPV or trust applicants + 5 identifiable operators. "
  "So in 8 of the 13 parsed consents - a clear majority - the party legally named as the applicant is NOT "
  "the operator of the facility.")
M("NSW", "NSW data centre projects with an identifiable independent peer review of acoustic evidence",
  3, "count", "REPORTED", "SRC_ATTACHMENT_CONSULTANTS", "medium",
  "DigiCo SYD1 expansion ('a14-acoustic-peer-review'); Lane Cove West mod 3 "
  "('peer-review-acoustic-assessment'); 51 Huntingwood Drive mod 1 ('appendix-b4-acoustic-review-"
  "statement' x2). Three of 63 projects, i.e. about 5%. Across the same 63 projects there are 181 "
  "acoustic and noise attachments. Independent checking of the amenity evidence is the exception, not "
  "the norm. Evidence tier: attachment filename only (RG-073).")

# ---------------------------------------------------------------------------
# ENGINEERING / STRATEGY CLAIM TESTS
# The brief supplied three strategy critiques. Each is tested rather than adopted.
# ---------------------------------------------------------------------------
ENGINEERING = [
    dict(claim_label="The $118m TfNSW 'Transport Equipment Centre of Excellence' is a 2025 outsourcing deal dressed up in buzzwords",
         claim_status="FACTUALLY_WRONG_PREMISE",
         premise_check=(
             "PARTLY TRUE, MATERIALLY MISDATED. The contract is real, the value is exact, and the label "
             "is real. But it is not a July 2025 award. Primary notice CAN-100812 records an EFFECTIVE "
             "DATE OF 29 MARCH 2018 and a contract end of 30 June 2027 - a 9 year 3 month term, 92% "
             "elapsed. The aggregator that supplied these figures dates the same contract '29 July 2025' "
             "in its listing and '29 Mar 2018' in its own contract record. July 2025 is when the NOTICE "
             "was published, not when the contract was let."),
         australia_reality=(
             "This is an eight-year-old continuously re-disclosed sole-source arrangement, obtained by "
             "DIRECT NEGOTIATION per the notice. It is roughly half of the firm's entire tracked "
             "Australian public-sector exposure. The same function has been outsourced since at least "
             "2018, when trade press reported TCS displacing Deloitte on a $76.7M three-year Transport "
             "for NSW software maintenance deal for this Centre. The correct finding is not 'a new $118m "
             "outsourcing deal' but 'a nine-year sole-sourced outsourcing arrangement worth more than the "
             "rest of the firm's Australian government portfolio combined, re-published in 2025 in a form "
             "that reads as new'. "
             "Note also what the notice discloses about accountability: variation provisions 'Not "
             "applicable', renegotiation provisions 'Not applicable', other private sector entities "
             "benefiting 'Not applicable', heightened modern slavery due diligence 'No', agency piggyback "
             "clause 'No', and 'No amendments have been made to this disclosure' across nine years."),
         replacement_spec=(
             "RESTATE THE FINDING AS A DURATION AND COMPETITION FINDING, NOT A SIZE FINDING. The "
             "defensible claims are: (1) a single directly negotiated contract has run 9.25 years and "
             "accounts for 50.5% of the firm's tracked Australian public spend; (2) the notice records no "
             "variation, renegotiation or amendment provisions across that term; (3) the contract expires "
             "30 June 2027 and is therefore a live recompete within the Observatory's reporting horizon. "
             "The user's proposed remedies - mandated open API standards, infrastructure-as-code delivery, "
             "state-owned deployment pipelines - are the right remedies for lock-in, and lock-in is "
             "exactly what a 9.25-year direct negotiation produces. They should be attached to the "
             "2027 expiry, which is when they can actually bite."),
         existing_policy_hook=(
             "NSW procurement rules require contract award notices above the disclosure threshold, which "
             "is why CAN-100812 exists and is readable at all. The direct-negotiation method is disclosed "
             "on the face of the notice."),
         residual_gap=(
             "No public register aggregates re-disclosures of the SAME contract, so a long-running "
             "sole-source arrangement appears in a 2025 dataset as fresh spend. That is the defect this "
             "row documents, and it is the same defect the Observatory found in the data centre pipeline "
             "itself: the BCA's own commissioned Oxford Economics research shows 44 GW of connection "
             "requests resolving to 2.8 GW of real draw, because gross aggregates are mistaken for net "
             "commitments. Double-counting is the recurring failure mode across both layers."),
         source_ids="SRC_BUYNsw_CAN100812,SRC_GOVMARKET_TECOE,SRC_GOVMARKET_TCS",
         as_of_date=AS_OF),
    dict(claim_label="Melbourne Water's 27 micro-contracts are fragmented procurement and a gross misuse of taxpayer funds",
         claim_status="PARTLY_SOUND",
         premise_check=(
             "THE COUNTS AND VALUES ARE CORRECT; THE CHARACTERISATION IS NOT. $5.3M across 27 contracts is "
             "confirmed by the aggregator, and the nine individually visible contracts sum to $1,794,000 at "
             "an average of about $199k, consistent with the stated total. But 27 low-value awards to one "
             "pre-qualified supplier is the normal operation of a panel or standing-offer arrangement, not "
             "evidence of 27 separate procurement failures. Consolidated panels exist precisely to avoid "
             "running a full tender for a $105k hardware replacement."),
         australia_reality=(
             "The legitimate concern is different from the one stated, and is about CATEGORY rather than "
             "FRAGMENTATION. The visible scopes are Citrix upgrades, SolarWinds implementation and support, "
             "M365 OneDrive and SharePoint Level 2 infrastructure support, end-of-life hardware "
             "replacement, GIS consulting on time-and-materials, cyber security project management, "
             "network zone model refinement, and disaster recovery infrastructure build phase 2. These are "
             "run-the-business operational tasks and staff augmentation. Buying them through a consulting "
             "panel at consulting rates is a real cost question; the fragmentation is a symptom, not the "
             "disease. Note that only one visible engagement is explicitly priced time-and-materials (the "
             "$197k GIS engagement), so the brief's claim of 'paying premium day rates' is not "
             "substantiated by the visible records and should not be asserted. "
             "RELEVANCE TO THIS OBSERVATORY: Melbourne Water is the Victorian water authority whose "
             "counterpart claims are live in the data centre debate. The NSW Guidelines of 17 August 2026 "
             "require 100% recycled water for water-intensive cooling, and the BCA's Submission No 116 "
             "claims recycled water already supplies 55% of AirTrunk's total water use - unverified, "
             "logged as RG-068. Whether any of the 17 paywalled TCS engagements at Melbourne Water touch "
             "recycled-water supply planning is an open question (RG-080) and would be materially more "
             "interesting than the procurement-style point."),
         replacement_spec=(
             "DROP 'gross misuse of taxpayer funds' - it is not evidenced and it discredits the rest. "
             "KEEP AND SHARPEN: (1) publish the panel drawdown as a single aggregate line per supplier per "
             "year so the total is visible rather than scattered across 27 notices; (2) require agencies to "
             "report what share of panel drawdown is run-the-business operational work versus discrete "
             "projects; (3) for the DR infrastructure build specifically, require the agency to state "
             "whether secondary-site capacity is involved, since that is data-centre-relevant scope. "
             "'Automate the maintenance away' and 'self-healing cloud infrastructure' are not remedies for "
             "a procurement-category problem and should not be presented as such."),
         existing_policy_hook=(
             "Victorian and Commonwealth procurement frameworks already require panel arrangements to be "
             "established competitively and drawdowns to be disclosed. The disclosure is happening - that "
             "is how the 27 are countable."),
         residual_gap=(
             "18 of the 27 contracts are behind the aggregator paywall, so their scopes are unknown. No "
             "public source states the onshore/offshore delivery split, which is the variable that would "
             "actually determine whether the rate is 'premium'."),
         source_ids="SRC_GOVMARKET_TCS",
         as_of_date=AS_OF),
    dict(claim_label="Commodity work (Office 365 setup, defect fixes) is being disguised as strategic projects, subsidising integrator overhead",
         claim_status="PARTLY_SOUND",
         premise_check=(
             "TRUE AS TO THE SCOPES. 'Office 365 Environment Setup for MoG GSS' ($189k, published 5 May "
             "2025) is tenant setup for a Machinery-of-Government change affecting Government Shared "
             "Services. Three OneStream awards on 17, 18 and 19 December 2024 totalling $1,735,000 "
             "include one titled 'Defect Fix Services for OneStream Solution' at $1.1M. These are "
             "operational and remedial scopes. Whether they were 'disguised as strategic projects' cannot "
             "be established: they were published under accurate titles that say plainly what they are."),
         australia_reality=(
             "The stronger and better-evidenced version of this critique is about AGENCY ATTRIBUTION AND "
             "THRESHOLDS, not disguise. Two findings survive scrutiny. First, the $1.1M award is titled "
             "'DEFECT FIX SERVICES' - a nine-figure-sum portfolio that includes a seven-figure remediation "
             "contract is a portfolio in which delivery quality is being paid for twice, once to build and "
             "once to fix. That is a legitimate and specific criticism. Second, the O365 contract's agency "
             "attribution is itself unreliable: the aggregator assigns it to the NSW Department of Customer "
             "Service while the title and pattern are consistent with a Commonwealth award, which means "
             "public reporting of who bought what cannot be relied on without going to the portal of "
             "record. "
             "The counter-argument the brief omits: MoG transitions are genuinely time-critical and "
             "genuinely exceed internal capacity by design, because a machinery-of-government change moves "
             "functions between agencies on a fixed political date. Buying surge capacity for that is "
             "defensible. The indefensible part is paying $1.1M to fix defects in a system already paid "
             "for."),
         replacement_spec=(
             "REPLACE 'stop treating integrators as a substitute for internal engineering' with two "
             "testable requirements: (1) defect remediation contracts above a threshold should require the "
             "agency to disclose whether the defect arose under a prior contract with the same supplier, "
             "and if so, whether the original contract carried acceptance criteria and warranty; (2) every "
             "award notice should name the portal of record so aggregation cannot misattribute the buyer. "
             "The brief's proposal to 'embed senior technical architects into delivery teams to audit code "
             "quality' is sound practice but is an agency capability question, not a procurement rule, and "
             "it costs money the brief does not account for."),
         existing_policy_hook=(
             "Contract award notices already require a description of goods and services, which is why the "
             "titles are accurate and this critique could be tested at all."),
         residual_gap=(
             "Warranty and acceptance terms are not published on award notices, so the 'paid twice' "
             "finding cannot be quantified from public data. It requires the contracts themselves, i.e. an "
             "FOI request - the same route the Observatory already drafted for tax concessions at "
             "reports/RG007_foi_strategy.md."),
         source_ids="SRC_GOVMARKET_TCS,SRC_BUYNsw_CAN100812",
         as_of_date=AS_OF),
    dict(claim_label="Consultancies, not developers, are the named legal applicants on NSW data centre consents",
         claim_status="SOUND",
         premise_check=(
             "TRUE AND VERIFIED FROM THE SIGNED INSTRUMENTS. In 4 of the 13 NSW data centre consents whose "
             "Schedule 1 parsed, the named Applicant is an engineering or planning consultancy - ARUP Pty "
             "Ltd, Cundall Johnston and Partners Pty Ltd (twice), and Lehr Consultants International "
             "(Australia) Pty Ltd. In a further 4 it is an opaque SPV or trust trustee - EMKC Cubed "
             "Management Pty Ltd (twice), HDI SYD1 Property Holdings Limited, and The Trustee for NineZero "
             "DC Sub Trust I. Only 5 of 13 name an identifiable operator, so the 13 divide 4 + 4 + 5."),
         australia_reality=(
             "In 8 of 13 parsed consents - a clear majority - the party legally named as the applicant on the "
             "instrument is not the operator of the facility. The most consequential instance is "
             "Glendenning Road SSD-73761707, the 235 MW consent that is the Observatory's benchmark "
             "post-Guidelines instrument: it carries all-times additional firmed renewable matching, a NOx "
             "cap under 10 tonnes per year excluding outages, 45 metre stacks, the first 170 hour "
             "generator cap in the sample, and 267.45 MW of installed back-up against a 235 MW load cap - "
             "and it names an acoustics and planning consultancy as the applicant. A member of the public "
             "reading that consent cannot tell who will operate the facility next to them. "
             "This is not a data-entry quirk and it is not an allegation. Agents lodging on behalf of "
             "principals is ordinary planning practice. But the consent is the enduring public legal "
             "record, and where it names an agent the beneficial operator is absent from the only document "
             "that runs with the land. Combined with the trust-series and per-site-SPV structures, the "
             "effect is that the NSW data centre pipeline's ownership is substantially undeterminable from "
             "its own primary instruments."),
         replacement_spec=(
             "REQUIRE THE OPERATOR TO BE NAMED ON THE INSTRUMENT. A consent condition or a Schedule 1 "
             "field should carry both the applicant (who may be an agent) and the intended operator and "
             "ultimate parent, updated on any change of control. This is a one-line change to a form and it "
             "would resolve RG-022, RG-023, RG-064, RG-065 and RG-081 at a stroke. It costs nothing to implement "
             "and it is the single highest-value transparency reform available in this layer."),
         existing_policy_hook=(
             "Section 4.38 of the Environmental Planning and Assessment Act 1979 consents already carry a "
             "Schedule 1 identifying the application, the applicant, the consent authority, the site and "
             "the development. The field exists; it is simply populated with the agent. The NSW Data "
             "Centre Guidelines of 17 August 2026 include a website-disclosure measure, and one consent in "
             "the sample carries a website disclosure condition - so the machinery for naming the operator "
             "publicly is already partly present."),
         residual_gap=(
             "Nothing in the Guidelines, the Commonwealth Expectations, or either parliamentary inquiry's "
             "terms of reference requires the beneficial operator or ultimate parent to be named on a "
             "consent. The Senate inquiry's TOR covers 'deals between Government and global AI companies' "
             "and the NSW inquiry's covers lobbying and donations, but neither covers the identity of the "
             "consent holder. That is a gap in the terms of reference themselves and is worth putting to "
             "both committees before they report on 16 November and 3 November 2026 respectively."),
         source_ids="SRC_CONSENT_APPLICANTS,SRC_SSD73761707_CONSENT,SRC_NSWPORTAL_CONSENTS",
         as_of_date=AS_OF),
]

# ---------------------------------------------------------------------------
# RESEARCH GAPS
# ---------------------------------------------------------------------------
GAPS = [
    ("B", "Obtain the full 65-record TCS contract list from the portals of record (AusTender and buy.nsw) rather than the aggregator, and identify every duplicate.",
     "The $352.7M figure in public circulation overstates distinct spend by at least $118.3M because one contract is published on two portals. 45 of 65 records are paywalled, so the true distinct total is unknown and could be lower still. Any public claim about taxpayer funding of this firm is currently untestable without doing this.",
     "AusTender contract notice search; buy.nsw supplier profile 75727 contract history; QTenders; Buying for Victoria",
     "scrape_portal", 2,
     "One duplicate CONFIRMED this session (CAN-100812 = GovMarket 'Operation and Maintenance of Transport Equipment Centre of Excellence', identical to the cent, identical 29 Mar 2018 award, identical 30 Jun 2027 expiry). De-duplicated total $234,423,257.18 across 64 records."),
    ("A", "Establish which consultancy authored each technical appendix in the NSW data centre consents, by opening the documents rather than reading filenames.",
     "The conditions in a consent are only as good as the evidence behind them. Acoustic, CFD, hydrogeological and traffic appendices set the numbers that become the conditions. 181 acoustic and noise attachments exist across 17 projects, but authorship is currently inferred from filenames in only a handful of cases. Without this, the Observatory cannot say who wrote the evidence base for the sector's amenity impacts.",
     "data/raw/nsw_planning/consents/*.txt title pages; the 6,866-attachment index; DPHI Assessment Reports (RTS) which name report authors",
     "manual_review", 1,
     "Filename-level pass COMPLETE and archived: Arup (CFD at 1-5 Khartoum Road; 7 technical notes at Apollo Place), Aurecon (plant and equipment systems report, Mamre Road), WSP (Dicker), Renzo Tonin (Talavera acoustic queries), Cundall (Davis Road advice). Named firms appear in only ~16 of 6,866 filenames, so this is a floor. Document-level pass required."),
    ("C", "Does any consultancy that authors technical evidence for data centre proponents also hold contracts with DPHI, the IPC, or the agencies writing the Guidelines?",
     "If the same firms write both the proponent's evidence and the regulator's guidance, the assessment is not independent in substance even where it is procedurally correct. This is the consultancy layer's central question and it is currently unanswered.",
     "AusTender and buy.nsw searches for DPHI/IPC/Planning; the NSW Data Centre Guidelines acknowledgement and authorship; Commonwealth Expectations authorship; IDA Round 1 advisory panel",
     "scrape_portal", 1,
     "Not started. Note the Guidelines are dated 17 August 2026 and a fresh ministerial delegation was executed the following day, 18 August 2026, under which both post-Guidelines consents in the sample were issued - so whoever advised on the Guidelines had immediate effect on two decisions."),
    ("C", "Do peer reviews of acoustic and CFD evidence ever review work by the same firm, and how often is peer review commissioned at all?",
     "Only 3 of 63 projects carry an identifiable independent peer review of acoustic evidence, against 181 acoustic attachments. Arup authored CFD modelling at 1-5 Khartoum Road and is the named applicant at 43-61 Turner Road; Cundall authored advice at Davis Road and is the named applicant there. Self-review threats need to be tested project by project.",
     "The peer review attachments themselves: a14-acoustic-peer-review (DigiCo SYD1); peer-review-acoustic-assessment (Lane Cove West mod 3); appendix-b4-acoustic-review-statement x2 (51 Huntingwood Drive mod 1)",
     "manual_review", 2,
     "Peer review confirmed to EXIST and to be rare (~5% of projects). Reviewing firms are not named in the filenames. Three documents to open."),
    ("A", "Does TCS or HyperVault have any Australian data centre footprint, application, or announced site?",
     "TCS is a BCA member, holds at least $234.4M in Australian government IT contracts including to PM&C which houses the Office of AI, and is now a hyperscale data centre developer. If HyperVault ever seeks Australian consent, a firm represented in the policy debate becomes a regulated party in it. Establishing the current position is what makes that a documented negative rather than an assumption.",
     "NSW planning portal; VIC Planning; QLD; TCS Australia and New Zealand site; HyperVault announcements; ASIC name searches for HyperVault entities",
     "scrape_portal", 1,
     "DOCUMENTED NEGATIVE as at 18 September 2026. The 20 November 2025 TCS press release does not mention Australia anywhere; Chairman Chandrasekaran is quoted on building 'GW-scale AI data centers in India'; The Asset reports proceeds support 'firm's GW-scale AI data centre build in India'. No Australian application located. Recheck on any HyperVault announcement."),
    ("C", "Are Jodi McKay's concurrent roles - Austrade Senior Trade and Investment Commissioner for South Asia, Director of the Australia-India CEO Forum (TCS a member), former NSW Opposition Leader - disclosed on the relevant registers, and do ministerial diaries record TCS contact?",
     "Maps a second access channel distinct from the BCA, running through a serving Commonwealth trade commissioner. The Senate inquiry TOR covers 'deals between Government and global AI companies'; this is the kind of relationship it should be asked about.",
     "Austrade disclosures; Australia-India CEO Forum membership and governance; Commonwealth ministerial diaries; NSW lobbyist register (RG-070); AEC donation disclosures",
     "manual_review", 3,
     "Roles CONFIRMED from Austrade's own site and Forum releases. Register and diary checks not done. Pairs with RG-070."),
    ("B", "Who commissioned and paid for the Oxford Economics research on phantom data centre demand, cited by both the BCA and Data Centres Australia?",
     "The 44 GW to 6 GW to 2.8 GW finding is the single most important number in the demand debate and it is industry-commissioned. It cuts AGAINST the sector's interest in a large headline pipeline, so it should be credited - but the Observatory records it as commissioned research without knowing who paid. Oxford Economics also does paid work for proponents.",
     "The Oxford Economics report 'Surging Data Centre Connection Requests Drive Phantom Demand' (21 November 2025) title page and funding disclosure; AEMO's commissioning record for the work the Guidelines cite",
     "manual_review", 2,
     "Report cited in BCA Submission No 116, which the Observatory holds at data/raw/nsw_planning/submissions/BCA_116.pdf. The funding disclosure has not been read. The NSW Guidelines separately cite Oxford Economics work prepared FOR AEMO, which may be a different engagement - resolving whether they are the same study matters."),
    ("C", "Does consent condition stringency vary by assessment officer once determination date is controlled for?",
     "Two officers handle 65% of the 63 NSW data centre planning records (Shaun Williams 40%, Patrick Copas 25%). Across the 20-consent battery Williams' 9 consents carry an average of 1.7 of the tracked conditions and Copas' 6 carry 1.2, with the single strictest consent (Thomas Bertwistle, Grand Avenue / Equinix SY10, 3 conditions including the only renewable PPA additionality requirement in the sample) handled by an officer with one case. Either this is officer variation or it is a time-and-proponent effect. It CANNOT CURRENTLY BE DISTINGUISHED.",
     "Determination dates for all 20 consents in the battery (MISSING - the field parsed empty on every row); the 6 remaining unparsed Schedule 1 applicants; condition battery extended from 20 to 46 consents",
     "manual_review", 1,
     "BLOCKED ON A DATA DEFECT DISCOVERED THIS SESSION: determination_date is EMPTY for all 20 rows of exports/nsw_planning/nsw_dc_consent_conditions.csv, so the era confound cannot be controlled. Four dates were recovered manually from the instruments (2026-09-14 Glendenning, 2026-09-02 Project Apollo, 2026-07-23 Project Pluto, 2020-07-14 Roberts Road). DO NOT REPORT AN OFFICER EFFECT UNTIL DATES ARE POPULATED - n is too small and the Guidelines changed the standard mid-sample."),
    ("D", "Do any TCS engagements for Melbourne Water touch recycled-water supply planning, third-party water schemes, or data centre service connections?",
     "Melbourne Water is both a TCS client (27 contracts) and the Victorian water authority whose counterparts are central to this Observatory's water findings. The NSW Guidelines require 100% recycled water for water-intensive cooling and the BCA claims recycled water already supplies 55% of AirTrunk's use (unverified, RG-068). A consultancy sitting inside a water authority's IT estate is a route into how those numbers are actually produced.",
     "The 18 paywalled Melbourne Water contracts; Melbourne Water contract disclosures; Victorian Tenders portal; Sydney Water and Melbourne Water FOI (pairs with RG-068)",
     "foi_request", 2,
     "Not started. Ten visible Melbourne Water scopes are all conventional IT (Citrix, SolarWinds, M365, DR, GIS, cyber PM, network zone, EOL hardware) with no water-supply planning content. The GIS and network-zone engagements are the two that could plausibly touch asset and supply geography."),
    ("C", "Resolve beneficial ownership of EMKC Cubed Management Pty Ltd, HDI SYD1 Property Holdings Limited and The Trustee for NineZero DC Sub Trust I.",
     "These three vehicles are the named applicants on FOUR NSW data centre consents, including 51 Huntingwood Drive with 632 MW of installed back-up generation - the largest in the sample - and the DigiCo SYD1 expansion in the City of Sydney. None discloses its operator on the face of the consent. This is the ownership half of the applicant-versus-proponent finding.",
     "Paid ASIC company extracts; ABN Lookup; trust deeds are not public so the route is ASIC officer and shareholder history plus the DPHI Assessment Report for each project, which usually names the proponent",
     "asic_search", 1,
     "Supersedes and extends RG-064, which named the same three vehicles. Now evidenced from the signed consents rather than inferred. Note EMKC holds TWO consents and 'HDI SYD1' is a per-site holding company, so the structures are deliberately site-specific."),
    ("C", "Extend the entity_type enum to include 'consultancy' and retype ARUP, LEHR, CUNDALL and the systems integrators.",
     "Three consultancies are currently typed 'other' in the entities table, which makes them unqueryable as a class. The consultancy_profile table carries firm_type as a workaround, but the base enum should be correct so that a single query can return every consultancy in the database.",
     "schema/01_schema.sql CHECK constraint on entities.entity_type; ALTER-and-rebuild via scripts/build_db.py",
     "manual_review", 4,
     "SCHEMA HYGIENE. Not a research question. Logged so it is not forgotten; workaround is consultancy_profile.firm_type, which is populated for all seven firms in this pack."),
    ("B", "Resolve the agency attribution and portal of record for the 'Office 365 Environment Setup for MoG GSS' contract and the three December 2024 OneStream awards.",
     "The aggregator attributes the O365 contract to the NSW Department of Customer Service while the title denotes a Commonwealth Machinery-of-Government change to Government Shared Services. If a widely used aggregator misattributes the buyer, then every derived claim about which government is funding what is unsafe. The three same-title OneStream awards on consecutive days may also be one scope split across notices.",
     "AusTender and buy.nsw notice search by title; the OneStream notices' description fields",
     "scrape_portal", 3,
     "Recorded at low confidence in the contracts table. This gap exists to protect the integrity of the layer rather than to add a fact."),
]

# ---------------------------------------------------------------------------
# ASSEMBLE
# ---------------------------------------------------------------------------
def build_pack() -> dict:
    rows = {
        "sources": SOURCES,
        "entities": ENTITIES,
        "entity_aliases": ENTITY_ALIASES,
        "ownership": OWNERSHIP,
        "consultancy_profile": PROFILES,
        "gov_contracts": [],
        "consultant_role": ROLES,
        "case_handling": CASE_HANDLING,
        "lobbying": LOBBYING,
        "metrics": METRICS,
        "engineering_claims": ENGINEERING,
        "research_gaps": [],
    }

    # Fill default provenance on consultancy_profile rows. Profiles use the shorthand
    # status=/conf= keys; expand them here so the loader's provenance rule is satisfied
    # without repeating four fields on every profile.
    PROF_DEFAULT_SRC = {
        "ENT_TCS": "SRC_BUYNsw_CAN100812",
        "ENT_ARUP": "SRC_CONSENT_APPLICANTS",
        "ENT_LEHR": "SRC_CONSENT_APPLICANTS",
        "ENT_CUNDALL": "SRC_CONSENT_APPLICANTS",
        "ENT_EMKC": "SRC_CONSENT_APPLICANTS",
        "ENT_HDI_SYD1": "SRC_CONSENT_APPLICANTS",
        "ENT_NINEZERO": "SRC_CONSENT_APPLICANTS",
        "ENT_TPG": "SRC_WIKI_BCA_MEMBERS",
    }
    PROF_KEY_MAP = {
        "exposure": "au_public_sector_exposure_aud",
        "exposure_as_of": "exposure_as_of",
        "exposure_tier": "exposure_source_tier",
        "offshore": "offshore_delivery",
    }
    for prof in PROFILES:
        for short, long_ in PROF_KEY_MAP.items():
            if short in prof and short != long_:
                prof[long_] = prof.pop(short)
        if "fact_status" not in prof:
            prof["fact_status"] = prof.pop("status", "REPORTED")
            prof["confidence"] = prof.pop("conf", "medium")
            prof["source_id"] = PROF_DEFAULT_SRC.get(prof["entity_id"], "SRC_CONSENT_APPLICANTS")
            prof["as_of_date"] = AS_OF

    # contracts: assign sequential ids so is_duplicate_of can point at row 1
    first_id = None
    for i, c in enumerate(CONTRACTS, start=1):
        row = {
            "id": i,
            "supplier_entity_id": "ENT_TCS",
            "supplier_name": c["supplier"],
            "agency": c["agency"],
            "contract_title": c["title"],
            "value_aud": c["value"],
            "value_incl_gst": c.get("gst", 1),
            "portal": c["portal"],
            "portal_id": c.get("portal_id"),
            "award_published": c.get("published"),
            "contract_start": c.get("start"),
            "contract_end": c.get("end"),
            "method_of_tendering": c.get("method"),
            "category": c.get("category"),
            "abn": c.get("abn"),
            "verification_note": c.get("vnote"),
            "fact_status": c["status"],
            "source_id": c.get("src", GM),
            "confidence": c["conf"],
            "as_of_date": AS_OF,
        }
        if c.get("dup"):
            row["is_duplicate_of"] = first_id
            row["duplicate_note"] = c["dupnote"]
            row["source_id"] = "SRC_GOVMARKET_TECOE"
        else:
            if first_id is None and "CAN-100812" == c.get("portal_id"):
                first_id = i
        rows["gov_contracts"].append(row)

    # buyer aggregates as metrics, clearly labelled as the aggregator's own arithmetic
    for agency, val, n, pct in BUYER_AGGREGATES:
        METRICS.append(dict(
            scope="national",
            metric_name=f"TCS portfolio by buyer (aggregator published): {agency}",
            value=val, unit="AUD", as_of=AS_OF,
            notes=(f"GovMarket publishes {n} contracts and {pct}% of portfolio for {agency}. "
                   "For Transport for NSW this INCLUDES the $118,312,700 duplicate, so the distinct "
                   "figure is $160,587,300 across 14 contracts - which is 68.5% of the de-duplicated "
                   "portfolio, not 79%. The other four buyers are not known to contain duplicates."
                   if agency == "Transport for NSW" else
                   "Aggregator arithmetic, not verified against a portal notice."),
            fact_status="REPORTED", source_id=GM, confidence="medium", as_of_date=AS_OF,
        ))

    for i, (pillar, q, why, tgt, method, pri, note) in enumerate(GAPS, start=1):
        rows["research_gaps"].append(dict(
            # EXPLICIT ids 72-83. These were previously autoincrement-assigned; other packs
            # (rg079_determinations, status_updates) address them by id in match/set updates,
            # so the numbering must survive a from-scratch rebuild. Verified 2026-09-18 that
            # 72+i reproduces the ids the database had assigned.
            id=71 + i,
            pillar=pillar, question=q, why_it_matters=why, target_source=tgt,
            retrieval_method=method, priority=pri, status="open",
            opened=AS_OF, notes=note,
            fact_status="VERIFIED", source_id="SRC_CONSENT_APPLICANTS",
            confidence="high", as_of_date=AS_OF,
        ))

    return {
        "pack_id": "consultants-layer-2026-09",
        "prepared_by": "scripts/curate_consultants.py (curated from primary notices, consents and portal nodes read 2026-09-18)",
        "prepared_on": AS_OF,
        "sources": SOURCES,
        "rows": rows,
    }


def main() -> None:
    pack = build_pack()
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(pack, fh, indent=1, ensure_ascii=False)
    n = {k: len(v) for k, v in pack["rows"].items()}
    print(f"wrote {OUT}")
    for k, v in n.items():
        print(f"  {k:22s} {v:4d}")
    print(f"  {'TOTAL ROWS':22s} {sum(n.values()):4d}")


if __name__ == "__main__":
    main()
