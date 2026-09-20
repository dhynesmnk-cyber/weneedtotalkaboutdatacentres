-- 0010: what a repeatable load needs.
--
-- Three things, all of which exist so that loading the curation pipeline into
-- this database is an auditable act rather than a mystery.

-- 1. Idempotent citations.
--
-- data_gaps already has data_gaps_unique_field (0002). citations had no
-- equivalent, so re-running a load would insert a second identical citation
-- every time. Two rows asserting the same source for the same claim is not
-- twice the evidence.
--
-- claim is nullable, and null is not equal to null in a unique index, so the
-- key coalesces it. Distinct claims against the same source stay distinct.
create unique index citations_unique_record_source
  on facts.citations (record_type, record_id, source_id, coalesce(claim, ''));

-- 2. Council name aliases.
--
-- The research records councils as its sources name them, which means
-- 'Blacktown' and 'Blacktown City Council' are both present, along with
-- 'Fairfield City', 'Fairfield City Council', and one site recorded as
-- 'Fairfield City; Blacktown' because it spans two. Twenty-nine distinct
-- values across ninety-three sites.
--
-- A loader that quietly normalised these would be making an unsourced
-- editorial judgement about which council a site sits in, and would do it
-- invisibly. So it does not: sites load with the LGA their source states, the
-- loader reports every value it cannot match, and a human resolves them here.
--
-- Seeded empty on purpose. Until a human fills it, the council column shows
-- both forms — visibly wrong, which is recoverable, rather than invisibly
-- wrong, which is not. Approval is recorded for the same reason
-- council_watchlist records it.
create table facts.lga_aliases (
  alias       text primary key,
  canonical   text not null,
  approved_by text not null,
  approved_at timestamptz not null default now(),
  note        text
);

comment on table facts.lga_aliases is
  'Human-approved council name equivalences. Empty until a human fills it; the
   loader never writes here and never guesses.';

-- 3. A record of every load.
--
-- The pipeline keeps an ingest_log; this is its counterpart on the serving
-- side. source_digest is the SHA-256 of the pipeline database the load came
-- from, which makes "which build of the research is on screen right now" a
-- question the database can answer.
create table facts.ingest_runs (
  id             uuid primary key default gen_random_uuid(),
  run_at         timestamptz not null default now(),
  source_system  text not null,
  source_digest  text not null,
  loader_version text not null,
  rows_by_table  jsonb not null,
  notes          text
);

create index ingest_runs_run_at_idx on facts.ingest_runs (run_at desc);

comment on column facts.ingest_runs.source_digest is
  'SHA-256 of the pipeline artefact this load read, so a published figure can
   be traced to the exact build that produced it.';
