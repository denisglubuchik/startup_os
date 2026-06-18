from dataclasses import asdict
from datetime import datetime
from enum import StrEnum
from typing import Any
from uuid import UUID

from src.domain.shared.events import DomainEvent
from src.infrastructure.db.models.outbox import OutboxMessageModel


class OutboxMapper:
    def to_model(self, event: DomainEvent) -> OutboxMessageModel:
        return OutboxMessageModel(
            id=event.event_id,
            aggregate_id=self._aggregate_id(event),
            workspace_id=self._workspace_id(event),
            event_type=event.event_type,
            payload=self._payload(event),
            occurred_at=event.occurred_at,
        )

    def _aggregate_id(self, event: DomainEvent) -> UUID:
        for attribute_name in ("hypothesis_id", "experiment_id", "task_id", "initiative_id"):
            value = getattr(event, attribute_name, None)
            if isinstance(value, UUID):
                return value

        msg = f"Event {event.event_type} does not expose an aggregate id"
        raise ValueError(msg)

    def _workspace_id(self, event: DomainEvent) -> UUID | None:
        value = getattr(event, "workspace_id", None)
        return value if isinstance(value, UUID) else None

    def _payload(self, event: DomainEvent) -> dict[str, Any]:
        return self._dump_value(asdict(event))

    def _dump_value(self, value: Any) -> Any:
        if isinstance(value, UUID):
            return str(value)
        if isinstance(value, datetime):
            return value.isoformat()
        if isinstance(value, StrEnum):
            return value.value
        if isinstance(value, dict):
            return {key: self._dump_value(item) for key, item in value.items()}
        if isinstance(value, list | tuple | set):
            return [self._dump_value(item) for item in value]
        return value
