-- 0009: the research agenda.
--
-- This is NOT facts.data_gaps, and conflating the two would lose both.
--
--   facts.data_gaps answers "this field on this record is empty, and here is
--   why" — a per-field absence with one of four reasons.
--
--   facts.research_agenda answers "here is a question we have not answered yet,
--   why it matters, and how we intend to get at it" — an open line of enquiry
--   that may span many records or none.
--
-- The pipeline calls its version research_gaps, which is where the confusion
-- would come from. The name is different here on purpose.
--
-- Publishing the agenda is the point: an observatory that shows what it has not
-- yet established is more honest than one that shows only what it has.

create table facts.research_agenda (
  id              uuid primary key default gen_random_uuid(),
  pipeline_id     text,
  pillar          text,
  question        text not null,
  why_it_matters  text,
  target_source   text,
  retrieval_method text,
  priority        integer,
  status          text not null default 'open',
  opened          date,
  resolved_date   date,
  notes           text,
  fact_status     facts.fact_status,
  confidence      facts.confidence_level,
  as_of_date      date,
  created_at      timestamptz not null default now(),
  updated_at      timestamptz not null default now(),

  constraint research_agenda_status_known
    check (status in ('open', 'in_progress', 'resolved')),
  constraint research_agenda_priority_range
    check (priority is null or priority between 1 and 5),

  -- A resolved question has a resolution date; an open one does not claim one.
  constraint research_agenda_resolution_complete
    check (
      (status = 'resolved' and resolved_date is not null)
      or (status <> 'resolved' and resolved_date is null)
    )
);

create unique index research_agenda_pipeline_id_key
  on facts.research_agenda (pipeline_id) where pipeline_id is not null;

create index research_agenda_status_idx   on facts.research_agenda (status);
create index research_agenda_priority_idx on facts.research_agenda (priority desc);

create trigger research_agenda_set_updated_at
  before update on facts.research_agenda
  for each row execute function facts.set_updated_at();

comment on table facts.research_agenda is
  'Open questions, not field-level gaps. See facts.data_gaps for those.';

comment on column facts.research_agenda.priority is
  '1 to 5, 5 most urgent, as graded by the curator.';

-- The pipeline also records an internal owner against each question. It is not
-- imported: who is assigned a task is workflow, not a finding, and this table
-- is publicly readable.
