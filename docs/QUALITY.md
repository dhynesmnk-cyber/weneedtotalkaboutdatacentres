# QUALITY.md

## Data quality
- Validation rules per field type (capacity numeric and positive, dates valid).
- A data_gaps row is required wherever a factual field is null, with a reason of
  unknown, not_disclosed, not_applicable or withheld. A null with no gap row is
  a data defect, not a gap.
- Gap reasons are never used to disguise an estimate. No value is inferred or
  interpolated to avoid recording a gap.
- Factual fields require at least one citations row. citations is the only
  mechanism; source_ids arrays do not exist.
- Deduplicate sites and entities on canonical name plus location.
- Canonical naming convention for operators, councils and entities.
- Site status must be one of the eleven values in SPEC.md. Free text is rejected.
- A value imported from the curation pipeline keeps its fact_status. A claimed
  record is never rendered as a verified one.
- Derived gaps use reason unknown and no stronger reason. not_disclosed and
  withheld are claims about the world: they need a human and a source, and are
  never inferred from a null.
- Council names are stored as their sources state them. Canonicalisation happens
  only through facts.lga_aliases, which records who approved each equivalence.

## Content quality
- Citation coverage measured per published record. Target one hundred percent
  for factual claims.
- Quarterly stale data review: reverify capacity, status and ownership.
- Correction log kept public for any post publish change.

## Code quality
- TypeScript strict, lint clean.
- Test coverage targets: ingestion parsers and financial calculations.
- Row Level Security tests for every public read path, in both the facts and
  editorial schemas.
- Tests assert the citations record_type check constraint, since a polymorphic
  record_id cannot be enforced by a foreign key.
- Tests assert that unconfirmed links are not publicly readable.

## Three layers of database testing
tests/schema.test.ts reads supabase/migrations as text and asserts that the
policies and constraints are declared. That catches a policy deleted or loosened
in a diff, but it proves nothing about behaviour: a policy can be declared and
still not do what it says.

supabase/tests/rls.test.sql is the behavioural evidence. It applies the
migrations to a real Postgres, seeds data as a superuser, then reads it back as
the anon role and asserts what the public API can and cannot see: proposed links
invisible, unapproved and future-dated editorial records invisible, every write
refused, every bad row rejected by a constraint. Run it with `npm run test:rls`
against any Postgres 14 or later; CI runs it on postgres:17 and postgres:16.

supabase/tests/load.test.sql is the third layer, run by `npm run test:load`.
It applies the migrations, generates the load artefact from the committed
pipeline database, applies it twice, and asserts what the anon role can see: all
93 sites readable, every one carrying a citation, every null explained by a gap,
no site holding a fabricated live capacity, every derived link still a proposal,
and no entity flagged major. Applying twice is what proves idempotence, which
cannot be tested any other way.

Both suites are mutation tested. Loosening the links policy to `using (true)`,
granting anon an insert, or dropping the paired-coordinates constraint each make
the RLS suite fail. Populating live_capacity_mw from it_capacity_mw, confirming
a link without a human, strengthening a derived gap reason, or deleting a
citation each make the load suite fail. A negative test that cannot fail is
worth nothing, so if these are changed, re-check that they still can.

## Audits
- Monthly sample audit: pick ten published claims, verify against sources.
- Record audit results and fix gaps found.
