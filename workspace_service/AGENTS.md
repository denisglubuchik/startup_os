# workspace_service

Owns identity, workspace membership, permissions, and tenant isolation.

## Responsibility

- Users and workspace references.
- Workspaces.
- Memberships.
- Invitations.
- Roles and permissions.
- Tenant isolation and access decisions.

## Boundaries

- This service is security-critical.
- Other services must not read this service's database directly.
- Other services should use explicit gRPC APIs or trusted authorization context.
- Changes to membership, roles, permissions, invitations, or tenant isolation should test both allowed and forbidden access where practical.

## Communication

- gRPC: workspace creation, membership lookup, invitation flows, role/permission checks.
- Kafka events: `WorkspaceCreated`, `MemberInvited`, `MemberJoinedWorkspace`, `RoleAssigned`, `MemberRemoved`.

## Current State

Folder placeholder only. No runnable service skeleton exists yet.

## Launch

Not available until the service skeleton is implemented. Add the exact command here when the service has an application entrypoint.

## Tests

Not available until tests are added. Add the exact test command here when the service has a test suite.
