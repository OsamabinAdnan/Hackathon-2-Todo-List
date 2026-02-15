---
name: chat-flow-testing
description: "Create comprehensive test suites for FastAPI chat endpoints using httpx (direct HTTP client) with pytest, covering JWT authentication, idempotency, conversation lifecycle, message validation, error responses, trace IDs, tool verification, user isolation, and schema validation. Use when: (1) testing POST /api/{user_id}/chat endpoint with direct HTTP requests (not browser automation), (2) validating JWT token handling (valid, expired, missing, invalid tokens → 401 responses), (3) testing idempotency via duplicate request detection, (4) verifying conversation lifecycle (create new → 201, resume → 200, wrong user → 403), (5) testing message validation edge cases and constraints, (6) validating error responses (timeout → 504, tool failure → 500, rate limit → 429), (7) verifying trace ID propagation for debugging, (8) testing tool execution verification (tool_calls array, status, execution_time_ms), (9) enforcing multi-user isolation (user A cannot access user B's conversation), (10) validating response schema compliance, (11) testing multi-step conversation flows (add task → list → complete → summary)."
---

# Chat Flow Testing

## Core Responsibility

Test the stateless chat endpoint (POST /api/{user_id}/chat) end-to-end with direct HTTP requests using httpx + pytest. Verify:

1. **Authentication**: JWT tokens (valid, expired, missing, invalid → 401)
2. **Authorization**: User isolation, conversation ownership (wrong user → 403)
3. **Conversation Lifecycle**: Create new (201), resume existing (200), stale detection
4. **Request Validation**: Message length, type, format edge cases
5. **Response Format**: ChatResponse schema, trace ID, execution metadata
6. **Tool Execution**: Tool calls array, status, execution times
7. **Error Handling**: Timeout (504), tool failure (500), rate limit (429), validation errors (400)
8. **Idempotency**: Duplicate requests with same idempotency_key return cached response
9. **Multi-Step Flows**: Sequential operations maintaining context through conversation history

## Quick Start: Test Structure

```python
# Use httpx async client for direct HTTP testing
import httpx
import pytest

@pytest.mark.asyncio
async def test_chat_new_conversation_with_jwt():
    """User sends message to start new conversation → 201 Created"""
    async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
        response = await client.post(
            "/api/{user_id}/chat",
            headers={"Authorization": f"Bearer {valid_jwt_token}"},
            json={"message": "Add buy milk to my tasks"}
        )

        assert response.status_code == 201
        data = response.json()
        assert "conversation_id" in data
        assert "message_id" in data
        assert "response" in data
        assert "trace_id" in data
```

## Section 1: JWT Authentication Tests

Test all JWT validation scenarios with direct HTTP requests.

### Valid Token - Success (200/201)
```python
@pytest.mark.asyncio
async def test_chat_valid_jwt_creates_conversation():
    """Valid JWT token allows message and creates conversation → 201"""
    async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
        response = await client.post(
            "/api/test-user-123/chat",
            headers={"Authorization": f"Bearer {generate_valid_jwt('test-user-123')}"},
            json={"message": "Hello"}
        )

        assert response.status_code == 201
        data = response.json()
        assert data["conversation_id"]
        assert data["message_id"]
```

### Missing Token - 401 Unauthorized
```python
@pytest.mark.asyncio
async def test_chat_missing_jwt_returns_401():
    """Missing Authorization header → 401 Unauthorized"""
    async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
        response = await client.post(
            "/api/test-user-123/chat",
            json={"message": "Hello"}
        )

        assert response.status_code == 401
        data = response.json()
        assert data["error"] == "UNAUTHORIZED"
        assert "trace_id" in data
```

### Expired Token - 401 Unauthorized
```python
@pytest.mark.asyncio
async def test_chat_expired_jwt_returns_401():
    """Expired JWT (exp time in past) → 401 Unauthorized"""
    expired_token = generate_jwt_with_expiry("test-user-123", past_timestamp())

    async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
        response = await client.post(
            "/api/test-user-123/chat",
            headers={"Authorization": f"Bearer {expired_token}"},
            json={"message": "Hello"}
        )

        assert response.status_code == 401
        data = response.json()
        assert data["error"] == "UNAUTHORIZED"
```

### Invalid Token - 401 Unauthorized
```python
@pytest.mark.asyncio
async def test_chat_invalid_jwt_signature_returns_401():
    """Invalid JWT signature → 401 Unauthorized"""
    invalid_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.invalid.signature"

    async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
        response = await client.post(
            "/api/test-user-123/chat",
            headers={"Authorization": f"Bearer {invalid_token}"},
            json={"message": "Hello"}
        )

        assert response.status_code == 401
        data = response.json()
        assert data["error"] == "UNAUTHORIZED"
```

### Invalid Bearer Format - 401
```python
@pytest.mark.asyncio
async def test_chat_invalid_bearer_format_returns_401():
    """Malformed Authorization header (e.g., 'Token X' instead of 'Bearer X') → 401"""
    async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
        response = await client.post(
            "/api/test-user-123/chat",
            headers={"Authorization": f"Token {generate_valid_jwt('test-user-123')}"},
            json={"message": "Hello"}
        )

        assert response.status_code == 401
        data = response.json()
        assert data["error"] == "UNAUTHORIZED"
```

## Section 2: Authorization & User Isolation Tests

Test user isolation - users cannot access other users' conversations.

### User A Accessing Own Conversation - 200/201
```python
@pytest.mark.asyncio
async def test_chat_user_accesses_own_conversation():
    """User A accessing own conversation → 200 OK"""
    user_a_token = generate_valid_jwt("user-a")

    # User A creates conversation
    async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
        response = await client.post(
            "/api/user-a/chat",
            headers={"Authorization": f"Bearer {user_a_token}"},
            json={"message": "First message"}
        )
        assert response.status_code == 201
        conversation_id = response.json()["conversation_id"]

    # User A resumes own conversation → 200
    async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
        response = await client.post(
            "/api/user-a/chat",
            headers={"Authorization": f"Bearer {user_a_token}"},
            json={
                "message": "Second message",
                "conversation_id": conversation_id
            }
        )
        assert response.status_code == 200
```

### User B Accessing User A's Conversation - 403 Forbidden
```python
@pytest.mark.asyncio
async def test_chat_user_b_cannot_access_user_a_conversation():
    """User B accessing User A's conversation → 403 Forbidden"""
    user_a_token = generate_valid_jwt("user-a")
    user_b_token = generate_valid_jwt("user-b")

    # User A creates conversation
    async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
        response = await client.post(
            "/api/user-a/chat",
            headers={"Authorization": f"Bearer {user_a_token}"},
            json={"message": "Private message"}
        )
        conversation_id = response.json()["conversation_id"]

    # User B tries to resume User A's conversation → 403
    async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
        response = await client.post(
            "/api/user-a/chat",  # Still using user-a in URL
            headers={"Authorization": f"Bearer {user_b_token}"},  # But user-b's token
            json={
                "message": "Trying to hijack",
                "conversation_id": conversation_id
            }
        )
        assert response.status_code == 403
        data = response.json()
        assert data["error"] == "ACCESS_DENIED"
```

### Token User ID Mismatch URL - 403 Forbidden
```python
@pytest.mark.asyncio
async def test_chat_token_user_id_must_match_url_user_id():
    """Token user_id must match URL user_id → 403"""
    user_a_token = generate_valid_jwt("user-a")

    # Token says "user-a" but URL says "user-b"
    async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
        response = await client.post(
            "/api/user-b/chat",
            headers={"Authorization": f"Bearer {user_a_token}"},
            json={"message": "Mismatch attempt"}
        )

        assert response.status_code == 403
        data = response.json()
        assert data["error"] == "ACCESS_DENIED"
```

## Section 3: Conversation Lifecycle Tests

Test conversation creation, resumption, and stale detection.

### Create New Conversation (No conversation_id) - 201
```python
@pytest.mark.asyncio
async def test_chat_create_new_conversation_returns_201():
    """Omitting conversation_id creates new conversation → 201 Created"""
    token = generate_valid_jwt("test-user")

    async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
        response = await client.post(
            "/api/test-user/chat",
            headers={"Authorization": f"Bearer {token}"},
            json={"message": "Start new"}
        )

        assert response.status_code == 201
        data = response.json()
        assert "conversation_id" in data
        assert data["conversation_id"]  # Not empty
```

### Resume Existing Conversation - 200
```python
@pytest.mark.asyncio
async def test_chat_resume_conversation_returns_200():
    """Providing conversation_id resumes existing → 200 OK"""
    token = generate_valid_jwt("test-user")

    # Create first
    async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
        response = await client.post(
            "/api/test-user/chat",
            headers={"Authorization": f"Bearer {token}"},
            json={"message": "First"}
        )
        conversation_id = response.json()["conversation_id"]

    # Resume second
    async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
        response = await client.post(
            "/api/test-user/chat",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "message": "Second",
                "conversation_id": conversation_id
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert data["conversation_id"] == conversation_id
```

### Non-Existent Conversation - 403 (Not 404 - Prevent Enumeration)
```python
@pytest.mark.asyncio
async def test_chat_nonexistent_conversation_returns_403():
    """Non-existent conversation_id → 403 (prevent enumeration)"""
    token = generate_valid_jwt("test-user")
    fake_conversation_id = "00000000-0000-0000-0000-000000000000"

    async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
        response = await client.post(
            "/api/test-user/chat",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "message": "To fake conversation",
                "conversation_id": fake_conversation_id
            }
        )

        assert response.status_code == 403
```

## Section 4: Message Validation Tests

Test message format, length, and edge cases.

### Valid Message - 200/201
```python
@pytest.mark.asyncio
async def test_chat_valid_message_formats():
    """Valid messages (1-5000 chars, various formats) → 200/201"""
    token = generate_valid_jwt("test-user")

    test_cases = [
        {"message": "Add task"},  # Short
        {"message": "a" * 5000},  # Max length
        {"message": "Add task with 'quotes' and \"double quotes\""},  # Special chars
        {"message": "Add task\nwith\nnewlines"},  # Newlines
        {"message": "Add task with émojis 🎉"},  # Unicode
    ]

    for case in test_cases:
        async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
            response = await client.post(
                "/api/test-user/chat",
                headers={"Authorization": f"Bearer {token}"},
                json=case
            )

            assert response.status_code in [200, 201]
```

### Empty Message - 400 Bad Request
```python
@pytest.mark.asyncio
async def test_chat_empty_message_returns_400():
    """Empty message → 400 Bad Request"""
    token = generate_valid_jwt("test-user")

    async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
        response = await client.post(
            "/api/test-user/chat",
            headers={"Authorization": f"Bearer {token}"},
            json={"message": ""}
        )

        assert response.status_code == 400
        data = response.json()
        assert data["error"] == "INVALID_INPUT"
```

### Message Too Long (>5000 chars) - 400
```python
@pytest.mark.asyncio
async def test_chat_message_too_long_returns_400():
    """Message > 5000 chars → 400 Bad Request"""
    token = generate_valid_jwt("test-user")

    async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
        response = await client.post(
            "/api/test-user/chat",
            headers={"Authorization": f"Bearer {token}"},
            json={"message": "x" * 5001}
        )

        assert response.status_code == 400
        data = response.json()
        assert data["error"] == "INVALID_INPUT"
```

### Invalid conversation_id Format - 400
```python
@pytest.mark.asyncio
async def test_chat_invalid_conversation_id_format_returns_400():
    """Invalid UUID format for conversation_id → 400"""
    token = generate_valid_jwt("test-user")

    async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
        response = await client.post(
            "/api/test-user/chat",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "message": "Test",
                "conversation_id": "not-a-uuid"
            }
        )

        assert response.status_code == 400
```

### Missing Required Field - 400
```python
@pytest.mark.asyncio
async def test_chat_missing_message_field_returns_400():
    """Missing 'message' field → 400"""
    token = generate_valid_jwt("test-user")

    async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
        response = await client.post(
            "/api/test-user/chat",
            headers={"Authorization": f"Bearer {token}"},
            json={}  # Missing 'message'
        )

        assert response.status_code == 400
```

## Section 5: Idempotency Tests

Test duplicate request detection via idempotency_key.

### Duplicate Request Returns Cached Response
```python
@pytest.mark.asyncio
async def test_chat_idempotency_duplicate_request():
    """Duplicate request with same idempotency_key → same response"""
    token = generate_valid_jwt("test-user")
    idempotency_key = "550e8400-e29b-41d4-a716-446655440000"

    # First request
    async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
        response1 = await client.post(
            "/api/test-user/chat",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "message": "Add milk",
                "idempotency_key": idempotency_key
            }
        )
        data1 = response1.json()
        message_id_1 = data1["message_id"]

    # Duplicate request (same idempotency_key)
    async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
        response2 = await client.post(
            "/api/test-user/chat",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "message": "Add milk",
                "idempotency_key": idempotency_key
            }
        )
        data2 = response2.json()
        message_id_2 = data2["message_id"]

    # Same response
    assert data1["response"] == data2["response"]
    assert message_id_1 == message_id_2
```

### Different Idempotency Key Creates New Message
```python
@pytest.mark.asyncio
async def test_chat_different_idempotency_key_creates_new_message():
    """Different idempotency_key → new message created"""
    token = generate_valid_jwt("test-user")

    async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
        response1 = await client.post(
            "/api/test-user/chat",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "message": "Add milk",
                "idempotency_key": "key1"
            }
        )
        message_id_1 = response1.json()["message_id"]

    async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
        response2 = await client.post(
            "/api/test-user/chat",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "message": "Add milk",
                "idempotency_key": "key2"
            }
        )
        message_id_2 = response2.json()["message_id"]

    # Different messages
    assert message_id_1 != message_id_2
```

## Section 6: Response Format & Trace ID Tests

Verify ChatResponse schema and trace ID propagation.

### Response Contains All Required Fields
```python
@pytest.mark.asyncio
async def test_chat_response_schema_completeness():
    """Response contains all required fields"""
    token = generate_valid_jwt("test-user")

    async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
        response = await client.post(
            "/api/test-user/chat",
            headers={"Authorization": f"Bearer {token}"},
            json={"message": "Hello"}
        )

        data = response.json()

        # Required fields
        assert "conversation_id" in data
        assert "message_id" in data
        assert "response" in data
        assert "trace_id" in data
        assert "execution_time_ms" in data
        assert "timestamp" in data
        assert "tool_calls" in data

        # Field types
        assert isinstance(data["conversation_id"], str)
        assert isinstance(data["message_id"], str)
        assert isinstance(data["response"], str)
        assert isinstance(data["trace_id"], str)
        assert isinstance(data["execution_time_ms"], int)
        assert isinstance(data["tool_calls"], list)
```

### Trace ID Format
```python
@pytest.mark.asyncio
async def test_chat_trace_id_format():
    """Trace ID is valid UUID format"""
    token = generate_valid_jwt("test-user")

    async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
        response = await client.post(
            "/api/test-user/chat",
            headers={"Authorization": f"Bearer {token}"},
            json={"message": "Test"}
        )

        trace_id = response.json()["trace_id"]

        # Valid UUID format
        import uuid
        uuid.UUID(trace_id)  # Should not raise
```

### Trace ID in Response Headers
```python
@pytest.mark.asyncio
async def test_chat_trace_id_in_response_headers():
    """Trace ID included in X-Trace-ID response header"""
    token = generate_valid_jwt("test-user")

    async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
        response = await client.post(
            "/api/test-user/chat",
            headers={"Authorization": f"Bearer {token}"},
            json={"message": "Test"}
        )

        assert "x-trace-id" in response.headers
        assert response.headers["x-trace-id"]
```

## Section 7: Tool Execution Verification

Verify tool_calls array, status, and execution metadata.

### Tool Calls Array Structure
```python
@pytest.mark.asyncio
async def test_chat_tool_calls_structure():
    """Tool calls array has correct structure"""
    token = generate_valid_jwt("test-user")

    async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
        response = await client.post(
            "/api/test-user/chat",
            headers={"Authorization": f"Bearer {token}"},
            json={"message": "Add buy milk"}
        )

        tool_calls = response.json()["tool_calls"]

        # Should have at least one tool call for "add task"
        assert len(tool_calls) >= 1

        for tool_call in tool_calls:
            assert "tool" in tool_call
            assert "status" in tool_call
            assert tool_call["status"] in ["success", "partial", "error", "skipped"]
            assert "execution_time_ms" in tool_call

            # Optional fields
            if tool_call["status"] == "success":
                assert "result" in tool_call
            elif tool_call["status"] == "error":
                assert "error" in tool_call
```

### Tool Execution Times
```python
@pytest.mark.asyncio
async def test_chat_tool_execution_times_measured():
    """Tool execution times are measured and included"""
    token = generate_valid_jwt("test-user")

    async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
        response = await client.post(
            "/api/test-user/chat",
            headers={"Authorization": f"Bearer {token}"},
            json={"message": "Add task and show summary"}
        )

        tool_calls = response.json()["tool_calls"]

        for tool_call in tool_calls:
            assert tool_call["execution_time_ms"] >= 0
            assert isinstance(tool_call["execution_time_ms"], int)
```

## Section 8: Error Response Tests

Test error handling for timeouts, tool failures, rate limits.

### Agent Timeout (>30s) - 504 Gateway Timeout
```python
@pytest.mark.asyncio
async def test_chat_agent_timeout_returns_504():
    """Agent execution timeout (>30s) → 504 Gateway Timeout"""
    token = generate_valid_jwt("test-user")

    async with httpx.AsyncClient(base_url="http://localhost:8000", timeout=60) as client:
        # Message that causes timeout (simulated)
        response = await client.post(
            "/api/test-user/chat",
            headers={"Authorization": f"Bearer {token}"},
            json={"message": "TIMEOUT_TRIGGER"}  # Simulated timeout
        )

        assert response.status_code == 504
        data = response.json()
        assert data["error"] == "TIMEOUT"
        assert "trace_id" in data
```

### Tool Execution Failure - 500 Internal Server Error
```python
@pytest.mark.asyncio
async def test_chat_tool_failure_returns_500():
    """Tool execution fails → 500 Internal Server Error"""
    token = generate_valid_jwt("test-user")

    async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
        # Message that causes tool error (simulated)
        response = await client.post(
            "/api/test-user/chat",
            headers={"Authorization": f"Bearer {token}"},
            json={"message": "TOOL_ERROR_TRIGGER"}
        )

        assert response.status_code == 500
        data = response.json()
        assert data["error"] == "INTERNAL_SERVER_ERROR"
```

### Rate Limit Exceeded - 429 Too Many Requests
```python
@pytest.mark.asyncio
async def test_chat_rate_limit_returns_429():
    """Too many requests → 429 Too Many Requests"""
    token = generate_valid_jwt("test-user")

    # Send multiple rapid requests
    async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
        for i in range(100):  # Exceed rate limit
            response = await client.post(
                "/api/test-user/chat",
                headers={"Authorization": f"Bearer {token}"},
                json={"message": f"Message {i}"}
            )

            if response.status_code == 429:
                data = response.json()
                assert "retry_after" in data
                assert isinstance(data["retry_after"], int)
                break
```

## Section 9: Multi-Step Conversation Flows

Test complex multi-message conversations.

### Add Task → List Tasks → Complete Task Flow
```python
@pytest.mark.asyncio
async def test_chat_multi_step_add_list_complete_flow():
    """Complete multi-step flow: add → list → complete"""
    token = generate_valid_jwt("test-user")
    conversation_id = None

    # Step 1: Add task
    async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
        response = await client.post(
            "/api/test-user/chat",
            headers={"Authorization": f"Bearer {token}"},
            json={"message": "Add buy milk"}
        )
        assert response.status_code in [200, 201]
        conversation_id = response.json()["conversation_id"]
        assert "add_task" in [tc["tool"] for tc in response.json()["tool_calls"]]

    # Step 2: List tasks
    async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
        response = await client.post(
            "/api/test-user/chat",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "message": "Show my tasks",
                "conversation_id": conversation_id
            }
        )
        assert response.status_code == 200
        assert "list_tasks" in [tc["tool"] for tc in response.json()["tool_calls"]]

    # Step 3: Complete task
    async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
        response = await client.post(
            "/api/test-user/chat",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "message": "Mark milk as done",
                "conversation_id": conversation_id
            }
        )
        assert response.status_code == 200
        assert "complete_task" in [tc["tool"] for tc in response.json()["tool_calls"]]
```

### Conversation History Preserved
```python
@pytest.mark.asyncio
async def test_chat_conversation_history_preserved_across_messages():
    """Conversation history maintained across messages"""
    token = generate_valid_jwt("test-user")

    # Message 1
    async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
        response = await client.post(
            "/api/test-user/chat",
            headers={"Authorization": f"Bearer {token}"},
            json={"message": "Add task 1"}
        )
        conversation_id = response.json()["conversation_id"]

    # Message 2 - should reference previous context
    async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
        response = await client.post(
            "/api/test-user/chat",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "message": "How many tasks do I have?",
                "conversation_id": conversation_id
            }
        )
        assert response.status_code == 200
        # Response should reference the task added in message 1
        response_text = response.json()["response"]
        assert "1" in response_text or "one" in response_text.lower()
```

## Section 10: Status Code Summary

| Scenario | Status Code | Error Code |
|----------|------------|-----------|
| Valid message, new conversation | 201 | N/A |
| Valid message, existing conversation | 200 | N/A |
| Missing JWT | 401 | UNAUTHORIZED |
| Expired JWT | 401 | UNAUTHORIZED |
| Wrong user accessing conversation | 403 | ACCESS_DENIED |
| Empty message | 400 | INVALID_INPUT |
| Message too long | 400 | INVALID_INPUT |
| Invalid UUID format | 400 | INVALID_INPUT |
| Agent timeout (>30s) | 504 | TIMEOUT |
| Tool execution failed | 500 | INTERNAL_SERVER_ERROR |
| Rate limit exceeded | 429 | TOO_MANY_REQUESTS |

---

## Testing Checklist

Use this checklist to validate complete chat endpoint test coverage:

- [ ] JWT validation (valid, expired, missing, invalid signature, malformed format)
- [ ] User isolation (user A cannot access user B's conversation)
- [ ] Token/URL user_id mismatch detection
- [ ] Conversation lifecycle (create 201, resume 200, non-existent 403)
- [ ] Message validation (empty, too long, edge cases, special chars)
- [ ] Idempotency (duplicate requests, different keys)
- [ ] Response schema (all required fields, types, trace ID)
- [ ] Tool execution (tool_calls array, status, execution_time_ms)
- [ ] Error responses (timeout 504, tool failure 500, rate limit 429)
- [ ] Multi-step flows (add → list → complete sequence)
- [ ] Conversation history preservation
- [ ] Trace ID propagation (body + headers)

---

## Quick Reference: Dummy Test Queries

Use these queries to manually test chat endpoint:

```python
# Add task
{"message": "Add buy milk"}

# List tasks
{"message": "Show my tasks"}

# Complete task
{"message": "Mark milk as done"}

# Get summary
{"message": "What's my task summary?"}

# Complex multi-step
{"message": "Add task1, then add task2, then show all"}

# Multilingual (Urdu)
{"message": "مجھے اپنا کام دکھائیں"}  # Show my tasks
```
