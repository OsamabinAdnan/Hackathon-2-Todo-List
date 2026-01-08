---
id: 008
title: Fix dashboard fetch and CRUD
stage: general
date: 2026-01-06
surface: agent
model: claude-sonnet-4-5-20250929
feature: none
branch: main
user: unknown
command: continue-session
labels: [dashboard,crud,frontend,tests]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
 - frontend/app/dashboard/page.tsx
 - frontend/package.json
 - frontend/vitest.config.ts
 - frontend/__tests__/setup.ts
 - frontend/__tests__/dashboard/dashboard-crud.test.tsx
 - backend/tests/conftest.py
 - backend/tests/test_tasks_list_shape.py
tests:
 - npm --prefix frontend run test
 - uv --directory backend run python -m pytest -q
 - npm --prefix frontend run lint
---

## Prompt

what about remaining stuff??

## Response snapshot

- Added per-task edit/delete icon buttons in both list and grid views in `frontend/app/dashboard/page.tsx`.
- Fixed "tasks disappear after reload" by making the dashboard accept the backend's raw-array response shape.
- Added Vitest + React Testing Library setup and a dashboard CRUD test suite; ran `npm --prefix frontend run test` successfully.
- Added minimal backend pytest scaffolding and ran `uv --directory backend run python -m pytest -q` (tests currently skipped due to SQLite not supporting PostgreSQL ARRAY used by Task.tags).
- Re-ran `npm --prefix frontend run lint` and resolved the remaining warning.

## Outcome

- ✅ Impact: Dashboard now reliably shows persisted tasks after reload, and each task has edit/delete actions that persist to the backend.
- 🧪 Tests: Frontend Vitest tests passing; backend pytest runs with 1 skipped due to ARRAY/SQLite limitation.
- 📁 Files: Updated dashboard page + added test tooling/config and initial tests.
- 🔁 Next prompts: Consider switching backend tests to run against Postgres (or adapting Task.tags for SQLite test dialect) so backend tests are not skipped.
- 🧠 Reflection: The key production bug was a client/server response-shape mismatch (array vs {tasks: []}), which silently cleared UI state on reload.

## Evaluation notes (flywheel)

- Failure modes observed: Config/tooling mismatch for Vitest ESM plugin, and SQLite incompatibility with PostgreSQL ARRAY type.
- Graders run and results (PASS/FAIL): Frontend lint PASS, frontend tests PASS, backend tests SKIP (needs Postgres).
- Prompt variant (if applicable): null
- Next experiment (smallest change to try): Add a Postgres-backed test session for backend pytest (env var driven DATABASE_URL for tests).
