"""Single source of truth for job, task, and worker state transitions."""
from meshcompute.common.errors import InvalidTransitionError
from meshcompute.coordinator.domain.models import JobStatus,TaskStatus,WorkerStatus

TASK_TRANSITIONS={
    TaskStatus.PENDING:{TaskStatus.ASSIGNED},
    TaskStatus.ASSIGNED:{TaskStatus.RUNNING,TaskStatus.PENDING,TaskStatus.FAILED},
    TaskStatus.RUNNING:{TaskStatus.COMPLETED,TaskStatus.PENDING,TaskStatus.FAILED},
    TaskStatus.COMPLETED:set(),TaskStatus.FAILED:set(),
}
JOB_TRANSITIONS={
    JobStatus.SUBMITTED:{JobStatus.RUNNING,JobStatus.COMPLETED,JobStatus.FAILED},
    JobStatus.RUNNING:{JobStatus.COMPLETED,JobStatus.FAILED},
    JobStatus.COMPLETED:set(),JobStatus.FAILED:set(),
}
WORKER_TRANSITIONS={
    WorkerStatus.ACTIVE:{WorkerStatus.STALE,WorkerStatus.OFFLINE},
    WorkerStatus.STALE:{WorkerStatus.ACTIVE,WorkerStatus.OFFLINE},
    WorkerStatus.OFFLINE:{WorkerStatus.ACTIVE},
}
def transition(current: str|TaskStatus,target: TaskStatus) -> TaskStatus:
    """Return a legal next task state or reject the transition."""
    state=TaskStatus(current)
    if target not in TASK_TRANSITIONS[state]: raise InvalidTransitionError(f"task transition {state} -> {target} is not allowed")
    return target
def transition_job(current: str|JobStatus,target: JobStatus) -> JobStatus:
    """Return a legal next job state or reject the transition."""
    state=JobStatus(current)
    if target not in JOB_TRANSITIONS[state]: raise InvalidTransitionError(f"job transition {state} -> {target} is not allowed")
    return target
def transition_worker(current: str|WorkerStatus,target: WorkerStatus) -> WorkerStatus:
    """Return a legal next worker state or reject the transition."""
    state=WorkerStatus(current)
    if target not in WORKER_TRANSITIONS[state]: raise InvalidTransitionError(f"worker transition {state} -> {target} is not allowed")
    return target
