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

Context: StartupOS needs a starting map for domain and service boundaries across identity, workspace management, strategy, goals, metrics, execution, experiments, documents, knowledge, notifications, and integrations.

Decision: Start with these bounded context hypotheses while treating them as provisional:

- Identity & Workspace
- Strategy, Goals & Metrics
- Execution / Tasks / Initiatives
- Experiments
- Documents / Knowledge
- Notifications / Integrations

Consequences:

- Codex and developers have a starting map.
- Random service creation is reduced.
- Early services can align with a documented domain hypothesis.
- Refactoring may be required as domain understanding improves.
- The project avoids pretending that first boundaries are final.

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
- `api_gateway` becomes the public API/BFF and may aggregate data for clients.
- `dashboard_service` can own derived projections, but not source-of-truth domain data.
- Kafka introduces operational and design complexity: event versioning, idempotent consumers, retry handling, and durable publishing must be handled before production use.
- gRPC contracts and Kafka event contracts need to be documented and tested.

Alternatives considered:

- Keep separate execution and experiments services: clearer theoretical boundaries, but more service overhead too early.
- Avoid an API gateway: simpler backend topology, but pushes aggregation and internal service knowledge toward clients.
- Use Kafka for all service communication: too indirect for request/response flows that need immediate answers.
- Make the whole system CQRS: too much complexity before real read/write pressure exists.

## Plan 0001: Initial Repository Setup

This is a plan, not implementation.

Goal: create a practical repository skeleton without overbuilding infrastructure.

Steps:

1. Choose the initial tech stack if it is not already chosen.
2. Create or verify the accepted service folders and local service `AGENTS.md` files.
3. Decide the concrete package layout inside each service.
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
