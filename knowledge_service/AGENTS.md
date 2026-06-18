# knowledge_service

Owns documents, notes, decisions, and linked startup knowledge.

## Responsibility

- Documents.
- Notes.
- Decisions.
- Knowledge links.
- Knowledge collections.
- Links between knowledge and goals, tasks, experiments, metrics, or workspaces.

## Boundaries

- Owns source-of-truth state for knowledge artifacts.
- Does not own goals, execution work, experiments, or workspace membership.
- Must not directly access other service databases.
- Search and rich knowledge graph features should wait until simpler document workflows are validated.

## Communication

- gRPC: create/update documents, record decisions, link documents, list knowledge.
- Kafka events: `DocumentCreated`, `DocumentUpdated`, `DocumentLinked`, `DecisionRecorded`.

## Current State

Folder placeholder only. No runnable service skeleton exists yet.

## Launch

Not available until the service skeleton is implemented. Add the exact command here when the service has an application entrypoint.

## Tests

Not available until tests are added. Add the exact test command here when the service has a test suite.
