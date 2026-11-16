# GIPA-004: data centre water agreements, trade waste approvals and recycled-water capacity, from Sydney Water

Status: **drafted**, 2026-11-15. Not lodged.

To: Sydney Water Corporation, under the Government Information (Public Access)
Act 2009 (NSW). Sydney Water is a State owned corporation and therefore an
agency under the Act.
Lodge: the formal access application form on
https://www.sydneywater.com.au/about/who-we-are/access-to-information.html
(form: https://www.sydneywater.com.au/content/dam/sydneywater/documents/access-application-form.pdf),
by email to GIPA@sydneywater.com.au or by post to the GIPA Officer.

Cost: $30 application fee, which covers the first hour of processing; further
processing at $30 an hour, and an advance processing fee may be asked for. Ask
for the 50% reduction on the ground of special benefit to the public (below).
A decision is due within 20 working days.

Pairs with FOI-005 (Melbourne Water), FOI-006 (Yarra Valley Water and South East
Water) and RTI-001 (Unitywater). Together they answer **RG-017**; this one also
feeds **RG-062** (no consent requires recycled water) and **RG-068** (the
unverified claim that recycled water already supplies 55% of AirTrunk's use).

## Why this request

The NSW planning record shows what a data centre **asks** for. It does not show
what the water utility **agreed to**, and that is where the constraint sits.

1. **NEXTDC S7 (SSD-113934740), Eastern Creek.** Its scoping report, archived,
   states at p36: average daily water demand at about 70% load of **5.44 ML/day**,
   peak at full site maturity **up to 7.79 ML/day**; that NEXTDC "has commenced
   engagement with Sydney Water regarding **interim potable water supply** for
   Stage 1, as well as potential recycled water opportunities, including supply
   from the **St Marys Advanced Water Treatment Plant**"; and that investigations
   are underway with coNEXA to connect to "the recycled water main associated
   with the S4 development". At p19 and p27 a recycled water solution is
   "actively being explored" and "being progressed". Nothing public says whether
   Sydney Water can supply it, at what volume, or from when.
2. **The consents do not require it.** All 20 archived consent instruments were
   read for RG-062: none requires recycled water. Glendenning B22, Apollo B24/B25
   and Pluto B21/B22 impose a duty to review and prioritise non-potable supply
   "where available". Whether it is available is a Sydney Water fact, not a
   planning fact.
3. **The corridor is concentrated.** Seventeen of the observatory's NSW sites are
   in the Eastern Creek – Kemps Creek – Horsley Park – Glendenning – Marsden Park
   corridor, all served from the same western Sydney system. Cumulative demand
   is the question no single EIS answers.

## Draft application text

> I apply under the *Government Information (Public Access) Act 2009* for access
> to the following information held by Sydney Water.
>
> **Part 1: agreements and approvals for data centres**
>
> 1. Any water supply agreement, servicing agreement, capacity allocation,
>    letters of offer or acceptance, or equivalent instrument between Sydney
>    Water and a proponent, operator or owner of a data centre (data storage
>    premises) in the Sydney Water operating area, made since 1 January 2019.
>    Where the document names a site, the site address is sought; the commercial
>    price terms may be redacted.
> 2. Any trade waste agreement, permit, consent or approval issued to a data
>    centre since 1 January 2019, including the approved discharge volume and
>    quality limits, and any application for one that was refused or withdrawn.
> 3. A list, or a document from which one can be produced, of the data centre
>    connections Sydney Water has agreed to serve since 1 January 2019, with the
>    site, the agreed annual or daily volume, and whether the supply is potable,
>    recycled or both.
>
> **Part 2: NEXTDC S7 and the western Sydney recycled water scheme**
>
> 4. Correspondence and file notes between Sydney Water and NEXTDC, its
>    consultants, or coNEXA concerning water supply to the proposed S7 data
>    centre at Eastern Creek (SSD-113934740), including any advice on interim
>    potable supply for Stage 1 and any advice on recycled water supply from the
>    St Marys Advanced Water Treatment Plant.
> 5. Any assessment of whether recycled water can be supplied to S7 and to the
>    NEXTDC S4 development at Horsley Park, including capacity, timing, pipeline
>    route or planning approval constraints, and any statement of the volume
>    available.
>
> **Part 3: capacity and constraints**
>
> 6. Any document stating the current committed and available capacity of the
>    recycled water schemes serving western Sydney, including St Marys Advanced
>    Water Treatment Plant and the Replacement Flows / Hawkesbury-Nepean
>    arrangements, and any allocation policy that ranks industrial customers.
> 7. Any document recording a constraint, refusal, deferral or queue affecting
>    supply to a data centre, including where a request exceeded available
>    capacity or where a scheme's capacity was already committed.
>
> I do not seek personal information about any individual. Names of officers
> below Senior Executive Service level, personal details in correspondence, and
> commercial price terms may be removed. An edited copy is acceptable.
>
> I ask for a 50% reduction in processing charges because the information is of
> special benefit to the public generally: data centres are the subject of a NSW
> Legislative Council inquiry, and the water they take, and whether recycled
> water is available to them, are matters of public interest in a drought-prone
> system.
>
> I would prefer the information electronically.

If Sydney Water says the scope is too wide, keep **Part 2** and lodge it alone:
it is one project, named, and it is the sharpest question. Part 3 is the one
that would generalise the answer.

## What each item would answer

| Item | Answers | Question |
| --- | --- | --- |
| 1, 3 | What the utility actually agreed to supply, and to whom | RG-017 |
| 2 | Whether cooling discharge is permitted, and at what volume and quality | RG-017 |
| 4, 5 | Whether S7's recycled-water strategy is deliverable, and what "interim potable" means in practice | RG-017, RG-073 |
| 6, 7 | Whether "where available" in the consents means available at all | RG-062, RG-068 |

## When it comes back

Record the acknowledgement, the decision date, what was released and every
public interest consideration against disclosure in
`data-pipeline/reports/hunts/RG-017.md`. Agreed volumes become `site_water`
facts citing the released instrument, with the utility as source and the
document's date as `as_of_date`; a refusal or a capacity constraint becomes a
`regulatory_events` row. Nothing is inferred from a released list: a site absent
from it is recorded as absent, not as unconnected.
