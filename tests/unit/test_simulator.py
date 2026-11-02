from meshcompute.sim.engine import simulate


def test_worker_failure_requeues_task_and_keeps_utilization_bounded():
    jobs = [
        {
            "job_id": "long-job",
            "tasks": [
                {
                    "task_id": task_id,
                    "job_id": "long-job",
                    "duration": 6.0,
                    "arrival": 0.0,
                }
                for task_id in range(4)
            ],
        }
    ]
    baseline = simulate(2, jobs, "fifo")
    recovered = simulate(2, jobs, "fifo", kill_worker=True)

    assert recovered["retries"] == 1
    assert recovered["makespan"] > baseline["makespan"]
    assert 0 < recovered["utilization"] <= 1
    failed_attempts = [attempt for attempt in recovered["schedule"] if not attempt["success"]]
    assert len(failed_attempts) == 1
    assert failed_attempts[0]["end"] == 2.0
