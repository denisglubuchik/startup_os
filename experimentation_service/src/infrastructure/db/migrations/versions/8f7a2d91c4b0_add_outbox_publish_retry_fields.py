"""add outbox publish retry fields

Revision ID: 8f7a2d91c4b0
Revises: 6f339686319a
Create Date: 2026-06-18 23:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "8f7a2d91c4b0"
down_revision: str | Sequence[str] | None = "6f339686319a"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("outbox_messages", sa.Column("locked_at", sa.DateTime(timezone=True)))
    op.add_column(
        "outbox_messages",
        sa.Column("attempt_count", sa.Integer(), server_default="0", nullable=False),
    )
    op.add_column("outbox_messages", sa.Column("next_attempt_at", sa.DateTime(timezone=True)))
    op.create_index("ix_outbox_messages_locked_at", "outbox_messages", ["locked_at"])
    op.create_index("ix_outbox_messages_next_attempt_at", "outbox_messages", ["next_attempt_at"])


def downgrade() -> None:
    op.drop_index("ix_outbox_messages_next_attempt_at", table_name="outbox_messages")
    op.drop_index("ix_outbox_messages_locked_at", table_name="outbox_messages")
    op.drop_column("outbox_messages", "next_attempt_at")
    op.drop_column("outbox_messages", "attempt_count")
    op.drop_column("outbox_messages", "locked_at")
