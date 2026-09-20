# PIPELINE_MAPPING.md

How the curation pipeline in `data-pipeline/` maps onto the Postgres fact layer,
and why each decision was made that way.

This document exists because the mapping is where fabrication would enter if it
entered anywhere. A rename is harmless. A reinterpretation — recording a refusal
as a withdrawal, or filling an empty column from a nearby one that looks similar
— puts a claim in front of a reader that no source ever made. Every decision
below is therefore argued, not just recorded.

## The arrangement

Postgres is the serving source of truth: it is what the website reads, and
nothing else. The pipeline is the upstream curation tool, where research is
gathered, sourced and graded before it is loaded.

That resolves the contradiction created when the pipeline was merged into this
repository on 18 September 2026. `CLAUDE.md` forbids a second database; a SQLite
database had nonetheless arrived in `main`. It is not a second source of truth —
it is the workshop, and Postgres is the shopfront.

## The governing rule

**A mapping may rename. It may never reinterpret.**

Where the two systems genuinely disagree about what a value means, the value is
carried across intact and the Postgres schema is widened to hold it. Where a
value has no honest destination, `lib/ingestion/vocabulary.ts` throws
`UnmappedValueError` and the load fails. Nothing is mapped to a near-enough
value.

## Site status

The pipeline distinguishes five lifecycle states the original six-value enum
could not represent. Migration `0005_status_vocabulary.sql` adds them rather
than flattening them.

| Pipeline | Postgres | Decision |
| --- | --- | --- |
| `operational` | `operating` | The only rename. Same state, two spellings. |
| `approved`, `under_construction`, `withdrawn` | unchanged | Identity. |
| `lodged` | `lodged` | **Added.** An application before an authority. |
| `pre_lodgement` | `pre_lodgement` | **Added.** In discussion, not yet lodged. |
| `refused` | `refused` | **Added.** See below. |
| `cancelled` | `cancelled` | **Added.** Abandoned after approval. |
| `rumoured` | `rumoured` | **Added.** See below. |
| — | `proposed`, `stalled` | Postgres-only. No load produces them; a human may. |

Two of these carry the argument:

**`refused` is not `withdrawn`.** A refusal is an authority stopping a project.
A withdrawal is a proponent stopping it. Mapping one onto the other would not
lose precision — it would tell the opposite story about who decided, which is
exactly the kind of claim this observatory exists to get right.

**`rumoured` is not `proposed`.** A rumour is an unverified report. A proposal is
a formal act. Promoting one to the other would manufacture the gap between
public perception and research data that the project was built to expose.

`stalled` stays because `docs/SPEC.md` calls it load-bearing, and because it is
a human editorial judgement about a project that has gone quiet — not something
an importer can determine.

## Capacity: four figures, never aggregated

The pipeline records up to four capacity figures per site, and its README
forbids combining them because they measure different things:

| Field | Means |
| --- | --- |
| `it_capacity_mw` | Load available to racks. A design rating. |
| `total_capacity_mw` | Site draw including cooling and losses. |
| `max_capacity_mw` | The ceiling the connection or consent permits. |
| `first_phase_mw` | What stage one delivers. |

Migration `0008_site_fields.sql` adds the three that were missing and
deliberately adds **no cross-field CHECK** between them. That is not an
oversight. `SITE_WESTERN_DOWNS` is a real, sourced row with a total of 3,240 MW
and a max of 2,160 MW; a `total <= max` constraint would reject it, which is the
proof that the constraint would be wrong rather than the data.

### `live_capacity_mw` is never populated

This is the trap the whole mapping is built around. `it_capacity_mw` is sitting
right there and looks like it would do. It would not: IT capacity is a design
rating, live capacity is what is energised today. Filling one from the other
would put a figure in front of a reader that nobody published.

It is enforced three times over, because a comment is not a guarantee:

- `NEVER_POPULATED` in `lib/ingestion/vocabulary.ts` names it and says why.
- A unit test asserts `transformSite` never emits it, even when
  `it_capacity_mw` is present.
- An assertion inside the load transaction rolls the entire load back if any
  loaded row has one.

The existing `sites_live_within_total` CHECK is untouched and still correct: the
pipeline has no live figure, so the column imports as null and the check passes
vacuously.

## Provenance

`0006_provenance.sql` carries the pipeline's grading across rather than
discarding it. These are **not** a second citation mechanism — `facts.citations`
remains the only path from a record to a source. They describe the strength of a
claim that is already cited.

| Pipeline | Postgres | Note |
| --- | --- | --- |
| `fact_status` VERIFIED/REPORTED/CLAIMED/GAP | `facts.fact_status` | Lower-cased. Ordered weakest to strongest. |
| `confidence` high/medium/low | `facts.confidence_level` | Verbatim. |
| `credibility` A–D | `facts.source_credibility` | Verbatim, on sources. |
| `as_of_date` | `sites.as_of_date` | The date a claim is good as at, **not** the retrieval date. |

`GAP` is preserved rather than dropped: a value established as absent is a
different record from one nobody has looked at.

Seven sites and three entities are `claimed` — a proponent's assertion nobody
has confirmed. Without the status they would render identically to a figure
parsed from a planning consent. `formatFactStatus` renders it as "Claimed by
proponent" for that reason.

## Citations come from two places

`source_refs` covers only 65 of the 93 sites, but all 93 carry a row-level
`source_id`. Both are imported: the row-level source as the site's primary
citation, plus each `source_ref` as an additional one. Importing `source_refs`
alone would leave 28 sites uncited and therefore unpublishable.

A site with no source is **rejected**, not imported uncited.

**`source_refs.quote` is not mapped onto `citations.claim`.** A quote is a
verbatim extract; `claim` names the specific assertion a source supports, and
`citationCoverage()` matches it against field names. Mapping one to the other
would manufacture field-level coverage the research does not have. All 376
`source_refs` have an empty quote today in any case, so `claim` imports as null
and imported citations are record-level. Reaching claim-level auditability is
curation work in the pipeline, not something the loader can invent.

## Gaps: two different things with similar names

| | Holds | Answers |
| --- | --- | --- |
| `facts.data_gaps` | Per-field absence + reason | "This field is empty, and here is why" |
| `facts.research_agenda` | An open question + why it matters | "We have not answered this yet" |

The pipeline calls the second one `research_gaps`, which is where the confusion
would come from. It is named differently here on purpose
(`0009_research_agenda.sql`), and its internal `owner` column is **not**
imported: who is assigned a task is workflow, not a finding, and the table is
publicly readable.

The pipeline has nulls, not gap records, so `data_gaps` rows are **derived** at
load: one per null factual field, with reason `unknown` and no stronger reason.
`docs/SPEC.md` defines `unknown` as "not yet researched, or researched without
result", which is exactly and only what a pipeline null asserts. Anything
stronger — `not_disclosed`, `withheld` — is a claim about the world that needs a
human and a source; deriving one would invent evidence of an event that may
never have happened.

Emitting no gaps instead would be worse than it looks: every site page would
paint its blanks with `UnexplainedBadge`, labelling ordinary unresearched fields
as data-quality defects. The derivation adds no information — it restates in the
schema's vocabulary what a null already said.

## Council names are loaded verbatim

The research records councils as its sources name them, so `Blacktown` and
`Blacktown City Council` both appear, along with `Fairfield City`,
`Fairfield City Council`, and one site recorded as `Fairfield City; Blacktown`
because it spans two. Twenty-nine distinct values across ninety-three sites.

The loader **reports** these and loads them unchanged. Canonicalising them
silently would be an unsourced editorial judgement about which council a site
sits in, made invisibly. A human resolves them by adding rows to
`facts.lga_aliases`, which records who decided.

Until that happens the council column shows both forms. That is visibly wrong,
which is recoverable; the alternative is invisibly wrong, which is not.

## Identity

Pipeline natural keys (`SITE_MAMRE_ROAD`) become UUIDv5 values derived from a
pinned namespace, carried alongside in `pipeline_id` (`0007`). This makes loads
idempotent — proven by applying the artefact twice in `scripts/test-load.sh` —
and lets a published record be traced back to the build that produced it via
`facts.ingest_runs.source_digest`.

**Deletion is never automated.** A site that disappears from the pipeline is
reported, not deleted. Removing a published record is a human act with the same
standing as publishing one.

## What is deliberately not mapped yet

`applications`, `modifications`, `lobbying`, `incentives`, `legal_instruments`,
`metrics`, `power_profile`, `water_profile` and the consultancy layer have no
destination table. Their `source_refs` are **reported as skipped**, not dropped
silently, so the count of what is not yet served is visible on every run.

## Running it

```bash
npm run load:pipeline -- --dry-run        # report only, writes nothing
npm run load:pipeline                      # emit .artifacts/load-pipeline.sql
npm run test:load                          # migrations + load + load again + assert
```

The loader emits SQL rather than writing to a database. A human reads the diff
before anything reaches the data — which is how "no agent publishes content"
becomes a guarantee rather than an assertion.

To regenerate `tests/fixtures/loaded-site.json` after a pipeline rebuild, run
`KEEP_TEST_DB=1 npm run test:load` and re-run the dump query recorded in
`scripts/ingestion/dump-fixture.sh`.
