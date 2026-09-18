-- 0003: the editorial layer.
--
-- Publication is a human act. Both tables carry approved_by and approved_at,
-- and RLS refuses to serve a record that has neither. No agent can publish by
-- writing a row. See the hard rule in CLAUDE.md.
--
-- approved_at is the human gate. publish_date is the reader-facing date and may
-- be set ahead of time, so the two are deliberately separate: approval is not
-- scheduling.

create table editorial.case_studies (
  id                uuid primary key default gen_random_uuid(),
  title             text not null,
  publish_date      date,
  data_as_of_date   date not null,
  site_id           uuid references facts.sites (id) on delete set null,
  metrics           jsonb not null default '{}'::jsonb,
  narrative         text,
  approved_by       text,
  approved_at       timestamptz,
  created_at        timestamptz not null default now(),
  updated_at        timestamptz not null default now(),

  constraint case_studies_approval_complete check (
    (approved_by is null and approved_at is null)
    or (approved_by is not null and approved_at is not null)
  ),
  -- A published record must state both dates. docs/UI.md: everything is dated,
  -- showing publish date and data as of date.
  constraint case_studies_published_has_date check (
    approved_at is null or publish_date is not null
  )
);

comment on column editorial.case_studies.metrics is
  'Financial metrics: total_capex_aud, annual_revenue_aud, annual_opex_aud,
   development_yield_pct, stabilised_cap_rate_pct, power_cost_per_kw.
   These are factual figures inside an editorial table, the one deliberate
   boundary crossing in the model. They carry citations like any other factual
   claim and are never estimated. See docs/SPEC.md "Schema separation".';
comment on column editorial.case_studies.data_as_of_date is
  'When the underlying data was current, which is not when the piece was
   published. Both are shown to the reader.';

create index case_studies_publish_date_idx
  on editorial.case_studies (publish_date desc);
create index case_studies_site_id_idx on editorial.case_studies (site_id);

create table editorial.essays (
  id           uuid primary key default gen_random_uuid(),
  title        text not null,
  publish_date date,
  youtube_id   text,
  body         text,
  tags         text[] not null default '{}',
  related_ids  uuid[] not null default '{}',
  approved_by  text,
  approved_at  timestamptz,
  created_at   timestamptz not null default now(),
  updated_at   timestamptz not null default now(),

  constraint essays_approval_complete check (
    (approved_by is null and approved_at is null)
    or (approved_by is not null and approved_at is not null)
  ),
  constraint essays_published_has_date check (
    approved_at is null or publish_date is not null
  )
);

comment on column editorial.essays.related_ids is
  'Open item. This is an untyped polymorphic array with the same shape problem
   that source_ids had, and should be resolved against facts.links rather than
   becoming a third relationship mechanism. Tracked in docs/SPEC.md
   "Citations".';

create index essays_publish_date_idx on editorial.essays (publish_date desc);

create trigger case_studies_set_updated_at
  before update on editorial.case_studies
  for each row execute function facts.set_updated_at();

create trigger essays_set_updated_at
  before update on editorial.essays
  for each row execute function facts.set_updated_at();
