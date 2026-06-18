# StartupOS Codex Guide

StartupOS is a SaaS platform for startup management. It is intended to connect startup strategy, goals, metrics, initiatives, tasks, experiments, evidence, decisions, knowledge, workflows, notifications, and integrations.

This repository is developed with Codex. Codex must read this file first at the start of a task, then route into the relevant project docs and rules below.

## Context Map

- Product context lives in `docs/product.md`.
- Domain context lives in `docs/domain.md`.
- Architecture context lives in `docs/architecture.md`.
- Accepted decisions and near-term plans live in `docs/decisions-and-plan.md`.
- Detailed Codex engineering rules live in `.codex/rules/startupos.md`.

## What To Read

- Read `.codex/rules/startupos.md` before implementation tasks.
- Read `docs/product.md` before changing product scope or user-facing behavior.
- Read `docs/domain.md` before changing domain models, use cases, permissions, workflows, or terminology.
- Read `docs/architecture.md` before changing service boundaries, persistence ownership, APIs, integrations, or deployment shape.
- Read `docs/decisions-and-plan.md` before changing accepted architecture decisions or following planned setup work.
- Read the local service `AGENTS.md` before editing files inside a service folder.

## Current Direction

StartupOS is intentionally microservice-oriented. This is a learning and engineering practice choice, not the simplest MVP path. Do not silently turn the project into a monolith.

Initial bounded context hypotheses are documented in `docs/domain.md` and accepted in `docs/decisions-and-plan.md`. Treat them as provisional. Update docs and decisions when architecture or domain boundaries change.

The accepted service map is: `api_gateway`, `workspace_service`, `strategy_goals_service`, `experimentation_service`, `knowledge_service`, `dashboard_service`, and `notification_service`.

Internal synchronous calls should use gRPC. Kafka is accepted for asynchronous domain events. CQRS-style read models are limited to `dashboard_service`; do not make the whole system CQRS. Do not introduce event sourcing, distributed transactions, or a new service for every small feature unless explicitly requested or already established.

## Engineering Principles

- Keep diffs focused on the requested task.
- Inspect relevant files before editing.
- Preserve meaningful existing content.
- Prefer small vertical slices over broad speculative foundations.
- Use domain language in names.
- Keep business rules out of controllers and transport adapters.
- Keep services responsible for their own domain model and persistence.
- Do not reformat unrelated files or upgrade dependencies without a reason tied to the task.

## Security And Multi-Tenancy

Workspace and tenant isolation are security-critical. Changes touching users, memberships, roles, permissions, invitations, or access control must consider allowed and forbidden access paths. Do not let one service directly read another service's database.

## Quality Gates

- Add or update tests for meaningful behavior changes.
- Run the relevant test or verification commands before claiming success.
- Do not claim tests passed unless they were actually run.
- Update docs or ADRs when a change alters architecture, domain boundaries, or development workflow.

## Final Response After Coding Tasks

End coding tasks with:

- what changed
- tests or checks run, with results
- files changed
- assumptions or follow-ups, if relevant
