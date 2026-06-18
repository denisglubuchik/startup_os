from datetime import UTC, datetime
from uuid import uuid4

import pytest

from src.domain.shared.errors import DomainError
from src.domain.task.aggregate import Task
from src.domain.task.events import (
    TaskAssigned,
    TaskBlocked,
    TaskCompleted,
    TaskCreated,
    TaskRescheduled,
    TaskStatusChanged,
    TaskUnblocked,
)
from src.domain.task.value_objects import (
    BlockReason,
    CancellationReason,
    DueDate,
    TaskPriority,
    TaskStatus,
    TaskTitle,
)


async def test_task_create_records_event_and_optional_assignment() -> None:
    assignee_id = uuid4()

    task = Task.create(
        workspace_id=uuid4(),
        title=TaskTitle("Call customers"),
        created_by=uuid4(),
        assignee_id=assignee_id,
    )

    events = task.pull_events()

    assert task.status == TaskStatus.TODO
    assert task.assignee_id == assignee_id
    assert [type(event) for event in events] == [TaskCreated, TaskAssigned]


async def test_task_start_is_idempotent_once_in_progress() -> None:
    task = valid_task()
    task.pull_events()

    task.start()
    task.start()

    events = task.pull_events()

    assert task.status == TaskStatus.IN_PROGRESS
    assert len(events) == 1
    assert isinstance(events[0], TaskStatusChanged)


async def test_blocked_task_cannot_be_completed_until_unblocked() -> None:
    task = valid_task()
    task.block(reason=BlockReason("Waiting for customer reply"), blocked_by=uuid4())

    with pytest.raises(DomainError, match="Blocked task cannot be completed"):
        task.complete(completed_by=uuid4())

    task.unblock(unblocked_by=uuid4())
    assert task.status == TaskStatus.TODO

    task.complete(completed_by=uuid4())

    events = task.pull_events()

    assert task.status == TaskStatus.DONE
    assert any(isinstance(event, TaskBlocked) for event in events)
    assert any(isinstance(event, TaskUnblocked) for event in events)
    assert any(isinstance(event, TaskCompleted) for event in events)


async def test_done_task_cannot_be_changed() -> None:
    task = valid_task()
    task.complete(completed_by=uuid4())

    with pytest.raises(DomainError, match="cannot be changed"):
        task.assign(assignee_id=uuid4(), assigned_by=uuid4())


async def test_task_reschedule_normalizes_due_date() -> None:
    task = valid_task()
    due_date = DueDate(datetime(2026, 1, 1, 12, 0, tzinfo=UTC))
    task.pull_events()

    task.reschedule(due_date=due_date)

    events = task.pull_events()

    assert task.due_date == due_date
    assert len(events) == 1
    assert isinstance(events[0], TaskRescheduled)
    assert events[0].due_at == due_date.value


async def test_task_due_date_rejects_naive_datetime() -> None:
    with pytest.raises(DomainError, match="due_at must be timezone-aware"):
        DueDate(datetime(2026, 1, 1, 12, 0))  # noqa: DTZ001


async def test_task_priority_change_is_idempotent() -> None:
    task = valid_task()
    task.pull_events()

    task.change_priority(TaskPriority.MEDIUM)

    assert task.pull_events() == []


async def test_task_cancel_prevents_later_start() -> None:
    task = valid_task()
    task.cancel(reason=CancellationReason("No longer needed"), cancelled_by=uuid4())

    with pytest.raises(DomainError, match="cannot be changed"):
        task.start()


def valid_task() -> Task:
    return Task.create(
        workspace_id=uuid4(),
        title=TaskTitle("Call customers"),
        created_by=uuid4(),
    )
