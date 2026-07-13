from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.task.aggregate import Task
from src.infrastructure.db.mappers.task import TaskMapper
from src.infrastructure.db.models.task import TaskModel
from src.infrastructure.db.repositories.base import SqlAlchemyRepository


class SqlAlchemyTaskRepository(SqlAlchemyRepository[Task, TaskModel]):
    def __init__(self, session: AsyncSession, mapper: TaskMapper) -> None:
        super().__init__(session, TaskModel, mapper)
