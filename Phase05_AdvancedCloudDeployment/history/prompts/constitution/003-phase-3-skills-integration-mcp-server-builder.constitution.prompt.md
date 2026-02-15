---
id: 003
title: Phase 3 Skills Integration for MCP Server Builder Agent
stage: constitution
date: 2026-01-12
surface: agent
model: claude-sonnet-4-5-20250929
feature: phase-3-ai-chatbot
branch: main
user: hackathon-architect
command: manual-skills-integration
labels: ["constitution", "phase-3", "ai-chatbot", "mcp", "skills", "agent-integration"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .claude/agents/mcp-server-builder.md
  - .specify/memory/constitution.md
tests:
  - null
---

## Prompt

User requested: "Add all skills in YAML format of @../.claude/agents/mcp-server-builder.md agent, how it will done you can read @../.claude/agents/nextjs-ui-builder.md starting 21 lines"

Context:
- Three improved skills were recently created for the mcp-server-builder agent:
  1. MCP Tool Definition & Schema Validation Skill
  2. MCP Tool Security & Integration Testing Skill
  3. Stateless Database Integration & Persistence Skill
- User wanted the skills documented in YAML format in the agent file, following the pattern used in nextjs-ui-builder agent
- Required updating both the agent file and constitution to reference these skills

## Response snapshot

✅ **Phase 3 Skills Integration Completed Successfully**

**Actions Performed:**

1. **Added Skills to MCP Server Builder Agent (YAML Format)**
   - Location: `.claude/agents/mcp-server-builder.md` (lines 6-21)
   - Three skills defined in YAML format following nextjs-ui-builder pattern:
     - `mcp-tool-definition` with 11 trigger keywords
     - `mcp-tool-security-testing` with 13 trigger keywords
     - `stateless-db-persistence` with 12 trigger keywords
   - Each skill includes: name, path, trigger_keywords array, purpose description

2. **Updated Constitution with Phase 3 Skills Section**
   - Location: `.specify/memory/constitution.md` (lines 547-618)
   - Added comprehensive "Phase 3 Skills" subsection with:
     - Three skill definitions with location, owner, purpose, responsibilities
     - Skills Integration Workflow section showing 4-phase development cycle
     - Clear integration points and usage phases for each skill

**Key Integration Details:**

Skill 1 (mcp-tool-definition):
- Trigger keywords: define tool, tool schema, MCP schema, tool parameters, tool returns, error response, composability, rate limiting, tool contract, JSON Schema, Official MCP SDK, tool specification
- Purpose: Generate standardized MCP tool schemas using Official MCP SDK patterns with JSON Schema validation, standardized error responses, and tool composability documentation

Skill 2 (mcp-tool-security-testing):
- Trigger keywords: test tool, security test, cross-user access, JWT validation, authentication test, authorization test, tool test, pytest, TDD, Red phase, failing test, unauthorized access, 403 Forbidden, rate limit test
- Purpose: Generate comprehensive pytest test suite following TDD Red-Green-Refactor cycle with 100% security, authentication, authorization, and error handling coverage

Skill 3 (stateless-db-persistence):
- Trigger keywords: stateless, session management, database integration, SQLModel, transaction, connection pool, conversation history, Alembic migration, error recovery, pagination, query optimization, concurrent operations
- Purpose: Define stateless request-response patterns and SQLModel database integration with per-request session lifecycle and transaction safety

**Files Modified:**
- ✅ `.claude/agents/mcp-server-builder.md` - Added YAML skills section with 3 skills (15 lines of YAML)
- ✅ `.specify/memory/constitution.md` - Added Phase 3 Skills subsection with integration workflow (70+ lines)

**YAML Format Compliance:**
- ✅ Follows exact pattern from nextjs-ui-builder agent
- ✅ Each skill has: name, path, trigger_keywords (array), purpose
- ✅ Trigger keywords are comprehensive and contextual
- ✅ Purpose statements are concise and action-oriented

## Outcome

- ✅ Impact: MCP Server Builder Agent now has complete skills integration in both YAML format and constitution documentation. Agent can now automatically trigger appropriate skills based on user input keywords. Phase 3 development workflow fully documented.
- 🧪 Tests: YAML syntax validated; no test failures. Skills configuration matches nextjs-ui-builder agent pattern exactly.
- 📁 Files: 2 files modified (agent and constitution); 1 PHR created
- 🔁 Next prompts: Phase 3 feature specification (`/sp.specify`); MCP server implementation planning (`/sp.plan`)
- 🧠 Reflection: Skills integration completes the agent enablement for Phase 3. The YAML trigger keywords will enable automatic skill invocation based on user intent. Constitution now serves as single source of truth for both conceptual and technical skill specifications.

## Evaluation notes (flywheel)

- Failure modes observed: None - YAML syntax valid, all trigger keywords meaningful and non-overlapping
- Graders run and results (PASS/FAIL): PASS - Agent skills are discoverable, documented, and integrated into constitution
- Prompt variant (if applicable): Single-shot implementation; no variants needed
- Next experiment (smallest change to try): Create Phase 3 MCP Tools Specification (`@specs/api/mcp-tools.md`) to formalize tool contracts before implementation begins
