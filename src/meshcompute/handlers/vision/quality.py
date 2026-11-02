"""Blur detection via variance of Laplacian (optional [vision] extra)."""

try:
    import cv2
    import numpy as np
except Exception:  # pragma: no cover
    cv2 = None
    np = None


def blur_score(path: str) -> float:
    if cv2 is None:
        raise RuntimeError("OpenCV is required for vision handlers")
    img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        raise RuntimeError("cannot read image")
    lap = cv2.Laplacian(img, cv2.CV_64F)
    return float(lap.var())
