from collections.abc import Iterator
from uuid import UUID

import grpc
import pytest
import pytest_asyncio
from alembic import command
from alembic.config import Config
from experimentation.v1 import experimentation_service_pb2, experimentation_service_pb2_grpc
from sqlalchemy import text
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from testcontainers.postgres import PostgresContainer

from src.api.grpc.server import create_grpc_server
from src.application.workers.outbox_publisher import OutboxPublisherWorker
from src.core.config import KafkaConfig
from src.infrastructure.db.models.outbox import OutboxMessageModel
from src.infrastructure.db.repositories.outbox import SqlAlchemyOutboxRepository
from src.infrastructure.di import create_container

POSTGRES_DB = "experimentation"
POSTGRES_USER = "startup_os"
POSTGRES_PASSWORD = "startup_os"  # noqa: S105
POSTGRES_PORT = 5432


class FakeEventPublisher:
    def __init__(self) -> None:
        self.messages: list[OutboxMessageModel] = []

    async def publish(self, message: OutboxMessageModel) -> None:
        self.messages.append(message)


@pytest.fixture
def postgres_url(monkeypatch: pytest.MonkeyPatch) -> Iterator[str]:
    with PostgresContainer(
        image="postgres:18-alpine",
        username=POSTGRES_USER,
        password=POSTGRES_PASSWORD,
        dbname=POSTGRES_DB,
        driver="asyncpg",
    ) as postgres:
        host = postgres.get_container_host_ip()
        port = postgres.get_exposed_port(POSTGRES_PORT)
        database_url = postgres.get_connection_url(driver="asyncpg")

        monkeypatch.setenv("DATABASE_URL", database_url)
        monkeypatch.setenv("PG_HOST", host)
        monkeypatch.setenv("PG_PORT", str(port))
        monkeypatch.setenv("PG_DB", POSTGRES_DB)
        monkeypatch.setenv("PG_USER", POSTGRES_USER)
        monkeypatch.setenv("PG_PASS", POSTGRES_PASSWORD)

        alembic_config = Config("alembic.ini")
        command.upgrade(alembic_config, "head")

        yield database_url


@pytest_asyncio.fixture
async def grpc_address(postgres_url: str) -> Iterator[str]:
    container = create_container()
    server = create_grpc_server(container)
    port = server.add_insecure_port("127.0.0.1:0")

    await server.start()

    try:
        yield f"127.0.0.1:{port}"
    finally:
        await server.stop(grace=None)
        await container.close()


@pytest.mark.e2e
async def test_formulate_hypothesis_persists_hypothesis_and_outbox_event(
    grpc_address: str,
    postgres_url: str,
) -> None:
    workspace_id = "11111111-1111-1111-1111-111111111111"
    created_by = "22222222-2222-2222-2222-222222222222"

    async with grpc.aio.insecure_channel(grpc_address) as channel:
        stub = experimentation_service_pb2_grpc.ExperimentationServiceStub(channel)
        response = await stub.FormulateHypothesis(
            experimentation_service_pb2.FormulateHypothesisRequest(
                workspace_id=workspace_id,
                statement="Founders will link experiments to measurable goals.",
                expected_outcome="Most founders can identify the metric being tested.",
                created_by=created_by,
                confidence="medium",
                priority="high",
            )
        )

    assert UUID(response.hypothesis_id)
    assert response.workspace_id == workspace_id
    assert response.status == "draft"

    engine = create_async_engine(postgres_url)
    try:
        async with engine.connect() as connection:
            hypothesis = (
                await connection.execute(
                    text(
                        """
                        select id, workspace_id, statement, status, confidence, priority
                        from hypotheses
                        where id = :hypothesis_id
                        """
                    ),
                    {"hypothesis_id": UUID(response.hypothesis_id)},
                )
            ).mappings().one()

            outbox_message = (
                await connection.execute(
                    text(
                        """
                        select aggregate_id, workspace_id, event_type, payload
                        from outbox_messages
                        where aggregate_id = :hypothesis_id
                        """
                    ),
                    {"hypothesis_id": UUID(response.hypothesis_id)},
                )
            ).mappings().one()
    finally:
        await engine.dispose()

    assert str(hypothesis["workspace_id"]) == workspace_id
    assert hypothesis["statement"] == "Founders will link experiments to measurable goals."
    assert hypothesis["status"] == "draft"
    assert hypothesis["confidence"] == "medium"
    assert hypothesis["priority"] == "high"

    assert str(outbox_message["aggregate_id"]) == response.hypothesis_id
    assert str(outbox_message["workspace_id"]) == workspace_id
    assert outbox_message["event_type"] == "HypothesisFormulated"
    assert outbox_message["payload"]["statement"] == (
        "Founders will link experiments to measurable goals."
    )


@pytest.mark.e2e
async def test_outbox_worker_publishes_and_marks_message_published(
    grpc_address: str,
    postgres_url: str,
) -> None:
    workspace_id = "11111111-1111-1111-1111-111111111111"
    created_by = "22222222-2222-2222-2222-222222222222"

    async with grpc.aio.insecure_channel(grpc_address) as channel:
        stub = experimentation_service_pb2_grpc.ExperimentationServiceStub(channel)
        response = await stub.FormulateHypothesis(
            experimentation_service_pb2.FormulateHypothesisRequest(
                workspace_id=workspace_id,
                statement="Outbox publisher should publish durable messages.",
                expected_outcome="The publisher marks the outbox row as published.",
                created_by=created_by,
                confidence="medium",
                priority="high",
            )
        )

    engine = create_async_engine(postgres_url)
    publisher = FakeEventPublisher()
    try:
        session_factory = async_sessionmaker(engine, expire_on_commit=False)
        async with session_factory() as session:
            worker = OutboxPublisherWorker(
                SqlAlchemyOutboxRepository(session),
                publisher,
                KafkaConfig(KAFKA_OUTBOX_BATCH_SIZE=10),
            )

            published_count = await worker.run_once()

        async with engine.connect() as connection:
            outbox_message = (
                await connection.execute(
                    text(
                        """
                        select aggregate_id, event_type, published_at, locked_at, publish_error
                        from outbox_messages
                        where aggregate_id = :hypothesis_id
                        """
                    ),
                    {"hypothesis_id": UUID(response.hypothesis_id)},
                )
            ).mappings().one()
    finally:
        await engine.dispose()

    assert published_count == 1
    assert len(publisher.messages) == 1
    assert str(publisher.messages[0].aggregate_id) == response.hypothesis_id
    assert publisher.messages[0].event_type == "HypothesisFormulated"
    assert str(outbox_message["aggregate_id"]) == response.hypothesis_id
    assert outbox_message["event_type"] == "HypothesisFormulated"
    assert outbox_message["published_at"] is not None
    assert outbox_message["locked_at"] is None
    assert outbox_message["publish_error"] is None
