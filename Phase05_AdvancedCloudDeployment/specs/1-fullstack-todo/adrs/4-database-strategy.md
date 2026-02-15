# ADR-4: Database Strategy

> **Scope**: Document decision clusters, not individual technology choices. Group related decisions that work together (e.g., "Database Strategy" not separate ADRs for database, ORM, migrations).

- **Status:** Proposed
- **Date:** 2026-01-03
- **Feature:** Fullstack Todo Application
- **Context:** The application requires a reliable, scalable database solution with proper user isolation, efficient querying, and support for the application's data model. The database must support the chosen ORM and deployment requirements while ensuring security and performance.

<!-- Significance checklist (ALL must be true to justify this ADR)
     1) Impact: Long-term consequence for architecture/platform/security?
     2) Alternatives: Multiple viable options considered with tradeoffs?
     3) Scope: Cross-cutting concern (not an isolated detail)?
     If any are false, prefer capturing as a PHR note instead of an ADR. -->

## Decision

We will use the following integrated database strategy:

- **Database**: Neon Serverless PostgreSQL for cloud-native, serverless operation
- **ORM**: SQLModel for type-safe, Pydantic-compatible database operations
- **Schema Evolution**: Direct model changes in development, Alembic for production
- **User Isolation**: Foreign key constraints enforcing user ownership at database level
- **Indexing Strategy**: Proper indexing for common queries (user_id, status, priority, due_date)
- **Security**: Encrypted connections, parameterized queries to prevent injection
- **Backup**: Neon's built-in point-in-time recovery

## Consequences

### Positive

- Serverless scaling with Neon reduces operational overhead
- SQLModel provides type safety with Pydantic compatibility
- Strong user isolation at database level
- Efficient querying with proper indexing
- Built-in security features from PostgreSQL
- Automatic backup and recovery

### Negative

- Vendor lock-in with Neon's PostgreSQL implementation
- Learning curve for serverless PostgreSQL concepts
- Potential cold start latency for serverless features
- Dependency on Neon's specific features

## Alternatives Considered

- **Alternative A**: Self-hosted PostgreSQL + SQLAlchemy: More control but higher operational overhead
- **Alternative B**: MongoDB + PyMongo: Different data model, document-based approach
- **Alternative C**: SQLite + SQLModel: Simpler but less scalable for multi-user application
- **Alternative D**: MySQL + SQLAlchemy: Different SQL dialect, alternative hosting options

## References

- Feature Spec: specs/1-fullstack-todo/spec.md
- Implementation Plan: specs/1-fullstack-todo/plan.md
- Related ADRs: None
- Evaluator Evidence: specs/1-fullstack-todo/research.md, specs/1-fullstack-todo/data-model.md