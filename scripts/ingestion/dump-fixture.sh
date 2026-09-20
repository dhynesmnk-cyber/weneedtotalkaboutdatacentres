#!/usr/bin/env bash
#
# Regenerate tests/fixtures/loaded-site.json from a loaded database.
#
# The render tests assert against real rows rather than invented ones, so the
# fixture has to come from a real load. Run the load first, keeping the
# database:
#
#   KEEP_TEST_DB=1 npm run test:load
#   ./scripts/ingestion/dump-fixture.sh
#
# The dump is taken as the anon role, so the fixture contains exactly what a
# reader could see and nothing more.

set -euo pipefail

PGHOST="${PGHOST:-127.0.0.1}"
PGPORT="${PGPORT:-5432}"
PGUSER="${PGUSER:-postgres}"
TEST_DB="${TEST_DB:-observatory_load_test}"
SITE="${SITE:-SITE_MAMRE_ROAD}"

export PGHOST PGPORT PGUSER

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
out="${repo_root}/tests/fixtures/loaded-site.json"

psql -tA -d "${TEST_DB}" -c "
select json_build_object(
  'site', (select row_to_json(s) from facts.sites s where s.pipeline_id='${SITE}'),
  'gaps', (select coalesce(json_agg(row_to_json(g)),'[]'::json) from facts.data_gaps g
            join facts.sites s on s.id=g.record_id
           where s.pipeline_id='${SITE}' and g.record_type='sites'),
  'citations', (select coalesce(json_agg(json_build_object(
                  'id',c.id,'source_id',c.source_id,'record_type',c.record_type,
                  'record_id',c.record_id,'claim',c.claim,'created_at',c.created_at,
                  'source',(select row_to_json(src) from facts.sources src where src.id=c.source_id))),'[]'::json)
                from facts.citations c join facts.sites s on s.id=c.record_id
               where s.pipeline_id='${SITE}' and c.record_type='sites'),
  'claimed', (select coalesce(json_agg(row_to_json(s)),'[]'::json) from (
                select name, status, fact_status, confidence from facts.sites
                 where fact_status='claimed' order by name limit 3) s)
)" | python3 -c "
import sys, json
raw = [line for line in sys.stdin if line.strip().startswith('{')][0]
json.dump(json.loads(raw), open('${out}', 'w'), indent=2, sort_keys=True)
print('wrote ${out}')
"
