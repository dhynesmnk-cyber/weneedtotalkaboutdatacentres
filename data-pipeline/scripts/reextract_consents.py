#!/usr/bin/env python3
"""
Re-extract text from the archived NSW consent PDFs. OFFLINE - no downloads.

Why this exists
---------------
The determination_date column of exports/nsw_planning/nsw_dc_consent_conditions.csv
was empty on all 20 rows (gap RG-079). Two root causes:
  1. consent_condition_audit.py parsed dates from "Date of decision"/"Determination Date"
     labels - which appear in Notices of Decision, not in consent instruments. Modern
     instruments carry the execution line on the COVER page as
     "Sydney 14 September 2026 File: EF24/10658", which no pattern matched.
  2. The extractor (scripts/pdf_text.py) cannot decrypt AES-encrypted PDFs: two
     instruments (lane_cove_west, macquarie_park) yielded 0 characters, so their
     battery rows were extraction-limited rather than evidence.

The PDFs themselves are intact: each was fetched 2026-09-18 13:36-13:38 UTC with its
SHA-256 recorded in <name>.pdf.meta.json, and each carries a %PDF header and a
%%EOF trailer. This script re-extracts from those archived PDFs using pypdf
(a real parser, handles AES via `cryptography`) and falls back to pdf_text.extract
only if pypdf is absent.

It also parses the cover/closing signature block: execution date, file reference,
the delegation relied on ("under delegation executed on 18 August 2026"), and the
signatory name and title.

Guarantees
----------
* Verifies each PDF against the SHA-256 in its meta.json before extracting.
* Never deletes: superseded .txt files are copied to consents/superseded_pdftext/
  (first backup wins, so re-runs cannot clobber the original archive copy).
* Records the extractor, char counts and re-extraction timestamp in meta.json.

Usage:  python3 scripts/reextract_consents.py [--verify-only]
"""
from __future__ import annotations

import argparse
import glob
import hashlib
import json
import os
import re
import shutil
import sys
from datetime import date, datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
from pdf_text import MIN_CHARS_PER_KB  # noqa: E402 - single reliability standard for the pipeline

CONSENTS = os.path.join(ROOT, "data", "raw", "nsw_planning", "consents")
SUPERSEDED = os.path.join(CONSENTS, "superseded_pdftext")

WEEKDAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
MONTHS = {m: i + 1 for i, m in enumerate(
    ["January", "February", "March", "April", "May", "June", "July",
     "August", "September", "October", "November", "December"])}

_MONTHS_ALT = "|".join(MONTHS)

# Primary anchor: the execution line "<D Month YYYY> File: <ref>". Works even when the
# "Sydney" prefix is separated from the date by the signature block (davis mod-1) or when
# the text layer is doubled ("9 October 20252025 File:" - apollo place).
FILE_DATE_RE = re.compile(rf"(\d{{1,2}}\s+(?:{_MONTHS_ALT})\s+20\d{{2}})\d*\s*File:\s*([A-Za-z0-9/\-\.]+)", re.I)
# Year-only variants (day/month image-stamped): "Sydney 2019 File: EF19/4251".
YEAR_FILE_RE = re.compile(r"Sydney\s+(20\d{2})\s+File:\s*([A-Za-z0-9/\-\.]+)", re.I)
# No File ref (turner, echidna): "Sydney 21 November 2025".
SYDNEY_RE = re.compile(rf"\bSydney\s+(\d{{1,2}}\s+(?:{_MONTHS_ALT})\s+20\d{{2}})", re.I)
DELEG_RE = re.compile(
    r"(?:As delegate of|delegate of|on behalf of)\s+(?:the\s+)?([A-Z][^\n]{3,90}?)"
    r"(?:\s+|\n\s*)under delegation(?:s)?\s*(?:made|executed|granted)?\s*(?:on\s+)?(\d{1,2}\s+[A-Za-z]+\s+20\d{2})?", re.I)
IPC_RE = re.compile(r"(Independent Planning Commission)[^\.]{0,80}?as the declared consent authority under (clause [^,\.]{2,60})", re.I)
SIGN_ON_BEHALF_RE = re.compile(
    r"Signed on behalf of the ([^\n]{3,80}?)(?:\s+pursuant to\s+|\n\s*pursuant to\s+)"
    r"delegations? under section\s*([\d\.A-Z]+)", re.I | re.S)
APPROVE_RE = re.compile(r"\b(?:I approve the|approves the|approve the|grant(?:ed)? (?:development )?consent)\b", re.I)
SCHED1_RE = re.compile(r"\bSCHEDULE\s*1\b")
NAME_RE = re.compile(r"^[A-Z][a-zA-Z'’\-]+(?:\s+[A-Z][a-zA-Z'’\-\.]+){1,2}$")
# Lines that look like person names but are org units, titles or template placeholders.
NOT_A_PERSON = re.compile(
    r"^(NSW Government|Department of|Independent Planning Commission|Member(s)? of|"
    r"\[.*\]|Sydney|Schedule|Development Consent|Section \d|These conditions|"
    r"(A/|Acting\s+)?(Director|Executive Director|Team Leader|Manager|Principal|Commissioner)\b|"
    r".*\b(Assessments|Commission|Government|Council|Department|Division|Branch|Services|"
    r"Industry|Sites|Resources|Energy|Regions|Compliance|Public Spaces|Secretariat)\s*$)", re.I)


def _normalize_head(txt: str, n: int = 9000) -> str:
    """Repair drop-cap line splits ('J\\noanna' -> 'Joanna', 'S\\nydney' -> 'Sydney') that
    pypdf emits when the first glyph of a line is separately positioned, then collapse
    whitespace. Applied to a parsing copy only - the archived .txt keeps raw output."""
    head = txt[:n]
    head = re.sub(r"(?<=[A-Za-z])\n(?=[a-z])", "", head)
    head = re.sub(r"(?<=[a-z])\n(?=[A-Z][a-z])", " ", head)
    return re.sub(r"[ \t]+", " ", head)


def _to_iso(d: int, mon: str, y: int) -> str | None:
    mon = mon.title()
    if mon not in MONTHS:
        return None
    try:
        return date(y, MONTHS[mon], d).isoformat()
    except ValueError:
        return None


def _iso_from(dstr: str) -> str:
    parts = dstr.split()
    return _to_iso(int(parts[0]), parts[1], int(parts[2])) or ""


def parse_execution(txt: str) -> dict:
    """The consent instrument's own execution details: date signed, file reference, and the
    delegation relied on. Deliberately does NOT fall back to bare 'dated <D Month YYYY>'
    matches: consent bodies quote dozens of report dates and a fallback silently captures
    the wrong one (verified against the 2026-09-18 archive: turner, echidna, poplars,
    apollo place all mis-parsed that way). Instruments whose text layer lacks the full
    execution line get execution_date='' with a note - the node metadata determination
    date is the fallback of record."""
    head = _normalize_head(txt)
    out: dict = {"execution_date": "", "execution_year": "", "execution_date_source": "",
                 "file_ref": "", "delegation_of": "", "delegation_executed": "",
                 "delegation_section": "", "parse_note": ""}
    m = FILE_DATE_RE.search(head)
    if m and (iso := _iso_from(m.group(1))):
        out.update(execution_date=iso, file_ref=m.group(2),
                   execution_date_source="cover:'<date> File:<ref>'")
    else:
        m = SYDNEY_RE.search(head)
        if m and (iso := _iso_from(m.group(1))):
            out.update(execution_date=iso, execution_date_source="cover:'Sydney <date>'")
        else:
            m = YEAR_FILE_RE.search(head)
            if m:
                out.update(execution_year=m.group(1), file_ref=m.group(2),
                           execution_date_source="cover:'Sydney <year> File:' (day/month image-stamped)",
                           parse_note="Day and month are in an image stamp, absent from the "
                                      "text layer; only the year is machine-readable.")
            else:
                out["parse_note"] = "No machine-readable execution line in the text layer."
    if not out["file_ref"]:
        m = re.search(r"\bFile:\s*([A-Z]{2,4}\d{2}[/\-]\d{3,8})", head)
        if m:
            out["file_ref"] = m.group(1)
            out["execution_date_source"] = out.get("execution_date_source") or "cover:'File:' ref only"
    m = DELEG_RE.search(head)
    if m:
        out["delegation_of"] = re.sub(r"\s+", " ", m.group(1)).strip()
        if m.group(2):
            out["delegation_executed"] = _iso_from(m.group(2)) or m.group(2)
    else:
        m = IPC_RE.search(head)
        if m:
            out["delegation_of"] = f"{m.group(1)} - declared consent authority under {m.group(2)}"
    m = SIGN_ON_BEHALF_RE.search(re.sub(r"\s+", " ", txt))
    if m:
        out["delegation_of"] = out["delegation_of"] or re.sub(r"\s+", " ", m.group(1)).strip()
        out["delegation_section"] = m.group(2)
    return out


def signatory(txt: str) -> dict:
    """Name/title of the person who signed the instrument. Scans the cover page between
    the approval sentence and SCHEDULE 1 for the first person-name line that is not an
    org unit, title or template placeholder."""
    head = _normalize_head(txt)
    lines = [l.strip() for l in head.split("\n") if l.strip()]
    start = 0
    for i, l in enumerate(lines):
        if APPROVE_RE.search(l):
            start = i
            break
    end = len(lines)
    for i in range(start, len(lines)):
        if SCHED1_RE.search(lines[i]):
            end = i
            break
    out = {"name": "", "title": "", "name_source": ""}
    for i in range(start, end):
        cand = lines[i]
        if NAME_RE.match(cand) and not NOT_A_PERSON.match(cand):
            out["name"] = cand
            out["name_source"] = "cover-block"
            titles = []
            for j in range(i + 1, min(i + 4, end)):
                if NAME_RE.match(lines[j]) and not NOT_A_PERSON.match(lines[j]):
                    break
                if re.match(r"^(A/|Acting\s)?(Director|Executive Director|Team Leader|Member|"
                            r"Manager|Principal|Commissioner)\b", lines[j], re.I) or \
                   re.search(r"\b(Assessments|Commission|Industry|Sites|Regions|Compliance|"
                             r"Energy|Resources|Public Spaces)\b", lines[j], re.I):
                    titles.append(lines[j])
                elif titles:
                    break
            out["title"] = " / ".join(titles)
            break
    if not out["name"]:
        placeholders = [l for l in lines[start:end] if l.startswith("[")]
        if placeholders:
            m = re.search(r"\[[^\]]+\]", placeholders[0])
            out.update(name=m.group(0) if m else placeholders[0],
                       name_source="template-placeholder")
    return out


def sha256(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def extract_pypdf(path: str) -> tuple[str, str]:
    import pypdf  # noqa: PLC0415
    import pypdf.__init__ as _pi  # noqa: PLC0415
    r = pypdf.PdfReader(path, strict=False)
    pages = []
    for p in r.pages:
        try:
            pages.append(p.extract_text() or "")
        except Exception as exc:  # noqa: BLE001 - one bad page must not lose the document
            pages.append(f"\n[[page extraction error: {exc}]]\n")
    return "\n".join(pages), f"pypdf-{pypdf.__version__}"


def extract_fallback(path: str) -> tuple[str, str]:
    sys.path.insert(0, os.path.join(ROOT, "scripts"))
    from pdf_text import extract  # noqa: PLC0415
    return extract(path, warn=False), "pdf_text(fallback)"


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--verify-only", action="store_true",
                    help="verify SHA-256 and report tail status without rewriting anything")
    a = ap.parse_args(argv)

    try:
        import pypdf  # noqa: F401
        extractor = "pypdf"
    except ImportError:
        extractor = "pdf_text"
        print("WARNING: pypdf not installed - falling back to pdf_text (degraded extractor)",
              file=sys.stderr)

    pdfs = sorted(glob.glob(os.path.join(CONSENTS, "*.pdf")))
    print(f"{len(pdfs)} archived consent PDFs; extractor={extractor}")
    results = []
    for pdf in pdfs:
        name = os.path.basename(pdf)[:-4]
        meta_p = pdf + ".meta.json"
        txt_p = os.path.join(CONSENTS, name + ".txt")
        meta = json.load(open(meta_p)) if os.path.exists(meta_p) else {}
        digest = sha256(pdf)
        ok_sha = (meta.get("sha256") == digest) if meta else None
        tail = ""
        if os.path.exists(txt_p):
            with open(txt_p, encoding="utf-8", errors="replace") as fh:
                fh.seek(0)
                data = fh.read()
            tail = "signature-block" if re.search(r"Dated\s*:", data[-4000:], re.I) else "TRUNCATED"
            if len(data) == 0:
                tail = "EMPTY"
        print(f"  {name[:56]:58s} sha256={'OK' if ok_sha else 'MISMATCH' if ok_sha is False else 'no-meta':8s}"
              f" tail={tail}")
        if not ok_sha:
            results.append({"project": name, "sha_ok": bool(ok_sha), "skipped": "sha mismatch"})
            continue
        if a.verify_only:
            results.append({"project": name, "sha_ok": True, "tail_before": tail})
            continue

        if extractor == "pypdf":
            txt, ex_name = extract_pypdf(pdf)
        else:
            txt, ex_name = extract_fallback(pdf)

        # backup the superseded extraction (never delete archived material; keep the FIRST
        # backup - the 13:36 pdf_text output - even if this script is re-run)
        if os.path.exists(txt_p) and os.path.getsize(txt_p) > 0:
            os.makedirs(SUPERSEDED, exist_ok=True)
            dst = os.path.join(SUPERSEDED, name + ".txt")
            if not os.path.exists(dst):
                shutil.copy2(txt_p, dst)
        with open(txt_p, "w", encoding="utf-8") as fh:
            fh.write(txt)

        d = parse_execution(txt)
        s = signatory(txt)
        kb = max(1, os.path.getsize(pdf)) // 1024
        ratio = round(len(txt) / kb, 1)
        meta["extraction"] = {"chars": len(txt), "kb": kb, "chars_per_kb": ratio,
                              "reliable": ratio >= MIN_CHARS_PER_KB}
        meta["reextracted_utc"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
        meta["extractor"] = ex_name
        meta["extraction_note"] = ("Re-extracted with pypdf after the 2026-09-18 13:36 pdf_text "
                                   "run degraded 18 of 20 texts and yielded 0 chars on 2. PDF "
                                   "sha256 verified against the fetch-time manifest first.")
        json.dump(meta, open(meta_p, "w"), indent=1)

        results.append({"project": name, "sha_ok": True, "chars": len(txt),
                        "chars_per_kb": ratio, "reliable": meta["extraction"]["reliable"],
                        "execution": d, "signatory": s})
        wd = d.get("weekday_matches")
        print(f"    -> {len(txt):>8,} chars  {ratio:>5.1f} c/KB  exec={d.get('execution_date') or '-':10s}"
              f" ({(d.get('execution_date_source') or '-')[:7]}) wd={str(wd):5s}"
              f" deleg={d.get('delegation_executed') or '-':10s} signed_by={s.get('name') or '?'}")

    out = os.path.join(ROOT, "exports", "nsw_planning", "reextraction_report.json")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    json.dump({"run_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
               "extractor": extractor, "results": results}, open(out, "w"), indent=1)
    print(f"\nwrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
