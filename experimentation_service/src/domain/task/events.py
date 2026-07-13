from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from src.domain.shared.events import DomainEvent
from src.domain.task.value_objects import TaskPriority, TaskStatus


@dataclass(frozen=True, slots=True, kw_only=True)
class TaskCreated(DomainEvent):
    task_id: UUID
    workspace_id: UUID
    created_by: UUID
    title: str


@dataclass(frozen=True, slots=True, kw_only=True)
class TaskRevised(DomainEvent):
    task_id: UUID
    workspace_id: UUID
    revised_by: UUID


@dataclass(frozen=True, slots=True, kw_only=True)
class TaskAssigned(DomainEvent):
    task_id: UUID
    workspace_id: UUID
    assignee_id: UUID
    assigned_by: UUID


@dataclass(frozen=True, slots=True, kw_only=True)
class TaskUnassigned(DomainEvent):
    task_id: UUID
    workspace_id: UUID
    unassigned_by: UUID


@dataclass(frozen=True, slots=True, kw_only=True)
class TaskRescheduled(DomainEvent):
    task_id: UUID
    workspace_id: UUID
    due_at: datetime | None


@dataclass(frozen=True, slots=True, kw_only=True)
class TaskPriorityChanged(DomainEvent):
    task_id: UUID
    workspace_id: UUID
    priority: TaskPriority


@dataclass(frozen=True, slots=True, kw_only=True)
class TaskStatusChanged(DomainEvent):
    task_id: UUID
    workspace_id: UUID
    status: TaskStatus


@dataclass(frozen=True, slots=True, kw_only=True)
class TaskBlocked(DomainEvent):
    task_id: UUID
    workspace_id: UUID
    blocked_by: UUID
    reason: str


@dataclass(frozen=True, slots=True, kw_only=True)
class TaskUnblocked(DomainEvent):
    task_id: UUID
    workspace_id: UUID
    unblocked_by: UUID


@dataclass(frozen=True, slots=True, kw_only=True)
class TaskCompleted(DomainEvent):
    task_id: UUID
    workspace_id: UUID
    completed_by: UUID


@dataclass(frozen=True, slots=True, kw_only=True)
class TaskCancelled(DomainEvent):
    task_id: UUID
    workspace_id: UUID
    cancelled_by: UUID
    reason: str
