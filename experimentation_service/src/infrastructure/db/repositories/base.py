from typing import Protocol, TypeVar
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

AggregateT = TypeVar("AggregateT")
ModelT = TypeVar("ModelT")


class Mapper(Protocol[AggregateT, ModelT]):
    def to_domain(self, model: ModelT) -> AggregateT:
        pass

    def to_model(self, aggregate: AggregateT, model: ModelT | None = None) -> ModelT:
        pass


class SqlAlchemyRepository[AggregateT, ModelT]:
    def __init__(
        self,
        session: AsyncSession,
        model_type: type[ModelT],
        mapper: Mapper[AggregateT, ModelT],
    ) -> None:
        self._session = session
        self._model_type = model_type
        self._mapper = mapper

    async def get(self, aggregate_id: UUID) -> AggregateT | None:
        model = await self._session.get(self._model_type, aggregate_id)
        if model is None:
            return None
        return self._mapper.to_domain(model)

    async def save(self, aggregate: AggregateT) -> None:
        model = await self._session.get(self._model_type, aggregate.id)
        model = self._mapper.to_model(aggregate, model)
        self._session.add(model)
