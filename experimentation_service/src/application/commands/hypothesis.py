from dataclasses import dataclass
from enum import StrEnum
from uuid import UUID

from src.application.errors import ValidationError
from src.application.interfaces.unit_of_work import UnitOfWork
from src.domain.hypothesis.aggregate import Hypothesis
from src.domain.hypothesis.value_objects import (
    ConfidenceLevel,
    ExpectedOutcome,
    HypothesisPriority,
    HypothesisStatement,
    HypothesisStatus,
)


@dataclass(frozen=True)
class FormulateHypothesisCommand:
    workspace_id: UUID
    statement: str
    expected_outcome: str | None
    created_by: UUID
    confidence: str = ConfidenceLevel.LOW.value
    priority: str = HypothesisPriority.MEDIUM.value


@dataclass(frozen=True)
class FormulateHypothesisResult:
    hypothesis_id: UUID
    workspace_id: UUID
    status: HypothesisStatus


class FormulateHypothesisUseCase:
    def __init__(self, uow: UnitOfWork) -> None:
        self._uow = uow

    async def execute(self, command: FormulateHypothesisCommand) -> FormulateHypothesisResult:
        hypothesis = Hypothesis.formulate(
            workspace_id=command.workspace_id,
            statement=HypothesisStatement(command.statement),
            expected_outcome=self._expected_outcome(command.expected_outcome),
            created_by=command.created_by,
            confidence=self._enum_value(ConfidenceLevel, command.confidence, "confidence"),
            priority=self._enum_value(HypothesisPriority, command.priority, "priority"),
        )

        async with self._uow:
            await self._uow.hypotheses.save(hypothesis)
            self._uow.collect_events(hypothesis)
            await self._uow.commit()

        return FormulateHypothesisResult(
            hypothesis_id=hypothesis.id,
            workspace_id=hypothesis.workspace_id,
            status=hypothesis.status,
        )

    def _expected_outcome(self, value: str | None) -> ExpectedOutcome | None:
        return None if value is None else ExpectedOutcome(value)

    def _enum_value[EnumT: StrEnum](
        self,
        enum_type: type[EnumT],
        value: str,
        field_name: str,
    ) -> EnumT:
        try:
            return enum_type(value)
        except ValueError as exc:
            msg = f"Invalid {field_name}: {value}"
            raise ValidationError(msg) from exc
