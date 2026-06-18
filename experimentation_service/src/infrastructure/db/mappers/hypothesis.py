from src.domain.hypothesis.aggregate import Hypothesis
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
from src.infrastructure.db.models.hypothesis import (
    HypothesisMetricReferenceModel,
    HypothesisModel,
)


class HypothesisMapper:
    def to_domain(self, model: HypothesisModel) -> Hypothesis:
        return Hypothesis(
            id=model.id,
            workspace_id=model.workspace_id,
            statement=HypothesisStatement(model.statement),
            expected_outcome=(
                ExpectedOutcome(model.expected_outcome)
                if model.expected_outcome is not None
                else None
            ),
            created_by=model.created_by,
            status=HypothesisStatus(model.status),
            confidence=ConfidenceLevel(model.confidence),
            priority=HypothesisPriority(model.priority),
            goal_ref=(
                GoalReference(
                    goal_id=model.goal_id,
                    title_snapshot=model.goal_title_snapshot,
                )
                if model.goal_id is not None
                else None
            ),
            metric_refs=[
                MetricReference(
                    metric_id=metric.metric_id,
                    name_snapshot=metric.name_snapshot,
                    unit_snapshot=metric.unit_snapshot,
                )
                for metric in model.metric_refs
            ],
            validation_outcome_ref=(
                ExperimentOutcomeReference(
                    experiment_id=model.validation_experiment_id,
                    outcome_summary=model.validation_outcome_summary or "",
                )
                if model.validation_experiment_id is not None
                else None
            ),
        )

    def to_model(
        self, hypothesis: Hypothesis, model: HypothesisModel | None = None
    ) -> HypothesisModel:
        model = model or HypothesisModel(id=hypothesis.id)
        model.workspace_id = hypothesis.workspace_id
        model.statement = hypothesis.statement.value
        model.expected_outcome = (
            hypothesis.expected_outcome.description
            if hypothesis.expected_outcome is not None
            else None
        )
        model.created_by = hypothesis.created_by
        model.status = hypothesis.status.value
        model.confidence = hypothesis.confidence.value
        model.priority = hypothesis.priority.value
        model.goal_id = hypothesis.goal_ref.goal_id if hypothesis.goal_ref else None
        model.goal_title_snapshot = (
            hypothesis.goal_ref.title_snapshot if hypothesis.goal_ref else None
        )
        model.validation_experiment_id = (
            hypothesis.validation_outcome_ref.experiment_id
            if hypothesis.validation_outcome_ref
            else None
        )
        model.validation_outcome_summary = (
            hypothesis.validation_outcome_ref.outcome_summary
            if hypothesis.validation_outcome_ref
            else None
        )
        model.metric_refs = [
            HypothesisMetricReferenceModel(
                hypothesis_id=hypothesis.id,
                metric_id=metric.metric_id,
                name_snapshot=metric.name_snapshot,
                unit_snapshot=metric.unit_snapshot,
            )
            for metric in hypothesis.metric_refs
        ]
        return model
