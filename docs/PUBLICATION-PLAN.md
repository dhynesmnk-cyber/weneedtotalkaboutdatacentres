# PUBLICATION-PLAN.md

How the research gets finished, the open questions get answered, and the first
ten essays (ES-001 to ES-010) get published.

Written 2026-11-17, at the start of Release 2; updated 2026-11-18 with the
author's zero-spend decision, the approve-now rule and five new essays
(ES-011 to ES-015). Owner: the author. Agents draft
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

## Decisions (the author, 2026-11-18)

| Question | Decision |
| --- | --- |
| Spending | **Zero spend.** No paid extract or search, and no request that carries a fee. That rules out every state request (NSW GIPA $30, Victorian FOI $34.50, Queensland RTI $59.60). The four Commonwealth FOI requests carry no application fee and are lodged, each asking for any processing charge to be waived; if a charge is still levied, the request is narrowed or withdrawn, never paid |
| Approvals | **Approve now; follow-ups later.** The author approves ES-000 to ES-010 at `/admin` as drafted. New evidence becomes a follow-up piece (see "Follow-ups" in Part 4), never an agent's edit to an approved essay |
| Conflict notes | **Unchanged.** A disclosure only where a piece touches Anthropic; none for Amazon or Google as investors |
| Five more essays | **ES-011 to ES-015**, on topics the research turned up, the fifth being who checks the consultants (Part 4, wave 3) |

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
7. **Done and live, 2026-11-17.** The hosted database was reloaded from
   `main@056aa5b` and checked as `anon`: none of the 639 published rows names
   anyone listed (docs/SUPABASE_SETUP.md).

**Gate:** no essay is approved until R2.0 is live, because essays link to
record pages.

### R2.1 Data for journalists (DELIVERY-PLAN, Release 2)

**Built 2026-11-17** (`lib/csv.ts`, `lib/dataExport.ts`, `app/data/`). It goes
live at merge; no reload is needed. Still to come: `manifest.py`, written when
the first download arrives.

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

All four wave-1 essays are drafted: ES-003, ES-004, ES-006 and ES-009 (Part 4).
The wave-2 briefs ES-002, ES-005, ES-008 and ES-010 are drafted from the
records in hand, each stating the downloads it still lacks as gaps. ES-007
stays a gap list.

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

### Requests to lodge, in order (zero spend, 2026-11-18)

Lodge each in your own name from its draft in docs/requests/, asking for any
processing charge to be waived on public-interest grounds. Then set its status
to `lodged` with the date in the index (docs/requests/README.md). The agent
works the due date out from that and marks each waiting question `blocked`.

| Order | Request | To | Fee | Decision due | Unlocks | Essay |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | FOI-002 and FOI-003 | Department of Defence | none; ask that any processing charge be waived | 30 days | RG-087, RG-089 | ES-009 follow-up |
| 2 | FOI-004 | Australian Criminal Intelligence Commission | none; as above | 30 days | RG-093 | ES-009 follow-up |
| 3 | FOI-001 | Treasury (foreign investment) | none; as above | 30 days, plus 30 if third parties are consulted | RG-006 | ES-004 follow-up |

**Not lodged under zero spend.** These stay drafted, so they can be lodged if
the decision changes, and the questions behind them are marked `blocked`, naming
the request and the free substitutes already tried:

| Request | Fee | Questions blocked on it | Free substitutes worked instead |
| --- | --- | --- | --- |
| GIPA-001 (DPHI ownership documents) | $30 | RG-021, RG-035, RG-037, RG-057, RG-059, RG-064 | ASIC's free monthly company dataset; land titles filed with applications; operators' own pages |
| GIPA-002 (Revenue NSW) | $30 | RG-007 | the NSW Budget tax expenditure statement; Revenue NSW's annual report |
| GIPA-003 (DPHI compliance and delegation) | $30 | RG-058, part of RG-040 and RG-069 | the NSW Electoral Commission's disclosure register (RG-069); download #19 (the SEPP versions) |
| GIPA-004 (Sydney Water) | $30 | RG-017, RG-062, RG-068 | the consents' and modifications' own recycled-water wording; IPART's and Sydney Water's public documents; download #27 |
| FOI-005 (Melbourne Water) | $34.50 | RG-080, part of RG-017 | Melbourne Water's annual report and published tenders |
| FOI-006 (Yarra Valley and South East Water) | each agency's fee | part of RG-017 | the utilities' annual reports |
| RTI-001 (Unitywater) | $59.60 | part of RG-017 | Unitywater's annual report |

### Deferred: paid searches

The eight paid searches stay deferred ($157, docs/requests/PAID-SEARCHES.md),
and under the zero-spend decision of 2026-11-18 they are not bought. RG-036,
RG-050, RG-052 and RG-081 can only be answered that way, so they stay open and
say so. Free substitutes are recorded: ASIC's free monthly company dataset,
issuers' annual reports and free foreign registry pages.

### Approvals

- **Done (2026-11-18):** the editor approved nine at `/admin`: ES-000 to ES-006,
  ES-009 and ES-010 (ES-010 edited first). ES-008 is not yet approved; ES-007 is
  not drafted.
- **Now:** ES-008, ES-011, ES-013 and ES-015, loaded as drafts on 2026-11-18.
- **Then:** each new draft (ES-011 onward, and each follow-up) as its pull
  request merges and the agent loads it.

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

#### Batch 7, first pass (2026-11-18)

At the author's direction to work every open question. Pack:
`data-pipeline/data/packs/batch7_open_questions.json`; each question's hunt log
has a dated entry.

- **Resolved.** RG-105: two buildings, per the Department's own report. RG-044:
  the Unions NSW proposal was not adopted; the Guidelines only encourage local
  content.
- **Settled in part.** RG-025: the executed Penrith agreement, read by OCR and
  checked against the page image, keeps $8,423,505.96. RG-088: Westpac is now
  reported by two outlets quoting the bank, so it is added as an entity.
- **Answered; the record change is the author's.**
  - RG-098: AirTrunk's own page makes SYD2 the Lane Cove West consent, and
    Apollo Place AirTrunk's "Phase 5".
  - RG-102: the Department's March 2026 report calls the Macquarie Park
    building operational.
  - RG-024: Microsoft Kemps Creek's 190 MW is an unlabelled "operational
    capacity", not IT load.
  - RG-071: AirTrunk's MEL2 page gives an area and a floor area, but no status.
- **Blocked.** RG-039 waits on RG-037.
- **Tried, refused, logged.**
  - RG-054, RG-010, RG-051, RG-101, RG-103 and RG-106 each have a refusal
    recorded and a lead noted.
  - Downloads #22 to #26 are new, for a person.
  - RG-090, RG-091 and RG-076 are updated, with nothing asserted that the
    record does not hold.
- **Second pass, same day.**
  - RG-045 resolved: the five modification reports, read from the portal, give
    the quantities.
    - Eastern Creek: 32 MW to 63 MW.
    - Roberts Road: 48 to 72 generators, with 96 proposed.
    - Lane Cove West: 116 smaller generators and 1,952 kL of fuel.
    - Talavera Road: 38 MW to 47 MW.
  - RG-072: the Commonwealth part is settled from the AusTender feed (7 TCS
    notices, $41,416,192.60).
  - RG-083: narrowed, since neither award is a Commonwealth notice.
  - RG-027: Firmus's own Wesley Vale page is archived; a site row is proposed
    for the author.
  - RG-042 and RG-018: leads recorded.
  - RG-001 and RG-082: proposed for closing.
- **Decided by the author, 2026-11-18.**
  - RG-098: the SYD2 seed row is merged into the Lane Cove West consent row,
    and AirTrunk is Apollo Place's operator.
  - RG-102: the Macquarie Park building is operational.
  - RG-024: Kemps Creek's unlabelled 190 MW is cleared.
  - RG-071 and RG-027: MEL2 and Wesley Vale are added, with no capacity
    stored.
  - RG-001 and RG-082: closed as wont_fix.
  - RG-104: stays open; the author cannot say which building the register
    means.
- **Not yet worked.**
  - Track A: RG-043, RG-061, RG-063, RG-104 (needs Macquarie's own statement).
  - Track R: RG-003, RG-008, RG-013, RG-019, RG-053, RG-073, RG-075, RG-097.

#### Batch 8, planned (2026-11-18): every remaining question, at zero spend

Seventy questions were unresolved after batch 7 (22 open, 47 in progress, 1
blocked). Each ends resolved, `blocked` on a named free document or free
Commonwealth request, proposed to the author for closing, or open and saying
why (the paid-search track). Pack: `data-pipeline/scripts/curate_batch8.py`, on
the batch 7 pattern.

| Route | Questions | What the agent does |
| --- | --- | --- |
| Agent, free sources | RG-003, RG-008, RG-013, RG-018, RG-019, RG-025 (payments), RG-027 (the rest), RG-034 (approved councils only), RG-043, RG-053, RG-061, RG-063, RG-073, RG-074, RG-075, RG-088, RG-091, RG-097, RG-100, RG-101, RG-103, RG-104, RG-106 | Works each from public sources through the archiver; a refusal becomes a download for a person |
| Free substitutes for unlodged requests | RG-007, RG-062, RG-068, RG-069, RG-080 | The substitutes in the request table above |
| Proposed to the author for closing | RG-076 and RG-090 (resolved-negative), RG-102 and the unmappable part of RG-013 (not retrievable at zero spend) | Proposes; only the author closes |
| The author's downloads | RG-004, RG-005, RG-010, RG-011, RG-014, RG-015, RG-016, RG-040, RG-041, RG-042, RG-048, RG-051, RG-054, RG-056, RG-066, RG-070, RG-072, RG-077, RG-083, RG-086, RG-092, RG-094 | Processes each download through a pack once it is in `data/raw/` |
| Free Commonwealth requests | RG-006, RG-087, RG-089, RG-093 | `blocked` until the reply |
| Blocked at zero spend | RG-021, RG-035, RG-037, RG-057, RG-058, RG-059, RG-064, RG-017; RG-039 on RG-037 | `blocked`, naming the unlodged request |
| Paid, not bought | RG-036, RG-050, RG-052, RG-081 | Open, saying so |

Download priority now follows the essays they unlock: #22 and #26 (ES-013);
#23, #24, #25 and Latrobe Council's Wesley Vale record (ES-014); #2 (ES-012);
#8 to #11 (ES-007, ES-015); #17 to #19 (ES-005's follow-up); #1, #3, #6 and #7
(ES-002's); #4 and #5 (ES-008's); #13, #14 and #16 (ES-009's); then #15, #20,
#21 and #27.

#### Batch 8, first pass (2026-11-18)

Pack `data/packs/batch8_open_questions.json` (`scripts/curate_batch8.py`). It
touches 23 questions. Unresolved after it: 68, of which 14 are `blocked`,
37 in progress and 17 open. The tables below are the snapshot taken after
batch 7, and this list is what changed.

- **Resolved: RG-062.** No consent or modification relies on the Guidelines'
  definition of recycled water. The closest usage, rainwater tanks under
  "Recycled water and reuse" at DigiCo SYD1, predates the Guidelines.
- **Resolved: RG-075.** The pass opened all five public review letters. In
  each, the reviewer is a different firm from the author.
  - Every review was engaged by the applicant, its planner or the report's own
    author. None was engaged by the Department.
  - The two acoustic reviews did no remodelling.
  - One firm wrote all three greenhouse reviews. At Project Atlas, the author
    of the greenhouse report engaged that reviewer.
- **Advanced: RG-073.** The firm behind 35 acoustic and air quality reports
  (18 consents), read from each report's own pages. In three of the six consents
  held by a consultancy, that consultancy wrote its own evidence.
- **Advanced: RG-061.** These counts are computed from the 20 instruments:
  - 15 consents cap generators at 200 hours a year, the line in the
    Guidelines;
  - the three decided since July 2026 set 170, 173 and 187 hours, and the 187
    is the applicant's own figure;
  - 13 cap diesel at 2,000 tonnes.

  At Macquarie Park, the environment regulator itself recommended the 200-hour
  cap "To ensure an EPL is not required".
- **Blocked: RG-008, on download #28.** Four sites need a licence, according to
  the reports: 51 Huntingwood Drive, NEXTDC S4, Marsden Park, and Roberts Road
  as modified. At Khartoum Road, the regulator does not consider itself the
  authority for air emissions, because no licence is required. RG-008 is now
  cited, so it publishes: 96 questions load.
- **Zero spend.** These questions are set to `blocked`, naming the request:
  - RG-021, 035, 037, 057, 059 and 064: GIPA-001's items;
  - RG-058: GIPA-003;
  - RG-017: the four water requests;
  - RG-006, 087, 089 and 093: the four free Commonwealth FOIs, until the author
    lodges them and a reply comes.

  RG-036, 050, 052 and 081 say they wait on paid extracts.
- **Proposed to the author for closing as resolved-negative:** RG-076 and
  RG-090. The pack closes neither.
- **New downloads:** #28 (the EPA register) and #29 (Project Echidna's air
  quality report, over the crawler's size limit).

#### Batch 8, second pass (2026-11-18)

Pack `data/packs/batch8b_open_questions.json` (`scripts/curate_batch8b.py`).
It touches 14 questions. Unresolved after it: 67, of which 20 are `blocked`,
34 in progress and 13 open. Sources: 329. Questions loaded: 98.

- **Resolved: RG-019.** Transgrid will put two synchronous condensers at the
  Kemps Creek 500 kV substation, energised from early 2028. None serves a data
  centre today.
- **RG-034: the modification half is done.** All 17 modification records are
  read. Three more add generators or diesel:
  - Lane Cove West Mod 4: diesel from 1,651 to 1,966.9 tonnes, "below the
    storage limit of 2,000 t". Decided under delegation, and not exhibited.
  - Lanceley Place Mod 2: from 30 to 42 generators.
  - Lane Cove West Mod 3: from 116 to 121 generators. This one was exhibited.

  Their reclassification is **proposed to the author**. Council development
  applications remain.
- **RG-018 and RG-043:** Transgrid's own page is now on the record:
  - "more than 10 GW" of data centre connection enquiries within 12 km of
    Sydney West;
  - capacity in the Sydney basin is "largely exhausted";
  - large users are to "play their role" in system strength.

  RG-018 is `blocked` on AEMO's list (download #31).
- **RG-100:** the 1,350 MW and 3,100 MW figures are re-sourced to Mandala's own
  October 2024 report.
- **Blocked:**
  - RG-068 and RG-080: the free substitutes were read and are silent;
    GIPA-004 and FOI-005 are not lodged.
  - RG-007, RG-063 and RG-069: each primary record was refused, so they are
    downloads #30, #33 and #34.
- **RG-027:** the Beetaloo release was refused (download #32).
- **Proposed to the author as not retrievable at zero spend:** RG-013 (the AWS
  and Google remainder) and RG-102 (Macquarie Park's end user).

#### The author's decisions and downloads (2026-11-18)

Pack `data/packs/batch8_decisions.json` (`scripts/curate_batch8_decisions.py`).
Unresolved after it: 62, of which 17 are `blocked`, 33 in progress and 12 open.
Sources: 332.

- **Decided.** RG-076 and RG-090 are resolved-negative. RG-013's remainder and
  RG-102 are closed as not retrievable at zero spend (`wont_fix`). Three
  modification rows are reclassified (Lane Cove West Mods 3 and 4, Lanceley
  Place Mod 2).
- **RG-018, resolved from download #31.** A Firmus company is registered to
  provide ancillary services as a load, and another ran a 20 MW ancillary service
  load at St Leonards, Tasmania, until 2023. CDC is an intending participant.
  NEXTDC's backup generators at seven sites are exempt, with zero export.
- **RG-007, from download #30.** The NSW tax expenditure statement never mentions
  data centres. Sydney Water's servicing rests on "full cost recovery".
- **RG-027, from download #32.** Beetaloo Digital holds a "not to deal"
  commitment over 185 ha at Weddell. The release names Energy North's Project
  Ares too. **Two new site rows are proposed to the author.**
- **RG-069, from download #34 in part and the AEC's free bulk returns.**
  - NSW: Amazon Web Services Australia is the one data centre company among the
    major political donor entities.
  - Commonwealth, 2020-21 to 2024-25: Amazon's own returns disclose $523,945 of
    donations to Labor and Liberal branches, and Macquarie Technology Group's
    $316,324 to parties.
  - Labor's returns record $27,900 from CDC as "Other Receipt".
  - AirTrunk's $104,500 in 2024-25 went to the Business Council of Australia,
    a lobby group.
  - The NSW amounts still need Amazon's own disclosures.
- **Duplicates fixed.** Two sources registered twice (Transgrid's data centre
  page, and NVIDIA's release) now cite the earlier rows. The two live
  duplicates are proposed to the author for removal.

**Second round (2026-11-18).** The author agreed:
- PR #47 was merged and loaded.
- The two duplicate source rows were removed from the hosted database, in one
  checked transaction.
- Two Northern Territory sites were added, each cited to the NT Government's
  release (`batch8_decisions_2.json`): Beetaloo Digital at Weddell and Energy
  North's Project Ares. Both are pre-lodgement, unmapped, and carry no capacity.

The author also read Amazon Web Services Australia's NSW disclosures. They show
$39,350 of political donations over 2023/24 to 2025/26: totals only, with no
recipients.

Not touched (no new free source reached them): RG-003, 025, 053, 088, 097,
101, 103, 104 and 106. Each waits on a named download already listed (#20,
#22, #26) or on the paid-search track, except RG-053, which needs the
Western Downs application (about 344 MB) fetched again.

#### A. Agent work on free sources, for an essay (13)

| Question | Status | Essay | Next action | What it asks |
| --- | --- | --- | --- | --- |
| RG-039 | blocked (RG-037) | ES-006 | Agent, free sources | Test compliance with the website-disclosure condition |
| RG-043 | in progress | ES-004 | Agent, free sources | Test Data Centres Australia's $10.3bn energy infrastructure payment and $1.1bn excess capacity … |
| RG-061 | in progress | ES-006 | Agent, free sources | Test whether the 'no ratchet' finding holds |
| RG-063 | in progress | ES-004 | Agent, free sources | Quantify the DPHI concierge function and dedicated data centre assessment team |
| RG-088 | in progress | ES-009 | Agent, free sources | Complete the register of Australian companies partnering with or buying Palantir |
| RG-090 | in progress | ES-009 | Agent, free sources | Establish Palantir's and NVIDIA's actual position in AUKUS: whether either company holds AUKUS … |
| RG-098 | resolved | ES-003 | Agent, free sources | Is AirTrunk SYD2 the same facility as the Lane Cove West Data Centre (SSD-9741, 1 Sirius Road),… |
| RG-101 | in progress | ES-009 | Agent, free sources | Where are the five HCF-certified facilities that still have no site record - Cloud Carrier DB1;… |
| RG-102 | in progress (end user) | ES-003 | Agent, free sources | Who is the end user of the Macquarie Park Data Centre (SSD-10467, Stockland Trust Management Li… |
| RG-103 | open | ES-009 | Agent, free sources | Addresses, site areas and capacities for the eight facilities added from the HCF register (ADC … |
| RG-104 | open | ES-009 | Agent, free sources | Is SITE_MACQ_IC3 - recorded as 'IC3 Super West', operational, from a grade-C directory - the re… |
| RG-105 | resolved | ES-003 | Agent, free sources | Are Road 1 (SSD-80814238, SITE_ROAD_1) and 1-5 Khartoum Road (SSD-63235720, SITE_KHARTOUM) two … |
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
| RG-001 | wont_fix | - | Record maintenance, free sources; no essay waits on it | Compute the straight-line distance from every mapped site to its nearest submarine cable landin… |
| RG-003 | in progress | - | Record maintenance, free sources; no essay waits on it | Ingest the Victorian planning register (Planning Online / Victoria's data centre fast-track lis… |
| RG-008 | open | - | Record maintenance, free sources; no essay waits on it | Extract environment protection licence conditions for every operating data centre |
| RG-010 | open | - | Record maintenance, free sources; no essay waits on it | Identify the proponent, site and status of the reported ~1 GW Western Australia data centre, an… |
| RG-013 | in progress | - | Record maintenance, free sources; no essay waits on it | Map hyperscaler site-level footprints |
| RG-018 | open | - | Record maintenance, free sources; no essay waits on it | Assess whether any Australian data centre currently provides system services (FCAS, system stre… |
| RG-019 | open | - | Record maintenance, free sources; no essay waits on it | Establish the existence and location of any synchronous condenser installation serving an Austr… |
| RG-024 | resolved | - | Record maintenance, free sources; no essay waits on it | Confirm Microsoft Kemps Creek's operational IT capacity, GFA and campus area from a primary sou… |
| RG-027 | open | - | Record maintenance, free sources; no essay waits on it | Verify and map the non-NEM and outer-metro proposals surfaced during RG-013: Wesley Vale AI dat… |
| RG-034 | in progress | - | Record maintenance, free sources; no essay waits on it | Extend the NSW register harvest to modification applications and to local council development a… |
| RG-042 | open | - | Record maintenance, free sources; no essay waits on it | Obtain IPART's actual position on Sydney Water's 25 per cent data centre water projection, and … |
| RG-044 | resolved | - | Record maintenance, free sources; no essay waits on it | Assess Unions NSW's proposal for local content and apprentice quotas at no less than Renewable … |
| RG-045 | resolved | - | Record maintenance, free sources; no essay waits on it | Fetch the modification reports and determinations for the five material post-consent modificati… |
| RG-051 | open | - | Record maintenance, free sources; no essay waits on it | Verify and map the reported ten-storey data centre outside Brisbane (Ipswich, plans reported fi… |
| RG-053 | open | - | Record maintenance, free sources; no essay waits on it | Extract the remaining appendices of the Western Downs application |
| RG-054 | open | - | Record maintenance, free sources; no essay waits on it | Track whether the Western Downs Digital Park is declared a Prescribed Project under the State D… |
| RG-071 | resolved | - | Record maintenance, free sources; no essay waits on it | Map AirTrunk's MEL2 campus, announced December 2025 as a site acquisition in Melbourne's north-… |
| RG-072 | open | - | Record maintenance, free sources; no essay waits on it | Obtain the full 65-record TCS contract list from the portals of record (AusTender and buy.nsw) … |
| RG-073 | open | - | Record maintenance, free sources; no essay waits on it | Establish which consultancy authored each technical appendix in the NSW data centre consents, b… |
| RG-075 | open | - | Record maintenance, free sources; no essay waits on it | Do peer reviews of acoustic and CFD evidence ever review work by the same firm, and how often i… |
| RG-076 | open | - | Record maintenance, free sources; no essay waits on it | Does TCS or HyperVault have any Australian data centre footprint, application, or announced sit… |
| RG-082 | wont_fix | - | Record maintenance, free sources; no essay waits on it | Extend the entity_type enum to include 'consultancy' and retype ARUP, LEHR, CUNDALL and the sys… |
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

#### ES-003 "Who is really applying" (M1). Drafted as "Nine approvals, no operator", waiting for approval

- **Drafted.** `editorial/essays/ES-003-nine-approvals-no-operator.md`, a deep
  dive of about 2,000 words. The claim was confirmed against RG-055 and
  narrowed to "nine of the 22 determined NSW data centre consents whose reports
  we hold". It also uses ST-022 (DigiCo's unnamed 71 MW tenant at SYD1) and the
  Glendenning Road consent's definition of "Applicant". It carries the
  conflict disclosure, because it touches the Western Downs project, though not
  its tenant. **Next:** the author approves at `/admin`; replies to GIPA-001
  become a follow-up piece, not an edit.
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

#### ES-004 "What the public gives" (M3). Drafted as "The $10.3 billion is two numbers added together", waiting for approval

- **Drafted.** `editorial/essays/ES-004-ten-point-three.md`, a brief of about
  1,000 words. The claim was confirmed against RG-043 and the transcripts.
  Transgrid's evidence is quoted as said ("We haven't actually fully
  connected one yet"), which is narrower than the card's wording. The
  Penrith agreement stays under RG-025, to keep the brief inside its tier.
  **Next:** the author approves at `/admin`.
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

#### ES-006 "Did anyone check?" (C2). Drafted as "A stronger rule, and two warning letters", waiting for approval

- **Drafted.** `editorial/essays/ES-006-two-warning-letters.md`, a brief of
  about 1,000 words. It uses the writing guide's model analogy for "prior to
  the commencement of operation", with where it breaks. The Roberts Road
  donation form is set beside the report's words, and nothing improper is
  alleged. **Next:** the author approves; GIPA-003's replies become a
  follow-up piece.
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

#### ES-009 "Whose data, whose rules" (C3). Drafted as "Twenty-nine contracts, and none says where", waiting for approval

- **Drafted.** `editorial/essays/ES-009-twenty-nine-contracts.md`, a deep
  dive of about 2,070 words. Totals were recomputed from the contracts table,
  with the A1 amendment counted once, at its latest value. One finding is new
  since the cards: the Hosting Certification Framework paused registrations
  from 3 November 2025, seventeen days before Palantir's announcement, so its
  absence from the register is weaker evidence than it looks. **Next:** the
  author approves; FOI replies become a follow-up piece.
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

#### ES-002 "Already in your super" (M2). Brief drafted as "Already in your super"; deep dive after downloads 1 to 3 and 6

- **Drafted.** `editorial/essays/ES-002-already-in-your-super.md`, a brief of
  about 800 words, from the three funds' files, NEXTDC's substantial holders
  and the Future Fund's December 2025 report. Whether the funds' IFM money is
  in the vehicle that owns the Mamre Road land is stated as unknown (RG-005).
  **Next:** the author approves the brief; downloads #1 to #3 and #6 make the
  deep dive.
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

#### ES-008 "The OpenAI deal" (M5). Drafted as "S7's OpenAI deal is a memorandum", waiting for approval

- **Drafted.** `editorial/essays/ES-008-a-memorandum.md`, a brief of about
  840 words. The claim is provable from NEXTDC's own announcement, so it was
  drafted before downloads #4 and #5; what the exchange asked stays a gap.
  It carries a conflict disclosure, because Anthropic and OpenAI both develop
  AI models. It also says that our upstream database lists OpenAI as
  anchor tenant, unpublished, pending the author's decision (RG-014).
  **Next:** the author decides whether to approve now or wait for #4.
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

#### ES-010 "The tenant" (C3). Drafted as "The tenant was named to the market, not the council", waiting for approval

- **Drafted.** `editorial/essays/ES-010-named-to-the-market.md`, a brief of
  about 870 words, with the conflict disclosure at the top. It uses only
  the lodged report, Dexus's release, the company register and two news
  reports. The leads in the RG-012 hunt log are not used. The Premier's
  statement (download #15) stays a gap. **Next:** the author reads the Dexus
  release and the planning report directly, then decides.
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

#### ES-005 "Who gets heard" (C1). Drafted as "Eight councils objected. One reached the commission.", waiting for approval

- **Drafted.** `editorial/essays/ES-005-eight-objections.md`, a brief of
  about 880 words. The claim is narrowed to what the reports show: Apollo was
  approved under the 18 August 2026 delegation while Ryde's objection stood.
  How the commission's role was set aside stays a gap until download #19 and
  GIPA-003. **Next:** the author approves; the inquiry downloads (#17, #18)
  make a follow-up.
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
- **Gap list (2026-11-18).** No draft: the records that would carry a claim
  are not in hand. Each is named with the question it settles:
  - RG-070: the NSW ministers' diaries, January 2025 to June 2026, for the
    Premier, the Treasurer and the planning, energy and industry ministers
    (download #8, 30 files). These would show which data centre companies and
    peak bodies met them, and when.
  - RG-070: the NSW and Commonwealth lobbyist registers, for every lobbyist
    whose clients include the operators and Data Centres Australia
    (downloads #9 and #10).
  - RG-077: the same registers and diaries, for the concurrent roles of a
    former NSW Opposition Leader, referred to by role (downloads #8 to #10).
  - RG-074: the Commonwealth and NSW contract records for the consultancies
    that hold data centre consents (download #11). These would show whether
    the same firms also work for the assessors.
- **Named parties.** Lobbyists, officials and ministers all appear by role
  until legal review is arranged.

### Wave 3: five new essays from the research (2026-11-18)

Topics the research turned up along the way. Each is drafted only once its
claim rests on records the database holds; until then its gaps are listed here.

#### ES-011 "The approval after the approval" (C2). Drafted as "Approved, then doubled", waiting for approval

- **Claim.** After consent, modifications decided by delegates doubled Eastern
  Creek's power (32 MW to 63 MW; the portal's own summary says 70.2 MW), took
  Roberts Road from 48 to 72 generators and its diesel from 1.9 to 2.4 million
  litres, with 96 generators now sought, and gave Lane Cove West 116 generators.
- **Evidence in hand.** RG-045 (the five modification reports), RG-034.
- **Free records still useful.** The other modification reports on the portal;
  RG-008's environment protection licences; the Guidelines' generator limits.
- **Reader action.** A question for the Planning Secretary: will the Department
  publish each site's cumulative generator and diesel totals, modifications
  included?
- **Named parties.** None. Delegates appear by role.

#### ES-012 "Shareholder and customer" (M2). Brief, after download #2

- **Claim.** At 31 December 2025 the Future Fund held Palantir shares worth
  A$165.3 million and NVIDIA shares worth A$2.1 billion, while Commonwealth
  agencies held 29 Palantir contracts worth $68.3 million. Its CDC stake reads
  29% against CDC's own 34.55%.
- **Evidence in hand.** SRC_FF_PIR_DEC25, the AusTender ledger (RG-086), CDC's
  release.
- **Waits on.** Download #2 (the Future Fund's 2025 and 2026 reports; RG-094).
- **Reader action.** A question for the Future Fund Board of Guardians (by role)
  on how holdings are screened against the Commonwealth's own contracts. No
  impropriety is implied.

#### ES-013 "The register that stopped registering" (C3). Drafted, waiting for approval

- **Claim.** The government's top hosting certification "represents the highest
  level of assurance", yet its register gives no location for any facility, has
  paused new registrations since 3 November 2025 "until HCF reforms have been
  completed", and lacked thirteen facilities our own record also lacked. One
  certified site is leased to a firm its operator will not name.
- **Evidence in hand.** SRC_HCF_REGISTER, ST-022, RG-101, RG-103, RG-104,
  RG-106.
- **Free records still useful.** Downloads #22 and #26; Home Affairs' public
  material on the reforms.
- **Reader action.** A question for the Department of Home Affairs: when will the
  reforms finish, and will the register say where each certified facility is?

#### ES-014 "Out past the substations" (C1). Deep dive, after downloads #23 to #25. Conflict disclosure at the top

- **Claim.** Gigawatt-scale data centres are being proposed in the regions:
  Western Downs (about 2,160 MW of IT load), an off-grid campus of up to 1 GW in
  the Kimberley referred under the EPBC Act, Firmus at Wesley Vale (about 26 MW
  rising to about 52 MW, 40 backup generators), and a ten-storey building at
  Swanbank.
- **Evidence in hand.** SRC_WDDP_TPR, Firmus's own page, NVIDIA's release.
- **Waits on.** Downloads #23 (Queensland's prescribed projects), #24 (the EPBC
  referral), #25 (Ipswich's record) and Latrobe Council's Wesley Vale record
  (RG-010, RG-027, RG-051, RG-054).
- **Conflict.** It touches the Western Downs project, whose tenant is Anthropic's
  Australian subsidiary, so the disclosure goes at the top.
- **Reader action.** A question for each state's planning minister (by role) on
  how a gigawatt load in a regional area is assessed.

#### ES-015 "Who checks the consultants" (C2). Drafted as "The applicant hires the checker" (brief), waiting for approval

- **Claim, as tested by batch 8.** The applicant engages the firm that writes
  the noise, air and greenhouse evidence, and the applicant, its planner or the
  report's own author engages the firm that checks it. The Department engages
  neither.
  - Three of the six consents held by a consultancy or design practice carry
    evidence written by that same firm: Turner Road and Project Echidna (Arup)
    and Davis Road (Cundall).
  - Review documents appear on 6 of 63 projects, about one in ten (the earlier
    estimate was one in twenty). The two acoustic reviews did no remodelling.
  - One firm wrote all three greenhouse reviews. At Project Atlas, the
    report's author engaged the reviewer.
- **Evidence in hand.** RG-073 and RG-075 (resolved), the five review letters,
  35 reports read for their authors, and RG-074's applicants.
- **Why a brief.** The contract half of the claim, whether these firms also work
  for the assessors, waits on download #11 (RG-074). It becomes a follow-up when
  that lands.
- **Reader action.** A question for the Planning Secretary: will the Department
  name every technical appendix's author and require independent peer review of
  acoustic and air quality evidence?

### Follow-ups to approved essays

Under the approve-now decision, new evidence on an approved essay becomes a new
piece. A follow-up takes the next free number (ES-016 onward), opens its
standfirst with "A follow-up to ES-00n", carries the tag `follow-up`, and meets
every essay rule (five sources at least, every number cited, people by role).
The editor links it from the original in `/admin`.

| Original | Follow-up written when |
| --- | --- |
| ES-002 | Downloads #1, #3, #6 and #7 arrive: the six funds in full |
| ES-003 | A free record names one of the unnamed operators. In hand already: SYD2 and Apollo Place are AirTrunk's (RG-098), and the Macquarie Park building is operating (RG-102) |
| ES-004 | RG-043's network and regulator figures, or RG-007's tax expenditure statement |
| ES-005 | Downloads #17 to #19: the planning policy as in force, and the inquiry submissions |
| ES-006 | RG-061's other conditions, or RG-069's electoral register. The modifications go to ES-011 |
| ES-008 | Downloads #4 and #5: the exchange's compliance letter and OpenAI's own page |
| ES-009 | The FOI-002, FOI-003 and FOI-004 replies, and downloads #13, #14 and #16 |
| ES-010 | Downloads #15 (Hansard) and #23 (the prescribed-projects list) |
| ES-007 | Drafted as its own essay when downloads #8 to #11 arrive |

### The order, in short

| Wave | When | Essays |
| --- | --- | --- |
| 0 | Now | R2.0 and R2.1. The author approves ES-000 and ES-001, lodges the requests, and starts the downloads |
| 1 | Now, from evidence in hand | ES-003, ES-004, ES-006, ES-009 (all drafted) |
| 2 | As each group of downloads arrives | ES-002, ES-008, ES-010 and ES-005 are drafted as briefs from what is in hand; ES-007 and ES-002's deep dive wait on the downloads |
| 3 | Now and as downloads arrive (2026-11-18) | ES-011, ES-013 and ES-015 drafted; ES-012 after download #2; ES-014 after downloads #23 to #25 |
| 4 | As downloads and the free Commonwealth replies arrive | Follow-up pieces (ES-016 onward). Never silent edits to an approved essay |

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
