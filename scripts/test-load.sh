#!/usr/bin/env bash
#
# End-to-end proof that the curation pipeline loads into this schema correctly.
#
# Creates a throwaway database, applies supabase/migrations in order, generates
# the load artefact from data-pipeline/, applies it TWICE, and asserts what the
# public can actually see. Any failed assertion aborts with a non-zero exit.
#
# Applying twice is the point of the second half: idempotence cannot be tested
# any other way, and a loader that duplicates rows on a re-run is a loader that
# cannot be run again after a correction.
#
# Needs a reachable Postgres 14 or later and no Supabase at all:
#
#   PGHOST=127.0.0.1 PGPORT=5432 PGUSER=postgres ./scripts/test-load.sh

set -euo pipefail

PGHOST="${PGHOST:-127.0.0.1}"
PGPORT="${PGPORT:-5432}"
PGUSER="${PGUSER:-postgres}"
TEST_DB="${TEST_DB:-observatory_load_test}"

export PGHOST PGPORT PGUSER

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
artefact="${repo_root}/.artifacts/load-pipeline.test.sql"

echo "Creating ${TEST_DB} on ${PGHOST}:${PGPORT}"
psql -q -d postgres -c "drop database if exists ${TEST_DB};"
psql -q -d postgres -c "create database ${TEST_DB};"

psql -q -d "${TEST_DB}" <<'SQL'
do $$
begin
  if not exists (select 1 from pg_roles where rolname = 'anon') then
    create role anon nologin;
  end if;
  if not exists (select 1 from pg_roles where rolname = 'authenticated') then
    create role authenticated nologin;
  end if;
  if not exists (select 1 from pg_roles where rolname = 'service_role') then
    create role service_role nologin bypassrls;
  end if;
end;
$$;
SQL

echo "Applying migrations"
for migration in "${repo_root}"/supabase/migrations/*.sql; do
  echo "  $(basename "${migration}")"
  psql -v ON_ERROR_STOP=1 -q -d "${TEST_DB}" -f "${migration}"
done

echo "Generating the load artefact"
(cd "${repo_root}" && npx tsx scripts/ingestion/load-pipeline.ts --out "${artefact}") \
  | sed 's/^/  /'

echo "Applying the load"
psql -v ON_ERROR_STOP=1 -q -d "${TEST_DB}" -f "${artefact}"

echo "Capturing row counts"
counts_before="$(psql -tA -d "${TEST_DB}" -c "
  select string_agg(t || '=' || n, ',' order by t) from (
    select 'sites' t, count(*) n from facts.sites
    union all select 'entities', count(*) from facts.entities
    union all select 'sources', count(*) from facts.sources
    union all select 'citations', count(*) from facts.citations
    union all select 'data_gaps', count(*) from facts.data_gaps
    union all select 'links', count(*) from facts.links
  ) x;")"
echo "  ${counts_before}"

echo "Applying the load a second time"
psql -v ON_ERROR_STOP=1 -q -d "${TEST_DB}" -f "${artefact}"

counts_after="$(psql -tA -d "${TEST_DB}" -c "
  select string_agg(t || '=' || n, ',' order by t) from (
    select 'sites' t, count(*) n from facts.sites
    union all select 'entities', count(*) from facts.entities
    union all select 'sources', count(*) from facts.sources
    union all select 'citations', count(*) from facts.citations
    union all select 'data_gaps', count(*) from facts.data_gaps
    union all select 'links', count(*) from facts.links
  ) x;")"

if [ "${counts_before}" != "${counts_after}" ]; then
  echo "NOT IDEMPOTENT" >&2
  echo "  first  load: ${counts_before}" >&2
  echo "  second load: ${counts_after}" >&2
  exit 1
fi
echo "  unchanged: the load is idempotent"

echo "Running assertions"
psql -v ON_ERROR_STOP=1 -q -d "${TEST_DB}" -f "${repo_root}/supabase/tests/load.test.sql"

if [ "${KEEP_TEST_DB:-}" != "1" ]; then
  psql -q -d postgres -c "drop database if exists ${TEST_DB};"
  rm -f "${artefact}"
fi

echo "Load tests passed."
