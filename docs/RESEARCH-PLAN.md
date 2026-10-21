# RESEARCH-PLAN.md

How the open research questions get researched, answered, and turned into story
cards for the essays published as *We need to talk about data centres*.

Written: 2026-10-21. Status: proposed, awaiting the author's sign-off.
Owner: the author. Agents draft; the author decides what is published.

## Why

The essays explain to ordinary Australians how data centre deals work now: who
applies, who owns, who pays, who benefits, who gets heard and who gets told
nothing. The research agenda (`research_gaps` in `data-pipeline/`) holds the
questions that the public record has not yet answered. This plan works through
those questions in an order chosen for the essays. It leaves each answer in the
database, cited as any other fact. It also leaves a short story card of how the
answer was found, for the author to draw on.

At the time of writing the agenda holds 94 questions: 14 resolved, 16 in
progress and 64 open. This plan takes on 46 of the 80 that remain. The other 34
stay on the agenda, parked (see the last section).

## Decisions taken with the author (2026-10-21)

| Question | Decision |
| --- | --- |
| Which threads come first | **Money and incentives**, then **communities and sovereignty** |
| FOI requests, paid ASIC extracts, regulator requests | Agents draft them and rank the paid searches by what each would unlock. The author sets a budget and lodges or buys the top of the list |
| Where stories live | One Markdown card per story in `editorial/stories/`, merged through pull requests |
| Voice | **What you heard, set against the record.** Each card opens with what the public is told, then shows what the documents say |
| Shape | **The hunt is the story.** A card tells the search: the question, where we looked, what was refused or missing, and what turned up |
| Tone (2026-10-21, after the pilots) | **Drama, not mechanics.** Brush over the technical detail and give the drama; the detail stays in the hunt logs and the database |

## How one question becomes a story

1. **Triage.** Choose the cheapest route that can actually answer the question,
   in this order:
   - documents already archived;
   - free public records (planning portal attachments, the ASIC free company
     search, ABN Lookup, annual reports, registers, Hansard);
   - a paid extract;
   - an FOI or GIPA request.

   Record the route chosen and why.
2. **Hunt log.** Keep a dated log for the question at
   `data-pipeline/reports/hunts/RG-nnn.md`. It records:
   - every search and every fetch;
   - every refusal: a 401, a 403, a robots.txt exclusion, a paywall, a
     restricted attachment;
   - every document archived, with its SHA-256;
   - each dead end.

   Leads from search-engine summaries go in a separate section headed as leads.
   They are never facts. The log is raw material for the card, so it is kept as
   the work happens, not reconstructed afterwards.
3. **Answer.** Load what the documents establish through a curated pack:
   - sources graded A to D;
   - values quoted;
   - gaps flagged with `unknown` rather than filled.

   The question moves to `resolved` or stays `in_progress`, with notes saying
   what is done and what remains. This step follows every rule in `CLAUDE.md`.
   A value that needs a human judgement is listed for the author, not chosen.
4. **Card.** Write the story card from the hunt log and the loaded facts, in the
   format set out in `editorial/stories/README.md`.
5. **Review.** Each batch arrives as one pull request:
   - the packs;
   - the hunt logs;
   - the cards, all marked `status: draft`.

   The author reviews the cards against `docs/REVIEW.md` (content review),
   including the legal check for every named party, and approves a card by
   setting `approved_by` and `approved_at`. No agent sets either field.

## Rules for this work

- **Every factual sentence in a card cites a source** in the database by its id.
  A sentence that cannot be cited does not appear.
- **Leads are not facts.** Something only a search summary, a social post or an
  unarchived page says may appear in a card only as an open question ("we
  could not find a record that…"). It is never stated, even with a hedge.
- **Refusals are reported, never bypassed.** A restricted attachment, a
  robots.txt exclusion or a paywall is part of the story, and the request
  behind it goes on the FOI and paid-search list.
- **Community opposition is sourced only from planning, council or
  parliamentary records** (`docs/REVIEW.md`). Social media can point to where
  to look; it is never the source.
- **Named people appear only in public roles** documented by a primary record.
  Any card that names a person or implies wrongdoing is flagged in its front
  matter for the legal check.
- **Cards are drafts for the author, not final prose.** `docs/SUBAGENTS.md`
  limits the writer_support role to outlines and cited snippets, so the essays
  themselves stay the author's work.
- **Conflict of interest.** RG-012 concerns Anthropic, whose model drafts much
  of this research. Its hunt log and card carry a disclosure, and the author
  should review that question's sources directly.
- **Scope.** Council registers are read only for the approved councils in
  `docs/SPEC.md`. No new scrapers are built for this plan; documents are read
  one at a time.

## The story lines

Each story line groups questions that answer one thing a reader would ask. A
line may yield one card or several. The second column states the claim each
line tests. Each card replaces it with a cited quote of who said it, or opens
with the question if nobody public did.

### Thread M: money and incentives

| Line | What the line tests | Questions | Free route | Needs payment or FOI |
| --- | --- | --- | --- | --- |
| M1 Who is really applying? | That the company on the application is the company building, owning or using the data centre | RG-035, RG-055, RG-037, RG-036, RG-021, RG-052, RG-050, RG-059, RG-064, RG-081, RG-057 | Title documents attached to each application (they name the registered proprietor), the ASIC free company search (name, ACN, registration date, status), ABN Lookup | ASIC company extracts for directors, shareholders and ultimate holding company; GIPA request for Davis Road's restricted attachments (RG-057) |
| M2 Your super, your savings | That data centre money is foreign or private, not ordinary Australians' | RG-004, RG-094, RG-005 | Super funds' published portfolio holdings, annual reports, Future Fund periodic investment report files | NSW title search for 706-752 Mamre Road (RG-005) |
| M3 What the public gives | That data centres pay their own way | RG-007, RG-006, RG-025, RG-063, RG-043 | Budget papers, council planning agreement registers, the executed Penrith VPA, DPHI annual reports and estimates, AER determinations | FOI to Revenue NSW, SRO Victoria and QRO (RG-007); FOI to Treasury on FIRB decisions (RG-006) |
| M4 Who is in the room | That approvals follow the process, not access | RG-070, RG-067, RG-078, RG-077, RG-074 | NSW and Commonwealth lobbyist registers, NSW ministerial diaries, the Oxford Economics report's own disclosures, AusTender and buy.nsw | None expected. The BCA site refuses non-browser clients, so its roster may need a human download |
| M5 The OpenAI deal | What NEXTDC and OpenAI announced for S7 | RG-014 | NEXTDC ASX announcements and investor presentations | None expected |

### Thread C: communities and sovereignty

| Line | What the line tests | Questions | Free route | Needs payment or FOI |
| --- | --- | --- | --- | --- |
| C1 Who gets heard | That locals and councils have their say | RG-040, RG-066, RG-015, RG-041, RG-048, RG-056, RG-011, RG-016 | Submissions on the NSW Planning Portal, Senate and NSW Legislative Council inquiry submissions, Victorian Part 9A decisions, council registers for approved councils | None expected. The NSW inquiry pages refuse non-browser clients, so some downloads may need a human |
| C2 Did anyone check? | That consent conditions are enforced after approval | RG-058, RG-039, RG-069, RG-085 | Portal attachments, including the image-only donation disclosure on SSD-10330 (read locally), and operators' websites | GIPA to DPHI for the Roberts Road warning letter (RG-058); request to the IPC on who signed the Talavera Road consent (RG-085) |
| C3 Whose data, whose rules | That government data stays sovereign and its handling is visible | RG-092, RG-086, RG-095, RG-088, RG-093, RG-090, RG-087, RG-089, RG-012 | AusTender historical data, state tender portals, Coles' ASX releases, the GTC keynote recording, IRAP and HCF records | FOI to Defence and ASD on data location and clearances (RG-087, RG-089); FOI on law-enforcement use (RG-093) |

## The FOI and paid-search track

The requests live in `docs/requests/`, one file per request, with an index:

- the agency;
- the law it is made under;
- the fee;
- the questions it would answer;
- the cards it would unlock;
- its status: drafted, lodged, acknowledged, decided, received.

- **Paid searches** (ASIC extracts, NSW title searches) are listed in
  `docs/requests/PAID-SEARCHES.md`, ranked by what each would unlock. The
  price of each is confirmed from the provider's current fee schedule when
  the list is drafted. The author sets a budget and buys from the top.
- **NSW GIPA applications** carry a $30 application fee and a decision period
  of 20 working days. **Commonwealth FOI requests** carry no application fee
  but can attract processing charges, with a decision period of 30 days. Both
  can be extended, so returns are processed as they arrive, not batched.
- Documents that come back go into `data-pipeline/data/raw/` with a manifest,
  exactly like fetched ones. The response and any refusal reasons are logged
  in the question's hunt log, because a refusal is often the story.

## Batches

Each batch is one pull request: packs, hunt logs, cards, and any new request
drafts. A batch ends with the author's review, not with a merge by an agent.

| Batch | Contents | Expected output |
| --- | --- | --- |
| 0 Set-up and pilot *(in review)* | This plan; the card format; a checker that refuses a card citing a source id the pipeline does not hold; two pilot cards from hunts already finished | Pilots: *The article that wasn't there* (RG-100: four records cited an article whose archived version never mentions them) and *How big is S7?* (RG-099: NEXTDC S7's scoping report gives two totals, and a later attachment is restricted). The author confirms or adjusts the voice before anything else is written |
| 1 Who is really applying (M1) | Every free route for the eleven M1 questions, including incorporation dates for the applicants behind every determined NSW consent (RG-055) | Answers and cards, plus `PAID-SEARCHES.md` ranked and costed, and the GIPA draft for RG-057. Budget question to the author |
| 2 Your super and the OpenAI deal (M2, M5) | Holdings disclosures, Future Fund files, NEXTDC disclosures | Answers and cards; the Mamre Road title search added to the paid list |
| 3 What the public gives and who is in the room (M3, M4) | Planning agreements, the DPHI concierge, the grid-payment claim, lobbyist registers and diaries, research funding, consultancy overlap | Answers and cards; FOI drafts for RG-007 and RG-006 |
| 4 Whose data, whose rules (C3) | The keynote quote, the Palantir contract ledger, Coles, corporate customers, AUKUS on the public record | Answers and cards; FOI drafts for RG-087, RG-089 and RG-093; RG-012 with its disclosure |
| 5 Who gets heard and did anyone check (C1, C2) | Council and community submissions on the record, both inquiries, Victoria's Part 9A decisions, compliance and the donation disclosure | Answers and cards; GIPA drafts for RG-058 and RG-085 |
| Rolling | Returned FOI decisions and purchased extracts | Each processed as it arrives, its question and card updated in a small pull request |

## Tracking

- The research agenda in `data-pipeline/` is the record of each question's
  state. It is loaded to the site, so readers see progress on `/research`.
- This file's batch table is updated in each batch's pull request.
- `editorial/stories/README.md` keeps the index of cards with their status.
- `docs/requests/README.md` keeps the index of requests with their status.

## Parked, not dropped

These 34 questions stay on the agenda but are not scheduled by this plan.
Most can be picked up if an essay needs them.

- **Mapping the physical footprint:**
  - RG-001, 003, 013, 024, 027, 034, 051, 053, 071, 084, 091, 098;
  - plus RG-097, 099 and 100, which continue where earlier batches left
    them.
- **Power, water, diesel and the engineering critique:** RG-008, 010, 017, 018,
  019, 042, 044, 045, 054, 061, 062, 068, 075, 082.
- **The consultancy layer:** RG-072, 073, 076, 080, 083.
