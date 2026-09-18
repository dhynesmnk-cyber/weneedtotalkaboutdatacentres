# weneedtotalkaboutdatacentres

Australian AI Data Centre Observatory: a public record of Australian AI data
centre sites, the entities behind them, and what is known and not known about
each — plus a separate editorial layer of video essays and analysis.

The governing principle is that a missing value is a finding, not a blank. Every
factual claim references a source record, and every gap states why it is a gap.

## Getting started

```bash
npm install
cp .env.example .env.local   # fill in once a Supabase project exists
npm run dev
```

The app runs without a database and says so. Pages render an explicit "no
database connected" state rather than sample data, because placeholder figures
in an observatory about data centre capacity could be mistaken for findings.

## Commands

| Command | Does |
| --- | --- |
| `npm run dev` | Development server |
| `npm run build` | Production build (needs no credentials) |
| `npm run lint` | ESLint |
| `npm run typecheck` | `tsc --noEmit` |
| `npm test` | Unit tests (vitest) |

## Layout

- `app/` — pages. Timeline, essay hub, map, list, and the four record pages.
- `components/` — the six components specified in `docs/UI.md`, plus empty states.
- `lib/` — typed data access. Components never query Supabase directly; an
  ESLint rule enforces it.
- `supabase/migrations/` — schema. Two Postgres schemas, `facts` and
  `editorial`, with RLS on every table.
- `scripts/ingestion/` — parsers for manually collected exports. Pure functions,
  no network access.
- `tests/` — unit tests for the financial calculations, the ingestion parser,
  formatting, evidence resolution, and migration/type parity.
- `docs/` — specification and process. Start with `docs/SPEC.md`.

## Before changing anything

Read `CLAUDE.md`. It carries the hard rules, and several of them are enforced in
the database rather than the application: unconfirmed links and unapproved
editorial records are invisible to the public API by policy, not by filtering.
