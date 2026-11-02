import tempfile
from pathlib import Path

from meshcompute.coordinator.domain.states import JobStatus, TaskStatus, can_transition
from meshcompute.handlers.graph.bfs import bfs
from meshcompute.handlers.graph.components import connected_components
from meshcompute.handlers.graph.pagerank import pagerank
from meshcompute.handlers.nlp.inverted_index import build_index, query
from meshcompute.handlers.nlp.langid import detect_language
from meshcompute.handlers.nlp.minhash_dedupe import jaccard_estimate, minhash_signature, shingles
from meshcompute.handlers.nlp.tfidf import tfidf
from meshcompute.handlers.nlp.tokenize import tokenize
from meshcompute.sim.engine import simulate
from meshcompute.sim.prng import mulberry32
from meshcompute.sim.workloads import make_workload
from meshcompute.worker.executor import execute_with_timeout


def test_states() -> None:
    assert can_transition(TaskStatus.PENDING, TaskStatus.ASSIGNED)
    assert not can_transition(JobStatus.COMPLETED, JobStatus.RUNNING)


def test_graph() -> None:
    assert bfs({1: [2], 2: []}, 1) == {1: 0, 2: 1}
    assert pagerank({1: [2], 2: []})
    assert connected_components([(1, 2), (3, 4)]) == [[1, 2], [3, 4]]


def test_nlp() -> None:
    assert tokenize("Hello world") == ["hello", "world"]
    assert tfidf(["a b", "b c"])
    sig = minhash_signature(shingles("the quick brown fox", 2))
    assert jaccard_estimate(sig, sig) == 1.0
    assert detect_language("the the the") == "en"
    idx = build_index(["hello world", "world peace"])
    assert query(idx, "world") == [0, 1]


def test_sim() -> None:
    jobs, _ = make_workload(seed=1)
    res = simulate(2, jobs, "fifo")
    assert "makespan" in res
    rng = mulberry32(1)
    assert 0.0 <= rng() <= 1.0


def test_executor() -> None:
    from meshcompute.core.settings import get_settings

    get_settings.cache_clear()
    with tempfile.TemporaryDirectory() as d:
        root = Path(d)
        p = root / "sample.txt"
        p.write_text("hello world hello", encoding="utf-8")
        # data dir set to root
        import os

        os.environ["MESH_COMPUTE_DATA_DIR"] = str(root)
        os.environ["MESH_COMPUTE_OUTPUT_DIR"] = str(root)
        from meshcompute.core.settings import get_settings

        get_settings.cache_clear()
        payload = {"input_ref": "sample.txt", "start_offset": 0, "end_offset": p.stat().st_size}
        out = execute_with_timeout("word_count", payload, 10)
        assert "total_words" in out
    get_settings.cache_clear()
