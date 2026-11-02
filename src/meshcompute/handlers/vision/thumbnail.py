"""Image thumbnails (optional [vision] extra)."""

from meshcompute.handlers.vision.safety import open_safe_image


def make_thumbnail(src_path: str, dst_path: str, size: tuple[int, int] = (64, 64)) -> str:
    im = open_safe_image(src_path)
    im.thumbnail(size)
    im.save(dst_path)
    return dst_path
