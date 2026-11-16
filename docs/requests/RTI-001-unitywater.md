# RTI-001: data centre water and trade waste agreements, from Unitywater

Status: **drafted**, 2026-11-15. Not lodged.

To: Unitywater, under the Right to Information Act 2009 (Qld).
Lodge: the process and form on
https://www.unitywater.com/about-us/publications-and-reports/right-to-information.
Unitywater's own page states the application fee; the Queensland Government's
fees page (https://www.rti.qld.gov.au/fees-and-charges) states the RTI application
fee as **$59.60 as at 1 July 2026**, and that **this fee cannot be waived**. Both
read 2026-11-15.

Cost: $59.60, not waivable. Processing and access charges are additional above the
threshold; check the live schedule before paying. This is the most expensive of
the four water requests and the one with the least to gain, so it is ranked last
(see below).

Answers **RG-017**. Pairs with GIPA-004 (Sydney Water), FOI-005 (Melbourne Water)
and FOI-006 (Yarra Valley Water, South East Water).

## Why this request, and why it is ranked last

Unitywater serves the Moreton Bay and Sunshine Coast regions, not the Brisbane
CBD. The observatory's three built Queensland rows are **NEXTDC B1 (Brisbane
CBD)**, **NEXTDC B2 (Fortitude Valley)** and **Polaris (Springfield Central)**.
None is recorded as being in Unitywater's area, and the observatory holds no LGA
or water-retailer field for any of them, so **the correct retailer for each must
be confirmed before anything is lodged** — that is a five-minute check on each
agency's "our area" map, and it is the first thing to do with this draft.

It is still worth drafting, for two reasons: the Western Downs Digital Park and
the reported Ipswich project show Queensland's growth is moving to greenfield
corridors where a utility's capacity is the binding constraint; and a Queensland
answer, even a short one, establishes whether a Queensland utility will release
data centre connection volumes at all. That determines whether the NSW and
Victorian pattern repeats.

**The same text works for any Queensland water agency under the same Act** — only
the addressee and the site list change. Lodging it with the agency that actually
serves Brisbane and Fortitude Valley, and the one that serves Springfield Central,
would answer more than Unitywater would. Confirm both from their own service-area
maps first; do not assume.

## Draft application text

> I apply under the *Right to Information Act 2009* (Qld) for access to documents
> held by [the Queensland water agency that serves the sites named below].
>
> 1. Any water supply agreement, servicing agreement, capacity allocation, letter
>    of offer or acceptance, or equivalent instrument between the agency and a
>    proponent, operator or owner of a data centre (data storage premises) in its
>    service area, made since 1 January 2019. Site addresses are sought;
>    commercial price terms may be redacted.
> 2. Any trade waste approval, permit or consent issued to a data centre since
>    1 January 2019, with the approved discharge volume and quality limits, and
>    any application refused or withdrawn.
> 3. A list, or a document from which one can be produced, of data centre
>    connections the agency has agreed to serve since 1 January 2019, with the
>    site, the agreed annual or daily volume, and whether the supply is potable,
>    recycled or both.
> 4. Any assessment of, or advice on, supplying recycled water to a data centre,
>    including from a third-party scheme, and any statement of the volume
>    available, the timing, or the approvals needed.
> 5. Any document recording a constraint, refusal, deferral or queue affecting
>    supply to a data centre, including where available capacity was already
>    committed.
>
> Where a site I have named is served by another agency, please say which, and
> transfer the item under the Act rather than refusing it.
>
> I do not seek personal information about any individual. Names of officers
> below executive level, personal details in correspondence, and commercial price
> terms may be removed. An edited copy is acceptable.
>
> I would prefer the documents electronically.

The RTI application fee cannot be waived, so no waiver request is made. Do not ask
for a reduction that the Act does not allow; it delays a valid application.

## What each item would answer

| Item | Answers | Question |
| --- | --- | --- |
| 1, 3 | Whether a Queensland utility will state an agreed data centre volume | RG-017 |
| 2 | Whether cooling discharge is permitted, and on what limits | RG-017 |
| 4, 5 | Whether recycled water and spare capacity exist in a growth corridor | RG-017 |

## Ranked against the other three water requests

| Order | Request | Fee | Why this order |
| --- | --- | --- | --- |
| 1 | GIPA-004 Sydney Water | $30, 50% reduction available | 17 NSW sites in one corridor, and a named project (S7) with stated demand of 5.44–7.79 ML/day |
| 2 | FOI-005 Melbourne Water | $34.50, waivable | Answers two questions at once (RG-017 and RG-080) |
| 3 | FOI-006 Yarra Valley Water and South East Water | per agency, waivable | The retail connection and trade waste consent the bulk authority does not hold |
| 4 | RTI-001 Unitywater | $59.60, **not waivable** | No observatory site confirmed in its area; confirm the right retailer and redirect first |

## When it comes back

Record the acknowledgement, decision date, documents released and each ground of
refusal in `data-pipeline/reports/hunts/RG-017.md`, noting which Queensland agency
answered. Agreed volumes become `water_profile` facts citing the released
instrument. If the answer is that no data centre connection exists in the area,
that is a finding and is recorded as one.
