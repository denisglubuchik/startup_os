# Decisions And Plan

## ADR 0001: Use Microservices For Learning

- Status: Accepted

Context: StartupOS is a SaaS platform for startup management. The simplest MVP architecture would likely be a monolith or modular monolith, but this project has an explicit learning goal: practice service boundaries, independent services, CI/CD, contracts between services, and distributed-system tradeoffs.

Decision: Use a microservice-oriented architecture from the beginning, primarily to learn and practice service boundaries, independent services, CI/CD, and distributed-system tradeoffs.

Consequences:

- Microservices add complexity.
- This is not the simplest MVP architecture.
- Service boundaries and contracts must be documented and maintained.
- The learning goal is intentional.
- The project should still avoid unnecessary infrastructure complexity.
- Message brokers, CQRS, event sourcing, and distributed transactions are not part of the initial architecture unless a later decision accepts them.
- ADR 0003 accepts Kafka for async domain events and limits CQRS-style reads to `dashboard_service`.

Alternatives considered:

- Modular monolith: simpler for MVP, but less practice with independent services and deployment tradeoffs.
- Pure monolith: fastest initial path, but works against the learning goal.
- Fully event-sourced / CQRS architecture from day one: too much complexity before the domain model is understood.

## ADR 0002: Initial Bounded Context Hypotheses

- Status: Accepted

Context: StartupOS needs a starting map for domain and service boundaries across identity, workspace management, strategy, goals, metrics, execution, experiments, evidence, decisions, knowledge, notifications, and integrations.

Decision: Start with these bounded context hypotheses while treating them as provisional:

- Identity & Workspace
- Strategy, Goals & Metrics
- Experimentation
- Knowledge & Decisions

Supporting capabilities:

- Dashboard Read Models
- Notifications / Integrations

Consequences:

- Codex and developers have a starting map.
- Random service creation is reduced.
- Early services can align with a documented domain hypothesis.
- Refactoring may be required as domain understanding improves.
- The project avoids pretending that first boundaries are final.
- Notifications and integrations are treated as supporting technical capabilities, not core domain contexts.

Alternatives considered:

- No explicit boundaries: flexible, but likely inconsistent.
- One broad startup-management context: simpler, but conflicts with the microservice learning goal.
- Separate context for every feature: too fragmented and overfit to early assumptions.

## ADR 0003: Initial Service Map And Communication Style

- Status: Accepted

Context: The project needs a concrete first service map that reflects the bounded context hypotheses without creating too many small services. The frontend will need an entrypoint that can route and aggregate service data. Some cross-service workflows should be asynchronous, especially dashboards, notifications, and side effects.

Decision: Start with these service folders:

- `api_gateway`
- `workspace_service`
- `strategy_goals_service`
- `experimentation_service`
- `knowledge_service`
- `dashboard_service`
- `notification_service`

Use gRPC for synchronous internal service calls. Use Kafka for asynchronous domain events. Limit CQRS-style read models to `dashboard_service`; source-of-truth writes remain in the owning services.

Consequences:

- The service map is smaller than one-service-per-bounded-context.
- Execution and experiments are combined in `experimentation_service` until there is a real reason to split them.
- `experimentation_service` owns evidence, experiment results, and outcome interpretation.
- `knowledge_service` owns decisions, insights, learning notes, and knowledge links.
- `api_gateway` becomes the public API/BFF and may aggregate data for clients.
- `dashboard_service` can own derived projections, but not source-of-truth domain data.
- `notification_service` is a supporting technical capability, not a core bounded context.
- Kafka introduces operational and design complexity: event versioning, idempotent consumers, retry handling, and durable publishing must be handled before production use.
- gRPC contracts and Kafka event contracts need to be documented and tested.

Alternatives considered:

- Keep separate execution and experiments services: clearer theoretical boundaries, but more service overhead too early.
- Avoid an API gateway: simpler backend topology, but pushes aggregation and internal service knowledge toward clients.
- Use Kafka for all service communication: too indirect for request/response flows that need immediate answers.
- Make the whole system CQRS: too much complexity before real read/write pressure exists.

## ADR 0004: Separate Experiment Results From Knowledge

- Status: Accepted

Context: `experimentation_service` and `knowledge_service` both touched the word learning, which could make source-of-truth ownership unclear.

Decision: `experimentation_service` owns hypotheses, experiments, execution checklists/tasks, evidence, experiment results, and outcome interpretation. `knowledge_service` owns decisions, decision rationale, insights, learning notes, knowledge links, and supporting documents.

Consequences:

- Raw evidence and experiment results have one source of truth.
- Decisions and reusable knowledge have one source of truth.
- Knowledge can link back to evidence and results without owning them.
- Codex should not build `knowledge_service` as a generic Notion-like document service first.

Alternatives considered:

- Let `experimentation_service` own learnings: simpler locally, but creates overlap with knowledge and decisions.
- Let `knowledge_service` own raw experiment results: makes knowledge too broad and weakens experimentation as the validation source of truth.

## ADR 0005: Initial Service Languages And Contract Standard

- Status: Accepted

Context: StartupOS will use both Go and Python. Without a common contract style, each service could drift into different HTTP frameworks, DTO shapes, and integration conventions.

Decision: Use these initial language choices:

- Go: `api_gateway`, `workspace_service`, `strategy_goals_service`, `dashboard_service`
- Python: `experimentation_service`, `knowledge_service`, `notification_service`

Use protobuf as the source of truth for internal service contracts. Use gRPC for synchronous service-to-service APIs. Use protobuf-defined event payloads for Kafka events where practical. Keep public HTTP API choices inside `api_gateway`; internal services should not expose random HTTP styles to each other.

Consequences:

- Go services cover the gateway, security-critical workspace logic, strategy/goals contracts, and dashboard projections.
- Python services cover experimentation workflows, knowledge/decision workflows, and notification/integration work.
- Mixed-language development stays manageable because generated protobuf types and clients define service boundaries.
- Protobuf schemas become part of the public internal contract and require review.
- Contract changes need backward compatibility thinking from the beginning.

Alternatives considered:

- All Go: simpler runtime and contracts, but less convenient for knowledge, integrations, and experimentation workflows.
- All Python: faster early iteration, but weaker fit for gateway and projection-heavy services.
- REST between all services: familiar, but easier to fragment across frameworks and DTO conventions.
- Hand-written DTOs per language: fast initially, but likely to drift and create integration bugs.

## ADR 0006: Experimentation Service Persistence And Outbox

- Status: Accepted

Context: `experimentation_service` now has domain aggregates for hypotheses, experiments, initiatives, and tasks. Application use cases need persistence boundaries that keep domain code independent from database details while still supporting durable domain event publication later.

Decision: Use SQLAlchemy async ORM for `experimentation_service` persistence, Alembic for migrations, repository ports in the application layer, SQLAlchemy repositories in infrastructure, and a Unit of Work that saves aggregate changes and writes domain events to an outbox table in the same transaction. Use Dishka for dependency injection of infrastructure dependencies such as session factories, mappers, repositories, and Unit of Work.

Consequences:

- Domain models remain free of SQLAlchemy, Alembic, Dishka, and transport concerns.
- Application use cases depend on repository and Unit of Work interfaces, not concrete database adapters.
- Outbox records make domain event publication durable once a Kafka publisher worker is added.
- Kafka publishing is not implemented yet; outbox storage is the first step.
- Repository and mapper code must stay explicit and split by aggregate rather than using one generic JSON blob mapper.
- Persistence schema is owned by `experimentation_service`; other services must not read it directly.

Alternatives considered:

- Direct SQLAlchemy use from application use cases: faster initially, but leaks infrastructure into orchestration code.
- JSON blob aggregate tables: quick to scaffold, but weak for relational integrity, migrations, and query/debug ergonomics.
- Publish Kafka events directly inside use cases: simpler code path, but can lose events if database commit and publish are not atomic.
- Event sourcing: rejected as too much complexity for the current stage.

## ADR 0007: Experimentation Service gRPC Slice And Runtime Wiring

- Status: Accepted

Context: `experimentation_service` needs its first synchronous internal API while preserving the domain/application/infrastructure boundaries already accepted for persistence. The service also needs a practical local runtime configuration and an end-to-end verification path.

Decision: Expose the first vertical slice, `FormulateHypothesis`, through gRPC. Keep protobuf contracts in the repository-level `proto/` tree, with `proto/startupos/experimentation/v1/experimentation_service.proto` as the source of truth. Generate Python gRPC code inside `experimentation_service/src/api/grpc/generated`. Keep gRPC adapters thin: protobuf request/response mapping happens in `src/api/grpc`, while business behavior stays in application use cases and domain aggregates. Use Dishka to wire runtime configuration, DB session factories, repositories, Unit of Work, and use cases. Use `pydantic-settings` for `.env`/environment-backed runtime configuration. Add a Testcontainers-based e2e test that starts Postgres, runs Alembic migrations, starts the gRPC server in process, calls the generated gRPC client, and verifies both aggregate persistence and outbox storage.

Consequences:

- Protobuf remains the internal service contract, not an application-layer DTO.
- The application layer remains transport-independent.
- Generated Python protobuf code is checked into the service-local generated folder and excluded from Ruff checks.
- Write use cases continue to use Unit of Work so aggregate persistence and outbox records are committed atomically.
- E2E tests require Docker access and are marked with `e2e`.
- Redis configuration is not wired yet.
- Logging is configured in `src/core` and uses `contextvars` for request-scoped observability fields. The gRPC server interceptor binds `x-correlation-id`, `x-request-id`, `x-causation-id`, `x-workspace-id`, and the gRPC method around the actual RPC handler execution.
- Kafka publishing from the outbox is still not implemented.

Alternatives considered:

- Put protobuf files inside `experimentation_service`: rejected because protobuf contracts are shared service contracts needed by clients such as `api_gateway`.
- Use application DTOs as gRPC DTOs directly: rejected because it would couple application code to transport details.
- Start with HTTP instead of gRPC: rejected because internal synchronous calls are standardized on gRPC.
- Add Kafka publishing immediately: deferred until more write use cases and event consumption needs exist.

## Plan 0001: Initial Repository Setup

This is a plan, not implementation.

Goal: create a practical repository skeleton without overbuilding infrastructure.

Steps:

1. Create or verify the accepted service folders and local service `AGENTS.md` files.
2. Decide the concrete package layout inside Go and Python services.
3. Add shared protobuf contract location and generation approach.
4. Add basic tooling for formatting, linting, and testing.
5. Add local development instructions.
6. Add the first service skeleton using the agreed internal layers.
7. Add initial tests for the first service skeleton.
8. Add CI later, after local tooling and service layout are stable.

Constraints:

- Do not introduce additional message brokers, broad CQRS, event sourcing, or distributed transactions.
- Do not create every provisional service before there is a vertical slice that needs it.
- Keep setup small enough to understand and change.
- Update docs and decisions if setup choices alter the architecture.
- Kafka is accepted for async domain events, but do not wire a broker until a real vertical slice needs event publishing or consuming.
- CQRS-style read models are accepted only inside `dashboard_service`.

Likely first vertical slice: Identity & Workspace is a strong candidate because workspace isolation, membership, and permissions affect every other context.
