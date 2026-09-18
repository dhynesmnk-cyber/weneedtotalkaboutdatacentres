#!/usr/bin/env bash
#
# Run the live Row Level Security and constraint tests.
#
# Creates a throwaway database, applies supabase/migrations in order, then runs
# supabase/tests/rls.test.sql against it. Any failed assertion aborts with a
# non-zero exit.
#
# Needs a reachable Postgres 14 or later. Point it at one with the standard PG
# environment variables, or let the defaults find a local instance:
#
#   PGHOST=127.0.0.1 PGPORT=5432 PGUSER=postgres ./scripts/test-rls.sh
#
# This does not need Supabase itself. The anon, authenticated and service_role
# roles that Supabase provides are created here so the grants and policies
# resolve exactly as they would in a real project.

set -euo pipefail

PGHOST="${PGHOST:-127.0.0.1}"
PGPORT="${PGPORT:-5432}"
PGUSER="${PGUSER:-postgres}"
TEST_DB="${TEST_DB:-observatory_rls_test}"

export PGHOST PGPORT PGUSER

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "Creating ${TEST_DB} on ${PGHOST}:${PGPORT}"
psql -q -d postgres -c "drop database if exists ${TEST_DB};"
psql -q -d postgres -c "create database ${TEST_DB};"

# Supabase supplies these roles. Create them so grants and policies resolve.
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

echo "Running assertions"
psql -v ON_ERROR_STOP=1 -q -d "${TEST_DB}" -f "${repo_root}/supabase/tests/rls.test.sql"

if [ "${KEEP_TEST_DB:-}" != "1" ]; then
  psql -q -d postgres -c "drop database if exists ${TEST_DB};"
fi

echo "RLS tests passed."
