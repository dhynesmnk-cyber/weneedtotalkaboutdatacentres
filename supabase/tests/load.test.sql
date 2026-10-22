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

select public.assert(
  (select count(*) from facts.sites where pipeline_id is not null) = 93,
  '93 sites loaded');

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
select public.assert(
  (select count(*) from facts.entities where pipeline_id is not null) = 139,
  '139 entities loaded');

select public.assert(
  (select count(*) from facts.sources where pipeline_id is not null) = 251,
  '251 sources loaded');

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
select public.assert(
  (select count(*) from facts.research_agenda where pipeline_id is not null) = 85,
  '85 research questions loaded');

select public.assert(
  (select count(*) from facts.research_agenda q
    where not exists (
      select 1 from facts.citations c
       where c.record_type = 'research_agenda' and c.record_id = q.id)) = 0,
  'every research question cites a source');

select public.assert(
  (select count(*) from facts.research_agenda
    where pipeline_id in ('RG-001', 'RG-004', 'RG-006', 'RG-008',
                          'RG-014', 'RG-016', 'RG-017', 'RG-018', 'RG-019')) = 0,
  'no uncited question was published');

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
  (select count(*) from facts.sites) = 93,
  'anon can read all 93 sites');

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
  (select count(*) from facts.research_agenda) = 85,
  'anon can read all 85 research questions');

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
