-- The essay drafts artefact (scripts/editorial/load-essays.ts), applied after
-- the pipeline load by scripts/test-load.sh. Run with -v essays=<artefact>.
--
-- What it must guarantee: drafts arrive unapproved and invisible, their
-- citations are derived from their text, a second load changes nothing, and a
-- piece the editor has edited is never overwritten.

\set ON_ERROR_STOP on

create or replace function public.assert_essays(condition boolean, message text)
returns void language plpgsql as $$
begin
  if condition is not true then
    raise exception 'ASSERTION FAILED: %', message;
  end if;
end;
$$;

\o /dev/null

select public.assert_essays(
  (select count(*) from editorial.essays where source_file like 'editorial/essays/%') > 0,
  'the drafts loaded');

select public.assert_essays(
  (select count(*) from editorial.essays
    where source_file like 'editorial/essays/%'
      and (approved_at is not null or approved_by is not null or publish_date is not null)) = 0,
  'no draft arrives approved, or with a publish date');

-- Citations are derived from the text: one row per distinct source cited.
select public.assert_essays(
  not exists (
    select 1
      from editorial.essays e
     where e.source_file like 'editorial/essays/%'
       and (select count(*) from facts.citations c
             where c.record_type = 'essays' and c.record_id = e.id)
           <> (select count(distinct m[1])
                 from regexp_matches(e.body, '\[(SRC_[A-Za-z0-9_]+)\]', 'g') as m)
  ),
  'every draft''s citations match the sources its text cites');

-- The public sees neither the drafts nor their citations.
set role anon;
select public.assert_essays(
  (select count(*) from editorial.essays where source_file like 'editorial/essays/%') = 0,
  'anon cannot see a draft');
select public.assert_essays(
  (select count(*) from facts.citations where record_type = 'essays') = 0,
  'anon cannot see a draft''s citations');
reset role;

-- The editor's version wins: an edited piece survives a reload untouched.
update editorial.essays
   set body = body || E'\nEdited by the editor.\n', edited_in_admin_at = now()
 where id = (select id from editorial.essays
              where source_file like 'editorial/essays/%' order by source_file limit 1);

\o
\i :essays
\o /dev/null

select public.assert_essays(
  (select count(*) from editorial.essays where body like '%Edited by the editor.%') = 1,
  'a reload leaves a piece the editor has edited alone');

\o

\echo 'All essay load assertions passed.'
