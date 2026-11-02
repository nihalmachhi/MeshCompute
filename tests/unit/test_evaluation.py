"""Generated quality reports remain deterministic and report measured pair counts."""

import pytest
from PIL import Image

from meshcompute.evaluation import evaluate_text_duplicates, evaluate_vision_duplicates
from meshcompute.handlers.vision.safety import open_safe_image


def test_text_duplicate_report_is_generated_and_bounded() -> None:
    first = evaluate_text_duplicates()
    assert first == evaluate_text_duplicates()
    assert first["pairs"] == 28
    assert 0 <= first["precision"] <= 1
    assert 0 <= first["recall"] <= 1
    assert "MinHash" in first["method"]


def test_vision_duplicate_report_is_generated_and_bounded() -> None:
    pytest.importorskip("PIL", reason="install the vision extra to run image evaluation")
    first = evaluate_vision_duplicates()
    assert first == evaluate_vision_duplicates()
    assert first["pairs"] == 66
    assert 0 <= first["precision"] <= 1
    assert 0 <= first["recall"] <= 1
    assert "dHash" in first["method"]


def test_image_decoder_rejects_unsupported_format_and_pixel_bomb(tmp_path) -> None:
    gif = tmp_path / "input.gif"
    Image.new("RGB", (8, 8)).save(gif)
    with pytest.raises(ValueError, match="format"):
        open_safe_image(gif)

    large = tmp_path / "large.png"
    Image.new("RGB", (5000, 4000)).save(large)
    with pytest.raises(ValueError, match="pixel limit"):
        open_safe_image(large)
