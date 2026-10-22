# Requests

Freedom of information requests, government information (GIPA) applications
and paid register searches that the research needs and only the author can
lodge or buy. The plan behind them is `docs/RESEARCH-PLAN.md`; each request
names the research questions it would answer.

Agents draft these. The author decides what to lodge and buy, under a budget
the author sets, and lodges them in their own name. When a response arrives,
put the documents in `data-pipeline/data/raw/` with a manifest, and the
question's hunt log records what came back, including any refusal and its
reasons.

## Index

| Request | To | Law or service | Cost | Questions | Status |
| --- | --- | --- | --- | --- | --- |
| [GIPA-001](GIPA-001-ownership-documents.md) | NSW Department of Planning, Housing and Infrastructure | GIPA Act 2009 (NSW) | $30 application fee | RG-021, RG-035, RG-037, RG-057, RG-059, RG-064 | drafted |
| [Paid searches](PAID-SEARCHES.md) | ASIC; NSW Land Registry Services | Register searches | $10 to $20 each | RG-021, RG-036, RG-037, RG-050, RG-052, RG-057, RG-059, RG-064, RG-081 | ranked, awaiting a budget |

Status runs: drafted, lodged, acknowledged, decided, received (or refused).

## Fees, as published

- **GIPA (NSW):** a $30 application fee, which also covers the first hour of
  processing; further processing is charged at $30 an hour. An agency should
  decide within 20 working days, or the application is deemed refused and the
  fee refunded. A 50% reduction in processing charges is available where the
  information is of special benefit to the public generally.
  ([IPC fact sheet](https://www.ipc.nsw.gov.au/resources/fact-sheet-gipa-act-fees-and-charges))
- **ASIC registers:** a current company extract is $10 and a current and
  historical extract $20 online.
  ([ASIC company registers](https://www.asic.gov.au/online-services/search-asic-registers/company-and-organisation-registers))
- **NSW title search:** $17.00 excluding GST from NSW Land Registry Services for
  2026/27; information brokers set their own prices.
  ([NSW LRS fees 2026/27](https://nswlrs.com.au/assets/f/1129775276948026/x/5fed3e7cd6/2026-2027_nsw-lrs-fees_final.pdf))

Check the live schedule before paying; these were read on 2026-10-21.

## Handling what comes back

An ASIC extract names directors and can show their residential addresses and
dates of birth. Only company-level facts are recorded: shareholders that are
companies, the ultimate holding company, registered charges, and directors by
name in their role. Addresses, birth details and anything else personal are
never committed.
