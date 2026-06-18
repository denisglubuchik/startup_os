from dataclasses import dataclass
from datetime import datetime
from uuid import UUID, uuid4

from src.domain.experiment.value_objects import (
    AmendmentReason,
    EvidenceSource,
    EvidenceType,
    ExperimentStepStatus,
)
from src.domain.shared.entity import Entity
from src.domain.shared.errors import DomainError
from src.domain.shared.time import require_utc_datetime


@dataclass(eq=False, kw_only=True)
class ExperimentStep(Entity[UUID]):
    title: str
    status: ExperimentStepStatus = ExperimentStepStatus.TODO
    assignee_id: UUID | None = None
    due_at: datetime | None = None
    completed_at: datetime | None = None

    @classmethod
    def create(
        cls,
        *,
        title: str,
        assignee_id: UUID | None = None,
        due_at: datetime | None = None,
    ) -> ExperimentStep:
        normalized = title.strip()

        if not normalized:
            raise DomainError("Experiment step title cannot be empty.")

        normalized_due_at = require_utc_datetime(due_at, "due_at") if due_at is not None else None

        return cls(
            id=uuid4(),
            title=normalized,
            assignee_id=assignee_id,
            due_at=normalized_due_at,
        )

    def start(self) -> None:
        if self.status != ExperimentStepStatus.TODO:
            raise DomainError("Only TODO step can be started.")

        self.status = ExperimentStepStatus.IN_PROGRESS

    def complete(self, *, completed_at: datetime) -> None:
        completed_at = require_utc_datetime(completed_at, "completed_at")

        if self.status in {
            ExperimentStepStatus.DONE,
            ExperimentStepStatus.BLOCKED,
            ExperimentStepStatus.CANCELLED,
        }:
            raise DomainError("Step cannot be completed.")

        self.status = ExperimentStepStatus.DONE
        self.completed_at = completed_at

    def block(self) -> None:
        if self.status == ExperimentStepStatus.DONE:
            raise DomainError("Completed step cannot be blocked.")

        self.status = ExperimentStepStatus.BLOCKED

    def cancel(self) -> None:
        if self.status == ExperimentStepStatus.DONE:
            raise DomainError("Completed step cannot be cancelled.")

        self.status = ExperimentStepStatus.CANCELLED


@dataclass(eq=False, kw_only=True)
class EvidenceItem(Entity[UUID]):
    evidence_type: EvidenceType
    source: EvidenceSource
    summary: str
    recorded_by: UUID
    recorded_at: datetime
    metric_observation_id: UUID | None = None

    @classmethod
    def record(
        cls,
        *,
        evidence_type: EvidenceType,
        source: EvidenceSource,
        summary: str,
        recorded_by: UUID,
        recorded_at: datetime,
        metric_observation_id: UUID | None = None,
    ) -> EvidenceItem:
        normalized = summary.strip()

        if not normalized:
            raise DomainError("Evidence summary cannot be empty.")

        recorded_at = require_utc_datetime(recorded_at, "recorded_at")

        return cls(
            id=uuid4(),
            evidence_type=evidence_type,
            source=source,
            summary=normalized,
            recorded_by=recorded_by,
            recorded_at=recorded_at,
            metric_observation_id=metric_observation_id,
        )


@dataclass(eq=False, kw_only=True)
class ExperimentAmendment(Entity[UUID]):
    reason: AmendmentReason
    description: str
    amended_by: UUID
    amended_at: datetime

    @classmethod
    def create(
        cls,
        *,
        reason: AmendmentReason,
        description: str,
        amended_by: UUID,
        amended_at: datetime,
    ) -> ExperimentAmendment:
        normalized = description.strip()

        if not normalized:
            raise DomainError("Experiment amendment description cannot be empty.")

        amended_at = require_utc_datetime(amended_at, "amended_at")

        return cls(
            id=uuid4(),
            reason=reason,
            description=normalized,
            amended_by=amended_by,
            amended_at=amended_at,
        )
