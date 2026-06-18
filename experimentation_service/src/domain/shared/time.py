from datetime import UTC, datetime

from src.domain.shared.errors import DomainError


def utc_now() -> datetime:
    return datetime.now(UTC)


def require_utc_datetime(value: datetime, field_name: str) -> datetime:
    if value.tzinfo is None or value.utcoffset() is None:
        raise DomainError(f"{field_name} must be timezone-aware.")

    return value.astimezone(UTC)
