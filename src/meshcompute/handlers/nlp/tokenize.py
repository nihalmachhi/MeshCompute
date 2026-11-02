"""Unicode tokenisation with bundled stop words."""

import re

STOP_WORDS = {
    "the",
    "a",
    "an",
    "and",
    "or",
    "of",
    "to",
    "in",
    "is",
    "it",
    "for",
    "on",
    "with",
    "as",
    "by",
    "at",
}


def tokenize(text: str) -> list[str]:
    return [
        t.lower() for t in re.findall(r"\b\w+\b", text, re.UNICODE) if t.lower() not in STOP_WORDS
    ]
