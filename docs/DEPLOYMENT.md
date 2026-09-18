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

## CI pipeline
- lint, typecheck, unit tests, build on every pull request.
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
