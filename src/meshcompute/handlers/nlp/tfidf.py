"""TF-IDF computation."""

import math
from collections import Counter

from .tokenize import tokenize


def tfidf(documents: list[str]) -> list[dict[str, float]]:
    tokenized = [tokenize(d) for d in documents]
    n = len(tokenized)
    df = Counter()
    for toks in tokenized:
        for term in set(toks):
            df[term] += 1
    result = []
    for toks in tokenized:
        counts = Counter(toks)
        total = len(toks) or 1
        vec = {}
        for term, c in counts.items():
            idf = math.log((n + 1) / (df[term] + 1)) + 1
            vec[term] = (c / total) * idf
        result.append(vec)
    return result
