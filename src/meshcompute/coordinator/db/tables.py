"""PostgreSQL table mappings; state changes are performed by domain services."""
from datetime import datetime
from typing import Any
from uuid import UUID,uuid4
from sqlalchemy import BigInteger,DateTime,Float,ForeignKey,Index,Integer,String,Text,UniqueConstraint,func
from sqlalchemy.dialects.postgresql import JSONB,UUID as PGUUID
from sqlalchemy.orm import DeclarativeBase,Mapped,mapped_column

class Base(DeclarativeBase):
    """Metadata root for SQLAlchemy models."""
class JobRecord(Base):
    """Persist job status and its eventual merged result."""
    __tablename__="jobs"
    id: Mapped[UUID]=mapped_column(PGUUID(as_uuid=True),primary_key=True,default=uuid4)
    job_type: Mapped[str]=mapped_column(String(80),nullable=False,index=True)
    input_ref: Mapped[str]=mapped_column(Text,nullable=False)
    chunk_count: Mapped[int]=mapped_column(Integer,nullable=False)
    status: Mapped[str]=mapped_column(String(20),nullable=False,index=True)
    result: Mapped[dict[str,Any]|None]=mapped_column(JSONB,nullable=True)
    created_at: Mapped[datetime]=mapped_column(DateTime(timezone=True),server_default=func.now(),nullable=False)
    finished_at: Mapped[datetime|None]=mapped_column(DateTime(timezone=True))
class WorkerRecord(Base):
    """Track a worker heartbeat and its currently leased task."""
    __tablename__="workers"
    id: Mapped[UUID]=mapped_column(PGUUID(as_uuid=True),primary_key=True,default=uuid4)
    name: Mapped[str]=mapped_column(String(120),nullable=False)
    status: Mapped[str]=mapped_column(String(20),nullable=False,index=True)
    registered_at: Mapped[datetime]=mapped_column(DateTime(timezone=True),server_default=func.now(),nullable=False)
    last_heartbeat_at: Mapped[datetime]=mapped_column(DateTime(timezone=True),server_default=func.now(),nullable=False,index=True)
    current_task_id: Mapped[UUID|None]=mapped_column(PGUUID(as_uuid=True),nullable=True)
class TaskRecord(Base):
    """Store a queued task payload and its fenced lease attempt."""
    __tablename__="tasks"
    __table_args__=(UniqueConstraint("job_id","task_index",name="uq_task_job_index"),
                    Index("ix_tasks_pending_queue","status","queued_at","task_index"),
                    Index("ix_tasks_lease_expiry","status","lease_expires_at"))
    id: Mapped[UUID]=mapped_column(PGUUID(as_uuid=True),primary_key=True,default=uuid4)
    job_id: Mapped[UUID]=mapped_column(PGUUID(as_uuid=True),ForeignKey("jobs.id",ondelete="CASCADE"),nullable=False,index=True)
    task_index: Mapped[int]=mapped_column(Integer,nullable=False)
    payload: Mapped[dict[str,Any]]=mapped_column(JSONB,nullable=False)
    status: Mapped[str]=mapped_column(String(20),nullable=False,index=True)
    attempt: Mapped[int]=mapped_column(Integer,nullable=False,default=0)
    max_attempts: Mapped[int]=mapped_column(Integer,nullable=False)
    worker_id: Mapped[UUID|None]=mapped_column(PGUUID(as_uuid=True),ForeignKey("workers.id",ondelete="SET NULL"),nullable=True,index=True)
    lease_expires_at: Mapped[datetime|None]=mapped_column(DateTime(timezone=True),nullable=True,index=True)
    queued_at: Mapped[datetime]=mapped_column(DateTime(timezone=True),server_default=func.now(),nullable=False)
    started_at: Mapped[datetime|None]=mapped_column(DateTime(timezone=True),nullable=True)
    finished_at: Mapped[datetime|None]=mapped_column(DateTime(timezone=True),nullable=True)
class TaskResultRecord(Base):
    """Enforce one committed result per task independently of worker retries."""
    __tablename__="task_results"
    task_id: Mapped[UUID]=mapped_column(PGUUID(as_uuid=True),ForeignKey("tasks.id",ondelete="CASCADE"),primary_key=True)
    attempt: Mapped[int]=mapped_column(Integer,nullable=False)
    output: Mapped[dict[str,Any]]=mapped_column(JSONB,nullable=False)
    duration_ms: Mapped[float]=mapped_column(Float,nullable=False)
    committed_at: Mapped[datetime]=mapped_column(DateTime(timezone=True),server_default=func.now(),nullable=False)
class TaskEventRecord(Base):
    """Append-only task audit event used by dashboards and failure analysis."""
    __tablename__="task_events"
    id: Mapped[int]=mapped_column(BigInteger,primary_key=True,autoincrement=True)
    task_id: Mapped[UUID]=mapped_column(PGUUID(as_uuid=True),ForeignKey("tasks.id",ondelete="CASCADE"),nullable=False,index=True)
    event_type: Mapped[str]=mapped_column(String(40),nullable=False)
    worker_id: Mapped[UUID|None]=mapped_column(PGUUID(as_uuid=True),nullable=True)
    at: Mapped[datetime]=mapped_column(DateTime(timezone=True),server_default=func.now(),nullable=False,index=True)
    details: Mapped[dict[str,Any]]=mapped_column(JSONB,nullable=False,default=dict)
