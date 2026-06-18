import asyncio

from dishka import Scope

from src.application.workers.outbox_publisher import OutboxPublisherWorker
from src.core.config import AppConfig, KafkaConfig, LoggingConfig
from src.core.logging import configure_logging
from src.infrastructure.di import create_worker_container


async def run_forever() -> None:
    container = create_worker_container()
    try:
        app_config = await container.get(AppConfig)
        logging_config = await container.get(LoggingConfig)
        kafka_config = await container.get(KafkaConfig)
        configure_logging(logging_config, app_config)

        while True:
            async with container(scope=Scope.REQUEST) as request_container:
                worker = await request_container.get(OutboxPublisherWorker)
                published_count = await worker.run_once()

            if published_count == 0:
                await asyncio.sleep(kafka_config.KAFKA_OUTBOX_POLL_INTERVAL_SECONDS)
    finally:
        await container.close()


def main() -> None:
    asyncio.run(run_forever())


if __name__ == "__main__":
    main()
