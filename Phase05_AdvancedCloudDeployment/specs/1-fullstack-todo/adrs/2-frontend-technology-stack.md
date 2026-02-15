# ADR-2: Frontend Technology Stack

> **Scope**: Document decision clusters, not individual technology choices. Group related decisions that work together (e.g., "Frontend Stack" not separate ADRs for framework, styling, deployment).

- **Status:** Proposed
- **Date:** 2026-01-03
- **Feature:** Fullstack Todo Application
- **Context:** The frontend must provide a responsive, modern dashboard UI with glassmorphism effects, 60fps animations, and WCAG 2.1 AA accessibility. The stack needs to support TypeScript strict mode, integrate with the chosen component library, and work with the selected styling approach.

<!-- Significance checklist (ALL must be true to justify this ADR)
     1) Impact: Long-term consequence for architecture/platform/security?
     2) Alternatives: Multiple viable options considered with tradeoffs?
     3) Scope: Cross-cutting concern (not an isolated detail)?
     If any are false, prefer capturing as a PHR note instead of an ADR. -->

## Decision

We will use the following integrated frontend stack:

- **Framework**: Next.js 15+ with App Router for modern React development
- **Language**: TypeScript with strict mode for type safety
- **Styling**: Tailwind CSS exclusively (no inline styles) for consistency
- **Components**: shadcn/ui for accessible, production-ready components
- **Animations**: GSAP + Framer Motion for 60fps animations
- **Theming**: next-themes for dark mode support
- **Fonts**: JetBrains Mono and Inter for premium feel
- **Deployment**: Vercel or Github Pages for optimal Next.js performance

## Consequences

### Positive

- Excellent developer experience with integrated tooling
- Strong TypeScript support throughout the stack
- Accessible components with shadcn/ui
- High-performance animations with GSAP/Framer Motion
- Mobile-first responsive design
- Fast deployments with Vercel or Github Pages

### Negative

- Learning curve for team members unfamiliar with Next.js App Router
- Bundle size considerations with multiple animation libraries
- Vercel/Github Pages vendor lock-in for deployment
- Dependency on multiple external libraries

## Alternatives Considered

- **Alternative Stack A**: Remix + Styled Components + Cloudflare Pages: Different routing approach, CSS-in-JS styling, alternative deployment
- **Alternative Stack B**: Vite + React + Material UI + Framer Motion: More lightweight, different tooling ecosystem
- **Alternative Stack C**: Create React App + Custom Components + CSS Modules: More traditional approach but less modern features

## References

- Feature Spec: specs/1-fullstack-todo/spec.md
- Implementation Plan: specs/1-fullstack-todo/plan.md
- Related ADRs: None
- Evaluator Evidence: specs/1-fullstack-todo/research.md