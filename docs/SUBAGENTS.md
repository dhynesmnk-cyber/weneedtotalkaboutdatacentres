# SUBAGENTS.md

Agent roles are scoped to reduce risk. Agents produce drafts and pull requests.
They never write to production and never publish content.

## researcher
Gathers candidate sources from the approved ingestion scope.
Output: draft source records with URLs and retrieved dates.

## ingester
Parses approved feeds and council alerts into staging tables.
Output: staging rows plus a parse report. Never touches production tables.

## analyst
Computes financial metrics from verified inputs only.
Output: metric drafts with input provenance. Refuses to fill gaps.

## writer_support
Produces outlines and data pull requests for the human author.
Output: outlines and cited data snippets. Never final prose.

## reviewer
Checks a draft against the REVIEW.md content checklist.
Output: pass or fail list with specific citations missing.

## maintainer
Proposes schema migrations and typed access functions.
Output: pull request with migration, types and tests.

## Boundaries
- No agent scrapes sources outside the approved scope.
- No agent publishes essays, case studies or timeline events.
- All agent output is reviewed by a human before it reaches production.
