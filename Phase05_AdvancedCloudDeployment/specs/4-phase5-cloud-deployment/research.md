# Research: Phase 5 Advanced Cloud Deployment

**Branch**: `main` | **Date**: 2026-02-10 | **Spec**: [spec.md](./spec.md)

## R-001: Dapr Pub/Sub with Kafka

**Decision**: Use Dapr HTTP API for all event publishing/subscription with Kafka as the backend broker.

**Rationale**: Phase05_Project.md explicitly mandates Dapr abstraction — no direct Kafka client libraries (kafka-python, aiokafka) are permitted. Dapr pub/sub decouples application code from the broker, enabling component-level swaps (e.g., Kafka → RabbitMQ) without code changes.

**Alternatives Considered**:
- **Direct kafka-python**: Simpler code but tight coupling to Kafka; violates project requirement
- **aiokafka (async)**: Good async support but same vendor lock-in issue
- **Dapr gRPC API**: Lower latency than HTTP but adds complexity (proto generation); HTTP is simpler and sufficient for hackathon scale

**Implementation Pattern**:
- Publish: `POST http://localhost:3500/v1.0/publish/{pubsubname}/{topic}` with JSON body
- Subscribe: Service exposes `GET /dapr/subscribe` returning topic subscription list
- Event handler: Service exposes `POST /api/events/{topic}` for Dapr to deliver events

## R-002: Dapr Bindings (Cron) AND Jobs API for Scheduling

**Decision**: Use BOTH Dapr Bindings (Cron) and Jobs API — each for its appropriate use case.

**Rationale**: Phase05_Project.md has two requirements that initially appear contradictory:
- **Part B** lists "Bindings (Cron)" as one of the 5 required Dapr building blocks
- **Use Case 4** recommends "Jobs API" over Cron Bindings for reminders

**Resolution**: These serve different purposes and BOTH should be implemented:

| Feature | Dapr Building Block | Use Case |
|---------|-------------------|----------|
| **Periodic batch operations** | Bindings (Cron) | Overdue task scans, cleanup jobs, health checks |
| **Exact-time reminders** | Jobs API | Individual reminder scheduling at precise times |

**Implementation**:
- **Bindings (Cron)**: Component configured to trigger `/api/cron/overdue-check` every 5 minutes. Scans for tasks that became overdue since last check. Satisfies Part B requirement.
- **Jobs API**: Used for scheduling individual task reminders at exact `remind_at` times. No polling overhead. Satisfies Use Case 4 recommendation.

**Why both?**
1. Satisfies Part B's requirement for "Bindings (Cron)" as a building block
2. Follows Use Case 4's recommendation for Jobs API for exact-time scheduling
3. Each mechanism handles what it's best suited for
4. Jobs API is alpha — Cron Bindings provides stable fallback for batch operations

**Risk**: Jobs API is alpha (v1.0-alpha1). Mitigation: Cron Bindings handles batch operations; Jobs API handles individual scheduling. If Jobs API becomes unstable, can fall back to Cron-only approach with more frequent polling.

## R-003: Kafka Deployment Strategy

**Decision**: Strimzi operator for both Minikube (local) and cloud; Redpanda Cloud as optional alternative for cloud.

**Rationale**: Strimzi provides a Kubernetes-native Kafka deployment with CRDs for clusters and topics. Free (no cloud costs for local), excellent learning experience, and production-grade operator pattern. For cloud, Redpanda Cloud Serverless (free tier) is a simpler alternative.

**Alternatives Considered**:
- **Bitnami Kafka Helm chart**: Simpler than Strimzi but no CRD-based topic management
- **Redpanda single binary**: Easier local setup but less Kubernetes-native
- **Confluent Cloud**: Industry standard but $400 credit expires; not suitable for Always Free

**Minikube Config**: 1 Kafka replica, 1 ZooKeeper replica, ephemeral storage
**Cloud Config**: 3 Kafka replicas, persistent storage, or Redpanda Cloud Serverless

## R-004: Dapr State Management for Conversation State

**Decision**: Use Dapr state store (state.postgresql) backed by Neon PostgreSQL for conversation state.

**Rationale**: Phase05_Project.md requires State Management as one of the 5 Dapr building blocks. Using Dapr state API for conversation state demonstrates the capability while keeping Neon DB as the single source of truth.

**Alternatives Considered**:
- **Direct SQLModel (current Phase 3 approach)**: Works but doesn't demonstrate Dapr state management
- **Redis state store**: Additional infrastructure; Neon DB already available
- **In-memory state store**: Not persistent; conversation history would be lost on restart

**Implementation**: Dapr state store component configured with Neon PostgreSQL connection string. Services use `GET/POST http://localhost:3500/v1.0/state/{storename}` for state operations.

## R-005: Dapr Service Invocation

**Decision**: Use Dapr Service Invocation for frontend-to-backend communication within Kubernetes.

**Rationale**: Phase05_Project.md requires Service Invocation as one of the 5 Dapr building blocks. Provides automatic service discovery, retries, mTLS, and load balancing without hardcoded service URLs.

**Alternatives Considered**:
- **Direct Kubernetes Service DNS**: Simpler but doesn't demonstrate Dapr capability; no built-in retries
- **Istio service mesh**: Overkill for hackathon; Dapr already provides service invocation

**Implementation**: Frontend calls `http://localhost:3500/v1.0/invoke/{app-id}/method/{path}` instead of direct service URLs.

## R-006: Dapr Secrets Management

**Decision**: Use Dapr Secrets API with Kubernetes Secrets as the backend store.

**Rationale**: Phase05_Project.md requires Secrets Management as one of the 5 Dapr building blocks. Kubernetes Secrets is the simplest backend and already available in K8s environments.

**Alternatives Considered**:
- **Direct Kubernetes Secrets (env vars)**: Current Phase 4 approach; works but doesn't demonstrate Dapr capability
- **HashiCorp Vault**: Production-grade but excessive complexity for hackathon
- **Azure Key Vault / AWS Secrets Manager**: Cloud-specific; breaks multi-cloud portability

**Implementation**: Services use `GET http://localhost:3500/v1.0/secrets/{storename}/{key}` to retrieve secrets at runtime.

## R-007: Idempotent Event Processing

**Decision**: Track processed event IDs in a `processed_events` database table per consumer service.

**Rationale**: Kafka provides at-least-once delivery. Consumers may receive duplicate events. Each consumer must track which events it has already processed to prevent duplicate task creation or notification delivery.

**Alternatives Considered**:
- **Kafka exactly-once semantics**: Complex configuration; at-least-once with idempotency is simpler and more robust
- **Dapr state store for tracking**: Possible but adds Dapr dependency for a simple table lookup
- **In-memory dedup cache**: Not persistent across restarts; would miss duplicates after pod restart

**Implementation**: `processed_events` table with columns: `event_id (UUID, PK)`, `service_name (VARCHAR)`, `processed_at (TIMESTAMP)`. Unique constraint on `(event_id, service_name)`.

## R-008: Oracle Cloud OKE Deployment

**Decision**: Oracle Cloud OKE with Always Free tier (4 OCPUs, 24GB RAM).

**Rationale**: Phase05_Project.md states "WE WILL GO WITH ORACLE CLOUD SETUP (Recommended - Always Free)". No time-limited credits, suitable for long-term learning.

**Alternatives Considered**:
- **Azure AKS**: $200 credit for 30 days — time-limited
- **Google GKE**: $300 credit for 90 days — time-limited
- **DigitalOcean DOKS**: $200 credit for 60 days — time-limited

## R-009: CI/CD Pipeline with GitHub Actions

**Decision**: GitHub Actions with separate workflows for build/test, staging deploy, and production deploy.

**Rationale**: GitHub-native, free for public repos, integrates with Helm and kubectl for deployments.

**Alternatives Considered**:
- **GitLab CI**: Good but team uses GitHub
- **Jenkins**: Self-hosted overhead; not suitable for hackathon
- **ArgoCD**: GitOps approach; adds complexity beyond GitHub Actions

## R-010: Microservice Communication Pattern

**Decision**: Async event-driven via Dapr pub/sub for all inter-service communication. Recurring service and notification service create tasks via backend REST API (through Dapr service invocation), not direct DB access.

**Rationale**: Consumer services should not have direct database write access. They consume events and call the backend API to perform operations, maintaining the backend as the single source of truth for task CRUD.

**Alternatives Considered**:
- **Direct DB writes from consumers**: Simpler but bypasses backend validation and breaks single-responsibility
- **Shared library for DB operations**: Tight coupling; defeats microservice architecture
