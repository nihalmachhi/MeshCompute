"""Initial durable coordinator schema (frozen DDL)."""

from alembic import op

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
    CREATE TABLE jobs (
        id UUID PRIMARY KEY,
        job_type VARCHAR(80) NOT NULL,
        input_ref TEXT NOT NULL,
        chunk_count INTEGER NOT NULL,
        status VARCHAR(20) NOT NULL,
        result JSONB,
        created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
        finished_at TIMESTAMPTZ,
        expires_at TIMESTAMPTZ
    );
    """)
    op.execute("CREATE INDEX ix_jobs_job_type ON jobs (job_type);")
    op.execute("CREATE INDEX ix_jobs_status ON jobs (status);")
    op.execute("""
    CREATE TABLE workers (
        id UUID PRIMARY KEY,
        name VARCHAR(120) NOT NULL,
        status VARCHAR(20) NOT NULL,
        registered_at TIMESTAMPTZ NOT NULL DEFAULT now(),
        last_heartbeat_at TIMESTAMPTZ NOT NULL DEFAULT now(),
        current_task_id UUID,
        token_hash VARCHAR(128)
    );
    """)
    op.execute("CREATE INDEX ix_workers_status ON workers (status);")
    op.execute("CREATE INDEX ix_workers_last_heartbeat_at ON workers (last_heartbeat_at);")
    op.execute("""
    CREATE TABLE tasks (
        id UUID PRIMARY KEY,
        job_id UUID NOT NULL REFERENCES jobs(id) ON DELETE CASCADE,
        task_index INTEGER NOT NULL,
        payload JSONB NOT NULL,
        status VARCHAR(20) NOT NULL,
        attempt INTEGER NOT NULL DEFAULT 0,
        max_attempts INTEGER NOT NULL,
        worker_id UUID REFERENCES workers(id) ON DELETE SET NULL,
        lease_expires_at TIMESTAMPTZ,
        queued_at TIMESTAMPTZ NOT NULL DEFAULT now(),
        started_at TIMESTAMPTZ,
        finished_at TIMESTAMPTZ,
        CONSTRAINT uq_task_job_index UNIQUE (job_id, task_index)
    );
    """)
    op.execute("CREATE INDEX ix_tasks_job_id ON tasks (job_id);")
    op.execute("CREATE INDEX ix_tasks_status ON tasks (status);")
    op.execute("CREATE INDEX ix_tasks_worker_id ON tasks (worker_id);")
    op.execute("CREATE INDEX ix_tasks_lease_expiry ON tasks (status, lease_expires_at);")
    op.execute("CREATE INDEX ix_tasks_lease_expires_at ON tasks (lease_expires_at);")
    op.execute("CREATE INDEX ix_tasks_pending_queue ON tasks (status, queued_at, task_index);")
    op.execute("""
    CREATE TABLE task_results (
        task_id UUID PRIMARY KEY REFERENCES tasks(id) ON DELETE CASCADE,
        attempt INTEGER NOT NULL,
        output JSONB NOT NULL,
        duration_ms DOUBLE PRECISION NOT NULL,
        committed_at TIMESTAMPTZ NOT NULL DEFAULT now()
    );
    """)
    op.execute("""
    CREATE TABLE task_events (
        id BIGSERIAL PRIMARY KEY,
        task_id UUID NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
        event_type VARCHAR(40) NOT NULL,
        worker_id UUID,
        at TIMESTAMPTZ NOT NULL DEFAULT now(),
        details JSONB NOT NULL DEFAULT '{}'
    );
    """)
    op.execute("CREATE INDEX ix_task_events_task_id ON task_events (task_id);")
    op.execute("CREATE INDEX ix_task_events_at ON task_events (at);")


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS task_events;")
    op.execute("DROP TABLE IF EXISTS task_results;")
    op.execute("DROP TABLE IF EXISTS tasks;")
    op.execute("DROP TABLE IF EXISTS workers;")
    op.execute("DROP TABLE IF EXISTS jobs;")
