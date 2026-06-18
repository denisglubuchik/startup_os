# Domain

StartupOS connects the operating system of an early startup: strategy, goals, metrics, execution, experiments, and knowledge.

The core domain idea is that startup teams need a shared structure for deciding what matters, tracking whether it is working, executing against priorities, validating assumptions, and preserving what they learn.

These bounded contexts are initial hypotheses, not final boundaries. The current service map intentionally combines execution and experiments into `experimentation_service`.

## Contexts

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
- Relationships: Execution links work to goals; Experiments validate assumptions; Knowledge links documents and decisions to goals.
- Open questions: Should goals and metrics split later? Are key results first-class objects or metric relationships?

### Experimentation

- Purpose: Manage execution work and validation workflows together.
- Owns: initiatives, tasks, assignees, statuses, deadlines, hypotheses, experiments, results, learnings, validation statuses.
- Possible events: `InitiativeCreated`, `TaskCreated`, `TaskAssigned`, `TaskCompleted`, `InitiativeCompleted`, `HypothesisCreated`, `ExperimentStarted`, `ExperimentCompleted`, `LearningCaptured`.
- Relationships: Work connects to goals, experiments validate assumptions, and both can produce knowledge.
- Open questions: Should execution and experiments split later? Are initiatives required for MVP, or are tasks enough initially? Are learnings owned here or by Knowledge?

### Documents / Knowledge

- Purpose: Preserve documents, notes, decisions, learnings, and links between knowledge and other domain objects.
- Owns: documents, notes, decisions, knowledge links, collections.
- Possible events: `DocumentCreated`, `DocumentUpdated`, `DocumentLinked`, `DecisionRecorded`.
- Relationships: Links context to goals, initiatives, tasks, experiments, and metrics.
- Open questions: Are documents simple notes at first or first-class linked knowledge objects?

### Notifications / Integrations

- Purpose: Manage notification preferences, delivery, external integrations, and side effects.
- Owns: notifications, preferences, integrations, delivery channels, external account references.
- Possible events: `NotificationPreferenceUpdated`, `NotificationQueued`, `NotificationDelivered`, `IntegrationConnected`.
- Relationships: May react to events from other contexts, but should not own core business state from other services.
- Open questions: Which notifications are essential for MVP? When should event-driven delivery be introduced?

### Dashboard Read Models

- Purpose: Provide read-optimized operating views across services.
- Owns: derived dashboard projections and query models.
- Possible event inputs: workspace, goal, task, experiment, document, and notification events from Kafka.
- Relationships: Consumes events from source-of-truth services and may use gRPC for explicit query fallbacks.
- Open questions: Which dashboard views are needed first? Which projections are worth storing versus computed on demand?

## Open Questions

- Should Strategy, Goals & Metrics be one context or split later?
- Should Experimentation split into separate execution and experiments contexts later?
- What is the exact relationship between goals, metrics, initiatives, tasks, and experiments?
- What permission model is needed for MVP?
- Are documents just notes, or do they become first-class linked knowledge objects?
- Which workflows are core for the first MVP?
- What should be event-driven later?
- What should remain synchronous?
- Which dashboard projections are needed for the first MVP?
- What should not be built yet?
- How should workspace-level roles interact with object-level permissions?
