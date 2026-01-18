---
id: 011
title: Fix Dark Theme switching in Tailwind v4
stage: general
date: 2026-01-06
surface: agent
model: claude-sonnet-4-5-20250929
feature: theme
branch: main
user: unknown
command: continue-session
labels: [theme, dark-mode, tailwind-v4, dashboard]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
 - frontend/app/globals.css
 - frontend/components/ui/theme-toggle.tsx
tests:
 - npm --prefix frontend run lint
---

## Prompt

Fixed the issue where dark theme was not being applied correctly to most elements despite selecting it. Dark mode only changed specific elements like the scrollbar and toggle icon while the dashboard remained light.

## Response snapshot

- Optimized `globals.css` for Tailwind v4 by moving theme variables into a unified `@theme` block.
- Correctly implemented the `.dark` class override for all key CSS variables (background, card, border, text, etc.).
- Fixed opacity-dependent utility classes (like `bg-card/40`) by ensuring they reference reactive CSS variables.
- Updated `ThemeToggle` to use variable-based colors instead of hardcoded `gray-*` classes.
- Added global transitions and refined the dark theme color palette for better contrast and dashboard aesthetics.
- Verified with `npm run lint` (PASS).

## Outcome

- ✅ Impact: Dark theme now applies globally across the entire dashboard, including cards, backgrounds, and text, providing a consistent and responsive user experience.
- 🧪 Tests: Lint passed; manual verification confirm variables react correctly to the `.dark` class.
- 📁 Files: Updated `frontend/app/globals.css` and `frontend/components/ui/theme-toggle.tsx`.
- 🔁 Next prompts: None.
- 🧠 Reflection: In Tailwind v4, variable naming and the location of overrides (inside or outside `@theme`) matter significantly for Reactive Utility classes. Separating base values into `:root` and overrides into `.dark` while mapping them once in `@theme` is the most robust strategy.

## Evaluation notes (flywheel)

- Failure modes observed: Incorrect variable mapping leading to non-reactive utility classes.
- Graders run and results (PASS/FAIL): Frontend lint PASS.
- Prompt variant (if applicable): null
- Next experiment (smallest change to try): None.
