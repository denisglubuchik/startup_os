from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID, uuid4

from src.domain.shared.time import utc_now


@dataclass(frozen=True, kw_only=True)
class DomainEvent:
    event_id: UUID = field(default_factory=uuid4)
    occurred_at: datetime = field(default_factory=utc_now)

    @property
    def event_type(self) -> str:
        return type(self).__name__
