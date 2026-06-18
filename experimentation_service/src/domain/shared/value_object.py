from dataclasses import dataclass


@dataclass(frozen=True)
class ValueObject:
    def __post_init__(self) -> None:
        self.validate()

    def validate(self) -> None:
        pass
