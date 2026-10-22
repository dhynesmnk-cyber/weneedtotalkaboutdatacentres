# FOI-003: what security clearance Palantir holds, from the Department of Defence

Status: **drafted**, 2026-10-22. Not lodged.

To: the Department of Defence, under the Freedom of Information Act 1982
(Cth). Lodge through the Freedom of Information page on defence.gov.au, and
check the lodgement address there before sending. It can go with FOI-002 or
on its own; separate requests are simpler to process.

Cost: no application fee; processing charges may apply (ask for a waiver
below). Decision due within 30 days, plus 30 if third parties are consulted.

## Why this request

Two sourced claims about the same regulator disagree by a year. Crikey (17
February 2026) reported that the Australian Signals Directorate granted
Palantir "a top security clearance" in November 2024. Palantir's own
announcement says it completed an IRAP assessment at the PROTECTED level on
20 November 2025, and an IRAP assessment is not a security clearance
(RG-089; security_records row 6).

The obvious request, to ASD, cannot be made: the FOI Act lists ASD as an
exempt agency, and documents that came from it are exempt whoever holds them
(SRC_FOI_ACT_1982). Defence, though, runs the security program that clears
companies to work on classified Defence contracts, and holds its own records
of that program. This request asks Defence only for what Defence itself made,
and asks for dates and levels, not for anything about individuals.

## Draft request text

> I request access under the *Freedom of Information Act 1982* to the
> following documents of the Department of Defence, for the period 1 January
> 2024 to 31 December 2025, about Palantir Technologies Australia Pty Ltd
> (ABN 48 144 948 309) and Palantir Technologies Inc.
>
> 1. Any document recording an application for, grant of, or change to
>    membership of the Defence Industry Security Program by either company,
>    showing the membership level and its date.
> 2. Any document recording a facility security clearance or
>    accreditation granted to premises of either company, showing the level
>    and date only.
> 3. Any Defence document that records a decision to accept, rely on or
>    review the Information Security Registered Assessors Program (IRAP)
>    assessment of "Palantir Platform Australia" for Defence use, with its
>    date.
>
> I do not seek any document that originated with or was received from the
> Australian Signals Directorate, any security assessment of an individual, or
> any personal information; names of individuals may be removed. An edited
> copy is acceptable.
>
> I ask that any charge be waived because giving access is in the general
> public interest: the security status of a foreign-owned supplier of
> government data platforms has been reported inconsistently, and the public
> has no other way to establish it.
>
> I would prefer the documents electronically.

## Alongside the request (not FOI)

These are questions the author can send directly; any answer goes in the
RG-089 hunt log as a statement, not a record.

- To Crikey: what record supports "a top security clearance" in November
  2024, and which agency granted it.
- To Palantir's Australian media contact: whether it held any Defence or ASD
  clearance or certification before its November 2025 IRAP announcement.

## What each item would answer

| Item | Answers | Card it would unlock |
| --- | --- | --- |
| 1 | Whether a November 2024 event was a Defence industry security membership | ST-013 *Outside the Act* |
| 2 | Whether Palantir's premises are cleared to hold classified material | the same |
| 3 | Whether Defence relies on the November 2025 IRAP assessment | the same, and RG-087 |

## When it comes back

Record the acknowledgement, decision date, documents released and each
exemption claimed in `data-pipeline/reports/hunts/RG-089.md`. A released date
and level become a `security_records` row citing the decision.
