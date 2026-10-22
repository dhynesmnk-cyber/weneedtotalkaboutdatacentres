# Paid searches, ranked

Status: **ranked, awaiting a budget**, 2026-10-22.

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
| 9 | ASIC current and historical extract: **Project Garden 1 Pty Ltd** | 684 182 929 | $20 | RG-055 | Who owns the Brookhollow Avenue proponent (GreenSquare DC campus) |

Ranks 1 to 3 cost $60 and answer the three biggest open questions. All nine
cost $177. The GIPA application (GIPA-001, $30) is separate and recommended
alongside rank 1.

## When an extract arrives

Save it under `data-pipeline/data/raw/asic/extracts/` and tell the agent. Only
company-level facts are recorded (docs/requests/README.md): shareholders that
are companies, the ultimate holding company, registered charges, and
directors by name in their role. Personal addresses and birth details are never
committed, so the extract PDF itself stays out of the repository and only its
manifest is kept.
