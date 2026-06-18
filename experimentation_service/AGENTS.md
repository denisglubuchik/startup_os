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
- Kafka events: `InitiativeCreated`, `TaskCreated`, `TaskAssigned`, `TaskCompleted`, `InitiativeCompleted`, `HypothesisFormulated`, `HypothesisTestingStarted`, `EvidenceRecorded`, `ExperimentResultRecorded`, `ExperimentOutcomeInterpreted`, `ExperimentCompleted`.

## Internal Structure

- `src/domain/`: domain aggregates, entities, value objects, domain events, errors, and time rules.
- `src/application/commands/`: application command DTOs and use cases.
- `src/application/interfaces/`: repository and unit-of-work ports used by application use cases.
- `src/api/grpc/`: gRPC server, service adapters, transport error mapping, and generated protobuf code.
- `src/core/config.py`: pydantic-settings runtime configuration loaded from environment variables and `.env`.
- `src/infrastructure/db/models/`: SQLAlchemy ORM models, split by aggregate.
- `src/infrastructure/db/mappers/`: explicit ORM/domain mappers.
- `src/infrastructure/db/repositories/`: SQLAlchemy repository implementations, split by aggregate.
- `src/infrastructure/db/migrations/`: Alembic migrations.
- `src/infrastructure/di.py`: Dishka provider wiring for config, DB session, mappers, repositories, Unit of Work, and use cases.
- `tests/support/`: shared application-test fakes and fixtures.

## Current State

Python/uv service has domain models and tests for hypotheses, experiments, initiatives, and tasks.

Persistence scaffolding exists:

- SQLAlchemy async ORM models.
- Repository interfaces in the application layer.
- SQLAlchemy repository implementations in infrastructure.
- Unit of Work implementation that writes domain events to an outbox table before commit.
- Alembic migration setup under `src/infrastructure/db/migrations`.
- Dishka dependency injection setup for configuration, infrastructure dependencies, and the first use case.

The first application and gRPC vertical slice exists:

- `FormulateHypothesisUseCase` in `src/application/commands/hypothesis.py`.
- Protobuf source: `../proto/startupos/experimentation/v1/experimentation_service.proto`.
- Generated Python gRPC code: `src/api/grpc/generated/experimentation/v1/`.
- gRPC adapter: `src/api/grpc/experimentation_service.py`.
- gRPC server: `src/api/grpc/server.py`.

Kafka publisher/consumer workers are not implemented yet.

Persistence notes:

- The database URL is read from `DATABASE_URL` by Alembic, with a local default in `alembic.ini`.
- Runtime DB settings are loaded from `PG_HOST`, `PG_PORT`, `PG_DB`, `PG_USER`, and `PG_PASS`; local defaults live in `.env`.
- gRPC runtime settings are loaded from `GRPC_HOST` and `GRPC_PORT`.
- Outbox records are stored durably but not published to Kafka yet.
- Write use cases should use Unit of Work so persistence and outbox records commit atomically. Simple read-only use cases may use repository ports directly.
- Do not import SQLAlchemy models into domain or application interfaces.

## Launch

From this directory:

```bash
uv run python main.py
```

This starts the gRPC server. Local defaults are read from `.env`.

Docker Compose starts the service and Postgres:

```bash
docker compose up --build
```

## Tests

From this directory:

```bash
uv run pytest
```

Tests use `pytest-asyncio`.

E2E tests require Docker/Testcontainers:

```bash
uv run pytest tests/e2e -m e2e -vv
```

CI policy:

- Pull requests run lint, format check, and `uv run pytest -m "not e2e"`.
- Pushes to `master` run the same checks plus the Testcontainers e2e job.

## Lint And Format

From this directory:

```bash
uv run ruff check .
uv run ruff format .
```

## Migrations

From this directory:

```bash
uv run alembic revision --autogenerate -m "message"
uv run alembic upgrade head
```

Run migrations with a valid `DATABASE_URL` when not using the local default.
