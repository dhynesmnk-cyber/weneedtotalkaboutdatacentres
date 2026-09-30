# UX.md

## Purpose
Describe the current user experience of the observatory as designed by SPEC.md
and UI.md, identify where it falls short on engagement and informativeness, and
set out a prioritised plan to fix it. This document does not change the hard
rules in CLAUDE.md: the database remains the source of truth, gaps are flagged
never guessed, fact stays separate from opinion, and humans approve publication.

## Audience recap (from SPEC.md)
- Local residents near proposed or operating sites.
- Journalists covering planning, energy and investment.
These two groups read very differently. Residents arrive with one question
("what is happening near me and should I care?"). Journalists arrive with data
literacy and need provenance and export. The current design serves both but
delights neither.

---

## Current state assessment

### What exists today
This assessment was first written on the scaffold branch, when the repository
held documentation only. It has since been checked against `main` as of
2026-09-30 (PR #14, `ed5dd2f`), which already has:

- The Next.js app: home, how to read this site, essay hub, map, list, coverage
  ("What's known"), and the site, entity, case study and essay record pages.
- A hosted Supabase database with the curation pipeline loaded: 93 sites, 117
  sources, 125 entities, every site cited, no invented live capacity.
- A home page that introduces the two layers, reads findings off the record,
  and shows how complete the record is (StatTile, StatusBreakdown), then the
  timeline.
- Map points for the 46 NSW State Significant Development sites, placed from
  the planning portal's own records. The rest have no coordinates yet, and the
  map says how many it could not place.
- Map popups with status and capacity, each with a gap badge, linking to the
  site profile.
- An explicit "no database connected" state instead of sample data.
- `npm run test:ui`: every page checked in a browser with axe for WCAG 2.2 AA
  at desktop and phone widths.

Weaknesses below that `main` has already closed or narrowed are marked as
such. The rest stand.

### Designed entry points (priority order per SPEC.md)
1. Timeline with six combinable event tracks.
2. Essay hub, date ordered, YouTube embeds plus written analysis.
3. Point map with site popups.
4. Sortable list of sites and entities.

### Strengths of the current design
- Evidence discipline is exceptional. Citations, gap badges, dated records and
  a public correction log build trust that most civic data sites lack.
- Fact versus opinion separation is a genuine differentiator for a contested
  topic.
- The links table (auto many-to-many between sites, entities and events) gives
  every record a natural web of related context. This is underused in the page
  specs.
- Clear agent boundaries mean editorial output cannot be silently fabricated.

### Weaknesses and gaps
1. No orientation layer. *Narrowed on `main`:* the home page now opens with
   what the site does and the two ways to read it, and /how-to-read explains
   evidence levels, gap reasons and dates. Still missing: a plain-language
   explainer of what an AI data centre consumes (power, water, land).
2. No place-based entry. Residents think in suburbs and LGAs, not in site IDs.
   The map is priority 3 and has no search-by-suburb or postcode specified.
3. Passive consumption only. Everything is browse-and-read. No subscriptions,
   no alerts, no way to be told when something changes near you. For a
   planning-approval story, timeliness is the whole value proposition.
4. Timeline scale problem. Six tracks over years of national activity will
   either overwhelm or look empty at launch. No density control, no "what
   changed this month" summary.
5. Essays are isolated islands. The essay page lists related sites and events,
   but nothing brings readers back into the data, and nothing brings data
   users into the essays. The core narrative (perception versus research) is
   asserted but not staged as an experience.
6. No comparison or aggregation views. Users cannot compare two sites or see a
   metric trend. Financial case studies exist per site but there is no rollup.
   Any capacity total must respect docs/PIPELINE_MAPPING.md: the four capacity
   figures measure different things and are never added to one another, so a
   total is always of one named figure, over the sites that report it, with
   the count that do not stated beside it.
7. Data access friction for journalists. No CSV export, no per-record citation
   copy, no "download the dataset behind this chart".
8. Trust signals are invisible. *Narrowed on `main`:* /how-to-read and the
   "What's known" coverage page surface evidence levels and gaps. The
   methodology and the correction log are still not public pages.
9. Accessibility spec is thin. *Narrowed on `main`:* axe checks every page
   for WCAG 2.2 AA in `test:ui`. Keyboard, screen reader and colour-blind
   behaviour for the timeline and map is still unspecified beyond that.
10. Mobile experience underspecified. `test:ui` checks every page at phone
    width, but residents on phones near a proposed site are the primary
    audience, and no mobile behaviour for the timeline and map is specified.

---

## Target experience principles
1. Answer the visitor's first question before showing them any data:
   "what is happening, where, and why should I care?"
2. Every number on screen is one tap from its source and its as-of date.
3. Make the absence of data as informative as the presence of it (gap counts
   become a credibility feature: "we track X, we know Y, we are missing Z").
4. Perception versus research must be a felt contrast, not a stated theme.
   Show the claim, then show the record.
5. Give returning users a reason to come back monthly (new events, changed
   statuses, new essays), and give first-time users a five-minute path to
   understanding.
6. Editorial depth without sacrificing rigor: essays and PSAs follow a fixed,
   repeatable pipeline (see below) so quality does not depend on mood.

---

## Prioritised improvement plan

### Phase 1: Orientation and place (launch blockers)
- Add a Home briefing block above the fold: three live stats drawn from the
  database (sites tracked, one named capacity figure over the sites that report
  it, events this quarter), each with a gap-aware footnote, plus a plain-language "What is an AI data centre?"
  explainer card (power, water, land, cooling, in numbers).
- Add "Check your area": suburb/LGA search that resolves to a results view
  (nearby sites, active planning events, linked council watchlist entries).
  Empty result is itself a message: "No tracked sites in your LGA yet, and
  here is how we would know if one appeared."
- Map popup: status, capacity with gap badge and a site profile link are done
  on `main`. Still to add: a link to any related essay.
- Add a "This month in data centres" digest page, generated from the events
  table, published monthly. Doubles as the subscription payload.

### Phase 2: Engagement loops
- Subscribe layer: email notifications per saved LGA/site/entity via Supabase
  Auth plus an Edge Function. Explicit consent, Australian privacy statement.
- Timeline density control: default to a rolling 12-month window with a
  significance filter (major entities and major projects first), plus a
  per-month sparkline so sparse months and surge months are both readable.
- Site comparison: select up to three sites, side-by-side metrics with gap
  badges shown for unknowns rather than hidden.
- Cross-linking everywhere: every site profile shows essays citing it; every
  essay shows the exact records its claims rest on (via the citations table),
  turning reading into browsing and browsing into reading.
- Public methodology page: how ingestion works, the approved council list,
  audit cadence, and the correction log rendered visibly. Trust as content.

### Phase 3: Informativeness and data utility
- National rollups: capacity by status (proposed, under construction,
  operating, stalled) and by state, one capacity figure at a time and never
  combined across figures, each total stating how many sites it covers and
  how many lack the figure, and linking to the underlying rows.
- Journalist toolkit: CSV export per table view, "cite this record" snippet
  with URL and data-as-of date, stable deep links for every record.
- Status change history on site profiles (derived from events), so "stalled"
  is shown as a dated transition, not an assertion.
- Glossary tooltips for technical terms (MW, cap rate, rack density) tied to
  the explainer content.

### Phase 4: Experience polish
- Responsive-first redesign of timeline and map for mobile; list fallbacks
  for both (already required by UI.md accessibility, now specified per page).
- Reduced-motion compliant transitions; colour-blind-safe track palette.
- Loading and empty states designed per component (a sparse launch dataset
  must look intentional, not broken: lean on gap messaging).

---

## Content production process: essays

A fixed pipeline that fits inside the SUBAGENTS.md boundaries (agents draft,
humans write and publish).

1. Framing brief (human editor). One sentence argument, target perception
   claim to test, audience (resident or journalist), word budget, publication
   slot. Rejected if no falsifiable angle.
2. Evidence pull (researcher + analyst agents). Query the database for the
   relevant sites, events and financials; produce a cited data pack. Any
   missing value arrives as a gap flag, never an estimate.
3. Outline (writer_support agent) against the brief; human author approves or
   restructures.
4. Draft (human author). Structure is fixed: the common perception, what the
   records show, where the data is too thin to answer, what to watch next.
   Opinion appears only after a FactOpinionDivider.
5. Internal review (reviewer agent) against REVIEW.md content checklist:
   citation coverage, gap flags, dates, defamation check on named parties.
6. Human editorial pass and legal sign-off for any named entity.
7. Publish: essay record with youtube_id if a video exists, body, tags,
   related_ids auto-populated from cited records; SourcePanel rendered from
   citations; DateStamp with publish and data-as-of dates.
8. Post-publish: any correction goes to the public correction log; quarterly
   reverification re-checks the numbers the essay leans on.

Cadence target: one essay per month. Every essay must cite at least five
database records, otherwise it is commentary and gets labelled as such.

## Content production process: PSAs

Public service announcements are short, action-oriented notices (e.g. "your
council exhibition period ends 14 November", "how to make a submission").
They are advisory, not advocacy: they tell people how the system works, not
what to conclude.

Rules specific to PSAs:
- Only trigger a PSA from a dated record: a planning event, a council
  watchlist item, or a case study finding. No free-floating advice.
- Template family with four slots: situation, who it affects, what you can do
  (with the official government/council channel, never our own commentary on
  merits), deadline with source link.
- Tone reviewed by a human; no named-party claims, so defamation risk stays
  minimal by design.
- Distribution: digest email, site banner on affected LGA pages, and a share
  card image generated from the record.

Pipeline:
1. Trigger detection during monthly ingest review (ingester output report).
2. Editor confirms trigger meets the dated-record rule.
3. writer_support drafts from the template with fields filled from the
   record; reviewer agent checks checklist.
4. Human approval, then publish with expiry date. Expired PSAs archive
   automatically rather than linger.

---

## Success measures
- Five-minute comprehension (usability tests): new visitors reach a site profile from home in
  two or fewer taps (instrument the click path).
- Return rate: subscribers to LGA alerts, and how many stay subscribed (no
  open tracking).
- Depth: median session includes one essay and one data record (the core
  narrative loop working).
- Trust: one hundred percent citation coverage sustained; correction log
  entries resolved within seven days.
- Production health: essays shipped per quarter vs target; PSA triggers acted
  on within five working days of detection.

## Settled questions
Settled on 2026-09-30; the decisions and their consequences are in
docs/UX-PLAN.md under "Scope decisions".
- Notification channel: email only in v1.
- Editorial calendar: David, as single editor.
- Explainer: a static page for evergreen prose, with every dated figure read
  from the database with its citation.
- Analytics: Netlify Analytics, so behaviour is measured in usability tests.
