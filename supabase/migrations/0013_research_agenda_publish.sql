-- 0013: let the research agenda be loaded and cited.
--
-- facts.research_agenda (0009) exists to be published, and 0011 made it
-- publicly readable, but nothing loaded it. Two things stood in the way of
-- loading the pipeline's research_gaps into it honestly.
--
-- 1. A question published on this site is published content, and every
--    factual claim in published content must reference a source record
--    (CLAUDE.md). A question's why_it_matters and notes do make claims ("ISPT
--    lists the property as 'Summit'"), and citations could not point at the
--    agenda because citable_record did not name it. It does now. The loader
--    rejects a question it cannot cite rather than importing it uncited.
--
-- 2. The pipeline records five states for a question and this table accepted
--    three. Mapping blocked onto open, or wont_fix onto resolved, would be
--    reinterpreting rather than renaming (docs/PIPELINE_MAPPING.md), so the
--    check widens to the pipeline's vocabulary. A question closed as won't fix
--    may say when; one still open, in progress or blocked may not.
--
-- Nothing in this migration uses the new enum value, because a value added by
-- ALTER TYPE cannot be used until the adding transaction commits (see 0005).

alter type facts.citable_record add value if not exists 'research_agenda';

alter table facts.research_agenda
  drop constraint research_agenda_status_known,
  add constraint research_agenda_status_known
    check (status in ('open', 'in_progress', 'blocked', 'resolved', 'wont_fix'));

alter table facts.research_agenda
  drop constraint research_agenda_resolution_complete,
  add constraint research_agenda_resolution_complete
    check (
      (status = 'resolved' and resolved_date is not null)
      or status = 'wont_fix'
      or (status in ('open', 'in_progress', 'blocked') and resolved_date is null)
    );
