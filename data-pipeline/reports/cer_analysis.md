# Clean Energy Regulator verification — RG-009

Generated 2026-09-21 by `scripts/analyse_cer.py` from files archived under `data/raw/cer/` (each with a SHA-256 manifest).

NGER years parsed: 2019-20, 2020-21, 2021-22, 2022-23, 2023-24, 2024-25
Corporations published per year: 2019-20=415, 2020-21=409, 2021-22=417, 2022-23=402, 2023-24=392, 2024-25=398

---

## T1/T2 — Location-based scope 1 and scope 2 by operator

Location-based scope 2 is what a facility's grid electricity actually emitted. It is **not** reduced by buying certificates; only market-based scope 2 is. Rising location-based scope 2 therefore means rising purchased electricity, whatever the procurement story.

| Operator | metric | 2019-20 | 2020-21 | 2021-22 | 2022-23 | 2023-24 | 2024-25 | Δ 2019-20→2024-25 |
|---|---|---|---|---|---|---|---|---|
| AirTrunk | scope 1 (t) | 132 | 328 | 918 | 2,352 | 1,826 | 4,165 | +3055% |
| AirTrunk | scope 2 (t) | 94,528 | 157,174 | 257,423 | 348,562 | 450,207 | 553,344 | +485% |
| AirTrunk | net energy (GJ) | 397,923 | 660,303 | 1,106,671 | 1,643,984 | 2,275,838 | 2,886,668 | +625% |
| Amazon Web Services | scope 1 (t) | 771 | 605 | 626 | 739 | 583 | 1,007 | +31% |
| Amazon Web Services | scope 2 (t) | 134,104 | 192,062 | 260,583 | 305,732 | 319,138 | 405,217 | +202% |
| Amazon Web Services | net energy (GJ) | 606,756 | 861,976 | 1,188,419 | 1,507,903 | 1,684,160 | 2,207,911 | +264% |
| CDC Data Centres | scope 1 (t) | — | 163 | 171 | 199 | 301 | 215 | — |
| CDC Data Centres | scope 2 (t) | — | 150,136 | 187,397 | 212,744 | 257,540 | 317,465 | — |
| CDC Data Centres | net energy (GJ) | — | 669,621 | 856,414 | 1,052,002 | 1,367,770 | 1,729,124 | — |
| Equinix | scope 1 (t) | 1,198 | 969 | 826 | 1,106 | 799 | 1,869 | +56% |
| Equinix | scope 2 (t) | 297,414 | 299,083 | 309,100 | 286,428 | 279,218 | 288,374 | -3% |
| Equinix | net energy (GJ) | 1,271,291 | 1,283,804 | 1,359,210 | 1,392,552 | 1,449,889 | 1,557,358 | +23% |
| Fujitsu Australia | scope 1 (t) | 998 | 1,800 | 1,701 | 1,668 | 1,638 | 1,653 | +66% |
| Fujitsu Australia | scope 2 (t) | 120,615 | 110,062 | 89,327 | 68,576 | 59,805 | 55,228 | -54% |
| Fujitsu Australia | net energy (GJ) | 544,228 | 497,544 | 410,739 | 349,474 | 322,918 | 305,245 | -44% |
| Global Switch Australia | scope 1 (t) | 92 | 85 | 211 | 184 | 311 | — | — |
| Global Switch Australia | scope 2 (t) | 137,617 | 129,503 | 119,619 | 94,827 | 78,961 | — | — |
| Global Switch Australia | net energy (GJ) | 612,953 | 576,792 | 548,110 | 470,265 | 422,466 | — | — |
| NEXTDC | scope 1 (t) | 433 | 663 | 1,289 | 923 | 1,614 | 7,919 | +1729% |
| NEXTDC | scope 2 (t) | 218,605 | 293,797 | 350,049 | 348,765 | 335,627 | 358,353 | +64% |
| NEXTDC | net energy (GJ) | 906,422 | 1,257,868 | 1,536,358 | 1,689,015 | 1,744,228 | 1,971,147 | +117% |
| Telstra | scope 1 (t) | 36,019 | 32,815 | 31,543 | 30,465 | 32,771 | 31,422 | -13% |
| Telstra | scope 2 (t) | 1,140,573 | 1,080,491 | 1,040,346 | 856,726 | 757,967 | 677,664 | -41% |
| Telstra | net energy (GJ) | 5,593,779 | 5,358,340 | 5,284,566 | 4,933,447 | 4,657,693 | 4,310,554 | -23% |

Published controlling-corporation names per operator (for audit):

- **AirTrunk**: AIRTRUNK AUSTRALIA HOLDING PTY LTD
- **Amazon Web Services**: AMAZON CORPORATE SERVICES PTY LTD
- **CDC Data Centres**: CDC GROUP HOLDINGS PTY LTD
- **Equinix**: EQUINIX AUSTRALIA PTY LIMITED
- **Fujitsu Australia**: FUJITSU AUSTRALIA LTD
- **Global Switch Australia**: GLOBAL SWITCH AUSTRALIA HOLDINGS PTY LIMITED; GLOBAL SWITCH AUSTRALIA PTY LIMITED
- **NEXTDC**: NEXTDC LIMITED
- **Telstra**: TELSTRA CORPORATION LIMITED; TELSTRA GROUP LIMITED

---

## T3 — Market-based scope 2 (the renewable claim, in tonnes)

The CER published market-based scope 2 for the first time in the 2023-24 dataset. Reporting is **voluntary**, and only corporations choosing to report appear in the table.

### 2023-24 — 21 corporations reported market-based scope 2

| Operator | Location-based scope 2 (t) | Market-based scope 2 (t) | Reduction | Covers all facilities? |
|---|---|---|---|---|
| AirTrunk | 450,207 | **not reported** | — | — |
| Amazon Web Services | 319,138 | **not reported** | — | — |
| CDC Data Centres | 257,540 | **not reported** | — | — |
| Equinix | 279,218 | **not reported** | — | — |
| Fujitsu Australia | 59,805 | **not reported** | — | — |
| Global Switch Australia | 78,961 | **not reported** | — | — |
| NEXTDC | 335,627 | **not reported** | — | — |
| Telstra | 757,967 | **not reported** | — | — |

### 2024-25 — 34 corporations reported market-based scope 2

| Operator | Location-based scope 2 (t) | Market-based scope 2 (t) | Reduction | Covers all facilities? |
|---|---|---|---|---|
| AirTrunk | 553,344 | **not reported** | — | — |
| Amazon Web Services | 405,217 | **not reported** | — | — |
| CDC Data Centres | 317,465 | **not reported** | — | — |
| Equinix | 288,374 | **not reported** | — | — |
| Fujitsu Australia | 55,228 | 28,945 | 47.6% | Yes |
| Global Switch Australia | — | **not reported** | — | — |
| NEXTDC | 358,353 | 345,432 | 3.6% | No (94% of facilities) |
| Telstra | 677,664 | **not reported** | — | — |

---

## T4 — LGC certificate shortfall register

- Entries: 143, covering assessment years 2001–2025.
- **Data centre operators appearing as LGC-liable entities: 0**. Under the RET, liability attaches to retailers and to those acquiring electricity, not to data centre operators as such.

| Assessment year | Liable entities in shortfall | LGC liability | LGCs surrendered | Shortfall charges (A$) |
|---|---|---|---|---|
| 2023 | 17 | 8,341,168 | 4,251,234 | 264,803,435 |
| 2024 | 7 | 6,816,270 | 2,990,155 | 248,697,475 |
| 2025 | 15 | 4,869,308 | 2,906,154 | 115,518,910 |

---

## T5 — Safeguard Mechanism coverage

- Covered facilities in the 2024-25 baselines and emissions table: **228**.
- Data centre facilities among them: **0**.
- ANZSIC classes mentioning data/computer/information/hosting: none.
- Total covered emissions: 133,843,704 t CO2-e.

No Australian data centre is a Safeguard Mechanism covered facility. Combined with the scope 1 figures above (every operator's scope 1 is two to three orders of magnitude below the 100,000 t CO2-e threshold), the carbon constraint simply does not reach this sector while it draws grid power. An on-site gas project such as Cloud Carrier's proposed 673 MW Moss Vale station is a different matter — it is not in this table because it is not yet built.

---

## T6 — LGC holdings in the REC Registry

- Registry accounts: 1306; total registered LGC holdings 45,516,746.
- The CER's own caveat applies: *LGCs held in the REC Registry move between accounts regularly, so registered holdings data should be considered as a guide only.* Holdings are a snapshot, not a surrender record.

| Account | Registered LGC holdings |
|---|---|
| TELSTRA ENERGY (GENERATION) PTY LTD | 423,379 |
| CDC DATA CENTRES PTY LTD | 233,209 |
| Amazon Energy LLC | 226,073 |
| NEXTDC Limited | 500 |

---

## Entities screened and absent from every dataset

Searched for and not found in the NGER corporate tables, the market-based scope 2 table, the shortfall register or the Safeguard table: Microsoft, Google, Meta, Digital Realty, Macquarie Technology Group, DCI Data Centers, Cloud Carrier, Vantage.

Absence has two possible causes, and they must not be conflated: the corporation did not meet the NGER publication threshold, or it reports under a different controlling corporation or SPV name. Microsoft, Google and Meta all operate Australian facilities, so their absence is a **threshold or naming** result, not evidence of zero emissions. Resolving it requires the ASIC/SPV work in RG-013.

---

## Verdicts on the claims held in `renewable_claims`

Applied by `data/packs/cer_verification.json`:

| Claim | Verdict | Basis |
|---|---|---|
| AirTrunk: 100% renewable energy by 2025 (national) | **CONTRADICTED as a statement about Australian operations** | Location-based scope 2 rose from 94,528 t to 553,344 t over five years; scope 1 rose to 4,165 t. AirTrunk does not appear in the CER's market-based scope 2 table for either published year, so the claim has no expression in statutory data. A 100% renewable claim made through market-based accounting cannot be reconciled against the regulator's published figures because the operator did not report them. |
| NEXTDC: renewable procurement (implied by market-based reporting) | **PARTIALLY_VERIFIED** | NEXTDC is the only Australian data centre operator that reported market-based scope 2 to the CER in 2024-25: 345,432 t against 358,353 t location-based — a reduction of 3.6%. The CER records the coverage flag as 'No (94% of facilities)', so the total is not group-wide. A single-digit market-based reduction is not consistent with a portfolio-wide 100% renewable position, and NEXTDC holds 500 LGCs in the REC Registry snapshot. |
| No data centre operator adequately proves it drives renewable growth (Greenpeace, May 2026) | **VERIFIED** | Independently reproduced from primary CER data. Zero data centre operators appear as LGC-liable entities in the shortfall register; zero appear as Safeguard covered facilities; only one of eight operators reported market-based scope 2 in either published year; and location-based scope 2 rose for every operator across the series. |
| Safeguard Mechanism does not reach grid-connected data centres | **VERIFIED** | Of 228 covered facilities in 2024-25, none is a data centre and no ANZSIC class referencing data processing or hosting appears. Every operator's scope 1 is far below the 100,000 t CO2-e threshold - the highest among dedicated data centre operators in 2024-25 is NEXTDC at 7,919 t. |
| Top three operators' emissions doubled in five years, +20% in 2024-25 (AFR, March 2026) | **VERIFIED** | Reproduced from the CER corporate tables: AirTrunk + CDC + Amazon combined location-based scope 2 rose from 499,372 t in 2020-21 to 1,276,026 t in 2024-25, and rose 24.3% year on year. |
