import sys
from importlib import import_module
from pathlib import Path
from uuid import UUID

from dishka import AsyncContainer, Scope

from src.api.grpc.errors import abort_application_error, abort_invalid_argument
from src.application.commands.hypothesis import (
    FormulateHypothesisCommand,
    FormulateHypothesisUseCase,
)
from src.application.errors import ApplicationError
from src.core.logging_context import bind_log_context
from src.domain.shared.errors import DomainError

_GENERATED_PATH = Path(__file__).parent / "generated"
if str(_GENERATED_PATH) not in sys.path:
    sys.path.append(str(_GENERATED_PATH))

experimentation_service_pb2 = import_module("experimentation.v1.experimentation_service_pb2")
experimentation_service_pb2_grpc = import_module(
    "experimentation.v1.experimentation_service_pb2_grpc"
)


class ExperimentationGrpcService(experimentation_service_pb2_grpc.ExperimentationServiceServicer):
    def __init__(self, container: AsyncContainer) -> None:
        self._container = container

    async def FormulateHypothesis(self, request, context):  # noqa: N802
        try:
            command = FormulateHypothesisCommand(
                workspace_id=self._parse_uuid(request.workspace_id, "workspace_id"),
                statement=request.statement,
                expected_outcome=self._optional_string(request, "expected_outcome"),
                created_by=self._parse_uuid(request.created_by, "created_by"),
                confidence=request.confidence,
                priority=request.priority,
            )
        except ValueError as exc:
            await abort_invalid_argument(context.abort, str(exc))
            raise

        try:
            with bind_log_context(workspace_id=str(command.workspace_id)):
                async with self._container(scope=Scope.REQUEST) as request_container:
                    formulate_hypothesis = await request_container.get(FormulateHypothesisUseCase)
                    result = await formulate_hypothesis.execute(command)
        except (ApplicationError, DomainError) as exc:
            await abort_application_error(context.abort, exc)
            raise

        return experimentation_service_pb2.HypothesisResponse(
            hypothesis_id=str(result.hypothesis_id),
            workspace_id=str(result.workspace_id),
            status=result.status.value,
        )

    def _parse_uuid(self, value: str, field_name: str) -> UUID:
        try:
            return UUID(value)
        except ValueError as exc:
            msg = f"Invalid {field_name}: {value}"
            raise ValueError(msg) from exc

    def _optional_string(self, request, field_name: str) -> str | None:
        if request.HasField(field_name):
            value = getattr(request, field_name)
            return value if value else None
        return None
