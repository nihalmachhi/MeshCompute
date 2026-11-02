"""Add delayed retries and a durable dead-letter queue."""

from alembic import op

revision = "0005_retry_dead_letters"
down_revision = "0004_priority_capabilities"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("ALTER TABLE tasks ADD COLUMN available_at TIMESTAMPTZ NOT NULL DEFAULT now();")
    op.execute("CREATE INDEX ix_tasks_available_at ON tasks (available_at);")
    op.execute(
        """
        CREATE TABLE dead_letters (
            task_id UUID PRIMARY KEY REFERENCES tasks(id) ON DELETE CASCADE,
            job_id UUID NOT NULL REFERENCES jobs(id) ON DELETE CASCADE,
            payload JSONB NOT NULL,
            attempts INTEGER NOT NULL,
            reason TEXT NOT NULL,
            created_at TIMESTAMPTZ NOT NULL DEFAULT now()
        );
        """
    )
    op.execute("CREATE INDEX ix_dead_letters_job_id ON dead_letters (job_id);")


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS dead_letters;")
    op.execute("DROP INDEX IF EXISTS ix_tasks_available_at;")
    op.execute("ALTER TABLE tasks DROP COLUMN IF EXISTS available_at;")
