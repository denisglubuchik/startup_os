from dataclasses import dataclass
from enum import StrEnum
from uuid import UUID

from src.domain.shared.errors import DomainError
from src.domain.shared.value_object import ValueObject


class HypothesisStatus(StrEnum):
    DRAFT = "draft"
    READY_FOR_EXPERIMENT = "ready_for_experiment"
    TESTING = "testing"
    VALIDATED = "validated"
    INVALIDATED = "invalidated"
    INCONCLUSIVE = "inconclusive"
    ARCHIVED = "archived"


class ConfidenceLevel(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class HypothesisPriority(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass(frozen=True, slots=True)
class HypothesisStatement(ValueObject):
    value: str

    def __post_init__(self) -> None:
        normalized = self.value.strip()

        if not normalized:
            raise DomainError("Hypothesis statement cannot be empty.")

        if len(normalized) < 10:
            raise DomainError("Hypothesis statement is too short.")

        object.__setattr__(self, "value", normalized)


@dataclass(frozen=True, slots=True)
class ExpectedOutcome(ValueObject):
    description: str

    def __post_init__(self) -> None:
        normalized = self.description.strip()

        if not normalized:
            raise DomainError("Expected outcome cannot be empty.")

        object.__setattr__(self, "description", normalized)


@dataclass(frozen=True, slots=True)
class GoalReference(ValueObject):
    goal_id: UUID
    title_snapshot: str | None = None


@dataclass(frozen=True, slots=True)
class MetricReference(ValueObject):
    metric_id: UUID
    name_snapshot: str | None = None
    unit_snapshot: str | None = None


@dataclass(frozen=True, slots=True)
class ExperimentOutcomeReference(ValueObject):
    experiment_id: UUID
    outcome_summary: str
