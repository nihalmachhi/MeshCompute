"""Add aged job priority and worker/task capability declarations."""

from alembic import op

revision = "0004_priority_capabilities"
down_revision = "0003_task_dependencies"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("ALTER TABLE jobs ADD COLUMN priority INTEGER NOT NULL DEFAULT 0;")
    op.execute("ALTER TABLE workers ADD COLUMN capabilities JSONB NOT NULL DEFAULT '[]'::jsonb;")
    op.execute(
        "ALTER TABLE tasks ADD COLUMN required_capabilities JSONB NOT NULL DEFAULT '[]'::jsonb;"
    )


def downgrade() -> None:
    op.execute("ALTER TABLE tasks DROP COLUMN IF EXISTS required_capabilities;")
    op.execute("ALTER TABLE workers DROP COLUMN IF EXISTS capabilities;")
    op.execute("ALTER TABLE jobs DROP COLUMN IF EXISTS priority;")
