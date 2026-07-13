from dataclasses import dataclass
from uuid import UUID, uuid4

from src.domain.shared.aggregate import AggregateRoot
from src.domain.shared.errors import DomainError
from src.domain.task.events import (
    TaskAssigned,
    TaskBlocked,
    TaskCancelled,
    TaskCompleted,
    TaskCreated,
    TaskPriorityChanged,
    TaskRescheduled,
    TaskRevised,
    TaskStatusChanged,
    TaskUnassigned,
    TaskUnblocked,
)
from src.domain.task.value_objects import (
    BlockReason,
    CancellationReason,
    DueDate,
    ExperimentReference,
    InitiativeReference,
    TaskDescription,
    TaskPriority,
    TaskStatus,
    TaskTitle,
)


@dataclass(eq=False, kw_only=True)
class Task(AggregateRoot[UUID]):
    workspace_id: UUID
    title: TaskTitle
    created_by: UUID

    description: TaskDescription | None = None
    status: TaskStatus = TaskStatus.TODO
    priority: TaskPriority = TaskPriority.MEDIUM
    assignee_id: UUID | None = None
    due_date: DueDate | None = None
    initiative_ref: InitiativeReference | None = None
    experiment_ref: ExperimentReference | None = None

    @classmethod
    def create(
        cls,
        *,
        workspace_id: UUID,
        title: TaskTitle,
        created_by: UUID,
        description: TaskDescription | None = None,
        priority: TaskPriority = TaskPriority.MEDIUM,
        assignee_id: UUID | None = None,
        due_date: DueDate | None = None,
        initiative_ref: InitiativeReference | None = None,
        experiment_ref: ExperimentReference | None = None,
    ) -> Task:
        task = cls(
            id=uuid4(),
            workspace_id=workspace_id,
            title=title,
            created_by=created_by,
            description=description,
            priority=priority,
            assignee_id=assignee_id,
            due_date=due_date,
            initiative_ref=initiative_ref,
            experiment_ref=experiment_ref,
        )

        task.record_event(
            TaskCreated(
                task_id=task.id,
                workspace_id=workspace_id,
                created_by=created_by,
                title=title.value,
            )
        )

        if assignee_id is not None:
            task.record_event(
                TaskAssigned(
                    task_id=task.id,
                    workspace_id=workspace_id,
                    assignee_id=assignee_id,
                    assigned_by=created_by,
                )
            )

        return task

    def revise(
        self,
        *,
        title: TaskTitle,
        description: TaskDescription | None,
        revised_by: UUID,
    ) -> None:
        self._ensure_can_be_changed()

        self.title = title
        self.description = description
        self.record_event(
            TaskRevised(task_id=self.id, workspace_id=self.workspace_id, revised_by=revised_by)
        )

    def assign(self, *, assignee_id: UUID, assigned_by: UUID) -> None:
        self._ensure_can_be_changed()

        if self.assignee_id == assignee_id:
            return

        self.assignee_id = assignee_id
        self.record_event(
            TaskAssigned(
                task_id=self.id,
                workspace_id=self.workspace_id,
                assignee_id=assignee_id,
                assigned_by=assigned_by,
            )
        )

    def unassign(self, *, unassigned_by: UUID) -> None:
        self._ensure_can_be_changed()

        if self.assignee_id is None:
            return

        self.assignee_id = None
        self.record_event(
            TaskUnassigned(
                task_id=self.id,
                workspace_id=self.workspace_id,
                unassigned_by=unassigned_by,
            )
        )

    def reschedule(self, *, due_date: DueDate | None) -> None:
        self._ensure_can_be_changed()

        if self.due_date == due_date:
            return

        self.due_date = due_date
        self.record_event(
            TaskRescheduled(
                task_id=self.id,
                workspace_id=self.workspace_id,
                due_at=due_date.value if due_date is not None else None,
            )
        )

    def change_priority(self, priority: TaskPriority) -> None:
        self._ensure_can_be_changed()

        if self.priority == priority:
            return

        self.priority = priority
        self.record_event(
            TaskPriorityChanged(
                task_id=self.id,
                workspace_id=self.workspace_id,
                priority=priority,
            )
        )

    def start(self) -> None:
        self._ensure_can_be_changed()

        if self.status == TaskStatus.IN_PROGRESS:
            return

        if self.status != TaskStatus.TODO:
            raise DomainError("Only TODO task can be started.")

        self.status = TaskStatus.IN_PROGRESS
        self._record_status_changed()

    def block(self, *, reason: BlockReason, blocked_by: UUID) -> None:
        self._ensure_can_be_changed()

        if self.status == TaskStatus.BLOCKED:
            raise DomainError("Task is already blocked.")

        if self.status not in {TaskStatus.TODO, TaskStatus.IN_PROGRESS}:
            raise DomainError("Only active task can be blocked.")

        self.status = TaskStatus.BLOCKED
        self.record_event(
            TaskBlocked(
                task_id=self.id,
                workspace_id=self.workspace_id,
                blocked_by=blocked_by,
                reason=reason.value,
            )
        )

    def unblock(self, *, unblocked_by: UUID) -> None:
        self._ensure_can_be_changed()

        if self.status != TaskStatus.BLOCKED:
            raise DomainError("Only blocked task can be unblocked.")

        self.status = TaskStatus.TODO
        self.record_event(
            TaskUnblocked(
                task_id=self.id,
                workspace_id=self.workspace_id,
                unblocked_by=unblocked_by,
            )
        )
        self._record_status_changed()

    def complete(self, *, completed_by: UUID) -> None:
        self._ensure_can_be_changed()

        if self.status == TaskStatus.BLOCKED:
            raise DomainError("Blocked task cannot be completed.")

        if self.status not in {TaskStatus.TODO, TaskStatus.IN_PROGRESS}:
            raise DomainError("Only active task can be completed.")

        self.status = TaskStatus.DONE
        self.record_event(
            TaskCompleted(
                task_id=self.id,
                workspace_id=self.workspace_id,
                completed_by=completed_by,
            )
        )

    def cancel(self, *, reason: CancellationReason, cancelled_by: UUID) -> None:
        self._ensure_can_be_changed()

        self.status = TaskStatus.CANCELLED
        self.record_event(
            TaskCancelled(
                task_id=self.id,
                workspace_id=self.workspace_id,
                cancelled_by=cancelled_by,
                reason=reason.value,
            )
        )

    def _record_status_changed(self) -> None:
        self.record_event(
            TaskStatusChanged(task_id=self.id, workspace_id=self.workspace_id, status=self.status)
        )

    def _ensure_can_be_changed(self) -> None:
        if self.status in {TaskStatus.DONE, TaskStatus.CANCELLED}:
            raise DomainError(f"Task with status '{self.status}' cannot be changed.")
