-- 0002: the fact layer.
--
-- Every field on sites is nullable by design. A null is not an oversight, it is
-- a gap, and facts.data_gaps records why. No value is ever inferred or
-- estimated to avoid a gap. See docs/SPEC.md "Gap flags".

create table facts.sources (
  id            uuid primary key default gen_random_uuid(),
  type          text not null,
  title         text not null,
  url           text,
  retrieved_date date not null,
  publisher     text,
  created_at    timestamptz not null default now(),
  updated_at    timestamptz not null default now()
);

comment on column facts.sources.type is
  'Unconstrained pending a spec decision on the source type domain. Canonical
   naming is required by docs/QUALITY.md but the permitted values are not yet
   enumerated in docs/SPEC.md.';

create index sources_retrieved_date_idx on facts.sources (retrieved_date desc);

create table facts.sites (
  id                uuid primary key default gen_random_uuid(),
  name              text not null,
  operator          text,
  lat               double precision,
  lng               double precision,
  lga               text,
  status            facts.site_status,
  total_capacity_mw numeric,
  live_capacity_mw  numeric,
  cooling_type      text,
  rack_density_kw   numeric,
  grid_connection   text,
  water_usage       numeric,
  notes             text,
  created_at        timestamptz not null default now(),
  updated_at        timestamptz not null default now(),

  -- Validation rules from docs/QUALITY.md. Capacity is numeric and positive;
  -- a value that fails these is a defect, not a gap.
  constraint sites_total_capacity_positive
    check (total_capacity_mw is null or total_capacity_mw > 0),
  constraint sites_live_capacity_positive
    check (live_capacity_mw is null or live_capacity_mw > 0),
  constraint sites_rack_density_positive
    check (rack_density_kw is null or rack_density_kw > 0),
  constraint sites_water_usage_non_negative
    check (water_usage is null or water_usage >= 0),

  -- Live capacity cannot exceed total capacity. Where both are known.
  constraint sites_live_within_total
    check (
      total_capacity_mw is null
      or live_capacity_mw is null
      or live_capacity_mw <= total_capacity_mw
    ),

  -- Coordinates are supplied together or not at all. Half a point is not a
  -- point, and the map layer should never receive one.
  constraint sites_coords_paired
    check ((lat is null) = (lng is null)),
  constraint sites_lat_range check (lat is null or lat between -90 and 90),
  constraint sites_lng_range check (lng is null or lng between -180 and 180)
);

create index sites_status_idx on facts.sites (status);
create index sites_lga_idx on facts.sites (lga);

create table facts.entities (
  id                     uuid primary key default gen_random_uuid(),
  name                   text not null,
  type                   text,
  role                   text,
  major_flag             boolean not null default false,
  public_actions_summary text,
  created_at             timestamptz not null default now(),
  updated_at             timestamptz not null default now()
);

comment on column facts.entities.major_flag is
  'Entity profiles are published only for entities flagged major by public
   prominence. See docs/SPEC.md "Entity profiles".';
comment on column facts.entities.type is
  'Unconstrained pending a spec decision, as with facts.sources.type.';

create index entities_major_flag_idx on facts.entities (major_flag) where major_flag;

create table facts.events (
  id         uuid primary key default gen_random_uuid(),
  category   facts.event_category not null,
  date       date not null,
  title      text not null,
  summary    text,
  site_id    uuid references facts.sites (id) on delete set null,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

-- The timeline reads in date order across combinable tracks.
create index events_date_idx on facts.events (date desc);
create index events_category_date_idx on facts.events (category, date desc);
create index events_site_id_idx on facts.events (site_id);

-- Derived many-to-many between sites, entities and events.
--
-- Ingestion proposes; a human confirms. Only confirmed links are publicly
-- readable, enforced in RLS rather than left to the application layer.
create table facts.links (
  id           uuid primary key default gen_random_uuid(),
  site_id      uuid references facts.sites (id) on delete cascade,
  entity_id    uuid references facts.entities (id) on delete cascade,
  event_id     uuid references facts.events (id) on delete cascade,
  state        facts.link_state not null default 'proposed',
  confirmed_by text,
  confirmed_at timestamptz,
  created_at   timestamptz not null default now(),

  -- A link joins at least two of the three. A row pointing at one record is
  -- not a relationship.
  constraint links_at_least_two_endpoints check (
    (case when site_id is not null then 1 else 0 end)
    + (case when entity_id is not null then 1 else 0 end)
    + (case when event_id is not null then 1 else 0 end) >= 2
  ),

  -- Confirmation is a human act and leaves a trace. A confirmed link with no
  -- confirmer is not confirmed.
  constraint links_confirmation_complete check (
    (state = 'proposed' and confirmed_by is null and confirmed_at is null)
    or (state = 'confirmed' and confirmed_by is not null and confirmed_at is not null)
  )
);

create unique index links_unique_triple
  on facts.links (
    coalesce(site_id, '00000000-0000-0000-0000-000000000000'::uuid),
    coalesce(entity_id, '00000000-0000-0000-0000-000000000000'::uuid),
    coalesce(event_id, '00000000-0000-0000-0000-000000000000'::uuid)
  );

create index links_state_idx on facts.links (state);

-- The single path from any record to a source. Earlier drafts also gave events,
-- case_studies and essays a source_ids array; two mechanisms for one
-- relationship meant citation coverage could never be enforced.
create table facts.citations (
  id          uuid primary key default gen_random_uuid(),
  source_id   uuid not null references facts.sources (id) on delete restrict,
  record_type facts.citable_record not null,
  record_id   uuid not null,
  claim       text,
  created_at  timestamptz not null default now()
);

comment on column facts.citations.record_id is
  'Polymorphic, so it carries no foreign key. Integrity is enforced by
   record_type, the typed accessors in lib/, and their tests. This is a
   deliberate trade-off recorded in docs/SPEC.md "Citations".';
comment on column facts.citations.claim is
  'The specific assertion this source supports. Optional, but a record with six
   claims and six sources is only auditable when each is named.';

create index citations_record_idx on facts.citations (record_type, record_id);
create index citations_source_id_idx on facts.citations (source_id);

-- Why a value is missing.
create table facts.data_gaps (
  id          uuid primary key default gen_random_uuid(),
  record_type facts.citable_record not null,
  record_id   uuid not null,
  field_name  text not null,
  reason      facts.gap_reason not null,
  noted_date  date not null default current_date,
  source_id   uuid references facts.sources (id) on delete set null,
  created_at  timestamptz not null default now()
);

comment on column facts.data_gaps.source_id is
  'Optional evidence for the gap itself, for example a planning document with
   the figure redacted.';

create unique index data_gaps_unique_field
  on facts.data_gaps (record_type, record_id, field_name);

create index data_gaps_record_idx on facts.data_gaps (record_type, record_id);

-- Approved councils for targeted ingestion.
--
-- CLAUDE.md permits council ingestion only for councils approved in
-- docs/SPEC.md. That approval is a human act, so approved_by and approved_at
-- are mandatory: there is no way to add a council without recording who
-- approved it. Candidates live in docs/COUNCIL_CANDIDATES.md and are not rows
-- in this table until approved.
create table facts.council_watchlist (
  id          uuid primary key default gen_random_uuid(),
  lga         text not null unique,
  state       text not null,
  approved_by text not null,
  approved_at timestamptz not null,
  notes       text,
  created_at  timestamptz not null default now(),

  constraint council_watchlist_state_valid
    check (state in ('NSW', 'VIC', 'QLD', 'SA', 'WA', 'TAS', 'NT', 'ACT'))
);

create trigger sources_set_updated_at
  before update on facts.sources
  for each row execute function facts.set_updated_at();

create trigger sites_set_updated_at
  before update on facts.sites
  for each row execute function facts.set_updated_at();

create trigger entities_set_updated_at
  before update on facts.entities
  for each row execute function facts.set_updated_at();

create trigger events_set_updated_at
  before update on facts.events
  for each row execute function facts.set_updated_at();
