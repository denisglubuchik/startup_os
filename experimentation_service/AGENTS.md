# experimentation_service

Owns execution work and validation workflows.

## Responsibility

- Initiatives.
- Tasks.
- Assignees, statuses, deadlines, and work planning.
- Hypotheses.
- Experiments.
- Results and learnings.
- Validation workflow.

## Boundaries

- Combines the earlier execution and experiments context hypotheses.
- Owns source-of-truth state for tasks, initiatives, hypotheses, experiments, results, and learnings.
- Does not own goals, metrics, documents, or workspace membership.
- Split execution and experiments only if the domain pressure becomes real.

## Communication

- gRPC: create/update tasks, create initiatives, assign work, create hypotheses, start/complete experiments, record results, capture learnings.
- Kafka events: `InitiativeCreated`, `TaskCreated`, `TaskAssigned`, `TaskCompleted`, `InitiativeCompleted`, `HypothesisCreated`, `ExperimentStarted`, `ExperimentCompleted`, `LearningCaptured`.

## Current State

Minimal Python/uv service exists. It currently has a simple `main.py`, tests, Ruff config, and no real domain implementation yet.

## Launch

From this directory:

```bash
uv run python main.py
```

## Tests

From this directory:

```bash
uv run pytest
```

## Lint And Format

From this directory:

```bash
uv run ruff check .
uv run ruff format .
```
