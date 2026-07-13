from collections.abc import Iterator
from contextlib import contextmanager
from contextvars import ContextVar, Token
from uuid import uuid4

type LogContextValue = str | None

_correlation_id: ContextVar[LogContextValue] = ContextVar("correlation_id", default=None)
_request_id: ContextVar[LogContextValue] = ContextVar("request_id", default=None)
_causation_id: ContextVar[LogContextValue] = ContextVar("causation_id", default=None)
_workspace_id: ContextVar[LogContextValue] = ContextVar("workspace_id", default=None)
_grpc_method: ContextVar[LogContextValue] = ContextVar("grpc_method", default=None)

_FIELDS = {
    "correlation_id": _correlation_id,
    "request_id": _request_id,
    "causation_id": _causation_id,
    "workspace_id": _workspace_id,
    "grpc_method": _grpc_method,
}


def current_log_context() -> dict[str, LogContextValue]:
    return {name: field.get() for name, field in _FIELDS.items()}


def new_context_id() -> str:
    return str(uuid4())


@contextmanager
def bind_log_context(**values: LogContextValue) -> Iterator[None]:
    tokens: list[tuple[ContextVar[LogContextValue], Token[LogContextValue]]] = []

    try:
        for name, value in values.items():
            if name not in _FIELDS:
                msg = f"Unknown log context field: {name}"
                raise ValueError(msg)
            tokens.append((_FIELDS[name], _FIELDS[name].set(value)))
        yield
    finally:
        for field, token in reversed(tokens):
            field.reset(token)
