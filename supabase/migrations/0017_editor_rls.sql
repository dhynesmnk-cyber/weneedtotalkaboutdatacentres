-- 0017: what the editor may do, and the one way a piece is approved.
--
-- Until now no API role could write anything (0004). This migration opens
-- exactly one path, and only for the signed-in editor (0014):
--
--   - read every essay, draft or published;
--   - create a draft, and change a draft's text and metadata;
--   - approve or retract, through the two functions below and nothing else.
--
-- The approval columns are left out of the column grants, so even the editor
-- cannot set approved_by or approved_at with an UPDATE: Postgres refuses the
-- statement before any policy runs. approve_essay() sets them, taking the
-- approver from the signed-in session. It accepts no approver argument, so no
-- caller can approve in someone else's name, and it is granted to
-- authenticated only, never to anon or service_role. An agent never holds an
-- editor session (CLAUDE.md: no agent publishes content).
--
-- A published piece cannot be edited in place. The editor retracts it, edits
-- the draft and approves again, so every published text has its own approval
-- record in editorial.approvals.

grant insert (title, slug, kind, standfirst, body, tags, youtube_id, data_as_of_date,
              conflict, named_parties, story_cards, proposal_no, publish_date)
  on editorial.essays to authenticated;

grant update (title, slug, standfirst, body, tags, youtube_id, data_as_of_date,
              conflict, named_parties, publish_date)
  on editorial.essays to authenticated;

create policy essays_editor_read on editorial.essays
  for select to authenticated
  using (editorial.is_editor());

create policy essays_editor_insert_draft on editorial.essays
  for insert to authenticated
  with check (editorial.is_editor() and approved_at is null and approved_by is null);

create policy essays_editor_update_draft on editorial.essays
  for update to authenticated
  using (editorial.is_editor() and approved_at is null)
  with check (editorial.is_editor() and approved_at is null and approved_by is null);

-- The checks a piece must pass before it can be published. Mirrors the
-- reviewer checklist in docs/REVIEW.md as far as a database can check it;
-- the rest (the legal check, the reading of sources) is the editor's
-- acknowledgement.
create function editorial.approve_essay(
  p_id                  uuid,
  p_publish_date        date,
  p_expected_updated_at timestamptz,
  p_legal_ack           boolean default false
)
returns editorial.essays
language plpgsql
security definer
set search_path = ''
as $$
declare
  piece  editorial.essays;
  actor  text := editorial.editor_email();
  cited  integer;
begin
  if not editorial.is_editor() then
    raise exception 'Only the signed-in editor can approve a piece.'
      using errcode = 'insufficient_privilege';
  end if;

  select * into piece from editorial.essays where id = p_id for update;
  if not found then
    raise exception 'There is no piece with id %.', p_id using errcode = 'no_data_found';
  end if;

  if piece.approved_at is not null then
    raise exception 'This piece is already approved.' using errcode = 'check_violation';
  end if;

  -- The editor approves the text they read. If it changed since they loaded
  -- it, they must read it again.
  if piece.updated_at is distinct from p_expected_updated_at then
    raise exception 'This piece changed after you opened it. Reload it and read it again before approving.'
      using errcode = 'serialization_failure';
  end if;

  if p_publish_date is null then
    raise exception 'Choose a publish date.' using errcode = 'check_violation';
  end if;

  if piece.data_as_of_date is null then
    raise exception 'Set the date the data is current to (data as at) before approving.'
      using errcode = 'check_violation';
  end if;

  if coalesce(btrim(piece.body), '') = '' then
    raise exception 'This piece has no text.' using errcode = 'check_violation';
  end if;

  if piece.kind in ('essay', 'proposal') then
    select count(distinct source_id) into cited
      from facts.citations
     where record_type = 'essays' and record_id = p_id;

    -- docs/UX.md: an essay cites at least five records, or it is commentary.
    if cited < 5 then
      raise exception 'An essay must cite at least five source records. This one cites %.', cited
        using errcode = 'check_violation';
    end if;

    -- Opinion is allowed only after the divider, which is drawn before this
    -- heading. Without it there is nowhere for the argument to go.
    if piece.body !~ '(^|\n)## (Our view|Our proposal)[ \t]*(\n|$)' then
      raise exception 'An essay needs an "## Our view" section (or "## Our proposal") so its argument sits after the divider.'
        using errcode = 'check_violation';
    end if;
  end if;

  if cardinality(piece.named_parties) > 0 and not coalesce(p_legal_ack, false) then
    raise exception 'This piece names people. Confirm the legal check in docs/REVIEW.md has been done.'
      using errcode = 'check_violation';
  end if;

  update editorial.essays
     set approved_by  = actor,
         approved_at  = now(),
         publish_date = p_publish_date
   where id = p_id
  returning * into piece;

  insert into editorial.approvals (record_type, record_id, action, actor_email, body_sha256)
  values ('essays', p_id, 'approve', actor,
          encode(sha256(convert_to(coalesce(piece.body, ''), 'UTF8')), 'hex'));

  return piece;
end;
$$;

create function editorial.retract_essay(p_id uuid, p_reason text)
returns editorial.essays
language plpgsql
security definer
set search_path = ''
as $$
declare
  piece editorial.essays;
  actor text := editorial.editor_email();
begin
  if not editorial.is_editor() then
    raise exception 'Only the signed-in editor can retract a piece.'
      using errcode = 'insufficient_privilege';
  end if;

  if coalesce(btrim(p_reason), '') = '' then
    raise exception 'Say why the piece is being retracted. The reason is kept with the record.'
      using errcode = 'check_violation';
  end if;

  update editorial.essays
     set approved_by = null,
         approved_at = null
   where id = p_id and approved_at is not null
  returning * into piece;

  if not found then
    raise exception 'There is no approved piece with id %.', p_id using errcode = 'no_data_found';
  end if;

  insert into editorial.approvals (record_type, record_id, action, actor_email, reason)
  values ('essays', p_id, 'retract', actor, p_reason);

  return piece;
end;
$$;

revoke all on function editorial.approve_essay(uuid, date, timestamptz, boolean)
  from public, anon, authenticated, service_role;
revoke all on function editorial.retract_essay(uuid, text)
  from public, anon, authenticated, service_role;
grant execute on function editorial.approve_essay(uuid, date, timestamptz, boolean) to authenticated;
grant execute on function editorial.retract_essay(uuid, text) to authenticated;
