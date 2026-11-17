-- ADCO schema migration 03: the PEOPLE register
-- 2026-11-17
--
-- WHY THIS TABLE EXISTS
-- ---------------------
-- The site publishes people by public role only, never by name, until legal review is
-- arranged (CLAUDE.md, hard rules). The research database is the workshop and may hold
-- names; the site may not. Until now the names were scattered: in lobbying.person ("Name,
-- role"), in case_handling.officer_name, and loose in source titles, entity names, site
-- notes and research questions, where nothing could find them to withhold them.
--
-- This register lists every named person the published record mentions that the lobbying
-- and case-handling tables do not already cover, with the public role the site publishes in
-- place of the name, and the record that states that role. It also overrides a role those
-- tables give where that role is not fit to publish as a label (too long, or not a role).
--
-- The loader (scripts/ingestion/load-pipeline.ts, lib/ingestion/people.ts) reads this table
-- together with lobbying.person and case_handling.officer_name, replaces each name in every
-- published text field, and refuses to write the load if any listed name survives.
--
-- Journalists' bylines in sources.publisher are deliberately not listed: a byline is a
-- citation's authorship, not a person appearing in our content (the author, 2026-11-17).

CREATE TABLE IF NOT EXISTS people (
    id            TEXT PRIMARY KEY,            -- PER_xxx, named for the role, never the person
    name          TEXT NOT NULL,               -- as the documents spell it
    aliases       TEXT,                        -- other spellings found in the record, '|' separated
    role          TEXT NOT NULL,               -- the public role the site publishes instead
    organisation_id TEXT REFERENCES entities(id),
    notes         TEXT,
    fact_status   TEXT NOT NULL DEFAULT 'VERIFIED' CHECK (fact_status IN
                    ('VERIFIED','REPORTED','CLAIMED','GAP')),
    source_id     TEXT REFERENCES sources(id),  -- the record that states the role
    confidence    TEXT CHECK (confidence IN ('high','medium','low')),
    as_of_date    TEXT
);
