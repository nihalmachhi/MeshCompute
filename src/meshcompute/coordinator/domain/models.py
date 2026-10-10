"""Domain states independent from persistence and transport frameworks."""
from enum import StrEnum

class TaskStatus(StrEnum):
    PENDING="PENDING"
    ASSIGNED="ASSIGNED"
    RUNNING="RUNNING"
    COMPLETED="COMPLETED"
    FAILED="FAILED"

class JobStatus(StrEnum):
    SUBMITTED="SUBMITTED"
    RUNNING="RUNNING"
    COMPLETED="COMPLETED"
    FAILED="FAILED"

class WorkerStatus(StrEnum):
    ACTIVE="ACTIVE"
    STALE="STALE"
    OFFLINE="OFFLINE"
