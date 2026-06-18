from dataclasses import dataclass
from uuid import UUID

from src.domain.experiment.value_objects import EvidenceType, ExperimentStatus, OutcomeType
from src.domain.shared.events import DomainEvent


@dataclass(frozen=True, slots=True, kw_only=True)
class ExperimentDesigned(DomainEvent):
    experiment_id: UUID
    workspace_id: UUID
    created_by: UUID
    title: str


@dataclass(frozen=True, slots=True, kw_only=True)
class ExperimentLinkedToHypothesis(DomainEvent):
    experiment_id: UUID
    workspace_id: UUID
    hypothesis_id: UUID


@dataclass(frozen=True, slots=True, kw_only=True)
class ExperimentLinkedToGoal(DomainEvent):
    experiment_id: UUID
    workspace_id: UUID
    goal_id: UUID


@dataclass(frozen=True, slots=True, kw_only=True)
class ExperimentLinkedToMetric(DomainEvent):
    experiment_id: UUID
    workspace_id: UUID
    metric_id: UUID


@dataclass(frozen=True, slots=True, kw_only=True)
class ExperimentScheduled(DomainEvent):
    experiment_id: UUID
    workspace_id: UUID


@dataclass(frozen=True, slots=True, kw_only=True)
class ExperimentRescheduled(DomainEvent):
    experiment_id: UUID
    workspace_id: UUID


@dataclass(frozen=True, slots=True, kw_only=True)
class ExperimentLaunched(DomainEvent):
    experiment_id: UUID
    workspace_id: UUID
    owner_id: UUID


@dataclass(frozen=True, slots=True, kw_only=True)
class ExperimentStepAdded(DomainEvent):
    experiment_id: UUID
    workspace_id: UUID
    step_id: UUID
    title: str


@dataclass(frozen=True, slots=True, kw_only=True)
class ExperimentStepCompleted(DomainEvent):
    experiment_id: UUID
    workspace_id: UUID
    step_id: UUID


@dataclass(frozen=True, slots=True, kw_only=True)
class EvidenceRecorded(DomainEvent):
    experiment_id: UUID
    workspace_id: UUID
    evidence_id: UUID
    evidence_type: EvidenceType


@dataclass(frozen=True, slots=True, kw_only=True)
class ExperimentResultRecorded(DomainEvent):
    experiment_id: UUID
    workspace_id: UUID
    recorded_by: UUID


@dataclass(frozen=True, slots=True, kw_only=True)
class ExperimentOutcomeInterpreted(DomainEvent):
    experiment_id: UUID
    workspace_id: UUID
    outcome: OutcomeType
    interpreted_by: UUID


@dataclass(frozen=True, slots=True, kw_only=True)
class ExperimentCompleted(DomainEvent):
    experiment_id: UUID
    workspace_id: UUID


@dataclass(frozen=True, slots=True, kw_only=True)
class ExperimentCancelled(DomainEvent):
    experiment_id: UUID
    workspace_id: UUID
    cancelled_by: UUID
    reason: str


@dataclass(frozen=True, slots=True, kw_only=True)
class ExperimentAmended(DomainEvent):
    experiment_id: UUID
    workspace_id: UUID
    amendment_id: UUID
    amended_by: UUID


@dataclass(frozen=True, slots=True, kw_only=True)
class ExperimentStatusChanged(DomainEvent):
    experiment_id: UUID
    workspace_id: UUID
    status: ExperimentStatus
