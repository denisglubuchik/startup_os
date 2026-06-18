from dataclasses import dataclass
from typing import TypeVar

IdT = TypeVar("IdT")


@dataclass
class Entity[IdT]:
    id: IdT

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Entity):
            return False
        return type(self) is type(other) and self.id == other.id

    def __hash__(self) -> int:
        return hash((type(self), self.id))
