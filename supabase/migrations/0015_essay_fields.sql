-- 0015: what an essay record needs to be written, checked and published.
--
-- One table serves every editorial piece that is argued in prose: essays, the
-- "Where we stand" position, and the "What if…?" policy proposals. One table
-- means one approval gate, one set of row level security policies and one way
-- of citing sources, rather than three of each to keep in step. `kind` says
-- which a row is.
--
-- Provenance columns record where a draft came from. An agent's draft arrives
-- from a Markdown file in editorial/essays/ through a reviewed SQL artefact
-- (scripts/editorial/load-essays.ts). Once the editor changes it in /admin,
-- the row is the source of truth and the loader leaves it alone.

create type editorial.piece_kind as enum ('essay', 'position', 'proposal');

alter table editorial.essays
  add column kind               editorial.piece_kind not null default 'essay',
  add column slug               text,
  add column standfirst         text,
  add column data_as_of_date    date,
  add column conflict           text,
  add column named_parties      text[] not null default '{}',
  add column story_cards        text[] not null default '{}',
  add column proposal_no        smallint,
  add column source_file        text,
  add column source_sha256      text,
  add column edited_in_admin_at timestamptz,
  add column last_edited_by     text;

comment on column editorial.essays.data_as_of_date is
  'When the records the piece relies on were current. Shown beside the publish
   date, as on case studies. Required before approval.';
comment on column editorial.essays.conflict is
  'A conflict of interest the reader should know about, shown above the body.
   For example, a piece touching Anthropic says that it was drafted with Claude,
   which Anthropic makes.';
comment on column editorial.essays.named_parties is
  'Every person the piece names, by role. Any entry requires the legal check in
   docs/REVIEW.md, and approval refuses to proceed without it.';
comment on column editorial.essays.edited_in_admin_at is
  'Set by trigger when the editor changes the row. From then on the row, not
   the Markdown file, is the source of truth, and the loader skips it.';

create unique index essays_slug_key on editorial.essays (slug) where slug is not null;

alter table editorial.essays
  add constraint essays_slug_format
    check (slug is null or slug ~ '^[a-z0-9]+(-[a-z0-9]+)*$'),
  add constraint essays_published_has_data_date
    check (approved_at is null or data_as_of_date is not null),
  add constraint essays_proposal_numbered
    check ((kind = 'proposal') = (proposal_no is not null)
           and (proposal_no is null or proposal_no between 1 and 9));

-- Every earlier version of an essay's text, so the editor can see what changed
-- between an agent's draft and what was approved.
create table editorial.essay_revisions (
  id         uuid primary key default gen_random_uuid(),
  essay_id   uuid not null references editorial.essays (id) on delete cascade,
  title      text not null,
  standfirst text,
  body       text,
  edited_by  text,
  edited_at  timestamptz not null,
  saved_at   timestamptz not null default now()
);

create index essay_revisions_essay_idx on editorial.essay_revisions (essay_id, saved_at desc);

alter table editorial.essay_revisions enable row level security;

grant select on editorial.essay_revisions to authenticated;

create policy essay_revisions_editor_read on editorial.essay_revisions
  for select to authenticated
  using (editorial.is_editor());

grant select on editorial.essay_revisions to service_role;

-- Before any change: keep the previous text, and stamp an editor's change with
-- who made it. The stamp is set here, not by the client, so it cannot be
-- forged, and the columns it writes are not granted to the editor (0017).
create function editorial.essays_before_update()
returns trigger
language plpgsql
security definer
set search_path = ''
as $$
begin
  if old.body is distinct from new.body
     or old.title is distinct from new.title
     or old.standfirst is distinct from new.standfirst then
    insert into editorial.essay_revisions (essay_id, title, standfirst, body, edited_by, edited_at)
    values (old.id, old.title, old.standfirst, old.body, old.last_edited_by, old.updated_at);
  end if;

  -- Only a change to what the reader sees counts as an edit. Approving or
  -- retracting is recorded in editorial.approvals instead.
  if editorial.is_editor()
     and (old.title, old.standfirst, old.body, old.tags, old.youtube_id, old.slug,
          old.data_as_of_date, old.conflict, old.named_parties)
         is distinct from
         (new.title, new.standfirst, new.body, new.tags, new.youtube_id, new.slug,
          new.data_as_of_date, new.conflict, new.named_parties) then
    new.last_edited_by := editorial.editor_email();
    new.edited_in_admin_at := now();
  end if;

  return new;
end;
$$;

create trigger essays_keep_revisions
  before update on editorial.essays
  for each row execute function editorial.essays_before_update();

create function editorial.essays_before_insert()
returns trigger
language plpgsql
security definer
set search_path = ''
as $$
begin
  if editorial.is_editor() then
    new.last_edited_by := editorial.editor_email();
    new.edited_in_admin_at := now();
  end if;
  return new;
end;
$$;

create trigger essays_stamp_editor
  before insert on editorial.essays
  for each row execute function editorial.essays_before_insert();

revoke all on function editorial.essays_before_update() from public, anon, authenticated, service_role;
revoke all on function editorial.essays_before_insert() from public, anon, authenticated, service_role;
