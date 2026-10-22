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
The search told as a story: what was at stake, the turns, the dead ends, the
reveal. Plain English, past tense, 150 to 300 words. Brush over the mechanics:
no page numbers, error codes, file names or technical units. Every factual
sentence still ends with its source id in square brackets, like this
[SRC_HCF_REGISTER].

## What the record shows
Three to five plain statements, each cited, each one a reader could check.

## Still unknown
What remains open, by question id, and what it would take to find out: a
named FOI request, a paid extract, a document a human must download.

## Essay hooks
Suggested angles for the author. Labelled as suggestions; they state no facts.
```

## Rules

- **Drama, not mechanics.** Give the reader the stakes and the turns, not the
  method. Page numbers, HTTP error codes, robots.txt, file formats, checksums
  and engineering units stay in the hunt log and the database, where the
  citations lead. Say "locked" rather than "401", "a sign telling automated
  readers to keep out" rather than "robots.txt". The checker flags these terms.
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
| [ST-002](ST-002-how-big-is-s7.md) | How big is S7? | M5 | RG-099 | draft |
| [ST-003](ST-003-the-client-who-cant-be-named.md) | The client who can't be named | M1 | RG-055, RG-064, RG-098 | draft |
| [ST-004](ST-004-four-letters.md) | Four letters | M1 | RG-021, RG-036, RG-005 | draft |
| [ST-005](ST-005-the-name-on-the-land.md) | The name on the land | M1 | RG-057, RG-023 | draft |
| [ST-006](ST-006-seventeen-days.md) | Seventeen days | M1 | RG-052, RG-050 | draft |
| [ST-007](ST-007-already-in-your-super.md) | Already in your super | M2 | RG-004, RG-094, RG-005 | draft |
| [ST-008](ST-008-not-mentioned-once.md) | Not mentioned once | M5 | RG-014 | draft |
