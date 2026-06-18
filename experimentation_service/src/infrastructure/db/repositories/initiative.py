from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.initiative.aggregate import Initiative
from src.infrastructure.db.mappers.initiative import InitiativeMapper
from src.infrastructure.db.models.initiative import InitiativeModel
from src.infrastructure.db.repositories.base import SqlAlchemyRepository


class SqlAlchemyInitiativeRepository(SqlAlchemyRepository[Initiative, InitiativeModel]):
    def __init__(self, session: AsyncSession, mapper: InitiativeMapper) -> None:
        super().__init__(session, InitiativeModel, mapper)
