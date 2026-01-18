# Todo AI Chatbot (Phase-3) - Implementation Plan

## Overview
This document outlines the implementation plan for the Todo AI Chatbot for Phase 3, extending the existing Todo application with conversational AI for natural language task management using OpenAI Agents SDK and Model Context Protocol (MCP).

## Phase 3.0: Read Official Docs
- [X] Read OpenAI Agents SDK documentation for agent creation and tool registration
- [X] Study Official MCP SDK for server and tool implementation
- [X] Review OpenRouter API integration with OpenAI SDK
- [X] Understand conversation persistence patterns with database storage
- [X] Document security and authentication best practices

## Phase 3.1: Spec Creation
- [X] Create agent behavior specification (already completed)
- [X] Create MCP tools specification (already completed)
- [X] Create chat API specification (already completed)

## Phase 3.2: Backend Augmentation

### 3.2.1: OpenAI Agents SDK with OpenRouter Integration
- [X] Create `agents/` directory in backend/app/agents/
- [X] Set up custom OpenAI client with OpenRouter configuration
  ```python
  from openai import AsyncOpenAI
  from app.config.settings import settings

  custom_client = AsyncOpenAI(
      base_url=settings.OPENROUTER_BASE_URL,
      api_key=settings.OPENROUTER_API_KEY,
      default_headers={
          "HTTP-Referer": settings.APP_URL,
          "X-Title": settings.APP_NAME
      }
  )
  ```
- [X] Implement agent initialization with proper instructions
- [X] Configure model settings for tool choice and behavior
- [X] Add error handling for OpenRouter API calls

### 3.2.2: MCP Server Implementation
- [X] Create `mcp/` directory in backend/app/mcp/
- [X] Initialize MCP server with authentication support
  ```python
  from mcp.server import Server
  from mcp.server.auth.provider import TokenVerifier
  from mcp.server.auth.settings import AuthSettings

  server = Server("Todo MCP Server")

  class JWTTokenVerifier(TokenVerifier):
      async def verify_token(self, token: str) -> dict:
          # Verify JWT token and return user information
          from jose import jwt
          from app.config.settings import settings

          try:
              payload = jwt.decode(
                  token,
                  settings.SECRET_KEY,
                  algorithms=[settings.ALGORITHM]
              )
              return payload
          except jwt.JWTError:
              return None

  # Configure server with authentication
  server.configure(
      auth=AuthSettings(
          token_verifier=JWTTokenVerifier(),
          required_scopes=["user"]
      )
  )
  ```
- [X] Set up streamable HTTP transport for MCP server

### 3.2.3: MCP Tools Implementation
- [X] Implement `add_task` MCP tool with user_id validation
  - [X] Validate user_id from JWT token
  - [X] Create task in database for authenticated user
  - [X] Return structured response with task_id
- [X] Implement `list_tasks` MCP tool with status filtering
  - [X] Validate user_id from JWT token
  - [X] Query tasks for authenticated user with status filter
  - [X] Return array of task objects
- [X] Implement `complete_task` MCP tool with ownership check
  - [X] Validate user_id and task ownership
  - [X] Update task completion status
  - [X] Return updated task info
- [X] Implement `update_task` MCP tool with ownership check
  - [X] Validate user_id and task ownership
  - [X] Update task title/description
  - [X] Return updated task info
- [X] Implement `delete_task` MCP tool with ownership check
  - [X] Validate user_id and task ownership
  - [X] Remove task from database
  - [X] Return confirmation
- [X] Add proper error handling for all tools
- [X] Add user isolation to prevent cross-user access

## Phase 3.3: Conversation Persistence

### 3.3.1: Database Schema Extensions
- [X] Create Conversation and Message SQLModel database models in backend/app/models/conversation.py
- [X] Create Alembic migration for conversation/message tables in backend/migrations/
- [X] Update existing Task model to include proper foreign key relationships if needed

### 3.3.2: Message Storage and Retrieval
- [X] Implement conversation creation/retrieval functions
- [X] Create message storage functions for user and assistant messages
- [X] Implement conversation history retrieval with pagination
- [X] Add functions to store tool call results in messages
- [X] Optimize queries with proper indexing

### 3.3.3: Stateless Server Implementation
- [X] Implement stateless request handling for chat endpoint
- [X] Fetch conversation history from database on each request
- [X] Store user message in database before agent processing
- [X] Store assistant response in database after agent processing
- [X] Ensure server maintains no in-memory conversation state

## Phase 3.4: [US3] Chat API Endpoint
- [X] Implement POST /api/{user_id}/chat endpoint in backend/app/routes/chat.py
- [X] Add JWT authentication to chat endpoint
- [X] Fetch conversation history from database
- [X] Store user messages in database
- [X] Store assistant responses in database
- [X] Return structured response with tool_calls

## Phase 3.5: Frontend ChatKit Integration
- [ ] Install ChatKit dependencies in frontend/package.json
- [ ] Configure ChatKit component with backend endpoint in frontend/components/ChatKitWrapper.tsx
- [ ] Style ChatKit to match Phase 2 theme (glassmorphism, dark mode) in frontend/components/ChatKitWrapper.tsx
- [ ] Attach JWT token to chat requests in frontend/lib/api/chat.ts
- [ ] Replace task CRUD UI with ChatKit component in frontend/app/dashboard/page.tsx

## Phase 3.6: Validation and Testing
- [ ] Test add_task functionality via chat
- [ ] Test list_tasks functionality via chat
- [ ] Test complete_task functionality via chat
- [ ] Test update_task functionality via chat
- [ ] Test delete_task functionality via chat
- [ ] Test conversation persistence across sessions
- [ ] Test user isolation (can't access other users' data)
- [ ] Test error handling and graceful degradation

## Phase 3.7: Security & Compliance
- [ ] Verify JWT token validation on all chat endpoints
- [ ] Test user isolation for conversations and tasks
- [ ] Validate proper error responses for unauthorized access
- [ ] Test rate limiting and request validation
- [ ] Perform security scan for vulnerabilities

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