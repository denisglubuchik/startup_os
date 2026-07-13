import asyncio
from datetime import datetime
from uuid import uuid4

import pytest

from src.domain.hypothesis.aggregate import Hypothesis
from src.domain.hypothesis.events import (
    HypothesisFormulated,
    HypothesisMarkedReadyForExperiment,
    HypothesisTestingStarted,
    HypothesisValidationStatusChanged,
)
from src.domain.hypothesis.value_objects import (
    ExpectedOutcome,
    ExperimentOutcomeReference,
    HypothesisStatement,
    HypothesisStatus,
    MetricReference,
)
from src.domain.shared.errors import DomainError


async def async_checkpoint() -> None:
    await asyncio.sleep(0)


async def test_formulate_creates_draft_hypothesis_and_event() -> None:
    await async_checkpoint()

    workspace_id = uuid4()
    created_by = uuid4()

    hypothesis = Hypothesis.formulate(
        workspace_id=workspace_id,
        statement=HypothesisStatement("Founders will connect goals to experiments."),
        expected_outcome=ExpectedOutcome("Most founders can name the goal being tested."),
        created_by=created_by,
    )

    events = hypothesis.pull_events()

    assert hypothesis.workspace_id == workspace_id
    assert hypothesis.created_by == created_by
    assert hypothesis.status == HypothesisStatus.DRAFT
    assert len(events) == 1
    assert isinstance(events[0], HypothesisFormulated)
    assert events[0].event_type == "HypothesisFormulated"
    assert isinstance(events[0].occurred_at, datetime)


async def test_ready_for_experiment_requires_expected_outcome() -> None:
    await async_checkpoint()

    hypothesis = Hypothesis.formulate(
        workspace_id=uuid4(),
        statement=HypothesisStatement("Users will understand the activation prompt."),
        expected_outcome=None,
        created_by=uuid4(),
    )
    hypothesis.link_to_metric(MetricReference(metric_id=uuid4()))

    with pytest.raises(DomainError, match="without expected outcome"):
        hypothesis.mark_ready_for_experiment()


async def test_ready_for_experiment_requires_metric_reference() -> None:
    await async_checkpoint()

    hypothesis = Hypothesis.formulate(
        workspace_id=uuid4(),
        statement=HypothesisStatement("Users will understand the activation prompt."),
        expected_outcome=ExpectedOutcome("Users can explain the prompt correctly."),
        created_by=uuid4(),
    )

    with pytest.raises(DomainError, match="without at least one metric reference"):
        hypothesis.mark_ready_for_experiment()


async def test_mark_ready_for_experiment_is_idempotent_once_ready() -> None:
    await async_checkpoint()

    hypothesis = ready_hypothesis()
    hypothesis.pull_events()

    hypothesis.mark_ready_for_experiment()

    assert hypothesis.status == HypothesisStatus.READY_FOR_EXPERIMENT
    assert hypothesis.pull_events() == []


async def test_testing_can_only_start_from_ready_state() -> None:
    await async_checkpoint()

    hypothesis = Hypothesis.formulate(
        workspace_id=uuid4(),
        statement=HypothesisStatement("Users will understand the activation prompt."),
        expected_outcome=ExpectedOutcome("Users can explain the prompt correctly."),
        created_by=uuid4(),
    )

    with pytest.raises(DomainError, match="Only ready hypothesis"):
        hypothesis.start_testing(experiment_id=uuid4())


async def test_start_testing_rejects_duplicate_start() -> None:
    await async_checkpoint()

    hypothesis = ready_hypothesis()
    experiment_id = uuid4()
    hypothesis.start_testing(experiment_id=experiment_id)
    hypothesis.pull_events()

    with pytest.raises(DomainError, match="already testing"):
        hypothesis.start_testing(experiment_id=uuid4())

    assert hypothesis.status == HypothesisStatus.TESTING
    assert hypothesis.pull_events() == []


async def test_testing_hypothesis_cannot_be_marked_ready_again() -> None:
    await async_checkpoint()

    hypothesis = ready_hypothesis()
    hypothesis.start_testing(experiment_id=uuid4())

    with pytest.raises(DomainError, match="Only draft hypothesis"):
        hypothesis.mark_ready_for_experiment()


async def test_testing_hypothesis_can_be_validated() -> None:
    await async_checkpoint()

    hypothesis = ready_hypothesis()
    experiment_id = uuid4()
    hypothesis.start_testing(experiment_id=experiment_id)
    hypothesis.pull_events()

    hypothesis.mark_validated(
        ExperimentOutcomeReference(
            experiment_id=experiment_id,
            outcome_summary="The metric moved enough to validate the assumption.",
        )
    )

    events = hypothesis.pull_events()

    assert hypothesis.status == HypothesisStatus.VALIDATED
    assert hypothesis.validation_outcome_ref is not None
    assert len(events) == 1
    assert isinstance(events[0], HypothesisValidationStatusChanged)
    assert events[0].experiment_id == experiment_id


def ready_hypothesis() -> Hypothesis:
    hypothesis = Hypothesis.formulate(
        workspace_id=uuid4(),
        statement=HypothesisStatement("Users will understand the activation prompt."),
        expected_outcome=ExpectedOutcome("Users can explain the prompt correctly."),
        created_by=uuid4(),
    )
    hypothesis.link_to_metric(MetricReference(metric_id=uuid4()))
    hypothesis.mark_ready_for_experiment()

    events = hypothesis.pull_events()
    assert any(isinstance(event, HypothesisMarkedReadyForExperiment) for event in events)
    assert not any(isinstance(event, HypothesisTestingStarted) for event in events)

    return hypothesis
