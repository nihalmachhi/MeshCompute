"""Replace globally claimed outbox rows with per-process LISTEN/NOTIFY cursors."""

from alembic import op

revision = "0007_outbox_listen_notify"
down_revision = "0006_job_idempotency"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("DROP INDEX IF EXISTS ix_outbox_events_pending;")
    op.execute("ALTER TABLE outbox_events DROP COLUMN IF EXISTS published_at;")
    op.execute("CREATE INDEX ix_outbox_events_cursor ON outbox_events (created_at, id);")


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS ix_outbox_events_cursor;")
    op.execute("ALTER TABLE outbox_events ADD COLUMN published_at TIMESTAMPTZ;")
    op.execute(
        "CREATE INDEX ix_outbox_events_pending ON outbox_events (created_at, id) "
        "WHERE published_at IS NULL;"
    )
