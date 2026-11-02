"""Persist service events in the same transaction as their state changes."""

from alembic import op

revision = "0002_outbox"
down_revision = "0001_initial"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        CREATE TABLE outbox_events (
            id UUID PRIMARY KEY,
            payload JSONB NOT NULL,
            created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            published_at TIMESTAMPTZ
        );
        """
    )
    op.execute(
        "CREATE INDEX ix_outbox_events_pending ON outbox_events (created_at, id) "
        "WHERE published_at IS NULL;"
    )


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS outbox_events;")
