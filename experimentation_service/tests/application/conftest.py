import pytest

from src.application.commands.hypothesis import FormulateHypothesisUseCase
from tests.support.fakes import FakeUnitOfWork


@pytest.fixture
def fake_uow() -> FakeUnitOfWork:
    return FakeUnitOfWork()


@pytest.fixture
def formulate_hypothesis_use_case(
    fake_uow: FakeUnitOfWork,
) -> FormulateHypothesisUseCase:
    return FormulateHypothesisUseCase(fake_uow)
