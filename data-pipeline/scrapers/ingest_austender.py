#!/usr/bin/env python3
"""
ADCO ingestion: AusTender (tenders.gov.au) — archive keyword searches over Commonwealth
contract notices, and the notices they point at.

Why this portal is in scope
---------------------------
AusTender is the Commonwealth's portal of record for contract notices. RG-072 already names it
as the portal that must replace the GovMarket aggregator behind the TCS spend figures
(SRC_GOVMARKET_TCS is credibility C, and its totals are the aggregator's own arithmetic,
inflated by at least one duplicate). Anything sourced here is primary_government, grade A, and
can carry VERIFIED rather than REPORTED.

It also reaches the third group in the consultancy layer — the systems integrators who hold the
government's own IT contracts. Palantir is the entry point this scraper was written for:

    https://www.tenders.gov.au/Search/KeywordSearch?keyword=palantir

WHAT THIS SCRAPER HAS AND HAS NOT BEEN PROVEN AGAINST
-----------------------------------------------------
IT HAS NEVER BEEN RUN AGAINST THE LIVE SITE. tenders.gov.au was unreachable from the authoring
environment (the egress proxy answered 403 to CONNECT), so nothing below is a tested claim about
AusTender's markup, its pagination, or its URL shapes — unlike ingest_cer.py and
ingest_nsw_dc.py, whose documented patterns were tested on 2026-09-18.

Everything is therefore built by DISCOVERY, not by hard-coded structure:

  * the only URL asserted is the keyword-search entry point above, which came from the operator;
  * result and pagination links are read out of whatever HTML comes back, not constructed;
  * nothing is parsed into fields, and nothing is curated. This archives bytes and hashes them.

The first live run is a human review step, not a load. Run --check, then --keyword, then
--inspect, and read the archived HTML before writing any curation script against it. If the
discovery functions find nothing, that is the expected failure mode for a site whose markup was
never seen — fix the selectors against the archived page, do not guess harder.

Usage:
    python3 scrapers/ingest_austender.py --check                  # reachability + robots.txt
    python3 scrapers/ingest_austender.py --keyword palantir       # archive the search results
    python3 scrapers/ingest_austender.py --keyword palantir --follow   # + each linked notice
    python3 scrapers/ingest_austender.py --url <any tenders.gov.au url>
    python3 scrapers/ingest_austender.py --inspect                # offline: what is archived
    python3 scrapers/ingest_austender.py --selftest               # offline: parser fixtures

Output: data/raw/austender/search/<keyword>_p<N>.html  (+ .meta.json with url, sha256, fetched_utc)
        data/raw/austender/notices/<id>.html           (+ .meta.json)
"""
from __future__ import annotations

import argparse
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
RAW = os.path.join(ROOT, "data", "raw", "austender")
SEARCH_DIR = os.path.join(RAW, "search")
NOTICE_DIR = os.path.join(RAW, "notices")

BASE = "https://www.tenders.gov.au"
SEARCH_PATH = "/Search/KeywordSearch"
DELAY = 2.0
MAX_PAGES = 20          # refuse to walk a pagination loop forever
UA = ("ADCO-research/1.0 (Australian Data Centre Observatory; open public-interest research "
      "database; single-threaded polite crawler; stop on request)")

# A contract/tender notice link on AusTender is any in-site link whose path segment names one of
# the notice types. Kept as a permissive alternation because the live markup has not been seen.
NOTICE_PATH_RE = re.compile(
    r"/(?:Cn|CN|Sme|SON|Son|ContractNotice|Tender|Ocn)/[A-Za-z0-9._%/-]*Show[A-Za-z0-9._%/-]*"
    r"|/(?:Cn|CN|SON|Son)/Show/[A-Za-z0-9._%-]+",
)
HREF_RE = re.compile(r"""<a\b[^>]*?\bhref\s*=\s*["']([^"']+)["']""", re.IGNORECASE)


def search_url(keyword: str, page: int = 1) -> str:
    """The one URL shape this scraper asserts, from the operator-supplied entry point."""
    q = {"keyword": keyword}
    if page > 1:
        q["page"] = str(page)
    return f"{BASE}{SEARCH_PATH}?{urllib.parse.urlencode(q)}"


def get(url: str, timeout: int = 90) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read()


def archive(path: str, body: bytes, url: str) -> str:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as fh:
        fh.write(body)
    with open(path + ".meta.json", "w", encoding="utf-8") as fh:
        json.dump({"url": url,
                   "fetched_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                   "sha256": hashlib.sha256(body).hexdigest(),
                   "bytes": len(body),
                   "user_agent": UA}, fh, indent=2)
    print(f"[saved] {os.path.relpath(path, ROOT)}  ({len(body):,} bytes)")
    return path


def links(body: bytes) -> list[str]:
    """Every href in the document, unescaped and absolutised against BASE."""
    text = body.decode("utf-8", "replace")
    out: list[str] = []
    for raw in HREF_RE.findall(text):
        href = html.unescape(raw).strip()
        if not href or href.startswith(("#", "mailto:", "javascript:")):
            continue
        out.append(urllib.parse.urljoin(BASE, href))
    return out


def notice_links(body: bytes) -> list[str]:
    """In-site links that look like a contract or tender notice. Order-preserving, deduplicated."""
    seen: dict[str, None] = {}
    for url in links(body):
        parts = urllib.parse.urlsplit(url)
        if parts.netloc and parts.netloc != urllib.parse.urlsplit(BASE).netloc:
            continue
        if NOTICE_PATH_RE.search(parts.path):
            seen.setdefault(urllib.parse.urlunsplit(parts), None)
    return list(seen)


def next_page_links(body: bytes, keyword: str) -> list[int]:
    """Page numbers reachable from this search page, read from its own pagination links."""
    pages: set[int] = set()
    want = keyword.casefold()
    for url in links(body):
        parts = urllib.parse.urlsplit(url)
        if not parts.path.rstrip("/").casefold().endswith(SEARCH_PATH.rstrip("/").casefold()):
            continue
        q = urllib.parse.parse_qs(parts.query)
        if [k.casefold() for k in q.get("keyword", [""])][:1] != [want]:
            continue
        for value in q.get("page", []):
            if value.isdigit():
                pages.add(int(value))
    return sorted(p for p in pages if p > 1)


def notice_id(url: str) -> str:
    """A filesystem-safe name for a notice URL: its last non-empty path segment, else a hash."""
    parts = urllib.parse.urlsplit(url)
    segs = [s for s in parts.path.split("/") if s]
    stem = segs[-1] if segs else ""
    safe = re.sub(r"[^A-Za-z0-9_.-]+", "_", urllib.parse.unquote(stem))[:110].strip("_")
    return safe or hashlib.sha256(url.encode()).hexdigest()[:16]


def robots() -> urllib.robotparser.RobotFileParser | None:
    rp = urllib.robotparser.RobotFileParser()
    rp.set_url(f"{BASE}/robots.txt")
    try:
        rp.read()
    except Exception as exc:  # noqa: BLE001 - any failure means "unknown", not "allowed"
        print(f"[warn] could not read {BASE}/robots.txt: {exc}", file=sys.stderr)
        return None
    return rp


def allowed(rp: urllib.robotparser.RobotFileParser | None, url: str, force: bool) -> bool:
    if rp is None or force:
        return True
    if rp.can_fetch(UA, url):
        return True
    print(f"[robots] disallowed, skipping: {url}", file=sys.stderr)
    return False


def fetch_note(exc: Exception) -> None:
    print(f"[FAILED] {exc}", file=sys.stderr)
    print("         If this is a CONNECT/403 or TLS failure the host is probably blocked by the\n"
          "         environment's network policy rather than by AusTender. Archive the pages from\n"
          "         a permitted network and copy data/raw/austender/ across; every consumer of this\n"
          "         archive is offline.", file=sys.stderr)


def do_check() -> int:
    url = search_url("palantir")
    print(f"[robots] {BASE}/robots.txt")
    rp = robots()
    if rp is not None:
        print(f"[robots] can_fetch({SEARCH_PATH}) = {rp.can_fetch(UA, url)}")
        delay = rp.crawl_delay(UA)
        if delay:
            print(f"[robots] crawl-delay = {delay}s (this scraper uses {DELAY}s)")
    try:
        body = get(url)
    except Exception as exc:  # noqa: BLE001
        fetch_note(exc)
        return 1
    print(f"[reachable] {url} ({len(body):,} bytes)")
    print(f"[discovered] {len(notice_links(body))} notice-shaped links, "
          f"{len(next_page_links(body, 'palantir'))} further pages")
    print("\nNothing was archived. Re-run with --keyword to archive, then --inspect, then read the\n"
          "HTML before writing any curation script against it.")
    return 0


def do_keyword(keyword: str, follow: bool, force: bool, max_pages: int) -> int:
    rp = robots()
    pending, done, bodies = [1], set(), []
    while pending:
        page = pending.pop(0)
        if page in done or len(done) >= max_pages:
            continue
        done.add(page)
        url = search_url(keyword, page)
        if not allowed(rp, url, force):
            continue
        try:
            body = get(url)
        except Exception as exc:  # noqa: BLE001
            fetch_note(exc)
            return 1
        archive(os.path.join(SEARCH_DIR, f"{notice_id(keyword)}_p{page}.html"), body, url)
        bodies.append(body)
        for nxt in next_page_links(body, keyword):
            if nxt not in done:
                pending.append(nxt)
        time.sleep(DELAY)

    found: list[str] = []
    for body in bodies:
        for url in notice_links(body):
            if url not in found:
                found.append(url)
    print(f"\n[search] archived {len(done)} page(s), {len(found)} notice-shaped link(s)")
    if not found:
        print("[search] no notice links matched. Read the archived HTML and fix NOTICE_PATH_RE\n"
              "         against what is actually there - do not widen it by guessing.")
    if not follow:
        if found:
            print("[search] re-run with --follow to archive each notice.")
        return 0

    for url in found:
        if not allowed(rp, url, force):
            continue
        try:
            body = get(url)
        except urllib.error.HTTPError as exc:
            print(f"[miss] {url}: HTTP {exc.code}", file=sys.stderr)
            time.sleep(DELAY)
            continue
        except Exception as exc:  # noqa: BLE001
            fetch_note(exc)
            return 1
        archive(os.path.join(NOTICE_DIR, notice_id(url) + ".html"), body, url)
        time.sleep(DELAY)
    return 0


def do_url(url: str, force: bool) -> int:
    if urllib.parse.urlsplit(url).netloc != urllib.parse.urlsplit(BASE).netloc:
        print(f"refusing an off-site url: {url}", file=sys.stderr)
        return 2
    if not allowed(robots(), url, force):
        return 1
    try:
        body = get(url)
    except Exception as exc:  # noqa: BLE001
        fetch_note(exc)
        return 1
    archive(os.path.join(RAW, "adhoc", notice_id(url) + ".html"), body, url)
    return 0


def do_inspect() -> int:
    """Offline: report what is archived and what the discovery functions find in it."""
    if not os.path.isdir(RAW):
        print(f"nothing archived yet under {os.path.relpath(RAW, ROOT)}")
        return 0
    total = 0
    for dirpath, _dirs, files in os.walk(RAW):
        for name in sorted(f for f in files if not f.endswith(".meta.json")):
            path = os.path.join(dirpath, name)
            with open(path, "rb") as fh:
                body = fh.read()
            meta_path = path + ".meta.json"
            meta = {}
            if os.path.exists(meta_path):
                with open(meta_path, encoding="utf-8") as fh:
                    meta = json.load(fh)
            digest = hashlib.sha256(body).hexdigest()
            state = "ok" if meta.get("sha256") == digest else "SHA256 MISMATCH"
            if not meta:
                state = "no manifest"
            total += 1
            print(f"{os.path.relpath(path, RAW):60s} {len(body):>9,}b  {state}")
            print(f"{'':60s} {len(notice_links(body)):>4} notice links  {meta.get('fetched_utc', '')}")
    print(f"\n{total} archived file(s) under {os.path.relpath(RAW, ROOT)}")
    return 0


FIXTURE = b"""<html><body>
<a href="/Cn/Show/abc-123">A contract notice</a>
<a href="/Cn/Show/abc-123">The same notice again</a>
<a href="https://www.tenders.gov.au/Son/Show/def-456">A standing offer</a>
<a href="/Search/KeywordSearch?keyword=palantir&amp;page=2">2</a>
<a href="/Search/KeywordSearch?keyword=palantir&amp;page=3">3</a>
<a href="/Search/KeywordSearch?keyword=other&amp;page=9">someone else's search</a>
<a href="https://example.com/Cn/Show/off-site">off site</a>
<a href="#top">anchor</a><a href="mailto:x@y.z">mail</a>
</body></html>"""


def do_selftest() -> int:
    """
    Fixture tests for the discovery functions. These prove the parser handles the shapes it was
    WRITTEN for; they do not prove those shapes match AusTender, which has never been seen.
    """
    failures = 0

    def check(name: str, got: object, want: object) -> None:
        nonlocal failures
        if got == want:
            print(f"[pass] {name}")
        else:
            failures += 1
            print(f"[FAIL] {name}\n       got  {got!r}\n       want {want!r}")

    check("notice_links dedupes, absolutises and drops off-site",
          notice_links(FIXTURE),
          ["https://www.tenders.gov.au/Cn/Show/abc-123",
           "https://www.tenders.gov.au/Son/Show/def-456"])
    check("next_page_links keeps only this keyword's pages, excludes page 1",
          next_page_links(FIXTURE, "palantir"), [2, 3])
    check("next_page_links is case-insensitive on the keyword",
          next_page_links(FIXTURE, "Palantir"), [2, 3])
    check("notice_id takes the last path segment",
          notice_id("https://www.tenders.gov.au/Cn/Show/abc-123"), "abc-123")
    check("notice_id sanitises separators",
          notice_id("https://www.tenders.gov.au/Cn/Show/CN%3A1234%2F56"), "CN_1234_56")
    check("search_url omits page=1", search_url("palantir"),
          "https://www.tenders.gov.au/Search/KeywordSearch?keyword=palantir")
    check("search_url encodes the keyword", search_url("tata consultancy", 2),
          "https://www.tenders.gov.au/Search/KeywordSearch?keyword=tata+consultancy&page=2")
    print(f"\n{'FAILED' if failures else 'ok'}: {failures} failure(s)")
    return 1 if failures else 0


def main(argv: list[str]) -> int:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--check", action="store_true", help="reachability and robots.txt; archives nothing")
    p.add_argument("--keyword", help="archive the keyword search, following its own pagination")
    p.add_argument("--follow", action="store_true", help="with --keyword, also archive each linked notice")
    p.add_argument("--url", help="archive one tenders.gov.au url")
    p.add_argument("--inspect", action="store_true", help="offline: list the archive and verify hashes")
    p.add_argument("--selftest", action="store_true", help="offline: run the parser fixtures")
    p.add_argument("--max-pages", type=int, default=MAX_PAGES, help=f"page cap (default {MAX_PAGES})")
    p.add_argument("--ignore-robots", action="store_true",
                   help="fetch even where robots.txt disallows it; needs a reason you can defend")
    a = p.parse_args(argv)

    if a.selftest:
        return do_selftest()
    if a.inspect:
        return do_inspect()
    if a.check:
        return do_check()
    if a.url:
        return do_url(a.url, a.ignore_robots)
    if a.keyword:
        return do_keyword(a.keyword, a.follow, a.ignore_robots, a.max_pages)
    p.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
