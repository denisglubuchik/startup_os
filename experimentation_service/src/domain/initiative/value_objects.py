from dataclasses import dataclass
from enum import StrEnum
from uuid import UUID

from src.domain.shared.errors import DomainError
from src.domain.shared.value_object import ValueObject


class InitiativeStatus(StrEnum):
    PLANNED = "planned"
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    ARCHIVED = "archived"


class InitiativePriority(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass(frozen=True, slots=True)
class InitiativeTitle(ValueObject):
    value: str

    def __post_init__(self) -> None:
        normalized = self.value.strip()

        if not normalized:
            raise DomainError("Initiative title cannot be empty.")

        if len(normalized) < 5:
            raise DomainError("Initiative title is too short.")

        object.__setattr__(self, "value", normalized)


@dataclass(frozen=True, slots=True)
class InitiativeDescription(ValueObject):
    value: str

    def __post_init__(self) -> None:
        normalized = self.value.strip()

        if not normalized:
            raise DomainError("Initiative description cannot be empty.")

        object.__setattr__(self, "value", normalized)


@dataclass(frozen=True, slots=True)
class GoalReference(ValueObject):
    goal_id: UUID
    title_snapshot: str | None = None

    def __post_init__(self) -> None:
        if self.title_snapshot is None:
            return

        normalized = self.title_snapshot.strip()
        object.__setattr__(self, "title_snapshot", normalized or None)


@dataclass(frozen=True, slots=True)
class CancellationReason(ValueObject):
    value: str

    def __post_init__(self) -> None:
        normalized = self.value.strip()

        if not normalized:
            raise DomainError("Cancellation reason cannot be empty.")

        object.__setattr__(self, "value", normalized)


@dataclass(frozen=True, slots=True)
class ArchiveReason(ValueObject):
    value: str

    def __post_init__(self) -> None:
        normalized = self.value.strip()

        if not normalized:
            raise DomainError("Archive reason cannot be empty.")

        object.__setattr__(self, "value", normalized)
