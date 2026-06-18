# strategy_goals_service

Owns startup strategy, goals, metrics, and progress tracking.

## Language

Go.

## Responsibility

- Strategy and strategic directions.
- Goals.
- Metrics.
- Measurable outcomes or key-result-like structures.
- Metric-to-goal links.
- Progress updates.

## Boundaries

- Owns the source-of-truth model for goals and metrics.
- Does not own execution tasks, experiments, documents, or workspace membership.
- Must not directly access other service databases.

## Communication

- gRPC: create/update goals, define metrics, link metrics to goals, update progress, query goal state.
- Contract source of truth: protobuf-generated services/types.
- Kafka events: `GoalCreated`, `GoalUpdated`, `MetricCreated`, `MetricLinkedToGoal`, `GoalProgressUpdated`.

## Current State

Folder placeholder only. No runnable service skeleton exists yet.

## Launch

Not available until the service skeleton is implemented. Add the exact command here when the service has an application entrypoint.

## Tests

Not available until tests are added. Add the exact test command here when the service has a test suite.
