from pathlib import Path
from types import SimpleNamespace

from meshcompute.core.errors import TaskExecutionError
from meshcompute.core.settings import get_settings
from meshcompute.worker import executor
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


def test_child_applies_cpu_memory_and_file_size_limits(monkeypatch):
    calls = []
    fake_resource = SimpleNamespace(
        RLIMIT_CPU=1,
        RLIMIT_AS=2,
        RLIMIT_FSIZE=3,
        setrlimit=lambda kind, limits: calls.append((kind, limits)),
    )
    monkeypatch.setattr(executor, "resource", fake_resource)

    executor._apply_resource_limits(cpu_seconds=10, memory_bytes=20, file_bytes=30)

    assert calls == [(1, (10, 10)), (2, (20, 20)), (3, (30, 30))]


def test_worker_rejects_oversized_child_result(tmp_path, monkeypatch):
    input_path = tmp_path / "small.txt"
    input_path.write_text("hello world", encoding="utf-8")
    monkeypatch.setenv("MESH_COMPUTE_DATA_DIR", str(tmp_path))
    get_settings.cache_clear()
    try:
        try:
            execute_with_timeout(
                "word_count",
                {
                    "input_ref": input_path.name,
                    "start_offset": 0,
                    "end_offset": input_path.stat().st_size,
                },
                timeout_seconds=10,
                max_result_bytes=1,
            )
        except TaskExecutionError as exc:
            assert "exceeds 1 bytes" in str(exc)
        else:
            raise AssertionError("oversized child result was accepted")
    finally:
        get_settings.cache_clear()
