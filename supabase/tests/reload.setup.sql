-- State for reload.test.sql: what production looks like between loads.
-- Runs against a loaded test database only.

create table public.reload_marks (what text primary key, record_id uuid not null);

-- What the pre-coordinates load left behind on a site that is now located.
insert into facts.data_gaps (record_type, record_id, field_name, reason, source_id)
select 'sites', id, 'lat', 'unknown', null
  from facts.sites where lat is not null order by id limit 1
on conflict (record_type, record_id, field_name) do nothing;

-- A person confirms a proposed link.
update facts.links
   set state = 'confirmed', confirmed_by = 'reload test', confirmed_at = now()
 where id = (select id from facts.links where state = 'proposed' order by id limit 1);

-- A person flags an entity as major.
with e as (select id from facts.entities where pipeline_id is not null order by id limit 1)
insert into public.reload_marks select 'entity', id from e;
update facts.entities set major_flag = true
 where id = (select record_id from public.reload_marks where what = 'entity');

-- A person strengthens a derived gap with a source.
with g as (
  select record_id from facts.data_gaps
   where record_type = 'sites' and field_name = 'cooling_type' and reason = 'unknown'
   order by record_id limit 1)
insert into public.reload_marks select 'gap', record_id from g;
update facts.data_gaps
   set reason = 'not_disclosed',
       source_id = (select id from facts.sources order by id limit 1)
 where record_type = 'sites' and field_name = 'cooling_type'
   and record_id = (select record_id from public.reload_marks where what = 'gap');
