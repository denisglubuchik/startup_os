from typing import Protocol
from uuid import UUID

from src.domain.experiment.aggregate import Experiment
from src.domain.hypothesis.aggregate import Hypothesis
from src.domain.initiative.aggregate import Initiative
from src.domain.task.aggregate import Task


class HypothesisRepository(Protocol):
    async def get(self, hypothesis_id: UUID) -> Hypothesis | None:
        pass

    async def save(self, hypothesis: Hypothesis) -> None:
        pass


class ExperimentRepository(Protocol):
    async def get(self, experiment_id: UUID) -> Experiment | None:
        pass

    async def save(self, experiment: Experiment) -> None:
        pass


class TaskRepository(Protocol):
    async def get(self, task_id: UUID) -> Task | None:
        pass

    async def save(self, task: Task) -> None:
        pass


class InitiativeRepository(Protocol):
    async def get(self, initiative_id: UUID) -> Initiative | None:
        pass

    async def save(self, initiative: Initiative) -> None:
        pass
