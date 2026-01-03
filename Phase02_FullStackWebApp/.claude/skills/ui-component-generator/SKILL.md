---
name: ui-component-generator
description: Generate reusable Next.js 15+ React components from feature specifications with TypeScript interfaces, Tailwind CSS styling, shadcn/ui integration, and accessibility attributes. Use when (1) Creating new UI components from @specs/ui/ or @specs/features/, (2) Building atomic components like buttons, cards, inputs, badges, (3) Implementing feature-specific components like TaskCard, PriorityTag, TaskFilter, (4) Converting design specifications into production-ready React components with proper TypeScript types, responsive behavior, and WCAG 2.1 AA compliance.
---

# UI Component Generator

Generate production-ready Next.js 15+ React components from feature specifications with TypeScript type safety, Tailwind CSS styling, and accessibility built-in.

## Core Workflow

### 1. Analyze Specification

Read the relevant specification file:
- `@specs/ui/design-system.md` - Design tokens, colors, typography, spacing
- `@specs/ui/dashboard-layout.md` - Layout patterns for component placement
- `@specs/features/task-crud.md` - Feature requirements and component behavior
- `@specs/ui/accessibility.md` - ARIA attributes and keyboard navigation requirements

### 2. Component Architecture

**Determine Component Type:**
- **Server Component (default)**: Static components without interactivity
- **Client Component ('use client')**: Components with hooks, event handlers, browser APIs

**File Structure:**
```
components/
├── ui/              # Primitive components (shadcn/ui style)
│   ├── Button.tsx
│   ├── Card.tsx
│   └── Badge.tsx
├── features/        # Feature-specific components
│   ├── TaskCard.tsx
│   ├── TaskFilter.tsx
│   └── PriorityTag.tsx
└── layouts/         # Page layouts
    ├── DashboardLayout.tsx
    └── AuthLayout.tsx
```

### 3. TypeScript Interface Design

Define comprehensive prop interfaces with JSDoc comments. Use proper async/Promise types for callbacks. Include optional props with `?` operator. Extend HTML element types when appropriate.

### 4. Tailwind CSS Styling

Apply design system from `@specs/ui/design-system.md`:
- Colors: `bg-white dark:bg-zinc-800`, `text-neutral-900 dark:text-neutral-50`
- Spacing: 8px base unit (`p-4 md:p-6`, `space-y-4`)
- Typography: `font-sans` (Inter), `font-mono` (JetBrains Mono)
- Glassmorphism: `bg-white/10 dark:bg-black/30 backdrop-blur-md border border-white/20`
- Responsive: `grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3` (mobile-first)

Use Tailwind classes exclusively. Support dark mode with `dark:` variant. Use `cn()` utility for conditional classes.

### 5. shadcn/ui Integration

Import and customize shadcn/ui components (Button, Card, Badge). Leverage their variant APIs for consistent styling.

### 6. State Management

Use React hooks (useState, useCallback) for client components. Memoize callbacks to prevent unnecessary re-renders.

### 7. Accessibility

Apply WCAG 2.1 AA standards from `@specs/ui/accessibility.md`:
- `aria-label` for icon-only buttons
- `aria-describedby` for form inputs with help text
- `aria-required` for required fields
- `role` for non-semantic elements
- `aria-hidden="true"` for decorative icons
- Focus indicators with `focus:ring-2 focus:ring-offset-2`

### 8. Responsive Behavior

Mobile-first breakpoints from `@specs/ui/responsive-design.md`. Stack vertically on mobile, use flexbox/grid on larger screens. Ensure touch-friendly sizing (44x44px minimum for buttons).

## Component Templates

See `references/component-templates.md` for complete examples of:
- Atomic components (Button with variants using CVA)
- Feature components (TaskCard with glassmorphism)
- Form components (TaskForm with validation)

## Quality Checklist

Before delivering a component, verify:
- [ ] TypeScript interface defined with JSDoc comments
- [ ] 'use client' directive added if using hooks/events
- [ ] Tailwind classes follow design system
- [ ] Dark mode supported with `dark:` variants
- [ ] Mobile-first responsive design implemented
- [ ] Accessibility attributes present (ARIA, semantic HTML)
- [ ] Focus indicators visible
- [ ] Component handles loading/error states
- [ ] Props validated with TypeScript (no `any` types)
- [ ] File path follows project structure conventions

## References

- **Design System**: `@specs/ui/design-system.md` for complete design tokens
- **Layout Patterns**: `@specs/ui/dashboard-layout.md` for component placement
- **Accessibility**: `@specs/ui/accessibility.md` for WCAG 2.1 AA requirements
- **Frontend Guidelines**: `frontend/CLAUDE.md` for Next.js 15+ conventions
- **Component Templates**: `references/component-templates.md` for complete examples
