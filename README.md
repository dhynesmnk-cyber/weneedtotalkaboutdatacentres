# weneedtotalkaboutdatacentres

Australian AI Data Centre Observatory: a public record of Australian AI data
centre sites, the entities behind them, and what is known and not known about
each — plus a separate editorial layer of video essays and analysis.

The governing principle is that a missing value is a finding, not a blank. Every
factual claim references a source record, and every gap states why it is a gap.

## Getting started

```bash
npm install
cp .env.example .env.local   # keys from Supabase → Settings → API
npm run dev
```

The app runs without a database and says so. Pages render an explicit "no
database connected" state rather than sample data, because placeholder figures
in an observatory about data centre capacity could be mistaken for findings.

The hosted database is up. The Supabase project is in Sydney
(`ap-southeast-2`), all eleven migrations are applied, and the research from
`data-pipeline/` is loaded: 93 sites, 117 sources, 125 entities, every site
cited and no site carrying an invented live capacity. Fill in `.env.local` and
the pages show real records. See `docs/SUPABASE_SETUP.md` for how it was stood
up and what remains.

`npm run test:load` still proves the same load end to end on a throwaway
Postgres with no Supabase project required, which is the check to run before
loading a correction.

No site has coordinates yet, so the map stays empty and says how many sites it
could not place. Geocoding them is human curation work with a source per point,
not something an importer may invent. Linked entities are blank and entity
profiles 404 for the same reason: every derived link loads as `proposed` and RLS
hides it, and no entity is flagged as major until a human decides it is.

## Commands

| Command | Does |
| --- | --- |
| `npm run dev` | Development server |
| `npm run build` | Production build (needs no credentials) |
| `npm run lint` | ESLint |
| `npm run typecheck` | `tsc --noEmit` |
| `npm test` | Unit tests (vitest) |
| `npm run test:rls` | Live RLS and constraint tests against a real Postgres |
| `npm run test:load` | Loads the research pipeline into a throwaway Postgres, twice, and asserts what a reader would see |
| `npm run load:pipeline` | Emits the load artefact from `data-pipeline/` for review |
| `npm run db:types` | Regenerate database types from the local Supabase stack |

## Layout

- `app/` — pages. Timeline, essay hub, map, list, and the four record pages.
- `components/` — the six components specified in `docs/UI.md`, plus empty states.
- `lib/` — typed data access. Components never query Supabase directly; an
  ESLint rule enforces it.
- `supabase/migrations/` — schema. Two Postgres schemas, `facts` and
  `editorial`, with RLS on every table.
- `scripts/ingestion/` — parsers for manually collected exports, and the loader
  that brings `data-pipeline/` into Postgres. Pure functions, no network access.
- `lib/ingestion/` — the vocabulary map, the row transforms and the SQL emitter.
  Every reconciliation decision lives here and is argued in
  `docs/PIPELINE_MAPPING.md`.
- `data-pipeline/` — the upstream curation tool (Python, SQLite): 93 sites, 125
  entities and 117 sources, every row graded and sourced. The app never reads
  it; it reaches Postgres through a reviewed SQL artefact.
- `tests/` — unit tests for the financial calculations, the ingestion parser,
  formatting, evidence resolution, and migration/type parity.
- `docs/` — specification and process. Start with `docs/SPEC.md`.

## Before changing anything

Read `CLAUDE.md`. It carries the hard rules, and several of them are enforced in
the database rather than the application: unconfirmed links and unapproved
editorial records are invisible to the public API by policy, not by filtering.
