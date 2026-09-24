# SUPABASE_SETUP.md

How to create the Supabase project, apply the schema, and load the research.

The migrations apply cleanly to real Postgres and the behavioural suites pass
against them, so the schema is known to work. Creating the project needs an
account and cannot be done from an agent session; applying the migrations and
loading the research can be, over the Management API, as described below.

This has been done once already — see Status. What follows is kept as the
procedure for rebuilding the project, or standing up a second one.

## Status

The project exists, all twelve migrations are applied, and the research is
loaded. Region `ap-southeast-2` (Sydney), Postgres 17. Steps 1-6 below are done;
what remains is listed under "What is still missing after this".

Verified as `anon` against the live database on 2026-09-21: 93 sites, 117
sources, 125 entities, 1885 data gaps, 0 sites with a live capacity, 0 visible
links, 0 uncited sites, 0 geocoded sites. PostgREST serves `facts` and
`editorial`, and an anon insert is refused with `42501`. As `service_role` the
same database shows the 58 proposed links that RLS hides from the public API —
the difference the weekly backup depends on.

Nothing in the app depends on a project existing: every page renders an explicit
"no database connected" state, and `npm run build` succeeds without
credentials.

There are **twelve** migrations. `0001`–`0004` create the two schemas, the ten
original tables and Row Level Security. `0005`–`0011` widen the schema to hold
the research in `data-pipeline/`: the extra site status values, the provenance
columns, the pipeline identity keys, the site fields, the research agenda, and
RLS for everything added. `0012` grants the service role select on both schemas,
without which ingestion jobs, edge functions and the weekly backup cannot read a
row. See `docs/PIPELINE_MAPPING.md` for why each exists.

`npm run test:load` proves end to end, on a throwaway Postgres and with no
Supabase project, that 93 sites, 125 entities and 117 sources land in this
schema correctly and that re-running the load changes nothing. That is the
check to run before loading anything into the hosted project, and it needs no
credentials.

CI runs both suites against Postgres 17 and 16 on every pull request, so the
version Supabase actually runs is covered rather than assumed.

The Supabase CLI is a devDependency, so `npx supabase ...` works without a
global install.

## Doing this from a Claude Code session

An agent session can only reach Supabase if the environment's network policy
allows it. By default `supabase.com` and `api.supabase.com` are blocked, and the
block is enforced by the proxy, so it cannot be worked around from inside a
session. Set both of the following on the environment at
https://claude.ai/code. **Neither takes effect until a new session starts**,
because the proxy configuration is fixed when the container boots.

1. **Network policy**: allow `api.supabase.com` and `supabase.com`, plus
   `<ref>.supabase.co` (PostgREST, which is what the app reads),
   `db.<ref>.supabase.co` and `aws-0-ap-southeast-2.pooler.supabase.com`.
2. **Access token**: `SUPABASE_ACCESS_TOKEN`, generated at
   https://supabase.com/dashboard/account/tokens.

### The constraint that is easy to miss

**The agent proxy carries HTTPS only.** `supabase db push` and `psql` speak the
Postgres wire protocol on port 5432 (6543 for the pooler), which is not HTTPS,
so opening the network policy may still not let a session connect to the
database directly.

**Confirmed on 2026-09-21, both halves.** `pg_isready` against
`db.<ref>.supabase.co:5432`, the pooler on `:6543` and the pooler on `:5432` all
report `no response`, so `psql` and `supabase db push` genuinely cannot run from
a session. The Management API over HTTPS
(`POST /v1/projects/{ref}/database/query`) does work, returns `201`, and carried
both the migrations and the load artefact — the whole 407 KB artefact in a
single request, in under seven seconds, so its transaction and its rollback
assertions stayed intact. Send the migrations one file per request, in order, so
that `0005` adds its enum values in a transaction of its own.

The Management API applies SQL outside the CLI's knowledge, so it leaves
`supabase_migrations.schema_migrations` empty and a later `supabase db push`
would try to re-apply everything. Backfill that table when you use this route;
it has been backfilled with `0001`-`0012`.

If the route ever stops working, fall back to running steps 2 and 6 from a local
clone — they are four commands — and let the session do the verification. Do not
spend an afternoon fighting the proxy over it.

### On the access token

A Supabase personal access token is **account wide**: it can create, modify and
delete projects across every organisation you belong to, and Supabase does not
offer a scoped-down variant. Set it as an environment secret rather than pasting
it into a conversation, so it does not end up in a transcript. Nothing in this
repository needs it at runtime — only the anon and service role keys do — so it
can be revoked once the project is stood up.

If you would rather not grant that, creating the project by hand and supplying
only the project URL and keys achieves the same result with far less exposure.

## 1. Create the project

At https://supabase.com/dashboard, create a project.

- **Region**: Sydney (`ap-southeast-2`). The audience and the data are
  Australian, and it keeps records onshore.
- **Plan**: the free tier is enough to start, but it has no point-in-time
  recovery. `docs/DEPLOYMENT.md` requires PITR, which needs Pro. Either upgrade
  before real data is loaded, or record the gap.
- Save the database password somewhere durable. It is shown once.

## 2. Apply the migrations

```bash
npx supabase login
npx supabase link --project-ref <your-project-ref>
npx supabase db push
```

`supabase db push` applies `supabase/migrations` in order. It should report
**twelve** migrations applied and no errors.

One thing not to worry about: `0005` adds values to the `site_status` enum, and
a new enum value cannot be used in the same transaction that adds it. No later
migration references those values — only the load artefact in step 6 does, and
that is a separate transaction — so the push is safe however it wraps them.

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

Supabase creates `anon`, `authenticated` and `service_role`. Migrations `0004`
and `0011` grant select to the first two and nothing else; `0012` grants select
to `service_role`, which is what the weekly backup reads with. Confirm the
public roles with:

```sql
select grantee, table_schema, table_name, privilege_type
from information_schema.role_table_grants
where grantee in ('anon','authenticated')
order by table_schema, table_name;
```

Every row should say `SELECT`. An `INSERT`, `UPDATE` or `DELETE` here means
something outside these migrations granted it. The same query with
`grantee = 'service_role'` should return 13 rows, all `SELECT`: that role
bypasses RLS, so the grant is the only thing limiting it.

## 5. Point the app at it

Copy the URL and keys from Settings → API into `.env.local`:

```
NEXT_PUBLIC_SUPABASE_URL=https://<ref>.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=<anon key>
SUPABASE_SERVICE_ROLE_KEY=<service role key>
```

Only the anon key reaches the browser. The service role key bypasses RLS and
belongs to ingestion jobs and edge functions alone — never to anything under
`app/` or `components/`.

At this point `npm run dev` shows empty lists rather than "no database
connected", because the database is real and genuinely has nothing in it yet.
Step 6 fixes that.

## 6. Load the research

The migrations create an empty schema. The research lives in `data-pipeline/`
and reaches Postgres as a reviewed SQL artefact — never by an agent writing
directly to the database.

```bash
# The direct connection string, from Settings → Database.
export DATABASE_URL="postgresql://postgres:<db-password>@db.<ref>.supabase.co:5432/postgres"

npm run load:pipeline                 # writes .artifacts/load-pipeline.sql
less .artifacts/load-pipeline.sql     # read it; this is the review step
psql "$DATABASE_URL" -v ON_ERROR_STOP=1 -f .artifacts/load-pipeline.sql
```

If the direct connection is refused, use the pooler details from
Settings → Database instead.

The artefact is transactional and ends with assertions that roll the whole load
back if any site arrives uncited, if any row carries a fabricated live capacity,
or if any link was confirmed without a named human. It is idempotent, so
applying it twice is safe — which is exactly what `npm run test:load` does to
prove it.

`npm run dev` should now show 93 sites on `/list`, each with its sources and a
gap badge stating why every empty field is empty.

### What stays empty on purpose

Three things will look broken and are not. Each is a human act the schema
deliberately refuses to perform on its own:

- **Linked entities is blank.** Every derived link loads as `proposed`, and the
  RLS policy in `0004` hides unconfirmed links from the public API. Derivation
  is not publication.
- **Entity profiles 404.** No entity carries `major_flag`, so nothing is
  profiled until someone decides which entities are prominent enough. See
  `docs/SPEC.md` "Entity profiles".
- **The map is empty.** No site in the research has coordinates, and the map
  says how many it could not place. Geocoding is curation work with a source per
  point, not something an importer may invent.

## 7. Set the same variables in Netlify

Site configuration → Environment variables. Set `NEXT_PUBLIC_SUPABASE_URL` and
`NEXT_PUBLIC_SUPABASE_ANON_KEY` for all contexts. Set
`SUPABASE_SERVICE_ROLE_KEY` only if a build-time or function path needs it; the
frontend does not.

## 8. Replace the hand-written types

`lib/types.ts` is maintained by hand and kept honest by the parity checks in
`tests/schema.test.ts`, which now understand `alter type ... add value` as well
as `create type`.

Generating them instead is the goal, but note before trying: `supabase gen
types --db-url` **requires a running Docker daemon**, which was verified by
attempting it. Whether `--linked` avoids that is untested. `npm run db:types`
currently passes `--local`, which needs Docker and a running local stack.

```bash
npx supabase gen types typescript --linked --schema facts --schema editorial \
  > lib/database.types.ts
```

If that works, re-point `lib/types.ts` at the generated `Database` type and
delete the parity tests rather than maintaining them alongside a generator. Keep
the hand-written domain types (`SiteWithEvidence`, `CitationWithSource`,
`CaseStudyMetrics`) — those are application concepts, not table shapes. If it
does not work, leave the hand-written types alone; they are tested and correct.

## Verifying before you trust it

Run the behavioural tests against the real database rather than assuming the
push worked:

```bash
PGHOST=db.<ref>.supabase.co PGPORT=5432 PGUSER=postgres \
  TEST_DB=observatory_rls_test ./scripts/test-rls.sh
```

This creates and drops a throwaway database on the instance, so it does not
touch project data.

Then confirm, as the anon role, that the public view is what it should be:

```sql
set role anon;
select count(*) from facts.sites;                          -- 93
select count(*) from facts.sites where live_capacity_mw is not null;  -- 0
select count(*) from facts.links;                          -- 0, all proposed
select count(*) from facts.sites s where not exists (
  select 1 from facts.citations c
   where c.record_type = 'sites' and c.record_id = s.id);  -- 0, every site cited
```

## What is still missing after this

- **Point-in-time recovery** is a Pro feature and is not enabled, at $100 a
  month on top of Pro. The gap is recorded in `docs/DEPLOYMENT.md` and
  mitigated by a weekly export; the recovery point objective is one week.
- **Weekly export** is automated in `.github/workflows/backup.yml`, with its
  two repository secrets set and a first run verified on 2026-09-21. It keeps
  90 days of artifacts on GitHub rather than object storage, so the backup and
  the code still share one provider.
- **The approved council list is still empty**, so no council ingestion may run.
  Candidates are in `docs/COUNCIL_CANDIDATES.md` awaiting sign-off.
- **Council name equivalences are approved and wired up** — five rows in
  `facts.lga_aliases` as of 2026-09-23, recorded in
  `docs/LGA_ALIAS_CANDIDATES.md`, resolved for display by `lib/councils.ts`.
  The list, the site record and the map popup all show the approved spelling;
  the record page also says what the source recorded. Stored values are
  unchanged.
- **Coordinates**, so the map stays empty. A human-curated
  `data-pipeline/data/inputs/site_coordinates.csv` with a method and source per
  row is the route; the slot exists and its column layout was corrected on
  2026-09-22. Geocoding itself is curation work with a source per point and
  cannot be automated away: an invented coordinate is a fabricated fact about
  where a data centre is.
