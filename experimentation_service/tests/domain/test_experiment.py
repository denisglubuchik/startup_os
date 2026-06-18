from datetime import UTC, datetime
from uuid import uuid4

import pytest

from src.domain.experiment.aggregate import Experiment
from src.domain.experiment.entities import ExperimentStep
from src.domain.experiment.events import (
    ExperimentCompleted,
    ExperimentDesigned,
    ExperimentLaunched,
    ExperimentRescheduled,
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
    ExperimentStepStatus,
    ExperimentTitle,
    HypothesisReference,
    OutcomeInterpretation,
    OutcomeType,
    SuccessCriteria,
)
from src.domain.shared.errors import DomainError


async def test_design_experiment_records_design_event() -> None:
    experiment = designed_experiment()

    events = experiment.pull_events()

    assert experiment.status == ExperimentStatus.DRAFT
    assert len(events) == 2
    assert isinstance(events[0], ExperimentDesigned)
    assert events[0].experiment_id == experiment.id


async def test_design_experiment_requires_hypothesis_reference() -> None:
    with pytest.raises(DomainError, match="at least one hypothesis"):
        Experiment.design_experiment(
            workspace_id=uuid4(),
            title=ExperimentTitle("Activation interview test"),
            design=valid_design(),
            success_criteria=valid_success_criteria(),
            created_by=uuid4(),
            owner_id=uuid4(),
            hypothesis_refs=[],
        )


async def test_reschedule_updates_schedule_and_records_event() -> None:
    experiment = designed_experiment()
    original_schedule = schedule_at(9, 10)
    updated_schedule = schedule_at(11, 12)
    experiment.schedule_experiment(original_schedule)
    experiment.pull_events()

    experiment.reschedule_experiment(updated_schedule)

    events = experiment.pull_events()

    assert experiment.schedule == updated_schedule
    assert experiment.status == ExperimentStatus.SCHEDULED
    assert len(events) == 1
    assert isinstance(events[0], ExperimentRescheduled)


async def test_schedule_twice_requires_reschedule_method() -> None:
    experiment = designed_experiment()
    experiment.schedule_experiment(schedule_at(9, 10))

    with pytest.raises(DomainError, match="Use reschedule_experiment"):
        experiment.schedule_experiment(schedule_at(11, 12))


async def test_launch_records_event() -> None:
    experiment = designed_experiment()
    experiment.pull_events()

    experiment.launch(launched_at=at_hour(9))

    events = experiment.pull_events()

    assert experiment.status == ExperimentStatus.RUNNING
    assert experiment.launched_at == at_hour(9)
    assert len(events) == 1
    assert isinstance(events[0], ExperimentLaunched)


async def test_evidence_can_only_be_recorded_for_running_experiment() -> None:
    experiment = designed_experiment()

    with pytest.raises(DomainError, match="only for running experiment"):
        record_evidence(experiment)


async def test_result_requires_evidence() -> None:
    experiment = running_experiment()

    with pytest.raises(DomainError, match="without evidence"):
        experiment.record_result(valid_result())


async def test_interpretation_requires_result() -> None:
    experiment = running_experiment()
    record_evidence(experiment)

    with pytest.raises(DomainError, match="before result is recorded"):
        experiment.interpret_outcome(valid_interpretation())


async def test_complete_requires_result_and_interpretation() -> None:
    experiment = running_experiment()

    with pytest.raises(DomainError, match="without result"):
        experiment.complete(completed_at=at_hour(11))

    record_evidence(experiment)
    experiment.record_result(valid_result())

    with pytest.raises(DomainError, match="without outcome interpretation"):
        experiment.complete(completed_at=at_hour(11))


async def test_experiment_can_complete_after_result_and_interpretation() -> None:
    experiment = running_experiment()
    record_evidence(experiment)
    experiment.record_result(valid_result())
    experiment.interpret_outcome(valid_interpretation())
    experiment.pull_events()

    experiment.complete(completed_at=at_hour(11))

    events = experiment.pull_events()

    assert experiment.status == ExperimentStatus.COMPLETED
    assert experiment.completed_at == at_hour(11)
    assert len(events) == 1
    assert isinstance(events[0], ExperimentCompleted)


async def test_cancelled_experiment_cannot_be_mutated() -> None:
    experiment = designed_experiment()
    experiment.cancel(
        reason=CancellationReason("Customer segment changed"),
        cancelled_by=uuid4(),
        cancelled_at=at_hour(9),
    )

    with pytest.raises(DomainError, match="cannot be changed"):
        experiment.add_step(title="Call customer")


async def test_amend_only_works_while_running() -> None:
    experiment = designed_experiment()

    with pytest.raises(DomainError, match="Only running experiment"):
        experiment.amend(
            reason=AmendmentReason("Customer availability changed"),
            description="Move interviews to next week.",
            amended_by=uuid4(),
            amended_at=at_hour(10),
        )

    experiment.launch(launched_at=at_hour(9))
    amendment_id = experiment.amend(
        reason=AmendmentReason("Customer availability changed"),
        description="Move interviews to next week.",
        amended_by=uuid4(),
        amended_at=at_hour(10),
    )

    assert experiment.amendments[0].id == amendment_id


async def test_blocked_step_cannot_be_completed() -> None:
    step = ExperimentStep.create(title="Interview customer")
    step.block()

    with pytest.raises(DomainError, match="Step cannot be completed"):
        step.complete(completed_at=at_hour(10))

    assert step.status == ExperimentStepStatus.BLOCKED


async def test_evidence_source_normalizes_empty_external_url_to_none() -> None:
    source = EvidenceSource(description=" Customer interview ", external_url="   ")

    assert source.description == "Customer interview"
    assert source.external_url is None


async def test_evidence_source_encodes_external_url() -> None:
    source = EvidenceSource(
        description="Customer interview",
        external_url=" HTTPS://EXAMPLE.COM/customer notes/one?q=hello world#part 1 ",
    )

    assert source.external_url == "https://example.com/customer%20notes/one?q=hello%20world#part%201"


async def test_evidence_source_requires_absolute_external_url() -> None:
    with pytest.raises(DomainError, match="scheme and host"):
        EvidenceSource(description="Customer interview", external_url="/relative/path")


def designed_experiment() -> Experiment:
    return Experiment.design_experiment(
        workspace_id=uuid4(),
        title=ExperimentTitle("Activation interview test"),
        design=valid_design(),
        success_criteria=valid_success_criteria(),
        created_by=uuid4(),
        owner_id=uuid4(),
        hypothesis_refs=[HypothesisReference(hypothesis_id=uuid4())],
    )


def running_experiment() -> Experiment:
    experiment = designed_experiment()
    experiment.launch(launched_at=at_hour(9))
    return experiment


def record_evidence(experiment: Experiment) -> None:
    experiment.record_evidence(
        evidence_type=EvidenceType.INTERVIEW_NOTE,
        source=EvidenceSource(description="Customer interview"),
        summary="Customer understood the workflow.",
        recorded_by=uuid4(),
        recorded_at=at_hour(10),
    )


def valid_result() -> ExperimentResult:
    return ExperimentResult(
        summary="Users understood the workflow.",
        recorded_by=uuid4(),
        recorded_at=at_hour(10),
    )


def valid_interpretation() -> OutcomeInterpretation:
    return OutcomeInterpretation(
        outcome=OutcomeType.SUPPORTS_HYPOTHESIS,
        reasoning="The observed behavior supports the hypothesis.",
        interpreted_by=uuid4(),
        interpreted_at=at_hour(10),
    )


def valid_design() -> ExperimentDesign:
    return ExperimentDesign(
        method="Customer interviews",
        audience="Early-stage founders",
        procedure="Ask founders to map a goal to an experiment.",
    )


def valid_success_criteria() -> SuccessCriteria:
    return SuccessCriteria("Five founders can complete the mapping unaided.")


def schedule_at(start_hour: int, end_hour: int) -> ExperimentSchedule:
    return ExperimentSchedule(
        planned_start_at=at_hour(start_hour),
        planned_end_at=at_hour(end_hour),
    )


def at_hour(hour: int) -> datetime:
    return datetime(2026, 1, 1, hour, 0, tzinfo=UTC)
