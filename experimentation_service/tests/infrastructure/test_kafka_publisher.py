from datetime import UTC, datetime
from uuid import UUID

from src.infrastructure.db.models.outbox import OutboxMessageModel
from src.infrastructure.kafka.publisher import KafkaEventPublisher


class FakeProducer:
    def __init__(self) -> None:
        self.sent: list[dict] = []
        self.started = False
        self.stopped = False

    async def start(self) -> None:
        self.started = True

    async def stop(self) -> None:
        self.stopped = True

    async def send_and_wait(self, topic, value, key, headers) -> None:
        self.sent.append(
            {
                "topic": topic,
                "value": value,
                "key": key,
                "headers": headers,
            }
        )


async def test_kafka_publisher_sends_outbox_envelope_and_headers() -> None:
    producer = FakeProducer()
    publisher = KafkaEventPublisher(producer, "experimentation.events")
    message = OutboxMessageModel(
        id=UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"),
        aggregate_id=UUID("bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb"),
        workspace_id=UUID("cccccccc-cccc-cccc-cccc-cccccccccccc"),
        event_type="HypothesisFormulated",
        payload={"statement": "Ship Kafka outbox publisher"},
        occurred_at=datetime(2026, 6, 18, 20, 0, tzinfo=UTC),
    )

    await publisher.start()
    await publisher.publish(message)
    await publisher.stop()

    assert producer.started is True
    assert producer.stopped is True
    assert producer.sent == [
        {
            "topic": "experimentation.events",
            "key": b"bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb",
            "value": (
                b'{"aggregate_id":"bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb",'
                b'"event_type":"HypothesisFormulated",'
                b'"message_id":"aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",'
                b'"occurred_at":"2026-06-18T20:00:00+00:00",'
                b'"payload":{"statement":"Ship Kafka outbox publisher"},'
                b'"workspace_id":"cccccccc-cccc-cccc-cccc-cccccccccccc"}'
            ),
            "headers": [
                ("message-id", b"aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"),
                ("event-type", b"HypothesisFormulated"),
                ("aggregate-id", b"bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb"),
                ("workspace-id", b"cccccccc-cccc-cccc-cccc-cccccccccccc"),
            ],
        }
    ]
