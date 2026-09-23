# LGA_ALIAS_CANDIDATES.md

## Status: APPROVED — all five, by David on 2026-09-23

These five equivalences are now rows in `facts.lga_aliases`, each carrying
`approved_by = 'David'`. They were drafted under the `researcher` role in
docs/SUBAGENTS.md, which proposes and never approves, and approved on David's
explicit instruction.

The table remains human-approved: CLAUDE.md and migration `0010` both state that
no import writes to it, and that is unchanged. A sixth pair would follow the
same route — proposed here, approved by a person, then inserted.

This file is kept as the record of what was decided and why, not as a pending
worklist.

### Why the table matters
`docs/QUALITY.md` grades the GovMarket aggregator C precisely because it merges
spelling variants of one entity without saying so. The alias table is how this
project does the same job honestly: the merge is recorded, attributed and
publishable, and RLS exposes it so a reader can check which names were treated
as equivalent and who decided.

The pipeline still loads both spellings verbatim; the alias table records the
equivalence rather than rewriting the data, so the counts below remain as
loaded. Nothing in `app/`, `components/` or `lib/` resolves through the table
yet — wiring the site list and any council join to it is separate work.

### How a further pair would be approved
Decide which spelling is canonical, then insert a row:

```sql
insert into facts.lga_aliases (alias, canonical, approved_by, note)
values ('<alias>', '<canonical>', '<your name>', '<why>');
```

Approval is per pair, not per batch.

### The direction chosen, and what it does not claim
`canonical` is the **fuller council form** in every pair — one rule applied
consistently. The short form is ambiguous outside context (`Blacktown` is also
a suburb) while `Blacktown City Council` can only be the council. The short
form does hold the larger share of sites in three of the five pairs, so this
was a choice against the majority spelling, made for unambiguity.

**No canonical value is asserted to be a council's legal name.** No register was
read, so no such claim is made, and each row's `note` records the site counts at
approval rather than a source for the name.

`The Hills Shire` is where that distinction bites, and its note says so: the
legal name is believed to carry a leading article that the canonical value
(`Hills Shire Council`) does not. Revisit that one with a register as source
before any canonical value is published as an official name.

---

## The five, as approved

All five are reported by `npm run load:pipeline`, with site counts, since the
detector was rewritten on 2026-09-22. Counts below are from the live database
on that date; `canonical` is the right-hand column.

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
