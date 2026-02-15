---
id: 007
title: Phase 5 Constitution Amendment - Event-Driven Architecture
stage: constitution
date: 2026-02-07
surface: agent
model: claude-sonnet-4-5
feature: phase5-advanced-cloud-deployment
branch: main
user: architect
command: /sp.constitution
labels: ["phase-5", "event-driven", "dapr", "kafka", "constitution", "major-version"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .specify/memory/constitution.md
tests:
  - null
---

## Prompt

```text
- Phase 5: Advanced Cloud Deployment

## PROJECT IDENTITY

**Project Name:** Taskify - Phase 5 Advanced Cloud Deployment
**Version:** 2.0.0
**Phase:** 5 of 5
**Foundation:** Phase 4 Local Kubernetes Deployment (Completed & Working)

--- ## CORE PRINCIPLES (Non-Negotiable)

### P1: Event-Driven First
- All inter-service communication MUST go through Kafka/Dapr pub/sub
- No direct HTTP calls between microservices for business events
- Synchronous calls allowed ONLY for user-facing request/response

### P2: Dapr Abstraction Layer
- Applications MUST NOT have direct dependencies on Kafka client libraries
- All pub/sub, state, and secrets accessed via Dapr sidecar HTTP API
- Infrastructure swappable by changing Dapr component YAML, not code

### P3: Cloud-Native Portability
- Deployment MUST work on: Minikube (local), AKS (Azure), GKE (Google), OKE (Oracle)
- Use Helm values files for environment-specific configuration
- No hardcoded cloud provider specifics in application code

### P4: Spec-Driven Development
- No code written without corresponding Task ID
- All features trace back to speckit.specify requirements
- Every PR must reference Task IDs and acceptance criteria

### P5: AI-Assisted Development
- Use kubectl-ai for Kubernetes operations where possible
- Use Gordon (docker ai) for container operations where possible
- Document AI tool usage in implementation notes

---

## TECHNOLOGY CONSTRAINTS

### MUST USE:
| Category | Technology | Version |
|----------|------------|---------|
| Runtime | Dapr | 1.12+ |
| Messaging | Kafka (via Redpanda/Strimzi) | 3.x |
| Orchestration | Kubernetes | 1.28+ |
| Package Manager | Helm | 3.x |
| CI/CD | GitHub Actions | - |
| Backend | FastAPI + Python | 3.11+ |
| Frontend | Next.js | 14+ |
| Database | Neon PostgreSQL | - |

### MUST NOT USE:
- Direct Kafka client libraries (kafka-python) - use Dapr
- LoadBalancer service type on Minikube - use NodePort
- Hardcoded connection strings - use Dapr secrets or K8s secrets
- `latest` image tags in production - use semantic versioning

---

## ARCHITECTURE CONSTRAINTS

### Microservices Boundaries:
- frontend: UI only, no business logic
- backend (chat-api): Chat + Task CRUD + Event publishing
- notification-service: Consume reminders, send notifications
- recurring-service: Consume task.completed, create next

### Event Topics (Kafka):
- task-events: backend → recurring-service, audit
- reminders: backend → notification-service
- task-updates: backend → websocket-service (future)

### Dapr Components Required:
- pubsub.kafka - Kafka abstraction
- state.postgresql - State management
- secretstores.kubernetes - Secrets
- Dapr Jobs API - Scheduled reminders

---

## QUALITY CONSTRAINTS

### Performance:
- API response time < 500ms (p95)
- Event processing latency < 2 seconds
- Pod startup time < 30 seconds

### Reliability:
- All services must have health endpoints
- Kubernetes liveness and readiness probes required
- Graceful shutdown handling for all services

### Security:
- No secrets in code or config maps
- Use Kubernetes secrets or Dapr secret stores
- Non-root container users

### Observability:
- Structured JSON logging
- Dapr observability enabled
- Health endpoints: /health, /ready

---

## DEPLOYMENT CONSTRAINTS

### Environment Hierarchy:
minikube (local) → staging (cloud) → production (cloud)

### Helm Values Strategy:
values.yaml, values-minikube.yaml, values-staging.yaml, values-production.yaml

### CI/CD Rules:
- Push to main → Deploy to staging
- Git tag v* → Deploy to production
- All deployments via Helm
- Rollback capability required

---

## DEFINITION OF DONE

A feature is complete when:
1. Code implements the Task specification exactly
2. Unit tests pass (>80% coverage for new code)
3. Works on Minikube locally
4. Works on cloud (AKS/GKE/OKE)
5. Dapr integration verified
6. Events published/consumed correctly
7. Documentation updated
8. CI/CD pipeline passes

---

Generate the constitution file at specs/speckit.constitution based on these principles.
```

## Response snapshot

Successfully updated the Phase 5 constitution with MAJOR version bump from 1.3.0 → 2.0.0.

**Key Updates:**

1. **Version Change**: 1.3.0 → 2.0.0 (MAJOR)
   - Rationale: Backward-incompatible architectural changes (event-driven first, Dapr abstraction layer, prohibition of direct Kafka dependencies)

2. **New Core Principles Added:**
   - XII. Event-Driven First (Phase 5 - NON-NEGOTIABLE)
   - XIII. Dapr Abstraction Layer (Phase 5 - NON-NEGOTIABLE)
   - XIV. Cloud-Native Portability (Phase 5 - NON-NEGOTIABLE)

3. **Updated Existing Principles:**
   - IV. Use Subagents and Skills: Added 5 Phase 5 specialized agents (event-stream-architect, kafka-operator, dapr-pubsub-integrator, doks-cloud-orchestrator, aiops-cloud-governor)
   - V. Context7 MCP Server: Added Phase 5 technologies (Dapr, Kafka, Redpanda, Strimzi, Event-Driven Architecture)
   - III. Test-Driven Development: Added event flow tests and Dapr integration tests
   - VIII. Modular & Future-Ready Design: Updated with event bus integration

4. **New Major Sections:**
   - Phase 5: Advanced Cloud Deployment (complete overview with Parts A, B, C)
   - Event-Driven Architecture (Kafka use cases, topics, event schemas)
   - Dapr Integration (building blocks, component definitions, usage patterns)
   - Microservices Architecture (service boundaries, Dapr sidecar injection, communication patterns)

5. **Updated Technology Stack:**
   - Added Phase 5 Event-Driven Stack (Kafka, Dapr, Oracle OKE, microservices)
   - Added Phase 5 specialized agents and tools

6. **Updated Constraints:**
   - Prohibited: Direct Kafka libraries, direct HTTP between services for business events, blocking event consumers
   - Required: Dapr for all infrastructure, event publishing for all task operations, idempotent consumers

7. **Updated Success Criteria:**
   - Added comprehensive Phase 5 requirements (event-driven, Dapr integration, cloud deployment)

**File Modified:**
- `.specify/memory/constitution.md` (v2.0.0)

**Status:**
- Version: 2.0.0
- Ratified: 2026-01-02 (Phase 2 Foundation)
- Last Amended: 2026-02-07 (Phase 5 Event-Driven Architecture)
- Status: Active for Phase 5 (all previous phases retained as foundation)

## Outcome

- ✅ Impact: MAJOR constitutional amendment for Phase 5 event-driven architecture; all Phase 2-4 content preserved
- 🧪 Tests: Constitution validation passed (no unresolved placeholders, semantic versioning followed)
- 📁 Files: 1 file modified (constitution.md v1.3.0 → v2.0.0)
- 🔁 Next prompts: Create Phase 5 specification files (event-driven-architecture.md, kafka-integration.md, dapr-integration.md, microservices.md)
- 🧠 Reflection: MAJOR version bump required due to backward-incompatible architectural principles (event-driven first, Dapr abstraction layer mandatory, prohibition of direct Kafka dependencies)

## Evaluation notes (flywheel)

- Failure modes observed: Initial attempt removed Phase 2-4 content (corrected by user feedback); proper amendment now adds Phase 5 content while preserving all previous phases
- Graders run and results (PASS/FAIL): ✅ PASS - No unresolved placeholders, semantic versioning correct (MAJOR bump), all sections properly updated
- Prompt variant (if applicable): User provided comprehensive Phase 5 principles in natural language format
- Next experiment (smallest change to try): Create event-driven architecture specification file to begin Phase 5 implementation
