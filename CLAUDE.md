# CLAUDE.md

Project: Australian AI Data Centre Observatory (working title)
Purpose: single source of truth for AI coding agents working in this repo.
Last reviewed: 2026-09-18
Next review: 2026-10-01

## Project summary
Public data observatory tracking Australian AI data centres, plus a separate
editorial layer of video essays and analysis. Core narrative: public perception
versus research data.

## Hard rules
- The database is the source of truth. The frontend never stores business data.
- Use PostgreSQL via Supabase. Do not introduce a second database.
- Do not build scrapers for all Australian councils. Only the approved council
  list in docs/SPEC.md.
- Do not build GIS overlays in v1. Point map only.
- Every factual claim in published content must reference a source record.
- Mark missing data explicitly with a gap flag. Never infer or fabricate values.
- Keep the fact layer and the editorial layer separate in data and in UI.
- No agent publishes content. Humans approve publication.

## Tech stack
- Frontend: Next.js App Router, TypeScript, Tailwind.
- Backend and data: Supabase (Postgres, Auth, Storage). Public read via Row Level Security.
- Maps: Leaflet, single point layer for v1. Rationale in docs/UI.md.
- Video: YouTube embeds. Essays stored as records with metadata.
- Ingestion: scheduled jobs (Supabase Edge Functions or GitHub Actions) for approved sources only.

## Repo layout
/app        public pages
/components UI components
/lib        typed data access and domain logic
/supabase   migrations and edge functions
/scripts    ingestion jobs
/docs       specs and process documents
/tests      unit tests (vitest)

## Conventions
- TypeScript strict mode.
- All database access through typed functions in /lib. No raw SQL in components.
- Schema changes only via supabase migrations. Never manual edits.
- Unit tests required for ingestion parsers and financial calculations.
- Australian English in all user facing strings and documentation.

## Key documents
docs/SPEC.md        product scope and data model
docs/COUNCIL_CANDIDATES.md  unapproved council candidates, pending sign-off
docs/UI.md          design system and page specs
docs/REVIEW.md      editorial and code review checklists
docs/SUBAGENTS.md   agent roles and boundaries
docs/DEPLOYMENT.md  release, infrastructure, backups
docs/QUALITY.md     data and content quality assurance

## Definition of done
A change is done when migrations are applied, types are updated, tests pass,
docs are updated if behaviour changed, and no fabricated data was introduced.
