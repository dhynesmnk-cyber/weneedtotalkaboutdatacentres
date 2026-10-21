# Hunt logs

One log per research question, `RG-nnn.md`, recording how it was worked: every
search and fetch, every refusal, every document archived, every dead end. The
plan that requires them is `docs/RESEARCH-PLAN.md`; the story cards in
`editorial/stories/` are written from them.

A log is a working record, not a source. Facts in it point at the source ids
and archives that hold them. Leads from search-engine summaries, social posts or
unarchived pages go only under **Leads**, and never become facts.

## Format

```markdown
# RG-nnn: short title

Question: the question as the research agenda states it.
Status: open | in_progress | resolved, as at the last entry.

## Log
- YYYY-MM-DD: what was done, what came back, where it is archived (SHA-256 prefix).

## Refused or restricted
- what refused, how (401, 403, robots.txt, paywall, restricted attachment), and what was not tried.

## Leads (not facts)
- what a summary or post suggested, and where it came from.

## Outcome
What the records now say, by row, and what remains open.
```

Logs for RG-099 and RG-100 were reconstructed on 2026-10-21 from the archives,
the curation scripts' notes and the working session, because their hunts
predate this format. From Batch 1 on, a log is kept as the work happens.
