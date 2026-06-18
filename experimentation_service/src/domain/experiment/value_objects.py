from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from urllib.parse import quote, urlsplit, urlunsplit
from uuid import UUID

from src.domain.shared.errors import DomainError
from src.domain.shared.time import require_utc_datetime
from src.domain.shared.value_object import ValueObject


class ExperimentStatus(StrEnum):
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    RUNNING = "running"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class ExperimentStepStatus(StrEnum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"
    BLOCKED = "blocked"
    CANCELLED = "cancelled"


class EvidenceType(StrEnum):
    METRIC_OBSERVATION = "metric_observation"
    INTERVIEW_NOTE = "interview_note"
    SURVEY_RESULT = "survey_result"
    ANALYTICS_SCREENSHOT = "analytics_screenshot"
    DOCUMENT_LINK = "document_link"
    MANUAL_OBSERVATION = "manual_observation"


class OutcomeType(StrEnum):
    SUPPORTS_HYPOTHESIS = "supports_hypothesis"
    CONTRADICTS_HYPOTHESIS = "contradicts_hypothesis"
    PARTIALLY_SUPPORTS_HYPOTHESIS = "partially_supports_hypothesis"
    INCONCLUSIVE = "inconclusive"


@dataclass(frozen=True, slots=True)
class ExperimentTitle(ValueObject):
    value: str

    def __post_init__(self) -> None:
        normalized = self.value.strip()

        if not normalized:
            raise DomainError("Experiment title cannot be empty.")

        if len(normalized) < 5:
            raise DomainError("Experiment title is too short.")

        object.__setattr__(self, "value", normalized)


@dataclass(frozen=True, slots=True)
class ExperimentDesign(ValueObject):
    """
    Describes how the experiment will be conducted.

    Example:
    - landing page test
    - 20 customer interviews
    - pricing smoke test
    - onboarding A/B test
    """

    method: str
    audience: str
    procedure: str

    def __post_init__(self) -> None:
        method = self.method.strip()
        audience = self.audience.strip()
        procedure = self.procedure.strip()

        if not method:
            raise DomainError("Experiment method cannot be empty.")

        if not audience:
            raise DomainError("Experiment audience cannot be empty.")

        if not procedure:
            raise DomainError("Experiment procedure cannot be empty.")

        object.__setattr__(self, "method", method)
        object.__setattr__(self, "audience", audience)
        object.__setattr__(self, "procedure", procedure)


@dataclass(frozen=True, slots=True)
class SuccessCriteria(ValueObject):
    """
    Describes how the team will decide whether the experiment succeeded.
    """

    description: str

    def __post_init__(self) -> None:
        normalized = self.description.strip()

        if not normalized:
            raise DomainError("Success criteria cannot be empty.")

        object.__setattr__(self, "description", normalized)


@dataclass(frozen=True, slots=True)
class ExperimentSchedule(ValueObject):
    planned_start_at: datetime
    planned_end_at: datetime

    def __post_init__(self) -> None:
        planned_start_at = require_utc_datetime(self.planned_start_at, "planned_start_at")
        planned_end_at = require_utc_datetime(self.planned_end_at, "planned_end_at")

        if planned_end_at <= planned_start_at:
            raise DomainError("Experiment planned end date must be after planned start date.")

        object.__setattr__(self, "planned_start_at", planned_start_at)
        object.__setattr__(self, "planned_end_at", planned_end_at)


@dataclass(frozen=True, slots=True)
class ExperimentResult(ValueObject):
    """
    Result answers: what happened?

    It is not a decision and not a final learning.
    """

    summary: str
    recorded_by: UUID
    recorded_at: datetime

    def __post_init__(self) -> None:
        normalized = self.summary.strip()
        recorded_at = require_utc_datetime(self.recorded_at, "recorded_at")

        if not normalized:
            raise DomainError("Experiment result summary cannot be empty.")

        object.__setattr__(self, "summary", normalized)
        object.__setattr__(self, "recorded_at", recorded_at)


@dataclass(frozen=True, slots=True)
class OutcomeInterpretation(ValueObject):
    """
    Interpretation answers: what does the result mean for the hypothesis?

    Final decisions and insights still belong to knowledge_service.
    """

    outcome: OutcomeType
    reasoning: str
    interpreted_by: UUID
    interpreted_at: datetime

    def __post_init__(self) -> None:
        normalized = self.reasoning.strip()
        interpreted_at = require_utc_datetime(self.interpreted_at, "interpreted_at")

        if not normalized:
            raise DomainError("Outcome interpretation reasoning cannot be empty.")

        object.__setattr__(self, "reasoning", normalized)
        object.__setattr__(self, "interpreted_at", interpreted_at)


@dataclass(frozen=True, slots=True)
class CancellationReason(ValueObject):
    value: str

    def __post_init__(self) -> None:
        normalized = self.value.strip()

        if not normalized:
            raise DomainError("Cancellation reason cannot be empty.")

        object.__setattr__(self, "value", normalized)


@dataclass(frozen=True, slots=True)
class AmendmentReason(ValueObject):
    value: str

    def __post_init__(self) -> None:
        normalized = self.value.strip()

        if not normalized:
            raise DomainError("Amendment reason cannot be empty.")

        object.__setattr__(self, "value", normalized)


@dataclass(frozen=True, slots=True)
class HypothesisReference(ValueObject):
    hypothesis_id: UUID
    statement_snapshot: str | None = None


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
class EvidenceSource(ValueObject):
    description: str
    external_url: str | None = None

    def __post_init__(self) -> None:
        normalized = self.description.strip()
        external_url = normalize_external_url(self.external_url)

        if not normalized:
            raise DomainError("Evidence source description cannot be empty.")

        object.__setattr__(self, "description", normalized)
        object.__setattr__(self, "external_url", external_url)


def normalize_external_url(value: str | None) -> str | None:
    if value is None:
        return None

    normalized = value.strip()
    if not normalized:
        return None

    parsed = urlsplit(normalized)
    if not parsed.scheme or not parsed.netloc:
        raise DomainError("Evidence source external URL must include scheme and host.")

    path = quote(parsed.path, safe="/%")
    query = quote(parsed.query, safe="=&;%")
    fragment = quote(parsed.fragment, safe="")

    return urlunsplit(
        (
            parsed.scheme.lower(),
            parsed.netloc.lower(),
            path,
            query,
            fragment,
        )
    )
