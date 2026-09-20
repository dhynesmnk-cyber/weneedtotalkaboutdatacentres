-- Live Row Level Security and constraint tests.
--
-- These replace the static text assertions in tests/schema.test.ts as the real
-- evidence that the database behaves as docs/QUALITY.md requires. They run
-- against a real Postgres with the migrations applied, seed data as a superuser,
-- then read it back as the anon role to prove what the public API can and
-- cannot see.
--
-- Run with scripts/test-rls.sh, which creates the database, applies the
-- migrations and executes this file. Any failed assertion aborts with an error,
-- so a clean exit is a pass.

\set ON_ERROR_STOP on

create or replace function public.assert(condition boolean, message text)
returns void language plpgsql as $$
begin
  if condition is not true then
    raise exception 'ASSERTION FAILED: %', message;
  end if;
end;
$$;

-- Assertions signal by raising, so their result rows are noise.
\o /dev/null

-- Repeatable: start from empty every run.
truncate facts.citations, facts.data_gaps, facts.links, facts.events,
         facts.sites, facts.entities, facts.sources, facts.council_watchlist,
         editorial.case_studies, editorial.essays cascade;

-- ---------------------------------------------------------------------------
-- Seed, as a superuser. RLS does not apply here, which is the point: this is
-- what ingestion and editing look like.
-- ---------------------------------------------------------------------------

insert into facts.sources (id, type, title, url, retrieved_date, publisher)
values ('50000000-0000-0000-0000-000000000001', 'planning_document',
        'Test source', 'https://example.org/doc', date '2026-09-18', 'Example');

insert into facts.sites (id, name, operator, status, total_capacity_mw)
values ('10000000-0000-0000-0000-000000000001', 'Visible Site', 'Operator', 'proposed', 100);

insert into facts.entities (id, name, major_flag)
values ('20000000-0000-0000-0000-000000000001', 'Visible Entity', true);

insert into facts.events (id, category, date, title, site_id)
values ('30000000-0000-0000-0000-000000000001', 'planning', date '2026-01-01',
        'Visible Event', '10000000-0000-0000-0000-000000000001');

-- One proposed link and one confirmed link, on different endpoint pairs so the
-- unique index does not collapse them.
insert into facts.links (site_id, entity_id, state)
values ('10000000-0000-0000-0000-000000000001',
        '20000000-0000-0000-0000-000000000001', 'proposed');

insert into facts.links (site_id, event_id, state, confirmed_by, confirmed_at)
values ('10000000-0000-0000-0000-000000000001',
        '30000000-0000-0000-0000-000000000001', 'confirmed', 'a human', now());

insert into facts.citations (source_id, record_type, record_id, claim)
values ('50000000-0000-0000-0000-000000000001', 'sites',
        '10000000-0000-0000-0000-000000000001', 'operator');

insert into facts.data_gaps (record_type, record_id, field_name, reason)
values ('sites', '10000000-0000-0000-0000-000000000001', 'water_usage', 'not_disclosed');

insert into facts.council_watchlist (lga, state, approved_by, approved_at)
values ('Example Shire', 'NSW', 'a human', now());

-- Editorial: one approved and published, one unapproved draft, one approved but
-- dated in the future.
insert into editorial.essays (id, title, publish_date, approved_by, approved_at)
values ('40000000-0000-0000-0000-000000000001', 'Published Essay',
        current_date - 1, 'a human', now());

insert into editorial.essays (id, title, publish_date)
values ('40000000-0000-0000-0000-000000000002', 'Draft Essay', current_date - 1);

insert into editorial.essays (id, title, publish_date, approved_by, approved_at)
values ('40000000-0000-0000-0000-000000000003', 'Future Essay',
        current_date + 7, 'a human', now());

insert into editorial.case_studies
  (id, title, publish_date, data_as_of_date, approved_by, approved_at)
values ('60000000-0000-0000-0000-000000000001', 'Published Case Study',
        current_date - 1, current_date - 30, 'a human', now());

insert into editorial.case_studies (id, title, publish_date, data_as_of_date)
values ('60000000-0000-0000-0000-000000000002', 'Draft Case Study',
        current_date - 1, current_date - 30);

-- ---------------------------------------------------------------------------
-- Read back as anon. This is what the public API sees.
-- ---------------------------------------------------------------------------

set role anon;

-- The fact layer is openly browsable. That is the point of the project.
select public.assert((select count(*) from facts.sites) = 1, 'anon can read sites');
select public.assert((select count(*) from facts.entities) = 1, 'anon can read entities');
select public.assert((select count(*) from facts.events) = 1, 'anon can read events');
select public.assert((select count(*) from facts.sources) = 1, 'anon can read sources');
select public.assert((select count(*) from facts.citations) = 1, 'anon can read citations');
select public.assert((select count(*) from facts.data_gaps) = 1, 'anon can read gaps');
select public.assert((select count(*) from facts.council_watchlist) = 1,
                     'anon can read the approved council list');

-- Derivation is not publication: a proposed link has no public standing.
select public.assert((select count(*) from facts.links) = 1,
                     'anon sees exactly one link');
select public.assert((select count(*) from facts.links where state = 'proposed') = 0,
                     'anon cannot see proposed links');
select public.assert((select count(*) from facts.links where state = 'confirmed') = 1,
                     'anon can see confirmed links');

-- No agent publishes content: approval gates the editorial layer.
select public.assert((select count(*) from editorial.essays) = 1,
                     'anon sees only the approved, published essay');
select public.assert(
  (select title from editorial.essays) = 'Published Essay',
  'the essay anon sees is the approved one');
select public.assert((select count(*) from editorial.case_studies) = 1,
                     'anon sees only the approved case study');
select public.assert(
  (select title from editorial.case_studies) = 'Published Case Study',
  'the case study anon sees is the approved one');

reset role;

-- ---------------------------------------------------------------------------
-- anon cannot write. Every statement below must be refused.
-- ---------------------------------------------------------------------------

do $$
declare
  refused int := 0;
  statements text[] := array[
    $s$insert into facts.sites (name) values ('Injected')$s$,
    $s$update facts.sites set name = 'Renamed'$s$,
    $s$delete from facts.sites$s$,
    $s$insert into editorial.essays (title) values ('Self published')$s$,
    $s$update editorial.essays set approved_by = 'an agent', approved_at = now()$s$,
    $s$update facts.links set state = 'confirmed'$s$,
    $s$insert into facts.council_watchlist (lga, state, approved_by, approved_at)
       values ('Snuck In', 'NSW', 'an agent', now())$s$
  ];
  stmt text;
begin
  foreach stmt in array statements loop
    begin
      set local role anon;
      execute stmt;
      reset role;
      raise exception 'ASSERTION FAILED: anon was allowed to run: %', stmt;
    exception
      when insufficient_privilege then
        refused := refused + 1;
      when others then
        -- A policy violation is also a refusal; anything else is a real failure.
        if sqlstate = '42501' then
          refused := refused + 1;
        else
          raise;
        end if;
    end;
  end loop;

  reset role;
  perform public.assert(refused = array_length(statements, 1),
                        format('all %s write attempts refused, got %s',
                               array_length(statements, 1), refused));
end;
$$;

-- ---------------------------------------------------------------------------
-- Constraints from docs/QUALITY.md. Each must reject the bad value.
-- ---------------------------------------------------------------------------

do $$
declare
  rejected int := 0;
  statements text[] := array[
    -- Capacity must be positive.
    $s$insert into facts.sites (name, total_capacity_mw) values ('Bad', -5)$s$,
    $s$insert into facts.sites (name, total_capacity_mw) values ('Bad', 0)$s$,
    -- Live capacity cannot exceed total.
    $s$insert into facts.sites (name, total_capacity_mw, live_capacity_mw)
       values ('Bad', 100, 150)$s$,
    -- Half a coordinate pair is not a point.
    $s$insert into facts.sites (name, lat) values ('Bad', -33.8)$s$,
    $s$insert into facts.sites (name, lng) values ('Bad', 151.2)$s$,
    -- Out of range coordinates.
    $s$insert into facts.sites (name, lat, lng) values ('Bad', -200, 151.2)$s$,
    -- A link needs at least two endpoints.
    $s$insert into facts.links (site_id) values ('10000000-0000-0000-0000-000000000001')$s$,
    -- A confirmed link must name its confirmer.
    $s$insert into facts.links (site_id, entity_id, state)
       values ('10000000-0000-0000-0000-000000000001',
               '20000000-0000-0000-0000-000000000001', 'confirmed')$s$,
    -- An approved essay must name its approver.
    $s$insert into editorial.essays (title, publish_date, approved_at)
       values ('Bad', current_date, now())$s$,
    -- An approved essay must carry a publish date.
    $s$insert into editorial.essays (title, approved_by, approved_at)
       values ('Bad', 'a human', now())$s$,
    -- A council cannot be added without a named approver.
    $s$insert into facts.council_watchlist (lga, state) values ('Bad', 'NSW')$s$,
    -- Only the eight states and territories.
    $s$insert into facts.council_watchlist (lga, state, approved_by, approved_at)
       values ('Bad', 'XX', 'a human', now())$s$,
    -- One gap per field per record.
    $s$insert into facts.data_gaps (record_type, record_id, field_name, reason)
       values ('sites', '10000000-0000-0000-0000-000000000001',
               'water_usage', 'unknown')$s$
  ];
  stmt text;
begin
  foreach stmt in array statements loop
    begin
      execute stmt;
      raise exception 'ASSERTION FAILED: database accepted a bad row: %', stmt;
    exception
      when check_violation or not_null_violation or unique_violation then
        rejected := rejected + 1;
    end;
  end loop;

  perform public.assert(rejected = array_length(statements, 1),
                        format('all %s bad rows rejected, got %s',
                               array_length(statements, 1), rejected));
end;
$$;

-- ---------------------------------------------------------------------------
-- Enum domains match what lib/types.ts declares.
-- ---------------------------------------------------------------------------

select public.assert(
  (select array_agg(enumlabel::text order by enumsortorder)
     from pg_enum e join pg_type t on t.oid = e.enumtypid
     where t.typname = 'site_status')
  = array['rumoured','pre_lodgement','proposed','lodged','approved',
          'under_construction','operating','stalled','refused','withdrawn',
          'cancelled'],
  'site_status domain matches');

-- Provenance domains added in 0006. fact_status is ordered weakest to
-- strongest, so a comparison reads the way a reader would expect.
select public.assert(
  (select array_agg(enumlabel::text order by enumsortorder)
     from pg_enum e join pg_type t on t.oid = e.enumtypid
     where t.typname = 'fact_status')
  = array['gap','claimed','reported','verified'],
  'fact_status domain matches');

select public.assert(
  (select array_agg(enumlabel::text order by enumsortorder)
     from pg_enum e join pg_type t on t.oid = e.enumtypid
     where t.typname = 'confidence_level')
  = array['low','medium','high'],
  'confidence_level domain matches');

select public.assert(
  (select array_agg(enumlabel::text order by enumsortorder)
     from pg_enum e join pg_type t on t.oid = e.enumtypid
     where t.typname = 'source_credibility')
  = array['A','B','C','D'],
  'source_credibility domain matches');

select public.assert(
  (select array_agg(enumlabel::text order by enumsortorder)
     from pg_enum e join pg_type t on t.oid = e.enumtypid
     where t.typname = 'gap_reason')
  = array['unknown','not_disclosed','not_applicable','withheld'],
  'gap_reason domain matches');

-- Every table has RLS on. A table added later without it would fail here.
select public.assert(
  (select count(*) from pg_tables
    where schemaname in ('facts','editorial') and not rowsecurity) = 0,
  'every table in facts and editorial has RLS enabled');

\o

\echo 'All RLS and constraint assertions passed.'
