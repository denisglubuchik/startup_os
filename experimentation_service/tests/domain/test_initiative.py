from uuid import uuid4

import pytest

from src.domain.initiative.aggregate import Initiative
from src.domain.initiative.events import (
    InitiativeCompleted,
    InitiativeCreated,
    InitiativeLinkedToGoal,
    InitiativeStatusChanged,
    InitiativeTaskAdded,
)
from src.domain.initiative.value_objects import (
    ArchiveReason,
    CancellationReason,
    GoalReference,
    InitiativePriority,
    InitiativeStatus,
    InitiativeTitle,
)
from src.domain.shared.errors import DomainError


async def test_initiative_create_records_events_for_goal_links() -> None:
    goal_ref = GoalReference(goal_id=uuid4())

    initiative = Initiative.create(
        workspace_id=uuid4(),
        title=InitiativeTitle("Improve activation"),
        created_by=uuid4(),
        owner_id=uuid4(),
        goal_refs=[goal_ref],
    )

    events = initiative.pull_events()

    assert initiative.status == InitiativeStatus.PLANNED
    assert [type(event) for event in events] == [InitiativeCreated, InitiativeLinkedToGoal]


async def test_link_goal_and_add_task_are_idempotent() -> None:
    initiative = valid_initiative()
    goal_ref = GoalReference(goal_id=uuid4())
    task_id = uuid4()
    initiative.pull_events()

    initiative.link_to_goal(goal_ref)
    initiative.link_to_goal(goal_ref)
    initiative.add_task(task_id)
    initiative.add_task(task_id)

    events = initiative.pull_events()

    assert initiative.goal_refs == [goal_ref]
    assert initiative.task_ids == [task_id]
    assert [type(event) for event in events] == [InitiativeLinkedToGoal, InitiativeTaskAdded]


async def test_goal_reference_normalizes_title_snapshot() -> None:
    goal_ref = GoalReference(goal_id=uuid4(), title_snapshot="  Improve activation  ")
    empty_goal_ref = GoalReference(goal_id=uuid4(), title_snapshot="   ")

    assert goal_ref.title_snapshot == "Improve activation"
    assert empty_goal_ref.title_snapshot is None


async def test_initiative_start_records_status_change_once() -> None:
    initiative = valid_initiative()
    initiative.pull_events()

    initiative.start()
    initiative.start()

    events = initiative.pull_events()

    assert initiative.status == InitiativeStatus.ACTIVE
    assert len(events) == 1
    assert isinstance(events[0], InitiativeStatusChanged)


async def test_initiative_completion_requires_all_tasks_completed() -> None:
    initiative = valid_initiative()
    task_id = uuid4()
    initiative.add_task(task_id)
    initiative.start()

    with pytest.raises(DomainError, match="incomplete tasks"):
        initiative.complete(completed_by=uuid4(), completed_task_ids=set())

    initiative.complete(completed_by=uuid4(), completed_task_ids={task_id})

    events = initiative.pull_events()

    assert initiative.status == InitiativeStatus.COMPLETED
    assert any(isinstance(event, InitiativeCompleted) for event in events)


async def test_active_initiative_cannot_remove_tasks() -> None:
    initiative = valid_initiative()
    task_id = uuid4()
    initiative.add_task(task_id)
    initiative.start()

    with pytest.raises(DomainError, match="planned initiatives"):
        initiative.remove_task(task_id)


async def test_completed_initiative_cannot_be_changed() -> None:
    initiative = valid_initiative()
    initiative.start()
    initiative.complete(completed_by=uuid4(), completed_task_ids=set())

    with pytest.raises(DomainError, match="cannot be changed"):
        initiative.change_priority(InitiativePriority.HIGH)


async def test_active_initiative_cannot_be_archived() -> None:
    initiative = valid_initiative()
    initiative.start()

    with pytest.raises(DomainError, match="Active initiative"):
        initiative.archive(reason=ArchiveReason("No longer useful"), archived_by=uuid4())


async def test_cancelled_initiative_cannot_be_started() -> None:
    initiative = valid_initiative()
    initiative.cancel(reason=CancellationReason("Strategy changed"), cancelled_by=uuid4())

    with pytest.raises(DomainError, match="cannot be changed"):
        initiative.start()


def valid_initiative() -> Initiative:
    return Initiative.create(
        workspace_id=uuid4(),
        title=InitiativeTitle("Improve activation"),
        created_by=uuid4(),
        owner_id=uuid4(),
    )
