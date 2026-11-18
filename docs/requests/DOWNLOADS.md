# Documents a person must download

Free, public documents that the research crawler could not fetch. Each site
refused it: it served a bot-check page, refused to serve its robots.txt (which
is read as "keep out"), or excluded the folder in its robots.txt. Every refusal
is recorded in `data-pipeline/data/raw/*/refused.json` and was never worked
around. A browser user agent would get past some of them; agents do not use
one.

These cost nothing. They need a person with a browser. Download each into the
folder named, and add a manifest beside it (`<file>.meta.json` with `url`,
`fetched_utc`, `sha256` and `bytes`, as the archived files have). The question's
hunt log records what came back.

**Order to work in (2026-11-18).** The ranks below are the order the list was
written in. Under the plan of 2026-11-18, do them in the order of the essays
they unlock:

1. #22 and #26 (ES-013: certified facilities).
2. #23, #24, #25, and Latrobe Council's record for Firmus's Wesley Vale
   application (ES-014: the regions).
3. #2 (ES-012: the Future Fund).
4. #8 to #11 (ES-007, and ES-015's contracts).
5. #17 to #19 (ES-005's follow-up).
6. #1, #3, #6 and #7 (ES-002's follow-up).
7. #4 and #5 (ES-008's follow-up).
8. #13, #14 and #16 (ES-009's follow-up).
9. Then #15, #20, #21 and #27.
10. #28 (RG-008: the four licences) and #29 (RG-073: the last air quality report), added 2026-11-18 by research batch 8.
11. #30 to #34 (RG-007, 018, 027, 063, 069), added 2026-11-18 by batch 8's second pass: each is the free primary record a robots.txt or a block refused.

All of them are free.

**Received from the author, 2026-11-17.** Three DigiCo Infrastructure REIT
documents for RG-101, not on the ranked list below: the crawler asked ASX for
two of them on 2026-11-16 and was served a bot-check page
(`data/raw/asx/dgt/refused.json`, which still records that). The author
downloaded them in a browser:
- the release of 15 October 2026 on SYD1's 71 MW contract;
- the AGM 2026 presentation;
- the Annual Report 2026.

ASX's terms (rank 4's note) are why the PDFs are not committed. Each has a manifest
and verbatim excerpts of the cited passages in `data/raw/asx/dgt/`. They placed
three of the five held register facilities; see `reports/hunts/RG-101.md`.

Ranked by what each would unlock. Drafted 2026-10-22, research batch 2; ranks 8 to 12 added the same day by batch 3, ranks 13 to 16 by batch 4, and ranks 17 to 21 by batch 5 (2026-10-30).

**Re-tested 2026-11-01 (rolling batch): every robots.txt refusal still
stands.** Each refusing site's robots.txt was read again as the crawler. Where
a site refuses to serve it, the refusal comes from the site's own front end
(Cloudflare, CloudFront, Akamai or Azure), not this project's network. Two
changed, neither enough to fetch:

- **The NSW lobbyist register (rank 9)** now begins with a hosting service's
  "Allow: /", but the site's own "Disallow: /" for every crawler is still
  there below it, so it stays refused (RG-070's hunt log).
- **Tenders WA (rank 13)** now serves its robots.txt, which allows only the
  home page; the contract search stays refused (RG-093's hunt log).

The eight refusals that came from the page itself (a 403, a 429 or a
bot-check page: OpenAI, CSC, Australian Retirement Trust, UniSuper, three state
tender portals and the keynote video) were not asked for again.

| Rank | Document | Where | Save to | Questions | Unlocks |
| --- | --- | --- | --- | --- | --- |
| 1 | AustralianSuper portfolio holdings disclosure, 30 June 2026: the MySuper Balanced option, and the option that holds most | australiansuper.com, investments, portfolio holdings | `data/raw/superannuation/australiansuper/` | RG-004 | What Australia's largest fund holds in NEXTDC and other data centre companies, beyond the 8.49% NEXTDC's report shows |
| 2 | Future Fund Periodic Investment Reports: the Future Fund at 30 June 2025 and 30 June 2026, and the Medical Research Future Fund, Future Drought Fund, Disaster Ready Fund, Housing Australia Future Fund, DisabilityCare Australia Fund and Aboriginal and Torres Strait Islander Land and Sea Future Fund at their latest date | futurefund.gov.au, portfolio holdings (the December 2025 file was at `https://www.futurefund.gov.au/-/media/FE8DB40A35A943E69D932EE3555613C0.ashx`) | `data/raw/futurefund/` | RG-094 | Whether the other funds hold the rest of CDC (34.55% against 29%); Palantir and NVIDIA holdings across public funds; the June 2025 Palantir figure Crikey reported |
| 3 | CSC portfolio holdings disclosure, latest date | csc.gov.au | `data/raw/superannuation/csc/` | RG-004 | CSC's 12.04% of CDC, with a value |
| 4 | NEXTDC, "Response to ASX Compliance Letter", 12 December 2025 | `https://www.asx.com.au/asx/v2/statistics/displayAnnouncement.do?display=pdf&idsId=03040682` | `data/raw/asx/nxt/` | RG-014 | What the exchange asked NEXTDC a week after the OpenAI announcement. ASX's terms limit free use of its documents to private investors: read it, then decide whether the observatory can cite it, or ask ASX |
| 5 | OpenAI, "OpenAI for Australia" (5 December 2025) | `https://openai.com/global-affairs/openai-for-australia/` | `data/raw/operators/openai/` | RG-014 | OpenAI's own account of what it agreed for S7 |
| 6 | UniSuper, Australian Retirement Trust and Aware Super portfolio holdings disclosures, 30 June 2026, default options | each fund's site | `data/raw/superannuation/<fund>/` | RG-004 | The rest of the six funds the question names |
| 7 | NSW Valuer General bulk property sales data, the years covering a sale of Lot 10 DP 1280592, Kemps Creek | valuergeneral.nsw.gov.au, property sales information | `data/raw/nsw_valuer_general/psi/` | RG-005 | The price and contract date of the Mamre Road land, if it has sold |
| 8 | NSW ministers' diary disclosures, January 2025 to June 2026: the Premier, the Treasurer, and the Planning, Energy and Industry ministers (30 files; the list is in `data/raw/registers/nsw_ministers_diaries/refused.json`) | nsw.gov.au, Cabinet Office, ministers' diary disclosures | `data/raw/registers/nsw_ministers_diaries/` | RG-070, RG-077 | Which data centre companies and bodies met the ministers who set the policy, and when |
| 9 | NSW Lobbyists Register: every lobbyist whose clients include AirTrunk, NEXTDC, Equinix, CDC, Microsoft, Amazon, Google, Goodman, Stockland or Data Centres Australia | lobbyists.elections.nsw.gov.au | `data/raw/registers/nsw_lobbyists/` | RG-070 | Who lobbies NSW for the industry, on whose behalf |
| 10 | Australian Government Register of Lobbyists: the same clients | lobbyists.ag.gov.au (needs a browser) | `data/raw/registers/cth_lobbyists/` | RG-070, RG-077 | The same, for the Commonwealth |
| 11 | AusTender contract notices for the NSW-facing Commonwealth agencies, and buy.nsw contract awards for DPHI, the IPC and Infrastructure NSW, searched for Arup, Cundall, Lehr and Greenbox | tenders.gov.au; buy.nsw.gov.au | `data/raw/registers/austender/`, `data/raw/registers/buynsw/` | RG-074 | Whether the firms that hold data centre consents also work for the assessors |
| 12 | **Done 2026-11-18, no download needed.** The executed Microsoft planning agreement (a 39-page scan) was re-fetched, its SHA-256 matched the archive, and it was read by OCR and checked against the page image: clause 6.1 keeps $8,423,505.96, indexed by CPI | already archived; OCR text at `data/raw/councils/penrith/` | `data-pipeline/reports/hunts/RG-025.md` | RG-025 | Settled: the signed figure is the draft's |
| 13 | Palantir contracts on the state and territory tender portals: Buying for Victoria, SA Tenders, ACT Tenders, Tenders WA, QTenders, Tasmania and the Northern Territory, and buy.nsw supplier profile 3813; search for Palantir and the ABN 48 144 948 309 | each portal's contract search | `data/raw/registers/state_tenders/` | RG-086, RG-093 | What states and territories have bought from Palantir, including any police or justice agency |
| 14 | Watch the NVIDIA GTC Washington, D.C. keynote of 28 October 2025 at about 1:25:14 and note Jensen Huang's sentence on Palantir word for word | youtube.com, video lQHK61IDFH4 | `data-pipeline/reports/hunts/RG-092.md` | RG-092 | Whether the quote two transcripts agree on is what he said |
| 15 | Queensland Hansard for 16 September 2026: the Premier's statement on Anthropic and the Western Downs Digital Park | parliament.qld.gov.au, Hansard | `data/raw/qld_western_downs/hansard/` | RG-012 | What the Queensland Government has said about the deal, in its own record |
| 16 | ASD's cloud assessment and authorisation FAQ, the page on the retirement of the Certified Cloud Services List | cyber.gov.au (it did not answer the crawler) | `data/raw/operators/asd/` | RG-089, RG-087 | Whether any "ASD certification" of a cloud service could exist after 2020 |
| 17 | NSW Legislative Council inquiry into data centres: the submission list, every submission, and the committee's report (due 30 September 2026) | parliament.nsw.gov.au, the inquiry page | `data/raw/nsw_inquiry/submissions/` | RG-015, RG-041, RG-016 | Who spoke to the inquiry, and what each said about subsidies, water, jobs and emissions |
| 18 | Senate inquiry into Artificial intelligence and data centres: submission list pages 2 to 6 and the submissions from the industry's companies and peak bodies | aph.gov.au, the committee's submissions page | `data/raw/senate_inquiry/` | RG-066, RG-016 | Who lobbies at Commonwealth level |
| 19 | State Environmental Planning Policy (Planning Systems) 2021, section 2.7, as in force on 14 July 2020 and on 2 September 2026, and the former State and Regional Development SEPP 2011 clause 8A | legislation.nsw.gov.au, historical versions | `data/raw/registers/nsw_legislation/` | RG-040, RG-069 | When a council objection or a donation disclosure made the Independent Planning Commission the consent authority, and whether that changed for data centres in August 2026 |
| 20 | Victoria's Development Facilitation Program decisions for data centres, and the NEXTDC M3 permit and conditions | planning.vic.gov.au; Maribyrnong planning register | `data/raw/vic_planning/` | RG-048, RG-056 | Whether Victoria's fast track carries weaker conditions than council permits |
| 21 | The Melton (Syncline Energy) and South Morang data centre applications | Melton and Whittlesea planning registers | `data/raw/vic_planning/` | RG-011 | Who the proponents are and what they applied for |
| 22 | DigiCo's own location pages: Adelaide 1 and 2, Sydney 1, Brisbane (BNE), Brisbane 1, 2 and 3, Townsville 1. Its robots.txt now allows crawling, but every page answered HTTP 403 on 2026-11-18 | digi-co.com.au/location/ (the list is in `data/raw/operators/digico/refused.json`) | `data/raw/operators/digico/` | RG-103, RG-106 | Addresses, status and capacity of DigiCo's Australian sites, including whether BNE and BNE3 are one site |
| 23 | Queensland's list of prescribed projects | statedevelopment.qld.gov.au, Coordinator-General, prescribed projects, list of projects | `data/raw/qld_western_downs/qld_prescribed/` | RG-054 | Whether the Western Downs Digital Park has been declared a prescribed project |
| 24 | The EPBC Act referral for Gingerah Energy's Project Meridien, the reported 1 GW off-grid data centre in the Kimberley | epbcpublicportal.environment.gov.au (search the referral by proponent) | `data/raw/wa_proposals/gingerah/` | RG-010 | The proponent, site and status of the WA proposal, from the referral itself |
| 25 | Ipswich City Council's development application for the Swanbank data centre (Northern Concept Swanb Pty Ltd), with its information request | Ipswich City Council, PD Online | `data/raw/qld_ipswich/swanbank/` | RG-051 | The applicant, site, height and stage of the ten-storey proposal, from the council's own record |
| 26 | Cloud Carrier's own DB1 page, and any planning record for a data centre at Moss Vale | cloudcarrier.com (robots.txt answers 403); NSW Planning Portal; Wingecarribee Shire Council (its site answered 403) | `data/raw/operators/cloudcarrier/` | RG-101 | Where Cloud Carrier's certified DB1 is, and its status |
| 27 | IPART's submission to the NSW Legislative Council inquiry into data centres, and IPART's review page on a water pricing framework for data centres | ipart.nsw.gov.au (it closed the connection on 2026-11-18) | `data/raw/operators/ipart/` | RG-042 | IPART's own statement of Sydney Water's data centre demand estimate, in place of the press's '25 per cent' |
| 28 | The NSW EPA's public register of environment protection licences: the licence, if one was issued, for 51 Huntingwood Drive (SSD-41589232), NEXTDC S4 Horsley Park (SSD-63741210), Marsden Park (SSD-70889211) and Roberts Road as modified (SSD-10330-Mod-2), with its conditions on generator hours, NOx limits and monitoring | epa.nsw.gov.au, POEO public register, search by premises or licence holder (an interactive application that redirected the crawler more than 50 times on 2026-11-18) | `data/raw/registers/nsw_epa/` | RG-008 | The four data centres the EPA said need a licence: whether they hold one, and what it allows |
| 29 | Project Echidna's air quality report (`project-echidna-eis-appendix-j-air-quality-report-42`, SSD-47320208): larger than the crawler's 120 MB limit | NSW Planning Portal, Project Echidna Data Centre, EIS documents | `data/raw/nsw_planning/documents/` | RG-073 | Which firm wrote the one consent air quality report not yet read |
| 30 | **Done 2026-11-18 (the author).** NSW Budget 2026-27, Budget Paper No. 1. Its tax expenditure statement (Appendix C) never mentions data centres | nsw.gov.au, 2026-27 budget papers, Budget Paper No. 1 (the PDF sits under a path robots.txt disallows) | `data/raw/registers/nsw_budget/` | RG-007 | Whether NSW gives data centres any tax concession, in the State's own statement of revenue forgone |
| 31 | **Done 2026-11-18 (the author).** AEMO's NEM Registration and Exemption List. A Firmus company is registered to provide ancillary services as a load; CDC is an intending participant; NEXTDC's generators are exempt with zero export | aemo.com.au, National Electricity Market, participate in the market, registration (answered HTTP 403) | `data/raw/registers/aemo/` | RG-018 | Whether any data centre is registered to provide frequency control or other system services |
| 32 | **Done 2026-11-18 (the author).** The NT Government's release of 22 July 2026 on Beetaloo Digital at Weddell (media advisers' contact details redacted in the archive) | territorycoordinator.nt.gov.au, news and insights (its robots.txt could not be read) | `data/raw/operators/ntgov/` | RG-027 | The land grant, site and scale of the gas-powered campus proposed near Darwin, from the government's own record |
| 33 | NSW Department of Planning, Housing and Infrastructure Annual Report 2024-25, Volumes 1 and 2 | nsw.gov.au, the Department's information access page, links to the National Library (nla.gov.au served a bot-check page) | `data/raw/registers/dphi/` | RG-063 | Whether the report gives the data centre concierge team's headcount or cost |
| 34 | **Done 2026-11-18 (the author).** The stakeholder register, then Amazon Web Services Australia's own major political donor disclosures, transcribed into the session: $15,200 (2023/24), $13,250 (2024/25, disclosure 130644) and $10,900 (2025/26), totals without recipients. The Commonwealth amounts came from the AEC's free bulk returns | efadisclosures.elections.nsw.gov.au (its robots.txt disallows every crawler) | `data/raw/registers/nsw_electoral_disclosures/` | RG-069 | What the donors disclosed to the Electoral Commission, beside what they disclosed on the planning portal |

The bulk sales data carries no buyer or seller names; it gives a price and
dates against a lot. The superannuation files are each fund's own statutory
disclosure, so they are graded A once archived.
