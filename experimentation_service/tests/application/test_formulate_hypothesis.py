from uuid import uuid4

import pytest

from src.application.commands.hypothesis import (
    FormulateHypothesisCommand,
    FormulateHypothesisUseCase,
)
from src.application.errors import ValidationError
from src.domain.hypothesis.events import HypothesisFormulated
from src.domain.hypothesis.value_objects import (
    ConfidenceLevel,
    HypothesisPriority,
    HypothesisStatus,
)
from tests.support.fakes import FakeUnitOfWork


async def test_formulate_hypothesis_saves_aggregate_and_collects_event(
    fake_uow: FakeUnitOfWork,
    formulate_hypothesis_use_case: FormulateHypothesisUseCase,
) -> None:
    workspace_id = uuid4()

    result = await formulate_hypothesis_use_case.execute(
        FormulateHypothesisCommand(
            workspace_id=workspace_id,
            statement="Founders will link experiments to measurable goals.",
            expected_outcome="Most founders can identify the tested metric.",
            created_by=uuid4(),
            confidence=ConfidenceLevel.MEDIUM.value,
            priority=HypothesisPriority.HIGH.value,
        )
    )

    assert result.workspace_id == workspace_id
    assert result.status == HypothesisStatus.DRAFT
    assert len(fake_uow.hypotheses.saved) == 1
    assert fake_uow.hypotheses.saved[0].id == result.hypothesis_id
    assert fake_uow.hypotheses.saved[0].confidence == ConfidenceLevel.MEDIUM
    assert fake_uow.hypotheses.saved[0].priority == HypothesisPriority.HIGH
    assert len(fake_uow.events) == 1
    assert isinstance(fake_uow.events[0], HypothesisFormulated)
    assert fake_uow.committed is True
    assert fake_uow.rolled_back is False


async def test_formulate_hypothesis_rejects_invalid_priority(
    formulate_hypothesis_use_case: FormulateHypothesisUseCase,
) -> None:
    with pytest.raises(ValidationError, match="Invalid priority"):
        await formulate_hypothesis_use_case.execute(
            FormulateHypothesisCommand(
                workspace_id=uuid4(),
                statement="Founders will link experiments to measurable goals.",
                expected_outcome=None,
                created_by=uuid4(),
                priority="urgent",
            )
        )
