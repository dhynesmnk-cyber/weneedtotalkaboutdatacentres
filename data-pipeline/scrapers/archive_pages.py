#!/usr/bin/env python3
"""
Archive a list of public web pages with SHA-256 manifests (batch S4: operators' own pages).

The operator's own facility page is the primary source for facts about the operator's own asset:
where it is, what it is called, who runs it. This archives the pages a curation reads, so every
value it takes can be checked against the page as it was read, and the page re-read later.

Polite, single-threaded, a pause between requests, a descriptive User-Agent; robots.txt is read
first and any disallowed URL is refused. Re-running skips pages already archived.

Archive: data/raw/operators/<group>/<name>.html, .html.meta.json (url, fetched_utc, sha256, bytes),
and .txt: the page's visible text, one line per block, with scripts and styles removed. The text is
what a curation quotes from; the HTML is kept so the text can be regenerated.

Usage:
    python3 scrapers/archive_pages.py GROUP URL [URL ...]
    python3 scrapers/archive_pages.py nextdc https://www.nextdc.com/data-centres/sydney-data-centres/s1-sydney
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
    path = urllib.parse.urlparse(url).path.strip("/") or "index"
    return re.sub(r"[^A-Za-z0-9._-]+", "_", path.split("/")[-1])[:80]


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print(__doc__, file=sys.stderr)
        return 2
    group, urls = argv[0], argv[1:]
    out = os.path.join(OUT, group)
    os.makedirs(out, exist_ok=True)
    robots: dict[str, urllib.robotparser.RobotFileParser] = {}
    for url in urls:
        base = os.path.join(out, name_for(url))
        if os.path.exists(base + ".txt"):
            print(f"archived already: {url}")
            continue
        host = "{0.scheme}://{0.netloc}".format(urllib.parse.urlparse(url))
        if host not in robots:
            rp = urllib.robotparser.RobotFileParser(host + "/robots.txt")
            rp.read()
            robots[host] = rp
        if not robots[host].can_fetch(UA, url):
            print(f"refused by robots.txt: {url}", file=sys.stderr)
            continue
        time.sleep(DELAY)
        body, final = get(url)
        if final != url:
            base = os.path.join(out, name_for(final))
        text = visible_text(body.decode("utf-8", errors="replace"))
        with open(base + ".html", "wb") as fh:
            fh.write(body)
        with open(base + ".txt", "w", encoding="utf-8") as fh:
            fh.write(text)
        json.dump(dict(url=final, requested_url=url, fetched_utc=datetime.now(timezone.utc).isoformat(timespec="seconds"),
                       sha256=hashlib.sha256(body).hexdigest(), bytes=len(body), user_agent=UA),
                  open(base + ".html.meta.json", "w"), indent=1)
        print(f"archived {url} ({len(body) // 1024} KB, {len(text)} chars of text)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
