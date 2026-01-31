# ADR-3: Backend Technology Stack

> **Scope**: Document decision clusters, not individual technology choices. Group related decisions that work together (e.g., "Backend Stack" not separate ADRs for framework, ORM, deployment).

- **Status:** Proposed
- **Date:** 2026-01-03
- **Feature:** Fullstack Todo Application
- **Context:** The backend must provide a high-performance API with FastAPI's async capabilities, proper data validation, and integration with the chosen database ORM. The stack needs to support Python 3.13+, proper type hints, and work with the selected deployment platform.

<!-- Significance checklist (ALL must be true to justify this ADR)
     1) Impact: Long-term consequence for architecture/platform/security?
     2) Alternatives: Multiple viable options considered with tradeoffs?
     3) Scope: Cross-cutting concern (not an isolated detail)?
     If any are false, prefer capturing as a PHR note instead of an ADR. -->

## Decision

We will use the following integrated backend stack:

- **Language**: Python 3.13+ for modern Python features
- **Framework**: FastAPI for high-performance async API development
- **Package Manager**: UV for fast dependency management
- **ORM**: SQLModel for type-safe database operations
- **Validation**: Pydantic for request/response validation
- **Authentication**: Integration with Better Auth for JWT handling
- **Deployment**: Hugging Face Spaces for optimal Python performance
- **Code Quality**: Ruff for linting and formatting

## Consequences

### Positive

- High-performance async API with FastAPI
- Type safety with Pydantic and SQLModel integration
- Excellent documentation generation with FastAPI
- Modern Python features with 3.13+
- Fast dependency installation with UV
- Seamless deployment to Hugging Face Spaces

### Negative

- Learning curve for team members unfamiliar with FastAPI
- Python 3.13+ may have limited hosting options
- Dependency on multiple new libraries
- UV package manager is less mature than pip

## Alternatives Considered

- **Alternative Stack A**: Django + Django REST Framework + Heroku: More traditional Python web framework, mature ecosystem, different deployment approach
- **Alternative Stack B**: Flask + SQLAlchemy + Gunicorn: More lightweight but less modern features
- **Alternative Stack C**: Node.js + Express + Prisma + Vercel: Different language ecosystem, alternative deployment platform

## References

- Feature Spec: specs/1-fullstack-todo/spec.md
- Implementation Plan: specs/1-fullstack-todo/plan.md
- Related ADRs: None
- Evaluator Evidence: specs/1-fullstack-todo/research.md