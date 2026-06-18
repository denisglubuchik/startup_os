# Architecture

StartupOS is a microservice-oriented SaaS platform for startup management. The architecture should support independent services, clear contracts, service ownership, and production-minded tradeoffs while staying practical for an early-stage project.

Microservices are not the simplest MVP architecture. This project intentionally uses a microservice-oriented direction to learn and practice service boundaries, distributed system design, independent services, service contracts, CI/CD, and production tradeoffs.

Avoid unnecessary infrastructure complexity, but keep the architecture honest about distributed-system practice. gRPC is the preferred protocol for synchronous internal calls. Kafka is the accepted backbone for asynchronous domain events. CQRS-style read models are limited to `dashboard_service` unless a later decision expands that pattern.

## Service Ownership

- Each service owns its domain model and persistence.
- Other services interact through explicit gRPC APIs or Kafka integration-event contracts.
- Services must not directly access another service's database.
- Early services should broadly align with bounded context hypotheses.

## Service Layering

Prefer this structure inside a service:

- `domain/`: domain model and business rules
- `application/`: use cases and orchestration
- `infrastructure/`: persistence and external adapters
- `api/`: controllers, DTOs, routing, validation, and transport concerns

## Communication

- Frontend clients call `api_gateway`.
- `api_gateway` calls internal services through gRPC and aggregates responses when needed.
- Protobuf is the source of truth for internal gRPC contracts.
- Protobuf schemas should also define Kafka event payloads where practical.
- Generated clients/types should be used in Go and Python services instead of hand-written contract shapes.
- HTTP framework choices are local to `api_gateway`; internal services should not expose ad hoc HTTP styles to each other.
- Source-of-truth services publish domain events to Kafka after durable state changes.
- Kafka events describe facts that already happened.
- Event consumers must be idempotent.
- `dashboard_service` and `notification_service` are the first natural Kafka consumers.
- Do not use Kafka for user-facing request flows that require an immediate answer.
- Do not use direct database access across service boundaries.

## Language Choices

The current language split is provisional and can change through a later docs update.

- Go: `api_gateway`, `workspace_service`, `strategy_goals_service`, `dashboard_service`
- Python: `experimentation_service`, `knowledge_service`, `notification_service`

Use Go for services where strict contracts, predictable runtime behavior, gateway concerns, or read-heavy projections are the main pressure. Use Python where iteration speed, integrations, text-heavy workflows, or experimentation workflows are the main pressure.

## Service Map

The accepted service folders are:

- `api_gateway`
- `workspace_service`
- `strategy_goals_service`
- `experimentation_service`
- `knowledge_service`
- `dashboard_service`
- `notification_service`

### api_gateway

- Language: Go
- Role: Public API gateway and BFF.
- Responsibilities: route frontend requests, call internal services over gRPC, aggregate frontend-shaped responses, handle API-level auth/session concerns, normalize errors.
- Owns: client-facing API contracts and composition logic.
- Does not own: domain data, business workflows, persistence.
- Note: Keep it thin enough that domain behavior remains in owning services.

### workspace_service

- Language: Go
- Context: Identity & Workspace
- Responsibilities: users, workspaces, memberships, invitations, roles, permissions, tenant isolation.
- Contracts: create workspace, invite member, accept invitation, list members, check access.
- Events: `WorkspaceCreated`, `MemberInvited`, `MemberJoinedWorkspace`, `RoleAssigned`.
- Note: This service is security-critical.

### strategy_goals_service

- Language: Go
- Context: Strategy, Goals & Metrics
- Responsibilities: strategy, goals, measurable outcomes, metrics, progress tracking.
- Contracts: create goal, update goal, define metric, link metric to goal, update progress.
- Events: `GoalCreated`, `MetricCreated`, `MetricLinkedToGoal`, `GoalProgressUpdated`.
- Note: Goals and metrics stay together initially and may split later.

### experimentation_service

- Language: Python
- Context: Experimentation, combining execution and experiments.
- Responsibilities: initiatives, tasks, execution checklists, ownership, statuses, deadlines, hypotheses, experiments, evidence, experiment results, outcome interpretations, validation workflows.
- Contracts: create initiative, create task, assign task, change status, create hypothesis, start experiment, add evidence, record result, interpret outcome, complete experiment.
- Events: `InitiativeCreated`, `TaskCreated`, `TaskAssigned`, `TaskCompleted`, `InitiativeCompleted`, `HypothesisFormulated`, `HypothesisTestingStarted`, `EvidenceRecorded`, `ExperimentResultRecorded`, `ExperimentOutcomeInterpreted`, `ExperimentCompleted`.
- Persistence: owns its own relational database schema through SQLAlchemy async ORM and Alembic migrations.
- Application boundary: repository and unit-of-work ports live in `src/application/interfaces`; write use cases use Unit of Work, while simple read paths may use repository ports directly.
- First application slice: `FormulateHypothesis` exists as an application command use case and is exposed through gRPC.
- gRPC contract: the source protobuf lives at `proto/startupos/experimentation/v1/experimentation_service.proto`; generated Python code is kept under `experimentation_service/src/api/grpc/generated`.
- Event durability: domain events are collected through Unit of Work and written to an outbox table in the same transaction as aggregate persistence. Kafka publishing from the outbox is not implemented yet.
- Dependency injection: configuration, session factories, repositories, Unit of Work, and use cases are wired through Dishka.
- Configuration: runtime settings are loaded through `pydantic-settings` from environment variables and local `.env` files.
- Note: This combines the previously separate execution and experiments hypotheses. Split later only if the domain pressure becomes real.

### knowledge_service

- Language: Python
- Context: Knowledge & Decisions
- Primary responsibilities: decisions, decision rationale, insights, learning notes, knowledge links.
- Secondary responsibilities: documents, notes, collections.
- Contracts: record decision, record insight, create learning note, link knowledge, create/update supporting document, list knowledge.
- Events: `DecisionRecorded`, `InsightRecorded`, `LearningNoteCreated`, `KnowledgeLinked`, `DocumentCreated`, `DocumentUpdated`.
- Note: Do not turn this into a generic document service. Documents support the core model of decisions, insights, and learning.

### dashboard_service

- Language: Go
- Context: Dashboard read models.
- Responsibilities: read-optimized projections and cross-service operating views.
- Contracts: get workspace dashboard, get goal dashboard, get execution dashboard, get experiment dashboard.
- Event inputs: workspace, goal, task, experiment, evidence, decision, insight, and document events from Kafka.
- Note: This is CQRS-like, but only for dashboard reads. Source-of-truth writes stay in owning services.

### notification_service

- Language: Python
- Role: Supporting technical capability for notifications and integrations.
- Responsibilities: notification preferences, delivery, external integrations, side effects.
- Contracts: update preferences, connect integration, disconnect integration, send or queue notification.
- Events: `NotificationPreferenceUpdated`, `NotificationQueued`, `NotificationDelivered`, `IntegrationConnected`.
- Note: This is not a core bounded context and must not own core business state from other services. It may be delayed until other services produce events worth reacting to.

## Development Approach

- Develop iteratively with small PRs.
- Implement one vertical slice at a time.
- Use docs for architectural context and decisions.
- Start with documentation and instruction layer, then repository skeleton, then `workspace_service`, then `strategy_goals_service`, then `experimentation_service`, then other services.
- Avoid building advanced infrastructure before there is a real need.

## Current Repository Notes

- `experimentation_service` has domain models for hypotheses, experiments, initiatives, and tasks, initial persistence scaffolding using SQLAlchemy async ORM, Alembic, Unit of Work, outbox storage, Dishka wiring, and a first gRPC vertical slice for formulating hypotheses.
- `goals_service` exists but is not part of the accepted service map. Do not expand it unless a later cleanup or migration task explicitly addresses it.
