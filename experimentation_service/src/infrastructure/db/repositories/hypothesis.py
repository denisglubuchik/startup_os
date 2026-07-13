from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.hypothesis.aggregate import Hypothesis
from src.infrastructure.db.mappers.hypothesis import HypothesisMapper
from src.infrastructure.db.models.hypothesis import HypothesisModel
from src.infrastructure.db.repositories.base import SqlAlchemyRepository


class SqlAlchemyHypothesisRepository(SqlAlchemyRepository[Hypothesis, HypothesisModel]):
    def __init__(self, session: AsyncSession, mapper: HypothesisMapper) -> None:
        super().__init__(session, HypothesisModel, mapper)
