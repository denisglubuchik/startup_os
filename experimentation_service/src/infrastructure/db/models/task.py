from datetime import datetime
from uuid import UUID

from sqlalchemy import DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from src.infrastructure.db.models.base import Base


class TaskModel(Base):
    __tablename__ = "tasks"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    workspace_id: Mapped[UUID] = mapped_column(index=True)
    title: Mapped[str] = mapped_column(String(300))
    created_by: Mapped[UUID]
    description: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(50))
    priority: Mapped[str] = mapped_column(String(50))
    assignee_id: Mapped[UUID | None]
    due_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    initiative_id: Mapped[UUID | None]
    initiative_title_snapshot: Mapped[str | None] = mapped_column(String(300))
    experiment_id: Mapped[UUID | None]
    experiment_title_snapshot: Mapped[str | None] = mapped_column(String(300))
