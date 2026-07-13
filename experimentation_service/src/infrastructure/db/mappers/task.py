from src.domain.task.aggregate import Task
from src.domain.task.value_objects import (
    DueDate,
    ExperimentReference,
    InitiativeReference,
    TaskDescription,
    TaskPriority,
    TaskStatus,
    TaskTitle,
)
from src.infrastructure.db.models.task import TaskModel


class TaskMapper:
    def to_domain(self, model: TaskModel) -> Task:
        return Task(
            id=model.id,
            workspace_id=model.workspace_id,
            title=TaskTitle(model.title),
            created_by=model.created_by,
            description=TaskDescription(model.description) if model.description else None,
            status=TaskStatus(model.status),
            priority=TaskPriority(model.priority),
            assignee_id=model.assignee_id,
            due_date=DueDate(model.due_at) if model.due_at is not None else None,
            initiative_ref=(
                InitiativeReference(
                    initiative_id=model.initiative_id,
                    title_snapshot=model.initiative_title_snapshot,
                )
                if model.initiative_id is not None
                else None
            ),
            experiment_ref=(
                ExperimentReference(
                    experiment_id=model.experiment_id,
                    title_snapshot=model.experiment_title_snapshot,
                )
                if model.experiment_id is not None
                else None
            ),
        )

    def to_model(self, task: Task, model: TaskModel | None = None) -> TaskModel:
        model = model or TaskModel(id=task.id)
        model.workspace_id = task.workspace_id
        model.title = task.title.value
        model.created_by = task.created_by
        model.description = task.description.value if task.description else None
        model.status = task.status.value
        model.priority = task.priority.value
        model.assignee_id = task.assignee_id
        model.due_at = task.due_date.value if task.due_date else None
        model.initiative_id = task.initiative_ref.initiative_id if task.initiative_ref else None
        model.initiative_title_snapshot = (
            task.initiative_ref.title_snapshot if task.initiative_ref else None
        )
        model.experiment_id = task.experiment_ref.experiment_id if task.experiment_ref else None
        model.experiment_title_snapshot = (
            task.experiment_ref.title_snapshot if task.experiment_ref else None
        )
        return model
