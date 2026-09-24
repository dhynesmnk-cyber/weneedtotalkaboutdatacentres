-- Re-loading over a database that has lived.
--
-- load.test.sql checks a fresh load. Production is never fresh: a person has
-- confirmed links, flagged entities as major and given gaps sourced reasons,
-- and an earlier load left gaps for fields the research has since filled.
-- scripts/test-load.sh sets that state up with reload.setup.sql, applies the
-- load again, then runs this.

\set ON_ERROR_STOP on
\o /dev/null

-- The stale gap: a derived "no coordinates" gap on a site that now has them.
select public.assert(
  (select count(*) from facts.sites s
     join facts.data_gaps g
       on g.record_type = 'sites' and g.record_id = s.id and g.field_name in ('lat', 'lng')
    where s.lat is not null) = 0,
  're-load removes derived gaps whose field the research has filled');

-- Human decisions survive.
select public.assert(
  (select state from facts.links where confirmed_by = 'reload test') = 'confirmed',
  're-load keeps a link a human confirmed');

select public.assert(
  (select major_flag from facts.entities
    where id = (select record_id from reload_marks where what = 'entity')),
  're-load keeps a major flag a human set');

select public.assert(
  (select reason = 'not_disclosed' and source_id is not null from facts.data_gaps
    where record_type = 'sites'
      and record_id = (select record_id from reload_marks where what = 'gap')
      and field_name = 'cooling_type'),
  're-load keeps a gap reason a human strengthened, with its source');

\o
\echo 'All re-load assertions passed.'
