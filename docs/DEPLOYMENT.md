# DEPLOYMENT.md

## Environments
- preview: per pull request, isolated Supabase branch.
- production: main branch, primary Supabase project.

## Hosting
- Frontend on Vercel.
- Backend and database on Supabase.
- Scheduled ingestion via Supabase Edge Functions or GitHub Actions cron.

## CI pipeline
- lint, typecheck, unit tests, build on every pull request.
- On merge to main: run supabase migrations, then deploy frontend.

## Secrets
- All secrets in platform environment variables.
- Never commit keys, tokens or connection strings.

## Backups and recovery
- Supabase point in time recovery enabled.
- Weekly export of content tables to object storage.
- Migration down scripts maintained for rollback.

## Monitoring
- Error tracking on frontend and edge functions.
- Uptime check on public pages.
- Alerts on ingestion job failure or parse error rate spike.
