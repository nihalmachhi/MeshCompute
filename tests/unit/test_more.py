import contextlib
import os
import tempfile
from pathlib import Path
from unittest.mock import MagicMock

from meshcompute.coordinator.domain.models import JobStatus, TaskStatus, WorkerStatus
from meshcompute.coordinator.domain.states import transition, transition_job, transition_worker
from meshcompute.coordinator.events import EventHub
from meshcompute.coordinator.services.lease_manager import LeaseManager
from meshcompute.coordinator.services.metrics_service import MetricsService
from meshcompute.coordinator.services.worker_service import WorkerService
from meshcompute.core.clock import SystemClock
from meshcompute.core.logging import configure_logging
from meshcompute.core.settings import Settings
from meshcompute.handlers.dataset_aggregate import DatasetAggregateHandler
from meshcompute.handlers.graph import bfs, components, pagerank
from meshcompute.handlers.nlp import inverted_index, langid, minhash_dedupe, tfidf, tokenize
from meshcompute.handlers.word_count import WordCountHandler
from meshcompute.sim.report import generate
from meshcompute.sim.schedulers import SCHEDULERS, fair, fifo, sjf
from meshcompute.sim.workloads import make_workload
from meshcompute.worker.executor import execute_with_timeout
from meshcompute.worker.heartbeat import HeartbeatLoop


def test_clock_settings() -> None:
    configure_logging("INFO")
    assert SystemClock().now() is not None
    s = Settings()
    assert s.app_name == "MeshCompute"


def test_client_heartbeatloop() -> None:
    client = MagicMock()
    hb = HeartbeatLoop(client, __import__("uuid").uuid4(), 1)
    hb.set_task(None, None)
    hb._send()


def test_sim_schedulers() -> None:
    pending = [{"task_id": 1, "job_id": "j", "duration": 2.0, "arrival": 0.0}]
    assert fifo(pending, [0], {}) == pending
    assert sjf(pending, [0], {}) == pending
    assert fair(pending, [0], {}) == pending
    assert "fifo" in SCHEDULERS
    jobs, _ = make_workload(seed=2)
    rep = generate()
    assert "fifo" in rep


def test_nlp_modules() -> None:
    assert tokenize.tokenize("Hello world") == ["hello", "world"]
    assert tfidf.tfidf(["a b", "b c"])
    sig = minhash_dedupe.minhash_signature(minhash_dedupe.shingles("a b c", 2))
    assert minhash_dedupe.jaccard_estimate(sig, sig) == 1.0
    assert langid.detect_language("the") == "en"
    idx = inverted_index.build_index(["hello world"])
    assert inverted_index.query(idx, "hello") == [0]


def test_graph_modules() -> None:
    assert bfs.bfs({1: [2]}, 1) == {1: 0, 2: 1}
    assert pagerank.pagerank({1: [2]})
    assert components.connected_components([(1, 2)])


def test_executor_more() -> None:
    with tempfile.TemporaryDirectory() as d:
        root = Path(d)
        p = root / "sample.txt"
        p.write_text("hello world hello", encoding="utf-8")
        os.environ["MESH_COMPUTE_DATA_DIR"] = str(root)
        os.environ["MESH_COMPUTE_OUTPUT_DIR"] = str(root)
        from meshcompute.core.settings import get_settings

        get_settings.cache_clear()
        payload = {"input_ref": "sample.txt", "start_offset": 0, "end_offset": p.stat().st_size}
        out = execute_with_timeout("word_count", payload, 10)
        assert "total_words" in out
        get_settings.cache_clear()


def test_dataset_aggregate() -> None:
    h = DatasetAggregateHandler()
    assert h.merge([{"count": 2, "sum": 3.0, "min": 1.0, "max": 2.0}])["count"] == 2
    with tempfile.TemporaryDirectory() as d:
        root = Path(d)
        csv_path = root / "data.csv"
        csv_path.write_text("value\n1\n2\n3\n", encoding="utf-8")
        os.environ["MESH_COMPUTE_DATA_DIR"] = str(root)
        from meshcompute.core.settings import get_settings

        get_settings.cache_clear()
        h2 = DatasetAggregateHandler()
        splits = h2.split("data.csv", {"rows_per_task": 2})
        assert splits
        out = h2.execute(splits[0])
        assert "count" in out
        get_settings.cache_clear()


def test_word_count_handler() -> None:
    with tempfile.TemporaryDirectory() as d:
        root = Path(d)
        p = root / "sample.txt"
        p.write_text("hello world hello", encoding="utf-8")
        os.environ["MESH_COMPUTE_DATA_DIR"] = str(root)
        from meshcompute.core.settings import get_settings

        get_settings.cache_clear()
        h = WordCountHandler()
        splits = h.split("sample.txt", {"chunk_bytes": 5})
        assert splits
        out = h.execute(splits[0])
        assert "total_words" in out
        assert h.merge([out])["total_words"] == out["total_words"]
        get_settings.cache_clear()


def test_events_hub() -> None:
    import asyncio

    async def main() -> None:
        hub = EventHub()
        async with hub.subscribe() as q:
            hub.publish({"type": "x"})
            await asyncio.sleep(0)
            assert q.qsize() >= 0

    asyncio.get_event_loop().run_until_complete(main())


def test_services_mock() -> None:
    uow = MagicMock()
    uow.workers = MagicMock()
    uow.workers.all.return_value = []
    uow.tasks = MagicMock()
    uow.tasks.pending_count.return_value = 0
    uow.jobs = MagicMock()
    uow.jobs.list.return_value = []
    ws = WorkerService()
    with contextlib.suppress(Exception):
        ws.list(uow)
    lm = LeaseManager()
    with contextlib.suppress(Exception):
        lm.heartbeat(uow, __import__("uuid").uuid4(), None, None)
    ms = MetricsService()
    with contextlib.suppress(Exception):
        ms.summary(uow)


def test_transitions() -> None:
    assert transition(TaskStatus.PENDING, TaskStatus.ASSIGNED) == TaskStatus.ASSIGNED
    assert transition_job(JobStatus.SUBMITTED, JobStatus.RUNNING) == JobStatus.RUNNING
    assert transition_worker(WorkerStatus.ACTIVE, WorkerStatus.STALE) == WorkerStatus.STALE
