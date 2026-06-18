from dataclasses import dataclass
from uuid import UUID

from src.domain.hypothesis.value_objects import HypothesisPriority, HypothesisStatus
from src.domain.shared.events import DomainEvent


@dataclass(frozen=True, slots=True)
class HypothesisFormulated(DomainEvent):
    hypothesis_id: UUID
    workspace_id: UUID
    created_by: UUID
    statement: str


@dataclass(frozen=True, slots=True)
class HypothesisRevised(DomainEvent):
    hypothesis_id: UUID
    workspace_id: UUID
    revised_by: UUID


@dataclass(frozen=True, slots=True)
class HypothesisLinkedToGoal(DomainEvent):
    hypothesis_id: UUID
    workspace_id: UUID
    goal_id: UUID


@dataclass(frozen=True, slots=True)
class HypothesisLinkedToMetric(DomainEvent):
    hypothesis_id: UUID
    workspace_id: UUID
    metric_id: UUID


@dataclass(frozen=True, slots=True)
class HypothesisPriorityChanged(DomainEvent):
    hypothesis_id: UUID
    workspace_id: UUID
    priority: HypothesisPriority


@dataclass(frozen=True, slots=True)
class HypothesisMarkedReadyForExperiment(DomainEvent):
    hypothesis_id: UUID
    workspace_id: UUID


@dataclass(frozen=True, slots=True)
class HypothesisTestingStarted(DomainEvent):
    hypothesis_id: UUID
    workspace_id: UUID
    experiment_id: UUID


@dataclass(frozen=True, slots=True)
class HypothesisValidationStatusChanged(DomainEvent):
    hypothesis_id: UUID
    workspace_id: UUID
    status: HypothesisStatus
    experiment_id: UUID
    outcome_summary: str


@dataclass(frozen=True, slots=True)
class HypothesisArchived(DomainEvent):
    hypothesis_id: UUID
    workspace_id: UUID
    archived_by: UUID
    reason: str
