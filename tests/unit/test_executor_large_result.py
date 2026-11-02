from pathlib import Path

from meshcompute.core.settings import get_settings
from meshcompute.worker.executor import execute_with_timeout


def test_worker_drains_multi_megabyte_result_without_timeout(monkeypatch, tmp_path):
    input_path: Path = tmp_path / "unique-words.txt"
    word_count = 180_000
    input_path.write_text(
        " ".join(f"unique{index}" for index in range(word_count)), encoding="utf-8"
    )
    monkeypatch.setenv("MESH_COMPUTE_DATA_DIR", str(tmp_path))
    get_settings.cache_clear()
    try:
        result = execute_with_timeout(
            "word_count",
            {
                "input_ref": input_path.name,
                "start_offset": 0,
                "end_offset": input_path.stat().st_size,
            },
            timeout_seconds=30,
        )
    finally:
        get_settings.cache_clear()
    serialized_size = len(repr(result).encode("utf-8"))
    assert serialized_size > 2_000_000
    assert result["total_words"] == word_count
    assert len(result["word_counts"]) == word_count
