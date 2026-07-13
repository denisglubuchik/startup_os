from dataclasses import dataclass, field
from uuid import UUID, uuid4

from src.domain.initiative.events import (
    InitiativeArchived,
    InitiativeCancelled,
    InitiativeCompleted,
    InitiativeCreated,
    InitiativeLinkedToGoal,
    InitiativePriorityChanged,
    InitiativeRevised,
    InitiativeStatusChanged,
    InitiativeTaskAdded,
    InitiativeTaskRemoved,
)
from src.domain.initiative.value_objects import (
    ArchiveReason,
    CancellationReason,
    GoalReference,
    InitiativeDescription,
    InitiativePriority,
    InitiativeStatus,
    InitiativeTitle,
)
from src.domain.shared.aggregate import AggregateRoot
from src.domain.shared.errors import DomainError


@dataclass(eq=False, kw_only=True)
class Initiative(AggregateRoot[UUID]):
    workspace_id: UUID
    title: InitiativeTitle
    created_by: UUID
    owner_id: UUID

    description: InitiativeDescription | None = None
    status: InitiativeStatus = InitiativeStatus.PLANNED
    priority: InitiativePriority = InitiativePriority.MEDIUM
    goal_refs: list[GoalReference] = field(default_factory=list)
    task_ids: list[UUID] = field(default_factory=list)

    @classmethod
    def create(
        cls,
        *,
        workspace_id: UUID,
        title: InitiativeTitle,
        created_by: UUID,
        owner_id: UUID,
        description: InitiativeDescription | None = None,
        priority: InitiativePriority = InitiativePriority.MEDIUM,
        goal_refs: list[GoalReference] | None = None,
    ) -> Initiative:
        initiative = cls(
            id=uuid4(),
            workspace_id=workspace_id,
            title=title,
            created_by=created_by,
            owner_id=owner_id,
            description=description,
            priority=priority,
            goal_refs=list(goal_refs or []),
        )

        initiative.record_event(
            InitiativeCreated(
                initiative_id=initiative.id,
                workspace_id=workspace_id,
                created_by=created_by,
                title=title.value,
            )
        )

        for goal_ref in initiative.goal_refs:
            initiative.record_event(
                InitiativeLinkedToGoal(
                    initiative_id=initiative.id,
                    workspace_id=workspace_id,
                    goal_id=goal_ref.goal_id,
                )
            )

        return initiative

    def revise(
        self,
        *,
        title: InitiativeTitle,
        description: InitiativeDescription | None,
        revised_by: UUID,
    ) -> None:
        self._ensure_can_be_changed()

        self.title = title
        self.description = description
        self.record_event(
            InitiativeRevised(
                initiative_id=self.id,
                workspace_id=self.workspace_id,
                revised_by=revised_by,
            )
        )

    def link_to_goal(self, goal_ref: GoalReference) -> None:
        self._ensure_can_be_changed()

        if any(existing.goal_id == goal_ref.goal_id for existing in self.goal_refs):
            return

        self.goal_refs.append(goal_ref)
        self.record_event(
            InitiativeLinkedToGoal(
                initiative_id=self.id,
                workspace_id=self.workspace_id,
                goal_id=goal_ref.goal_id,
            )
        )

    def add_task(self, task_id: UUID) -> None:
        self._ensure_can_be_changed()

        if task_id in self.task_ids:
            return

        self.task_ids.append(task_id)
        self.record_event(
            InitiativeTaskAdded(
                initiative_id=self.id,
                workspace_id=self.workspace_id,
                task_id=task_id,
            )
        )

    def remove_task(self, task_id: UUID) -> None:
        self._ensure_can_be_changed()

        if self.status != InitiativeStatus.PLANNED:
            raise DomainError("Tasks can be removed only from planned initiatives.")

        if task_id not in self.task_ids:
            return

        self.task_ids.remove(task_id)
        self.record_event(
            InitiativeTaskRemoved(
                initiative_id=self.id,
                workspace_id=self.workspace_id,
                task_id=task_id,
            )
        )

    def change_priority(self, priority: InitiativePriority) -> None:
        self._ensure_can_be_changed()

        if self.priority == priority:
            return

        self.priority = priority
        self.record_event(
            InitiativePriorityChanged(
                initiative_id=self.id,
                workspace_id=self.workspace_id,
                priority=priority,
            )
        )

    def start(self) -> None:
        self._ensure_can_be_changed()

        if self.status == InitiativeStatus.ACTIVE:
            return

        if self.status != InitiativeStatus.PLANNED:
            raise DomainError("Only planned initiative can be started.")

        self.status = InitiativeStatus.ACTIVE
        self._record_status_changed()

    def complete(self, *, completed_by: UUID, completed_task_ids: set[UUID]) -> None:
        self._ensure_can_be_changed()

        if self.status != InitiativeStatus.ACTIVE:
            raise DomainError("Only active initiative can be completed.")

        incomplete_task_ids = set(self.task_ids) - completed_task_ids
        if incomplete_task_ids:
            raise DomainError("Initiative cannot be completed with incomplete tasks.")

        self.status = InitiativeStatus.COMPLETED
        self.record_event(
            InitiativeCompleted(
                initiative_id=self.id,
                workspace_id=self.workspace_id,
                completed_by=completed_by,
            )
        )

    def cancel(self, *, reason: CancellationReason, cancelled_by: UUID) -> None:
        self._ensure_can_be_changed()

        self.status = InitiativeStatus.CANCELLED
        self.record_event(
            InitiativeCancelled(
                initiative_id=self.id,
                workspace_id=self.workspace_id,
                cancelled_by=cancelled_by,
                reason=reason.value,
            )
        )

    def archive(self, *, reason: ArchiveReason, archived_by: UUID) -> None:
        if self.status == InitiativeStatus.ACTIVE:
            raise DomainError("Active initiative cannot be archived.")

        if self.status == InitiativeStatus.ARCHIVED:
            return

        self.status = InitiativeStatus.ARCHIVED
        self.record_event(
            InitiativeArchived(
                initiative_id=self.id,
                workspace_id=self.workspace_id,
                archived_by=archived_by,
                reason=reason.value,
            )
        )

    def _record_status_changed(self) -> None:
        self.record_event(
            InitiativeStatusChanged(
                initiative_id=self.id,
                workspace_id=self.workspace_id,
                status=self.status,
            )
        )

    def _ensure_can_be_changed(self) -> None:
        if self.status in {
            InitiativeStatus.COMPLETED,
            InitiativeStatus.CANCELLED,
            InitiativeStatus.ARCHIVED,
        }:
            raise DomainError(f"Initiative with status '{self.status}' cannot be changed.")
