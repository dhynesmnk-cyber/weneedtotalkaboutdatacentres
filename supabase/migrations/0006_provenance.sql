-- 0006: provenance columns carried over from the curation pipeline.
--
-- Every row the pipeline produces states how well established it is, how
-- confident the curator was, and what date the claim is good as at. Dropping
-- that on import would turn a graded research record into an undifferentiated
-- assertion, which is the opposite of what this project is for.
--
-- This is not a second citation mechanism. facts.citations remains the only
-- path from a record to a source (docs/SPEC.md "Citations"). These columns
-- describe the *strength* of a claim that is already cited.

-- How well established a claim is. Ordered weakest to strongest so that a
-- comparison in a query reads the way a reader would expect.
create type facts.fact_status as enum (
  'gap',       -- no value established; the record exists, the fact does not
  'claimed',   -- asserted by an interested party, not independently confirmed
  'reported',  -- reported by a secondary source such as press
  'verified'   -- confirmed against a primary source
);

comment on type facts.fact_status is
  'Strength of a claim. A "claimed" row is never presented to a reader as
   verified; see docs/QUALITY.md.';

-- Curator confidence, distinct from fact_status: a reported figure can be held
-- with high confidence, and a primary document can still be ambiguous.
create type facts.confidence_level as enum ('low', 'medium', 'high');

-- Source grading, A strongest. Primary government and regulator documents grade
-- A; press and market research grade B or C.
create type facts.source_credibility as enum ('A', 'B', 'C', 'D');

alter table facts.sites
  add column fact_status facts.fact_status,
  add column confidence  facts.confidence_level,
  add column as_of_date  date;

alter table facts.entities
  add column fact_status facts.fact_status,
  add column confidence  facts.confidence_level,
  add column as_of_date  date;

alter table facts.sources
  add column credibility facts.source_credibility;

comment on column facts.sites.as_of_date is
  'The date the claim is good as at, which is not the date the source was
   retrieved. A 2024 capacity figure read in 2026 is as_of 2024.';

create index sites_fact_status_idx    on facts.sites (fact_status);
create index entities_fact_status_idx on facts.entities (fact_status);
