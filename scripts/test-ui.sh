#!/usr/bin/env bash
#
# Browser smoke test of the public site against the real pipeline load.
#
# Loads data-pipeline/ into a throwaway database (via test-load.sh), serves it
# through PostgREST as the anon role, builds and starts the site against it,
# then runs scripts/ui/smoke.ts: status codes, uncaught browser errors, and
# axe WCAG 2.2 AA checks on every public page at desktop and phone widths.
#
# Needs a reachable Postgres 14 or later, Docker (for PostgREST), and a
# Playwright Chromium (`npx playwright install chromium`, or CHROMIUM_PATH):
#
#   PGHOST=127.0.0.1 PGPORT=5432 PGUSER=postgres PGPASSWORD=postgres \
#     ./scripts/test-ui.sh
#
# No Supabase project and no secrets. Nothing here is test data: every record
# on screen is one the pipeline load put there.

set -euo pipefail

PGHOST="${PGHOST:-127.0.0.1}"
PGPORT="${PGPORT:-5432}"
PGUSER="${PGUSER:-postgres}"
TEST_DB="${TEST_DB:-observatory_ui_test}"
POSTGREST_IMAGE="${POSTGREST_IMAGE:-postgrest/postgrest:v12.2.3}"
POSTGREST_PORT="${POSTGREST_PORT:-3100}"
PROXY_PORT="${PROXY_PORT:-3200}"
APP_PORT="${APP_PORT:-3000}"

export PGHOST PGPORT PGUSER

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${repo_root}"

container="observatory-ui-postgrest-$$"
pids=()

# Job control puts each background job in its own process group, so cleanup
# can stop the whole group: npx and tsx each start a child process, and
# killing only the parent would leave a server holding its port.
set -m

cleanup() {
  for pid in "${pids[@]:-}"; do
    [ -n "${pid}" ] && kill -- "-${pid}" 2>/dev/null || true
  done
  docker rm -f "${container}" >/dev/null 2>&1 || true
  if [ "${KEEP_TEST_DB:-}" != "1" ]; then
    psql -q -d postgres -c "drop database if exists ${TEST_DB};" || true
  fi
}
trap cleanup EXIT

wait_for() {
  local url="$1" name="$2"
  for _ in $(seq 1 60); do
    if curl -s -o /dev/null "${url}"; then return 0; fi
    sleep 1
  done
  echo "${name} did not come up at ${url}" >&2
  return 1
}

echo "Loading the pipeline into ${TEST_DB}"
TEST_DB="${TEST_DB}" KEEP_TEST_DB=1 ./scripts/test-load.sh >/dev/null

echo "Starting PostgREST on ${POSTGREST_PORT}"
docker run -d --name "${container}" --network host \
  -e PGRST_DB_URI="postgres://${PGUSER}:${PGPASSWORD:-}@${PGHOST}:${PGPORT}/${TEST_DB}" \
  -e PGRST_DB_SCHEMAS="facts,editorial" \
  -e PGRST_DB_ANON_ROLE=anon \
  -e PGRST_SERVER_PORT="${POSTGREST_PORT}" \
  "${POSTGREST_IMAGE}" >/dev/null
wait_for "http://127.0.0.1:${POSTGREST_PORT}/" "PostgREST"

npx tsx scripts/ui/rest-proxy.ts "${PROXY_PORT}" "${POSTGREST_PORT}" &
pids+=("$!")

if [ "${SKIP_BUILD:-}" != "1" ]; then
  echo "Building"
  npm run build >/dev/null
fi

echo "Starting the site on ${APP_PORT}"
# The anon key is a placeholder: the proxy drops it, and the database role is
# fixed by PostgREST. The site only needs both variables set to connect.
NEXT_PUBLIC_SUPABASE_URL="http://127.0.0.1:${PROXY_PORT}" \
NEXT_PUBLIC_SUPABASE_ANON_KEY="ui-smoke-test" \
  npx next start -p "${APP_PORT}" -H 127.0.0.1 >/dev/null &
pids+=("$!")
wait_for "http://127.0.0.1:${APP_PORT}/" "The site"

APP_URL="http://127.0.0.1:${APP_PORT}" \
REST_URL="http://127.0.0.1:${PROXY_PORT}/rest/v1" \
  npx tsx scripts/ui/smoke.ts
