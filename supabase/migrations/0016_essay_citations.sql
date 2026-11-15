-- 0016: an essay's citations come from its text, and a draft's stay private.
--
-- 1. Citations follow the text. An essay cites a source by writing its
--    pipeline id in square brackets, [SRC_NSWGUIDE26], the same convention the
--    story cards use. Whenever the body changes, this trigger rebuilds the
--    essay's rows in facts.citations from those ids. There is no second list to
--    keep in step with the prose, so the source panel cannot drift from what
--    the essay actually cites.
--
--    An id the database does not hold is an error, and the save is refused.
--    CLAUDE.md: a record that cannot be cited is rejected, not imported
--    uncited. This is also why the pipeline must be reloaded before an essay
--    citing newer sources can be loaded.
--
-- 2. A draft's citations were readable by anyone. citations_public_read (0004)
--    served every row, so once drafts existed their citations, including any
--    claim text, would have been public while the drafts themselves were
--    hidden. Citations of an editorial record are now visible exactly when the
--    record is. The sub-select runs under the reader's own row level security,
--    so the rule cannot drift from the essays' and case studies' own policies.

create function editorial.sync_essay_citations()
returns trigger
language plpgsql
security definer
set search_path = ''
as $$
declare
  cited   text[];
  missing text[];
begin
  select coalesce(array_agg(distinct m[1]), '{}')
    into cited
    from regexp_matches(coalesce(new.body, ''), '\[(SRC_[A-Za-z0-9_]+)\]', 'g') as m;

  -- Aliased as c(src), not id: inside the sub-select an unqualified id would
  -- resolve to facts.sources.id.
  select coalesce(array_agg(c.src order by c.src), '{}')
    into missing
    from unnest(cited) as c(src)
   where not exists (select 1 from facts.sources s where s.pipeline_id = c.src);

  if cardinality(missing) > 0 then
    raise exception 'This text cites sources the database does not hold: %',
      array_to_string(missing, ', ')
      using errcode = 'foreign_key_violation',
            hint = 'Load the research pipeline first, or correct the source id.';
  end if;

  delete from facts.citations
   where record_type = 'essays' and record_id = new.id;

  insert into facts.citations (source_id, record_type, record_id)
  select s.id, 'essays', new.id
    from facts.sources s
   where s.pipeline_id = any (cited);

  return null;
end;
$$;

revoke all on function editorial.sync_essay_citations() from public, anon, authenticated, service_role;

create trigger essays_sync_citations
  after insert or update of body on editorial.essays
  for each row execute function editorial.sync_essay_citations();

-- An essay that is deleted takes its citations with it.
create function editorial.drop_essay_citations()
returns trigger
language plpgsql
security definer
set search_path = ''
as $$
begin
  delete from facts.citations where record_type = 'essays' and record_id = old.id;
  return null;
end;
$$;

revoke all on function editorial.drop_essay_citations() from public, anon, authenticated, service_role;

create trigger essays_drop_citations
  after delete on editorial.essays
  for each row execute function editorial.drop_essay_citations();

drop policy citations_public_read on facts.citations;

create policy citations_public_read on facts.citations
  for select to anon, authenticated
  using (
    case record_type
      when 'essays' then
        exists (select 1 from editorial.essays e where e.id = record_id)
      when 'case_studies' then
        exists (select 1 from editorial.case_studies c where c.id = record_id)
      else true
    end
  );
