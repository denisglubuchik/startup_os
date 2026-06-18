# api_gateway

Public API gateway and BFF for StartupOS.

## Language

Go.

## Responsibility

- Exposes client-facing APIs.
- Routes requests to internal services through gRPC.
- Aggregates service responses for frontend use cases.
- Handles API-level auth/session concerns, request validation, error normalization, and response shaping.

## Boundaries

- Does not own domain data.
- Does not contain business workflows that belong in domain services.
- Does not directly access service databases.
- Should stay thin enough that source-of-truth behavior remains in owning services.

## Communication

- Inbound: frontend/client HTTP API.
- Outbound: gRPC to internal services.
- Contract source of truth: protobuf-generated clients/types.
- Kafka: only if gateway-level async needs appear later; not expected initially.

## Current State

Folder placeholder only. No runnable service skeleton exists yet.

## Launch

Not available until the service skeleton is implemented. Add the exact command here when the service has an application entrypoint.

## Tests

Not available until tests are added. Add the exact test command here when the service has a test suite.
