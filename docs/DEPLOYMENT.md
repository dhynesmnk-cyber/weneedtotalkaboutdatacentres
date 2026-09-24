# DEPLOYMENT.md

## Environments
- preview: per pull request, Netlify deploy preview paired with an isolated
  Supabase branch.
- production: main branch, Netlify production deploy against the primary
  Supabase project.

## Hosting
- Frontend on Netlify. Configuration lives in netlify.toml at the repo root.
- Backend and database on Supabase.
- Scheduled ingestion via Supabase Edge Functions or GitHub Actions cron.

## Supabase project setup
Step by step instructions are in docs/SUPABASE_SETUP.md. In summary:
- Apply supabase/migrations in order. They create the facts and editorial
  schemas, not public.
- Both schemas must be added under "Exposed schemas" in the project's API
  settings. Neither is reachable through PostgREST otherwise, and every query
  will fail with a schema error rather than an empty result. The local stack
  reads this from supabase/config.toml; a hosted project does not.
- Row Level Security is enabled on every table by migration 0004. Do not disable
  it to debug a query: an unfiltered read is the failure mode the policies exist
  to prevent.
- Point in time recovery is a Pro plan feature and is **not enabled**. The gap
  is recorded under "Backups and recovery" below, along with the weekly export
  that mitigates it. Do not assume a restore point exists for an arbitrary
  moment: the most that can be recovered is the last weekly export.

## CI pipeline
- lint, typecheck, unit tests, build on every pull request.
- The build runs with no Supabase credentials on purpose. Every page that reads
  data is dynamic, so the build never touches the database, and a build that
  only passes with credentials present would be hiding that.
- On merge to main: run supabase migrations, then deploy frontend.

## Caching
Database reads are cached for five minutes (`RECORD_CACHE_SECONDS`, default
300). That bounds how stale a page can be and lets a burst of readers share one
set of queries. Before this was set explicitly, Next.js cached every read for a
year, so a load or a retraction reached readers only on the next deploy.

A change should not wait out the cache. After applying a pipeline load, and
after approving or retracting an essay or case study, clear it:

```
curl -X POST -H "Authorization: Bearer $REVALIDATE_SECRET" \
  https://<site>/api/revalidate
```

The endpoint exists only when `REVALIDATE_SECRET` is set in Netlify. It clears
a cache and can change nothing else. Without it, changes appear within
`RECORD_CACHE_SECONDS`.

## Map tiles
The map uses OpenStreetMap's own tile servers unless `MAP_TILE_URL` and
`MAP_TILE_ATTRIBUTION` are set. Those servers are for light use under the OSM
tile usage policy and are not a production service: choose a provider before
launch and set both. They are read at request time, so changing provider needs
no rebuild. The map is only drawn once some site has coordinates.

## Secrets
- All secrets in Netlify environment variables and Supabase project settings.
- Never commit keys, tokens or connection strings.
- Only the anon key is exposed to the browser. The service role key is used
  exclusively by ingestion jobs and edge functions, never in frontend code.

## Backups and recovery

### The gap, stated plainly
Point in time recovery is **off**. It costs $100 a month for seven days of
retention on top of Pro, which is not proportionate to this project yet. The
recovery point objective is therefore **one week**, not one second, and the
recovery time objective is however long it takes a human to read and apply a
restore artefact.

Revisit this the moment curation starts in earnest. The calculation below turns
on the curated tables being nearly empty; it stops holding once they are not.

### What actually needs backing up
Most of the fact layer is **derived**. `npm run load:pipeline` rebuilds it from
`data-pipeline/`, which is SQLite committed to git, and the load is idempotent.
Losing those rows costs one command.

The rest is **curated**: confirmed links, coordinates, approved councils,
aliases, the research agenda, and everything in `editorial`. Nothing can
recreate these, because overriding derivation is what they exist to do.
`lib/backup/tables.ts` classifies every table and says why, and
`tests/backup/tables.test.ts` fails if a migration adds a table nobody
classified.

Two curated things hide inside derived tables and are listed in
`CURATED_COLUMNS`: `facts.sites.lat/lng`, `facts.entities.major_flag`, and the
confirmation columns on `facts.links`. They are why "just re-run the loader" is
not a complete recovery.

### The weekly export
`.github/workflows/backup.yml` runs `npm run backup:export` every Sunday at
19:00 UTC and uploads the result as a workflow artifact, kept for 90 days —
about thirteen recovery points. It reads over PostgREST with the service role
key, which bypasses RLS: a backup taken with the anon key would silently omit
every proposed link and unapproved essay and still look complete.

It needs two repository secrets, `NEXT_PUBLIC_SUPABASE_URL` and
`SUPABASE_SERVICE_ROLE_KEY`, and the grant in migration `0012`. Without that
grant the service role cannot read either schema at all and the export fails
with `42501`.

The artifact holds the whole database, `editorial` included. Anyone with read
access to the repository can download it. That is acceptable for a private
repository and would not be for a public one.

### Restoring
```bash
# Unzip the artifact, then:
npm run backup:verify  -- --out <dir>                    # digests and row counts
npm run backup:restore -- --in <dir> --curated-only --out .artifacts/restore.sql
less .artifacts/restore.sql                              # this is the review step
psql "$DATABASE_URL" -v ON_ERROR_STOP=1 -f .artifacts/restore.sql
```

`--curated-only` is usually right: the derived tables come back faster and more
trustworthily from `npm run load:pipeline`. Drop the flag to restore everything.

Two properties worth knowing before you need them. The artefact **upserts** — it
recovers lost or corrupted rows but does not remove rows created after the
backup, so it does not rewind the database as a whole; restore into an empty
database if that is what you want. And it is transactional, ending in row count
assertions that roll the whole thing back if less arrived than the manifest
promised.

Verified end to end on 2026-09-21, against the live database with the service
role key. The export read 2529 rows; a restore into a throwaway Postgres 16
reproduced 117 sources, 125 entities, 93 sites, 250 citations, 1885 data gaps
and all 58 links, every one still `proposed`. Applying it twice changed nothing.
In the restored database `anon` saw 0 links and 93 sites while `service_role`
saw all 58, so the security model survives a restore rather than being flattened
by it.

The same export taken with the anon key returned 2471 rows and 0 links. That is
the 58 row difference migration `0012` exists to close, and it is why a backup
must not be taken through the public API.

### Still missing
- Migration down scripts for rollback.
- An off-GitHub copy. Today the backup and the code share one provider, so
  losing the GitHub account loses both. A monthly manual download to somewhere
  else closes most of that at no cost.

## Monitoring
- Error tracking on frontend and edge functions.
- Uptime check on public pages.
- Alerts on ingestion job failure or parse error rate spike.
