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
- Source-of-truth services publish domain events to Kafka after durable state changes.
- Kafka events describe facts that already happened.
- Event consumers must be idempotent.
- `dashboard_service` and `notification_service` are the first natural Kafka consumers.
- Do not use Kafka for user-facing request flows that require an immediate answer.
- Do not use direct database access across service boundaries.

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

- Role: Public API gateway and BFF.
- Responsibilities: route frontend requests, call internal services over gRPC, aggregate frontend-shaped responses, handle API-level auth/session concerns, normalize errors.
- Owns: client-facing API contracts and composition logic.
- Does not own: domain data, business workflows, persistence.
- Note: Keep it thin enough that domain behavior remains in owning services.

### workspace_service

- Context: Identity & Workspace
- Responsibilities: users, workspaces, memberships, invitations, roles, permissions, tenant isolation.
- Contracts: create workspace, invite member, accept invitation, list members, check access.
- Events: `WorkspaceCreated`, `MemberInvited`, `MemberJoinedWorkspace`, `RoleAssigned`.
- Note: This service is security-critical.

### strategy_goals_service

- Context: Strategy, Goals & Metrics
- Responsibilities: strategy, goals, measurable outcomes, metrics, progress tracking.
- Contracts: create goal, update goal, define metric, link metric to goal, update progress.
- Events: `GoalCreated`, `MetricCreated`, `MetricLinkedToGoal`, `GoalProgressUpdated`.
- Note: Goals and metrics stay together initially and may split later.

### experimentation_service

- Context: Experimentation, combining execution and experiments.
- Responsibilities: initiatives, tasks, ownership, statuses, deadlines, hypotheses, experiments, results, learnings, validation workflows.
- Contracts: create initiative, create task, assign task, change status, create hypothesis, start experiment, record result, complete experiment, capture learning.
- Events: `InitiativeCreated`, `TaskCreated`, `TaskAssigned`, `TaskCompleted`, `InitiativeCompleted`, `HypothesisCreated`, `ExperimentStarted`, `ExperimentCompleted`, `LearningCaptured`.
- Note: This combines the previously separate execution and experiments hypotheses. Split later only if the domain pressure becomes real.

### knowledge_service

- Context: Documents / Knowledge
- Responsibilities: documents, notes, decisions, knowledge organization, links to other domain objects.
- Contracts: create document, update document, link document, record decision, list knowledge.
- Events: `DocumentCreated`, `DocumentUpdated`, `DocumentLinked`, `DecisionRecorded`.
- Note: Search and rich knowledge graph features should wait.

### dashboard_service

- Context: Dashboard read models.
- Responsibilities: read-optimized projections and cross-service operating views.
- Contracts: get workspace dashboard, get goal dashboard, get execution dashboard, get experiment dashboard.
- Event inputs: workspace, goal, task, experiment, and document events from Kafka.
- Note: This is CQRS-like, but only for dashboard reads. Source-of-truth writes stay in owning services.

### notification_service

- Context: Notifications / Integrations
- Responsibilities: notification preferences, delivery, external integrations, side effects.
- Contracts: update preferences, connect integration, disconnect integration, send or queue notification.
- Events: `NotificationPreferenceUpdated`, `NotificationQueued`, `NotificationDelivered`, `IntegrationConnected`.
- Note: This service may be delayed until other services produce events worth reacting to.

## Development Approach

- Develop iteratively with small PRs.
- Implement one vertical slice at a time.
- Use docs for architectural context and decisions.
- Start with documentation and instruction layer, then repository skeleton, then `workspace_service`, then `strategy_goals_service`, then `experimentation_service`, then other services.
- Avoid building advanced infrastructure before there is a real need.

## Current Repository Notes

- `experimentation_service` already exists as a minimal Python service.
- `goals_service` exists but is not part of the accepted service map. Do not expand it unless a later cleanup or migration task explicitly addresses it.
