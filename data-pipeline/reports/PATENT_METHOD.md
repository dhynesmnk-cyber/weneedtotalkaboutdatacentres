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

One limitation to plan around: IPGOD/IP RAPID is **bibliographic and process data** — who filed
what, when, and what happened to it. Topic modelling needs the *text* of the specification. So
acquisition is two-stage:

1. **IP RAPID / IPGOD** (data.gov.au) to resolve the assignee and filing layer — which is also the
   cheapest way to test the finding above properly, by counting filings per operator against the
   register rather than against a search engine.
2. **AusPat** (`ipsearch.ipaustralia.gov.au/patents/`), EPO OPS or USPTO bulk for full specification
   text, for whichever subset stage 1 says is worth reading.

No scraper was written for either. There is already one never-run scraper in this repo
(`ingest_austender.py`); adding a second untested one would be speculative machinery. Acquisition
should be built by whoever can test it against the live source.

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

Resolve design decision 1, then acquire stage-1 data from IP RAPID and count filings per operator
against the register. That single count either confirms or overturns the finding at the top of this
document, and it is cheap. Everything else depends on it.
