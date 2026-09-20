-- 0005: widen the site status vocabulary to the one the research uses.
--
-- The curation pipeline (data-pipeline/) distinguishes five lifecycle states
-- this enum could not represent. Flattening them into 'proposed' and
-- 'withdrawn' would destroy real research: a refused application and a
-- withdrawn one are different outcomes, and a rumoured site is a weaker claim
-- than a lodged one. See docs/PIPELINE_MAPPING.md.
--
-- 'operational' in the pipeline and 'operating' here are the same state spelled
-- two ways. That one is reconciled in the mapping layer, not by adding a
-- synonym to this enum.
--
-- This migration adds enum values and does nothing else, deliberately. A value
-- added by ALTER TYPE cannot be used until the adding transaction commits, so
-- any migration that references these must come after this one.

alter type facts.site_status add value if not exists 'rumoured'      before 'proposed';
alter type facts.site_status add value if not exists 'pre_lodgement' before 'proposed';
alter type facts.site_status add value if not exists 'lodged'        after  'proposed';
alter type facts.site_status add value if not exists 'refused'       after  'stalled';
alter type facts.site_status add value if not exists 'cancelled'     after  'withdrawn';
