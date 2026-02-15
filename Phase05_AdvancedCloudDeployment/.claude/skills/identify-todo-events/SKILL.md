---
name: identify-todo-events
description: Scans Todo features and generates a complete list of domain events (e.g., task.created, task.updated, task.completed, task.recurring.rescheduled, task.reminder.triggered) with triggers, producers, and consumers. Use when analyzing Todo application features to identify potential domain events for event-driven architecture.
---

# Identify Todo Events

This skill helps identify domain events in a Todo application by analyzing features and generating a complete list of events with their triggers, producers, and consumers.

## When to Use This Skill

Use this skill when:
- Designing event-driven architecture for a Todo application
- Analyzing existing Todo features to identify potential domain events
- Planning event sourcing or CQRS patterns
- Implementing Kafka topics or other messaging infrastructure
- Documenting system events for observability

## Event Identification Process

### 1. Analyze Todo Features
Scan all Todo application features to identify state changes and business operations that should produce events.

Common Todo features that generate events:
- Task management (create, update, delete, complete)
- User management (signup, login, profile updates)
- Recurring tasks (generation, rescheduling)
- Reminders and notifications
- Priority changes
- Due date modifications
- Tags and categorization
- Collaboration features (sharing, assignments)

### 2. Define Event Categories
Organize events into logical categories:

**Task Events:**
- `task.created`
- `task.updated`
- `task.deleted`
- `task.completed`
- `task.reopened`
- `task.priority.changed`
- `task.due.date.changed`
- `task.assigned`
- `task.tag.added`
- `task.tag.removed`

**User Events:**
- `user.registered`
- `user.profile.updated`
- `user.logged.in`
- `user.logged.out`
- `user.settings.changed`

**Recurring Task Events:**
- `recurring.task.generated`
- `recurring.task.rescheduled`
- `recurring.task.skipped`

**Reminder Events:**
- `reminder.scheduled`
- `reminder.triggered`
- `reminder.dismissed`
- `reminder.rescheduled`

### 3. Document Event Details
For each event, specify:

- **Event Name**: Standardized name following convention (domain.action.object)
- **Producer**: Component that generates the event
- **Consumer(s)**: Components that react to the event
- **Trigger**: Action or condition that causes the event
- **Payload**: Required and optional data fields
- **Metadata**: Timestamp, user context, correlation IDs

### 4. Event Payload Schema
Define the structure of each event payload:

```json
{
  "eventId": "unique identifier",
  "eventType": "task.created",
  "timestamp": "ISO 8601 timestamp",
  "userId": "user identifier",
  "correlationId": "request correlation",
  "data": {
    // Event-specific data
  },
  "metadata": {
    "source": "producing service",
    "version": "payload schema version"
  }
}
```

## Event Mapping Example

| Event | Producer | Consumers | Trigger |
|-------|----------|-----------|---------|
| `task.created` | Task Service | Notification Service, Analytics Service | User creates a new task |
| `task.completed` | Task Service | Notification Service, Stats Service | User marks task as complete |
| `reminder.triggered` | Scheduler Service | Notification Service | Scheduled reminder time reached |

## Output Format

Generate a complete event catalog in the following format:

```
## Domain Events Catalog

### Task Events
- `task.created`: [Description and details]
- `task.updated`: [Description and details]
- ...

### User Events
- `user.registered`: [Description and details]
- ...

### Recurring Task Events
- `recurring.task.generated`: [Description and details]
- ...

### Reminder Events
- `reminder.scheduled`: [Description and details]
- ...
```

## Best Practices

- Follow consistent naming conventions (lowercase with dots as separators)
- Make events immutable (represent state changes, not commands)
- Include sufficient context in event payloads
- Use correlation IDs for tracing across services
- Version event schemas when evolving
- Consider event partitioning strategy for scalable consumption