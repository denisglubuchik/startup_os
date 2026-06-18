import json
import logging
from dataclasses import dataclass

import grpc
import pytest

from src.api.grpc.logging import LoggingContextInterceptor
from src.core.config import AppConfig, LoggingConfig
from src.core.logging_context import bind_log_context, current_log_context
from src.core.logging import JsonFormatter, configure_logging


@dataclass(frozen=True)
class HandlerCallDetails:
    method: str
    invocation_metadata: tuple[tuple[str, str], ...]


def test_configure_logging_sets_root_level() -> None:
    configure_logging(LoggingConfig(LOG_LEVEL="DEBUG"), AppConfig())

    assert logging.getLogger().level == logging.DEBUG


def test_configure_logging_rejects_invalid_level() -> None:
    with pytest.raises(ValueError, match="Invalid log level"):
        configure_logging(LoggingConfig(LOG_LEVEL="verbose"), AppConfig())


def test_json_formatter_outputs_structured_log_record() -> None:
    formatter = JsonFormatter()
    record = logging.LogRecord(
        name="experimentation_service.test",
        level=logging.INFO,
        pathname=__file__,
        lineno=1,
        msg="service started",
        args=(),
        exc_info=None,
    )

    payload = json.loads(formatter.format(record))

    assert payload["level"] == "INFO"
    assert payload["logger"] == "experimentation_service.test"
    assert payload["message"] == "service started"
    assert "timestamp" in payload


def test_log_context_is_scoped() -> None:
    assert current_log_context()["correlation_id"] is None

    with bind_log_context(
        correlation_id="correlation-1",
        request_id="request-1",
        workspace_id="workspace-1",
    ):
        context = current_log_context()

        assert context["correlation_id"] == "correlation-1"
        assert context["request_id"] == "request-1"
        assert context["workspace_id"] == "workspace-1"

    assert current_log_context()["correlation_id"] is None


def test_json_formatter_includes_bound_context() -> None:
    formatter = JsonFormatter()
    record = logging.LogRecord(
        name="experimentation_service.test",
        level=logging.INFO,
        pathname=__file__,
        lineno=1,
        msg="handled request",
        args=(),
        exc_info=None,
    )

    with bind_log_context(correlation_id="correlation-1", grpc_method="/service/Method"):
        payload = json.loads(formatter.format(record))

    assert payload["correlation_id"] == "correlation-1"
    assert payload["grpc_method"] == "/service/Method"


async def test_grpc_interceptor_binds_context_around_rpc_handler() -> None:
    observed_context = None
    interceptor = LoggingContextInterceptor()

    async def behavior(request, context):
        nonlocal observed_context
        observed_context = current_log_context()
        return "response"

    async def continuation(handler_call_details):
        return grpc.unary_unary_rpc_method_handler(behavior)

    handler = await interceptor.intercept_service(
        continuation,
        HandlerCallDetails(
            method="/startupos.experimentation.v1.ExperimentationService/FormulateHypothesis",
            invocation_metadata=(
                ("x-correlation-id", "correlation-1"),
                ("x-request-id", "request-1"),
                ("x-causation-id", "causation-1"),
            ),
        ),
    )

    assert current_log_context()["correlation_id"] is None

    response = await handler.unary_unary("request", None)

    assert response == "response"
    assert observed_context["correlation_id"] == "correlation-1"
    assert observed_context["request_id"] == "request-1"
    assert observed_context["causation_id"] == "causation-1"
    assert observed_context["grpc_method"] == (
        "/startupos.experimentation.v1.ExperimentationService/FormulateHypothesis"
    )
    assert current_log_context()["correlation_id"] is None
