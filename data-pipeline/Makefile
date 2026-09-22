# Australian Data Centre Observatory
#
#   make            build the database from seed, apply curated verification packs, regenerate docs
#                   and export + verify exports/csv/
#   make check-export   verify the committed CSVs match the database (no writes)
#   make fetch-cer  download Clean Energy Regulator datasets into data/raw/cer/
#   make fetch-austender  archive an AusTender keyword search into data/raw/austender/
#                         (KEYWORD=palantir by default; needs network, see the scraper docstring)
#   make verify     re-run the CER verification analysis and rewrite its pack
#   make clean      remove generated artefacts (never touches data/raw/ or the packs)
#
# No third-party dependencies beyond the standard library and openpyxl (for CER XLSX files).
# If make is not installed, use:  python3 scripts/rebuild_all.py   [--fetch to re-download first]

PY ?= python3
DB  = exports/australian_data_centre_observatory.db
# Load order matters: later packs may cite sources registered by earlier ones.
PACKS = data/packs/cer_verification.json
PACKS_ALLOW_MISSING = data/packs/rg013_hyperscaler_sites.json \
                      data/packs/rg002_nsw_ssd_register.json \
                      data/packs/rg026_consent_conditions.json \
                      data/packs/rg015_inquiry_record.json \
                      data/packs/rg034_consent_modifications.json \
                      data/packs/rg003_vic_qld.json \
                      data/packs/rg049_western_downs.json \
                      data/packs/rg038_consent_comparison.json \
                      data/packs/rg046_guidelines_scope.json \
                      data/packs/rg060_consent_matrix.json \
                      data/packs/airtrunk_bca_influence.json \
                      data/packs/consultants_layer.json \
                      data/packs/rg079_determinations.json \
                      data/packs/status_updates.json \
                      data/packs/palantir_nvidia_thread.json
CER_YEARS = 2019-20,2020-21,2021-22,2022-23,2023-24,2024-25
# AusTender keyword to archive. Palantir is the entry point the scraper was written for; the
# same target serves RG-072 with KEYWORD="tata consultancy".
KEYWORD ?= palantir

.PHONY: all build verify load docs check-export check-packs check-austender check-patents check-filings reextract-consents battery-offline fetch-cer fetch-registers fetch-austender query unverified clean

all: check-packs check-austender check-patents build verify load check-filings docs

check-packs:
	$(PY) scripts/check_packs.py

# Offline fixture tests for the AusTender link-discovery parser. In `all` on the repo's own
# lesson from check_packs.py: a check no driver runs is a check that silently rots. Proves the
# parser handles the shapes it was written for, NOT that those shapes match AusTender.
check-austender:
	$(PY) scrapers/ingest_austender.py --selftest

# Planted-topic recovery test for the LDA sampler in scripts/analyse_patents.py. Real ground
# truth, and it fails if the sampler is broken - verified by mutation. See reports/PATENT_METHOD.md.
check-patents:
	$(PY) scripts/analyse_patents.py --selftest

# Fixture tests for the filings counter, including the one that matters: a near-miss name is NOT
# silently absorbed into a tracked entity. Reads the database for the match table; writes nothing.
check-filings:
	$(PY) scripts/count_patent_filings.py --selftest

# Re-extract the archived consent PDFs with pypdf (offline; sha256-verified against the fetch manifests)
reextract-consents:
	$(PY) scripts/reextract_consents.py

# Re-analyse the battery from the archived extractions - no network, no re-download
battery-offline:
	$(PY) scripts/consent_condition_audit.py --offline

build:
	$(PY) scripts/build_db.py

# Regenerate the verification pack from the archived raw CER files, then load it.
verify:
	$(PY) scripts/analyse_cer.py
	$(PY) scripts/curate_rg013.py
	$(PY) scripts/curate_rg002.py
	$(PY) scripts/curate_rg026.py
	$(PY) scripts/curate_rg015.py
	$(PY) scripts/curate_rg034.py
	$(PY) scripts/curate_rg003.py
	$(PY) scripts/curate_rg049.py
	$(PY) scripts/curate_rg038.py
	$(PY) scripts/curate_rg046.py
	$(PY) scripts/curate_rg060.py
	$(PY) scripts/curate_rg079.py
	$(PY) scripts/curate_airtrunk_bca.py
	$(PY) scripts/curate_consultants.py
	$(PY) scripts/curate_status.py
	$(PY) scripts/curate_palantir_nvidia.py

load: build verify
	@for p in $(PACKS); do \
		echo "--- loading $$p"; \
		$(PY) scripts/load_pack.py $$p || exit 1; \
	done
	@for p in $(PACKS_ALLOW_MISSING); do \
		echo "--- loading $$p (cross-pack sources allowed)"; \
		$(PY) scripts/load_pack.py $$p --allow-missing-source || exit 1; \
	done

docs:
	$(PY) scripts/extraction_audit.py
	$(PY) scripts/gen_dictionary.py
	# Authoritative CSV export. Runs LAST, after every pack has loaded, and verifies
	# each file it wrote against the database - it fails the build on any divergence.
	# build_db.py also writes CSVs but it runs before the packs load, so those are
	# seed-only and must not be relied on.
	$(PY) scripts/export_csv.py
	# Post-load documentation: build_db.py wrote build_report.md and viewer/db.json at SEED
	# stage; finalize regenerates both from the loaded database. Must run after every pack.
	$(PY) scripts/finalize_docs.py

# Verify the committed CSVs match the database without rewriting anything.
check-export:
	$(PY) scripts/export_csv.py --verify

# Network steps - run once, then work from the archive.
fetch-cer:
	$(PY) scrapers/ingest_cer.py --check
	$(PY) scrapers/ingest_cer.py --years $(CER_YEARS)

fetch-registers:
	$(PY) scrapers/ingest_cer.py --registers

# AusTender contract notices - the portal of record RG-072 needs in place of the GovMarket
# aggregator. Never run against the live site (see the scraper docstring): --check first, then
# read the archived HTML before anything is curated from it.
fetch-austender:
	$(PY) scrapers/ingest_austender.py --check
	$(PY) scrapers/ingest_austender.py --keyword "$(KEYWORD)" --follow

query:
	$(PY) scripts/query.py --list

unverified:
	$(PY) scripts/query.py unverified

clean:
	rm -f $(DB) exports/csv/*.csv exports/cer/*.csv viewer/db.json reports/build_report.md
	rm -rf data/__pycache__ scripts/__pycache__
