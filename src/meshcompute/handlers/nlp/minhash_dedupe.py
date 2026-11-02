"""MinHash and LSH for near-duplicate documents."""

import hashlib


def shingles(text: str, k: int = 3) -> set[str]:
    toks = text.split()
    return set(" ".join(toks[i : i + k]) for i in range(max(1, len(toks) - k + 1)))


def minhash_signature(shingle_set: set[str], num_hashes: int = 64) -> list[int]:
    sig = []
    for i in range(num_hashes):
        min_val = None
        for s in shingle_set:
            h = int(hashlib.md5((str(i) + s).encode()).hexdigest(), 16)
            if min_val is None or h < min_val:
                min_val = h
        sig.append(min_val if min_val is not None else 0)
    return sig


def jaccard_estimate(sig_a: list[int], sig_b: list[int]) -> float:
    if not sig_a:
        return 0.0
    return sum(1 for a, b in zip(sig_a, sig_b, strict=False) if a == b) / len(sig_a)
