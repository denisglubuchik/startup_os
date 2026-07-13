from datetime import UTC, datetime, timedelta, timezone
from uuid import uuid4

import pytest

from src.domain.experiment.aggregate import Experiment
from src.domain.experiment.value_objects import (
    EvidenceSource,
    EvidenceType,
    ExperimentDesign,
    ExperimentSchedule,
    ExperimentStatus,
    ExperimentTitle,
    HypothesisReference,
    SuccessCriteria,
)
from src.domain.shared.errors import DomainError


async def test_experiment_schedule_rejects_naive_datetimes() -> None:
    with pytest.raises(DomainError, match="planned_start_at must be timezone-aware"):
        ExperimentSchedule(
            planned_start_at=datetime(2026, 1, 1, 9, 0),  # noqa: DTZ001
            planned_end_at=datetime(2026, 1, 1, 10, 0, tzinfo=UTC),
        )


async def test_experiment_schedule_normalizes_aware_datetimes_to_utc() -> None:
    local_tz = timezone(timedelta(hours=3))

    schedule = ExperimentSchedule(
        planned_start_at=datetime(2026, 1, 1, 12, 0, tzinfo=local_tz),
        planned_end_at=datetime(2026, 1, 1, 13, 0, tzinfo=local_tz),
    )

    assert schedule.planned_start_at == datetime(2026, 1, 1, 9, 0, tzinfo=UTC)
    assert schedule.planned_end_at == datetime(2026, 1, 1, 10, 0, tzinfo=UTC)


async def test_launch_rejects_naive_datetime() -> None:
    experiment = designed_experiment()

    with pytest.raises(DomainError, match="launched_at must be timezone-aware"):
        experiment.launch(launched_at=datetime(2026, 1, 1, 9, 0))  # noqa: DTZ001


async def test_launch_normalizes_datetime_to_utc() -> None:
    experiment = designed_experiment()
    local_tz = timezone(timedelta(hours=-5))

    experiment.launch(launched_at=datetime(2026, 1, 1, 4, 0, tzinfo=local_tz))

    assert experiment.status == ExperimentStatus.RUNNING
    assert experiment.launched_at == datetime(2026, 1, 1, 9, 0, tzinfo=UTC)


async def test_record_evidence_rejects_naive_datetime() -> None:
    experiment = designed_experiment()
    experiment.launch(launched_at=datetime(2026, 1, 1, 9, 0, tzinfo=UTC))

    with pytest.raises(DomainError, match="recorded_at must be timezone-aware"):
        experiment.record_evidence(
            evidence_type=EvidenceType.INTERVIEW_NOTE,
            source=EvidenceSource(description="Customer call"),
            summary="The customer understood the workflow.",
            recorded_by=uuid4(),
            recorded_at=datetime(2026, 1, 1, 9, 30),  # noqa: DTZ001
        )


def designed_experiment() -> Experiment:
    return Experiment.design_experiment(
        workspace_id=uuid4(),
        title=ExperimentTitle("Activation interview test"),
        design=ExperimentDesign(
            method="Customer interviews",
            audience="Early-stage founders",
            procedure="Ask founders to map a goal to an experiment.",
        ),
        success_criteria=SuccessCriteria("Five founders can complete the mapping unaided."),
        created_by=uuid4(),
        owner_id=uuid4(),
        hypothesis_refs=[HypothesisReference(hypothesis_id=uuid4())],
    )
