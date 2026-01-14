---
id: 003
title: "Phase 3 AI Chatbot Clarification"
stage: "clarify"
date_iso: "2026-01-13"
model: "claude-sonnet-4-5-20250929"
feature: "2-todo-ai-chatbot"
branch: "main"
user: "osamabinadnan"
command: "sp.clarify"
labels: ["spec", "clarification", "ai-chatbot", "phase3"]
links:
  spec: "null"
  ticket: "null"
  adr: "null"
  pr: "null"
files_yaml: |
  - specs/2-todo-ai-chatbot/spec.md
tests_yaml: |
  - "specs/2-todo-ai-chatbot/spec.md: Updated clarifications section with 5 key decisions"
---

# Phase 3 AI Chatbot Clarification

## Original Prompt
Clarify spec for Phase 3: Todo AI Chatbot

## Summary of Changes
This clarification session resolved 5 key architectural decisions for the Phase 3 AI Chatbot implementation:

1. **Frontend UI Approach**: Use OpenAI ChatKit (hosted solution) with domain allowlist configuration
2. **MCP Server Implementation**: Build MCP server with Official MCP SDK that exposes task operations as tools to agent
3. **Agent Integration Architecture**: FastAPI backend handles stateless chat endpoint and uses OpenAI Agents SDK for orchestration, connecting to separate MCP server
4. **Conversation Persistence**: Stateless architecture using Neon Serverless PostgreSQL database via SQLModel with detailed request cycle
5. **Security & Authentication**: JWT token validation on each request with user_id verification

## Technical Decisions Made
- MCP tools will be stateless and store state in the database
- Clear separation between FastAPI backend (agent orchestration) and MCP server (task operations)
- All conversation state persisted to database for seamless resumption
- User isolation enforced through JWT token validation
- Official MCP SDK used to build MCP server

## Impact
These clarifications provide clear architectural direction for implementing the AI chatbot while maintaining alignment with Phase 2 infrastructure and security requirements. The stateless architecture ensures scalability and reliability.

## Next Steps
Proceed with `/sp.plan` to create implementation plan based on these clarified requirements.