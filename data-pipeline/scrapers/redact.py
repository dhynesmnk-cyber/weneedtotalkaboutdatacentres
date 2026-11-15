#!/usr/bin/env python3
"""
Strip third-party credentials from a fetched page before it is archived.

An archived page is a snapshot of someone else's site, and those sites embed their own
credentials: the NSW Planning Portal and the Independent Planning Commission both ship a
Google Maps browser key, and Penrith's consultation platform ships a session token in its
page settings. None of it is ours. It was already public on their site, but committing it
here republishes another party's credential and trips secret scanners — Netlify's smart
detection reads repository code, not just the published build, so an archived page under
data/raw/ fails the site build even though the site never serves it.

This lives in one module because the lesson of 2026-09-18 is that a redaction applied to
one scraper is not a redaction. That fix went into ingest_nsw_planning.py; the pages
archived later by archive_pages.py (Penrith, Talavera Road) went straight to disk with
their keys intact, and took the production deploy down with them.

Redaction happens BEFORE anything is written, so the credential never reaches disk. The
caller hashes the bytes it actually stores and keeps the upstream digest alongside them,
so the manifest never claims the stored file is byte-identical to what the server sent.

Nothing here redacts an archive that is already committed. Where a redaction would touch a
hash-verified document, redact nothing and raise it instead (data-pipeline/README.md).

Run the fixtures: python3 scrapers/redact.py --selftest
"""
from __future__ import annotations

import re
import sys

GOOGLE_KEY = b"REDACTED-THIRD-PARTY-GOOGLE-MAPS-API-KEY"
PAGE_TOKEN = b"REDACTED-THIRD-PARTY-PAGE-TOKEN"

# Google browser keys are "AIza" followed by 35 characters. The portal's begin "AIzaSy",
# which the narrower 2026-09-18 pattern matched; this covers the rest of the family too.
#
# The token pattern is deliberately anchored to a JSON/JS key named token or authtoken.
# A bare JWT pattern would be too blunt for an archive: it would rewrite any long base64
# triple it found, including ones that are part of the evidence rather than a credential.
REDACTIONS: tuple[tuple[re.Pattern[bytes], bytes, bytes], ...] = (
    (re.compile(rb"AIza[0-9A-Za-z_-]{35}"), GOOGLE_KEY, GOOGLE_KEY),
    (re.compile(rb"""(["'](?:auth)?token["']\s*:\s*["'])(eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,})""",
                re.I),
     rb"\1" + PAGE_TOKEN, PAGE_TOKEN),
)


def redact(body: bytes) -> tuple[bytes, list[str]]:
    """The body to store, and the labels of what was removed.

    Labels carry a count, so a manifest records how many credentials a page shipped rather
    than merely that it shipped one.
    """
    applied: list[str] = []
    for pattern, replacement, label in REDACTIONS:
        body, count = pattern.subn(replacement, body)
        if count:
            applied.append(f"{label.decode()} x{count}")
    return body, applied


def redact_text(text: str) -> tuple[str, list[str]]:
    """The same rules for text that has already been decoded (a PDF's extracted pages).

    A PDF's own bytes are never rewritten: replacing a string inside a PDF breaks its
    cross-reference offsets. Its extracted text is derived, so that is what is cleaned.
    """
    body, applied = redact(text.encode("utf-8"))
    return body.decode("utf-8"), applied


def _selftest() -> int:
    """Fixtures. Keys are assembled at run time so no literal credential sits in this file
    for the repository's own secret check to find."""
    key = b"AIza" + b"S" * 35
    token = b"eyJ" + b"a" * 12 + b"." + b"b" * 12 + b"." + b"c" * 12
    failures: list[str] = []

    def check(label: str, got: object, want: object) -> None:
        if got != want:
            failures.append(f"{label}: got {got!r}, want {want!r}")

    # A portal page: the key sits in a script src and in a settings block. Both go.
    page = b'<script src="https://maps.googleapis.com/maps/api/js?key=' + key + b'"></script>'
    body, applied = redact(page)
    check("portal key removed", key in body, False)
    check("portal sentinel present", GOOGLE_KEY in body, True)
    check("portal label", applied, [f"{GOOGLE_KEY.decode()} x1"])
    check("surrounding markup intact", body.startswith(b'<script src="https://maps.googleapis.com'), True)

    # Two occurrences are counted, not collapsed.
    body, applied = redact(page + b"\n" + page)
    check("two keys counted", applied, [f"{GOOGLE_KEY.decode()} x2"])

    # A consultation platform's session token, in both quote styles.
    for quoted in (b'"token":"' + token + b'"', b"'authtoken': \"" + token + b'"'):
        body, applied = redact(quoted)
        check("token removed", token in body, False)
        check("token key kept", b"token" in body, True)
        check("token label", applied, [f"{PAGE_TOKEN.decode()} x1"])

    # A long base64 triple that is NOT under a token key is evidence, not a credential.
    innocent = b'<p data-evidence="' + token + b'">a quoted figure</p>'
    body, applied = redact(innocent)
    check("innocent triple untouched", body, innocent)
    check("innocent unlabelled", applied, [])

    # Ordinary pages pass through byte for byte.
    plain = b"<h1>Talavera Road</h1><p>132 MW, stage 1.</p>"
    check("plain page untouched", redact(plain), (plain, []))

    # The text path, used for a PDF's extracted pages.
    text, applied = redact_text("page 1\nkey=" + key.decode() + "\n")
    check("text key removed", key.decode() in text, False)
    check("text label", applied, [f"{GOOGLE_KEY.decode()} x1"])

    # A near miss must not be eaten: 34 characters is not a key.
    short = b"AIza" + b"S" * 34
    check("short near miss untouched", redact(short), (short, []))

    for failure in failures:
        print(f"FAIL {failure}", file=sys.stderr)
    print(f"redact selftest: {len(failures)} failure(s)")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(_selftest() if "--selftest" in sys.argv[1:] else 0)
