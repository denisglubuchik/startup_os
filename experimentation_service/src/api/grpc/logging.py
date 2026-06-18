from collections.abc import Awaitable, Callable
from typing import Any

import grpc

from src.core.logging_context import bind_log_context, new_context_id

type LogContext = dict[str, str | None]


class LoggingContextInterceptor(grpc.aio.ServerInterceptor):
    async def intercept_service(
        self,
        continuation: Callable[[grpc.HandlerCallDetails], Awaitable[grpc.RpcMethodHandler]],
        handler_call_details: grpc.HandlerCallDetails,
    ) -> grpc.RpcMethodHandler:
        log_context = self._log_context(handler_call_details)
        handler = await continuation(handler_call_details)
        return self._wrap_handler(handler, log_context)

    def _log_context(self, handler_call_details: grpc.HandlerCallDetails) -> LogContext:
        metadata = dict(handler_call_details.invocation_metadata or ())
        request_id = metadata.get("x-request-id") or new_context_id()
        correlation_id = metadata.get("x-correlation-id") or request_id

        return {
            "correlation_id": correlation_id,
            "request_id": request_id,
            "causation_id": metadata.get("x-causation-id"),
            "workspace_id": metadata.get("x-workspace-id"),
            "grpc_method": handler_call_details.method,
        }

    def _wrap_handler(
        self,
        handler: grpc.RpcMethodHandler,
        log_context: LogContext,
    ) -> grpc.RpcMethodHandler:
        if handler.request_streaming and handler.response_streaming:
            return grpc.stream_stream_rpc_method_handler(
                self._wrap_stream_stream(handler.stream_stream, log_context),
                request_deserializer=handler.request_deserializer,
                response_serializer=handler.response_serializer,
            )

        if handler.request_streaming:
            return grpc.stream_unary_rpc_method_handler(
                self._wrap_stream_unary(handler.stream_unary, log_context),
                request_deserializer=handler.request_deserializer,
                response_serializer=handler.response_serializer,
            )

        if handler.response_streaming:
            return grpc.unary_stream_rpc_method_handler(
                self._wrap_unary_stream(handler.unary_stream, log_context),
                request_deserializer=handler.request_deserializer,
                response_serializer=handler.response_serializer,
            )

        return grpc.unary_unary_rpc_method_handler(
            self._wrap_unary_unary(handler.unary_unary, log_context),
            request_deserializer=handler.request_deserializer,
            response_serializer=handler.response_serializer,
        )

    def _wrap_unary_unary(self, behavior, log_context: LogContext):
        async def wrapped(request: Any, context: grpc.aio.ServicerContext) -> Any:
            with bind_log_context(**log_context):
                return await behavior(request, context)

        return wrapped

    def _wrap_unary_stream(self, behavior, log_context: LogContext):
        async def wrapped(request: Any, context: grpc.aio.ServicerContext):
            with bind_log_context(**log_context):
                async for response in behavior(request, context):
                    yield response

        return wrapped

    def _wrap_stream_unary(self, behavior, log_context: LogContext):
        async def wrapped(request_iterator: Any, context: grpc.aio.ServicerContext) -> Any:
            with bind_log_context(**log_context):
                return await behavior(request_iterator, context)

        return wrapped

    def _wrap_stream_stream(self, behavior, log_context: LogContext):
        async def wrapped(request_iterator: Any, context: grpc.aio.ServicerContext):
            with bind_log_context(**log_context):
                async for response in behavior(request_iterator, context):
                    yield response

        return wrapped
