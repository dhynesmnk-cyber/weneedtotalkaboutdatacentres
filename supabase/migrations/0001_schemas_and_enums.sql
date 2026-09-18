-- 0001: schemas and enumerated domains.
--
-- The fact layer and the editorial layer are separate schemas, not just
-- separate tables, so Row Level Security can be reviewed one layer at a time.
-- See docs/SPEC.md "Schema separation".

create schema if not exists facts;
create schema if not exists editorial;

comment on schema facts is
  'Verified, sourced records. Every factual field carries citations.';
comment on schema editorial is
  'Published analysis and video essays. Opinion lives here, never in facts.';

-- Site lifecycle. "stalled" is load bearing: the evidence policy permits naming
-- stalled projects with citations, so the schema has to represent one rather
-- than leaving it implied by an absence of recent events.
create type facts.site_status as enum (
  'proposed',
  'approved',
  'under_construction',
  'operating',
  'stalled',
  'withdrawn'
);

-- Timeline tracks. Matches the track selector in docs/UI.md.
create type facts.event_category as enum (
  'planning',
  'construction',
  'media',
  'political',
  'community',
  'financial'
);

-- Why a value is missing. The reason is the point: an operator declining to
-- disclose is a different claim from nobody having looked yet.
create type facts.gap_reason as enum (
  'unknown',          -- not yet researched, or researched without result
  'not_disclosed',    -- sought, and the holder did not provide it
  'not_applicable',   -- the field does not apply to this record
  'withheld'          -- exists but redacted or commercial in confidence
);

-- Derived links are proposals until a human confirms them. Ingestion may write
-- 'proposed'; only a human sets 'confirmed'. See docs/SPEC.md "Link generation".
create type facts.link_state as enum ('proposed', 'confirmed');

-- Which tables a citation or gap may point at. A polymorphic record_id cannot
-- carry a real foreign key, so this enum is the integrity boundary, backed by
-- the typed accessors in lib/ and their tests.
create type facts.citable_record as enum (
  'sites',
  'entities',
  'events',
  'case_studies',
  'essays'
);

-- Helper for updated_at columns.
create or replace function facts.set_updated_at()
returns trigger
language plpgsql
as $$
begin
  new.updated_at = now();
  return new;
end;
$$;
