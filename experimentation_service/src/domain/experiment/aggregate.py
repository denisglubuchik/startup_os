from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID, uuid4

from src.domain.experiment.entities import EvidenceItem, ExperimentAmendment, ExperimentStep
from src.domain.experiment.events import (
    EvidenceRecorded,
    ExperimentAmended,
    ExperimentCancelled,
    ExperimentCompleted,
    ExperimentDesigned,
    ExperimentLaunched,
    ExperimentLinkedToGoal,
    ExperimentLinkedToHypothesis,
    ExperimentLinkedToMetric,
    ExperimentOutcomeInterpreted,
    ExperimentRescheduled,
    ExperimentResultRecorded,
    ExperimentScheduled,
    ExperimentStepAdded,
    ExperimentStepCompleted,
)
from src.domain.experiment.value_objects import (
    AmendmentReason,
    CancellationReason,
    EvidenceSource,
    EvidenceType,
    ExperimentDesign,
    ExperimentResult,
    ExperimentSchedule,
    ExperimentStatus,
    ExperimentTitle,
    GoalReference,
    HypothesisReference,
    MetricReference,
    OutcomeInterpretation,
    SuccessCriteria,
)
from src.domain.shared.aggregate import AggregateRoot
from src.domain.shared.errors import DomainError
from src.domain.shared.time import require_utc_datetime


@dataclass(eq=False, kw_only=True)
class Experiment(AggregateRoot[UUID]):
    workspace_id: UUID
    title: ExperimentTitle
    design: ExperimentDesign
    success_criteria: SuccessCriteria
    created_by: UUID
    owner_id: UUID

    status: ExperimentStatus = ExperimentStatus.DRAFT

    hypothesis_refs: list[HypothesisReference] = field(default_factory=list)
    goal_refs: list[GoalReference] = field(default_factory=list)
    metric_refs: list[MetricReference] = field(default_factory=list)

    schedule: ExperimentSchedule | None = None
    steps: list[ExperimentStep] = field(default_factory=list)
    evidence_items: list[EvidenceItem] = field(default_factory=list)
    amendments: list[ExperimentAmendment] = field(default_factory=list)

    result: ExperimentResult | None = None
    outcome_interpretation: OutcomeInterpretation | None = None

    launched_at: datetime | None = None
    completed_at: datetime | None = None
    cancelled_at: datetime | None = None

    @classmethod
    def design_experiment(
        cls,
        *,
        workspace_id: UUID,
        title: ExperimentTitle,
        design: ExperimentDesign,
        success_criteria: SuccessCriteria,
        created_by: UUID,
        owner_id: UUID,
        hypothesis_refs: list[HypothesisReference],
        goal_refs: list[GoalReference] | None = None,
        metric_refs: list[MetricReference] | None = None,
    ) -> Experiment:
        if not hypothesis_refs:
            raise DomainError("Experiment must test at least one hypothesis.")

        experiment = cls(
            id=uuid4(),
            workspace_id=workspace_id,
            title=title,
            design=design,
            success_criteria=success_criteria,
            created_by=created_by,
            owner_id=owner_id,
            hypothesis_refs=list(hypothesis_refs),
            goal_refs=list(goal_refs or []),
            metric_refs=list(metric_refs or []),
        )

        experiment.record_event(
            ExperimentDesigned(
                experiment_id=experiment.id,
                workspace_id=workspace_id,
                created_by=created_by,
                title=title.value,
            )
        )

        for hypothesis_ref in hypothesis_refs:
            experiment.record_event(
                ExperimentLinkedToHypothesis(
                    experiment_id=experiment.id,
                    workspace_id=workspace_id,
                    hypothesis_id=hypothesis_ref.hypothesis_id,
                )
            )

        for goal_ref in experiment.goal_refs:
            experiment.record_event(
                ExperimentLinkedToGoal(
                    experiment_id=experiment.id,
                    workspace_id=workspace_id,
                    goal_id=goal_ref.goal_id,
                )
            )

        for metric_ref in experiment.metric_refs:
            experiment.record_event(
                ExperimentLinkedToMetric(
                    experiment_id=experiment.id,
                    workspace_id=workspace_id,
                    metric_id=metric_ref.metric_id,
                )
            )

        return experiment

    def schedule_experiment(self, schedule: ExperimentSchedule) -> None:
        self._ensure_not_finished()

        if self.status == ExperimentStatus.SCHEDULED:
            raise DomainError("Experiment is already scheduled. Use reschedule_experiment.")

        if self.status != ExperimentStatus.DRAFT:
            raise DomainError("Only draft experiment can be scheduled.")

        self.schedule = schedule
        self.status = ExperimentStatus.SCHEDULED

        self.record_event(
            ExperimentScheduled(
                experiment_id=self.id,
                workspace_id=self.workspace_id,
            )
        )

    def reschedule_experiment(self, schedule: ExperimentSchedule) -> None:
        self._ensure_not_finished()

        if self.status != ExperimentStatus.SCHEDULED:
            raise DomainError("Only scheduled experiment can be rescheduled.")

        self.schedule = schedule

        self.record_event(
            ExperimentRescheduled(
                experiment_id=self.id,
                workspace_id=self.workspace_id,
            )
        )

    def launch(self, *, launched_at: datetime) -> None:
        self._ensure_not_finished()
        launched_at = require_utc_datetime(launched_at, "launched_at")

        if self.status not in {
            ExperimentStatus.DRAFT,
            ExperimentStatus.SCHEDULED,
        }:
            raise DomainError("Experiment cannot be launched from current status.")

        if not self.hypothesis_refs:
            raise DomainError("Experiment cannot launch without hypothesis.")

        self.status = ExperimentStatus.RUNNING
        self.launched_at = launched_at

        self.record_event(
            ExperimentLaunched(
                experiment_id=self.id,
                workspace_id=self.workspace_id,
                owner_id=self.owner_id,
            )
        )

    def add_step(
        self,
        *,
        title: str,
        assignee_id: UUID | None = None,
        due_at: datetime | None = None,
    ) -> UUID:
        self._ensure_not_finished()

        step = ExperimentStep.create(
            title=title,
            assignee_id=assignee_id,
            due_at=due_at,
        )

        self.steps.append(step)

        self.record_event(
            ExperimentStepAdded(
                experiment_id=self.id,
                workspace_id=self.workspace_id,
                step_id=step.id,
                title=step.title,
            )
        )

        return step.id

    def complete_step(self, *, step_id: UUID, completed_at: datetime) -> None:
        self._ensure_not_finished()
        completed_at = require_utc_datetime(completed_at, "completed_at")

        step = self._get_step(step_id)
        step.complete(completed_at=completed_at)

        self.record_event(
            ExperimentStepCompleted(
                experiment_id=self.id,
                workspace_id=self.workspace_id,
                step_id=step.id,
            )
        )

    def record_evidence(
        self,
        *,
        evidence_type: EvidenceType,
        source: EvidenceSource,
        summary: str,
        recorded_by: UUID,
        recorded_at: datetime,
        metric_observation_id: UUID | None = None,
    ) -> UUID:
        if self.status != ExperimentStatus.RUNNING:
            raise DomainError("Evidence can be recorded only for running experiment.")

        evidence = EvidenceItem.record(
            evidence_type=evidence_type,
            source=source,
            summary=summary,
            recorded_by=recorded_by,
            recorded_at=recorded_at,
            metric_observation_id=metric_observation_id,
        )

        self.evidence_items.append(evidence)

        self.record_event(
            EvidenceRecorded(
                experiment_id=self.id,
                workspace_id=self.workspace_id,
                evidence_id=evidence.id,
                evidence_type=evidence.evidence_type,
            )
        )

        return evidence.id

    def record_result(self, result: ExperimentResult) -> None:
        if self.status != ExperimentStatus.RUNNING:
            raise DomainError("Result can be recorded only for running experiment.")

        if self.result is not None:
            raise DomainError("Experiment result has already been recorded.")

        if not self.evidence_items:
            raise DomainError("Experiment result cannot be recorded without evidence.")

        self.result = result

        self.record_event(
            ExperimentResultRecorded(
                experiment_id=self.id,
                workspace_id=self.workspace_id,
                recorded_by=result.recorded_by,
            )
        )

    def interpret_outcome(self, interpretation: OutcomeInterpretation) -> None:
        if self.status != ExperimentStatus.RUNNING:
            raise DomainError("Outcome can be interpreted only for running experiment.")

        if self.result is None:
            raise DomainError("Experiment outcome cannot be interpreted before result is recorded.")

        if self.outcome_interpretation is not None:
            raise DomainError("Experiment outcome has already been interpreted.")

        self.outcome_interpretation = interpretation

        self.record_event(
            ExperimentOutcomeInterpreted(
                experiment_id=self.id,
                workspace_id=self.workspace_id,
                outcome=interpretation.outcome,
                interpreted_by=interpretation.interpreted_by,
            )
        )

    def complete(self, *, completed_at: datetime) -> None:
        completed_at = require_utc_datetime(completed_at, "completed_at")

        if self.status != ExperimentStatus.RUNNING:
            raise DomainError("Only running experiment can be completed.")

        if self.result is None:
            raise DomainError("Experiment cannot be completed without result.")

        if self.outcome_interpretation is None:
            raise DomainError("Experiment cannot be completed without outcome interpretation.")

        self.status = ExperimentStatus.COMPLETED
        self.completed_at = completed_at

        self.record_event(
            ExperimentCompleted(
                experiment_id=self.id,
                workspace_id=self.workspace_id,
            )
        )

    def cancel(
        self,
        *,
        reason: CancellationReason,
        cancelled_by: UUID,
        cancelled_at: datetime,
    ) -> None:
        self._ensure_not_finished()
        cancelled_at = require_utc_datetime(cancelled_at, "cancelled_at")

        self.status = ExperimentStatus.CANCELLED
        self.cancelled_at = cancelled_at

        self.record_event(
            ExperimentCancelled(
                experiment_id=self.id,
                workspace_id=self.workspace_id,
                cancelled_by=cancelled_by,
                reason=reason.value,
            )
        )

    def amend(
        self,
        *,
        reason: AmendmentReason,
        description: str,
        amended_by: UUID,
        amended_at: datetime,
    ) -> UUID:
        amended_at = require_utc_datetime(amended_at, "amended_at")

        if self.status != ExperimentStatus.RUNNING:
            raise DomainError("Only running experiment can be amended.")

        amendment = ExperimentAmendment.create(
            reason=reason,
            description=description,
            amended_by=amended_by,
            amended_at=amended_at,
        )

        self.amendments.append(amendment)

        self.record_event(
            ExperimentAmended(
                experiment_id=self.id,
                workspace_id=self.workspace_id,
                amendment_id=amendment.id,
                amended_by=amended_by,
            )
        )

        return amendment.id

    def _get_step(self, step_id: UUID) -> ExperimentStep:
        for step in self.steps:
            if step.id == step_id:
                return step

        raise DomainError("Experiment step not found.")

    def _ensure_not_finished(self) -> None:
        if self.status in {
            ExperimentStatus.COMPLETED,
            ExperimentStatus.CANCELLED,
        }:
            raise DomainError(f"Experiment with status '{self.status}' cannot be changed.")
