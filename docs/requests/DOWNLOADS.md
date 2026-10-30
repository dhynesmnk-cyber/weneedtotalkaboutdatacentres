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

Ranked by what each would unlock. Drafted 2026-10-22, research batch 2; ranks 8 to 12 added the same day by batch 3, ranks 13 to 16 by batch 4, and ranks 17 to 21 by batch 5 (2026-10-30).

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
| 12 | Read the executed Microsoft planning agreement (a 39-page scan; archived at `data/raw/councils/penrith/`, so no download is needed) and note the contribution in clause 6.1 | already archived | `data-pipeline/reports/hunts/RG-025.md` | RG-025 | Whether the signed figure is the draft's $8,423,505.96 |
| 13 | Palantir contracts on the state and territory tender portals: Buying for Victoria, SA Tenders, ACT Tenders, Tenders WA, QTenders, Tasmania and the Northern Territory, and buy.nsw supplier profile 3813; search for Palantir and the ABN 48 144 948 309 | each portal's contract search | `data/raw/registers/state_tenders/` | RG-086, RG-093 | What states and territories have bought from Palantir, including any police or justice agency |
| 14 | Watch the NVIDIA GTC Washington, D.C. keynote of 28 October 2025 at about 1:25:14 and note Jensen Huang's sentence on Palantir word for word | youtube.com, video lQHK61IDFH4 | `data-pipeline/reports/hunts/RG-092.md` | RG-092 | Whether the quote two transcripts agree on is what he said |
| 15 | Queensland Hansard for 16 September 2026: the Premier's statement on Anthropic and the Western Downs Digital Park | parliament.qld.gov.au, Hansard | `data/raw/qld_western_downs/hansard/` | RG-012 | What the Queensland Government has said about the deal, in its own record |
| 16 | ASD's cloud assessment and authorisation FAQ, the page on the retirement of the Certified Cloud Services List | cyber.gov.au (it did not answer the crawler) | `data/raw/operators/asd/` | RG-089, RG-087 | Whether any "ASD certification" of a cloud service could exist after 2020 |
| 17 | NSW Legislative Council inquiry into data centres: the submission list, every submission, and the committee's report (due 30 September 2026) | parliament.nsw.gov.au, the inquiry page | `data/raw/nsw_inquiry/submissions/` | RG-015, RG-041, RG-016 | Who spoke to the inquiry, and what each said about subsidies, water, jobs and emissions |
| 18 | Senate inquiry into Artificial intelligence and data centres: submission list pages 2 to 6 and the submissions from the industry's companies and peak bodies | aph.gov.au, the committee's submissions page | `data/raw/senate_inquiry/` | RG-066, RG-016 | Who lobbies at Commonwealth level |
| 19 | State Environmental Planning Policy (Planning Systems) 2021, section 2.7, as in force on 14 July 2020 and on 2 September 2026, and the former State and Regional Development SEPP 2011 clause 8A | legislation.nsw.gov.au, historical versions | `data/raw/registers/nsw_legislation/` | RG-040, RG-069 | When a council objection or a donation disclosure made the Independent Planning Commission the consent authority, and whether that changed for data centres in August 2026 |
| 20 | Victoria's Development Facilitation Program decisions for data centres, and the NEXTDC M3 permit and conditions | planning.vic.gov.au; Maribyrnong planning register | `data/raw/vic_planning/` | RG-048, RG-056 | Whether Victoria's fast track carries weaker conditions than council permits |
| 21 | The Melton (Syncline Energy) and South Morang data centre applications | Melton and Whittlesea planning registers | `data/raw/vic_planning/` | RG-011 | Who the proponents are and what they applied for |

The bulk sales data carries no buyer or seller names; it gives a price and
dates against a lot. The superannuation files are each fund's own statutory
disclosure, so they are graded A once archived.
