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
- Point in time recovery is a Pro plan feature. The backup policy below assumes
  it. On the free tier, record the gap rather than assuming it is covered.

## CI pipeline
- lint, typecheck, unit tests, build on every pull request.
- The build runs with no Supabase credentials on purpose. Every page that reads
  data is dynamic, so the build never touches the database, and a build that
  only passes with credentials present would be hiding that.
- On merge to main: run supabase migrations, then deploy frontend.

## Secrets
- All secrets in Netlify environment variables and Supabase project settings.
- Never commit keys, tokens or connection strings.
- Only the anon key is exposed to the browser. The service role key is used
  exclusively by ingestion jobs and edge functions, never in frontend code.

## Backups and recovery
- Supabase point in time recovery enabled.
- Weekly export of content tables to object storage.
- Migration down scripts maintained for rollback.

## Monitoring
- Error tracking on frontend and edge functions.
- Uptime check on public pages.
- Alerts on ingestion job failure or parse error rate spike.
