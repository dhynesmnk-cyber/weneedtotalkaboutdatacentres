#!/usr/bin/env python3
"""
ADCO seed data v1.0.0  (as at 2026-09-18)

Every factual row carries: source_id, fact_status, confidence, as_of_date.
fact_status vocabulary:
  VERIFIED  - read directly in a primary document (government, regulator, portal, legislation)
  REPORTED  - credible secondary reporting of a primary fact
  CLAIMED   - proponent / industry assertion, not independently confirmed
  GAP       - known unknown, tracked in research_gaps
"""

ACCESSED = "2026-09-18"

# ---------------------------------------------------------------------
# SOURCES
# ---------------------------------------------------------------------
SOURCES = [
 dict(id="SRC_NSWGUIDE26", title="NSW Data Centre Guidelines",
      publisher="NSW Government (Infrastructure NSW / DPHI)",
      url="https://www.infrastructure.nsw.gov.au/media/4jlictae/id0073_nsw-data-centre_guidelines.pdf",
      doc_type="primary_government", published="2026-08-17", credibility="A",
      notes="Six principles, 17 numbered performance measures. Primary source for dPUE/dWUE limits, "
            "Group 6 diesel limits, 25% demand-flexibility requirement, PPA additionality criteria."),
 dict(id="SRC_AEMO26", title="Digital demand surge: Preparing Australia's power systems for the rise of data centres",
      publisher="AEMO", url="https://www.aemo.com.au/newsroom/news-updates/digital-demand-surge",
      doc_type="primary_regulator", published="2026-06-01", credibility="A",
      notes="162 operational DCs nationally; ~2% of grid-supplied electricity; QED Q1 2026 connection "
            "queue disclosure (11 projects >5 MW = 5.4 GW, 60% NSW / 40% VIC); 15 sites in WA SWIS; "
            "2025 I&A projections 12 TWh/6% by 2030 and 34 TWh/12% by 2050."),
 dict(id="SRC_TRANSGRID26", title="New transmission capacity in Sydney to be funded by data centres",
      publisher="Transgrid", url="https://www.transgrid.com.au/media-publications/news-articles/new-transmission-capacity-in-sydney-to-be-funded-by-data-centres/",
      doc_type="primary_regulator", published="2026-08-26", credibility="A",
      notes="20 GW of large-load connection enquiries; no capacity in Sydney basin today; 1.5 GW signed in "
            "Western Sydney; up to 2 GW unlockable via South Creek 500/330 kV substation, proponent-funded."),
 dict(id="SRC_TRANSGRIDCAP", title="Data centres and electricity capacity in NSW",
      publisher="Transgrid", url="https://www.transgrid.com.au/about-us/network/network-connections/data-centres-and-electricity-capacity-in-nsw/",
      doc_type="primary_regulator", published="2026-08-20", credibility="A",
      notes="Network Capacity Allocation Policy: large load = inverter-based load >=30 MW/30 MVA; capacity "
            "allocated only on signature of a Network Connection Agreement; 3-month planning-criteria window."),
 dict(id="SRC_ABCNSW26", title="NSW government offers fast-track scheme for data centres that comply with new guidelines",
      publisher="ABC News", url="https://www.abc.net.au/news/2026-08-17/data-centres-fast-tracked-under-new-nsw-scheme/107043984",
      doc_type="news", published="2026-08-16", credibility="A",
      notes="75-day assessment; >60 DCs operating or under construction in NSW, 19 in pipeline; data centres "
            "could be 11% of NSW energy needs by 2030 (Sharpe); IPART water pricing review; NSW Office of AI; "
            "'Stop the Slop' and Western Sydney protest, Lane Cove cluster of four."),
 dict(id="SRC_REUTERS_S7", title="OpenAI's Australian data centre drops water recycling plan, testing a drive to curb resource use",
      publisher="Reuters", url="https://www.reuters.com/business/energy/openais-australian-data-centre-drops-water-recycling-plan-testing-drive-curb-2026-07-22/",
      doc_type="investigation", published="2026-07-23", credibility="A",
      notes="NEXTDC S7 = 612 MW, Eastern Creek; recycled-water talks abandoned for lack of pipeline planning "
            "permission; switch to direct-to-chip liquid cooling; NSW imposed PUE cap of 1.3 from late 2025; "
            "review of 35 NSW applications; Sydney Water and coNEXA named as possible recycled-water suppliers."),
 dict(id="SRC_REUTERS_AI", title="Australia to establish government AI office, curb data centres' water use",
      publisher="Reuters", url="https://www.reuters.com/world/asia-pacific/australia-establish-government-ai-office-coordinate-regulation-2026-07-14/",
      doc_type="news", published="2026-07-15", credibility="A",
      notes="Commonwealth Office of AI in PM&C; national AI standard to set rules on siting, power and water; "
            "legislation flagged for early 2027."),
 dict(id="SRC_BB2026", title="AI data centres are booming in Australia - but at what cost?",
      publisher="BBC News", url="https://www.bbc.com/news/articles/cgl3we7wdr3o",
      doc_type="news", published="2026-09-03", credibility="A",
      notes="162 data centres nationally, 90 more planned, >A$155bn investment lined up; 1 GW western Sydney "
            "project to be Australia's largest single energy user; Marsden Park DC under construction 100 m from "
            "a community; Cloud Carrier three gas-fired power stations; AEMO tripling demand by 2030; "
            "Climate Council +26% NSW prices by 2035; Greenpeace renewable-claims finding."),
 dict(id="SRC_GREENPEACE_SUB", title="Submission No 120 - Inquiry into Data Centres (Greenpeace Australia Pacific)",
      publisher="NSW Legislative Council / Greenpeace Australia Pacific",
      url="https://www.parliament.nsw.gov.au/fileapi/parlfiles/getartifact?serverRelativeUrl=/lcdocs/submissions/95082/0120%20Greenpeace%20Australia.pdf",
      doc_type="primary_government", published="2026-04-03", credibility="A",
      notes="Mamre Road EIS emissions figures; Cloud Carrier 673 MW gas proposal; Clean Energy Regulator data on "
            "top-three operator emissions; Sydney Water potable-cooling and pricing evidence; Safeguard Mechanism "
            "threshold analysis; Data Center Map Greater Sydney counts."),
 dict(id="SRC_GP2026", title="Energy Vampires: the AI data centres draining Australia",
      publisher="Greenpeace Australia Pacific",
      url="https://www.greenpeace.org.au/greenpeace-reports/ai-data-centres-draining-energy-australia/",
      doc_type="think_tank", published="2026-05-27", credibility="B",
      notes="Headline finding: no data centre operator analysed adequately proves its claim of driving "
            "Australia's renewable energy growth."),
 dict(id="SRC_IA_MAMRE", title="Concern over Australia's most power-hungry data centre",
      publisher="Information Age (ACS)",
      url="https://ia.acs.org.au/article/2026/concern-over-australia-s-most-power-hungry-data-centre.html",
      doc_type="news", published="2026-04-30", credibility="B",
      notes="Mamre Road / 'Summit' site: 1.2 GW, 52 ha, six four-storey buildings, 728 cooling units, 846 diesel "
            "generators, >18,000 kL diesel storage, 22.4 ML water/yr, ~500 construction + ~500 operational jobs; "
            "land owned by IFM Investors; understood to be AirTrunk SYD4; Penrith City Council objection; "
            "NSW EPA 10 April 2026 finding that the EIS 'does not provide the information required'; "
            "school and Diocese objections."),
 dict(id="SRC_WMEDIA_ISPT", title="AirTrunk named as buyer of ISPT's 1GW Western Sydney site",
      publisher="w.media", url="https://w.media/airtrunk-named-as-buyer-of-ispts-1gw-western-sydney-site/",
      doc_type="news", published="2025-11-11", credibility="B",
      notes="Site at 706-752 Mamre Road, Mamre Road Precinct within the Western Sydney Employment Area; sale "
            "conditional on approval of the 1 GW data centre application; plans at EIS stage."),
 dict(id="SRC_DCD_MAMRE", title="AirTrunk set to buy planned 1GW data center site in Western Sydney, Australia",
      publisher="Data Center Dynamics",
      url="https://www.datacenterdynamics.com/en/news/airtrunk-set-to-buy-planned-1gw-data-center-site-in-western-sydney-australia/",
      doc_type="news", published="2025-11-11", credibility="B",
      notes="ISPT lists 706-752 Mamre Road as 'Summit', a 52-hectare holding masterplanned for 245,000 sqm."),
 dict(id="SRC_AIRTRUNK_BC", title="Completion of AirTrunk acquisition by Blackstone - marking new era of growth",
      publisher="AirTrunk", url="https://airtrunk.com/completion-of-airtrunk-acquisition-by-blackstone-marking-new-era-of-growth/",
      doc_type="primary_company", published="2024-12-23", credibility="A",
      notes="A$24bn close; consortium = Blackstone Real Estate Partners, Blackstone Infrastructure Partners, "
            "Blackstone Tactical Opportunities, Blackstone private equity strategy for individual investors, "
            "plus CPP Investments. Largest-ever global data centre deal and largest Australian transaction of 2024."),
 dict(id="SRC_BC_DEAL", title="Blackstone Announces Agreement to Acquire AirTrunk in a A$24B Transaction",
      publisher="Blackstone", url="https://www.blackstone.com/news/press/blackstone-announces-agreement-to-acquire-airtrunk-in-a-a24b-transaction/",
      doc_type="primary_company", published="2024-09-04", credibility="A",
      notes="Transaction subject to approval from the Australian Foreign Investment Review Board."),
 dict(id="SRC_CPP", title="CPP Investments Announces Investment in Asia Pacific Data Centre Operator AirTrunk",
      publisher="CPP Investments", url="https://www.cppinvestments.com/newsroom/cpp-investments-announces-investment-in-asia-pacific-data-centre-operator-airtrunk/",
      doc_type="primary_company", published="2024-09-04", credibility="A",
      notes="CPP Investments to acquire a 12% interest in AirTrunk."),
 dict(id="SRC_INFRAINV", title="Blackstone and CPP Investments acquire AirTrunk for A$24bn",
      publisher="Infrastructure Investor", url="https://www.infrastructureinvestor.com/blackstone-and-cpp-investments-acquire-airtrunk-for-a24bn/",
      doc_type="news", published="2024-09-05", credibility="B",
      notes="The two parties acquire the 88% stake in AirTrunk owned by Macquarie Asset Management and PSP Investments."),
 dict(id="SRC_CDC2025", title="Sovereign CDC Progress Secured as Shareholders Double Down on Growth",
      publisher="CDC Data Centres", url="https://cdc.com/resources/news/sovereign-cdc-progress-secured-as-shareholders-double-down-on-growth/",
      doc_type="primary_company", published="2025-02-18", credibility="A",
      notes="2.5 GW across operational, construction and pipeline; CSC sale process launched late 2024; Future Fund "
            "acquires 10.46% (total 34.55%), Infratil 1.58% (total 49.75%), CSC retains 12.04%, management 3.66%; "
            "enterprise value ~$17bn; Melbourne south-west campus phase one $2.7bn."),
 dict(id="SRC_CERTSTRAT", title="Top Data Centres in Australia: 2026 Directory and Market Overview",
      publisher="CertifiedStrategic.com", url="https://certifiedstrategic.com/insights/top-data-centres-in-australia-2026-directory-and-market-overview",
      doc_type="market_research", published="2026-03-04", credibility="B",
      notes="60 Hosting Certification Framework 'Certified Strategic' facilities across 13 providers; operator-by-"
            "operator site lists; NEXTDC M4 Fishermans Bend 162 MW / A$2bn approval January 2026; CDC Marsden Park "
            "504 MW; Mandala 1,350 MW (2024) to 3,100 MW (2030); CBRE ~1.4 GW (2025) to ~1.8 GW (2028)."),
 dict(id="SRC_MS2026", title="Microsoft deepens commitment to Australia with A$25 billion investment in AI infrastructure, security, and skills",
      publisher="Microsoft Source Asia", url="https://news.microsoft.com/source/asia/features/investing-in-australias-ai-future/",
      doc_type="primary_company", published="2026-04-23", credibility="A",
      notes="A$25bn (US$18bn) capex+opex by end-2029; footprint expansion >140%; MoU with the Australian Government "
            "affirming the Expectations; prior A$5bn (Oct 2023) grew presence to 29 sites across three Azure regions; "
            "claims 100% renewable matching and water-positive by 2030; EY-Parthenon $36bn / 186,000 FTE FY25 claim."),
 dict(id="SRC_MS2023", title="Microsoft announces A$5 billion investment in computing capacity and capability",
      publisher="Microsoft News Centre Australia",
      url="https://news.microsoft.com/en-au/features/microsoft-announces-a5-billion-investment-in-computing-capacity-and-capability-to-help-australia-seize-the-ai-era/",
      doc_type="primary_company", published="2023-10-24", credibility="A"),
 dict(id="SRC_AWS2025", title="Amazon will invest AU$20 billion in data center infrastructure in Australia by 2029",
      publisher="Amazon / aboutamazon.com", url="https://www.aboutamazon.com/news/aws/amazon-data-center-investment-in-australia",
      doc_type="primary_company", published="2025-06-14", credibility="A",
      notes="AU$20bn (US$13bn) 2025-2029; new data centres in Sydney and Melbourne; new renewable energy projects "
            "announced alongside."),
 dict(id="SRC_ABC_WD", title="Australia's largest proposed data centre could draw a quarter of the state's peak power",
      publisher="ABC News", url="https://www.abc.net.au/news/2026-09-14/western-downs-digital-park-data-centre-energy-queensland/107115082",
      doc_type="news", published="2026-09-14", credibility="A",
      notes="Western Downs Digital Park: A$31.9bn, 2.16 GW total peak capacity, former feedlot site ~250 km west of "
            "Brisbane; Energy Queensland involvement."),
 dict(id="SRC_WESTPAC", title="Powering the AI Economy: Australia's $155bn data centre pipeline",
      publisher="Westpac IQ", url="https://www.westpaciq.com.au/economics/2026/05/australian-AI-data-bulletin-2026",
      doc_type="market_research", published="2026-05-29", credibility="B",
      notes="Investment pipeline estimated to exceed $155bn, or 5.6% of one year's GDP."),
 dict(id="SRC_MALLESONS", title="Big day for data centres: New renewable energy, grid connection and cost recovery rules explained",
      publisher="King & Wood Mallesons", url="https://www.mallesons.com/au/en/insights/latest-thinking/big-day-for-data-centres.html",
      doc_type="law_firm_analysis", published="2026-08-06", credibility="B",
      notes="5 August 2026: AEMC advice to ECMC on mandatory demand offsetting; ECMC July 2026 agreement with QLD "
            "and NT dissenting; Minister Bowen rule change requests ERC0448 and ERC0456 on network cost recovery; "
            "NSW Electricity Infrastructure Investment Amendment Bill 2026; REGO obligation 12 months to implement, "
            "connections/AEMO registration reforms 24-36 months."),
 dict(id="SRC_AEMC", title="AEMC proposes new grid standards for data centre connections",
      publisher="AEMC", url="https://www.aemc.gov.au/news-centre/media-releases/aemc-proposes-new-grid-standards-data-centre-connections",
      doc_type="primary_regulator", published="2026-03-12", credibility="A",
      notes="Draft rule/determination creating a new standard for large inverter-based loads; fault ride-through "
            "rather than tripping; not retrospective."),
 dict(id="SRC_VICPLAN", title="Sustainable Data Centre Action Plan (AI Mission Statement)",
      publisher="Victorian Government DJSIR",
      url="https://djsir.vic.gov.au/priorities-and-initiatives/ai-mission-statement/sustainable-data-centre-action-plan",
      doc_type="primary_government", published="2026-08-03", credibility="A",
      notes="$5.5m action plan; five focus areas; potential project pipeline worth more than $25bn; led by DJSIR "
            "with DEECA, DTP and DGS."),
 dict(id="SRC_VICINVEST", title="Data Centres - Invest Victoria",
      publisher="Invest Victoria", url="https://invest.vic.gov.au/explore-your-sector/digital-technology/data-centres",
      doc_type="primary_government", published="2026", credibility="A",
      notes="Confirms Sustainable Data Centre Action Plan funding of $5.5 million."),
 dict(id="SRC_CEC", title="Powering the digital economy",
      publisher="Clean Energy Council",
      url="https://cleanenergycouncil.org.au/getmedia/22afe57b-17e3-4cc4-918a-6ae9964edacb/powering-the-digital-economy.pdf",
      doc_type="industry_body", published="2026-07-15", credibility="B",
      notes="References the Victorian Data Centre Strategy consultation paper (March 2026) and fast-tracking of "
            "priority projects including $51.9bn of data centre investment."),
 dict(id="SRC_NSWINQ", title="Inquiry into Data Centres (self-referred 29 January 2026)",
      publisher="NSW Legislative Council Portfolio Committee",
      url="https://www.parliament.nsw.gov.au/committees/inquiries/Pages/inquiry-details.aspx?pk=3169",
      doc_type="primary_government", published="2026-08-05", credibility="A",
      notes="Terms of reference updated 5 August 2026; public hearings held in Sydney from 29 May 2026."),
 dict(id="SRC_DCA_TAX", title="Data Centres Australia response on tax and incentives",
      publisher="Data Centres Australia",
      url="https://datacentres.org.au/data-centres-australia-welcomes-nsw-government-consultation-on-data-centre-policy/",
      doc_type="industry_body", published="2026", credibility="C",
      notes="Industry body position: 'Data centres pay all standard taxes - corporate tax, payroll tax, land tax, "
            "stamp duty, council rates and GST. They receive no special tax concessions.' Treated as a CLAIMED "
            "position requiring independent testing against revenue-office records."),
 dict(id="SRC_EPAVIC", title="Data centres - legal obligations and risk management",
      publisher="Environment Protection Authority Victoria", url="https://www.epa.vic.gov.au/data-centres",
      doc_type="primary_regulator", published="2026-08-31", credibility="A",
      notes="Victorian EPA guidance for data centre proponents/operators; general environmental duty, noise "
            "(Publication 1826.5, published 5 September 2025) and generator requirements."),
 dict(id="SRC_CISC", title="Cyber Security Legislative Reforms / Enhanced CIRMP Rules 2026",
      publisher="Critical Infrastructure Security Centre (Home Affairs)",
      url="https://www.cisc.gov.au/legislation-regulation-and-compliance/cyber-security-legislative-reforms",
      doc_type="primary_government", published="2026", credibility="A",
      notes="Security of Critical Infrastructure Amendment (2025 Measures No. 1) commenced 4 April 2025; CISC began "
            "consulting on enhanced CIRMP rules on 16 December 2025."),
 dict(id="SRC_CLAYTONUTZ", title="Enhancing response and prevention powers in relation to critical infrastructure assets",
      publisher="Clayton Utz", url="https://www.claytonutz.com/insights/2025/april/enhancing-response-and-prevention-powers-in-relation-to-critical-infrastructure-assets",
      doc_type="law_firm_analysis", published="2025-04-07", credibility="B",
      notes="2025 SOCI reforms include deeming data storage systems owned/operated for government as critical "
            "infrastructure assets and clarifying obligations for systems storing or processing business critical data."),
 dict(id="SRC_BIRD", title="Australia Sets New National Expectations for Data Centres and AI Infrastructure",
      publisher="Bird & Bird", url="https://www.twobirds.com/en/insights/2026/australia/australia-sets-new-national-expectations-for-data-centres-and-ai-infrastructure",
      doc_type="law_firm_analysis", published="2026-04-08", credibility="B",
      notes="Full text summary of the five Expectations; not legally binding; applies to new or expanded hyperscale "
            "and large-scale AI compute; small edge/enterprise facilities excluded; implementation coordinated with "
            "States and Territories via the Energy and Climate Change Ministerial Council."),
 dict(id="SRC_DISR", title="Expectations of data centres and AI infrastructure developers",
      publisher="Australian Government Department of Industry, Science and Resources",
      url="https://www.industry.gov.au/publications/expectations-data-centres-and-ai-infrastructure-developers",
      doc_type="primary_government", published="2026-03-23", credibility="A",
      notes="The primary Commonwealth instrument. To be read in full for the Observatory's Pillar C coding."),
 dict(id="SRC_REUTERS_DCD", title="NextDC S7 Australian data center to offer 612MW of capacity, OpenAI Stargate planned as customer",
      publisher="Data Center Dynamics",
      url="https://www.datacenterdynamics.com/en/news/australian-stargate-data-center-in-sydney-will-offer-612mw-of-capacity/",
      doc_type="news", published="2026-07-02", credibility="B"),
 dict(id="SRC_CAPBRIEF", title="NextDC confirms OpenAI partnership on $7.6b Sydney AI data centre build",
      publisher="Capital Brief",
      url="https://www.capitalbrief.com/briefing/nextdc-confirms-openai-partnership-on-76b-sydney-ai-data-centre-build-d10ef65f-4fca-4631-bb8a-3cd81b19ad35/",
      doc_type="news", published="2025-12-05", credibility="B",
      notes="S7 at Eastern Creek; subject to further planning work, total power capacity could reach 650 MW."),
 dict(id="SRC_NEXTDC_S7", title="S7 Sydney Data Centre - In Planning",
      publisher="NEXTDC", url="https://www.nextdc.com/data-centres/sydney-data-centres/s7-sydney",
      doc_type="primary_company", published="2026", credibility="A",
      notes="Planned for Eastern Creek; described by the proponent as a 550 MW+ hyperscale facility."),
 dict(id="SRC_GUARDIAN_MELB", title="Mega datacentre planned for outer Melbourne will be almost six times the size of Chadstone",
      publisher="The Guardian Australia",
      url="https://www.theguardian.com/australia-news/2026/jul/26/mega-datacentre-planned-for-outer-melbourne-will-be-almost-six-times-the-size-of-chadstone-shopping-centre",
      doc_type="news", published="2026-07-26", credibility="A",
      notes="Victoria's fast-track application process is getting approvals down to three months; state measures "
            "to attract data centre construction."),
 dict(id="SRC_GUARDIAN_WATER", title="Thirsty work: how the rise of massive datacentres strains Australia's drinking water supply",
      publisher="The Guardian Australia",
      url="https://www.theguardian.com/environment/2025/dec/04/thirsty-work-how-the-rise-of-massive-datacentres-strains-australias-drinking-water-supply",
      doc_type="investigation", published="2025-12-04", credibility="A",
      notes="Calls for a ban on drinking-water use for cooling; Sydney Water says its estimates of data centre water "
            "use are reviewed regularly."),
 dict(id="SRC_ABC_WATER", title="AI to take up one quarter of Sydney's water in a decade, Sydney Water says",
      publisher="ABC News", url="https://www.abc.net.au/news/2025-08-27/ai-to-take-up-one-quarter-of-sydney-water-in-a-decade/105700928",
      doc_type="news", published="2025-08-26", credibility="A",
      notes="Sydney Water: data centres could use the equivalent of 25% of the city's yearly drinking water supply by 2035."),
 dict(id="SRC_WSAA", title="Data Centres and water in Australia",
      publisher="Water Services Association of Australia",
      url="https://wsaa.asn.au/Common/Uploaded%20files/library/report/WSAA%20Data%20Centres%20and%20water%20in%20Australia%20-%20December%202025.pdf",
      doc_type="industry_body", published="2025-12-05", credibility="B"),
 dict(id="SRC_RENEW_MOSSVALE", title="Protests called as data centre developer super-sizes plans for fossil gas generation in Southern Highlands",
      publisher="RenewEconomy",
      url="https://reneweconomy.com.au/protests-called-as-data-centre-developer-super-sizes-plans-for-fossil-gas-generation-in-southern-highlands/",
      doc_type="news", published="2026-05-19", credibility="B",
      notes="Cloud Carrier and two related companies already hold council planning permission for a 14 MW gas unit "
            "and are pursuing a much larger gas generation proposal; protests called."),
 dict(id="SRC_ABC_MOSSVALE", title="Cloud Carrier proposes gas-fired power station to run AI data centres",
      publisher="ABC News", url="https://www.abc.net.au/news/2026-03-04/gas-plant-ai-data-centre-moss-vale/106405944",
      doc_type="news", published="2026-03-04", credibility="A",
      notes="On-site gas-fired engines at Moss Vale described as enough to power 70,000 homes."),
 dict(id="SRC_DCD_CDC", title="Australia's CDC files for data center in Kemps Creek, Sydney",
      publisher="Data Center Dynamics",
      url="https://www.datacenterdynamics.com/en/news/australias-cdc-files-for-data-center-in-kemps-creek-sydney/",
      doc_type="news", published="2026-08-05", credibility="B",
      notes="Marsden Park could offer more than 504 MW with potential to scale to around 1 GW; new Kemps Creek filing."),
 dict(id="SRC_NINE_MAP", title="Map exposes Australia's bold plan to become the data centre capital of the world",
      publisher="Nine / 60 Minutes Australia",
      url="https://www.nine.com.au/australia-news/map-exposes-australia-s-bold-plan-to-become-the-data-centre-capital-of-the-world-20260615-p606xw.html",
      doc_type="news", published="2026-06-16", credibility="B",
      notes="504 MW CDC data centre on track at Marsden Park; biggest campus in the Southern Hemisphere."),
 dict(id="SRC_PINSENT", title="New NSW authority launched to support approvals for data centres",
      publisher="Pinsent Masons", url="https://www.pinsentmasons.com/out-law/news/nsw-authority-for-data-centres",
      doc_type="law_firm_analysis", published="2025-09-30", credibility="B",
      notes="NSW approval-support authority: eligible projects must be valued at more than A$1bn, be primarily "
            "non-residential and be related to data centres."),
 dict(id="SRC_AIRTRUNK_PPA", title="AirTrunk clean energy / Google, AirTrunk and OX2 to add renewable energy capacity in Australia",
      publisher="AirTrunk", url="https://airtrunk.com/sustainability/clean-energy/",
      doc_type="primary_company", published="2026", credibility="B",
      notes="AirTrunk states it has signed multiple Australian renewable sourcing contracts and achieved 100% "
            "renewable energy by 2025; 25 MW solar partnership with OX2; December 2023 Google-AirTrunk-OX2 "
            "arrangement procures generation plus energy attribute certificates with time-matching."),
 dict(id="SRC_AFR_NGER", title="Data centre power emissions double over 5 years",
      publisher="Australian Financial Review",
      url="https://www.afr.com/policy/energy-and-climate/data-centre-power-emissions-double-over-five-years-20260303-p5o6vx",
      doc_type="news", published="2026-03-03", credibility="B",
      notes="Clean Energy Regulator NGERS data: emissions of the top three data centre operators (AirTrunk, CDC, "
            "Amazon) doubled in five years and rose 20% in 2024-25. Underlying CER dataset is downloadable."),
 dict(id="SRC_CONV", title="Can Australia build one of the world's largest data centres?",
      publisher="The Conversation", url="https://stories.theconversation.com/can-australia-build-one-of-the-worlds-largest-data-centres/",
      doc_type="academic", published="2026-02-10", credibility="B",
      notes="Mamre Road campus north of Western Sydney Airport earmarked as Australia's largest at 1 GW."),
 dict(id="SRC_SUBCO", title="SUBCO SMAP hypercable - the quiet infrastructure play reshaping Australia's AI connectivity",
      publisher="CertifiedStrategic.com",
      url="https://certifiedstrategic.com/insights/subco-s-smap-hypercable-the-quiet-infrastructure-play-that-will-reshape-australia-s-ai-connectivity",
      doc_type="market_research", published="2026", credibility="C",
      notes="SMAP east-west connectivity spine from March 2026; NEXTDC, CDC, Equinix and AirTrunk named as anchor "
            "operators. Low-confidence secondary source: requires confirmation from SUBCO before use."),
 dict(id="SRC_METACABLE", title="Unlocking global AI potential with next-generation subsea infrastructure (Project Waterworth)",
      publisher="Meta Engineering", url="https://engineering.fb.com/2025-02-14/connectivity/project-waterworth-ai-subsea-infrastructure/",
      doc_type="primary_company", published="2025-02-14", credibility="A",
      notes="Multi-billion dollar, multi-year cable; Australian landing point reported at Perth; depths to 7,000 m."),
 dict(id="SRC_CABLEMAP", title="Submarine Cable Map - Australia",
      publisher="TeleGeography", url="https://www.submarinecablemap.com/country/australia",
      doc_type="market_research", published="2026-09-04", credibility="A",
      notes="Authoritative machine-readable list of Australian cable systems and landing stations; intended source "
            "for the proximity field in the sites table."),
 dict(id="SRC_SMH_WSYD", title="Data centres are popping up all over Sydney. But what impact do they have on our suburbs?",
      publisher="Sydney Morning Herald",
      url="https://www.smh.com.au/national/nsw/data-centres-are-popping-up-all-over-sydney-but-what-impact-do-they-have-on-our-suburbs-20260114-p5ntv6.html",
      doc_type="investigation", published="2026-01-28", credibility="A",
      notes="Western Sydney data centre capacity increase equivalent to the average electricity load of more than "
            "10 million households; at peak they will demand almost four times as much power as the rest of the city."),
 dict(id="SRC_SUPCHAIN", title="Anthropic to Site Giant Data Center in Queensland",
      publisher="SupplyChainBrain", url="https://www.supplychainbrain.com/articles/44854-anthropic-to-site-giant-data-center-in-queensland",
      doc_type="news", published="2026", credibility="C",
      notes="Reports Anthropic plans to use part of Western Downs Digital Park (725.5 ha former feedlot, A$32bn). "
            "Requires primary confirmation before elevation to REPORTED."),
 dict(id="SRC_CHANGEORG", title="Petition: Stop data centre construction in Melton",
      publisher="Change.org (community)", url="https://www.change.org/p/stop-data-centre-construction-in-melton",
      doc_type="community", published="2026-05-31", credibility="C",
      notes="Community petition; primary artefact of local opposition, not a source of fact about the project."),
 dict(id="SRC_MELTONCC", title="City of Melton statement on data centre commentary",
      publisher="City of Melton", url="https://www.facebook.com/cityofmelton/posts/1467894358701853/",
      doc_type="community", published="2026", credibility="C",
      notes="Council statement noting growing Victorian community opposition; Victorian Farmers Federation estimate "
            "that proposed Victorian data centres would demand nine gigawatts (equivalent to four Loy Yang stations) "
            "is reported second-hand here and must be verified against the VFF primary document."),
 dict(id="SRC_NSWPORTAL", title="Mamre Road Data Centre Campus - NSW Planning Portal major project page",
      publisher="NSW Department of Planning, Housing and Infrastructure",
      url="https://www.planningportal.nsw.gov.au/major-projects/projects/mamre-road-data-centre-campus",
      doc_type="primary_planning_portal", published="2026-08-25", credibility="A",
      notes="Authoritative SSD record: 'Construction and operation of a data centre campus with a power capacity of "
            "1 GW including six four-storey data centre buildings'; departmental direction to assess cumulative "
            "impacts of the Mamre Road / Kemps Creek precinct."),
 dict(id="SRC_WA_1GW", title="WA plans for a gigawatt-scale data centre powered by renewable energy",
      publisher="6PR NewsTalk / state reporting (aggregated)",
      url="https://www.facebook.com/NewsTalk6PR/posts/1755763385699593/",
      doc_type="news", published="2026", credibility="C",
      notes="Reports a planned ~1 GW WA facility among the largest AI-focused data centres globally. Low confidence: "
            "primary WA Government or proponent confirmation outstanding."),
]

# ---------------------------------------------------------------------
# ENTITIES
# ---------------------------------------------------------------------
def E(**kw):
    kw.setdefault("fact_status", "REPORTED")
    kw.setdefault("confidence", "medium")
    kw.setdefault("as_of_date", "2026-09-18")
    return kw

ENTITIES = [
 # --- hyperscalers / AI labs ---
 E(id="ENT_MICROSOFT", name="Microsoft", entity_type="hyperscaler", domicile="United States",
   hq_country="US", website="microsoft.com", source_id="SRC_MS2026", confidence="high",
   notes="29 Australian datacentre sites across three Azure regions after the A$5bn (2023) program; "
         "A$25bn commitment to end-2029 signed alongside an MoU with the Australian Government."),
 E(id="ENT_AWS", name="Amazon Web Services", legal_name="Amazon Web Services, Inc.",
   entity_type="hyperscaler", domicile="United States", hq_country="US", website="aws.amazon.com",
   source_id="SRC_AWS2025", confidence="high",
   notes="AU$20bn 2025-2029 infrastructure commitment; Sydney and Melbourne regions."),
 E(id="ENT_GOOGLE", name="Google", legal_name="Google LLC / Alphabet Inc.", entity_type="hyperscaler",
   domicile="United States", hq_country="US", website="google.com", source_id="SRC_AIRTRUNK_PPA",
   fact_status="REPORTED", notes="Named counterparty to the AirTrunk-OX2 renewable arrangement (Dec 2023). "
   "Australian site-level footprint not yet verified in this release - see research_gaps."),
 E(id="ENT_META", name="Meta", entity_type="hyperscaler", domicile="United States", hq_country="US",
   website="meta.com", source_id="SRC_METACABLE",
   notes="Project Waterworth subsea cable proponent with an Australian landing point; domestic data centre "
         "footprint unverified in this release."),
 E(id="ENT_OPENAI", name="OpenAI", entity_type="ai_lab", domicile="United States", hq_country="US",
   website="openai.com", source_id="SRC_REUTERS_S7", confidence="high",
   notes="'OpenAI for Countries' / Stargate program; plans to help plan, build, run and buy compute from the "
         "NEXTDC S7 campus in Sydney."),
 E(id="ENT_ANTHROPIC", name="Anthropic", entity_type="ai_lab", domicile="United States", hq_country="US",
   website="anthropic.com", source_id="SRC_SUPCHAIN", fact_status="CLAIMED", confidence="low",
   notes="Reported prospective user of part of Western Downs Digital Park (Qld) and of a 5-20 GW Australian "
         "build. Not confirmed by a primary source at time of writing."),
 # --- operators / developers ---
 E(id="ENT_AIRTRUNK", name="AirTrunk", entity_type="colocation_operator", domicile="United States (Blackstone-controlled)",
   hq_country="AU", website="airtrunk.com", source_id="SRC_AIRTRUNK_BC", confidence="high",
   notes="Founded in Australia; acquired for A$24bn by a Blackstone-led consortium with CPP Investments, "
         "completed 23 December 2024 after FIRB process. Hyperscale campuses in Sydney, Melbourne and Perth."),
 E(id="ENT_NEXTDC", name="NEXTDC", entity_type="colocation_operator", domicile="Australia", hq_country="AU",
   asx_ticker="NXT", website="nextdc.com", source_id="SRC_REUTERS_S7", confidence="high",
   notes="ASX-listed; 13 HCF Certified Strategic sites across all mainland capitals plus Darwin; S7 Eastern Creek "
         "is the OpenAI-anchored 612 MW project."),
 E(id="ENT_CDC", name="CDC Data Centres", entity_type="colocation_operator", domicile="Australia / New Zealand",
   hq_country="AU", website="cdc.com", source_id="SRC_CDC2025", confidence="high",
   notes="2.5 GW across operational, construction and development pipeline; sovereign-ownership deal February 2025 "
         "kept control with Infratil, the Future Fund and CSC; enterprise value ~$17bn."),
 E(id="ENT_EQUINIX", name="Equinix", entity_type="colocation_operator", domicile="United States", hq_country="US",
   asx_ticker=None, website="equinix.com", source_id="SRC_CERTSTRAT",
   notes="10 HCF Certified Strategic Enclaves plus one Strategic Facility across Sydney, Melbourne, Canberra and Perth; "
         "hosts cloud on-ramps and the Southern Cross NEXT gateway."),
 E(id="ENT_DIGITALREALTY", name="Digital Realty", entity_type="colocation_operator", domicile="United States",
   hq_country="US", website="digitalrealty.com", source_id="SRC_CERTSTRAT",
   notes="Four HCF Certified Strategic Enclaves: SYD10, SYD11 and SYD14 at Erskine Park and MEL11 at Deer Park."),
 E(id="ENT_MACQUARIE_TG", name="Macquarie Technology Group", entity_type="colocation_operator",
   domicile="Australia", hq_country="AU", asx_ticker="MAQ", website="macquarietechnologygroup.com",
   source_id="SRC_CERTSTRAT",
   notes="Five HCF Certified Strategic sites (IC1-IC3 Sydney, IC4-IC5 Fairbairn ACT); the only vertically "
         "integrated certified facility plus certified sovereign cloud stack."),
 E(id="ENT_DCI", name="DCI Data Centers", entity_type="colocation_operator", domicile="Australia",
   hq_country="AU", website="dcidatacenters.com", source_id="SRC_CERTSTRAT",
   notes="Single HCF Certified Strategic Enclave, SYD-01 Eastern Creek."),
 E(id="ENT_CLOUDCARRIER", name="Cloud Carrier", entity_type="developer", domicile="Australia", hq_country="AU",
   website="cloudcarrier.com.au", source_id="SRC_GREENPEACE_SUB",
   notes="Proposes the Southern Highlands Data Campus at Moss Vale, with an attached 673 MW fossil-gas power "
         "station; already holds council permission for a 14 MW gas unit."),
 E(id="ENT_ZERRA", name="Zerra DC", entity_type="developer", domicile="Singapore", hq_country="SG",
   source_id="SRC_ABC_WD", fact_status="REPORTED", confidence="low",
   notes="Reported proponent of Western Downs Digital Park (Qld). Entity details unverified."),
 E(id="ENT_TELSTRA", name="Telstra", entity_type="telecom", domicile="Australia", hq_country="AU",
   asx_ticker="TLS", source_id="SRC_CERTSTRAT",
   notes="Two HCF certified sites: Deakin (ACT) Strategic Enclave and St Leonards (NSW) Strategic Enclave."),
 E(id="ENT_VANTAGE", name="Vantage Data Centers", entity_type="developer", domicile="United States",
   hq_country="US", website="vantage.com", source_id="SRC_CERTSTRAT", fact_status="GAP", confidence="low",
   notes="Placeholder: Australian sites not yet mapped in this release. AustralianSuper holds a significant "
         "minority stake in Vantage Data Centers Europe (2023) - relevant to Pillar B capital tracing."),
 # --- utilities / networks ---
 E(id="ENT_TRANSGRID", name="Transgrid", entity_type="network_business", domicile="Australia", hq_country="AU",
   website="transgrid.com.au", source_id="SRC_TRANSGRID26", confidence="high",
   notes="NSW transmission network service provider; describes itself as pension fund-owned. Publisher of the "
         "Network Capacity Allocation Policy and the 20 August 2026 Sydney Basin Network Capacity Update."),
 E(id="ENT_AUSGRID", name="Ausgrid", entity_type="network_business", domicile="Australia", hq_country="AU",
   website="ausgrid.com.au", source_id="SRC_TRANSGRIDCAP", fact_status="GAP", confidence="low",
   notes="Placeholder: distribution-level connection data for Western Sydney data centres not yet captured."),
 E(id="ENT_SYDNEYWATER", name="Sydney Water", entity_type="utility", domicile="Australia", hq_country="AU",
   website="sydneywater.com.au", source_id="SRC_ABC_WATER", confidence="high",
   notes="Named in S7 planning documents as a possible recycled-water supplier; projected data centre demand "
         "equivalent to ~25% of Greater Sydney's yearly drinking water supply by 2035."),
 E(id="ENT_CONEXA", name="coNEXA", entity_type="utility", domicile="Australia", hq_country="AU",
   source_id="SRC_REUTERS_S7", notes="Privately owned recycled water company named as a possible S7 supplier."),
 E(id="ENT_AEMO", name="AEMO", entity_type="regulator", domicile="Australia", hq_country="AU",
   website="aemo.com.au", source_id="SRC_AEMO26", confidence="high",
   notes="System operator and NEM planner; first disclosed data centre connection queue statistics in QED Q1 2026."),
 E(id="ENT_AEMC", name="AEMC", entity_type="regulator", domicile="Australia", hq_country="AU",
   website="aemc.gov.au", source_id="SRC_AEMC", confidence="high"),
 E(id="ENT_AER", name="Australian Energy Regulator", entity_type="regulator", domicile="Australia",
   hq_country="AU", website="aer.gov.au", source_id="SRC_NSWGUIDE26",
   notes="Assesses network investment for prudence and efficiency - a check on cost recovery from data centres."),
 E(id="ENT_ORIGIN", name="Origin Energy", entity_type="utility", domicile="Australia", hq_country="AU",
   asx_ticker="ORG", source_id="SRC_AIRTRUNK_PPA", fact_status="GAP", confidence="low",
   notes="Placeholder for PPA counterparty mapping; specific AirTrunk-Origin contracts not yet verified."),
 # --- investors / owners ---
 E(id="ENT_BLACKSTONE", name="Blackstone", entity_type="pe_firm", domicile="United States", hq_country="US",
   website="blackstone.com", source_id="SRC_AIRTRUNK_BC", confidence="high",
   notes="Leads the AirTrunk consortium through Blackstone Real Estate Partners, Blackstone Infrastructure "
         "Partners, Blackstone Tactical Opportunities and its private equity strategy for individual investors. "
         "Describes itself as the largest data center provider in the world."),
 E(id="ENT_CPP", name="CPP Investments (Canada Pension Plan Investment Board)", entity_type="super_fund",
   domicile="Canada", hq_country="CA", website="cppinvestments.com", source_id="SRC_CPP", confidence="high",
   notes="12% interest in AirTrunk."),
 E(id="ENT_MACQUARIE_AM", name="Macquarie Asset Management", entity_type="investor", domicile="Australia",
   hq_country="AU", source_id="SRC_INFRAINV", confidence="high",
   notes="Former holder (with PSP Investments) of the 88% AirTrunk stake sold in 2024."),
 E(id="ENT_PSP", name="PSP Investments", entity_type="super_fund", domicile="Canada", hq_country="CA",
   source_id="SRC_INFRAINV", confidence="high", notes="Former AirTrunk co-holder; exited in the 2024 transaction."),
 E(id="ENT_IFM", name="IFM Investors", entity_type="super_fund", domicile="Australia", hq_country="AU",
   website="ifminvestors.com", source_id="SRC_IA_MAMRE", confidence="high",
   notes="Owner of the 'Summit' landholding at 706-752 Mamre Road, Kemps Creek - the site of Australia's largest "
         "proposed data centre. Australian industry-superannuation capital."),
 E(id="ENT_ISPT", name="ISPT (Core Fund)", entity_type="investor", domicile="Australia", hq_country="AU",
   website="ispt.com.au", source_id="SRC_DCD_MAMRE", confidence="medium",
   notes="Listed the Mamre Road property as 'Summit'; a superannuation-owned property manager. Relationship to "
         "IFM Investors' stated ownership needs reconciliation - see research_gaps."),
 E(id="ENT_FUTUREFUND", name="Future Fund", entity_type="sovereign_wealth", domicile="Australia", hq_country="AU",
   source_id="SRC_CDC2025", confidence="high", notes="34.55% of CDC Data Centres after February 2025."),
 E(id="ENT_INFRATIL", name="Infratil", entity_type="investor", domicile="New Zealand", hq_country="NZ",
   asx_ticker=None, source_id="SRC_CDC2025", confidence="high",
   notes="49.75% of CDC Data Centres - the largest single shareholder, NZ-listed infrastructure investor."),
 E(id="ENT_CSC", name="Commonwealth Superannuation Corporation", entity_type="super_fund", domicile="Australia",
   hq_country="AU", source_id="SRC_CDC2025", confidence="high",
   notes="Retains 12.04% of CDC after running the late-2024 sale process that tested international bids."),
 E(id="ENT_AUSTRALIANSUPER", name="AustralianSuper", entity_type="super_fund", domicile="Australia",
   hq_country="AU", website="australiansuper.com", source_id="SRC_CERTSTRAT", fact_status="GAP", confidence="low",
   notes="Placeholder: domestic superannuation exposure to data centres (including via Vantage Europe and "
         "reported 2024 commitments) not yet traced. See research_gaps RG-004."),
 E(id="ENT_MAMRE_OWNER", name="CDC management / Greg Boorer", entity_type="other", domicile="Australia",
   hq_country="AU", source_id="SRC_CDC2025", notes="3.66% of CDC as the largest individual shareholder."),
 # --- government ---
 E(id="ENT_DISR", name="Department of Industry, Science and Resources (Cth)", entity_type="government_agency",
   domicile="Australia", hq_country="AU", source_id="SRC_DISR", fact_status="VERIFIED", confidence="high"),
 E(id="ENT_OFFICE_AI", name="Office of AI (Commonwealth, PM&C)", entity_type="government_agency",
   domicile="Australia", hq_country="AU", source_id="SRC_REUTERS_AI", confidence="high",
   notes="Announced 15 July 2026 to sit within the Department of the Prime Minister and Cabinet and coordinate a "
         "whole-of-government approach to AI standards."),
 E(id="ENT_NSW_DPHI", name="NSW Department of Planning, Housing and Infrastructure", entity_type="regulator",
   domicile="Australia", hq_country="AU", source_id="SRC_NSWGUIDE26", fact_status="VERIFIED", confidence="high"),
 E(id="ENT_NSW_EPA", name="NSW Environment Protection Authority", entity_type="regulator", domicile="Australia",
   hq_country="AU", source_id="SRC_IA_MAMRE", confidence="high"),
 E(id="ENT_NSW_TREASURY", name="NSW Treasury (Office of the Treasurer)", entity_type="government_agency",
   domicile="Australia", hq_country="AU", source_id="SRC_ABCNSW26",
   notes="Treasurer Daniel Mookhey announced the NSW Data Centre Guidelines and fast-track pathway."),
 E(id="ENT_IPART", name="IPART (Independent Pricing and Regulatory Tribunal NSW)", entity_type="regulator",
   domicile="Australia", hq_country="AU", source_id="SRC_ABCNSW26",
   notes="Commissioned to review water pricing for data centres to protect network users and manage drought risk."),
 E(id="ENT_VIC_DJSIR", name="Victorian Department of Jobs, Skills, Industry and Regions", entity_type="government_agency",
   domicile="Australia", hq_country="AU", source_id="SRC_VICPLAN", fact_status="VERIFIED", confidence="high"),
 E(id="ENT_EPA_VIC", name="Environment Protection Authority Victoria", entity_type="regulator", domicile="Australia",
   hq_country="AU", source_id="SRC_EPAVIC", fact_status="VERIFIED", confidence="high"),
 E(id="ENT_DTA", name="Digital Transformation Agency", entity_type="government_agency", domicile="Australia",
   hq_country="AU", source_id="SRC_CERTSTRAT",
   notes="Administers the Hosting Certification Framework (Certified Strategic / Certified Assured)."),
 E(id="ENT_CISC", name="Critical Infrastructure Security Centre (Home Affairs)", entity_type="regulator",
   domicile="Australia", hq_country="AU", source_id="SRC_CISC", fact_status="VERIFIED", confidence="high"),
 E(id="ENT_CER", name="Clean Energy Regulator", entity_type="regulator", domicile="Australia", hq_country="AU",
   website="cleanenergyregulator.gov.au", source_id="SRC_AFR_NGER", confidence="high",
   notes="Administers the National Greenhouse and Energy Reporting scheme, the Renewable Energy Target (LGCs) and "
         "the Safeguard Mechanism - the three datasets the Observatory uses to test renewable claims."),
 E(id="ENT_FIRB", name="Foreign Investment Review Board / Treasurer (Cth)", entity_type="regulator",
   domicile="Australia", hq_country="AU", source_id="SRC_BC_DEAL", fact_status="VERIFIED", confidence="high"),
 E(id="ENT_NSWLC", name="NSW Legislative Council Portfolio Committee (data centres inquiry)",
   entity_type="government_agency", domicile="Australia", hq_country="AU", source_id="SRC_NSWINQ",
   fact_status="VERIFIED", confidence="high"),
 E(id="ENT_PENRITH_CC", name="Penrith City Council", entity_type="council", domicile="Australia", hq_country="AU",
   source_id="SRC_IA_MAMRE", confidence="high",
   notes="Objected to the Mamre Road campus, arguing the site is 'not suitable for a proposed development of this scale'."),
 E(id="ENT_MELTON_CC", name="City of Melton", entity_type="council", domicile="Australia", hq_country="AU",
   source_id="SRC_MELTONCC", fact_status="REPORTED", confidence="low"),
 E(id="ENT_WESTERN_DOWNS", name="Western Downs Regional Council", entity_type="council", domicile="Australia",
   hq_country="AU", source_id="SRC_ABC_WD", confidence="medium"),
 E(id="ENT_ENERGY_QLD", name="Energy Queensland", entity_type="utility", domicile="Australia", hq_country="AU",
   source_id="SRC_ABC_WD", confidence="medium"),
 # --- community / advocacy ---
 E(id="ENT_STOPTHESLOP", name="Stop the Slop", entity_type="community_group", domicile="Australia", hq_country="AU",
   source_id="SRC_ABCNSW26", confidence="high",
   notes="Western Sydney campaign opposing data centre expansion in residential suburbs; spokesperson Sophie Shanaaz."),
 E(id="ENT_GREENPEACE", name="Greenpeace Australia Pacific", entity_type="other", domicile="Australia",
   hq_country="AU", source_id="SRC_GREENPEACE_SUB", confidence="high",
   notes="Submission No 120 to the NSW data centres inquiry; publisher of 'Energy Vampires' (May 2026)."),
 E(id="ENT_CLIMATECOUNCIL", name="Climate Council", entity_type="other", domicile="Australia", hq_country="AU",
   source_id="SRC_BB2026", confidence="high",
   notes="Modelled +26% NSW power prices by 2035 without new renewable generation and storage."),
 E(id="ENT_NCC", name="Nature Conservation Council NSW", entity_type="other", domicile="Australia", hq_country="AU",
   source_id="SRC_GREENPEACE_SUB", confidence="medium",
   notes="Recommended disclosure of water projections at the planning stage and a bar on siting in water-poor areas."),
 E(id="ENT_MAMRE_SCHOOL", name="Mamre Anglican School (Anglican Schools Corporation)", entity_type="other",
   domicile="Australia", hq_country="AU", source_id="SRC_IA_MAMRE", confidence="high",
   notes="Directly across the road from the Summit site; raised air quality, noise and emergency-incident concerns; "
         "has identified an alternative site and sought government help to relocate."),
 E(id="ENT_CATH_PARRA", name="Catholic Church of the Diocese of Parramatta", entity_type="other",
   domicile="Australia", hq_country="AU", source_id="SRC_IA_MAMRE", confidence="high",
   notes="Objected to the Mamre Road proposal, citing cumulative impacts, emergency access, servicing resilience "
         "and stormwater feasibility affecting Emmaus Retirement Village."),
 E(id="ENT_CATH_SCHOOLS", name="Catholic Schools Parramatta Diocese", entity_type="other", domicile="Australia",
   hq_country="AU", source_id="SRC_IA_MAMRE", confidence="high",
   notes="Did not object in principle but sought limits on air quality impacts and diesel generator testing outside "
         "school hours and peak outdoor activity periods."),
 E(id="ENT_DATA_CENTRES_AU", name="Data Centres Australia", entity_type="industry_body", domicile="Australia",
   hq_country="AU", source_id="SRC_DCA_TAX", confidence="medium"),
 E(id="ENT_VFF", name="Victorian Farmers Federation", entity_type="industry_body", domicile="Australia",
   hq_country="AU", source_id="SRC_MELTONCC", fact_status="CLAIMED", confidence="low",
   notes="Reported estimate that data centres proposed for Victoria would demand nine gigawatts, equivalent to "
         "four Loy Yang power stations. Secondary reporting only - primary VFF document required."),
 E(id="ENT_SUBCO", name="SUBCO Consortium", entity_type="telecom", domicile="Australia", hq_country="AU",
   source_id="SRC_SUBCO", fact_status="CLAIMED", confidence="low",
   notes="Reported SMAP east-west 'hypercable' from March 2026 with NEXTDC, CDC, Equinix and AirTrunk as anchors. "
         "Unverified."),
 E(id="ENT_OX2", name="OX2", entity_type="developer", domicile="Sweden", hq_country="SE",
   source_id="SRC_AIRTRUNK_PPA", notes="Counterparty to the Google-AirTrunk-OX2 renewable arrangement (Dec 2023)."),
]

# ---------------------------------------------------------------------
# OWNERSHIP
# ---------------------------------------------------------------------
OWNERSHIP = [
 dict(holder_id="ENT_BLACKSTONE", target_id="ENT_AIRTRUNK", stake_pct=88.0, instrument="equity",
      effective_from="2024-12-23", event="acquisition of the Macquarie AM / PSP stake",
      transaction_value_aud=24e9, firb_reviewed=1, firb_outcome="approved (transaction completed following regulatory approvals)",
      source_id="SRC_AIRTRUNK_BC", fact_status="VERIFIED", confidence="high", as_of_date="2024-12-23",
      notes="Consortium vehicles: Blackstone Real Estate Partners, Blackstone Infrastructure Partners, "
            "Blackstone Tactical Opportunities, Blackstone PE strategy for individual investors."),
 dict(holder_id="ENT_CPP", target_id="ENT_AIRTRUNK", stake_pct=12.0, instrument="equity",
      effective_from="2024-12-23", event="acquisition", source_id="SRC_CPP",
      fact_status="VERIFIED", confidence="high", as_of_date="2024-12-23"),
 dict(holder_id="ENT_MACQUARIE_AM", target_id="ENT_AIRTRUNK", stake_pct=None, instrument="equity",
      effective_to="2024-12-23", event="exit (part of the 88% stake sold)", source_id="SRC_INFRAINV",
      fact_status="REPORTED", confidence="medium", as_of_date="2024-09-05"),
 dict(holder_id="ENT_PSP", target_id="ENT_AIRTRUNK", stake_pct=None, instrument="equity",
      effective_to="2024-12-23", event="exit (part of the 88% stake sold)", source_id="SRC_INFRAINV",
      fact_status="REPORTED", confidence="medium", as_of_date="2024-09-05"),
 dict(holder_id="ENT_INFRATIL", target_id="ENT_CDC", stake_pct=49.75, instrument="equity",
      effective_from="2025-02-18", event="pre-emptive acquisition of 1.58% from CSC",
      source_id="SRC_CDC2025", fact_status="VERIFIED", confidence="high", as_of_date="2025-02-18"),
 dict(holder_id="ENT_FUTUREFUND", target_id="ENT_CDC", stake_pct=34.55, instrument="equity",
      effective_from="2025-02-18", event="pre-emptive acquisition of 10.46% from CSC",
      source_id="SRC_CDC2025", fact_status="VERIFIED", confidence="high", as_of_date="2025-02-18"),
 dict(holder_id="ENT_CSC", target_id="ENT_CDC", stake_pct=12.04, instrument="equity",
      effective_from="2025-02-18", event="retained after sale process", source_id="SRC_CDC2025",
      fact_status="VERIFIED", confidence="high", as_of_date="2025-02-18"),
 dict(holder_id="ENT_MAMRE_OWNER", target_id="ENT_CDC", stake_pct=3.66, instrument="equity",
      effective_from="2025-02-18", event="management holding", source_id="SRC_CDC2025",
      fact_status="VERIFIED", confidence="high", as_of_date="2025-02-18"),
]

# ---------------------------------------------------------------------
# SITES  (Pillar A)
# ---------------------------------------------------------------------
def S(**kw):
    kw.setdefault("market", "NEM")
    kw.setdefault("fact_status", "REPORTED")
    kw.setdefault("confidence", "medium")
    kw.setdefault("as_of_date", "2026-09-18")
    kw.setdefault("hcf_certified", "unknown")
    return kw

SITES = [
 # --- NSW: AirTrunk ---
 S(id="SITE_AIRTRUNK_SYD1", name="AirTrunk SYD1 (Huntingwood)", operator_id="ENT_AIRTRUNK",
   suburb="Huntingwood", lga="Blacktown City Council", state="NSW", status="operational",
   hcf_certified="certified_strategic", source_id="SRC_CERTSTRAT",
   notes="HCF Certified Strategic Facility in the 20-100 MW band. Campus includes co-located battery storage "
         "referenced by the NSW Government as a grid-flexibility exemplar."),
 S(id="SITE_AIRTRUNK_SYD2", name="AirTrunk SYD2 (Lane Cove)", operator_id="ENT_AIRTRUNK",
   suburb="Lane Cove", lga="Lane Cove Council", state="NSW", status="operational",
   hcf_certified="certified_strategic", source_id="SRC_CERTSTRAT",
   notes="HCF Certified Strategic Facility, 20-100 MW band. Located in the lower north shore industrial park that "
         "ABC and the BBC report as having four further data centres in the pipeline; residents report noise at "
         "350 m. Site-code mapping to AirTrunk's own nomenclature unverified - see research_gaps."),
 S(id="SITE_AIRTRUNK_SYD3", name="AirTrunk SYD3 (Sydney West)", operator_id="ENT_AIRTRUNK",
   suburb="Eastern Creek / Huntingwood corridor", lga="Blacktown City Council", state="NSW",
   status="operational", source_id="SRC_CERTSTRAT", fact_status="GAP", confidence="low",
   notes="Referenced in secondary market data as SYD3 Sydney West. Capacity and status to be confirmed from "
         "the NSW Planning Portal - see research_gaps RG-002."),
 S(id="SITE_MAMRE_ROAD", name="Mamre Road Data Centre Campus ('Summit', understood to be AirTrunk SYD4)",
   operator_id="ENT_AIRTRUNK", owner_id="ENT_IFM", suburb="Kemps Creek", lga="Penrith City Council",
   state="NSW", status="lodged", proponent="KNBDC SYD4 Pty Ltd", it_capacity_mw=1000.0, max_capacity_mw=1200.0,
   campus_area_ha=52.0, gfa_sqm=245000.0, capital_cost_aud=5e9,
   construction_jobs=500, operational_jobs=500,
   hcf_certified="unknown", source_id="SRC_NSWPORTAL", fact_status="VERIFIED", confidence="high",
   as_of_date="2026-08-25",
   notes="NSW Planning Portal: 'Construction and operation of a data centre campus with a power capacity of 1 GW "
         "including six four-storey data centre buildings'. Proposal documents put power capacity at 1.2 GW. "
         "Six buildings, 728 cooling units, 846 diesel back-up generators, >18,000 kL diesel storage, lithium-ion "
         "batteries, ~22.4 million litres of water per year. Land held by IFM Investors (listed by ISPT as 'Summit'); "
         "AirTrunk identified as buyer, conditional on approval of the 1 GW application. First Australian project "
         "above 1 GW. EIS commits to 100% renewable electricity procurement by 2030."),
 # --- NSW: NEXTDC ---
 S(id="SITE_NEXTDC_S7", name="NEXTDC S7 Sydney (Eastern Creek)", operator_id="ENT_NEXTDC",
   anchor_tenant_id="ENT_OPENAI", suburb="Eastern Creek", lga="Blacktown City Council", state="NSW",
   status="lodged", it_capacity_mw=612.0, max_capacity_mw=650.0, capital_cost_aud=7.6e9,
   source_id="SRC_REUTERS_S7", confidence="high", as_of_date="2026-07-23",
   notes="Planning documents lodged April 2026 for a 612 MW facility; proponent page describes 550 MW+; Capital "
         "Brief reported potential total capacity of 650 MW and a $7.6bn build with OpenAI as anchor. Would be "
         "among the largest AI data centres in the world. OpenAI to help plan, build, run and buy compute."),
 S(id="SITE_NEXTDC_S1", name="NEXTDC S1 Sydney", operator_id="ENT_NEXTDC", suburb="Sydney",
   lga=None, state="NSW", status="operational", hcf_certified="certified_strategic",
   source_id="SRC_CERTSTRAT", notes="HCF Certified Strategic."),
 S(id="SITE_NEXTDC_S2", name="NEXTDC S2 Sydney", operator_id="ENT_NEXTDC", suburb="Sydney",
   state="NSW", status="operational", hcf_certified="certified_strategic", source_id="SRC_CERTSTRAT"),
 S(id="SITE_NEXTDC_S3", name="NEXTDC S3 Sydney", operator_id="ENT_NEXTDC", suburb="Sydney",
   state="NSW", status="operational", hcf_certified="certified_strategic", source_id="SRC_CERTSTRAT",
   notes="20-100 MW enclave."),
 # --- NSW: CDC ---
 S(id="SITE_CDC_EC", name="CDC Eastern Creek campus (EC1-EC4)", operator_id="ENT_CDC",
   suburb="Eastern Creek", lga="Blacktown City Council", state="NSW", status="operational",
   hcf_certified="certified_strategic", source_id="SRC_CERTSTRAT",
   notes="Four HCF Certified Strategic sites."),
 S(id="SITE_CDC_MARSDEN", name="CDC Marsden Park campus", operator_id="ENT_CDC", suburb="Marsden Park",
   lga="Blacktown City Council", state="NSW", status="under_construction",
   it_capacity_mw=504.0, max_capacity_mw=1000.0, source_id="SRC_DCD_CDC", confidence="high",
   as_of_date="2026-08-05",
   notes="Ground broken October 2024; described as the largest data centre campus in the Southern Hemisphere when "
         "complete; 504 MW with potential to scale to around 1 GW. BBC reports the facility is being built about "
         "100 m from a local community."),
 S(id="SITE_CDC_KEMPS", name="CDC Kemps Creek (new filing)", operator_id="ENT_CDC", suburb="Kemps Creek",
   lga="Penrith City Council", state="NSW", status="lodged", source_id="SRC_DCD_CDC",
   as_of_date="2026-08-05", notes="Filed August 2026; capacity not yet disclosed."),
 # --- NSW: Cloud Carrier gas campus ---
 S(id="SITE_CLOUDCARRIER_SH", name="Cloud Carrier Southern Highlands Data Campus", operator_id="ENT_CLOUDCARRIER",
   suburb="Moss Vale", lga="Wingecarribee Shire Council", state="NSW", status="lodged",
   campus_area_ha=67.0, max_capacity_mw=700.0, source_id="SRC_GREENPEACE_SUB", confidence="high",
   as_of_date="2026-03-27",
   notes="67-hectare campus. A 673 MW fossil-gas power station ('Southern Highlands Data Campus Power Station') is "
         "proposed to serve it, bringing total project capacity to ~700 MW. No EIS published at the time of the "
         "Greenpeace submission; a September 2025 Request for SEARs claimed the gas generation would produce lower "
         "emissions than the coal-dominated grid. Greenpeace estimates ~2.4 Mt CO2-e per year on reciprocating-"
         "engine assumptions. A 14 MW gas unit already holds council planning permission."),
 # --- NSW: other ---
 S(id="SITE_DR_ERSKINE", name="Digital Realty Erskine Park (SYD10, SYD11, SYD14)", operator_id="ENT_DIGITALREALTY",
   suburb="Erskine Park", lga="Penrith City Council", state="NSW", status="operational",
   hcf_certified="certified_strategic", source_id="SRC_CERTSTRAT", notes="20-100 MW band enclaves."),
 S(id="SITE_DCI_SYD01", name="DCI SYD-01 Eastern Creek", operator_id="ENT_DCI", suburb="Eastern Creek",
   lga="Blacktown City Council", state="NSW", status="operational", hcf_certified="certified_strategic",
   source_id="SRC_CERTSTRAT"),
 S(id="SITE_MACQ_IC3", name="Macquarie IC3 'Super West' (Macquarie Park)", operator_id="ENT_MACQUARIE_TG",
   suburb="Macquarie Park", lga="City of Ryde", state="NSW", status="operational",
   hcf_certified="certified_strategic", source_id="SRC_CERTSTRAT",
   notes="Purpose-built AI-ready certified data centre with direct-to-chip liquid cooling."),
 S(id="SITE_MACQ_IC12", name="Macquarie IC1 / IC2 Strategic Enclaves (Sydney)", operator_id="ENT_MACQUARIE_TG",
   suburb="Sydney", state="NSW", status="operational", hcf_certified="certified_strategic",
   source_id="SRC_CERTSTRAT"),
 S(id="SITE_EQUINIX_SYD", name="Equinix Sydney (SY3-SY7)", operator_id="ENT_EQUINIX", suburb="Sydney",
   state="NSW", status="operational", hcf_certified="certified_strategic", source_id="SRC_CERTSTRAT",
   notes="Adjacent to International Business Exchange facilities hosting AWS, Azure and Google Cloud on-ramps; "
         "gateway for the Southern Cross NEXT subsea cable."),
 S(id="SITE_TELSTRA_STLEON", name="Telstra St Leonards Strategic Enclave", operator_id="ENT_TELSTRA",
   suburb="St Leonards", state="NSW", status="operational", hcf_certified="certified_strategic",
   source_id="SRC_CERTSTRAT", notes="Below 5 MW."),
 S(id="SITE_STOCKLAND_MP", name="Stockland Macquarie Park Stage 1 data centre", operator_id=None,
   suburb="Macquarie Park", lga="City of Ryde", state="NSW", status="under_construction",
   capital_cost_aud=264e6, source_id="SRC_CERTSTRAT", fact_status="CLAIMED", confidence="low",
   notes="Five-storey data centre, A$264m; reported to be for AWS with a north-zone start in September 2026. "
         "Third-party source only - see research_gaps."),
 # --- VIC ---
 S(id="SITE_NEXTDC_M4", name="NEXTDC M4 Melbourne (Fishermans Bend)", operator_id="ENT_NEXTDC",
   suburb="Port Melbourne (Fishermans Bend)", lga="City of Port Phillip", state="VIC", status="approved",
   it_capacity_mw=162.0, capital_cost_aud=2e9, source_id="SRC_CERTSTRAT", confidence="high",
   as_of_date="2026-01-31",
   notes="Victorian Government development approval January 2026. Designed for AI, defence and sovereign technology "
         "workloads; rack densities above 1,000 kW; direct-to-chip liquid cooling."),
 S(id="SITE_CDC_LAVERTON", name="CDC Laverton campus (Melbourne south-west)", operator_id="ENT_CDC",
   suburb="Laverton", lga="City of Wyndham", state="VIC", status="under_construction",
   it_capacity_mw=150.0, capital_cost_aud=2.7e9, source_id="SRC_CDC2025", confidence="high",
   as_of_date="2025-02-18", notes="Phase one of a multi-phase campus; construction commenced early 2025."),
 S(id="SITE_CDC_BROOKLYN", name="CDC Brooklyn (Melbourne)", operator_id="ENT_CDC", suburb="Brooklyn",
   state="VIC", status="operational", hcf_certified="certified_strategic", source_id="SRC_CERTSTRAT"),
 S(id="SITE_AIRTRUNK_MEL1", name="AirTrunk MEL1 (Derrimut)", operator_id="ENT_AIRTRUNK", suburb="Derrimut",
   state="VIC", status="operational", hcf_certified="certified_strategic", source_id="SRC_CERTSTRAT",
   notes="20-100 MW band."),
 S(id="SITE_DR_MEL11", name="Digital Realty MEL11 (Deer Park)", operator_id="ENT_DIGITALREALTY",
   suburb="Deer Park", state="VIC", status="operational", hcf_certified="certified_strategic",
   source_id="SRC_CERTSTRAT"),
 S(id="SITE_NEXTDC_M123", name="NEXTDC M1 / M2 / M3 Melbourne", operator_id="ENT_NEXTDC", suburb="Melbourne",
   state="VIC", status="operational", hcf_certified="certified_strategic", source_id="SRC_CERTSTRAT",
   notes="M2 and M3 are 20-100 MW enclaves."),
 S(id="SITE_EQUINIX_MEL", name="Equinix Melbourne (ME1, ME2, ME4)", operator_id="ENT_EQUINIX", suburb="Melbourne",
   state="VIC", status="operational", hcf_certified="certified_strategic", source_id="SRC_CERTSTRAT"),
 S(id="SITE_MELTON_SYNCLINE", name="Syncline Energy Melton data centre hub (proposed)", operator_id=None,
   suburb="Melton", lga="City of Melton", state="VIC", status="lodged", source_id="SRC_MELTONCC",
   fact_status="CLAIMED", confidence="low", as_of_date="2026-07-27",
   notes="Residents rallied against the proposal; concerns raised about siting on 'Green Wedge' land, water for "
         "cooling, grid capacity and diesel/gas back-up generation. Proponent identity, capacity and application "
         "reference unverified - see research_gaps RG-011."),
 S(id="SITE_SOUTH_MORANG", name="South Morang data centre (approved, ~A$1bn)", operator_id=None,
   suburb="South Morang", lga="City of Whittlesea", state="VIC", status="approved",
   source_id="SRC_MELTONCC", fact_status="CLAIMED", confidence="low", as_of_date="2026-08-01",
   notes="Reported as a newly approved ~A$1bn facility that drew community backlash. Operator and application "
         "reference unverified - see research_gaps RG-011."),
 # --- QLD ---
 S(id="SITE_WESTERN_DOWNS", name="Western Downs Digital Park", operator_id="ENT_ZERRA",
   anchor_tenant_id="ENT_ANTHROPIC", suburb="Western Downs (former feedlot, ~250 km west of Brisbane)",
   lga="Western Downs Regional Council", state="QLD", market="NEM", status="lodged",
   it_capacity_mw=1440.0, max_capacity_mw=2160.0, campus_area_ha=725.5, capital_cost_aud=31.9e9,
   source_id="SRC_ABC_WD", confidence="medium", as_of_date="2026-09-14",
   notes="Australia's largest proposed data centre. Up to four AI-ready buildings of 360 MW each = 1.44 GW of IT "
         "capacity; 2.16 GW total peak capacity, roughly a quarter of Queensland's peak demand and equivalent to "
         "the load of ~1.5 million average homes. Development application lodged with Western Downs Regional "
         "Council; Energy Queensland referenced in reporting; Anthropic reported as a prospective user "
         "(unverified - see research_gaps RG-012)."),
 # --- ACT ---
 S(id="SITE_CDC_CANBERRA", name="CDC Canberra (Fyshwick F1-F2, Hume H1-H5)", operator_id="ENT_CDC",
   suburb="Fyshwick / Hume", state="ACT", status="operational", hcf_certified="certified_strategic",
   source_id="SRC_CERTSTRAT", notes="Nine HCF Certified Strategic sites across two precincts."),
 S(id="SITE_MACQ_FAIRBAIRN", name="Macquarie IC4 / IC5 Fairbairn (ACT)", operator_id="ENT_MACQUARIE_TG",
   suburb="Fairbairn", state="ACT", status="operational", hcf_certified="certified_strategic",
   source_id="SRC_CERTSTRAT"),
 S(id="SITE_NEXTDC_C1", name="NEXTDC C1 Canberra", operator_id="ENT_NEXTDC", suburb="Canberra", state="ACT",
   status="operational", hcf_certified="certified_strategic", source_id="SRC_CERTSTRAT"),
 S(id="SITE_EQUINIX_CA1", name="Equinix CA1 Canberra", operator_id="ENT_EQUINIX", suburb="Canberra", state="ACT",
   status="operational", hcf_certified="certified_strategic", source_id="SRC_CERTSTRAT"),
 S(id="SITE_TELSTRA_DEAKIN", name="Telstra Deakin Strategic Enclave (ACT)", operator_id="ENT_TELSTRA",
   suburb="Deakin", state="ACT", status="operational", hcf_certified="certified_strategic",
   source_id="SRC_CERTSTRAT", notes="2.5-20 MW band."),
 # --- WA (WEM - outside the NEM) ---
 S(id="SITE_NEXTDC_P12", name="NEXTDC P1 / P2 Perth", operator_id="ENT_NEXTDC", suburb="Perth", state="WA",
   market="WEM", status="operational", hcf_certified="certified_strategic", source_id="SRC_CERTSTRAT",
   notes="Only HCF Certified Strategic facilities in WA in the directory; WA hosts 15 operational sites across "
         "the South West Interconnected System per AEMO."),
 S(id="SITE_EQUINIX_PER", name="Equinix Perth (PE2, PE3)", operator_id="ENT_EQUINIX", suburb="Perth", state="WA",
   market="WEM", status="operational", hcf_certified="certified_strategic", source_id="SRC_CERTSTRAT"),
 S(id="SITE_WA_1GW", name="Proposed ~1 GW WA renewable-powered data centre", operator_id=None, suburb=None,
   state="WA", market="WEM", status="rumoured", max_capacity_mw=1000.0, source_id="SRC_WA_1GW",
   fact_status="CLAIMED", confidence="low", as_of_date="2026-09-01",
   notes="Reported as a planned WA facility that at full scale could reach ~1 GW, placing it among the largest "
         "AI-focused data centres globally. No primary confirmation located - see research_gaps RG-010."),
 # --- SA / NT / TAS ---
 S(id="SITE_NEXTDC_A1", name="NEXTDC A1 Adelaide", operator_id="ENT_NEXTDC", suburb="Adelaide", state="SA",
   status="operational", hcf_certified="certified_strategic", source_id="SRC_CERTSTRAT",
   notes="Only HCF Certified Strategic facility in Adelaide in the directory."),
 S(id="SITE_NEXTDC_D1", name="NEXTDC D1 Darwin", operator_id="ENT_NEXTDC", suburb="Darwin", state="NT",
   market="NT", status="operational", hcf_certified="certified_strategic", source_id="SRC_CERTSTRAT",
   notes="Only HCF Certified Strategic facility in the NT; Darwin is outside the NEM (NT has its own "
         "system, and the NT dissented from the July 2026 ECMC data centre agreement)."),
 # --- Hyperscaler national footprints (no site-level verification yet) ---
 S(id="SITE_MS_AU_FLEET", name="Microsoft Australia datacentre fleet (29 sites, 3 Azure regions)",
   operator_id="ENT_MICROSOFT", state="Multi", market="Multi", status="operational",
   source_id="SRC_MS2026", fact_status="CLAIMED", confidence="high", as_of_date="2026-04-23",
   notes="Company-reported count following the A$5bn (2023) program. Site addresses, capacities and grid "
         "connection points not disclosed - see research_gaps RG-013."),
 S(id="SITE_AWS_AU_FLEET", name="AWS Australia (Sydney and Melbourne regions, 2025-29 build)",
   operator_id="ENT_AWS", state="Multi", market="Multi", status="under_construction",
   source_id="SRC_AWS2025", fact_status="CLAIMED", confidence="high", as_of_date="2025-06-14",
   notes="AU$20bn commitment to 2029. Individual sites not publicly mapped - see research_gaps RG-013."),
]

# ---------------------------------------------------------------------
# APPLICATIONS / REGULATORY PATHWAYS
# ---------------------------------------------------------------------
APPLICATIONS = [
 dict(site_id="SITE_MAMRE_ROAD", jurisdiction="NSW Department of Planning, Housing and Infrastructure",
      pathway="state_significant_development", reference="SSD-92743706", lodged="2025-12",
      outcome="additional_info_requested", decision_maker="NSW DPHI (consent authority), NSW EPA (advisory)",
      capacity_mw_in_app=1000.0,
      conditions_summary="Department directed assessment of cumulative impacts in the Mamre Road / Kemps Creek "
                         "precinct; NSW EPA requested further information on air quality, noise, greenhouse gas "
                         "emissions and waste storage.",
      source_id="SRC_NSWPORTAL", fact_status="VERIFIED", confidence="high", as_of_date="2026-08-25",
      notes="EIS finalised February 2026 by Willowtree Planning. NSW EPA advice dated 10 April 2026 states the EIS "
            "'does not provide the information required to allow us to complete our assessment'."),
 dict(site_id="SITE_NEXTDC_S7", jurisdiction="NSW Department of Planning, Housing and Infrastructure",
      pathway="state_significant_development", lodged="2026-04", outcome="under_assessment",
      capacity_mw_in_app=612.0,
      conditions_summary="Subject to the post-late-2025 NSW requirements for a fixed PUE limit (cap of 1.3) and "
                         "disclosed water use; one of six projects assessed against the new state-based rules.",
      source_id="SRC_REUTERS_S7", fact_status="REPORTED", confidence="high", as_of_date="2026-07-23"),
 dict(site_id="SITE_CDC_MARSDEN", jurisdiction="NSW Department of Planning, Housing and Infrastructure",
      pathway="state_significant_development", decided="2025-11", outcome="approved",
      capacity_mw_in_app=504.0, source_id="SRC_CERTSTRAT", fact_status="REPORTED", confidence="medium",
      notes="Reported NSW planning approval November 2025, following an October 2024 ground-breaking."),
 dict(site_id="SITE_NEXTDC_M4", jurisdiction="Victorian Government (planning scheme amendment / ministerial approval)",
      pathway="fast_track_scheme", decided="2026-01", outcome="approved", capacity_mw_in_app=162.0,
      source_id="SRC_CERTSTRAT", fact_status="REPORTED", confidence="medium",
      notes="Described as Victorian Government development approval; consistent with Victoria's fast-track "
            "process reported to reduce approvals to about three months."),
 dict(site_id="SITE_CLOUDCARRIER_SH", jurisdiction="NSW DPHI (Request for SEARs) / Wingecarribee Shire Council",
      pathway="state_significant_development", lodged="2025-09", outcome="under_assessment",
      capacity_mw_in_app=700.0, source_id="SRC_GREENPEACE_SUB", fact_status="REPORTED", confidence="medium",
      notes="Request for SEARs September 2025 for the campus and the 673 MW gas power station. A separate 14 MW gas "
            "unit already holds council planning permission."),
 dict(site_id="SITE_WESTERN_DOWNS", jurisdiction="Western Downs Regional Council",
      pathway="local_council", outcome="under_assessment", capacity_mw_in_app=2160.0,
      source_id="SRC_ABC_WD", fact_status="REPORTED", confidence="medium", as_of_date="2026-09-14",
      notes="Queensland sits outside the scope of the NSW fast-track framework and dissented (with the NT) from the "
            "July 2026 ECMC agreement on mandatory renewable offsetting."),
]

LAND_EVENTS = [
 dict(site_id="SITE_MAMRE_ROAD", event_date="2025-11-11", event_type="option",
      seller_id="ENT_IFM", buyer_id="ENT_AIRTRUNK", area_ha=52.0,
      conditionality="Sale of the land is conditional on approval of the 1 GW data centre application",
      source_id="SRC_WMEDIA_ISPT", fact_status="REPORTED", confidence="medium", as_of_date="2025-11-11",
      notes="ISPT lists the property as 'Summit', masterplanned for 245,000 sqm. Reported value of the wider "
            "AirTrunk commitment exceeds A$5bn. Reconcile ISPT/IFM ownership - see research_gaps RG-005."),
]

# ---------------------------------------------------------------------
# POWER + WATER PROFILES  (Pillar A engineering detail / Pillar E evidence)
# ---------------------------------------------------------------------
POWER = [
 dict(site_id="SITE_MAMRE_ROAD", connection_type="tbd", network_business_id="ENT_TRANSGRID",
      max_demand_mw=1200.0, genset_count=846, genset_fuel="diesel", diesel_storage_kl=18000.0,
      emission_standard="to be assessed against NSW Clean Air Regulation Group 6 limits under the 2026 Guidelines",
      grid_services_role="load only (no demand flexibility or storage committed in the EIS as reviewed)",
      source_id="SRC_IA_MAMRE", fact_status="REPORTED", confidence="high", as_of_date="2026-04-30",
      notes="846 diesel back-up generators and >18,000 kL of diesel storage; lithium-ion batteries present. "
            "Greenpeace analysis of the EIS: peak grid emissions of 1,297,028 t CO2-e in 2032 and 33,041,033 t "
            "over the project life; 2,888,431 t in a slow-decarbonisation scenario peaking in 2037; substituting "
            "'renewable diesel' in back-up generators reduces scope 1+2 from 1,700,709 to 1,699,810 t/yr."),
 dict(site_id="SITE_NEXTDC_S7", connection_type="tbd", network_business_id="ENT_TRANSGRID",
      max_demand_mw=612.0, pue_design=None, demand_response_pct=None,
      grid_services_role="unknown; Transgrid states Sydney basin capacity is exhausted without proponent-funded "
                         "augmentation",
      source_id="SRC_REUTERS_S7", fact_status="REPORTED", confidence="high", as_of_date="2026-07-23",
      notes="NEXTDC declined to give a target PUE for S7. Must commit to a fixed PUE limit under the new NSW "
            "requirements; the state-imposed cap is 1.3."),
 dict(site_id="SITE_CLOUDCARRIER_SH", connection_type="behind_the_meter_gas", onsite_gas_mw=673.0,
      onsite_gas_type="fossil gas, reciprocating engines",
      grid_services_role="islanded / self-supplied generation for the campus",
      source_id="SRC_GREENPEACE_SUB", fact_status="REPORTED", confidence="medium", as_of_date="2026-03-27",
      notes="The clearest Australian instance of the 'standalone islanded power' model. Greenpeace estimates "
            "~2.4 Mt CO2-e per year, approximately equal to the whole of NSW's economy-wide gas abatement "
            "projected for 2028."),
 dict(site_id="SITE_WESTERN_DOWNS", connection_type="tbd", network_business_id=None, max_demand_mw=2160.0,
      source_id="SRC_ABC_WD", fact_status="REPORTED", confidence="medium", as_of_date="2026-09-14",
      notes="2.16 GW peak is comparable to roughly a quarter of Queensland peak demand; connection arrangements "
            "and Energy Queensland's role require confirmation."),
 dict(site_id="SITE_AIRTRUNK_SYD1", connection_type="distribution", battery_mwh=None,
      grid_services_role="co-located battery storage supporting the Western Sydney campus",
      source_id="SRC_NSWGUIDE26", fact_status="REPORTED", confidence="medium", as_of_date="2026-08-17",
      notes="Cited by the NSW Government as an example of a data centre managing grid-connected consumption during "
            "peak and low-generation periods. AirTrunk published 'AirTrunk stands ready to flex and invest in the "
            "grid' on 1 May 2026. Battery MW/MWh not disclosed in the Guidelines - see research_gaps RG-008."),
]

WATER = [
 dict(site_id="SITE_NEXTDC_S7", cooling_technology="direct_to_chip_liquid", water_source="closed_loop_no_makeup",
      supplier_id="ENT_SYDNEYWATER", supply_agreement_status="abandoned", potable_dependency=0,
      source_id="SRC_REUTERS_S7", fact_status="REPORTED", confidence="high", as_of_date="2026-07-23",
      notes="Planning documents lodged April 2026 proposed using Sydney's treated sewage (recycled water) with "
            "Sydney Water and coNEXA named as possible suppliers. NEXTDC walked away from the talks because the "
            "planning permission needed to build the recycled-water pipeline was unavailable. The facility will "
            "instead circulate liquid coolant around the chips with heat rejected to air - no water, but more "
            "energy. NEXTDC states it does not plan to use any drinking water for S7 and that it has previously "
            "deployed waterless cooling at 50 MW of compute, one twelfth of the S7 proposal."),
 dict(site_id="SITE_MAMRE_ROAD", cooling_technology="hybrid", water_source="mixed", annual_water_kl=22400.0,
      potable_dependency=None, source_id="SRC_IA_MAMRE", fact_status="REPORTED", confidence="high",
      as_of_date="2026-04-30",
      notes="728 cooling units; estimated 22.4 million litres (22,400 kL) of water per year - about nine Olympic "
            "swimming pools. Source (potable vs recycled) not established in the reporting; NSW Guidelines would "
            "require recycled water for 100% of cooling if a water-intensive open-loop system is used."),
]

# ---------------------------------------------------------------------
# ENERGY AGREEMENTS + RENEWABLE CLAIM AUDIT  (Pillar B / verification)
# ---------------------------------------------------------------------
ENERGY_AGREEMENTS = [
 dict(buyer_id="ENT_AIRTRUNK", seller_id="ENT_OX2", agreement_type="ppa_physical", technology="solar",
      capacity_mw=25.0, additionality="new_build_post_fid", in_nsw=1, disclosed=1,
      source_id="SRC_AIRTRUNK_PPA", fact_status="CLAIMED", confidence="medium", as_of_date="2023-12-19",
      notes="Google-AirTrunk-OX2 arrangement: AirTrunk procures the generation plus energy attribute certificates "
            "with time-matching. Time-matching is a materially stronger claim than annual volumetric matching, but "
            "certificate surrender evidence has not been checked against Clean Energy Regulator data."),
]

RENEWABLE_CLAIMS = [
 dict(claimant_id="ENT_AIRTRUNK", claim_date="2026", claim_scope="national", claim_type="percentage_renewable",
      claim_text="AirTrunk states it has signed multiple renewable energy sourcing contracts in Australia and "
                 "achieved 100% renewable energy by 2025.",
      instrument_relied_on="unspecified (generation contracts plus energy attribute certificates)",
      lgc_surrender_evidence="not checked - Clean Energy Regulator LGC/STC surrender data download outstanding",
      verification_status="UNVERIFIED",
      verification_note="Additionality and time-matching are asserted for one 25 MW OX2 solar arrangement only. "
                        "Greenpeace's May 2026 assessment found no operator analysed adequately proved it was "
                        "driving renewable growth.",
      source_id="SRC_AIRTRUNK_PPA", fact_status="CLAIMED", confidence="medium", as_of_date="2026-09-18"),
 dict(claimant_id="ENT_MICROSOFT", claim_date="2026-04-23", claim_scope="global", claim_type="percentage_renewable",
      claim_text="Achievement of 100% renewable energy to match energy consumption, and water-positive operations "
                 "by 2030.",
      instrument_relied_on="unspecified global matching",
      lgc_surrender_evidence="not checked",
      verification_status="NOT_ASSESSED",
      verification_note="Global claim; Australian-specific matching not separately disclosed. The NSW Guidelines "
                        "note PPAs to date skew to solar rather than the wind, storage and firming assets NSW needs.",
      source_id="SRC_MS2026", fact_status="CLAIMED", confidence="medium", as_of_date="2026-04-23"),
 dict(claimant_id="ENT_AIRTRUNK", site_id="SITE_MAMRE_ROAD", claim_date="2026-02", claim_scope="site",
      claim_type="percentage_renewable",
      claim_text="The Mamre Road EIS commits the project to running solely on electricity generated from renewable "
                 "sources by 2030, with a stated target of 100% renewable electricity procurement through PPAs, "
                 "virtual PPAs, customer procurement of green tariffs and RECs.",
      instrument_relied_on="PPAs / vPPAs / green tariffs / RECs plus a small volume of carbon offsets for back-up "
                           "generators",
      lgc_surrender_evidence="not checked",
      verification_status="UNVERIFIED",
      verification_note="Greenpeace analysis of the EIS: claimed scope 2 emissions fall from 23,574,172 t to "
                        "818,316-918,316 t only once procurement strategies are counted, so the entire decarbonisation "
                        "claim rests on instruments that are not yet contracted or evidenced. Would fail the NSW "
                        "Guidelines' Principle 3 test (>=40% wind, storage at 25% of generation for 4 hours, "
                        "10-year terms, pre-FID additionality).",
      source_id="SRC_GREENPEACE_SUB", fact_status="REPORTED", confidence="medium", as_of_date="2026-04-03"),
 dict(claimant_id="ENT_CLOUDCARRIER", site_id="SITE_CLOUDCARRIER_SH", claim_date="2025-09", claim_scope="site",
      claim_type="other",
      claim_text="Request for SEARs states the proposed natural gas generation 'is expected to produce lower "
                 "greenhouse gas emissions than the current coal-dominated grid, resulting in a measurable "
                 "improvement in overall emissions performance'.",
      instrument_relied_on="grid intensity comparison",
      verification_status="CONTRADICTED",
      verification_note="The generation serves new demand rather than displacing coal, so the emissions are "
                        "additional. Greenpeace estimates ~2.4 Mt CO2-e/yr and notes AEMO's 2026 projections put "
                        "NSW grid intensity below the level assumed. Also likely to exceed the Safeguard Mechanism "
                        "facility threshold, unlike grid-powered data centres.",
      source_id="SRC_GREENPEACE_SUB", fact_status="REPORTED", confidence="medium", as_of_date="2026-04-03"),
]

# ---------------------------------------------------------------------
# FINANCIAL FLOWS  (Pillar B)
# ---------------------------------------------------------------------
FLOWS = [
 dict(flow_date="2024-12-23", flow_type="acquisition", from_entity_id="ENT_BLACKSTONE", to_entity_id="ENT_AIRTRUNK",
      amount_aud=24e9, vehicle="Blackstone Real Estate Partners / Infrastructure Partners / Tactical Opportunities / "
                               "BX PE individual-investor strategy, with CPP Investments",
      foreign_control=1, source_id="SRC_AIRTRUNK_BC", fact_status="VERIFIED", confidence="high",
      as_of_date="2024-12-23",
      notes="Largest data centre transaction globally and the largest Australian transaction of 2024. FIRB approval "
            "was a condition of the September 2024 agreement."),
 dict(flow_date="2024-12-23", flow_type="acquisition", from_entity_id="ENT_CPP", to_entity_id="ENT_AIRTRUNK",
      amount_aud=None, foreign_control=1, source_id="SRC_CPP", fact_status="VERIFIED", confidence="high",
      notes="12% interest acquired as part of the A$24bn transaction."),
 dict(flow_date="2024-12-23", flow_type="asset_sale", from_entity_id="ENT_AIRTRUNK", to_entity_id="ENT_MACQUARIE_AM",
      amount_aud=None, foreign_control=0, source_id="SRC_INFRAINV", fact_status="REPORTED", confidence="medium",
      notes="Macquarie Asset Management and PSP Investments exited their combined 88% stake - a domestic "
            "infrastructure-manager and Canadian-pension exit into US private equity."),
 dict(flow_date="2025-02-18", flow_type="acquisition", from_entity_id="ENT_FUTUREFUND", to_entity_id="ENT_CDC",
      amount_aud=None, foreign_control=0, source_id="SRC_CDC2025", fact_status="VERIFIED", confidence="high",
      notes="Future Fund lifted its direct CDC holding to 34.55% by exercising pre-emptive rights over CSC's 12.04% "
            "sale process, which had attracted international bids. Enterprise value ~$17bn implied."),
 dict(flow_date="2025-02-18", flow_type="acquisition", from_entity_id="ENT_INFRATIL", to_entity_id="ENT_CDC",
      amount_aud=None, foreign_control=1, source_id="SRC_CDC2025", fact_status="VERIFIED", confidence="high",
      notes="Infratil (NZ) lifted to 49.75% - the largest CDC shareholder is a foreign-listed infrastructure investor, "
            "which qualifies the 'sovereign ownership' framing of the February 2025 announcement."),
 dict(flow_date="2023-10-24", flow_type="capex_commitment", from_entity_id="ENT_MICROSOFT", amount_aud=5e9,
      foreign_control=1, source_id="SRC_MS2023", fact_status="VERIFIED", confidence="high",
      notes="A$5bn over two years; grew the Australian footprint to 29 sites across three Azure regions."),
 dict(flow_date="2026-04-23", flow_type="capex_commitment", from_entity_id="ENT_MICROSOFT", amount_aud=25e9,
      foreign_control=1, source_id="SRC_MS2026", fact_status="VERIFIED", confidence="high",
      as_of_date="2026-04-23",
      notes="A$25bn (US$18bn) of capital and operating expenditure by end-2029; footprint to expand by more than "
            "140%. Signed alongside an MoU with the Australian Government affirming the March 2026 Expectations, "
            "plus expansion of the Microsoft-ASD Cyber-Shield and a commitment to AI-skill three million Australians "
            "by 2028. Microsoft also cites EY-Parthenon analysis claiming $36bn of local economic contribution and "
            "the equivalent of 186,000 full-time jobs in FY25 - an economic-contribution figure, not an employment "
            "headcount, and it should not be read as data centre jobs."),
 dict(flow_date="2025-06-14", flow_type="capex_commitment", from_entity_id="ENT_AWS", amount_aud=20e9,
      foreign_control=1, source_id="SRC_AWS2025", fact_status="VERIFIED", confidence="high",
      notes="AU$20bn (US$13bn) 2025-2029 for new data centres in Sydney and Melbourne, with new renewable energy "
            "projects announced alongside."),
 dict(flow_date="2025-12-05", flow_type="capex_commitment", from_entity_id="ENT_NEXTDC", site_id="SITE_NEXTDC_S7",
      amount_aud=7.6e9, foreign_control=0, source_id="SRC_CAPBRIEF", fact_status="REPORTED", confidence="medium",
      notes="S7 Sydney AI data centre build with OpenAI confirmed as partner / anchor. Commercial terms of the "
            "OpenAI offtake are not disclosed - see research_gaps RG-014."),
 dict(flow_date="2025-02-18", flow_type="capex_commitment", from_entity_id="ENT_CDC", site_id="SITE_CDC_LAVERTON",
      amount_aud=2.7e9, foreign_control=0, source_id="SRC_CDC2025", fact_status="VERIFIED", confidence="high",
      notes="Laverton phase one. CDC states the two new campuses (Laverton and Sydney) will add ~1 GW."),
]

# ---------------------------------------------------------------------
# INCENTIVES / SUBSIDIES  (Pillar B - the audit that has not yet been done)
# ---------------------------------------------------------------------
INCENTIVES = [
 dict(jurisdiction="NSW", granting_body="NSW Government (DPHI / Treasury)", recipient_id=None, site_id=None,
      incentive_type="fast_track_approval", instrument="NSW Data Centre Guidelines (17 August 2026)",
      amount_aud=None, start_date="2026-08-17",
      conditions="Compliance with six principles and 17 performance measures: dPUE <=1.25 with dWUE <=1.0 "
                 "(potable) or <=1.6 (non-potable), or dPUE <=1.3 with dWUE <=0.4; 100% recycled water for "
                 "water-intensive cooling; NSW Clean Air Group 6 limits for diesel generators; 25% demand "
                 "reduction for up to two hours without using diesel back-up; PPAs meeting wind, storage, "
                 "ten-year and pre-FID additionality tests; benefit-sharing; local content; training and skills.",
      conditionality_score=5, domestic_compute_allocation=0, disclosed=1,
      source_id="SRC_NSWGUIDE26", fact_status="VERIFIED", confidence="high", as_of_date="2026-08-17",
      notes="The 'incentive' is a 75-day assessment commitment. The Guidelines set no penalties for non-compliance; "
            "the Treasurer's stated sanction is the risk of refusal. This is the closest Australian instrument to the "
            "conditionality model the Observatory recommends, though it stops short of reserving domestic compute."),
 dict(jurisdiction="NSW", granting_body="NSW Government", recipient_id=None, site_id=None,
      incentive_type="other", instrument="NSW data centre approvals authority (launched 2025)",
      amount_aud=None, start_date="2025-09",
      conditions="Eligibility: project value above A$1bn, primarily non-residential and data-centre related.",
      conditionality_score=1, domestic_compute_allocation=0, disclosed=1,
      source_id="SRC_PINSENT", fact_status="REPORTED", confidence="medium",
      notes="An approvals-facilitation body rather than a financial subsidy. Its existence is a form of in-kind "
            "state support and should be counted in any subsidy register."),
 dict(jurisdiction="VIC", granting_body="Victorian Government (DJSIR, DEECA, DTP, DGS)", recipient_id=None,
      incentive_type="co_funded_infrastructure", instrument="Sustainable Data Centre Action Plan (A$5.5m)",
      amount_aud=5.5e6, start_date="2026-05",
      conditions="Whole-of-government coordination across land, energy, water and workforce; not an operator subsidy.",
      conditionality_score=2, domestic_compute_allocation=0, disclosed=1,
      source_id="SRC_VICPLAN", fact_status="VERIFIED", confidence="high", as_of_date="2026-08-03",
      notes="Victoria frames a potential pipeline of more than $25bn. Separately, a fast-track process is reported "
            "to reduce approvals to about three months, and the Clean Energy Council records $51.9bn of Victorian "
            "data centre investment being fast-tracked as priority projects."),
 dict(jurisdiction="Commonwealth", granting_body="Australian Government (DISR)", recipient_id=None,
      incentive_type="fast_track_approval",
      instrument="Expectations of data centres and AI infrastructure developers (23 March 2026)",
      amount_aud=None, start_date="2026-03-23",
      conditions="Five expectations: national interest and cyber security; clean energy additionality and cost "
                 "coverage plus grid security contributions; sustainable water use including non-potable and "
                 "circular water; Australian jobs, apprenticeships and training; and support for start-ups, "
                 "researchers and not-for-profits to access compute on favourable terms.",
      conditionality_score=4, domestic_compute_allocation=1, disclosed=1,
      source_id="SRC_BIRD", fact_status="VERIFIED", confidence="high", as_of_date="2026-04-08",
      notes="Not legally binding. Aligned proponents are 'more likely to receive priority consideration through "
            "Commonwealth regulatory processes'. Expectation 5.1 is the only Australian instrument that already "
            "requires a form of domestic compute allocation - it is voluntary and unquantified."),
 dict(jurisdiction="All", granting_body="State revenue offices", recipient_id=None,
      incentive_type="alleged", instrument="payroll tax / land tax / stamp duty concessions (unverified)",
      amount_aud=None, disclosed=0, conditionality_score=0, domestic_compute_allocation=0,
      source_id="SRC_DCA_TAX", fact_status="GAP", confidence="low", as_of_date="2026-09-18",
      notes="AUDIT REQUIRED. The industry body Data Centres Australia asserts that data centres pay all standard "
            "taxes and receive no special concessions. No primary revenue-office evidence either way has been "
            "located. This is the single most important open item in Pillar B: payroll tax exemptions, land tax "
            "thresholds and leasehold terms for sites on state-owned land (including the Western Sydney Employment "
            "Area and Aerotropolis) must be obtained by FOI. See research_gaps RG-003."),
]

# ---------------------------------------------------------------------
# LEGAL INSTRUMENTS  (Pillar C)
# ---------------------------------------------------------------------
def L(**kw):
    kw.setdefault("binding", 1)
    kw.setdefault("fact_status", "VERIFIED")
    kw.setdefault("confidence", "high")
    kw.setdefault("as_of_date", "2026-09-18")
    return kw

INSTRUMENTS = [
 L(id="LAW_EXPECTATIONS26", name="Expectations of data centres and AI infrastructure developers",
   jurisdiction="Commonwealth", instrument_type="policy_expectation", status="in_force", made="2026-03-23",
   binding=0, url="https://www.industry.gov.au/publications/expectations-data-centres-and-ai-infrastructure-developers",
   source_id="SRC_DISR",
   summary="Five national expectations covering national interest and cyber security, energy transition, water, "
           "skills and workforce, and research, innovation and local capability. Applies to new or expanded "
           "hyperscale and large-scale AI compute; excludes small edge and on-site enterprise facilities.",
   relevance="The top of the Australian policy stack. Creates no legal obligations but drives priority treatment "
             "in Commonwealth processes and is being implemented with states via the Energy and Climate Change "
             "Ministerial Council."),
 L(id="LAW_NSWGUIDE26", name="NSW Data Centre Guidelines", jurisdiction="NSW", instrument_type="guideline",
   status="in_force", made="2026-08-17", binding=0,
   url="https://www.infrastructure.nsw.gov.au/media/4jlictae/id0073_nsw-data-centre_guidelines.pdf",
   source_id="SRC_NSWGUIDE26",
   summary="Six principles, 17 performance measures, and a 75-day assessment commitment for compliant projects. "
           "Sets dPUE and dWUE bands, requires 100% recycled water for water-intensive cooling, applies NSW Clean "
           "Air Regulation Group 6 limits to diesel back-up generators, requires a 25% two-hour demand reduction "
           "capability that cannot be met with diesel, and imposes PPA additionality, wind-share, storage-share, "
           "ten-year-term and pre-FID tests.",
   relevance="The most detailed operational data centre standard in Australia and the benchmark against which "
             "every NSW site in this database should be scored."),
 L(id="LAW_EIEIA2026", name="Electricity Infrastructure Investment Amendment Bill 2026 (NSW)", jurisdiction="NSW",
   binding=0, instrument_type="bill", status="announced", made="2026-08-05",
   url="https://legislation.nsw.gov.au/view/pdf/bill/affe6b31-bef0-49e6-98e1-f9eac558401a",
   source_id="SRC_MALLESONS", fact_status="REPORTED", confidence="medium",
   summary="Would give the NSW minister power to control grid access in NSW and make data centres pay for network "
           "infrastructure; introduces REZ-style large load infrastructure access schemes.",
   relevance="The legislative vehicle converting the 'user pays' principle into enforceable NSW law. Track passage "
             "and the regulations it enables."),
 L(id="LAW_EPA_CLEAN_AIR", name="Protection of the Environment Operations (Clean Air) Regulation 2022 (NSW)",
   jurisdiction="NSW", instrument_type="regulation", status="in_force",
   source_id="SRC_NSWGUIDE26",
   summary="Group 6 limits for stationary reciprocating internal combustion engines (diesel back-up generators): "
           "NOx 450 mg/m3, particulates 50 mg/m3, VOCs 1,140 mg/m3, CO 5,880 mg/m3. Outside metropolitan cities "
           "and regional towns, away from sensitive receivers, US EPA Tier 2 limits may be met instead with an air "
           "quality impact assessment.",
   relevance="THE KEY LOOPHOLE. NSW Government guidance records that current regulation allows data centres to run "
             "generators up to 200 hours a year without being subject to any point-source NOx emission limits, and "
             "that planning consents may limit only the number of generators running concurrently outside "
             "emergencies. The largest Sydney data centres now have generator capacity comparable to NSW's larger "
             "gas power plants."),
 L(id="LAW_SOCI", name="Security of Critical Infrastructure Act 2018 (Cth) as amended", jurisdiction="Commonwealth",
   instrument_type="act", status="in_force", url="https://www.cisc.gov.au/legislation-regulation-and-compliance/cyber-security-legislative-reforms",
   source_id="SRC_CISC",
   summary="The data storage or processing sector is a critical infrastructure sector. The Security of Critical "
           "Infrastructure Amendment (2025 Measures No. 1) commenced 4 April 2025 and clarifies obligations for "
           "data storage systems storing or processing business critical data, including deeming certain "
           "government-owned or operated data storage systems critical infrastructure assets.",
   relevance="Determines which facilities carry positive security obligations, register on the Critical "
             "Infrastructure Register, and must maintain a risk management program."),
 L(id="LAW_CIRMP26", name="Critical Infrastructure Risk Management Program Rules (Enhanced Rules 2026)",
   jurisdiction="Commonwealth", binding=1, instrument_type="rule", status="consultation", made="2025-12-16",
   source_id="SRC_CISC", fact_status="REPORTED", confidence="medium",
   summary="CISC began consulting on 16 December 2025 on a suite of enhanced rules requiring critical "
           "infrastructure providers to identify and minimise, mitigate or eliminate risks across their assets, "
           "including cyber and physical risk.",
   relevance="Will set the compliance baseline for data storage and processing assets. Track the final rules and "
             "commencement dates."),
 L(id="LAW_NER_IBL", name="National Electricity Rule change - access standards for large inverter-based loads "
                          "(AEMC draft determination, 12 March 2026)",
   jurisdiction="NEM", binding=0, instrument_type="determination", status="draft", made="2026-03-12",
   url="https://www.aemc.gov.au/news-centre/media-releases/aemc-proposes-new-grid-standards-data-centre-connections",
   source_id="SRC_AEMC",
   summary="Creates a new standard for large inverter-based loads, requiring data centres to ride through grid "
           "faults rather than disconnecting. Not retrospective. Follows AEMO's April 2024 rule change request on "
           "improving NEM access standards.",
   relevance="Directly answers the 'grid stabiliser vs base load extractor' question: AEMO cites the July 2024 "
             "Virginia event in which ~1,500 MW of data centre load disconnected after a single network fault. "
             "AEMO estimates 12 months to implement the REGO obligation and 24-36 months for connections and "
             "registration reform."),
 L(id="LAW_ERC0448_56", name="Ministerial rule change requests ERC0448 and ERC0456 (network cost recovery for "
                             "data centre demand)",
   jurisdiction="NEM", binding=0, instrument_type="rule", status="proposed", made="2026-08-05",
   url="https://www.aemc.gov.au/sites/default/files/2026-08/ERC0448%20and%20ERC0456%20-%20Rule%20change%20request_0.pdf",
   source_id="SRC_MALLESONS", fact_status="REPORTED", confidence="medium",
   summary="Commonwealth Energy Minister lodged two requests to amend the National Electricity Rules so that data "
           "centres pay for network costs they cause or accelerate. Standard AEMC process: 6-12 months.",
   relevance="Federal-level implementation of 'no net cost to consumers'. Together with the ECMC agreement of "
             "July 2026 (Queensland and the Northern Territory dissenting) it would mandate that data centres "
             "offset demand by investing in additional renewable and firming generation."),
 L(id="LAW_REGO", name="Renewable Electricity Guarantee of Origin (REGO) scheme obligation for data centres",
   jurisdiction="Commonwealth", binding=0, instrument_type="policy_expectation", status="announced", made="2026-08-05",
   source_id="SRC_MALLESONS", fact_status="REPORTED", confidence="medium",
   summary="A national AI Standard would require data centres to obtain certificates from renewable generators to "
           "prove they fully offset their power use with renewable energy that may not otherwise have been built, "
           "and to prove they have enough firmed power behind them. AEMC estimates 12 months to implement.",
   relevance="This is the additionality test the Observatory recommends. It replaces bare LGC purchase with a "
             "certificate tied to generation that would not otherwise exist - and would finally make corporate "
             "'100% renewable' claims auditable."),
 L(id="LAW_SAFEGUARD", name="Safeguard Mechanism (Cth)", jurisdiction="Commonwealth", instrument_type="act",
   status="in_force", source_id="SRC_GREENPEACE_SUB", fact_status="REPORTED", confidence="medium",
   summary="Applies to facilities emitting above 100,000 t CO2-e per year.",
   relevance="STRUCTURAL GAP. Grid-connected data centres will generally fall below the threshold because their "
             "scope 1 emissions come only from back-up diesel, whereas on-site gas projects such as Moss Vale are "
             "likely to exceed it. The result is that the more polluting configuration attracts the carbon "
             "constraint while the grid-connected configuration does not - unless the emissions of the generators "
             "supplying them are captured elsewhere."),
 L(id="LAW_EPAVIC", name="Victorian EPA data centre obligations (general environmental duty, noise Publication "
                         "1826.5, Application Technical Information Requirements for Data Centres)",
   jurisdiction="VIC", binding=0, instrument_type="guideline", status="in_force", url="https://www.epa.vic.gov.au/data-centres",
   source_id="SRC_EPAVIC",
   summary="Victoria requires data centre applicants to demonstrate consideration of best available technologies, "
           "including US EPA Tier 4 generators, to prohibit non-emergency use of back-up generators, and to "
           "monitor in operation. Noise is assessed under Publication 1826.5 (published 5 September 2025).",
   relevance="Victoria's generator regime is materially stricter than the NSW Group 6 / 200-hour position on "
             "non-emergency use. This asymmetry drives siting arbitrage between states and should be a standing "
             "column in the Observatory's comparison table."),
 L(id="LAW_HCF", name="Hosting Certification Framework (Whole-of-Government Hosting Strategy)",
   jurisdiction="Commonwealth", binding=0, instrument_type="code", status="in_force", source_id="SRC_CERTSTRAT",
   fact_status="REPORTED", confidence="medium",
   summary="Administered by the Digital Transformation Agency. Certified Strategic is the highest designation and "
           "is required for sensitive and PROTECTED government workloads. 60 Certified Strategic facilities and "
           "enclaves are operated by 13 providers.",
   relevance="The only existing Australian mechanism that ties a facility to sovereign government workload - and "
             "therefore the closest thing to a domestic compute allocation requirement currently in force."),
 L(id="LAW_NSW_INQUIRY", name="NSW Legislative Council Inquiry into Data Centres", jurisdiction="NSW",
   binding=0, instrument_type="inquiry", status="in_force", made="2026-01-29",
   url="https://www.parliament.nsw.gov.au/committees/inquiries/Pages/inquiry-details.aspx?pk=3169",
   source_id="SRC_NSWINQ",
   summary="Self-referred 29 January 2026; submissions opened 4 February and closed 27 March 2026; public hearings "
           "in Sydney from 29 May 2026; terms of reference updated 5 August 2026. Transgrid's Executive General "
           "Manager told the inquiry that existing regulatory arrangements were not designed for this level of "
           "large, clustered load growth.",
   relevance="The principal public evidence base for Pillars C and D. Every submission is a citable primary "
             "document and should be systematically ingested."),
 L(id="LAW_IPART_WATER", name="IPART review of water pricing for data centres (NSW)", jurisdiction="NSW",
   binding=0, instrument_type="inquiry", status="announced", made="2026-08-17", source_id="SRC_ABCNSW26",
   fact_status="REPORTED", confidence="high",
   summary="Aimed at ensuring water users on the network are protected and that the impacts of drought and water "
           "scarcity are appropriately managed.",
   relevance="Will determine whether data centres pay the full long-run marginal cost of water or are cross-"
             "subsidised by household users."),
 L(id="LAW_TRANSGRID_NCAP", name="Transgrid Network Capacity Allocation Policy", jurisdiction="NSW",
   binding=0, instrument_type="policy_expectation", status="in_force", url="https://www.transgrid.com.au/media/r0zjfiym/transgrid-network-capacity-allocation-policy-1.pdf",
   source_id="SRC_TRANSGRIDCAP",
   summary="Applies to any relevant large load, meaning an inverter-based load greater than or equal to 30 MW or "
           "30 MVA. Network capacity is allocated only on signature of a Network Connection Agreement, via either "
           "a conditional NCA before performance standards are agreed or a full NCA afterwards. Allocated capacity "
           "remains valid only if planning criteria are satisfied within three months of signing.",
   relevance="This is the mechanism that kills phantom demand. It is the single most effective existing control on "
             "speculative connection hoarding in the NEM and should be the model for a national rule."),
 L(id="LAW_AI_STANDARD", name="National AI Standard (proposed legislation, Commonwealth)", jurisdiction="Commonwealth",
   binding=0, instrument_type="bill", status="announced", made="2026-07-15", source_id="SRC_REUTERS_AI",
   fact_status="REPORTED", confidence="medium",
   summary="Would set clear rules for large data centres on where they are built and the power and water they use; "
           "legislation flagged for introduction in early 2027. Delivered through the new Office of AI in PM&C.",
   relevance="The instrument that would make the March 2026 Expectations binding. Watch for the draft bill."),
 L(id="LAW_VIC_STRATEGY", name="Victorian Data Centre Strategy (consultation paper, March 2026) and fast-track "
                              "process for priority projects",
   jurisdiction="VIC", binding=0, instrument_type="strategy", status="consultation", made="2026-03",
   source_id="SRC_CEC", fact_status="REPORTED", confidence="medium",
   summary="Used to fast-track priority projects, including $51.9bn of data centre investment. Victoria's "
           "fast-track application process is reported to reduce approvals to about three months.",
   relevance="Speed-over-conditionality risk: compare Victoria's three-month fast track with the NSW 75-day "
             "pathway, which at least attaches 17 performance measures."),
]

INSTRUMENT_APPLICATION = [
 dict(instrument_id="LAW_NSWGUIDE26", site_id="SITE_NEXTDC_S7", applies_from="2026-08-17",
      obligation="Fixed PUE limit (state cap 1.3) and disclosed water use; if the Guidelines are adopted for this "
                 "project, dPUE/dWUE bands, recycled-water or closed-loop cooling, Group 6 generator limits and a "
                 "25% two-hour demand reduction capability.",
      compliance_status="not_assessed",
      evidence="Reuters review of 35 NSW applications found S7 among six projects facing the new state-based rules; "
               "NEXTDC did not give a target PUE.",
      source_id="SRC_REUTERS_S7", fact_status="REPORTED", confidence="high", as_of_date="2026-07-23"),
 dict(instrument_id="LAW_EXPECTATIONS26", entity_id="ENT_MICROSOFT", applies_from="2026-04-23",
      obligation="Memorandum of Understanding affirming commitment to the five Expectations.",
      compliance_status="partially_compliant",
      evidence="Microsoft's MoU with the Australian Government was signed on 23 April 2026 alongside the A$25bn "
               "announcement. No public reporting against individual expectation sub-clauses yet.",
      source_id="SRC_MS2026", fact_status="VERIFIED", confidence="high", as_of_date="2026-04-23"),
 dict(instrument_id="LAW_EPA_CLEAN_AIR", site_id="SITE_MAMRE_ROAD", applies_from="2026-04-10",
      obligation="Site-specific air quality impact assessment across all planned and reasonably foreseeable "
                 "generator operating scenarios including routine testing and maintenance; Group 6 limits.",
      compliance_status="non_compliant",
      evidence="NSW EPA advice of 10 April 2026: the EIS 'does not provide the information required to allow us to "
               "complete our assessment'; further information requested on air quality, noise, greenhouse gas "
               "emissions and waste storage.",
      source_id="SRC_IA_MAMRE", fact_status="REPORTED", confidence="high", as_of_date="2026-04-30"),
 dict(instrument_id="LAW_SAFEGUARD", site_id="SITE_CLOUDCARRIER_SH", applies_from=None,
      obligation="Facility-level emissions reporting and safeguard obligations if above 100,000 t CO2-e/yr.",
      compliance_status="unknown",
      evidence="Greenpeace notes that on-site gas projects are likely to exceed the Safeguard Mechanism threshold, "
               "whereas grid-purchasing data centres will not.",
      source_id="SRC_GREENPEACE_SUB", fact_status="REPORTED", confidence="medium", as_of_date="2026-04-03"),
]

# ---------------------------------------------------------------------
# REGULATORY + COMMUNITY EVENTS  (Pillars C & D)
# ---------------------------------------------------------------------
REG_EVENTS = [
 dict(event_date="2026-04-10", regulator_id="ENT_NSW_EPA", site_id="SITE_MAMRE_ROAD",
      event_type="additional_information_request",
      summary="NSW EPA advised the Department that the Mamre Road EIS 'does not provide the information required "
              "to allow us to complete our assessment' and requested further information on air quality, noise, "
              "greenhouse gas emissions and waste storage, citing potential significant air quality and noise "
              "impacts and proximity to schools, aged care facilities and existing residences.",
      source_id="SRC_IA_MAMRE", fact_status="REPORTED", confidence="high", as_of_date="2026-04-30"),
 dict(event_date="2026-08-20", regulator_id="ENT_TRANSGRID", event_type="determination",
      summary="Sydney Basin Network Capacity Update published: no capacity to connect any of the 20 GW of large "
              "load enquiries without user-paid augmentation; up to 2 GW unlockable via a new South Creek 500/330 "
              "kV substation and further Western Sydney upgrades, at proponent cost; capacity allocated in the "
              "order connection agreements are signed.",
      source_id="SRC_TRANSGRID26", fact_status="VERIFIED", confidence="high", as_of_date="2026-08-26"),
 dict(event_date="2026-05", regulator_id="ENT_TRANSGRID", event_type="hearing",
      summary="Transgrid Executive General Manager Jason Krstanoski told the NSW Legislative Council inquiry that "
              "existing regulatory arrangements were not designed for this level of large, clustered load growth.",
      source_id="SRC_REUTERS_S7", fact_status="REPORTED", confidence="medium"),
 dict(event_date="2026-03-12", regulator_id="ENT_AEMC", instrument_id="LAW_NER_IBL", event_type="determination",
      summary="AEMC published a draft rule proposing new technical standards for large data centres and similar "
              "inverter-based loads, requiring fault ride-through rather than disconnection.",
      source_id="SRC_AEMC", fact_status="VERIFIED", confidence="high", as_of_date="2026-03-12"),
 dict(event_date="2026-07", regulator_id="ENT_AEMO", event_type="review_announced",
      summary="ECMC agreed at its July 2026 meeting, with Queensland and the Northern Territory dissenting, to "
              "progress regulatory arrangements mandating that data centres offset their electricity demand by "
              "investing in additional renewable and firming generation. NER changes to be considered in "
              "September 2026.",
      source_id="SRC_MALLESONS", fact_status="REPORTED", confidence="medium", as_of_date="2026-08-06"),
 dict(event_date="2026-08-05", regulator_id="ENT_AEMC", instrument_id="LAW_ERC0448_56",
      event_type="rule_change_request",
      summary="AEMC published advice to the ECMC on regulatory pathways to require data centres to fully offset "
              "demand and demonstrate firmed capacity; the Commonwealth Energy Minister lodged ERC0448 and "
              "ERC0456 on network cost recovery the same day.",
      source_id="SRC_MALLESONS", fact_status="REPORTED", confidence="medium", as_of_date="2026-08-06"),
 dict(event_date="2026-08-17", regulator_id="ENT_NSW_TREASURY", instrument_id="LAW_NSWGUIDE26",
      event_type="fast_track_granted",
      summary="NSW Data Centre Guidelines and the 75-day fast-track pathway took effect, alongside a new NSW "
              "Office of AI and the commissioning of an IPART water pricing review.",
      source_id="SRC_ABCNSW26", fact_status="VERIFIED", confidence="high", as_of_date="2026-08-17"),
 dict(event_date="2026-01-29", regulator_id="ENT_NSWLC", instrument_id="LAW_NSW_INQUIRY",
      event_type="inquiry_opened",
      summary="NSW Legislative Council self-referred an inquiry into data centres; submissions 4 February to "
              "27 March 2026; public hearings from 29 May 2026.",
      source_id="SRC_NSWINQ", fact_status="VERIFIED", confidence="high"),
 dict(event_date="2026-03-03", regulator_id="ENT_CER", event_type="other",
      summary="Clean Energy Regulator NGERS data reported by the AFR: greenhouse gas emissions of the top three "
              "data centre operators (AirTrunk, CDC, Amazon) doubled over five years and rose 20% in 2024-25.",
      source_id="SRC_AFR_NGER", fact_status="REPORTED", confidence="medium",
      notes="The underlying CER dataset is public and downloadable - a direct ingestion target for the "
            "verification module."),
]

COMMUNITY_EVENTS = [
 dict(event_date="2026-04", site_id="SITE_MAMRE_ROAD", locality="Kemps Creek", state="NSW",
      event_type="council_rejection", actor="Penrith City Council", severity=5,
      summary="Penrith City Council told the NSW Government it objected to the Mamre Road proposal, arguing the "
              "site was 'not suitable for a proposed development of this scale'.",
      source_id="SRC_IA_MAMRE", fact_status="REPORTED", confidence="high", as_of_date="2026-04-30"),
 dict(event_date="2026-04", site_id="SITE_MAMRE_ROAD", locality="Kemps Creek", state="NSW",
      event_type="school_or_institution_objection", actor="Mamre Anglican School / Anglican Schools Corporation",
      severity=4,
      summary="The school directly across the road raised concerns about air quality, noise during and after "
              "construction, and the location of power generation and diesel storage relative to students; it "
              "noted that community understanding of data centre impacts 'has not had time to be reliably "
              "informed', flagged significant consequences in the event of a fire, and has identified an "
              "alternative site while seeking government help to relocate.",
      source_id="SRC_IA_MAMRE", fact_status="REPORTED", confidence="high", as_of_date="2026-04-30"),
 dict(event_date="2026-04", site_id="SITE_MAMRE_ROAD", locality="Kemps Creek", state="NSW",
      event_type="school_or_institution_objection",
      actor="Catholic Church of the Diocese of Parramatta (Emmaus Retirement Village)", severity=4,
      summary="Formal objection: the proposal 'fails to adequately address cumulative impacts, emergency access, "
              "servicing resilience and stormwater feasibility, and places unacceptable and unresolved risk on "
              "existing community critical land uses'. Concerns raised about water and electricity supply to the "
              "retirement village operated by Catholic Healthcare.",
      source_id="SRC_IA_MAMRE", fact_status="REPORTED", confidence="high", as_of_date="2026-04-30"),
 dict(event_date="2026-04", site_id="SITE_MAMRE_ROAD", locality="Kemps Creek", state="NSW",
      event_type="objection_submission", actor="Catholic Schools Parramatta Diocese", severity=3,
      summary="Did not object in principle but asked that impacts be minimised, that diesel back-up generator "
              "testing occur outside school hours and peak outdoor activity periods, and that noise, construction "
              "traffic and fuel and battery storage impacts be limited. Affected schools: Emmaus Catholic College "
              "and Trinity Catholic Primary.",
      source_id="SRC_IA_MAMRE", fact_status="REPORTED", confidence="high", as_of_date="2026-04-30"),
 dict(event_date="2026-08-16", locality="Western Sydney", state="NSW", event_type="protest",
      group_id="GRP_STOPTHESLOP", actor="Stop the Slop / community organisers and students", severity=3,
      summary="Protest the day before the NSW Guidelines launched, calling for a moratorium on new AI data centre "
              "builds until communities are consulted. Organisers asked where the water and power will come from, "
              "how waste will be managed, what back-up systems will be used during outages, and what will happen "
              "to local power and water prices. Spokesperson Sophie Shanaaz: 'We're really focused on getting all "
              "these AI data centres out of our suburbs ... eating our resources.' Community organiser Gokulan "
              "Gopal said there is 'not enough regulation at the moment'.",
      source_id="SRC_ABCNSW26", fact_status="REPORTED", confidence="high", as_of_date="2026-08-16"),
 dict(event_date="2026-09-03", locality="Lane Cove", state="NSW", event_type="media_campaign",
      actor="Lane Cove residents", severity=4,
      summary="Residents report constant low-frequency hum from an operating data centre 350 m from homes, with "
              "descriptions ranging from 'a jet plane about to take off' to a high-pitched whine; four further data "
              "centres are in the pipeline at the local industrial park, and residents fear impacts on the national "
              "park and river.",
      source_id="SRC_BB2026", fact_status="REPORTED", confidence="high", as_of_date="2026-09-03"),
 dict(event_date="2026-09-03", site_id="SITE_CDC_MARSDEN", locality="Marsden Park", state="NSW",
      event_type="media_campaign", actor="Marsden Park residents", severity=4,
      summary="The largest data centre in the Southern Hemisphere is under construction approximately 100 m from a "
              "local community.",
      source_id="SRC_BB2026", fact_status="REPORTED", confidence="high", as_of_date="2026-09-03"),
 dict(event_date="2026-07-27", site_id="SITE_MELTON_SYNCLINE", locality="Melton", state="VIC",
      event_type="protest", actor="Melton residents", severity=3,
      summary="Residents rallied against Syncline Energy's proposed data centre hub; a council meeting on 27 July "
              "2026 was used to organise opposition. Concerns include siting on Green Wedge land, water for "
              "cooling, grid strain, and diesel and gas back-up generation producing 24/7 low-frequency noise and "
              "glare.",
      source_id="SRC_MELTONCC", fact_status="REPORTED", confidence="low", as_of_date="2026-07-27"),
 dict(event_date="2026-05-31", site_id="SITE_MELTON_SYNCLINE", locality="Melton", state="VIC",
      event_type="petition", actor="Change.org petitioners", severity=2,
      summary="Petition 'Stop data centre construction in Melton' argues that a data centre in a residential area "
              "will degrade quality of life, harm the local environment and permanently alter the character of the "
              "area.",
      source_id="SRC_CHANGEORG", fact_status="REPORTED", confidence="low", as_of_date="2026-05-31"),
 dict(event_date="2026-05-19", site_id="SITE_CLOUDCARRIER_SH", locality="Moss Vale / Southern Highlands",
      state="NSW", event_type="protest", actor="Southern Highlands community and ACF", severity=4,
      summary="Protests called after the developer expanded plans for fossil gas generation to serve the campus. "
              "The Australian Conservation Foundation is investigating the proposal.",
      source_id="SRC_RENEW_MOSSVALE", fact_status="REPORTED", confidence="medium", as_of_date="2026-05-19"),
 dict(event_date="2026-08-01", site_id="SITE_SOUTH_MORANG", locality="South Morang", state="VIC",
      event_type="media_campaign", actor="Local residents / The Westsider", severity=3,
      summary="Community backlash reported against a newly approved ~A$1bn data centre.",
      source_id="SRC_MELTONCC", fact_status="CLAIMED", confidence="low", as_of_date="2026-08-01"),
 dict(event_date="2026-03-27", site_id="SITE_MAMRE_ROAD", locality="NSW", state="NSW",
      event_type="objection_submission", group_id="GRP_GREENPEACE", actor="Greenpeace Australia Pacific",
      severity=4,
      summary="Submission No 120 to the NSW Legislative Council inquiry urges the Government not to 'roll out the "
              "red carpet' without legislated protections, democratic oversight and community consent, and to "
              "treat AI data centres as a high-risk infrastructure category that must prove compatibility with "
              "NSW climate, energy, water and social objectives before approval is contemplated.",
      source_id="SRC_GREENPEACE_SUB", fact_status="VERIFIED", confidence="high", as_of_date="2026-04-03"),
]

COMMUNITY_GROUPS = [
 dict(id="GRP_STOPTHESLOP", name="Stop the Slop", locality="Western Sydney", state="NSW", formed="2026",
      focus="Opposition to AI data centre expansion in residential suburbs; moratorium pending community "
            "consultation; water, power, waste and price impacts.",
      source_id="SRC_ABCNSW26", fact_status="REPORTED", confidence="high", as_of_date="2026-08-16"),
 dict(id="GRP_GREENPEACE", name="Greenpeace Australia Pacific", locality="Sydney", state="NSW",
      focus="Energy transition risk from data centre demand; additionality of renewable claims; gas-fired data "
            "centre generation; water use; transparency and rigour of approval criteria.",
      source_id="SRC_GREENPEACE_SUB", fact_status="VERIFIED", confidence="high", as_of_date="2026-04-03"),
 dict(id="GRP_LANECOVE", name="Lane Cove data centre residents (unformalised)", locality="Lane Cove", state="NSW",
      focus="Noise from an operating facility 350 m from homes and four further proposals in the local industrial "
            "park; impacts on the national park and river.",
      source_id="SRC_BB2026", fact_status="REPORTED", confidence="medium", as_of_date="2026-09-03"),
 dict(id="GRP_MELTON", name="Melton community campaign against Syncline Energy proposal", locality="Melton",
      state="VIC", focus="Green Wedge land use, cooling water, grid strain, diesel and gas back-up generation, "
            "24/7 low-frequency noise.",
      source_id="SRC_MELTONCC", fact_status="REPORTED", confidence="low", as_of_date="2026-07-27"),
 dict(id="GRP_HIGHLANDS", name="Southern Highlands / Moss Vale opposition to Cloud Carrier gas campus",
      locality="Moss Vale", state="NSW", focus="673 MW fossil gas generation attached to a data campus; water "
            "security; emissions.",
      source_id="SRC_RENEW_MOSSVALE", fact_status="REPORTED", confidence="medium", as_of_date="2026-05-19"),
]

# ---------------------------------------------------------------------
# SECURITY / SOVEREIGNTY  (Pillar C)
# ---------------------------------------------------------------------
SECURITY = [
 dict(subject_entity_id="ENT_AIRTRUNK", regime="firb", status="approved", foreign_control_pct=100.0,
      ultimate_controller="United States (Blackstone-led consortium; CPP Investments 12%)",
      determination_date="2024-12-23",
      conditions="Not publicly disclosed. The September 2024 agreement recorded that the transaction was subject "
                 "to approval from the Australian Foreign Investment Review Board and it completed on 23 December "
                 "2024 following regulatory approvals.",
      notes="FIRB does not publish conditions for national security business approvals; obtain via the annual "
            "Foreign Investment Approvals report and FOI. See research_gaps RG-006.",
      source_id="SRC_BC_DEAL", fact_status="REPORTED", confidence="high", as_of_date="2024-12-23"),
 dict(subject_entity_id="ENT_AIRTRUNK", regime="soci_act",
      status="AirTrunk operates three HCF Certified Strategic facilities; sector is a declared critical "
             "infrastructure sector under the SOCI Act",
      foreign_control_pct=100.0, ultimate_controller="United States",
      notes="Asset-level critical infrastructure designation depends on whether the facility stores or processes "
            "business critical data or is owned/operated for government. Site-by-site mapping outstanding.",
      source_id="SRC_CLAYTONUTZ", fact_status="REPORTED", confidence="medium", as_of_date="2025-04-07"),
 dict(subject_entity_id="ENT_CDC", regime="soci_act",
      status="Sovereign-positioned operator; 12 HCF Certified Strategic sites including nine in Canberra serving "
             "government and national critical infrastructure customers",
      foreign_control_pct=49.75, ultimate_controller="Infratil (New Zealand) 49.75%; Future Fund (Cth) 34.55%; "
                                                    "CSC (Cth) 12.04%; management 3.66%",
      notes="The February 2025 announcement framed the pre-emptive exercise as preserving 'sovereign ownership', "
            "yet the largest single shareholder is a New Zealand-listed infrastructure investor and 46.59% sits "
            "with two Commonwealth bodies. The Observatory records the arithmetic rather than the framing.",
      source_id="SRC_CDC2025", fact_status="VERIFIED", confidence="high", as_of_date="2025-02-18"),
 dict(subject_entity_id="ENT_MACQUARIE_TG", regime="hosting_certification_framework",
      status="Only vertically integrated certified stack: certified physical facilities plus an HCF-certified "
             "Sovereign Cloud service",
      sovereign_data_carriage=1, source_id="SRC_CERTSTRAT", fact_status="REPORTED", confidence="medium"),
 dict(subject_entity_id="ENT_NEXTDC", site_id="SITE_NEXTDC_S7", regime="other",
      status="Foreign anchor tenant with an operational role",
      notes="OpenAI is to help plan, build, run and buy compute from S7. That places a foreign AI laboratory inside "
            "the operational control loop of Australia's largest proposed AI facility - a control question that the "
            "SOCI Act's data storage or processing provisions do not obviously reach, because the asset is "
            "Australian-owned while the operator influence is foreign. Flag for legal analysis.",
      source_id="SRC_REUTERS_S7", fact_status="REPORTED", confidence="high", as_of_date="2026-07-23"),
]

# ---------------------------------------------------------------------
# METRICS
# ---------------------------------------------------------------------
def M(as_of, scope, name, value, unit, **kw):
    kw.setdefault("fact_status", "REPORTED")
    kw.setdefault("confidence", "medium")
    return dict(as_of=as_of, scope=scope, metric_name=name, value=value, unit=unit, **kw)

METRICS = [
 M("2026-06","Australia","operational_data_centres",162,"count", basis="actual",
   source_id="SRC_AEMO26", fact_status="VERIFIED", confidence="high",
   notes="AEMO, citing DCByte. Predominantly Sydney and Melbourne. BBC separately reports 162 with 90 more planned."),
 M("2026","Australia","planned_data_centres",90,"count", basis="pipeline", source_id="SRC_BB2026",
   fact_status="REPORTED", confidence="medium"),
 M("2026","Australia","grid_share_of_electricity",2.0,"%", basis="actual", source_id="SRC_AEMO26",
   fact_status="VERIFIED", confidence="high", notes="Today's national grid-supplied electricity use."),
 M("2026-03","Australia","transmission_connection_queue_projects",11,"count", basis="pipeline",
   source_id="SRC_AEMO26", fact_status="VERIFIED", confidence="high",
   notes="Projects >5 MW progressing through the transmission connection process at the end of the March 2026 "
         "quarter; ~60% NSW, ~40% VIC; most at early stages."),
 M("2026-03","Australia","transmission_connection_queue_mw",5400,"MW", basis="pipeline",
   source_id="SRC_AEMO26", fact_status="VERIFIED", confidence="high"),
 M("2026-06","Australia","transmission_connection_queue_mw",9000,"MW", basis="pipeline",
   source_id="SRC_AEMO26", fact_status="REPORTED", confidence="low",
   notes="Secondary reporting indicates the queue rose from 5.4 GW to 9 GW in one quarter, with 7.6 GW still at "
         "application stage. Confirm against QED Q2 2026 before publication."),
 M("2026","Australia","data_centre_pipeline_investment",155,"AUD bn", basis="estimate",
   source_id="SRC_WESTPAC", fact_status="REPORTED", confidence="medium",
   notes="Westpac IQ: exceeds $155bn, or 5.6% of one year's GDP."),
 M("2030","Australia","data_centre_energy",12,"TWh/yr", basis="forecast_central", source_id="SRC_AEMO26",
   fact_status="VERIFIED", confidence="high", notes="~6% of grid-supplied electricity; ~25% p.a. growth."),
 M("2050","Australia","data_centre_energy",34,"TWh/yr", basis="forecast_central", source_id="SRC_AEMO26",
   fact_status="VERIFIED", confidence="high", notes="~12% of grid-supplied electricity."),
 M("2026","WA","operational_data_centres_swis",15,"count", basis="actual", source_id="SRC_AEMO26",
   fact_status="VERIFIED", confidence="high",
   notes="South West Interconnected System. WA is in the WEM, not the NEM - a scope caveat for any "
         "'National Electricity Market' framing."),
 M("2024","Australia","deployable_capacity",1350,"MW", basis="actual", source_id="SRC_CERTSTRAT",
   fact_status="REPORTED", confidence="medium", notes="Mandala Partners, Data Centres as Enabling Infrastructure."),
 M("2030","Australia","deployable_capacity",3100,"MW", basis="forecast_central", source_id="SRC_CERTSTRAT",
   fact_status="REPORTED", confidence="medium", notes="Mandala Partners; requires >A$26bn of new investment."),
 M("2025","Australia","live_capacity",1400,"MW", basis="actual", source_id="SRC_CERTSTRAT",
   fact_status="REPORTED", confidence="medium", notes="CBRE, August 2025."),
 M("2028","Australia","live_capacity",1800,"MW", basis="forecast_central", source_id="SRC_CERTSTRAT",
   fact_status="REPORTED", confidence="medium", notes="CBRE; demand outpaces supply by 0.7-1.7 GW."),
 M("2026-07","NSW","operational_or_construction_data_centres",60,"count", basis="actual",
   source_id="SRC_ABCNSW26", fact_status="REPORTED", confidence="high"),
 M("2026-07","NSW","ssd_pipeline_projects",19,"count", basis="pipeline", source_id="SRC_NSWGUIDE26",
   fact_status="VERIFIED", confidence="high"),
 M("2026-07","NSW","ssd_pipeline_value",50.3,"AUD bn", basis="pipeline", source_id="SRC_NSWGUIDE26",
   fact_status="VERIFIED", confidence="high"),
 M("2030","NSW","grid_share_of_energy",11.0,"%", basis="forecast_central", source_id="SRC_ABCNSW26",
   fact_status="REPORTED", confidence="high",
   notes="NSW Minister for Climate Change, Environment and Energy. AEMO forecast: doubling from 5% of NSW "
         "grid-supplied energy in 2026 to 11% by 2030, over the same period in which ~7 GW of NSW coal generation "
         "is scheduled to retire."),
 M("2040","NEM","grid_share_step_change",6.0,"%", basis="forecast_low", source_id="SRC_GREENPEACE_SUB",
   fact_status="REPORTED", confidence="medium", notes="AEMO 2025 ESOO lowest-growth scenario: 3% to 6% by 2040."),
 M("2040","NEM","grid_share_high_growth",13.0,"%", basis="forecast_high", source_id="SRC_GREENPEACE_SUB",
   fact_status="REPORTED", confidence="medium",
   notes="AEMO highest-growth scenario; more than total EV load or total residential electrification. Step Change "
         "projection for 2040 jumped from just under 5 TWh (2024 report) to 27 TWh (2025 report)."),
 M("2026-08","Sydney basin","large_load_connection_enquiries",20000,"MW", basis="enquiry",
   source_id="SRC_TRANSGRID26", fact_status="VERIFIED", confidence="high",
   notes="Transgrid: insufficient capacity exists today to connect any of the 20 GW of enquiries."),
 M("2024-12","Sydney West (12 km radius)","data_centre_connection_enquiries",10000,"MW", basis="enquiry",
   source_id="SRC_TRANSGRIDCAP", fact_status="VERIFIED", confidence="high",
   notes="Equivalent to the peak winter load for the whole of NSW concentrated in one local area. Enquiries "
         "received since late 2024."),
 M("2026-08","Western Sydney","signed_data_centre_connection_capacity",1500,"MW", basis="signed",
   source_id="SRC_TRANSGRID26", fact_status="VERIFIED", confidence="high"),
 M("2026-08","Western Sydney","unlockable_capacity_with_augmentation",2000,"MW", basis="estimate",
   source_id="SRC_TRANSGRID26", fact_status="VERIFIED", confidence="high",
   notes="Requires a new South Creek 500/330 kV substation plus substation and transmission upgrades, funded by "
         "proponents."),
 M("2026","NSW","average_demand",8750,"MW", basis="actual", source_id="SRC_TRANSGRID26",
   fact_status="VERIFIED", confidence="high", notes="NSW average electricity demand ranges 7.5-10 GW; midpoint shown."),
 M("2025","Australia","phantom_share_of_connection_requests",85.7,"%", basis="estimate",
   source_id="SRC_NSWGUIDE26", fact_status="VERIFIED", confidence="high",
   notes="Oxford Economics for AEMO: 6 in every 7 MW of data centre connection requests are phantom demand."),
 M("2026","NSW","applications_likely_to_proceed",20.0,"%", basis="estimate", source_id="SRC_NSWGUIDE26",
   fact_status="VERIFIED", confidence="high", notes="Consultation with energy utilities on their connections pipeline."),
 M("2026","NSW","ssd_project_pue_average",1.3,"ratio", basis="actual", source_id="SRC_NSWGUIDE26",
   fact_status="VERIFIED", confidence="high", notes="Range 1.15-1.4 across recent EISs; latest application "
   "requirements specify 1.3."),
 M("2026","NSW","ssd_project_wue_average",1.0,"L/kWh", basis="actual", source_id="SRC_NSWGUIDE26",
   fact_status="VERIFIED", confidence="high", notes="9 of 12 proposed projects; planning requirements do not yet "
   "specify WUE."),
 M("2026","NSW","diesel_generator_unregulated_hours",200,"hours/yr", basis="actual", source_id="SRC_NSWGUIDE26",
   fact_status="VERIFIED", confidence="high",
   notes="Current regulation allows generator use up to 200 hours a year without point-source NOx limits. The "
         "largest data centres have generator capacity comparable to NSW's larger gas power plants."),
 M("2023-03 to 2026-05","NSW","renewable_projects_approved",49,"count", basis="actual",
   source_id="SRC_NSWGUIDE26", fact_status="VERIFIED", confidence="high",
   notes="10.2 GW of new generation and over 30 GWh of storage approved. Separately, 10 GW approved and 41 GW "
         "proposed statewide."),
 M("2026-02","NSW","ssd_projects_with_ppa_commitment",50.0,"%", basis="actual", source_id="SRC_NSWGUIDE26",
   fact_status="VERIFIED", confidence="high",
   notes="Over half of proposed projects in the planning system had committed to some form of PPA or longer-term "
         "renewable sourcing. PPAs to date skew to solar rather than the wind, storage and firming NSW needs."),
 M("2035","Sydney","data_centre_share_of_drinking_water",25.0,"%", basis="forecast_central",
   source_id="SRC_ABC_WATER", fact_status="REPORTED", confidence="high",
   notes="Sydney Water projection: the equivalent of about a quarter of the city's yearly drinking water supply."),
 M("2025","Sydney","water_price_increase_attributable",168,"AUD/household/yr", basis="estimate",
   source_id="SRC_GREENPEACE_SUB", fact_status="REPORTED", confidence="medium",
   notes="Sydney Water reported rising potable demand from data centres as a factor in the regulator's 2025 price "
         "determination."),
 M("2035","NSW","wholesale_price_impact_without_new_supply",26.0,"%", basis="forecast_central",
   source_id="SRC_BB2026", fact_status="REPORTED", confidence="medium",
   notes="Climate Council: without significant new renewable generation and storage, data centres could push NSW "
         "power prices 26% higher by 2035."),
 M("2026","Western Sydney","peak_demand_vs_rest_of_city",4.0,"x", basis="estimate", source_id="SRC_SMH_WSYD",
   fact_status="REPORTED", confidence="medium",
   notes="SMH investigation: the capacity increase equals the average load of more than 10 million households and "
         "at peak would demand almost four times as much power as the rest of the city."),
 M("2026","VIC","data_centre_pipeline_value",51.9,"AUD bn", basis="pipeline", source_id="SRC_CEC",
   fact_status="REPORTED", confidence="low",
   notes="Clean Energy Council reference to Victorian fast-tracked priority projects. Reconcile with the Victorian "
         "Government's own 'more than $25bn' pipeline figure - the two are not measuring the same thing."),
 M("2026","VIC","proposed_demand_estimated_by_farmers",9000,"MW", basis="estimate", source_id="SRC_MELTONCC",
   fact_status="CLAIMED", confidence="low",
   notes="Victorian Farmers Federation estimate reported second-hand: equivalent to four Loy Yang power stations. "
         "Primary VFF document required before use."),
 M("2026","NSW","hcf_certified_strategic_facilities_national",60,"count", basis="actual",
   source_id="SRC_CERTSTRAT", fact_status="REPORTED", confidence="medium",
   notes="60 Certified Strategic facilities and enclaves nationally across 13 providers, unchanged during the "
         "certification pause."),
 M("2024-07","Virginia (US) - comparative","load_disconnected_after_single_fault",1500,"MW", basis="actual",
   source_id="SRC_AEMO26", fact_status="VERIFIED", confidence="high",
   notes="The empirical basis for the AEMC fault ride-through standard. Approximately 1,500 MW of data centre load "
         "disconnected following a single network fault, contributing to system instability."),
 M("2026","NEM","large_data_centre_connection_lead_time",2,"years", basis="estimate", source_id="SRC_AEMO26",
   fact_status="VERIFIED", confidence="high", notes="Application to energisation; large data centres then ramp over "
   "5-10 years."),
]

# ---------------------------------------------------------------------
# RESEARCH GAPS  (the ingestion backlog)
# ---------------------------------------------------------------------
GAPS = [
 ("A","RG-001","Compute the straight-line distance from every mapped site to its nearest submarine cable landing "
   "station, and record the cable system and landing point name.",
   "Pillar A requires proximity to cable landing stations. No verified distances exist in this release; the field "
   "is deliberately empty rather than estimated.",
   "TeleGeography Submarine Cable Map (landing station coordinates) + geocoded site addresses",
   "dataset_download",4),
 ("A","RG-002","Ingest every State Significant Development and State Significant Infrastructure data centre "
   "application from the NSW Planning Portal: reference, lodged date, proponent SPV, capacity, EIS metrics, "
   "submissions, EPA advice, determination and conditions.",
   "The NSW portal is the authoritative record for the 19-project, $50.3bn pipeline and for site-level PUE, WUE, "
   "generator and water figures. Currently only 6 NSW applications are in the database.",
   "https://www.planningportal.nsw.gov.au/major-projects (searchable list; per-project attachment API)",
   "scrape_portal",5),
 ("A","RG-003","Ingest the Victorian planning register (Planning Online / Victoria's data centre fast-track list) "
   "and the Queensland development application registers for data centre projects.",
   "Victoria's $25-51.9bn pipeline and Queensland's 2.16 GW Western Downs project are only lightly represented. "
   "Victoria's three-month fast track needs primary documentation.",
   "VicPlanning / DTP; Western Downs Regional Council planning scheme records", "scrape_portal",4),
 ("B","RG-004","Trace domestic superannuation exposure to Australian data centres: AustralianSuper, Aware Super, "
   "UniSuper, Cbus, Hostplus, Australian Retirement Trust - direct holdings, platform stakes, debt facilities and "
   "listed vehicle positions.",
   "Pillar B's core question. IFM Investors (industry super capital) owns the Mamre Road land and the Future Fund "
   "and CSC hold 46.59% of CDC, but the broader super exposure is unmapped.",
   "Annual and quarterly reports; ASIC company registers; fund investment disclosures; AFR/Investor intelligence",
   "manual_review",5),
 ("B","RG-005","Reconcile the ownership of 706-752 Mamre Road: ISPT lists the property as 'Summit' while "
   "Information Age reports the site is owned by IFM Investors. Establish the registered proprietor, the fund "
   "vehicle, the sale price and the conditions precedent.",
   "Two credible sources conflict. Land ownership by superannuation capital is a headline Pillar B finding and "
   "cannot rest on an unresolved discrepancy.",
   "NSW Land Registry Services title search; ASIC; ISPT and IFM disclosures", "manual_review",5),
 ("B","RG-006","Obtain FIRB records for every data centre-related foreign investment since 2020: application, "
   "national security business notification, decision, and any conditions.",
   "The Blackstone/CPP acquisition of AirTrunk was FIRB-reviewed but conditions are not published. Without them "
   "the Observatory cannot assess what control foreign entities actually have.",
   "Foreign Investment Approvals annual reports; Treasurer's decisions; FOI to Treasury", "foi_request",5),
 ("B","RG-007","Establish whether any Australian state has granted payroll tax exemptions, land tax concessions, "
   "stamp duty relief or concessional leasehold land to a data centre proponent, and on what conditions.",
   "This is the central factual dispute in the project brief. The industry body asserts no special concessions "
   "exist; no primary evidence has been located either way. The answer determines whether Pillar B's subsidy "
   "thesis holds in Australia at all.",
   "FOI to NSW Revenue, Revenue NSW, SRO Victoria, QRO; state budget papers; NSW Ombudsman; Land and Property "
   "leases in the Western Sydney Employment Area and Aerotropolis", "foi_request",5),
 ("C","RG-008","Extract environment protection licence conditions for every operating data centre: permitted "
   "generator run hours, NOx limits, monitoring, noise limits and any exemptions from industrial air quality "
   "baselines.",
   "Pillar C asks whether operators are granted exemptions. The NSW Guidelines confirm a 200-hour/yr unregulated "
   "window exists; site-level licence conditions have not been retrieved.",
   "NSW EPA public register of licences; EPA Victoria licence register; SA EPA", "scrape_portal",5),
 ("C","RG-009","Download Clean Energy Regulator NGERS emissions data per data centre operator and facility for "
   "2019-2025, and LGC/STC creation and surrender records per liable entity.",
   "This is the verification engine for every '100% renewable' claim in the database. The AFR has already shown "
   "top-three operator emissions doubled in five years.",
   "https://www.cleanenergyregulator.gov.au (NGERS and RET datasets, CSV)", "dataset_download",5),
 ("C","RG-010","Identify the proponent, site and status of the reported ~1 GW Western Australia data centre, and "
   "map all 15 SWIS operational sites.",
   "WA sits outside the NEM; the brief's NEM-only framing would omit a gigawatt-scale facility.",
   "WA Government announcements; Western Power connection data; AEMO WEM ESOO", "manual_review",3),
 ("D","RG-011","Verify the Melton (Syncline Energy) and South Morang proposals: proponent legal entity, "
   "application reference, capacity, back-up generation, water source, and the council's decision record.",
   "Both currently sit at CLAIMED/low confidence from social and local reporting. They are important Pillar D "
   "case studies and must not be published at that confidence level.",
   "City of Melton and City of Whittlesea planning registers; VicPlanning", "scrape_portal",4),
 ("D","RG-012","Confirm the Anthropic / Western Downs Digital Park relationship from a primary source, and obtain "
   "the Zerra DC development application.",
   "A foreign AI laboratory anchoring Australia's largest proposed facility is a material sovereignty finding; it "
   "currently rests on secondary and social reporting.",
   "Western Downs Regional Council DA register; Anthropic and Queensland Government statements", "manual_review",4),
 ("A","RG-013","Map hyperscaler site-level footprints: Microsoft's 29 Australian sites, AWS Sydney and Melbourne "
   "facilities, Google and Meta facilities, with capacity and grid connection point.",
   "Hyperscalers disclose national investment totals but not sites. Without site data the physical footprint in "
   "Pillar A is materially understated.",
   "Planning portals (SSD/SSI searches by proponent SPV); council DA registers; ASIC SPV searches; property "
   "transactions", "scrape_portal",5),
 ("B","RG-014","Obtain the commercial structure of the OpenAI-NEXTDC S7 arrangement: offtake term, capacity "
   "committed, price basis, funding of the build, and whether OpenAI holds any equity or option over the asset.",
   "Determines whether Australia is hosting a sovereign asset with a foreign tenant, or a foreign-owned compute "
   "node built on an ASX-listed shell.",
   "NEXTDC ASX announcements and investor presentations; OpenAI statements", "manual_review",4),
 ("C","RG-015","Ingest all submissions to the NSW Legislative Council data centres inquiry and classify them by "
   "organisation type and position.",
   "Roughly 120+ submissions constitute the largest single body of primary Australian evidence on this topic and "
   "are freely downloadable.",
   "https://www.parliament.nsw.gov.au/committees/inquiries/Pages/inquiry-details.aspx?pk=3169", "scrape_portal",4),
 ("D","RG-016","Build the community action group register: name, locality, formed date, campaign focus, "
   "affiliation and contact, for every corridor (Western Sydney, Lane Cove/Macquarie Park, Moss Vale, Melton, "
   "Whittlesea, Western Downs, ACT).",
   "Pillar D requires tracking group formation, not just events. Only five groups are currently recorded.",
   "Facebook groups, Change.org, council submission registers, local media", "scrape_portal",3),
 ("C","RG-017","Retrieve water access agreements and trade waste approvals between data centres and Sydney Water, "
   "Yarra Valley Water, South East Water, Melbourne Water and Unitywater, including recycled water scheme "
   "capacity constraints.",
   "The S7 recycled-water collapse happened because pipeline planning permission was unavailable. That failure mode "
   "needs to be documented across every corridor.",
   "FOI to water utilities; IPART water pricing review submissions", "foi_request",4),
 ("E","RG-018","Assess whether any Australian data centre currently provides system services (FCAS, system "
   "strength, synthetic inertia) or is merely a base load extractor, and quantify contracted demand flexibility.",
   "This is the engineering question at the heart of the critique. AirTrunk's Western Sydney battery is the only "
   "documented example and its MW/MWh are undisclosed.",
   "AEMO market registration lists; FCAS participant registers; operator sustainability reports", "dataset_download",4),
 ("E","RG-019","Establish the existence and location of any synchronous condenser installation serving an "
   "Australian data centre corridor.",
   "The brief proposes mandating synchronous condensers at data centres. No Australian evidence of load-side "
   "installation has been located; existing machines are network-side. This determines whether the recommendation "
   "is sound or misdirected.",
   "Transgrid and AEMO system strength reports; network business capital plans", "manual_review",4),
]

# ---------------------------------------------------------------------
# ENGINEERING CLAIM REGISTER  (Pillar E)
# ---------------------------------------------------------------------
ENGINEERING = [
 dict(claim_label="Standalone islanded power (on-site gas/diesel as the primary supply)",
      claim_status="PARTLY_SOUND",
      premise_check="Partly true. The dominant Australian model is grid connection, not islanding. Transgrid has "
                    "20 GW of connection enquiries and allocates capacity only on signature of a Network "
                    "Connection Agreement, which is the opposite of bypassing the grid. But genuine islanded "
                    "proposals exist: Cloud Carrier's 673 MW fossil gas station at Moss Vale serving a ~700 MW "
                    "campus is the clearest case.",
      australia_reality="Diesel at Australian data centres is back-up, not baseload - and that is where the real "
                    "problem sits. NSW regulation permits up to 200 generator hours a year with no point-source "
                    "NOx limits, and the largest Sydney facilities now have generator capacity comparable to NSW's "
                    "larger gas power plants. The Mamre Road proposal alone specifies 846 generators and more than "
                    "18,000 kL of diesel storage. So the externality is not stranded-asset carbon risk from "
                    "islanding; it is unpriced local NOx and particulate exposure in residential corridors, plus "
                    "fire and explosion risk from diesel and lithium-ion storage.",
      replacement_spec="Do not mandate islanding removal alone. Mandate (a) Group 6 limits with no 200-hour "
                    "exemption in urban and peri-urban zones, scaling to US EPA Tier 4 as Victoria already "
                    "requires, (b) a prohibition on non-emergency generator use, (c) continuous emissions "
                    "monitoring with public reporting, (d) SCR on all sets above 560 kW, and (e) a hard cap on "
                    "on-site diesel inventory tied to a Fire and Rescue NSW preliminary hazard analysis. For the "
                    "rare genuinely islanded project, require the Safeguard Mechanism to apply regardless of the "
                    "100 kt threshold.",
      existing_policy_hook="NSW Data Centre Guidelines Principle 1 Ref 4 (Group 6 limits, Tier 2 alternative for "
                    "remote sites); Victorian EPA requirements (Tier 4, non-emergency use prohibited, monitoring); "
                    "NSW Guidelines Ref 6 (fire and explosion risk, diesel and lithium-ion); Safeguard Mechanism.",
      residual_gap="The 200-hour unregulated window is acknowledged in NSW Government guidance but not closed. "
                    "No Australian jurisdiction requires continuous public emissions reporting from data centre "
                    "generators. Cumulative precinct-level air quality assessment is directed at Mamre Road/Kemps "
                    "Creek but is not a standing requirement.",
      evidence_site_ids="SITE_CLOUDCARRIER_SH,SITE_MAMRE_ROAD,SITE_AIRTRUNK_SYD2",
      source_ids="SRC_NSWGUIDE26,SRC_EPAVIC,SRC_GREENPEACE_SUB,SRC_IA_MAMRE", as_of_date="2026-09-18"),

 dict(claim_label="Mandate synchronous condensers at every data centre for grid stability",
      claim_status="FACTUALLY_WRONG_PREMISE",
      premise_check="The diagnosis is right, the instrument is wrong. Data centres are large inverter-based loads "
                    "that degrade system strength; AEMO says so explicitly. But synchronous condensers are "
                    "network-side assets commissioned by transmission businesses to supply system strength at "
                    "nodes. A load does not install one.",
      australia_reality="The regulatory response already underway is different and better targeted: the AEMC's "
                    "March 2026 draft determination creates access standards for large inverter-based loads, "
                    "requiring fault ride-through rather than disconnection. AEMO cites the July 2024 Virginia "
                    "event where ~1,500 MW of data centre load tripped after a single fault. NSW requires a 25% "
                    "reduction in grid-supplied demand for up to two hours, achievable only by load shifting or "
                    "on-site/proximate renewables and storage - and expressly not by diesel generators.",
      replacement_spec="Replace 'install synchronous condensers' with: (1) mandatory compliance with the new large "
                    "inverter-based load access standards including fault ride-through and voltage control; "
                    "(2) a proponent contribution to network-side system strength where the connection degrades "
                    "it, priced through the connection agreement rather than self-supplied hardware; (3) contracted "
                    "demand flexibility of at least 25% of average load for two hours, registered with AEMO as a "
                    "schedulable or semi-scheduled resource; (4) co-located or proximate battery storage sized at "
                    "25% of generation capacity for four hours where the project relies on PPAs; (5) registration "
                    "as a demand response provider so the facility is dispatchable in the wholesale market rather "
                    "than merely interruptible by private contract.",
      existing_policy_hook="AEMC draft determination on access standards for inverter-based loads; NSW Guidelines "
                    "Principle 2 Ref 9 (25% / 2-hour demand reduction, diesel excluded) and Principle 3 Ref 13(b) "
                    "(storage at 25% of generation for four hours); Transgrid Network Capacity Allocation Policy; "
                    "AEMO rule change request of April 2024.",
      residual_gap="No Australian instrument yet requires a data centre to register as a market participant "
                    "providing demand response, and system strength contributions are negotiated case by case "
                    "rather than standardised. The Commonwealth's stated intent to make large AI data centres "
                    "'work flexibly' is not yet in rules.",
      evidence_site_ids="SITE_AIRTRUNK_SYD1,SITE_NEXTDC_S7,SITE_MAMRE_ROAD",
      source_ids="SRC_AEMC,SRC_AEMO26,SRC_NSWGUIDE26,SRC_TRANSGRIDCAP", as_of_date="2026-09-18"),

 dict(claim_label="Evaporative cooling on potable water is the standard Australian design and must be banned",
      claim_status="PARTLY_SOUND",
      premise_check="Directionally right but overstated. Most Sydney data centres do use drinking water for "
                    "cooling, and Sydney Water projects data centre demand equal to about a quarter of the city's "
                    "yearly drinking water supply by 2035. However Australian design WUE is already low: recent "
                    "NSW EISs average a WUE of 1.0, and the largest current proposals are moving to waterless "
                    "direct-to-chip liquid cooling, not evaporative towers.",
      australia_reality="The binding constraint is infrastructure, not intent. NEXTDC abandoned recycled water for "
                    "S7 (612 MW) because the planning permission needed to build a recycled-water pipeline was "
                    "unavailable in Western Sydney, and switched to a more energy-intensive air-cooled "
                    "direct-to-chip design. That is the actual Australian failure mode: a water mandate without "
                    "the pipes forces an energy penalty. NSW has responded with a two-branch standard - dPUE <=1.25 "
                    "with dWUE <=1.0 (potable) or <=1.6 (non-potable), or dPUE <=1.3 with dWUE <=0.4 - plus a "
                    "requirement that water-intensive cooling use 100% recycled water or have a signed transition "
                    "agreement with the utility.",
      replacement_spec="Keep the water-neutrality objective but sequence it correctly: (1) fund and fast-track "
                    "recycled water trunk infrastructure as a condition of precinct rezoning, before data centre "
                    "approvals are granted, so the waterless fallback is not the default; (2) require closed-loop "
                    "or direct-to-chip designs with a published WUE commitment measured under ISO/IEC 30134-9:2022; "
                    "(3) where potable water is used as an interim supply, require a hybrid system capable of "
                    "reduced water use during declared water restrictions, as NSW already asks; (4) cap the energy "
                    "penalty - a waterless design must still meet dPUE <=1.3 or be refused; (5) publish site-level "
                    "water use quarterly, not commercially-in-confidence only.",
      existing_policy_hook="NSW Guidelines Principle 1 Ref 1-3 (dPUE/dWUE bands, 100% recycled water for "
                    "water-intensive cooling, drought-responsive design, smart metering); Commonwealth Expectation "
                    "3 (minimise use, non-potable and circular water, cover water infrastructure costs, drought "
                    "resilience, transparent reporting); IPART water pricing review announced 17 August 2026.",
      residual_gap="Reporting remains commercial-in-confidence under NSW Ref 7, so the public cannot audit actual "
                    "water use. No national WUE standard binds outside NSW. Recycled water network build-out is "
                    "not a condition precedent to rezoning, which is precisely what broke the S7 design.",
      evidence_site_ids="SITE_NEXTDC_S7,SITE_MAMRE_ROAD",
      source_ids="SRC_REUTERS_S7,SRC_NSWGUIDE26,SRC_ABC_WATER,SRC_GREENPEACE_SUB,SRC_WSAA", as_of_date="2026-09-18"),

 dict(claim_label="Unconditional subsidies for foreign hyperscalers",
      claim_status="PARTLY_SOUND",
      premise_check="Not established for Australia. No verified evidence of payroll tax waivers, land tax "
                    "exemptions or concessional leasehold land granted to a data centre proponent has been "
                    "located; the industry body asserts none exist and this is recorded as an untested claim "
                    "(RG-007). What is verifiable is non-cash state support: a 75-day fast-track assessment in "
                    "NSW, a three-month fast track in Victoria, a NSW approvals authority for projects above "
                    "A$1bn, and A$5.5m of Victorian coordination funding.",
      australia_reality="The subsidy in Australia is largely procedural and infrastructural rather than fiscal - "
                    "and in 2026 it became conditional. The Commonwealth Expectations and the NSW Guidelines both "
                    "trade speed for performance: additionality in PPAs (pre-FID projects, >=40% wind, storage at "
                    "25% of generation for four hours, ten-year terms), user-pays network augmentation, recycled "
                    "water, demand flexibility, benefit-sharing with councils, local content, and training. "
                    "Expectation 5 already asks hyperscalers and neoclouds to give Australian start-ups, "
                    "researchers and not-for-profits compute access on favourable terms - the domestic allocation "
                    "principle in embryonic, voluntary, unquantified form.",
      replacement_spec="Sharpen what exists rather than invent a new regime: (1) make Expectation 5 quantified and "
                    "contractual - a stated percentage of installed capacity reserved for Australian universities, "
                    "CSIRO, the Bureau of Meteorology and accredited start-ups, at published prices, as a condition "
                    "of fast-tracking; (2) require disclosure of the operating FTE count per 100 MW so the jobs-to-"
                    "capex ratio is public, and test economic-contribution claims (Microsoft's 186,000 FTE-equivalent "
                    "figure is a modelling output, not employment) against payroll data; (3) make any fast-track "
                    "benefit legally revocable for non-compliance, since NSW currently sets no penalties; (4) where "
                    "state land or infrastructure is provided, take an equity or revenue-share position rather than "
                    "a discount; (5) publish a national subsidy register covering in-kind support, which is "
                    "currently invisible.",
      existing_policy_hook="Commonwealth Expectations 4 and 5; NSW Guidelines Principles 4, 5 and 6 (benefit-"
                    "sharing, local content, training and skills, with CDC Academy and the TAFE NSW Datacentre "
                    "Academy cited as exemplars); Hosting Certification Framework (the only existing mechanism "
                    "that ties a facility to sovereign government workload).",
      residual_gap="The subsidy register does not exist. Fast-track benefits carry no published penalty for "
                    "non-compliance. Domestic compute allocation is voluntary and unquantified. Jobs claims are "
                    "unaudited. FOI requests to state revenue offices (RG-007) are the critical path.",
      evidence_site_ids="SITE_MS_AU_FLEET,SITE_AWS_AU_FLEET,SITE_NEXTDC_S7",
      source_ids="SRC_NSWGUIDE26,SRC_BIRD,SRC_DCA_TAX,SRC_MS2026,SRC_PINSENT,SRC_VICPLAN", as_of_date="2026-09-18"),

 dict(claim_label="The whole ecosystem sits inside the National Electricity Market",
      claim_status="FACTUALLY_WRONG_PREMISE",
      premise_check="False as a scoping rule. WA operates the Wholesale Electricity Market and the South West "
                    "Interconnected System, with 15 operational data centre sites; the NT is outside the NEM and "
                    "dissented from the July 2026 ECMC data centre agreement, as did Queensland.",
      australia_reality="The largest single proposed facility in the country, Western Downs Digital Park at 2.16 GW "
                    "peak, is in Queensland - inside the NEM but in a state that has refused the national "
                    "offsetting mandate. A reported ~1 GW facility is planned in WA, outside it entirely. Any "
                    "database scoped to the NEM would omit both, and would also mis-describe the regulatory "
                    "position of the two dissenting jurisdictions.",
      replacement_spec="Scope the database to Australia, with a `market` column (NEM / WEM / NT) on every site and "
                    "a jurisdictional-applicability flag on every legal instrument. Report state-by-state "
                    "regulatory divergence as a first-class finding, because siting arbitrage between a state that "
                    "prohibits non-emergency generator use and one that allows 200 unregulated hours is itself a "
                    "policy failure worth quantifying.",
      existing_policy_hook="ECMC July 2026 agreement with Queensland and NT dissenting; AEMO's separate NEM and "
                    "WEM Electricity Statements of Opportunities.",
      residual_gap="No national instrument binds WA or the NT. The proposed Commonwealth legislation is the only "
                    "route to national coverage and is not expected before early 2027.",
      evidence_site_ids="SITE_WESTERN_DOWNS,SITE_WA_1GW,SITE_NEXTDC_D1,SITE_NEXTDC_P12",
      source_ids="SRC_AEMO26,SRC_MALLESONS,SRC_ABC_WD,SRC_WA_1GW", as_of_date="2026-09-18"),

 dict(claim_label="Renewable energy claims by operators can be taken at face value",
      claim_status="UNSOUND_AS_STATED",
      premise_check="False. Greenpeace Australia Pacific assessed operators in May 2026 and found that no data "
                    "centre operator analysed adequately proved its claim of driving Australia's renewable energy "
                    "growth. Clean Energy Regulator data reported by the AFR shows the top three operators' "
                    "emissions doubled in five years and rose 20% in 2024-25.",
      australia_reality="The Mamre Road EIS is the worked example: claimed scope 2 emissions fall from 23,574,172 t "
                    "to about 918,316 t only once PPAs, vPPAs, green tariffs and RECs are counted, so the entire "
                    "decarbonisation claim rests on instruments that are neither contracted nor evidenced. NSW "
                    "records that PPAs to date skew to solar rather than the wind, storage and firming the state "
                    "needs, and that just over half of projects in the planning system had committed to any form "
                    "of PPA as at February 2026.",
      replacement_spec="Adopt the NSW Principle 3 test as the national audit standard and enforce it against "
                    "public data: contracted PPAs must be for NSW (or in-state) projects that had not reached FID "
                    "when contracted, with a minimum 40% wind component, storage at 25% of generation capacity "
                    "for four hours, and terms of at least ten years. Then reconcile every claim against Clean "
                    "Energy Regulator LGC/STC surrender records and NGERS emissions per facility, and publish a "
                    "per-operator scorecard. From year four of operation, contracted supply must equal annual "
                    "average energy and rise with the load ramp.",
      existing_policy_hook="NSW Guidelines Principle 3 Ref 13 (a-g); proposed REGO obligation under the national "
                    "AI Standard (12 months to implement per AEMC); Commonwealth Expectation 2.1 (new and "
                    "additional clean energy).",
      residual_gap="REGO is not law. Until it is, additionality is a guideline. The Observatory's own audit "
                    "depends on RG-009 (CER dataset ingestion), which is the highest-value single task in the "
                    "project.",
      evidence_site_ids="SITE_MAMRE_ROAD,SITE_CLOUDCARRIER_SH,SITE_AIRTRUNK_SYD1",
      source_ids="SRC_GP2026,SRC_GREENPEACE_SUB,SRC_AFR_NGER,SRC_NSWGUIDE26,SRC_MALLESONS", as_of_date="2026-09-18"),

 dict(claim_label="Phantom demand makes the pipeline a reliable measure of future load",
      claim_status="UNSOUND_AS_STATED",
      premise_check="False, and the database must not treat lodged capacity as committed capacity. Oxford "
                    "Economics, preparing AEMO's forecast, estimates that 6 in every 7 MW of data centre "
                    "connection requests are phantom demand. Energy utilities tell NSW that about 20% of "
                    "applications in their connections pipeline are likely to proceed.",
      australia_reality="Transgrid has 20 GW of large-load enquiries and zero available capacity; only 1.5 GW has "
                    "progressed to signed connection agreements in Western Sydney. AEMO's transmission queue is "
                    "the hard filter: 11 projects above 5 MW totalling 5.4 GW at the end of the March 2026 "
                    "quarter, reportedly 9 GW by June with 7.6 GW still at application stage. Transgrid's Network "
                    "Capacity Allocation Policy allocates capacity only on signature of an NCA and lapses it if "
                    "planning criteria are not met within three months.",
      replacement_spec="Store three separate capacity fields per project - lodged, signed (NCA executed) and "
                    "energised - and never aggregate them. Publish every headline figure with its basis "
                    "(enquiry / pipeline / signed / actual). Apply the 20% proceeds-likelihood haircut when "
                    "modelling grid, water and price impacts, and reconcile state pipelines against the AEMO "
                    "connection queue quarterly, since the queue is the only figure that survives commercial "
                    "attrition.",
      existing_policy_hook="Transgrid Network Capacity Allocation Policy (>=30 MW inverter-based loads, NCA-"
                    "signature allocation, three-month criteria window); AEMO QED quarterly connection queue "
                    "disclosure from Q1 2026.",
      residual_gap="Distribution-level connections are not yet visible; AEMO is working with DNSPs to improve "
                    "reporting. Sub-30 MW facilities fall outside the Transgrid policy entirely.",
      evidence_site_ids=None,
      source_ids="SRC_NSWGUIDE26,SRC_TRANSGRID26,SRC_TRANSGRIDCAP,SRC_AEMO26", as_of_date="2026-09-18"),
]
