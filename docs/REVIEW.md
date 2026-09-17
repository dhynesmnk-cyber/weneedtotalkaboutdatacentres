# REVIEW.md

Two review tracks run in parallel. Both are mandatory before merge or publish.

## Content review (pre publish)
- Legal and defamation check for any named party.
- Every factual claim has a citation in the source panel.
- Gaps are flagged, not estimated.
- Fact and opinion are separated and labelled by placement.
- Publish date and data as of date are present.
- No fabricated numbers or inferred financials.
- Community opposition sourced only from planning or council records.

## Code review (pre merge)
- Migration present for any schema change.
- Types updated and strict mode clean.
- Tests added or updated for parsers and financial calculations.
- Row Level Security verified for public read paths.
- No secrets in repo or logs.
- Docs updated if behaviour changed.

## Cadence
- Content review on every publish.
- Code review on every pull request.
- Quarterly review of this document set against the live codebase (first week of January, April, July, October).
