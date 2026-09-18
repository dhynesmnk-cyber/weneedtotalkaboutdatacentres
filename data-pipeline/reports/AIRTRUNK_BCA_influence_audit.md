# AirTrunk and the Business Council of Australia — an influence audit

**Release:** v1.9.0 · **Prepared:** 18 September 2026 · **Companion to:** `findings_memo.md`
**New in this release:** a `lobbying` table and `v_influence` view (10 records), 7 new sources, 6 new gaps

---

## 1. What was asked, and the short answer

The question was: how much lobbying power does the Business Council of Australia have, given that its
membership includes Telstra, the banks, BHP — and, since 2025, AirTrunk?

**Short answer: a great deal, and the AirTrunk seat is more consequential than it first appears — but
not for the reason it looks like.**

Three things make it consequential:

1. **AirTrunk is not just a member. Its founder and CEO Robin Khuda sits on the BCA Board**, appointed
   27 June 2025 alongside Telstra CEO Vicki Brady. The board is nine seats: Telstra, Commonwealth
   Bank, Wesfarmers, Google Australia & NZ, BHP Australia, Gilbert + Tobin, AirTrunk, plus the BCA's
   President and Chief Executive.
2. **All four hyperscalers are BCA members** — Amazon, Apple, Google and AirTrunk all appear in the
   published membership. That matters because this project has established that **none of AWS, Google
   or Meta appears in any of the 46 NSW data centre planning records** harvested. Their policy
   representation in Australia runs through the BCA, not through planning portals. Influence and
   physical footprint are in different places.
3. **The BCA lodged Submission No 116 to the NSW data centres inquiry**, and it is the most complete
   articulation of the sector's position available anywhere in the public record. It is also, in its
   silences, the most revealing document in this project.

What it is **not**: evidence of anything improper. Board seats for member chief executives are how
the BCA is constituted. Everything below is disclosed, public and lawful. The value of recording it
is that a database which tracks who owns the land, who holds the consent and what the emissions are,
but not who is in the room when the framework is written, is describing only half the system.

---

## 2. Who is in the room

**Board (as published on bca.com.au, read 18 September 2026):**

| Seat | Person | Role |
|---|---|---|
| President | Geoff Culbert | BCA President |
| Chief Executive | Bran Black | BCA CEO |
| Director | **Vicki Brady** | CEO & Managing Director, **Telstra** |
| Director | **Matt Comyn** | CEO, **Commonwealth Bank of Australia** |
| Director | Danny Gilbert AM | Chairman, Gilbert + Tobin |
| Director | **Robin Khuda** | Founder & CEO, **AirTrunk** |
| Director | **Rob Scott** | Managing Director, **Wesfarmers** |
| Director | **Mel Silva** | Managing Director & VP, **Google Australia and New Zealand** |
| Director | **Geraldine Slattery** | President Australia, **BHP** |

**Executive:** Wendy Black (Executive Director Policy — gave evidence to the NSW inquiry on 29 May
2026), Ben Wicks (Executive Director Public Affairs and Advocacy), Pero Stojanovski (Chief
Economist), Natalie Stirling (Executive Director Strategy, Membership and Engagement), Ian Anderson
(Executive Director Finance and Operations, Company Secretary).

**Scale:** the BCA states it represents "more than 120 chief executives" and describes itself as
representing "Australia's largest employers". Published membership logos include Accenture, AGL
Energy, **AirTrunk**, Allens, **Amazon**, Amcor, Ampol, **ANZ**, APA Group, **Apple**, Ashurst
Perkins Coie, ATCO, Atlassian and the Australian Securities Exchange, among others.

**Timing.** AirTrunk's membership logo is served from a `2025/05` asset path and the board
announcement is dated 27 June 2025 — i.e. **six months after Blackstone completed its A$24bn
acquisition on 23 December 2024**, ten months before the NSW Data Centre Consultation Paper (March
2026), and fourteen months before the NSW Data Centre Guidelines (17 August 2026). The asset path is
a weak date signal and is graded `REPORTED/medium`; the board appointment is `VERIFIED/high` from
AirTrunk's own announcement.

**The asymmetry worth naming.** Per AFR reporting of 27 November 2025, the BCA "counts AirTrunk but
not NextDC among its membership." So the **Blackstone-controlled** operator holds a board seat at
Australia's principal business peak body, while the **ASX-listed Australian** operator does not
belong to it. NEXTDC is the proponent of the OpenAI-anchored 612 MW S7 campus. Whatever explains
that — fee levels, corporate preference, timing — it means the peak body's data centre voice is not
the listed domestic one.

---

## 3. AirTrunk's position in this database

Everything below is already in the database and sourced. It is collected here because the influence
question only means something next to the substantive record.

**Ownership.** Blackstone-led consortium (Blackstone Real Estate Partners, Infrastructure Partners,
Tactical Opportunities, and its individual-investor PE strategy) **88%**, **CPP Investments 12%**,
enterprise value above **A$24bn**, completed **23 December 2024** after a FIRB-reviewed process.
Vendors were Macquarie Asset Management and PSP Investments. Largest data centre transaction
globally and largest Australian transaction of 2024. **FIRB conditions are not published** (RG-006).

**Sites.** Three HCF Certified Strategic facilities: SYD1 Huntingwood, SYD2 Lane Cove, MEL1
Derrimut. SYD3 recorded as a gap. Reported prospective buyer of the **Mamre Road Data Centre
Campus** — 1 to 1.2 GW at Kemps Creek, 52 ha, six four-storey buildings, **728 cooling units, 846
diesel back-up generators, >18,000 kL diesel storage**, ~22.4 ML water/yr, ~500 construction and
~500 operational jobs. The named proponent there is **KNBDC SYD4 Pty Ltd**, whose ABR-resolved trust
stack was incorporated between 3 April and 19 June 2025 in North Sydney and whose **beneficial owner
is not publicly disclosed anywhere** — a web search for "KNBDC" returns zero results (RG-029/RG-036).
**A MEL2 campus in Melbourne's north-west was announced in December 2025** and is not yet mapped
(RG-071).

**Emissions, from Clean Energy Regulator primary data.** AirTrunk Australia Holding Pty Ltd:

| | 2019-20 | 2020-21 | 2021-22 | 2022-23 | 2023-24 | 2024-25 | Δ |
|---|---|---|---|---|---|---|---|
| Scope 1 (t CO₂-e) | 132 | 328 | 918 | 2,352 | 1,826 | **4,165** | +3,055% |
| Scope 2, location-based (t) | 94,528 | 157,174 | 257,423 | 348,562 | 450,207 | **553,344** | +485% |
| Net energy (GJ) | 397,923 | 660,303 | 1,106,671 | 1,643,984 | 2,275,838 | **2,886,668** | +625% |

AirTrunk **does not appear** in the CER's market-based scope 2 table in either published year
(2023-24 or 2024-25), and holds **no account** in the REC Registry LGC holdings snapshot of
31 July 2026. Its "100% renewable energy by 2025" claim is recorded as **`CONTRADICTED`** as a
statement about Australian operations — not because the contracts don't exist, but because the claim
has no expression in statutory data.

**Regulatory position at Mamre Road.** The NSW EPA advised on **10 April 2026** that the EIS "does
not provide the information required to allow us to complete our assessment", requesting more on air
quality, noise, greenhouse gas emissions and waste storage. **Penrith City Council objected**,
calling the site "not suitable for a proposed development of this scale". Mamre Anglican School,
directly across the road, raised air quality, noise and fire risk and has identified an alternative
site while seeking government help to relocate. The Catholic Diocese of Parramatta objected outright.

---

## 4. Submission No 116, read closely

Received **2 April 2026**. 1,120,166 bytes, 59,431 characters extracted at **54.4 chars/KB** — above
this project's reliability floor, so absences below are meaningful. One caveat, stated because it
conditions every negative: my extractor drops `ff`/`ffi` ligatures, so I repaired the text before
testing and re-ran every absence check. "Offset" was a false absence until repaired.

### 4.1 The four recommendations

1. "Recognise data centres as a strategic economic opportunity for NSW and **recalibrate policy
   settings, regulatory approaches and community narratives** to enable and attract investment at
   scale."
2. Align the NSW approach with the Commonwealth Expectations "to create a national and consistent
   approach so Australia can compete for investment and streamline national data centre operations."
3. "Give the new Investment Delivery Authority the ability to **rapidly assess and recommend public
   infrastructure investments that support major private sector projects**."
4. Monitor planning reforms "focusing on efficiency, consistency, and certainty in the planning
   system."

Two observations. **Recommendation 1 asks government to recalibrate "community narratives"** — a
request to change public discourse, not an environmental standard. The submission is candid about
why: "the public debate can sometimes reduce them to symbols of trivial internet content", and
"better, more reliable information about the benefits and impacts of data centres will help dispel
some prevalent myths about them." **Recommendation 3 asks for public infrastructure investment to be
directed at private projects** — which is state directed facilitation, and is precisely what terms of
reference (g)(iii) asked the committee to examine.

The submission also states: "The BCA has consistently called for a reduction in regulatory burden,
and **we do not support introducing additional regulation where it is unnecessary**."

### 4.2 What is absent

Verified by keyword search after ligature repair. These words appear **nowhere** in 59,431
characters:

`subsid*` · `payroll` · `land tax` · `diesel` · `generator` · `back-up` · `NOx` · `nitrogen` ·
`noise` · `air quality` · `200 hours` · `community benefit` · `local content`

Set that against what the committee was asked to inquire into:

| Term of reference | Corresponding word absent from the submission |
|---|---|
| (c)(ii) "the role of on-site backup generation, **including diesel and gas, and associated emissions and health impacts**" | diesel, generator, back-up, NOx, nitrogen, air quality, 200 hours |
| (e)(i) "impacts on surrounding communities, **including noise, air quality and heat**, traffic…" | noise, air quality |
| (g)(iii) "the extent of **public subsidies, concessions or state directed facilitation** provided to the sector" | subsid* |

None of the four recommendations proposes an environmental, emissions, water, noise,
community-benefit, local-content or domestic-compute measure.

**This is an argument, not an accusation.** A peak body is entitled to scope its submission to the
questions it considers material and to argue that its sector is misunderstood. The observation worth
recording is narrower and more useful: the inquiry's own terms of reference identify diesel
generation, noise, air quality and subsidies as matters for examination, and the sector's most
powerful representative addressed none of them in writing, while addressing water at length and
devoting two case studies to human benefit.

### 4.3 What it does say, with numbers

**On tax — the sector answers the subsidy question directly, in one sentence:**
> "Not only do datacentre operators in Australia **pay full taxes with no concessions**, they form
> the infrastructure that allows Australian companies, workers and communities to participate fully
> in the digital economy."

And in §3.7, naming its members: "Companies such as **AirTrunk, Telstra, AWS, Microsoft, Google, and
Goodman** who build and operate facilities across the country. These companies employ thousands of
Australians, pay local taxes and reinvest heavily in new infrastructure." **AirTrunk is listed
first.**

**On phantom demand — the most deflating number in the entire debate, and it is industry-funded:**
> "In 2025 the Australian Energy Market Operator (AEMO) received around **44 gigawatts** of
> connection requests linked to data centre proposals. Only about **six gigawatts** of project
> capacity is expected to proceed, with only **2.8 gigawatts** of actual electricity draw once those
> facilities reach maturity — **15 times lower than what is sometimes reported**."
> — citing Oxford Economics, *Surging Data Centre Connection Requests Drive Phantom Demand*,
> 21 November 2025

**This deserves credit and should be quoted by critics too.** It cuts against the sector's interest
in a large headline pipeline, and it is consistent with everything else in the record: the NSW
Guidelines' 6-in-7 phantom finding, utilities' 20% proceeds-likelihood, Transgrid's evidence that
against 10 GW of enquiries and 6 GW of formal applications **no data centre had committed** as at
22 May 2026, and the NSW IDA's refusal to endorse **$40.7bn** of proposals as "premature or overly
speculative". The practical consequence for this database: **no pipeline figure may be reported as
demand.** On the industry's own commissioned numbers, realised national draw is about **2.8 GW**.

The limit of that argument also needs stating, because it will be over-claimed: phantom demand is a
reason to discount aggregate forecasts, **not** a reason to relax site-level conditions. A facility
that is built still sits 100 m from houses at Marsden Park and 350 m from houses at Lane Cove, still
installs 267.45 MW of diesel generation against a 235 MW load, and still draws the water it draws.

**On water — and this is the source of the number the inquiry heard orally:**
> "Across Australia, data centres consume around **5.5 gigalitres** of water each year, which
> represents approximately **0.04 per cent** of national potable water use. In Sydney, data centres
> account for about **0.7 per cent** of total water consumption… industry projections indicate that
> data centre water use is expected to remain **below two per cent** of total potable water supply
> through to 2030."

That 0.04% is the figure Belinda Dennett of Data Centres Australia gave orally under parliamentary
privilege on 1 May 2026 — so **the two peak bodies used the same numbers to the same inquiry.** They
are separately constituted and separately funded, which is worth knowing before treating the
repetition as independent corroboration.

For scale: the Mamre Road EIS alone claims 22.4 ML/yr, so 5.5 GL is roughly **245 such facilities**.

**On AirTrunk specifically — the most favourable water credential claimed for it anywhere:**
> "For example, **recycled water now supplies 55 per cent of AirTrunk's total use**, and its
> Singapore site runs entirely on reclaimed water." (footnote 23)

**On renewables:**
> "Since 2020, companies such as Amazon, Microsoft and Equinix have contracted close to **one
> gigawatt** of renewable electricity capacity from wind and solar projects in Australia… Across the
> sector, around **70 per cent** of electricity used by data centres is already **offset** by
> renewable energy, through a mix of on-site solar generation and long-term renewable power purchase
> agreements."
>
> "When data centre operators commit to long-term electricity contracts, they **underpin the
> financing of new wind and solar capacity that might otherwise struggle to proceed**."

**On approvals:**
> "In the BCA's 2025 **Regulation Rumble**, the state ranked **last** as at June 2025 for planning
> system performance… The state performs well in planning process transparency, but efficiency,
> consistency, and certainty for proponents lagged behind most other states and territories."

Note the provenance: the ranking is the BCA's **own publication**, offered to a parliamentary inquiry
as evidence about whether that state should regulate a sector less. Not a conflict of interest in any
legal sense — but the arbiter and the interested party are the same organisation.

**Framing.** The submission's persuasive core is two case studies: **"Amy's homework"** (a Year 10
student in Parramatta uploading a maths assignment before the deadline) and **"Margaret's health
monitor"** (a 78-year-old living alone with a heart condition whose wrist monitor alerts her doctor
to a rhythm change). Both are true of some data centre traffic and both are effective. Neither bears
on the marginal emissions, water or amenity impact of a *new hyperscale campus*, which is what the
inquiry was asked about. Recording this is not a criticism of the advocacy — it is the reason a
database should hold the marginal-impact evidence separately from the average-benefit case.

---

## 5. Cross-examination: every industry claim against the primary regulator data

This is the part the database exists for. Claims from Submission No 116 and the oral evidence, tested
against Clean Energy Regulator datasets, signed consents and the planning register.

| Claim | Source | Verdict | Basis |
|---|---|---|---|
| "Operators pay full taxes with no concessions" | BCA Sub 116; DCA orally 1 May 2026 | **UNVERIFIED** | No revenue-office record either way. RG-007 FOI strategy drafted. Note the claim addresses *tax* and is silent on *state directed facilitation*, which is documented and substantial |
| "Data centre operators do not receive subsidies or tax incentives" | DCA, under privilege | **PARTIALLY_VERIFIED** | The tax limb is untested; the cost-allocation limb ("pay 100% connection costs and augmentations") **is** corroborated by Transgrid's published position |
| "Will pay $10.3bn in energy infrastructure to 2030, $1.1bn excess capacity for public use" | DCA, under privilege | **CLAIMED** | Not reconciled to any network business capital plan. RG-043 |
| "~70% of electricity already offset by renewable energy" | BCA Sub 116 | **CONTRADICTED** | CER data: location-based scope 2 **rose** for every hyperscale operator 2019-20→2024-25; only 2 of 8 operators reported market-based scope 2 in 2024-25 and none in 2023-24; NEXTDC's market-based figure is only 3.6% below location-based; **0** data centre operators are LGC-liable entities (0 of 143 shortfall-register entries); **0 of 228** Safeguard covered facilities is a data centre |
| "Operator contracts underpin new wind and solar that might otherwise struggle" | BCA Sub 116 | **CONTRADICTED** | Greenpeace (May 2026) found no operator analysed adequately proved it drives renewable growth — independently reproduced from CER data. NSW Government records that PPAs "largely skew to solar projects, not the new wind, storage and other firming assets needed for grid stability" |
| "Recycled water supplies 55% of AirTrunk's total use" | BCA Sub 116, fn 23 | **UNVERIFIED** | No metered water data for any Australian site; Sydney Water agreements not public. Highest-value verification target in the water pillar. RG-068 |
| "Data centres use ~5.5 GL/yr, 0.04% national, 0.7% Sydney" | BCA Sub 116 | **CLAIMED** | Directly contradicted in framing by Sydney Water's MD, who stood by a 25%-of-Greater-Sydney-by-2035 projection under questioning. The two are probably measuring current use vs a 10-year forward projection from applications received. RG-042 seeks IPART's actual position |
| "25% of Sydney's water by 2035 is not based in fact and was dismissed by IPART as unverifiable" | DCA, under privilege | **CONTRADICTED** | Sydney Water's MD asked directly: "**We do** [stand by it], and we acknowledge the uncertainty." The IPART characterisation is unverified |
| "44 GW of requests → ~6 GW proceeding → 2.8 GW actual draw" | BCA Sub 116, citing Oxford Economics | **REPORTED — and credible** | Consistent with AEMO, Transgrid, NSW utilities and the IDA's $40.7bn of non-endorsed proposals. Adopted into the database as the deflation factor |
| "Data centres in Australia pay for their own connections and any network upgrades, unlike much of the US" | BCA Sub 116 | **VERIFIED** | Transgrid, 26 Aug 2026: costs "borne by the proponents creating that demand rather than existing electricity consumers". Network Capacity Allocation Policy makes capacity conditional on committing to fund augmentation |

**Pattern worth stating plainly.** The claims about **cost allocation** hold up against primary data.
The claims about **environmental performance** do not. That distinction should shape how the
Observatory argues: the sector's "we pay our way" case is well founded and conceding it costs
nothing, while the "we are already green" case fails against the regulator's own numbers.

---

## 6. The influence map, as data

A new `lobbying` table records actor, named person, channel, recipient, date, instrument, position
sought, outcome, whether it was disclosed, and provenance. `python3 scripts/query.py --sql "SELECT *
FROM v_influence"` prints it. Ten records, all disclosed:

| Date | Actor | Channel | Instrument |
|---|---|---|---|
| 2026-07-15 | BCA (Bran Black) | media_campaign | Response to the Commonwealth grid mandate |
| 2026-05-29 | BCA (Wendy Black) | parliamentary_evidence | NSW inquiry public hearing |
| 2026-05-01 | Data Centres Australia (Belinda Dennett) | parliamentary_evidence | NSW inquiry, first witness |
| 2026-04-02 | BCA | peak_body_submission | Submission No 116 |
| 2025-11-21 | BCA | commissioned_research | Oxford Economics, phantom demand |
| 2025-06-27 | **AirTrunk (Robin Khuda)** | **peak_body_board** | **BCA Board appointment** |
| 2025-06-02 | BCA | media_campaign | AI report: "simplify data centre approvals" |
| 2025-06 | BCA | commissioned_research | Regulation Rumble 2025 |
| 2025-05 | AirTrunk | peak_body_membership | BCA membership |
| — | (Roberts Road / CDC) | political_donation | Statutory disclosure, **image-only, unread** |

**The last row is the one that matters most and is the least readable.** A **political donation
disclosure** is filed on SSD-10330 (Roberts Road Data Centre, applicant **Canberra Data Centres Pty
Ltd** — a CDC facility, *not* AirTrunk). It is the only donation document located across the entire
63-project NSW register. It is publicly listed but published **only as a scanned image with no
extractable text**, so the donor, recipient and amount are unknown. The NSW inquiry's terms of
reference (h)(iv) expressly cover "the impact of lobbying and donations on government policy setting
surrounding data centre developments". A statutory disclosure that cannot be searched is a
transparency finding in itself (RG-069).

**The channel that leaves no trace.** The NSW package includes a **DPHI concierge function** and
**pre-assessment proponent support that begins before a site has been selected** (§3 of the
Guidelines). Site selection is where every downstream environmental and community outcome is
determined, and the Guidelines themselves say brownfield sites away from sensitive receivers create
fewer complexities. So the most consequential influence happens in meetings that appear in no
submission and no register unless a lobbyist or ministerial diary disclosure captures them. **No
equivalent capability is funded for councils or community groups.** RG-070 is the register check;
RG-063 asks the resourcing-symmetry question.

---

## 7. What I cannot prove, and what would prove it

Nothing in this report alleges improper conduct. The honest limits:

1. **A board seat is not a lobbying record.** I have no evidence of what Robin Khuda said in any BCA
   board meeting, and board minutes are not public. The finding is about *access and structure*, not
   about any act.
2. **I have not established that the BCA's data centre positions are AirTrunk-driven.** The
   submission is a BCA document; attributing its content to any one member would be speculation.
3. **Donations are unread.** One disclosure exists in the whole register and it is an unsearchable
   image (RG-069).
4. **Lobbyist and ministerial-diary registers have not been checked** (RG-070). That is the obvious
   next evidence layer and it is free.
5. **AirTrunk's 55% recycled water claim is unverified** (RG-068) — and it is the claim most
   favourable to AirTrunk in this report, so verifying it is an obligation, not an option.
6. **KNBDC's ownership is still unknown**, so the link between AirTrunk and the Mamre Road proponent
   remains an inference from a site code and a postcode (RG-029/RG-036/RG-052).
7. **The BCA membership roster is incomplete** — bca.com.au returns a challenge page to non-browser
   clients, so the roster was read from the rendered page rather than enumerated (RG-067).
8. **96 of 116 Senate submissions are unread** because the list is a JavaScript postback pager
   (RG-066). The Senate inquiry reports **16 November 2026** and its terms of reference are the only
   ones in Australia that expressly reach "deals between the Government and global Artificial
   Intelligence companies".

---

## 8. Why this belongs in the database

The brief's Pillar B asks about capital flows and Pillar C about regulatory capture. Both are
incomplete without an influence layer, because in Australia the physical footprint and the policy
footprint of the hyperscalers are in **different places**: AWS, Google and Meta appear in **zero** of
46 NSW planning records, and all three are BCA members, one with its country managing director on the
board.

A database that can say "AirTrunk's location-based scope 2 rose 485% while its peak body told a
parliamentary inquiry that 70% of the sector's electricity is already offset by renewables, and
while its founder-CEO sat on that peak body's board alongside Telstra, CBA, BHP, Wesfarmers and
Google" is doing something no single one of those facts does alone. That is the argument for keeping
`lobbying` next to `renewable_claims` and `power_profile` in the same schema, joined on the same
entities.

---

## 9. Reproducing this

```bash
cd au-dc-observatory
python3 scripts/rebuild_all.py                       # includes scripts/curate_airtrunk_bca.py
python3 scripts/query.py --sql "SELECT * FROM v_influence"
python3 scripts/query.py claims                      # renewable claim audit, all 11 claims
python3 scripts/query.py unverified                  # everything that must not be published as fact
```

Primary documents archived with SHA-256 manifests: BCA Submission No 116
(`data/raw/nsw_inquiry/submissions/BCA_116.pdf`, 1,120,166 bytes). Senate submissions index
(`data/raw/senate_inquiry/submissions_index.json`, first 20 of 116).
