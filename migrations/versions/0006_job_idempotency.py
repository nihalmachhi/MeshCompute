"""Persist idempotency keys for safe job-submission retries."""

from alembic import op

revision = "0006_job_idempotency"
down_revision = "0005_retry_dead_letters"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        CREATE TABLE job_idempotency_keys (
            key_hash VARCHAR(64) PRIMARY KEY,
            request_hash VARCHAR(64) NOT NULL,
            job_id UUID NOT NULL REFERENCES jobs(id) ON DELETE CASCADE,
            created_at TIMESTAMPTZ NOT NULL DEFAULT now()
        );
        """
    )
    op.execute("CREATE INDEX ix_job_idempotency_keys_job_id ON job_idempotency_keys (job_id);")


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS job_idempotency_keys;")
