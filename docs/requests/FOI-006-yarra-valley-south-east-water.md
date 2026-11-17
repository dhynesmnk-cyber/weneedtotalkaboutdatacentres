# FOI-006: data centre water and trade waste agreements, from Yarra Valley Water and South East Water

Status: **drafted**, 2026-11-15. Not lodged.

To: **two agencies, one text, two applications** under the Freedom of Information
Act 1982 (Vic):

- **Yarra Valley Water** — https://www.yvw.com.au/about-us/organisation-overview/freedom-information-foi,
  foi@yvw.com.au. Serves the northern and eastern metropolitan area, including
  **South Morang**.
- **South East Water** — https://southeastwater.com.au/about-us/corporate-information/freedom-of-information/,
  which states a request must be in writing to the agency holding the documents.
  Serves the south-east, including the **Derrimut / Deer Park / Brooklyn**
  industrial belt's retail water and trade waste.

Cost: each agency sets and publishes its own application fee, indexed each
1 July. Melbourne Water publishes **$34.50 from 1 July 2026**; use the fee on each
agency's own page at the time of lodgement rather than assuming it is the same.
A decision is due within 30 days of a valid request. Ask for the fee to be waived
on public interest grounds.

Answers **RG-017**. Pairs with GIPA-004 (Sydney Water), FOI-005 (Melbourne Water)
and RTI-001 (Unitywater). Melbourne Water is the bulk authority; these two are the
retailers that actually issue the connection and the trade waste consent, which is
why the request cannot stop at Melbourne Water.

Note on timing: Victoria entered caretaker period on 3 November 2026 for the
28 November 2026 election. That governs announcements, not the statutory FOI duty.

## Why this request

A data centre's cooling water is a retail connection and a trade waste discharge
before it is a bulk supply question. The observatory's Victorian rows record
capacity, status and planning history; **none records an agreed water volume or a
permitted discharge**, because no operator or agency publishes one. The
NSW work has shown what that gap hides: all 20 archived NSW consents were read for
RG-062 and **none requires recycled water** — the consents impose a duty to
prioritise non-potable supply "where available", and whether it is available is a
utility fact. Victoria has no equivalent consent condition set at all, so the
utility record is the only place the answer can come from.

The sites to name, so the request is not a fishing expedition:

| Agency | Sites in its area |
| --- | --- |
| Yarra Valley Water | South Morang data centre (approved); NEXTDC M1/M2/M3 and Equinix ME1/ME2/ME4 as applicable to their addresses |
| South East Water | AirTrunk MEL1 (Derrimut), Digital Realty MEL11 (Deer Park), CDC Brooklyn, CDC Laverton (under construction), NEXTDC M4 (Fishermans Bend) |

Where an address sits on a boundary, ask the agency to say so and to name the
agency that holds the document, rather than refusing the item.

## Draft application text

Send the same text to each agency, changing only the addressee and the site list.

> I apply under the *Freedom of Information Act 1982* (Vic) for access to
> documents held by [Yarra Valley Water / South East Water].
>
> 1. Any water supply agreement, servicing agreement, capacity allocation,
>    letter of offer or acceptance, or equivalent instrument between the
>    corporation and a proponent, operator or owner of a data centre (data
>    storage premises) in its service area, made since 1 January 2019. Site
>    addresses are sought; commercial price terms may be redacted.
> 2. Any trade waste agreement, consent, permit or approval issued to a data
>    centre since 1 January 2019, with the approved discharge volume and quality
>    limits, and any application for one that was refused or withdrawn.
> 3. A list, or a document from which one can be produced, of data centre
>    connections the corporation has agreed to serve since 1 January 2019, with
>    the site, the agreed annual or daily volume, and whether the supply is
>    potable, recycled or both.
> 4. Any assessment of, or advice on, supplying recycled water to a data centre,
>    including from a third-party or retailer scheme, and any statement of the
>    volume available, the timing, or the approvals needed.
> 5. Any document recording a constraint, refusal, deferral or queue affecting
>    supply to a data centre, including where available capacity was already
>    committed, and any correspondence with Melbourne Water about such a
>    constraint.
>
> The sites I am aware of in your area are: [site list from the table above].
> Where a site is served by another corporation, please say which, rather than
> refusing the item.
>
> I do not seek personal information about any individual. Names of officers
> below executive level, personal details in correspondence, and commercial price
> terms may be removed. An edited copy is acceptable.
>
> I ask that the application fee be waived, and any access charges be reduced or
> waived, because release is in the public interest: the volume of drinking
> water taken by data centres for cooling, and whether recycled water is
> available to them, are matters of general public concern.
>
> I would prefer the documents electronically.

## What each item would answer

| Item | Answers | Question |
| --- | --- | --- |
| 1, 3 | The agreed volume per site — the first water figures for any Victorian row | RG-017 |
| 2 | Whether cooling discharge is permitted, and at what volume and quality | RG-017 |
| 4 | Whether recycled water is on offer to a Victorian data centre at all | RG-017, RG-068 |
| 5 | Where the constraint sits: retailer, bulk authority, or scheme capacity | RG-017 |

## When it comes back

Record the acknowledgement, decision date, documents released and each exemption
claimed in `data-pipeline/reports/hunts/RG-017.md`, separately for each agency —
one may release what the other refuses, and that difference is itself a finding.
Agreed volumes become `water_profile` facts citing the released instrument, with
the corporation as source. A site absent from a released list is recorded as
absent, not as unconnected.
