# SPEC.md

## Purpose
Define product scope, audience and data model for the observatory.

## Audience
- Local residents near proposed or operating sites.
- Journalists covering planning, energy and investment.

## Goals
- Track Australian AI data centre sites, entities, events and finances.
- Publish dated case studies and video essays that compare public perception
  with research data.
- Keep raw data openly browsable for advanced users while guiding general
  readers through editorial content.

## Non goals for v1
- Full GIS overlays (power grid zones, water catchments, boundaries).
- Tracking of individual community members.
- Paid access tiers.
- Automated AEMO ingestion (quarterly manual parse instead).
- Scraping of all councils (approved list only).

## Entry points, in priority order
1. Timeline (separate event tracks, combinable).
2. Essay hub (date ordered, YouTube embeds plus written analysis).
3. Map (simple point map with site popups).
4. List (sortable index of sites and entities).

## Data model (core tables)
- sites: id, name, operator, lat, lng, lga, status, total_capacity_mw,
  live_capacity_mw, cooling_type, rack_density_kw, grid_connection,
  water_usage, notes. Every field nullable, with any missing value recorded
  in data_gaps. See Site status values and Gap flags below.
  Migration 0008 adds the fields the research carries: proponent, suburb,
  state, market, address, it_capacity_mw, max_capacity_mw, first_phase_mw,
  campus_area_ha, gfa_sqm, capital_cost_aud, construction_jobs,
  operational_jobs, operational_from, target_completion, hcf_certified.
  The four capacity figures measure different things and are never aggregated
  or substituted for one another; live_capacity_mw is never populated by an
  import. See docs/PIPELINE_MAPPING.md.
- entities: id, name, type, role, major_flag, public_actions_summary.
- events: id, category, date, title, summary, site_id.
- event_categories: planning, construction, media, political, community, financial.
- links: many to many between sites, entities and events, proposed by ingestion
  when an entity or site is mentioned in a record. See Link generation below.
- case_studies: id, title, publish_date, data_as_of_date, site_id,
  metrics jsonb, narrative.
- sources: id, type, title, url, retrieved_date, publisher.
- citations: id, source_id, record_type, record_id, claim, created_at.
  The single mechanism linking any record or claim to a source.
- data_gaps: id, record_type, record_id, field_name, reason, noted_date,
  source_id. Records why a value is missing.
- essays: id, title, publish_date, youtube_id, body, tags, related_ids.
- council_watchlist: approved councils for targeted ingestion. See Ingestion scope.
- research_agenda: open research questions, with why each matters and how it is
  to be answered. NOT the same as data_gaps: a gap is a per-field absence, a
  research question is an open line of enquiry. Publishing the agenda is
  deliberate, because an observatory that shows what it has not established is
  more honest than one that shows only what it has.
- lga_aliases: human-approved council name equivalences. Empty until a human
  fills it; no import writes here.
- ingest_runs: one row per load of the curation pipeline, carrying the SHA-256
  of the build it read, so a published figure is traceable to its source build.

## Provenance columns
sites and entities carry fact_status (verified, reported, claimed, gap),
confidence (low, medium, high) and as_of_date. sources carry credibility (A-D).

These are not a second citation mechanism. citations remains the only path from
a record to a source; these describe the strength of a claim that is already
cited. A claimed record is a proponent's assertion nobody has confirmed, and is
never presented to a reader as verified.

## Schema separation
The fact layer and the editorial layer are separate in the database, not only in
the UI. Two Postgres schemas, each with its own Row Level Security policy set so
public read paths can be reviewed one layer at a time.

- facts: sites, entities, events, links, sources, citations, data_gaps,
  council_watchlist.
- editorial: essays, case_studies.

One record type spans the boundary deliberately. case_studies.metrics holds
factual figures inside an editorial table. Those figures carry citations exactly
like any other factual claim, and are never presented as narrative.

## Relationships
- links table creates many-to-many between sites, entities and events.
- citations table links any record (sites, entities, events, case_studies, essays)
  to sources.
- Foreign keys: site_id references sites(id), entity_id references entities(id),
  event_id references events(id), source_id references sources(id).

## Citations
citations is the only path from a record to a source. Earlier drafts also gave
events, case_studies and essays a source_ids array, which meant two mechanisms
for one relationship and no way to enforce that every factual claim references a
source. The arrays are removed.

- One row per claim per source. The optional claim field names the specific
  assertion being supported, so a record with six claims and six sources is
  auditable rather than merely well cited on average.
- record_type is constrained by check to the table names listed above.
- Known trade off: a polymorphic record_id cannot carry a real foreign key.
  Referential integrity is enforced by the record_type check constraint, the
  typed accessors in /lib, and their tests. This is a deliberate choice with a
  named cost, not an oversight.
- Open item for the scaffold pass: essays.related_ids has the same untyped
  polymorphic shape. Resolve it against the links table rather than reinventing
  a third mechanism.

## Gap flags
Every field in sites is nullable. A null means the value is missing, and
data_gaps records why. The reason is the point. An operator declining to
disclose water usage is a different claim from nobody having asked yet, and both
are different from the figure not applying to that site at all.

- reason is constrained to one of: unknown, not_disclosed, not_applicable,
  withheld.
  - unknown: not yet researched, or researched without result.
  - not_disclosed: asked or publicly sought, and the holder did not provide it.
  - not_applicable: the field does not apply to this site.
  - withheld: exists but is redacted or commercial in confidence in the source.
- source_id is optional and cites the evidence for the gap itself, for example a
  planning document with the figure redacted.
- A value is never inferred, estimated or interpolated to avoid a gap.
- The UI renders the reason, not a bare marker. See GapBadge in UI.md.

## Site status values
status is constrained to one of: rumoured, pre_lodgement, proposed, lodged,
approved, under_construction, operating, stalled, refused, withdrawn,
cancelled.

Five of these (rumoured, pre_lodgement, lodged, refused, cancelled) were added
in migration 0005 to hold distinctions the curation pipeline records and the
original six values could not. Two matter especially, and the reasoning is in
docs/PIPELINE_MAPPING.md:

- refused is not withdrawn. A refusal is an authority stopping a project; a
  withdrawal is a proponent stopping it. They are opposite claims about who
  decided.
- rumoured is not proposed. A rumour is an unverified report; a proposal is a
  formal act.

stalled is load bearing. The evidence policy permits naming stalled projects
with citations, so the schema has to be able to represent one rather than
leaving it implied by an absence of recent events. No import produces it: it is
a human editorial judgement about a project that has gone quiet.

## Link generation
links are derived records, and derivation is not publication.

- Ingestion proposes links into a staging state when an entity or site is
  mentioned in a record. Ingestion never writes directly to production tables.
- Each link carries a confirmation state: proposed or confirmed, plus
  confirmed_by and confirmed_at.
- Only confirmed links are publicly visible. A human confirms them.
- This follows the ingester boundary in SUBAGENTS.md and the rule that no agent
  publishes content. An automatic mention match is a suggestion, not a finding.

## Financial case study metrics
total_capex_aud, annual_revenue_aud, annual_opex_aud, development_yield_pct,
stabilised_cap_rate_pct, power_cost_per_kw. Gaps flagged, never estimated.

## Evidence policy
- Factual claims carry citations shown in a source panel.
- Named stalled projects are permitted with citations.
- No right of reply process. Fact and opinion separated visually in UI.
- Community opposition tracked only via planning submissions and council data.

## Entity profiles
- Profiles only for entities flagged major by public prominence.
- Fields: name, type, role, public actions summary.
- Relationships to sites and events generated automatically from mentions.

## Ingestion scope
- Approved council watchlist via targeted alerts and feeds.
- AEMO Generation Information parsed manually each quarter.
- ASX and company announcement feeds automated.
- Mainstream news feeds automated for perception events.
- Commonwealth procurement (AusTender) archived on demand, never on a schedule.
  See "Commonwealth procurement" below.

## Commonwealth procurement
`data-pipeline/scrapers/ingest_austender.py` archives keyword searches on
tenders.gov.au. It is the portal of record wanted in place of the GovMarket
aggregator, which is graded C because it silently merges spelling variants of
the same entity.

The scraper exists; the source is not yet approved for unattended use, and the
two are deliberately not the same thing.

**Status: manual only. It is excluded from `rebuild_all.py --fetch`, so no
scheduled job runs it, and it has never been run against the live site.** Its
first live run is a human review step: read the archived HTML before writing any
curation against it, because none of its parsing has been tested on real
AusTender markup.

Approving it for scheduled ingestion is a human decision and belongs in the
table below, alongside a note on what the archive is to be used for.

| Source | Approved for scheduled use | Approved on | Approved by |
| --- | --- | --- | --- |
| tenders.gov.au keyword search | no — manual only | | |

## Approved council list
The hard rule in CLAUDE.md permits council ingestion only for councils approved
here. That approval is a human decision.

**Status: the approved list is currently empty. No council ingestion may run.**

Candidates are drafted, with a source for each, in docs/COUNCIL_CANDIDATES.md.
They are proposals only and carry no authority until a human moves them into the
table below. Entries land in the council_watchlist table once approved.

Council names appear in the data under more than one spelling. Proposed
equivalences are in docs/LGA_ALIAS_CANDIDATES.md and are likewise proposals
only: `facts.lga_aliases` requires a named approver per row and no import
writes to it.

| LGA | State | Approved on | Approved by |
| --- | --- | --- | --- |
| _(none yet)_ | | | |
