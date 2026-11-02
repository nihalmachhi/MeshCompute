"""Dominant colours via simple quantisation (optional [vision] extra)."""

try:
    from PIL import Image
except Exception:  # pragma: no cover
    Image = None


def dominant_colors(path: str, k: int = 5) -> list[tuple[int, int, int]]:
    if Image is None:
        raise RuntimeError("Pillow is required for vision handlers")
    with Image.open(path) as im:
        im = im.convert("RGB").resize((64, 64))
        colors = im.getcolors(maxcolors=64 * 64) or []
        colors.sort(reverse=True)
        return [c[1] for c in colors[:k]]
