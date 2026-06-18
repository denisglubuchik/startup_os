from dataclasses import dataclass, field
from uuid import UUID, uuid4

from src.domain.hypothesis.events import (
    HypothesisArchived,
    HypothesisFormulated,
    HypothesisLinkedToGoal,
    HypothesisLinkedToMetric,
    HypothesisMarkedReadyForExperiment,
    HypothesisPriorityChanged,
    HypothesisRevised,
    HypothesisTestingStarted,
    HypothesisValidationStatusChanged,
)
from src.domain.hypothesis.value_objects import (
    ConfidenceLevel,
    ExpectedOutcome,
    ExperimentOutcomeReference,
    GoalReference,
    HypothesisPriority,
    HypothesisStatement,
    HypothesisStatus,
    MetricReference,
)
from src.domain.shared.aggregate import AggregateRoot
from src.domain.shared.errors import DomainError


@dataclass(eq=False, kw_only=True)
class Hypothesis(AggregateRoot[UUID]):
    workspace_id: UUID
    statement: HypothesisStatement
    expected_outcome: ExpectedOutcome | None
    created_by: UUID

    status: HypothesisStatus = HypothesisStatus.DRAFT
    confidence: ConfidenceLevel = ConfidenceLevel.LOW
    priority: HypothesisPriority = HypothesisPriority.MEDIUM

    goal_ref: GoalReference | None = None
    metric_refs: list[MetricReference] = field(default_factory=list)
    validation_outcome_ref: ExperimentOutcomeReference | None = None

    @classmethod
    def formulate(
        cls,
        *,
        workspace_id: UUID,
        statement: HypothesisStatement,
        expected_outcome: ExpectedOutcome | None,
        created_by: UUID,
        confidence: ConfidenceLevel = ConfidenceLevel.LOW,
        priority: HypothesisPriority = HypothesisPriority.MEDIUM,
    ) -> Hypothesis:
        hypothesis = cls(
            id=uuid4(),
            workspace_id=workspace_id,
            statement=statement,
            expected_outcome=expected_outcome,
            created_by=created_by,
            confidence=confidence,
            priority=priority,
        )

        hypothesis.record_event(
            HypothesisFormulated(
                hypothesis_id=hypothesis.id,
                workspace_id=workspace_id,
                created_by=created_by,
                statement=statement.value,
            )
        )

        return hypothesis

    def revise(
        self,
        *,
        statement: HypothesisStatement,
        expected_outcome: ExpectedOutcome | None,
        revised_by: UUID,
    ) -> None:
        self._ensure_can_be_changed()

        self.statement = statement
        self.expected_outcome = expected_outcome

        self.record_event(
            HypothesisRevised(
                hypothesis_id=self.id,
                workspace_id=self.workspace_id,
                revised_by=revised_by,
            )
        )

    def link_to_goal(self, goal_ref: GoalReference) -> None:
        self._ensure_can_be_changed()

        self.goal_ref = goal_ref

        self.record_event(
            HypothesisLinkedToGoal(
                hypothesis_id=self.id,
                workspace_id=self.workspace_id,
                goal_id=goal_ref.goal_id,
            )
        )

    def link_to_metric(self, metric_ref: MetricReference) -> None:
        self._ensure_can_be_changed()

        if any(existing.metric_id == metric_ref.metric_id for existing in self.metric_refs):
            return

        self.metric_refs.append(metric_ref)

        self.record_event(
            HypothesisLinkedToMetric(
                hypothesis_id=self.id,
                workspace_id=self.workspace_id,
                metric_id=metric_ref.metric_id,
            )
        )

    def change_priority(self, priority: HypothesisPriority) -> None:
        self._ensure_can_be_changed()

        if self.priority == priority:
            return

        self.priority = priority

        self.record_event(
            HypothesisPriorityChanged(
                hypothesis_id=self.id,
                workspace_id=self.workspace_id,
                priority=priority,
            )
        )

    def mark_ready_for_experiment(self) -> None:
        self._ensure_can_be_changed()

        if self.status == HypothesisStatus.READY_FOR_EXPERIMENT:
            return

        if self.status != HypothesisStatus.DRAFT:
            raise DomainError("Only draft hypothesis can be marked ready for experiment.")

        if self.expected_outcome is None:
            raise DomainError("Hypothesis cannot be ready for experiment without expected outcome.")

        if not self.metric_refs:
            raise DomainError(
                "Hypothesis cannot be ready for experiment without at least one metric reference."
            )

        self.status = HypothesisStatus.READY_FOR_EXPERIMENT

        self.record_event(
            HypothesisMarkedReadyForExperiment(
                hypothesis_id=self.id,
                workspace_id=self.workspace_id,
            )
        )

    def start_testing(self, *, experiment_id: UUID) -> None:
        if self.status == HypothesisStatus.TESTING:
            raise DomainError("Hypothesis is already testing.")

        if self.status != HypothesisStatus.READY_FOR_EXPERIMENT:
            raise DomainError("Only ready hypothesis can start testing.")

        self.status = HypothesisStatus.TESTING

        self.record_event(
            HypothesisTestingStarted(
                hypothesis_id=self.id,
                workspace_id=self.workspace_id,
                experiment_id=experiment_id,
            )
        )

    def mark_validated(self, outcome_ref: ExperimentOutcomeReference) -> None:
        self._set_validation_status(
            status=HypothesisStatus.VALIDATED,
            outcome_ref=outcome_ref,
        )

    def mark_invalidated(self, outcome_ref: ExperimentOutcomeReference) -> None:
        self._set_validation_status(
            status=HypothesisStatus.INVALIDATED,
            outcome_ref=outcome_ref,
        )

    def mark_inconclusive(self, outcome_ref: ExperimentOutcomeReference) -> None:
        self._set_validation_status(
            status=HypothesisStatus.INCONCLUSIVE,
            outcome_ref=outcome_ref,
        )

    def archive(self, *, archived_by: UUID, reason: str) -> None:
        normalized_reason = reason.strip()

        if not normalized_reason:
            raise DomainError("Archive reason cannot be empty.")

        if self.status == HypothesisStatus.TESTING:
            raise DomainError("Testing hypothesis cannot be archived.")

        self.status = HypothesisStatus.ARCHIVED

        self.record_event(
            HypothesisArchived(
                hypothesis_id=self.id,
                workspace_id=self.workspace_id,
                archived_by=archived_by,
                reason=normalized_reason,
            )
        )

    def _set_validation_status(
        self,
        *,
        status: HypothesisStatus,
        outcome_ref: ExperimentOutcomeReference,
    ) -> None:
        if self.status != HypothesisStatus.TESTING:
            raise DomainError("Only testing hypothesis can receive validation status.")

        self.status = status
        self.validation_outcome_ref = outcome_ref

        self.record_event(
            HypothesisValidationStatusChanged(
                hypothesis_id=self.id,
                workspace_id=self.workspace_id,
                status=status,
                experiment_id=outcome_ref.experiment_id,
                outcome_summary=outcome_ref.outcome_summary,
            )
        )

    def _ensure_can_be_changed(self) -> None:
        if self.status in {
            HypothesisStatus.VALIDATED,
            HypothesisStatus.INVALIDATED,
            HypothesisStatus.INCONCLUSIVE,
            HypothesisStatus.ARCHIVED,
        }:
            raise DomainError(f"Hypothesis with status '{self.status}' cannot be changed.")
