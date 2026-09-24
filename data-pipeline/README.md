# Australian Data Centre Observatory (ADCO)

An open, queryable, source-linked database of the Australian data centre build-out: the physical
footprint, the capital behind it, the regulatory frameworks that permit it, and the friction it
generates. Built for policy critique and engineering analysis that can survive being checked.

**Release v2.1.0 · data as at 18 September 2026 · 1,241 data rows (+376 source refs) · 93 sites · 125 entities · 325 metrics · 117 catalogued sources (70 primary)**

v2.1.0 adds **the determination layer** and repairs a silent data-loss incident. The archived consent
texts had degraded — the dependency-free extractor cannot open AES-encrypted portal PDFs (2 of 20 yielded
zero characters) and splits numerals across glyph boundaries (Glendenning's 235 MW parsed as 23). All 20
instruments were sha256-verified against their fetch manifests and re-extracted with pypdf
(`scripts/reextract_consents.py`); the battery now has the full population behind it (reliable **20/20**;
generator-hours caps **17**; website disclosure **19**; PUE **7**). `determination_date` is populated on
all 20 rows and **RG-079 is resolved**: condition stringency is template-dominated and no officer effect
is detectable at n=20 — but Williams+Copas officer **15 of 20 determined consents**, both post-Guidelines
determinations were signed by one A/Director under a **delegation executed one day after the Guidelines
took effect**, and the Talavera Road IPC consent was published with `'[Name of Commissioner]'` signature
placeholders (RG-085). RG-065 resolved: all 20 Schedule 1 applicants parse — **11 of 20 consents are held
by consultancies or undisclosed vehicles**. Two more pipeline defects fixed: seed-stage `viewer/db.json`
and `reports/build_report.md` (now regenerated post-load by `scripts/finalize_docs.py`) and pack/driver
drift (now a build failure via `scripts/check_packs.py`). Register:
`exports/nsw_planning/nsw_dc_consent_determinations.csv`.

v1.8.0 completes the consent audit: `scripts/consent_condition_audit.py` indexed all **6,866 attachments
across 63 project nodes**, downloaded and tested **all 20 signed consents** for determined NSW data centre SSDs,
and ran a 21-test condition battery. **The NSW Data Centre Guidelines are cited in zero of eighteen reliably
extracted consents** — including the one approved a month after they took effect. PUE appears in 5, WUE in 4, a
renewable supply condition in 4, an NOx mass cap in 2. Four codenames resolved from Schedule 1 (Equinix
Hyperscale 2 (SY10), Macquarie Data Centres, Goodman, NEXTDC). **Two of my own earlier findings are retracted:**
website disclosure is standard practice (16/18), not a Glendenning distinction; and apparent demand-response
prevalence was a parser false positive matching a condition that *prohibits* diesel load curtailment. Also added
`scripts/extraction_audit.py` after discovering the PDF extractor silently under-yields on structured
publications — see `reports/extraction_audit.md`. *(v2.1.0: the battery now stands on all 20 extractions —
zero of twenty cite the Guidelines; website disclosure is 19/20.)*

v1.7.0 closes two more gaps from **signed consents**. RG-038: four consents spanning 2020–2026 show the
**200-hour generator condition is a Department standard**, not a regulatory gap — and that **installed back-up
generation exceeds the facility's entire load in every case** (Glendenning 267.45 MW against a 235 MW cap;
Davis Road 181.92 MW against 160.85 MW). Only one of four applicants is an operating company. RG-046: the
Guidelines convert *the proponent's own EIS commitments* into conditions, so they cannot reach s.4.55
modifications — **the framework has no ratchet**. An "ASIC certificate Amazon Corporate Services Pty Ltd" on the
Davis Road application is access-restricted and has reopened RG-023.

v1.6.0 reads Australia's largest data centre proposal from its **primary lodged application** (344 MB,
~870 pp, Urbis Town Planning Report V4 for WDDP Pty Ltd, 14 Aug 2026): 2,160 MW IT load against **3,240 MVA
total facility demand** — an implied design PUE of ~1.50, i.e. ~1,080 MW of non-IT overhead, more than S7's
entire IT load; "**primarily** air-cooled" (not 100%); **no reticulated town water**, so potable supply is by
**road tanker**; 981 MW of adjacent gas capacity; and Prescribed Project status being pursued in parallel under
the *SDPWO Act 1971* (Qld). The ABR resolves a six-entity Zerra stack in which two SPVs were incorporated
**four days before the report was dated** — the same pattern as Mamre Road's KNBDC trusts.

v1.5.0 adds three accountability findings. **Victoria's Development Facilitation Program** (Part 9A,
*Planning and Environment Act 1987*) sends data centre applications to the Minister, permits waiver of
planning scheme requirements, and removes VCAT merits review for objectors *and* review of permit conditions;
at NEXTDC M3 West Footscray objections fell from **80+ to 5** when the pathway changed. **Consent drift**: all
17 post-consent modifications to NSW data centre SSDs are recorded — 15 approved, including additional
generators and diesel storage at Roberts Road and a power consumption increase at Eastern Creek — and the NSW
Guidelines say nothing about modifications. **The water dispute is on the record**: DCA told the Legislative
Council the 25% figure "is not based in fact"; Sydney Water's Managing Director, asked directly, said "We do
[stand by it]". Plus the full inquiry record: terms of reference, 5 transcripts, 37 witnesses, report due
**3 November 2026**.

v1.4.0 resolves **RG-002** for the State Significant Development layer: `scrapers/ingest_nsw_dc.py` harvested
**all 46 data centre SSD records** from the NSW Planning Portal (case ids, stages, decisions, determination
dates and authorities, LGAs, descriptions, attachment counts), with every node JSON archived under a SHA-256
manifest. Sites went 57 → 91. Two findings only the harvest could produce: **zero** of the 46 is titled AWS,
Amazon, Google or Meta, so hyperscaler footprints cannot be mapped from planning titles; and **three**
applications were withdrawn — the only direct planning-record evidence of proposals that did not survive.
RG-007's FOI strategy is drafted at `reports/RG007_foi_strategy.md`.

v1.3.0 resolved **RG-026**: the signed consent for SSD-73761707 (Glendenning Road, 235 MW, 16 September 2026 —
one month after the NSW Data Centre Guidelines took effect) was read in full. It requires **all** operational
electricity demand including non-IT load to be matched with **additional, firmed renewable supply at all
times** via NSW-based NEM PPAs before operation may begin; caps generators at **170 h/yr**, installed back-up at
**267.45 MW**, diesel at **2,000 t**, and NOx below **10 t/yr** with 45 m stacks; and requires website
publication of environmental performance and audit reports. It does **not** impose a numeric PUE/WUE ceiling or
the 25% demand-reduction measure. See `reports/findings_memo.md` §5.

v1.2.0 substantially advanced **RG-013**: the NSW Investment Delivery Authority's Round 1 proponent
list (15 projects, $51.9bn endorsed, $40.7bn rejected as speculative) is now primary evidence;
Microsoft is resolved to consent SSD-10101987 at Kemps Creek with 61 generators and 30 diesel tanks;
and the first documented developer→council payment (Microsoft/Penrith Voluntary Planning Agreement,
executed 7 June 2023) is in the incentive register. See `reports/findings_memo.md` §3.

v1.1.0 closes research gap **RG-009**: the renewable claim audit now runs on primary Clean Energy
Regulator data (NGER corporate emissions 2019-20 → 2024-25, market-based scope 2, the LGC shortfall
register, Safeguard baselines and REC Registry holdings) instead of on press reporting. See
`reports/cer_analysis.md`.

> ⚠️ **Read `reports/findings_memo.md` §1 before using this data.** Five factual premises in the
> originating project brief did not survive verification (the AirTrunk buyer, the existence of cash
> subsidies, the synchronous-condenser mechanism, the NEM-only scope, and the novelty of the policy
> asks). The memo records the corrections and what they change.

---

## Layout

```
au-dc-observatory/
├── schema/01_schema.sql          24 tables, 8 views, CHECK-constrained vocabularies
├── data/seed_data.py             curated v1 seed (every row carries source + provenance)
├── data/packs/EXAMPLE_pack.json  worked example of the curated ingestion format
├── data/raw/                     archived raw scrapes (created on demand, SHA-256 manifest per file)
├── scripts/build_db.py           rebuild SQLite + CSV exports + viewer data + build report
├── scripts/reextract_consents.py pypdf re-extraction of the archived consent PDFs (sha256-verified, offline)
├── scripts/finalize_docs.py      regenerates build_report.md + viewer/db.json from the LOADED database
├── scripts/check_packs.py        fails the build if any pack/curation script is wired into only one driver
├── scripts/analyse_patents.py    dependency-free LDA topic model for a patent corpus (validated, never run on patents)
├── scripts/count_patent_filings.py  filings per tracked operator from an IPGOD 102 / IP RAPID extract
├── scripts/query.py              15 preset queries, arbitrary SQL, per-site evidence dossier
├── scripts/load_pack.py          validated loader for curated packs (writes ingest_log)
├── scripts/gen_dictionary.py     regenerates reports/DATA_DICTIONARY.md from the live schema
├── scrapers/ingest_nsw_dc.py         NSW Planning Portal register harvester (--harvest, --mods, --attachments)
├── scrapers/ingest_nsw_planning.py   NSW Planning Portal single-project archiver (polite, single-threaded)
├── scrapers/ingest_cer.py            Clean Energy Regulator NGERS / LGC / Safeguard fetcher
├── scrapers/ingest_austender.py      AusTender keyword-search archiver — NEVER RUN LIVE, see its docstring
├── exports/australian_data_centre_observatory.db
├── exports/csv/*.csv             every table and view, one file each
├── viewer/index.html             dependency-free query console (reads viewer/db.json)
└── reports/
    ├── findings_memo.md          the analysis: Pillars A–E, engineering critique, limitations
    ├── cer_analysis.md           generated: the RG-009 verification audit, tests T1–T6
    ├── RG007_foi_strategy.md     five FOI request templates + four free parallel routes
    ├── AIRTRUNK_BCA_influence_audit.md   AirTrunk, the BCA, and Submission No 116 read closely
    ├── palantir_australia_triage.md  UNVERIFIED LEADS: Palantir AU source triage, not database content
    ├── PATENT_METHOD.md          the Iliadis & Acker patent method transplanted: what it can and cannot answer here
    ├── extraction_audit.md       generated: PDF extraction yield per archived document
    ├── DATA_DICTIONARY.md        every table, every field, every controlled vocabulary
    └── build_report.md           generated: row counts, verification ledger, gap list
```

## Quick start

```bash
cd au-dc-observatory
make all                              # or: python3 scripts/rebuild_all.py  (if make is absent)
                                      #     python3 scripts/rebuild_all.py --fetch  (re-download CER first)
# or step by step:
python3 scripts/build_db.py                 # idempotent rebuild (stdlib + openpyxl)
python3 scripts/analyse_cer.py              # re-run the RG-009 verification tests
python3 scripts/load_pack.py data/packs/cer_verification.json
python3 scripts/gen_dictionary.py

python3 scripts/query.py --list             # available presets
python3 scripts/query.py pipeline           # capacity and capex by state and status
python3 scripts/query.py biggest            # the twenty largest sites
python3 scripts/query.py diesel             # generator counts, diesel storage, gas capacity
python3 scripts/query.py water              # cooling technology and water source per site
python3 scripts/query.py control            # who owns whom, with FIRB flag
python3 scripts/query.py money              # capital flows, newest first
python3 scripts/query.py incentives         # subsidy / fast-track register
python3 scripts/query.py law                # instruments, binding vs non-binding
python3 scripts/query.py loopholes          # instruments with non-compliance or exemptions
python3 scripts/query.py friction           # community events by severity
python3 scripts/query.py claims             # renewable claim audit
python3 scripts/query.py unverified         # everything that must NOT be published as fact
python3 scripts/query.py dossier SITE_MAMRE_ROAD   # full evidence dossier for one site

python3 scripts/query.py --csv pipeline > pipeline.csv
python3 scripts/query.py --sql "SELECT state, SUM(max_capacity_mw) FROM sites GROUP BY state"

cd viewer && python3 -m http.server 8000    # then open http://localhost:8000
```

Opening `viewer/index.html` directly from disk works but shows a static fallback snapshot, because
browsers block `fetch()` on `file://`. Serving the folder gives the live database. The viewer has no
external dependencies — inline CSS, no CDN, no network calls — so it renders identically offline.

## What's new in v2.1.0 — the determination layer

Every signed consent now carries its execution block: **who signed, in what capacity, on what date,
under which ministerial delegation, on which file** — parsed from the instruments' own cover pages and
cross-checked against portal node metadata. `exports/nsw_planning/nsw_dc_consent_determinations.csv`
is the register; `case_handling` grows from 71 to **83 rows** (20 signatory/authority records with real
case ids, delegation dates, decision dates and file references; the five `'(unparsed)'` case ids are gone).

Headline results: five signature blocks decide the entire sample (Bakopanos 9, Ritchie 6, Sargeant 3,
Shirley 1, one unnamed IPC panel); four delegation regimes since 2017 culminate in the **delegation
executed 18 August 2026 — one day after the Guidelines took effect** — under which both post-Guidelines
consents were signed; **RG-079 resolved** (template-dominated conditions, no officer effect detectable
at n=20); **RG-065 resolved** (all 20 applicants parse; 11 of 20 held by consultancies or undisclosed
vehicles); **RG-084/085 opened** (Stockland Macquarie Park site duplication; the Talavera IPC consent
published with `'[Name of Commissioner]'` placeholders).

The repair itself is part of the record: the archived extractions had silently degraded (AES-encrypted
PDFs the dependency-free extractor cannot open; numerals split across glyph boundaries), so all 20 PDFs
were sha256-verified against their fetch manifests and re-extracted with pypdf; superseded texts are kept
under `data/raw/nsw_planning/consents/superseded_pdftext/`. `consent_condition_audit.py --offline`
re-analyses the archive with **no network access and no clobbering** of the pypdf texts, and the online
path now refuses to overwrite a pypdf extraction when the freshly downloaded bytes hash identically.
Two more pipeline defects were fixed: `viewer/db.json` and `reports/build_report.md` were seed-stage
snapshots (`scripts/finalize_docs.py` now regenerates both post-load), and pack/driver drift is a build
failure (`scripts/check_packs.py`). New Make targets: `check-packs`, `reextract-consents`,
`battery-offline`.

Full write-up: `reports/findings_memo.md` (v2.1.0 block + the determination register) and
`reports/CONSULTANCY_LAYER.md` §3.

## What's new in v2.0.0 — the consultancy / advisory layer

Schema migration `schema/02_consultants.sql` adds four tables and six views covering a population the
project had until now only captured incidentally, inside entity notes: **the consultancies**.

Three distinct groups live here and were previously conflated:

1. **Technical consultants** who author the evidence base for a consent — acoustic, CFD,
   hydrogeological, traffic, plant-and-equipment reports. Their numbers become the conditions.
2. **Planning agents** who are the *named Schedule 1 applicant* on the consent itself. In 4 of the 13
   parsed NSW consents that is a consultancy, and in 4 more an opaque SPV — so in a majority of cases
   the party legally named on the instrument is **not** the operator. See `v_applicant_vs_proponent`.
   *(v2.1.0: all 20 now parse — 7 held by consultancies/architects, 4 by opaque vehicles; 11 of 20.)*
3. **Systems integrators** who hold the government's own IT contracts and sit on the peak bodies that
   write sector policy. Worked example: Tata Consultancy Services.

| Table | Rows | Purpose |
|---|---|---|
| `consultancy_profile` | 8 | firm type, pipeline role, peak-body membership, operator status, exposure **and its source tier** |
| `gov_contracts` | 23 | one row per distinct contract, with an `is_duplicate_of` self-reference |
| `consultant_role` | 22 | separates named applicant / technical author / peer reviewer |
| `case_handling` | 71 → **83** | case planners, delegate signatories, **ministerial delegation dates**, decision dates (v2.1.0 added the 20-row signatory register) |

New views: `v_consultant_public_money`, `v_consultant_spend_totals` (de-duplicated),
`v_case_officer_load`, `v_applicant_vs_proponent`, `v_consultant_influence`,
`v_contract_reconciliation`. New query presets: `consultants`, `contracts`, `spend`, `reconcile`,
`duplicates`, `applicants`, `officers`, `influence2`.

Full write-up: **`reports/CONSULTANCY_LAYER.md`**.

### Two integrity defects found and fixed while building it

Both would have silently corrupted a verification database, so they are recorded rather than quietly
patched.

- **`exports/csv/` was stale.** `build_db.py` writes CSVs *before* the packs load, so the committed
  files held seed rows only — `lobbying` 0 of 13, `metrics` 41 of 313, `gov_contracts` 0 of 23. Anyone
  reading the CSVs instead of the SQLite file was getting the wrong data. **`scripts/export_csv.py`**
  is now the single authoritative export, runs last in `rebuild_all.py`, re-reads every file it wrote
  and **fails the build** if any row count diverges from the database.
- **Re-running a pack duplicated rows.** Tables with an autoincrement PK and no unique key are
  append-only; reloading a pack doubled them (measured: 1,566 → 1,639 rows). Fixed with runtime
  composite-key upserts (NULL-safe), an exact-duplicate probe, and a `--force-append` escape hatch
  that errors loudly by default. Skips are logged as `skipped_identical`. **Reloading a pack twice now
  adds zero rows.**

Also fixed: `build_db.py` applies *all* `schema/*.sql` in filename order so migrations survive a
rebuild; and `load_pack.py` honours `engineering_claims.source_ids` (plural) — that table was
previously unloadable from any pack because the loader demanded a singular `source_id`.

## The verification discipline

Four things make this a database rather than a scrapbook.

**1. Every row carries provenance.** `source_id`, `fact_status`, `confidence`, `as_of_date`. There
are no unsourced assertions in the seed, and `load_pack.py` refuses to insert one.

**2. `fact_status` is a controlled vocabulary with teeth.**

| Status | Meaning | May it be published as fact? |
|---|---|---|
| `VERIFIED` | The primary document was read (legislation, regulator, planning portal, first-party release) | Yes |
| `REPORTED` | Credible secondary reporting of a primary fact | Yes, with attribution |
| `CLAIMED` | Proponent or industry assertion, not independently confirmed | No — attribute as a claim |
| `GAP` | Known unknown, tracked in `research_gaps` | No |

**3. Sources are graded A–D** by document class, not by reputation. A law firm's analysis is B even
when it is excellent; a Facebook post is C even when it is true. Grade informs how hard to push.

**4. Nothing is silently dropped.** `build_db.py` reports integrity problems and refuses to hide
them; `load_pack.py` rolls back the whole pack on a single validation error; `ingest_log` records
every load.

`python3 scripts/query.py unverified` is the honesty check. Run it before publishing anything.

## What the CER verification found

`scripts/analyse_cer.py` runs five independent tests against the archived regulator datasets. Results
as at 18 September 2026, all reproducible from `data/raw/cer/`:

| Test | Result |
|---|---|
| T1/T2 scope 1 + 2 trend | AirTrunk scope 2 **+485%** over five years to 553,344 t; Amazon +202%; CDC +111% since 2020-21; NEXTDC +64%. AirTrunk + CDC + Amazon combined +165%, and +23.8% in 2024-25 alone — the AFR/Greenpeace headline **reproduces**. |
| T3 market-based scope 2 | Only **2 of 8** operators reported it in 2024-25 (NEXTDC, Fujitsu); **none** in 2023-24. NEXTDC's is **3.6%** below location-based, covering 94% of facilities. AirTrunk, CDC, Amazon, Equinix, Telstra and Global Switch do not report it at all. |
| T4 LGC shortfall register | **Zero** data centre operators among 143 liable entities (2001-2025). Retailers' 2024 shortfall charges totalled **A$180.3m**; 2025 **A$115.5m**. |
| T5 Safeguard Mechanism | **Zero** of 228 covered facilities is a data centre; no data/hosting ANZSIC class appears. Highest operator scope 1 is 7,919 t against a 100,000 t threshold. |
| T6 REC Registry holdings | CDC 233,209 LGCs; Amazon Energy LLC 226,073; **NEXTDC 500**; AirTrunk, Equinix and Global Switch hold none. Snapshot only — the CER warns holdings move constantly. |

Claim verdicts applied: AirTrunk "100% renewable by 2025" → **CONTRADICTED** (as a statement about
Australian operations); Greenpeace "no operator adequately proves it drives renewable growth" →
**VERIFIED** by independent reproduction. Full reasoning in `reports/cer_analysis.md`.

## Ingestion

Scrapers never write to the database. The path is always: **archive raw → curate → validate → load.**

```bash
# 1. Archive raw material (writes data/raw/nsw_planning/ with SHA-256 manifests)
python3 scrapers/ingest_nsw_planning.py --project mamre-road-data-centre-campus
python3 scrapers/ingest_nsw_planning.py --attachment "SSD-92743706!20260119T012428.711 GMT"
python3 scrapers/ingest_cer.py --check        # is the Clean Energy Regulator reachable?
python3 scrapers/ingest_cer.py --download     # landing pages + manifest, for human review
python3 scrapers/ingest_austender.py --check                 # reachability + robots.txt
python3 scrapers/ingest_austender.py --keyword palantir      # archive the search results
python3 scrapers/ingest_austender.py --inspect               # offline: list archive, verify hashes

# 2. Curate into a pack (see data/packs/EXAMPLE_pack.json for the exact shape)

# 3. Validate, then load
python3 scripts/load_pack.py data/packs/my_pack.json --dry-run
python3 scripts/load_pack.py data/packs/my_pack.json
```

All scrapers are single-threaded with a fixed delay, send a descriptive User-Agent identifying the
project, and are designed to stop when asked. Public planning registers are a service, not a data
vendor. `ingest_austender.py` additionally reads `robots.txt` and skips what it disallows, unless
`--ignore-robots` is passed with a reason the operator can defend.

### AusTender: added as a source, not yet read

`scrapers/ingest_austender.py` was added for the Commonwealth portal of record, entered from the
keyword search `https://www.tenders.gov.au/Search/KeywordSearch?keyword=palantir`. Two things about
it are worth stating plainly, because neither is visible from the file listing.

**It has never been run against the live site.** tenders.gov.au was unreachable from the
environment it was written in (the egress proxy answered 403 to CONNECT), so nothing in it is a
tested claim about AusTender's markup, pagination or URL shapes — unlike `ingest_cer.py` and
`ingest_nsw_dc.py`, whose patterns were tested on 2026-09-18. It is built by discovery rather than
by hard-coded structure: the only asserted URL is the search entry point above, and result and
pagination links are read out of whatever HTML returns. `make check-austender` runs fixture tests
over the link-discovery functions; those prove the parser handles the shapes it was written for,
and prove nothing about whether AusTender uses them. **The first live run is a human review step.**

**No Palantir data is in the database, and none should be inferred to be.** Nothing was fetched, so
there is no archive, no source record and no fact. `sources.accessed` is `NOT NULL` and means the
date we read the document; registering a source for a page nobody has opened would be exactly the
fabrication the verification discipline exists to prevent. Palantir does not appear anywhere in the
database and will not until the archive exists and is curated.

The same target serves **RG-072** with `KEYWORD="tata consultancy"`, which is the gap that already
names AusTender as the portal that must replace the GovMarket aggregator behind the $234.4M figure.

A first pass at the Palantir leads is triaged in **`reports/palantir_australia_triage.md`** — also
unverified, and marked as such, because no source in it could be fetched either. Three things in it
bear on how the archive gets curated. The **relevance hook is hosting, not the customer roster**:
Palantir Platform Australia is reported to run Foundry and AIP in **Australian AWS regions** after an
IRAP PROTECTED assessment, which makes Palantir a demand-side tenant of hyperscaler capacity and ties
to RG-013 and to Amazon's measured scope 2. A **name collision** will contaminate any keyword search:
`palantirconsulting.com.au` is an unrelated Australian structural and façade engineering firm, so
curation must disambiguate on ABN, never on the string. And a supplied roster of 13 entities proved
both over- and under-inclusive — three entries rest only on buyer-intent or technographic vendors,
while four real Commonwealth relationships (ASD, Veterans' Affairs, ACIC, and a buy.nsw supplier
profile) were absent. That is the GovMarket failure again, which is the argument for the portal of
record.

### Credentials in archived pages

Archived HTML is a snapshot of someone else's page, and those pages can embed their own API keys.
The NSW Planning Portal ships a Google Maps browser key in its `drupal-settings-json` block, so it
appeared in `glendenning.html`, `kemps_creek.html` and `mamre_road.html`. It is the Portal's key, not
ours, and it was already public on their site — but committing it here republishes another party's
credential and trips secret scanners, so it is redacted to
`REDACTED-THIRD-PARTY-GOOGLE-MAPS-API-KEY`.

Recording the edit rather than making it quietly: only that one JSON string changed, no curation
script reads these three files, and no SHA-256 manifest covers them, so nothing downstream moves.
Where a redaction would touch a hash-verified document, redact nothing — leave the archive intact and
raise it instead. `ingest_nsw_planning.py` now applies the same redaction at archive time, so future
scrapes never write the key to disk.

## Scope decisions worth knowing about

- **Australia, not the NEM.** Every site carries `market` ∈ {NEM, WEM, NT}. WA and the NT are inside
  the database and outside the NEM; Queensland is inside the NEM and dissented from the July 2026
  ECMC offsetting agreement. Scoping to the NEM would have hidden the largest project in the country.
- **Three capacity fields, never aggregated.** `it_capacity_mw` (critical load), `total_capacity_mw`
  (with cooling overhead) and `max_capacity_mw` (full campus build-out) are stored separately,
  because conflating them is how pipeline numbers get inflated.
- **Capacity basis is a first-class field.** `metrics.basis` ∈ {actual, pipeline, signed, enquiry,
  forecast_low/central/high, estimate}. Transgrid has 20 GW of *enquiries* and 1.5 GW of *signed*
  agreements; those are different numbers and must never be summed.
- **Money is AUD REAL, power is MW, water is kL/yr.** No unit drift.
- **Unverified proximity fields are left empty.** `nearest_cable_ls_km` awaits RG-001. A blank is
  more useful than a guess. Its site half is now in: see "Site coordinates" below. The landing-station
  half (`data/inputs/cable_landing_stations.csv`) is still empty.
- **Site coordinates come from the planning record, not a geocoder.** 46 sites, every NSW State
  Significant Development project, carry the location point the NSW Planning Portal records for the
  project (`field_coordinates` on the archived node JSON). `scripts/curate_site_coordinates.py`
  verifies each node against its SHA-256 manifest, joins it to its site by SSD number, cites the
  project's own portal page, and writes `data/packs/site_coordinates.json` and
  `data/inputs/site_coordinates.csv` (method `planning_portal_point`). It refuses to write if a hash
  fails, a reference maps to two sites, or a point falls outside NSW. The point is the planning
  record's location for the project, not a surveyed building footprint. The other 47 sites (22 NSW
  sites outside the SSD register, and every site in other states) have no coordinates and carry a gap
  saying so.

## Status of the four pillars

| Pillar | State | Blocking gap |
|---|---|---|
| A — Physical infrastructure | **93 sites, 54 applications.** The complete NSW data centre SSD register (46 records) harvested and archived; Microsoft resolved to consent; NSW IDA proponent list captured; all 20 determined consents parsed to Schedule 1 (applicants, signatories, delegations — v2.1.0 determination register). | RG-034 (modifications + council DAs), RG-035 (codename SPVs — 11 of 20 applicants now known), RG-003 (VIC/QLD registers), RG-001 (cable proximity), RG-064/081 (EMKC/HDI/NineZero ownership), RG-084 (Stockland Macquarie Park) |
| B — Capital and control | Ownership chains verified for AirTrunk and CDC; 10 capital flows; 9 incentive records; **270 VERIFIED metric rows** including the full CER emissions series; consultancy layer: 23 de-duplicated TCS contracts, $234.4M verified spend. | RG-007 (FOI on tax/land concessions), RG-006 (FIRB), RG-004 (super exposure), RG-005 (Mamre title), RG-072 (TCS portals of record), RG-078 (Oxford Economics funder) |
| C — Regulatory framework | Strongest pillar: 22 instruments, 8 site-level applications, 24 regulatory events, including the 200-hour diesel exemption, the Victorian Tier 4 asymmetry, and the **delegation executed 18 Aug 2026 — one day after the Guidelines** — under which both post-Guidelines consents were signed. RG-079 resolved (template-dominated conditions; no officer effect at n=20). | RG-008 (EP licence conditions per site), RG-074 (consultancy overlap with DPHI/IPC contracts), RG-085 (Talavera IPC placeholder signatures) |
| D — Community impact | 21 events, 6 groups, institutional objections documented at Mamre Road and Glendenning (Blacktown objection overridden). | RG-016 (group register), RG-011 (verify Melton/South Morang) |
| E — Engineering critique | Complete: 7 propositions tested, verdicts issued, replacement specs written against existing policy hooks. | RG-018/019 (grid services and system strength evidence) |

## Licence and citation

Data: CC BY 4.0. Code: MIT. Cite as:

> Australian Data Centre Observatory, *Verified database of the Australian data centre ecosystem*,
> v1.0.0, data as at 18 September 2026.

The underlying facts belong to their sources. `SELECT id, title, publisher, url FROM sources` prints
the full attribution list; every exported CSV row can be traced back to it via `source_refs`.
