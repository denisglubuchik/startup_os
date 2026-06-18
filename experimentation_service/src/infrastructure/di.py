from collections.abc import AsyncIterable

from dishka import Provider, Scope, make_async_container, provide
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.application.commands.hypothesis import FormulateHypothesisUseCase
from src.application.interfaces.repositories import (
    ExperimentRepository,
    HypothesisRepository,
    InitiativeRepository,
    TaskRepository,
)
from src.application.interfaces.unit_of_work import UnitOfWork
from src.core.config import AppConfig, DBConfig, GrpcConfig
from src.infrastructure.db.mappers.experiment import ExperimentMapper
from src.infrastructure.db.mappers.hypothesis import HypothesisMapper
from src.infrastructure.db.mappers.initiative import InitiativeMapper
from src.infrastructure.db.mappers.outbox import OutboxMapper
from src.infrastructure.db.mappers.task import TaskMapper
from src.infrastructure.db.repositories.experiment import SqlAlchemyExperimentRepository
from src.infrastructure.db.repositories.hypothesis import SqlAlchemyHypothesisRepository
from src.infrastructure.db.repositories.initiative import SqlAlchemyInitiativeRepository
from src.infrastructure.db.repositories.task import SqlAlchemyTaskRepository
from src.infrastructure.db.unit_of_work import SqlAlchemyUnitOfWork


class ConfigProvider(Provider):
    @provide(scope=Scope.APP)
    def app_config(self) -> AppConfig:
        return AppConfig()

    @provide(scope=Scope.APP)
    def db_config(self) -> DBConfig:
        return DBConfig()

    @provide(scope=Scope.APP)
    def grpc_config(self) -> GrpcConfig:
        return GrpcConfig()


class InfrastructureProvider(Provider):
    @provide(scope=Scope.APP)
    def session_factory(
        self,
        config: DBConfig,
    ) -> async_sessionmaker[AsyncSession]:
        engine = create_async_engine(config.database_url)
        return async_sessionmaker(engine, expire_on_commit=False)

    @provide(scope=Scope.REQUEST)
    async def session(
        self,
        session_factory: async_sessionmaker[AsyncSession],
    ) -> AsyncIterable[AsyncSession]:
        async with session_factory() as session:
            yield session

    hypothesis_mapper = provide(HypothesisMapper, scope=Scope.APP)
    experiment_mapper = provide(ExperimentMapper, scope=Scope.APP)
    task_mapper = provide(TaskMapper, scope=Scope.APP)
    initiative_mapper = provide(InitiativeMapper, scope=Scope.APP)
    outbox_mapper = provide(OutboxMapper, scope=Scope.APP)

    @provide(scope=Scope.REQUEST)
    def hypothesis_repository(
        self,
        session: AsyncSession,
        mapper: HypothesisMapper,
    ) -> HypothesisRepository:
        return SqlAlchemyHypothesisRepository(session, mapper)

    @provide(scope=Scope.REQUEST)
    def experiment_repository(
        self,
        session: AsyncSession,
        mapper: ExperimentMapper,
    ) -> ExperimentRepository:
        return SqlAlchemyExperimentRepository(session, mapper)

    @provide(scope=Scope.REQUEST)
    def task_repository(
        self,
        session: AsyncSession,
        mapper: TaskMapper,
    ) -> TaskRepository:
        return SqlAlchemyTaskRepository(session, mapper)

    @provide(scope=Scope.REQUEST)
    def initiative_repository(
        self,
        session: AsyncSession,
        mapper: InitiativeMapper,
    ) -> InitiativeRepository:
        return SqlAlchemyInitiativeRepository(session, mapper)

    @provide(scope=Scope.REQUEST)
    def unit_of_work(
        self,
        session: AsyncSession,
        hypothesis_mapper: HypothesisMapper,
        experiment_mapper: ExperimentMapper,
        task_mapper: TaskMapper,
        initiative_mapper: InitiativeMapper,
        outbox_mapper: OutboxMapper,
    ) -> UnitOfWork:
        return SqlAlchemyUnitOfWork(
            session=session,
            hypothesis_mapper=hypothesis_mapper,
            experiment_mapper=experiment_mapper,
            task_mapper=task_mapper,
            initiative_mapper=initiative_mapper,
            outbox_mapper=outbox_mapper,
        )

    @provide(scope=Scope.REQUEST)
    def formulate_hypothesis_use_case(
        self,
        uow: UnitOfWork,
    ) -> FormulateHypothesisUseCase:
        return FormulateHypothesisUseCase(uow)


def create_container():
    return make_async_container(ConfigProvider(), InfrastructureProvider())
