# Essay drafts

Drafts of the essays, the "Where we stand" position and the "What if…?"
proposals, written as Markdown so they can be reviewed in a pull request like
any other change. A draft here is not published and cannot publish itself.

How a draft reaches readers:

1. An agent (or anyone) writes `ES-nnn-slug.md` here, from the story cards in
   `editorial/stories/`, and opens a pull request.
2. `npm run check:essays` runs the rules below. CI runs them too.
3. After merge, `npm run load:essays` writes `.artifacts/load-essays.sql`. A
   person reviews it and applies it, after the research pipeline load
   (docs/SUPABASE_SETUP.md). The draft appears, unapproved, at `/admin`.
4. The editor reads it beside a preview of the page, edits it there if need be,
   and approves it. Only the editor can approve, and the database records who
   did and which text they approved.

Once the editor has edited or approved a piece in `/admin`, the database holds
the text that matters. A later change to the file here is the agent's proposal:
the loader reports it and leaves the piece alone. The file stays as the record
of what the agent first proposed, and `/admin` keeps every later version.

## Format

```markdown
---
id: ES-001
slug: six-in-seven
kind: essay                 # essay | position | proposal
title: Six in seven
standfirst: One or two sentences saying what the piece argues.
story_cards: [ST-011]
questions: [RG-078, RG-070]
sources: [SRC_NSWGUIDE26, SRC_OXEC_PHANTOM_2025]
data_as_of: 2026-10-22      # when the records it relies on were current
named_parties: ["Secretary, NSW Premier's Department (by role)"]
conflict: null              # a disclosure shown above the text, or null
tags: [phantom demand]
youtube_id: null
proposal_no: null           # 1 to 9 for a proposal, otherwise null
status: draft               # always draft; the editor approves in /admin
---
```

`approved_by`, `approved_at` and `publish_date` may not appear: the editor sets
them, in `/admin`, and nowhere else.

### Sections

An essay has exactly these, in order (docs/UX.md):

1. `## The common perception`: the claim as the public meets it, quoted from
   whoever made it.
2. `## What the records show`
3. `## Where the data is too thin`: open questions, cited by id.
4. `## What to watch next`
5. `## Our view`: the argument. The divider is drawn above this heading, and
   the page colours everything after it as editorial.

A proposal: `## Australia’s rules now`, `## Elsewhere`, `## What it would
take`, `## Our proposal`. A position: any cited sections, ending with
`## Our view`.

### Citations and callouts

- `[SRC_ID]` cites a source the research database holds. It renders as a
  numbered superscript that links to the source panel, numbered in the order
  the text first cites each source.
- `[RG-070]` points at an open research question, linking to it.
- `> [!PULLQUOTE]` on the first line of a block quote makes a pull quote.
- `> [!FIGURE] 6 in 7` makes a figure: the value on the first line, the cited
  caption below.

## Rules

`lib/editorial/rules.ts`, run by `npm run check:essays`, by the loader, and live
beside the editor in `/admin`:

- Every paragraph before the opinion section cites a source or an open
  question.
- Every sentence that states a number cites it, opinion included.
- An essay or proposal cites at least five distinct sources; below that it is
  commentary (docs/UX.md). The database enforces this again at approval.
- Every cited id exists, and `sources` in the front matter lists exactly the
  sources the text cites.
- A piece touching Anthropic, which makes the model that drafts these essays,
  carries a conflict disclosure.
- No personal name the research holds appears in the text. People are referred
  to by their public role until legal review is arranged
  (docs/DELIVERY-PLAN.md, decision 7), and each is listed in `named_parties`,
  which makes the editor confirm the legal check before approving.
- Mechanics (file formats, error codes, page numbers) draw a note, not an
  error: a general reader rarely needs them.

The checks cannot tell a fact from a lead or judge an argument. That is the
editor's reading, against the checklist in docs/REVIEW.md.

## Index

| Draft | Title | Kind | Story cards | Status |
| --- | --- | --- | --- | --- |
| [ES-000](ES-000-where-we-stand.md) | Where we stand | position | ST-007, ST-011 | draft |
| [ES-001](ES-001-six-in-seven.md) | Six in seven | essay | ST-011 | draft |
