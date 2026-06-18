import grpc
from dishka import AsyncContainer

from src.api.grpc.experimentation_service import (
    ExperimentationGrpcService,
    experimentation_service_pb2_grpc,
)
from src.core.config import GrpcConfig
from src.infrastructure.di import create_container


def create_grpc_server(container: AsyncContainer) -> grpc.aio.Server:
    server = grpc.aio.server()
    experimentation_service_pb2_grpc.add_ExperimentationServiceServicer_to_server(
        ExperimentationGrpcService(container),
        server,
    )
    return server


def create_container_from_env() -> AsyncContainer:
    return create_container()


async def serve(address: str | None = None) -> None:
    container = create_container_from_env()
    server = create_grpc_server(container)
    grpc_config = await container.get(GrpcConfig)
    listen_address = address or grpc_config.address
    server.add_insecure_port(listen_address)

    await server.start()
    print(f"experimentation_service gRPC server listening on {listen_address}")

    try:
        await server.wait_for_termination()
    finally:
        await container.close()
