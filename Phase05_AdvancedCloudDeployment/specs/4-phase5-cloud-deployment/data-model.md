# Data Model: Phase 5 Advanced Cloud Deployment

**Branch**: `main` | **Date**: 2026-02-10 | **Spec**: [spec.md](./spec.md)

## Existing Entities (Phase 2-4, Unchanged)

### User
| Field | Type | Constraints |
|-------|------|-------------|
| id | UUID | PK, auto-generated |
| email | VARCHAR(255) | UNIQUE, NOT NULL, indexed |
| password_hash | VARCHAR(255) | NOT NULL |
| name | VARCHAR(100) | NOT NULL |
| created_at | TIMESTAMP | NOT NULL, default now() |
| updated_at | TIMESTAMP | NOT NULL, default now() |
| last_login_at | TIMESTAMP | nullable |

### Task
| Field | Type | Constraints |
|-------|------|-------------|
| id | UUID | PK, auto-generated |
| user_id | UUID | FK → users.id, NOT NULL, indexed |
| title | VARCHAR(255) | NOT NULL |
| description | VARCHAR(1000) | nullable |
| status | VARCHAR(20) | NOT NULL, default "todo", indexed |
| priority | ENUM(high,medium,low,none) | NOT NULL, default "none", indexed |
| due_date | TIMESTAMP | nullable, indexed |
| recurrence_pattern | ENUM(none,daily,weekly,monthly,yearly) | NOT NULL, default "none" |
| tags | ARRAY(VARCHAR) | default [] |
| created_at | TIMESTAMP | NOT NULL, indexed |
| updated_at | TIMESTAMP | NOT NULL |
| completed_at | TIMESTAMP | nullable |

### Conversation (Phase 3)
| Field | Type | Constraints |
|-------|------|-------------|
| id | UUID | PK, auto-generated |
| user_id | UUID | FK → users.id, NOT NULL, indexed |
| created_at | TIMESTAMP | NOT NULL |
| updated_at | TIMESTAMP | NOT NULL |

### Message (Phase 3)
| Field | Type | Constraints |
|-------|------|-------------|
| id | UUID | PK, auto-generated |
| conversation_id | UUID | FK → conversations.id, NOT NULL, indexed |
| user_id | UUID | NOT NULL, indexed |
| role | VARCHAR(20) | NOT NULL (user/assistant/system) |
| content | TEXT | NOT NULL |
| tool_calls | JSON | nullable |
| created_at | TIMESTAMP | NOT NULL |

## New Entities (Phase 5)

### ProcessedEvent (Idempotency Tracking)

**Purpose**: Tracks which events have been processed by each consumer service to prevent duplicate processing.

| Field | Type | Constraints |
|-------|------|-------------|
| id | UUID | PK, auto-generated |
| event_id | UUID | NOT NULL |
| service_name | VARCHAR(50) | NOT NULL |
| processed_at | TIMESTAMP | NOT NULL, default now() |
| user_id | UUID | NOT NULL |

**Constraints**:
- UNIQUE(event_id, service_name) — prevents duplicate processing per service

**Used by**: notification-service, recurring-service

## Event Schemas (Kafka Topics)

### TaskEvent (topic: `task-events`)

Published by backend on every task CRUD operation.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| event_id | UUID | yes | Unique event identifier |
| event_type | STRING | yes | One of: task.created, task.updated, task.completed, task.deleted |
| task_id | UUID | yes | ID of the affected task |
| user_id | UUID | yes | ID of the user who performed the action |
| timestamp | ISO8601 | yes | When the event occurred |
| correlation_id | UUID | yes | For distributed tracing |
| task_data | OBJECT | yes* | Full task object (*null for task.deleted) |
| previous_data | OBJECT | no | Previous task state (for task.updated only) |

### ReminderEvent (topic: `reminders`)

Published by Dapr Jobs API callback when a reminder fires.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| event_id | UUID | yes | Unique event identifier |
| event_type | STRING | yes | Always "reminder.due" |
| task_id | UUID | yes | ID of the task |
| user_id | UUID | yes | ID of the user to notify |
| title | STRING | yes | Task title for notification display |
| due_at | ISO8601 | yes | When the task is due |
| remind_at | ISO8601 | yes | When the reminder was scheduled |
| timestamp | ISO8601 | yes | When the event was published |
| correlation_id | UUID | yes | For distributed tracing |

### TaskUpdateEvent (topic: `task-updates`, reserved for future)

Created for future real-time client sync. Topic created but no consumer in Phase 5.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| event_id | UUID | yes | Unique event identifier |
| event_type | STRING | yes | Type of update |
| task_id | UUID | yes | ID of the affected task |
| user_id | UUID | yes | ID of the user |
| timestamp | ISO8601 | yes | When the event occurred |
| task_data | OBJECT | yes | Current task state |

## Dapr Component Configurations

### pubsub.kafka (kafka-pubsub)
| Metadata Key | Minikube Value | Cloud Value |
|-------------|----------------|-------------|
| brokers | taskflow-kafka-kafka-bootstrap.kafka:9092 | {redpanda-cloud-url}:9092 |
| consumerGroup | todo-service | todo-service |
| authType | none | sasl (SCRAM-SHA-256) |
| maxMessageBytes | 1048576 | 1048576 |

### state.postgresql (statestore)
| Metadata Key | Value |
|-------------|-------|
| connectionString | {NEON_DB_URL} |
| tableName | dapr_state |
| metadataTableName | dapr_metadata |

### secretstores.kubernetes (kubernetes-secrets)
No additional metadata — uses default Kubernetes RBAC.

### bindings.cron (cron-binding)
Dapr Cron Binding for periodic background tasks (overdue reminders, cleanup jobs).

| Metadata Key | Value |
|-------------|-------|
| schedule | @every 5m |
| route | /api/cron/overdue-check |

```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: cron-binding
spec:
  type: bindings.cron
  version: v1
  metadata:
    - name: schedule
      value: "@every 5m"
    - name: route
      value: "/api/cron/overdue-check"
```

### Jobs API (scheduler)
Dapr Jobs API for exact-time reminder scheduling (per Use Case 4). Built-in feature, not a component — uses Dapr sidecar HTTP API directly at `http://localhost:3500/v1.0-alpha1/jobs/{name}`.

**Note**: Bindings (Cron) and Jobs API serve different purposes:
- **Bindings (Cron)**: Periodic batch operations (every X minutes)
- **Jobs API**: Exact-time scheduling for individual events (no polling)

## Entity Relationships

```
User (1) ──── (N) Task
User (1) ──── (N) Conversation
Conversation (1) ──── (N) Message
Task (1) ──── (N) TaskEvent [published to Kafka]
Task (1) ──── (N) ReminderEvent [published to Kafka]
ProcessedEvent ──── tracks events per service
```

## State Transitions

### Task Status
```
todo → completed (mark complete)
completed → todo (reopen)
any → deleted (soft/hard delete)
```

### Event Lifecycle
```
Operation → Event Published → Kafka Topic → Dapr Delivers → Consumer Processes → Idempotency Check → Action Taken
```

### Reminder Lifecycle
```
Task Created with due_date → Schedule Dapr Job → Job fires at remind_at → Publish ReminderEvent → Notification Service logs it
Task updated → Cancel old job → Schedule new job
Task deleted → Cancel associated job
```
