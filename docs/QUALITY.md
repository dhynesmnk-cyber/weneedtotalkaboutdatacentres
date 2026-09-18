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
- Site status must be one of the six values in SPEC.md. Free text is rejected.

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

## Two layers of database testing
tests/schema.test.ts reads supabase/migrations as text and asserts that the
policies and constraints are declared. That catches a policy deleted or loosened
in a diff, but it proves nothing about behaviour: a policy can be declared and
still not do what it says.

supabase/tests/rls.test.sql is the behavioural evidence. It applies the
migrations to a real Postgres, seeds data as a superuser, then reads it back as
the anon role and asserts what the public API can and cannot see: proposed links
invisible, unapproved and future-dated editorial records invisible, every write
refused, every bad row rejected by a constraint. Run it with `npm run test:rls`
against any Postgres 14 or later; CI runs it on a postgres:16 service.

The suite is mutation tested. Loosening the links policy to `using (true)`,
granting anon an insert, or dropping the paired-coordinates constraint each make
it fail. A negative test that cannot fail is worth nothing, so if these are
changed, re-check that they still can.

## Audits
- Monthly sample audit: pick ten published claims, verify against sources.
- Record audit results and fix gaps found.
