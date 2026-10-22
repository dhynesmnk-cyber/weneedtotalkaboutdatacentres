# FOI-002: where Defence's Palantir systems run, from the Department of Defence

Status: **drafted**, 2026-10-22. Not lodged.

To: the Department of Defence, under the Freedom of Information Act 1982
(Cth). Lodge through the Freedom of Information page on defence.gov.au, and
check the lodgement address there before sending.

Cost: no application fee. Processing charges may apply; ask for them to be
waived in the public interest (below). Defence must acknowledge within 14 days
and decide within 30, plus 30 more if it consults third parties such as
Palantir.

## Why this request

Palantir says its Australian platform is "hosted in Australian Amazon Web
Services (AWS) regions" (SRC_PALANTIR_IRAP_NOV25). That is a statement about
a platform, not about any contract. None of the 29 Commonwealth contract
notices with Palantir says where its software runs, and 11 of them name the
US parent company rather than its Australian subsidiary (RG-086, RG-087).

The agency with the most sensitive Palantir contracts, the Australian Signals
Directorate, is outside the FOI Act altogether: Schedule 2 lists it as an
exempt agency, and section 7(2A) makes any document that came from it exempt
in any agency's hands (SRC_FOI_ACT_1982). Defence is not exempt, except for
documents on operational intelligence and special access programs. So this
request goes to Defence, about Defence's own three current contracts, and asks
only where the software and data sit, not what the software does.

Expect claims under section 33 (security) and section 47 or 47G (commercial
information). Ask for an edited copy (section 22) rather than a refusal; a
decision that says which exemption covers which page is itself a record.

## Draft request text

> I request access under the *Freedom of Information Act 1982* to the
> following documents of the Department of Defence about these contracts with
> Palantir Technologies Australia Pty Ltd (ABN 48 144 948 309), as published
> on AusTender: CN4104368 (Data Services), CN4115523 (Software) and CN4218984
> (ICT System Platform), including amendments.
>
> 1. The parts of each contract, statement of requirement or schedule that
>    state where the software is hosted and where Commonwealth data is stored
>    or processed: the country, and whether on Defence premises, in a
>    commercial cloud (and if so which provider and region), or elsewhere.
> 2. Any clause or schedule in those contracts about data sovereignty, data
>    residency, access to Commonwealth data from outside Australia, or access
>    by the supplier's related companies or personnel outside Australia.
> 3. For any system delivered under those contracts, the page or pages of its
>    security authorisation that record the hosting location and the
>    jurisdiction of the data, and the date of the authorisation.
>
> I do not seek any description of what the software is used for, any
> operational or intelligence information, or any document that originated
> with or was received from the Australian Signals Directorate. I do not seek
> personal information; names of officers below Senior Executive Service level
> and of supplier staff may be removed. An edited copy is acceptable.
>
> I ask that any charge be waived because giving access is in the general
> public interest: the Prime Minister has announced national standards for
> where AI data centres are built, and whether government data held by a
> foreign-owned supplier stays in Australia is a matter of public debate.
>
> I would prefer the documents electronically.

## What each item would answer

| Item | Answers | Card it would unlock |
| --- | --- | --- |
| 1 | Where Defence's Palantir systems and data physically sit | ST-013 *Outside the Act*, and the site register (RG-087 asks to map any hosting facility to it) |
| 2 | Whether data residency is a contract term at all | the same |
| 3 | Whether the hosting location was checked when the system was approved | the same |

## When it comes back

Record the acknowledgement, decision date, documents released and each
exemption claimed in `data-pipeline/reports/hunts/RG-087.md`. A hosting
location becomes a `security_records` note citing the decision; a named
facility is matched to `sites` only by a human.
