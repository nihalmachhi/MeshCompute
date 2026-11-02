"""Dominant colours via simple quantisation (optional [vision] extra)."""

from meshcompute.handlers.vision.safety import open_safe_image


def dominant_colors(path: str, k: int = 5) -> list[tuple[int, int, int]]:
    im = open_safe_image(path).convert("RGB").resize((64, 64))
    colors = im.getcolors(maxcolors=64 * 64) or []
    colors.sort(reverse=True)
    return [c[1] for c in colors[:k]]
