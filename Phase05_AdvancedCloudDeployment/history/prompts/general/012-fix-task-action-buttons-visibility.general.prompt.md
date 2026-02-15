---
id: 012
title: Fix Task Action buttons visibility in Light and Dark themes
stage: general
date: 2026-01-06
surface: agent
model: claude-sonnet-4-5-20250929
feature: dashboard
branch: main
user: unknown
command: continue-session
labels: [ui, theme, accessibility, bug-fix]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
 - frontend/components/tasks/TaskCard.tsx
tests:
 - npm --prefix frontend run lint
---

## Prompt

Fixed an issue where the Edit and Delete buttons in the TaskCard component were disappearing or hard to see in both light and dark themes. The buttons were previously set to `opacity-0` and only appeared on hover, which caused them to be "missing" for users when not actively hovering or when contrast was low.

## Response snapshot

- Removed `opacity-0` and `group-hover:opacity-100` from the task action button container to ensure buttons are always visible.
- Added a subtle background (`bg-accent/5`) and transparent border to the action buttons in their resting state to improve presence and contrast.
- Updated transition from `transition-colors` to `transition-all` to support border and background transitions.
- Improved hover states with matched border colors (`hover:border-primary/20` and `hover:border-danger/20`).
- Verified with `npm run lint` (PASS).

## Outcome

- ✅ Impact: Users can now immediately see and access task management actions (Edit/Delete) without needing to guess where they are or rely on hover states.
- 🧪 Tests: Lint passed.
- 📁 Files: Updated `frontend/components/tasks/TaskCard.tsx`.
- 🔁 Next prompts: None.
- 🧠 Reflection: While "show on hover" can reduce visual clutter, it often fails accessibility and usability tests if the elements are completely invisible at rest. Providing a subtle, low-opacity background ensures they are discoverable while maintaining the clean "glass" aesthetic of the dashboard.

## Evaluation notes (flywheel)

- Failure modes observed: Reliance on hover for critical functionality hide buttons from touch/mobile users and cause "disappearing" bug reports.
- Graders run and results (PASS/FAIL): Frontend lint PASS.
- Prompt variant (if applicable): null
- Next experiment (smallest change to try): None.
