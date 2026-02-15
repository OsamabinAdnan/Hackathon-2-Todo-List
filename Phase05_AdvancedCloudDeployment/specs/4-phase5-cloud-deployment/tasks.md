# Tasks: Phase 5 Advanced Cloud Deployment

**Input**: Design documents from `specs/4-phase5-cloud-deployment/`
**Prerequisites**: plan.md ✅, spec.md ✅, research.md ✅, data-model.md ✅, quickstart.md ✅, contracts/events/ ✅
**Date**: 2026-02-13

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Foundation Infrastructure)

**Purpose**: Project initialization, directory structure, and core dependencies

- [x] T001 Create directory structure: `services/notification-service/`, `services/recurring-service/`, `dapr-components/minikube/`, `dapr-components/production/`, `kubernetes/`, `scripts/`
- [x] T002 [P] Add httpx dependency to `backend/requirements.txt` for Dapr HTTP client
- [x] T003 [P] Create `backend/app/publishers/__init__.py` package initialization
- [x] T004 [P] Create `services/notification-service/requirements.txt` with FastAPI, httpx, SQLModel dependencies
- [x] T005 [P] Create `services/recurring-service/requirements.txt` with FastAPI, httpx, SQLModel dependencies
- [x] T006 [P] Create notification-service project structure: `app/__init__.py`, `app/config/__init__.py`, `app/consumers/__init__.py`, `app/utils/__init__.py`
- [x] T007 [P] Create recurring-service project structure: `app/__init__.py`, `app/config/__init__.py`, `app/consumers/__init__.py`, `app/utils/__init__.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

### Kafka Infrastructure

- [x] T008 Create `kubernetes/kafka-cluster-minikube.yaml` with Strimzi Kafka CRD (1 replica, ephemeral storage)
- [x] T009 [P] Create `kubernetes/kafka-cluster-production.yaml` with Strimzi Kafka CRD (3 replicas, persistent storage)
- [x] T010 Create `kubernetes/kafka-topics.yaml` with KafkaTopic CRDs for `task-events`, `reminders`, `task-updates` topics
- [x] T011 Create `scripts/setup-kafka-strimzi.sh` to install Strimzi operator and deploy Kafka cluster

### Dapr Components (All 5 Building Blocks)

- [x] T012 Create `dapr-components/minikube/pubsub-kafka.yaml` with Kafka pub/sub component (FR-024)
- [x] T013 [P] Create `dapr-components/minikube/state-postgresql.yaml` with PostgreSQL state store (FR-025)
- [x] T014 [P] Create `dapr-components/minikube/secretstore-kubernetes.yaml` with K8s secrets component (FR-028)
- [x] T015 [P] Create `dapr-components/minikube/cron-binding.yaml` for periodic overdue task checks (FR-027)
- [x] T016 [P] Create `dapr-components/production/pubsub-kafka.yaml` for cloud environment
- [x] T017 [P] Create `dapr-components/production/state-postgresql.yaml` for cloud environment
- [x] T018 [P] Create `dapr-components/production/secretstore-kubernetes.yaml` for cloud environment
- [x] T019 Create `scripts/setup-dapr.sh` to install Dapr on Kubernetes cluster

### Base Models and Configuration

- [x] T020 Add Dapr configuration settings to `backend/app/config/settings.py` (DAPR_HTTP_PORT, PUBSUB_NAME, STATE_STORE_NAME)
- [x] T021 Create `backend/app/models/processed_event.py` with ProcessedEvent SQLModel for idempotency tracking
- [x] T022 Create `services/notification-service/app/config/settings.py` with service configuration
- [x] T023 [P] Create `services/recurring-service/app/config/settings.py` with service configuration

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - Event-Driven Task Operations (Priority: P1) 🎯 MVP

**Goal**: All task CRUD operations publish events to Kafka via Dapr pub/sub for downstream service consumption

**Independent Test**: Create/update/complete/delete tasks via REST API and MCP tools. Verify events appear on `task-events` topic using Kafka consumer or Dapr pub/sub subscription test.

### Implementation for User Story 1

- [x] T024 [P] [US1] Create `backend/app/publishers/base_publisher.py` with DaprPublisher base class for HTTP pub/sub
- [x] T025 [US1] Create `backend/app/publishers/task_event_publisher.py` with publish_task_event() function following task-event-schema.json
- [x] T026 [US1] Modify `backend/app/routes/tasks.py` to call publish_task_event() after create_task endpoint (FR-001)
- [x] T027 [US1] Modify `backend/app/routes/tasks.py` to call publish_task_event() after update_task endpoint (FR-002)
- [x] T028 [US1] Modify `backend/app/routes/tasks.py` to call publish_task_event() after complete_task endpoint (FR-003)
- [x] T029 [US1] Modify `backend/app/routes/tasks.py` to call publish_task_event() after delete_task endpoint (FR-004)
- [x] T030 [US1] Modify `backend/app/mcp/tools.py` add_task tool to call publish_task_event() (FR-001)
- [x] T031 [US1] Modify `backend/app/mcp/tools.py` update_task tool to call publish_task_event() (FR-002)
- [x] T032 [US1] Modify `backend/app/mcp/tools.py` complete_task tool to call publish_task_event() (FR-003)
- [x] T033 [US1] Modify `backend/app/mcp/tools.py` delete_task tool to call publish_task_event() (FR-004)
- [x] T034 [US1] Add non-blocking error handling for event publishing failures in base_publisher.py (FR-006)
- [x] T035 [US1] Add correlation_id generation and propagation in task_event_publisher.py (FR-005)

**Checkpoint**: Task events are published to Kafka. US1 is independently testable.

---

## Phase 4: User Story 4 - Dapr-Abstracted Service Communication (Priority: P1)

**Goal**: All inter-service communication abstracted through all 5 Dapr building blocks for multi-cloud portability

**Independent Test**: Deploy services with Dapr sidecars. Verify services use Dapr HTTP APIs. Swap Dapr component config and verify services work without code changes.

### Implementation for User Story 4

- [x] T036 [P] [US4] Create `backend/app/services/dapr_state.py` for Dapr State Management API wrapper (FR-025)
- [x] T037 [US4] Modify `backend/app/routes/chat.py` to use Dapr state API for conversation state storage
- [x] T038 [P] [US4] Create `backend/app/services/dapr_secrets.py` for Dapr Secrets API wrapper (FR-028)
- [x] T039 [US4] Modify `backend/app/config/settings.py` to fetch secrets via Dapr Secrets API at startup
- [x] T040 [P] [US4] Create `backend/app/routes/cron.py` with `/api/cron/overdue-check` endpoint for Dapr Cron Binding (FR-027)
- [x] T041 [US4] Register cron endpoint in `backend/app/main.py` router
- [x] T042 [P] [US4] Add Dapr subscription declaration endpoint `/dapr/subscribe` to `backend/app/main.py` (FR-030)
- [x] T043 [US4] Add Dapr app-id annotation configuration to backend for Service Invocation (FR-026)

**Checkpoint**: All 5 Dapr building blocks operational. US4 is independently testable.

---

## Phase 5: User Story 2 - Automated Reminder Notifications (Priority: P2)

**Goal**: Users receive timely reminder notifications via event-driven processing using Dapr Jobs API

**Independent Test**: Create task with due date and reminder time. Verify reminder event published at scheduled time. Verify notification service logs the reminder.

### Implementation for User Story 2

- [x] T044 [P] [US2] Create `backend/app/services/reminder_scheduler.py` with Dapr Jobs API scheduling (FR-008)
- [x] T045 [US2] Create `/api/jobs/trigger` callback endpoint in `backend/app/routes/jobs.py` for Dapr Jobs API (FR-009)
- [x] T046 [US2] Register jobs router in `backend/app/main.py`
- [x] T047 [US2] Modify `backend/app/routes/tasks.py` create_task to schedule reminder via Jobs API when remind_at is set
- [x] T048 [US2] Modify `backend/app/routes/tasks.py` update_task to reschedule reminder when remind_at changes (FR-010)
- [x] T049 [US2] Modify `backend/app/routes/tasks.py` delete_task to cancel reminder job (FR-011)
- [x] T050 [P] [US2] Create `backend/app/publishers/reminder_event_publisher.py` following reminder-event-schema.json
- [x] T051 [US2] Integrate reminder event publishing into jobs trigger callback

### Notification Service

- [x] T052 [P] [US2] Create `services/notification-service/app/main.py` FastAPI application with Dapr subscription (FR-012)
- [x] T053 [US2] Create `services/notification-service/app/consumers/reminder_consumer.py` for `reminders` topic (FR-013, FR-014)
- [x] T054 [US2] Create `services/notification-service/app/utils/idempotency.py` for duplicate event detection (FR-015)
- [x] T055 [US2] Add `/health` and `/ready` endpoints to notification-service (FR-045)
- [x] T056 [US2] Add `/dapr/subscribe` endpoint to notification-service declaring `reminders` subscription (FR-030)
- [x] T057 [US2] Create `services/notification-service/Dockerfile` with Dapr-compatible configuration (FR-016)

**Checkpoint**: Reminder scheduling and notification service operational. US2 is independently testable.

---

## Phase 6: User Story 3 - Recurring Task Automation (Priority: P2)

**Goal**: Completing a recurring task automatically creates the next occurrence via event-driven processing

**Independent Test**: Create recurring tasks (daily/weekly/monthly). Mark complete. Verify next occurrence created with correct date.

### Implementation for User Story 3

- [x] T058 [P] [US3] Create `services/recurring-service/app/main.py` FastAPI application with Dapr subscription (FR-017)
- [x] T059 [US3] Create `services/recurring-service/app/consumers/task_completion_consumer.py` for `task-events` topic (FR-018, FR-019)
- [x] T060 [US3] Create `services/recurring-service/app/utils/recurrence_calculator.py` for date calculations (FR-020, FR-021)
- [x] T061 [US3] Create `services/recurring-service/app/utils/idempotency.py` for duplicate event detection (FR-022)
- [x] T062 [US3] Add `/health` and `/ready` endpoints to recurring-service (FR-045)
- [x] T063 [US3] Add `/dapr/subscribe` endpoint to recurring-service declaring `task-events` subscription (FR-030)
- [x] T064 [US3] Implement Dapr Service Invocation to call backend API for creating next task occurrence
- [x] T065 [US3] Create `services/recurring-service/Dockerfile` with Dapr-compatible configuration (FR-023)

**Checkpoint**: Recurring task automation operational. US3 is independently testable.

---

## Phase 7: User Story 5 - Local Minikube Deployment (Priority: P1)

**Goal**: Single-command deployment of complete event-driven system to Minikube for local testing

**Independent Test**: Fresh Minikube cluster → run deploy script → all pods running with Dapr sidecars → events flow correctly → health checks pass

### Helm Chart Updates

- [x] T066 [P] [US5] Update `helm/todo-chatbot/Chart.yaml` to version 2.0.0 with Phase 5 metadata
- [x] T067 [US5] Update `helm/todo-chatbot/values.yaml` with Dapr sidecar and new service configurations
- [x] T068 [P] [US5] Create `helm/todo-chatbot/values-minikube.yaml` with Minikube-specific overrides
- [x] T069 [US5] Modify `helm/todo-chatbot/templates/backend-deployment.yaml` to add Dapr annotations (FR-038)
- [x] T070 [P] [US5] Modify `helm/todo-chatbot/templates/frontend-deployment.yaml` to add Dapr annotations (FR-038)
- [x] T071 [US5] Create `helm/todo-chatbot/templates/notification-deployment.yaml` with Dapr annotations (FR-038)
- [x] T072 [P] [US5] Create `helm/todo-chatbot/templates/notification-service.yaml` K8s Service resource
- [x] T073 [US5] Create `helm/todo-chatbot/templates/recurring-deployment.yaml` with Dapr annotations (FR-038)
- [x] T074 [P] [US5] Create `helm/todo-chatbot/templates/recurring-service.yaml` K8s Service resource
- [x] T075 [US5] Update `helm/todo-chatbot/templates/NOTES.txt` with Phase 5 deployment instructions

### Deployment Scripts

- [x] T076 [US5] Create `scripts/deploy-minikube-phase5.sh` for single-command Minikube deployment (FR-035)
- [x] T077 [P] [US5] Create `scripts/verify-phase5.sh` to validate pods, sidecars, health, and event flow (FR-036)
- [x] T078 [P] [US5] Create `scripts/test-event-flow.sh` for end-to-end event verification
- [x] T079 [P] [US5] Create `scripts/cleanup-phase5.sh` to remove all Phase 5 resources (FR-039)

### Docker Images

- [x] T080 [US5] Update `backend/Dockerfile` with httpx dependency and Dapr-compatible entrypoint
- [x] T081 [P] [US5] Build and test notification-service Docker image locally
- [x] T082 [P] [US5] Build and test recurring-service Docker image locally

**Checkpoint**: Complete Minikube deployment operational. US5 is independently testable.

---

## Phase 8: User Story 6 - Cloud Deployment (Oracle OKE) (Priority: P3)

**Goal**: Production deployment to Oracle Cloud OKE using same Helm charts with cloud-specific values

**Independent Test**: Deploy to OKE with production values → external access via Ingress with TLS → verification scripts pass

### Implementation for User Story 6

- [ ] T083 [P] [US6] Create `helm/todo-chatbot/values-staging.yaml` for staging environment
- [ ] T084 [US6] Create `helm/todo-chatbot/values-production.yaml` for Oracle OKE with production configs (FR-037)
- [ ] T085 [P] [US6] Create Ingress template in `helm/todo-chatbot/templates/ingress.yaml` with TLS configuration
- [ ] T086 [US6] Create `scripts/deploy-oke-phase5.sh` for Oracle OKE deployment
- [ ] T087 [US6] Update production Kafka config for Strimzi or Redpanda Cloud integration (FR-031)
- [ ] T088 [US6] Configure OCI Container Registry integration for image push

**Checkpoint**: Oracle OKE deployment operational. US6 is independently testable.

---

## Phase 9: User Story 7 - CI/CD Pipeline (Priority: P3)

**Goal**: Automated build, test, and deployment pipelines via GitHub Actions

**Independent Test**: Push to main → images built and tested → staging deployed. Create v* tag → production deployed with health checks.

### Implementation for User Story 7

- [ ] T089 [P] [US7] Create `.github/workflows/build-and-test.yml` for image build and test on push (FR-040, FR-041)
- [ ] T090 [US7] Create `.github/workflows/deploy-staging.yml` for staging deployment on main push (FR-042)
- [ ] T091 [US7] Create `.github/workflows/deploy-production.yml` for production deployment on v* tag (FR-042)
- [ ] T092 [US7] Add health check verification and automatic rollback to deploy workflows (FR-043)
- [ ] T093 [US7] Add GitHub commit status reporting to all workflows

**Checkpoint**: CI/CD pipeline operational. US7 is independently testable.

---

## Phase 10: Polish & Cross-Cutting Concerns

**Purpose**: Final improvements affecting multiple user stories

- [ ] T094 [P] Add structured JSON logging with correlation IDs to all services (FR-044)
- [ ] T095 [P] Verify `/health` and `/ready` endpoints on all services (FR-045)
- [ ] T096 Enable Dapr distributed tracing configuration (FR-046)
- [ ] T097 Run quickstart.md validation end-to-end
- [ ] T098 [P] Security review: verify no hardcoded secrets, all credentials via Dapr Secrets API
- [ ] T099 Performance validation: verify < 500ms API response, < 2s event processing

---

## Dependencies & Execution Order

### Phase Dependencies

```
Phase 1 (Setup) → Phase 2 (Foundational) → User Stories can begin
                                          ↓
                              ┌───────────┴───────────┐
                              ↓                       ↓
                    US1 (P1) Event Publishing   US4 (P1) Dapr Blocks
                              ↓                       ↓
                              └─────────┬─────────────┘
                                        ↓
                              ┌─────────┴─────────┐
                              ↓                   ↓
                    US2 (P2) Reminders    US3 (P2) Recurring
                              ↓                   ↓
                              └─────────┬─────────┘
                                        ↓
                              US5 (P1) Minikube Deploy
                                        ↓
                              ┌─────────┴─────────┐
                              ↓                   ↓
                    US6 (P3) OKE Cloud    US7 (P3) CI/CD
                              ↓                   ↓
                              └─────────┬─────────┘
                                        ↓
                              Phase 10 (Polish)
```

### User Story Dependencies

| User Story | Depends On | Can Parallel With |
|------------|------------|-------------------|
| US1 Event Publishing | Phase 2 Foundational | US4 |
| US4 Dapr Blocks | Phase 2 Foundational | US1 |
| US2 Reminders | US1 (for event publishing) | US3 (after US1 done) |
| US3 Recurring | US1 (for event consumption) | US2 (after US1 done) |
| US5 Minikube | US1, US2, US3, US4 (all services ready) | - |
| US6 OKE Cloud | US5 (local deployment works) | US7 |
| US7 CI/CD | US5 (deployment scripts exist) | US6 |

### Within Each User Story

- Models before services
- Services before endpoints
- Core implementation before integration
- Story complete before moving to next priority

### Parallel Opportunities

**Phase 1**: T002-T007 all parallelizable (different files)
**Phase 2**: T012-T018 parallelizable (different component files)
**Phase 3 (US1)**: T024 parallel with setup, then sequential through endpoints
**Phase 4 (US4)**: T036, T038, T040, T042 parallelizable
**Phase 5 (US2)**: T044, T050, T052 parallelizable
**Phase 6 (US3)**: T058 starts the phase, then parallelizable work
**Phase 7 (US5)**: T066, T068, T070, T072, T074, T077-T079, T081-T082 parallelizable
**Phase 8 (US6)**: T083, T085 parallelizable
**Phase 9 (US7)**: T089 starts, rest can follow

---

## Parallel Example: Phase 2 Foundation

```bash
# Parallel batch 1 (Kafka infra)
T008 & T009 & T010 & T011  # Kafka YAMLs and setup script

# Parallel batch 2 (Dapr components - Minikube)
T012 & T013 & T014 & T015  # All Minikube Dapr components

# Parallel batch 3 (Dapr components - Production)
T016 & T017 & T018 & T019  # All Production Dapr components

# Parallel batch 4 (Service configs)
T020 & T021 & T022 & T023  # All config files
```

---

## Parallel Example: User Story 5 (Minikube Deployment)

```bash
# Parallel batch 1 (Helm values files)
T066 & T068  # Chart.yaml and values-minikube.yaml

# Sequential (values.yaml depends on knowing structure)
T067  # values.yaml

# Parallel batch 2 (Helm templates)
T069 & T070 & T071 & T072 & T073 & T074  # All deployment templates

# Parallel batch 3 (Scripts)
T076 & T077 & T078 & T079  # All deployment scripts

# Parallel batch 4 (Docker)
T080 & T081 & T082  # All Dockerfile updates
```

---

## Implementation Strategy

### MVP Scope (Recommended First Iteration)

**MVP = Phase 1 + Phase 2 + US1 + US4 + US5**

This delivers:
- ✅ Event publishing for all task operations
- ✅ All 5 Dapr building blocks operational
- ✅ Working Minikube deployment
- ✅ Foundation for US2/US3

### Incremental Delivery

1. **Week 1**: Phases 1-2 (Foundation), US1 (Events), US4 (Dapr)
2. **Week 2**: US2 (Reminders), US3 (Recurring), US5 (Minikube)
3. **Week 3**: US6 (OKE), US7 (CI/CD), Polish

### Total Task Count: 99 tasks

| Phase | Task Count |
|-------|------------|
| Setup | 7 |
| Foundational | 16 |
| US1 Event Publishing | 12 |
| US4 Dapr Blocks | 8 |
| US2 Reminders | 14 |
| US3 Recurring | 8 |
| US5 Minikube | 17 |
| US6 OKE Cloud | 6 |
| US7 CI/CD | 5 |
| Polish | 6 |

---

## Summary

- **Total Tasks**: 99
- **User Stories**: 7 (US1-US7)
- **Priority Order**: P1 (US1, US4, US5) → P2 (US2, US3) → P3 (US6, US7)
- **Parallel Opportunities**: 45+ tasks marked [P]
- **MVP Scope**: 43 tasks (Phases 1-2 + US1 + US4 + US5)
- **Key Deliverables**:
  - Event-driven task operations via Kafka/Dapr
  - All 5 Dapr building blocks + Jobs API
  - Notification and Recurring microservices
  - Single-command Minikube deployment
  - Oracle OKE cloud deployment
  - GitHub Actions CI/CD pipeline
