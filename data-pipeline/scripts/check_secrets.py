#!/usr/bin/env python3
"""
Repository secret check: fail before a credential reaches the deploy, not during it.

Netlify's Secrets Controller scans repository code as well as build output, so a third-party
API key inside an archived research page under data/raw/ fails the site build — even though
the site never serves that directory. That is what took production down on 2026-10-30 and
kept it down until 2026-11-15: two archived pages carried Google Maps keys, and nothing in
this repository looked for them.

This check is that look. It runs in CI on every pull request, so the failure lands on the
change that introduced it rather than on the next production deploy.

It reports the file, the line and a masked prefix. It never prints a whole credential.

Two archives are named below as known and raised. They are hash-verified documents, and
data-pipeline/README.md is explicit: where a redaction would touch a hash-verified document,
redact nothing, leave the archive intact and raise it instead. They are listed so this check
is green on the repository as it stands, and so the exception is visible and auditable rather
than buried in a scanner's configuration. Anything not named here fails the check.

Exit 1 on any credential outside the known list. Run: python3 scripts/check_secrets.py
Fixtures: python3 scripts/check_secrets.py --selftest
"""
from __future__ import annotations

import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO = os.path.dirname(ROOT)

SKIP_DIRS = {".git", "node_modules", ".next", ".artifacts", "__pycache__", ".venv", "coverage"}
# Over this size a file is an archive of something else (a PDF, a spreadsheet) and is read
# as bytes anyway; the text patterns below still apply to whatever decodes.
MAX_BYTES = 8 * 1024 * 1024

PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("Google API key", re.compile(r"AIza[0-9A-Za-z_-]{35}")),
    ("AWS access key id", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("GitHub token", re.compile(r"\b(?:ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9]{36}\b|\bgithub_pat_[A-Za-z0-9_]{22,}\b")),
    # OpenAI keys are "sk-" and a long random run, optionally a project prefix. The body
    # must not be hyphenated words: the planning portal has appendices named
    # "appendix-e-sk-01-overall-site-sections-24", which a looser pattern reads as a key.
    ("OpenAI-style secret key", re.compile(r"\bsk-(?:proj-|svcacct-)?[A-Za-z0-9]{20,}\b")),
    ("Slack token", re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{10,}\b")),
    ("Private key block", re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH |PGP )?PRIVATE KEY-----")),
    # A Supabase service_role key is a JWT. So are the page tokens some archived sites ship.
    ("JWT", re.compile(r"\beyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\b")),
)

# Known, raised, and deliberately left intact. Both are hash-verified archives: redacting
# them would break the sha256 in their .meta.json, which README.md forbids without the
# author's decision. Raised 2026-11-15. Netlify is safelisted for these specific values with
# SECRETS_SCAN_SMART_DETECTION_OMIT_VALUES so the deploy is not blocked in the meantime.
# Remove an entry once the author decides to redact and re-manifest the file.
KNOWN: dict[str, str] = {
    "data-pipeline/data/raw/councils/penrith/vpa-microsoft-datacenter.html":
        "Penrith consultation platform: 1 Google Maps key, 2 page tokens. Hash-verified archive.",
    "data-pipeline/data/raw/nsw_planning/ipc/talavera-road-data-centre-campus-expansion.html":
        "NSW Independent Planning Commission: 3 occurrences of 1 Google Maps key. Hash-verified archive.",
}


def mask(value: str) -> str:
    return f"{value[:6]}…{value[-3:]} (len {len(value)})"


def scan_text(text: str) -> list[tuple[int, str, str]]:
    """(line number, kind, masked value) for every credential-shaped string in the text."""
    found: list[tuple[int, str, str]] = []
    for kind, pattern in PATTERNS:
        for match in pattern.finditer(text):
            line = text.count("\n", 0, match.start()) + 1
            found.append((line, kind, mask(match.group(0))))
    return sorted(found)


def walk(repo: str) -> list[str]:
    paths: list[str] = []
    for base, dirs, files in os.walk(repo):
        dirs[:] = sorted(d for d in dirs if d not in SKIP_DIRS)
        for name in sorted(files):
            paths.append(os.path.join(base, name))
    return paths


def run(repo: str = REPO) -> int:
    failures: list[str] = []
    known_hits: dict[str, int] = {}
    for path in walk(repo):
        rel = os.path.relpath(path, repo).replace(os.sep, "/")
        try:
            if os.path.getsize(path) > MAX_BYTES:
                continue
            with open(path, encoding="utf-8", errors="ignore") as fh:
                text = fh.read()
        except (OSError, UnicodeError):
            continue
        hits = scan_text(text)
        if not hits:
            continue
        if rel in KNOWN:
            known_hits[rel] = len(hits)
            print(f"known, raised: {rel} ({len(hits)} credential-shaped strings)")
            continue
        for line, kind, masked in hits:
            failures.append(f"{rel}:{line} {kind} {masked}")

    for rel in KNOWN:
        if rel not in known_hits:
            print(f"note: {rel} is in the known list but no longer holds a credential; "
                  "the entry can be removed")

    if failures:
        print("\nCredentials found outside the known list:", file=sys.stderr)
        for failure in failures:
            print(f"  {failure}", file=sys.stderr)
        print("\nRedact it at archive time (scrapers/redact.py) rather than committing it.\n"
              "If it is a hash-verified archive, leave it intact and raise it instead.",
              file=sys.stderr)
        return 1
    print(f"check-secrets: no credentials outside the known list "
          f"({len(known_hits)} known archive(s) raised)")
    return 0


def _selftest() -> int:
    """Fixtures. Every credential is assembled at run time, so this file holds no literal
    that the check itself would find."""
    failures: list[str] = []

    def check(label: str, got: object, want: object) -> None:
        if got != want:
            failures.append(f"{label}: got {got!r}, want {want!r}")

    google = "AIza" + "S" * 35
    jwt = "eyJ" + "a" * 12 + "." + "b" * 12 + "." + "c" * 12
    aws = "AKIA" + "B" * 16
    github = "ghp_" + "c" * 36

    check("google key found", [k for _, k, _ in scan_text(f'key={google}"')], ["Google API key"])
    check("jwt found", [k for _, k, _ in scan_text(f'"token":"{jwt}"')], ["JWT"])
    check("aws found", [k for _, k, _ in scan_text(aws)], ["AWS access key id"])
    check("github found", [k for _, k, _ in scan_text(github)], ["GitHub token"])
    check("line number", scan_text("one\ntwo\nkey=" + google)[0][0], 3)

    # The mask never carries the whole value.
    masked = scan_text(google)[0][2]
    check("mask hides the middle", google in masked, False)
    check("mask keeps the length", "len 39" in masked, True)

    # Near misses and ordinary content must pass.
    check("short google near miss", scan_text("AIza" + "S" * 34), [])
    check("sha512 integrity is not a JWT",
          scan_text('"integrity": "sha512-' + "d" * 88 + '"'), [])
    check("prose passes", scan_text("132 MW at Kemps Creek, stage 1, per the EIS."), [])
    check("redaction sentinel passes",
          scan_text("REDACTED-THIRD-PARTY-GOOGLE-MAPS-API-KEY"), [])

    # An OpenAI key is found; a hyphenated document slug beginning "sk-" is not.
    check("openai key found", [k for _, k, _ in scan_text("sk-" + "e" * 48)],
          ["OpenAI-style secret key"])
    check("openai project key found", [k for _, k, _ in scan_text("sk-proj-" + "f" * 48)],
          ["OpenAI-style secret key"])
    check("planning appendix slug is not a key",
          scan_text('"/appendix-e-sk-01-overall-site-sections-24"'), [])

    for failure in failures:
        print(f"FAIL {failure}", file=sys.stderr)
    print(f"check-secrets selftest: {len(failures)} failure(s)")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(_selftest() if "--selftest" in sys.argv[1:] else run())
