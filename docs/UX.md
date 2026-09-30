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
The repository contains documentation only. There is no application code yet:
no /app, /components, /lib, /supabase or /scripts directories exist. The UX
described below is the designed experience from SPEC.md and UI.md, evaluated
before any code is written. This is the cheapest possible moment to correct
course.

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
1. No orientation layer. A first-time resident lands on a timeline of events
   they have no context for. There is no "start here", no plain-language
   explainer of what an AI data centre actually consumes (power, water, land).
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
6. No comparison or aggregation views. Users cannot compare two sites, see
   totals ("how much committed capacity nationally"), or see a metric trend.
   Financial case studies exist per site but there is no rollup.
7. Data access friction for journalists. No CSV export, no per-record citation
   copy, no "download the dataset behind this chart".
8. Trust signals are invisible. The rigorous process (source panels, audits,
   correction log) is not surfaced as a story users can see and believe.
9. Accessibility spec is thin. WCAG 2.2 AA is named but no keyboard, screen
   reader or colour-blind behaviour is specified for the timeline and map,
   which are the hardest components to make accessible.
10. Mobile experience unaddressed. Residents on phones near a proposed site
    are the primary audience; no responsive or progressive-web-app behaviour
    is specified anywhere.

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
  database (sites tracked, total committed MW, events this quarter), each with
  a gap-aware footnote, plus a plain-language "What is an AI data centre?"
  explainer card (power, water, land, cooling, in numbers).
- Add "Check your area": suburb/LGA search that resolves to a results view
  (nearby sites, active planning events, linked council watchlist entries).
  Empty result is itself a message: "No tracked sites in your LGA yet, and
  here is how we would know if one appeared."
- Upgrade the map popup to include status, capacity with gap badge, and links
  to the site profile and any related essay.
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
- National rollups: aggregate capacity by status (proposed, under construction,
  live, stalled) and by state, each figure linking to the underlying rows.
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
- Five-minute comprehension: new visitors reach a site profile from home in
  two or fewer taps (instrument the click path).
- Return rate: subscribers to LGA alerts; monthly digest open rate.
- Depth: median session includes one essay and one data record (the core
  narrative loop working).
- Trust: one hundred percent citation coverage sustained; correction log
  entries resolved within seven days.
- Production health: essays shipped per quarter vs target; PSA triggers acted
  on within five working days of detection.

## Open questions for the team
- Is email the right v1 notification channel, or SMS given residents on-site?
- Who owns the monthly editorial calendar: single editor or rotating?
- Does the explainer content live in the database (as records) or as static
  pages? Recommendation: static pages for evergreen explainers, database for
  anything with a data-as-of date.
