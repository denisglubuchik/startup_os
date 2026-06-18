import asyncio

from src.api.grpc.server import serve


def main() -> None:
    asyncio.run(serve())


if __name__ == "__main__":
    main()
