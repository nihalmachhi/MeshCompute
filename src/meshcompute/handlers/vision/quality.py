"""Blur detection via variance of Laplacian (optional [vision] extra)."""

try:
    import cv2
    import numpy as np
except ImportError:  # pragma: no cover
    cv2 = None
    np = None

from meshcompute.handlers.vision.safety import open_safe_image


def blur_score(path: str) -> float:
    if cv2 is None:
        raise RuntimeError("OpenCV is required for vision handlers")
    image = open_safe_image(path)
    img = cv2.cvtColor(np.asarray(image.convert("RGB")), cv2.COLOR_RGB2GRAY)
    lap = cv2.Laplacian(img, cv2.CV_64F)
    return float(lap.var())
