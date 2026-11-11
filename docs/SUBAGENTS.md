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
Drafts essays, the position and proposals in full, as Markdown in
editorial/essays/, from the story cards, every factual sentence cited.
Output: a draft file through a pull request, passing `npm run check:essays`.
Never approves, never sets approval fields, never holds the editor's session.
The editor edits and approves at /admin (docs/UX-PLAN.md, decision 6).

## reviewer
Checks a draft against the REVIEW.md content checklist, running
`npm run check:essays` for the mechanical part.
Output: pass or fail list with specific citations missing.

## maintainer
Proposes schema migrations and typed access functions.
Output: pull request with migration, types and tests.

## Boundaries
- No agent scrapes sources outside the approved scope.
- No agent publishes essays, case studies or timeline events. Approval is a
  database function that takes the approver from the signed-in editor's
  session; no agent holds that session.
- All agent output is reviewed by a human before it reaches production.
