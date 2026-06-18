from src.domain.experiment.aggregate import Experiment
from src.domain.experiment.entities import EvidenceItem, ExperimentAmendment, ExperimentStep
from src.domain.experiment.value_objects import (
    AmendmentReason,
    EvidenceSource,
    EvidenceType,
    ExperimentDesign,
    ExperimentResult,
    ExperimentSchedule,
    ExperimentStatus,
    ExperimentStepStatus,
    ExperimentTitle,
    GoalReference,
    HypothesisReference,
    MetricReference,
    OutcomeInterpretation,
    OutcomeType,
    SuccessCriteria,
)
from src.infrastructure.db.models.experiment import (
    EvidenceItemModel,
    ExperimentAmendmentModel,
    ExperimentGoalReferenceModel,
    ExperimentHypothesisReferenceModel,
    ExperimentMetricReferenceModel,
    ExperimentModel,
    ExperimentStepModel,
)


class ExperimentMapper:
    def to_domain(self, model: ExperimentModel) -> Experiment:
        return Experiment(
            id=model.id,
            workspace_id=model.workspace_id,
            title=ExperimentTitle(model.title),
            design=ExperimentDesign(
                method=model.method,
                audience=model.audience,
                procedure=model.procedure,
            ),
            success_criteria=SuccessCriteria(model.success_criteria),
            created_by=model.created_by,
            owner_id=model.owner_id,
            status=ExperimentStatus(model.status),
            hypothesis_refs=[
                HypothesisReference(
                    hypothesis_id=reference.hypothesis_id,
                    statement_snapshot=reference.statement_snapshot,
                )
                for reference in model.hypothesis_refs
            ],
            goal_refs=[
                GoalReference(goal_id=reference.goal_id, title_snapshot=reference.title_snapshot)
                for reference in model.goal_refs
            ],
            metric_refs=[
                MetricReference(
                    metric_id=reference.metric_id,
                    name_snapshot=reference.name_snapshot,
                    unit_snapshot=reference.unit_snapshot,
                )
                for reference in model.metric_refs
            ],
            schedule=(
                ExperimentSchedule(
                    planned_start_at=model.planned_start_at,
                    planned_end_at=model.planned_end_at,
                )
                if model.planned_start_at is not None and model.planned_end_at is not None
                else None
            ),
            steps=[self._step_to_domain(step) for step in model.steps],
            evidence_items=[
                self._evidence_to_domain(evidence) for evidence in model.evidence_items
            ],
            amendments=[self._amendment_to_domain(amendment) for amendment in model.amendments],
            result=(
                ExperimentResult(
                    summary=model.result_summary,
                    recorded_by=model.result_recorded_by,
                    recorded_at=model.result_recorded_at,
                )
                if model.result_summary is not None
                and model.result_recorded_by is not None
                and model.result_recorded_at is not None
                else None
            ),
            outcome_interpretation=(
                OutcomeInterpretation(
                    outcome=OutcomeType(model.outcome),
                    reasoning=model.outcome_reasoning,
                    interpreted_by=model.outcome_interpreted_by,
                    interpreted_at=model.outcome_interpreted_at,
                )
                if model.outcome is not None
                and model.outcome_reasoning is not None
                and model.outcome_interpreted_by is not None
                and model.outcome_interpreted_at is not None
                else None
            ),
            launched_at=model.launched_at,
            completed_at=model.completed_at,
            cancelled_at=model.cancelled_at,
        )

    def to_model(
        self, experiment: Experiment, model: ExperimentModel | None = None
    ) -> ExperimentModel:
        model = model or ExperimentModel(id=experiment.id)
        model.workspace_id = experiment.workspace_id
        model.title = experiment.title.value
        model.method = experiment.design.method
        model.audience = experiment.design.audience
        model.procedure = experiment.design.procedure
        model.success_criteria = experiment.success_criteria.description
        model.created_by = experiment.created_by
        model.owner_id = experiment.owner_id
        model.status = experiment.status.value
        model.planned_start_at = (
            experiment.schedule.planned_start_at if experiment.schedule is not None else None
        )
        model.planned_end_at = (
            experiment.schedule.planned_end_at if experiment.schedule is not None else None
        )
        model.result_summary = experiment.result.summary if experiment.result else None
        model.result_recorded_by = experiment.result.recorded_by if experiment.result else None
        model.result_recorded_at = experiment.result.recorded_at if experiment.result else None
        model.outcome = (
            experiment.outcome_interpretation.outcome.value
            if experiment.outcome_interpretation
            else None
        )
        model.outcome_reasoning = (
            experiment.outcome_interpretation.reasoning
            if experiment.outcome_interpretation
            else None
        )
        model.outcome_interpreted_by = (
            experiment.outcome_interpretation.interpreted_by
            if experiment.outcome_interpretation
            else None
        )
        model.outcome_interpreted_at = (
            experiment.outcome_interpretation.interpreted_at
            if experiment.outcome_interpretation
            else None
        )
        model.launched_at = experiment.launched_at
        model.completed_at = experiment.completed_at
        model.cancelled_at = experiment.cancelled_at
        model.hypothesis_refs = [
            ExperimentHypothesisReferenceModel(
                experiment_id=experiment.id,
                hypothesis_id=reference.hypothesis_id,
                statement_snapshot=reference.statement_snapshot,
            )
            for reference in experiment.hypothesis_refs
        ]
        model.goal_refs = [
            ExperimentGoalReferenceModel(
                experiment_id=experiment.id,
                goal_id=reference.goal_id,
                title_snapshot=reference.title_snapshot,
            )
            for reference in experiment.goal_refs
        ]
        model.metric_refs = [
            ExperimentMetricReferenceModel(
                experiment_id=experiment.id,
                metric_id=reference.metric_id,
                name_snapshot=reference.name_snapshot,
                unit_snapshot=reference.unit_snapshot,
            )
            for reference in experiment.metric_refs
        ]
        model.steps = [self._step_to_model(experiment.id, step) for step in experiment.steps]
        model.evidence_items = [
            self._evidence_to_model(experiment.id, evidence)
            for evidence in experiment.evidence_items
        ]
        model.amendments = [
            self._amendment_to_model(experiment.id, amendment)
            for amendment in experiment.amendments
        ]
        return model

    def _step_to_domain(self, model: ExperimentStepModel) -> ExperimentStep:
        return ExperimentStep(
            id=model.id,
            title=model.title,
            status=ExperimentStepStatus(model.status),
            assignee_id=model.assignee_id,
            due_at=model.due_at,
            completed_at=model.completed_at,
        )

    def _step_to_model(self, experiment_id, step: ExperimentStep) -> ExperimentStepModel:
        return ExperimentStepModel(
            id=step.id,
            experiment_id=experiment_id,
            title=step.title,
            status=step.status.value,
            assignee_id=step.assignee_id,
            due_at=step.due_at,
            completed_at=step.completed_at,
        )

    def _evidence_to_domain(self, model: EvidenceItemModel) -> EvidenceItem:
        return EvidenceItem(
            id=model.id,
            evidence_type=EvidenceType(model.evidence_type),
            source=EvidenceSource(
                description=model.source_description,
                external_url=model.source_external_url,
            ),
            summary=model.summary,
            recorded_by=model.recorded_by,
            recorded_at=model.recorded_at,
            metric_observation_id=model.metric_observation_id,
        )

    def _evidence_to_model(self, experiment_id, evidence: EvidenceItem) -> EvidenceItemModel:
        return EvidenceItemModel(
            id=evidence.id,
            experiment_id=experiment_id,
            evidence_type=evidence.evidence_type.value,
            source_description=evidence.source.description,
            source_external_url=evidence.source.external_url,
            summary=evidence.summary,
            recorded_by=evidence.recorded_by,
            recorded_at=evidence.recorded_at,
            metric_observation_id=evidence.metric_observation_id,
        )

    def _amendment_to_domain(self, model: ExperimentAmendmentModel) -> ExperimentAmendment:
        return ExperimentAmendment(
            id=model.id,
            reason=AmendmentReason(model.reason),
            description=model.description,
            amended_by=model.amended_by,
            amended_at=model.amended_at,
        )

    def _amendment_to_model(
        self,
        experiment_id,
        amendment: ExperimentAmendment,
    ) -> ExperimentAmendmentModel:
        return ExperimentAmendmentModel(
            id=amendment.id,
            experiment_id=experiment_id,
            reason=amendment.reason.value,
            description=amendment.description,
            amended_by=amendment.amended_by,
            amended_at=amendment.amended_at,
        )
