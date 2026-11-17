# FOI-005: data centre water agreements and TCS's work inside Melbourne Water

Status: **drafted**, 2026-11-15. Not lodged.

To: Melbourne Water Corporation, under the Freedom of Information Act 1982 (Vic).
Lodge online: https://apply.melbournewater.com.au/prweb/PRAuth/app/MWForms_8816/FOI
(the form linked from
https://www.melbournewater.com.au/about/publications/legislation/freedom-information).
Contact: foi@melbournewater.com.au, Freedom of Information Officer, Melbourne
Water, PO Box 4342, Melbourne Vic 3001.

Cost: **$34.50 application fee from 1 July 2026**, as Melbourne Water publishes on
that page (read 2026-11-15). Access charges may apply; if the estimate exceeds
$70.00 Melbourne Water will ask whether to proceed and require a deposit. A
decision is due within 30 days of a valid request, unless extended under the Act.
Ask for the fee to be waived on public interest grounds; the fee is waivable,
unlike Queensland's.

Answers **RG-017** (Part 1) and **RG-080** (Part 2). Pairs with GIPA-004 (Sydney
Water), FOI-006 (Yarra Valley Water, South East Water) and RTI-001 (Unitywater).

Note on timing: Victoria entered caretaker period on 3 November 2026 for the
28 November 2026 election. Caretaker conventions govern government announcements,
not an agency's statutory FOI duty, but a decision may land after the election.

## Why this request

**Part 1 — water.** The observatory holds eleven Victorian sites, four of them in
Melbourne Water's western and north-western growth corridors: AirTrunk MEL1
(Derrimut), CDC Brooklyn, CDC Laverton (under construction), Digital Realty MEL11
(Deer Park), plus the approved South Morang project, the lodged Melton Syncline
hub and the pre-lodgement Plumpton AI Hub. Melbourne Water is the bulk water and
waterway authority for the region and the authority whose recycled-water schemes
would have to supply them. No public document says what it has agreed to supply,
or what its schemes can carry.

**Part 2 — the consultancy.** Melbourne Water appears in the observatory's
contract records as a client of **Tata Consultancy Services**, with 27 contracts.
The ten scopes that are visible are conventional IT — Citrix, SolarWinds, M365,
disaster recovery, GIS, cyber project management, network zone work, end-of-life
hardware. Two of them, **GIS** and **network zone**, could plausibly touch asset
and supply geography. RG-080 asks whether any TCS engagement touches
recycled-water supply planning, third-party water schemes or data centre service
connections. Nothing alleges wrongdoing; the question is what a consultancy
sitting inside a water authority's IT estate can see, and whether any contract
puts it near the water-supply planning that data centre applicants depend on.

## Draft application text

> I apply under the *Freedom of Information Act 1982* (Vic) for access to
> documents held by Melbourne Water.
>
> **Part 1: data centre water supply, recycled water and trade waste**
>
> 1. Any agreement, offer, servicing plan, capacity allocation or equivalent
>    instrument between Melbourne Water and a proponent, operator or owner of a
>    data centre (data storage premises) in Melbourne Water's operating area,
>    made since 1 January 2019. Site addresses are sought; commercial price terms
>    may be redacted.
> 2. Any trade waste agreement, consent or approval issued to a data centre since
>    1 January 2019, with the approved discharge volume and quality limits, and
>    any application refused or withdrawn.
> 3. Any assessment of, or advice on, a request to supply recycled water to a
>    data centre, including the Western Treatment Plant and Eastern Treatment
>    Plant recycled water schemes, any third-party or retailer scheme, and any
>    statement of the volume available, the timing, or the pipeline or planning
>    approvals needed.
> 4. Any document recording a constraint, refusal, deferral or queue affecting
>    water supply to a data centre, including where available capacity was
>    already committed.
> 5. Any document stating committed and available capacity of the recycled water
>    schemes Melbourne Water operates, and any policy ranking industrial
>    customers for allocation.
>
> **Part 2: consultancy engagements touching water supply planning**
>
> 6. For each engagement of Tata Consultancy Services (in any of its Australian
>    entities) by Melbourne Water since 1 January 2019: the statement of work or
>    scope of services, and any variation, excluding price and payment terms.
> 7. Any of those scopes, statements of work, deliverables, data-sharing
>    schedules or access schedules that concern recycled water supply planning,
>    third-party water schemes, water supply or servicing geography, or data
>    centre service connections.
> 8. Any information security or data access schedule applying to those
>    engagements that identifies which Melbourne Water systems or datasets the
>    consultant may access, including geographic information systems.
>
> I do not seek personal information about any individual. Names of officers
> below executive level, personal details in correspondence, and commercial price
> terms may be removed. An edited copy is acceptable.
>
> I ask that the application fee be waived, and any access charges be reduced or
> waived, because release is in the public interest: the water taken by data
> centres, whether recycled water is available to them, and what a consultancy
> engaged by a water authority can access, are matters of general public concern.
>
> I would prefer the documents electronically.

If Melbourne Water says the scope is too wide, split it: **Part 2 items 6 and 7**
alone is a small, named request, and it is the one RG-080 needs. Part 1 can be
re-lodged narrowed to the three western sites (Derrimut, Brooklyn, Laverton).

## What each item would answer

| Item | Answers | Question |
| --- | --- | --- |
| 1, 2 | What Melbourne Water agreed to supply and to permit, site by site | RG-017 |
| 3, 4, 5 | Whether recycled water is available to Victorian data centres, and what constrains it | RG-017, RG-068 |
| 6, 7 | Whether any TCS scope touches water-supply planning rather than conventional IT | RG-080 |
| 8 | What systems and datasets the engagement can reach | RG-080, RG-068 |

## When it comes back

Record the acknowledgement, decision date, documents released and each exemption
claimed in `data-pipeline/reports/hunts/RG-017.md` and `RG-080.md`. Agreed volumes
become `water_profile` facts; a scope becomes a `consultant_role` row against the
existing `gov_contracts` record, citing the released statement of work. Only
company-level facts are recorded; officer names below executive level are not
committed. A refusal is recorded with its reasons and is not worked around.
