#!/usr/bin/env python3
"""
HCF certification from the Commonwealth's own register (batch S3, RG-096).

The Hosting Certification Framework's "Certified Service Providers" page, published by the
Department of Home Affairs, lists every data centre facility and enclave certified at the
Strategic level. Until now the 26 sites recorded as certified_strategic all rested on a grade-B
market directory (SRC_CERTSTRAT), and 67 sites had no HCF value at all.

What this script does:
  * Reads the archived page (data/raw/hcf/), verified against its SHA-256 manifest. The live site
    refused automated clients, so the archive is the Internet Archive's capture of 28 September
    2026 in its original HTML; see the manifest's "method".
  * Parses the two facility lists: "Certified Strategic Facility" (the whole facility) and
    "Certified Strategic Enclave" (a certified area within a facility). Both are the Strategic
    level, so both record certified_strategic; which one applies is kept verbatim in the
    source_refs quote, because the schema has no column for it and inventing one is not this
    script's call.
  * Matches site records to register entries through MATCHES below: a site is matched only when
    EVERY facility its record names appears in the register under that provider.
  * Uses "fill": a site that already holds a different value keeps it, and the difference is
    reported at load. The register is added as a source with its quote either way, so the 26
    existing values now cite a primary document.

What it does not do:
  * Absence from the register is never recorded as not_certified. The register lists only
    certified providers, and new registrations have been paused since 3 November 2025.
  * A certified cloud service (e.g. "Microsoft Azure Cloud (Australian Regions)") is not a
    facility certification and is never applied to a site.

Refuses to write if the archive fails its SHA-256 check, the page no longer has the expected
headings, or a MATCHES facility is missing from the register.

Outputs:
  * data/packs/hcf_register.json - the register as a source, fill rows with quotes, and RG-096
    opened and resolved with the search recorded.

Run:
    python3 scripts/curate_hcf_register.py
    python3 scripts/load_pack.py data/packs/hcf_register.json --allow-missing-source
"""
from __future__ import annotations

import hashlib
import html
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ARCHIVE = os.path.join(ROOT, "data", "raw", "hcf", "certified-service-providers.20260928125530.html")
OUT_PACK = os.path.join(ROOT, "data", "packs", "hcf_register.json")

SOURCE_ID = "SRC_HCF_REGISTER"
TODAY = "2026-10-10"
FACILITY = "Service Provider and Certified Strategic Facility:"
ENCLAVE = "Service Provider and Certified Strategic Enclave:"
END = "Cloud Services"

# site id -> (provider as the register names it, facilities the site record names).
# Every facility listed must appear under that provider for the site to be matched.
MATCHES: dict[str, tuple[str, list[str]]] = {
    "SITE_AIRTRUNK_SYD1": ("AirTrunk Australia", ["SYD1"]),
    "SITE_AIRTRUNK_SYD2": ("AirTrunk Australia", ["SYD2"]),
    "SITE_AIRTRUNK_MEL1": ("AirTrunk Australia", ["MEL1"]),
    "SITE_CDC_CANBERRA": ("Canberra Data Centres", ["H1", "H2", "H3", "H4", "H5", "F1", "F2"]),
    "SITE_CDC_EC": ("Canberra Data Centres", ["EC1", "EC2", "EC3", "EC4"]),
    # The record is named for the Brooklyn campus and does not list its buildings; the register
    # certifies Brooklyn 1. The quote says so, so a reader can see the scope.
    "SITE_CDC_BROOKLYN": ("Canberra Data Centres", ["Brooklyn 1"]),
    "SITE_DCI_SYD01": ("DCI Data Centers", ["SYD-01"]),
    "SITE_DR_ERSKINE": ("Digital Realty", ["SYD10", "SYD11", "SYD14"]),
    "SITE_DR_MEL11": ("Digital Realty", ["MEL11"]),
    "SITE_EQUINIX_CA1": ("Equinix Australia", ["CA1"]),
    "SITE_EQUINIX_SYD": ("Equinix Australia", ["SY3", "SY4", "SY5", "SY6", "SY7"]),
    "SITE_EQUINIX_PER": ("Equinix Australia", ["PE2", "PE3"]),
    "SITE_EQUINIX_MEL": ("Equinix Australia", ["ME1", "ME2", "ME4"]),
    "SITE_MACQ_FAIRBAIRN": ("Macquarie Technology Group", ["IC4", "IC5"]),
    "SITE_MACQ_IC12": ("Macquarie Technology Group", ["IC1", "IC2"]),
    "SITE_MACQ_IC3": ("Macquarie Technology Group", ["IC3"]),
    "SITE_NEXTDC_A1": ("NEXTDC", ["Adelaide 1"]),
    "SITE_NEXTDC_C1": ("NEXTDC", ["Canberra 1"]),
    "SITE_NEXTDC_D1": ("NEXTDC", ["Darwin 1"]),
    "SITE_NEXTDC_M123": ("NEXTDC", ["Melbourne 1", "Melbourne 2", "Melbourne 3"]),
    "SITE_NEXTDC_P12": ("NEXTDC", ["Perth 1", "Perth 2"]),
    "SITE_NEXTDC_S1": ("NEXTDC", ["Sydney 1"]),
    "SITE_NEXTDC_S2": ("NEXTDC", ["Sydney 2"]),
    "SITE_NEXTDC_S3": ("NEXTDC", ["Sydney 3"]),
    "SITE_TELSTRA_DEAKIN": ("Telstra", ["Deakin"]),
    "SITE_TELSTRA_STLEON": ("Telstra", ["St Leonards"]),
}


def page_text(raw: str) -> list[str]:
    """The page's visible lines, in order."""
    raw = re.sub(r"<(script|style)\b.*?</\1>", " ", raw, flags=re.S | re.I)
    raw = re.sub(r"<(br|/p|/li|/div|/h[1-6]|p|li|div|h[1-6])\b[^>]*>", "\n", raw, flags=re.I)
    text = html.unescape(re.sub(r"<[^>]+>", " ", raw))
    return [re.sub(r"\s+", " ", line).strip() for line in text.splitlines() if line.strip()]


def expand(facilities: str) -> list[str]:
    """ "Melbourne 1, 2 and 3" -> ["Melbourne 1", "Melbourne 2", "Melbourne 3"]. """
    out: list[str] = []
    stem = ""
    for token in re.split(r",\s*|\s+and\s+", facilities.strip().rstrip(".")):
        token = token.strip()
        if not token:
            continue
        if token.isdigit() and stem:
            out.append(f"{stem} {token}")
            continue
        m = re.fullmatch(r"(.*\D)\s+(\d+)", token)
        stem = m.group(1) if m else ""
        out.append(token)
    return out


def register(lines: list[str], errors: list[str]) -> dict[str, list[dict]]:
    """provider -> [{scope, line, facilities}] for the two data centre lists."""
    found: dict[str, list[dict]] = {}
    scope = None
    for line in lines:
        if line == FACILITY:
            scope = "facility"
            continue
        if line == ENCLAVE:
            scope = "enclave"
            continue
        if scope and line.startswith(END):
            break
        if not scope:
            continue
        parts = re.split(r"\s+[–-]\s+", line, maxsplit=1)
        if len(parts) != 2:
            errors.append(f"cannot read register line {line!r}")
            continue
        provider, facilities = parts
        found.setdefault(provider.strip(), []).append(
            dict(scope=scope, line=line, facilities=expand(facilities)))
    if not found:
        errors.append("the register's facility and enclave headings were not found")
    return found


def main() -> int:
    errors: list[str] = []
    raw = open(ARCHIVE, "rb").read()
    meta = json.load(open(ARCHIVE + ".meta.json"))
    if hashlib.sha256(raw).hexdigest() != meta["sha256"]:
        errors.append("archived register fails its SHA-256 check")
    entries = register(page_text(raw.decode("utf-8")), errors)

    rows = []
    matched = []
    for site, (provider, wanted) in sorted(MATCHES.items()):
        listed = entries.get(provider, [])
        hits = [e for e in listed if all(f in e["facilities"] for f in wanted)]
        if len(hits) != 1:
            errors.append(f"{site}: {provider} {wanted} is not listed once in the register "
                          f"(found {len(hits)})")
            continue
        e = hits[0]
        heading = FACILITY if e["scope"] == "facility" else ENCLAVE
        rows.append(dict(
            match=dict(id=site),
            fill=dict(hcf_certified="certified_strategic"),
            add_sources=[dict(id=SOURCE_ID, quote=f"{heading} {e['line']}")],
        ))
        matched.append(f"{site} ({e['scope']})")

    if errors:
        print("refusing to write; fix these first:", file=sys.stderr)
        for e in errors:
            print(f"  {e}", file=sys.stderr)
        return 1

    capture = meta["capture_utc"][:10]
    source = dict(
        id=SOURCE_ID,
        title="Certified Service Providers - Hosting Certification Framework",
        publisher="Department of Home Affairs (Hosting Certification Framework)",
        url=meta["original_url"],
        doc_type="primary_government",
        published=None,
        credibility="A",
        accessed=TODAY,
        notes=(f"The Commonwealth register of HCF-certified data centre facilities, enclaves and "
               f"cloud services. Read {TODAY} from the Internet Archive capture of {capture} "
               f"({meta['url']}), original HTML, SHA-256 {meta['sha256']}, archived at "
               f"data/raw/hcf/{os.path.basename(ARCHIVE)}; the live site refused automated "
               f"clients. Publisher from the page footer (Home Affairs logo). Lists the Strategic "
               f"level only, and states that new registrations are paused from 3 November 2025."),
    )
    gap = dict(
        id=96, pillar="C", priority=3, status="resolved", opened=TODAY, resolved_date=TODAY,
        question=("Which of the observatory's sites does the Commonwealth Hosting Certification "
                  "Framework register list as certified, and at what level?"),
        why_it_matters=("HCF certification decides which facilities may host Australian Government "
                        "data. Every certification value in the record rested on a grade-B market "
                        "directory, and 67 sites had none."),
        target_source=meta["original_url"],
        retrieval_method="manual_review",
        notes=(f"RESOLVED {TODAY}. Read the register's Certified Service Providers page (Internet "
               f"Archive capture of {capture}; the live site refused automated clients). It lists "
               f"Strategic facilities and enclaves only; no Assured facility is listed. "
               f"{len(matched)} site records match listed facilities, each on every facility the "
               f"record names: {', '.join(matched)}. All {len(matched)} already held "
               f"certified_strategic from SRC_CERTSTRAT; each now also cites the register, with "
               f"the register's line quoted. No site gained a value. The sites not listed keep "
               f"`unknown`: absence is not recorded as not_certified, because the register lists "
               f"only certified providers and new registrations have been paused since 3 November "
               f"2025. Not applied: AirTrunk SYD3 is not listed (AirTrunk's certified facilities "
               f"are SYD1, SYD2 and MEL1); Microsoft Azure is certified as a cloud service, which "
               f"is not a facility certification; DigiCo SYD1 is a certified enclave in the "
               f"existing facility, not the expansion project the site record describes."),
        fact_status="VERIFIED", source_id=SOURCE_ID, confidence="high", as_of_date=capture,
    )

    pack = {
        "pack_id": "hcf-register-2026-09",
        "prepared_by": "scripts/curate_hcf_register.py from data/raw/hcf/",
        "prepared_on": TODAY,
        "_comment": [
            "Confirms sites.hcf_certified against the Commonwealth HCF register (batch S3). Uses",
            "fill, so no existing value is overwritten; each matched site also cites the register",
            "with the register's own line quoted, which says whether the facility or an enclave",
            "within it is certified. Opens and resolves RG-096 with the search recorded.",
        ],
        "sources": [source],
        "rows": {"sites": rows, "research_gaps": [gap]},
    }
    with open(OUT_PACK, "w") as f:
        json.dump(pack, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print(f"register read: {sum(len(v) for v in entries.values())} provider lines; "
          f"{len(rows)} sites matched; wrote {os.path.relpath(OUT_PACK, ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
