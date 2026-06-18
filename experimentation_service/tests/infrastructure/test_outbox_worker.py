from dataclasses import dataclass
from uuid import UUID

from src.application.workers.outbox_publisher import OutboxPublisherWorker
from src.core.config import KafkaConfig


@dataclass
class OutboxMessage:
    id: UUID
    workspace_id: UUID | None = None


class FakeRepository:
    def __init__(self, messages: list[OutboxMessage]) -> None:
        self.messages = messages
        self.published: list[UUID] = []
        self.failed: list[tuple[UUID, str]] = []

    async def claim_batch(self, *, limit, lock_timeout, max_attempts):
        return self.messages[:limit]

    async def mark_published(self, message_id: UUID) -> None:
        self.published.append(message_id)

    async def mark_failed(self, message_id: UUID, *, error, retry_delay, max_attempts) -> None:
        self.failed.append((message_id, error))


class FakePublisher:
    def __init__(self, error: Exception | None = None) -> None:
        self.error = error
        self.published: list[OutboxMessage] = []

    async def publish(self, message: OutboxMessage) -> None:
        if self.error:
            raise self.error
        self.published.append(message)


async def test_outbox_worker_marks_message_published() -> None:
    message = OutboxMessage(UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"))
    repository = FakeRepository([message])
    publisher = FakePublisher()

    worker = OutboxPublisherWorker(repository, publisher, KafkaConfig())
    count = await worker.run_once()

    assert count == 1
    assert publisher.published == [message]
    assert repository.published == [message.id]
    assert repository.failed == []


async def test_outbox_worker_marks_message_failed_for_retry() -> None:
    message = OutboxMessage(UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"))
    repository = FakeRepository([message])
    publisher = FakePublisher(RuntimeError("broker unavailable"))

    worker = OutboxPublisherWorker(repository, publisher, KafkaConfig())
    count = await worker.run_once()

    assert count == 1
    assert repository.published == []
    assert repository.failed == [(message.id, "broker unavailable")]
