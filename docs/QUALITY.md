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

## Audits
- Monthly sample audit: pick ten published claims, verify against sources.
- Record audit results and fix gaps found.
