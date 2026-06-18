from types import TracebackType
from typing import Self

from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.shared.aggregate import AggregateRoot
from src.domain.shared.events import DomainEvent
from src.infrastructure.db.mappers.experiment import ExperimentMapper
from src.infrastructure.db.mappers.hypothesis import HypothesisMapper
from src.infrastructure.db.mappers.initiative import InitiativeMapper
from src.infrastructure.db.mappers.outbox import OutboxMapper
from src.infrastructure.db.mappers.task import TaskMapper
from src.infrastructure.db.repositories.experiment import SqlAlchemyExperimentRepository
from src.infrastructure.db.repositories.hypothesis import SqlAlchemyHypothesisRepository
from src.infrastructure.db.repositories.initiative import SqlAlchemyInitiativeRepository
from src.infrastructure.db.repositories.task import SqlAlchemyTaskRepository


class SqlAlchemyUnitOfWork:
    def __init__(
        self,
        session: AsyncSession,
        hypothesis_mapper: HypothesisMapper,
        experiment_mapper: ExperimentMapper,
        task_mapper: TaskMapper,
        initiative_mapper: InitiativeMapper,
        outbox_mapper: OutboxMapper,
    ) -> None:
        self.session = session
        self.hypotheses = SqlAlchemyHypothesisRepository(session, hypothesis_mapper)
        self.experiments = SqlAlchemyExperimentRepository(session, experiment_mapper)
        self.tasks = SqlAlchemyTaskRepository(session, task_mapper)
        self.initiatives = SqlAlchemyInitiativeRepository(session, initiative_mapper)
        self._outbox_mapper = outbox_mapper
        self._events: list[DomainEvent] = []

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        if exc_type is not None:
            await self.rollback()

    def collect_events(self, aggregate: AggregateRoot[object]) -> None:
        self._events.extend(aggregate.pull_events())

    async def commit(self) -> None:
        for event in self._events:
            self.session.add(self._outbox_mapper.to_model(event))

        await self.session.commit()
        self._events.clear()

    async def rollback(self) -> None:
        self._events.clear()
        await self.session.rollback()
