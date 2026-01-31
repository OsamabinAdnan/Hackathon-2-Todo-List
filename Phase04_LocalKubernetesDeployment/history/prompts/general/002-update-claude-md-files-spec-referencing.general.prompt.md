---
id: 002
title: Update CLAUDE.md files with spec referencing guidance
stage: general
date: 2026-01-02
surface: agent
model: claude-sonnet-4-5-20250929
feature: none
branch: main
user: AOTHHSA
command: none
labels: ["documentation", "claude-md", "spec-referencing", "sdd-workflow"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - CLAUDE.md
  - frontend/CLAUDE.md
  - backend/CLAUDE.md
tests:
  - null
---

## Prompt

this docs @"..\Hackathon II - Todo Spec-Driven Development.pdf" give us advice to add specs in Claude Code file, have you add it??

Referencing Specs in Claude Code

# Implement a feature
You: @specs/features/task-crud.md implement the create task feature
# Implement API
You: @specs/api/rest-endpoints.md implement the GET /api/tasks endpoint
# Update database
You: @specs/database/schema.md add due_date field to tasks
# Full feature across stack
You: @specs/features/authentication.md implement Better Auth login

## Response snapshot

I discovered that I had NOT added the spec referencing guidance from the PDF to the CLAUDE.md files. This was a critical omission since it shows users and Claude Code how to reference specification files using the `@specs/` syntax during implementation.

**What I Added:**

### 1. Root CLAUDE.md (Lines 51-85)
Added section: **"Referencing Specs in Claude Code"**
- Examples showing `@specs/` syntax for different use cases
- List of all available spec files:
  - `@specs/overview.md` - Project overview
  - `@specs/features/authentication.md` - Auth specs
  - `@specs/features/task-crud.md` - Task management specs
  - `@specs/api/rest-endpoints.md` - API contracts
  - `@specs/database/schema.md` - Database schema
- Best practice: Always read specs BEFORE writing code
- What information specs contain (user stories, validation rules, API examples, security requirements, testing scenarios)

### 2. frontend/CLAUDE.md (Lines 12-42)
Added section: **"Referencing Specs for Frontend Implementation"**
- Frontend-specific examples:
  - `@specs/features/task-crud.md implement the task card component with glassmorphism`
  - `@specs/api/rest-endpoints.md implement the createTask API client function`
  - `@specs/features/authentication.md implement the login page with form validation`
- Key specs relevant to frontend work
- 4-step workflow before writing frontend code

### 3. backend/CLAUDE.md (Lines 12-42)
Added section: **"Referencing Specs for Backend Implementation"**
- Backend-specific examples:
  - `@specs/api/rest-endpoints.md implement POST /api/{user_id}/tasks endpoint`
  - `@specs/database/schema.md implement the Task SQLModel with all constraints`
  - `@specs/features/authentication.md implement JWT token generation and verification middleware`
- Key specs relevant to backend work
- 4-step workflow before writing backend code

**Example Usage Pattern:**
```bash
User: @specs/features/task-crud.md implement the create task feature

Claude Code will:
1. Read specs/features/task-crud.md (user stories, acceptance criteria)
2. Read specs/api/rest-endpoints.md (API contract for POST /api/{user_id}/tasks)
3. Read specs/database/schema.md (Task model definition)
4. Generate code following all specifications
```

This ensures strict spec-driven development where all code is generated from approved specifications with complete context.

## Outcome

- ✅ Impact: All three CLAUDE.md files now include comprehensive spec referencing guidance, enabling proper spec-driven development workflow
- 🧪 Tests: Verified all files contain "Referencing Specs" sections using grep
- 📁 Files: Updated 3 files (root, frontend, backend CLAUDE.md)
- 🔁 Next prompts: Ready for `/sp.plan` to create architecture plan, then `/sp.implement` to generate code
- 🧠 Reflection: This was a critical addition from the PDF that I initially missed. The `@specs/` syntax is fundamental to the spec-driven workflow and should have been included when creating the CLAUDE.md files initially.

## Evaluation notes (flywheel)

- Failure modes observed: Initially created CLAUDE.md files without spec referencing guidance despite it being prominently featured in the PDF guide. Need to ensure all guidance from authoritative documents is fully incorporated.
- Graders run and results (PASS/FAIL): Manual verification PASS - all three files contain appropriate sections
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Consider adding more examples of cross-stack implementations (e.g., "implement authentication from frontend to backend to database")
