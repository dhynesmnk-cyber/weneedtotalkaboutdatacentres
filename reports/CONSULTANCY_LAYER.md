# The Consultancy Layer

## Tata Consultancy Services, the advisory chain, and who actually writes a data centre consent

**Australian Data Centre Observatory — v2.1.0**
Prepared 18 September 2026 · Schema migration `02_consultants.sql` · Packs `consultants-layer-2026-09`, `rg079-determinations-2026-09`

---

## 0. Read this first: what happened to the numbers you supplied

You supplied a detailed breakdown of TCS's Australian public sector contracts totalling
**AUD $352.7 million across 65 engagements**. Almost all of it checks out. Two things do not, and
one of them matters a great deal.

### The provenance is a commercial aggregator, not a portal

Every figure you supplied — the $352.7M, the 65 engagements, the 79% buyer concentration, the
per-agency subtotals, the individual contract values and dates — matches, number for number, the
supplier page at **govmarket.com.au**. That is a subscription product ($49.99/month) which scrapes
AusTender and the state portals and then *"categorises, enriches"* the results, publishing summaries
it labels **"AI summary · inferred from awarded contracts."**

That is not a criticism of you. It is a criticism of how these numbers circulate. GovMarket is a
legitimate and useful tool. But it is a **secondary** source, and the Observatory's rule is that
secondary sources enter as `REPORTED` at credibility C, never `VERIFIED`. Every row loaded from it
is graded that way.

### The headline number is inflated by $118,312,700

This is the material finding, and it is provable from primary documents.

The **$118.3M "Transport Equipment Centre of Excellence"** appears **twice** in the 65-contract
portfolio:

| # | Title as listed | Dated | Value | Source portal |
|---|---|---|---|---|
| 1 | CW2307478 – Transport Equip Centre of Excellence | 17 Jul 2025 | $118,312,700.00 | buy.nsw **CAN-100812** |
| 2 | Operation and Maintenance of Transport Equipment Centre of Excellence | 29 Jul 2025 | $118,312,700.00 | AusTender |

These are the **same contract**. Not two similar contracts — the same one. The values are identical
to the cent. And GovMarket's *own* contract-detail page for record #2 says:

> *"Awarded 29 Mar 2018 — 9y 3mo term · 92% elapsed"* … *"Expires Wed, 30 June 2027"*

That is exactly what the primary notice says. The aggregator lists the same underlying contract
once per portal and sums both.

**Corrected figures:**

| | Published | Observatory de-duplicated |
|---|---|---|
| Total portfolio | **$352,735,957.18** | **$234,423,257.18** |
| Distinct engagements | **65** | **64** |
| Transport for NSW | $278.9M / 15 contracts / **79%** | $160,587,300 / 14 contracts / **68.5%** |

The overstatement is **50.5% of the corrected figure**. Half the widely-quoted number is one
contract counted twice.

And 45 of the 65 records are behind the paywall, so **more duplicates cannot be excluded**. $234.4M
is a *ceiling* on distinct spend, not a floor.

> **Why this belongs in a data centre database.** This is the identical failure mode the Observatory
> already documented in the sector itself: the BCA's own commissioned Oxford Economics research shows
> **44 GW** of connection requests resolving to **6 GW** proceeding and **2.8 GW** of actual draw —
> because a gross aggregate gets mistaken for a net commitment. AirTrunk's "100% renewable by 2025"
> claim failed the same way. Aggregates that are not de-duplicated are the recurring defect across
> both layers. Finding it in the consultancy data is not a digression; it is the same finding.

### The biggest contract is not a 2025 award. It is a 2018 sole-source deal that runs nine years.

You described it as *"a massive AUD $118.3 million contract"* from *"July 2025."* The primary notice
says otherwise, and the difference is the whole story:

From **CAN-100812**, read in full ([buy.nsw.gov.au](https://buy.nsw.gov.au/notices/6BD465F8-5DCF-4433-A0495C518C94EE38)):

```
Agency                     Transport for NSW
Description                Transport Equip Centre of Excellence - Maintain and Operate Services
Method of tendering        DIRECT NEGOTIATION
Estimated amount inc GST   $118,312,700.00
Effective date             29-MAR-2018
Contract end date          30-JUN-2027
Publish date               17-JUL-2025
Supplier                   TATA Consultancy Services LTd, ABN 28109981777
                           76 Berry Street North Sydney NSW 2060
```

**July 2025 is when the *notice* was published. The contract began 29 March 2018.** Term: **9 years
3 months**, 92% elapsed. Obtained by **direct negotiation** — no competitive tender.

The notice is equally clear about what it does *not* contain:

- Variation provisions: *"Not applicable"*
- Renegotiation provisions: *"Not applicable"*
- Other private sector entities benefiting: *"Not applicable"*
- Heightened modern slavery due diligence: *"No"*
- Agency piggyback clause: *"No"*
- Amendments: *"No amendments have been made to this disclosure"* — in nine years

**One directly-negotiated contract, unchanged and unamended for nine years, accounts for 50.5% of
this firm's entire tracked Australian public-sector exposure.** The aggregator's own detail page
notes it is *"larger than 98% of TATA Consultancy's contracts · ~531× their median win"* — implying a
median win of about **$222,811**.

This is a far better story than "a new $118M outsourcing deal," and it is defensible. Trade press
corroborates the duration: in June 2018 TCS *"won a $76.7 million, three-year software maintenance
and support deal with Transport for NSW … replac[ing] Deloitte"* for this same Centre. The function
has been outsourced continuously since at least 2018.

**And it expires 30 June 2027** — a live recompete inside this project's horizon. Your proposed
remedies (open API mandates, infrastructure-as-code delivery, state-owned deployment pipelines) are
the right remedies for lock-in, and lock-in is precisely what a 9.25-year direct negotiation
produces. They should be aimed at that expiry, which is when they can bite.

### Two smaller corrections

- **RBA CoreMod**: you dated it July 2025; the aggregator dates publication **30 July 2025**. Value
  $14.0M confirmed. AusTender record of primary not yet read (RG-072).
- **"Office 365 Environment Setup for MoG GSS" ($189k)**: attributed to *NSW* Department of Customer
  Service. "MoG GSS" denotes a **Machinery-of-Government** change to Government Shared Services, and
  the award pattern is consistent with a **Commonwealth** publication. Carried at **low confidence**
  pending resolution. If a widely-used aggregator misattributes the *buyer*, then every derived claim
  about which government funds what is unsafe — that is RG-083.

### What you got exactly right

Verified or consistent with the aggregator, and worth stating plainly:

- ✅ $5.3M across **27** Melbourne Water contracts — confirmed, and it *is* the highest contract count
  of any buyer (avg ~$196k)
- ✅ Individual Melbourne Water values: DR Infra Build Phase 2 **$289k**, Citrix Upgrade **$209k**,
  GIS Consultant T&M **$197k**, Cyber Security PM **$140k**, M365 OneDrive/SharePoint L2 **$192k**,
  SolarWinds Phase 2 **$157k** — all confirmed to the dollar
- ✅ Three OneStream awards on **consecutive days** (17, 18, 19 Dec 2024) totalling **$1,735,000** —
  your "roughly $1.7 million" was right
- ✅ Azure EiPaaS **$829k** (Aug 2024), SAP Fiori **$570k** (Jul 2024), RBA Cloud Build **$2M**,
  Defence benchmarking **$1.1M**, PM&C ICT **$135k**, NSWEC software licensing **$239k**
- ✅ icare **$8.5M** across 2 contracts
- ✅ The two expiring contracts flagged for recompete (RBA Cloud Build ~2mo, NSWEC licensing ~4mo)

---

## 1. Why TCS belongs in a data centre observatory at all

Three facts, each verified, that do not appear together anywhere in the public debate.

### (a) It is a member of the Business Council of Australia

TCS appears on the BCA membership list (as at April 2025), corroborated by a TCS-hosted post: *"TCS
is a member of Business Council of Australia and Australia-India CEO Forum."*

The BCA is the body whose board includes **Robin Khuda, founder and CEO of AirTrunk**, alongside the
CEOs of Telstra, Commonwealth Bank, Wesfarmers, Google Australia/NZ and BHP Australia. It is the body
that made **Submission No 116** to the NSW Legislative Council inquiry into data centres on 2 April
2026, which asserted that *"datacentre operators in Australia pay full taxes with no concessions"*
and asked government to *"recalibrate … community narratives."*

**Accenture is on the same membership list.** So at least two global systems integrators sit inside
the peak body that submitted to the data centre inquiry.

### (b) TPG — its data centre joint-venture partner — is *also* a BCA member

The BCA list includes **TPG Capital**. TPG is investing up to **Rs 8,820 crore** in TCS's HyperVault
for a **27.5–49%** stake.

Investor and investee are both members of the same Australian peak body. This is the *same structural
pattern* the Observatory already records for **Blackstone/CPP Investments and AirTrunk**: private
capital and its portfolio company inside one room, in a body that submits to parliamentary inquiries
about the sector they are building.

### (c) From 20 November 2025, TCS is a data centre *operator*

Per TCS's own press release ([tcs.com](https://www.tcs.com/who-we-are/newsroom/press-release/tcs-secures-1bn-investment-from-tpg-accelerate-ai-data-center-business-hypervault)):

> *"HyperVault aims to establish AI data centers with capacity in excess of a GW"* … *"purpose-built,
> liquid-cooled data centers with high rack densities"* … *"will deliver secure, reliable, large-scale
> AI-ready infrastructure for hyperscalers and AI-driven organizations."*

- Combined commitment up to **Rs 18,000 crore** (~US$2.1bn); TCS retains majority (51%)
- TPG participates via **TPG Rise Climate** and its Global South Initiative (with ALTÉRRA), plus TPG
  Asia Real Estate
- Jim Coulter (Executive Chairman, TPG): data centers are *"a multifaceted asset class"* at *"the
  intersection of green energy infrastructure, technology and real estate"*
- Advisers: TCS by AZB & Partners and **Deloitte** Touche Tohmatsu India; TPG by Cyril Amarchand
  Mangaldas, **Latham & Watkins** and **PwC** — four of the six being firms that also appear in
  Australian public procurement
- Subject to conditions precedent and statutory approvals

**Australia is not mentioned anywhere in the release.** Chandrasekaran is quoted on building
*"GW-scale AI data centers in India."* The Asset reports proceeds support the *"GW-scale AI data
centre build in India."* This is recorded as a **documented negative** (RG-076), not an assumption —
and it should be rechecked on any HyperVault announcement.

**So the position is this.** A firm that is politically represented in the room where Australian data
centre policy is negotiated, is paid at least $234.4M by the agencies affected by that policy
(including PM&C, which houses the Office of AI), and is now a hyperscale data centre developer — is a
**structural conflict of position**. Nothing here alleges misconduct, and none is implied. But the
BCA's "no concessions" submission was made by a body whose membership includes a data centre
operator, a data centre developer, the hyperscalers, *and* their suppliers. The inquiry received one
submission from it.

### A second access channel

**Jodi McKay** — former NSW Leader of the Opposition and Cabinet Minister — is
**Australia's Senior Trade and Investment Commissioner for South Asia** at Austrade, based in Mumbai
(confirmed on Austrade's own site). She is also **Director of the Australia-India CEO Forum**, of
which **TCS is a member**, and TCS **co-chairs** the Forum's Australia India Women's Leadership Forum.

A firm holding Commonwealth and NSW IT contracts is a member of, and co-chairs a programme of, a
bilateral forum directed by a serving Commonwealth trade commissioner, in a role she holds after
leading the opposition in the state where most of those contracts sit. Entirely lawful, entirely
normal in trade promotion. Recorded because the Senate inquiry's terms of reference cover *"deals
between Government and global AI companies,"* and because this project's method is to map access
rather than assume its absence. (RG-077)

---

## 2. The finding that matters more: consultancies are the named applicants on NSW data centre consents

While verifying the TCS data I parsed the **Schedule 1 "Applicant"** field from all 20 signed NSW
data centre consents already archived in this project. 13 parsed cleanly.

| Named Applicant | Type | Project | Case ID |
|---|---|---|---|
| **ARUP Pty Ltd** | engineering consultancy | 43-61 Turner Road | SSD-68013714 |
| **Cundall Johnston and Partners Pty Ltd** | engineering consultancy | Davis Road | SSD-59416728 |
| **Cundall Johnston and Partners Pty Ltd** | engineering consultancy | Davis Road Mod 1 | — |
| **Lehr Consultants International (Australia) Pty Ltd** | planning/acoustics consultancy | Glendenning Road | SSD-73761707 |
| EMKC Cubed Management Pty Ltd | opaque SPV | 51 Huntingwood Drive | SSD-41589232 |
| EMKC Cubed Management Pty Ltd | opaque SPV | Apollo Place | SSD-67407231 |
| HDI SYD1 Property Holdings Limited | per-site SPV | DigiCo SYD1 Expansion | SSD-69637456 |
| The Trustee for NineZero DC Sub Trust I | trust trustee | DCI Poplars | — |
| NEXTDC Limited | operator | NEXTDC S4 Horsley Park | — |
| Goodman Property Services (Aust) Pty Ltd | developer | Project Apollo Macquarie Park | — |
| Canberra Data Centres Pty Ltd | operator | Roberts Road | SSD-10330 |
| Macquarie Data Centres Pty Ltd | operator | Talavera Road Campus | — |
| Equinix Hyperscale 2 (SY10) Pty Ltd | operator SPV | Grand Avenue Rosehill | — |

**In 4 of 13 consents the named applicant is a consultancy. In 4 more it is an opaque vehicle. Only 6
of 13 name an identifiable operator.** So in 8 of 13 parsed consents — a clear majority — the party
legally named on the instrument is not the party that will run the facility.

### The most consequential instance

**Glendenning Road, SSD-73761707** — the Observatory's benchmark post-Guidelines consent, and the
single most-read instrument in this database. It carries:

- all-times additional firmed renewable matching
- NOx cap under 10 t/yr excluding outages
- 45 metre stacks
- a **170 hour** generator cap — the first departure from the Department's 200 hour template
- **267.45 MW** of installed back-up against a **235 MW** load cap

Its Schedule 1 names **Lehr Consultants International (Australia) Pty Ltd** — a planning, engineering
and acoustics consultancy — as the Applicant. **A member of the public reading that consent cannot
tell who will operate the 235 MW facility near them.**

This is not a data-entry quirk and not an allegation. Agents lodge on behalf of principals all the
time. But the consent is the *enduring public legal record*, and it is the document that runs with
the land. Where it names an agent, the beneficial operator is absent from the only permanent record.

**The fix is one line.** Require the consent to name both the applicant (who may be an agent) *and*
the intended operator and ultimate parent, updated on any change of control. The Schedule 1 field
already exists; it is simply populated with the agent. The Guidelines already include a
website-disclosure measure, and one consent in the sample already carries a website disclosure
condition — so the machinery is partly present. This single change would resolve **RG-022, RG-023,
RG-064, RG-065 and RG-081** at a stroke, at no implementation cost. It is the highest-value
transparency reform available in this layer.

**And neither parliamentary inquiry asks for it.** The Senate TOR covers "deals between Government and
global AI companies"; the NSW TOR covers lobbying and donations. Neither covers the identity of the
consent holder. That is a gap in the terms of reference themselves, and it can still be put to both
committees — NSW reports **3 November 2026**, the Senate **16 November 2026**.

### Who wrote the evidence?

A filename-level pass over the **6,866 archived attachments** found named firms in only ~16
filenames — so this is a **floor**, not a census (RG-073 exists to open the documents):

| Firm | Evidence found | Project |
|---|---|---|
| **Arup** | CFD modelling advice (+ 2 variants, + Dec 2025 RFI response) | 1-5 Khartoum Road |
| **Arup** | 7 numbered technical notes (`appendix-c7-arup-technical-note-206..212`) | Apollo Place |
| **Aurecon** | *plant and equipment systems report* | Mamre Road campus (321 attachments) |
| **Renzo Tonin** | acoustic query response | Talavera Road Mod 1 |
| **Cundall** | technical advice (`bcs-advice-davis-road…`) | Davis Road — *the same project where Cundall is the named applicant* |
| **WSP** | one letter | Dicker data warehouse |

Two things stand out.

**The Aurecon appendix is the one that matters.** A "plant and equipment systems report" is where
cooling plant and back-up generation get specified — the exact two things the NSW Guidelines of
17 August 2026 now regulate hardest through dPUE/dWUE bands, recycled-water requirements and
generator hour caps. It sits on the largest campus in the register.

**Independent peer review exists, and is rare.** Across 63 projects there are **181 acoustic and noise
attachments** and exactly **three** identifiable independent peer reviews (~5%):

- `a14-acoustic-peer-review` — DigiCo SYD1 expansion
- `peer-review-acoustic-assessment` — Lane Cove West Mod 3 (which carries *three* separate acoustic assessments)
- `appendix-b4-acoustic-review-statement` ×2 — 51 Huntingwood Drive Mod 1 (the modification that *reduced* the scale of the 632 MW-back-up facility)

The reviewing firms are not named in any filename (RG-075). Acoustic evidence is the basis for the
amenity conditions that decide whether a data centre can run its generators at night next to houses.
Independent checking of it is the exception, not the norm.

The filenames also show the regulator dialogue directly: `a3-acoustic-response-dphi-scoping-report-comments`
(×6, Kemps Creek) and `acoustic-logic-rfi-response-epa-comments` (Stack SYD01). Consultants respond
to DPHI SEARS scoping and to EPA comments — **that is the mechanism by which the technical evidence
base for a consent is actually set.**

---

## 3. Bonus finding: who decided, and under what authority

Parsing the delegation recitals from the same 20 consents produced something unexpected.

Every consent opens: *"As delegate of the Minister for Planning and Public Spaces under delegation
executed on [date], I approve…"*

| Delegation executed | Consents | Note |
|---|---|---|
| 11 October 2017 | 2 | Dicker Data (2019-04-12), Lane Cove West (2019-11-15) — both signed Anthea Sargeant |
| 9 March 2020 | 1 | Roberts Road, decided 14 Jul 2020 |
| 26 April 2021 | 1 | Macquarie Park, decided 28 May 2021 — signed Chris Ritchie |
| 9 March 2022 | **12** | the standing regime 2022→2026, including Project Pluto, decided 23 Jul 2026 |
| 14 June 2022 (IPC) | 1 | Project Echidna — delegate of the **NSW Independent Planning Commission**, not the Minister |
| **18 August 2026** | **2** | **Glendenning Road; Project Apollo Macquarie Park** |
| *(none — IPC determination)* | 1 | Talavera Road: published with **'[Name of Commissioner]' signature placeholders** (RG-085) |

*(v2.1.0: the six formerly unparsed recitals — RG-065 — are resolved by the pypdf re-extraction; all
twenty instruments now parse, and every row above is verified from the archived cover pages.)*

**The NSW Data Centre Guidelines were published 17 August 2026. A fresh ministerial delegation was
executed the following day.** The two consents issued under it are the first two post-Guidelines
decisions in the sample:

- **Glendenning Road** — signed **14 September 2026** by **Joanna Bakopanos, A/Director, Industry
  Assessments**, file EF 24/10658
- **Project Apollo Macquarie Park** — signed **2 September 2026**, Bakopanos acting

(Note: the database elsewhere records Glendenning as determined 16 September 2026. The instrument is
signed **14 September**; the Notice of Decision confirms "**Date of decision 14 September 2026**", and
the portal's `field_date_of_determination_mp` records 16 September — the registration date. Both are
recorded rather than reconciled by assumption.)

**Project Pluto is the control case** — decided 23 July 2026, i.e. *also* mid-2026, but under the
**2022** delegation and therefore before the Guidelines and before the fresh delegation.

### Officer concentration

The portal publishes the case officer on all 63 project records. These are NSW assessment officers,
not consultants:

| Officer | Cases | Share |
|---|---|---|
| Shaun Williams | 25 | **40%** |
| Patrick Copas | 16 | **25%** |
| Jeffrey Peng | 7 | 11% |
| Dave Auster | 5 | 8% |
| Catriona Shirley | 3 | 5% |
| Joanna Bakopanos | 2 | 3% |
| 5 others | 1 each | 10% |

**Two officers handle 65% of the NSW data centre pipeline.** Eleven named individuals decide the
shape of the state's data centre build-out. This is disclosed accountability, not a leak — the
portal publishes it.

**(v2.1.0) Mapped onto the 20 determined consents, the concentration is starker: Williams 9, Copas 6
— 75% of everything the state has actually decided — and the two post-Guidelines determinations are
theirs (Glendenning = Williams, Project Apollo = Copas). Joanna Bakopanos appears on both sides of
the record: case planner for Talavera Road in the portal's own assignments, and signatory of 9 of the
20 instruments as A/Director Industry Assessments.**

### The honest caveat — resolved in v2.1.0 (RG-079)

Across the 20-consent condition battery, Williams' 9 consents and Copas' 6 were originally compared
without dates: **`determination_date` was EMPTY on all 20 rows**, so officer variation could not be
separated from the time-and-proponent effect, and the report refused to claim one. *(The earlier
draft of this section also called Grand Avenue's renewable condition "the only renewable PPA
additionality requirement in the whole sample" — the pypdf re-extraction recovered renewable
provisions in five consents; that claim was an extraction artefact and is retracted.)*

The dates are now populated on all 20 rows — 18 from the instruments' own cover-page execution lines,
2 from portal node metadata where the date is an image stamp — and the test was run
(`scripts/curate_rg079.py`; register at `exports/nsw_planning/nsw_dc_consent_determinations.csv`).
**Finding: no officer effect is detectable, and the evidence says stringency is template-dominated.**
The 200-hour generator cap appears in 14 of the 17 consents carrying any cap; website disclosure in
19 of 20; the Guidelines in 0 of 20. On a documented strictness index, Williams' portfolio (n=9,
mean 6.56, range 2–14) and Copas' (n=6, mean 4.50, range 1–11) overlap completely, within-officer
variation exceeds between-officer variation, and the index is era-confounded — scores rise steeply
with determination date because PUE/WUE/renewable/recycled-water provisions only became standard in
instruments from late 2024. The documented departures from template (NEXTDC S4's 5.5 t/yr NOx cap
including testing; Glendenning's 170 hours and 10 t/yr; Pluto 173; Apollo 187) are attributed by the
record to proponent EIS commitments and site-specific assessment — not to the case officer. The
structural finding stands: one office manages and signs the pipeline, under a delegation executed one
day after the Guidelines took effect. n=20 with two post-Guidelines observations cannot support
statistical inference; internal condition-setting records are reachable only via the RG-007 FOI route.

---

## 4. Your strategy critique, tested

The brief asked for unworkable ideas to be dismantled. Three critiques were supplied. All three are
recorded in `engineering_claims` with their status. Summary:

### "The $118m Centre of Excellence masks a standard outsourcing agreement" → `FACTUALLY_WRONG_PREMISE`

**Right instinct, wrong premise, and the truth is worse.** It is not a 2025 award — it is a
**29 March 2018 direct negotiation** running **9 years 3 months**, and the notice records *no*
variation, renegotiation or amendment provisions in that time. Nor is "Centre of Excellence" vendor
marketing: it is the **agency's own** contract title, in use since at least 2018.

The defensible findings are: (1) one directly negotiated contract has run 9.25 years and is **50.5%**
of the firm's tracked Australian public spend; (2) the notice records no amendment across that term;
(3) it **expires 30 June 2027** and is a live recompete.

**Also: this contract has nothing to do with data centres.** It covers transport equipment — fleet
telemetry, signalling, plant. Its relevance to this Observatory is as a *pattern*, not as sector
spend. Presenting it as data centre expenditure would be wrong.

Your remedies are sound and should be attached to the 2027 expiry.

### "Melbourne Water's 27 micro-contracts are a gross misuse of taxpayer funds" → `PARTLY_SOUND`

**The counts are right; the characterisation is not.** 27 low-value awards to one pre-qualified
supplier is the normal operation of a **panel or standing-offer arrangement**, not 27 procurement
failures. Consolidated panels exist precisely so nobody runs a full tender for a $105k hardware swap.

The real issue is **category, not fragmentation**. The visible scopes are Citrix upgrades, SolarWinds
support, M365 L2 infrastructure support, EOL hardware, GIS on T&M, cyber PM, network zone refinement,
DR infrastructure build. That is run-the-business work and staff augmentation bought through a
consulting panel — a legitimate cost question.

**Drop "gross misuse of taxpayer funds."** It is not evidenced and it discredits the rest. Also: only
**one** visible engagement is explicitly time-and-materials (the $197k GIS contract), so *"paying
premium day rates"* is **not substantiated** by the visible records and should not be asserted. The
onshore/offshore split — the variable that would actually determine whether a rate is "premium" — is
disclosed on no notice.

**And "automate the maintenance away" / "self-healing cloud infrastructure" are not remedies for a
procurement-category problem.** You cannot automate away a Citrix upgrade decision.

*The genuinely interesting Melbourne Water angle is different:* it is a **water authority** — and the
NSW Guidelines now require **100% recycled water** for water-intensive cooling, while the BCA's
Submission No 116 claims recycled water already supplies **55%** of AirTrunk's total water use
(**unverified**, RG-068). Whether any of the 18 paywalled TCS engagements touch recycled-water supply
planning is RG-080, and would matter far more than the procurement-style point.

### "Commodity work disguised as strategic projects" → `PARTLY_SOUND`

**True as to the scopes.** But they were published under *accurate* titles — "Defect Fix Services",
"Office 365 Environment Setup". Nothing was disguised.

The stronger version of your argument survives, and it is this: **a $1.1M award titled "DEFECT FIX
SERVICES" means delivery quality is being paid for twice** — once to build, once to fix. That is
specific and damning. The counter-argument the brief omits: MoG transitions are genuinely
time-critical and genuinely exceed internal capacity by design, because a machinery-of-government
change moves functions on a fixed political date. Buying surge capacity for that is defensible.
Paying $1.1M to fix defects in a system already paid for is not.

Your proposal to embed senior architects in delivery teams is sound practice, but it is an **agency
capability** question, not a procurement rule — and it costs money the brief does not account for.

**Replace it with two testable requirements:** (1) defect-remediation contracts above a threshold must
disclose whether the defect arose under a prior contract with the same supplier, and whether that
contract carried acceptance criteria and warranty; (2) every award notice must name its **portal of
record**, so aggregation cannot misattribute the buyer — which is exactly what happened to the O365
contract.

---

## 5. What was built

### Schema migration `02_consultants.sql` — 4 tables, 6 views

| Table | Rows | Purpose |
|---|---|---|
| `consultancy_profile` | 8 | firm type, role in pipeline, peak-body membership, operator status, exposure + **exposure source tier** |
| `gov_contracts` | 23 | one row per distinct contract, with **`is_duplicate_of`** self-reference |
| `consultant_role` | 22 | separates **named applicant** from **technical author** from **peer reviewer** |
| `case_handling` | 71 | case planners, delegate signatories, **delegation dates**, decision dates |

Views: `v_consultant_public_money`, `v_consultant_spend_totals` (de-duplicated), `v_case_officer_load`,
`v_applicant_vs_proponent`, `v_consultant_influence`, and **`v_contract_reconciliation`** — which
exists specifically so the enumerated rows ($142.0M across 22) can never be confused with the full
portfolio ($234.4M across 64).

### The `is_duplicate_of` design decision

The duplicate could have been deleted. It was **retained as a row with `is_duplicate_of` set**, so the
inflation is *auditable* rather than silently corrected. A reader can see both the published gross and
the de-duplicated figure and verify the arithmetic themselves:

```
$ python3 scripts/query.py reconcile
firm                             enumerated_records  enumerated_distinct  published_portfolio_aud  deduplicated_portfolio_aud
Tata Consultancy Services Limited                 23                   22           352,735,957.18              234,423,257.18
```

### Database state

**1,241 data rows (+ 376 source references) · 30 tables · 16 views · 117 sources (70 primary) · 125 entities · 325 metrics · 79 research gaps (13 resolved)**

*(v2.1.0 counting basis: data rows exclude `source_refs`, which are counted separately; the v2.0.0
header figure of 1,465 used a different basis. Final post-load figures are now regenerated by
`scripts/finalize_docs.py` — see defect #4 below.)*

(The new layer contributes 89 `VERIFIED` and 35 `REPORTED` rows and no `CLAIMED` rows: nothing was
loaded on assertion alone. Every aggregator-sourced figure is `REPORTED` at credibility C.)

New query presets: `consultants`, `contracts`, `spend`, `reconcile`, `duplicates`, `applicants`,
`officers`, `influence2`.

### Two loader defects found and fixed while building this

Both are the kind of thing that silently corrupts a verification database, so they are worth naming.

1. **`engineering_claims` was unloadable from any pack.** The base schema gives that table
   `source_ids` (plural — it is designed to cite *multiple* sources), but the loader unconditionally
   demanded `source_id`. Added `SOURCE_COL_OVERRIDE` so multi-source rows validate every cited id.

2. **Re-running any pack silently duplicated rows.** Tables with an autoincrement PK and no unique
   key (`lobbying`, `metrics`, `research_gaps`, `consultant_role`, `engineering_claims`) are
   append-only. Reloading a pack doubled them — I measured it: 1,566 → 1,639 rows including the ingest log. Fixed three ways:
   composite-key upserts discovered at runtime (`composite_unique_targets`, NULL-safe); an exact-row
   duplicate probe that skips identical rows; and a `--force-append` flag with a loud error if you
   really mean to append. **Verified: reloading the pack twice now adds zero rows.** The skip count is
   written to `ingest_log` as `skipped_identical`.

Also: `build_db.py` now applies **all** `schema/*.sql` in filename order, so migrations survive a
rebuild, and `PROVENANCE_EXEMPT` allows pure mapping tables (`entity_aliases`, which had never been
populated) to load without fake provenance.

### A third defect: an orphaned pack, and three metrics that never existed

Checking whether the new pack was wired into the pipeline surfaced a consistency check worth running
on any project like this: **does every pack on disk appear in both `rebuild_all.py` and the `Makefile`?**

It found `data/packs/rg060_consent_conditions.json` — 8 curated metrics, wired into **neither**
pipeline. It had been silently doing nothing. Cross-referencing against the database:

- 5 of its metrics were independently regenerated by the wired `rg060_consent_matrix.json` pack
- **3 were genuinely absent from the database**: `consents_analysed_reliably` (18),
  `consents_extraction_limited` (2), and `consents_with_generator_hours_cap` (14)

The third is not a duplicate of the existing `consents_with_200_hour_generator_cap` (11) — the
**3-consent gap between them is exactly where site-specific departures from the Department's 200-hour
template live**, including Glendenning's 170 hours. And the first two supply the **denominator** for
every `consents_with_*` metric in the pack: those "0 of 18" negative findings are only safe to rely on
because 18 of 20 extractions cleared the reliability floor. Without them, the battery metrics had no
stated base.

Fixed by moving the three into `scripts/curate_rg060.py`, **computed from source** rather than
hardcoded, and retiring the orphan to `data/packs/retired/` with a README explaining the lesson.
Verified after rebuild: 18, 2 and 14 — matching the orphan's values exactly. `EXAMPLE_pack.json` is
the only remaining unwired file, and it is a template.

*(v2.1.0: the pypdf re-extraction moved these values — **20 reliable, 0 extraction-limited, 17
generator-hours caps (14 at the 200-hour template)** — and RG-065 resolved with all 20 applicants
parsing. The orphan's `--pack` emission path now writes to `data/packs/retired/` so a re-run can
never again create an unwired pack in the live directory.)*

### A fourth and fifth defect (v2.1.0): seed-stage documentation, and driver drift

4. **`viewer/db.json` and `reports/build_report.md` were seed-stage snapshots.** `build_db.py`
   writes both while it builds — *before any pack loads*. The offline viewer therefore showed 41
   metrics and zero `case_handling` rows against a database holding 325 and 83, and the build report
   claimed 326 rows and 60 sources against 1,241 rows and 117 sources. Anyone using the viewer or
   quoting the report was reading a database that no longer existed. Fixed by
   `scripts/finalize_docs.py`, which runs **last** in both drivers and regenerates both artifacts
   from the loaded database, including the full research-gap register (build_db only ever listed the
   seed gaps) and integrity spot-checks.

5. **Driver drift — the class of bug #3 belongs to — is now a build failure.** `curate_consultants.py`
   was present in `rebuild_all.py` but missing from the Makefile's verify target; pack order was
   duplicated by hand in two places. `scripts/check_packs.py` now runs first in both drivers and
   fails the build if any pack in `data/packs/` is wired into only one driver, if any
   `scripts/curate_*.py` is not run by both, if a listed pack is missing from disk, or if the two
   drivers' load orders diverge. As part of this, the consultancy-layer gap ids (72–83) were made
   **explicit** — they had been autoincrement-assigned, and cross-pack `match/set` updates address
   gaps by id, so the numbering must survive a from-scratch rebuild.

---

## 6. Research gaps opened: RG-072 → RG-083

| ID | P | Pri | Question |
|---|---|---|---|
| **RG-073** | A | **1** | Which consultancy authored each technical appendix? (filename pass done — 16 of 6,866; documents must be opened) |
| **RG-074** | C | **1** | Does any consultancy authoring evidence for proponents **also hold contracts with DPHI/IPC** or the agencies writing the Guidelines? |
| **RG-076** | A | **1** | Does TCS/HyperVault have any **Australian** data centre footprint? (documented negative as at today) |
| **RG-079** | C | **1** | ~~Does condition stringency vary by officer once date is controlled?~~ **RESOLVED v2.1.0 — dates populated on all 20; no officer effect detectable at n=20; conditions are template-dominated (see §3)** |
| **RG-081** | C | **1** | Beneficial ownership of EMKC Cubed, HDI SYD1, NineZero DC Sub Trust I (extends RG-064) |
| RG-072 | B | 2 | Full 65-record TCS list from portals of record; find every duplicate |
| RG-075 | C | 2 | Do peer reviews ever review the same firm's work? Who performs them? |
| RG-078 | B | 2 | **Who commissioned and paid for the Oxford Economics phantom-demand research?** |
| RG-080 | D | 2 | Do TCS/Melbourne Water engagements touch recycled-water supply planning? (pairs with RG-068) |
| RG-077 | C | 3 | McKay concurrent roles: registers and ministerial diaries (pairs with RG-070) |
| RG-083 | B | 3 | Resolve agency attribution and portal of record for O365 MoG and the OneStream trio |
| RG-082 | C | 4 | Schema hygiene: add `'consultancy'` to the `entity_type` enum; retype ARUP/LEHR/CUNDALL |

**RG-074 is the central question of this layer** and it is unanswered: if the same firms write both
the proponent's evidence and the regulator's guidance, the assessment is not independent in substance
even where it is procedurally correct. Note the timing — the Guidelines were published 17 August
2026, a fresh ministerial delegation was executed **the next day**, and both post-Guidelines consents
in the sample were issued under it. Whoever advised on the Guidelines had immediate effect on two
decisions.

**(v2.1.0) RG-074 advanced to `in_progress`.** All 20 Schedule 1 applicants now parse (RG-065
resolved): **seven consents are held by consultancies or an architectural practice** — ARUP Pty Ltd
(Turner Road) and ARUP Australia Pty Ltd (Echidna), two distinct legal entities; Cundall Johnston and
Partners (Davis Road consent *and* Mod 1); Lehr Consultants (Glendenning Road *and* Station Road);
Greenbox Architecture (Lane Cove West). Cross-referenced against the tracked `gov_contracts`
population: **none of these firms appears** — but that population is TCS-weighted, so the absence is
a scoping limit, not an answer. The remaining work is an agency-side pull: DPHI, IPC and
Planning-portfolio contracts from AusTender and buy.nsw, searched **by agency** and matched against
these firms and the RG-073 appendix authors. Two further gaps opened from the determination layer:
**RG-084** (are the two Stockland Macquarie Park site records one project or two?) and **RG-085**
(who decided Talavera Road? the published IPC instrument carries '[Name of Commissioner]'
placeholders).

**RG-078** is the most valuable single item in the influence layer. The 44 GW → 6 GW → 2.8 GW finding
is the most important number in the demand debate and it is **industry-commissioned**. It cuts
*against* the sector's interest in a large headline pipeline, so it should be credited — but the
Observatory records it as commissioned research without knowing who paid. The NSW Guidelines cite
Oxford Economics work prepared **for AEMO**, which may be a different engagement. Whether they are the
same study matters.

---

## 7. Sources

| ID | Source | Tier | Credibility |
|---|---|---|---|
| `SRC_BUYNsw_CAN100812` | buy.nsw Contract Award Notice CAN-100812 | primary_government | **A** |
| `SRC_TCS_HYPERVAULT` | TCS press release, 20 Nov 2025 | primary_company | **A** |
| `SRC_AUSTRADE_MCKAY` | Austrade commissioner profile | primary_government | **A** |
| `SRC_CONSENT_APPLICANTS` | Schedule 1 parse, 20 signed consents | primary_planning_portal | **A** |
| `SRC_CONSENT_DELEGATIONS` | Delegation recitals, 20 signed consents | primary_planning_portal | **A** |
| `SRC_PORTAL_PLANNERS` | 63 portal node records (`field_party_role`) | primary_planning_portal | **A** |
| `SRC_ATTACHMENT_CONSULTANTS` | 6,866-attachment filename index | derived from primary | B |
| `SRC_GOVMARKET_TCS` | GovMarket supplier portfolio page | market_research | **C** |
| `SRC_GOVMARKET_TECOE` | GovMarket contract detail page | market_research | **C** |
| `SRC_WIKI_BCA_MEMBERS` | Wikipedia BCA membership list | other | **C** |

No figure sourced from a C-tier source is recorded as `VERIFIED` anywhere in this layer, with **one
deliberate and documented exception**: `gov_contracts` row 2, the duplicate listing. Its `source_id`
is the aggregator page, because *that is where the second listing was observed*, and its
`fact_status` is `VERIFIED` because the **duplication** was proven by comparison against primary
notice CAN-100812 — identical value to the cent, identical award date, identical expiry. What is
verified there is the duplication, not a new fact about spend. The row carries that explanation in
its own `verification_note`.

Row 1 — the same contract, read in the primary notice — cites `SRC_BUYNsw_CAN100812` at credibility A.
An earlier draft of this pack defaulted it to the C-tier aggregator; that was caught by a
self-consistency check (`C-tier source used as VERIFIED`) and corrected.

---

## 8. The one-paragraph version

The $352.7M figure you found is real arithmetic on real data, but it double-counts a single $118.3M
contract, so the defensible number is **$234.4M across 64 engagements** — and that contract is not a
2025 outsourcing deal but a **nine-year directly-negotiated sole-source arrangement from March 2018
that expires in June 2027**, which is a much better story. TCS matters to this project not because of
its contract total but because it is simultaneously a **BCA member** (alongside AirTrunk, the
hyperscalers, and its own JV partner TPG), a **$234.4M recipient of Australian public money**, and
from November 2025 a **hyperscale data centre developer** through HyperVault. The more consequential
discovery was made while verifying it: in 8 of the 13 parsed NSW data centre consents — a clear majority —, the party
named on the instrument is a **consultancy or an opaque SPV rather than the operator** — including the
235 MW Glendenning consent, the most important document in this database, which names an acoustics
firm. Both post-Guidelines consents were signed under a ministerial delegation executed **one day
after** the Guidelines were published. Two officers handle **65%** of the state's data centre
pipeline. And of 181 acoustic attachments across 63 projects, only **three** carry an identifiable
independent peer review.
