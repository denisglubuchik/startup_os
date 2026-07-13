from dataclasses import dataclass
from uuid import UUID

from src.domain.initiative.value_objects import InitiativePriority, InitiativeStatus
from src.domain.shared.events import DomainEvent


@dataclass(frozen=True, slots=True, kw_only=True)
class InitiativeCreated(DomainEvent):
    initiative_id: UUID
    workspace_id: UUID
    created_by: UUID
    title: str


@dataclass(frozen=True, slots=True, kw_only=True)
class InitiativeRevised(DomainEvent):
    initiative_id: UUID
    workspace_id: UUID
    revised_by: UUID


@dataclass(frozen=True, slots=True, kw_only=True)
class InitiativeLinkedToGoal(DomainEvent):
    initiative_id: UUID
    workspace_id: UUID
    goal_id: UUID


@dataclass(frozen=True, slots=True, kw_only=True)
class InitiativeTaskAdded(DomainEvent):
    initiative_id: UUID
    workspace_id: UUID
    task_id: UUID


@dataclass(frozen=True, slots=True, kw_only=True)
class InitiativeTaskRemoved(DomainEvent):
    initiative_id: UUID
    workspace_id: UUID
    task_id: UUID


@dataclass(frozen=True, slots=True, kw_only=True)
class InitiativePriorityChanged(DomainEvent):
    initiative_id: UUID
    workspace_id: UUID
    priority: InitiativePriority


@dataclass(frozen=True, slots=True, kw_only=True)
class InitiativeStatusChanged(DomainEvent):
    initiative_id: UUID
    workspace_id: UUID
    status: InitiativeStatus


@dataclass(frozen=True, slots=True, kw_only=True)
class InitiativeCompleted(DomainEvent):
    initiative_id: UUID
    workspace_id: UUID
    completed_by: UUID


@dataclass(frozen=True, slots=True, kw_only=True)
class InitiativeCancelled(DomainEvent):
    initiative_id: UUID
    workspace_id: UUID
    cancelled_by: UUID
    reason: str


@dataclass(frozen=True, slots=True, kw_only=True)
class InitiativeArchived(DomainEvent):
    initiative_id: UUID
    workspace_id: UUID
    archived_by: UUID
    reason: str
