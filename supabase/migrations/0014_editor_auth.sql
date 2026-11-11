-- 0014: who may edit, and how the database knows who is asking.
--
-- The site gains one signed-in role: the editor, who edits drafts and approves
-- them for publication at /admin. Publication stays a human act (CLAUDE.md):
-- an agent writes drafts, never holds the editor's session, and cannot approve.
--
-- Identity comes from the request's JWT claims, which PostgREST sets on every
-- Supabase API request as the setting request.jwt.claims. Supabase verifies the
-- token's signature before PostgREST sees it, so the claims are the signed-in
-- user's own. They are read directly rather than through Supabase's auth.jwt()
-- so that these migrations still apply to the plain Postgres the RLS, load and
-- UI tests run on.
--
-- Being signed in is not enough. The editor's email must also be on the
-- allow-list below. Rows are inserted by hand (docs/SUPABASE_SETUP.md), so
-- the editor's address is never committed to the repository.

create table editorial.editors (
  email     text primary key,
  added_by  text not null,
  added_at  timestamptz not null default now(),

  constraint editors_email_normalised check (email = lower(email) and email like '%_@_%')
);

comment on table editorial.editors is
  'The allow-list of people who may edit and approve editorial records. Read
   only by editorial.is_editor(); granted to no API role.';

alter table editorial.editors enable row level security;
-- No grant to anon or authenticated and no policy: the API cannot read or
-- change the allow-list. The weekly backup reads it through the service role,
-- like every other table (0012), so a restore brings the editor back.
grant select on editorial.editors to service_role;

-- The current request's JWT claims, or an empty object outside an API request.
create function editorial.request_claims()
returns jsonb
language sql
stable
set search_path = ''
as $$
  select coalesce(nullif(current_setting('request.jwt.claims', true), ''), '{}')::jsonb;
$$;

-- True only for a signed-in user whose email is on the allow-list. The anon
-- and service_role keys carry no email and a different role, so neither can
-- ever pass, whatever the allow-list holds.
create function editorial.is_editor()
returns boolean
language sql
stable
security definer
set search_path = ''
as $$
  select coalesce(
    (editorial.request_claims() ->> 'role') = 'authenticated'
    and exists (
      select 1
      from editorial.editors e
      where e.email = lower(editorial.request_claims() ->> 'email')
    ),
    false
  );
$$;

-- The signed-in editor's email, as recorded on what they change.
create function editorial.editor_email()
returns text
language sql
stable
set search_path = ''
as $$
  select lower(editorial.request_claims() ->> 'email');
$$;

-- Hosted Supabase can grant the API roles execute on new functions by
-- default, so every grant here is revoked by name, not only from public.
revoke all on function editorial.request_claims() from public, anon, authenticated, service_role;
revoke all on function editorial.is_editor() from public, anon, authenticated, service_role;
revoke all on function editorial.editor_email() from public, anon, authenticated, service_role;
-- Policies on tables the editor reads call is_editor() as the signed-in role.
grant execute on function editorial.is_editor() to authenticated;

-- Every approval and retraction, in order. Written only by the functions in
-- 0017. The body's hash records exactly which text was approved.
create table editorial.approvals (
  id           uuid primary key default gen_random_uuid(),
  record_type  text not null,
  record_id    uuid not null,
  action       text not null,
  actor_email  text not null,
  reason       text,
  body_sha256  text,
  at           timestamptz not null default now(),

  constraint approvals_record_type_known check (record_type in ('essays')),
  constraint approvals_action_known check (action in ('approve', 'retract')),
  constraint approvals_retraction_has_reason check (action <> 'retract' or reason is not null)
);

create index approvals_record_idx on editorial.approvals (record_type, record_id, at desc);

alter table editorial.approvals enable row level security;

grant select on editorial.approvals to authenticated;

create policy approvals_editor_read on editorial.approvals
  for select to authenticated
  using (editorial.is_editor());

-- Backups read every table through the service role (0012).
grant select on editorial.approvals to service_role;
