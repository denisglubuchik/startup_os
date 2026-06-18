from src.domain.initiative.aggregate import Initiative
from src.domain.initiative.value_objects import (
    GoalReference,
    InitiativeDescription,
    InitiativePriority,
    InitiativeStatus,
    InitiativeTitle,
)
from src.infrastructure.db.models.initiative import (
    InitiativeGoalReferenceModel,
    InitiativeModel,
    InitiativeTaskModel,
)


class InitiativeMapper:
    def to_domain(self, model: InitiativeModel) -> Initiative:
        return Initiative(
            id=model.id,
            workspace_id=model.workspace_id,
            title=InitiativeTitle(model.title),
            created_by=model.created_by,
            owner_id=model.owner_id,
            description=InitiativeDescription(model.description) if model.description else None,
            status=InitiativeStatus(model.status),
            priority=InitiativePriority(model.priority),
            goal_refs=[
                GoalReference(goal_id=goal.goal_id, title_snapshot=goal.title_snapshot)
                for goal in model.goal_refs
            ],
            task_ids=[task.task_id for task in model.tasks],
        )

    def to_model(
        self, initiative: Initiative, model: InitiativeModel | None = None
    ) -> InitiativeModel:
        model = model or InitiativeModel(id=initiative.id)
        model.workspace_id = initiative.workspace_id
        model.title = initiative.title.value
        model.created_by = initiative.created_by
        model.owner_id = initiative.owner_id
        model.description = initiative.description.value if initiative.description else None
        model.status = initiative.status.value
        model.priority = initiative.priority.value
        model.goal_refs = [
            InitiativeGoalReferenceModel(
                initiative_id=initiative.id,
                goal_id=goal.goal_id,
                title_snapshot=goal.title_snapshot,
            )
            for goal in initiative.goal_refs
        ]
        model.tasks = [
            InitiativeTaskModel(initiative_id=initiative.id, task_id=task_id)
            for task_id in initiative.task_ids
        ]
        return model
