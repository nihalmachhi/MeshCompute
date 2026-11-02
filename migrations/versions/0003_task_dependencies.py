"""Persist dependency edges for topologically released tasks."""

from alembic import op

revision = "0003_task_dependencies"
down_revision = "0002_outbox"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        CREATE TABLE task_dependencies (
            task_id UUID NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
            depends_on_task_id UUID NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
            PRIMARY KEY (task_id, depends_on_task_id),
            CONSTRAINT ck_task_dependencies_no_self CHECK (task_id <> depends_on_task_id)
        );
        """
    )
    op.execute(
        "CREATE INDEX ix_task_dependencies_prerequisite ON task_dependencies (depends_on_task_id);"
    )


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS task_dependencies;")
