-- 0008: the site fields the research actually carries.
--
-- docs/SPEC.md's original sites table was drawn before the research existed.
-- These columns are the ones the curation pipeline populates and cites.
--
-- On capacity: the pipeline records up to four independent figures per site and
-- its README explicitly forbids aggregating them, because they measure
-- different things. IT capacity is the load available to racks; total is the
-- site draw including cooling and losses; max is the ceiling the connection or
-- consent permits; first phase is what stage one delivers. Summing or
-- substituting them would manufacture a figure nobody published, so there is
-- deliberately NO cross-field CHECK relating them. Each is bounded on its own.
--
-- The existing sites_live_within_total check is untouched and remains correct:
-- the pipeline has no live capacity figure at all, so live_capacity_mw imports
-- as null and the check passes vacuously.

alter table facts.sites
  add column proponent          text,
  add column suburb             text,
  add column state              text,
  add column market             text,
  add column address            text,
  add column it_capacity_mw     numeric,
  add column max_capacity_mw    numeric,
  add column first_phase_mw     numeric,
  add column campus_area_ha     numeric,
  add column gfa_sqm            numeric,
  add column capital_cost_aud   numeric,
  add column construction_jobs  integer,
  add column operational_jobs   integer,
  add column operational_from   text,
  add column target_completion  text,
  add column hcf_certified      text;

-- Each capacity figure is positive on its own terms. No relation between them
-- is asserted; see the note above.
alter table facts.sites
  add constraint sites_it_capacity_positive
    check (it_capacity_mw is null or it_capacity_mw > 0),
  add constraint sites_max_capacity_positive
    check (max_capacity_mw is null or max_capacity_mw > 0),
  add constraint sites_first_phase_positive
    check (first_phase_mw is null or first_phase_mw > 0),
  add constraint sites_campus_area_positive
    check (campus_area_ha is null or campus_area_ha > 0),
  add constraint sites_gfa_positive
    check (gfa_sqm is null or gfa_sqm > 0),
  add constraint sites_capital_cost_non_negative
    check (capital_cost_aud is null or capital_cost_aud >= 0),
  add constraint sites_construction_jobs_non_negative
    check (construction_jobs is null or construction_jobs >= 0),
  add constraint sites_operational_jobs_non_negative
    check (operational_jobs is null or operational_jobs >= 0);

-- Australian jurisdictions, plus 'Multi' for a site or portfolio that spans
-- more than one. Free text here would defeat the canonical naming rule in
-- docs/QUALITY.md.
alter table facts.sites
  add constraint sites_state_known
    check (state is null or state in
      ('NSW','VIC','QLD','SA','WA','TAS','NT','ACT','Multi'));

-- Electricity market the site sits in. NEM is the eastern interconnected
-- market, WEM is Western Australia's, NT is its own.
alter table facts.sites
  add constraint sites_market_known
    check (market is null or market in ('NEM','WEM','NT','Multi'));

comment on column facts.sites.operational_from is
  'Text, not a date. Sources state these as "2025", "H2 2026" or "late 2027",
   and coercing that to a date would invent a precision the source does not
   have.';

comment on column facts.sites.hcf_certified is
  'Hosting Certification Framework standing, as the source states it. A status
   with an "unknown" value, not a boolean: not knowing whether a site is
   certified is different from knowing it is not.';

create index sites_state_idx on facts.sites (state);
