from typing import Protocol, Self

from src.domain.shared.aggregate import AggregateRoot

from .repositories import (
    ExperimentRepository,
    HypothesisRepository,
    InitiativeRepository,
    TaskRepository,
)


class UnitOfWork(Protocol):
    hypotheses: HypothesisRepository
    experiments: ExperimentRepository
    tasks: TaskRepository
    initiatives: InitiativeRepository

    async def __aenter__(self) -> Self: ...

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None: ...

    def collect_events(self, aggregate: AggregateRoot[object]) -> None:
        pass

    async def commit(self) -> None:
        pass

    async def rollback(self) -> None:
        pass
