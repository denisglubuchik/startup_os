import logging
from datetime import timedelta
from typing import Protocol
from uuid import UUID

from src.core.config import KafkaConfig
from src.core.logging_context import bind_log_context

logger = logging.getLogger(__name__)


class OutboxMessage(Protocol):
    id: UUID
    workspace_id: UUID | None


class OutboxRepository(Protocol):
    async def claim_batch(
        self,
        *,
        limit: int,
        lock_timeout: timedelta,
        max_attempts: int,
    ) -> list[OutboxMessage]: ...

    async def mark_published(self, message_id: UUID) -> None: ...

    async def mark_failed(
        self,
        message_id: UUID,
        *,
        error: str,
        retry_delay: timedelta,
        max_attempts: int,
    ) -> None: ...


class EventPublisher(Protocol):
    async def publish(self, message: OutboxMessage) -> None: ...


class OutboxPublisherWorker:
    def __init__(
        self,
        repository: OutboxRepository,
        publisher: EventPublisher,
        config: KafkaConfig,
    ) -> None:
        self._repository = repository
        self._publisher = publisher
        self._config = config

    async def run_once(self) -> int:
        messages = await self._repository.claim_batch(
            limit=self._config.KAFKA_OUTBOX_BATCH_SIZE,
            lock_timeout=timedelta(seconds=self._config.KAFKA_OUTBOX_LOCK_TIMEOUT_SECONDS),
            max_attempts=self._config.KAFKA_OUTBOX_MAX_ATTEMPTS,
        )

        for message in messages:
            workspace_id = str(message.workspace_id) if message.workspace_id else None
            with bind_log_context(workspace_id=workspace_id, causation_id=str(message.id)):
                try:
                    await self._publisher.publish(message)
                except Exception as exc:
                    logger.exception(
                        "Failed to publish outbox message",
                        extra={"outbox_message_id": str(message.id)},
                    )
                    await self._repository.mark_failed(
                        message.id,
                        error=str(exc),
                        retry_delay=timedelta(
                            seconds=self._config.KAFKA_OUTBOX_RETRY_DELAY_SECONDS
                        ),
                        max_attempts=self._config.KAFKA_OUTBOX_MAX_ATTEMPTS,
                    )
                else:
                    await self._repository.mark_published(message.id)
                    logger.info(
                        "Published outbox message",
                        extra={"outbox_message_id": str(message.id)},
                    )

        return len(messages)
