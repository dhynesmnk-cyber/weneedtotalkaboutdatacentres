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
  water_usage, notes. Every field nullable with explicit gap flag.
- entities: id, name, type, role, major_flag, public_actions_summary.
- events: id, category, date, title, summary, site_id, source_ids.
- event_categories: planning, construction, media, political, community, financial.
- links: auto generated many to many between sites, entities and events,
  created when an entity or site is mentioned in a record.
- case_studies: id, title, publish_date, data_as_of_date, site_id,
  metrics jsonb, narrative, source_ids.
- sources: id, type, title, url, retrieved_date, publisher.
- citations: join table linking claims or records to sources.
- essays: id, title, publish_date, youtube_id, body, tags, related_ids.
- council_watchlist: approved councils for targeted ingestion.

## Relationships
- links table creates many-to-many between sites, entities and events automatically.
- citations table links any record (sites, entities, events, case_studies, essays) to sources.
- Foreign keys: site_id references sites(id), entity_id references entities(id), 
  event_id references events(id), source_id references sources(id).

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
