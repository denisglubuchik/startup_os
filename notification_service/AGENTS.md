# notification_service

Owns notifications, preferences, delivery, and later integrations.

## Responsibility

- Notification preferences.
- Notification records.
- Delivery attempts.
- Delivery channels.
- External integration settings when introduced.

## Boundaries

- Reacts to domain events from other services.
- Does not own core business state from other services.
- Must not directly access other service databases.
- Delivery side effects should be idempotent where practical.

## Communication

- gRPC: update preferences, query notification state, manage integrations when introduced.
- Kafka consumers: events that should trigger notifications.
- Kafka events: `NotificationPreferenceUpdated`, `NotificationQueued`, `NotificationDelivered`, `IntegrationConnected`, `IntegrationDisconnected`.

## Current State

Folder placeholder only. No runnable service skeleton exists yet.

## Launch

Not available until the service skeleton is implemented. Add the exact command here when the service has an application entrypoint.

## Tests

Not available until tests are added. Add the exact test command here when the service has a test suite.
