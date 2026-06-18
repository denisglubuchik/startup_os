# Product

This document is a living draft.

## Vision

StartupOS is a SaaS platform for startup management. It helps startup teams connect strategy, goals, metrics, execution, experiments, evidence, decisions, and knowledge in one operating system.

Target users:

- startup founders
- early startup teams
- operators
- product and technology leads

Core problem: startup knowledge, strategy, goals, execution, and metrics are often fragmented across documents, spreadsheets, task tools, dashboards, and chat. This makes it harder to understand priorities, track progress, preserve decisions, and learn from experiments.

Intended value:

- strategy explains why work matters
- goals and metrics show what progress means
- initiatives and tasks organize execution
- experiments validate assumptions and produce evidence
- decisions, insights, and knowledge preserve what was learned and why it matters
- dashboards give a read-optimized view of startup operating state

## Scope

In scope:

- workspace management
- users, memberships, and roles
- strategy and goals
- metrics and progress tracking
- initiatives and tasks
- experiments
- knowledge, decisions, and supporting documents
- dashboards and operating views
- notifications and integrations later

Out of scope for the initial stage:

- billing
- complex analytics or BI
- marketplace
- advanced automation
- mobile apps
- heavy enterprise compliance

Build enough to support coherent startup operating workflows. Defer features that require heavy infrastructure or unclear domain assumptions.

## Glossary

- StartupOS: A SaaS platform for managing startup strategy, execution, metrics, experiments, and knowledge.
- Workspace: A tenant-level area where a startup team manages its work and knowledge.
- User: A person with an account in StartupOS.
- Member: A user who belongs to a workspace.
- Role: A named access level or responsibility set within a workspace.
- Permission: A specific allowed action or access rule.
- Strategy: The high-level direction, choices, and priorities for a startup.
- Goal: A desired outcome the team wants to achieve.
- Metric: A measurable signal used to track progress or performance.
- Initiative: A coordinated body of work intended to advance a goal or strategy.
- Task: A specific unit of execution work.
- Experiment: A structured test of a hypothesis.
- Hypothesis: A testable assumption about customers, product, market, or execution.
- Evidence: Information collected while running an experiment or validating an assumption.
- Experiment Result: The recorded outcome of an experiment.
- Insight: A meaningful interpretation of evidence, results, or operating experience.
- Decision: A recorded choice made by the team.
- Decision Rationale: The reasoning and evidence behind a decision.
- Learning Note: A knowledge artifact that captures what the team learned and why it matters.
- Document: A supporting written artifact such as a note, plan, or reference.
- Knowledge Base: The organized collection of decisions, insights, learning notes, documents, and links.
- Dashboard: A read-optimized view that combines operating data from multiple services.
- Notification: A message or alert about relevant activity.
- Integration: A connection between StartupOS and an external service.
- Bounded Context: A domain boundary where terms, rules, and models have a consistent meaning.
- Service: An independently owned application component aligned with a bounded context or clear capability.
- Tenant Isolation: The guarantee that data and access are separated between workspaces.
