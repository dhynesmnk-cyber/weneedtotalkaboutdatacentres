#!/usr/bin/env python3
"""
Archive the one document per NSW SSD data centre project that states its figures (batch S2).

For each of the 46 State Significant Development records archived under
data/raw/nsw_planning/nodes/, pick the document most likely to state capital investment value,
jobs, floor area, capacity, cooling, water and grid connection, and archive it:

  determined projects   the Department's assessment report (its project summary states them)
  in assessment, RTS    the environmental impact statement, main volume
  preparing an EIS      the scoping report, else the request for SEARs

Candidates come from the node's own attachment list. Each is resolved through the portal's JSON
(`<slug>?_format=json`), which names the file, its folder and whether it is public. A document the
portal marks not public, or answers 401 for, is skipped and the next candidate tried: restricted
material is never fetched another way.

Polite and single-threaded, as scrapers/ingest_nsw_dc.py: one request at a time, a pause between,
a descriptive User-Agent. Re-running is offline for anything already archived.

Archive (data/raw/nsw_planning/documents/):
  <case>_<kind>.pdf            the document; not committed (re-fetch from the manifest's url, and
                               check it against the manifest's sha256)
  <case>_<kind>.pdf.meta.json  url, slug, label, folder, fetched_utc, sha256, bytes, extractor
  <case>_<kind>.txt            the text, one "[[page N]]" marker per page, so a quote can cite it,
                               with personal contact details (names in contact fields, emails,
                               mobile numbers) redacted

The manifest's sha256 lets a PDF that is not committed be re-fetched and verified.

Usage:
    python3 scrapers/fetch_ssd_documents.py --list       # the plan, no network
    python3 scrapers/fetch_ssd_documents.py --limit 5    # fetch the first five not yet archived
    python3 scrapers/fetch_ssd_documents.py              # fetch everything not yet archived

Needs pypdf, and cryptography for the portal's AES-encrypted PDFs.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
from curate_site_coordinates import NODES, first, read_nodes  # noqa: E402

OUT = os.path.join(ROOT, "data", "raw", "nsw_planning", "documents")
BASE = "https://www.planningportal.nsw.gov.au"
UA = ("ADCO-research/1.0 (Australian Data Centre Observatory; open public-interest research "
      "database; single-threaded polite crawler; stop on request)")
DELAY = 3.0
MAX_BYTES = 120 * 1024 * 1024
# PDFs are not committed: forty of them would add some 100 MB to the repository, and each can be
# re-fetched from its manifest's url and checked against its sha256. The text, which is what every
# quote is checked against, is committed.
PDF_COMMIT_LIMIT = 0

# (kind, slug pattern, label pattern the resolved file must match). Earlier kinds are preferred
# for a determined project; the stage decides where the search starts.
NOT_MAIN = re.compile(r"appendix|attachment|response|council|epa|agency|letter|cover|draft|"
                      r"submission|mod-?\d|modification|addendum|amend|revised|supplementary|"
                      r"tfnsw|heritage|fire|cphr|dpe-|water-nsw|endeavour|ausgrid|hnsw|frnsw|"
                      r"(^|-)ach(-|$)|traffic|(^|-)app-?\d", re.I)
# A resolved file is rejected if its label or folder says it is not the project's own document:
# agency advice filed against the EIS, or an appendix whose title happens to contain the words.
NOT_MAIN_FILE = re.compile(r"^(HNSW|FRNSW|EPA|TfNSW|DPE|DPHI|Council)\b|\bApp(endix)?\.?\s*\d|"
                           r"traffic|heritage|response", re.I)
NOT_MAIN_FOLDER = {"Agency Advice", "Submissions", "Response to Submissions"}
KINDS = [
    ("assessment", re.compile(r"assessment-report", re.I), re.compile(r"assessment report", re.I)),
    ("eis", re.compile(r"(^|-)environmental-impact-statement|(^|-)eis(-|$)", re.I),
     re.compile(r"environmental impact statement|\beis\b", re.I)),
    ("scoping", re.compile(r"scoping-report", re.I), re.compile(r"scoping", re.I)),
    ("sears_request", re.compile(r"request.{0,30}sears", re.I), re.compile(r"request|sears|scoping", re.I)),
]
START = {"Determination": 0, "Assessment": 1, "Response to Submissions": 1, "Withdrawn": 1}


def get(url: str, timeout: int = 240, limit: int | None = None) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        # read() with no argument: read(-1) skips chunked-transfer decoding in http.client.
        body = resp.read(limit + 1) if limit else resp.read()
    if limit and len(body) > limit:
        raise ValueError(f"larger than {limit} bytes")
    return body


def candidates(node: dict, start: int) -> list[tuple[str, str, re.Pattern]]:
    slugs = [(a.get("url") or "").strip("/") for a in (node.get("field_attachment") or [])]
    out = []
    for kind, pattern, label in KINDS[start:]:
        out += [(kind, s, label) for s in slugs if pattern.search(s) and not NOT_MAIN.search(s)]
    return out


def resolve(slug: str) -> dict | None:
    try:
        j = json.loads(get(f"{BASE}/{slug}?_format=json", timeout=90))
    except urllib.error.HTTPError as exc:
        if exc.code in (401, 403):
            return None
        raise
    g = lambda k: (j.get(k) or [{}])[0]  # noqa: E731
    return dict(uri=g("field_content_url").get("uri"), public=g("field_is_public").get("value"),
                folder=g("field_folder_name").get("value"), label=g("field_label").get("value"))


# Personal contact details a lodgement form or a document control page carries. The portal publishes
# them, but this archive is committed, and committing them would republish a person's details for no
# research purpose. Company names and ABNs are kept: they identify the applicant.
CONTACT_LABEL = re.compile(r"^(First Name|Last Name|Phone|Mobile|Email)\s*$", re.I | re.M)
EMAIL = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
MOBILE = re.compile(r"(?<!\d)(?:\+?61\s?|0)4\d{2}\s?\d{3}\s?\d{3}(?!\d)")


def redact(text: str) -> tuple[str, int]:
    """Text with personal contact details replaced, and how many replacements were made."""
    lines = text.split("\n")
    n = 0
    for i, line in enumerate(lines[:-1]):
        if CONTACT_LABEL.match(line.strip()) and lines[i + 1].strip():
            lines[i + 1] = "[redacted]"
            n += 1
    text = "\n".join(lines)
    text, k = EMAIL.subn("[email redacted]", text)
    text, m = MOBILE.subn("[mobile redacted]", text)
    return text, n + k + m


def extract(path: str) -> tuple[str, str]:
    import pypdf  # noqa: PLC0415
    reader = pypdf.PdfReader(path, strict=False)
    pages = []
    for i, page in enumerate(reader.pages, start=1):
        try:
            text = page.extract_text() or ""
        except Exception as exc:  # noqa: BLE001 - one bad page must not lose the document
            text = f"[[page extraction error: {exc}]]"
        pages.append(f"[[page {i}]]\n{text}")
    return "\n".join(pages), f"pypdf-{pypdf.__version__}"


def plan() -> list[dict]:
    errors: list[str] = []
    out = []
    for n in sorted(read_nodes(errors), key=lambda r: r["case_id"]):
        node = json.load(open(os.path.join(NODES, n["slug"] + ".json")))
        stage = first(node, "field_case_stage").get("value") or ""
        out.append(dict(case=n["case_id"], slug=n["slug"], stage=stage,
                        candidates=candidates(node, START.get(stage, 2))))
    if errors:
        raise SystemExit("refusing: " + "; ".join(errors))
    return out


def archived(case: str) -> str | None:
    for kind, _, _ in KINDS:
        if os.path.exists(os.path.join(OUT, f"{case}_{kind}.txt")):
            return kind
    return None


def fetch(item: dict) -> str:
    for kind, slug, label in item["candidates"]:
        time.sleep(DELAY)
        meta = resolve(slug)
        if not meta or not meta["uri"] or meta["public"] is False:
            continue
        if not label.search(meta["label"] or ""):
            continue
        if NOT_MAIN_FILE.search(meta["label"] or "") or meta["folder"] in NOT_MAIN_FOLDER:
            continue
        time.sleep(DELAY)
        try:
            body = get(meta["uri"], limit=MAX_BYTES)
        except (urllib.error.HTTPError, ValueError) as exc:
            print(f"  {item['case']}: {slug} not fetched ({exc})", file=sys.stderr)
            continue
        if not body.startswith(b"%PDF"):
            continue
        base = os.path.join(OUT, f"{item['case']}_{kind}")
        os.makedirs(OUT, exist_ok=True)
        with open(base + ".pdf", "wb") as fh:
            fh.write(body)
        try:
            text, extractor = extract(base + ".pdf")
        except Exception as exc:  # noqa: BLE001 - report and move on; the PDF stays for a retry
            print(f"  {item['case']}: {slug} fetched but not extracted ({exc})", file=sys.stderr)
            return "fetched, extraction failed"

        text, redactions = redact(text)
        with open(base + ".txt", "w", encoding="utf-8") as fh:
            fh.write(text)
        json.dump(dict(
            url=meta["uri"], project_slug=item["slug"], attachment_slug=slug, kind=kind,
            label=meta["label"], folder=meta["folder"],
            fetched_utc=datetime.now(timezone.utc).isoformat(timespec="seconds"),
            sha256=hashlib.sha256(body).hexdigest(), bytes=len(body), user_agent=UA,
            extractor=extractor, chars=len(text), pages=text.count("[[page "),
            text_redactions=redactions,
            # A lodgement form's PDF carries the contact details redacted from its text.
            pdf_committed=len(body) <= PDF_COMMIT_LIMIT and kind != "sears_request",
        ), open(base + ".pdf.meta.json", "w"), indent=1)
        return f"{kind} ({len(body) // 1024} KB, {text.count('[[page ')} pages)"
    return "nothing public found"


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--list", action="store_true", help="show the plan; no network")
    ap.add_argument("--limit", type=int, help="fetch at most this many projects")
    a = ap.parse_args(argv)

    items = plan()
    done = 0
    for item in items:
        have = archived(item["case"])
        if a.list:
            kinds = sorted({k for k, _, _ in item["candidates"]})
            print(f"{item['case']:<15} {item['stage'][:24]:<24} "
                  f"{'archived: ' + have if have else 'candidates: ' + ', '.join(kinds) or 'none'}")
            continue
        if have:
            continue
        if a.limit is not None and done >= a.limit:
            break
        print(f"{item['case']}: {fetch(item)}", flush=True)
        done += 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
