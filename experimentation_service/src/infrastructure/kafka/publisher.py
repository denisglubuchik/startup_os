import json
from typing import Any

from aiokafka import AIOKafkaProducer

from src.infrastructure.db.models.outbox import OutboxMessageModel

type KafkaHeaders = list[tuple[str, bytes]]


class KafkaEventPublisher:
    def __init__(self, producer: AIOKafkaProducer, topic: str) -> None:
        self._producer = producer
        self._topic = topic

    async def start(self) -> None:
        await self._producer.start()

    async def stop(self) -> None:
        await self._producer.stop()

    async def publish(self, message: OutboxMessageModel) -> None:
        await self._producer.send_and_wait(
            self._topic,
            key=str(message.aggregate_id).encode(),
            value=_json_bytes(_envelope(message)),
            headers=_headers(message),
        )


def _envelope(message: OutboxMessageModel) -> dict[str, Any]:
    return {
        "message_id": str(message.id),
        "event_type": message.event_type,
        "aggregate_id": str(message.aggregate_id),
        "workspace_id": str(message.workspace_id) if message.workspace_id else None,
        "occurred_at": message.occurred_at.isoformat(),
        "payload": message.payload,
    }


def _headers(message: OutboxMessageModel) -> KafkaHeaders:
    headers: KafkaHeaders = [
        ("message-id", str(message.id).encode()),
        ("event-type", message.event_type.encode()),
        ("aggregate-id", str(message.aggregate_id).encode()),
    ]
    if message.workspace_id:
        headers.append(("workspace-id", str(message.workspace_id).encode()))
    return headers


def _json_bytes(payload: dict[str, Any]) -> bytes:
    return json.dumps(payload, separators=(",", ":"), sort_keys=True).encode()
