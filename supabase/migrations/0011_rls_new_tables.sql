-- 0011: Row Level Security for the tables added in 0009 and 0010.
--
-- 0004 ends with `alter default privileges ... revoke all on tables`, so a new
-- table is unreachable until it is granted explicitly. That default is the
-- point: a table added without thinking about who may read it is invisible,
-- not open. Each table below is therefore opted in deliberately.
--
-- Same shape as 0004 throughout: RLS on, select granted to anon and
-- authenticated, one select policy, and no insert, update or delete policy for
-- anyone. Writes remain the service role's alone.

alter table facts.research_agenda enable row level security;
alter table facts.lga_aliases     enable row level security;
alter table facts.ingest_runs     enable row level security;

grant select on facts.research_agenda, facts.lga_aliases, facts.ingest_runs
  to anon, authenticated;

-- The research agenda is published for the same reason gaps are: an observatory
-- that shows what it has not established yet is more honest than one that shows
-- only what it has.
create policy research_agenda_public_read on facts.research_agenda
  for select to anon, authenticated using (true);

-- The alias table is a methodological statement. Publishing it lets a reader
-- check which council names were treated as equivalent, and who decided.
create policy lga_aliases_public_read on facts.lga_aliases
  for select to anon, authenticated using (true);

-- The load log is published so a figure on a page can be traced to the build
-- that produced it without asking anyone.
create policy ingest_runs_public_read on facts.ingest_runs
  for select to anon, authenticated using (true);
