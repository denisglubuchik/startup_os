from uuid import UUID

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.infrastructure.db.models.base import Base


class HypothesisModel(Base):
    __tablename__ = "hypotheses"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    workspace_id: Mapped[UUID] = mapped_column(index=True)
    statement: Mapped[str] = mapped_column(String(500))
    expected_outcome: Mapped[str | None] = mapped_column(String(1000))
    created_by: Mapped[UUID]
    status: Mapped[str] = mapped_column(String(50))
    confidence: Mapped[str] = mapped_column(String(50))
    priority: Mapped[str] = mapped_column(String(50))
    goal_id: Mapped[UUID | None]
    goal_title_snapshot: Mapped[str | None] = mapped_column(String(300))
    validation_experiment_id: Mapped[UUID | None]
    validation_outcome_summary: Mapped[str | None] = mapped_column(String(2000))

    metric_refs: Mapped[list[HypothesisMetricReferenceModel]] = relationship(
        cascade="all, delete-orphan",
        lazy="selectin",
    )


class HypothesisMetricReferenceModel(Base):
    __tablename__ = "hypothesis_metric_references"

    hypothesis_id: Mapped[UUID] = mapped_column(
        ForeignKey("hypotheses.id", ondelete="CASCADE"),
        primary_key=True,
    )
    metric_id: Mapped[UUID] = mapped_column(primary_key=True)
    name_snapshot: Mapped[str | None] = mapped_column(String(300))
    unit_snapshot: Mapped[str | None] = mapped_column(String(100))
