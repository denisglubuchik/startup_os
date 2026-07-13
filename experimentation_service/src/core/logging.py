import json
import logging
import logging.config
from datetime import UTC, datetime
from typing import Any

from src.core.config import AppConfig, LoggingConfig
from src.core.logging_context import current_log_context


class ContextualLogFilter(logging.Filter):
    def __init__(self, service_name: str) -> None:
        super().__init__()
        self._service_name = service_name

    def filter(self, record: logging.LogRecord) -> bool:
        record.service_name = self._service_name
        for name, value in current_log_context().items():
            setattr(record, name, value or "-")
        return True


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "timestamp": datetime.fromtimestamp(record.created, UTC).isoformat(),
            "level": record.levelname,
            "service": getattr(record, "service_name", "experimentation_service"),
            "logger": record.name,
            "message": record.getMessage(),
        }
        payload.update(
            {name: value for name, value in current_log_context().items() if value is not None}
        )

        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)

        return json.dumps(payload, ensure_ascii=False)


def configure_logging(
    logging_config: LoggingConfig,
    app_config: AppConfig | None = None,
) -> None:
    level = _normalize_log_level(logging_config.LOG_LEVEL)
    formatter_name = "json" if logging_config.LOG_FORMAT == "json" else "console"
    app_name = app_config.APP_NAME if app_config else "experimentation_service"

    logging.config.dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "console": {
                    "format": (
                        "%(asctime)s %(levelname)s [%(service_name)s] [%(name)s] "
                        "correlation_id=%(correlation_id)s request_id=%(request_id)s "
                        "workspace_id=%(workspace_id)s grpc_method=%(grpc_method)s %(message)s"
                    ),
                },
                "json": {
                    "()": JsonFormatter,
                },
            },
            "filters": {
                "context": {
                    "()": ContextualLogFilter,
                    "service_name": app_name,
                },
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "level": level,
                    "formatter": formatter_name,
                    "filters": ["context"],
                },
            },
            "root": {
                "level": level,
                "handlers": ["console"],
            },
            "loggers": {
                app_name: {
                    "level": level,
                    "propagate": True,
                },
                "grpc": {
                    "level": level,
                    "propagate": True,
                },
                "sqlalchemy.engine": {
                    "level": "WARNING",
                    "propagate": True,
                },
            },
        }
    )


def _normalize_log_level(level: str) -> str:
    normalized = level.upper()
    if normalized not in logging.getLevelNamesMapping():
        msg = f"Invalid log level: {level}"
        raise ValueError(msg)
    return normalized
