# dashboard_service

Owns read-optimized dashboard projections.

## Responsibility

- Dashboard query models.
- Cross-service read projections.
- Workspace operating views.
- Goal, execution, experimentation, and knowledge summaries.

## Boundaries

- This service is CQRS-like only for reads.
- Owns derived read models, not source-of-truth domain data.
- Does not perform domain writes for other services.
- Must not directly access other service databases.
- Rebuildable projections are preferred over irreplaceable state.

## Communication

- gRPC: dashboard queries from `api_gateway`.
- Kafka consumers: workspace, goal, metric, task, experiment, and document events.
- gRPC fallbacks to source services are acceptable for explicit query needs, but stored projections should come from event streams where practical.

## Current State

Folder placeholder only. No runnable service skeleton exists yet.

## Launch

Not available until the service skeleton is implemented. Add the exact command here when the service has an application entrypoint.

## Tests

Not available until tests are added. Add the exact test command here when the service has a test suite.
