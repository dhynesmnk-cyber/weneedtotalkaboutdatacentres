# Story cards

Short, cited accounts of how a research question was answered, written as raw
material for the essays in *We need to talk about data centres*. The plan that
produces them is `docs/RESEARCH-PLAN.md`.

A card is part of the editorial layer. It holds no data of its own: every fact
in it is a record in the research database, cited by its source id. A card is a
draft for the author until the author approves it. No agent approves a card or
publishes one.

## Format

One file per card, named `ST-nnn-short-slug.md`, numbered in the order written.

```markdown
---
id: ST-001
title: The article that wasn't there
thread: communities-sovereignty      # money | communities-sovereignty
story_line: C3                       # from docs/RESEARCH-PLAN.md
questions: [RG-100]                  # research questions it draws on
sources: [SRC_CERTSTRAT, SRC_HCF_REGISTER]
data_as_of: 2026-10-21               # when the underlying records were current
named_parties: []                    # people named; any entry means a legal check
conflict: null                       # a disclosure, where one applies
status: draft                        # draft | approved | withdrawn
approved_by: null                    # set by the author, never by an agent
approved_at: null
---

## What you heard
The claim as the public meets it, quoted from whoever made it, with its source.
If nobody public has said it, open with the question instead.

## The hunt
The search as it happened: the question, where we looked, what was refused,
restricted or missing, and what turned up. Plain English, past tense, 200 to
400 words. Every factual sentence ends with its source id in square brackets,
like this [SRC_HCF_REGISTER].

## What the record shows
Three to five plain statements, each cited, each one a reader could check.

## Still unknown
What remains open, by question id, and what it would take to find out: a
named FOI request, a paid extract, a document a human must download.

## Essay hooks
Suggested angles for the author. Labelled as suggestions; they state no facts.
```

## Rules

- **Citations.** A factual sentence cites at least one source id the research
  database holds. A card citing an id the database does not hold fails review.
- **Leads.** A claim found only in a search summary, a social post or an
  unarchived page appears only as an open question, never as a statement.
- **Refusals.** A 401, a 403, a robots.txt exclusion, a paywall or a restricted
  attachment is reported as found. It is never worked around.
- **Community opposition** comes only from planning, council or parliamentary
  records.
- **People** appear only in public roles shown by a primary record. List every
  person named in `named_parties`, so the legal check in `docs/REVIEW.md`
  cannot be skipped.
- **Fact and comment** stay apart by placement: comment belongs only under
  *Essay hooks*.
- **Australian English**, written for a reader who has never opened a planning
  document. Explain an acronym the first time it appears.

## Index

| Card | Title | Line | Questions | Status |
| --- | --- | --- | --- | --- |
| [ST-001](ST-001-the-article-that-wasnt-there.md) | The article that wasn't there | C3 | RG-100, RG-096 | draft |
| [ST-002](ST-002-612-or-700.md) | 612 or 700? | M5 | RG-099 | draft |
