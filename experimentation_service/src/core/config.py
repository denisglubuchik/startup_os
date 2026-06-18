from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


class AppConfig(Settings):
    APP_NAME: str = "experimentation_service"


class GrpcConfig(Settings):
    GRPC_HOST: str = "0.0.0.0"  # noqa: S104
    GRPC_PORT: int = 50051

    @property
    def address(self) -> str:
        return f"{self.GRPC_HOST}:{self.GRPC_PORT}"


class DBConfig(Settings):
    PG_HOST: str = "localhost"
    PG_PORT: int = 5432
    PG_DB: str
    PG_USER: str
    PG_PASS: str

    @property
    def database_url(self) -> str:
        return f"postgresql+asyncpg://{self.PG_USER}:{self.PG_PASS}@{self.PG_HOST}:{self.PG_PORT}/{self.PG_DB}"


class RedisConfig(Settings):
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: str = ""
    REDIS_USER: str = ""
    REDIS_DB: int = 0
    APP_REDIS_PREFIX: str = "experimentation"


class LoggingConfig(Settings):
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: Literal["console", "json"] = "console"


class KafkaConfig(Settings):
    KAFKA_BOOTSTRAP_SERVERS: str = "localhost:9092"
    KAFKA_EXPERIMENTATION_EVENTS_TOPIC: str = "experimentation.events"
    KAFKA_OUTBOX_BATCH_SIZE: int = 100
    KAFKA_OUTBOX_POLL_INTERVAL_SECONDS: float = 1.0
    KAFKA_OUTBOX_RETRY_DELAY_SECONDS: float = 10.0
    KAFKA_OUTBOX_LOCK_TIMEOUT_SECONDS: float = 300.0
    KAFKA_OUTBOX_MAX_ATTEMPTS: int = 10
