# Paid searches, ranked

Status: **ranked, deferred by the author**, 2026-11-15 — *"no budget for now but I'll do it
later, work around it for now"*. **8 searches, $157**, unchanged in rank and price. The author
will fund them later; nothing here is cancelled. Rank 9 (Project Garden 1, RG-055) was withdrawn
on 2026-11-15: RG-055 was resolved on 2026-10-22 from ASIC's free Company Dataset, so paying for
it would buy nothing.

**The free workaround has been run, and it is exhausted for ownership.** See the two tables
below: what the free records already give for every one of the eight, and the three land-ownership
statements found in the archived EISs on 2026-11-15 that a paid title search would otherwise have
been needed for.

Free records answered what they could in research batch 1. ASIC's Company
Dataset gives every applicant company's registration date and former names,
and two title searches the applicants filed name the landowners. What they
cannot show is who owns a company, and two titles were not filed in a readable
form. These searches would fill that, ranked by what each unlocks for the
essays.

Prices are ASIC's online fees ($10 current extract, $20 current and historical)
and the NSW LRS fee ($17.00 excluding GST; brokers charge more). Buy the
**current and historical** extract: it shows former officeholders and
shareholders, which is where a change of hands shows up.

| Rank | Search | ACN or title | Cost | Answers | Unlocks |
| --- | --- | --- | --- | --- | --- |
| 1 | ASIC current and historical extract: **AirTrunk SYD4 Pty Ltd** (formerly KNBDC SYD4) | 687 904 963 | $20 | RG-021, RG-036 | Who owns the company behind Australia's first gigawatt campus, and since when. Card ST-004 |
| 2 | ASIC current and historical extract: **CKTSME Management Pty Ltd** (formerly EMKC Cubed Management) | 650 102 640 | $20 | RG-064, RG-081 | Who stands behind the holder of two consents, including the largest back-up generation in the sample. Card ST-003 |
| 3 | ASIC current and historical extract: **WDDP Pty Ltd** | 700 788 058 | $20 | RG-052 | Who owns the proponent of Australia's largest proposal, registered 17 days before its report. Card ST-006 |
| 4 | NSW title search: **Lot 2 DP 1137162**, Glendenning Road | Lot 2 DP 1137162 | $17 | RG-037 | Who owns the land under a 235 MW consent held by a consultancy |
| 5 | ASIC current and historical extract: **Amazon Australia Company Pty Ltd** | 663 812 468 | $20 | RG-057 | Which Amazon business holds the Davis Road land. Card ST-005 |
| 6 | ASIC current and historical extract: **Zerra WDDP Manager Australia Pty Ltd** (formerly AGP DC Manager Australia) | 684 250 584 | $20 | RG-050 | Who AGP is, and where it sits |
| 7 | ASIC current and historical extract: **NineZero DC Sub TC I Pty Ltd** | 607 631 845 | $20 | RG-059 | Who stands behind DCI's two consents |
| 8 | ASIC current and historical extract: **KNBDC AU Development Pty Ltd** | 687 116 098 | $20 | RG-036 | The development company above the AirTrunk SYD4 stack |

Ranks 1 to 3 cost $60 and answer the three biggest open questions. All eight
cost **$157** (seven ASIC extracts at $20 and one title search at $17). The GIPA
application (GIPA-001, $30) is separate and recommended alongside rank 1.

**What these searches cannot do.** They give entities, officeholders, share
parcels and charges — not facility addresses, statuses or capacities. They do
**not** unblock RG-101's five held HCF facilities (Cloud Carrier DB1, DigiCo BNE2,
ADL1, SYD1, Vocus TransACT House Dickson): every route to a primary document for
those five is refused, and the cheapest way through is a person reading three
DigiCo PDFs in a browser, not a paid extract. See
`data-pipeline/reports/hunts/RG-101.md`.

**Withdrawn: rank 9, Project Garden 1 Pty Ltd (684 182 929), $20, RG-055.**
RG-055 asked whether fresh SPV incorporation immediately before lodgement is the
general pattern. It was answered on 2026-10-22 from ASIC's Company Dataset
(`SRC_ASIC_COMPANIES_202610`), which is free and gave registration dates for the
21 determined consents whose applicant is a company. The pattern did not hold.
Buying this extract would not add to that answer.

## What the free records already give (checked 2026-11-15)

ASIC's Company Dataset (`SRC_ASIC_COMPANIES_202610`, archived at
`data-pipeline/data/raw/asic/company_dataset_202610_extract.csv`) covers **all eight** targets.
It gives registration date, every former name with the date the current name took effect, status,
class and ABN. It does **not** give shareholders, officeholders or charges — which is the whole
reason for the paid extract.

| Rank | Company | Registered | Name history the free dataset gives | Still needs the paid extract |
| --- | --- | --- | --- | --- |
| 1 | AirTrunk SYD4 Pty Ltd (687 904 963) | 10 Jun 2025 | KNBDC SYD4 Pty Ltd → AirTrunk SYD4 Pty Ltd from **16 Jun 2026** | who owns it |
| 2 | CKTSME Management Pty Ltd (650 102 640) | 11 May 2021 | 263 EMKC Management Pty Limited → EMKC Cubed Management Pty Ltd → CKTSME Management Pty Ltd from **3 Jun 2025** | who owns it |
| 3 | WDDP Pty Ltd (700 788 058) | **28 Jul 2026** | no former name; 17 days before the planning report | who owns it |
| 4 | Glendenning land, Lot 2 DP 1137162 | — | not a company; no free register states the proprietor | the title itself |
| 5 | Amazon Australia Company Pty Ltd (663 812 468) | 14 Nov 2022 | no former name; ABN recorded as 0 | which Amazon business holds the land |
| 6 | Zerra WDDP Manager Australia Pty Ltd (684 250 584) | 5 Feb 2025 | AGP DC Manager Australia → Zerra DC Manager Australia → Zerra WDDP Manager Australia from **13 Aug 2026** | who AGP/Zerra is |
| 7 | NineZero DC Sub TC I Pty Ltd (607 631 845) | 13 Aug 2015 | no former name | who stands behind DCI's consents |
| 8 | KNBDC AU Development Pty Ltd (687 116 098) | 15 May 2025 | no former name; keeps the KNBDC name | the company above the SYD4 stack |

All of this is already in the record (`ENT_KNBDC`, `ENT_EMKC`, `ENT_WDDP`, `ENT_NINEZERO` and
RG-055's resolution). **No new fact was bought or invented by re-reading it**, and the ownership
half of every rank is still open. That is the honest limit of the workaround.

## Free land-ownership statements found instead of buying titles (2026-11-15)

Three archived EISs state ownership themselves. These are the applicant's own statements of title,
**not** title searches, and are recorded as such — loaded by
`data-pipeline/scripts/curate_rg061_rg099.py`.

| Site | What the document says | What was done |
| --- | --- | --- |
| **Julius Avenue** (SSD-80018208) | Cover: "Prepared by Willowtree Planning Pty Ltd **on behalf of ISPT Pty Ltd**", "6-8 JULIUS AVENUE, NORTH RYDE **LOT 89 DP 1082131**". Table 6 "REGISTERED LANDOWNERS": "89/1082131 **ISPT Pty Ltd**", "Landowner's consent has been obtained from the above entity" | quoted on the row; **`owner_id` deliberately not set** — the only ISPT entity held is "ISPT (Core Fund)", and how ISPT Pty Ltd relates to it is RG-005's question |
| **NEXTDC S5** (SSD-63168959) | "Land Ownership The site is owned by **NEXTDC Limited**." | `owner_id` set to `ENT_NEXTDC` (the listed company, ASX: NXT) |
| **Road 1** (SSD-80814238) | Table 5: "Land ownership **The land is owned by Stockland.** Address 1-5 Khartoum Road, Macquarie Park … **Part Lot 2 DP 1043041**" | quoted on the row and against **RG-105**, which asks whether Road 1 and SSD-63235720 are one campus |

A fourth, already recorded: the Western Downs report names **Wambo Cattle Company Pty Limited
(ACN 058 718 326)** as registered owner of Lot 125 on DY316, with a title search in its Appendix B
(`ENT_WAMBO`). No other archived planning document states a registered proprietor — the whole
archive was searched for "registered proprietor", "registered landowner", "land ownership" and
"owner of the site" on 2026-11-15.

**What this does not replace.** Rank 4 (the Glendenning title) is untouched: no archived document
names the proprietor of Lot 2 DP 1137162, and the consent holder is a consultancy. Only a title
search will answer it.

## When an extract arrives

Save it under `data-pipeline/data/raw/asic/extracts/` and tell the agent. Only
company-level facts are recorded (docs/requests/README.md): shareholders that
are companies, the ultimate holding company, registered charges, and
directors by name in their role. Personal addresses and birth details are never
committed, so the extract PDF itself stays out of the repository and only its
manifest is kept.
