# experimentation_service

Owns execution work and validation workflows.

## Language

Python.

## Responsibility

- Initiatives.
- Tasks.
- Execution checklists.
- Assignees, statuses, deadlines, and work planning.
- Hypotheses.
- Experiments.
- Evidence.
- Experiment results.
- Outcome interpretation.
- Validation workflow.

## Boundaries

- Combines the earlier execution and experiments context hypotheses.
- Owns source-of-truth state for tasks, initiatives, hypotheses, experiments, evidence, experiment results, and outcome interpretation.
- Does not own goals, metrics, decisions, insights, learning notes, documents, or workspace membership.
- Decisions, insights, and learning notes belong in `knowledge_service`.
- Split execution and experiments only if the domain pressure becomes real.

## Communication

- gRPC: create/update tasks, create initiatives, assign work, create hypotheses, start/complete experiments, add evidence, record results, interpret outcomes.
- Contract source of truth: protobuf-generated services/types.
- Kafka events: `InitiativeCreated`, `TaskCreated`, `TaskAssigned`, `TaskCompleted`, `InitiativeCompleted`, `HypothesisCreated`, `ExperimentStarted`, `EvidenceAdded`, `ExperimentResultRecorded`, `ExperimentOutcomeInterpreted`, `ExperimentCompleted`.

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
