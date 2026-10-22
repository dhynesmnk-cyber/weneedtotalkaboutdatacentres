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

Ranked by what each would unlock. Drafted 2026-10-22, research batch 2.

| Rank | Document | Where | Save to | Questions | Unlocks |
| --- | --- | --- | --- | --- | --- |
| 1 | AustralianSuper portfolio holdings disclosure, 30 June 2026: the MySuper Balanced option, and the option that holds most | australiansuper.com, investments, portfolio holdings | `data/raw/superannuation/australiansuper/` | RG-004 | What Australia's largest fund holds in NEXTDC and other data centre companies, beyond the 8.49% NEXTDC's report shows |
| 2 | Future Fund Periodic Investment Reports: the Future Fund at 30 June 2025 and 30 June 2026, and the Medical Research Future Fund, Future Drought Fund, Disaster Ready Fund, Housing Australia Future Fund, DisabilityCare Australia Fund and Aboriginal and Torres Strait Islander Land and Sea Future Fund at their latest date | futurefund.gov.au, portfolio holdings (the December 2025 file was at `https://www.futurefund.gov.au/-/media/FE8DB40A35A943E69D932EE3555613C0.ashx`) | `data/raw/futurefund/` | RG-094 | Whether the other funds hold the rest of CDC (34.55% against 29%); Palantir and NVIDIA holdings across public funds; the June 2025 Palantir figure Crikey reported |
| 3 | CSC portfolio holdings disclosure, latest date | csc.gov.au | `data/raw/superannuation/csc/` | RG-004 | CSC's 12.04% of CDC, with a value |
| 4 | NEXTDC, "Response to ASX Compliance Letter", 12 December 2025 | `https://www.asx.com.au/asx/v2/statistics/displayAnnouncement.do?display=pdf&idsId=03040682` | `data/raw/asx/nxt/` | RG-014 | What the exchange asked NEXTDC a week after the OpenAI announcement. ASX's terms limit free use of its documents to private investors: read it, then decide whether the observatory can cite it, or ask ASX |
| 5 | OpenAI, "OpenAI for Australia" (5 December 2025) | `https://openai.com/global-affairs/openai-for-australia/` | `data/raw/operators/openai/` | RG-014 | OpenAI's own account of what it agreed for S7 |
| 6 | UniSuper, Australian Retirement Trust and Aware Super portfolio holdings disclosures, 30 June 2026, default options | each fund's site | `data/raw/superannuation/<fund>/` | RG-004 | The rest of the six funds the question names |
| 7 | NSW Valuer General bulk property sales data, the years covering a sale of Lot 10 DP 1280592, Kemps Creek | valuergeneral.nsw.gov.au, property sales information | `data/raw/nsw_valuer_general/psi/` | RG-005 | The price and contract date of the Mamre Road land, if it has sold |

The bulk sales data carries no buyer or seller names; it gives a price and
dates against a lot. The superannuation files are each fund's own statutory
disclosure, so they are graded A once archived.
