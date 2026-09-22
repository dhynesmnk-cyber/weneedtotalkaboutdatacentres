# The Palantir–NVIDIA thread: defence-AI, sovereign infrastructure and the Australian footprint

**Opened 2026-09-21 · pack `data/packs/palantir_nvidia_thread.json` · 36 sources, 51 rows, gaps RG-086…RG-094 · curation script `scripts/curate_palantir_nvidia.py`**

This thread tracks one question the observatory did not previously ask: **when the hardware
layer of AI (NVIDIA) and the decision layer of AI (Palantir) merge into a single stack sold to
governments as "sovereign", what does that stack physically, financially and legally land on in
Australia?** It spans Pillars A–D: sites and capacity (the NVIDIA DSX buildout), capital and
control (contracts, the Future Fund holding, corporate customers), the regulatory framework
(IRAP, the DTA panel, the PM's AI standards, AUKUS revolving-door rules) and community impact
(political interventions, the facial-recognition landscape).

Everything below is either a sourced row in the pack or an explicitly-labelled reading. Where
the originating brief's premises did not survive verification, §1 says so first.

---

## 1. Premise checks (read before using this thread)

The thread originated from an external project brief whose framing traces to a December 2025
GNCA Investigates YouTube video ("We're All So F'd | NVIDIA x Palantir, Global Surveillance,
'Pre-Crime' Arrests, & AI", recorded as `SRC_GNCA_VIDEO`, grade C, provenance only). Five
premises were checked against primary sources before any row was written. Following the
findings_memo §1 practice, the corrections are recorded, not applied silently.

| # | Premise in the brief | Verdict | What the sources actually support |
|---|---|---|---|
| 1 | "Gotham (law enforcement)" | **Repositioned** | Palantir's own platform page: Gotham is "The Operating System for Global Decision Making … for operators across roles and all domains" — defence/intelligence positioning. Documented law-enforcement use is real but American and specific: New Orleans predictive policing with "threat scores" (ACLU, 2018), ICE's ICM backbone and ELITE targeting app (ACLU/404 Media/The Intercept, 2025-26). No Australian police deployment found (RG-093). |
| 2 | "'Pre-crime' arrest capabilities" | **Not a product claim** | Characterisation from the video. Nearest VERIFIED Australian fact: the WA Police real-time facial-recognition trial (from 2 Jul 2026) produced a live arrest during its launch press conference — 130,000+ faces scanned, 33 alerts, 19 arrests in week one. That system has **no named vendor and no evidenced Palantir connection**. The two must never be merged in a row. |
| 3 | "Apollo (cloud infrastructure)" | **Repositioned** | Officially "The Operating System for Continuous Delivery — from the back of a humvee to the hull of a submarine." It is the mechanism that lets the same Palantir software run anywhere (cloud, on-prem, classified, edge) — which is *why* the data-residency question (RG-087) must be answered per deployment, not per platform. |
| 4 | Huang would "accelerate everything that Palantir does" | **Verified in longer form** | The circulating phrase is the GNCA description's paraphrase. Contemporaneous transcript (Sherwood News, GTC Washington DC, 28 Oct 2025): *"We work with Palantir to accelerate everything Palantir does so that we can do data processing at a much much larger scale and more speed — … and process that data for our government, for national security, and for enterprises around the world."* The full sentence is more explicit about government/national-security purpose than the paraphrase. Keynote-recording verification: RG-092. |
| 5 | "A significant shift toward AI-as-weapon systems" | **Interpretation — facts recorded, label not** | The pack records the primary-sourced facts an editorial layer may weigh: Maven designated a US **program of record** for weapons-targeting AI (Deputy SecDef letter, 9 Mar 2026, via Reuters); the **UK government's own release** describing Palantir work on the "kill chain" and "faster options for attacking an enemy target", capabilities "proven on the battlefield in Ukraine" (gov.uk, 18 Sep 2025); the UN Special Rapporteur's "reasonable grounds" finding that Palantir provided automated predictive-policing technology for battlefield targeting to the Israeli military (A/HRC/59/23, via Al Jazeera). Palantir's position — humans select and approve targets — is recorded alongside (Reuters). "AI-as-weapon" is a characterisation; the database carries claims, not labels. |

Two further discrepancies found **between sources** are recorded as open items rather than
resolved by preference:

- **The ASD clearance date.** Crikey (17 Feb 2026) states ASD granted Palantir "a top security
  clearance" in **November 2024**. Palantir's own primary announcement of IRAP PROTECTED is
  **20 November 2025**, and an IRAP assessment is not a security clearance. Both claims are in
  the pack as sourced; neither is recorded as fact. RG-089.
- **The $7.15m contract's owner.** AusTender notice CN4104368 lists CASG Commercial Group as
  the contracting branch; Crikey attributes the deal to the Cyber Warfare Division. The notice
  is primary and the discrepancy is written into the row's verification note.

---

## 2. The partnership: three phases, one stack

| Phase | Date | Primary source | What it is |
|---|---|---|---|
| 1. Operational AI | 28 Oct 2025, GTC Washington DC | NVIDIA newsroom; Palantir blog | NVIDIA accelerated computing, CUDA-X and Nemotron open models integrated into the Palantir **Ontology** at the core of AIP; Blackwell coming to AIP; "Enterprises will be able to run AIP in **NVIDIA AI factories**"; AIP supported in the **NVIDIA AI Factory for Government** reference design announced the same day (FedRAMP/high-assurance environments, partners incl. Lockheed's Astris AI, Northrop, CrowdStrike). Lowe's first commercial pilot. |
| 2. Sovereign engine | 29 Jun 2026 | Palantir investor release | Engine for running Nemotron open models in **sovereign environments** — "classified, air-gapped, and other sensitive" — for US government agencies and critical infrastructure. Agencies can "change the weights of the models themselves"; telemetry-driven post-training means "customers will own self-improving models specific to their mission". Delivered via the joint **Sovereign AI Operating System Reference Architecture** (palantir.com/sovereignaios). |
| 3. Sovereign supply chain | 10 Sep 2026 | NVIDIA newsroom | NVIDIA runs Palantir Foundry/AIP + post-trained Nemotron **on its own supply chain** ("from wafer to first token"; 1.3m parts per Vera Rubin rack), on SAIOS, deployable on-prem (Dell, Cisco) or colo/cloud (Rackspace, Nebius). The reference customer is now the vendor itself — the stack is exportable to any organisation that wants supply-chain AI "on infrastructure you control". |

The through-line for Australia: the product being sold in phases 2–3 is **sovereignty as an
architecture** — open weights + your data centre + your flag. That is the same word the
Australian government uses (below), which is why the thread belongs in this observatory.

## 3. Australia I: NVIDIA's 2 GW lands on the site register

On **9 September 2026** NVIDIA announced it is collaborating with **Firmus, Sharon AI, IREN,
ResetData, Megaport (via Latitude.sh), CDC, NEXTDC and AirTrunk** to expand land, power and
shell capacity for multiple generations of NVIDIA **DSX AI factories** — "up to a
**2-gigawatt buildout by 2027**" (all figures company claims inside the release; recorded as
CLAIMED metrics, never summed with consent-based capacity):

- **Sharon AI**: up to 68,000 NVIDIA GPUs; framing explicitly invokes "security or sovereignty"
  and "gigawatt-scale AI factories for Australian enterprises, researchers, **government**".
- **IREN**: DSX blueprint applied to its **800 MW Bundey campus, South Australia** — a site the
  observatory's registers do not yet contain (RG-091).
- **CDC**: ">550 MW operating across AU/NZ, 800 MW under construction", zero-water cooling
  "certified for NVIDIA accelerated computing infrastructure" — to be reconciled against the
  observatory's consent-based CDC rows, not merged with them.
- **NEXTDC**: "AI factories built on NVIDIA DSX"; **AirTrunk**: direct-to-chip liquid-cooled
  powered shells; **ResetData**: selling "Australian data residency" to government customers;
  **Firmus**: Project Southgate.
- Named Nemotron users: **Heidi** (health) and **Atlassian**.

Eight weeks earlier, on **15 July 2026**, the Prime Minister announced mandatory **"Australian
Standards for AI"** — one national framework for where large AI data centres are built and the
power and water they use; a legal obligation on next-generation facilities to underwrite new
generation, pay full grid-connection costs and be **net generators** ("put at least as much
energy into our grid as they take out"); legislation planned for early 2027. The speech frames
the stakes in exactly the partnership's vocabulary: refuse to be "a data warehouse for AI
products made overseas"; do not "subcontract our sovereignty and security to the control of
foreign monopolies"; AI is "a critical — and urgent — innovation priority for our defence force
and security agencies".

**The mapping question (RG-091):** the Oct 2025 release says customers can "run AIP in NVIDIA
AI factories"; NVIDIA is now building AI factories in Australia with eight partners, three of
which (NEXTDC, AirTrunk, CDC) are already in the observatory's 93-site register. Whether any
Australian DSX factory will host Palantir workloads — government or commercial — is the open
circuit between the two halves of this thread. No source answers it yet; that is a gap, not a
negative.

## 4. Australia II: the Palantir footprint, verified

**The Australian entity.** Palantir Technologies Australia Pty Ltd, **ABN 48 144 948 309**,
Canberra ACT 2601 — named as supplier on every AusTender notice in the ledger except ASD's,
which names the **US parent** ("PALANTIR TECHNOLOGIES INC.", Denver; ABN "Exempt").

**The Commonwealth contract ledger** (every notice read in full; all VERIFIED rows):

| CN | Agency | Title | Value (AUD) | Period | Method | Notes |
|---|---|---|---|---|---|---|
| CN3992202 | **ASD** | Software Licencing | $696,981.39 | 2023-07-01 → 2024-06-30 | Limited tender — *select Defence intelligence agencies* exemption | Supplier = **US parent**. The most sensitive buyer, the least documented contract. |
| CN3996124 | **ACIC** | Software Maintenance & Support | $1,402,122.87 (orig. $3,630,000, **reduced** by A1 amendment, unexplained on the notice) | 2023-06-01 → 2025-03-31 | Open tender via DTA panel SON3490955 | What the national criminal-intelligence body runs on it is undisclosed (RG-093). |
| CN4104368 | **Defence** (CASG) | Data Services | $7,150,000.00 | 2024-08-16 → 2027-12-13 | Open tender (AIC/RFP/38833/1) | Crikey: FOI emails show it is the **Foundry** platform. Longest-running current contract. |
| CN4115523 | **Defence** (JCG Cyber Warfare Division) | Software | $4,135,076.99 | 2024-12-11 → 2025-06-30 (ext. to 2025-12-10) | Open tender via SON3490955 | The "existing supplier" foothold for the next row. |
| CN4218984 (+A1) | **Defence** (JCG Cyber Warfare Division) | ICT System Platform | $7,639,894.90 → **$10,389,894.90** | 2026-02-06 → 2027-02-01 | **Limited tender**, condition 10.3.e, one supplier invited | Amendment **+36%** eight weeks after execution (2 Apr 2026). Defence's largest Palantir contract (Crikey). |

Catalogued Defence subtotal: **$18.9m** at original values ($21.7m counting the amendment).
Crikey's AusTender analysis puts **total Defence spend since 2013 at more than $26m** — so a
tail of older notices is not yet in the ledger. The complete ledger across all Commonwealth and
state governments is **RG-086** (priority 5); the DTA **Software and ERP Marketplace panel
(SON3490955)** matters because its Category 2 is open to Commonwealth, state, territory **and
local government** buyers — the procurement channel exists for every level of government
without a fresh approach to market.

**Data residency — what is known and what is not.** Palantir's IRAP PROTECTED announcement
(20 Nov 2025, primary) states that **Palantir Platform Australia (PPA)** delivers Foundry and
AIP "**hosted in Australian Amazon Web Services (AWS) regions**". That is the company's own
answer to the brief's storage question — for PPA. It does not establish that the Defence Cyber
Warfare Division platform, the ASD licence (contracted with the US parent) or the ACIC
deployment run on PPA, in those regions, or onshore at all; Apollo exists precisely so the same
software can run anywhere. Per-deployment residency, mapped against the observatory's site
register (starting with `SITE_AWS_AU_FLEET`), is **RG-087** (priority 5, FOI route).

**Sovereign capital.** The **Future Fund** — the Commonwealth's sovereign wealth fund — held
**620,169 Palantir shares worth A$165,307,100** (0.06% of the fund) at 31 Dec 2025, read
directly from the archived Periodic Investment Report CSV (`data/raw/futurefund/`, SHA-256
manifest). Trajectory: A$1.6m (Feb 2023) → A$103.6m/498,339 shares (Jun 2025, Crikey citing the
FF report) → A$165.3m (Dec 2025, primary). Crikey notes the stake is **larger than the fund's
holdings in AGL, Seek or NEXTDC** — sovereign capital holding more of the defence-AI vendor than
of an Australian data-centre operator that is simultaneously an NVIDIA DSX partner. Other
Commonwealth funds and CSC: **RG-094**.

**Corporate customers** (the brief's "which Australian companies" question): **Rio Tinto**
(verified — four-year Foundry/AIP extension, Nov 2024; the Ontology coordinates **53 driverless
iron-ore trains across the Pilbara** from the RTIO Operations Centre in WA); **Coles** (reported
— Palantir analytics across supermarkets since 2024; workforce management against 24,000
process standards "measured to 15-minute increments"); **Westpac** (single weak source — a
LinkedIn post via Crikey; no entity row created until corroborated, RG-088).

**The revolving door, in writing.** The UK's Advisory Committee on Business Appointments —
a government ethics regulator — published its advice on **Damian Parmenter CBE**, the UK's
former **Director General for AUKUS** (2023 → 1 Feb 2025), joining **Palantir Technologies UK
as "Senior Counsellor"** (July 2025) with a remit including "international opportunities within
Europe and the **Indo-Pacific**". ACOBA's letter (primary, read in full) found he "would have
amassed a network of contacts while in office **especially in the US and Australia** by virtue
of his role at AUKUS … a risk these contacts … may be seen to offer new business development
opportunities for Palantir", and imposed two-year lobbying bars. The Australian mirror: ABC Four
Corners (Aug 2026) records **Mike Kelly, a former defence materiel minister, as Palantir's
Australian president 2020–2024** — across the period the ledger's contracts were awarded —
inside a population of **60+ former defence insiders** now in weapons firms or lobbying, around
a program lobbyists describe as "$368 billion" (Pyne) and "a multi-billion-dollar feast"
(Shoebridge). Whether Palantir or NVIDIA hold any actual AUKUS Pillar II work is **not
evidenced** — asserting it would fabricate the link; **RG-090** tests it.

**Political record.** Senator Shoebridge (Greens) called for a **freeze on government contracts
with Palantir** (Jul 2025); Senator Pocock called the Feb 2026 limited tender "terrible
procurement process … land and expand" (Feb 2026); the contract was amended upward by $2.75m
seven weeks later. Both recorded as `political_intervention` rows with outcomes.

## 5. The global defence-AI record (context rows, not Australian facts)

- **Project Maven**: began 2017 as drone-imagery labelling; Google employees protested ("The
  Business of War", NYT, Apr 2018) and Google declined to renew; Palantir became a follow-on
  integrator. Maven Smart System IDIQ: **US$480m** (May 2024) → ceiling **US$1.3bn** (May 2025)
  → designated an official **program of record** by Deputy SecDef letter of 9 Mar 2026 —
  "locks in long-term use of Palantir's weapons-targeting technology across the U.S. military"
  (Reuters). Reuters also reports Maven is already "the primary AI operating system" of the US
  military and was used across thousands of strikes on Iran in early March 2026; Palantir's
  position (humans approve targets) is recorded in the same row.
- **US Army enterprise agreement**: up to **US$10bn** over 10 years, consolidating 75 contracts
  (army.mil, 31 Jul 2025).
- **UK MoD strategic partnership** (gov.uk, 18 Sep 2025, signed by the Defence Secretary):
  Palantir investment pledge up to **£1.5bn**, London as European defence HQ, MoD opportunities
  "worth up to **£750m** over five years", explicit **kill-chain**/Digital Targeting Web
  language, capabilities "proven on the battlefield in Ukraine", and a promise that "data
  remains sovereign". A Five Eyes government's own primary description of what the partnership
  pattern buys — and the contrast case for what Australia has published about its own Palantir
  use: nothing beyond contract titles.
- **UN Special Rapporteur report A/HRC/59/23** (Jun 2025, via Al Jazeera): Palantir among 48
  named corporate actors; "reasonable grounds" to believe it provided automated
  predictive-policing technology used for battlefield automated decision-making and target-list
  generation for the Israeli military ("Lavender", "Gospel", "Where's Daddy?"). BlackRock
  (8.6%) and Vanguard (9.1%) recorded as largest institutional investors.
- **US domestic surveillance** (ACLU, Mar 2026, with 404 Media/The Intercept underpinnings):
  ELITE deportation-targeting maps with "address confidence scores" drawing on HHS/USCIS/
  Thomson Reuters CLEAR data; ICM as ICE's case backbone; the 2018 New Orleans "threat score"
  predictive-policing lineage; Amnesty International's call to cease the work.

## 6. The Australian surveillance landscape (deliberately separate)

The verified Australian facial-recognition facts involve **no Palantir system on any evidence
found**, and the pack keeps it that way:

- **WA Police**: Australia's first law-enforcement **real-time** FRT trial (mobile van, Perth,
  from 2 Jul 2026): ~4,000-person watchlist (warrants, registered child sex offenders, missing
  persons); week one 130,000+ faces / 33 alerts / **19 arrests** / two acknowledged false
  alerts; live arrest during the launch press conference. The state privacy regulator (OIC WA)
  was **not consulted** and warns of "collective privacy harms". Commissioner: "not about mass
  surveillance … less intrusive than a standard CCTV camera". Vendor **undisclosed** (RG-093).
- **NSW Police**: ran a **2011-vintage Cognitec** algorithm inside PhotoTrac SIS until early
  2025 without ever contracting support or updates, alongside NYX adapted in-house from
  Google's FaceNet (Biometric Update, grade C, attributed claims).
- **Attitudes**: 45% of Australians now rate facial recognition their biggest privacy risk
  (2026 OAIC survey, up from 27% in 2023).

## 7. Gaps opened (the honest part of the ledger)

| RG | Pillar | Prio | Question (abridged) | Route |
|---|---|---|---|---|
| 086 | B | 5 | Complete Palantir contract ledger: all Commonwealth notices back to 2013, all state portals, SON3490955 panel membership and every call-off | dataset_download + FOI |
| 087 | C | 5 | Where Australian data sits per deployment (entity, platform, region, on-prem/offshore); map hosting facilities to the site register | foi_request |
| 088 | B | 4 | Corporate customer register: verify Westpac; find others via disclosures/AIPCon/ASX | manual_review |
| 089 | C | 3 | Resolve the ASD clearance discrepancy (Crikey "Nov 2024 top clearance" vs IRAP PROTECTED "Nov 2025"); what regime, what scope | foi_request |
| 090 | C | 4 | Palantir/NVIDIA position in AUKUS Pillar II; Parmenter's Indo-Pacific activity; post-separation conditions for Kelly (or their absence) | manual_review |
| 091 | A | 4 | Map the DSX buildout to sites: Bundey (SA), Project Southgate, NEXTDC/AirTrunk/CDC claims vs consents; will any host Palantir workloads | scrape_portal |
| 092 | C | 2 | Verify the Huang quote against the keynote recording (t≈5114s); archive transcript | manual_review |
| 093 | D | 4 | Any Australian law-enforcement Palantir use? ACIC platform purpose; WA FRT vendor; NSW RTIC tooling | foi_request |
| 094 | B | 3 | Public-fund exposure beyond the Future Fund: June-2025 PIR primary check; MRFF/CSC/state funds' PLTR and NVDA holdings | dataset_download |

## 8. Method, grading and archive

- 36 sources: 13 primary government (AusTender ×7, ACOBA, gov.uk, army.mil, pm.gov.au, Future
  Fund PIR), 6 primary company (NVIDIA newsroom ×3, NVIDIA blog, Palantir IR ×2, Palantir
  platforms/blog), 10 news/investigation (Reuters, ABC, Guardian, Crikey ×4, Sherwood, NYT,
  Al Jazeera, DefenseScoop, Biometric Update, iTnews, International Mining), 2 advocacy
  (ACLU, GNCA video as provenance). Grading per `sources.credibility`: A for primary read in
  full; B for credible secondary and trade press; C for Biometric Update and the GNCA video.
- Search-abstract-only readings are marked as such in the source notes (army.mil, DefenseScoop,
  NYT 2018, Al Jazeera's underlying OHCHR document was **not** read — the record rests on Al
  Jazeera's summary and says so).
- **Raw archive**: `data/raw/futurefund/futurefund_pir_2025-12-31.csv` with SHA-256 manifest
  (the only primary file downloaded for this thread; the ACOBA PDF and all web pages were read
  in session and cited by URL).
- Every row carries `fact_status` / `confidence` / `as_of_date` / `source_id`. Company claims
  inside partner announcements (2 GW, 68k GPUs, CDC's 550/800 MW) are **CLAIMED**, never
  merged with consent-based capacity, and the metrics notes say never to sum them.
- Amendment notice CN4218984-A1 is stored with `is_duplicate_of` its parent so no total
  double-counts the same contract — the same auditability pattern the consultancy layer uses
  for aggregator duplicates.
- **No site rows were created from the NVIDIA release.** Partner marketing figures do not
  populate the site register; RG-091 is the reconciliation route, and the `live_capacity` rule
  applies unchanged.

## 9. What this thread deliberately does not say

- It does not say Palantir runs predictive policing, facial recognition or "pre-crime" tooling
  in Australia. No primary source places any Palantir system in an Australian police force;
  the verified Australian FRT systems have other or undisclosed vendors.
- It does not say the NVIDIA–Palantir partnership has an Australian defence deployment. The
  Australian record is: five Commonwealth contract notices, one platform-hosting statement
  (PPA on AWS AU regions), one IRAP assessment, and an ethics letter about a UK official's
  move. Everything beyond that is RG-086…RG-094.
- It does not treat "sovereign AI" as sovereignty. The pack records who says the word, about
  what, in which primary document — the PM's speech, NVIDIA's release, Palantir's IRAP
  announcement, Sharon AI's quote — and leaves the distance between the word and the
  per-deployment facts (RG-087) visible.
