"""Image thumbnails (optional [vision] extra)."""

try:
    from PIL import Image
except Exception:  # pragma: no cover
    Image = None


def make_thumbnail(src_path: str, dst_path: str, size: tuple[int, int] = (64, 64)) -> str:
    if Image is None:
        raise RuntimeError("Pillow is required for vision handlers")
    with Image.open(src_path) as im:
        im.thumbnail(size)
        im.save(dst_path)
    return dst_path
