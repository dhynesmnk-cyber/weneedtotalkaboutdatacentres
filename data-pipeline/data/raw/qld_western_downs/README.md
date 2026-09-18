# Western Downs Digital Park — lodged development application

The primary document was fetched on 2026-09-18, analysed, and then **removed from this workspace**
because at 343,666,719 bytes it exceeds the workspace snapshot cap and would crowd out the rest of
the evidence base.

Re-fetch (single command, ~3 minutes):

    python3 scrapers/ingest_cer.py --url "qld_wd=https://wdrcdevelopmenti.blob.core.windows.net/devdocs/6393206_1.pdf"

Verify against the archived manifest (`wdrc_6393206_1.pdf.meta.json`):

    sha256 = 47137f5b5ed4953b3831d18c107ca136aaae8830acfb5f0ed55de7d20156b331
    bytes  = 343,666,719
    url    = https://wdrcdevelopmenti.blob.core.windows.net/devdocs/6393206_1.pdf

What is retained here:

- `wdrc_6393206_1.pdf.meta.json` — the provenance manifest above
- `opening_streams.txt` — the decoded Town Planning Report (Urbis V4, 14 August 2026), which is the
  source of every Western Downs fact now in the database

Re-extract after re-fetching (streaming mode is mandatory; the document embeds survey imagery whose
streams decompress to gigabytes):

    python3 scripts/pdf_text.py data/raw/qld_western_downs/wdrc_6393206_1.pdf \
        --max-streams 250 --out data/raw/qld_western_downs/opening_streams.txt

The appendices were NOT decoded — see research gap RG-053.
