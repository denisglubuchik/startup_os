# knowledge_service

Owns decisions, insights, learning notes, and linked startup knowledge.

## Language

Python.

## Responsibility

- Decisions.
- Decision rationale.
- Insights.
- Learning notes.
- Knowledge links.
- Documents as supporting artifacts.
- Notes as supporting artifacts.
- Knowledge collections.
- Links between knowledge and goals, tasks, experiments, evidence, results, metrics, or workspaces.

## Boundaries

- Owns source-of-truth state for knowledge artifacts.
- Primary model is decisions, insights, learning notes, and knowledge links.
- Documents, notes, and collections are secondary supporting artifacts.
- Does not own goals, execution work, experiments, raw evidence, experiment results, or workspace membership.
- Must not directly access other service databases.
- Do not build this as a generic document service first.
- Search and rich knowledge graph features should wait until the decision and insight workflows are validated.

## Communication

- gRPC: record decisions, record insights, create learning notes, link knowledge, create/update supporting documents, list knowledge.
- Contract source of truth: protobuf-generated services/types.
- Kafka events: `DecisionRecorded`, `InsightRecorded`, `LearningNoteCreated`, `KnowledgeLinked`, `DocumentCreated`, `DocumentUpdated`.

## Current State

Folder placeholder only. No runnable service skeleton exists yet.

## Launch

Not available until the service skeleton is implemented. Add the exact command here when the service has an application entrypoint.

## Tests

Not available until tests are added. Add the exact test command here when the service has a test suite.
