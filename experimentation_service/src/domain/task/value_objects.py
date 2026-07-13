from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from uuid import UUID

from src.domain.shared.errors import DomainError
from src.domain.shared.time import require_utc_datetime
from src.domain.shared.value_object import ValueObject


class TaskStatus(StrEnum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    BLOCKED = "blocked"
    DONE = "done"
    CANCELLED = "cancelled"


class TaskPriority(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass(frozen=True, slots=True)
class TaskTitle(ValueObject):
    value: str

    def __post_init__(self) -> None:
        normalized = self.value.strip()

        if not normalized:
            raise DomainError("Task title cannot be empty.")

        if len(normalized) < 3:
            raise DomainError("Task title is too short.")

        object.__setattr__(self, "value", normalized)


@dataclass(frozen=True, slots=True)
class TaskDescription(ValueObject):
    value: str

    def __post_init__(self) -> None:
        normalized = self.value.strip()

        if not normalized:
            raise DomainError("Task description cannot be empty.")

        object.__setattr__(self, "value", normalized)


@dataclass(frozen=True, slots=True)
class BlockReason(ValueObject):
    value: str

    def __post_init__(self) -> None:
        normalized = self.value.strip()

        if not normalized:
            raise DomainError("Block reason cannot be empty.")

        object.__setattr__(self, "value", normalized)


@dataclass(frozen=True, slots=True)
class CancellationReason(ValueObject):
    value: str

    def __post_init__(self) -> None:
        normalized = self.value.strip()

        if not normalized:
            raise DomainError("Cancellation reason cannot be empty.")

        object.__setattr__(self, "value", normalized)


@dataclass(frozen=True, slots=True)
class DueDate(ValueObject):
    value: datetime

    def __post_init__(self) -> None:
        object.__setattr__(self, "value", require_utc_datetime(self.value, "due_at"))


@dataclass(frozen=True, slots=True)
class InitiativeReference(ValueObject):
    initiative_id: UUID
    title_snapshot: str | None = None


@dataclass(frozen=True, slots=True)
class ExperimentReference(ValueObject):
    experiment_id: UUID
    title_snapshot: str | None = None
