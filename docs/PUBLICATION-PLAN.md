# PUBLICATION-PLAN.md

How the research gets finished, the open questions get answered, and the first
ten essays (ES-001 to ES-010) get published.

Written 2026-11-17, at the start of Release 2. Owner: the author. Agents draft
and do the free research; the author does the downloads, lodges the requests
and approves every essay. Nothing here publishes anything.

This plan sits beside the others. docs/DELIVERY-PLAN.md holds the releases and
docs/RESEARCH-PLAN.md the method for turning a question into a story card.
editorial/WRITING.md is the house voice every draft follows.

## Decisions (the author, 2026-11-17)

| Question | Decision |
| --- | --- |
| Voice | **"We"**, the observatory's voice. The writing guide adapts the author's article brief from another publication; everything else in it carries over (editorial/WRITING.md) |
| Human steps | **The author does the free downloads and lodges the FOI, GIPA and RTI requests.** Paid searches stay deferred |
| Dataset licence | **CC BY 4.0** for the CSV downloads and the `/data` page |
| Cadence | **As each essay is ready.** No fixed schedule: an essay publishes once its evidence is complete and the author approves it |
| Names in published source titles | **Replaced by role.** The verbatim title stays in the research database and the archive (see R2.0) |

## Where things stand (2026-11-17)

- **The record:** 102 sites, 296 sources and 146 entities, loaded to the hosted
  database from `main@39d7335`.
- **The research agenda:** 100 questions. 22 are resolved, 42 in progress and 36
  open.
- **Story cards:** 22 drafts, ST-001 to ST-022.
- **Essays:** ES-000 "Where we stand" (a position, not one of the ten) and
  ES-001 "Six in seven" are drafted, loaded unapproved and waiting for the
  author at `/admin`. Nothing is published.
- **Human steps:** none is done yet.
  - 21 free downloads are ranked in docs/requests/DOWNLOADS.md.
  - 11 requests are drafted in docs/requests/.
  - 8 paid searches ($157) are ranked and deferred.

## What "finished" means

- **A question is finished** in one of three ways:
  - it is resolved, with its answer in the database through a reviewed pack;
  - it is `blocked`, naming the one document or request its answer waits on;
  - the author closes it.

  It is never answered by a guess, and a refusal is recorded, never worked
  around.
- **An essay is finished** when the author approves it at `/admin`. Before
  that:
  - it has passed `npm run check:essays`;
  - it reads to editorial/WRITING.md;
  - every claim in its record sections rests on a source the database holds.
- **The ten essays are ES-001 to ES-010**, the roster in docs/DELIVERY-PLAN.md
  Releases 2 to 4. ES-000 is the position page and is separate.

## Part 1. Release 2: the agent's work

In order. Each item is one pull request, merged on the author's authority as
before.

### R2.0 People by role across the published record (do first)

**Found on 2026-11-17.** The essays already screen for personal names, but the
record the loader publishes does not, and some names reach the site:
- three entity rows that are individuals, listed by name;
- two source titles, which name chief executives because those are the
  documents' real headlines;
- one site's notes, naming a planning delegate;
- RG-079's text, ranking two named planning officers;
- RG-090's text, naming a former minister;
- RG-077's text, naming a former minister. That name is missing from the
  pipeline's lobbying records, so no list-based screen would catch it.

The hard rule is people by role until legal review is arranged (`CLAUDE.md`).
The research database is the workshop and may keep the names. The shopfront may
not.

**The fix, as built (2026-11-17):**
1. **The register.** A new research-database table, `people`
   (data-pipeline/schema/03_people.sql), lists each named person the lobbying
   and case-handling tables do not already cover, with the public role the site
   uses instead.
   - Every role is checked verbatim against the record that states it, by
     `scripts/curate_people.py`.
   - The register also overrides two lobbying roles too long to publish as a
     label.
2. **The loader** (lib/ingestion/people.ts) reads the register,
   `lobbying.person` and `case_handling.officer_name` at load time. No list of
   names is committed outside the research database. It replaces every name in
   every published text field:
   - with the role in square brackets;
   - with "[name withheld]" where the text already states the role beside the
     name;
   - for NSW planning officers, with a number fixed for the whole load, so
     RG-079's caseload analysis stays readable.

   A surname used alone after the full name is replaced too.
3. **The refusal.** The loader refuses to write a load that still names anyone
   it lists. It reports the field by role, never by name.
4. **Bylines are kept.** Journalists' bylines in a source's publisher field are
   not listed, on the author's decision of 2026-11-17. A byline is a citation's
   authorship.
5. **The essay screen reads the same three sources**, so a draft cannot name
   anyone the record withholds.
6. **The result.**
   - 26 people are listed.
   - Names are withheld in 19 fields: source titles, entity names, one site's
     notes, and RG-077, RG-079, RG-090, RG-076 and RG-092.
   - The load test asserts that the five entities which are individuals load
     under their role.
7. **Reload** the hosted database once this merges, and check it as `anon`.

**Gate:** no essay is approved until R2.0 is live, because essays link to
record pages.

### R2.1 Data for journalists (DELIVERY-PLAN, Release 2)

- **Downloads.** `app/data/{sites,entities,sources,research}.csv` on a new
  `lib/csv.ts`:
  - a formula-injection guard;
  - a `<field>_gap` column instead of a blank;
  - unit tests.
- **A `/data` page:**
  - the **CC BY 4.0** licence and how to attribute;
  - the as-of date and the load digest;
  - what each file holds;
  - what is deliberately absent: proposed links, unapproved essays, names.
- **Download manifests.** `data-pipeline/scripts/manifest.py <file> --url …`
  writes the manifest beside each document the author supplies, so a download
  enters the archive the same way the DigiCo documents did.

### R2.2 Process what the author brings back

Each download or request reply becomes one small pull request:
1. a manifest;
2. the hunt log;
3. a pack;
4. a rebuild;
5. the affected story card;
6. a reload.

If the document came through ASX, only verbatim excerpts are committed, as for
DigiCo's.

### R2.3 Batch 7: the parked questions

Part 3 below is the triage the delivery plan asked for. The agent then works
track A (13 questions) and the record-maintenance track R (26 questions) on
free sources, between essays. Questions waiting on a request move to `blocked`,
with the request named.

### R2.4 Essays from the evidence in hand

ES-003, ES-004, ES-006 and ES-009 can be drafted now (Part 4, wave 1).

Releases 3 (influence data) and 4 ("What if…?") stay as docs/DELIVERY-PLAN.md
sets them out. ES-007 does not wait for Release 3's tables, only for the
downloads it needs.

## Part 2. The author's steps

### Free downloads, in the order they unlock essays

Ranks are those in docs/requests/DOWNLOADS.md. Save each file to the folder
named there. Then upload it to a session, or put it in your Drive and say
where. The agent writes the manifest and does the rest.

| Order | Downloads | Unlocks | Essay |
| --- | --- | --- | --- |
| 1 | #8 ministers' diaries, #9 NSW lobbyist register, #10 Commonwealth lobbyist register | RG-070, RG-077 | ES-007 (and an update to ES-001) |
| 2 | #1 AustralianSuper, #2 Future Fund, #3 CSC, #6 UniSuper, ART and Aware holdings | RG-004, RG-094 | ES-002 |
| 3 | #4 NEXTDC's response to the ASX compliance letter, #5 OpenAI's "OpenAI for Australia" | RG-014 | ES-008 |
| 4 | #15 Queensland Hansard, 16 September 2026 | RG-012 | ES-010 |
| 5 | #13 state tender portals for Palantir, #14 the GTC keynote quote, #16 ASD's cloud FAQ | RG-086, RG-092, RG-093, RG-087, RG-089 | ES-009 (an update) |
| 6 | #17 NSW inquiry submissions, #18 Senate inquiry submissions | RG-015, RG-041, RG-016, RG-066 | ES-005 |
| 7 | #19 the planning SEPP as in force, #20 Victoria's DFP decisions and the M3 permit, #21 Melton and South Morang | RG-040, RG-069, RG-048, RG-056, RG-011 | ES-005, ES-006 |
| 8 | #11 AusTender and buy.nsw for the four consultancies | RG-074 | ES-007 |
| 9 | #7 Valuer General sales data, Kemps Creek | RG-005 | ES-002 |
| 10 | #12: read the archived Microsoft planning agreement and note clause 6.1 | RG-025 | ES-004 |

**ASX documents (#4).** The note at rank 4 asks for a decision on ASX's terms.
The DigiCo precedent applies unless the author says otherwise: the agent
commits the manifest and the verbatim excerpts, never the PDF.

### Requests to lodge, in order

Lodge each in your own name from its draft in docs/requests/. Then set its
status to `lodged` with the date in the index (docs/requests/README.md). The
agent works the due date out from that and marks each waiting question
`blocked`.

| Order | Request | To | Fee (as published) | Decision due | Unlocks | Essay |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | GIPA-001 | NSW Planning (DPHI): ownership documents | $30 | 20 working days | RG-021, RG-035, RG-037, RG-057, RG-059, RG-064 | ES-003 |
| 2 | GIPA-003 | DPHI: compliance and delegation | $30 | 20 working days | RG-058, RG-069, RG-040 | ES-006, ES-005 |
| 3 | FOI-002 and FOI-003 | Department of Defence | none; processing may be charged | 30 days | RG-087, RG-089 | ES-009 |
| 4 | FOI-004 | Australian Criminal Intelligence Commission | none; processing may be charged | 30 days | RG-093 | ES-009 |
| 5 | GIPA-002 | Revenue NSW | $30 | 20 working days | RG-007 | ES-004 |
| 6 | FOI-001 | Treasury (foreign investment) | none; processing may be charged | 30 days, plus 30 if third parties are consulted | RG-006 | ES-004 |
| 7 | GIPA-004 | Sydney Water | $30 | 20 working days | RG-017, RG-062, RG-068 | ES-008 |
| 8 | FOI-005 | Melbourne Water | $34.50, waivable | 30 days | RG-017, RG-080 | ES-008 |
| 9 | FOI-006 | Yarra Valley Water and South East Water (two applications) | each agency's own fee | 30 days | RG-017 | ES-008 |
| 10 | RTI-001 | Unitywater | $59.60, not waivable | see the draft | RG-017 | ES-008 |

**Cost.** Application fees come to about $214 for the NSW, Melbourne Water and
Queensland requests, plus the two Victorian water agencies' own fees, before
any processing charges. Commonwealth applications carry no fee. Check each
agency's live page before paying (docs/requests/README.md, "Fees, as
published").

### Deferred: paid searches

The eight paid searches stay deferred ($157, docs/requests/PAID-SEARCHES.md).
RG-036, RG-050, RG-052 and RG-081 can only be answered that way, so they stay
open and say so. Free substitutes are already recorded.

### Approvals

- **Now:** ES-000 and ES-001 at `/admin`, after SMTP is set up
  (docs/DELIVERY-PLAN.md, launch checklist).
- **Then:** each draft as its pull request merges and the agent loads it.

## Part 3. The research: every unresolved question

78 questions are unresolved, in five tracks:

| Track | Questions | Who moves it | What finished looks like |
| --- | --- | --- | --- |
| A. Agent work on free sources, for an essay | 13 | The agent, now | Resolved, or `blocked` on a named document |
| D. Waits on a download | 22 | The author downloads; the agent processes | Resolved from the downloaded document |
| F. Waits on a request | 13 | The author lodges; the agency decides | `blocked` until the reply; then resolved, or refused with the reasons recorded |
| P. Waits on a paid search (deferred) | 4 | Nobody, for now | Stays open, saying so |
| R. Record maintenance; no essay waits on it | 26 | The agent, between essays | Resolved, `blocked`, or closed by the author |

Rules for every track:
- An answer enters only through a pack, with its source graded and its values
  quoted.
- A question whose remaining answer waits on a request is `blocked`, never left
  `in_progress`.
- **Only the author closes a question.** The agent may propose closing one as
  `wont_fix` or `not_retrievable`, with the reason. Two candidates now:
  - RG-082 is a schema change (a `consultancy` entity type), not a research
    question. It moves to the engineering backlog.
  - RG-001 asks for distances to cable landings. That is analysis the v1 rule
    against GIS overlays leaves for later.

Questions are listed by track. "What it asks" is the question's opening clause;
the full text is on `/research`.

#### A. Agent work on free sources, for an essay (13)

| Question | Status | Essay | Next action | What it asks |
| --- | --- | --- | --- | --- |
| RG-039 | open | ES-006 | Agent, free sources | Test compliance with the website-disclosure condition |
| RG-043 | in progress | ES-004 | Agent, free sources | Test Data Centres Australia's $10.3bn energy infrastructure payment and $1.1bn excess capacity … |
| RG-061 | in progress | ES-006 | Agent, free sources | Test whether the 'no ratchet' finding holds |
| RG-063 | in progress | ES-004 | Agent, free sources | Quantify the DPHI concierge function and dedicated data centre assessment team |
| RG-088 | in progress | ES-009 | Agent, free sources | Complete the register of Australian companies partnering with or buying Palantir |
| RG-090 | in progress | ES-009 | Agent, free sources | Establish Palantir's and NVIDIA's actual position in AUKUS: whether either company holds AUKUS … |
| RG-098 | open | ES-003 | Agent, free sources | Is AirTrunk SYD2 the same facility as the Lane Cove West Data Centre (SSD-9741, 1 Sirius Road),… |
| RG-101 | in progress | ES-009 | Agent, free sources | Where are the five HCF-certified facilities that still have no site record - Cloud Carrier DB1;… |
| RG-102 | open | ES-003 | Agent, free sources | Who is the end user of the Macquarie Park Data Centre (SSD-10467, Stockland Trust Management Li… |
| RG-103 | open | ES-009 | Agent, free sources | Addresses, site areas and capacities for the eight facilities added from the HCF register (ADC … |
| RG-104 | open | ES-009 | Agent, free sources | Is SITE_MACQ_IC3 - recorded as 'IC3 Super West', operational, from a grade-C directory - the re… |
| RG-105 | open | ES-003 | Agent, free sources | Are Road 1 (SSD-80814238, SITE_ROAD_1) and 1-5 Khartoum Road (SSD-63235720, SITE_KHARTOUM) two … |
| RG-106 | open | ES-009 | Agent, free sources | Where are DigiCo's four other Australian properties - Townsville 1 (TSV1), Adelaide 2 (ADL2), B… |

#### D. Waits on a download you do (22)

| Question | Status | Essay | Next action | What it asks |
| --- | --- | --- | --- | --- |
| RG-004 | in progress | ES-002 | Download #1, #3, #6 | Trace domestic superannuation exposure to Australian data centres |
| RG-005 | in progress | ES-002 | Download #7 | Reconcile the ownership of 706-752 Mamre Road |
| RG-011 | in progress | ES-005 | Download #21 | Verify the Melton (Syncline Energy) and South Morang proposals |
| RG-014 | in progress | ES-008 | Download #4, #5 | Obtain the commercial structure of the OpenAI-NEXTDC S7 arrangement |
| RG-015 | in progress | ES-005 | Download #17 | Ingest all submissions to the NSW Legislative Council data centres inquiry and classify them by… |
| RG-016 | open | ES-005 | Download #17, #18 | Build the community action group register |
| RG-025 | in progress | ES-004 | Download #12 | Extract the contribution amount and schedule from the executed Microsoft / Penrith City Council… |
| RG-040 | in progress | ES-005 | Download #19; lodge GIPA-003 | Collect every council submission on data centre SSD applications in Blacktown, Penrith, Fairfie… |
| RG-041 | in progress | ES-005 | Download #17 | Harvest the ~120 submissions to the NSW Legislative Council Inquiry into Data Centres and code … |
| RG-048 | open | ES-005 | Download #20 | Enumerate every Victorian data centre permit issued through the Development Facilitation Progra… |
| RG-056 | open | ES-005 | Download #20 | Obtain the Minister for Planning's determination and permit conditions for the NEXTDC M3 expans… |
| RG-066 | in progress | ES-005 | Download #18 | Harvest all 116 submissions to the Senate Environment and Communications References Committee i… |
| RG-069 | in progress | ES-006 | Download #19; lodge GIPA-003 | Read the political donation disclosure filed on SSD-10330 (Roberts Road Data Centre, applicant … |
| RG-070 | in progress | ES-001, ES-007 | Download #8, #9, #10 | Check the NSW and Commonwealth lobbyist registers and ministerial diaries for meetings between … |
| RG-074 | in progress | ES-007 | Download #11 | Does any consultancy that authors technical evidence for data centre proponents also hold contr… |
| RG-077 | open | ES-007 | Download #8, #10 | Are a former NSW minister's concurrent roles - Austrade Senior Trade and Investment Commissione… |
| RG-086 | in progress | ES-009 | Download #13 | Build the complete Palantir contract ledger for ALL Australian governments |
| RG-087 | in progress | ES-009 | Download #16; lodge FOI-002 | Establish where Australian data actually sits for each Palantir deployment |
| RG-089 | in progress | ES-009 | Download #16; lodge FOI-003 | Resolve the ASD clearance discrepancy |
| RG-092 | in progress | ES-009 | Download #14 | Verify the Jensen Huang 'accelerate everything Palantir does' quote against the GTC Washington … |
| RG-093 | in progress | ES-009 | Download #13; lodge FOI-004 | Establish whether any Australian law-enforcement or criminal-justice agency runs Palantir softw… |
| RG-094 | in progress | ES-002 | Download #2 | Extend the public-money exposure check beyond the Future Fund |

#### F. Waits on a request you lodge (13)

| Question | Status | Essay | Next action | What it asks |
| --- | --- | --- | --- | --- |
| RG-006 | in progress | ES-004 | Lodge FOI-001 | Obtain FIRB records for every data centre-related foreign investment since 2020: application, n… |
| RG-007 | in progress | ES-004 | Lodge GIPA-002 | Establish whether any Australian state has granted payroll tax exemptions, land tax concessions… |
| RG-017 | open | ES-008 | Lodge GIPA-004, FOI-005, FOI-006, RTI-001 | Retrieve water access agreements and trade waste approvals between data centres and Sydney Wate… |
| RG-021 | in progress | ES-003 | Lodge GIPA-001; paid search deferred | Resolve KNBDC SYD4 Pty Ltd |
| RG-035 | in progress | ES-003 | Lodge GIPA-001 | Resolve the codename SPVs behind Project Duke, Project Atlas, Project Echidna, Project Apollo, … |
| RG-037 | in progress | ES-003 | Lodge GIPA-001; paid search deferred | Identify the developer and end user of the Glendenning Road Data Centre (SSD-73761707, 235 MW, … |
| RG-057 | in progress | ES-003 | Lodge GIPA-001; paid search deferred | Obtain the access-restricted documents on the Davis Road Data Centre application (SSD-59416728) |
| RG-058 | in progress | ES-006 | Lodge GIPA-003 | Obtain the warning letter issued in relation to the Roberts Road Data Centre (SSD-10330) and th… |
| RG-059 | in progress | ES-003 | Lodge GIPA-001; paid search deferred | Resolve 'The Trustee for NineZero DC Sub Trust I', the applicant for the DCI Poplars Data Centr… |
| RG-062 | open | - | Lodge GIPA-004 | Establish whether any consent or modification has relied on the Guidelines' definition of recyc… |
| RG-064 | in progress | ES-003 | Lodge GIPA-001; paid search deferred | Resolve EMKC Cubed Management Pty Ltd and HDI SYD1 Property Holdings Limited |
| RG-068 | open | - | Lodge GIPA-004 | Test whether AirTrunk's and the BCA's recycled water claims can be verified |
| RG-080 | open | - | Lodge FOI-005 | Do any TCS engagements for Melbourne Water touch recycled-water supply planning, third-party wa… |

#### P. Waits on a paid search (deferred) (4)

| Question | Status | Essay | Next action | What it asks |
| --- | --- | --- | --- | --- |
| RG-036 | in progress | ES-003 | Paid search (deferred); free substitutes recorded | Obtain ASIC company extracts for KNBDC AU Development Pty Ltd (ACN 687 116 098), KNBDC AU Finan… |
| RG-050 | in progress | ES-003 | Paid search (deferred); free substitutes recorded | Establish the domicile and ultimate ownership of AGP, the investment firm that owns Zerra DC, a… |
| RG-052 | in progress | ES-003 | Paid search (deferred); free substitutes recorded | Obtain ASIC company extracts for WDDP Pty Ltd and the six Zerra Australian entities, and establ… |
| RG-081 | in progress | ES-003 | Paid search (deferred); free substitutes recorded | Resolve beneficial ownership of EMKC Cubed Management Pty Ltd, HDI SYD1 Property Holdings Limit… |

#### R. Record maintenance; no essay waits on it (26)

| Question | Status | Essay | Next action | What it asks |
| --- | --- | --- | --- | --- |
| RG-001 | open | - | Record maintenance, free sources; no essay waits on it | Compute the straight-line distance from every mapped site to its nearest submarine cable landin… |
| RG-003 | in progress | - | Record maintenance, free sources; no essay waits on it | Ingest the Victorian planning register (Planning Online / Victoria's data centre fast-track lis… |
| RG-008 | open | - | Record maintenance, free sources; no essay waits on it | Extract environment protection licence conditions for every operating data centre |
| RG-010 | open | - | Record maintenance, free sources; no essay waits on it | Identify the proponent, site and status of the reported ~1 GW Western Australia data centre, an… |
| RG-013 | in progress | - | Record maintenance, free sources; no essay waits on it | Map hyperscaler site-level footprints |
| RG-018 | open | - | Record maintenance, free sources; no essay waits on it | Assess whether any Australian data centre currently provides system services (FCAS, system stre… |
| RG-019 | open | - | Record maintenance, free sources; no essay waits on it | Establish the existence and location of any synchronous condenser installation serving an Austr… |
| RG-024 | open | - | Record maintenance, free sources; no essay waits on it | Confirm Microsoft Kemps Creek's operational IT capacity, GFA and campus area from a primary sou… |
| RG-027 | open | - | Record maintenance, free sources; no essay waits on it | Verify and map the non-NEM and outer-metro proposals surfaced during RG-013: Wesley Vale AI dat… |
| RG-034 | in progress | - | Record maintenance, free sources; no essay waits on it | Extend the NSW register harvest to modification applications and to local council development a… |
| RG-042 | open | - | Record maintenance, free sources; no essay waits on it | Obtain IPART's actual position on Sydney Water's 25 per cent data centre water projection, and … |
| RG-044 | open | - | Record maintenance, free sources; no essay waits on it | Assess Unions NSW's proposal for local content and apprentice quotas at no less than Renewable … |
| RG-045 | open | - | Record maintenance, free sources; no essay waits on it | Fetch the modification reports and determinations for the five material post-consent modificati… |
| RG-051 | open | - | Record maintenance, free sources; no essay waits on it | Verify and map the reported ten-storey data centre outside Brisbane (Ipswich, plans reported fi… |
| RG-053 | open | - | Record maintenance, free sources; no essay waits on it | Extract the remaining appendices of the Western Downs application |
| RG-054 | open | - | Record maintenance, free sources; no essay waits on it | Track whether the Western Downs Digital Park is declared a Prescribed Project under the State D… |
| RG-071 | open | - | Record maintenance, free sources; no essay waits on it | Map AirTrunk's MEL2 campus, announced December 2025 as a site acquisition in Melbourne's north-… |
| RG-072 | open | - | Record maintenance, free sources; no essay waits on it | Obtain the full 65-record TCS contract list from the portals of record (AusTender and buy.nsw) … |
| RG-073 | open | - | Record maintenance, free sources; no essay waits on it | Establish which consultancy authored each technical appendix in the NSW data centre consents, b… |
| RG-075 | open | - | Record maintenance, free sources; no essay waits on it | Do peer reviews of acoustic and CFD evidence ever review work by the same firm, and how often i… |
| RG-076 | open | - | Record maintenance, free sources; no essay waits on it | Does TCS or HyperVault have any Australian data centre footprint, application, or announced sit… |
| RG-082 | open | - | Record maintenance, free sources; no essay waits on it | Extend the entity_type enum to include 'consultancy' and retype ARUP, LEHR, CUNDALL and the sys… |
| RG-083 | open | - | Record maintenance, free sources; no essay waits on it | Resolve the agency attribution and portal of record for the 'Office 365 Environment Setup for M… |
| RG-091 | open | - | Record maintenance, free sources; no essay waits on it | Map the NVIDIA DSX Australian buildout onto the physical site register |
| RG-097 | in progress | ES-008 | Record maintenance, free sources; no essay waits on it | What does each NSW State Significant Development data centre project's own planning document st… |
| RG-100 | in progress | - | Record maintenance, free sources; no essay waits on it | Replace CertifiedStrategic.com (SRC_CERTSTRAT) for what still rests on it alone |

## Part 4. The first ten essays

**Gates.** An essay goes to the author only when all of these hold:
1. R2.0 is live.
2. Its brief below is complete. A claim that the records cannot yet prove
   becomes a gap list, not a draft.
3. Every record-section claim cites a source the database holds.
4. `npm run check:essays` passes.
5. It reads to editorial/WRITING.md.

The author approves, and approval publishes.

**Tiers.** These follow editorial/WRITING.md, section 6:
- **brief**: 600 to 1,000 words;
- **deep dive**: 2,000 to 3,500 words, only where the evidence supports it.

**Candidate claims.** Each claim below is a candidate written from the story
cards. The drafting agent confirms it against the cited records, or weakens it,
before writing.

### Wave 1: the evidence is in hand

#### ES-001 "Six in seven" (M4). Drafted, waiting for approval

- **Claim.** The most reassuring number in the NSW Data Centre Guidelines
  comes from a briefing commissioned by AWS, and the Guidelines do not say so.
- **Cards and questions.** ST-011, ST-021; RG-078, RG-070, RG-067, RG-061.
- **Next.** The author approves at `/admin`. When downloads #8 to #10 come back,
  any meetings the diaries show go into ES-007, not into an edit of an approved
  essay.

#### ES-003 "Who is really applying" (M1). Deep dive, draft now

- **Claim.** In nine of the NSW data centre approvals whose assessment reports
  we hold, the Department says the applicant acts for, or was approached by, an
  operator it does not name.
- **Evidence in hand.**
  - ST-003: the nine assessment reports, and AirTrunk's own page on Apollo
    Place.
  - ST-004: the Mamre Road applicant renamed AirTrunk SYD4, and the land title.
  - ST-005: the Davis Road title in an Amazon company's name.
  - ST-006: WDDP Pty Ltd, registered seventeen days before its planning report.
  - ST-020: one consent counted twice, and an Amazon tenant no record supports.
- **Our receipts.** Locked attachments, a register of names and nothing else,
  and a caveat on a title.
- **Reader action.** A question for the Department of Planning, put in
  writing: "For each data centre consent where the applicant acts for an
  operator, will the Department publish the operator's name before
  determination?" Alternatively, GIPA-001's wording.
- **Gaps.**
  - RG-021, RG-035, RG-037, RG-057, RG-059 and RG-064 wait on GIPA-001.
  - RG-036, RG-050, RG-052 and RG-081 wait on paid searches (deferred).
  - RG-098 and RG-105 are agent work.
- **Conflict.** None, unless the draft touches the Western Downs tenant
  (ST-016).
- **Named parties.** None; companies only.

#### ES-004 "What the public gives" (M3). Brief, draft now

- **Claim.** The industry's "$10.3 billion" of energy infrastructure spending
  is not a figure its own commissioned report states.
  - The report gives $3.1 billion spent from 2020 to 2025 and $7.2 billion
    forecast to 2030.
  - The only $10.3 billion the report states is the Australian Government's
    grid funding.
- **Evidence in hand.**
  - ST-009: the inquiry transcript, the Mandala report, and Transgrid's 22 May
    2026 evidence.
  - ST-010: the consents' contributions of $3,568.10 to about $8.6 million,
    Penrith's draft agreement, and the Investment Delivery Authority's budget.
- **Reader action.** A question for Data Centres Australia: "Which document
  states $10.3 billion of energy infrastructure paid for by operators, and on
  which page?"
- **Gaps.**
  - RG-007 waits on GIPA-002.
  - RG-006 waits on FOI-001.
  - RG-025 waits on download #12.
  - RG-063 and RG-043 are agent work.
- **Named parties.** None; peak bodies and companies only.

#### ES-006 "Did anyone check?" (C2). Brief, draft now

- **Claim.** Since July 2026, NSW approvals have required data centres to match
  all their electricity with firmed renewable supply before operating, a
  stronger rule than the three applicants offered. The public record of whether
  conditions are enforced runs to two warning letters.
- **Evidence in hand.**
  - ST-021: three approvals and the assessment reports' weaker offers.
  - ST-019: the Roberts Road and Station Road warning letters, and Glendenning's
    audit conditions.
  - ST-018: the donation disclosures and the delegation.
- **Reader action.** A question for the Planning Secretary: "How many
  compliance actions has the Department taken on data centre consents since
  2019, and will it publish them?" Alternatively, GIPA-003's wording.
- **Gaps.**
  - RG-058 and RG-069 wait on GIPA-003.
  - RG-039 (the website-disclosure condition) and the rest of RG-061 are agent
    work.
- **Named parties.** None. Officers appear by role, if at all.

#### ES-009 "Whose data, whose rules" (C3). Deep dive, draft now

- **Claim.** Commonwealth agencies have published 29 contracts with Palantir
  since 2013, worth $68,258,634.93 at their latest values, and none of them
  records where the software is hosted.
- **Evidence in hand.**
  - ST-012: the AusTender ledger.
  - ST-013: hosting, and the signals directorate outside the FOI Act.
  - ST-014: Coles.
  - ST-015: WA Police and NEC.
  - ST-022: the government's certified facilities, and the tenant DigiCo will
    not name.
- **Reader action.** FOI-002's wording, for any reader to lodge with Defence.
  Alternatively, a question for each agency: "In which facility, and under
  which certification, is the data your Palantir contract processes held?"
- **Gaps.**
  - RG-087 and RG-089 wait on FOI-002 and FOI-003.
  - RG-093 waits on FOI-004.
  - RG-086 waits on download #13 and RG-092 on #14.
  - RG-088 and RG-090 are agent work.

  Replies arrive after publication, so they go into a follow-up piece, not an
  edit.
- **Named parties.** None. The keynote speaker and former office holders appear
  by role.

### Wave 2: after the author's downloads

#### ES-002 "Already in your super" (M2). Brief now, deep dive after downloads 1 to 3 and 6

- **Claim.** Ordinary Australians' retirement savings already hold data centre
  operators. At 30 June 2026, Cbus's Growth option held A$344.5 million of
  NEXTDC shares, Hostplus's Balanced option A$109.1 million and HESTA's Balanced
  Growth option A$73.5 million.
- **Evidence in hand.** ST-007: the three funds' holdings files, NEXTDC's
  annual report, the Future Fund's report, and the Mamre Road title.
- **Waits on.** Downloads #1, #2, #3 and #6 (RG-004, RG-094), and #7 (RG-005).
- **Reader action.** A question for the member's own fund: "What is the fund's
  total exposure to data centre owners and operators, by option, at the last
  disclosure date?"

#### ES-008 "The OpenAI deal" (M5). Brief

- **Claim.** NEXTDC's S7 deal with OpenAI is a memorandum of understanding that
  states no price, term, capacity or ownership stake, for a site whose own
  planning document gives its size two ways.
- **Evidence in hand.**
  - ST-008: the announcement, the compliance-letter listing, and the FY26
    "TBD".
  - ST-002: 612 megawatts against about 700, and the water demand.
- **Waits on.** Downloads #4 and #5 (RG-014). GIPA-004 (RG-017) would add the
  water story.
- **Reader action.** A question for NEXTDC's investor relations team: "What
  capacity, term and price does the OpenAI memorandum commit either party to?"
- **Gaps.** RG-014, RG-097 and RG-099 (S7's IT load).

#### ES-010 "The tenant" (C3). Brief, conflict disclosure at the top

- **Claim.** The application for the Western Downs Digital Park does not
  mention its tenant. About a month later, Dexus told the stock exchange that the
  consortium had entered into lease documentation with Anthropic's Australian
  subsidiary.
- **Evidence in hand.** ST-016 and ST-006: the planning report, the Dexus
  announcement, and the ASIC registration dates.
- **Waits on.** Download #15, the Premier's statement in Hansard (RG-012).
- **Conflict.** This piece is about Anthropic, which makes the model that
  drafts it. The disclosure goes at the top, the checker requires it, and the
  author should read this one with particular care.
- **Reader action.** A question for the Queensland Government: "Was the
  Western Downs Digital Park's tenant disclosed to any Queensland agency before
  16 September 2026, and when?"
- **Gaps.** RG-012, RG-053 and RG-054.

#### ES-005 "Who gets heard" (C1). Brief

- **Claim.** Of the eight local council objections to data centres the
  Department has decided, one reached the Independent Planning Commission. A
  delegation of 18 August 2026 now lets an officer decide some data centres
  over a council's objection.
- **Evidence in hand.** ST-017: the assessment reports, the planning website,
  and the Apollo delegation.
- **Waits on.**
  - Downloads #17 and #18 (RG-015, RG-041, RG-066, RG-016).
  - Downloads #19 to #21 (RG-040, RG-048, RG-056, RG-011).
  - GIPA-003 (RG-040).
- **Reader action.** A question for the local council: "Did the council object
  to this data centre, and was the objection maintained to determination?"

#### ES-007 "Who is in the room" (M4, follow-up to ES-001). Gap list until the downloads come back

- **Claim.** Not yet set. It is written from what downloads #8 to #11 show
  about meetings, lobbyists and consultancies (RG-070, RG-077, RG-074). Until
  then the essay is a gap list, not a draft.
- **Named parties.** Lobbyists, officials and ministers all appear by role
  until legal review is arranged.

### The order, in short

| Wave | When | Essays |
| --- | --- | --- |
| 0 | Now | R2.0 and R2.1. The author approves ES-000 and ES-001, lodges the requests, and starts the downloads |
| 1 | Now, from evidence in hand | ES-003, ES-004, ES-006, ES-009 |
| 2 | As each group of downloads arrives | ES-002, ES-008, ES-010, ES-005, ES-007 |
| 3 | As replies arrive (20 working days to 30 days after lodgement, longer if extended) | Follow-up pieces for ES-003, ES-006 and ES-009. Never silent edits to an approved essay |

## How an essay moves

1. **Brief.** The entry above is completed in the writing guide's format.
2. **Draft.** The agent writes `editorial/essays/ES-nnn-slug.md` to the guide,
   runs `npm run check:essays`, and opens a pull request. If the evidence is
   missing, it writes a gap list here instead.
3. **Merge and load.** After merge, the agent loads the draft (`npm run
   load:essays`, unapproved) and checks as `anon` that it is not visible.
4. **Approval.** The author reads, edits and approves at `/admin`. Approval
   publishes.
5. **Afterwards.** An approved essay belongs to the editor. New evidence becomes
   a follow-up piece, or the editor's own edit, never an agent's.
