from meshcompute.coordinator.domain.states import JobStatus, TaskStatus, can_transition


def test_task_state_machine_accepts_retry_and_completion() -> None:
    assert can_transition(TaskStatus.PENDING, TaskStatus.RUNNING)
    assert can_transition(TaskStatus.RUNNING, TaskStatus.PENDING)
    assert can_transition(TaskStatus.RUNNING, TaskStatus.COMPLETED)


def test_task_state_machine_rejects_terminal_reopen() -> None:
    assert not can_transition(TaskStatus.COMPLETED, TaskStatus.PENDING)


def test_job_terminal_state_is_not_reopened() -> None:
    assert not can_transition(JobStatus.COMPLETED, JobStatus.RUNNING)
