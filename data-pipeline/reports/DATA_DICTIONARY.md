# ADCO data dictionary

Schema v1.0.0 · generated from the live database by `scripts/gen_dictionary.py`.

30 tables, 16 views. Conventions: power in **MW**, water in **kL/yr**, money in
**AUD (REAL)**, dates **ISO-8601** (`YYYY-MM-DD`, or `YYYY-MM` where the day is unknown).

Every factual table carries the four provenance columns `fact_status`, `confidence`, `as_of_date`
and `source_id` (FK → `sources`). `source_refs` provides the normalised link plus an optional
verbatim quote.

---

## `applications` (table, 54 rows)

Planning and approval pathways, including the outcome and the conditions imposed. Distinguishes state-significant, local council, fast-track and non-planning approvals (grid, water, licence).

| Column | Type | Constraints |
|---|---|---|
| `id` | INTEGER | **PK** |
| `site_id` | TEXT | NOT NULL → `sites.id` |
| `jurisdiction` | TEXT | NOT NULL |
| `pathway` | TEXT | NOT NULL |
| `reference` | TEXT |  |
| `lodged` | TEXT |  |
| `decided` | TEXT |  |
| `outcome` | TEXT |  |
| `decision_maker` | TEXT |  |
| `capacity_mw_in_app` | REAL |  |
| `conditions_summary` | TEXT |  |
| `appeal_status` | TEXT |  |
| `notes` | TEXT |  |
| `fact_status` | TEXT | NOT NULL default `'REPORTED'` |
| `source_id` | TEXT | → `sources.id` |
| `confidence` | TEXT |  |
| `as_of_date` | TEXT |  |

## `case_handling` (table, 83 rows)

_No description recorded._

| Column | Type | Constraints |
|---|---|---|
| `id` | INTEGER | **PK** |
| `case_id` | TEXT | NOT NULL |
| `project_slug` | TEXT | NOT NULL |
| `officer_name` | TEXT |  |
| `officer_role` | TEXT |  |
| `acting` | INTEGER | NOT NULL default `0` |
| `consent_authority` | TEXT |  |
| `delegation_date` | TEXT |  |
| `decision_date` | TEXT |  |
| `file_reference` | TEXT |  |
| `notes` | TEXT |  |
| `fact_status` | TEXT | NOT NULL default `'REPORTED'` |
| `source_id` | TEXT | → `sources.id` |
| `confidence` | TEXT |  |
| `as_of_date` | TEXT |  |

## `community_events` (table, 24 rows)

Dated friction: objections, protests, petitions, council deferrals and rejections, litigation, political interventions, school and institution objections, benefit agreements. `severity` 1–5, where 5 is a formal council objection.

| Column | Type | Constraints |
|---|---|---|
| `id` | INTEGER | **PK** |
| `event_date` | TEXT |  |
| `site_id` | TEXT | → `sites.id` |
| `group_id` | TEXT | → `community_groups.id` |
| `locality` | TEXT |  |
| `state` | TEXT |  |
| `event_type` | TEXT | NOT NULL |
| `actor` | TEXT |  |
| `summary` | TEXT | NOT NULL |
| `severity` | INTEGER |  |
| `outcome` | TEXT |  |
| `notes` | TEXT |  |
| `fact_status` | TEXT | NOT NULL default `'REPORTED'` |
| `source_id` | TEXT | → `sources.id` |
| `confidence` | TEXT |  |
| `as_of_date` | TEXT |  |

## `community_groups` (table, 6 rows)

Register of campaign organisations. Only five are recorded; RG-016 expands it.

| Column | Type | Constraints |
|---|---|---|
| `id` | TEXT | **PK** |
| `name` | TEXT | NOT NULL |
| `locality` | TEXT |  |
| `state` | TEXT |  |
| `formed` | TEXT |  |
| `focus` | TEXT |  |
| `contact_or_url` | TEXT |  |
| `notes` | TEXT |  |
| `fact_status` | TEXT | NOT NULL default `'REPORTED'` |
| `source_id` | TEXT | → `sources.id` |
| `confidence` | TEXT |  |
| `as_of_date` | TEXT |  |

## `consultancy_profile` (table, 8 rows)

_No description recorded._

| Column | Type | Constraints |
|---|---|---|
| `entity_id` | TEXT | **PK** → `entities.id` |
| `firm_type` | TEXT |  |
| `role_in_pipeline` | TEXT |  |
| `peak_body_member` | TEXT |  |
| `on_peak_body_board` | INTEGER |  |
| `also_an_operator` | INTEGER | NOT NULL default `0` |
| `operator_vehicle` | TEXT |  |
| `au_public_sector_exposure_aud` | REAL |  |
| `exposure_as_of` | TEXT |  |
| `exposure_source_tier` | TEXT |  |
| `offshore_delivery` | TEXT |  |
| `notes` | TEXT |  |
| `fact_status` | TEXT | NOT NULL default `'REPORTED'` |
| `source_id` | TEXT | → `sources.id` |
| `confidence` | TEXT |  |
| `as_of_date` | TEXT |  |

## `consultant_role` (table, 22 rows)

_No description recorded._

| Column | Type | Constraints |
|---|---|---|
| `id` | INTEGER | **PK** |
| `project_slug` | TEXT | NOT NULL |
| `case_id` | TEXT |  |
| `site_id` | TEXT | → `sites.id` |
| `entity_id` | TEXT | NOT NULL → `entities.id` |
| `role` | TEXT | NOT NULL |
| `evidence_document` | TEXT |  |
| `is_named_applicant` | INTEGER | NOT NULL default `0` |
| `true_proponent` | TEXT |  |
| `proponent_known` | INTEGER | NOT NULL default `0` |
| `notes` | TEXT |  |
| `fact_status` | TEXT | NOT NULL default `'REPORTED'` |
| `source_id` | TEXT | → `sources.id` |
| `confidence` | TEXT |  |
| `as_of_date` | TEXT |  |

## `energy_agreements` (table, 1 rows)

PPAs, vPPAs, green tariffs, firming, gas, network and water agreements. `additionality` is the load-bearing field: a PPA against an existing asset is not new generation.

| Column | Type | Constraints |
|---|---|---|
| `id` | INTEGER | **PK** |
| `buyer_id` | TEXT | NOT NULL → `entities.id` |
| `seller_id` | TEXT | → `entities.id` |
| `site_id` | TEXT | → `sites.id` |
| `agreement_type` | TEXT | NOT NULL |
| `technology` | TEXT |  |
| `capacity_mw` | REAL |  |
| `annual_volume_gwh` | REAL |  |
| `term_years` | REAL |  |
| `signed` | TEXT |  |
| `commences` | TEXT |  |
| `expiry` | TEXT |  |
| `additionality` | TEXT |  |
| `in_nsw` | INTEGER |  |
| `wind_share_pct` | REAL |  |
| `storage_share_pct` | REAL |  |
| `disclosed` | INTEGER | NOT NULL default `0` |
| `notes` | TEXT |  |
| `fact_status` | TEXT | NOT NULL default `'REPORTED'` |
| `source_id` | TEXT | → `sources.id` |
| `confidence` | TEXT |  |
| `as_of_date` | TEXT |  |

## `engineering_claims` (table, 11 rows)

Pillar E. Each proposition from the brief is tested against Australian evidence, given a verdict, and — where it fails — replaced with a specification anchored to an existing policy instrument, plus the residual gap that policy still leaves.

| Column | Type | Constraints |
|---|---|---|
| `id` | INTEGER | **PK** |
| `claim_label` | TEXT | NOT NULL |
| `claim_status` | TEXT | NOT NULL |
| `premise_check` | TEXT | NOT NULL |
| `australia_reality` | TEXT | NOT NULL |
| `replacement_spec` | TEXT |  |
| `existing_policy_hook` | TEXT |  |
| `residual_gap` | TEXT |  |
| `evidence_site_ids` | TEXT |  |
| `source_ids` | TEXT |  |
| `as_of_date` | TEXT |  |

## `entities` (table, 138 rows)

Companies, funds, agencies, councils, community groups and utilities. `domicile` is the country of ultimate control, which is the field that matters for sovereignty analysis — it is not the same as where the entity trades.

| Column | Type | Constraints |
|---|---|---|
| `id` | TEXT | **PK** |
| `name` | TEXT | NOT NULL |
| `legal_name` | TEXT |  |
| `entity_type` | TEXT | NOT NULL |
| `domicile` | TEXT |  |
| `hq_country` | TEXT |  |
| `asx_ticker` | TEXT |  |
| `website` | TEXT |  |
| `notes` | TEXT |  |
| `fact_status` | TEXT | NOT NULL default `'REPORTED'` |
| `source_id` | TEXT | → `sources.id` |
| `confidence` | TEXT |  |
| `as_of_date` | TEXT |  |

## `entity_aliases` (table, 11 rows)

Trading names, SPVs and former names, so that scraped records can be resolved to a canonical entity.

| Column | Type | Constraints |
|---|---|---|
| `id` | INTEGER | **PK** |
| `entity_id` | TEXT | NOT NULL → `entities.id` |
| `alias` | TEXT | NOT NULL |

## `financial_flows` (table, 10 rows)

Money moving: equity, acquisitions, debt, capital raises, land purchases and capex commitments, with a `foreign_control` flag.

| Column | Type | Constraints |
|---|---|---|
| `id` | INTEGER | **PK** |
| `flow_date` | TEXT |  |
| `flow_type` | TEXT | NOT NULL |
| `from_entity_id` | TEXT | → `entities.id` |
| `to_entity_id` | TEXT | → `entities.id` |
| `site_id` | TEXT | → `sites.id` |
| `amount_aud` | REAL |  |
| `amount_original` | REAL |  |
| `currency_original` | TEXT |  |
| `vehicle` | TEXT |  |
| `foreign_control` | INTEGER |  |
| `notes` | TEXT |  |
| `fact_status` | TEXT | NOT NULL default `'REPORTED'` |
| `source_id` | TEXT | → `sources.id` |
| `confidence` | TEXT |  |
| `as_of_date` | TEXT |  |

## `gov_contracts` (table, 29 rows)

_No description recorded._

| Column | Type | Constraints |
|---|---|---|
| `id` | INTEGER | **PK** |
| `supplier_entity_id` | TEXT | → `entities.id` |
| `supplier_name` | TEXT | NOT NULL |
| `agency` | TEXT | NOT NULL |
| `agency_entity_id` | TEXT | → `entities.id` |
| `contract_title` | TEXT | NOT NULL |
| `value_aud` | REAL |  |
| `value_incl_gst` | INTEGER |  |
| `portal` | TEXT | NOT NULL |
| `portal_id` | TEXT |  |
| `award_published` | TEXT |  |
| `contract_start` | TEXT |  |
| `contract_end` | TEXT |  |
| `method_of_tendering` | TEXT |  |
| `category` | TEXT |  |
| `abn` | TEXT |  |
| `is_duplicate_of` | INTEGER | → `gov_contracts.id` |
| `duplicate_note` | TEXT |  |
| `verification_note` | TEXT |  |
| `fact_status` | TEXT | NOT NULL default `'REPORTED'` |
| `source_id` | TEXT | → `sources.id` |
| `confidence` | TEXT |  |
| `as_of_date` | TEXT |  |

## `incentives` (table, 9 rows)

The subsidy register. Covers cash concessions AND in-kind support (fast-tracking, approvals authorities, co-funded infrastructure), because in Australia the latter is what actually exists. `conditionality_score` is 0–5; `domestic_compute_allocation` records whether sovereign compute is reserved.

| Column | Type | Constraints |
|---|---|---|
| `id` | INTEGER | **PK** |
| `jurisdiction` | TEXT | NOT NULL |
| `granting_body` | TEXT |  |
| `recipient_id` | TEXT | → `entities.id` |
| `site_id` | TEXT | → `sites.id` |
| `incentive_type` | TEXT | NOT NULL |
| `instrument` | TEXT |  |
| `amount_aud` | REAL |  |
| `start_date` | TEXT |  |
| `end_date` | TEXT |  |
| `conditions` | TEXT |  |
| `conditionality_score` | INTEGER |  |
| `domestic_compute_allocation` | INTEGER |  |
| `disclosed` | INTEGER | NOT NULL default `0` |
| `notes` | TEXT |  |
| `fact_status` | TEXT | NOT NULL default `'REPORTED'` |
| `source_id` | TEXT | → `sources.id` |
| `confidence` | TEXT |  |
| `as_of_date` | TEXT |  |

## `ingest_log` (table, 119 rows)

Audit trail of every curated pack load: what was inserted, updated and rejected.

| Column | Type | Constraints |
|---|---|---|
| `id` | INTEGER | **PK** |
| `run_at` | TEXT | NOT NULL |
| `pack` | TEXT | NOT NULL |
| `table_name` | TEXT | NOT NULL |
| `action` | TEXT | NOT NULL |
| `rows_affected` | INTEGER | NOT NULL default `0` |
| `detail` | TEXT |  |

## `instrument_application` (table, 8 rows)

How an instrument actually bites on a named site or entity, and whether they comply. This is where an exemption or an adverse finding is recorded.

| Column | Type | Constraints |
|---|---|---|
| `id` | INTEGER | **PK** |
| `instrument_id` | TEXT | NOT NULL → `legal_instruments.id` |
| `site_id` | TEXT | → `sites.id` |
| `entity_id` | TEXT | → `entities.id` |
| `applies_from` | TEXT |  |
| `obligation` | TEXT |  |
| `compliance_status` | TEXT |  |
| `evidence` | TEXT |  |
| `notes` | TEXT |  |
| `fact_status` | TEXT | NOT NULL default `'REPORTED'` |
| `source_id` | TEXT | → `sources.id` |
| `confidence` | TEXT |  |
| `as_of_date` | TEXT |  |

## `land_events` (table, 1 rows)

Land acquisition, option, rezoning and leasehold events. Where the domestic retirement capital shows up in this sector.

| Column | Type | Constraints |
|---|---|---|
| `id` | INTEGER | **PK** |
| `site_id` | TEXT | → `sites.id` |
| `event_date` | TEXT |  |
| `event_type` | TEXT | NOT NULL |
| `seller_id` | TEXT | → `entities.id` |
| `buyer_id` | TEXT | → `entities.id` |
| `area_ha` | REAL |  |
| `value_aud` | REAL |  |
| `conditionality` | TEXT |  |
| `notes` | TEXT |  |
| `fact_status` | TEXT | NOT NULL default `'REPORTED'` |
| `source_id` | TEXT | → `sources.id` |
| `confidence` | TEXT |  |
| `as_of_date` | TEXT |  |

## `legal_instruments` (table, 22 rows)

Acts, regulations, rules, determinations, bills, policies, guidelines, strategies, codes and inquiries. `binding` is the field that separates the Commonwealth Expectations (0) from the Clean Air Regulation (1).

| Column | Type | Constraints |
|---|---|---|
| `id` | TEXT | **PK** |
| `name` | TEXT | NOT NULL |
| `jurisdiction` | TEXT | NOT NULL |
| `instrument_type` | TEXT | NOT NULL |
| `status` | TEXT | NOT NULL |
| `made` | TEXT |  |
| `commenced` | TEXT |  |
| `binding` | INTEGER | NOT NULL default `1` |
| `summary` | TEXT |  |
| `relevance` | TEXT |  |
| `url` | TEXT |  |
| `fact_status` | TEXT | NOT NULL default `'VERIFIED'` |
| `source_id` | TEXT | → `sources.id` |
| `confidence` | TEXT |  |
| `as_of_date` | TEXT |  |

## `lobbying` (table, 15 rows)

_No description recorded._

| Column | Type | Constraints |
|---|---|---|
| `id` | INTEGER | **PK** |
| `actor_id` | TEXT | NOT NULL → `entities.id` |
| `person` | TEXT |  |
| `channel` | TEXT | NOT NULL |
| `recipient` | TEXT |  |
| `event_date` | TEXT |  |
| `instrument` | TEXT |  |
| `position` | TEXT | NOT NULL |
| `outcome` | TEXT |  |
| `aligned_with_outcome` | INTEGER |  |
| `disclosed` | INTEGER | NOT NULL default `1` |
| `notes` | TEXT |  |
| `fact_status` | TEXT | NOT NULL default `'REPORTED'` |
| `source_id` | TEXT | → `sources.id` |
| `confidence` | TEXT |  |
| `as_of_date` | TEXT |  |

## `metrics` (table, 340 rows)

Time series of system-level figures. `basis` is mandatory discipline: actual / pipeline / signed / enquiry / forecast. Enquiry and signed figures are never summed.

| Column | Type | Constraints |
|---|---|---|
| `id` | INTEGER | **PK** |
| `as_of` | TEXT | NOT NULL |
| `scope` | TEXT | NOT NULL |
| `metric_name` | TEXT | NOT NULL |
| `value` | REAL | NOT NULL |
| `unit` | TEXT | NOT NULL |
| `basis` | TEXT |  |
| `scenario` | TEXT |  |
| `notes` | TEXT |  |
| `fact_status` | TEXT | NOT NULL default `'REPORTED'` |
| `source_id` | TEXT | → `sources.id` |
| `confidence` | TEXT |  |
| `as_of_date` | TEXT |  |

## `modifications` (table, 17 rows)

_No description recorded._

| Column | Type | Constraints |
|---|---|---|
| `id` | INTEGER | **PK** |
| `site_id` | TEXT | → `sites.id` |
| `parent_case` | TEXT |  |
| `mod_case` | TEXT | NOT NULL |
| `title` | TEXT | NOT NULL |
| `lga` | TEXT |  |
| `stage` | TEXT |  |
| `decision` | TEXT |  |
| `determination_date` | TEXT |  |
| `change_type` | TEXT |  |
| `what_changed` | TEXT |  |
| `materiality` | INTEGER |  |
| `notes` | TEXT |  |
| `fact_status` | TEXT | NOT NULL default `'VERIFIED'` |
| `source_id` | TEXT | → `sources.id` |
| `confidence` | TEXT |  |
| `as_of_date` | TEXT |  |

## `ownership` (table, 12 rows)

The control chain. One row per holder per period; `effective_to IS NULL` means current. Carries the FIRB flag and outcome. This is Pillar B's core table.

| Column | Type | Constraints |
|---|---|---|
| `id` | INTEGER | **PK** |
| `holder_id` | TEXT | NOT NULL → `entities.id` |
| `target_id` | TEXT | NOT NULL → `entities.id` |
| `stake_pct` | REAL |  |
| `instrument` | TEXT |  |
| `effective_from` | TEXT |  |
| `effective_to` | TEXT |  |
| `transaction_value_aud` | REAL |  |
| `event` | TEXT |  |
| `firb_reviewed` | INTEGER | NOT NULL default `0` |
| `firb_outcome` | TEXT |  |
| `notes` | TEXT |  |
| `fact_status` | TEXT | NOT NULL default `'REPORTED'` |
| `source_id` | TEXT | → `sources.id` |
| `confidence` | TEXT |  |
| `as_of_date` | TEXT |  |

## `power_profile` (table, 19 rows)

Engineering and grid reality per site: connection type and point, NCA status, who funds augmentation, PUE, demand flexibility, storage, synchronous condenser flag, on-site gas, generator count and fuel, diesel inventory, emission standard, EPA licence, Safeguard exposure.

| Column | Type | Constraints |
|---|---|---|
| `id` | INTEGER | **PK** |
| `site_id` | TEXT | NOT NULL → `sites.id` |
| `connection_type` | TEXT |  |
| `network_business_id` | TEXT | → `entities.id` |
| `connection_point` | TEXT |  |
| `nca_status` | TEXT |  |
| `nca_date` | TEXT |  |
| `augmentation_funded_by` | TEXT |  |
| `augmentation_detail` | TEXT |  |
| `max_demand_mw` | REAL |  |
| `average_load_mw` | REAL |  |
| `annual_energy_gwh` | REAL |  |
| `pue_design` | REAL |  |
| `pue_operating` | REAL |  |
| `demand_response_pct` | REAL |  |
| `demand_response_hours` | REAL |  |
| `battery_mw` | REAL |  |
| `battery_mwh` | REAL |  |
| `synchronous_condenser` | INTEGER | NOT NULL default `0` |
| `onsite_gas_mw` | REAL |  |
| `onsite_gas_type` | TEXT |  |
| `genset_count` | INTEGER |  |
| `genset_total_mw` | REAL |  |
| `genset_fuel` | TEXT |  |
| `genset_annual_test_hours` | REAL |  |
| `diesel_storage_kl` | REAL |  |
| `emission_standard` | TEXT |  |
| `epa_licence_id` | TEXT |  |
| `safeguard_mechanism_exposed` | INTEGER |  |
| `grid_services_role` | TEXT |  |
| `notes` | TEXT |  |
| `fact_status` | TEXT | NOT NULL default `'REPORTED'` |
| `source_id` | TEXT | → `sources.id` |
| `confidence` | TEXT |  |
| `as_of_date` | TEXT |  |

## `regulatory_events` (table, 25 rows)

Dated regulator actions: additional information requests, adverse findings, licence conditions, hearings, rule change requests, determinations, fast-track grants.

| Column | Type | Constraints |
|---|---|---|
| `id` | INTEGER | **PK** |
| `event_date` | TEXT | NOT NULL |
| `regulator_id` | TEXT | → `entities.id` |
| `instrument_id` | TEXT | → `legal_instruments.id` |
| `site_id` | TEXT | → `sites.id` |
| `entity_id` | TEXT | → `entities.id` |
| `event_type` | TEXT | NOT NULL |
| `summary` | TEXT | NOT NULL |
| `outcome` | TEXT |  |
| `notes` | TEXT |  |
| `fact_status` | TEXT | NOT NULL default `'REPORTED'` |
| `source_id` | TEXT | → `sources.id` |
| `confidence` | TEXT |  |
| `as_of_date` | TEXT |  |

## `renewable_claims` (table, 11 rows)

The audit table. A claim is `VERIFIED` only when contracted instruments satisfy an additionality test AND reconcile to Clean Energy Regulator certificate surrender and NGERS emissions data. Nothing meets that bar yet — RG-009 is the blocker.

| Column | Type | Constraints |
|---|---|---|
| `id` | INTEGER | **PK** |
| `claimant_id` | TEXT | NOT NULL → `entities.id` |
| `site_id` | TEXT | → `sites.id` |
| `claim_date` | TEXT |  |
| `claim_scope` | TEXT | NOT NULL |
| `claim_text` | TEXT | NOT NULL |
| `claim_type` | TEXT | NOT NULL |
| `target_year` | INTEGER |  |
| `instrument_relied_on` | TEXT |  |
| `lgc_surrender_evidence` | TEXT |  |
| `verification_status` | TEXT | NOT NULL default `'UNVERIFIED'` |
| `verification_note` | TEXT |  |
| `fact_status` | TEXT | NOT NULL default `'CLAIMED'` |
| `source_id` | TEXT | → `sources.id` |
| `confidence` | TEXT |  |
| `as_of_date` | TEXT |  |

## `research_gaps` (table, 88 rows)

The ingestion backlog and the list of things we do not know. Each row names the target source and the retrieval method. This is the project's work queue.

| Column | Type | Constraints |
|---|---|---|
| `id` | INTEGER | **PK** |
| `pillar` | TEXT | NOT NULL |
| `question` | TEXT | NOT NULL |
| `why_it_matters` | TEXT |  |
| `target_source` | TEXT |  |
| `retrieval_method` | TEXT |  |
| `priority` | INTEGER | NOT NULL default `3` |
| `status` | TEXT | NOT NULL default `'open'` |
| `owner` | TEXT |  |
| `opened` | TEXT | NOT NULL |
| `resolved_date` | TEXT |  |
| `notes` | TEXT |  |
| `fact_status` | TEXT | NOT NULL default `'VERIFIED'` |
| `source_id` | TEXT | → `sources.id` |
| `confidence` | TEXT |  |
| `as_of_date` | TEXT |  |

## `security_records` (table, 6 rows)

FIRB, SOCI Act, Critical Infrastructure Register, CIRMP, Hosting Certification Framework and related regimes, with the ultimate controller and any conditions.

| Column | Type | Constraints |
|---|---|---|
| `id` | INTEGER | **PK** |
| `subject_entity_id` | TEXT | → `entities.id` |
| `site_id` | TEXT | → `sites.id` |
| `regime` | TEXT | NOT NULL |
| `status` | TEXT |  |
| `foreign_control_pct` | REAL |  |
| `ultimate_controller` | TEXT |  |
| `determination_date` | TEXT |  |
| `conditions` | TEXT |  |
| `sovereign_data_carriage` | INTEGER |  |
| `notes` | TEXT |  |
| `fact_status` | TEXT | NOT NULL default `'REPORTED'` |
| `source_id` | TEXT | → `sources.id` |
| `confidence` | TEXT |  |
| `as_of_date` | TEXT |  |

## `sites` (table, 93 rows)

Physical facilities and proposals. Three capacity fields are stored separately and must never be summed: `it_capacity_mw` (critical load), `total_capacity_mw` (with cooling overhead), `max_capacity_mw` (full campus build-out). `market` records NEM / WEM / NT because the regulatory regime differs.

| Column | Type | Constraints |
|---|---|---|
| `id` | TEXT | **PK** |
| `name` | TEXT | NOT NULL |
| `operator_id` | TEXT | → `entities.id` |
| `owner_id` | TEXT | → `entities.id` |
| `anchor_tenant_id` | TEXT | → `entities.id` |
| `proponent` | TEXT |  |
| `suburb` | TEXT |  |
| `lga` | TEXT |  |
| `state` | TEXT | NOT NULL |
| `market` | TEXT | NOT NULL default `'NEM'` |
| `lat` | REAL |  |
| `lon` | REAL |  |
| `address` | TEXT |  |
| `status` | TEXT | NOT NULL |
| `it_capacity_mw` | REAL |  |
| `total_capacity_mw` | REAL |  |
| `max_capacity_mw` | REAL |  |
| `first_phase_mw` | REAL |  |
| `campus_area_ha` | REAL |  |
| `gfa_sqm` | REAL |  |
| `capital_cost_aud` | REAL |  |
| `construction_jobs` | INTEGER |  |
| `operational_jobs` | INTEGER |  |
| `operational_from` | TEXT |  |
| `target_completion` | TEXT |  |
| `nearest_cable_ls_km` | REAL |  |
| `nearest_cable_ls_name` | TEXT |  |
| `proximity_note` | TEXT |  |
| `hcf_certified` | TEXT |  |
| `notes` | TEXT |  |
| `fact_status` | TEXT | NOT NULL default `'REPORTED'` |
| `source_id` | TEXT | → `sources.id` |
| `confidence` | TEXT |  |
| `as_of_date` | TEXT |  |

## `source_refs` (table, 376 rows)

Normalised many-to-many link from any table row to a source, with an optional verbatim quote. `entity_table` + `entity_rowid` identify the row; for text-PK tables `entity_rowid` holds the text id (e.g. `SITE_MAMRE_ROAD`), otherwise the integer rowid.

| Column | Type | Constraints |
|---|---|---|
| `id` | INTEGER | **PK** |
| `entity_table` | TEXT | NOT NULL |
| `entity_rowid` | TEXT | NOT NULL |
| `source_id` | TEXT | NOT NULL → `sources.id` |
| `quote` | TEXT |  |

## `sources` (table, 153 rows)

Provenance root. Every factual row points here. Graded A–D by document class, not reputation.

| Column | Type | Constraints |
|---|---|---|
| `id` | TEXT | **PK** |
| `title` | TEXT | NOT NULL |
| `publisher` | TEXT | NOT NULL |
| `url` | TEXT | NOT NULL |
| `doc_type` | TEXT | NOT NULL |
| `published` | TEXT |  |
| `accessed` | TEXT | NOT NULL |
| `credibility` | TEXT | NOT NULL default `'B'` |
| `notes` | TEXT |  |

## `water_profile` (table, 3 rows)

Cooling technology, water source, supply agreement status, annual volume, WUE, potable dependency and drought response. The S7 row is the canonical case study in infrastructure sequencing failure.

| Column | Type | Constraints |
|---|---|---|
| `id` | INTEGER | **PK** |
| `site_id` | TEXT | NOT NULL → `sites.id` |
| `cooling_technology` | TEXT |  |
| `water_source` | TEXT |  |
| `supplier_id` | TEXT | → `entities.id` |
| `supply_agreement_status` | TEXT |  |
| `annual_water_kl` | REAL |  |
| `wue_design` | REAL |  |
| `wue_operating` | REAL |  |
| `potable_dependency` | INTEGER |  |
| `drought_response` | TEXT |  |
| `offset_commitment` | TEXT |  |
| `notes` | TEXT |  |
| `fact_status` | TEXT | NOT NULL default `'REPORTED'` |
| `source_id` | TEXT | → `sources.id` |
| `confidence` | TEXT |  |
| `as_of_date` | TEXT |  |

## `v_applicant_vs_proponent` (view, 13 rows)

_No description recorded._

<details><summary>definition</summary>

```sql
CREATE VIEW v_applicant_vs_proponent AS
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
ORDER BY cr.proponent_known, cr.project_slug
```

</details>

## `v_case_officer_load` (view, 17 rows)

_No description recorded._

<details><summary>definition</summary>

```sql
CREATE VIEW v_case_officer_load AS
SELECT officer_name,
       officer_role,
       COUNT(*)                        AS cases,
       MIN(decision_date)              AS earliest_decision,
       MAX(decision_date)              AS latest_decision,
       GROUP_CONCAT(DISTINCT delegation_date) AS delegations_used
FROM case_handling
WHERE officer_name IS NOT NULL
GROUP BY officer_name, officer_role
ORDER BY cases DESC
```

</details>

## `v_community_friction` (view, 24 rows)

Community events joined to site and group, newest first.

<details><summary>definition</summary>

```sql
CREATE VIEW v_community_friction AS
SELECT ce.event_date, ce.state, ce.locality, ce.event_type, ce.actor, ce.summary,
       ce.severity, s.name AS site, g.name AS community_group, ce.outcome,
       ce.fact_status
FROM community_events ce
LEFT JOIN sites s          ON s.id = ce.site_id
LEFT JOIN community_groups g ON g.id = ce.group_id
ORDER BY ce.event_date DESC
```

</details>

## `v_consent_drift` (view, 17 rows)

_No description recorded._

<details><summary>definition</summary>

```sql
CREATE VIEW v_consent_drift AS
SELECT m.parent_case, s.name AS site, m.lga, m.mod_case, m.title, m.change_type,
       m.decision, m.determination_date, m.materiality, m.what_changed, m.fact_status
FROM modifications m
LEFT JOIN sites s ON s.id = m.site_id
ORDER BY m.determination_date DESC
```

</details>

## `v_consultant_influence` (view, 10 rows)

_No description recorded._

<details><summary>definition</summary>

```sql
CREATE VIEW v_consultant_influence AS
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
ORDER BY cp.au_public_sector_exposure_aud DESC
```

</details>

## `v_consultant_public_money` (view, 29 rows)

_No description recorded._

<details><summary>definition</summary>

```sql
CREATE VIEW v_consultant_public_money AS
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
ORDER BY c.value_aud DESC
```

</details>

## `v_consultant_spend_totals` (view, 10 rows)

_No description recorded._

<details><summary>definition</summary>

```sql
CREATE VIEW v_consultant_spend_totals AS
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
ORDER BY distinct_value_aud DESC
```

</details>

## `v_contract_reconciliation` (view, 3 rows)

_No description recorded._

<details><summary>definition</summary>

```sql
CREATE VIEW v_contract_reconciliation AS
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
WHERE e.id IN (SELECT DISTINCT supplier_entity_id FROM gov_contracts)
```

</details>

## `v_foreign_control` (view, 45 rows)

Operators and their current holders, with domicile and FIRB flag.

<details><summary>definition</summary>

```sql
CREATE VIEW v_foreign_control AS
SELECT e.id, e.name, e.entity_type, e.domicile, e.hq_country,
       o.holder_id, h.name AS holder, h.domicile AS holder_domicile,
       o.stake_pct, o.instrument, o.effective_from, o.firb_reviewed, o.firb_outcome
FROM entities e
LEFT JOIN ownership o ON o.target_id = e.id AND o.effective_to IS NULL
LEFT JOIN entities h  ON h.id = o.holder_id
WHERE e.entity_type IN ('colocation_operator','developer','hyperscaler','ai_lab','telecom')
```

</details>

## `v_incentive_register` (view, 9 rows)

Every recorded incentive, subsidy or fast-track benefit with its conditions.

<details><summary>definition</summary>

```sql
CREATE VIEW v_incentive_register AS
SELECT i.jurisdiction, i.granting_body, e.name AS recipient, s.name AS site,
       i.incentive_type, i.instrument, i.amount_aud, i.conditions,
       i.conditionality_score, i.domestic_compute_allocation, i.disclosed,
       i.fact_status, i.source_id
FROM incentives i
LEFT JOIN entities e ON e.id = i.recipient_id
LEFT JOIN sites s    ON s.id = i.site_id
ORDER BY i.jurisdiction, i.incentive_type
```

</details>

## `v_influence` (view, 15 rows)

_No description recorded._

<details><summary>definition</summary>

```sql
CREATE VIEW v_influence AS
SELECT e.name AS actor, l.person, l.channel, l.recipient, l.event_date, l.instrument,
       l.position, l.outcome, l.disclosed, l.fact_status, l.confidence, s.url AS source_url
FROM lobbying l
JOIN entities e ON e.id = l.actor_id
LEFT JOIN sources s ON s.id = l.source_id
ORDER BY l.event_date DESC
```

</details>

## `v_pipeline_by_state` (view, 21 rows)

Sites, capacity and capex by state / market / status.

<details><summary>definition</summary>

```sql
CREATE VIEW v_pipeline_by_state AS
SELECT s.state,
       s.market,
       s.status,
       COUNT(*)                                   AS n_sites,
       ROUND(SUM(COALESCE(s.max_capacity_mw, s.total_capacity_mw, s.it_capacity_mw,0)),1) AS mw_sum,
       ROUND(SUM(COALESCE(s.capital_cost_aud,0))/1e9,2) AS capex_aud_bn
FROM sites s
GROUP BY s.state, s.market, s.status
ORDER BY s.state, mw_sum DESC
```

</details>

## `v_renewable_audit` (view, 11 rows)

Claims joined to claimant and site, ordered by verification status.

<details><summary>definition</summary>

```sql
CREATE VIEW v_renewable_audit AS
SELECT c.claimant_id, e.name AS claimant, s.name AS site,
       c.claim_date, c.claim_type, c.claim_scope, c.target_year,
       c.instrument_relied_on, c.lgc_surrender_evidence,
       c.verification_status, c.verification_note, c.claim_text
FROM renewable_claims c
LEFT JOIN entities e ON e.id = c.claimant_id
LEFT JOIN sites s    ON s.id = c.site_id
ORDER BY c.verification_status, c.claim_date DESC
```

</details>

## `v_site_dossier` (view, 93 rows)

Publication-ready site summary with primary source and counts of applications, community events, regulatory events and applicable instruments.

<details><summary>definition</summary>

```sql
CREATE VIEW v_site_dossier AS
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
LEFT JOIN sources src ON src.id = s.source_id
```

</details>

## `v_site_full` (view, 93 rows)

One row per site with operator, owner, tenant, power profile and water profile joined.

<details><summary>definition</summary>

```sql
CREATE VIEW v_site_full AS
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
LEFT JOIN water_profile w ON w.site_id = s.id
```

</details>

## `v_verification_ledger` (view, 42 rows)

Row counts by table / fact_status / confidence. The health check.

<details><summary>definition</summary>

```sql
CREATE VIEW v_verification_ledger AS
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
UNION ALL SELECT 'metrics', fact_status, confidence, COUNT(*) FROM metrics GROUP BY 1,2,3
```

</details>

---

## Controlled vocabularies

- **fact_status**: `VERIFIED` · `REPORTED` · `CLAIMED` · `GAP`
- **confidence**: `high` · `medium` · `low`
- **sites.status**: `operational` · `under_construction` · `approved` · `lodged` · `pre_lodgement` · `refused` · `withdrawn` · `cancelled` · `rumoured`
- **sites.market**: `NEM` · `WEM` · `NT` · `Multi`
- **power_profile.connection_type**: `transmission` · `distribution` · `behind_the_meter_gas` · `behind_the_meter_diesel` · `islanded` · `hybrid` · `tbd`
- **water_profile.cooling_technology**: `air_cooled` · `closed_loop_water` · `adiabatic` · `evaporative` · `direct_to_chip_liquid` · `immersion` · `hybrid` · `tbd`
- **water_profile.water_source**: `potable_mains` · `recycled_water` · `closed_loop_no_makeup` · `bore_groundwater` · `rainwater` · `sea_water` · `mixed` · `tbd`
- **renewable_claims.verification_status**: `VERIFIED` · `PARTIALLY_VERIFIED` · `UNVERIFIED` · `CONTRADICTED` · `NOT_ASSESSED`
- **energy_agreements.additionality**: `new_build_pre_fid` · `new_build_post_fid` · `expansion_existing` · `existing_asset` · `unknown`
- **incentives.incentive_type**: `payroll_tax_exemption` · `land_tax_exemption` · `stamp_duty_relief` · `leasehold_land_concession` · `grant` · `tax_increment` · `rate_concession` · `fast_track_approval` · `co_funded_infrastructure` · `equity_stake` · `guarantee` · `offtake_commitment` · `other` · `alleged` · `none_found`
- **metrics.basis**: `actual` · `forecast_low` · `forecast_central` · `forecast_high` · `pipeline` · `signed` · `enquiry` · `estimate`
- **engineering_claims.claim_status**: `SOUND` · `PARTLY_SOUND` · `UNSOUND_AS_STATED` · `ALREADY_MANDATED` · `FACTUALLY_WRONG_PREMISE`
- **sources.credibility**: `A` · `B` · `C` · `D`

---

## Provenance semantics

| `fact_status` | Meaning | Publishable as fact? |
|---|---|---|
| `VERIFIED` | Primary document read directly | Yes |
| `REPORTED` | Credible secondary reporting of a primary fact | Yes, with attribution |
| `CLAIMED` | Proponent or industry assertion, unconfirmed | No — attribute as a claim |
| `GAP` | Known unknown, tracked in `research_gaps` | No |

| Source credibility | Definition |
|---|---|
| A | Primary government, regulator, legislation, planning portal, first-party company document, major broadcaster or wire |
| B | Established trade press, law firm analysis, think tank, market research |
| C | Single-source, social, community or aggregator |
| D | Unusable — never admitted |

