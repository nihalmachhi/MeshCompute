from meshcompute.handlers.dataset_aggregate import DatasetAggregateHandler
from meshcompute.handlers.word_count import WordCountHandler


def test_word_count_merges_chunk_results() -> None:
    handler = WordCountHandler()
    first = {"word_counts": {"mesh": 1, "compute": 1}}
    second = {"word_counts": {"compute": 1, "tasks": 1}}
    assert handler.merge([first, second]) == {
        "total_words": 4,
        "unique_words": 3,
        "word_counts": {"compute": 2, "mesh": 1, "tasks": 1},
    }


def test_dataset_aggregate_merges_numeric_partials() -> None:
    handler = DatasetAggregateHandler()
    output = handler.merge(
        [
            {"count": 3, "sum": 6.0, "min": 1.0, "max": 3.0},
            {"count": 2, "sum": 9.0, "min": 4.0, "max": 5.0},
        ]
    )
    assert output["count"] == 5
    assert output["sum"] == 15
    assert output["mean"] == 3.0


def test_dataset_chunks_use_record_aware_byte_ranges_for_multiline_csv(monkeypatch, tmp_path):
    from meshcompute.core.settings import get_settings

    csv_path = tmp_path / "quoted.csv"
    csv_path.write_text(
        'value,note\n1,"two lines\ninside one record"\n2,plain\n3,"another\nrecord"\n',
        encoding="utf-8",
        newline="",
    )
    monkeypatch.setenv("MESH_COMPUTE_DATA_DIR", str(tmp_path))
    get_settings.cache_clear()
    handler = DatasetAggregateHandler()
    chunks = handler.split("quoted.csv", {"rows_per_task": 1, "value_column": "value"})
    assert len(chunks) == 3
    assert all("byte_start" in chunk and "byte_end" in chunk for chunk in chunks)
    partials = [handler.execute(chunk) for chunk in chunks]
    assert sum(item["count"] for item in partials) == 3
    assert sum(item["sum"] for item in partials) == 6
    get_settings.cache_clear()
