"""Bounded image decoding shared by optional Pillow-based handlers."""

from __future__ import annotations

import warnings
from pathlib import Path
from typing import Any

MAX_IMAGE_PIXELS = 16_000_000
ALLOWED_IMAGE_FORMATS = ("JPEG", "PNG", "BMP")


def open_safe_image(path: str | Path) -> Any:
    """Load an allowed raster image after enforcing format and pixel-count bounds."""
    try:
        from PIL import Image, UnidentifiedImageError
    except ImportError as exc:  # pragma: no cover - optional vision dependency
        raise RuntimeError("Pillow is required for vision handlers") from exc

    with warnings.catch_warnings():
        warnings.simplefilter("error", Image.DecompressionBombWarning)
        try:
            with Image.open(path, formats=ALLOWED_IMAGE_FORMATS) as image:
                width, height = image.size
                if width <= 0 or height <= 0 or width * height > MAX_IMAGE_PIXELS:
                    raise ValueError("image exceeds the configured pixel limit")
                image.load()
                return image.copy()
        except UnidentifiedImageError as exc:
            raise ValueError("unsupported or invalid image format") from exc
