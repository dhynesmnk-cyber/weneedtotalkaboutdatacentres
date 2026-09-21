-- 0012: let the service role read both schemas.
--
-- 0004 revokes default privileges so a new table is unreachable until someone
-- opts it in, and 0004 and 0011 then opt every table in for anon and
-- authenticated only. The service role was never granted anything, which meant
-- the role the deployment documentation reserves for ingestion jobs, edge
-- functions and backups could not read a single row: PostgREST answered 42501,
-- "permission denied for schema facts".
--
-- The role bypasses Row Level Security, so this grant is what stands between it
-- and the data. It is therefore SELECT and nothing else. Write access is a
-- separate decision with a separate blast radius, and nothing in the repository
-- needs it yet: the pipeline loader emits SQL for a human to apply rather than
-- writing to the database itself, which is the guarantee behind "no agent
-- publishes content". A future ingestion job that genuinely needs to write
-- should add its own migration naming the tables it writes to, rather than
-- widening this one.
--
-- Read access for this role is what makes a free backup possible. The weekly
-- export in .github/workflows/backup.yml reads through PostgREST with this key
-- precisely because the role bypasses RLS: a backup taken through the public
-- API would silently omit every proposed link and every unapproved essay, and
-- look complete while doing it.

grant usage on schema facts     to service_role;
grant usage on schema editorial to service_role;

grant select on
  facts.sources,
  facts.entities,
  facts.sites,
  facts.events,
  facts.citations,
  facts.data_gaps,
  facts.links,
  facts.lga_aliases,
  facts.council_watchlist,
  facts.research_agenda,
  facts.ingest_runs
  to service_role;

grant select on editorial.essays, editorial.case_studies to service_role;

-- Deliberately no `alter default privileges` for this role. A table added by a
-- later migration stays unreadable until someone names it here, which is the
-- same discipline 0004 established and the reason tests/backup/tables.test.ts
-- fails when a migration adds a table the backup catalogue does not list.
