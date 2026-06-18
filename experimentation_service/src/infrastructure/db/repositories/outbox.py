from datetime import UTC, datetime, timedelta
from uuid import UUID

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.db.models.outbox import OutboxMessageModel


class SqlAlchemyOutboxRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def claim_batch(
        self,
        *,
        limit: int,
        lock_timeout: timedelta,
        max_attempts: int,
    ) -> list[OutboxMessageModel]:
        now = datetime.now(UTC)
        stale_lock_before = now - lock_timeout
        statement = (
            select(OutboxMessageModel)
            .where(
                OutboxMessageModel.published_at.is_(None),
                OutboxMessageModel.attempt_count < max_attempts,
                or_(
                    OutboxMessageModel.locked_at.is_(None),
                    OutboxMessageModel.locked_at < stale_lock_before,
                ),
                or_(
                    OutboxMessageModel.next_attempt_at.is_(None),
                    OutboxMessageModel.next_attempt_at <= now,
                ),
            )
            .order_by(OutboxMessageModel.created_at)
            .limit(limit)
            .with_for_update(skip_locked=True)
        )
        messages = list((await self._session.scalars(statement)).all())

        for message in messages:
            message.locked_at = now

        await self._session.commit()
        return messages

    async def mark_published(self, message_id: UUID) -> None:
        message = await self._session.get(OutboxMessageModel, message_id)
        if message is None:
            return

        message.published_at = datetime.now(UTC)
        message.locked_at = None
        message.next_attempt_at = None
        message.publish_error = None
        await self._session.commit()

    async def mark_failed(
        self,
        message_id: UUID,
        *,
        error: str,
        retry_delay: timedelta,
        max_attempts: int,
    ) -> None:
        message = await self._session.get(OutboxMessageModel, message_id)
        if message is None:
            return

        now = datetime.now(UTC)
        message.attempt_count += 1
        message.locked_at = None
        message.publish_error = error[:4000]
        message.next_attempt_at = (
            now + retry_delay if message.attempt_count < max_attempts else None
        )
        await self._session.commit()
