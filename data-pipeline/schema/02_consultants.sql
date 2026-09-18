-- ADCO schema migration 02: the CONSULTANCY / ADVISORY layer
-- v2.0.0, 2026-09-18
--
-- WHY THIS LAYER EXISTS
-- ---------------------
-- Data centre approvals in Australia are not written by developers and read by regulators.
-- They are assembled by a third group that the Observatory had until now only captured
-- incidentally, inside entity notes: the consultancies. Three separate populations belong here,
-- and conflating them was the original error.
--
--   (1) TECHNICAL CONSULTANTS who author the evidence base for a consent - acoustic, CFD,
--       hydrogeological, traffic, ESD reports. Arup authored the CFD modelling advice attached
--       to a data centre application. Their numbers become the conditions.
--   (2) PLANNING AGENTS who are the named Schedule 1 APPLICANT on the consent itself. In 4 of
--       the 20 NSW consents in the battery the named applicant is a consultancy or an opaque
--       SPV, not the operator. That is a transparency finding, not a data-entry quirk.
--   (3) SYSTEMS INTEGRATORS who hold the government's own IT contracts and sit on the peak
--       bodies that write the sector's policy submissions. TCS is the worked example: BCA
--       member, ~$234m-$353m of Australian public contracts, and from November 2025 a
--       data centre OPERATOR in its own right through HyperVault.
--
-- Every table here carries the standard provenance triple (fact_status, confidence, as_of_date)
-- and a source_id foreign key. Nothing enters as VERIFIED unless it was read in a primary
-- document; aggregator-sourced figures enter as REPORTED with the aggregator named, and
-- user-supplied or second-hand figures enter as CLAIMED until tested.

-- ---------------------------------------------------------------------------
-- 1. consultancy_profile : one row per firm in the advisory chain
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS consultancy_profile (
    entity_id           TEXT PRIMARY KEY REFERENCES entities(id),
    firm_type           TEXT CHECK (firm_type IN (
                            'engineering','acoustics','planning_consultant','environmental',
                            'hydrogeology','traffic','systems_integrator','big4','management_consulting',
                            'law_firm','economic_consulting','surveying','other')),
    role_in_pipeline    TEXT CHECK (role_in_pipeline IN (
                            'eis_author','specialist_report_author','planning_agent',
                            'named_applicant','project_manager','operator_advisor',
                            'government_advisor','government_contractor','peer_reviewer')),
    peak_body_member    TEXT,               -- 'BCA', 'DCA', 'AIIA', 'Consult Australia', NULL
    on_peak_body_board  INTEGER CHECK (on_peak_body_board IN (0,1)),
    also_an_operator    INTEGER NOT NULL DEFAULT 0 CHECK (also_an_operator IN (0,1)),
                                            -- 1 = the firm is itself building/operating data centres
    operator_vehicle    TEXT,               -- e.g. 'HyperVault (JV with TPG)'
    au_public_sector_exposure_aud REAL,     -- total tracked government contract value
    exposure_as_of      TEXT,
    exposure_source_tier TEXT CHECK (exposure_source_tier IN (
                            'primary_portal','aggregator','company_disclosure','media','estimate')),
    offshore_delivery   TEXT,               -- onshore/offshore delivery model, if evidenced
    notes               TEXT,
    fact_status         TEXT NOT NULL DEFAULT 'REPORTED' CHECK (fact_status IN
                            ('VERIFIED','REPORTED','CLAIMED','GAP')),
    source_id           TEXT REFERENCES sources(id),
    confidence          TEXT CHECK (confidence IN ('high','medium','low')),
    as_of_date          TEXT
);

-- ---------------------------------------------------------------------------
-- 2. gov_contracts : taxpayer-funded contracts held by advisory firms
--    One row per DISTINCT contract. Aggregators double-count the same contract
--    when it is published on two portals; is_duplicate_of exists to record that
--    rather than silently inflating a total.
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS gov_contracts (
    id                  INTEGER PRIMARY KEY,
    supplier_entity_id  TEXT REFERENCES entities(id),
    supplier_name       TEXT NOT NULL,      -- as written on the notice
    agency              TEXT NOT NULL,
    agency_entity_id    TEXT REFERENCES entities(id),
    contract_title      TEXT NOT NULL,
    value_aud           REAL,
    value_incl_gst      INTEGER CHECK (value_incl_gst IN (0,1)),
    portal              TEXT NOT NULL CHECK (portal IN (
                            'AusTender','buy.nsw','QTenders','Buying for Victoria','SA Tenders',
                            'WA Tenders','TAS Tenders','NT Tenders','ACT Tenders','TenderLink',
                            'VendorPanel','Gateway','aggregator','other')),
    portal_id           TEXT,               -- CAN-100812, CN-xxxx, notice GUID
    award_published     TEXT,               -- date the NOTICE was published
    contract_start      TEXT,               -- effective date of the contract itself
    contract_end        TEXT,
    method_of_tendering TEXT,               -- 'Direct negotiation', 'Open', 'Limited', ...
    category            TEXT,               -- UNSPSC / portal category
    abn                 TEXT,
    is_duplicate_of     INTEGER REFERENCES gov_contracts(id),
                                            -- same underlying contract, second portal record
    duplicate_note      TEXT,
    verification_note   TEXT,               -- what was checked against what
    fact_status         TEXT NOT NULL DEFAULT 'REPORTED' CHECK (fact_status IN
                            ('VERIFIED','REPORTED','CLAIMED','GAP')),
    source_id           TEXT REFERENCES sources(id),
    confidence          TEXT CHECK (confidence IN ('high','medium','low')),
    as_of_date          TEXT,
    UNIQUE (supplier_name, agency, contract_title, portal_id)
);

-- ---------------------------------------------------------------------------
-- 3. consultant_role : who did what on which data centre project
--    This is the table that separates the AGENT from the PROPONENT.
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS consultant_role (
    id                  INTEGER PRIMARY KEY,
    project_slug        TEXT NOT NULL,      -- NSW planning portal slug, joins to case_handling
    case_id             TEXT,
    site_id             TEXT REFERENCES sites(id),
    entity_id           TEXT NOT NULL REFERENCES entities(id),
    role                TEXT NOT NULL CHECK (role IN (
                            'named_applicant','eis_author','acoustic_consultant','cfd_modelling',
                            'hydrogeology','traffic_assessment','esd_consultant','bushfire_ecology',
                            'geotechnical','contamination','heritage','project_manager',
                            'planning_agent','peer_reviewer','other')),
    evidence_document   TEXT,               -- the attachment slug or consent schedule
    is_named_applicant  INTEGER NOT NULL DEFAULT 0 CHECK (is_named_applicant IN (0,1)),
    true_proponent      TEXT,               -- the operator, where separately evidenced
    proponent_known     INTEGER NOT NULL DEFAULT 0 CHECK (proponent_known IN (0,1)),
    notes               TEXT,
    fact_status         TEXT NOT NULL DEFAULT 'REPORTED' CHECK (fact_status IN
                            ('VERIFIED','REPORTED','CLAIMED','GAP')),
    source_id           TEXT REFERENCES sources(id),
    confidence          TEXT CHECK (confidence IN ('high','medium','low')),
    as_of_date          TEXT
);

-- ---------------------------------------------------------------------------
-- 4. case_handling : the NSW assessment officer and the decision instrument
--    Extracted from the signed consent and the planning portal node. Establishes
--    WHO decided, UNDER WHAT DELEGATION, ON WHAT DATE.
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS case_handling (
    id                  INTEGER PRIMARY KEY,
    case_id             TEXT NOT NULL,
    project_slug        TEXT NOT NULL,
    officer_name        TEXT,
    officer_role        TEXT CHECK (officer_role IN (
                            'case_planner','delegate_signatory','determination_authority',
                            'director','acting_director','executive_director','other')),
    acting              INTEGER NOT NULL DEFAULT 0 CHECK (acting IN (0,1)),
    consent_authority   TEXT,               -- 'Minister for Planning and Public Spaces', 'IPC'
    delegation_date     TEXT,               -- date the ministerial delegation was executed
    decision_date       TEXT,
    file_reference      TEXT,               -- e.g. EF 24/10658
    notes               TEXT,
    fact_status         TEXT NOT NULL DEFAULT 'REPORTED' CHECK (fact_status IN
                            ('VERIFIED','REPORTED','CLAIMED','GAP')),
    source_id           TEXT REFERENCES sources(id),
    confidence          TEXT CHECK (confidence IN ('high','medium','low')),
    as_of_date          TEXT,
    UNIQUE (case_id, project_slug, officer_role)
);

-- ---------------------------------------------------------------------------
-- VIEWS
-- ---------------------------------------------------------------------------

-- Public money flowing to firms that also advise on, or operate in, the sector.
CREATE VIEW IF NOT EXISTS v_consultant_public_money AS
SELECT e.name                        AS firm,
       c.agency,
       c.contract_title,
       c.value_aud,
       c.portal,
       c.portal_id,
       c.method_of_tendering,
       c.contract_start,
       c.contract_end,
       c.is_duplicate_of,
       c.fact_status,
       c.confidence,
       s.url                          AS source_url
FROM gov_contracts c
JOIN entities e          ON e.id = c.supplier_entity_id
LEFT JOIN sources s      ON s.id = c.source_id
ORDER BY c.value_aud DESC;

-- De-duplicated spend totals per firm per agency. This is the honest number.
CREATE VIEW IF NOT EXISTS v_consultant_spend_totals AS
SELECT e.name AS firm,
       c.agency,
       COUNT(*)                                              AS records,
       SUM(CASE WHEN c.is_duplicate_of IS NULL THEN 1 ELSE 0 END) AS distinct_contracts,
       ROUND(SUM(CASE WHEN c.is_duplicate_of IS NULL THEN c.value_aud ELSE 0 END), 2)
                                                             AS distinct_value_aud,
       ROUND(SUM(c.value_aud), 2)                            AS gross_value_aud,
       ROUND(SUM(c.value_aud)
             - SUM(CASE WHEN c.is_duplicate_of IS NULL THEN c.value_aud ELSE 0 END), 2)
                                                             AS double_counted_aud
FROM gov_contracts c
JOIN entities e ON e.id = c.supplier_entity_id
GROUP BY e.name, c.agency
ORDER BY distinct_value_aud DESC;

-- Concentration of decision-making in the NSW data centre pipeline.
CREATE VIEW IF NOT EXISTS v_case_officer_load AS
SELECT officer_name,
       officer_role,
       COUNT(*)                        AS cases,
       MIN(decision_date)              AS earliest_decision,
       MAX(decision_date)              AS latest_decision,
       GROUP_CONCAT(DISTINCT delegation_date) AS delegations_used
FROM case_handling
WHERE officer_name IS NOT NULL
GROUP BY officer_name, officer_role
ORDER BY cases DESC;

-- Consents where the named applicant is NOT the operator.
CREATE VIEW IF NOT EXISTS v_applicant_vs_proponent AS
SELECT cr.project_slug,
       cr.case_id,
       e.name          AS named_applicant,
       cp.firm_type,
       cr.true_proponent,
       cr.proponent_known,
       cr.fact_status,
       cr.source_id
FROM consultant_role cr
JOIN entities e            ON e.id = cr.entity_id
LEFT JOIN consultancy_profile cp ON cp.entity_id = e.id
WHERE cr.is_named_applicant = 1
ORDER BY cr.proponent_known, cr.project_slug;

-- Which consultancies are inside the influence network AND holding public money.
CREATE VIEW IF NOT EXISTS v_consultant_influence AS
SELECT e.name                              AS firm,
       cp.peak_body_member,
       cp.on_peak_body_board,
       cp.also_an_operator,
       cp.operator_vehicle,
       cp.au_public_sector_exposure_aud,
       cp.exposure_source_tier,
       l.channel,
       l.recipient,
       l.event_date,
       l.instrument,
       l.fact_status                       AS lobbying_fact_status
FROM consultancy_profile cp
JOIN entities e ON e.id = cp.entity_id
LEFT JOIN lobbying l ON l.actor_id = e.id
ORDER BY cp.au_public_sector_exposure_aud DESC;

-- Reconciliation between what is ENUMERATED in gov_contracts and what the
-- aggregator PUBLISHES for the whole portfolio. These are different quantities and
-- conflating them is exactly the error this layer exists to prevent.
CREATE VIEW IF NOT EXISTS v_contract_reconciliation AS
SELECT
    e.name AS firm,
    (SELECT COUNT(*) FROM gov_contracts g WHERE g.supplier_entity_id = e.id)                AS enumerated_records,
    (SELECT COUNT(*) FROM gov_contracts g WHERE g.supplier_entity_id = e.id
       AND g.is_duplicate_of IS NULL)                                                       AS enumerated_distinct,
    (SELECT ROUND(SUM(g.value_aud), 2) FROM gov_contracts g
       WHERE g.supplier_entity_id = e.id)                                                   AS enumerated_gross_aud,
    (SELECT ROUND(SUM(g.value_aud), 2) FROM gov_contracts g
       WHERE g.supplier_entity_id = e.id AND g.is_duplicate_of IS NULL)                      AS enumerated_distinct_aud,
    (SELECT m.value FROM metrics m WHERE m.metric_name LIKE
       '%published aggregator total%' AND m.scope = 'national' LIMIT 1)                      AS published_portfolio_aud,
    (SELECT m.value FROM metrics m WHERE m.metric_name LIKE
       '%Observatory de-duplicated total%' AND m.scope = 'national' LIMIT 1)                 AS deduplicated_portfolio_aud,
    (SELECT m.value FROM metrics m WHERE m.metric_name LIKE
       '%distinct Australian public contracts%' LIMIT 1)                                     AS deduplicated_contract_count
FROM entities e
WHERE e.id IN (SELECT DISTINCT supplier_entity_id FROM gov_contracts);
