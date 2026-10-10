# COUNCIL_CANDIDATES.md

## Status: UNAPPROVED — PENDING HUMAN SIGN-OFF

Nothing in this file authorises anything. These are candidate local government
areas for the approved council list in docs/SPEC.md, drafted under the
`researcher` role in docs/SUBAGENTS.md, which proposes and never approves.

The hard rule in CLAUDE.md permits council ingestion only for councils approved
in docs/SPEC.md. That list is currently empty. **No ingestion may run against any
council below until a human moves it across.**

### How to approve
Strike the rows you do not want. For each row you keep, add it to the approved
table in docs/SPEC.md with the date and your name, and add a matching row to the
`council_watchlist` table. Approval is per council, not per batch.

### Drafting rules applied
- Every candidate names a council-level source. No council was added because it
  seemed likely.
- Figures are quoted as the source states them, not converted, rounded or
  combined.
- Where a source does not give a figure, it is left out rather than estimated.
- All sources retrieved 2026-09-18. Retrieval dates belong in `sources` on
  ingestion.

---

## Candidates

### New South Wales

**Penrith City Council**
Mamre Road precinct, Kemps Creek. Microsoft facility at 769 Mamre Road under
SSD 10101987, with a voluntary planning agreement executed 7 June 2023. A
separate 52-hectare, 1.2 GW campus proposal (SSD-92743706) is before the NSW
government; Penrith City Council objected to it.
Basis: named sites, council is a party to both.
- https://yoursaypenrith.com.au/vpa-microsoft-datacenter
- https://ia.acs.org.au/article/2026/concern-over-australia-s-most-power-hungry-data-centre.html

**Blacktown City Council**
Eastern Creek. NEXTDC S7, a planned 550 MW+ hyperscale campus on a 258,000 sqm
site. Blacktown City Council is named as the planning authority for
SSD-113934740, council reference MC-26-00005.
Basis: named site, council is the planning authority.
- https://www.planningportal.nsw.gov.au/major-projects/projects/nextdc-s7-data-centre-eastern-creek
- https://www.theurbandeveloper.com/articles/eastern-creek-data-centre-550mw-openai-nextdc

**City of Ryde**
Macquarie Park Innovation District. Council's submission to the NSW
parliamentary inquiry into data centres records five facilities operating in the
precinct and a further seven State Significant Development proposals under
assessment. Council states that concentration has outpaced infrastructure
delivery and planning controls.
Basis: cluster of named sites, council has made a formal position statement.
- https://files.parliament.nsw.gov.au/fileapi/ParlFiles/GetArtifact/0041%20City%20of%20Ryde.pdf
- https://w.media/sydney-council-warns-data-centre-clustering-is-straining-infrastructure/

### Victoria

**Latrobe City Council**
Morwell, on a 123-hectare site near the former Hazelwood Power Station. Keppel
Ltd proposal, reported at 720 MW and $10 billion. Council has published its own
statement and expects to receive a planning application.
Basis: named site, council has published on it directly.
- https://www.latrobe.vic.gov.au/news-and-media/10_billion_data_centre_proposed_for_Morwell_0
- https://www.abc.net.au/news/2026-01-22/keppel-data-centre-latrobe-valley/106123748

**Wyndham City Council**
Melbourne's west. Council is reviewing the expansion of data centres across the
municipality and is part of a seven-council push for tougher controls.
Basis: council activity, not yet a single named site in the sources retrieved.
- https://www.werribeenews.com.au/news/wyndhams-future-data-centre-boom-sparks-push-for-greater-oversight
- https://www.theindiansun.com.au/2026/08/20/melbournes-west-unites-to-demand-tougher-controls-on-data-centres/

**Melton City Council**
Part of the same seven-council push. The group estimates at least eight large
facilities operating or planned across their combined areas.
Basis: council activity. Which of the eight fall inside Melton is not broken out
in the source — a gap to resolve before ingestion, not to guess at.
- https://www.theindiansun.com.au/2026/08/20/melbournes-west-unites-to-demand-tougher-controls-on-data-centres/

**Moorabool Shire Council**
Part of the same seven-council push.
Basis: council activity. Same unresolved breakdown as Melton.
- https://www.theindiansun.com.au/2026/08/20/melbournes-west-unites-to-demand-tougher-controls-on-data-centres/

**Hume City Council**
Council voted on a data centre energy and water management position, having
warned of a volume of data centre water applications.
Basis: council activity and a formal council decision.
- https://www.abc.net.au/news/2025-08-26/hume-council-votes-on-data-centres-energy-water-management-plan/105694556

### Queensland

**Western Downs Regional Council**
A 725-hectare site near Dalby. Zerra DC proposal reported at $31.9 billion, with
Anthropic signed as a user from 2027. The proposal is before the council's
planning team. A Queensland parliament e-petition against it had passed 1,300
signatures at time of reporting.
Basis: named site, council is the assessing authority, documented community
opposition through a formal channel.
- https://www.abc.net.au/news/2026-09-16/queensland-data-centre-anthropic-dalby/107160640
- https://www.abc.net.au/news/2026-09-14/western-downs-digital-park-data-centre-energy-queensland/107115082

**Ipswich City Council**
Swanbank industrial precinct. Proposal for a ten-storey data centre with a gross
floor area of approximately 82,576 sqm.
Basis: named site within the LGA.
- https://yourneighbourhood.com.au/large-data-centre-swanbank-ipswich/

### South Australia

**Goyder Regional Council**
Bundey, north-east of Adelaide. IREN proposal requiring up to 800 MW, targeting
operation in 2028. The council's mayor is quoted on the proposal's local
employment claims. Local division over water demand is reported.
Basis: named site, council leadership on record.
- https://www.abc.net.au/news/2026-06-19/proposed-data-centre-in-south-australia-dividing-locals/106810776

### Western Australia

**City of Gosnells**
Maddington industrial area, about 20 km south-east of central Perth. CDC campus,
$415 million first stage, up to 200 MW at completion. The City of Gosnells
recommended approval; the application was determined by a Development Assessment
Panel in September 2025.
Basis: named site, council made a formal recommendation.
- https://developedproperty.com.au/news/cdc-data-centre-approved/
- https://www.abc.net.au/news/2026-08-13/councils-grapple-with-data-centre-applications/107029724

---

## Known gaps in this draft

Recorded rather than filled, per the hard rule against inferring values.

- **No candidates for NT or Tasmania.** Not a finding that none exist — the
  searches behind this draft did not surface council-level sources for either.
  Reason code if carried into data: `unknown`.
- **ACT is unresolved.** The ACT's local government arrangements differ from the
  states, so it is unclear whether a council-level watchlist entry is even the
  right shape there. Needs a source on who the planning authority is before any
  entry is drafted.
- **Melton and Moorabool are thinly sourced.** Both qualify through a joint
  council position rather than a site identified inside their boundaries. The
  eight facilities cited are not broken down by LGA in the source. Either find a
  per-LGA source or approve them knowing the basis is weaker than the rest.
- **Two qualification bases are mixed here.** Some councils qualify because a
  named site sits in the LGA; others because the council has taken a public
  position. If the approved list is meant to mean only the first, strike the
  second group: Wyndham, Melton, Moorabool, Hume.
- **No capacity figure is independently verified.** Every MW and dollar figure
  above is as reported by the cited source. None has been cross-checked against
  a primary planning document, and none should be loaded into `sites` without
  one.

---

## Proposed for approval, ranked by what the records would close

Drafted 2026-10-09 under the `researcher` role. It proposes and approves
nothing: the approved table in docs/SPEC.md is unchanged, and stays empty until
a human fills it.

### Why these, in this order
The ranking is by how many of the public record's "Not yet researched" values
a council's development application records could plausibly answer, from
`data-pipeline/reports/gap_worklist.csv`. Only sites without an NSW State
Significant Development record are counted, because the planning portal
already holds those. "Plausible" means fields a DA and its documents can state:
address, suburb, proponent, coordinates (through the address), capacity, campus
and floor area, capital cost, jobs, cooling, water use and target completion.
HCF certification, live capacity, rack density, grid connection and opening
date are left out. These are ceilings, not promises: a record may not exist
online, may predate the tracker, or may show the site was assessed by the state.

| Rank | Council | Sites it would serve | Gaps on them | DA-plausible | Tracker | robots.txt (checked 2026-10-09) |
|---:|---|---|---:|---:|---|---|
| 1 | Blacktown City Council (NSW) | AirTrunk SYD1, AirTrunk SYD3, CDC Eastern Creek, DCI SYD-01 | 77 | 60 | blacktown-web.t1cloud.com (eTrack) | `Disallow: /` |
| 2 | Penrith City Council (NSW) | CDC Kemps Creek, Digital Realty Erskine Park, STACK 78 Lockwood Road, Stockland Fife Kemps Creek | 77 | 58 | datracker.penrithcity.nsw.gov.au | none published (404) |
| 3 | City of Ryde (NSW) | Macquarie IC3, Stockland 'Project A', Stockland Macquarie Park Stage 1 | 57 | 42 | ryde-web.t1cloud.com (eTrack) | `Disallow: /` |
| 4 | Melton City Council (VIC) | Syncline Energy Melton hub, Victorian AI Hub (Plumpton) | 36 | 26 | Online Planning Register on melton.vic.gov.au | does not disallow it |
| 5 | Ipswich City Council (QLD) | Ten-storey data centre outside Brisbane | 21 | 15 | developmenti.ipswich.qld.gov.au | none published (404) |
| 6 | Wyndham City Council (VIC) | CDC Laverton | 18 | 13 | not found | — |
| 7 | Western Downs Regional Council (QLD) | Western Downs Digital Park | 12 | 6 | not checked | — |

Latrobe, Moorabool, Hume, Goyder and Gosnells would close nothing today: no
site in the record sits in them without a state planning record.

### Recommendation
Approve **Blacktown, Penrith and Ryde** first: NSW, named sites in each, about
160 plausible values between them, and the qualification basis is the stronger
one (a named site in the LGA, not a council position).

Hold Melton, Ipswich, Wyndham and Western Downs. Each serves one or two sites,
and for the Victorian ones the state's Development Facilitation Program or the
ministerial permits register may be the record of decision rather than the
council (batch S6 in the plan looks there first).

### What approval would and would not permit
- **Manual retrieval only, this round.** No scraper and no scheduled job. A
  person, or an agent at a person's direction, finds the record for a named
  site, downloads its documents, and archives each under
  `data-pipeline/data/raw/councils/<council>/` with a `.meta.json` manifest
  (url, retrieved date, SHA-256), as the portal archive does.
- **Blacktown and Ryde disallow automated access** to their eTrack hosts in
  robots.txt. Their documents must be downloaded by a person in a browser, not
  fetched by a script, even after approval. Penrith and Ipswich publish no
  robots.txt; fetch politely (one request at a time, a pause between) and stop
  if asked.
- **Terms of use were not checked.** Read each tracker's terms before the first
  retrieval and record the outcome here.
- **Council is still never derived.** A DA names the council that determined
  it; that document, not the site's address, is what the council field cites.

### To approve (for the approver to complete)
For each council kept, add a row to the approved table in docs/SPEC.md:

```
| Blacktown City Council | NSW | YYYY-MM-DD | <your name> |
| Penrith City Council   | NSW | YYYY-MM-DD | <your name> |
| City of Ryde           | NSW | YYYY-MM-DD | <your name> |
```

and the matching `council_watchlist` rows, applied by hand (no import writes
to this table). The names follow the approved spellings in `facts.lga_aliases`:

```sql
insert into facts.council_watchlist (lga, state, approved_by, approved_at, notes) values
  ('Blacktown City Council', 'NSW', '<your name>', '<YYYY-MM-DD>',
   'Manual retrieval only; eTrack disallows automated access (robots.txt).'),
  ('Penrith City Council',   'NSW', '<your name>', '<YYYY-MM-DD>',
   'Manual retrieval only, one request at a time.'),
  ('City of Ryde',           'NSW', '<your name>', '<YYYY-MM-DD>',
   'Manual retrieval only; eTrack disallows automated access (robots.txt).');
```
