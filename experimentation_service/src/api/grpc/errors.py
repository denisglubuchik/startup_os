from collections.abc import Awaitable, Callable

import grpc

from src.application.errors import ApplicationError, NotFoundError, ValidationError
from src.domain.shared.errors import DomainError

type Abort = Callable[[grpc.StatusCode, str], Awaitable[None]]


async def abort_invalid_argument(abort: Abort, details: str) -> None:
    await abort(grpc.StatusCode.INVALID_ARGUMENT, details)


async def abort_application_error(abort: Abort, error: ApplicationError | DomainError) -> None:
    if isinstance(error, NotFoundError):
        await abort(grpc.StatusCode.NOT_FOUND, str(error))
        return

    if isinstance(error, ValidationError | DomainError):
        await abort(grpc.StatusCode.INVALID_ARGUMENT, str(error))
        return

    await abort(grpc.StatusCode.FAILED_PRECONDITION, str(error))
