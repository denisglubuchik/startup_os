# StartupOS Codex Rules

These rules apply to Codex work in StartupOS. Keep changes practical, focused, and aligned with the current docs.

## Workflow

- Inspect relevant files before editing.
- Read `AGENTS.md` first, then the relevant docs in `docs/`.
- For non-trivial tasks, state a short plan before editing.
- Keep diffs focused and do not modify unrelated files.
- Do not reformat unrelated code.
- Do not upgrade dependencies unless required by the task.
- If a task references a plan in `docs/decisions-and-plan.md`, implement only the requested step.

Preferred backend implementation order:

1. Domain model or domain change
2. Application use case
3. Tests
4. Infrastructure adapter or repository implementation
5. API/controller layer
6. Documentation update if needed

For large tasks, implement a narrow vertical slice first.

## Architecture

- StartupOS is intentionally microservice-oriented.
- Each service owns its domain model and persistence.
- Services must not directly access another service's database.
- Cross-service communication should use explicit APIs or integration events.
- Use gRPC for synchronous internal commands and queries.
- Use Kafka for asynchronous domain events and side effects.
- Do not silently turn the project into a monolith.
- Do not create a new service for every small feature.
- Do not introduce RabbitMQ, broad CQRS, event sourcing, or distributed transactions unless explicitly requested or accepted in a decision.
- Keep CQRS-style read models limited to `dashboard_service` unless a later decision expands that pattern.

Preferred internal service structure:

- `domain/`: entities, value objects, aggregates, domain services, domain events, and business rules.
- `application/`: use cases, application services, commands, queries, transactions, and ports.
- `infrastructure/`: persistence, external adapters, framework integrations, clients, and implementation details.
- `api/`: HTTP controllers, request/response DTOs, routing, validation, and transport concerns.

Dependency direction:

- `domain/` must not depend on framework, database, transport, or infrastructure code.
- `application/` may depend on `domain/`.
- `infrastructure/` implements adapters and may depend on `application/` and `domain/`.
- `api/` calls application use cases and must not contain business workflows.

Add or split a service only for a clear reason such as distinct domain language, lifecycle, scaling pressure, persistence needs, security requirements, or contract boundary.

The accepted service folders are:

- `api_gateway`
- `workspace_service`
- `strategy_goals_service`
- `experimentation_service`
- `knowledge_service`
- `dashboard_service`
- `notification_service`

Read the local service `AGENTS.md` before editing a service folder.

## DDD

- Use DDD where it improves clarity; do not add ceremony for trivial CRUD.
- Business rules belong in the domain model or application use cases.
- Controllers should not contain business workflows.
- API DTOs should not be domain or ORM entities.
- Repositories should hide persistence details.
- Domain events should describe facts that already happened.

Good event names:

- `WorkspaceCreated`
- `MemberInvited`
- `GoalCreated`
- `MetricLinkedToGoal`
- `InitiativeCompleted`
- `ExperimentCompleted`
- `DocumentLinked`

Bad event names:

- `CreateWorkspaceRequested`
- `UpdateGoalEvent`
- `ProcessData`

## Testing

- Add or update tests for meaningful behavior changes.
- Prefer behavior tests over implementation-detail tests.
- Use unit tests for domain rules, value objects, aggregates, and pure application logic.
- Use integration tests for persistence, APIs, service boundaries, and external adapters.
- Use end-to-end tests only for critical user flows.
- Changes touching workspace membership, roles, permissions, user access, tenant isolation, or invitations should test both allowed and forbidden access where practical.
- Do not claim tests passed unless they were actually run.

## Code Style

- Follow existing project conventions.
- Write readable code with explicit names, small functions, simple control flow, and clear error handling.
- Use domain language in names.
- Avoid clever abstractions, hidden side effects, global mutable state, premature generalization, and unnecessary dependencies.
- Avoid unrelated formatting changes.
- Comments should explain non-obvious business rules, tradeoffs, or constraints.

## Documentation

Update docs when a change alters product scope, domain terminology, service boundaries, architecture, or development workflow. Significant architecture decisions belong in `docs/decisions-and-plan.md`.

Final responses after implementation should include what changed, tests or checks run, files changed, and assumptions or follow-ups when relevant.
