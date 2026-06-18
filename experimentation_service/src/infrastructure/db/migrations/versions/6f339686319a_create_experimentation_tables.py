"""create experimentation tables

Revision ID: 6f339686319a
Revises:
Create Date: 2026-06-18 15:19:25.892002

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "6f339686319a"
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    create_hypothesis_tables()
    create_experiment_tables()
    create_task_table()
    create_initiative_tables()
    create_outbox_table()


def downgrade() -> None:
    op.drop_table("outbox_messages")
    op.drop_table("initiative_tasks")
    op.drop_table("initiative_goal_references")
    op.drop_table("initiatives")
    op.drop_table("tasks")
    op.drop_table("experiment_amendments")
    op.drop_table("experiment_evidence_items")
    op.drop_table("experiment_steps")
    op.drop_table("experiment_metric_references")
    op.drop_table("experiment_goal_references")
    op.drop_table("experiment_hypothesis_references")
    op.drop_table("experiments")
    op.drop_table("hypothesis_metric_references")
    op.drop_table("hypotheses")


def uuid_column(name: str, *, primary_key: bool = False, nullable: bool = False):
    return sa.Column(name, postgresql.UUID(as_uuid=True), primary_key=primary_key, nullable=nullable)


def create_hypothesis_tables() -> None:
    op.create_table(
        "hypotheses",
        uuid_column("id", primary_key=True),
        uuid_column("workspace_id"),
        sa.Column("statement", sa.String(length=500), nullable=False),
        sa.Column("expected_outcome", sa.String(length=1000), nullable=True),
        uuid_column("created_by"),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("confidence", sa.String(length=50), nullable=False),
        sa.Column("priority", sa.String(length=50), nullable=False),
        uuid_column("goal_id", nullable=True),
        sa.Column("goal_title_snapshot", sa.String(length=300), nullable=True),
        uuid_column("validation_experiment_id", nullable=True),
        sa.Column("validation_outcome_summary", sa.String(length=2000), nullable=True),
    )
    op.create_index("ix_hypotheses_workspace_id", "hypotheses", ["workspace_id"])
    op.create_table(
        "hypothesis_metric_references",
        uuid_column("hypothesis_id", primary_key=True),
        uuid_column("metric_id", primary_key=True),
        sa.Column("name_snapshot", sa.String(length=300), nullable=True),
        sa.Column("unit_snapshot", sa.String(length=100), nullable=True),
        sa.ForeignKeyConstraint(["hypothesis_id"], ["hypotheses.id"], ondelete="CASCADE"),
    )


def create_experiment_tables() -> None:
    op.create_table(
        "experiments",
        uuid_column("id", primary_key=True),
        uuid_column("workspace_id"),
        sa.Column("title", sa.String(length=300), nullable=False),
        sa.Column("method", sa.String(length=300), nullable=False),
        sa.Column("audience", sa.String(length=500), nullable=False),
        sa.Column("procedure", sa.Text(), nullable=False),
        sa.Column("success_criteria", sa.Text(), nullable=False),
        uuid_column("created_by"),
        uuid_column("owner_id"),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("planned_start_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("planned_end_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("result_summary", sa.Text(), nullable=True),
        uuid_column("result_recorded_by", nullable=True),
        sa.Column("result_recorded_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("outcome", sa.String(length=100), nullable=True),
        sa.Column("outcome_reasoning", sa.Text(), nullable=True),
        uuid_column("outcome_interpreted_by", nullable=True),
        sa.Column("outcome_interpreted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("launched_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("cancelled_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_experiments_workspace_id", "experiments", ["workspace_id"])
    create_experiment_reference_table("experiment_hypothesis_references", "hypothesis_id", sa.Text())
    create_experiment_reference_table("experiment_goal_references", "goal_id", sa.String(300))
    create_experiment_metric_references()
    create_experiment_steps()
    create_experiment_evidence_items()
    create_experiment_amendments()


def create_experiment_reference_table(
    table_name: str,
    referenced_id_column: str,
    snapshot_type,
) -> None:
    snapshot_column = (
        "statement_snapshot" if referenced_id_column == "hypothesis_id" else "title_snapshot"
    )
    op.create_table(
        table_name,
        uuid_column("experiment_id", primary_key=True),
        uuid_column(referenced_id_column, primary_key=True),
        sa.Column(snapshot_column, snapshot_type, nullable=True),
        sa.ForeignKeyConstraint(["experiment_id"], ["experiments.id"], ondelete="CASCADE"),
    )


def create_experiment_metric_references() -> None:
    op.create_table(
        "experiment_metric_references",
        uuid_column("experiment_id", primary_key=True),
        uuid_column("metric_id", primary_key=True),
        sa.Column("name_snapshot", sa.String(length=300), nullable=True),
        sa.Column("unit_snapshot", sa.String(length=100), nullable=True),
        sa.ForeignKeyConstraint(["experiment_id"], ["experiments.id"], ondelete="CASCADE"),
    )


def create_experiment_steps() -> None:
    op.create_table(
        "experiment_steps",
        uuid_column("id", primary_key=True),
        uuid_column("experiment_id"),
        sa.Column("title", sa.String(length=300), nullable=False),
        sa.Column("status", sa.String(length=50), nullable=False),
        uuid_column("assignee_id", nullable=True),
        sa.Column("due_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["experiment_id"], ["experiments.id"], ondelete="CASCADE"),
    )


def create_experiment_evidence_items() -> None:
    op.create_table(
        "experiment_evidence_items",
        uuid_column("id", primary_key=True),
        uuid_column("experiment_id"),
        sa.Column("evidence_type", sa.String(length=100), nullable=False),
        sa.Column("source_description", sa.String(length=500), nullable=False),
        sa.Column("source_external_url", sa.Text(), nullable=True),
        sa.Column("summary", sa.Text(), nullable=False),
        uuid_column("recorded_by"),
        sa.Column("recorded_at", sa.DateTime(timezone=True), nullable=False),
        uuid_column("metric_observation_id", nullable=True),
        sa.ForeignKeyConstraint(["experiment_id"], ["experiments.id"], ondelete="CASCADE"),
    )


def create_experiment_amendments() -> None:
    op.create_table(
        "experiment_amendments",
        uuid_column("id", primary_key=True),
        uuid_column("experiment_id"),
        sa.Column("reason", sa.Text(), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        uuid_column("amended_by"),
        sa.Column("amended_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["experiment_id"], ["experiments.id"], ondelete="CASCADE"),
    )


def create_task_table() -> None:
    op.create_table(
        "tasks",
        uuid_column("id", primary_key=True),
        uuid_column("workspace_id"),
        sa.Column("title", sa.String(length=300), nullable=False),
        uuid_column("created_by"),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("priority", sa.String(length=50), nullable=False),
        uuid_column("assignee_id", nullable=True),
        sa.Column("due_at", sa.DateTime(timezone=True), nullable=True),
        uuid_column("initiative_id", nullable=True),
        sa.Column("initiative_title_snapshot", sa.String(length=300), nullable=True),
        uuid_column("experiment_id", nullable=True),
        sa.Column("experiment_title_snapshot", sa.String(length=300), nullable=True),
    )
    op.create_index("ix_tasks_workspace_id", "tasks", ["workspace_id"])


def create_initiative_tables() -> None:
    op.create_table(
        "initiatives",
        uuid_column("id", primary_key=True),
        uuid_column("workspace_id"),
        sa.Column("title", sa.String(length=300), nullable=False),
        uuid_column("created_by"),
        uuid_column("owner_id"),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("priority", sa.String(length=50), nullable=False),
    )
    op.create_index("ix_initiatives_workspace_id", "initiatives", ["workspace_id"])
    op.create_table(
        "initiative_goal_references",
        uuid_column("initiative_id", primary_key=True),
        uuid_column("goal_id", primary_key=True),
        sa.Column("title_snapshot", sa.String(length=300), nullable=True),
        sa.ForeignKeyConstraint(["initiative_id"], ["initiatives.id"], ondelete="CASCADE"),
    )
    op.create_table(
        "initiative_tasks",
        uuid_column("initiative_id", primary_key=True),
        uuid_column("task_id", primary_key=True),
        sa.ForeignKeyConstraint(["initiative_id"], ["initiatives.id"], ondelete="CASCADE"),
    )


def create_outbox_table() -> None:
    op.create_table(
        "outbox_messages",
        uuid_column("id", primary_key=True),
        uuid_column("aggregate_id"),
        uuid_column("workspace_id", nullable=True),
        sa.Column("event_type", sa.String(length=200), nullable=False),
        sa.Column("payload", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("occurred_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("publish_error", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_outbox_messages_aggregate_id", "outbox_messages", ["aggregate_id"])
    op.create_index("ix_outbox_messages_workspace_id", "outbox_messages", ["workspace_id"])
    op.create_index("ix_outbox_messages_event_type", "outbox_messages", ["event_type"])
