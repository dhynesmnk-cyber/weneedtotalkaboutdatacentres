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

select public.assert(
  (select count(*) from facts.entities where pipeline_id is not null) = 125,
  '125 entities loaded');

select public.assert(
  (select count(*) from facts.sources where pipeline_id is not null) = 117,
  '117 sources loaded');

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
