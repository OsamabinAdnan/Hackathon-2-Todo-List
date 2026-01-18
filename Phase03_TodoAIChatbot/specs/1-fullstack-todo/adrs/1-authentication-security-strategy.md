# ADR-1: Authentication and Security Strategy

> **Scope**: Document decision clusters, not individual technology choices. Group related decisions that work together (e.g., "Frontend Stack" not separate ADRs for framework, styling, deployment).

- **Status:** Proposed
- **Date:** 2026-01-03
- **Feature:** Fullstack Todo Application
- **Context:** The application requires secure, multi-user authentication with strict user isolation. The system must prevent cross-user access to tasks while maintaining stateless, scalable authentication. The architecture must support JWT tokens for stateless operation and enforce user isolation at both application and database levels.

<!-- Significance checklist (ALL must be true to justify this ADR)
     1) Impact: Long-term consequence for architecture/platform/security?
     2) Alternatives: Multiple viable options considered with tradeoffs?
     3) Scope: Cross-cutting concern (not an isolated detail)?
     If any are false, prefer capturing as a PHR note instead of an ADR. -->

## Decision

We will use Better Auth with JWT tokens for stateless authentication. Key components include:

- **Authentication Library**: Better Auth for comprehensive auth solution
- **Token Strategy**: JWT tokens with 7-day expiry and refresh capability
- **Storage**: httpOnly cookies for secure token storage
- **User Isolation**: Middleware enforcement at API level, foreign key constraints at database level
- **Password Security**: bcrypt or argon2 hashing via Better Auth
- **Rate Limiting**: Per-user rate limiting to prevent abuse

## Consequences

### Positive

- Stateless authentication scales well
- User isolation enforced at multiple levels (middleware + database)
- Built-in security features from Better Auth
- Complies with constitution requirements

### Negative

- JWT token management complexity
- Token revocation challenges (no native logout without additional infrastructure)
- Dependency on Better Auth library

## Alternatives Considered

- **Session-based authentication**: Traditional server-side sessions with shared storage; violates constitution's stateless requirement
- **Custom JWT implementation**: Build JWT handling from scratch; more complex and error-prone
- **OAuth providers only**: Limit to external auth providers; reduces user registration options
- **Short-lived tokens with refresh rotation**: More complex token management; overkill for Phase 2

## References

- Feature Spec: specs/1-fullstack-todo/spec.md
- Implementation Plan: specs/1-fullstack-todo/plan.md
- Related ADRs: None
- Evaluator Evidence: specs/1-fullstack-todo/research.md