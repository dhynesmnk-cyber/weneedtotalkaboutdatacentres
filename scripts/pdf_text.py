#!/usr/bin/env python3
"""
Minimal dependency-free PDF text extractor.

The sandbox has no poppler/pdftotext and no pypdf, but NSW planning documents are
ordinary text PDFs with FlateDecode streams. This handles the common cases:
  * FlateDecode content streams
  * Tj / TJ / ' / " text-showing operators
  * literal strings with escapes, and hex strings
  * basic ToUnicode-free heuristics (ligature and octal fixups)

It is deliberately approximate: it exists to let the Observatory grep consent conditions,
not to reproduce layout. Anything load-bearing must be read in the original PDF, which is
archived with a SHA-256 manifest under data/raw/.

Usage:
    python3 scripts/pdf_text.py file.pdf                 # to stdout
    python3 scripts/pdf_text.py file.pdf --grep PUE      # lines matching, with context
    python3 scripts/pdf_text.py file.pdf --out file.txt
"""
from __future__ import annotations

import argparse
import os
import re
import sys
import warnings
import zlib


# Planning documents embed survey imagery, point clouds and rendered plans whose streams
# decompress to gigabytes. A text extractor must skip them, not die on them, so inflation is
# incremental with a hard ceiling and the oversized cases are abandoned early.
MAX_TEXT_STREAM = 16 * 1024 * 1024    # a content stream this large is never text
MAX_RAW_STREAM = 24 * 1024 * 1024
_INFLATE_CHUNK = 1024 * 1024


def _decompress(raw: bytes) -> bytes | None:
    if len(raw) > MAX_RAW_STREAM:
        return None
    for candidate in (raw, raw[:-1], raw[:-2]):
        if not candidate:
            continue
        d = zlib.decompressobj()
        out = bytearray()
        try:
            for i in range(0, len(candidate), _INFLATE_CHUNK):
                out += d.decompress(candidate[i:i + _INFLATE_CHUNK], _INFLATE_CHUNK * 8)
                if len(out) > MAX_TEXT_STREAM:
                    return None
        except (zlib.error, MemoryError, OverflowError):
            continue
        return bytes(out)
    return None


def _streams(data: bytes) -> list[bytes]:
    """Decode every stream object, skipping ones that are too large to be text."""
    out: list[bytes] = []
    for m in re.finditer(rb"stream\r?\n", data):
        start = m.end()
        end = data.find(b"endstream", start)
        if end == -1:
            continue
        dec = _decompress(data[start:end])
        if dec is not None:
            out.append(dec)
    return out


_ESC = {b"n": b"\n", b"r": b"\r", b"t": b"\t", b"b": b"\b", b"f": b"\f",
        b"(": b"(", b")": b")", b"\\": b"\\"}


def _unescape(b: bytes) -> bytes:
    out = bytearray()
    i = 0
    while i < len(b):
        c = b[i:i + 1]
        if c == b"\\":
            nxt = b[i + 1:i + 2]
            if nxt.isdigit():
                oct_digits = b[i + 1:i + 4]
                j = 0
                while j < len(oct_digits) and oct_digits[j:j + 1].isdigit():
                    j += 1
                try:
                    out.append(int(oct_digits[:j], 8) & 0xFF)
                except ValueError:
                    out.append(0x20)
                i += 1 + j
                continue
            out += _ESC.get(nxt, nxt)
            i += 2
            continue
        out += c
        i += 1
    return bytes(out)


def _hex(b: bytes) -> bytes:
    h = re.sub(rb"[^0-9A-Fa-f]", b"", b)
    if len(h) % 2:
        h += b"0"
    return bytes.fromhex(h.decode("ascii"))


def _parse_cmap(d: bytes) -> dict[int, str]:
    """Parse a ToUnicode CMap's bfchar and bfrange blocks into {cid: unicode}."""
    out: dict[int, str] = {}
    for block in re.findall(rb"beginbfchar(.*?)endbfchar", d, re.S):
        for src, dst in re.findall(rb"<([0-9A-Fa-f]+)>\s*<([0-9A-Fa-f]+)>", block):
            try:
                out[int(src, 16)] = _hex_to_text(dst)
            except ValueError:
                continue
    for block in re.findall(rb"beginbfrange(.*?)endbfrange", d, re.S):
        for m in re.finditer(rb"<([0-9A-Fa-f]+)>\s*<([0-9A-Fa-f]+)>\s*(<([0-9A-Fa-f]+)>|\[(.*?)\])",
                             block, re.S):
            lo, hi = int(m.group(1), 16), int(m.group(2), 16)
            if hi - lo > 65535:
                continue
            if m.group(4):
                base = int(m.group(4), 16)
                for i, cid in enumerate(range(lo, hi + 1)):
                    out[cid] = chr(base + i)
            elif m.group(5):
                dsts = re.findall(rb"<([0-9A-Fa-f]+)>", m.group(5))
                for i, cid in enumerate(range(lo, hi + 1)):
                    if i < len(dsts):
                        out[cid] = _hex_to_text(dsts[i])
    return out


def _hex_to_text(h: bytes) -> str:
    raw = bytes.fromhex(h.decode("ascii"))
    if len(raw) % 2 == 0:
        return "".join(chr(int.from_bytes(raw[i:i + 2], "big")) for i in range(0, len(raw), 2))
    return raw.decode("utf-16-be", "replace")


def build_cmap(path_or_bytes) -> dict[int, str]:
    """Merge every ToUnicode CMap in the document into one cid->unicode map.

    Fonts are not tracked per-resource, which would need a full xref/object parser. Merging is
    a deliberate approximation: it is exact for the common case where subset fonts follow the
    Adobe-Identity-UCS convention, and it can mis-decode where two subsets assign the same CID
    to different glyphs. Any result used load-bearing must be checked against the rendered PDF.
    """
    data = path_or_bytes if isinstance(path_or_bytes, bytes) else open(path_or_bytes, "rb").read()
    merged: dict[int, str] = {}
    for m in re.finditer(rb"stream\r?\n", data):
        start = m.end()
        end = data.find(b"endstream", start)
        if end == -1:
            continue
        dec = _decompress(data[start:end])
        if dec and (b"beginbfchar" in dec or b"beginbfrange" in dec):
            for cid, uni in _parse_cmap(dec).items():
                merged.setdefault(cid, uni)
    return merged


def _decode_string(raw: bytes, cmap: dict[int, str]) -> str:
    """Decode a PDF string using the merged CMap when it looks 2-byte CID-encoded."""
    if len(raw) >= 2 and len(raw) % 2 == 0:
        cids = [int.from_bytes(raw[i:i + 2], "big") for i in range(0, len(raw), 2)]
        known = sum(1 for c in cids if c in cmap)
        # Treat as CID-encoded when most 2-byte codes are known and it is not plain ASCII
        if known >= max(1, int(0.6 * len(cids))) and not all(32 <= c < 127 for c in cids):
            return "".join(cmap.get(c, "") for c in cids)
    return raw.decode("latin-1", "replace")


def _text_ops(content: bytes, cmap: dict[int, str] | None = None) -> str:
    """Walk text-showing operators, inserting spaces/newlines at plausible points."""
    cmap = cmap or {}
    pieces: list[str] = []
    # tokens: (string) Tj | [ ... ] TJ | T* | Td | TD | Tm | ET
    token_re = re.compile(
        rb"\(((?:\\.|[^\\()])*)\)\s*Tj"          # literal string Tj
        rb"|\<([0-9A-Fa-f\s]*)\>\s*Tj"            # hex string Tj
        rb"|\[((?:[^\[\]\\]|\\.)*)\]\s*TJ"        # array TJ
        rb"|(T\*|Td|TD|Tm|ET|BT)", re.S)
    for m in token_re.finditer(content):
        lit, hx, arr, pos = m.group(1), m.group(2), m.group(3), m.group(4)
        if pos:
            if pos in (b"T*", b"ET"):
                pieces.append("\n")
            elif pos in (b"Td", b"TD", b"Tm"):
                pieces.append("\n")
            continue
        if lit is not None:
            pieces.append(_decode_string(_unescape(lit), cmap))
        elif hx is not None:
            raw = _hex(hx)
            # A simple font writes 1-byte codes; a Type0/Identity-H font writes 2-byte CIDs.
            if cmap and not (len(raw) % 2 == 0 and all(c == 0 for c in raw[0::2])):
                pieces.append(_decode_string(raw, cmap))
            elif len(raw) % 2 == 0 and all(c == 0 for c in raw[0::2]):
                pieces.append(raw[1::2].decode("latin-1", "replace"))
            else:
                pieces.append(_decode_string(raw, cmap))
        elif arr is not None:
            for sm in re.finditer(rb"\(((?:\\.|[^\\()])*)\)|(\<[0-9A-Fa-f\s*\>])|(-?\d+(?:\.\d+)?)", arr):
                if sm.group(1) is not None:
                    pieces.append(_decode_string(_unescape(sm.group(1)), cmap))
                elif sm.group(2) is not None:
                    pieces.append(_decode_string(_hex(sm.group(2)[1:-1]), cmap))
                else:
                    # a large negative kern means a space
                    try:
                        if float(sm.group(3)) <= -120:
                            pieces.append(" ")
                    except (TypeError, ValueError):
                        pass
    txt = "".join(pieces)
    # clean up
    txt = txt.replace("\u00ad", "").replace("\ufb01", "fi").replace("\ufb02", "fl")
    txt = re.sub(r"[ \t]+", " ", txt)
    # The naive pass emits a newline for every text-positioning operator, which fragments
    # words mid-token ("Infrastru\ncture"). Re-join fragments: a newline followed by a
    # lowercase continuation and no terminal punctuation is almost always a broken word.
    lines = txt.split("\n")
    joined: list[str] = []
    for ln in lines:
        ln = ln.strip()
        if not ln:
            if joined and joined[-1] != "":
                joined.append("")
            continue
        if joined and joined[-1] and not re.search(r"[.:;)\]\-\u2013\u2014,]$", joined[-1]) \
           and re.match(r"^[a-z0-9(]", ln) and len(joined[-1]) < 60:
            joined[-1] = joined[-1] + ln
        else:
            joined.append(ln)
    txt = "\n".join(joined)
    txt = re.sub(r"\n{3,}", "\n\n", txt)
    return txt.strip()


# Rough expected text density for a text-bearing PDF. Anything far below this means the
# document uses structures this extractor cannot walk (cross-reference streams, object streams,
# font encodings without a usable ToUnicode) and the output MUST NOT be used to draw a negative
# conclusion. The NSW Data Centre Guidelines yields ~8 chars/KB against ~60-90 for the planning
# consents, which is how the truncation was caught.
MIN_CHARS_PER_KB = 20


class LowYieldWarning(RuntimeWarning):
    pass


def yield_stats(path: str, chars: int) -> dict:
    kb = max(1, os.path.getsize(path) // 1024)
    ratio = chars / kb
    return {"chars": chars, "kb": kb, "chars_per_kb": round(ratio, 1),
            "reliable": ratio >= MIN_CHARS_PER_KB}


def extract(path: str, max_streams: int | None = None, warn: bool = True) -> str:
    data = open(path, "rb").read()
    if max_streams is not None and len(data) > 48 * 1024 * 1024:
        # Very large document: only read far enough to find the requested streams.
        data = _head_for_streams(data, max_streams)
    streams = _streams(data)
    if max_streams is not None:
        streams = streams[:max_streams]
    cmap = build_cmap(data)
    chunks = [_text_ops(s, cmap) for s in streams]
    chunks = [c for c in chunks if c]
    txt = "\n".join(chunks)
    if warn:
        st = yield_stats(path, len(txt))
        if not st["reliable"]:
            import warnings
            warnings.warn(
                f"{os.path.basename(path)}: extraction yield {st['chars_per_kb']} chars/KB "
                f"({st['chars']:,} chars from {st['kb']:,} KB) is below the {MIN_CHARS_PER_KB} "
                f"chars/KB reliability floor. This extractor could not walk the document's "
                f"structure. DO NOT use the output to conclude that a term is absent - fetch "
                f"the document through a full PDF renderer instead.",
                LowYieldWarning, stacklevel=2)
    return txt


def _head_for_streams(data: bytes, want: int) -> bytes:
    """Truncate the buffer once `want` stream starts have been seen, so a 344 MB file is
    not fully scanned when only the opening pages are needed."""
    seen = 0
    pos = 0
    while seen < want:
        m = re.compile(rb"stream\r?\n").search(data, pos)
        if not m:
            break
        e = data.find(b"endstream", m.end())
        if e == -1:
            pos = m.end()
            seen += 1
            continue
        pos = e + len(b"endstream")
        seen += 1
    return data[:min(len(data), pos + 1024)]


def iter_text(path: str, chunk_bytes: int = 24 * 1024 * 1024):
    """Yield (stream_index, text) without holding the whole decoded document.

    Needed for the very large planning documents - the Western Downs Digital Park
    application is 344 MB and ~870 pages - where `extract` would balloon memory.
    """
    buf = b""
    idx = 0
    pending = b""
    with open(path, "rb") as fh:
        cmap = build_cmap(fh.read())
    size = os.path.getsize(path)
    with open(path, "rb") as fh:
        while True:
            block = fh.read(chunk_bytes)
            if not block:
                break
            buf += block
            # process only complete streams inside buf
            while True:
                m = re.search(rb"stream\r?\n", buf)
                if not m:
                    break
                end = buf.find(b"endstream", m.end())
                if end == -1:
                    break
                raw = buf[m.end():end]
                dec = _decompress(raw)
                if dec is None:
                    buf = buf[end + len(b"endstream"):]
                    continue
                txt = _text_ops(dec, cmap)
                idx += 1
                if txt.strip():
                    yield idx, txt
                buf = buf[end + len(b"endstream"):]
            # keep the tail so a stream spanning the boundary is not lost
            if len(buf) > 64 * 1024 * 1024:
                buf = buf[-32 * 1024 * 1024:]
        _ = pending, size


def main(argv: list[str]) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("pdf")
    p.add_argument("--out")
    p.add_argument("--grep", action="append", default=[], help="case-insensitive pattern; prints matches with context")
    p.add_argument("--context", type=int, default=1, help="lines of context around a grep match")
    p.add_argument("--max-hits", type=int, default=40)
    p.add_argument("--max-streams", type=int, help="only decode the first N streams (large documents)")
    p.add_argument("--stream", action="store_true",
                   help="use the low-memory streaming decoder (required for very large PDFs)")
    p.add_argument("--stream-limit", type=int, default=4000, help="max streams to scan in --stream mode")
    a = p.parse_args(argv)

    if a.out:
        open(a.out, "w", encoding="utf-8").write(txt)
        print(f"wrote {a.out} ({len(txt):,} chars)", file=sys.stderr)
    if not a.grep:
        print(txt)
        return 0

    lines = txt.splitlines()
    for pat in a.grep:
        rx = re.compile(pat, re.I)
        hits = [i for i, l in enumerate(lines) if rx.search(l)]
        print(f"\n===== /{pat}/ :: {len(hits)} matching lines =====")
        shown = 0
        for i in hits[: a.max_hits]:
            lo, hi = max(0, i - a.context), min(len(lines), i + a.context + 1)
            for l in lines[lo:hi]:
                print(("> " if l is lines[i] else "  ") + l.strip())
            print("  " + "-" * 60)
            shown += 1
        if len(hits) > a.max_hits:
            print(f"  ... {len(hits) - a.max_hits} further matches suppressed")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
