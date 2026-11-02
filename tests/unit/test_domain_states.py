from meshcompute.coordinator.domain.states import JobStatus, TaskStatus, transition, transition_job


def test_task_state_machine_accepts_retry_and_completion() -> None:
    assert transition(TaskStatus.PENDING, TaskStatus.ASSIGNED) == TaskStatus.ASSIGNED
    assert transition(TaskStatus.ASSIGNED, TaskStatus.PENDING) == TaskStatus.PENDING
    assert transition(TaskStatus.RUNNING, TaskStatus.COMPLETED) == TaskStatus.COMPLETED


def test_task_state_machine_rejects_terminal_reopen() -> None:
    try:
        transition(TaskStatus.COMPLETED, TaskStatus.PENDING)
        raised = False
    except Exception:
        raised = True
    assert raised


def test_job_terminal_state_is_not_reopened() -> None:
    try:
        transition_job(JobStatus.COMPLETED, JobStatus.RUNNING)
        raised = False
    except Exception:
        raised = True
    assert raised
