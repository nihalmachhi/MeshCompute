"""Deterministic synthetic evaluations for optional vision and text handlers."""

from __future__ import annotations

import tempfile
from itertools import combinations
from pathlib import Path
from typing import Any

from meshcompute.handlers.nlp.minhash_dedupe import jaccard_estimate, minhash_signature, shingles


def _pair_metrics(labels: list[bool], predictions: list[bool]) -> dict[str, float | int]:
    """Compute pairwise precision and recall with explicit zero-denominator behavior."""
    pairs = zip(labels, predictions, strict=True)
    values = list(pairs)
    true_positive = sum(actual and predicted for actual, predicted in values)
    false_positive = sum(not actual and predicted for actual, predicted in values)
    false_negative = sum(actual and not predicted for actual, predicted in values)
    precision = (
        true_positive / (true_positive + false_positive) if true_positive + false_positive else 0
    )
    recall = (
        true_positive / (true_positive + false_negative) if true_positive + false_negative else 0
    )
    return {
        "pairs": len(labels),
        "true_positives": true_positive,
        "false_positives": false_positive,
        "false_negatives": false_negative,
        "precision": round(precision, 3),
        "recall": round(recall, 3),
    }


def evaluate_text_duplicates() -> dict[str, float | int | str]:
    """Evaluate MinHash on generated multilingual documents and small edits."""
    documents = {
        "en-a": "the quick brown fox jumps over the quiet river every morning " * 8,
        "en-b": "the quick brown fox jumps over a quiet river every morning " * 8,
        "fr-a": "bonjour le monde nous apprenons les systèmes distribués ensemble " * 8,
        "fr-b": "bonjour le monde nous apprenons les systèmes distribués aujourd'hui " * 8,
        "hi-a": "namaste duniya hum milkar naye vichar seekhte hain " * 8,
        "hi-b": "namaste duniya hum milkar naye vichar banate hain " * 8,
        "negative-a": "database transactions preserve consistent durable records " * 8,
        "negative-b": "mountains rivers forests and birds shape a changing landscape " * 8,
    }
    signatures = {
        name: minhash_signature(shingles(text), num_hashes=64) for name, text in documents.items()
    }
    labels: list[bool] = []
    predictions: list[bool] = []
    for left, right in combinations(documents, 2):
        labels.append(
            left.split("-")[0] == right.split("-")[0] and left.endswith("a") and right.endswith("b")
        )
        predictions.append(jaccard_estimate(signatures[left], signatures[right]) >= 0.45)
    return {
        "method": "64-permutation MinHash; similarity threshold 0.45",
        **_pair_metrics(labels, predictions),
    }


def evaluate_vision_duplicates() -> dict[str, float | int | str]:
    """Evaluate dHash on generated originals and resize/crop/brightness/JPEG variants."""
    try:
        from PIL import Image, ImageDraw, ImageEnhance
    except ImportError as exc:  # pragma: no cover - covered in the vision extra job
        raise RuntimeError("install the vision extra to generate image evaluations") from exc

    from meshcompute.handlers.vision.phash_dedupe import dhash, hamming

    images: dict[str, tuple[str, Any]] = {}
    for group in range(3):
        image = Image.new("RGB", (96, 96), "white")
        draw = ImageDraw.Draw(image)
        if group == 0:
            for x in range(0, 96, 16):
                draw.rectangle((x, 0, x + 7, 95), fill="black")
        elif group == 1:
            for x in range(0, 96, 24):
                for y in range(0, 96, 24):
                    if (x + y) % 48 == 0:
                        draw.rectangle((x, y, x + 11, y + 11), fill="black")
        else:
            draw.ellipse((14, 14, 82, 82), outline="black", width=7)
            draw.ellipse((34, 34, 62, 62), fill="black")
        crop = image.crop((6, 6, 90, 90)).resize((96, 96))
        variants = [
            image,
            image.resize((48, 48)).resize((96, 96)),
            ImageEnhance.Brightness(image).enhance(1.2),
            crop,
        ]
        for variant_index, variant in enumerate(variants):
            images[f"{group}-{variant_index}"] = (str(group), variant.copy())

    labels: list[bool] = []
    predictions: list[bool] = []
    with tempfile.TemporaryDirectory(prefix="meshcompute-vision-") as temp_dir:
        paths: dict[str, Path] = {}
        for name, (_group, image) in images.items():
            path = Path(temp_dir) / f"{name}.jpg"
            image.save(path, format="JPEG", quality=68)
            paths[name] = path
        hashes = {name: dhash(str(path)) for name, path in paths.items()}
        for left, right in combinations(images, 2):
            labels.append(images[left][0] == images[right][0])
            predictions.append(hamming(hashes[left], hashes[right]) <= 12)
    return {"method": "64-bit dHash; Hamming threshold 12", **_pair_metrics(labels, predictions)}


def generate_evaluation(seed: int = 42) -> dict[str, object]:
    """Combine seeded scheduler metrics with generated vision and text pair evaluations."""
    del seed  # The fixed synthetic data itself is deterministic and has no random choices.
    return {
        "synthetic": True,
        "vision_duplicate_detection": evaluate_vision_duplicates(),
        "text_duplicate_detection": evaluate_text_duplicates(),
    }
