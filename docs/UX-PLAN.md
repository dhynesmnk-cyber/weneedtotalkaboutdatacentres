# UX-PLAN.md

## Purpose
Execution plan to optimise the user experience of the Australian AI Data
Centre Observatory. This converts the assessment and improvement ideas in
docs/UX.md into a sequenced, verifiable program of work with owners, acceptance
criteria, measurement gates and explicit UX-relevant schema/migration items.

This plan does not change any hard rules from CLAUDE.md:
- The database remains the source of truth; the frontend never stores business data.
- Gaps are flagged, never guessed or inferred.
- Fact layer and editorial layer stay separate in data and UI.
- No agent publishes content; humans approve publication.
- Maps stay point-only in v1; council coverage stays within the approved list.

Related documents: SPEC.md (scope/data model), UI.md (design system/pages),
UX.md (assessment and rationale), REVIEW.md and QUALITY.md (checklists),
SUBAGENTS.md (agent boundaries), DEPLOYMENT.md.

## Status against `main` (checked 2026-09-30)
This plan was drafted on the scaffold branch before the app existed. Checked
against `main` at `ed5dd2f`:

| Item | State on `main` |
|---|---|
| Trust primitives (SourcePanel, GapBadge, DateStamp, FactOpinionDivider) | Built, in `components/`. Extend, do not re-create. |
| StatCard | Exists as `StatTile`. Add the as-of date and gap footnote there. |
| A1 home briefing | Partly done: home shows sites tracked, how complete the record is, and status counts. |
| A2 explainer | Not started. /how-to-read covers how to read the record, not what a data centre consumes. |
| B3 map popup | Done apart from the related-essay link. |
| F3 missing data | Largely done by /how-to-read and /coverage. |
| G3 empty states | Done for "no database connected" and the unplaced map points. |
| G5 axe in CI | Done: `npm run test:ui` checks every page for WCAG 2.2 AA at desktop and phone widths. Manual screen-reader pass still to do. |
| Everything else | Not started. |

The scaffold branch also carried a prototype app (`lib/sample-data.ts`,
`components/blocks/`, `components/primitives/`). It is **not** adopted. Its
sample data conflicts with the rule that pages show an explicit "no database
connected" state rather than placeholder figures, and its components duplicate
ones already on `main`. `AreaSearch` and `ClaimVsRecord` may be read for
ideas when Epics B and D start.

## Scope decisions (confirm before Phase 0 exit)
1. Notification channel for v1: email via Supabase Auth + Edge Function.
   SMS deferred (cost, privacy surface). Decision owner: product lead.
2. Explainer content: static pages for evergreen material; anything with a
   data-as-of date lives in the database. No new CMS.
3. Digest generation: derived from the events table by a scheduled job outputting
   a draft that a human approves before it is published or emailed.
4. Analytics: privacy-respecting, cookieless, self-hosted where possible
   (e.g. Plausible-class tooling); no third-party advertising trackers. Any
   analytics addition requires a privacy note update.

---

## Success metrics (defined before building)
Baseline at launch, reviewed monthly. All instrumentation is first-party only.

| Metric | Target (6 months post-launch) | Instrument |
|---|---|---|
| Time-to-first-site-profile | ≤ 2 taps from home; median < 90 s | click-path events |
| Five-minute comprehension | ≥ 40% of sessions view explainer + one record | session cohort |
| Citation coverage | 100% of published claims linked to source records | REVIEW checklist gate |
| Gap-flag discipline | 0 blank numeric fields rendered without GapBadge | component test suite |
| Return rate | ≥ 25% of subscribers open two consecutive digests | digest stats |
| Narrative loop | median session includes ≥ 1 essay AND ≥ 1 data record | session cohort |
| Correction SLA | 100% resolved within 7 days | correction log |
| Essay cadence | ≥ 1/month shipped through full pipeline | editorial calendar |
| PSA latency | published ≤ 5 working days after trigger detection | PSA pipeline log |
| Accessibility | WCAG 2.2 AA on all templates; axe-core 0 violations | CI audit |
| Performance | LCP < 2.5 s mobile; INP < 200 ms; CLS < 0.1 | Lighthouse CI budget |

Anti-metrics (things we deliberately do NOT optimise for): raw time-on-page,
outrage-driven share volume, dark-pattern email capture growth.

---

## Design-system foundation (Phase 0 deliverables, consumed by every phase)
Additions to UI.md, built as shared components so later phases assemble rather
than invent:

- Trust primitives: SourcePanel, GapBadge, DateStamp and FactOpinionDivider
  exist on `main`. New: CitationChip ("cite this record" snippet).
- Narrative primitives: StatTile, extended with as-of date and gap footnote, ClaimVsRecord
  (perception claim card beside the evidence record — stages the core narrative),
  EmptyStateMessage (gap-aware empty states, e.g. "no sites tracked in your LGA
  yet, and here is how we would know if one appeared").
- Wayfinding primitives: Breadcrumb, SectionNav, BackToContext bar (persistent
  "you are reading X, see underlying data" strip on essay pages).
- Tokens: colour-blind-safe six-colour track palette (verified with simulated
  deuteranopia/protanopia/tritanopia), type scale, spacing, focus-ring spec,
  motion tokens (all transitions honour prefers-reduced-motion).
- Every primitive ships with: keyboard behaviour spec, screen-reader label spec,
  and a Storybook-style gallery page (internal route) for review.

---

## Epics

### Epic A — Orientation (first-time visitor)
Owner: front-end + editor. Depends on: Phase 0 tokens/primitives.
- A1 Home briefing block: three live StatTiles (sites tracked, one named
  capacity figure, events this quarter), each gap-aware, above the fold. The
  capacity tile names which of the four figures it shows, sums only the sites
  that report that figure, and states how many do not. It never adds one
  figure to another (docs/PIPELINE_MAPPING.md, "Capacity: four figures, never
  aggregated") and never uses `live_capacity_mw`, which no import populates.
- A2 "What is an AI data centre?" explainer (static page): power, water, land,
  cooling in numbers; glossary terms wired to tooltips (E4).
- A3 Start-here path: home → explainer → nearest activity, ≤ 2 taps.
Acceptance: new-visitor task test (5 participants) completes "find what's
happening near me and understand why it matters" unaided.

### Epic B — Place-based access
Owner: front-end + data. Depends on: migration M1.
- B1 Suburb/postcode search resolving to LGA/site results, backed by a
  locality lookup table (M1). No geocoding vendor dependency in v1; curated
  locality list for approved council areas plus national postcode→LGA mapping.
- B2 Area results view: nearby sites, active planning events, watchlist items,
  linked essays; designed empty state.
- B3 Map popup: status, capacity with gap badge and site profile link are done.
  Remaining: link to related essays.
- B4 Per-LGA landing pages (SEO entry point for residents searching their area).
Acceptance: search returns correct LGA for top-50 tested suburb/postcode inputs;
area page renders fully offline-of-data with empty-state messaging.

### Epic C — Timeline readability and return loops
Owner: front-end. Depends on: Phase 0 palette.
- C1 Default rolling 12-month window + significance filter (major entities/
  projects first); advanced users can widen range and toggle all six tracks.
- C2 Per-month sparkline density control so sparse and surge months both read.
- C3 Keyboard-operable timeline with accessible list fallback (already required
  by UI.md; now specified and tested per breakpoint).
- C4 Monthly digest page generated from events table; human-approved payload.
- C5 LGA/site/entity alert subscriptions (Supabase Auth + Edge Function;
  explicit consent, AU privacy statement, one-click unsubscribe).
Acceptance: timeline usable at 360px width; subscription flow passes privacy
review; digest open-rate metric instrumented from first send.

### Epic D — Cross-linking the narrative (fact ↔ editorial loop)
Owner: full-stack. Depends on: existing links/citations tables (SPEC.md).
- D1 Site profiles show every essay citing the site (reverse citation query).
- D2 Essay pages render the exact records behind each claim (SourcePanel from
  citations) + persistent BackToContext bar.
- D3 ClaimVsRecord module on home and essay hub: common perception stated, then
  the record(s) that support or contradict it, dated.
Acceptance: every published essay cites ≥ 5 database records (enforced by
publish checklist); zero orphan essays (each reachable from ≥ 1 data record).

### Epic E — Informativeness and data utility
Owner: full-stack. Depends on: migrations M2–M3.
- E1 National/state rollups by status (proposed, under construction,
  operating, stalled), one capacity figure per rollup, never combined across
  figures, each showing how many sites it covers and how many lack the figure;
  every aggregate links to underlying rows (M2).
- E2 Journalist toolkit: CSV export per table view, "cite this record" snippet,
  stable deep links for every record (M3).
- E3 Status-change history on site profiles derived from events (dated
  transitions, not assertions).
- E4 Glossary tooltips tied to explainer content.
- E5 Comparison view: up to three sites side-by-side; unknowns shown as gap
  badges, never hidden.
Acceptance: exported CSV row counts match DB queries in tests; rollup totals
reconcile with row-level sums automatically in CI.

### Epic F — Trust as visible content
Owner: front-end + editor.
- F1 Public methodology page: ingestion sources, approved council list, audit
  cadence, agent boundaries (from SUBAGENTS.md, humanised).
- F2 Correction log rendered publicly with resolution status and dates.
- F3 "How we handle missing data" section normalising gap flags as honesty.
Acceptance: methodology page linked in footer of every fact-layer page;
correction entries display publish→resolve duration.

### Epic G — Mobile, accessibility, performance polish
Owner: front-end. Runs alongside C–F, closes the program.
- G1 Mobile-first pass on timeline and map (list fallbacks mandatory).
- G2 Colour-blind-safe palette applied everywhere; contrast re-audit.
- G3 Loading/error/empty states designed per component; sparse launch dataset
  must look intentional (gap messaging, not blanks).
- G4 Performance budget in CI (Lighthouse): LCP/INP/CLS thresholds above.
- G5 axe-core in CI across all page templates (done: `test:ui`); manual screen-reader pass
  (VoiceOver iOS, NVDA Chrome) on timeline, map, search, subscription flows.
Acceptance: AA sign-off recorded in QUALITY.md per release; budgets green in CI.

---

## Schema / migration backlog (supabase migrations only; no manual edits)
`main` has migrations 0001–0012, so these take numbers from 0013 in the order
they ship.
- M1 `localities`: name, postcode, lga_code, lat/lng centroid, source_id —
  powers suburb search (B1). Populated from ABS/Australian Postal Directory
  equivalent public dataset; every row carries a source record.
- M2 `v_rollup_capacity_by_status_state` (SQL views) — aggregates computed in
  Postgres so the DB stays the single source of truth for rollups (E1). One
  column set per capacity figure, each with a count of reporting and
  non-reporting sites; no view adds figures together.
- M3 `record_slugs`: stable slug per site/entity/event/essay for deep links and
  citation snippets (E2).
- M4 `subscriptions`: user_id, target_type (lga/site/entity), target_id,
  consent_timestamp, channel — Supabase Auth protected, RLS enforced. This is
  the first personal data the observatory would hold. It does not ship until
  the privacy review is signed off and DEPLOYMENT.md's backup classification
  says how it is exported and retained.
- M5 `digests` + `digest_items`: approved monthly digests as records with
  publish and data-as-of dates (C4). PSAs reuse digests with a `psa` tag and
  expiry_date column (see below).
- Explicitly out of scope: GIS overlays, per-parcel geometry, any second store.

## PSA production integration (operational, from UX.md)
PSAs run as a standing sub-process of Epic C/F pipelines, not a code epic:
1. Trigger detection during monthly ingest review (dated records only).
2. Editor confirms trigger; writer_support drafts from the four-slot template
   (situation / who it affects / what you can do via official channels /
   deadline with source link).
3. Reviewer agent checks REVIEW.md; human approval; publish with expiry_date.
4. Distribution: digest email, banner on affected LGA page (B4), generated
   share card. Expired PSAs archive automatically (M5 expiry handling).
KPI: trigger→publish ≤ 5 working days; 0 undated triggers published.

---

## Sequencing and dependencies

| Stage | Contents | Exit gate |
|---|---|---|
| Phase 0 (weeks 1–2) | Scope decisions, success metrics instrumented (privacy-reviewed), design tokens + primitive library | Primitives pass contrast/keyboard specs; analytics decision signed off |
| Phase 1 (weeks 3–8) | Epics A, B, F; migrations M1, M3 | New-visitor task test passes; AA audit green on shipped templates; suburb search accuracy check |
| Phase 2 (weeks 9–14) | Epics C, D; migrations M2, M4, M5 | Timeline usable on mobile; first digest sent; zero orphan essays; essay citation rule enforced |
| Phase 3 (weeks 15–18) | Epic E | Rollups reconcile in CI; CSV export tests pass; comparison view gap-badge complete |
| Phase 4 (weeks 19–20) | Epic G | Full AA sign-off; performance budgets green; launch checklist |

Cadence: two-week iterations; each iteration ends with a usability test against
the current build (moderated, 5 participants, mixed resident/journalist) and a
metrics review. Features that fail their acceptance task are fixed or cut —
they do not roll forward untested.

Team assumption: 1 front-end, 1 full-stack/data, 1 editor/content (part-time),
agents used within SUBAGENTS.md limits (drafts and checks only).

## Risks and mitigations
- Sparse launch data makes the site look empty → gap messaging as a feature
  (EmptyStateMessage, "we track X, we know Y, we are missing Z"), significance
  filtering hides nothing but prioritises.
- Subscription privacy burden → minimal PII (email + targets only), consent
  timestamps, one-click unsubscribe, documented retention; privacy review is a
  Phase 0 exit gate, not a late add-on.
- Editorial pipeline throughput (monthly essay + digest + PSAs) is the real
  bottleneck → fixed templates, agent-assisted evidence pulls, quarterly
  reverification batched to one week per quarter.
- Locality data drift (postcode↔LGA boundary changes) → M1 rows carry source
  and as-of date; annual refresh scheduled with the audit cadence.
- Scope creep toward GIS dashboards → point-map-only rule restated in every
  planning retro; any overlay proposal needs a written exception to CLAUDE.md.

## Governance
- This plan is reviewed at each phase exit gate and updated in place; changes
  to metrics or scope require sign-off from the product lead and editor.
- UX.md remains the rationale document; UX-PLAN.md is the execution tracker.
- Definition of done for any item: acceptance criteria met, AA checks green,
  metrics instrumented, docs/UI.md and docs/SPEC.md updated if surfaces changed.
