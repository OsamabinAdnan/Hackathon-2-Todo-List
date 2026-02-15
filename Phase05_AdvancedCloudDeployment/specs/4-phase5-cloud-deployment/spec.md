# Feature Specification: Phase 5 Advanced Cloud Deployment

**Feature**: Phase 5 - Event-Driven Architecture with Kafka, Dapr, and Cloud Deployment
**Created**: 2026-02-10
**Status**: Draft
**Input**: User description: "Phase 5 Advanced Cloud Deployment with Kafka, Dapr event-driven architecture, microservices, Minikube and Oracle OKE deployment"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Event-Driven Task Operations (Priority: P1)

As a system operator, I need all task operations (create, update, complete, delete) to publish events to a message broker so that downstream services can react to task changes without direct coupling to the main application.

**Why this priority**: This is the foundation of Phase 5. Without event publishing, no downstream service (notifications, recurring tasks) can function. Every other user story depends on events being published reliably.

**Independent Test**: Create, update, complete, and delete tasks via the API and AI chatbot. Verify that corresponding events appear on the message broker topics. Can be validated with a topic consumer or broker monitoring tools.

**Acceptance Scenarios**:

1. **Given** a user creates a new task, **When** the task is saved successfully, **Then** a `task.created` event is published to the `task-events` topic containing the full task data, user ID, and timestamp
2. **Given** a user updates an existing task, **When** the update is persisted, **Then** a `task.updated` event is published with both old and new task data
3. **Given** a user marks a task as complete, **When** the completion is saved, **Then** a `task.completed` event is published to trigger downstream processing (recurring task creation, audit)
4. **Given** a user deletes a task, **When** the deletion is confirmed, **Then** a `task.deleted` event is published with the task ID and user ID
5. **Given** the message broker is temporarily unavailable, **When** a task operation occurs, **Then** the task operation still succeeds for the user, the event publishing failure is logged, and the system remains functional
6. **Given** an event is published via the AI chatbot MCP tools, **When** add_task, update_task, complete_task, or delete_task tools execute, **Then** the same events are published as when using the REST API directly

---

### User Story 2 - Automated Reminder Notifications (Priority: P2)

As a user with tasks that have due dates, I need to receive timely reminder notifications so that I do not miss important deadlines.

**Why this priority**: Directly enhances user value by making the reminder feature (implemented in Phase 2) operational via event-driven processing. Depends on event infrastructure from US1.

**Independent Test**: Create a task with a due date and reminder time. Verify that when the scheduled time arrives, a reminder event is published and the notification service processes it and logs the notification.

**Acceptance Scenarios**:

1. **Given** a user creates a task with a due date and reminder time, **When** the reminder time is reached, **Then** a reminder event is published to the `reminders` topic containing task ID, title, due date, reminder time, and user ID
2. **Given** the notification service receives a reminder event, **When** processing the event, **Then** the service logs the notification details (task title, user, due date) as confirmation of delivery
3. **Given** multiple tasks have reminders due at the same time, **When** processing reminders, **Then** each reminder is published as a separate event and processed independently
4. **Given** a task's due date or reminder time is updated, **When** the update is saved, **Then** the previously scheduled reminder is cancelled and a new one is scheduled at the updated time
5. **Given** the notification service has already processed a reminder event, **When** the same event is delivered again (duplicate), **Then** the service detects the duplicate and skips processing without creating duplicate notifications

---

### User Story 3 - Recurring Task Automation (Priority: P2)

As a user with recurring tasks, I need the next occurrence to be created automatically when I complete the current one so that I do not have to manually recreate routine tasks.

**Why this priority**: Automates the recurring task feature from Phase 2. Same priority as reminders since both enhance existing features with event-driven processing. Depends on US1 for task completion events.

**Independent Test**: Create recurring tasks with daily, weekly, and monthly patterns. Mark each as complete. Verify that the recurring task service creates the next occurrence with the correct future date and same task properties.

**Acceptance Scenarios**:

1. **Given** a user completes a recurring task with a daily pattern, **When** the completion event is consumed by the recurring task service, **Then** a new task is created for the next day with the same title, description, priority, and tags
2. **Given** a user completes a recurring task with a weekly pattern, **When** the completion event is consumed, **Then** a new task is created for the same day next week
3. **Given** a user completes a recurring task with a monthly pattern, **When** the completion event is consumed, **Then** a new task is created for the same day next month, handling month-end edge cases (e.g., January 31 becomes February 28 or 29)
4. **Given** the recurring task service is temporarily unavailable, **When** a recurring task is completed, **Then** the completion event remains in the message broker for later processing (at-least-once delivery)
5. **Given** the recurring task service receives the same completion event twice, **When** processing the duplicate, **Then** the service detects the duplicate and does not create a second next occurrence

---

### User Story 4 - Dapr-Abstracted Service Communication (Priority: P1)

As a system operator, I need all inter-service communication to be abstracted through Dapr building blocks so that services are decoupled from infrastructure and can be deployed to any environment without code changes.

**Why this priority**: Dapr abstraction is a core Phase 5 requirement. All five Dapr building blocks (Pub/Sub, State Management, Service Invocation, Bindings, Secrets Management) must be used per Part B. This enables multi-cloud portability.

**Independent Test**: Deploy services with Dapr sidecars. Verify that services communicate exclusively through Dapr HTTP APIs. Swap a Dapr component configuration (e.g., change pub/sub backend) and verify services continue working without code changes.

**Acceptance Scenarios**:

1. **Given** a service needs to publish an event, **When** publishing via the Dapr pub/sub API, **Then** the event reaches the configured message broker (Kafka) without the service having any direct broker dependency
2. **Given** the frontend needs to call the backend, **When** using Dapr service invocation, **Then** the call is routed through the Dapr sidecar with automatic retries and service discovery
3. **Given** a service needs to store or retrieve conversation state, **When** using the Dapr state management API, **Then** state is persisted to the configured state store (PostgreSQL) without direct database code
4. **Given** the system needs to run periodic background tasks, **When** using Dapr Bindings (Cron), **Then** the cron binding triggers the configured endpoint at scheduled intervals (e.g., every 5 minutes for overdue task scans)
5. **Given** a task has a scheduled reminder, **When** the reminder time arrives, **Then** the Dapr Jobs API triggers a callback at the exact scheduled time without polling (per Use Case 4)
6. **Given** a service needs database credentials or API keys, **When** using the Dapr secrets API, **Then** secrets are retrieved from the configured secret store (Kubernetes Secrets) without hardcoded values
7. **Given** a Dapr component configuration is changed (e.g., Kafka broker address), **When** services are restarted, **Then** services work with the new configuration without any code changes

---

### User Story 5 - Local Minikube Deployment with Full Stack (Priority: P1)

As a developer, I need to deploy the complete event-driven system (all services, Kafka, Dapr) to Minikube with a single command so that I can test and demonstrate the full system locally.

**Why this priority**: Critical for development, testing, and demonstration. All services must be deployable and verifiable locally before cloud deployment.

**Independent Test**: Start with a fresh Minikube cluster. Run the deployment script. Verify all pods are running with Dapr sidecars, Kafka topics exist, events flow between services, and health checks pass.

**Acceptance Scenarios**:

1. **Given** Minikube is running, **When** executing the deployment script, **Then** Kafka (via Strimzi operator) is deployed with required topics (task-events, reminders, task-updates)
2. **Given** Kafka is running, **When** continuing deployment, **Then** Dapr is installed with all five building blocks configured (pub/sub, state, service invocation, jobs, secrets)
3. **Given** infrastructure is ready, **When** deploying application services, **Then** frontend, backend, notification-service, and recurring-service pods are running with Dapr sidecars injected
4. **Given** all services are deployed, **When** executing the verification script, **Then** all health checks pass, event flow is confirmed (create task → event published → consumed by downstream services), and all Dapr components are operational
5. **Given** a developer wants to clean up, **When** running the cleanup script, **Then** all Phase 5 resources are removed from Minikube without affecting other workloads

---

### User Story 6 - Cloud Deployment (Oracle OKE) (Priority: P3)

As a project owner, I need the application deployed to Oracle Cloud (OKE) so that users can access it from anywhere with production-grade reliability.

**Why this priority**: Final deployment target for Phase 5. Lower priority because local Minikube deployment (US5) must work first and provides most of the development and learning value.

**Independent Test**: Deploy to OKE using the same Helm charts with production-specific values. Run the same verification scripts. Verify external access via Ingress with TLS.

**Acceptance Scenarios**:

1. **Given** an Oracle Cloud account is configured with OKE access (4 OCPUs, 24GB RAM, Always Free tier), **When** deploying using the cloud deployment script, **Then** all services are deployed with production-grade configuration
2. **Given** the OKE cluster is ready, **When** deploying Kafka, **Then** either Redpanda Cloud (Serverless) or self-hosted Strimzi is configured based on environment values
3. **Given** infrastructure is ready, **When** deploying via Helm, **Then** the same charts used for Minikube work with environment-specific values (values-production.yaml) without code changes
4. **Given** services are deployed, **When** users access the application, **Then** external access is available via Ingress with TLS termination
5. **Given** a deployment fails health checks, **When** the post-deployment verification runs, **Then** automatic rollback to the previous version occurs

---

### User Story 7 - CI/CD Pipeline (Priority: P3)

As a development team, I need automated build, test, and deployment pipelines so that code changes are automatically validated and deployed without manual intervention.

**Why this priority**: Automation and DevOps best practice. Lower priority since manual deployment works first; CI/CD adds convenience, safety, and reproducibility.

**Independent Test**: Push a code change to the main branch. Verify automated image build, test execution, and staging deployment. Create a git tag. Verify production deployment with health checks.

**Acceptance Scenarios**:

1. **Given** code is pushed to the main branch, **When** the CI/CD pipeline triggers, **Then** Docker images are built, tests are executed, and images are pushed to the container registry
2. **Given** images are built successfully, **When** the staging deployment step runs, **Then** the application is deployed to the staging environment with health check verification
3. **Given** a git tag matching `v*` is created, **When** the production deployment pipeline triggers, **Then** the application is deployed to the production environment
4. **Given** a deployment fails health checks, **When** the post-deployment verification detects failure, **Then** automatic rollback to the previous version occurs and the team is notified
5. **Given** the pipeline completes (success or failure), **When** the workflow finishes, **Then** deployment status is reported in GitHub (commit status or PR comment)

---

### Edge Cases

- **Kafka broker unavailable during event publishing**: Task operation succeeds for the user; event publishing failure is logged; system continues functioning; events are not lost on the client side (client can retry)
- **Dapr sidecar fails or restarts**: Kubernetes automatically restarts the sidecar; application temporarily cannot communicate via Dapr; health checks reflect degraded state; once sidecar recovers, operations resume
- **Recurring task service is down when completion events are published**: Events remain in Kafka topic (7-day retention policy); when service recovers, it processes the backlog; idempotency prevents duplicate task creation
- **Notification service receives duplicate reminder events**: Service tracks processed event IDs; duplicates are detected and skipped; no duplicate notifications are generated
- **Monthly recurring task completed on January 31**: Next occurrence is created for February 28 (or 29 in leap years); system handles all month-end edge cases
- **OKE free tier resources exhausted**: System alerts when nearing resource limits (90% CPU/memory); documentation provides guidance on scaling within free tier constraints
- **Dapr component misconfiguration**: Services fail health checks; deployment script validates component connectivity before marking deployment as successful; clear error messages guide troubleshooting
- **Concurrent task operations publish overlapping events**: Each event includes a unique correlation ID and timestamp; consumers process events in order per partition; idempotency prevents inconsistent state

## Requirements *(mandatory)*

### Functional Requirements

#### Event Publishing (Backend)

- **FR-001**: System MUST publish a `task.created` event to `task-events` topic when a task is created via REST API or MCP tools
- **FR-002**: System MUST publish a `task.updated` event to `task-events` topic when a task is updated
- **FR-003**: System MUST publish a `task.completed` event to `task-events` topic when a task is marked complete
- **FR-004**: System MUST publish a `task.deleted` event to `task-events` topic when a task is deleted
- **FR-005**: All published events MUST include: event_type, task_id, user_id, timestamp, task_data (where applicable), and correlation_id
- **FR-006**: Event publishing MUST be non-blocking; if the broker is unavailable, the task operation MUST still succeed and the failure MUST be logged
- **FR-007**: System MUST NOT include direct Kafka client libraries (kafka-python, aiokafka); all pub/sub MUST go through Dapr HTTP API

#### Reminder System

- **FR-008**: System MUST schedule reminders using Dapr Jobs API at the exact reminder time (not cron polling)
- **FR-009**: When a reminder job fires, the system MUST publish a `reminder.due` event to the `reminders` topic
- **FR-010**: When a task's reminder time is updated, the system MUST cancel the previous scheduled job and create a new one
- **FR-011**: When a task is deleted, the system MUST cancel any associated scheduled reminder job

#### Notification Service

- **FR-012**: Notification service MUST be a separate microservice with its own health and readiness endpoints
- **FR-013**: Notification service MUST subscribe to the `reminders` topic via Dapr pub/sub
- **FR-014**: Notification service MUST log reminder details (task title, user, due date) as confirmation of delivery
- **FR-015**: Notification service MUST implement idempotent event processing by tracking processed event IDs
- **FR-016**: Notification service MUST have a Dapr sidecar enabled with app-id `notification-service`

#### Recurring Task Service

- **FR-017**: Recurring task service MUST be a separate microservice with its own health and readiness endpoints
- **FR-018**: Recurring task service MUST subscribe to the `task-events` topic via Dapr pub/sub
- **FR-019**: Recurring task service MUST filter for `task.completed` events where the task has a recurrence pattern
- **FR-020**: Recurring task service MUST create the next occurrence with the correct date based on recurrence pattern (daily, weekly, monthly)
- **FR-021**: Recurring task service MUST handle month-end edge cases (January 31 → February 28/29)
- **FR-022**: Recurring task service MUST implement idempotent event processing
- **FR-023**: Recurring task service MUST have a Dapr sidecar enabled with app-id `recurring-service`

#### Dapr Building Blocks (All Five Required per Part B)

- **FR-024**: All services MUST use Dapr Pub/Sub for event publishing and subscription (Kafka as backend)
- **FR-025**: Services MUST use Dapr State Management for conversation state storage (PostgreSQL as backend)
- **FR-026**: Frontend-to-backend communication MUST use Dapr Service Invocation for automatic discovery and retries
- **FR-027**: System MUST use Dapr Bindings (Cron) for periodic background tasks (e.g., checking for overdue reminders, cleanup jobs)
- **FR-027a**: Reminder scheduling for individual tasks MUST use Dapr Jobs API for exact-time callback scheduling (per Use Case 4 recommendation)
- **FR-028**: All services MUST use Dapr Secrets Management for accessing credentials (Kubernetes Secrets as backend)
- **FR-029**: Services MUST publish events via HTTP POST to `http://localhost:3500/v1.0/publish/{pubsubname}/{topic}`
- **FR-030**: Services MUST expose subscription declarations for Dapr to discover topic subscriptions

**Note on Bindings vs Jobs API**: Phase05_Project.md Part B requires "Bindings (Cron)" as one of the 5 building blocks. Use Case 4 recommends "Jobs API" for exact-time reminders. This spec implements BOTH:
- **Bindings (Cron)** (FR-027): For periodic batch operations (overdue task scans, cleanup, health checks)
- **Jobs API** (FR-027a): For scheduling individual reminders at exact times (no polling overhead)

#### Kafka Infrastructure

- **FR-031**: Kafka MUST be deployed using Strimzi operator on Minikube (local) and Strimzi or Redpanda Cloud (cloud)
- **FR-032**: Three Kafka topics MUST be created: `task-events`, `reminders`, `task-updates`
- **FR-033**: Kafka topics MUST have a retention policy of 7 days
- **FR-034**: Kafka topics MUST have replication factor of 1 (Minikube) or 3 (cloud)

#### Deployment

- **FR-035**: A single deployment script MUST deploy the complete system to Minikube including Kafka (Strimzi), Dapr (all building blocks), and all application services
- **FR-036**: A verification script MUST validate: pod status, Dapr sidecar injection, health endpoints, and end-to-end event flow
- **FR-037**: Helm charts MUST support environment-specific values files: values-minikube.yaml, values-staging.yaml, values-production.yaml
- **FR-038**: Helm charts MUST include Dapr annotations for all application services (frontend, backend, notification, recurring)
- **FR-039**: A cleanup script MUST remove all Phase 5 resources from the cluster

#### CI/CD Pipeline

- **FR-040**: CI/CD pipeline MUST build Docker images on push to main branch
- **FR-041**: CI/CD pipeline MUST run tests as part of the build process
- **FR-042**: CI/CD pipeline MUST deploy to staging on push to main, production on git tag (`v*`)
- **FR-043**: CI/CD pipeline MUST perform health checks post-deployment and rollback on failure

#### Monitoring and Logging

- **FR-044**: All services MUST emit structured JSON logs with correlation IDs
- **FR-045**: All services MUST expose `/health` and `/ready` endpoints
- **FR-046**: Dapr observability MUST be enabled for distributed tracing

### Key Entities

- **TaskEvent**: Represents a published event for task lifecycle changes
  - Attributes: event_type (created/updated/completed/deleted), task_id, user_id, timestamp, task_data (full task object), correlation_id
  - Relationships: Published by backend, consumed by recurring-service and notification-service

- **ReminderEvent**: Represents a scheduled reminder notification
  - Attributes: task_id, title, due_at, remind_at, user_id, timestamp, correlation_id
  - Relationships: Published by Dapr Jobs callback, consumed by notification-service

- **ProcessedEvent**: Tracks which events have been processed by each consumer (for idempotency)
  - Attributes: event_id, service_name, processed_at, user_id
  - Relationships: One per event per consumer service; prevents duplicate processing

- **DaprComponent**: Configuration for Dapr infrastructure building blocks
  - Types: pubsub.kafka, state.postgresql, secretstores.kubernetes, Jobs API
  - Relationships: Configured per environment (Minikube, staging, production); used by all services

- **KafkaTopic**: Message queue for event streaming
  - Attributes: topic_name, partitions, replication_factor, retention_policy
  - Instances: task-events, reminders, task-updates

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Task operations publish corresponding events within 100ms of operation completion
- **SC-002**: Reminder notifications are processed within 2 seconds of the scheduled reminder time
- **SC-003**: Recurring task service creates the next occurrence within 5 seconds of receiving a completion event
- **SC-004**: System supports 1000 concurrent task operations with 99.9% event publishing success rate
- **SC-005**: Complete system deploys to Minikube using a single script and passes all verification checks
- **SC-006**: Complete system deploys to Oracle OKE using the same Helm charts with environment-specific values
- **SC-007**: All five Dapr building blocks (Pub/Sub, State, Service Invocation, Jobs, Secrets) are operational and used by at least one service
- **SC-008**: Event consumers achieve zero duplicate processing through idempotent handling
- **SC-009**: CI/CD pipeline builds, tests, and deploys to staging on push to main
- **SC-010**: Failed deployments automatically rollback within 2 minutes of health check failure
- **SC-011**: Same Helm charts deploy successfully to Minikube and Oracle OKE without code changes (multi-cloud portability)
- **SC-012**: All services achieve 99.5% uptime on cloud deployment measured over 30 days

### Business Value Metrics

- **SC-013**: Developers can deploy the complete event-driven system locally (Minikube) without manual infrastructure configuration
- **SC-014**: Recurring tasks automatically create next occurrence on completion with 100% automation rate
- **SC-015**: Reminder notifications are delivered reliably with 99.5% delivery rate
- **SC-016**: Swapping a Dapr component backend (e.g., Kafka → RabbitMQ) requires only YAML configuration changes, not code changes

## Assumptions

1. **Phase Completion Assumptions**:
   - Phase 2 features (priorities, tags, search, filter, sort, due dates, recurring tasks) are fully implemented and working in the backend
   - Phase 3 AI chatbot with MCP tools is functional
   - Phase 4 containerization and Helm charts exist and deploy to Minikube successfully

2. **Infrastructure Assumptions**:
   - Minikube is already installed and running on developer machines
   - Oracle Cloud account is available with OKE access (Always Free tier: 4 OCPUs, 24GB RAM)
   - Docker Desktop is available for building container images

3. **Integration Assumptions**:
   - Neon PostgreSQL database from Phase 2 continues to be used (no migration needed)
   - JWT authentication from Phase 2 works with new microservices
   - Frontend requires no changes for Phase 5 (event-driven changes are backend and infrastructure focused)

4. **Performance Assumptions**:
   - Dapr sidecar overhead is acceptable (< 10ms latency per request)
   - Kafka throughput of 10,000 events/second is sufficient for expected load
   - Event processing latency of 2 seconds meets user expectations for reminders

5. **Deployment Assumptions**:
   - GitHub Actions runners are available for CI/CD
   - Container registry (Docker Hub or GitHub Container Registry) is accessible
   - Deployment scripts have sufficient permissions to create Kubernetes resources

## Non-Functional Requirements

| ID         | Category       | Requirement                                                                 |
| ---------- | -------------- | --------------------------------------------------------------------------- |
| **NFR-001** | Performance    | API response time < 500ms (p95) for task operations                        |
| **NFR-002** | Performance    | Event processing latency < 2 seconds from publish to consume               |
| **NFR-003** | Performance    | Pod startup time < 30 seconds for all services                             |
| **NFR-004** | Availability   | 99.5% uptime on cloud deployment (30-day measurement)                      |
| **NFR-005** | Reliability    | Event delivery guarantee: at-least-once (Kafka default)                    |
| **NFR-006** | Reliability    | All event consumers MUST be idempotent (no duplicate processing)           |
| **NFR-007** | Security       | All secrets stored in Kubernetes Secrets, accessed via Dapr Secrets API     |
| **NFR-008** | Security       | No hardcoded credentials in code, config files, or environment variables   |
| **NFR-009** | Security       | Container images run as non-root users                                     |
| **NFR-010** | Observability  | All services emit structured JSON logs with correlation IDs                |
| **NFR-011** | Observability  | All services expose /health and /ready endpoints                           |
| **NFR-012** | Observability  | Dapr observability enabled for distributed tracing                         |
| **NFR-013** | Scalability    | Each service scales independently via Horizontal Pod Autoscaler            |
| **NFR-014** | Scalability    | System supports 10,000 events/second throughput                            |
| **NFR-015** | Maintainability | Zero direct Kafka client dependencies in application code                 |
| **NFR-016** | Portability    | Same Helm charts work on Minikube, AKS, GKE, and OKE with values files    |

## Out of Scope

1. **Not Included in Phase 5**:
   - Real push notifications (email, SMS, mobile push) — Phase 5 logs notifications only
   - WebSocket service for real-time client sync — `task-updates` topic is created but not consumed
   - Audit service for complete event history — optional future enhancement
   - Advanced Kafka features (schema registry, stream processing)
   - Multi-region deployment or disaster recovery

2. **Changes Not Required**:
   - Frontend modifications — Phase 5 is backend and infrastructure focused
   - Database schema changes beyond idempotency tracking — uses existing Neon PostgreSQL schema
   - Authentication changes — continues using Phase 2 JWT implementation

3. **Advanced Features Deferred**:
   - Kafka Connect for external integrations
   - Advanced monitoring with Prometheus and Grafana (basic health checks only in Phase 5)
   - Canary deployments or blue-green deployments (simple rolling updates only)
   - Service mesh beyond Dapr (no Istio or Linkerd)

## Dependencies

1. **Phase 4 Completion** (CRITICAL):
   - Working Minikube deployment with Helm charts
   - Containerized frontend and backend with optimized Dockerfiles
   - Kubernetes manifests for deployments, services, and ingress

2. **Phase 2 Features** (REQUIRED):
   - Task CRUD operations with priorities, tags, search, filter, sort
   - Due dates and recurring tasks (basic implementation)
   - Neon PostgreSQL database with task and user tables

3. **Phase 3 Features** (REQUIRED):
   - AI chatbot with MCP tools (add_task, list_tasks, complete_task, delete_task, update_task)
   - JWT authentication and user isolation
   - Stateless backend architecture

4. **External Dependencies** (REQUIRED):
   - Neon PostgreSQL (continues from Phase 2)
   - Oracle Cloud account with OKE access (for cloud deployment)
   - GitHub account with Actions enabled (for CI/CD)

## Risk and Mitigation

| Risk                                          | Impact | Probability | Mitigation                                                                                           |
| --------------------------------------------- | ------ | ----------- | ---------------------------------------------------------------------------------------------------- |
| Kafka/Dapr complexity overwhelms setup        | High   | Medium      | Provide comprehensive deployment scripts, documentation, and AI-assisted operations                  |
| Oracle Cloud free tier resource limitations    | Medium | Low         | Document resource limits; design for efficiency; provide monitoring guidance                          |
| Event delivery failures cause data inconsistency | High | Low         | Implement idempotent consumers; use Kafka 7-day retention for replay; add correlation IDs             |
| Dapr sidecar performance overhead             | Medium | Low         | Benchmark early; use Dapr HTTP API for simplicity; monitor latency metrics                           |
| Multi-cloud portability issues                | Medium | Medium      | Test Helm charts on all target platforms; use environment-specific values files; avoid cloud-specific APIs |
| CI/CD pipeline complexity                     | Low    | Medium      | Start with simple pipeline; add features incrementally; use GitHub Actions marketplace               |
| Dapr Jobs API stability (alpha feature)       | Medium | Medium      | Monitor Dapr release notes; have fallback to cron bindings if Jobs API is unstable                    |
