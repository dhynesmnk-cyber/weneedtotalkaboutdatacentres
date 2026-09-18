# QUALITY.md

## Data quality
- Validation rules per field type (capacity numeric and positive, dates valid).
- Gap flag required wherever a value is unknown.
- Factual fields require at least one source reference.
- Deduplicate sites and entities on canonical name plus location.
- Canonical naming convention for operators, councils and entities.

## Content quality
- Citation coverage measured per published record. Target one hundred percent
  for factual claims.
- Quarterly stale data review: reverify capacity, status and ownership.
- Correction log kept public for any post publish change.

## Code quality
- TypeScript strict, lint clean.
- Test coverage targets: ingestion parsers and financial calculations.
- Row Level Security tests for every public read path.

## Audits
- Monthly sample audit: pick ten published claims, verify against sources.
- Record audit results and fix gaps found.
