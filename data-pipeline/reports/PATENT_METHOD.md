# The patent-corpus method, applied to data centre operators

**Status: method built and validated; not yet run on patents.** No patent source is reachable from
this environment. What follows is the method transplant, the design decisions it forces, and one
finding that changes what the method is for.

The source method is Iliadis & Acker (2022), assessed in `reports/palantir_australia_triage.md`:
assemble a patent corpus, preprocess it, topic-model it with Latent Dirichlet Allocation, then
interpret the topics into themes. Their corpus was 155 Palantir patents containing the word
"ontology", scraped from Google Patents.

## The finding: it does not transplant to the operators

The obvious reading of "apply it to the data centre operators" is to swap Palantir's assignee name
for NEXTDC's and re-run. That does not work, and the reason is worth recording.

The operators this project actually tracks, by sites held in the database:

| Entity | Sites | Type |
|---|---|---|
| NEXTDC | 13 | colocation_operator |
| CDC Data Centres | 7 | colocation_operator |
| Equinix | 5 | colocation_operator |
| Macquarie Technology Group | 4 | colocation_operator |
| AirTrunk | 4 | colocation_operator |
| Stockland | 3 | developer |
| Telstra, Syncline, STACK, Microsoft, Goodman, Digital Realty, DCI | 2 each | mixed |

Searching for patent portfolios held by the Australian-domiciled operators — NEXTDC, AirTrunk, CDC
— surfaced **none**. CDC Data Centres Pty Ltd appears in trademark records, **not** patent records.
Equinix, by contrast, does hold data centre patents, including rack arrangement for cooling
efficiency and a sealed convective-cooling chamber. This is not an absence of evidence problem
with an obvious fix: it is what you would predict. **These firms are infrastructure operators and
property developers, not research and development companies.** They buy plant; they do not patent
it.

So the patent layer and the site layer describe **different populations**. The 93 sites are held
by operators who file few or no patents. The patents that govern how those sites are cooled and
powered are held by a different set: the hyperscalers (Microsoft, Amazon, Google), the
international operators (Equinix, Digital Realty), and above all the equipment vendors who appear
nowhere in this database.

That is not a reason to abandon the method. It is a reason to be precise about the question it
answers. Applied here, a patent corpus is evidence about **equipment and hyperscaler design
intent** — what the industry is building toward — and not about any Australian site. Anyone who
runs it expecting a finding about NEXTDC will get nothing, correctly.

## The caveat that matters most

**A patent is an imagined capability, not an installed one.** Iliadis & Acker are explicit that
their corpus shows how Palantir "plans, imagines, and speaks about" its capabilities. Only 51 of
their 155 patents were even granted.

For this project that has a hard consequence. A cooling patent held by an operator is **not**
evidence that any site uses that cooling. Treating it as such would be the same error the schema
already refuses when it forbids populating `live_capacity_mw` from `it_capacity_mw`: one is what
is energised, the other a design rating. A patent is a third thing, weaker than both — a design
*aspiration*, filed, sometimes not granted, often never built.

So: a patent may be cited as VERIFIED evidence that **a filing exists and says what it says**. It
may never populate a site field, a capacity, a cooling type or a water figure. If the method ever
produces a pack, this is the line it must not cross.

## Corpus acquisition: the route is IP Australia, not Google Patents

Iliadis & Acker scraped Google Patents. For an Australian-scoped observatory there is a better
source, and it is a primary one.

**IP Australia publishes Intellectual Property Government Open Data (IPGOD)** on data.gov.au —
over 100 years of applications across patents, trade marks, designs and plant breeder's rights,
with derived applicant information, across up to 40 tables. IPGOD has been **superseded by IP
RAPID**, a weekly-updated release of the same product. That is `primary_government`, credibility
**A**, versus a scrape of a commercial search interface.

**Correction to an earlier draft of this document.** It said IPGOD carries only bibliographic and
process data, so that specification text would have to come from a second source. That was wrong
and it changed the plan for the worse. IPGOD's published table list includes:

| Table | Contents |
|---|---|
| IPGOD 101 | Patents summary |
| IPGOD 102 | Patents **applicant** information |
| IPGOD 103 | Patents application information |
| IPGOD 107 | Patents process information |
| IPGOD 122B | Patents **abstract** information |

122B is abstract *text*. Abstracts are a standard and defensible corpus for patent topic
modelling, so **one primary source covers both stages** — 102 for the filing count, 122B for the
topic model — and neither requires scraping a commercial search interface. Full specification text
from AusPat, EPO OPS or USPTO bulk becomes an optional third stage, for whichever subset turns out
to be worth reading closely, rather than a prerequisite.

Acquisition is still not built, and deliberately: every IP Australia and data.gov.au endpoint is
blocked from here, so a fetcher could not be tested. There is already one never-run scraper in
this repo (`ingest_austender.py`) and a second would be speculative machinery. Download the
extract by hand from data.gov.au; the analysis scripts read local files and never fetch.

## Stage 1 is built, and cannot be run here

`scripts/count_patent_filings.py` takes an IPGOD 102 / IP RAPID applicant extract and counts
distinct filings per tracked operator. **It has not produced a count, because the extract cannot
be downloaded from this environment.** No number in this document comes from IP Australia.

The counting is trivial. The real problem is **name matching**, and the project has already
recorded what failure looks like there: `SRC_GOVMARKET_TCS` is graded C precisely because the
aggregator "consolidates 14 spelling variants of the TCS name into one master entity", and its
totals are inflated by a duplicate. Silent consolidation is the defect.

So the script refuses to do it:

- The match table is built **from the database only** — `entities.name`, `entities.legal_name` and
  the human-curated `entity_aliases`. It invents no names. Against the current database that is 31
  name forms for the 25 site-holding entities.
- A row counts only on an **exact match after conservative normalisation** — case, punctuation, and
  trailing legal-form suffixes, so "NEXTDC Limited" meets "NextDC Ltd."
- Anything that merely shares a leading word is reported as a **candidate for human review** and
  counted nowhere. `Nextdc Holdings Pty Ltd` does not become NEXTDC. Promoting a candidate is a
  human act recorded in `entity_aliases`, exactly as `lga_aliases` works for councils.
- Consequently **the counts are a floor, not a total**, and the generated report says so on its
  face.

The IPGOD column names could not be verified either, so rather than hard-code a guess the script
detects the applicant and application-number columns from the header, prints what it chose, and
takes `--name-col` / `--id-col` overrides.

`make check-filings` covers this with fixtures, including the load-bearing negative: a near-miss
name must not be absorbed into a tracked entity. It also asserts that repeated application numbers
are deduplicated, since an applicant table has one row per applicant per application and a
two-applicant filing would otherwise count twice.

## What was built and what it proves

`scripts/analyse_patents.py` implements the analysis half, dependency-free — a collapsed Gibbs
sampler for LDA in standard library Python, because the Makefile promises nothing beyond the
standard library and openpyxl, and a scikit-learn import would break that for one script. It is
seeded, so the same corpus and seed give the same topics; a build that cannot be reproduced cannot
be verified.

**It is validated.** `make check-patents` plants four topics with disjoint vocabularies — cooling,
power, water, network — in a synthetic corpus, and asserts the model recovers them. It currently
recovers all four at 10 of 10 terms, mapping one-to-one. The test has a real ground truth and can
fail: disabling the sampler so it always assigns topic 0 fails five of the checks, which was
verified by mutation rather than assumed, per the standard in docs/QUALITY.md.

**What it does not prove**, stated because the limits of a green test are easy to overclaim:

- It has never seen a patent. The preprocessing, in particular the `PATENT_BOILERPLATE` stoplist,
  is **reasoned, not tuned**. Patent prose is heavily formulaic and those words otherwise dominate
  every topic — the model recovers the genre instead of the subject. Expect to revise the list
  against a real corpus.
- The synthetic test validates **the sampler, not the stoplist**. Emptying `PATENT_BOILERPLATE`
  still recovers all four planted topics, because the planted noise is uniformly distributed in a
  way real boilerplate is not. Only a real corpus can tune that list.
- Topic *stability* is untested. Iliadis & Acker's n=155 is small for LDA, and they resolved 20
  topics into 3 themes by hand. Any real run should check whether topics survive a change of seed
  before anything is claimed from them.

## Design decisions the first real run has to make

These are the method's actual content, and none has a default worth guessing:

1. **Scoping.** Iliadis & Acker fixed the assignee (Palantir) and filtered by one keyword
   ("ontology"). Here the choice is inverted and harder: the assignee set is the open question, so
   the corpus is probably keyword-scoped across many assignees — cooling, PUE, water recovery,
   power distribution — with the assignees falling out as a result.
2. **Applications or grants.** Only a third of the source corpus was granted. For this project the
   *application* may be the more interesting artefact, since it records design intent at a date,
   and lag between priority and grant ran to 12 years in their sample.
3. **Jurisdiction.** Their corpus was 117 US filings against one via Australia. An Australian
   observatory scoping to Australian filings would get a near-empty corpus; scoping to US filings
   answers a question about global equipment design that only indirectly touches Australian sites.
4. **What a topic licenses.** Topics are unnamed by construction and naming them is interpretation,
   not measurement. The script prints that warning into every report it writes.

## Next step

Download IPGOD 102 (or the IP RAPID equivalent) from data.gov.au and run:

```bash
python3 scripts/count_patent_filings.py --extract <file> --out reports/patent_filings.md
```

That single count either confirms or overturns the finding at the top of this document. Read the
review-candidate list before believing the totals: if it is long, the floor is well below the
truth and the gap is `entity_aliases` work, not a finding about patenting behaviour.

Then resolve design decision 1 and pull IPGOD 122B abstracts for the assignees that survive.
