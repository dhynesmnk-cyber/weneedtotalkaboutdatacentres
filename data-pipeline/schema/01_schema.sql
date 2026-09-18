-- =====================================================================
-- AUSTRALIAN DATA CENTRE OBSERVATORY (ADCO)
-- Relational schema v1.0.0  |  SQLite >= 3.35
--
-- Design rules
--   1. Every substantive claim carries: source_id + confidence + as_of_date.
--      No orphan assertions. `fact_status` marks whether a row is
--      VERIFIED (primary source read), REPORTED (credible secondary),
--      CLAIMED (proponent/industry assertion, unverified) or GAP (known
--      unknown, tracked in research_gaps).
--   2. Entities, sites and instruments are referenced by human-readable
--      stable codes (ENT_xxx, SITE_xxx, LAW_xxx, SRC_xxx) so that CSV /
--      JSON seed data can be joined without knowing rowids.
--   3. Money is stored as REAL with an explicit currency code. Power is
--      MW (not kW, not GW) to avoid unit drift. Water is kL/yr.
--   4. All dates are ISO-8601 (YYYY-MM-DD or YYYY-MM).
-- =====================================================================

PRAGMA foreign_keys = ON;

-- ---------------------------------------------------------------------
-- 0. Provenance
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS sources (
    id            TEXT PRIMARY KEY,            -- SRC_xxx
    title         TEXT NOT NULL,
    publisher     TEXT NOT NULL,
    url           TEXT NOT NULL,
    doc_type      TEXT NOT NULL CHECK (doc_type IN (
                    'primary_government','primary_planning_portal','primary_regulator',
                    'primary_company','primary_legislation','primary_court',
                    'news','investigation','academic','think_tank','industry_body',
                    'law_firm_analysis','market_research','community','other')),
    published     TEXT,                        -- ISO date
    accessed      TEXT NOT NULL,               -- ISO date we read it
    credibility   TEXT NOT NULL DEFAULT 'B' CHECK (credibility IN ('A','B','C','D')),
    notes         TEXT
);

-- Every factual table below may point at up to three sources.
-- A link table keeps this normalised.
CREATE TABLE IF NOT EXISTS source_refs (
    id            INTEGER PRIMARY KEY,
    entity_table  TEXT NOT NULL,               -- e.g. 'sites'
    entity_rowid  TEXT NOT NULL,
    source_id     TEXT NOT NULL REFERENCES sources(id),
    quote         TEXT,                        -- verbatim supporting extract
    UNIQUE (entity_table, entity_rowid, source_id)
);

-- ---------------------------------------------------------------------
-- A. Physical infrastructure
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS entities (
    id            TEXT PRIMARY KEY,            -- ENT_xxx
    name          TEXT NOT NULL,
    legal_name    TEXT,
    entity_type   TEXT NOT NULL CHECK (entity_type IN (
                    'hyperscaler','ai_lab','colocation_operator','developer',
                    'telecom','utility','network_business','investor','pe_firm',
                    'super_fund','sovereign_wealth','government_agency','regulator',
                    'council','community_group','industry_body','vendor','other')),
    domicile      TEXT,                        -- country of ultimate control
    hq_country    TEXT,
    asx_ticker    TEXT,
    website       TEXT,
    notes         TEXT,
    fact_status   TEXT NOT NULL DEFAULT 'REPORTED' CHECK (fact_status IN
                    ('VERIFIED','REPORTED','CLAIMED','GAP')),
    source_id     TEXT REFERENCES sources(id),
    confidence    TEXT CHECK (confidence IN ('high','medium','low')),
    as_of_date    TEXT
);
CREATE INDEX IF NOT EXISTS idx_entities_type ON entities(entity_type);

CREATE TABLE IF NOT EXISTS entity_aliases (
    id            INTEGER PRIMARY KEY,
    entity_id     TEXT NOT NULL REFERENCES entities(id),
    alias         TEXT NOT NULL UNIQUE
);

-- Ownership / control chain (Pillar B core table)
CREATE TABLE IF NOT EXISTS ownership (
    id            INTEGER PRIMARY KEY,
    holder_id     TEXT NOT NULL REFERENCES entities(id),
    target_id     TEXT NOT NULL REFERENCES entities(id),
    stake_pct     REAL CHECK (stake_pct >= 0 AND stake_pct <= 100),
    -- 'board_seat' and 'policy_role' are governance influence rather than capital, and are
    -- recorded here because this table is the database's control-and-influence chain.
    instrument    TEXT CHECK (instrument IN (
                    'equity','pre_emptive_right','convertible','debt','mezzanine',
                    'fund_lp_interest','joint_venture','option','land_purchase',
                    'leasehold','offtake','board_seat','policy_role','unknown')),
    effective_from TEXT,
    effective_to  TEXT,
    transaction_value_aud REAL,
    event         TEXT,                        -- 'acquisition', 'stake_sale', etc.
    firb_reviewed INTEGER NOT NULL DEFAULT 0 CHECK (firb_reviewed IN (0,1)),
    firb_outcome  TEXT,
    notes         TEXT,
    fact_status   TEXT NOT NULL DEFAULT 'REPORTED' CHECK (fact_status IN
                    ('VERIFIED','REPORTED','CLAIMED','GAP')),
    source_id     TEXT REFERENCES sources(id),
    confidence    TEXT CHECK (confidence IN ('high','medium','low')),
    as_of_date    TEXT
);
CREATE INDEX IF NOT EXISTS idx_ownership_target ON ownership(target_id);
CREATE INDEX IF NOT EXISTS idx_ownership_holder ON ownership(holder_id);

CREATE TABLE IF NOT EXISTS sites (
    id            TEXT PRIMARY KEY,            -- SITE_xxx
    name          TEXT NOT NULL,
    operator_id   TEXT REFERENCES entities(id),
    owner_id      TEXT REFERENCES entities(id), -- land / asset owner if different
    anchor_tenant_id TEXT REFERENCES entities(id),
    proponent     TEXT,                        -- legal entity named on the planning application (often an SPV)
    suburb        TEXT,
    lga           TEXT,                        -- local government area
    state         TEXT NOT NULL CHECK (state IN
                    ('NSW','VIC','QLD','SA','TAS','WA','NT','ACT','Multi')),
    market        TEXT NOT NULL DEFAULT 'NEM' CHECK (market IN ('NEM','WEM','NT','Multi')),
    lat           REAL, lon REAL,
    address       TEXT,
    status        TEXT NOT NULL CHECK (status IN (
                    'operational','under_construction','approved','lodged',
                    'pre_lodgement','refused','withdrawn','cancelled','rumoured')),
    it_capacity_mw        REAL,                -- IT / critical load
    total_capacity_mw     REAL,                -- incl. cooling overhead
    max_capacity_mw       REAL,                -- full campus build-out
    first_phase_mw        REAL,
    campus_area_ha        REAL,
    gfa_sqm               REAL,
    capital_cost_aud      REAL,
    construction_jobs     INTEGER,
    operational_jobs      INTEGER,
    operational_from      TEXT,
    target_completion     TEXT,
    nearest_cable_ls_km   REAL,                -- straight-line to cable landing station
    nearest_cable_ls_name TEXT,
    proximity_note        TEXT,
    hcf_certified         TEXT CHECK (hcf_certified IN
                    ('certified_strategic','certified_assured','not_certified','unknown')),
    notes                 TEXT,
    fact_status   TEXT NOT NULL DEFAULT 'REPORTED' CHECK (fact_status IN
                    ('VERIFIED','REPORTED','CLAIMED','GAP')),
    source_id     TEXT REFERENCES sources(id),
    confidence    TEXT CHECK (confidence IN ('high','medium','low')),
    as_of_date    TEXT
);
CREATE INDEX IF NOT EXISTS idx_sites_state  ON sites(state);
CREATE INDEX IF NOT EXISTS idx_sites_status ON sites(status);
CREATE INDEX IF NOT EXISTS idx_sites_op     ON sites(operator_id);

-- Planning / approval pathway (Pillar A + C)
CREATE TABLE IF NOT EXISTS applications (
    id            INTEGER PRIMARY KEY,
    site_id       TEXT NOT NULL REFERENCES sites(id),
    jurisdiction  TEXT NOT NULL,               -- 'NSW DPHI (SSD)', 'Melton CC', ...
    pathway       TEXT NOT NULL CHECK (pathway IN (
                    'state_significant_development','state_significant_infrastructure',
                    'local_council','ministerial_call_in','fast_track_scheme',
                    'crown_development','environmental_protection_licence',
                    'grid_connection','water_access','other')),
    reference     TEXT,                        -- SSD-xxxxxxxx etc.
    lodged        TEXT,
    decided       TEXT,
    outcome       TEXT CHECK (outcome IN (
                    'approved','approved_with_conditions','refused','deferred',
                    'withdrawn','under_assessment','additional_info_requested',
                    'not_required','unknown')),
    decision_maker TEXT,
    capacity_mw_in_app REAL,
    conditions_summary TEXT,
    appeal_status TEXT,
    notes         TEXT,
    fact_status   TEXT NOT NULL DEFAULT 'REPORTED' CHECK (fact_status IN
                    ('VERIFIED','REPORTED','CLAIMED','GAP')),
    source_id     TEXT REFERENCES sources(id),
    confidence    TEXT CHECK (confidence IN ('high','medium','low')),
    as_of_date    TEXT
);
CREATE INDEX IF NOT EXISTS idx_app_site ON applications(site_id);

-- Land acquisition / rezoning / lease events
CREATE TABLE IF NOT EXISTS land_events (
    id            INTEGER PRIMARY KEY,
    site_id       TEXT REFERENCES sites(id),
    event_date    TEXT,
    event_type    TEXT NOT NULL CHECK (event_type IN (
                    'purchase','option','leasehold_grant','rezoning','land_swap',
                    'compulsory_acquisition','pre_emptive_sale','rumoured_purchase')),
    seller_id     TEXT REFERENCES entities(id),
    buyer_id      TEXT REFERENCES entities(id),
    area_ha       REAL,
    value_aud     REAL,
    conditionality TEXT,                       -- e.g. 'conditional on 1GW approval'
    notes         TEXT,
    fact_status   TEXT NOT NULL DEFAULT 'REPORTED' CHECK (fact_status IN
                    ('VERIFIED','REPORTED','CLAIMED','GAP')),
    source_id     TEXT REFERENCES sources(id),
    confidence    TEXT CHECK (confidence IN ('high','medium','low')),
    as_of_date    TEXT
);

-- ---------------------------------------------------------------------
-- B. Power, grid and water engineering
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS power_profile (
    id            INTEGER PRIMARY KEY,
    site_id       TEXT NOT NULL UNIQUE REFERENCES sites(id),
    connection_type   TEXT CHECK (connection_type IN (
                    'transmission','distribution','behind_the_meter_gas',
                    'behind_the_meter_diesel','islanded','hybrid','tbd')),
    network_business_id TEXT REFERENCES entities(id),  -- Transgrid / Ausgrid / Western Power...
    connection_point    TEXT,
    nca_status      TEXT CHECK (nca_status IN (
                    'signed','conditional_nca','in_negotiation','enquiry_only','none')),
    nca_date        TEXT,
    augmentation_funded_by TEXT CHECK (augmentation_funded_by IN (
                    'proponent','network','shared','unclear','not_required')),
    augmentation_detail TEXT,
    max_demand_mw   REAL,
    average_load_mw REAL,
    annual_energy_gwh REAL,
    pue_design      REAL,
    pue_operating   REAL,
    demand_response_pct REAL,                  -- % of avg load sheddable
    demand_response_hours REAL,
    battery_mw      REAL,
    battery_mwh     REAL,
    synchronous_condenser INTEGER NOT NULL DEFAULT 0 CHECK (synchronous_condenser IN (0,1)),
    onsite_gas_mw   REAL,
    onsite_gas_type TEXT,
    genset_count    INTEGER,
    genset_total_mw REAL,
    genset_fuel     TEXT,
    genset_annual_test_hours REAL,
    diesel_storage_kl REAL,
    emission_standard TEXT,                      -- 'NSW Clean Air Group 6', 'US EPA Tier 4'
    epa_licence_id  TEXT,
    safeguard_mechanism_exposed INTEGER CHECK (safeguard_mechanism_exposed IN (0,1)),
    grid_services_role TEXT,                    -- 'load only' | 'FCAS' | 'demand response' | 'storage dispatch'
    notes         TEXT,
    fact_status   TEXT NOT NULL DEFAULT 'REPORTED' CHECK (fact_status IN
                    ('VERIFIED','REPORTED','CLAIMED','GAP')),
    source_id     TEXT REFERENCES sources(id),
    confidence    TEXT CHECK (confidence IN ('high','medium','low')),
    as_of_date    TEXT
);

CREATE TABLE IF NOT EXISTS water_profile (
    id            INTEGER PRIMARY KEY,
    site_id       TEXT NOT NULL UNIQUE REFERENCES sites(id),
    cooling_technology TEXT CHECK (cooling_technology IN (
                    'air_cooled','closed_loop_water','adiabatic','evaporative',
                    'direct_to_chip_liquid','immersion','hybrid','tbd')),
    water_source   TEXT CHECK (water_source IN (
                    'potable_mains','recycled_water','closed_loop_no_makeup',
                    'bore_groundwater','rainwater','sea_water','mixed','tbd')),
    supplier_id    TEXT REFERENCES entities(id),
    -- 'not_required' = the design needs no water supply agreement at all (e.g. 100% air-cooled)
    supply_agreement_status TEXT CHECK (supply_agreement_status IN (
                    'signed','in_negotiation','abandoned','not_available','none','not_required',
                    'unknown')),
    annual_water_kl REAL,
    wue_design     REAL,
    wue_operating  REAL,
    potable_dependency INTEGER CHECK (potable_dependency IN (0,1)),
    drought_response TEXT,
    offset_commitment TEXT,
    notes          TEXT,
    fact_status   TEXT NOT NULL DEFAULT 'REPORTED' CHECK (fact_status IN
                    ('VERIFIED','REPORTED','CLAIMED','GAP')),
    source_id     TEXT REFERENCES sources(id),
    confidence    TEXT CHECK (confidence IN ('high','medium','low')),
    as_of_date    TEXT
);

-- ---------------------------------------------------------------------
-- C. Energy procurement & renewable claim verification
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS energy_agreements (
    id            INTEGER PRIMARY KEY,
    buyer_id      TEXT NOT NULL REFERENCES entities(id),
    seller_id     TEXT REFERENCES entities(id),
    site_id       TEXT REFERENCES sites(id),
    agreement_type TEXT NOT NULL CHECK (agreement_type IN (
                    'ppa_physical','ppa_virtual','green_tariff','rec_lease',
                    'firming_agreement','gas_supply','network_agreement',
                    'water_agreement','offtake','mou','unknown')),
    technology    TEXT CHECK (technology IN (
                    'solar','wind','hydro','battery','pumped_hydro','gas','coal',
                    'mixed','other')),
    capacity_mw   REAL,
    annual_volume_gwh REAL,
    term_years    REAL,
    signed        TEXT,
    commences     TEXT,
    expiry        TEXT,
    additionality TEXT CHECK (additionality IN (
                    'new_build_pre_fid','new_build_post_fid','expansion_existing',
                    'existing_asset','unknown')),
    in_nsw        INTEGER CHECK (in_nsw IN (0,1)),
    wind_share_pct REAL,
    storage_share_pct REAL,
    disclosed     INTEGER NOT NULL DEFAULT 0 CHECK (disclosed IN (0,1)),
    notes         TEXT,
    fact_status   TEXT NOT NULL DEFAULT 'REPORTED' CHECK (fact_status IN
                    ('VERIFIED','REPORTED','CLAIMED','GAP')),
    source_id     TEXT REFERENCES sources(id),
    confidence    TEXT CHECK (confidence IN ('high','medium','low')),
    as_of_date    TEXT
);

CREATE TABLE IF NOT EXISTS renewable_claims (
    id            INTEGER PRIMARY KEY,
    claimant_id   TEXT NOT NULL REFERENCES entities(id),
    site_id       TEXT REFERENCES sites(id),
    claim_date    TEXT,
    claim_scope   TEXT NOT NULL CHECK (claim_scope IN (
                    'global','national','state','site','product')),
    claim_text    TEXT NOT NULL,
    claim_type    TEXT NOT NULL CHECK (claim_type IN (
                    'percentage_renewable','net_zero_year','water_positive',
                    'carbon_neutral','additional_generation','time_matched',
                    'diesel_offset','other')),
    target_year   INTEGER,
    instrument_relied_on TEXT,                  -- LGC / REGO / carbon offset / green tariff
    lgc_surrender_evidence TEXT,                -- Clean Energy Regulator reference or 'none found'
    verification_status TEXT NOT NULL DEFAULT 'UNVERIFIED' CHECK (verification_status IN (
                    'VERIFIED','PARTIALLY_VERIFIED','UNVERIFIED','CONTRADICTED','NOT_ASSESSED')),
    verification_note TEXT,
    fact_status   TEXT NOT NULL DEFAULT 'CLAIMED' CHECK (fact_status IN
                    ('VERIFIED','REPORTED','CLAIMED','GAP')),
    source_id     TEXT REFERENCES sources(id),
    confidence    TEXT CHECK (confidence IN ('high','medium','low')),
    as_of_date    TEXT
);

-- ---------------------------------------------------------------------
-- D. Capital flows, subsidies and incentives
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS financial_flows (
    id            INTEGER PRIMARY KEY,
    flow_date     TEXT,
    flow_type     TEXT NOT NULL CHECK (flow_type IN (
                    'equity_investment','acquisition','debt_facility','fund_raise',
                    'capital_raise','asset_sale','land_purchase','capex_commitment',
                    'green_bond','private_placement','dividend','other')),
    from_entity_id TEXT REFERENCES entities(id),
    to_entity_id   TEXT REFERENCES entities(id),
    site_id        TEXT REFERENCES sites(id),
    amount_aud     REAL,
    amount_original REAL,
    currency_original TEXT,
    vehicle        TEXT,                        -- 'Blackstone Real Estate Partners X'
    foreign_control INTEGER CHECK (foreign_control IN (0,1)),
    notes          TEXT,
    fact_status   TEXT NOT NULL DEFAULT 'REPORTED' CHECK (fact_status IN
                    ('VERIFIED','REPORTED','CLAIMED','GAP')),
    source_id     TEXT REFERENCES sources(id),
    confidence    TEXT CHECK (confidence IN ('high','medium','low')),
    as_of_date    TEXT
);

CREATE TABLE IF NOT EXISTS incentives (
    id            INTEGER PRIMARY KEY,
    jurisdiction  TEXT NOT NULL,               -- 'NSW', 'VIC', 'Commonwealth'...
    granting_body TEXT,
    recipient_id  TEXT REFERENCES entities(id),
    site_id       TEXT REFERENCES sites(id),
    incentive_type TEXT NOT NULL CHECK (incentive_type IN (
                    'payroll_tax_exemption','land_tax_exemption','stamp_duty_relief',
                    'leasehold_land_concession','grant','tax_increment','rate_concession',
                    'fast_track_approval','co_funded_infrastructure','equity_stake',
                    'guarantee','offtake_commitment','other','alleged','none_found')),
    instrument    TEXT,                        -- s. of Act, program name
    amount_aud    REAL,
    start_date    TEXT,
    end_date      TEXT,
    conditions    TEXT,                        -- jobs, local content, compute allocation
    conditionality_score INTEGER CHECK (conditionality_score BETWEEN 0 AND 5),
    domestic_compute_allocation INTEGER CHECK (domestic_compute_allocation IN (0,1)),
    disclosed     INTEGER NOT NULL DEFAULT 0 CHECK (disclosed IN (0,1)),
    notes         TEXT,
    fact_status   TEXT NOT NULL DEFAULT 'REPORTED' CHECK (fact_status IN
                    ('VERIFIED','REPORTED','CLAIMED','GAP')),
    source_id     TEXT REFERENCES sources(id),
    confidence    TEXT CHECK (confidence IN ('high','medium','low')),
    as_of_date    TEXT
);

-- ---------------------------------------------------------------------
-- E. Legal / regulatory framework
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS legal_instruments (
    id            TEXT PRIMARY KEY,            -- LAW_xxx
    name          TEXT NOT NULL,
    jurisdiction  TEXT NOT NULL,
    instrument_type TEXT NOT NULL CHECK (instrument_type IN (
                    'act','regulation','amendment_act','rule','determination',
                    'policy_expectation','guideline','strategy','bill','licence_condition',
                    'code','order','inquiry')),
    status        TEXT NOT NULL CHECK (status IN (
                    'in_force','commenced_staged','draft','consultation','announced',
                    'passed','lapsed','superseded','proposed')),
    made          TEXT,
    commenced     TEXT,
    binding       INTEGER NOT NULL DEFAULT 1 CHECK (binding IN (0,1)),
    summary       TEXT,
    relevance     TEXT,                        -- why the Observatory tracks it
    url           TEXT,
    fact_status   TEXT NOT NULL DEFAULT 'VERIFIED' CHECK (fact_status IN
                    ('VERIFIED','REPORTED','CLAIMED','GAP')),
    source_id     TEXT REFERENCES sources(id),
    confidence    TEXT CHECK (confidence IN ('high','medium','low')),
    as_of_date    TEXT
);

CREATE TABLE IF NOT EXISTS instrument_application (
    id            INTEGER PRIMARY KEY,
    instrument_id TEXT NOT NULL REFERENCES legal_instruments(id),
    site_id       TEXT REFERENCES sites(id),
    entity_id     TEXT REFERENCES entities(id),
    applies_from  TEXT,
    obligation    TEXT,                        -- what it actually requires of them
    compliance_status TEXT CHECK (compliance_status IN (
                    'compliant','partially_compliant','non_compliant','exemption_granted',
                    'exemption_sought','unknown','not_assessed')),
    evidence      TEXT,
    notes         TEXT,
    fact_status   TEXT NOT NULL DEFAULT 'REPORTED' CHECK (fact_status IN
                    ('VERIFIED','REPORTED','CLAIMED','GAP')),
    source_id     TEXT REFERENCES sources(id),
    confidence    TEXT CHECK (confidence IN ('high','medium','low')),
    as_of_date    TEXT
);

CREATE TABLE IF NOT EXISTS regulatory_events (
    id            INTEGER PRIMARY KEY,
    event_date    TEXT NOT NULL,
    regulator_id  TEXT REFERENCES entities(id),
    instrument_id TEXT REFERENCES legal_instruments(id),
    site_id       TEXT REFERENCES sites(id),
    entity_id     TEXT REFERENCES entities(id),
    event_type    TEXT NOT NULL CHECK (event_type IN (
                    'additional_information_request','adverse_finding','licence_granted',
                    'licence_condition_imposed','enforcement','penalty','inquiry_opened',
                    'hearing','submission_deadline','rule_change_request','determination',
                    'objection_upheld','fast_track_granted','review_announced','other')),
    summary       TEXT NOT NULL,
    outcome       TEXT,
    notes         TEXT,
    fact_status   TEXT NOT NULL DEFAULT 'REPORTED' CHECK (fact_status IN
                    ('VERIFIED','REPORTED','CLAIMED','GAP')),
    source_id     TEXT REFERENCES sources(id),
    confidence    TEXT CHECK (confidence IN ('high','medium','low')),
    as_of_date    TEXT
);
CREATE INDEX IF NOT EXISTS idx_reg_events_date ON regulatory_events(event_date);

-- ---------------------------------------------------------------------
-- F. National security & sovereignty
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS security_records (
    id            INTEGER PRIMARY KEY,
    subject_entity_id TEXT REFERENCES entities(id),
    site_id       TEXT REFERENCES sites(id),
    regime        TEXT NOT NULL CHECK (regime IN (
                    'firb','soci_act','critical_infrastructure_register','cirmp',
                    'hosting_certification_framework','protective_security',
                    'export_control','telecoms_security','other')),
    status        TEXT,                        -- 'critical infrastructure asset', 'notified', 'cleared'
    foreign_control_pct REAL,
    ultimate_controller TEXT,                  -- country / entity name
    determination_date TEXT,
    conditions    TEXT,
    sovereign_data_carriage INTEGER CHECK (sovereign_data_carriage IN (0,1)),
    notes         TEXT,
    fact_status   TEXT NOT NULL DEFAULT 'REPORTED' CHECK (fact_status IN
                    ('VERIFIED','REPORTED','CLAIMED','GAP')),
    source_id     TEXT REFERENCES sources(id),
    confidence    TEXT CHECK (confidence IN ('high','medium','low')),
    as_of_date    TEXT
);

-- ---------------------------------------------------------------------
-- G. Community impact & externalities
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS community_groups (
    id            TEXT PRIMARY KEY,            -- GRP_xxx
    name          TEXT NOT NULL,
    locality      TEXT,
    state         TEXT,
    formed        TEXT,
    focus         TEXT,
    contact_or_url TEXT,
    notes         TEXT,
    fact_status   TEXT NOT NULL DEFAULT 'REPORTED' CHECK (fact_status IN
                    ('VERIFIED','REPORTED','CLAIMED','GAP')),
    source_id     TEXT REFERENCES sources(id),
    confidence    TEXT CHECK (confidence IN ('high','medium','low')),
    as_of_date    TEXT
);

CREATE TABLE IF NOT EXISTS community_events (
    id            INTEGER PRIMARY KEY,
    event_date    TEXT,
    site_id       TEXT REFERENCES sites(id),
    group_id      TEXT REFERENCES community_groups(id),
    locality      TEXT,
    state         TEXT,
    event_type    TEXT NOT NULL CHECK (event_type IN (
                    'objection_submission','protest','petition','council_deferral',
                    'council_rejection','regulator_adverse_finding','litigation',
                    'media_campaign','meeting','political_intervention',
                    'school_or_institution_objection','benefit_agreement','other')),
    actor         TEXT,                        -- who did it
    summary       TEXT NOT NULL,
    severity      INTEGER CHECK (severity BETWEEN 1 AND 5),
    outcome       TEXT,
    notes         TEXT,
    fact_status   TEXT NOT NULL DEFAULT 'REPORTED' CHECK (fact_status IN
                    ('VERIFIED','REPORTED','CLAIMED','GAP')),
    source_id     TEXT REFERENCES sources(id),
    confidence    TEXT CHECK (confidence IN ('high','medium','low')),
    as_of_date    TEXT
);
CREATE INDEX IF NOT EXISTS idx_comm_site  ON community_events(site_id);
CREATE INDEX IF NOT EXISTS idx_comm_state ON community_events(state);

-- ---------------------------------------------------------------------
-- H. System metrics (time series, for the externality dashboard)
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS metrics (
    id            INTEGER PRIMARY KEY,
    as_of         TEXT NOT NULL,               -- '2026' or '2026-03' or '2026-03-31'
    scope         TEXT NOT NULL,               -- 'Australia','NEM','NSW','Sydney','Western Sydney'
    metric_name   TEXT NOT NULL,
    value         REAL NOT NULL,
    unit          TEXT NOT NULL,
    basis         TEXT CHECK (basis IN ('actual','forecast_low','forecast_central',
                    'forecast_high','pipeline','signed','enquiry','estimate')),
    scenario      TEXT,                        -- 'Step Change', 'Green Energy Exports'
    notes         TEXT,
    fact_status   TEXT NOT NULL DEFAULT 'REPORTED' CHECK (fact_status IN
                    ('VERIFIED','REPORTED','CLAIMED','GAP')),
    source_id     TEXT REFERENCES sources(id),
    confidence    TEXT CHECK (confidence IN ('high','medium','low')),
    as_of_date    TEXT
);
CREATE INDEX IF NOT EXISTS idx_metrics_name ON metrics(metric_name, scope);

-- ---------------------------------------------------------------------
-- I. Research backlog / known unknowns
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS research_gaps (
    id            INTEGER PRIMARY KEY,
    pillar        TEXT NOT NULL CHECK (pillar IN ('A','B','C','D','E')),
    question      TEXT NOT NULL,
    why_it_matters TEXT,
    target_source TEXT,                        -- portal / dataset / FOI route
    retrieval_method TEXT CHECK (retrieval_method IN (
                    'scrape_portal','foi_request','asic_search','dataset_download',
                    'manual_review','regulator_request','interview','not_retrievable')),
    priority      INTEGER NOT NULL DEFAULT 3 CHECK (priority BETWEEN 1 AND 5),
    status        TEXT NOT NULL DEFAULT 'open' CHECK (status IN
                    ('open','in_progress','blocked','resolved','wont_fix')),
    owner         TEXT,
    opened        TEXT NOT NULL,
    resolved_date TEXT,
    notes         TEXT,
    -- provenance for the gap itself: what made us aware of it
    fact_status   TEXT NOT NULL DEFAULT 'VERIFIED' CHECK (fact_status IN
                    ('VERIFIED','REPORTED','CLAIMED','GAP')),
    source_id     TEXT REFERENCES sources(id),
    confidence    TEXT CHECK (confidence IN ('high','medium','low')),
    as_of_date    TEXT
);

-- ---------------------------------------------------------------------
-- J. Engineering critique register (Pillar E - dismantling unworkable ideas)
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS engineering_claims (
    id            INTEGER PRIMARY KEY,
    claim_label   TEXT NOT NULL,               -- 'Standalone islanded power'
    claim_status  TEXT NOT NULL CHECK (claim_status IN (
                    'SOUND','PARTLY_SOUND','UNSOUND_AS_STATED','ALREADY_MANDATED',
                    'FACTUALLY_WRONG_PREMISE')),
    premise_check TEXT NOT NULL,               -- is the premise true in AU?
    australia_reality TEXT NOT NULL,           -- what the evidence shows
    replacement_spec TEXT,                     -- the corrected engineering requirement
    existing_policy_hook TEXT,                 -- instrument that already does this
    residual_gap  TEXT,                        -- what policy still does NOT do
    evidence_site_ids TEXT,                    -- comma separated SITE_ codes
    source_ids    TEXT,
    as_of_date    TEXT
);

-- ---------------------------------------------------------------------
-- Views
-- ---------------------------------------------------------------------
CREATE VIEW IF NOT EXISTS v_pipeline_by_state AS
SELECT s.state,
       s.market,
       s.status,
       COUNT(*)                                   AS n_sites,
       ROUND(SUM(COALESCE(s.max_capacity_mw, s.total_capacity_mw, s.it_capacity_mw,0)),1) AS mw_sum,
       ROUND(SUM(COALESCE(s.capital_cost_aud,0))/1e9,2) AS capex_aud_bn
FROM sites s
GROUP BY s.state, s.market, s.status
ORDER BY s.state, mw_sum DESC;

CREATE VIEW IF NOT EXISTS v_site_full AS
SELECT s.id, s.name, s.state, s.market, s.status,
       op.name  AS operator,
       ow.name  AS land_or_asset_owner,
       an.name  AS anchor_tenant,
       s.max_capacity_mw, s.total_capacity_mw, s.it_capacity_mw, s.capital_cost_aud,
       s.construction_jobs, s.operational_jobs,
       p.connection_type, p.nca_status, p.network_business_id, p.pue_design,
       p.battery_mwh, p.onsite_gas_mw, p.genset_count, p.genset_total_mw,
       p.diesel_storage_kl, p.emission_standard, p.demand_response_pct,
       w.cooling_technology, w.water_source, w.annual_water_kl, w.wue_design,
       s.nearest_cable_ls_name, s.nearest_cable_ls_km,
       s.fact_status, s.confidence, s.as_of_date
FROM sites s
LEFT JOIN entities op ON op.id = s.operator_id
LEFT JOIN entities ow ON ow.id = s.owner_id
LEFT JOIN entities an ON an.id = s.anchor_tenant_id
LEFT JOIN power_profile p ON p.site_id = s.id
LEFT JOIN water_profile w ON w.site_id = s.id;

CREATE VIEW IF NOT EXISTS v_foreign_control AS
SELECT e.id, e.name, e.entity_type, e.domicile, e.hq_country,
       o.holder_id, h.name AS holder, h.domicile AS holder_domicile,
       o.stake_pct, o.instrument, o.effective_from, o.firb_reviewed, o.firb_outcome
FROM entities e
LEFT JOIN ownership o ON o.target_id = e.id AND o.effective_to IS NULL
LEFT JOIN entities h  ON h.id = o.holder_id
WHERE e.entity_type IN ('colocation_operator','developer','hyperscaler','ai_lab','telecom');

CREATE VIEW IF NOT EXISTS v_incentive_register AS
SELECT i.jurisdiction, i.granting_body, e.name AS recipient, s.name AS site,
       i.incentive_type, i.instrument, i.amount_aud, i.conditions,
       i.conditionality_score, i.domestic_compute_allocation, i.disclosed,
       i.fact_status, i.source_id
FROM incentives i
LEFT JOIN entities e ON e.id = i.recipient_id
LEFT JOIN sites s    ON s.id = i.site_id
ORDER BY i.jurisdiction, i.incentive_type;

CREATE VIEW IF NOT EXISTS v_renewable_audit AS
SELECT c.claimant_id, e.name AS claimant, s.name AS site,
       c.claim_date, c.claim_type, c.claim_scope, c.target_year,
       c.instrument_relied_on, c.lgc_surrender_evidence,
       c.verification_status, c.verification_note, c.claim_text
FROM renewable_claims c
LEFT JOIN entities e ON e.id = c.claimant_id
LEFT JOIN sites s    ON s.id = c.site_id
ORDER BY c.verification_status, c.claim_date DESC;

CREATE VIEW IF NOT EXISTS v_community_friction AS
SELECT ce.event_date, ce.state, ce.locality, ce.event_type, ce.actor, ce.summary,
       ce.severity, s.name AS site, g.name AS community_group, ce.outcome,
       ce.fact_status
FROM community_events ce
LEFT JOIN sites s          ON s.id = ce.site_id
LEFT JOIN community_groups g ON g.id = ce.group_id
ORDER BY ce.event_date DESC;

CREATE VIEW IF NOT EXISTS v_verification_ledger AS
SELECT 'sites' AS tbl, fact_status, confidence, COUNT(*) AS n FROM sites GROUP BY 1,2,3
UNION ALL SELECT 'applications', fact_status, confidence, COUNT(*) FROM applications GROUP BY 1,2,3
UNION ALL SELECT 'power_profile', fact_status, confidence, COUNT(*) FROM power_profile GROUP BY 1,2,3
UNION ALL SELECT 'water_profile', fact_status, confidence, COUNT(*) FROM water_profile GROUP BY 1,2,3
UNION ALL SELECT 'energy_agreements', fact_status, confidence, COUNT(*) FROM energy_agreements GROUP BY 1,2,3
UNION ALL SELECT 'renewable_claims', fact_status, confidence, COUNT(*) FROM renewable_claims GROUP BY 1,2,3
UNION ALL SELECT 'financial_flows', fact_status, confidence, COUNT(*) FROM financial_flows GROUP BY 1,2,3
UNION ALL SELECT 'incentives', fact_status, confidence, COUNT(*) FROM incentives GROUP BY 1,2,3
UNION ALL SELECT 'community_events', fact_status, confidence, COUNT(*) FROM community_events GROUP BY 1,2,3
UNION ALL SELECT 'regulatory_events', fact_status, confidence, COUNT(*) FROM regulatory_events GROUP BY 1,2,3
UNION ALL SELECT 'metrics', fact_status, confidence, COUNT(*) FROM metrics GROUP BY 1,2,3;

-- ---------------------------------------------------------------------
-- K. Ingestion audit trail (added v1.0.0)
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS ingest_log (
    id            INTEGER PRIMARY KEY,
    run_at        TEXT NOT NULL,
    pack          TEXT NOT NULL,               -- filename or portal run id
    table_name    TEXT NOT NULL,
    action        TEXT NOT NULL CHECK (action IN ('insert','update','skip','reject','ok')),
    rows_affected INTEGER NOT NULL DEFAULT 0,
    detail        TEXT
);
CREATE INDEX IF NOT EXISTS idx_ingest_run ON ingest_log(run_at);

CREATE VIEW IF NOT EXISTS v_site_dossier AS
SELECT s.id AS site_id, s.name AS site, s.state, s.status,
       op.name AS operator, an.name AS anchor_tenant,
       COALESCE(s.max_capacity_mw, s.total_capacity_mw, s.it_capacity_mw) AS headline_mw,
       s.capital_cost_aud, s.construction_jobs, s.operational_jobs,
       src.title AS primary_source, src.publisher, src.url AS source_url,
       s.fact_status, s.confidence, s.as_of_date,
       (SELECT COUNT(*) FROM applications a WHERE a.site_id = s.id)          AS n_applications,
       (SELECT COUNT(*) FROM community_events c WHERE c.site_id = s.id)      AS n_community_events,
       (SELECT COUNT(*) FROM regulatory_events r WHERE r.site_id = s.id)      AS n_regulatory_events,
       (SELECT COUNT(*) FROM instrument_application i WHERE i.site_id = s.id) AS n_instruments
FROM sites s
LEFT JOIN entities op ON op.id = s.operator_id
LEFT JOIN entities an ON an.id = s.anchor_tenant_id
LEFT JOIN sources src ON src.id = s.source_id;

-- ---------------------------------------------------------------------
-- L. Post-consent modifications (added v1.5.0, RG-034)
-- A consent's original capacity is not its operating capacity. Fuel storage,
-- generator counts, building height and power consumption all change by
-- modification, and modifications appear in no headline pipeline figure.
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS modifications (
    id            INTEGER PRIMARY KEY,
    site_id       TEXT REFERENCES sites(id),
    parent_case   TEXT,                        -- the SSD being modified
    mod_case      TEXT NOT NULL,               -- e.g. SSD-10330-Mod-2
    title         TEXT NOT NULL,
    lga           TEXT,
    stage         TEXT,
    decision      TEXT,
    determination_date TEXT,
    change_type   TEXT CHECK (change_type IN (
                    'capacity_increase','fuel_storage_increase','generator_increase',
                    'height_increase','layout','design','fit_out','fire_or_safety',
                    'road_or_access','landscaping','scale_reduction','other')),
    what_changed  TEXT,                        -- the material change, in words
    materiality   INTEGER CHECK (materiality BETWEEN 1 AND 5),
    notes         TEXT,
    fact_status   TEXT NOT NULL DEFAULT 'VERIFIED' CHECK (fact_status IN
                    ('VERIFIED','REPORTED','CLAIMED','GAP')),
    source_id     TEXT REFERENCES sources(id),
    confidence    TEXT CHECK (confidence IN ('high','medium','low')),
    as_of_date    TEXT
);
CREATE INDEX IF NOT EXISTS idx_mod_parent ON modifications(parent_case);
CREATE INDEX IF NOT EXISTS idx_mod_site   ON modifications(site_id);

CREATE VIEW IF NOT EXISTS v_consent_drift AS
SELECT m.parent_case, s.name AS site, m.lga, m.mod_case, m.title, m.change_type,
       m.decision, m.determination_date, m.materiality, m.what_changed, m.fact_status
FROM modifications m
LEFT JOIN sites s ON s.id = m.site_id
ORDER BY m.determination_date DESC;

-- ---------------------------------------------------------------------
-- M. Lobbying and policy influence (added v1.9.0)
-- The NSW inquiry's terms of reference (h)(iv) asks about "the impact of
-- lobbying and donations on government policy setting surrounding data centre
-- developments". Nothing else in this schema can hold that evidence.
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS lobbying (
    id            INTEGER PRIMARY KEY,
    actor_id      TEXT NOT NULL REFERENCES entities(id),   -- who is doing the lobbying
    person        TEXT,                                    -- named individual, and their role
    channel       TEXT NOT NULL CHECK (channel IN (
                    'peak_body_board','peak_body_membership','peak_body_submission',
                    'own_submission','parliamentary_evidence','ministerial_meeting',
                    'media_campaign','commissioned_research','industry_forum',
                    'political_donation','lobbyist_register','revolving_door','other')),
    recipient     TEXT,                                    -- government body / inquiry / minister
    event_date    TEXT,
    instrument    TEXT,                                    -- submission no, report title, register
    position      TEXT NOT NULL,                           -- what was asked for, in their words
    outcome       TEXT,                                    -- what happened to it
    aligned_with_outcome INTEGER CHECK (aligned_with_outcome IN (0,1)),
    disclosed     INTEGER NOT NULL DEFAULT 1 CHECK (disclosed IN (0,1)),
    notes         TEXT,
    fact_status   TEXT NOT NULL DEFAULT 'REPORTED' CHECK (fact_status IN
                    ('VERIFIED','REPORTED','CLAIMED','GAP')),
    source_id     TEXT REFERENCES sources(id),
    confidence    TEXT CHECK (confidence IN ('high','medium','low')),
    as_of_date    TEXT
);
CREATE INDEX IF NOT EXISTS idx_lobby_actor ON lobbying(actor_id);
CREATE INDEX IF NOT EXISTS idx_lobby_channel ON lobbying(channel);

CREATE VIEW IF NOT EXISTS v_influence AS
SELECT e.name AS actor, l.person, l.channel, l.recipient, l.event_date, l.instrument,
       l.position, l.outcome, l.disclosed, l.fact_status, l.confidence, s.url AS source_url
FROM lobbying l
JOIN entities e ON e.id = l.actor_id
LEFT JOIN sources s ON s.id = l.source_id
ORDER BY l.event_date DESC;
