from dataclasses import dataclass, field
from typing import TypeVar

from .entity import Entity
from .events import DomainEvent

IdT = TypeVar("IdT")


@dataclass
class AggregateRoot[IdT](Entity[IdT]):
    _domain_events: list[DomainEvent] = field(default_factory=list, init=False, repr=False)

    def record_event(self, event: DomainEvent) -> None:
        self._domain_events.append(event)

    def pull_events(self) -> list[DomainEvent]:
        events = list(self._domain_events)
        self._domain_events.clear()
        return events
