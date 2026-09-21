#!/usr/bin/env python3
"""
ADCO analysis: topic-model a patent corpus.

This is the Iliadis & Acker (2022) method — corpus, preprocess, Latent Dirichlet Allocation,
interpret the topics — reimplemented for this project's operators. Their paper is assessed in
`reports/palantir_australia_triage.md`; see `reports/PATENT_METHOD.md` for whether the method
actually transplants, which is a question with a real answer and it is partly "no".

Dependency-free by design. The Makefile promises nothing beyond the standard library and openpyxl,
so LDA here is a collapsed Gibbs sampler in ~80 lines rather than a scikit-learn import. It is
seeded and therefore reproducible: the same corpus and seed give the same topics, which matters
because a build that cannot be reproduced cannot be verified.

WHAT IS AND IS NOT ESTABLISHED
------------------------------
The sampler is validated: `--selftest` plants topics with known vocabularies in a synthetic corpus
and asserts the model recovers them. That is a real test with a real ground truth, and it can fail.

It has never been run on patents, because no patent source is reachable from the authoring
environment (patents.google.com, IP Australia, USPTO, EPO and Espacenet are all blocked). So the
preprocessing — in particular PATENT_BOILERPLATE — is reasoned, not tuned. Expect to revise the
stoplist against a real corpus before trusting any topic.

Usage:
    python3 scripts/analyse_patents.py --selftest
    python3 scripts/analyse_patents.py --corpus data/raw/patents/text --topics 20
    python3 scripts/analyse_patents.py --corpus DIR --topics 20 --seed 42 --out reports/patents.md
"""
from __future__ import annotations

import argparse
import glob
import json
import math
import os
import random
import re
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Ordinary English function words.
STOPWORDS = set("""
a about above after again against all am an and any are as at be because been before being below
between both but by can cannot could did do does doing down during each few for from further had
has have having he her here hers herself him himself his how i if in into is it its itself me more
most my myself no nor not of off on once only or other ought our ours ourselves out over own same
she should so some such than that the their theirs them themselves then there these they this those
through to too under until up very was we were what when where which while who whom why with would
you your yours yourself yourselves
""".split())

# Patent prose is ~40% boilerplate. Left in, these dominate every topic and the model recovers the
# genre rather than the subject matter. Iliadis & Acker hit the same wall. THIS LIST IS REASONED,
# NOT TUNED - it has never met a real corpus. Revise it against one before trusting a topic.
PATENT_BOILERPLATE = set("""
accordance according additional additionally also although apparatus appreciatedapparent art
aspect aspects associated based claim claimed claims comprise comprises comprising configured
corresponding described describes description desired detailed disclosed disclosure embodiment
embodiments example examples exemplary fig figs figure figures first foregoing further generally
herein however illustrated implementation implementations include included includes including
instance invention least may method methods one operation particular plurality preferred present
provide provided provides referring relates respective said second selected shown similar skilled
specific step steps substantially such system systems technique techniques third thus various
wherein whereby whether without
""".split())

TOKEN_RE = re.compile(r"[a-z]{3,}")


def tokenise(text: str) -> list[str]:
    toks = TOKEN_RE.findall(text.lower())
    out = []
    for t in toks:
        if t in STOPWORDS or t in PATENT_BOILERPLATE:
            continue
        # Crude singularisation. Real lemmatisation needs a dependency; this handles the plural
        # forms that otherwise split one concept across two vocabulary entries.
        if len(t) > 4 and t.endswith("ies"):
            t = t[:-3] + "y"
        elif len(t) > 4 and t.endswith("ses"):
            t = t[:-2]
        elif len(t) > 3 and t.endswith("s") and not t.endswith("ss"):
            t = t[:-1]
        if t in STOPWORDS or t in PATENT_BOILERPLATE or len(t) < 3:
            continue
        out.append(t)
    return out


def build_vocab(docs: list[list[str]], min_df: int = 2, max_df_ratio: float = 0.5) -> dict[str, int]:
    """Drop terms in too few documents (noise) or too many (uninformative)."""
    df = Counter()
    for d in docs:
        df.update(set(d))
    n = len(docs)
    keep = sorted(w for w, c in df.items() if c >= min_df and c <= max_df_ratio * n)
    return {w: i for i, w in enumerate(keep)}


class LDA:
    """Collapsed Gibbs sampler for Latent Dirichlet Allocation."""

    def __init__(self, n_topics: int, alpha: float = 0.1, beta: float = 0.01, seed: int = 42):
        self.K = n_topics
        self.alpha = alpha
        self.beta = beta
        self.rng = random.Random(seed)

    def fit(self, docs: list[list[int]], vocab_size: int, iterations: int = 300) -> None:
        K, V = self.K, vocab_size
        self.n_dk = [[0] * K for _ in docs]
        self.n_kw = [[0] * V for _ in range(K)]
        self.n_k = [0] * K
        self.z = []
        for d, doc in enumerate(docs):
            zs = []
            for w in doc:
                k = self.rng.randrange(K)
                zs.append(k)
                self.n_dk[d][k] += 1
                self.n_kw[k][w] += 1
                self.n_k[k] += 1
            self.z.append(zs)

        ab = self.alpha
        bb = self.beta
        Vb = V * bb
        for _ in range(iterations):
            for d, doc in enumerate(docs):
                n_dk_d = self.n_dk[d]
                zs = self.z[d]
                for i, w in enumerate(doc):
                    k = zs[i]
                    n_dk_d[k] -= 1
                    self.n_kw[k][w] -= 1
                    self.n_k[k] -= 1

                    probs = [0.0] * K
                    total = 0.0
                    for kk in range(K):
                        p = (n_dk_d[kk] + ab) * (self.n_kw[kk][w] + bb) / (self.n_k[kk] + Vb)
                        probs[kk] = p
                        total += p
                    r = self.rng.random() * total
                    acc = 0.0
                    new_k = K - 1
                    for kk in range(K):
                        acc += probs[kk]
                        if r <= acc:
                            new_k = kk
                            break

                    zs[i] = new_k
                    n_dk_d[new_k] += 1
                    self.n_kw[new_k][w] += 1
                    self.n_k[new_k] += 1

    def top_words(self, inv_vocab: list[str], n: int = 20) -> list[list[tuple[str, float]]]:
        out = []
        for k in range(self.K):
            row = self.n_kw[k]
            tot = self.n_k[k] or 1
            idx = sorted(range(len(row)), key=lambda w: row[w], reverse=True)[:n]
            out.append([(inv_vocab[w], row[w] / tot) for w in idx if row[w] > 0])
        return out


def load_corpus(path: str) -> tuple[list[str], list[str]]:
    files = sorted(glob.glob(os.path.join(path, "**", "*.txt"), recursive=True))
    if not files:
        raise SystemExit(f"no .txt documents under {path}")
    return files, [open(f, encoding="utf-8", errors="replace").read() for f in files]


def run(corpus_dir: str, n_topics: int, iterations: int, seed: int, top_n: int,
        out_path: str | None) -> int:
    names, raw = load_corpus(corpus_dir)
    docs_tokens = [tokenise(t) for t in raw]
    vocab = build_vocab(docs_tokens)
    if not vocab:
        raise SystemExit("empty vocabulary after preprocessing - corpus too small or too uniform")
    inv = [""] * len(vocab)
    for w, i in vocab.items():
        inv[i] = w
    docs = [[vocab[t] for t in d if t in vocab] for d in docs_tokens]
    kept = sum(len(d) for d in docs)
    print(f"{len(docs)} documents, {kept:,} tokens, vocabulary {len(vocab):,}")
    if kept < 1000:
        print("[warn] very small corpus: topics from this will not be stable. Iliadis & Acker used\n"
              "       155 patents and >2.5M words; treat anything smaller as indicative only.",
              file=sys.stderr)

    lda = LDA(n_topics, seed=seed)
    lda.fit(docs, len(vocab), iterations=iterations)
    topics = lda.top_words(inv, top_n)

    lines = [f"# Patent corpus topics", "",
             f"Corpus: `{corpus_dir}` — {len(docs)} documents, {kept:,} tokens, "
             f"vocabulary {len(vocab):,}.",
             f"Model: collapsed-Gibbs LDA, K={n_topics}, {iterations} iterations, seed {seed}.", "",
             "Topics are unnamed by construction. Naming them is the analyst's interpretive step, "
             "as it was in the source method — do not present an inferred topic as a finding "
             "without reading the patents behind it.", ""]
    for k, words in enumerate(topics):
        terms = ", ".join(w for w, _ in words)
        print(f"topic {k:>2}: {terms}")
        lines.append(f"**Topic {k}** — {terms}")
        lines.append("")

    if out_path:
        dest = out_path if os.path.isabs(out_path) else os.path.join(ROOT, out_path)
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        with open(dest, "w", encoding="utf-8") as fh:
            fh.write("\n".join(lines))
        print(f"\nwrote {os.path.relpath(dest, ROOT)}")
    return 0


# --- validation -------------------------------------------------------------------------------

PLANTED = {
    "cooling":  "chiller coolant evaporative immersion airflow plenum condenser refrigerant heat exchanger".split(),
    "power":    "busbar switchgear rectifier inverter generator transformer voltage feeder ups battery".split(),
    "water":    "potable recycled effluent blowdown makeup treatment borehole reclaimed greywater cooling_tower".split(),
    "network":  "fibre transceiver latency router backbone peering interconnect spine leaf topology".split(),
}


def synthetic_corpus(seed: int = 7, docs_per_topic: int = 40, doc_len: int = 120) -> list[str]:
    """Documents drawn from four disjoint planted vocabularies, plus shared boilerplate noise."""
    rng = random.Random(seed)
    noise = "embodiment plurality wherein comprising apparatus said configured".split()
    out = []
    for words in PLANTED.values():
        for _ in range(docs_per_topic):
            body = [rng.choice(words) for _ in range(doc_len)]
            body += [rng.choice(noise) for _ in range(doc_len // 3)]
            rng.shuffle(body)
            out.append(" ".join(body))
    return out


def selftest() -> int:
    """
    Plant four topics with disjoint vocabularies, then assert LDA recovers them. This has a real
    ground truth and can genuinely fail; it is the only claim this file makes about correctness.
    """
    failures = 0

    def check(name: str, ok: bool, detail: str = "") -> None:
        nonlocal failures
        if ok:
            print(f"[pass] {name}")
        else:
            failures += 1
            print(f"[FAIL] {name}{(' - ' + detail) if detail else ''}")

    # Preprocessing
    toks = tokenise("The apparatus comprises a plurality of chillers and evaporative condensers.")
    check("tokenise strips stopwords and patent boilerplate",
          "apparatus" not in toks and "comprises" not in toks and "plurality" not in toks,
          f"got {toks}")
    check("tokenise singularises plurals", "chiller" in toks and "condenser" in toks, f"got {toks}")

    raw = synthetic_corpus()
    docs_tokens = [tokenise(t) for t in raw]
    vocab = build_vocab(docs_tokens)
    check("boilerplate noise is excluded from the vocabulary",
          not ({"embodiment", "plurality", "wherein", "comprising"} & set(vocab)),
          f"leaked {sorted({'embodiment','plurality','wherein','comprising'} & set(vocab))}")

    inv = [""] * len(vocab)
    for w, i in vocab.items():
        inv[i] = w
    docs = [[vocab[t] for t in d if t in vocab] for d in docs_tokens]

    lda = LDA(4, seed=11)
    lda.fit(docs, len(vocab), iterations=200)
    topics = [set(w for w, _ in t[:10]) for t in lda.top_words(inv, 10)]

    # Each planted topic must be recovered by some inferred topic. Vocabularies are disjoint, so a
    # working sampler should match nearly all of them; 7 of 10 is a deliberately loose floor.
    for name, words in PLANTED.items():
        planted = set(tokenise(" ".join(words)))
        best = max((len(planted & t) for t in topics), default=0)
        check(f"recovers planted topic '{name}' ({best}/10 terms)", best >= 7)

    # And the mapping must be one-to-one: four planted topics should not collapse onto one.
    claimed = set()
    for words in PLANTED.values():
        planted = set(tokenise(" ".join(words)))
        best_i = max(range(len(topics)), key=lambda i: len(planted & topics[i]))
        claimed.add(best_i)
    check(f"four planted topics map to four distinct inferred topics ({len(claimed)}/4)",
          len(claimed) == 4)

    print(f"\n{'FAILED' if failures else 'ok'}: {failures} failure(s)")
    return 1 if failures else 0


def main(argv: list[str]) -> int:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--corpus", help="directory of .txt patent documents, one per file")
    p.add_argument("--topics", type=int, default=20)
    p.add_argument("--iterations", type=int, default=300)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--top-words", type=int, default=20)
    p.add_argument("--out", help="write a markdown topic report here")
    p.add_argument("--selftest", action="store_true", help="offline: planted-topic recovery test")
    a = p.parse_args(argv)

    if a.selftest:
        return selftest()
    if a.corpus:
        return run(a.corpus, a.topics, a.iterations, a.seed, a.top_words, a.out)
    p.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
