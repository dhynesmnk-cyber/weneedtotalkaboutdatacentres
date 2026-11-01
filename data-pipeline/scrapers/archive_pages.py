#!/usr/bin/env python3
"""
Archive a list of public web pages with SHA-256 manifests (batch S4: operators' own pages).

The operator's own facility page is the primary source for facts about the operator's own asset:
where it is, what it is called, who runs it. This archives the pages a curation reads, so every
value it takes can be checked against the page as it was read, and the page re-read later.

Polite, single-threaded, a pause between requests, a descriptive User-Agent; robots.txt is read
first and any disallowed URL is refused. Re-running skips pages already archived.

Archive: data/raw/operators/<group>/<name>.html, .html.meta.json (url, fetched_utc, sha256, bytes),
and .txt: the page's visible text, one line per block, with scripts and styles removed. A PDF is kept
as <name>.pdf and .pdf.meta.json, its .txt extracted page by page with "[[page N]]" markers. The text is
what a curation quotes from; the HTML is kept so the text can be regenerated. A CSV (a super fund's
portfolio holdings disclosure) is kept as <name>.csv and .csv.meta.json; the CSV is its own text.

A site that answers 401, 403 or 429, or serves a bot-check page in place of the document, has refused
the request. The refusal is recorded in <group>/refused.json and the URL is never fetched another way.

--raw-dir puts the group under data/raw/<dir>/ instead of data/raw/operators/ (research batch 2 keeps
super funds' disclosures under data/raw/superannuation/).

Usage:
    python3 scrapers/archive_pages.py [--raw-dir DIR] GROUP URL [URL ...]
    python3 scrapers/archive_pages.py nextdc https://www.nextdc.com/data-centres/sydney-data-centres/s1-sydney
    python3 scrapers/archive_pages.py --selftest    # offline tests of the robots.txt reader
"""
from __future__ import annotations

import gzip
import hashlib
import html
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import urllib.robotparser
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "data", "raw", "operators")
UA = ("ADCO-research/1.0 (Australian Data Centre Observatory; open public-interest research "
      "database; single-threaded polite crawler; stop on request)")
DELAY = 3.0


def get(url: str) -> tuple[bytes, str]:
    """(body, final URL after redirects). Asks for gzip, which the standard library can undo,
    because a server left to choose may answer in an encoding it cannot."""
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "text/html,*/*",
                                               "Accept-Encoding": "gzip"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        body = resp.read()
        if resp.headers.get("Content-Encoding", "").lower() == "gzip":
            body = gzip.decompress(body)
        return body, resp.geturl()


def visible_text(raw: str) -> str:
    raw = re.sub(r"<(script|style|noscript|svg)\b.*?</\1>", " ", raw, flags=re.S | re.I)
    raw = re.sub(r"<!--.*?-->", " ", raw, flags=re.S)
    raw = re.sub(r"<(br|/p|/li|/div|/h[1-6]|/tr|/td|/th|/dt|/dd|p|li|div|h[1-6]|tr)\b[^>]*>", "\n", raw,
                 flags=re.I)
    text = html.unescape(re.sub(r"<[^>]+>", " ", raw))
    lines = [re.sub(r"[ \t ]+", " ", line).strip() for line in text.splitlines()]
    return "\n".join(line for line in lines if line)


def name_for(url: str) -> str:
    path = urllib.parse.unquote(urllib.parse.urlparse(url).path).strip("/") or "index"
    name = re.sub(r"[^A-Za-z0-9._-]+", "_", path.split("/")[-1])[:80]
    return re.sub(r"\.(pdf|html?|csv)$", "", name, flags=re.I)   # the archive adds its own extension


# What a bot-check service serves, with status 200, in place of the page that was asked for.
CHALLENGE = re.compile(rb"Pardon Our Interruption|_Incapsula_Resource|Request unsuccessful\. Incapsula")


def refuse(out: str, url: str, how: str) -> None:
    path = os.path.join(out, "refused.json")
    refused = json.load(open(path)) if os.path.exists(path) else {}
    refused[url] = dict(how=how, checked_utc=datetime.now(timezone.utc).isoformat(timespec="seconds"),
                        user_agent=UA)
    json.dump(refused, open(path, "w"), indent=1, sort_keys=True)
    print(f"refused ({how}): {url}", file=sys.stderr)


def robots_groups(lines: list[str]) -> list[tuple[list[str], list[str]]]:
    """A robots.txt's groups as (user-agents, rule lines), grouped as RFC 9309 groups them: a
    user-agent line after a rule starts a new group, and blank lines and comments do not count."""
    groups: list[tuple[list[str], list[str]]] = []
    agents: list[str] = []
    rules: list[str] = []
    for raw in lines:
        key, sep, value = raw.split("#", 1)[0].strip().partition(":")
        key = key.strip().lower()
        if not sep:
            continue
        if key == "user-agent":
            if rules:
                groups.append((agents, rules))
                agents, rules = [], []
            agents.append(value.strip())
        elif agents and key in ("allow", "disallow", "crawl-delay", "request-rate"):
            rules.append(f"{key}: {value.strip()}")
    if agents and rules:
        groups.append((agents, rules))
    return groups


class Robots(urllib.robotparser.RobotFileParser):
    """A robots.txt reader that does not read a no as a yes. A file can give every crawler
    ("User-agent: *") more than one group: the NSW lobbyist register's (2026-11-01) opens with a block
    its hosting service added, "Allow: /", and still ends with the site's own "Disallow: /". Older
    robotparsers obey only the first such group; newer ones merge them, as RFC 9309 says, and settle
    the tie between "Allow: /" and "Disallow: /" as allow. Either way the file reads as yes. Here each
    group for every crawler is also read alone, and a URL is fetched only if robotparser and every one
    of those groups allow it, unless a group names this crawler, which robotparser then obeys."""

    def parse(self, lines) -> None:
        lines = list(lines)
        super().parse(lines)
        groups = robots_groups(lines)
        self.named = [a.lower() for agents, _ in groups for a in agents if a and a != "*"]
        self.star: list[urllib.robotparser.RobotFileParser] = []
        for agents, rules in groups:
            if "*" in agents:
                rp = urllib.robotparser.RobotFileParser()
                rp.parse(["User-agent: *", *rules])
                self.star.append(rp)

    def _star(self, useragent: str) -> list[urllib.robotparser.RobotFileParser]:
        """The groups for every crawler, each read alone; none if a group names this crawler."""
        token = useragent.split("/")[0].lower()
        if any(agent in token for agent in getattr(self, "named", [])):
            return []
        return getattr(self, "star", [])

    def can_fetch(self, useragent: str, url: str) -> bool:
        return super().can_fetch(useragent, url) and all(rp.can_fetch(useragent, url)
                                                         for rp in self._star(useragent))

    def crawl_delay(self, useragent: str):
        """The longest crawl-delay robotparser or any of those groups asks this crawler for."""
        delays = [d for d in (super().crawl_delay(useragent),
                              *(rp.crawl_delay(useragent) for rp in self._star(useragent)))
                  if d is not None]
        return max(delays) if delays else None

    def refusal(self, useragent: str, url: str) -> str | None:
        """Why this crawler may not fetch url, as refused.json records it, or None if it may."""
        if self.can_fetch(useragent, url):
            return None
        if self.disallow_all:
            return "robots.txt could not be read (refused), read as disallow-all"
        if super().can_fetch(useragent, url):
            return "disallowed by robots.txt (one of its groups for every crawler)"
        return "disallowed by robots.txt"


def robots_for(host: str) -> Robots:
    """The host's robots.txt, read as this crawler. RobotFileParser.read() would ask with Python's own
    User-Agent, which some sites refuse while serving this one. As robotparser does, a robots.txt
    refused with 401 or 403 means disallow everything, and one that is missing means allow."""
    rp = Robots(host + "/robots.txt")
    try:
        body, _ = get(host + "/robots.txt")
        rp.parse(body.decode("utf-8", errors="replace").splitlines())
    except urllib.error.HTTPError as exc:
        if exc.code in (401, 403):
            rp.disallow_all = True
        else:
            rp.allow_all = True
    return rp


# The NSW lobbyist register's robots.txt as read on 2026-11-01, cut down: the hosting service's block
# first, a crawler named and refused, then the site's own rule, indented as it is served.
LOBBYISTS_ROBOTS = """# BEGIN Cloudflare Managed content
User-agent: *
Content-Signal: search=yes,ai-train=no,use=reference
Allow: /

User-agent: ClaudeBot
Disallow: /
# END Cloudflare Managed Content

    User-agent: *
    Disallow: /
"""


def do_selftest() -> int:
    """Offline fixture tests for the robots.txt reader. They prove it reads the shapes written here,
    not that any site's file has kept its shape."""
    failures = 0

    def check(name: str, got: object, want: object) -> None:
        nonlocal failures
        if got == want:
            print(f"[pass] {name}")
        else:
            failures += 1
            print(f"[FAIL] {name}\n       got  {got!r}\n       want {want!r}")

    def robots(text: str) -> Robots:
        rp = Robots()
        rp.parse(text.splitlines())
        return rp

    page = "https://example.org/whoisontheregister"
    plain = urllib.robotparser.RobotFileParser()
    plain.parse(LOBBYISTS_ROBOTS.splitlines())
    check("robotparser alone reads the lobbyist file as allowed (why Robots exists)",
          plain.can_fetch(UA, page), True)
    check("a later 'Disallow: /' for every crawler refuses", robots(LOBBYISTS_ROBOTS).can_fetch(UA, page), False)
    check("and says which group refused", robots(LOBBYISTS_ROBOTS).refusal(UA, page),
          "disallowed by robots.txt (one of its groups for every crawler)")
    check("an earlier 'Disallow: /' refuses too (newer robotparsers merge the two and allow)",
          robots("User-agent: *\nDisallow: /\n\nUser-agent: *\nAllow: /\n").can_fetch(UA, page), False)
    check("one group that allows everything allows", robots("User-agent: *\nAllow: /\n").refusal(UA, page), None)
    check("one group that refuses everything refuses", robots("User-agent: *\nDisallow: /\n").refusal(UA, page),
          "disallowed by robots.txt")
    named = "User-agent: ADCO-research\nAllow: /\n\nUser-agent: *\nDisallow: /\n\nUser-agent: *\nDisallow: /\n"
    check("a group naming this crawler is obeyed alone", robots(named).can_fetch(UA, page), True)
    other = "User-agent: SomeoneElse\nAllow: /\n\nUser-agent: *\nAllow: /\n\nUser-agent: *\nDisallow: /\n"
    check("a group naming another crawler changes nothing for this one", robots(other).can_fetch(UA, page), False)
    two = "User-agent: *\nDisallow: /private\n\nUser-agent: *\nDisallow: /tmp\n"
    check("each group's own paths are refused: the first",
          robots(two).can_fetch(UA, "https://example.org/private/a"), False)
    check("each group's own paths are refused: the second",
          robots(two).can_fetch(UA, "https://example.org/tmp/a"), False)
    check("a path neither group refuses is allowed", robots(two).can_fetch(UA, "https://example.org/public"), True)
    for name, slow in (("first", "User-agent: *\nCrawl-delay: 10\nAllow: /\n\nUser-agent: *\nCrawl-delay: 2\nDisallow: /tmp\n"),
                       ("last", "User-agent: *\nCrawl-delay: 2\nAllow: /\n\nUser-agent: *\nCrawl-delay: 10\nDisallow: /tmp\n")):
        check(f"the longest crawl-delay is kept when it comes {name}", robots(slow).crawl_delay(UA), 10)
    check("no crawl-delay in any group is none", robots(two).crawl_delay(UA), None)
    check("blank lines do not end a group",
          robots_groups("User-agent: *\n\nDisallow: /x\n".splitlines()), [(["*"], ["disallow: /x"])])
    check("a group naming '*' among other agents counts",
          robots("User-agent: Foo\nUser-agent: *\nAllow: /\n\nUser-agent: *\nDisallow: /\n").can_fetch(UA, page),
          False)
    refused = Robots()
    refused.disallow_all = True
    check("a robots.txt the site refused reads as disallow-all", refused.refusal(UA, page),
          "robots.txt could not be read (refused), read as disallow-all")
    missing = Robots()
    missing.allow_all = True
    check("a missing robots.txt allows", missing.refusal(UA, page), None)

    print(f"\n{'FAILED' if failures else 'ok'}: {failures} failure(s)")
    return 1 if failures else 0


def main(argv: list[str]) -> int:
    if argv[:1] == ["--selftest"]:
        return do_selftest()
    raw_dir = "operators"
    if argv[:1] == ["--raw-dir"] and len(argv) > 1:
        raw_dir, argv = argv[1], argv[2:]
    if len(argv) < 2:
        print(__doc__, file=sys.stderr)
        return 2
    group, urls = argv[0], argv[1:]
    out = os.path.join(os.path.dirname(OUT), raw_dir, group)
    os.makedirs(out, exist_ok=True)
    robots: dict[str, Robots] = {}
    for url in urls:
        base = os.path.join(out, name_for(url))
        if os.path.exists(base + ".txt") or os.path.exists(base + ".csv"):
            print(f"archived already: {url}")
            continue
        host = "{0.scheme}://{0.netloc}".format(urllib.parse.urlparse(url))
        if host not in robots:
            robots[host] = robots_for(host)
        why = robots[host].refusal(UA, url)
        if why:
            refuse(out, url, why)
            continue
        time.sleep(DELAY)
        try:
            body, final = get(url)
        except urllib.error.HTTPError as exc:
            if exc.code in (401, 403, 429):
                refuse(out, url, f"HTTP {exc.code}")
                continue
            raise
        if CHALLENGE.search(body[:20000]):
            refuse(out, url, "bot-check page served in place of the document")
            continue
        if final != url:
            base = os.path.join(out, name_for(final))
        # A PDF (a report an operator or researcher publishes) is kept as .pdf with its text extracted
        # page by page, "[[page N]]" markers and all, by the same extractor the SSD documents use.
        is_pdf = body.startswith(b"%PDF")
        is_csv = urllib.parse.urlparse(final).path.lower().endswith(".csv")
        ext = ".pdf" if is_pdf else ".csv" if is_csv else ".html"
        with open(base + ext, "wb") as fh:
            fh.write(body)
        extra = {}
        if is_pdf:
            from fetch_ssd_documents import extract  # noqa: PLC0415 - only PDFs need pypdf
            text, extra["extractor"] = extract(base + ext)
            extra["pages"] = text.count("[[page ")
        elif is_csv:
            text = body.decode("utf-8-sig", errors="replace")
        else:
            text = visible_text(body.decode("utf-8", errors="replace"))
        if not is_csv:
            with open(base + ".txt", "w", encoding="utf-8") as fh:
                fh.write(text)
        json.dump(dict(url=final, requested_url=url, fetched_utc=datetime.now(timezone.utc).isoformat(timespec="seconds"),
                       sha256=hashlib.sha256(body).hexdigest(), bytes=len(body), user_agent=UA, **extra),
                  open(base + ext + ".meta.json", "w"), indent=1)
        print(f"archived {url} ({len(body) // 1024} KB, {len(text)} chars of text)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
