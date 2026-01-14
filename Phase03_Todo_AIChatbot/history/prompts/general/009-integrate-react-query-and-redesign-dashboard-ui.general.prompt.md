---
id: 009
title: Integrate React Query and Redesign Dashboard UI
stage: general
date: 2026-01-06
surface: agent
model: claude-sonnet-4-5-20250929
feature: dashboard
branch: main
user: unknown
command: continue-session
labels: [react-query, ui-redesign, dashboard, frontend, tests]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
 - frontend/app/dashboard/page.tsx
 - frontend/app/layout.tsx
 - frontend/components/providers/QueryProvider.tsx
 - frontend/components/tasks/TaskCard.tsx
 - frontend/hooks/use-tasks.ts
 - frontend/lib/api.ts
 - frontend/lib/types.ts
 - frontend/__tests__/dashboard/dashboard-crud.test.tsx
tests:
 - npm --prefix frontend run test
 - npm --prefix frontend run lint
---

## Prompt

Integrated React Query for fetching and state management in the dashboard. Redesigned the Dashboard UI (both Grid and List views) to be "very attractive" and fixed the layout destructuring issue observed in Grid mode. Ensured the backend was not modified ("dont destructure backend").

## Response snapshot

- Installed `@tanstack/react-query` and set up `QueryProvider` in `app/layout.tsx`.
- Created a centralized `taskApi` client and custom hooks (`useTasks`, `useCreateTask`, `useUpdateTask`, `useDeleteTask`) for robust data management.
- Extracted and redesigned the `TaskCard` component with a professional, glassmorphism-based UI and fixed positioning for action buttons.
- Resolved the Grid view "destructuring" issue by enforcing strict layout constraints and using modern CSS grid patterns.
- Refactored `app/dashboard/page.tsx` to remove manual state management and complex `useEffect` logic, significantly improving code maintainability.
- Updated Vitest tests to include `QueryClientProvider` and matched expectations with the new UI labels/structure.
- Verified all fixes with `npm run lint` and `npm run test` (both PASS).

## Outcome

- ✅ Impact: Dashboard is now highly performant with immediate UI feedback (via React Query) and has a professional, attractive design that works flawlessly in both Grid and List modes.
- 🧪 Tests: Frontend Vitest tests 100% PASS with the new architecture.
- 📁 Files: Cleanly separated API, types, hooks, and components for better scalability.
- 🔁 Next prompts: Consider implementing optimistic updates in mutation hooks for even faster-feeling interactions.
- 🧠 Reflection: Moving to a dedicated component (`TaskCard`) and a professional state management library (React Query) solved both the technical "disappearing tasks" bug and the aesthetic layout issues in one cohesive sweep.

## Evaluation notes (flywheel)

- Failure modes observed: Missing `cn` import and missing `QueryClientProvider` in tests (both resolved).
- Graders run and results (PASS/FAIL): Frontend lint PASS, frontend tests PASS.
- Prompt variant (if applicable): null
- Next experiment (smallest change to try): Add `framer-motion` layout animations between view mode toggles.
