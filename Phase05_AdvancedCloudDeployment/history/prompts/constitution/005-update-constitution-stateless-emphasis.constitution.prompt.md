---
id: 005
title: Update Constitution Stateless Emphasis
stage: constitution
date: 2026-01-16
surface: agent
model: claude-sonnet-4-5-20250929
feature: phase-3-ai-chatbot
branch: main
user: claude
command: sp.constitution
labels: [constitution, phase-3, stateless-architecture, ai-chatbot]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .specify/memory/constitution.md
tests:
  - constitution validation
---

## Prompt

```
You are Claude Code acting as a senior AI systems engineer executing Phase-3 of a Spec-Driven Development workflow using Spec-Kit Plus.

====================================
PHASE-3 OBJECTIVE
====================================

Extend the existing Phase-2 Todo Full-Stack Web Application into an AI-powered Conversational User Interface (CUI).

This phase introduces:
- Natural language task management
- AI agents powered by OpenAI Agents SDK
- An MCP (Model Context Protocol) server exposing task operations as tools

The existing Phase-2 frontend, backend, authentication, and database code is preserved and reused.

====================================
CORE PRINCIPLES
====================================

- Spec-first development is mandatory
- No manual coding; Claude Code performs all changes
- Phase-2 functionality must remain intact
- Conversational interface replaces GUI task interactions
- All AI behavior must be tool-driven via MCP

====================================
ARCHITECTURAL CONSTRAINTS
====================================

Frontend:
- Next.js (App Router)
- Tailwind CSS
- shadcn/ui
- OpenAI ChatKit UI

Backend:
- FastAPI
- SQLModel
- Neon PostgreSQL
- OpenAI Agents SDK
- Official MCP SDK

====================================
KEY DESIGN RULE
====================================

The server must be stateless.
All conversation and task state must be persisted in the database.
```

## Response snapshot

The constitution file at `.specify/memory/constitution.md` has been successfully updated from version 1.1.0 to 1.2.0. The update emphasizes the stateless architecture requirements for Phase 3: Todo AI Chatbot Integration, with specific focus on the requirement that "the server must be stateless; all conversation and task state must be persisted in the database."

Key changes include:
1. Enhanced emphasis on stateless server architecture in Section X (AI Chatbot Integration)
2. Reinforced the stateless design principle in Section VII (Model Context Protocol)
3. Updated sync impact report documenting the changes
4. Maintained all existing principles, specifications, and requirements for both Phase 2 and Phase 3
5. Updated version information to 1.2.0 with proper dates and amendment type

## Outcome

- ✅ Impact: Constitution updated to v1.2.0 with enhanced stateless architecture emphasis for Phase 3
- 🧪 Tests: No functional tests required, only documentation update
- 📁 Files: .specify/memory/constitution.md updated successfully
- 🔁 Next prompts: Ready for Phase 3 implementation following updated constitution
- 🧠 Reflection: The update successfully emphasizes the critical stateless architecture requirement while preserving all existing functionality and requirements.

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): N/A for documentation update
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Begin Phase 3 implementation following the updated constitution guidelines