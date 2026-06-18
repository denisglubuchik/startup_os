# Domain

StartupOS connects the operating system of an early startup: strategy, goals, metrics, execution, experiments, evidence, decisions, and knowledge.

The core domain idea is that startup teams need a shared structure for deciding what matters, tracking whether it is working, executing against priorities, validating assumptions, and preserving what they learned and why decisions changed.

These bounded contexts are initial hypotheses, not final boundaries. The current service map intentionally combines execution and experiments into `experimentation_service`.

## Domain Areas

### Identity & Workspace

- Purpose: Manage users, workspaces, membership, permissions, and tenant isolation.
- Owns: users, workspaces, members, roles, permissions, invitations.
- Possible events: `WorkspaceCreated`, `MemberInvited`, `MemberJoinedWorkspace`, `RoleAssigned`, `MemberRemoved`.
- Relationships: Other contexts rely on workspace and member identity, but must not read identity persistence directly.
- Open questions: What permission model is enough for MVP? Are roles global templates, workspace-specific, or both?

### Strategy, Goals & Metrics

- Purpose: Model startup direction, desired outcomes, measurable progress, and strategic alignment.
- Owns: strategy, strategic directions, goals, metrics, measurable outcomes, progress updates.
- Possible events: `GoalCreated`, `GoalUpdated`, `MetricCreated`, `MetricLinkedToGoal`, `GoalProgressUpdated`.
- Relationships: Experimentation links work to goals; experiments validate assumptions; Knowledge & Decisions links decisions and insights to goals.
- Open questions: Should goals and metrics split later? Are key results first-class objects or metric relationships?

### Experimentation

- Purpose: Manage execution work and validation workflows together.
- Owns: initiatives, tasks, execution checklists, assignees, statuses, deadlines, hypotheses, experiments, evidence, experiment results, outcome interpretations, validation statuses.
- Possible events: `InitiativeCreated`, `TaskCreated`, `TaskAssigned`, `TaskCompleted`, `InitiativeCompleted`, `HypothesisCreated`, `ExperimentStarted`, `EvidenceAdded`, `ExperimentResultRecorded`, `ExperimentOutcomeInterpreted`, `ExperimentCompleted`.
- Relationships: Work connects to goals, experiments validate assumptions, and results can lead to insights, learning notes, and decisions in Knowledge & Decisions.
- Open questions: Should execution and experiments split later? Are initiatives required for MVP, or are tasks enough initially? Which evidence types are needed first?

### Knowledge & Decisions

- Purpose: Preserve what the team learned, what decision was made, why it was made, and what evidence it was based on.
- Primary ownership: decisions, decision rationale, insights, learning notes, knowledge links.
- Secondary ownership: documents, notes, collections.
- Possible events: `DecisionRecorded`, `InsightRecorded`, `LearningNoteCreated`, `KnowledgeLinked`, `DocumentCreated`, `DocumentUpdated`.
- Relationships: Links decisions and insights to goals, metrics, initiatives, tasks, experiments, evidence, and results.
- Boundary: Does not own raw experiment evidence or experiment results; those remain in Experimentation.
- Open questions: What is the minimum useful model for decisions and insights? When should documents become richer than supporting artifacts?

### Dashboard Read Models

- Purpose: Provide read-optimized operating views across services.
- Owns: derived dashboard projections and query models.
- Possible event inputs: workspace, goal, task, experiment, evidence, decision, insight, document, and notification events from Kafka.
- Relationships: Consumes events from source-of-truth services and may use gRPC for explicit query fallbacks.
- Open questions: Which dashboard views are needed first? Which projections are worth storing versus computed on demand?

## Supporting Technical Capabilities

### Notifications / Integrations

- Purpose: Provide notification delivery, external integration hooks, and event-driven side effects.
- Owns: notifications, preferences, integrations, delivery channels, external account references.
- Possible events: `NotificationPreferenceUpdated`, `NotificationQueued`, `NotificationDelivered`, `IntegrationConnected`.
- Relationships: May react to events from other contexts, but should not own core business state from other services.
- Boundary: Supporting technical capability, not a core bounded context.
- Open questions: Which notifications are essential for MVP? When should event-driven delivery be introduced?

## Open Questions

- Should Strategy, Goals & Metrics be one context or split later?
- Should Experimentation split into separate execution and experiments contexts later?
- What is the exact relationship between goals, metrics, initiatives, tasks, and experiments?
- What permission model is needed for MVP?
- What is the right split between experiment outcome interpretation and knowledge insights?
- Are documents just supporting artifacts, or do they become first-class linked knowledge objects?
- Which workflows are core for the first MVP?
- What should be event-driven later?
- What should remain synchronous?
- Which dashboard projections are needed for the first MVP?
- What should not be built yet?
- How should workspace-level roles interact with object-level permissions?
