-- Behavioural assertions over a loaded database.
--
-- supabase/tests/rls.test.sql proves the policies work against seeded fixtures.
-- This file proves the *real research* survives the trip intact, and that
-- nothing was invented on the way. It runs after scripts/test-load.sh has
-- applied the load artefact twice.
--
-- Everything below that concerns what a reader can see is asserted as the anon
-- role, because that is the only thing the public API can be.

\set ON_ERROR_STOP on
\o /dev/null

create or replace function public.assert(condition boolean, description text)
returns void language plpgsql as $$
begin
  if condition is not true then
    raise exception 'ASSERTION FAILED: %', description;
  end if;
end;
$$;

-- ---------------------------------------------------------------------------
-- The research arrived.
-- ---------------------------------------------------------------------------

-- 2026-11-15: the author approved two changes to the site table. RG-084 merged
-- SITE_STOCKLAND_MP into SITE_MACQUARIE_PARK_DC - one consent (SSD-10467) recorded
-- twice - taking one row away. The HCF register follow-up added the eight certified
-- facilities that had no record at all (ADC Mitchell and Fyshwick, NEXTDC B1 and B2,
-- Fujitsu Western Sydney and Homebush Bay, Polaris, Macquarie IC3 East), each placed
-- by an operator's own archived page: +8. 93 - 1 + 8 = 100.
-- 2026-11-17: RG-101's third pass, on DigiCo's own ASX documents (supplied by the
-- author), adds DigiCo ADL1 (SA) and BNE2 (QLD) from its Annual Report's portfolio
-- list: +2. Its third facility, SYD1, is the existing SITE_DIGICO_SYD1, matched not
-- added. 100 + 2 = 102.
-- 2026-11-18: the author's decisions on research batch 7. AirTrunk SYD2 is the
-- facility the Lane Cove West consent approved (RG-098), so the seed row
-- SITE_AIRTRUNK_SYD2 is retired into SITE_LANE_COVE_WEST: -1. AirTrunk MEL2 (VIC,
-- RG-071) and Firmus Wesley Vale (TAS, RG-027) are added from the operators' own
-- pages: +2. 102 - 1 + 2 = 103.
-- 2026-11-18: the author's second round on batch 8 adds two Northern Territory proposals
-- named in the NT Government's release of 22 July 2026 (Beetaloo Digital at Weddell;
-- Energy North's Project Ares at Murranji station), unmapped and with no capacity: 105.
select public.assert(
  (select count(*) from facts.sites where pipeline_id is not null) = 105,
  '105 sites loaded');

-- Pinned counts track the reviewed contents of the committed pipeline, so a
-- curated pack that adds rows raises them by an argued amount - the change is
-- in the diff that raises it, not silent. 2026-09-22: the Palantir-NVIDIA
-- research thread (data/packs/palantir_nvidia_thread.json) adds 13 entities
-- and 36 sources. Rebased 2026-09-30 onto main's 157 sources, giving 193.
-- Sites stay 93 because the thread adds no site rows (its infrastructure
-- claims are CLAIMED-grade metrics pending RG-091). The assertions remain
-- falsifiable: a loader that dropped any thread row fails them.
-- 2026-10-10: batch S3 (data/packs/hcf_register.json) adds one source, the
-- Commonwealth HCF register, giving 194. Batch S2 (data/packs/ssd_documents.json)
-- adds 41, one planning document per NSW SSD project it reads, giving 235.
-- Batch S4 (data/packs/operator_sources.json) adds 11 operator web pages, giving 246.
-- 2026-10-14: v2.2.2 adds two. RG-099 reads STACK SYD01's EIS (SRC_SSD82211208_EIS,
-- in data/packs/ssd_documents.json) and RG-100 the Mandala report CertifiedStrategic.com
-- named for two figures it does not state (SRC_MANDALA_DCEI_2025, in
-- data/packs/certstrat_review.json), giving 248.
-- 2026-10-22: research batch 1 (data/packs/who_applies.json) adds three sources,
-- ASIC's company register extract and the title searches filed with the Davis
-- Road and Mamre Road applications, giving 251; and one entity, Amazon
-- Australia Company Pty Ltd, the registered owner of the Davis Road site,
-- giving 139.
-- 2026-10-22: research batch 2 (data/packs/super_and_openai.json) adds ten
-- sources, three super funds' holdings files, six NEXTDC documents and the ASX's
-- list of NEXTDC's 2025 announcements, giving 261 (it re-declares SRC_NEXTDC_S7,
-- which adds none); and one entity, La Caisse, giving 140.
-- 2026-10-22: research batch 3 (data/packs/public_and_room.json) adds seven sources:
-- Penrith's planning agreement with Microsoft (its explanatory note and draft),
-- Oxford Economics' phantom-demand briefing, the BCA's member directory, the
-- 2025-26 Budget release on the Investment Delivery Authority, the FIRB quarterly
-- report and the NSW ministers' diary index, giving 268 (it re-declares
-- SRC_PENRITH_VPA and SRC_NSWGUIDE26, which add none). No entity is added.
-- 2026-10-22: research batch 4 (data/packs/whose_data.json) adds ten sources: the
-- AusTender feed (the Open Contracting Partnership's copy), the FOI Act, WA
-- Police's facial recognition privacy assessment, three news reports and Coles'
-- notice of meeting on Coles and Palantir, Dexus's release on the Western Downs
-- campus, a second keynote transcript and Palantir's WesTrac release, giving
-- 278; and two entities, AUSTRAC (a Palantir buyer since 2016) and WesTrac (a
-- Palantir customer), giving 142.
-- 2026-10-30: research batch 5 (data/packs/who_heard.json) adds six sources: the
-- Roberts Road and Talavera Road donation disclosures, the Commission's statement
-- of reasons and the Department's referral letter for Talavera Road, the planning
-- portal's page on who decides, and the councils' submissions, giving 284. No
-- entity is added.
-- 2026-11-15: the HCF register follow-up adds three entities - Australian Data
-- Centres, Polaris Data Centre and the Springfield City Group that owns it - giving
-- 145. The register's certified provider for Polaris (Springfield Real Estate Sales
-- Pty Ltd) is NOT asserted as an entity: how it relates to the owner is RG-103.
-- 2026-11-17: RG-101's third pass adds DigiCo Infrastructure REIT, operator of SYD1,
-- ADL1 and BNE2: 145 + 1 = 146.
-- 2026-11-18: research batch 7 adds Westpac, a Palantir customer now reported by two
-- outlets quoting the bank, the threshold RG-088 set: 146 + 1 = 147.
select public.assert(
  (select count(*) from facts.entities where pipeline_id is not null) = 147,
  '147 entities loaded');

-- 2026-11-17: people by role (R2.0, CLAUDE.md). The entities that are individuals
-- load under their public role, in square brackets; the loader refuses to write a
-- load that still names anyone it lists (lib/ingestion/people.ts).
select public.assert(
  (select count(*) from facts.entities
    where pipeline_id in ('ENT_KHUDA', 'ENT_BCA_CE', 'ENT_BCA_PRES', 'ENT_WENDY_BLACK', 'ENT_MAMRE_OWNER')
      and name !~ '\[[^]]+\]') = 0,
  'entities that are individuals are published under their role');

-- 2026-11-15: the HCF register follow-up archives eight operator pages (ADC's home
-- and locations pages, Polaris, Fujitsu's 2020 footprint release, NEXTDC B1 and B2,
-- Macquarie IC3 East and IC3 Super West), giving 292. It re-declares SRC_HCF_REGISTER
-- and SRC_NXT_FY26_PRESENTATION verbatim from the packs that register them, which add
-- none. The RG-084 merge adds no source: it cites the consent and assessment already
-- archived.
-- 2026-11-15: RG-099 is resolved on Road 1's own EIS, which had no source row of its
-- own (the ssd_documents batch took no figure from it). curate_rg061_rg099.py registers
-- SRC_SSD80814238_EIS from the archived manifest: 292 + 1 = 293.
-- 2026-11-17: RG-101's third pass registers DigiCo's release of 15 October 2026, its
-- AGM 2026 presentation and its Annual Report 2026, each with a manifest and verbatim
-- excerpts (the PDFs are not committed): 293 + 3 = 296.
-- 2026-11-18: research batch 7 registers the Information Age and Cyber Daily reports on
-- Westpac (5 November 2026), Cyber Daily's earlier report (16 October), AirTrunk's MEL2
-- page and NVIDIA's Australian release (9 September 2026): 296 + 5 = 301. Its second
-- pass registers the four modification assessment reports and Roberts Road's Mod 4
-- report (RG-045), and Firmus's Wesley Vale page (RG-027): 301 + 6 = 307.
-- 2026-11-18: research batch 8 registers the two acoustic peer reviews and the three
-- greenhouse gas reviews it opened (RG-075), and one bulk record for the 35 acoustic and
-- air quality reports it read for their authors (RG-073): 307 + 6 = 313.
-- 2026-11-18: batch 8's second pass registers the eleven remaining modification reports
-- (RG-034), Transgrid's data centre page and its two system strength documents (RG-018,
-- RG-019, RG-043), Mandala's October 2024 report (RG-100) and Melbourne Water's annual
-- report (RG-080): 313 + 16 = 329.
-- 2026-11-18: two of those were duplicates of earlier rows with the same URL (Transgrid's
-- data centre page, SRC_TRANSGRIDCAP; NVIDIA's release, SRC_NVIDIA_AU_2GW, duplicated in
-- batch 7), and now cite the originals; the author's downloads add the 2026-27 Budget Paper
-- No. 1, AEMO's registration list, the NT Government's Beetaloo release, the NSW Electoral
-- Commission's stakeholder register and the AEC's annual returns: 329 - 2 + 5 = 332.
-- 2026-11-18: the author's transcription of Amazon Web Services Australia's NSW major
-- political donor disclosures (RG-069): 332 + 1 = 333.
select public.assert(
  (select count(*) from facts.sources where pipeline_id is not null) = 333,
  '333 sources loaded');

-- The research agenda. 2026-10-09: the pipeline holds 89 questions; 79 load.
-- The other ten (RG-001, 004, 005, 006, 008, 014, 016, 017, 018, 019, all from
-- the seed) carry no source, so the loader rejects them rather than publish a
-- question uncited. Sourcing one raises this by one, in the same diff.
-- 2026-10-14: merged with batches S3, S2 and S4, which open RG-096 (cites the
-- HCF register), RG-097 (the NSW portal register) and RG-098 (AirTrunk's SYD2
-- page). The pipeline holds 92 questions; the same ten are rejected; 82 load.
-- 2026-10-14: v2.2.1 opens RG-099 (cites the NSW portal register) and RG-100
-- (cites SRC_CERTSTRAT): 94 questions, the same ten rejected, 84 load.
-- 2026-10-22: research batch 1 cites RG-005 (the Mamre Road title search and
-- ASIC's register), so nine are rejected and 85 load.
-- 2026-10-22: research batch 2 cites RG-004 (three super funds' holdings files
-- and NEXTDC's annual report) and RG-014 (NEXTDC's OpenAI announcement and later
-- reports), so seven are rejected and 87 load.
-- 2026-10-22: research batch 3 cites RG-006 (the FIRB quarterly report), so six
-- are rejected and 88 load. Research batches 4 and 5 cite none of the six, so 88
-- still load (batch 5 adds notes to RG-016, which stays uncited).
-- 2026-11-15: RG-084 is resolved (not removed), and four questions open, all cited:
-- RG-101 (the five register facilities still unplaced, cites the register), RG-102
-- (the Macquarie Park end-user and start-date claims the merge refused to adopt,
-- cites the portal record), RG-103 (addresses and capacities for the eight new rows,
-- cites the register) and RG-104 (IC3 Super West recorded operational while its
-- operator says under construction, cites that page). 98 questions, the same six
-- rejected, 92 load.
-- 2026-11-15: RG-061 is answered for the renewable obligation and stays in_progress;
-- RG-099 is resolved; RG-017 gains its first citation (NEXTDC S7's scoping report, which
-- states the water demand and the Sydney Water engagement, so the question is publishable
-- before any FOI is lodged); RG-105 opens on the address and lot Road 1 shares with
-- SSD-63235720, cited to Road 1's EIS and the neighbour's consent. 99 questions, five
-- rejected (RG-001, 008, 016, 018, 019), 94 load.
-- 2026-11-17: RG-106 opens on DigiCo's four other Australian properties, cited to its
-- Annual Report. 100 questions, the same five rejected, 95 load.
-- 2026-11-18: research batch 8 gives RG-008 its first citations (the EPA's advice on
-- licences, as the Department's assessment reports record it), so four are rejected
-- (RG-001, 016, 018, 019) and 96 load.
-- 2026-11-18: the second pass cites RG-018 and RG-019 (Transgrid's own pages), so two are
-- rejected (RG-001, 016) and 98 load.
select public.assert(
  (select count(*) from facts.research_agenda where pipeline_id is not null) = 98,
  '98 research questions loaded');

select public.assert(
  (select count(*) from facts.research_agenda q
    where not exists (
      select 1 from facts.citations c
       where c.record_type = 'research_agenda' and c.record_id = q.id)) = 0,
  'every research question cites a source');

select public.assert(
  (select count(*) from facts.research_agenda
    where pipeline_id in ('RG-001', 'RG-016')) = 0,
  'no uncited question was published');

-- 2026-11-18: RG-008 leaves this list. Research batch 8 cites it to the EPA's advice on
-- licences as the Department's assessment reports record it, so it is published.
-- 2026-11-18: RG-018 and RG-019 leave it too, each cited to Transgrid's own pages.

-- 2026-11-15: RG-017 leaves this list. It is now cited to NEXTDC S7's scoping report,
-- which states the water demand and the Sydney Water engagement, so the question is
-- publishable while the four water requests remain drafted and unlodged.

-- A question keeps the label the research cites it by.
select public.assert(
  (select count(*) from facts.research_agenda where pipeline_id !~ '^RG-[0-9]{3}$') = 0,
  'every research question is labelled RG-nnn');

-- ---------------------------------------------------------------------------
-- Nothing was invented.
-- ---------------------------------------------------------------------------

-- The single most important assertion here. it_capacity_mw is a design rating;
-- filling live capacity from it would put a figure in front of a reader that
-- no source ever published.
select public.assert(
  (select count(*) from facts.sites
    where pipeline_id is not null and live_capacity_mw is not null) = 0,
  'no loaded site has a fabricated live capacity');

-- Every gap the loader derives says only "not yet researched", which is all a
-- null in the pipeline actually asserts. A stronger reason would be a claim
-- about the world, and claims need a human and a source.
select public.assert(
  (select count(*) from facts.data_gaps g
    join facts.sites s on s.id = g.record_id
   where s.pipeline_id is not null
     and g.reason <> 'unknown') = 0,
  'every derived gap uses reason unknown and no stronger reason');

select public.assert(
  (select count(*) from facts.data_gaps g
    join facts.sites s on s.id = g.record_id
   where s.pipeline_id is not null and g.source_id is not null) = 0,
  'no derived gap claims a source it does not have');

-- Council names are loaded exactly as the sources state them. Picking between
-- 'Blacktown' and 'Blacktown City Council' is a human decision recorded in
-- facts.lga_aliases, not something a loader does quietly.
select public.assert(
  (select count(*) from facts.lga_aliases) = 0,
  'the loader wrote no council aliases');

-- ---------------------------------------------------------------------------
-- Nothing was published.
-- ---------------------------------------------------------------------------

select public.assert(
  (select count(*) from facts.links where state = 'confirmed') = 0,
  'every derived link is still a proposal');

select public.assert(
  (select count(*) from facts.entities where major_flag) = 0,
  'the loader flagged no entity as major');

select public.assert(
  (select count(*) from editorial.essays) = 0
  and (select count(*) from editorial.case_studies) = 0,
  'the loader touched no editorial record');

-- ---------------------------------------------------------------------------
-- The load is auditable.
-- ---------------------------------------------------------------------------

select public.assert(
  (select count(*) from facts.ingest_runs) = 2,
  'both load runs were recorded');

select public.assert(
  (select count(distinct source_digest) from facts.ingest_runs) = 1,
  'both runs read the same pipeline build');

-- ---------------------------------------------------------------------------
-- What the public actually sees.
-- ---------------------------------------------------------------------------

set role anon;

select public.assert(
  (select count(*) from facts.sites) = 105,
  'anon can read all 105 sites');

-- The invariant that makes the fact layer publishable at all.
select public.assert(
  (select count(*) from facts.sites s
    where not exists (
      select 1 from facts.citations c
       where c.record_type = 'sites' and c.record_id = s.id
    )) = 0,
  'every site anon can see carries at least one citation');

-- The research agenda is published, and each question's sources with it.
select public.assert(
  (select count(*) from facts.research_agenda) = 98,
  'anon can read all 98 research questions');

select public.assert(
  (select count(*) from facts.research_agenda q
    where not exists (
      select 1 from facts.citations c
       where c.record_type = 'research_agenda' and c.record_id = q.id
    )) = 0,
  'every research question anon can see carries at least one citation');

-- No site can render an UnexplainedBadge: every empty factual field on every
-- visible site has a gap record explaining it.
select public.assert(
  (select count(*) from facts.sites s
    where s.status is null
      and not exists (
        select 1 from facts.data_gaps g
         where g.record_type = 'sites' and g.record_id = s.id
           and g.field_name = 'status'
      )) = 0,
  'every null status is explained by a gap record');

select public.assert(
  (select count(*) from facts.sites s
    where s.lga is null
      and not exists (
        select 1 from facts.data_gaps g
         where g.record_type = 'sites' and g.record_id = s.id
           and g.field_name = 'lga'
      )) = 0,
  'every null council is explained by a gap record');

-- Coordinates. 46 NSW SSD sites carry the point the NSW Planning Portal
-- records for the project (data-pipeline/scripts/curate_site_coordinates.py).
-- Each must cite a primary planning-portal record, the rest must say why they
-- have none, and no site may both have coordinates and a gap claiming it has
-- none.
select public.assert(
  (select count(*) from facts.sites where lat is not null and lng is not null) = 46,
  '46 sites have coordinates');

select public.assert(
  (select count(*) from facts.sites s
    where s.lat is not null
      and not exists (
        select 1 from facts.citations c
          join facts.sources src on src.id = c.source_id
         where c.record_type = 'sites' and c.record_id = s.id
           and src.type = 'primary_planning_portal' and src.credibility = 'A'
      )) = 0,
  'every located site cites a primary planning-portal record');

select public.assert(
  (select count(*) from facts.sites s
    where s.lat is null
      and not exists (
        select 1 from facts.data_gaps g
         where g.record_type = 'sites' and g.record_id = s.id
           and g.field_name = 'lat'
      )) = 0,
  'every site without coordinates is explained by a gap record');

select public.assert(
  (select count(*) from facts.sites s
     join facts.data_gaps g
       on g.record_type = 'sites' and g.record_id = s.id and g.field_name in ('lat', 'lng')
    where s.lat is not null) = 0,
  'no located site also carries a gap saying it has no coordinates');

-- Derivation is not publication: proposed links have no public standing.
select public.assert(
  (select count(*) from facts.links) = 0,
  'anon sees no link, because every one is still a proposal');

-- The research grades its claims, and the grading survives to the reader. If
-- this ever returns zero, either the pipeline changed or the import dropped
-- the distinction between an assertion and a confirmed fact.
select public.assert(
  (select count(*) from facts.sites where fact_status = 'claimed') > 0,
  'claimed sites are visible and still marked as claimed');

select public.assert(
  (select count(*) from facts.sites where fact_status = 'verified') > 0,
  'verified sites are marked as verified');

reset role;

\o

\echo 'All load assertions passed.'
