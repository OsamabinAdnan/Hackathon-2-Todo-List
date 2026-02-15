# Implementation Plan: Phase 5 Advanced Cloud Deployment

**Branch**: `main` | **Date**: 2026-02-10 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `specs/4-phase5-cloud-deployment/spec.md`

## Summary

Phase 5 transforms the Todo application from a monolithic deployment into an event-driven microservices architecture using Apache Kafka (via Strimzi) and Dapr. The backend publishes task lifecycle events to Kafka topics through the Dapr pub/sub API. Two new microservices — a notification service and a recurring task service — consume these events via Dapr subscriptions. All five Dapr building blocks (Pub/Sub, State Management, Service Invocation, Jobs API, Secrets Management) are utilized. The system deploys first to Minikube (local), then to Oracle Cloud OKE, with CI/CD via GitHub Actions.

## Technical Context

**Language/Version**: Python 3.13+ (backend, services), TypeScript/Node.js 22+ (frontend)
**Primary Dependencies**: FastAPI, SQLModel, httpx (Dapr HTTP client), Strimzi operator, Dapr 1.13+, Helm 3
**Storage**: Neon PostgreSQL (existing), Kafka (event streaming), Dapr state store (PostgreSQL-backed)
**Testing**: pytest (backend + services), Vitest (frontend)
**Target Platform**: Kubernetes (Minikube local, Oracle OKE cloud)
**Project Type**: Web application (monorepo with microservices)
**Performance Goals**: < 500ms API response (p95), < 2s event processing, 10,000 events/sec throughput
**Constraints**: No direct Kafka client libraries, all communication via Dapr HTTP API, Oracle OKE Always Free tier (4 OCPUs, 24GB RAM)
**Scale/Scope**: 4 services (frontend, backend, notification, recurring), 3 Kafka topics, 4 Dapr components

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Gate | Status | Evidence |
|------|--------|----------|
| Spec-Driven Development | PASS | spec.md created via /sp.specify with 7 user stories, 46 FRs |
| No Manual Coding | PASS | All code will be generated via /sp.implement |
| TDD (Red-Green-Refactor) | PASS | Tests written before implementation per tasks ordering |
| Subagents/Skills Used | PASS | Using event-stream-architect, kafka-operator, dapr-pubsub-integrator agents |
| Context7 Documentation | PENDING | Will lookup Dapr, Strimzi, httpx docs during implementation |
| Event-Driven First (Phase 5) | PASS | All inter-service communication via Dapr pub/sub + Kafka |
| Dapr Abstraction Layer (Phase 5) | PASS | All 5 building blocks specified: Pub/Sub, State, Service Invocation, Jobs, Secrets |
| Cloud-Native Portability (Phase 5) | PASS | Same Helm charts for Minikube/OKE via values files |

## Project Structure

### Documentation (this feature)

```text
specs/4-phase5-cloud-deployment/
├── spec.md                      # Feature specification
├── plan.md                      # This file
├── research.md                  # Phase 0 research decisions
├── data-model.md                # Entity and event schema definitions
├── quickstart.md                # Deployment guide
├── contracts/
│   └── events/
│       ├── task-event-schema.json    # TaskEvent JSON Schema
│       └── reminder-event-schema.json # ReminderEvent JSON Schema
├── checklists/
│   └── requirements.md          # Spec quality checklist
└── tasks.md                     # Task breakdown (created by /sp.tasks)
```

### Source Code (repository root)

```text
backend/
├── app/
│   ├── main.py                  # FastAPI app (MODIFY: add Dapr subscription endpoint)
│   ├── config/
│   │   └── settings.py          # (MODIFY: add Dapr config)
│   ├── models/
│   │   ├── task.py              # Existing task model (NO CHANGE)
│   │   └── processed_event.py   # NEW: idempotency tracking model
│   ├── routes/
│   │   ├── tasks.py             # (MODIFY: add event publishing after CRUD)
│   │   └── chat.py              # (NO CHANGE)
│   ├── mcp/
│   │   └── tools.py             # (MODIFY: add event publishing after tool execution)
│   ├── publishers/
│   │   ├── __init__.py          # NEW
│   │   ├── base_publisher.py    # NEW: Dapr HTTP pub/sub base class
│   │   └── task_event_publisher.py # NEW: task event publishing functions
│   ├── services/
│   │   └── reminder_scheduler.py # NEW: Dapr Jobs API scheduling
│   └── middleware/
│       └── auth.py              # (NO CHANGE)
├── tests/
│   ├── test_dapr_publishing.py  # NEW: event publishing tests
│   ├── test_event_schemas.py    # NEW: schema validation tests
│   └── test_task_routes_events.py # NEW: integration tests
├── Dockerfile                   # (MODIFY: add httpx dependency)
└── requirements.txt             # (MODIFY: add httpx)

services/
├── notification-service/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI app with Dapr subscription
│   │   ├── config/
│   │   │   ├── __init__.py
│   │   │   └── settings.py
│   │   ├── consumers/
│   │   │   ├── __init__.py
│   │   │   └── reminder_consumer.py
│   │   └── utils/
│   │       ├── __init__.py
│   │       └── idempotency.py
│   ├── tests/
│   │   ├── test_reminder_consumer.py
│   │   ├── test_idempotency.py
│   │   └── test_dapr_subscription.py
│   ├── Dockerfile
│   └── requirements.txt
│
└── recurring-service/
    ├── app/
    │   ├── __init__.py
    │   ├── main.py              # FastAPI app with Dapr subscription
    │   ├── config/
    │   │   ├── __init__.py
    │   │   └── settings.py
    │   ├── consumers/
    │   │   ├── __init__.py
    │   │   └── task_completion_consumer.py
    │   └── utils/
    │       ├── __init__.py
    │       ├── recurrence_calculator.py
    │       └── idempotency.py
    ├── tests/
    │   ├── test_task_completion_consumer.py
    │   ├── test_recurrence_calculator.py
    │   └── test_idempotency.py
    ├── Dockerfile
    └── requirements.txt

dapr-components/
├── minikube/
│   ├── pubsub-kafka.yaml        # Kafka pub/sub component
│   ├── state-postgresql.yaml    # PostgreSQL state store
│   └── secretstore-kubernetes.yaml # K8s secrets component
└── production/
    ├── pubsub-kafka.yaml        # Production Kafka pub/sub
    ├── state-postgresql.yaml    # Production state store
    └── secretstore-kubernetes.yaml # Production secrets

kubernetes/
├── strimzi-operator.yaml        # Strimzi operator install reference
├── kafka-cluster-minikube.yaml  # Kafka cluster for Minikube (1 replica)
├── kafka-cluster-production.yaml # Kafka cluster for OKE (3 replicas)
└── kafka-topics.yaml            # KafkaTopic CRDs (task-events, reminders, task-updates)

helm/todo-chatbot/
├── Chart.yaml                   # (MODIFY: bump to 2.0.0)
├── values.yaml                  # (MODIFY: add Dapr + service configs)
├── values-minikube.yaml         # NEW: Minikube-specific values
├── values-staging.yaml          # NEW: staging values
├── values-production.yaml       # NEW: production OKE values
├── templates/
│   ├── backend-deployment.yaml  # (MODIFY: add Dapr annotations)
│   ├── frontend-deployment.yaml # (MODIFY: add Dapr annotations)
│   ├── notification-deployment.yaml # NEW
│   ├── notification-service.yaml    # NEW
│   ├── recurring-deployment.yaml    # NEW
│   ├── recurring-service.yaml       # NEW
│   └── NOTES.txt                # (MODIFY: add Phase 5 instructions)

scripts/
├── setup-kafka-strimzi.sh       # NEW: Kafka setup automation
├── setup-dapr.sh                # NEW: Dapr installation
├── deploy-minikube-phase5.sh    # NEW: single-command Minikube deploy
├── deploy-oke-phase5.sh         # NEW: OKE cloud deploy
├── verify-phase5.sh             # NEW: health and event flow verification
├── test-event-flow.sh           # NEW: end-to-end event test
└── cleanup-phase5.sh            # NEW: teardown all Phase 5 resources

.github/workflows/
├── build-and-test.yml           # NEW: build + test on push
├── deploy-staging.yml           # NEW: deploy staging on push to main
└── deploy-production.yml        # NEW: deploy production on tag v*
```

**Structure Decision**: Monorepo with microservices pattern. Backend stays in `backend/`, new consumer services in `services/`. Infrastructure configs in `dapr-components/` and `kubernetes/`. Helm chart extended in `helm/todo-chatbot/`.

## Architecture

### Component Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         KUBERNETES CLUSTER (Minikube / OKE)                  │
│                                                                             │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────────────┐  │
│  │  Frontend Pod     │  │  Backend Pod     │  │  Notification Pod        │  │
│  │ ┌──────┐ ┌─────┐ │  │ ┌──────┐ ┌─────┐│  │ ┌──────────┐ ┌────────┐ │  │
│  │ │Next.js│ │Dapr │ │  │ │Fast  │ │Dapr ││  │ │Notif     │ │Dapr    │ │  │
│  │ │ :3000 │ │Side │ │  │ │API   │ │Side ││  │ │Service   │ │Sidecar │ │  │
│  │ │       │←→│car  │ │  │ │:8000 │←→│car  ││  │ │:8001     │←→│        │ │  │
│  │ └──────┘ └─────┘ │  │ └──────┘ └─────┘│  │ └──────────┘ └────────┘ │  │
│  └──────────────────┘  └──────────────────┘  └──────────────────────────┘  │
│                              │                          │                   │
│  ┌──────────────────────┐    │    ┌─────────────────────┤                   │
│  │  Recurring Task Pod  │    │    │                     │                   │
│  │ ┌──────────┐ ┌─────┐ │   │    │                     │                   │
│  │ │Recurring │ │Dapr │ │   │    │                     │                   │
│  │ │Service   │ │Side │ │   │    │                     │                   │
│  │ │:8002     │←→│car  │ │   │    │                     │                   │
│  │ └──────────┘ └─────┘ │   │    │                     │                   │
│  └──────────────────────┘   │    │                     │                   │
│                              │    │                     │                   │
│  ┌───────────────────────────┴────┴─────────────────────┘                  │
│  │                    DAPR CONTROL PLANE                                    │
│  │  ┌────────────────┐ ┌──────────────┐ ┌─────────────┐ ┌──────────────┐  │
│  │  │ pubsub.kafka   │ │state.postgres│ │secretstore  │ │  Jobs API    │  │
│  │  │ (Kafka broker) │ │ (Neon DB)    │ │ (K8s)       │ │ (scheduler)  │  │
│  │  └───────┬────────┘ └──────┬───────┘ └──────┬──────┘ └──────┬───────┘  │
│  └──────────┼─────────────────┼────────────────┼───────────────┼──────────┘│
│             │                 │                │               │            │
│  ┌──────────▼────────┐  ┌────▼──────┐         │               │            │
│  │ Kafka Cluster     │  │ Neon DB   │         │               │            │
│  │ (Strimzi)         │  │ (External)│    K8s Secrets     Dapr Runtime      │
│  │ ┌──────────────┐  │  └───────────┘                                      │
│  │ │ task-events   │  │                                                     │
│  │ │ reminders     │  │                                                     │
│  │ │ task-updates  │  │                                                     │
│  │ └──────────────┘  │                                                     │
│  └───────────────────┘                                                     │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Event Flow

```
1. User creates/updates/completes/deletes task
   → Backend REST API or MCP tool handles request
   → Task persisted to Neon DB
   → Backend publishes TaskEvent via Dapr pub/sub HTTP API
   → Kafka stores event in task-events topic

2. Reminder scheduling
   → Task created with due_date + remind_at
   → Backend schedules Dapr Job at remind_at time
   → At scheduled time, Dapr calls /api/jobs/trigger callback
   → Backend publishes ReminderEvent to reminders topic

3. Notification processing
   → Dapr delivers ReminderEvent to notification-service
   → Service checks idempotency (processed_events table)
   → If new: logs notification, marks event processed
   → If duplicate: skips silently

4. Recurring task processing
   → Dapr delivers TaskEvent (task.completed) to recurring-service
   → Service checks if task has recurrence_pattern != "none"
   → If recurring: calculates next due date, calls backend API to create new task
   → Idempotency prevents duplicate task creation
```

### Dapr Building Block Usage Map (All 5 per Part B)

| Building Block | Service(s) | Usage |
|---------------|-----------|-------|
| **Pub/Sub** | Backend → Kafka → notification-service, recurring-service | Task events, reminder events |
| **State Management** | Backend | Conversation state via Dapr state API |
| **Service Invocation** | Frontend → Backend, recurring-service → Backend | HTTP calls via Dapr sidecar |
| **Bindings (Cron)** | Backend | Periodic batch operations (overdue task scans every 5 min) |
| **Secrets Management** | All services | Retrieve DB URLs, API keys, JWT secrets |

**Additionally (per Use Case 4)**:
| **Jobs API** | Backend | Schedule individual reminders at exact times (no polling) |

**Note**: Both Bindings (Cron) and Jobs API are used — Bindings satisfies Part B requirement, Jobs API follows Use Case 4 recommendation. See R-002 in research.md for detailed rationale.

## Implementation Phases

### Phase 0: Setup (Foundation)
1. Create directory structure: `services/`, `dapr-components/`, `kubernetes/`
2. Add httpx dependency to backend
3. Create Dapr component YAML files (Minikube + production)
4. Create Kafka infrastructure YAML files (Strimzi operator, cluster, topics)

### Phase 1: Event Publishing (US1 — P1)
1. **Tests first**: Write failing tests for event publishing
2. Create `backend/app/publishers/base_publisher.py` — Dapr HTTP pub/sub base
3. Create `backend/app/publishers/task_event_publisher.py` — publish functions
4. Modify `backend/app/routes/tasks.py` — call publisher after CRUD
5. Modify `backend/app/mcp/tools.py` — call publisher after tool execution
6. Add Dapr config to `backend/app/config/settings.py`

### Phase 2: Reminder System (US2 — P2)
1. **Tests first**: Write failing tests for reminder scheduling and notification
2. Create `backend/app/services/reminder_scheduler.py` — Dapr Jobs API
3. Create notification-service (full microservice)
4. Implement idempotent event processing

### Phase 3: Recurring Tasks (US3 — P2)
1. **Tests first**: Write failing tests for recurrence calculation and consumption
2. Create recurring-service (full microservice)
3. Implement recurrence date calculator (daily, weekly, monthly with edge cases)
4. Implement idempotent event processing

### Phase 4: Dapr Integration (US4 — P1)
1. Configure State Management for conversation state
2. Configure Service Invocation for frontend → backend
3. Configure Secrets Management for all services
4. Verify all 5 building blocks operational

### Phase 5: Minikube Deployment (US5 — P1)
1. Create/update Helm chart templates (Dapr annotations, new services)
2. Create deployment scripts (setup-kafka, setup-dapr, deploy-minikube)
3. Create verification and cleanup scripts
4. End-to-end validation

### Phase 6: Cloud Deployment (US6 — P3)
1. Create production Helm values for Oracle OKE
2. Create OKE deployment script
3. Configure Ingress with TLS

### Phase 7: CI/CD Pipeline (US7 — P3)
1. Create GitHub Actions workflows
2. Configure staging and production deployment pipelines
3. Implement automatic rollback on health check failure

## Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Event publishing via Dapr HTTP API | httpx POST to localhost:3500 | Project mandate: no direct Kafka libraries |
| Reminder scheduling | Dapr Jobs API | Phase05_Project.md Use Case 4: exact-time, no polling |
| Kafka operator | Strimzi | Free, Kubernetes-native, CRD-based topic management |
| Consumer task creation | Via backend REST API (Dapr service invocation) | Backend remains single source of truth for task CRUD |
| Idempotency | processed_events DB table | Persistent across restarts, simple to implement |
| Cloud target | Oracle OKE Always Free | No time-limited credits |
| State management | Dapr state.postgresql | Demonstrates Dapr capability with existing Neon DB |

## Risk Register

| Risk | Mitigation | Fallback |
|------|-----------|----------|
| Dapr Jobs API is alpha | Monitor releases, test thoroughly | Switch to cron bindings |
| Strimzi resource-heavy on Minikube | Use ephemeral storage, 1 replica | Use Redpanda single binary |
| OKE free tier resources exhausted | Monitor usage, efficient resource requests | Stay on Minikube for demo |
| Event ordering across partitions | Use user_id as partition key | Accept eventual consistency |
