# LGA_ALIAS_CANDIDATES.md

## Status: UNAPPROVED — PENDING HUMAN SIGN-OFF

Nothing in this file changes any data. These are candidate equivalences for the
`facts.lga_aliases` table, drafted under the `researcher` role in
docs/SUBAGENTS.md, which proposes and never approves.

CLAUDE.md and migration `0010` both state that `lga_aliases` is human-approved
and that no import writes to it. Every row carries `approved_by`, and an agent
cannot supply a name for that column without inventing one. **So this file stops
at the proposal.**

### Why the table matters
`docs/QUALITY.md` grades the GovMarket aggregator C precisely because it merges
spelling variants of one entity without saying so. The alias table is how this
project does the same job honestly: the merge is recorded, attributed and
publishable, and RLS exposes it so a reader can check which names were treated
as equivalent and who decided.

Until a row exists, the pipeline loads both spellings verbatim and the site
counts below stay split across them. That is the intended behaviour, not a bug:
a split count is visibly wrong, whereas a wrong merge is invisible.

### How to approve
For each pair you accept, decide which spelling is canonical, then insert a row:

```sql
insert into facts.lga_aliases (alias, canonical, approved_by, note)
values ('Blacktown', 'Blacktown City Council', '<your name>', '<why>');
```

Approval is per pair, not per batch. Strike any you do not want.

### The direction is a real decision, not a formality
`canonical` is what the site list and any future council join will display, so
it is worth settling deliberately:

- **Official-name form** (`Blacktown City Council`) matches the councils'
  own legal names and the approved-council table in docs/SPEC.md, which will
  eventually need to join to these values.
- **Short form** (`Blacktown`) is what most planning-portal records use and
  what currently holds the larger share of sites in four of the five pairs.

A source for the official name belongs in the `note` column. I have not asserted
one, because no register was read from this environment.

---

## Candidates

All five are reported by `npm run load:pipeline`, with site counts, since the
detector was rewritten on 2026-09-22. Counts below are from the live database
on the same date.

| Spelling A | Sites | Spelling B | Sites | Confidence |
| --- | ---: | --- | ---: | --- |
| `Blacktown` | 11 | `Blacktown City Council` | 4 | high |
| `Penrith` | 4 | `Penrith City Council` | 4 | high |
| `Lane Cove` | 5 | `Lane Cove Council` | 1 | high |
| `Fairfield City` | 2 | `Fairfield City Council` | 1 | high |
| `The Hills Shire` | 1 | `Hills Shire Council` | 2 | high |

The first four differ only by a `City`/`Council` suffix on an otherwise
identical name, which is the ordinary short-form/legal-name split.

The fifth is the one that prompted the detector rewrite, and it is worth
knowing why it was invisible. The old check was a prefix test:

```ts
lgas.filter((lga) => lgas.some((other) => other !== lga && other.startsWith(lga)))
```

That sees a suffix being added — `Blacktown` against `Blacktown City Council` —
and nothing else. Neither `The Hills Shire` nor `Hills Shire Council` is a
prefix of the other, so neither was reported, and the list read as a total when
it was a floor.

`lib/ingestion/lga.ts` replaces it with a comparison key: case, punctuation, a
leading article and trailing body words (`Council`, `City`, `Shire`,
`Regional`) are all normalised away, and spellings sharing a key are grouped.
The key exists only for comparison and is never stored — it deliberately
discards what distinguishes two councils that genuinely share a stem, which is
why it may only ever suggest.

---

## Not aliases: multi-LGA cells

Two sites carry two council names in one field. These are **not** spelling
variants and must not be added to `lga_aliases`, which maps one name to one
canonical name.

| Value | Sites |
| --- | ---: |
| `Fairfield City; Blacktown` | 1 |
| `Penrith; Blacktown` | 1 |

A site on a boundary genuinely sitting in two LGAs needs a modelled
many-to-many, not a merge. Collapsing it to either council would assert a
jurisdiction nobody verified, and collapsing it to the joined string makes a
third fake council.

Recorded here so the decision is deliberate. The current behaviour — loading the
string verbatim — is the honest one until the schema supports two.

The loader reports these in a section of their own, under a warning not to
merge them. The old prefix test had no such separation: `Fairfield City;
Blacktown` starts with `Fairfield City`, so a cell naming two councils was part
of why a third name appeared on the variant list.
