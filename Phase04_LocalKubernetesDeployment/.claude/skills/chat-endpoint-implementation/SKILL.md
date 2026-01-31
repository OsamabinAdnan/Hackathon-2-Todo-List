---
name: chat-endpoint-implementation
description: "Generate production-grade FastAPI chat endpoints (POST /api/{user_id}/chat) with Pydantic request/response validation, Agent SDK configuration, JWT authentication, idempotency handling, transaction management, and conversation history pagination. Use when: (1) implementing chat endpoint from @specs/api/rest-endpoints.md, (2) integrating OpenAI Agent SDK with MCP tool routing, (3) designing request/response contracts with validation models, (4) adding idempotency and trace ID tracking, (5) managing conversation history pagination and token counting, (6) handling agent execution timeouts and error recovery, (7) ensuring user authorization and preventing cross-user access."
---

# Chat Endpoint Implementation

## Core Responsibility

Implement the complete `POST /api/{user_id}/chat` endpoint that:
1. Validates JWT tokens and extracts user_id
2. Receives user message + optional conversation_id
3. Manages conversation lifecycle (create new or resume existing)
4. Fetches paginated conversation history with token counting
5. Executes OpenAI Agent SDK with MCP tools
6. Persists user message and AI response in database
7. Returns formatted response to ChatKit UI with trace ID

## Quick Start: Request/Response Contract

### User starts new conversation
**Request:**
```json
{
  "message": "Add buy milk to my tasks",
  "idempotency_key": "550e8400-e29b-41d4-a716-446655440000"
}
```

**Response (201 Created):**
```json
{
  "conversation_id": "550e8400-e29b-41d4-a716-446655440001",
  "message_id": "550e8400-e29b-41d4-a716-446655440002",
  "response": "Task 'buy milk' created successfully. You now have 3 pending tasks.",
  "tool_calls": [{"tool": "add_task", "parameters": {"title": "buy milk"}, "status": "success"}],
  "execution_time_ms": 1250,
  "trace_id": "550e8400-e29b-41d4-a716-446655440003"
}
```

### User resumes conversation
**Request:**
```json
{
  "message": "What's my task summary?",
  "conversation_id": "550e8400-e29b-41d4-a716-446655440001",
  "idempotency_key": "550e8400-e29b-41d4-a716-446655440004"
}
```

**Response (200 OK):**
```json
{
  "conversation_id": "550e8400-e29b-41d4-a716-446655440001",
  "message_id": "550e8400-e29b-41d4-a716-446655440005",
  "response": "You have 3 tasks: 1 completed, 2 pending. By priority: 1 high, 1 medium, 1 low.",
  "tool_calls": [{"tool": "get_task_summary", "status": "success", "result": {...}}],
  "execution_time_ms": 850,
  "trace_id": "550e8400-e29b-41d4-a716-446655440006"
}
```

## Section 1: Pydantic Request/Response Models

Define strict validation models for type safety and automatic OpenAPI documentation. See `references/pydantic-models.md` for complete implementations.

### Key Models

**ChatRequest:**
```python
- message: str (required, 1-5000 chars)
- conversation_id: Optional[UUID] (resume existing, omit for new)
- idempotency_key: Optional[UUID] (auto-generated if omitted)
```

**ChatResponse:**
```python
- conversation_id: UUID
- message_id: UUID
- response: str (AI response text)
- tool_calls: List[ToolCallResponse]
- execution_time_ms: int
- trace_id: str (for debugging)
- timestamp: datetime
```

**ToolCallResponse:**
```python
- tool: str (name)
- parameters: dict (input)
- status: "success" | "partial" | "error" | "skipped"
- result: Optional[dict] (output if success)
- error: Optional[str] (message if failed)
- execution_time_ms: int
```

**ChatErrorResponse:**
```python
- error: str (error code: "UNAUTHORIZED", "INVALID_INPUT", etc.)
- message: str (user-friendly message)
- details: Optional[dict] (additional context)
- trace_id: str
- timestamp: datetime
```

## Section 2: Agent SDK Configuration

Configure OpenAI Agents SDK with MCP tools, system prompts, and timeout management. See `references/agent-sdk-config.md`.

### MCP Tools Routing
Map tools to agent:
- `add_task`: Create new task
- `list_tasks`: List tasks with filtering
- `complete_task`: Mark task complete
- `delete_task`: Delete task
- `update_task`: Modify task
- `get_task_summary`: Total, completed, pending, by_priority aggregation

### Agent Initialization
```
initialize_agent(user_id, user_preferences) → OpenAI client
- Injects system prompt with user language (EN/UR)
- Attaches MCP tools
- Sets timeout (30s agent, 10s per tool)
```

### Agent Execution with Retry
```
execute_agent(client, user_message, conversation_history, trace_id)
- Builds message array: system prompt + history + current message
- Executes agent with tool_choice="auto"
- Invokes each tool and captures results
- Retries on transient errors (exponential backoff: 100ms → 200ms → 400ms)
- Returns: {response, tool_calls, execution_time_ms, status}
```

## Section 3: JWT Authentication & Authorization

Validate JWT tokens, extract user_id, and prevent cross-user access.

### Authentication Middleware
```
get_current_user(Authorization: Bearer {token})
- Decode JWT with HS256 algorithm
- Extract user_id from token.sub
- Verify token not expired
- Return: {user_id, email, exp}
- Raise: 401 Unauthorized if invalid/expired
```

### Authorization Check
```
authorize_conversation_access(user_id, conversation_id, session)
- Query Conversation where id=conversation_id AND user_id=user_id
- Return: True if authorized
- Raise: 403 Forbidden if conversation not found or not owned by user
```

## Section 4: Idempotency & Trace ID

Detect duplicate requests and track requests for debugging.

### Idempotency Store (Redis)
```
check_idempotency(user_id, idempotency_key) → Optional[ChatResponse]
- Check Redis cache: idempotency:{user_id}:{key}
- Return cached response if exists
- TTL: 24 hours (prevent reuse across day boundaries)

store_idempotency(user_id, idempotency_key, response)
- Store response in Redis with 24hr TTL
- Used for duplicate detection on retry
```

### Trace ID Propagation
```
generate_trace_id() → str (UUID)
get_trace_id() → str (from context or generate new)

Middleware:
- Extract X-Trace-ID header or generate new
- Store in contextvars for log correlation
- Return in response header + response body
- Enables end-to-end request tracing
```

## Section 5: Transaction Management

Ensure atomic operations with automatic rollback on failures.

### Transaction Wrapper
```
execute_in_transaction(session, operation, *args, **kwargs)
- Try: Execute operation
- On IntegrityError: Rollback, raise 409 Conflict
- On SQLAlchemyError: Rollback, raise 500 Internal Server Error
- On Success: Commit, return result
```

### Rollback Scenarios
- Agent execution fails → rollback message storage
- Tool invocation fails → store error in Message, allow partial success
- Database constraint violated → rollback, return 409

## Section 6: Conversation History Pagination

Retrieve conversation history with pagination, token counting, and truncation for context window limits.

### History Retrieval
```
get_conversation_history(session, conversation_id, user_id, limit=50, offset=0)
- Verify user owns conversation (403 if not)
- Fetch messages ordered by created_at ASC (oldest first)
- Apply limit + offset for pagination
- Return: [{role, content, tool_calls, timestamp}, ...]
```

### Token Counting & Truncation
```
count_tokens(text) → int
- Use tiktoken.encoding_for_model("gpt-4")
- Count tokens per message

truncate_history_for_context(messages, max_tokens=8000)
- Calculate available: 8000 - 500 (reserve) = 7500 tokens
- If total_tokens > 7500:
  - Remove oldest messages until within limit
  - Keep newest messages to preserve conversation context
  - Log: "History truncated: 50 → 30 messages (7500 tokens, limit 7500)"
```

## Section 7: Complete Request Lifecycle

Wire all components together:

1. **Validate JWT** → Extract user_id (401 if invalid)
2. **Check Idempotency** → Return cached response if duplicate (200 OK)
3. **Authorize User** → Verify user_id in URL matches token (403 if mismatch)
4. **Create/Fetch Conversation** → Create new if conversation_id omitted, verify ownership (404/403 if not found/unauthorized)
5. **Fetch History** → Get paginated messages (limit: 50, offset: 0)
6. **Truncate for Tokens** → Fit within 8K token limit
7. **Store User Message** → Persist to Message table (transaction)
8. **Execute Agent** → Run Agent SDK, invoke tools, capture responses
9. **Store AI Response** → Persist to Message table with tool_calls (transaction commit)
10. **Build Response** → Format ChatResponse with trace_id
11. **Store Idempotency** → Cache for duplicate detection
12. **Return Response** → 200 OK with headers, or 201 Created if new conversation

### Error Handling Throughout
- Auth failures → 401/403
- Invalid input → 400
- Resource conflicts → 409
- Agent timeout → 504
- Database errors → 500 (rollback automatic)

## Implementation Flow Diagram

See `references/request-lifecycle.md` for detailed flow diagram with decision points, error paths, and database operations.

## Key Design Patterns

### Stateless Architecture
- No session state maintained on server
- All context retrieved from database each request
- Duplicate requests produce consistent results (idempotency)

### User Isolation (CRITICAL)
- ALL queries filter by user_id
- Verify user owns resource before access
- Return 403 Forbidden, never 404 (prevents user enumeration)

### Transaction Safety
- Message storage atomic (all-or-nothing)
- Rollback on agent failure
- No orphaned messages

### Error Recovery
- Retry agent execution (exponential backoff)
- Partial success allowed (some tools fail, others succeed)
- Tool errors stored in Message, returned to user

### Logging & Debugging
- Trace ID propagates through entire request
- Structured logging with user_id, conversation_id, trace_id
- Tool execution times tracked for performance analysis

---

## References

See bundled reference files for implementation details:
- **pydantic-models.md** - Complete Pydantic model definitions with validation rules
- **agent-sdk-config.md** - OpenAI Agents SDK configuration patterns and initialization
- **request-lifecycle.md** - Detailed flow diagram and database transaction sequences
