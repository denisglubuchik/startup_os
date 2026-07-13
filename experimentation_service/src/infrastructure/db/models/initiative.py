from uuid import UUID

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.infrastructure.db.models.base import Base


class InitiativeModel(Base):
    __tablename__ = "initiatives"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    workspace_id: Mapped[UUID] = mapped_column(index=True)
    title: Mapped[str] = mapped_column(String(300))
    created_by: Mapped[UUID]
    owner_id: Mapped[UUID]
    description: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(50))
    priority: Mapped[str] = mapped_column(String(50))

    goal_refs: Mapped[list[InitiativeGoalReferenceModel]] = relationship(
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    tasks: Mapped[list[InitiativeTaskModel]] = relationship(
        cascade="all, delete-orphan",
        lazy="selectin",
    )


class InitiativeGoalReferenceModel(Base):
    __tablename__ = "initiative_goal_references"

    initiative_id: Mapped[UUID] = mapped_column(
        ForeignKey("initiatives.id", ondelete="CASCADE"),
        primary_key=True,
    )
    goal_id: Mapped[UUID] = mapped_column(primary_key=True)
    title_snapshot: Mapped[str | None] = mapped_column(String(300))


class InitiativeTaskModel(Base):
    __tablename__ = "initiative_tasks"

    initiative_id: Mapped[UUID] = mapped_column(
        ForeignKey("initiatives.id", ondelete="CASCADE"),
        primary_key=True,
    )
    task_id: Mapped[UUID] = mapped_column(primary_key=True)
