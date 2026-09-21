# Palantir in Australia — source triage

**Status: UNVERIFIED LEADS. Nothing in this document is in the database, and nothing in it may be
published as fact.** Compiled 2026-09-21 from a supplied 13-entity list plus web search.

## The evidentiary floor, stated first

Every line below sits *below* the project's grade D. The authoring environment could not fetch a
single one of these pages: `tenders.gov.au`, `investors.palantir.com`, `itnews.com.au`,
`abc.net.au`, `defenceconnect.com.au`, `theirstack.com`, `capitalbrief.com`,
`appsruntheworld.com` and `greens.org.au` were all blocked by the egress proxy, and so was every
other domain tried. What follows was assembled from **search-engine result summaries** — not from
the documents, and not even from the reporting about the documents.

The project's ladder is VERIFIED (primary document read) → REPORTED (credible secondary read) →
CLAIMED (assertion) → GAP. A summary of a search index is not on that ladder at all. So the
column below is **corroboration**, meaning how many mutually independent routes point the same
way, and it is a measure of where to look, never of what is true.

This document is a **fetch list and a triage**, to be consumed by `scrapers/ingest_austender.py`
and by a human reading primary records. It is not a curation pack and must not become one without
re-reading the underlying documents.

## What this has to do with data centres

The supplied list is a customer roster, and a customer roster is not on its own in this project's
scope. One thing found while checking it is:

> Palantir Platform Australia (PPA) delivers Foundry and AIP **hosted in Australian Amazon Web
> Services regions**, following Palantir's **IRAP PROTECTED** assessment (announced via Business
> Wire, release id dated 20 November 2025).

That is the hook, and it runs the other way from the roster. It makes Palantir a **demand-side
tenant of Australian hyperscaler capacity**: Commonwealth PROTECTED-level government workloads and
a set of large enterprise workloads landing in AWS Australian regions. That connects to RG-013
(hyperscaler site resolution, where **zero** of the 46 NSW data centre SSD records is titled AWS,
Amazon, Google or Meta) and to the CER series already in the database (Amazon scope 2 **+202%**
over five years). Which physical sites PPA actually runs in is unknown and is the question worth
opening — the customer names are a proxy for the size of the load, not the finding.

Treat the roster as evidence of demand, not as an end in itself.

## Triage of the supplied 13

Corroboration: **multi** = several independent secondary routes agree; **single** = one route;
**aggregator** = only a technographic or buyer-intent vendor; **none** = nothing found.

| # | Entity | Corrob. | Finding |
|---|---|---|---|
| 1 | Rio Tinto | multi | Supported. Reported as running Foundry **on AWS** for rail and SAP data. The AWS detail is the useful part. |
| 2 | WesTrac | multi | Strongest commercial entry: Palantir's **own press release** exists, so this is the one item that can reach grade A by reading a single primary document. Foundry across servicing and rebuild operations centres, **Perth, WA**. |
| 3 | Westpac | multi | Supported. Named alongside Coles and Rio Tinto in Crikey's 8 Jul 2025 piece. No contract detail found. |
| 4 | Qantas | **none** | **Not corroborated.** Targeted searching returned nothing on a Qantas deployment. Rests on the supplied Capital Brief and TheirStack citations alone. Do not carry forward without reading Capital Brief directly. |
| 5 | Transurban | aggregator | **Unsupported as stated.** The cited source is a **buyer-intent** engine, which models who is *likely to purchase*. That is a prediction, not a deployment. Drop or re-source. |
| 6 | Coles | multi | Supported, but **the supplied description is wrong on three counts** — see below. |
| 7 | Nuix | **none** | **Unsupported.** Supplied uncited; searching found no Palantir partnership or integration. Both firms merely operate in analytics. Drop unless a primary source appears. |
| 8 | Nixil | single | Real Australian firm; **verifiably advertises for "Senior Palantir PySpark Developer"** roles working in Foundry (ZipRecruiter, LiveHire). But **"certified Palantir deployment partner" is unconfirmed** — hiring for a skill is not certification. Downgrade the claim, keep the entity. |
| 9 | VMO (Val Morgan Outdoor) | aggregator | **Unsupported as stated.** TheirStack is technology *detection*, inferred from signals like job ads and DNS. Not evidence of a commercial relationship. |
| 10 | Department of Defence | multi | Strongly supported and **richer than supplied**: **$7.6m, one year, published on AusTender 11 February 2026, limited tender** (no open market approach), for an "ICT System Platform" for the **Cyber Warfare Division**, embedding Foundry in the **Industrial Intelligence Capability**. Context found: **~$26m since 2023-24** and **~$50m in federal contracts since 2016-17**. |
| 11 | AUSTRAC | multi | Strongly supported and **much richer than supplied**: original **$7.5m, 2017**, Gotham and Foundry, ended **31 Dec 2022** at a final **$8.6m**; **$8.1m** renewal 2023; **five variations in 12 months** taking it past **$12m**; a **+$2.75m** amendment published **9 Jan 2026**; a separate **$1.9m** implementation and sustainment contract published **18 Feb 2026**. |
| 12 | Vic Dept of Justice and Community Safety | aggregator | **Weak.** The only route found is the same buyer-intent vendor, asserting Foundry adoption in 2021. No Victorian primary record surfaced. |
| 13 | Victorian Government (broad base) | single | **Citations misattributed.** The two `tenders.gov.au/Cn/Show/...` URLs filed here are **Commonwealth** notices (CN4220255 and CN3942923-A1) that surfaced against **AUSTRAC**, not Victoria. A genuine Victorian item exists and was missed: the **Victorian Government used Palantir to analyse COVID data** (ACS *Information Age*, 2022). |

## The Coles entry is wrong in a way worth naming

Supplied: *"Signed a 3-year deal in 2024 ... though the collaboration concluded prematurely in late
2026."*

What the reporting says:

- Signed **February 2024**; Foundry and AIP across **840+** stores (supplied: "850+"), covering
  rostering, bakery production, trading performance, store operations and supply chain.
- Coles announced in **early September 2026** that it **will not extend beyond 2027**.
- It has therefore **not concluded**. Coles is reported to be "still working through plans to
  transition away".
- The reason is omitted from the supplied entry: a **public pressure campaign** over Palantir's
  work with US Immigration and Customs Enforcement and with militaries and intelligence agencies.

"Concluded prematurely in late 2026" is, on today's date of 21 September 2026, a claim about a
month that has not happened, describing an ending that has not occurred. It is the kind of error
that survives being repeated and does not survive being checked, which is the whole reason this
project reads primary documents.

## Entities the supplied list missed

Searching surfaced Commonwealth customers absent from the 13:

- **Australian Signals Directorate**
- **Department of Veterans' Affairs**
- **Australian Criminal Intelligence Commission** — reported as deepening through successive
  contract variations, the same "contract creep" pattern as AUSTRAC
- **buy.nsw supplier profile 3813**, Palantir Technologies Australia Pty Ltd — a NSW procurement
  presence, on the same portal RG-072 already needs for the TCS reconciliation

A roster assembled from technographic vendors is both **over-inclusive** (three of thirteen are
aggregator artefacts) and **under-inclusive** (it misses four real government relationships). That
is the characteristic failure of aggregators, and it is the same finding the project already
recorded against GovMarket in SRC_GOVMARKET_TCS.

## Trap for the AusTender keyword search

**`palantirconsulting.com.au` is an unrelated Australian structural, façade and remedial
engineering consultancy.** A keyword search for "palantir" on any Australian procurement portal
will return false positives on this name. Any curation script written against the archive must
disambiguate on ABN or supplier identity, not on the string "palantir".

## Fetch list for the first live run

Primary and near-primary, in the order worth spending the first run on:

1. `https://www.tenders.gov.au/Search/KeywordSearch?keyword=palantir` — the register itself
2. `https://www.tenders.gov.au/Cn/Show/e95aa7ba10d64ad1b1d14596b8783479` — CN4220255
3. `https://www.tenders.gov.au/Cn/Show/824b951a-e5c5-4869-a4e5-6c6f4cf67af1` — CN3942923-A1
4. `https://buy.nsw.gov.au/supplier/profile/3813` — Palantir Technologies Australia Pty Ltd
5. `https://www.palantir.com/newsroom/press-releases/palantir-continues-expansion-in-australia-with-westrac-partnership/` — primary_company, grade A
6. `https://www.businesswire.com/news/home/20251120911748/en` — IRAP PROTECTED and the PPA-on-AWS statement, the load-bearing claim for this project's scope

Secondary, for attribution once read: Crikey (8 Jul 2025 roster; 17 Feb 2026 Defence), Canberra
Times (Defence limited tender; AUSTRAC $5.06m), ARN ($8.1m AUSTRAC extension), iTnews and ACS
*Information Age* (Coles), InnovationAus (Defence IIC), *The IJF* (Defence licences at a reported
$7.4m per year), ACS *Information Age* (Victorian COVID data, 2022).

## What must happen before any of this is loaded

1. Archive the primary records with `scrapers/ingest_austender.py` — which **has never been run
   against the live site** and whose first run is a human review step.
2. Read them. Grade them. Drop every entity whose only support is a technographic or buyer-intent
   vendor, or carry it explicitly as CLAIMED with the aggregator named, as SRC_GOVMARKET_TCS is.
3. Resolve the scope question: whether the finding is the **AWS-region hosting of PROTECTED-level
   Commonwealth workloads**, which is about data centres, or the customer roster, which on its own
   is not.
4. Only then curate a pack. `sources.accessed` means the date a human read the document.
