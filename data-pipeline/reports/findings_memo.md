# Australian Data Centre Observatory — findings memo

**Release:** v2.1.0 · **Data as at:** 18 September 2026 · **Prepared:** 18 September 2026
**Database:** `exports/australian_data_centre_observatory.db` — SQLite, 30 tables, 16 views,
**1,241 data rows** (+ 376 source references), **93 sites**, 325 metrics, 125 entities, 22 legal instruments, 17 consent modifications
**Sources catalogued:** 117, of which **70 are primary documents** · **Gaps:** 53 open, 13 in progress, **13 resolved**
**Primary documents downloaded and read this release:** 20 signed NSW development consents, the 344 MB
Western Downs application, 5 Legislative Council transcripts, 6 Clean Energy Regulator datasets

**v2.1.0 change — the determination layer, and a data-loss incident caught and repaired.** RG-079 is
**resolved**: `determination_date` is now populated on all 20 consent-battery rows, and WHO-decided-WHEN-
UNDER-WHAT-DELEGATION is a first-class register (`exports/nsw_planning/nsw_dc_consent_determinations.csv`;
20 `case_handling` signatory rows in the DB). What it took, and what it found:

1. **The archived consent texts had silently degraded.** On 18 September a pipeline re-run overwrote all 20
   extractions; the dependency-free extractor cannot decrypt **AES-encrypted** portal PDFs (Lane Cove West and
   Macquarie Park yielded **0 characters** — their battery rows were empty, not absent) and **splits numerals
   across glyph boundaries** (Glendenning's 235 MW parsed as 23; NEXTDC S4's 294 MW as "2 94"; its 200-hour
   cap vanished). Every PDF was **sha256-verified against its fetch-time manifest** and re-extracted with pypdf
   (`scripts/reextract_consents.py`); superseded texts are kept under `consents/superseded_pdftext/`. All 20 now
   clear the reliability floor: **reliable 18 → 20, extraction-limited 2 → 0**, and the battery counts moved
   with the recovered text (generator-hours caps 14 → **17**; 200-hour template 11 → **14**; website
   disclosure 16 → **19**; diesel and genset caps 12 → **14**; PUE 5 → **7**; renewable 4 → **5**; recycled
   water 4 → **5**). Glendenning's `total_power_cap` corrected 23 → **235 MW**.
2. **The officer-effect answer (RG-079): conditions are template-dominated, and no officer effect is
   detectable at n=20.** The 200-hour cap appears in 14 of the 17 consents carrying any cap; website
   disclosure in 19 of 20; the Guidelines in **0 of 20 including both post-Guidelines determinations**.
   Officer portfolios overlap completely on a documented strictness index (Williams n=9, mean 6.56, range
   2–14; Copas n=6, mean 4.50, range 1–11), and within-officer variation exceeds between-officer variation.
   Where conditions DO depart from template, the record attributes them to proponent EIS commitments
   (NEXTDC S4) or site-specific assessment (Glendenning air quality) — not to the case officer.
3. **The structural finding survives, and sharpens.** Shaun Williams and Patrick Copas officer **15 of the
   20 determined consents (75%)** — and **both post-Guidelines determinations**: Glendenning (Williams) and
   Project Apollo (Copas). Both were signed by **Joanna Bakopanos, A/Director Industry Assessments, under a
   ministerial delegation executed 18 August 2026 — one day after the Guidelines took effect** — now verified
   from the instruments' own cover pages in the repaired archive, replacing the 9 March 2022 delegation
   under which the previous twelve were signed. Bakopanos signs **9 of 20** instruments (45%) and also
   appears as *case planner* for Talavera Road: the same small office both manages and signs the pipeline.
4. **Two accountability defects in the published instruments.** The Talavera Road IPC consent — the only
   determination in the sample NOT made under ministerial delegation — was published with its signature
   block left as **"[Name of Commissioner]" template placeholders** and a year-only execution line ("Sydney
   2023"): the published instrument does not name who decided it (RG-085). And Lane Cove West / Dicker Data
   carry execution dates only as image stamps, absent from the text layer.
5. **RG-065 resolved: all 20 Schedule 1 applicants now parse.** The seven formerly unparsed: Khartoum Road =
   **Stockland Development Pty Limited**; Lane Cove West = **Greenbox Architecture Pty Ltd** (an architectural
   practice holding a data centre consent); Macquarie Park = **Stockland Trust Management Limited**; Echidna =
   **ARUP Australia Pty Ltd** (a *different* Arup entity from Turner Road's ARUP Pty Ltd); Pluto = **Goodman
   Property Services (Aust) Pty Ltd**; Station Road = **Lehr Consultants**; Dicker = **Dicker Data Limited**.
   Final structure: 4 operating companies (5 consents), Equinix via project SPV, 2 property groups, 1
   end-user, **7 consents held by consultancies/architects**, 4 by opaque SPVs/trusts — so in **11 of 20**
   consents the legal person responsible for every condition is either a consultancy or an entity whose
   controller is undisclosed. RG-074 advanced: none of these firms appears in the tracked `gov_contracts`
   table, so the assessment-side overlap question now needs DPHI/IPC agency-level contract pulls.
6. **Two more pipeline defects found and fixed** (bringing the running total to five): `viewer/db.json` and
   `reports/build_report.md` were written by `build_db.py` at **seed stage** — the viewer showed 41 metrics
   against a database holding 325, and the report claimed 326 rows against 1,241 — now regenerated post-load
   by `scripts/finalize_docs.py`; and pack/driver drift (the class that orphaned the rg060 pack, and which
   left `curate_consultants.py` out of the Makefile) is now caught at build start by
   `scripts/check_packs.py`, which fails the build if any pack or curation script is wired into only one
   driver, or if load order diverges. The consultants-layer gap ids (72–83) were made explicit so cross-pack
   `match/set` updates survive from-scratch rebuilds.

**v2.0.0 change — the consultancy / advisory layer.** Schema migration `02_consultants.sql` adds four
tables (`consultancy_profile`, `gov_contracts`, `consultant_role`, `case_handling`) and six views for a
population previously captured only incidentally inside entity notes. **Full write-up:
`reports/CONSULTANCY_LAYER.md`.** Four findings carry into the main memo:

1. **A $118.3M figure in public circulation is double-counted.** The widely quoted "AUD $352.7M across 65
   engagements" for Tata Consultancy Services traces to the commercial aggregator GovMarket, which lists
   the *same* contract once per portal. Primary notice **CAN-100812** confirms $118,312,700 exactly — but
   also that it was **effective 29 March 2018, ends 30 June 2027, and was obtained by DIRECT
   NEGOTIATION**. De-duplicated: **$234,423,257.18 across 64 engagements**. One nine-year sole-source
   contract is **50.5%** of the firm's entire tracked Australian public spend.
2. **In 8 of 13 parsed NSW data centre consents the named Schedule 1 applicant is NOT the operator** — 4
   are consultancies (Arup; Cundall ×2; Lehr) and 4 are opaque SPVs or trust trustees (EMKC Cubed ×2; HDI
   SYD1; NineZero DC Sub Trust I). Only 5 name an identifiable operator. This includes **Glendenning Road
   SSD-73761707**, the 235 MW benchmark consent, which names an acoustics and planning consultancy.
   A one-line form change would resolve RG-022, RG-023, RG-064, RG-065 and RG-081 at once.
   **[v2.1.0: all 20 applicants now parse — 11 of 20 are consultancies or opaque vehicles; RG-065 resolved.]**
3. **Both post-Guidelines consents were signed under a ministerial delegation executed 18 August 2026 —
   one day after the Guidelines were published** (17 August 2026). Glendenning was signed 14 September
   2026 by Joanna Bakopanos, A/Director Industry Assessments, file EF 24/10658. Project Pluto (23 July
   2026) is the control case: mid-2026, but under the **2022** delegation.
   **[v2.1.0: verified from the instruments' own cover pages in the repaired pypdf archive; recorded as a
   regulatory event and in the `case_handling` signatory register.]**
4. **Two officers handle 65% of the NSW data centre pipeline** (Shaun Williams 25 of 63 project records,
   Patrick Copas 16). Whether condition stringency varies by officer **cannot yet be answered**:
   `determination_date` parsed empty on all 20 rows of the consent battery, so the era confound was
   uncontrolled. Logged as RG-079, priority 1, **blocked**. Do not report an officer effect until dates
   are populated. **[v2.1.0: RESOLVED — dates populated on all 20; no officer effect detectable at n=20;
   conditions are template-dominated. See the v2.1.0 block above.]**

Three pipeline defects were found and fixed while building this layer, all of which had been silently
degrading the database: `exports/csv/` was **stale** (written before packs load — `lobbying` 0 of 13,
`metrics` 41 of 313), now fixed by `scripts/export_csv.py` which runs last and **fails the build** on any
divergence; **re-running a pack duplicated rows** in append-only tables (measured 1,566 → 1,639), now
fixed with runtime composite-key upserts and an exact-duplicate probe, verified idempotent; and an
**orphaned pack** (`rg060_consent_conditions.json`, wired into neither pipeline) meant three curated
metrics never reached the database — including `consents_with_generator_hours_cap` (14), whose gap
against `consents_with_200_hour_generator_cap` (11) is exactly where site-specific departures from the
Department's 200-hour template live. All three recovered; values confirmed 18 / 2 / 14. **[v2.1.0: the
re-extraction superseded these values — now 20 / 0 / 17; and defects #4 (seed-stage viewer/build-report)
and #5 (pack/driver drift) were found and fixed, with `scripts/check_packs.py` now failing the build on
any future drift.]**

Also note for Pillar B: **TCS is a BCA member** (alongside Accenture), and from 20 November 2025 a
**hyperscale data centre developer** through HyperVault, a JV with **TPG — itself a BCA member** — targeting
>1 GW of liquid-cooled AI capacity. India-scoped; **no Australian footprint announced** (documented
negative, RG-076). Investor and investee inside the same peak body mirrors the Blackstone/CPP–AirTrunk
pattern already recorded in §4.

**v1.8.0 change — RG-060: all twenty consents, and two retractions.** The condition battery now covers
every determined NSW data centre SSD. **The NSW Data Centre Guidelines are cited in zero of eighteen
consents**, including the one approved a month after they took effect. PUE appears in 5, WUE in 4, a renewable
supply condition in 4, an NOx mass cap in **2**. Two of my own earlier findings are corrected: website
disclosure is in 16 of 18 consents so it is *standard practice*, not a Glendenning distinction; and the apparent
demand-response prevalence was a **parser false positive** matching a condition that *prohibits* diesel load
curtailment — no consent requires any non-diesel demand response. And the stricter NOx cap is **not** the
post-Guidelines consent: NEXTDC S4 accepts 5.5 t/yr including testing against Glendenning's 10 t/yr excluding
outages. Four codenames resolved from Schedule 1, including Equinix Hyperscale 2 (SY10), Macquarie Data
Centres and Goodman. See §5.

I also hardened `scripts/pdf_text.py` with a **yield guard** after discovering it silently under-extracted the
Guidelines PDF (8.2 chars/KB against 46–82 for the consents). The guard now warns and the audit is published,
so no negative finding can rest on a failed extraction again. Two documents in the archive are image-only and
one is partially extracted — all flagged. (regulator, legislation, planning portal,
parliamentary record, first-party company) · **Research gaps:** 57 tracked — 37 open, 10 in progress, **10 resolved**

**Resolved gaps:** RG-002 (complete NSW SSD register, 46 records) · RG-009 (Clean Energy Regulator
verification engine) · RG-022/RG-023 (proponent and hyperscaler attribution, both closed as documented
negatives and then RG-023 reopened on new evidence) · RG-026 (first post-Guidelines consent, read in full) ·
RG-028 (emissions-signature identification method, disproved) · RG-038 (four-consent condition comparison,
2020–2026) · RG-046 (whether the Guidelines reach modifications — they cannot) · RG-047 (superseded) ·
RG-049 (Western Downs primary application) · RG-003 advanced for both VIC and QLD.

**v1.9.0 change — an influence layer, prompted by a user observation.** AirTrunk's founder and CEO
**Robin Khuda sits on the Business Council of Australia board** (appointed 27 June 2025 alongside Telstra's
Vicki Brady), on a nine-seat board that also carries CBA, Wesfarmers, Google Australia & NZ, BHP Australia and
Gilbert + Tobin. **All four hyperscalers — Amazon, Apple, Google, AirTrunk — are BCA members**, while
**NEXTDC is not**. Since this project established that AWS, Google and Meta appear in **zero** of 46 NSW
planning records, their Australian policy representation runs through the BCA rather than through planning
portals: influence and physical footprint are in different places. I read **BCA Submission No 116** to the NSW
inquiry in full and cross-examined every quantified claim against the CER data — see the companion report. Two
things stand out. The submission's **"44 GW of requests → ~6 GW proceeding → 2.8 GW actual draw"** is the most
deflating number in the debate and it is *industry-funded*, so it should be quoted by critics too. And against
terms of reference expressly covering diesel generation, emissions and health impacts, noise and air quality,
and public subsidies, the words **diesel, generator, back-up, NOx, noise, air quality and subsidy appear
nowhere** in 59,431 characters — verified after repairing the ff/ffi ligatures my own extractor drops. New
`lobbying` table and `v_influence` view, 10 records, all disclosed.

**v1.7.0 change — two more gaps closed from primary consents.**

- **RG-038.** Four signed consents spanning six years show the **200-hour generator condition is a Department
  standard, not a regulatory gap**: Roberts Road (2020), Davis Road (2024) and DCI Poplars all cap generator
  operation at exactly 200 hours a year; Glendenning's 170 is the first departure. And **installed back-up
  generation exceeds the facility's entire load in every consent where both are stated** — Glendenning 267.45 MW
  against a 235 MW cap, Davis Road 181.92 MW against 160.85 MW. These are parallel power stations, not standby
  reserves, and in three of four consents they carry no NOx mass cap, no stack height and no emissions testing.
  Only one of the four applicants is an operating data centre company.
- **RG-046.** The Guidelines' own mechanism resolves it: applicants must demonstrate compliance, and
  "conditions will then require applicants to meet obligations, mitigation measures and **commitments outlined
  in their Environmental Impact Statement**." A s.4.55 modification has no EIS, so the Guidelines cannot attach
  to it. **The framework has no ratchet** — and RG-034 shows the drift is real.
- Two documents that would settle further questions are access-restricted, including an **"ASIC certificate
  Amazon Corporate Services Pty Ltd"** filed on the Davis Road application — the first documentary trace of a
  hyperscaler inside an NSW planning record, which is why RG-023 is reopened (RG-057).

**v1.5.0 change — three new findings, all of them about accountability rather than capacity.**

1. **Victoria's fast track removes the checks, not just the delay** (§5.2). The Development Facilitation
   Program under Part 9A of the *Planning and Environment Act 1987* sends data centre applications straight
   to the Minister, lets the Minister waive or vary planning scheme requirements, and removes VCAT merits
   review for applicants *and* objectors plus any review of permit conditions. It is available above $10m
   regional / $20m metro — i.e. to every significant proposal. At NEXTDC M3 West Footscray, objections fell
   from **more than 80** on the original council permit to **5** on the DFP expansion, one of them from the
   council that no longer decides. This is the brief's "unconditional subsidies" concern made concrete, and
   the currency is accountability rather than cash.
2. **Consents drift upward after approval, and nothing tracks it** (§5.3). All 17 post-consent modifications
   to NSW data centre SSDs are now in the database: 15 approved, 1 withdrawn, 2 undetermined. Five change the
   environmental envelope the original consent was assessed against — **additional back-up generators and
   diesel storage at Roberts Road (approved 6 March 2026)**, **a power consumption increase at Eastern Creek
   (5 August 2026)**, **fuel storage at Lane Cove West**, an expansion at Talavera Road, and a second round of
   operational-infrastructure changes at Roberts Road still pending. Four were approved between 5 and 28
   August 2026, either side of the Guidelines taking effect. The NSW Guidelines say nothing about
   modifications.
3. **The water numbers are irreconcilable, and the regulator that could settle it hasn't** (§4.2). Under
   parliamentary privilege Data Centres Australia said the 25% figure "is not based in fact" and "was
   dismissed by IPART as being unverifiable"; Sydney Water's Managing Director, asked directly, said "**We
   do** [stand by it], and we acknowledge the uncertainty." Both are now in the database with their verdicts.

**v1.4.0 change.** RG-002 resolved for the State Significant Development layer: a purpose-built harvester
(`scrapers/ingest_nsw_dc.py`) pulled **all 46 data centre SSD records** off the NSW Planning Portal with case
ids, stages, decisions, determination dates and authorities, LGAs, development descriptions and attachment
counts — every node JSON archived with a SHA-256 manifest. Site count went 57 → **91**. Two findings the
harvest produced that no amount of news reading would have: **zero** of the 46 is titled AWS, Amazon, Google
or Meta (so hyperscaler footprints cannot be mapped from planning titles at all — RG-023 closed as a negative,
re-scoped to RG-035), and **three applications were withdrawn** (Augusta Street, 52 Turner Road, Mowbray Road),
which is the only direct planning-record evidence of proposals that did not survive. RG-007's FOI strategy is
drafted with five request templates and four free parallel routes. See §3.2 and `reports/RG007_foi_strategy.md`.

**v1.3.0 change — the headline result.** RG-026 resolved: the signed consent for SSD-73761707
(Glendenning Road, 235 MW, 16 September 2026) has been read in full. It binds the operator to match
**all** operational electricity demand, including non-IT load, with **additional, firmed renewable
energy supply at all times** through NSW-based NEM PPAs — hourly matching with explicit
additionality, as a condition precedent to operation. It caps generators at **170 hours/year**
(below the 200-hour unregulated window), **267.45 MW** installed back-up, **2,000 tonnes** of diesel,
**45 m** stacks and **<10 t/yr NOx**. It requires website publication of environmental performance
and audit reports. It does **not** impose a numeric PUE/WUE ceiling or the 25% demand-reduction
measure. Blacktown City Council's objection — 823 parking spaces required vs 165 offered, cumulative
urban heat, and net job loss against **three existing warehouses on the site** — did not prevent
approval. See §5.1.

**v1.2.0 change:** RG-013 substantially advanced. The NSW Investment Delivery Authority Round 1
proponent list (15 projects, $51.9bn, and $40.7bn *rejected* as speculative) is now primary evidence
in the database; Microsoft is resolved to consent SSD-10101987 at Kemps Creek; a Microsoft/Penrith
Voluntary Planning Agreement is recorded as the first documented developer→council payment; and the
202.4 MW Glendenning Road approval over Blacktown Council's objection is captured with its
consultancy-named proponent. See §3.1.

**v1.1.0 change:** the renewable claim audit now runs on primary Clean Energy Regulator data rather
than on press reporting. AirTrunk's "100% renewable by 2025" claim moved from `UNVERIFIED` to
`CONTRADICTED`; the Greenpeace finding moved to `VERIFIED` by independent reproduction; 122 verified
NGERS metric rows were added.

**v1.1.0 change:** the renewable claim audit now runs on primary Clean Energy Regulator data rather
than on press reporting. AirTrunk's "100% renewable by 2025" claim moved from `UNVERIFIED` to
`CONTRADICTED`; the Greenpeace finding moved to `VERIFIED` by independent reproduction; 122 verified
NGERS metric rows were added.

---

## 1. Executive summary

The investigative frame in the project brief is sound, but five of its factual premises do not
survive contact with the Australian record as it stood in September 2026. Correcting them changes
what the database has to measure.

**1. The policy window the brief asks for has already opened — and closed on some of the brief's
own proposals.** Between March and August 2026 Australia built a three-tier data centre regime:
Commonwealth *Expectations of data centres and AI infrastructure developers* (23 March 2026), a
Commonwealth Office of AI plus a promised national AI Standard with binding legislation flagged for
early 2027 (15 July 2026), and the NSW *Data Centre Guidelines* with a 75-day fast-track pathway
(17 August 2026). On 5 August 2026 three further instruments landed in a single day: AEMC advice to
the Energy and Climate Change Ministerial Council on mandatory demand offsetting, Minister Bowen's
rule change requests ERC0448 and ERC0456 on network cost recovery, and the NSW *Electricity
Infrastructure Investment Amendment Bill 2026*.

The brief's "solid engineering replacement" for water — recycled wastewater instead of potable
mains — is now NSW policy almost verbatim. Its demand-response proposal is now NSW policy at a
specified quantum (25% of average load for two hours, diesel explicitly excluded). Its
additionality critique of renewable claims is now a proposed Commonwealth certificate scheme
(REGO). Critique that ignores this will read as uninformed. The productive position is
**enforcement and quantification**, not proposal — and the leverage point is that of the 17
instruments this database tracks, only **4 are binding** (§5).

**2. The buyer of AirTrunk was not Brookfield.** It was Blackstone, leading a consortium with CPP
Investments, at an enterprise value above A$24bn — the largest data centre transaction globally and
the largest Australian transaction of 2024, completed 23 December 2024. The vendors were
Macquarie Asset Management and PSP Investments (88%). CPP took 12%. This is a domestic
infrastructure-manager and Canadian-pension exit into US private equity, which is a materially
different Pillar B story from "private equity bought a local champion".

**3. The subsidy thesis is unevidenced in Australia, and the observable subsidy is procedural.**
No verified instance of a payroll tax waiver, land tax exemption or concessional leasehold grant to
a data centre proponent has been located. The industry body asserts none exist. What is documented
is *speed*: a 75-day assessment pathway in NSW, a three-month fast track in Victoria, a NSW
approvals authority for projects above A$1bn, and A$5.5m of Victorian coordination funding. Those
are real state supports with real value; they are simply not cash. This is the single largest open
item in Pillar B and it requires FOI, not scraping (RG-007).

**4. The synchronous-condenser recommendation is aimed at the wrong asset.** Data centres are large
inverter-based *loads*. Synchronous condensers are network-side system-strength assets. The
regulatory response actually under way is the AEMC's March 2026 draft determination creating access
standards for large inverter-based loads — fault ride-through rather than disconnection — prompted
by AEMO's April 2024 rule change request and by the July 2024 Virginia event in which ~1,500 MW of
data centre load tripped on a single fault. The brief's *objective* (facilities as grid assets) is
right; the *mechanism* must be load-side.

**5. Scoping to the National Electricity Market would have hidden the biggest project in the
country.** Western Downs Digital Park in Queensland — A$31.9bn, 2.16 GW peak, roughly a quarter of
Queensland's peak demand — is in the NEM but in a state that dissented (with the NT) from the July
2026 ECMC offsetting agreement. A reported ~1 GW facility is planned in WA, which is in the
Wholesale Electricity Market, not the NEM at all. The database carries a `market` column
(NEM/WEM/NT) on every site for this reason.

**What the evidence does support, strongly:**

- The grid is the binding constraint, not land or capital. Transgrid has 20 GW of large-load
  connection enquiries and states there is insufficient capacity in the Sydney basin to connect
  *any* of them without user-paid augmentation. Only 1.5 GW has reached signed connection
  agreements in Western Sydney. Up to 2 GW more is unlockable via a new South Creek 500/330 kV
  substation, at proponent cost.
- Most of the pipeline is not real. Oxford Economics, preparing AEMO's forecast, estimates 6 in
  every 7 MW of connection requests are phantom demand; utilities tell NSW that ~20% of
  applications will proceed.
- The diesel loophole is genuine and quantified by the NSW Government itself: generators may run up
  to 200 hours a year with no point-source NOx limits, and the largest Sydney facilities have
  generator capacity comparable to NSW's larger gas power plants. Mamre Road alone specifies 846
  generators and >18,000 kL of diesel storage.
- Renewable claims do not survive audit — and this is now proven from primary regulator data, not
  press reporting (§4.1). AirTrunk's location-based scope 2 rose 485% over five years to 553,344 t
  CO2-e while it advertises 100% renewable energy by 2025; it does not appear in the CER's
  market-based scope 2 table in either published year. Only two of eight operators reported
  market-based scope 2 at all, and NEXTDC's is just 3.6% below its location-based figure. No data
  centre is an LGC-liable entity, and none is a Safeguard Mechanism covered facility.
- Community friction has reached institutions, not just protests. Penrith City Council formally
  objected to Mamre Road; the NSW EPA found its EIS incomplete; a school across the road is seeking
  to relocate; the Catholic Diocese of Parramatta objected outright.

---

## 2. Evidence base and credibility grading

Every row in the database carries `source_id`, `fact_status` (VERIFIED / REPORTED / CLAIMED / GAP),
`confidence` (high / medium / low) and `as_of_date`. Sources are graded A–D:

| Grade | Definition | Examples in this release |
|---|---|---|
| A | Primary government, regulator, legislation, planning portal, first-party company document, major broadcaster/wire | NSW Data Centre Guidelines; AEMO; Transgrid; Reuters; ABC; BBC; Microsoft/AWS/AirTrunk/CDC releases |
| B | Established trade press, law firm analysis, think tank, market research | Data Center Dynamics; Information Age; KWM; Bird & Bird; Greenpeace; Westpac IQ; CertifiedStrategic |
| C | Single-source, social, community or aggregator | Change.org petition; Facebook council posts; SUBCO/SMAP; the ~1 GW WA report |
| D | Unusable | none admitted |

`python3 scripts/query.py unverified` lists every row that must not be published as fact. There are
currently 7 such site rows, 3 low-confidence metrics and 1 GAP incentive row.

---

## 3. Pillar A — physical footprint

**National position.** AEMO counts 162 operational data centres, predominantly Sydney and Melbourne,
using ~2% of grid-supplied electricity; 15 sites operate in WA's South West Interconnected System.
The BBC reports 162 operating with 90 more planned and more than A$155bn of investment lined up
(Westpac IQ: >A$155bn, or 5.6% of one year's GDP). Capacity is doubling roughly every four years.

**NSW.** About 60 data centres operating or under construction, with 19 projects in the State
Significant Development pipeline worth A$50.3bn as at July 2026. AEMO forecasts data centres
doubling from 5% of NSW grid-supplied energy in 2026 to 11% by 2030 — over the same period in which
about 7 GW of NSW coal generation retires. The NSW Government's own guidance states plainly that
current regulatory frameworks "are not fit for purpose".

**Queued, not committed.** AEMO's QED Q1 2026 was the first to disclose the transmission connection
queue: 11 projects above 5 MW totalling 5.4 GW of maximum demand, ~60% NSW and ~40% Victoria, most
at early stages. Reported secondary figures put the queue at 9 GW by June with 7.6 GW still at
application stage — flagged low-confidence pending QED Q2.

**The five projects that matter most:**

| Site | State | Status | MW | Capital | Note |
|---|---|---|---|---|---|
| Western Downs Digital Park | QLD | lodged | 2,160 peak / 1,440 IT | A$31.9bn | 725.5 ha former feedlot, ~250 km west of Brisbane; up to four 360 MW AI-ready buildings; Anthropic reported as a prospective user (unverified) |
| Mamre Road Campus ("Summit", AirTrunk SYD4) | NSW | lodged | 1,200 / 1,000 | >A$5bn | 52 ha Kemps Creek; six four-storey buildings; 728 cooling units; 846 diesel generators; >18,000 kL diesel; ~22.4 ML water/yr; ~500 construction + ~500 operational jobs |
| CDC Marsden Park | NSW | under construction | ~1,000 / 504 | — | Largest campus in the Southern Hemisphere when complete; BBC reports construction ~100 m from a community |
| Cloud Carrier Southern Highlands | NSW | lodged | ~700 | — | Moss Vale, 67 ha, served by a proposed 673 MW fossil-gas power station |
| NEXTDC S7 Eastern Creek | NSW | lodged | 650 / 612 | A$7.6bn | OpenAI anchor under OpenAI for Countries; would be among the largest AI data centres globally |

**Cable proximity.** The `nearest_cable_ls_km` field is deliberately empty. It requires geocoding
site addresses against TeleGeography landing-station coordinates (RG-001). Populating it with
estimates would poison a field the brief specifically asks for. Known landing clusters for later
computation: Sydney (Southern Cross and SX NEXT, INDIGO, Hawaiki, APX/EAC), Perth (INDIGO West,
Australia–Singapore Cable, Project Waterworth), Darwin, and the eastern seaboard.

### RG-013 substantially advanced — the proponent list is now primary evidence

A single NSW Government ministerial release does most of this work. On **27 March 2026** the
Treasurer, the Minister for Industry and Trade and the Minister for Planning jointly announced
Round 1 of the **Investment Delivery Authority**: 15 data centre projects worth **$51.9bn**, with
the proponent legal entity and local government area named for each. That list is now in the
database and it resolves most of the NSW pipeline's ownership question at a stroke:

| Proponent (as named by NSW Government) | Project | LGA |
|---|---|---|
| Microsoft Datacenter (Australia) Pty Ltd | Honeman Close Data Centre | Blacktown |
| KNBDC SYD4 Pty Ltd | Mamre Road Data Centre Campus | Penrith |
| NEXTDC Limited | S7 Eastern Creek; S4; S5 + Innovation Hub | Blacktown, Fairfield, Ryde |
| STACK Infrastructure Australia Pty Ltd | 78 Lockwood Road | Penrith |
| Stockland | 2 Davis Rd Wetherill Park; Fife Kemps Creek; "Project A" | Fairfield, Penrith, Ryde |
| Goodman Property Services (Aust) Pty Ltd | "Project Atlas" | Blacktown |
| AIMS Capital Management Ltd | Bella Vista Data Centre Campus | Hills Shire |
| GreenSquare DC Pty Ltd | SYD1 (Stage 2) | Hills Shire |
| Lane Cove DC Alliance | 16–20 Mars Road, Lane Cove West | Lane Cove |
| Lehr Consultants International (Australia) Pty Ltd | Glendenning Road Data Centre | Blacktown |

One further endorsed project is withheld "due to commercial sensitivities". **No AWS, Google or Meta
project appears anywhere on the list** — they are either outside the IDA process, in the withheld
slot, or in another state (RG-023).

**Microsoft is now resolved to a consent.** Kemps Creek Data Centre, **SSD-10101987**, approved
13 July 2023 by the Director. Proponent **Microsoft Datacentre (Australia) Pty Ltd** (Level 27, 1
Denison Street, Macquarie Park), confirmed by the Condition A11 staging plan lodged by Willowtree
Planning in October 2023 for **707-769 Mamre Road, Kemps Creek**. Consent scope: two data storage
buildings, **61 generators**, a substation, a high voltage switch yard and **30 diesel storage
tanks**. Trackers report 190 MW IT load, 60,943 sqm GFA on 14.43 ha and A$1.3bn (grade-C; RG-024).
It sits inside the Mamre Road Precinct immediately adjacent to the proposed 1 GW campus — so
Kemps Creek now has at least three separate consents (Microsoft operating, Stockland Fife endorsed,
Mamre Road 1 GW lodged) whose cumulative diesel generation and air quality impacts are assessed
against each other only if someone adds them up. That is the Department's own cumulative-impact
direction, and this database is now in a position to do the arithmetic.

**The anonymisation problem is worse than expected, and is itself a finding.** The 202.4 MW
**Glendenning Road Data Centre (SSD-73761707)** was **approved on 16 September 2026** — one month
after the NSW Data Centre Guidelines took effect — over **Blacktown City Council's formal
objection**. Three five-storey buildings, 43.2 m maximum height. The planning portal does not
publish the proponent; the NSW Government's own release names *Lehr Consultants International
(Australia) Pty Ltd*, a planning and engineering consultancy. So a 202 MW facility has been approved
in Western Sydney with its developer and end user effectively undisclosed in public documents
(RG-022). Separately, **Project Echidna** (Eastern Creek, 35 MW) and **52 Turner Road** (40 MW, with
diesel and lithium-ion battery storage) show the codename convention that makes attribution hard.

**The subsidy question gets a real answer, and it isn't a tax break.** Two mechanisms are now
documented. First, the IDA endorsement itself: state-facilitated coordination, publicly named, with
a published rejection rate. Second — and this runs the *other* way — a **Voluntary Planning
Agreement between Penrith City Council and Microsoft Datacenter (Australia) Pty Ltd** for Lot 2 DP
1271142, 769 Mamre Road, notified 9 March–6 April 2023, endorsed by council 29 May 2023 and
**executed 7 June 2023**, under which Microsoft makes monetary contributions to fund open space and
landscaping in the Mamre Road Precinct. That is a hyperscaler paying a council, not a government
paying a hyperscaler. The amount is in the executed agreement (RG-025), and surveying VPAs and
s7.11/s7.12 contributions across Blacktown, Penrith, Fairfield, Ryde and Hills Shire would finally
put real numbers into the subsidy debate — in both directions.

**Phantom demand now has a government-side number.** The same release records that the IDA **declined
to endorse around $40.7bn** of data centre and technology proposals as "premature or overly
speculative", against $51.9bn endorsed. That is the first hard Australian quantification of
speculative pipeline, and it independently corroborates the Oxford Economics finding in the NSW
Guidelines that 6 in every 7 MW of connection requests are phantom. It should replace the estimate
in any public communication, because it is the government's own assessment of its own pipeline.

**A methodological negative result worth recording.** The first attempt at RG-013 screened the CER
NGERS corporate table for anonymous ACN-named SPVs with a data-centre emissions signature (very high
scope 2, near-zero scope 1). The two strongest candidates resolved via the Australian Business
Register to **KFC Australia** (A.C.N. 085 239 998 Pty Ltd; scope 2 156,819 t) and **Saputo Dairy
Australia's holding company** (A.C.N. 166 119 133 Pty Ltd; scope 1 127,086 t, scope 2 124,002 t).
Any electricity-intensive, low-combustion business looks like a data centre in NGER data. Emissions
signature is not an identification method; entity resolution must go through ASIC/ABR and
planning-portal proponent names. Recorded as RG-028 (resolved) so the mistake is not repeated.

**Also surfaced, not yet verified:** the Plumpton "Victorian AI Hub" — **Syncline Energy**, 350 ha
about 30 km north-west of Melbourne, an empty paddock next to Melbourne's renewable energy hub off
the Calder Freeway, reported maximum **2.4 GW** across four buildings (more than Loy Yang A), with
the proponent telling residents in writing that construction will not start for at least two years.
Over 3,600 petition signatures. This links the previously unverified Melton "Syncline Energy"
proposal to a named proponent, lifting it from CLAIMED/low to REPORTED/medium. Also noted and
unverified: Wesley Vale (Tasmania), Beetaloo Digital at Berry (NSW south coast), Frederick Street
Artarmon (RG-027).

**One count discrepancy to stop repeating.** The Guardian reported **285** operating Australian data
centres in July 2026; AEMO says **162**; NSW said **90** in March 2026 and **~60** in August 2026
once multi-stage double counting is removed. These are different definitions, not different facts.
Cite the definition, not the number.

### RG-002 resolved — the complete NSW data centre SSD register

`scrapers/ingest_nsw_dc.py` enumerates the portal's Drupal search
(`field_case_type_value=State Significant Development&combine=Data Centre`, nine results per page), resolves
each project slug to its node id, and pulls the structured record from `/node/<nid>?_format=json`. Harvested
**46 projects**; every node JSON archived under `data/raw/nsw_planning/nodes/` with SHA-256 manifests; tidy
output at `exports/nsw_planning/nsw_data_centre_projects.csv`.

**Concentration by local government area** (a project straddling two LGAs is counted in both):

| LGA | Projects | LGA | Projects |
|---|---|---|---|
| Blacktown | 11 | City of Sydney | 2 |
| City of Ryde | 9 | Camden | 2 |
| Lane Cove | 5 | Fairfield City | 2 (+1 straddling Blacktown) |
| Penrith | 4 (+1 straddling Blacktown) | Willoughby City | 2 |
| Cumberland, The Hills Shire, Parramatta, Bayside, Sutherland Shire | 1 each | Cessnock City | 1 |
| Queanbeyan-Palerang Regional | 1 | | |

**By stage:** 24 Determination (all Approved) · 9 Prepare EIS · 5 Assessment · 4 Response to Submissions ·
**3 Withdrawn**.

Three things this settles:

1. **The "19 projects worth $50.3bn" figure in the NSW Guidelines is not the same population as this
   register.** The Guidelines count projects *in the planning pipeline*; 24 of these 46 are already determined.
   Anyone quoting either number needs to say which.
2. **Hyperscalers are invisible in the planning record.** Of 46 projects, none is titled AWS, Amazon, Google
   or Meta. Microsoft appears only through its proponent entity on Kemps Creek (SSD-10101987, approved,
   operating) and Honeman Close (SSD-58601963, in Assessment, description referencing 96 MW — one stage of a
   multi-stage campus, not a total). The sector's convention is codenames: **Project Duke, Atlas, Echidna,
   Apollo, Pluto, Mars, KC1, Road 1** — and the NSW Government's own IDA release confirms the convention
   (Goodman's "Project Atlas", Stockland's "Project A"), with one endorsed project withheld entirely for
   commercial sensitivity. So RG-023 is closed as a *negative*: the NSW planning record cannot map hyperscaler
   footprints. The route is ASIC resolution of the codename SPVs plus the title documents attached to each
   application (RG-035), plus landlord tenancy disclosure.
3. **Withdrawn applications are the missing category in every pipeline estimate.** Augusta Street (Blacktown,
   SSD-10469), 52 Turner Road (Camden, SSD-60185233, 40 MW) and Mowbray Road (Lane Cove, SSD-13475973).
   Together with the IDA's $40.7bn of non-endorsed proposals and Transgrid's 20 GW of unconverted enquiries,
   these are the only *direct* evidence of proposals that did not survive. Any phantom-demand analysis should
   count them.

**Corrections the harvest forced on earlier releases:** 52 Turner Road was recorded as `lodged` from a search
snippet and is in fact **withdrawn**, in Camden LGA; NEXTDC S4 is **approved** (SSD-63741210) at **Horsley
Park**, straddling Fairfield City and Blacktown, not merely IDA-endorsed; NEXTDC S7's portal stage is
**Prepare EIS**, which is *earlier* than "lodged" implies; CDC Marsden Park's description references both
**504 MW and 720 MW**, so the consented capacity may exceed the 504 MW universally reported — reconcile against
the determination before quoting either. New sites added include **STACK SYD01 Erskine Park (450 MW, in
Assessment)**, Davis Road (Cundall) 180 MW, Project Pluto 126 MW, KC1 Kemps Creek 144 MW, NEXTDC S4 Phase 2
134.4 MW, Frederick Street Artarmon 81 MW (Willoughby, Prepare EIS), 23-25 Waterloo Road 70 MW, Project
Echidna 35 MW, 1-5 Khartoum Road 35 MW, Road 1 34.3 MW, 22 O'Riordan Street Alexandria 38 MW, and
**Kurri Kurri** (Cessnock, Prepare EIS) — a regional Hunter siting consistent with Transgrid's public
encouragement to look outside the constrained Sydney basin.

Two artefacts worth naming because they show how thin the public record is: **Lane Cove West Data Centre**
carries four modifications including *"Mod 1 fuel storage"*, and **Roberts Road** carries *"Mod 2 additional
back-up generators and diesel storage"*. Post-consent modifications, not original applications, are where
generator and fuel capacity actually changes — and modifications are not captured by any headline pipeline
figure (RG-034).

---

## 4. Pillar B — capital and control

**AirTrunk.** Blackstone-led consortium (Blackstone Real Estate Partners, Blackstone Infrastructure
Partners, Blackstone Tactical Opportunities, Blackstone's individual-investor PE strategy) with CPP
Investments at 12%; A$24bn enterprise value; FIRB approval was a condition and the deal completed
23 December 2024. FIRB conditions are not published — RG-006 is an FOI task.

**CDC Data Centres.** The February 2025 "sovereign ownership" announcement is arithmetically more
interesting than its framing. CSC ran an international bidding process in late 2024; the existing
shareholders exercised pre-emptive rights over its 12.04%. Result: Infratil (New Zealand) 49.75%,
Future Fund (Cth) 34.55%, CSC (Cth) 12.04%, management 3.66%; enterprise value ~A$17bn; 2.5 GW
across operational, construction and pipeline. The largest single shareholder in Australia's
self-described sovereign data centre operator is a New Zealand-listed infrastructure investor.

**Land is where the superannuation money is.** The Mamre Road site — the largest data centre
proposal in Australia — is held by IFM Investors (industry superannuation capital), listed by ISPT
as "Summit", with AirTrunk identified as buyer *conditional on approval of the 1 GW application*.
Two credible sources describe the owner differently (IFM vs ISPT Core Fund); RG-005 is a title
search to resolve it. This is the cleanest available example of the structure the brief suspects:
domestic retirement capital owning the land and shell, foreign private equity operating it, a
foreign AI laboratory as anchor tenant.

**Public capex commitments on the record:** Microsoft A$5bn (Oct 2023, delivered) and A$25bn
(April 2026, to end-2029); AWS A$20bn (June 2025, to 2029); NEXTDC A$7.6bn (S7); CDC A$2.7bn
(Laverton phase one). Microsoft's accompanying claim of A$36bn local economic contribution and the
equivalent of 186,000 full-time jobs in FY25 is an EY-Parthenon *modelling* output, not an
employment headcount. It should never be reported as data centre jobs — the Mamre Road EIS, by
contrast, claims ~500 operational jobs for a 1 GW campus, which is the honest order of magnitude.

**RG-007 is now a drafted strategy, not just a gap.** `reports/RG007_foi_strategy.md` contains five
ready-to-lodge request templates (Revenue NSW, NSW DPHI/Investment NSW, SRO Victoria, Queensland Revenue
Office, Commonwealth Treasury/FIRB) with the correct statutory basis and fees — NSW $30 per request under the
GIPA Act with processing at $30/hour. Every request is deliberately framed to seek **policy instruments,
determinations, guidelines and aggregate counts**, never a named taxpayer's assessment, because a request
naming a taxpayer will be refused on confidentiality grounds and would waste the attempt. Four free parallel
routes are identified that should be worked first, the strongest being the NSW Legislative Council inquiry
record: a question put to a revenue officer in the 29 May 2026 public hearings, or an industry/union
submission lobbying for or against concessions, would answer this without waiting 8–12 weeks for an FOI
decision. The strategy also commits the Observatory to recording a **documented negative as a publishable
finding** (`incentive_type = none_found`, `fact_status = VERIFIED`) rather than treating absence of evidence
as evidence of concealment.

**Subsidy register — the honest state of play.** Recorded as verified: the NSW 75-day fast-track
(conditionality score 5/5 — 17 performance measures attached), the NSW approvals authority for
projects >A$1bn (1/5), Victoria's A$5.5m Sustainable Data Centre Action Plan (2/5), and the
Commonwealth Expectations (4/5, and the only Australian instrument that already gestures at
domestic compute allocation via Expectation 5). Recorded as a GAP: any cash concession. RG-007
requires FOI to Revenue NSW, SRO Victoria and QRO, plus a review of leasehold terms in the Western
Sydney Employment Area and Aerotropolis.

### RG-009 resolved — the renewable claim audit now runs on primary regulator data

Downloaded, parsed and loaded from the Clean Energy Regulator (archived under `data/raw/cer/` with
SHA-256 manifests; analysis in `reports/cer_analysis.md`; tidy series in
`exports/cer/dc_operators_nger_trend.csv`): NGER corporate emissions and energy data for all six
years 2019-20 → 2024-25, the market-based scope 2 tables for 2023-24 and 2024-25, the LGC
certificate shortfall register (143 entries, 2001-2025), the 2024-25 Safeguard baselines table (228
facilities) and the REC Registry LGC holdings snapshot (1,306 accounts, as at 31 July 2026).

**Location-based scope 2 by controlling corporation, t CO₂-e** *(what the grid electricity actually
emitted; not reducible by buying certificates)*

| Operator (as published) | 2019-20 | 2020-21 | 2021-22 | 2022-23 | 2023-24 | 2024-25 | Δ |
|---|---|---|---|---|---|---|---|
| AirTrunk Australia Holding Pty Ltd | 94,528 | 157,174 | 257,423 | 348,562 | 450,207 | **553,344** | +485% |
| Amazon Corporate Services Pty Ltd | 134,104 | 192,062 | 260,583 | 305,732 | 319,138 | **405,217** | +202% |
| NEXTDC Limited | 218,605 | 293,797 | 350,049 | 348,765 | 335,627 | **358,353** | +64% |
| CDC Group Holdings Pty Ltd | — | 150,136 | 187,397 | 212,744 | 257,540 | **317,465** | +111% (from 2020-21) |
| Equinix Australia Pty Limited | 297,414 | 299,083 | 309,100 | 286,428 | 279,218 | **288,374** | −3% |
| Global Switch Australia | 137,617 | 129,503 | 119,619 | 94,827 | 78,961 | absent | — |
| Telstra Group Limited | 1,140,573 | 1,080,491 | 1,040,346 | 856,726 | 757,967 | **677,664** | −41% |
| Fujitsu Australia Ltd | 120,615 | 110,062 | 89,327 | 68,576 | 59,805 | **55,228** | −54% |

**Scope 1 (back-up diesel and on-site generation), t CO₂-e — 2019-20 → 2024-25:** AirTrunk 132 →
4,165 (+3,055%); NEXTDC 433 → 7,919 (+1,729%); Equinix 1,198 → 1,869; Amazon 771 → 1,007; CDC
absent → 215. NEXTDC's 18-fold rise in a single year (1,614 → 7,919) is the largest jump in the
series and is worth a facility-level follow-up: it is consistent with increased generator running
hours, which is exactly what the 200-hour unregulated window permits.

Five results, each now recorded in the database with its verdict:

1. **The AFR/Greenpeace headline reproduces.** AirTrunk + CDC + Amazon combined scope 2 rose from
   499,372 t (2020-21) to 1,276,026 t (2024-25) — +156%, i.e. more than doubled — and rose +24.3%
   in 2024-25 alone. `VERIFIED`.
2. **AirTrunk's "100% renewable energy by 2025" is `CONTRADICTED` as a statement about Australian
   operations.** Not because the contracts don't exist, but because the claim has no expression in
   statutory data: location-based scope 2 rose 485%, AirTrunk does not appear in the CER's
   market-based scope 2 table in either published year, and holds no account in the REC Registry
   LGC holdings snapshot. A market-based claim that the regulator cannot see is unauditable — which
   is precisely the condition the proposed REGO obligation exists to end.
3. **Only two of eight operators reported market-based scope 2 in 2024-25, and none in 2023-24.**
   NEXTDC reported 345,432 t against 358,353 t location-based — a **3.6% reduction**, and the CER
   records that it covers only 94% of facilities. Fujitsu reported a 47.6% reduction across all
   facilities, but it is a broad IT services group, so the figure is not attributable to data
   centres. A 3.6% market-based reduction is not consistent with a portfolio-wide renewable
   position.
4. **No data centre operator is an LGC-liable entity.** Zero matches across 143 shortfall-register
   entries spanning 2001-2025. Under the RET, liability attaches to retailers and acquirers, not to
   data centres. So a data centre's "100% renewable" claim cannot be tested against its own
   surrender record — it depends on certificates routed through retailers, and those retailers are
   materially failing: shortfall charges of A$180.3m in the 2024 assessment year (AGL Sales
   A$83.6m, Alinta A$96.6m, Red Energy A$54.3m, Lumo A$14.0m) and A$115.5m in 2025 (Red Energy
   A$62.3m, Aurora A$38.2m, Lumo A$15.2m).
5. **No data centre is a Safeguard Mechanism covered facility.** Zero of 228 covered facilities in
   2024-25, and no ANZSIC class referencing data processing or hosting appears at all. Every
   operator's scope 1 is two to three orders of magnitude below the 100,000 t threshold (highest in
   2024-25: NEXTDC at 7,919 t). The structural gap identified in §5 is confirmed on primary data:
   the carbon constraint does not reach this sector while it draws grid power, and would reach an
   on-site gas project like Moss Vale immediately.

REC Registry holdings snapshot (a guide only, per the CER's own caveat — holdings move between
accounts constantly): CDC Data Centres Pty Ltd 233,209 LGCs; Amazon Energy LLC 226,073; Telstra
Energy (Generation) 423,379; **NEXTDC Limited 500**; AirTrunk, Equinix and Global Switch — no
account.

### The water dispute, on the record

The inquiry transcripts put the sharpest factual conflict in the whole Australian debate on the public
record, with both sides named.

**Data Centres Australia (Belinda Dennett, CEO, 1 May 2026, under parliamentary privilege):** "There is
significant misinformation around water use in the public debate. The ABS water accounts show that data
centre water use is 0.04 per cent of Australia's water use, and less than 1 per cent of Sydney's water use.
The 25 per cent of Sydney's water by 2035 that has been widely repeated in the media and in submissions to
this inquiry is not based in fact. It was dismissed by IPART — the independent pricing regulator — as being
unverifiable, and it should be dismissed." DCA also gave a second figure: the Chair attributed to it an
estimate of **1.9 per cent** on 22 May.

**Sydney Water (Darren Cleary, Managing Director, 22 May 2026):** asked by the Chair whether he stood by the
25 per cent forecast — "**We do**, and we acknowledge the uncertainty." His method: forecasts are built on
applications actually received, with obviously duplicative or entirely speculative applications removed.
Current applications alone represent water demand "the equivalent of a new suburb connecting to our
system." He conceded the ten-year figure could be 20, 10 or 5 per cent. And he gave the committee a reason
to weight water applications above energy applications: "by the time places get to applying for water …
they've typically secured that energy connection. We think there is less of a case where the demand that's
coming to a water utility is phantom."

**Assessment.** The two are probably measuring different things — present measured consumption against a
ten-year forward projection from applications — but the framing gap is three orders of magnitude and both
were put to the committee. Sydney Water made **no written submission** to the inquiry, which the Chair
described as perplexing given it was invited to appear. The claim that IPART dismissed the figure is
**unverified** and is RG-042; it should not be repeated in either direction until IPART's determination is
read.

**The strongest quantified evidence in the record came from the housing sector, not the environment
sector.** The UDIA told the committee that a medium-sized data centre using about **5 megalitres per day**
has water demand broadly equivalent to **9,000 homes**; that the Department of Planning's Urban Development
Program identifies about **121,000 housing lots** still to be created across three south-west Sydney growth
areas, constrained by water and sewer; and that survey work representing more than 36,000 planned dwellings
found **22,400 of them — 62 per cent — unable to proceed** for lack of committed water or wastewater
infrastructure. The UDIA also noted that Sydney Water's IPART determination funds it for **100,000 fewer
homes** over five years than the National Housing Accord requires Sydney to deliver. Its five principles:
data centre growth should not displace housing servicing capacity; full cost recovery from proponents not
households; **recycled water and other rainfall-independent supply should be the default servicing model,
with potable water not a routine input**; and an up-front total servicing cap on water volume for data
centres, system-wide or by region. That is a developer-side industry body asking for a hard cap.

**Screened and absent:** Microsoft, Google, Meta, Digital Realty, Macquarie Technology Group, DCI
Data Centers, Cloud Carrier and Vantage do not appear in any CER dataset. This is a threshold-or-
naming result, not evidence of zero emissions — all of them operate Australian facilities. Resolving
it requires the ASIC/SPV work in RG-013, which is now the highest-value remaining Pillar A/B task.

**Circular financing.** No Australian instance of vendor circular financing has been verified. The
closest structural analogue is the OpenAI–NEXTDC arrangement at S7, where OpenAI is to "help plan,
build, run and buy computer processing from" a facility built by an ASX-listed landlord — an anchor
tenant with an operational role, on undisclosed commercial terms (RG-014). Whether the local market
"relies entirely on REITs to fund the shell while tenants supply the hardware" is not yet testable
from this evidence base; NEXTDC is ASX-listed, AirTrunk is PE-owned, CDC is privately held, and
only one of the three is a listed vehicle.

---

## 5. Pillar C — regulatory audit

**The loophole, in the regulator's own words.** NSW Government guidance records that current
regulation allows data centres to use generators for up to 200 hours a year *without being subject
to any point-source emission limits for oxides of nitrogen*, and that planning consents may restrict
only how many generators run concurrently outside emergencies. The 2026 Guidelines then impose NSW
Clean Air Regulation "Group 6" limits (NOx 450 mg/m³, particulates 50 mg/m³, VOC 1,140 mg/m³, CO
5,880 mg/m³), with a US EPA Tier 2 alternative only for sites outside metropolitan cities and
regional towns and away from sensitive receivers. **Victoria is stricter**: its EPA requires
consideration of best available technology including US EPA Tier 4 generators, *prohibits
non-emergency use*, and requires monitoring in operation. That asymmetry is a siting arbitrage and
should be a standing comparison column.

**Cumulative impacts are being adjudicated in real time.** On 10 April 2026 the NSW EPA advised
that the Mamre Road EIS "does not provide the information required to allow us to complete our
assessment", requesting more on air quality, noise, greenhouse gas emissions and waste storage, and
citing proximity to schools, aged care and residences. The Department separately directed assessment
of cumulative impacts in the Mamre Road/Kemps Creek precinct. This is the strongest available
evidence that the assessment system is not simply rubber-stamping.

**Grid rules.** The AEMC's 12 March 2026 draft determination creates a new standard for large
inverter-based loads requiring fault ride-through; it is not retrospective. Transgrid's Network
Capacity Allocation Policy applies to inverter-based loads ≥30 MW/30 MVA, allocates capacity only on
signature of a Network Connection Agreement, and lapses the allocation if planning criteria are not
met within three months — the most effective existing control on speculative connection hoarding
anywhere in the NEM. AEMO estimates ~2 years from application to energisation and a 5–10 year load
ramp.

**Cost recovery.** Transgrid's 26 August 2026 position: where new large users drive network
investment beyond their physical connection, "those costs will be borne by the proponents creating
that demand rather than existing electricity consumers". The Commonwealth's ERC0448/ERC0456 would
put that into the National Electricity Rules. NSW's *Electricity Infrastructure Investment Amendment
Bill 2026* would give the state minister power over grid access. Implementation timelines: 12 months
for the REGO obligation, 24–36 months for connections and registration reform, 6–12 months for the
ministerial rule change requests.

**Carbon.** The Safeguard Mechanism creates a structural perverse outcome: grid-connected data
centres will generally sit below the 100 kt CO₂-e facility threshold because their scope 1
emissions are back-up diesel only, while on-site gas projects like Moss Vale are likely to exceed
it. The dirtier configuration attracts the carbon constraint.

### RG-026 resolved — the first post-Guidelines consent is more binding than the Guidelines

The empirical test of whether the NSW regime actually bites is now answered, and the answer is not
what either the critics or the industry expect. **SSD-73761707, the Glendenning Road Data Centre,
was consented on 16 September 2026** — one month after the Data Centre Guidelines took effect — and
I have read the signed instrument in full (2,172,177 bytes, 35 pages, archived with a SHA-256
manifest).

Schedule 1: Applicant **Lehr Consultants International (Australia) Pty Ltd**; consent authority the
**Minister for Planning and Public Spaces**; site Lot 2 DP 1137162, 2 Glendenning Road; development
the construction and **24/7 operation** of a data centre with **total power consumption of 235 MW**
across three five-storey buildings and **22 data halls**, with emergency back-up generators, cooling
plant, and diesel and lithium-ion battery storage. Signed 14 September 2026 by Joanna Bakopanos,
A/Director Industry Assessments, as delegate under **a delegation executed on 18 August 2026 — one
day after the Guidelines took effect**. File EF24/10658.

*Note a discrepancy I cannot resolve from the public record:* the portal summary and assessment
record describe **202.4 MW**, the signed consent permits **235 MW** total consumption and caps
back-up generation at **267.45 MW** installed. The 202.4 MW figure is most likely assessed IT or
connected load, but the consent does not say so.

**Where the consent is stricter than the Guidelines — considerably stricter:**

- **B20 (condition precedent to operation):** the applicant must demonstrate to the Planning
  Secretary's satisfaction that it has "offset all greenhouse gas generation associated with the
  supply of electricity to the development (**including both non-IT and IT loads**) by demonstrating
  that all operational electricity demand is matched with a portfolio of **additional, firmed
  renewable energy supply at all times**", via **PPA(s) and a firming agreement for NSW-based supply
  within the National Electricity Market**, plus a framework for managing shortfalls through demand
  flexibility and firming. B21 requires written evidence within six months of construction commencing
  that the PPA process has begun.

  This is **hourly matching with explicit additionality, in-state, and covering the whole load** —
  stricter than the Guidelines' Principle 3 test (40% wind, storage at 25% of generation for four
  hours, ten-year terms, pre-FID), stricter than the Commonwealth Expectations, and stricter than
  anything the REGO proposal currently describes. It is imposed as a binding condition precedent, not
  a guideline. **The additionality principle this project has been arguing for is already law in at
  least one Australian consent.**

- **A6:** back-up generation capped at **267.45 MW installed**; total power consumption capped at
  **235 MW**.
- **A7:** generator operation capped at **170 hours per year** — *below* the 200-hour unregulated
  window the NSW Government's own guidance describes. Max 20 generators tested at any one time (max 3
  at 100% load, max 17 at no load), max **1** generator tested during the 6–10pm evening period, max
  **5 hours** of testing per 24 hours. The note defines the count as real-time hours at the site, so
  five generators tested concurrently for an hour counts as one hour — closing the
  multiply-counted-hours loophole.
- **A7(e):** on-site diesel storage capped at **2,000 tonnes** (~2,350 kL). Compare the Mamre Road
  proposal's >18,000 kL.
- **B14:** flue gases vented through **45 m vertical stacks**; total **NOx as NO₂-equivalent below
  10 tonnes per year** from generator operation (the cap does not apply during unplanned outage
  events). *Derived, not stated:* at 267.45 MW for the full 170 hours, 10 t/yr implies roughly
  465 mg/m³ — the same order as the Group 6 limit of 450 mg/m³ — but an absolute mass cap binds
  harder than a concentration limit because it applies however few hours the generators run.
- **B15:** annual emissions testing of at least one generator on a rotational basis, to EPA *Approved
  Methods* (TM-11 for NO₂, TM-2/TM-25 for temperature, velocity, oxygen, flowrate).
- **B16:** generator and enclosure design must **not preclude retrofitting additional air pollution
  controls**.
- **B7:** receiver-specific noise limits in dB(A) L<sub>Aeq</sub>(15 min) that differ between
  "back-up generators in use (including testing)" and "all other times", for named addresses at
  Polonia Avenue Plumpton, Knox Road Doonside, Derby Street Rooty Hill and Nurrangingy Reserve.
- **B22–B23:** a Sustainability Management Plan, approved before operation, requiring continuous
  metering of IT electricity, total electricity and total water; **annual reporting of PUE, WUE and
  CO₂-e**; alignment with the greenhouse gas mitigation hierarchy in the NSW *Guide for Large
  Emitters* (EPA, 2025); measures to prioritise recycled or non-potable water for cooling "where
  available"; and a **three-yearly review** of back-up power technology for lower- or zero-emissions
  alternatives and of water servicing arrangements.
- **Part C disclosure:** the applicant must make statutory approvals, all approved strategies, plans
  and programs (excluding hazard and risk studies), regular environmental performance reporting and a
  comprehensive monitoring summary **publicly available on its website**; C17 requires each
  Independent Audit Report and its response to be published within 60 days. **This is a stronger
  transparency obligation than the Guidelines**, which permit water and energy forecast data to be
  provided commercial-in-confidence.

**Where the consent is weaker than the Guidelines:** no numeric dPUE or dWUE ceiling (B22 requires
reporting and "continual improvement" only, so the Guidelines' dPUE ≤1.25/1.3 and dWUE bands are
absent); no 25% two-hour demand reduction capability (demand flexibility appears only as a way to
manage renewable shortfalls); recycled water is not mandated, only prioritised where available. The
Guidelines are never cited in the consent. The most likely explanation is timing: conditions were
drafted during assessment, before the final Guidelines text existed. That makes this a transitional
artefact rather than a policy failure — but it means the Guidelines' headline efficiency and
flexibility metrics are **not yet reaching consents**, and RG-031 exists to test whether later ones
pick them up.

**Blacktown City Council's objection (12 June 2025, six pages, Judith Portelli, Manager Development
Assessment, file MC-25-000041) asked that its matters be addressed and the response returned to
Council before any determination. Consent issued 15 months later regardless.** The objection matters
because it raises three externalities the Guidelines' 17 performance measures do not measure at all:

1. **Net employment loss.** The proponent's Social and Economic Impact Assessment "does not factor in
   the existing employment numbers across the **3 existing warehouses on the site**". Council demanded
   a revised analysis using existing FTE and skill diversity, or business-as-usual figures if those
   businesses cease. This is the jobs-to-capex critique made by a council inside a statutory process,
   and it is unanswerable from the proponent's own numbers.
2. **Cumulative urban heat.** The site is "in one of the hottest parts of Western Sydney that is
   already vulnerable to urban heat"; servers must be kept below 33.3 °C; the facility "will increase
   the temperature of the microclimate" and the number of hot days and heatwaves for an already
   vulnerable community. The ESD report "fails to appropriately articulate the temperature increase to
   the microclimate generated from the 3 centres compared to a conventional industrial development".
   And: "with Blacktown becoming a preferred location for new data centres this impact is going to be
   intensified as colocation with other DC occurs. Impacts of not only this site, but all existing and
   proposed DC should be better assessed." Council asks for alignment with the *Greater Sydney Heat
   Smart City Plan 2025–2030*.
3. **Parking and amenity.** 823 spaces required under the Blacktown DCP, 165 proposed; the Transport
   for NSW *Guide to Transport Impact Assessment* (2024) yields 179. Building visible above the tree
   canopy at full planting maturity, no other buildings of this height in the vicinity, directly
   abutting Nurragingy Reserve. Underground fuel tanks proposed in the landscape setback. Council:
   "the financial gains of the owner should be balanced with improved investment back into the site
   and surrounding community."

**Proponent resolution — and a transparency failure worth naming.** The signed consent's named
Applicant is a **planning and engineering consultancy**. The ABN on the pre-application document
(54 146 035 707) resolves via the ABR to **Willowtree Planning (NSW) Pty Ltd** — the EIS author, and
the same consultancy that prepared the Mamre Road EIS. Both are agents. The developer and end user of
a 235 MW facility in Western Sydney are not identifiable from the public record (RG-030).

For Mamre Road the ABR does resolve the structure. **KNBDC** is a per-project trust stack, all
registered in NSW 2060 (North Sydney): KNBDC AU Financing Holdco Pty Ltd (ACN 685 936 074, 3 April
2025), KNBDC AU Development Pty Ltd (ACN 687 116 098, 15 May 2025), then for SYD4 a Land Trust, a
Hold Trust and an Intermediate Hold Trust (all Fixed Unit Trusts, all 19 June 2025) with **NBDC Pty
Ltd** (ACN 606 821 452, incorporated 1 July 2015) as trustee, plus parallel MEL3 and "MEL EXP"
stacks including dedicated FinCos. The whole structure was assembled in a ten-week window in
mid-2025. **A web search for "KNBDC" returns zero results**: the sponsor of Australia's largest data
centre proposal is not publicly identified anywhere. The ABR publishes no shareholding, so beneficial
ownership needs a paid ASIC extract (RG-029). The "SYD4" match to AirTrunk's reported site code and
the North Sydney postcode are suggestive and are recorded as inference, not fact.

Also resolved: **Syncline Energy Pty Ltd** (ABN 26 117 458 803, active from 7 December 2005, VIC
3000) — a company incorporated nearly two decades before the AI data centre market, proposing 2.4 GW
at Plumpton. **GreenSquareDC Pty Limited** (ABN 18 656 101 861, NSW 2000). "Lane Cove DC Alliance"
does not resolve to any entity on the ABR, suggesting an unincorporated joint venture or a trading
name.

### Victoria's Development Facilitation Program — the fast track with no checks

Victoria does not merely process data centres quickly. Under **Part 9A of the *Planning and Environment Act
1987* (Vic)**, the Development Facilitation Program:

- sends the application **directly to the Minister for Planning**, bypassing the local council as
  responsible authority;
- lets the Minister **waive or vary planning scheme requirements**;
- removes **VCAT merits review for both applicants and objectors**;
- removes **any review rights over conditions** in Ministerial permits;
- leaves only judicial review on jurisdictional error, procedural unfairness or legal unreasonableness.

Eligibility is a construction-cost threshold: **above $10m in regional Victoria or $20m in metropolitan
Melbourne**. As the practitioner analysis puts it, "given that modern data centre facilities routinely
exceed these thresholds, the DFP is effectively available for all significant proposals", and the advice to
developers is to "**pursue the DFP**" as the default pathway. Victoria's Sustainable Data Centre Action Plan
expressly supports data centre access to it.

The measured effect is at **NEXTDC M3, West Footscray**. The original permit went through the standard
council pathway and drew **more than 80 objections** — noise (the continuous hum of air conditioning), light
pollution, health and wellbeing, and loss of industrial land that might otherwise support diverse
employment. Maribyrnong City Council approved it in 2021 anyway. The **expansion** was lodged through the
DFP. It has drawn **5 objections**, one of them from Maribyrnong City Council — which no longer decides the
matter. The Minister for Planning does.

Objections fell by more than 90 per cent with no change in the underlying amenity issues. Two readings are
possible and both matter: either the DFP suppresses participation because objectors know it cannot change
the outcome, or the expansion is genuinely less impactful. Nothing in the public record distinguishes them,
**and that is the accountability problem** — there is no merits appeal in which the question could be tested.

Two further Victorian features belong in any national comparison. Data centres are expressly classified as
**"Utility Installation" at cl.73.03 of the Victorian Planning Provisions**, giving definitional certainty
that Queensland lacks entirely and NSW has only partially. And the **Environment Protection Regulations
2021 (Vic) do not prescribe data centres as an activity requiring an EPA permission, permit or licence** —
obligations attach instead to associated activities (noise, contamination, waste, diesel storage, back-up
generation), so there is no single Victorian register of data centre environmental permissions to harvest.
That is why Victoria can require US EPA Tier 4 generators and prohibit non-emergency use through guidance
and permit conditions, and why the resulting obligation varies site by site.

The Commonwealth context above all of this: the federal direction that large data centres must be
"**net generators, not net users**" of electricity, with the Commonwealth reserving the right to override
inconsistent state approaches and, as at August 2026, no clarity on how that would operate.

### RG-049 resolved — Australia's largest proposal, read from the lodged application

The Western Downs Digital Park development application was downloaded from the Western Downs Regional
Council register (**343,666,719 bytes, ~870 pages**) and the Town Planning Report decoded: Urbis,
Report V4, Project Code P00 67336, dated **14 August 2026**, prepared for **WDDP Pty Ltd**, lodged
18–19 August 2026. The source PDF was analysed and then removed from the workspace with its SHA-256
manifest and a one-line re-fetch command retained, because 344 MB would crowd out the rest of the
evidence base.

**Capacity, corrected.** "The ultimate campus has been designed to support approximately **2,160 MW of
IT load** (approximately **3,240 MVA total facility demand**) across **six data buildings**. Each stage
incorporates three **540 MVA transformers**, providing continuous N+1 redundancy throughout the
network." Four stages (1A, 1B, 2A, 2B), each data hall 36,000 sqm — 144,000 sqm total. Note the
document's own internal inconsistency: the description of the development says "**four** large Research
and Technology Industry buildings delivered across four stages" while the capacity paragraph says "six
data buildings". Secondary reporting said four buildings of 360 MW totalling 1.44 GW IT, which matches
neither.

**The derived number that matters most: an implied design PUE of about 1.50.** 3,240 MVA of total
facility demand against 2,160 MW of IT load. That is far above the NSW Guidelines' dPUE ceilings of
1.25/1.3 and above the 1.15–1.4 range of recent NSW EISs, and it means roughly **1,080 MW of the
facility's demand is non-IT overhead — more than the entire IT load of NEXTDC's 612 MW S7 project**.
The application does not state a PUE; this is the Observatory's arithmetic and is labelled as derived
in the database. It is the predictable consequence of choosing air cooling in a hot inland climate, and
it is the strongest available quantification of what the water-for-energy trade actually costs.

**Water — the primary document inverts the public story in both directions.** The report states the
development "will utilise **primarily** air-cooled technology", which "eliminates the need for
water-based evaporative cooling". Note "primarily": the widely quoted "100 percent air-cooled" is a
slight overstatement. Mechanical water demand is limited to the **one-time commissioning flush and
fill**. But: "**There is no reticulated (town) water network in the vicinity of the site**", and the
primary supply across all three demand categories is **potable water delivered by road tanker and held
in on-site storage tanks** — arriving treated to drinking-water standard, so no on-site treatment is
required — with rainwater harvesting and treated wastewater reuse as supplementary non-potable sources
and the final strategy **deferred to detailed design**, including "any associated water entitlements".
So this is not a water-neutral design; it is a design with no cooling-water demand and a trucked
drinking-water supply, for a site that will also house **up to 1,500 construction workers**. Demand is
highest during construction.

**Grid and generation.** Substations step transmission voltage to 33 kV; a battery storage system is
integrated **in series between each 33 kV incomer bus and the data building load** through dual power
conversion, described as multi-purpose and supporting **energy arbitrage with the network** — but also
as "an ancillary component of the development … proposed only for the operation of the development",
with no capacity, duration, market registration or contracted flexibility disclosed. The site adjoins
the **Braemar generation hub**: Braemar 1 (~504 MW) and Braemar 2 (~450 MW), gas and coal seam gas,
plus APA's Daandine CGPF (~27.4 MW) — **981 MW of existing fossil capacity** — and the report
acknowledges supply "via the gas power stations and generators" while also describing the locality as
one of the largest renewable energy hubs. Stage 1A connects to the existing network.

**Land and pathway.** 725.5 ha freehold, **Lot 125 on DY516**, frontages to Dalby-Kogan Road and
Grahams Road, 37 km north-west of Dalby, single consolidated lot, single landowner — **Wambo Cattle
Company Pty Limited (A.C.N. 058 718 326)** — currently partially rural with the approved Wambo
Feedlot; two easements including one for electrical transmission; title search and written owner
consent at Appendix B. Assessed under the *Planning Act 2016* (Qld) as **Research and Technology
Industry, Workforce Accommodation and High Impact Industry**, all subject to Impact Assessment with
notification and submission rights; Western Downs Regional Council is assessment manager. **In parallel
the proponent is pursuing declaration as a Prescribed Project under the *State Development and Public
Works Organisation Act 1971* (Qld)**, which would let the Coordinator-General work with regulators "to
ensure that there are no unreasonable delays" — coordination, not override, unless a notice issues
(RG-054). Queensland has no data-centre-specific classification at all, so nothing attaches
data-centre performance measures to a 2,160 MW facility in a state that dissented from the national
renewable-offsetting agreement.

**Proponent — and the pattern is now confirmed twice.** The application names **WDDP Pty Ltd** and
mentions neither Zerra nor AGP nor Anthropic anywhere. The ABR resolves a six-entity Zerra stack, all
NSW 2000: Zerra WDDP Manager Australia (5 Feb 2025), Zerra Investments Australia (17 Apr 2025), Zerra
DC Operator (Australia) (25 Nov 2025, business name "Zerra DC"), Zerra Operator FinCo (**5 Aug 2026**),
and **Zerra WDDP Asset Manager plus Zerra WDDP Investments AU — both 10 August 2026, four days before
the report was dated, neither registered for GST**. Set that against Mamre Road: KNBDC AU Financing
Holdco (3 Apr 2025), KNBDC AU Development (15 May 2025), and the SYD4 Land, Hold and Intermediate
Hold Trusts (all 19 Jun 2025). **Two of Australia's three largest data centre proposals are fronted by
purpose-built SPVs incorporated days or weeks before lodgement, with no operating history and no
publicly disclosed ownership.** That is now a testable proposition rather than a suspicion, and RG-055
tests it across all 24 determined NSW consents. The compliance consequence matters more than the
transparency one: the entity legally responsible for a consent's conditions is routinely a company with
no assets and no traceable owner.

**This changes the subsidy analysis.** The incentive register now spans conditionality scores from 5 to 0:

| Jurisdiction | Mechanism | Conditionality |
|---|---|---|
| NSW | Data Centre Guidelines 75-day pathway | **5/5** — 17 performance measures attached |
| NSW | Penrith VPA with Microsoft | 4/5 — developer pays council |
| Cth | Expectations priority consideration | 4/5 — five expectations, one already covering compute access |
| VIC | Sustainable Data Centre Action Plan | 2/5 — A$5.5m coordination funding |
| NSW | IDA endorsement | 2/5 — coordination, with a published rejection rate |
| NSW | Approvals authority >A$1bn | 1/5 |
| **VIC** | **Development Facilitation Program** | **0/5 — a cost threshold and nothing else** |

### Consent drift: what happens after approval

A consent's original capacity is not its operating capacity. All **17 post-consent modifications** to NSW
data centre SSDs are now in the database (`python3 scripts/query.py drift`), and the pattern is one-way:

| Modification | Site | Change | Decision |
|---|---|---|---|
| SSD-10330-Mod-2 | Roberts Road, Blacktown | **Additional back-up generators and diesel storage** | Approved 6 Mar 2026 |
| SSD-21342738-Mod-2 | Eastern Creek Expansion, Blacktown | **Power consumption increase** | Approved 5 Aug 2026 |
| SSD-9741-Mod-1 | Lane Cove West | **Fuel storage** | Approved 14 Apr 2020 |
| SSD-24299707-Mod-1 | Talavera Road campus, Ryde | **Expansion** | Approved 19 Dec 2024 |
| SSD-10330-Mod-4 | Roberts Road, Blacktown | Changes to operational infrastructure | **Undetermined** |
| SSD-66777221-Mod-3 | Lanceley Place, Artarmon | Fire access and switchroom | Approved 11 Aug 2026 |
| SSD-10101987-Mod-1 | Microsoft Kemps Creek | Data hall fit-out | Approved 18 Nov 2024 |
| SSD-41589232-Mod-2 | 51 Huntingwood Drive | Design updates | Approved 28 Aug 2026 |

**Fifteen of the seventeen were approved.** One was withdrawn — and it was the *scale reduction* at 51
Huntingwood Drive, which was abandoned and replaced by design updates eleven days before the Guidelines took
effect. Two remain undetermined. Four were approved between 5 and 28 August 2026, straddling 17 August.

The **NSW Data Centre Guidelines say nothing about modifications.** Neither does the Glendenning consent
contain any modification-specific performance measure. So a facility that satisfies dPUE, dWUE,
generator-hours, diesel-storage and PPA-additionality tests at consent can move away from all of them by
modification, without fresh exhibition and without a fresh cumulative-impact assessment. RG-045 fetches the
modification reports to quantify each change — the portal's modification pages do not publish the development
description, so the quantum is currently unknown and every `what_changed` field is read off the Department's
own modification title. RG-046 asks the prior question: do the Guidelines, the Expectations or any draft NER
change apply to modifications at all? The Expectations say "new or **expanded**", which suggests expansion is
captured; the NSW text does not address it.

### RG-038 resolved — four consents, six years, and the 200-hour number is a Department standard

I downloaded and read the signed consents for four NSW data centres spanning six years. Together they
turn several open questions into measured facts.

| | Roberts Road | DCI Poplars | Davis Road | Glendenning Road |
|---|---|---|---|---|
| Case | SSD-10330 | — | SSD-59416728 | SSD-73761707 |
| Approved | **14 Jul 2020** | — | **20 Dec 2024** | **16 Sep 2026** |
| Applicant on the consent | **Canberra Data Centres Pty Ltd** | **The Trustee for NineZero DC Sub Trust I** | **Cundall Johnston and Partners Pty Ltd** | **Lehr Consultants International (Aust) Pty Ltd** |
| Total power cap | — | — | 160.85 MW | 235 MW |
| **Installed back-up generation cap** | **170 MW** | **35 MW** | **181.92 MW** | **267.45 MW** |
| **Generator hours per year** | **200** | **200** | **200** | **170** |
| Diesel storage cap | 2,000 t | 2,000 t | **none** | 2,000 t |
| Generator testing concurrency | real-time counting | max 1 at a time | max 6 at a time | max 20; max 3 at full load; max 1 in 6–10pm; max 5 h/day |
| NOx mass cap | none | none | none | **<10 t/yr as NO₂-eq** |
| Stack height | none | none | none | **45 m vertical** |
| Annual emissions testing | present | — | — | present, rotational |
| Renewable procurement / additionality | **none** | **none** | **none** | **all demand incl. non-IT, additional firmed, at all times, NSW NEM PPAs** |
| PUE / WUE | none | none | none | reporting only, no ceiling |
| Recycled / non-potable water | none | none | none | prioritised where available |

**Three findings.**

**1. The "200-hour loophole" is not a regulatory gap — it is a standard consent condition.** Roberts
Road (2020), Davis Road (2024) and DCI Poplars all cap generator operation at *exactly* 200 hours per
year including testing. That is the same figure the NSW Data Centre Guidelines describe as the current
unregulated window. So the Department has been writing 200 hours into data centre consents for at
least six years. Glendenning's 170 hours is the **first departure** in this sample. The correct
critique is therefore not "the regulation permits 200 hours" but "the consent authority has chosen 200
hours, consistently, and only once chose differently."

**2. Installed back-up generation exceeds the facility's entire load in every consent where both are
stated.** Glendenning: 267.45 MW installed against a 235 MW consumption cap (ratio 1.14). Davis Road:
181.92 MW against 160.85 MW (1.13). Roberts Road: 170 MW installed. These are not standby reserves
sized for a fraction of load — **they are parallel power stations sized to carry the whole facility**,
sitting behind every consent. In three of the four they carry no NOx mass cap, no stack height
requirement and no emissions testing condition. That reframes the diesel question: the issue is not
that generators might run 200 hours a year, it is that the installed capacity to run the entire data
centre on diesel already exists, and mostly unpriced for air quality. Against that, Mamre Road's
proposal of 846 generators and >18,000 kL of diesel is roughly nine times the 2,000-tonne storage cap
the Department has applied consistently since 2020.

**3. Only one of four applicants is an operating data centre company.** Canberra Data Centres Pty Ltd
(2020) is. The others are a consulting engineer whose own name is in the project title (Cundall
Johnston and Partners, 2024), a planning and engineering consultancy (Lehr Consultants, 2026), and a
**trust trustee** (The Trustee for NineZero DC Sub Trust I). Add Mamre Road's KNBDC SYD4 Pty Ltd and
Western Downs' WDDP Pty Ltd and **four of the six most consequential Australian applications name an
entity that is not an identifiable operator** — and the only one that does is the oldest. The
compliance consequence outweighs the transparency one: the legal person responsible for a consent's
conditions is routinely a consultancy or a freshly incorporated trustee.

Two documents that would settle related questions are **access-restricted** (HTTP 401, `field_is_public`
false): an **"ASIC certificate Amazon Corporate Services Pty Ltd"** filed on the Davis Road application
— the first documentary trace of a hyperscaler inside an NSW data centre planning record, which is why
RG-023 has been reopened — and a document titled **"CDC Data Centres response warning letter"** on the
Roberts Road project. Every project's compliance tab in the portal reads "There are no enforcements for
this project", so a warning letter would sit below the disclosure threshold. RG-057 and RG-058 are FOI
tasks. The Roberts Road record also carries a **political donation disclosure**, which is public but a
scanned image with no extractable text — directly relevant to the inquiry's terms of reference (h)(iv)
on lobbying and donations.

### RG-046 resolved — the Guidelines cannot reach modifications, by construction

Section 3 of the NSW Data Centre Guidelines sets out what the Government actually offers, and it is
more than the 75-day headline: a **concierge function inside DPHI** that proactively engages
proponents; **pre-assessment proponent support that begins before a site has been selected**, advising
on site selection and on what to expect, before the request for SEARs; **SEARs within two months** and
proportional to the assessment; **DA assessment in no longer than 75 days** in state government hands;
and **dedicated post-consent staff specifically for data centres**.

The mechanism sentence is the important one:

> "Applicants submitting data centre applications will need to demonstrate whether they comply with
> the Guidelines in their assessments. **Conditions will then require applicants to meet obligations,
> mitigation measures and commitments outlined in their Environmental Impact Statement.** Compliance
> will be monitored in line with existing DPHI compliance practices and programs."

So the Guidelines do not impose fixed numeric ceilings. They require the proponent to demonstrate
compliance, and then **convert the proponent's own EIS commitments into consent conditions**. That
explains exactly what the four-consent comparison found: Glendenning has all-times renewable matching
and a 10 t/yr NOx cap because its EIS and assessment produced them, not because a schedule of limits
exists. It also explains why there is no dPUE ceiling anywhere — a ceiling can only appear if the
proponent offered one.

And it answers RG-046 by construction. The Guidelines are addressed to "applicants **submitting** data
centre **applications**" and to commitments "outlined in **their Environmental Impact Statement**". A
modification under s.4.55 does not submit an application with an EIS; it varies an existing consent.
There is no instrument by which the Guidelines' performance measures attach to it. Post-consent
activity is reached only through "annual reviews, Independent Audits and other periodic reporting
requirements" — monitoring against the *original* commitments, not a re-test against current standards.
Combined with the observed drift (additional generators and diesel at Roberts Road approved March 2026,
a power consumption increase at Eastern Creek approved August 2026, four modifications approved between
5 and 28 August 2026), **the framework has no ratchet**: a facility can only be held to what it
promised when it was approved, and the promise can be varied afterwards without the Guidelines
re-applying.

Two further things Section 3 and Principle 1 concede that the critique should use honestly. The
Guidelines state outright that "**typically, data centres that use less water use more energy and vice
versa**" — the trade-off the S7 and Western Downs cases both illustrate is acknowledged government
policy, not an oversight. And they define recycled water to include "**on-site water treatment, such as
from captured stormwater**", which is a much weaker definition than "recycled wastewater network" and
would permit a facility to claim compliance with Principle 1 Ref 2 using its own roof runoff.

### Governance findings from the inquiry record

Three accountability findings, all from the corrected transcripts:

1. **The Premier's Department made no submission** to the inquiry despite an invitation, and despite budget
   estimates evidence that a government submission was expected. Secretary Simon Draper PSM said the
   department thought appearing in person "would probably be more effective for the Committee." The Chair
   replied: "**It's not.**" Ms Jacqui Munro MLC established that no submission had been prepared and none had
   been sought from the Minister.
2. **Sydney Water also made no submission.** The Chair: "you're only here because you were invited. Some
   Committees take the view that if you don't get a submission, you don't then invite a witness, so it was a
   little bit perplexing that we didn't end up with a submission."
3. **The only land tax discussion in the record runs the opposite way to a concession.** On 8 May 2026 a
   committee member proposed that community benefit sharing might be funded by "a shift in land tax
   associated with data centres". The witness had done no analysis of the implication and cautioned that
   market equality within zones would need to be considered. Nobody proposed a land tax *exemption*.

The committee — chaired by **Abigail Boyd MLC (The Greens)** — reports by **3 November 2026**. Its terms of
reference cover, in order: scale and clustering; the planning framework including SSD classification and
fast-track mechanisms such as the IDA; electricity demand, grid impacts and on-site back-up generation;
water and cooling; local environmental and community impacts including heat; **land use and housing,
including the opportunity cost of allocating industrial land to data centres and whether resource demands
impinge on new housing supply**; economic and distributional outcomes including **(g)(iii) "the extent of
public subsidies, concessions or state directed facilitation provided to the sector"**; governance and
transparency including conflicts of interest in accelerated approval frameworks and **the impact of lobbying
and donations**; workforce; and lessons from other jurisdictions. That is this project's scope, set by a
parliament, with a report date. **Anything the Observatory publishes after 3 November 2026 must be read
against the committee's findings.**

**Unions NSW made the only quantified workforce-conditionality proposal in the Australian record:** local
content quotas and apprentice quotas for data centres *and their associated renewable energy*, at no less
than the standards already set by the **Renewable Energy Sector Board** for renewable energy zones, plus
training, WHS and industrial standards. Because the RESB precedent already exists in an adjacent sector, the
feasibility objection is weak. Unions NSW also warned that the NSW Government's proposed model — operators
putting money into the market to fund renewable energy rather than directly building it — risks being
"opaque", preventing local content from being tracked. That is a direct critique of the Guidelines' PPA
portfolio approach and of the proposed REGO certificate scheme, and it is the strongest available argument for
requiring project-level rather than portfolio-level contracting (RG-044).

### RG-060 resolved — all twenty consents, and two corrections to my own earlier findings

`scripts/consent_condition_audit.py` now indexes all **6,866 attachments across 63 archived project
nodes**, ranks and selects the best consent document per project, skips anything the portal marks
`field_is_public=false`, downloads under a 12 MB cap with SHA-256 manifests **and per-document
extraction-yield statistics**, then runs a 21-test condition battery and parses Schedule 1. All 20
determined and approved data centre SSDs were processed; **all 20 extract above the reliability floor**
after the 2026-09-18 pypdf re-extraction (see v2.1.0) — the earlier run had 18 of 20, with Lane Cove
West and Macquarie Park lost to AES-encrypted PDFs the dependency-free extractor could not open.
Matrix: `exports/nsw_planning/nsw_dc_consent_conditions.csv`; determination layer:
`exports/nsw_planning/nsw_dc_consent_determinations.csv`.

| Condition | Consents with it (of 20) |
|---|---|
| Website public disclosure | **19** |
| Diesel storage cap | 14 |
| Cap on installed back-up generating capacity | 14 |
| Generator hours cap — **200 h/yr** | **14** (plus 170 at Glendenning, 173 at Pluto, 187 at Project Apollo) |
| Battery storage provision | 8 |
| Annual emissions testing | 6 |
| **Any PUE provision** | **7** |
| **Renewable supply / PPA condition** | **5** |
| **Any WUE provision** | **4** |
| **Recycled or non-potable water provision** | **5** |
| Stack height requirement | 3 |
| **NOx mass cap (t/yr)** | **2** |
| Tier standard / best available technology | 2 |
| Numerically stated NOx concentration limit | 0 |
| **Cites the NSW Data Centre Guidelines** | **0** |

**The Guidelines are cited in zero of twenty consents — including Glendenning and Project Apollo,
determined after they took effect.** They have no legal footprint in the instrument that actually binds anyone.

**Two corrections to what I reported earlier, both found by this run rather than by re-reading:**

1. **Website disclosure is not a Glendenning distinction.** In §5.1 I called the consent's requirement
   to publish approvals, plans, performance reporting and Independent Audit Reports on the applicant's
   website "a stronger transparency obligation than the Guidelines". It appears in **19 of 20**
   consents. It is standard Department practice. The claim was wrong and is retracted here rather
   than left standing.
2. **The apparent demand-response prevalence was a parser false positive.** My `demand_response`
   pattern matched in 17 of 20 consents. On inspection every match is the consent's *definition* of
   Load Curtailment and a condition **prohibiting** it — "this development consent does not permit the
   use of the back-up generators … to support load curtailment at the site". That is consistent with
   NSW Guidelines Principle 2 Ref 9, which excludes diesel. But the real finding is the gap: **no
   consent in the sample requires any non-diesel demand response capability at all.** The Guidelines'
   25% / two-hour measure appears nowhere.

**The NOx result is more interesting than my four-consent version, and it inverts the story.** There
are two mass caps, not one, and **the stricter one is not the post-Guidelines consent**:

- **NEXTDC S4, Horsley Park** — stacks **38.7 m**; total NOx as NO₂-equivalent below **5.5 t/yr**,
  **including testing and commissioning**. Also the largest diesel cap in the sample at **4,472 t**,
  installed back-up 360 MW against a 294 MW load cap, and one of only two Tier references.
- **Glendenning Road** — stacks **45 m**; NOx below **10 t/yr**, **excluding unplanned outage events**.

NEXTDC Limited is the Schedule 1 applicant for S4, so an operating company voluntarily accepted the
tightest air-quality limits in the state, in a consent that predates the Guidelines. That is the
strongest available evidence for the Section 3 mechanism — conditions track what the proponent's own
EIS offered — and it demolishes the argument that strict conditions deter investment. It also means
the Department's post-Guidelines consent was *less* strict than a proponent-led one two years earlier.

**Four codenames resolved from Schedule 1**, which is the constructive half of RG-035 — and since
v2.1.0, **all twenty applicants parse** (RG-065 resolved):

| Project | Schedule 1 applicant |
|---|---|
| Grand Avenue Expansion, Rosehill | **Equinix Hyperscale 2 (SY10) Pty Limited** |
| Talavera Road Campus Expansion | **Macquarie Data Centres Pty Ltd** |
| Project Apollo, Macquarie Park | **Goodman Property Services (Aust) Pty Limited** |
| Project Pluto | **Goodman Property Services (Aust) Pty Ltd** (same company, two consents) |
| NEXTDC S4, Horsley Park | **NEXTDC Limited** |
| Roberts Road | **Canberra Data Centres Pty Ltd** (so Roberts Road is a CDC facility) |
| DigiCo SYD1 Expansion | HDI SYD1 Property Holdings Limited |
| 43–61 Turner Road | ARUP Pty Ltd (the engineering consultancy) |
| Project Echidna | ARUP Australia Pty Ltd (a **different** Arup legal entity) |
| 51 Huntingwood Drive **and** Apollo Place | **EMKC Cubed Management Pty Ltd** (both) |
| Glendenning Road **and** Station Road Expansion | **Lehr Consultants International (Australia) Pty Ltd** (both) |
| Davis Road (consent and Mod 1) | **Cundall Johnston and Partners Pty Ltd** (both) |
| 1–5 Khartoum Road | **Stockland Development Pty Limited** |
| Macquarie Park (SSD-10467) | **Stockland Trust Management Limited** |
| Lane Cove West | **Greenbox Architecture Pty Ltd** (an architectural practice) |
| DCI Poplars | The Trustee for NineZero DC Sub Trust I |
| Dicker Data | Dicker Data Limited (warehouse/distribution centre; end-user) |

**Only 4 companies operating data centres hold consents in their own group name — 5 of the 20 consents.**
The rest: Equinix resolves through its project SPV; two Stockland property entities; one listed end-user;
**seven consents held by consultancies or an architectural practice** (two Arup entities, Cundall ×2,
Lehr ×2, Greenbox); and four by opaque vehicles or a trust trustee (EMKC ×2, HDI SYD1, NineZero). In
**11 of 20 consents the legal person responsible for every condition is either a consultancy or an
entity whose controller is not disclosed on the instrument.** Still no AWS, Google or Meta entity in
any Schedule 1 — which *strengthens* the RG-023 negative, except for the access-restricted Amazon
ASIC certificate on Davis Road.

The most concerning single entry is **EMKC Cubed Management Pty Ltd**: one undisclosed vehicle holds
the consent for **51 Huntingwood Drive** — which carries the **largest installed back-up generation in
the sample at 632 MW**, larger than most of the facilities it would back up — *and* for **Apollo Place
in Lane Cove**. Those are the two corridors with the most concentrated data centre activity and the
loudest community opposition in the state, and in neither case does the public record say who operates
the facility or who is legally responsible for the conditions (RG-064).

**Installed back-up generation exceeds the load cap in all six consents stating both:** Glendenning
267.45/235 (1.14×), Davis Road 181.92/160.85 (1.13×), NEXTDC S4 360/294 (1.22×), Project Apollo
185/135 (1.37×), Apollo Place 63.8/45 (1.42×), Project Pluto 170/100 (**1.70×**). Systemic, not
anomalous.

### The determination register — who decided, when, under what delegation (v2.1.0, RG-079 resolved)

Every one of the 20 signed consents now carries its execution block, parsed from the instrument's own
cover page and cross-checked against portal node metadata (`field_date_of_determination_mp`). Full
register: `exports/nsw_planning/nsw_dc_consent_determinations.csv` and the 20 `case_handling` signatory
rows in the database. In chronological order:

| Determined | Consent | Signatory (title) | Delegation executed | Case officer |
|---|---|---|---|---|
| 2019-04-12¹ | Dicker Data (SSD8662) | Anthea Sargeant (Executive Director) | 2017-10-11 | Chloe Dunlop |
| 2019-11-15¹ | Lane Cove West (SSD-9741) | Anthea Sargeant (Executive Director) | 2017-10-11 | Patrick Copas |
| 2020-07-14 | Roberts Road (SSD-10330) | Anthea Sargeant (Executive Director) | 2020-03-09 | Patrick Copas |
| 2021-05-28 | Macquarie Park (SSD-10467) | Chris Ritchie (Director) | 2021-04-26 | Patrick Copas |
| 2022-12-16 | Station Road (SSD-33781208) | Chris Ritchie (Director) | 2022-03-09 | Patrick Copas |
| 2023-09-15 | 51 Huntingwood Drive (SSD-41589232) | Chris Ritchie (Director) | 2022-03-09 | Shaun Williams |
| 2024-01-19¹ | Talavera Road (SSD-24299707) | **[Name of Commissioner]** — placeholder | IPC determination | Joanna Bakopanos |
| 2024-04-05 | Project Echidna (SSD-47320208) | Chris Ritchie (A/Executive Director) | 2022-06-14 (IPC) | Shaun Williams |
| 2024-12-16 | Grand Avenue (SSD-53338465) | Joanna Bakopanos (A/Director) | 2022-03-09 | Thomas Bertwistle |
| 2024-12-20 | Davis Road (SSD-59416728) | Joanna Bakopanos (A/Director) | 2022-03-09 | Shaun Williams |
| 2025-08-15 | Davis Road Mod 1 (tree removal) | Catriona Shirley (A/Team Leader) | 2022-03-09 | Dave Auster |
| 2025-10-09 | Apollo Place (SSD-67407231) | Joanna Bakopanos (A/Director) | 2022-03-09 | Jeffrey Peng |
| 2025-11-06 | DCI Poplars (SSD-64287712) | Joanna Bakopanos (A/Director) | 2022-03-09 | Patrick Copas |
| 2025-11-21 | 43–61 Turner Road (SSD-68013714) | Joanna Bakopanos (A/Director) | 2022-03-09 | Shaun Williams |
| 2025-12-23 | DigiCo SYD1 (SSD-69637456) | Chris Ritchie (Executive Director) | 2022-03-09 | Shaun Williams |
| 2025-12-24 | NEXTDC S4 (SSD-63741210) | Chris Ritchie (Executive Director) | 2022-03-09 | Shaun Williams |
| 2026-03-11 | 1–5 Khartoum Road (SSD-63235720) | Joanna Bakopanos (A/Director) | 2022-03-09 | Shaun Williams |
| 2026-07-23 | Project Pluto (SSD-69223466) | Joanna Bakopanos (A/Director) | 2022-03-09 | Shaun Williams |
| **2026-09-02** | **Project Apollo (SSD-74069708)** | Joanna Bakopanos (Acting Director) | **2026-08-18** | **Patrick Copas** |
| **2026-09-14**² | **Glendenning Road (SSD-73761707)** | Joanna Bakopanos (A/Director) | **2026-08-18** | **Shaun Williams** |

¹ Execution date is an image stamp absent from the text layer (Dicker, Lane Cove West) or year-only
(Talavera, "Sydney 2023"); date shown is the portal determination date. ² Signed 14 September, registered
16 September — the only signing-to-registration gap in the sample; the Notice of Decision confirms "Date
of decision 14 September 2026".

What the register shows beyond the individual rows:

- **Five signature blocks decide everything**: Bakopanos 9, Ritchie 6, Sargeant 3, Shirley 1, and one
  unnamed IPC panel. One acting director signs 45% of the sample and both determinations made after the
  Guidelines took effect.
- **Four delegation regimes since 2017** (2017-10-11 → 2020-03-09 → 2021-04-26 → 2022-03-09), then a
  five-year stable period under the 9 March 2022 delegation (12 instruments), broken by the **delegation
  executed 18 August 2026 — one day after the Guidelines took effect** — under which both post-Guidelines
  consents were signed. The delegation instrument itself has not been sighted; its existence and date are
  established by the consents signed under it (recorded as a regulatory event).
- **The pipeline-to-signature loop is one office**: Joanna Bakopanos appears as *case planner* for
  Talavera Road in the portal's own planner assignments, and as signatory of nine consents. Assessment
  and determination are legally separate functions — but Industry Assessments both manages and signs
  the pipeline, and Williams + Copas officer 15 of the 20 determined consents (75%).
- **Glendenning's portal project description says 202.4 MW; the signed consent permits 235 MW.** The
  discrepancy is unexplained on the public record (see RG-026 pack notes).

### Kurri Kurri: the site that satisfies the critique and the one that doesn't

The **Kurri Kurri Data Centre** (SSD-128819490, Prepare EIS) is a 540 MW proposal on 21 ha at Hart Road,
**Loxford**, in the Cessnock LGA — the former Hydro Aluminium Kurri Kurri smelter site in the Hunter. The
smelter opened around 1969, ceased production in 2012 and was closed by Norsk Hydro in 2014; remediation is
substantially complete and the site is largely vacant. The proposal is a large two-storey facility with **two
substations connecting to the existing 132 kV Ausgrid transmission line**, adjacent to Snowy Hydro's **660 MW
Kurri Kurri gas power station** which launched in 2025.

This is, almost point for point, what the NSW Data Centre Guidelines say they want: brownfield, remediated,
outside the constrained Sydney basin, co-located with existing generation and transmission, in a region
seeking economic diversification. The Guidelines even predict the benefit — development where the network has
spare capacity can *reduce* consumer bills because new demand pays for assets running below potential output.
Any critique that treats all data centre siting as equivalent loses this case, and should say so.

It also carries the cost. In 2020 the same site was sold to **Stevens Group and McCloy Group** to develop
**"Loxford Waters"**, a 2,000-hectare suburb with **2,000 new homes** plus industrial estates and a business
park. That is the inquiry's terms of reference (f)(iii)-(iv) — whether data centre resource demands impinge on
new housing supply — realised on a specific parcel, and it belongs in the database next to the UDIA's
121,000 constrained lots.

Two further cautions. The applicant is **ADW Johnson Pty Ltd**, a project management firm, and the **intended
end user is unclear** — the third instance in this database of a consultancy or project manager being the
named applicant for a large facility, after Lehr Consultants at Glendenning Road and Willowtree Planning on
the Mamre Road documents. And the co-located generator is a **gas** peaker, so "close to generation" here
means close to new fossil capacity; whether that counts as the colocation the Guidelines intend is a question
worth putting to the Department.

**The single most important structural finding in Pillar C: of the 17 instruments this database
tracks, exactly 4 are binding.** The SOCI Act, the Safeguard Mechanism, the NSW Clean Air Regulation
and the (still-in-consultation) CIRMP rules. Everything else — the Commonwealth Expectations, the
NSW Data Centre Guidelines, the AEMC draft determination, the ministerial rule change requests, the
NSW amendment bill, Transgrid's allocation policy, Victoria's action plan and strategy, both
inquiries — is a guideline, a draft, a proposal, an announcement or a policy expectation. Run
`python3 scripts/query.py law` to see the split. The Australian data centre regime is, as at
September 2026, overwhelmingly soft law with hard political momentum behind it. That is the critique
worth making, and it is a stronger one than "the rules are too weak": the rules barely exist yet,
and the window to make them binding is the next 12–36 months of implementation.

**National security.** The data storage or processing sector is a critical infrastructure sector
under the SOCI Act; the 2025 Measures No. 1 amendments commenced 4 April 2025, clarifying
obligations for systems storing or processing business critical data and deeming certain
government-owned or operated data storage systems critical infrastructure assets. CISC began
consulting on enhanced CIRMP rules on 16 December 2025. Separately, the Hosting Certification
Framework (60 Certified Strategic facilities across 13 providers) is the only mechanism that
currently ties a facility to sovereign government workload.

**An unresolved sovereignty question worth a legal note:** at S7 the asset is Australian-owned and
ASX-listed while the anchor tenant — a foreign AI laboratory — is to help plan, build, run and buy
compute from it. The SOCI Act reaches assets and data, not tenant influence over operations. Whether
that constitutes foreign control of domestic compute is a live question the current regime does not
clearly answer.

**The inquiry.** The NSW Legislative Council self-referred an inquiry into data centres on 29 January
2026; submissions ran 4 February to 27 March; public hearings began 29 May; terms of reference were
updated 5 August 2026. Roughly 120+ submissions are freely downloadable primary evidence (RG-015).

---

## 6. Pillar D — community and externalities

**Institutional objections (severity 4–5).** Penrith City Council objected to Mamre Road, calling
the site "not suitable for a proposed development of this scale". Mamre Anglican School, directly
across the road, raised air quality, noise, generator and diesel-storage proximity, and fire
consequences, and has identified an alternative site while seeking government help to relocate. The
Catholic Church of the Diocese of Parramatta objected outright, citing cumulative impacts, emergency
access, servicing resilience and stormwater feasibility affecting Emmaus Retirement Village. The
Catholic Schools Parramatta Diocese did not object in principle but asked that generator testing
occur outside school hours.

**Campaign formation.** "Stop the Slop" (Western Sydney) protested on 16 August 2026, the day
before the NSW Guidelines launched, calling for a moratorium pending consultation. Organisers asked
where water and power will come from, how waste will be managed, what happens during an outage, and
what the effect will be on local power and water prices. Melton residents rallied against a
Syncline Energy proposal with a council meeting on 27 July 2026; a Change.org petition followed.
Southern Highlands protests were called over the Moss Vale gas proposal.

**Lived amenity.** In Lane Cove, residents report a constant low-frequency hum from an operating
facility 350 m from homes — described as a jet plane about to take off, or a high-pitched whine —
with four more data centres in the pipeline at the local industrial park. At Marsden Park, the
largest campus in the Southern Hemisphere is under construction about 100 m from a community.

**Price and resource externalities.** Climate Council modelling: without significant new renewable
generation and storage, data centres could push NSW power prices 26% higher by 2035. Sydney Water
projects data centre demand equal to roughly a quarter of Greater Sydney's yearly drinking water
supply by 2035, and reported rising potable demand from data centres as a factor in the 2025 price
determination (a A$168/household/yr increase). An SMH investigation put the Western Sydney capacity
increase at the equivalent of more than 10 million households' average load, demanding almost four
times as much power as the rest of the city at peak. IPART has been asked to review water pricing
for data centres.

**The externality the brief does not mention.** NSW's own guidance identifies a benefit case the
critique should engage with honestly: data centres sited where the network has spare capacity —
former coal stations, REZ locations — can *reduce* consumer bills by paying for assets running
below potential output, whereas the same load in congested Sydney brings forward upgrades. The
Guidelines also note data centres will "increase the supply of rainfall-independent water" because
their investment can fund recycled-water infrastructure that serves other users. A critique that
ignores both will be dismissed; a database that can test both will not be.

---

## 7. Pillar E — dismantling the unworkable ideas

The full register is in the `engineering_claims` table (`python3 scripts/query.py --sql "SELECT *
FROM engineering_claims"`) and in the viewer's *Engineering critique* tab. Summary verdicts:

| Proposition | Verdict |
|---|---|
| Standalone islanded power | **PARTLY SOUND.** Diagnosis of a real externality, wrong location. Australian diesel is back-up, not baseload, and the harm is a 200-hour/yr unregulated NOx window plus fire and diesel-storage risk in residential corridors — not stranded carbon assets. One genuine islanded case exists: Moss Vale's 673 MW gas station. |
| Mandate synchronous condensers | **FACTUALLY WRONG PREMISE.** Right objective, wrong instrument. Condensers are network-side. Replace with fault ride-through compliance, priced system-strength contributions, AEMO-registered demand response, and storage at 25% of generation for four hours. |
| Evaporative cooling on potable water | **PARTLY SOUND.** Real pressure, but design WUE already averages 1.0 in NSW EISs and the largest proposals are going waterless. The binding failure is infrastructure sequencing: S7 abandoned recycled water because pipeline planning permission was unavailable, and took an energy penalty instead. |
| Unconditional subsidies for foreign hyperscalers | **PARTLY SOUND.** Unevidenced as cash in Australia; verifiable as procedural speed and now heavily conditioned. Sharpen what exists: quantify Expectation 5, publish operating FTE per 100 MW, make fast-tracking revocable, take equity where state land is provided, and publish an in-kind subsidy register. |
| Scope everything to the NEM | **FACTUALLY WRONG PREMISE.** Would omit WA entirely and mis-state Queensland's and the NT's position. Scope to Australia with a `market` column. |
| Take renewable claims at face value | **UNSOUND AS STATED.** Adopt NSW Principle 3 Ref 13 as the audit standard and reconcile to CER certificate surrenders and NGERS emissions. |
| Treat the pipeline as future load | **UNSOUND AS STATED.** Store lodged / signed / energised separately, publish the basis on every figure, and apply the ~20% proceeds-likelihood haircut. |

---

## 8. Reproducing and extending this database

```bash
cd au-dc-observatory
python3 scripts/build_db.py                       # rebuild SQLite + CSV + viewer/db.json + build report
python3 scripts/query.py --list                   # 15 preset queries
python3 scripts/query.py dossier SITE_MAMRE_ROAD  # full evidence dossier for one site
python3 scripts/query.py unverified               # everything that must not be published as fact
python3 scripts/load_pack.py data/packs/EXAMPLE_pack.json --dry-run   # curated ingestion, validated
```

The viewer (`viewer/index.html`) is dependency-free with inline CSS and no network calls; it reads
`viewer/db.json`. In a sandboxed preview `fetch()` is blocked and it falls back to a static
snapshot — serve it locally (`python3 -m http.server`) for the live version, or work from the CSVs.

**Ingestion policy.** No scraper writes to the database. `scrapers/ingest_nsw_planning.py` archives
raw HTML with SHA-256 manifests and emits a worklist; `scrapers/ingest_cer.py` targets the Clean
Energy Regulator's NGERS, RET/LGC and Safeguard datasets. Both are single-threaded, rate-limited,
carry a descriptive User-Agent and stop on request. A human curates the raw material into a JSON
pack, and `scripts/load_pack.py` validates it (unknown columns rejected; `source_id` must resolve;
provenance mandatory) before writing, logging every action to `ingest_log`.

**Next six tasks, in priority order:** RG-007 (FOI on tax and land concessions — settles Pillar B's
central claim), RG-002 (NSW Planning Portal SSD ingestion — 19 projects, A$50.3bn), RG-013
(hyperscaler site mapping, now also the route to explaining Microsoft/Google/Meta's absence from
every CER dataset), RG-006 (FIRB records), RG-005 (Mamre Road title search), RG-004
(superannuation exposure). ~~RG-009~~ resolved in v1.1.0; its residual is facility-level attribution,
which the CER does not publish in this dataset.

---

## 9. Limitations

1. **Coverage is much improved but still partial.** 91 site records — including the complete NSW data
   centre SSD register — against a national count that is itself
   contested (162 per AEMO, 285 per the Guardian/ABS framing, 90 in NSW alone per the March 2026
   ministerial release, ~60 in NSW once multi-stage double counting is removed per the August 2026
   Guidelines, and 46 NSW SSD records of which 24 are already determined). The database is a verified
   skeleton with an explicit backlog, not a complete census; publishing it as complete would be the exact
   sin the project exists to criticise. Coverage outside NSW is still thin: Victoria, Queensland, WA, the
   ACT, SA and the NT are represented by directory-level records, not harvested registers (RG-003).
   Capacity figures exist for only a minority of sites, and the portal's development descriptions often
   state a single stage rather than the campus total — the Glendenning 202.4 MW vs 235 MW consent
   discrepancy is the clearest example. Modification applications are enumerated but not yet ingested
   (RG-034), and they are where generator and fuel-storage capacity actually changes.
2. **Operational capacity is mostly undisclosed.** Enclave-level sites are recorded with HCF band
   (20–100 MW) rather than figures. Only 8 of 41 sites carry any MW value.
3. **Verification is corporate-level, not facility-level.** As of v1.1.0, emissions and certificate
   data are reconciled to published *controlling corporations*, because that is the granularity the
   CER publishes in these datasets. Emissions cannot yet be attributed to individual sites, so a
   claim about one campus (e.g. Mamre Road) cannot be audited against measured data — only against
   its own EIS. Absence of Microsoft, Google and Meta from every CER dataset is a threshold-or-
   naming result, not a finding of zero emissions.
4. **Two conflicts are recorded, not resolved:** ISPT vs IFM ownership of the Mamre Road site, and
   Victoria's pipeline value (>$25bn per DJSIR vs $51.9bn per the Clean Energy Council).
5. **Recency risk.** This is a fast-moving regulatory space; four material instruments landed on
   5 August 2026 alone. Re-run the source checks before any publication after October 2026.
6. **Social-source dependence.** South Morang and the WA 1 GW site still rest on grade-C sources and are
   marked CLAIMED/low. They are leads, not findings. Melton has been upgraded to REPORTED/medium now that
   the Guardian identifies Syncline Energy, resolved on the ABR to Syncline Energy Pty Ltd (ABN 26 117 458
   803, active since 7 December 2005, VIC 3000).
7. **One deliberate false positive is retained.** "Dicker Data Warehouse and Distribution Centre"
   (Sutherland Shire) is almost certainly a logistics facility for an IT reseller that the keyword search
   caught. It is kept in the register with a warning note rather than silently dropped, because a harvest
   that hides its own false positives cannot be audited.**v1.7.0 change — two more gaps closed from primary consents.** RG-038: four signed consents spanning
2020–2026 show the **200-hour generator condition is a Department standard**, not a regulatory gap, and that
**installed back-up generation exceeds the facility's entire load in every case** (Glendenning 267.45 MW against
a 235 MW cap; Davis Road 181.92 MW against 160.85 MW). Only one of the four applicants is an operating
company; the others are two consultancies and a trust trustee. RG-046: the Guidelines bind applicants to *their
own EIS commitments*, so they cannot reach s.4.55 modifications — the framework has **no ratchet**. Two key
documents are access-restricted, including an **ASIC certificate for Amazon Corporate Services Pty Ltd** filed
on the Davis Road application, which reopens RG-023. See §5.


