#!/usr/bin/env python3
"""
Archive the public ownership documents on NSW data centre applications (research batch 1).

An application's owner's consent letter and title documents name who owns the land and, often,
who the applicant acts for. They are listed in the attachment index the portal harvest built
(exports/nsw_planning/nsw_dc_attachment_index.csv). This fetches only the attachments named in
WANTED, one at a time, through the same portal JSON the SSD document fetcher uses: a document the
portal marks not public, or answers 401 or 403 for, is recorded as restricted and never fetched
another way.

Archive (data/raw/nsw_planning/ownership/):
  <case>__<attachment>.pdf            not committed; the manifest's url and sha256 re-fetch it
  <case>__<attachment>.pdf.meta.json  url, slugs, label, folder, fetched_utc, sha256, bytes, pages
  <case>__<attachment>.txt            the text, one "[[page N]]" marker per page, with personal
                                      contact details redacted
  restricted.json                     every attachment the portal refused, and how

Usage:
    python3 scrapers/fetch_ownership_documents.py --list   # the plan, no network
    python3 scrapers/fetch_ownership_documents.py          # fetch what is not yet archived
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import time
import urllib.error
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fetch_ssd_documents import DELAY, MAX_BYTES, UA, extract, get, redact, resolve  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "data", "raw", "nsw_planning", "ownership")

# (case, project slug, attachment slug, research question). Chosen by reading the attachment
# index for the questions in docs/RESEARCH-PLAN.md story line M1.
WANTED = [
    ("SSD-73761707", "glendenning-road-data-centre", "appendix-03-title-documents-36", "RG-037"),
    ("SSD-73761707", "glendenning-road-data-centre", "owners-consent-6713", "RG-037"),
    ("SSD-92743706", "mamre-road-data-centre-campus", "appendix-3-title-documents-388", "RG-021"),
    ("SSD-92743706", "mamre-road-data-centre-campus", "ifm-owners-consent-mamre-road", "RG-021"),
    ("SSD-92743706", "mamre-road-data-centre-campus", "gpt-owners-consent-mamre-road", "RG-021"),
    ("SSD-92743706", "mamre-road-data-centre-campus", "gibb-group-owners-consent-mamre-road", "RG-021"),
    ("SSD-59416728", "davis-road-data-centre-cundall", "appendix-3-title-documents-310", "RG-057"),
    ("SSD-59416728", "davis-road-data-centre-cundall", "land-owners-consent-letter-226", "RG-057"),
    ("SSD-59416728", "davis-road-data-centre-cundall", "asics-certificate-amazon-corporate-services-pty-ltd-62",
     "RG-057"),
    ("SSD-67407231", "apollo-place-data-centre", "landowner-consents-60", "RG-064"),
    ("SSD-67407231", "apollo-place-data-centre", "appendix-05-survey-plan-title-documents-60", "RG-064"),
    ("SSD-41589232", "51-huntingwood-drive-data-centre", "ssd-41589232-letter-landowner-psims-53", "RG-064"),
    ("SSD-64287712", "dci-poplars-data-centre-project-0", "xlandowners-consent-188", "RG-059"),
    ("SSD-21342738", "eastern-creek-data-centre-expansion-project", "xlandowners-consent-175", "RG-059"),
    ("SSD-71368959", "project-duke-data-centre", "landowners-consent-4148", "RG-035"),
    ("SSD-71368959", "project-duke-data-centre", "landowners-consentpoa-62", "RG-035"),
    ("SSD-82052708", "project-mars-data-centre", "appendix-g-owners-consent-35", "RG-035"),
]


def base(case: str, attachment: str) -> str:
    return os.path.join(OUT, f"{case}__{attachment}")


def fetch_one(case: str, project: str, attachment: str, restricted: dict) -> str:
    time.sleep(DELAY)
    meta = resolve(attachment)
    if meta is None:
        restricted[attachment] = dict(case=case, project_slug=project, how="401 or 403 on the portal's JSON",
                                      checked_utc=datetime.now(timezone.utc).isoformat(timespec="seconds"))
        return "restricted (401/403)"
    if meta["public"] is False or not meta["uri"]:
        restricted[attachment] = dict(case=case, project_slug=project, how="marked not public",
                                      label=meta["label"], folder=meta["folder"],
                                      checked_utc=datetime.now(timezone.utc).isoformat(timespec="seconds"))
        return "restricted (not public)"
    time.sleep(DELAY)
    try:
        body = get(meta["uri"], limit=MAX_BYTES)
    except urllib.error.HTTPError as exc:
        restricted[attachment] = dict(case=case, project_slug=project, how=f"HTTP {exc.code} on the file",
                                      label=meta["label"],
                                      checked_utc=datetime.now(timezone.utc).isoformat(timespec="seconds"))
        return f"restricted (HTTP {exc.code})"
    if not body.startswith(b"%PDF"):
        return "not a PDF; skipped"
    b = base(case, attachment)
    os.makedirs(OUT, exist_ok=True)
    with open(b + ".pdf", "wb") as fh:
        fh.write(body)
    text, extractor = extract(b + ".pdf")
    text, redactions = redact(text)
    with open(b + ".txt", "w", encoding="utf-8") as fh:
        fh.write(text)
    json.dump(dict(
        url=meta["uri"], case=case, project_slug=project, attachment_slug=attachment, label=meta["label"],
        folder=meta["folder"], fetched_utc=datetime.now(timezone.utc).isoformat(timespec="seconds"),
        sha256=hashlib.sha256(body).hexdigest(), bytes=len(body), user_agent=UA, extractor=extractor,
        chars=len(text), pages=text.count("[[page "), text_redactions=redactions, pdf_committed=False,
    ), open(b + ".pdf.meta.json", "w"), indent=1)
    return f"archived ({len(body) // 1024} KB, {text.count('[[page ')} pages, {len(text.strip())} chars)"


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--list", action="store_true", help="show the plan; no network")
    a = ap.parse_args(argv)
    path = os.path.join(OUT, "restricted.json")
    restricted = json.load(open(path)) if os.path.exists(path) else {}
    for case, project, attachment, question in WANTED:
        done = os.path.exists(base(case, attachment) + ".txt")
        if a.list:
            state = "archived" if done else "restricted" if attachment in restricted else "to fetch"
            print(f"{question}  {case}  {attachment}: {state}")
            continue
        if done or attachment in restricted:
            continue
        print(f"{question}  {case}  {attachment}: {fetch_one(case, project, attachment, restricted)}", flush=True)
        os.makedirs(OUT, exist_ok=True)
        json.dump(restricted, open(path, "w"), indent=1, sort_keys=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
