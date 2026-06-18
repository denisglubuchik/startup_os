import asyncio

from src.api.grpc.server import serve
from src.core.config import AppConfig, LoggingConfig
from src.core.logging import configure_logging


def main() -> None:
    configure_logging(LoggingConfig(), AppConfig())
    asyncio.run(serve())


if __name__ == "__main__":
    main()
