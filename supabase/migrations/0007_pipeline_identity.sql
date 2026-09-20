-- 0007: stable identity for rows that originate in the curation pipeline.
--
-- The pipeline keys its records with readable natural keys (SITE_MSFT_KEMPS,
-- ENT_MSFT_DC_AU, SRC_NSW_IDA); this schema keys on uuid. Carrying the pipeline
-- key alongside the uuid does two things:
--
--   1. Makes the load idempotent. The loader upserts on pipeline_id, so running
--      it twice produces one row, not two, and a re-run after a pipeline
--      correction updates the row it corrected rather than duplicating it.
--   2. Makes a published record traceable back to the pack that produced it,
--      which is what lets a reader's question be answered by re-running the
--      pipeline rather than by memory.
--
-- Nullable, because a row created directly in this database (a human-entered
-- correction) has no pipeline origin and should not pretend to.

alter table facts.sites    add column pipeline_id text;
alter table facts.entities add column pipeline_id text;
alter table facts.sources  add column pipeline_id text;

create unique index sites_pipeline_id_key    on facts.sites    (pipeline_id) where pipeline_id is not null;
create unique index entities_pipeline_id_key on facts.entities (pipeline_id) where pipeline_id is not null;
create unique index sources_pipeline_id_key  on facts.sources  (pipeline_id) where pipeline_id is not null;

comment on column facts.sites.pipeline_id is
  'Natural key from data-pipeline/, e.g. SITE_MSFT_KEMPS. Null for rows that did
   not come from the pipeline. Unique where present, which is what makes the
   load idempotent.';
