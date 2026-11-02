"""Inverted index build with small query support."""

from collections import defaultdict

from .tokenize import tokenize


def build_index(documents: list[str]) -> dict[str, list[int]]:
    index = defaultdict(list)
    for doc_id, doc in enumerate(documents):
        for term in set(tokenize(doc)):
            index[term].append(doc_id)
    return dict(index)


def query(index: dict[str, list[int]], term: str) -> list[int]:
    return index.get(term.lower(), [])
