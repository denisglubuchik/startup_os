from datetime import datetime
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.infrastructure.db.models.base import Base


class ExperimentModel(Base):
    __tablename__ = "experiments"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    workspace_id: Mapped[UUID] = mapped_column(index=True)
    title: Mapped[str] = mapped_column(String(300))
    method: Mapped[str] = mapped_column(String(300))
    audience: Mapped[str] = mapped_column(String(500))
    procedure: Mapped[str] = mapped_column(Text)
    success_criteria: Mapped[str] = mapped_column(Text)
    created_by: Mapped[UUID]
    owner_id: Mapped[UUID]
    status: Mapped[str] = mapped_column(String(50))
    planned_start_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    planned_end_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    result_summary: Mapped[str | None] = mapped_column(Text)
    result_recorded_by: Mapped[UUID | None]
    result_recorded_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    outcome: Mapped[str | None] = mapped_column(String(100))
    outcome_reasoning: Mapped[str | None] = mapped_column(Text)
    outcome_interpreted_by: Mapped[UUID | None]
    outcome_interpreted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    launched_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    cancelled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    hypothesis_refs: Mapped[list[ExperimentHypothesisReferenceModel]] = relationship(
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    goal_refs: Mapped[list[ExperimentGoalReferenceModel]] = relationship(
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    metric_refs: Mapped[list[ExperimentMetricReferenceModel]] = relationship(
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    steps: Mapped[list[ExperimentStepModel]] = relationship(
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    evidence_items: Mapped[list[EvidenceItemModel]] = relationship(
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    amendments: Mapped[list[ExperimentAmendmentModel]] = relationship(
        cascade="all, delete-orphan",
        lazy="selectin",
    )


class ExperimentHypothesisReferenceModel(Base):
    __tablename__ = "experiment_hypothesis_references"

    experiment_id: Mapped[UUID] = mapped_column(
        ForeignKey("experiments.id", ondelete="CASCADE"),
        primary_key=True,
    )
    hypothesis_id: Mapped[UUID] = mapped_column(primary_key=True)
    statement_snapshot: Mapped[str | None] = mapped_column(Text)


class ExperimentGoalReferenceModel(Base):
    __tablename__ = "experiment_goal_references"

    experiment_id: Mapped[UUID] = mapped_column(
        ForeignKey("experiments.id", ondelete="CASCADE"),
        primary_key=True,
    )
    goal_id: Mapped[UUID] = mapped_column(primary_key=True)
    title_snapshot: Mapped[str | None] = mapped_column(String(300))


class ExperimentMetricReferenceModel(Base):
    __tablename__ = "experiment_metric_references"

    experiment_id: Mapped[UUID] = mapped_column(
        ForeignKey("experiments.id", ondelete="CASCADE"),
        primary_key=True,
    )
    metric_id: Mapped[UUID] = mapped_column(primary_key=True)
    name_snapshot: Mapped[str | None] = mapped_column(String(300))
    unit_snapshot: Mapped[str | None] = mapped_column(String(100))


class ExperimentStepModel(Base):
    __tablename__ = "experiment_steps"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    experiment_id: Mapped[UUID] = mapped_column(ForeignKey("experiments.id", ondelete="CASCADE"))
    title: Mapped[str] = mapped_column(String(300))
    status: Mapped[str] = mapped_column(String(50))
    assignee_id: Mapped[UUID | None]
    due_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class EvidenceItemModel(Base):
    __tablename__ = "experiment_evidence_items"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    experiment_id: Mapped[UUID] = mapped_column(ForeignKey("experiments.id", ondelete="CASCADE"))
    evidence_type: Mapped[str] = mapped_column(String(100))
    source_description: Mapped[str] = mapped_column(String(500))
    source_external_url: Mapped[str | None] = mapped_column(Text)
    summary: Mapped[str] = mapped_column(Text)
    recorded_by: Mapped[UUID]
    recorded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    metric_observation_id: Mapped[UUID | None]


class ExperimentAmendmentModel(Base):
    __tablename__ = "experiment_amendments"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    experiment_id: Mapped[UUID] = mapped_column(ForeignKey("experiments.id", ondelete="CASCADE"))
    reason: Mapped[str] = mapped_column(Text)
    description: Mapped[str] = mapped_column(Text)
    amended_by: Mapped[UUID]
    amended_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
