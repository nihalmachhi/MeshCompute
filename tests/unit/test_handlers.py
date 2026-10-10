from meshcompute.worker.handlers.dataset_aggregate import DatasetAggregateHandler
from meshcompute.worker.handlers.word_count import WordCountHandler


def test_word_count_merges_chunk_results() -> None:
    handler = WordCountHandler()
    first = {"word_counts": {"mesh": 1, "compute": 1}}
    second = {"word_counts": {"compute": 1, "tasks": 1}}
    assert handler.merge([first, second]) == {"total_words": 4, "unique_words": 3, "word_counts": {"compute": 2, "mesh": 1, "tasks": 1}}


def test_dataset_aggregate_merges_numeric_partials() -> None:
    handler = DatasetAggregateHandler()
    output = handler.merge([
        {"count": 3, "sum": 6.0, "min": 1.0, "max": 3.0},
        {"count": 2, "sum": 9.0, "min": 4.0, "max": 5.0},
    ])
    assert output["count"] == 5
    assert output["sum"] == 15
    assert output["mean"] == 3.0
