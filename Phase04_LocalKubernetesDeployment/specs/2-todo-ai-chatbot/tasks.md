# Todo AI Chatbot (Phase-3) - Tasks

## Overview
This document breaks down the implementation of the Todo AI Chatbot for Phase 3 into executable tasks following the checklist format. Each task is designed to be testable and verifiable.

## Phase 1: Setup
- [X] T001 Set up MCP server directory structure in backend/app/mcp/
- [X] T002 Configure environment variables for OpenRouter integration in backend/.env

## Phase 2: Foundational
- [X] T003 Create Conversation and Message SQLModel database models in backend/app/models/conversation.py
- [X] T004 Create Alembic migration for conversation/message tables in backend/migrations/
- [X] T005 [P] Set up MCP server infrastructure in backend/app/mcp/server.py
- [X] T006 [P] Install OpenAI Agents SDK in backend/requirements.txt
- [X] T007 [P] Configure OpenRouter client with custom base URL in backend/app/config/

## Phase 3: [US1] MCP Tools Implementation
- [X] T008 [US1] Implement add_task MCP tool with user_id validation in backend/app/mcp/tools.py
- [X] T009 [US1] Implement list_tasks MCP tool with status filtering in backend/app/mcp/tools.py
- [X] T010 [US1] Implement complete_task MCP tool with ownership check in backend/app/mcp/tools.py
- [X] T011 [US1] Implement update_task MCP tool with ownership check in backend/app/mcp/tools.py
- [X] T012 [US1] Implement delete_task MCP tool with ownership check in backend/app/mcp/tools.py
- [X] T013 [US1] Add error handling for all MCP tools in backend/app/mcp/tools.py

## Phase 4: [US2] AI Agent Configuration
- [X] T014 [US2] Create agent directory structure in backend/app/agents/
- [X] T015 [US2] Define agent instructions for todo management in backend/app/agents/todo_agent.py
- [X] T016 [US2] Connect agent to MCP tools in backend/app/agents/todo_agent.py
- [X] T017 [US2] Configure tool invocation logic in backend/app/agents/todo_agent.py
- [X] T018 [US2] Add conversation context management in backend/app/agents/todo_agent.py

## Phase 5: [US3] Chat API Endpoint
- [X] T019 [US3] Implement POST /api/{user_id}/chat endpoint in backend/app/routes/chat.py
- [X] T020 [US3] Add JWT authentication to chat endpoint in backend/app/routes/chat.py
- [X] T021 [US3] Fetch conversation history from database in backend/app/routes/chat.py
- [X] T022 [US3] Store user messages in database in backend/app/routes/chat.py
- [X] T023 [US3] Store assistant responses in database in backend/app/routes/chat.py
- [X] T024 [US3] Return structured response with tool_calls in backend/app/routes/chat.py

## Phase 6: [US4] Frontend ChatKit Integration
- [X] T025 [US4] Install Chatbot dependencies in frontend/package.json
- [X] T026 [US4] Configure Chatbot component with backend endpoint in frontend/components/ChatKitWrapper.tsx
- [X] T027 [US4] Style Chatbot to match Phase 2 theme (glassmorphism, dark mode) in frontend/components/ChatKitWrapper.tsx
- [X] T028 [US4] Attach JWT token to chat requests in frontend/lib/api/chat.ts
- [ ] T029 [US4] Implement an AI-powered Chatbot component on the Dashboard (frontend/app/dashboard/page.tsx) with the following requirements:
    - [ ] Add a floating Chatbot button positioned at the bottom-right corner of the Dashboard.
    - [ ] When clicked, the button should open a Chatbot panel or modal.
    - [ ] The Chatbot must be able to list all tasks and perform full CRUD operations (create, read, update, delete) on tasks.
    - [ ] All task changes performed via the Chatbot should immediately reflect on the Dashboard UI.
    - [ ] Display Sonner notifications for successful actions and error states.
    - [ ] The Chatbot should execute all task operations through an AI Agent integrated with MCP tools.
    - [ ] Keep in mind the functionality of Dashboard remain as usual (same we made in Phase 2), Chatbot just give user the ability to manage tasks via natural language

## Phase 7: [US5] Validation and Testing
- [ ] T030 [US5] Test add_task functionality via chat in backend/tests/test_mcp_tools.py
- [ ] T031 [US5] Test list_tasks functionality via chat in backend/tests/test_mcp_tools.py
- [ ] T032 [US5] Test complete_task functionality via chat in backend/tests/test_mcp_tools.py
- [ ] T033 [US5] Test update_task functionality via chat in backend/tests/test_mcp_tools.py
- [ ] T034 [US5] Test delete_task functionality via chat in backend/tests/test_mcp_tools.py
- [ ] T035 [US5] Test conversation persistence across sessions in backend/tests/test_conversation_persistence.py
- [ ] T036 [US5] Test user isolation (can't access other users' data) in backend/tests/test_security.py
- [ ] T037 [US5] Test error handling and graceful degradation in backend/tests/test_error_handling.py

## Phase 8: Polish & Cross-Cutting Concerns
- [ ] T038 Add rate limiting to chat endpoint in backend/app/middleware/rate_limiter.py
- [ ] T039 Optimize database queries for conversation history in backend/app/utils/query_optimizer.py
- [ ] T040 Add comprehensive logging for chat interactions in backend/app/utils/logger.py
- [ ] T041 Update documentation for Phase 3 features in docs/phase3-implementation.md
- [ ] T042 Perform security review of authentication implementation in backend/app/middleware/auth.py

## Dependencies & Execution Order

### Story Dependencies:
- US1 (MCP Tools) must complete before US2 (AI Agent) and US3 (Chat API)
- US2 (AI Agent) must complete before US3 (Chat API)
- US3 (Chat API) must complete before US4 (Frontend Integration)
- US4 (Frontend Integration) must complete before US5 (Validation)

### Parallel Opportunities:
- Tasks T005, T006, T007 can run in parallel during foundational phase
- MCP tool implementations (T008-T012) can be developed in parallel
- Database operations (T021-T023) can run in parallel during API implementation

### MVP Scope:
- Minimum viable product includes US1 (MCP Tools) and US3 (Chat API)
- Basic chat functionality allowing users to manage tasks via natural language
- Conversation persistence and user authentication

## Implementation Strategy

### Approach:
1. Complete foundational setup (database models, MCP infrastructure)
2. Implement MCP tools (core functionality)
3. Configure AI agent in dedicated backend/app/agents/ folder
4. Create chat API endpoint that integrates with the agent
5. Integrate frontend ChatKit
6. Perform validation and testing

### Delivery:
- Incremental delivery with each user story providing complete functionality
- Early validation of core concepts before UI integration
- Continuous testing throughout development process