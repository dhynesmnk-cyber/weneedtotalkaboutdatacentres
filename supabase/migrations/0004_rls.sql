-- 0004: Row Level Security.
--
-- Default deny. Every table has RLS enabled and only the SELECT policies below.
-- No INSERT, UPDATE or DELETE policy exists for anon or authenticated, so the
-- public API cannot write to any table under any circumstance. Ingestion and
-- editing run under the service role, which bypasses RLS and never reaches the
-- browser (see .env.example).
--
-- Two rules are enforced here rather than in the application, because a rule
-- that lives only in the application is a convention, not a guarantee:
--   1. Unconfirmed links are invisible. Derivation is not publication.
--   2. Unapproved editorial records are invisible. No agent publishes content.

grant usage on schema facts to anon, authenticated;
grant usage on schema editorial to anon, authenticated;

alter table facts.sources            enable row level security;
alter table facts.sites              enable row level security;
alter table facts.entities           enable row level security;
alter table facts.events             enable row level security;
alter table facts.links              enable row level security;
alter table facts.citations          enable row level security;
alter table facts.data_gaps          enable row level security;
alter table facts.council_watchlist  enable row level security;
alter table editorial.case_studies   enable row level security;
alter table editorial.essays         enable row level security;

-- Fact layer: openly browsable. This is the point of the project.
grant select on facts.sources, facts.sites, facts.entities, facts.events,
                facts.citations, facts.data_gaps, facts.council_watchlist
  to anon, authenticated;

create policy sources_public_read on facts.sources
  for select to anon, authenticated using (true);

create policy sites_public_read on facts.sites
  for select to anon, authenticated using (true);

create policy entities_public_read on facts.entities
  for select to anon, authenticated using (true);

create policy events_public_read on facts.events
  for select to anon, authenticated using (true);

create policy citations_public_read on facts.citations
  for select to anon, authenticated using (true);

-- Gaps are findings and are published like any other record.
create policy data_gaps_public_read on facts.data_gaps
  for select to anon, authenticated using (true);

-- The approved council list is public so the ingestion boundary is auditable
-- from outside.
create policy council_watchlist_public_read on facts.council_watchlist
  for select to anon, authenticated using (true);

-- Links: confirmed only. A proposed link is an ingestion suggestion and has no
-- public standing.
grant select on facts.links to anon, authenticated;

create policy links_public_read_confirmed_only on facts.links
  for select to anon, authenticated
  using (state = 'confirmed');

-- Editorial layer: approved and dated only.
grant select on editorial.case_studies, editorial.essays to anon, authenticated;

create policy case_studies_public_read_approved_only on editorial.case_studies
  for select to anon, authenticated
  using (
    approved_at is not null
    and publish_date is not null
    and publish_date <= current_date
  );

create policy essays_public_read_approved_only on editorial.essays
  for select to anon, authenticated
  using (
    approved_at is not null
    and publish_date is not null
    and publish_date <= current_date
  );

-- Nothing is granted on future tables by default.
alter default privileges in schema facts revoke all on tables from anon, authenticated;
alter default privileges in schema editorial revoke all on tables from anon, authenticated;
