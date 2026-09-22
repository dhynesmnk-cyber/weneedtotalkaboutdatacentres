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

## Candidates flagged by the loader

Counts are sites carrying each spelling, from the live database on 2026-09-22.

| Spelling A | Sites | Spelling B | Sites | Confidence |
| --- | ---: | --- | ---: | --- |
| `Blacktown` | 11 | `Blacktown City Council` | 4 | high |
| `Penrith` | 4 | `Penrith City Council` | 4 | high |
| `Lane Cove` | 5 | `Lane Cove Council` | 1 | high |
| `Fairfield City` | 2 | `Fairfield City Council` | 1 | high |

Each pair differs only by the presence of the `City`/`Council` suffix on an
otherwise identical name, which is the ordinary short-form/legal-name split.

---

## Candidate the loader did not flag

| Spelling A | Sites | Spelling B | Sites | Confidence |
| --- | ---: | --- | ---: | --- |
| `The Hills Shire` | 1 | `Hills Shire Council` | 2 | high |

**This one is worth a second look, because the detector missed it.**
`scripts/ingestion/load-pipeline.ts:168` flags an LGA when some other value
*starts with* it:

```ts
lgas.filter((lga) => lgas.some((other) => other !== lga && other.startsWith(lga)))
```

That catches a suffix being added — `Blacktown` against `Blacktown City
Council` — and it is why the reported list holds only the shorter member of
each pair. It cannot catch a difference at the front. Neither
`Hills Shire Council` nor `The Hills Shire` is a prefix of the other, so
neither is reported.

The consequence is narrow, but it means the loader's variant list is a floor
and not a total, in the same way `count_patent_filings.py` reports its counts
as a floor. Anyone reading that list as exhaustive would be wrong.

Fixable in the loader by normalising a leading article before the comparison.
Not done here: changing the detector changes what every future load reports,
which deserves its own review rather than riding along with a documentation
change.

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
