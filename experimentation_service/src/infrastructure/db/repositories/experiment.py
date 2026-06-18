from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.experiment.aggregate import Experiment
from src.infrastructure.db.mappers.experiment import ExperimentMapper
from src.infrastructure.db.models.experiment import ExperimentModel
from src.infrastructure.db.repositories.base import SqlAlchemyRepository


class SqlAlchemyExperimentRepository(SqlAlchemyRepository[Experiment, ExperimentModel]):
    def __init__(self, session: AsyncSession, mapper: ExperimentMapper) -> None:
        super().__init__(session, ExperimentModel, mapper)
