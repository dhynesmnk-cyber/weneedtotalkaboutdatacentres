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
- People named only by public role, each listed in named_parties, until legal
  review is arranged.
- A piece touching Anthropic carries the conflict disclosure, and its sources
  were read directly, not through the draft.
- `npm run check:essays` passes; the preview at /admin was read in full.

## Code review (pre merge)
- Migration present for any schema change.
- Types updated and strict mode clean.
- Tests added or updated for parsers and financial calculations.
- Row Level Security verified for public read paths.
- No secrets in repo or logs.
- Nothing under app/ uses the service role key; /admin pages check
  currentEditor() and every editorial write path has an RLS test.
- Docs updated if behaviour changed.

## Cadence
- Content review on every publish.
- Code review on every pull request.
- Quarterly review of this document set against the live codebase (first week of January, April, July, October).
