# SUPABASE_SETUP.md

How to create the Supabase project and point the app at it.

The migrations in `supabase/migrations` have been applied to a real Postgres 16
and the behavioural tests in `supabase/tests/rls.test.sql` pass against them, so
the schema is known to work. What follows is the project creation and linking,
which needs an account and cannot be done from an agent session.

## Status

No Supabase project exists yet. Nothing in the app depends on one: every page
renders an explicit "no database connected" state, and `npm run build` succeeds
without credentials.

## 1. Create the project

At https://supabase.com/dashboard, create a project.

- **Region**: Sydney (`ap-southeast-2`). The audience and the data are
  Australian, and it keeps records onshore.
- **Plan**: the free tier is enough to start, but note that it has no
  point-in-time recovery. `docs/DEPLOYMENT.md` requires PITR, which needs Pro.
  Either upgrade before real data is loaded, or record the gap.
- Save the database password somewhere durable. It is shown once.

## 2. Apply the migrations

```bash
npm install -g supabase          # or brew install supabase/tap/supabase
supabase login
supabase link --project-ref <your-project-ref>
supabase db push
```

`supabase db push` applies `supabase/migrations` in order. It should report four
migrations applied and no errors.

## 3. Expose the schemas

**This step is not optional and is the most common way to get a working database
and a broken app.**

The schemas are `facts` and `editorial`, not `public`. PostgREST only serves
schemas it has been told about, so until this is done every query fails with a
schema error rather than returning an empty result.

Dashboard → **Settings → API → Exposed schemas**: add `facts` and `editorial`.

`supabase/config.toml` already declares both for the local stack, so
`supabase start` needs no equivalent step.

## 4. Confirm the roles

Supabase creates `anon`, `authenticated` and `service_role`. Migration 0004
grants select to the first two and nothing else. Confirm with:

```sql
select grantee, table_schema, table_name, privilege_type
from information_schema.role_table_grants
where grantee in ('anon','authenticated')
order by table_schema, table_name;
```

Every row should say `SELECT`. An `INSERT`, `UPDATE` or `DELETE` here means
something outside these migrations granted it.

## 5. Point the app at it

Copy the URL and anon key from Settings → API into `.env.local`:

```
NEXT_PUBLIC_SUPABASE_URL=https://<ref>.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=<anon key>
SUPABASE_SERVICE_ROLE_KEY=<service role key>
```

Only the anon key reaches the browser. The service role key bypasses RLS and
belongs to ingestion jobs and edge functions alone — never to anything under
`app/` or `components/`.

Then `npm run dev`. The pages should switch from "no database connected" to
empty lists, because the database is real and genuinely has nothing in it yet.

## 6. Set the same variables in Netlify

Site configuration → Environment variables. Set `NEXT_PUBLIC_SUPABASE_URL` and
`NEXT_PUBLIC_SUPABASE_ANON_KEY` for all contexts. Set
`SUPABASE_SERVICE_ROLE_KEY` only if a build-time or function path needs it;
the frontend does not.

## 7. Replace the hand-written types

`lib/types.ts` is maintained by hand and kept honest by the parity checks in
`tests/schema.test.ts`. Once the project exists, generate them instead:

```bash
supabase gen types typescript --linked --schema facts --schema editorial \
  > lib/database.types.ts
```

Then re-point `lib/types.ts` at the generated `Database` type and delete the
parity tests rather than maintaining them alongside a generator. Keep the
hand-written domain types (`SiteWithEvidence`, `CitationWithSource`,
`CaseStudyMetrics`) — those are application concepts, not table shapes.

## Verifying before you trust it

Run the behavioural tests against the real database rather than assuming the
push worked:

```bash
PGHOST=db.<ref>.supabase.co PGPORT=5432 PGUSER=postgres \
  TEST_DB=observatory_rls_test ./scripts/test-rls.sh
```

This creates and drops a throwaway database on the instance, so it does not
touch project data. If the connection is refused, use the pooler details from
Settings → Database instead.

## What is still missing after this

- **Point-in-time recovery** is a Pro feature. `docs/DEPLOYMENT.md` requires it.
- **Weekly export of content tables** to object storage is not automated.
- **The approved council list is still empty**, so no ingestion may run.
  Candidates are in `docs/COUNCIL_CANDIDATES.md` awaiting sign-off.
