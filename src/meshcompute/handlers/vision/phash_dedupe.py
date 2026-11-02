"""Perceptual hashing and union-find clustering (optional [vision] extra)."""

from meshcompute.handlers.vision.safety import open_safe_image


def dhash(path: str, size: int = 8) -> int:
    from PIL import Image

    im = (
        open_safe_image(path)
        .convert("L")
        .resize(
            (size + 1, size),
            Image.Resampling.LANCZOS if hasattr(Image, "Resampling") else Image.LANCZOS,
        )
    )
    bits = 0
    for y in range(size):
        for x in range(size):
            left = im.getpixel((x, y))
            right = im.getpixel((x + 1, y))
            bits = (bits << 1) | (1 if left > right else 0)
    return bits


def hamming(a: int, b: int) -> int:
    return bin(a ^ b).count("1")


class UnionFind:
    def __init__(self):
        self.parent = {}

    def find(self, x):
        self.parent.setdefault(x, x)
        while self.parent[x] != x:
            self.parent[x] = self.parent[self.parent[x]]
            x = self.parent[x]
        return x

    def union(self, a, b):
        ra, rb = self.find(a), self.find(b)
        if ra != rb:
            self.parent[ra] = rb

    def clusters(self):
        groups = {}
        for x in self.parent:
            groups.setdefault(self.find(x), []).append(x)
        return list(groups.values())


def cluster_hashes(hashes: dict[str, int], threshold: int = 10) -> list[list[str]]:
    uf = UnionFind()
    for k in hashes:
        uf.find(k)
    items = list(hashes.items())
    for i in range(len(items)):
        for j in range(i + 1, len(items)):
            if hamming(items[i][1], items[j][1]) <= threshold:
                uf.union(items[i][0], items[j][0])
    return uf.clusters()
