"""Pydantic request and response models for the public API."""
from datetime import datetime
from typing import Any,Literal
from uuid import UUID
from pydantic import BaseModel,Field

JobType=Literal["word_count","image_resize","dataset_aggregate"]
class JobSubmission(BaseModel):
    """Validated built-in job request; no code can be submitted."""
    job_type: JobType
    input_ref: str=Field(min_length=1,max_length=1024)
    options: dict[str,Any]=Field(default_factory=dict)
class JobAccepted(BaseModel):
    """Immediate response to an accepted job."""
    job_id: UUID
    status: str
    task_count: int
class JobView(BaseModel):
    """Job summary with counts for all task states."""
    id: UUID
    job_type: str
    status: str
    task_count: int
    tasks_by_state: dict[str,int]
    created_at: datetime
    finished_at: datetime|None
class JobPage(BaseModel):
    """Stable paginated job list response."""
    items: list[JobView]
    limit: int
    offset: int
class WorkerRegistration(BaseModel):
    """Worker self-description sent during registration."""
    name: str=Field(min_length=1,max_length=120)
class WorkerRegistered(BaseModel):
    """Coordinator-created worker identity and heartbeat cadence."""
    worker_id: UUID
    heartbeat_interval_seconds: int
class HeartbeatRequest(BaseModel):
    """Worker liveness plus the active lease fencing token."""
    task_id: UUID|None=None
    attempt: int|None=Field(default=None,ge=1)
class TaskClaimRequest(BaseModel):
    """Worker requests the next available task."""
    worker_id: UUID
class ClaimedTask(BaseModel):
    """Task payload and attempt fencing token sent to a worker."""
    task_id: UUID
    job_id: UUID
    task_index: int
    job_type: str
    payload: dict[str,Any]
    attempt: int
    lease_expires_at: datetime
class TaskIdentity(BaseModel):
    """Worker identity and current attempt required for task mutations."""
    worker_id: UUID
    attempt: int=Field(ge=1)
class TaskStartRequest(TaskIdentity):
    """Worker starts the task it owns."""
class TaskCompleteRequest(TaskIdentity):
    """Worker submits one JSON result with measured runtime."""
    output: dict[str,Any]
    duration_ms: float=Field(ge=0)
class TaskFailureRequest(TaskIdentity):
    """Worker reports a bounded error summary for retry handling."""
    error: str=Field(min_length=1,max_length=1000)
class TaskMutationResponse(BaseModel):
    """Stable response for task completion or failure."""
    task_id: UUID
    status: str
    idempotent: bool=False

class WorkerHeartbeatResponse(BaseModel):
    """Worker heartbeat acknowledgement with renewed lease when applicable."""
    worker_id: UUID
    lease_expires_at: datetime|None
class TaskPageItem(BaseModel):
    """Task row shown on the dashboard."""
    task_id: UUID
    task_index: int
    status: str
    attempt: int
    max_attempts: int
    worker_id: UUID|None
    lease_expires_at: datetime|None
    queued_at: datetime
    started_at: datetime|None
    finished_at: datetime|None

class WorkerView(BaseModel):
    """Worker status row used by the operational dashboard."""
    worker_id: UUID
    name: str
    status: str
    last_heartbeat_at: datetime
    heartbeat_age_seconds: int
    current_task_id: UUID|None
