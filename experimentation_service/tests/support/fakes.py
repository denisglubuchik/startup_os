from dataclasses import dataclass, field
from uuid import UUID

from src.domain.experiment.aggregate import Experiment
from src.domain.hypothesis.aggregate import Hypothesis
from src.domain.initiative.aggregate import Initiative
from src.domain.shared.aggregate import AggregateRoot
from src.domain.shared.events import DomainEvent
from src.domain.task.aggregate import Task


@dataclass
class FakeRepository[AggregateT]:
    saved: list[AggregateT] = field(default_factory=list)

    async def get(self, aggregate_id: UUID) -> AggregateT | None:
        return next(
            (aggregate for aggregate in self.saved if aggregate.id == aggregate_id),
            None,
        )

    async def save(self, aggregate: AggregateT) -> None:
        existing = await self.get(aggregate.id)
        if existing is not None:
            self.saved.remove(existing)
        self.saved.append(aggregate)


@dataclass
class FakeUnitOfWork:
    hypotheses: FakeRepository[Hypothesis] = field(default_factory=FakeRepository)
    experiments: FakeRepository[Experiment] = field(default_factory=FakeRepository)
    tasks: FakeRepository[Task] = field(default_factory=FakeRepository)
    initiatives: FakeRepository[Initiative] = field(default_factory=FakeRepository)
    events: list[DomainEvent] = field(default_factory=list)
    committed: bool = False
    rolled_back: bool = False

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        if exc_type is not None:
            await self.rollback()

    def collect_events(self, aggregate: AggregateRoot[object]) -> None:
        self.events.extend(aggregate.pull_events())

    async def commit(self) -> None:
        self.committed = True

    async def rollback(self) -> None:
        self.rolled_back = True
