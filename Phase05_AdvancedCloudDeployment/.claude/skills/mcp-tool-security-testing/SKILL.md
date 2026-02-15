# MCP Tool Security & Integration Testing Skill

## Overview

This skill creates comprehensive pytest test suites for MCP tools, ensuring security isolation, proper agent integration, error handling, and TDD compliance. Tests cover authentication, authorization, tool composition, conversation context, and concurrent operations with 100% coverage for security-critical paths.

**Skill Type:** Test-Driven Development (Red Phase)
**Phase:** Phase 3 (AI Chatbot Integration)
**Agent:** mcp-server-builder
**Testing Framework:** pytest, pytest-asyncio, unittest.mock
**Dependencies:** @specs/testing/backend-testing.md, Official MCP SDK

---

## When to Use This Skill

Use this skill when you need to:

1. **Generate failing test suites** for each MCP tool (Red phase of TDD)
2. **Create mock AI agent behavior** that simulates OpenAI Agents SDK tool invocation
3. **Test user authentication & JWT extraction** from headers/claims
4. **Verify cross-user access prevention** (critical security requirement)
5. **Test tool composition scenarios** (list_tasks followed by delete_task)
6. **Verify conversation history context** availability to agent
7. **Test error handling paths** (task_not_found, invalid_parameter, unauthorized)
8. **Simulate concurrent operations** (multiple users simultaneously)
9. **Verify task summary generation** (totals, priorities, completion counts)
10. **Test rate limiting enforcement** (429 responses)
11. **Validate response format** against MCP protocol specification

---

## Core Testing Capabilities

### 1. TDD Red Phase: Failing Tests

Generate tests that FAIL before implementation, defining expected behavior:

```python
# Example: Failing test for add_task
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

@pytest.fixture
def authenticated_user_headers():
    """JWT token for authenticated user"""
    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def other_user_headers():
    """JWT token for different user"""
    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
    return {"Authorization": f"Bearer {token}"}

# RED: This test should FAIL before implementation
def test_add_task_creates_task(authenticated_user_headers):
    """Test that add_task creates a task with valid parameters"""
    response = client.post(
        "/api/550e8400-e29b-41d4-a716-446655440000/tasks",
        json={
            "title": "Buy groceries",
            "description": "Milk, eggs, bread"
        },
        headers=authenticated_user_headers
    )

    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "created"
    assert data["title"] == "Buy groceries"
    assert "task_id" in data
    assert "created_at" in data
    # This test FAILS before add_task is implemented
```

### 2. Authentication & JWT Testing

Test JWT token extraction and validation:

```python
def test_add_task_requires_authentication(no_auth_headers):
    """Test that add_task requires valid JWT token"""
    response = client.post(
        "/api/550e8400-e29b-41d4-a716-446655440000/tasks",
        json={"title": "Test"},
        headers={}  # No auth header
    )

    assert response.status_code == 401
    data = response.json()
    assert data["error"] == "authentication_required"

def test_add_task_rejects_expired_token(expired_token_headers):
    """Test that expired JWT token is rejected"""
    response = client.post(
        "/api/550e8400-e29b-41d4-a716-446655440000/tasks",
        json={"title": "Test"},
        headers=expired_token_headers
    )

    assert response.status_code == 401
    data = response.json()
    assert data["error"] == "authentication_required"

def test_add_task_validates_user_id_from_jwt(authenticated_user_headers):
    """Test that user_id is correctly extracted from JWT claims"""
    # Token claims: {"sub": "550e8400-e29b-41d4-a716-446655440000", ...}
    response = client.post(
        "/api/550e8400-e29b-41d4-a716-446655440000/tasks",
        json={"title": "Test"},
        headers=authenticated_user_headers
    )

    # Should succeed because user_id in URL matches JWT claim
    assert response.status_code == 201

def test_add_task_rejects_mismatched_user_id(authenticated_user_headers):
    """Test that mismatched user_id is rejected (403 Forbidden)"""
    response = client.post(
        "/api/99999999-9999-9999-9999-999999999999/tasks",  # Different user
        json={"title": "Test"},
        headers=authenticated_user_headers
    )

    # Should fail because URL user_id != JWT claim user_id
    assert response.status_code == 403
    data = response.json()
    assert data["error"] == "unauthorized_access"
```

### 3. Cross-User Access Prevention (CRITICAL SECURITY)

Test that users cannot access other users' tasks:

```python
def test_list_tasks_prevents_cross_user_access(authenticated_user_headers, other_user_headers):
    """Test that user cannot list tasks of another user"""
    # User A creates a task
    response = client.post(
        "/api/550e8400-e29b-41d4-a716-446655440000/tasks",
        json={"title": "User A's task"},
        headers=authenticated_user_headers
    )
    assert response.status_code == 201

    # User B tries to list User A's tasks
    response = client.get(
        "/api/550e8400-e29b-41d4-a716-446655440000/tasks",
        headers=other_user_headers
    )

    # Should be forbidden or return only User B's tasks
    assert response.status_code == 403

def test_delete_task_prevents_cross_user_deletion(authenticated_user_headers, other_user_headers, task_id):
    """Test that user cannot delete another user's task"""
    response = client.delete(
        f"/api/99999999-9999-9999-9999-999999999999/tasks/{task_id}",
        headers=other_user_headers
    )

    assert response.status_code == 403
    data = response.json()
    assert data["error"] == "unauthorized_access"

def test_update_task_prevents_cross_user_modification(authenticated_user_headers, other_user_headers, task_id):
    """Test that user cannot update another user's task"""
    response = client.put(
        f"/api/99999999-9999-9999-9999-999999999999/tasks/{task_id}",
        json={"title": "Modified by attacker"},
        headers=other_user_headers
    )

    assert response.status_code == 403
    data = response.json()
    assert data["error"] == "unauthorized_access"

def test_complete_task_prevents_cross_user_completion(other_user_headers, other_user_task_id):
    """Test that user cannot complete another user's task"""
    response = client.patch(
        f"/api/550e8400-e29b-41d4-a716-446655440000/tasks/{other_user_task_id}/complete",
        headers=other_user_headers
    )

    assert response.status_code == 403
```

### 4. Parameter Validation Testing

Test that parameters are validated correctly:

```python
def test_add_task_requires_title(authenticated_user_headers):
    """Test that title parameter is required"""
    response = client.post(
        "/api/550e8400-e29b-41d4-a716-446655440000/tasks",
        json={"description": "No title provided"},
        headers=authenticated_user_headers
    )

    assert response.status_code == 400
    data = response.json()
    assert data["error"] == "invalid_parameter"
    assert "title" in data["details"]

def test_add_task_rejects_empty_title(authenticated_user_headers):
    """Test that empty title is rejected"""
    response = client.post(
        "/api/550e8400-e29b-41d4-a716-446655440000/tasks",
        json={"title": ""},
        headers=authenticated_user_headers
    )

    assert response.status_code == 400
    data = response.json()
    assert data["error"] == "invalid_parameter"

def test_add_task_rejects_oversized_title(authenticated_user_headers):
    """Test that title exceeding 200 chars is rejected"""
    long_title = "x" * 201
    response = client.post(
        "/api/550e8400-e29b-41d4-a716-446655440000/tasks",
        json={"title": long_title},
        headers=authenticated_user_headers
    )

    assert response.status_code == 400
    data = response.json()
    assert data["error"] == "invalid_parameter"

def test_list_tasks_validates_status_enum(authenticated_user_headers):
    """Test that status parameter accepts only valid values"""
    # Valid values
    for status in ["all", "pending", "completed"]:
        response = client.get(
            f"/api/550e8400-e29b-41d4-a716-446655440000/tasks?status={status}",
            headers=authenticated_user_headers
        )
        assert response.status_code == 200

    # Invalid value
    response = client.get(
        "/api/550e8400-e29b-41d4-a716-446655440000/tasks?status=invalid",
        headers=authenticated_user_headers
    )

    assert response.status_code == 400
    data = response.json()
    assert data["error"] == "invalid_parameter"
```

### 5. Error Handling Testing

Test standardized error responses:

```python
def test_list_tasks_handles_task_not_found(authenticated_user_headers):
    """Test that 404 is returned for non-existent task"""
    response = client.get(
        "/api/550e8400-e29b-41d4-a716-446655440000/tasks/99999999-9999-9999-9999-999999999999",
        headers=authenticated_user_headers
    )

    assert response.status_code == 404
    data = response.json()
    assert data["error"] == "task_not_found"
    assert "task_id" in data["details"]

def test_complete_task_returns_invalid_state_if_already_completed(authenticated_user_headers, completed_task_id):
    """Test that completing an already-completed task returns error"""
    response = client.patch(
        f"/api/550e8400-e29b-41d4-a716-446655440000/tasks/{completed_task_id}/complete",
        headers=authenticated_user_headers
    )

    assert response.status_code == 422
    data = response.json()
    assert data["error"] == "invalid_state"
    assert "already completed" in data["message"].lower()

def test_database_error_returns_500(authenticated_user_headers, mock_db_failure):
    """Test that database errors return 500 with retry hint"""
    with mock_db_failure:
        response = client.post(
            "/api/550e8400-e29b-41d4-a716-446655440000/tasks",
            json={"title": "Test"},
            headers=authenticated_user_headers
        )

    assert response.status_code == 500
    data = response.json()
    assert data["error"] == "database_error"
    assert "retry" in data["message"].lower()
```

### 6. Tool Composition Testing

Test that tools can be combined in agent workflows:

```python
def test_find_task_by_title_composition(authenticated_user_headers):
    """Test agent pattern: list_tasks -> find by title -> update_task"""
    # Step 1: Create a task
    create_response = client.post(
        "/api/550e8400-e29b-41d4-a716-446655440000/tasks",
        json={"title": "Original Title"},
        headers=authenticated_user_headers
    )
    task_id = create_response.json()["task_id"]

    # Step 2: List tasks to verify creation
    list_response = client.get(
        "/api/550e8400-e29b-41d4-a716-446655440000/tasks?status=all",
        headers=authenticated_user_headers
    )
    tasks = list_response.json()["tasks"]
    assert len(tasks) >= 1
    assert any(t["title"] == "Original Title" for t in tasks)

    # Step 3: Agent would find task and update it
    found_task = next(t for t in tasks if t["title"] == "Original Title")
    update_response = client.put(
        f"/api/550e8400-e29b-41d4-a716-446655440000/tasks/{found_task['task_id']}",
        json={"title": "Updated Title"},
        headers=authenticated_user_headers
    )

    assert update_response.status_code == 200
    assert update_response.json()["title"] == "Updated Title"

def test_list_and_delete_composition(authenticated_user_headers):
    """Test agent pattern: list_tasks -> find by name -> delete_task"""
    # Create and list, then delete
    task_id = "test-id"
    delete_response = client.delete(
        f"/api/550e8400-e29b-41d4-a716-446655440000/tasks/{task_id}",
        headers=authenticated_user_headers
    )

    assert delete_response.status_code == 200
    data = delete_response.json()
    assert data["status"] == "deleted"
```

### 7. Mock AI Agent Integration Testing

Test tools with mock OpenAI Agents SDK behavior:

```python
@pytest.fixture
def mock_openai_agent():
    """Mock agent that simulates OpenAI Agents SDK tool invocation"""
    from unittest.mock import MagicMock, AsyncMock

    agent = MagicMock()
    agent.invoke = AsyncMock()

    async def simulated_tool_call(tool_name, parameters):
        """Simulate agent calling an MCP tool"""
        if tool_name == "add_task":
            # Simulate agent extracting and calling add_task
            return {
                "task_id": "6ba7b810-9dad-11d1-80b4-00c04fd430c8",
                "status": "created",
                "title": parameters["title"]
            }
        elif tool_name == "list_tasks":
            return {"tasks": [], "pagination": {"total": 0}}

    agent.invoke = simulated_tool_call
    return agent

@pytest.mark.asyncio
async def test_agent_can_call_add_task_tool(mock_openai_agent):
    """Test that agent can successfully invoke add_task tool"""
    result = await mock_openai_agent.invoke(
        "add_task",
        {
            "user_id": "550e8400-e29b-41d4-a716-446655440000",
            "title": "Buy groceries"
        }
    )

    assert result["status"] == "created"
    assert result["title"] == "Buy groceries"

@pytest.mark.asyncio
async def test_agent_receives_proper_error_when_tool_fails(mock_openai_agent):
    """Test that agent receives standardized error response from tool"""
    # Mock tool returning error
    mock_openai_agent.invoke.side_effect = Exception(
        json.dumps({
            "error": "invalid_parameter",
            "message": "Title is required"
        })
    )

    with pytest.raises(Exception) as exc_info:
        await mock_openai_agent.invoke("add_task", {"user_id": "xyz"})

    error_data = json.loads(str(exc_info.value))
    assert error_data["error"] == "invalid_parameter"
```

### 8. Conversation Context Testing

Test that tools provide context for multi-turn conversations:

```python
def test_conversation_context_available_to_tool(authenticated_user_headers, conversation_id):
    """Test that conversation history is available when invoking tools"""
    # This test verifies that tools can access conversation context
    # for providing better responses

    response = client.post(
        f"/api/550e8400-e29b-41d4-a716-446655440000/chat",
        json={
            "conversation_id": conversation_id,
            "message": "List my tasks"
        },
        headers=authenticated_user_headers
    )

    assert response.status_code == 200
    data = response.json()

    # Tool should have had access to conversation history
    assert "tool_calls" in data
    assert len(data["tool_calls"]) > 0
    assert data["tool_calls"][0]["tool"] == "list_tasks"

def test_tool_can_reference_previous_context(authenticated_user_headers, conversation_with_history):
    """Test that agent can use previous messages for context"""
    # Previous message: "Create a task called Buy milk"
    # Current message: "Mark it complete"
    # Agent should remember previous task and complete it

    response = client.post(
        f"/api/550e8400-e29b-41d4-a716-446655440000/chat",
        json={
            "conversation_id": conversation_with_history,
            "message": "Mark it complete"
        },
        headers=authenticated_user_headers
    )

    assert response.status_code == 200
    data = response.json()
    assert "complete_task" in [tc["tool"] for tc in data["tool_calls"]]
```

### 9. Concurrent Operations Testing

Test that multiple users can use tools simultaneously:

```python
def test_concurrent_add_task_operations(authenticated_user_headers, other_user_headers):
    """Test that concurrent add_task calls work correctly"""
    import concurrent.futures

    def create_task(headers, title):
        return client.post(
            "/api/550e8400-e29b-41d4-a716-446655440000/tasks",
            json={"title": title},
            headers=headers
        )

    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        future_1 = executor.submit(create_task, authenticated_user_headers, "Task 1")
        future_2 = executor.submit(create_task, other_user_headers, "Task 2")

        response_1 = future_1.result()
        response_2 = future_2.result()

    # Both should succeed
    assert response_1.status_code == 201
    assert response_2.status_code == 201

    # But their tasks should be separate
    assert response_1.json()["task_id"] != response_2.json()["task_id"]

def test_concurrent_list_prevents_data_mixing(authenticated_user_headers, other_user_headers):
    """Test that concurrent list operations don't mix user data"""
    import concurrent.futures

    def list_tasks(headers):
        response = client.get(
            "/api/550e8400-e29b-41d4-a716-446655440000/tasks",
            headers=headers
        )
        return response.json()["tasks"]

    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        future_1 = executor.submit(list_tasks, authenticated_user_headers)
        future_2 = executor.submit(list_tasks, other_user_headers)

        tasks_1 = future_1.result()
        tasks_2 = future_2.result()

    # Users should get different task lists
    # (or one might be empty if User B has no tasks)
    # But they should never see each other's tasks
    assert not any(t["owner_id"] != "550e8400-e29b-41d4-a716-446655440000" for t in tasks_1)
```

### 10. Task Summary Generation Testing

Test chatbot's task summary functionality:

```python
def test_task_summary_counts_correct(authenticated_user_headers):
    """Test that task summary returns accurate counts"""
    # Create multiple tasks with different statuses
    client.post("/api/550e8400-e29b-41d4-a716-446655440000/tasks",
                json={"title": "Task 1"}, headers=authenticated_user_headers)

    response = client.post("/api/550e8400-e29b-41d4-a716-446655440000/tasks",
                           json={"title": "Task 2"}, headers=authenticated_user_headers)
    task_2_id = response.json()["task_id"]

    # Complete one task
    client.patch(f"/api/550e8400-e29b-41d4-a716-446655440000/tasks/{task_2_id}/complete",
                 headers=authenticated_user_headers)

    # Get summary
    response = client.get(
        "/api/550e8400-e29b-41d4-a716-446655440000/tasks/summary",
        headers=authenticated_user_headers
    )

    data = response.json()
    assert data["total"] == 2
    assert data["completed"] == 1
    assert data["pending"] == 1
    assert data["completion_percentage"] == 50.0
```

### 11. Rate Limiting Testing

Test rate limit enforcement:

```python
def test_add_task_enforces_rate_limit(authenticated_user_headers):
    """Test that add_task rate limit (100/minute) is enforced"""
    # Make 101 requests
    responses = []
    for i in range(101):
        response = client.post(
            "/api/550e8400-e29b-41d4-a716-446655440000/tasks",
            json={"title": f"Task {i}"},
            headers=authenticated_user_headers
        )
        responses.append(response)

    # First 100 should succeed
    assert all(r.status_code == 201 for r in responses[:100])

    # 101st should fail with 429 Too Many Requests
    assert responses[100].status_code == 429
    data = responses[100].json()
    assert data["error"] == "rate_limit_exceeded"
    assert "reset_in_seconds" in data["details"]
```

---

## Test Coverage Requirements

| Category | Coverage | Tests |
|----------|----------|-------|
| **Authentication** | 100% | JWT extraction, expiry, mismatched user_id |
| **Authorization** | 100% | Cross-user access prevention (all 5 tools) |
| **Parameter Validation** | 100% | Required fields, enums, size limits |
| **Error Handling** | 100% | task_not_found, invalid_parameter, invalid_state, database_error |
| **Tool Composition** | 100% | List+Update, List+Delete, List+Complete patterns |
| **Agent Integration** | 100% | Mock agent tool invocation, error propagation |
| **Conversation Context** | 100% | History availability, multi-turn context |
| **Concurrency** | 100% | Simultaneous operations, data isolation |
| **Task Summary** | 100% | Count accuracy, completion percentage |
| **Rate Limiting** | 100% | Enforcement per tool, reset timing |

---

## Test Output Format

This skill produces:

1. **test_mcp_tools_security.py** - Security & authorization tests
2. **test_mcp_tools_integration.py** - Agent integration tests
3. **test_mcp_tools_errors.py** - Error handling tests
4. **test_mcp_tools_composition.py** - Tool composition tests
5. **test_mcp_tools_concurrency.py** - Concurrent operation tests
6. **conftest.py** - Shared fixtures, mocks, database setup

---

## Pytest Fixtures Provided

```python
@pytest.fixture
def authenticated_user_headers():
    """Valid JWT token for user 550e8400-e29b-41d4-a716-446655440000"""

@pytest.fixture
def other_user_headers():
    """Valid JWT token for different user"""

@pytest.fixture
def expired_token_headers():
    """Expired JWT token"""

@pytest.fixture
def invalid_token_headers():
    """Malformed JWT token"""

@pytest.fixture
def mock_openai_agent():
    """Mock agent that simulates tool invocation"""

@pytest.fixture
def conversation_with_history():
    """Database conversation with multiple messages"""

@pytest.fixture
def task_id():
    """Valid task ID owned by authenticated user"""

@pytest.fixture
def mock_db_failure():
    """Context manager that simulates database error"""
```

---

## Integration with MCP Server Builder Agent

This skill works with mcp-server-builder to:
- Generate failing tests BEFORE implementation (Red phase)
- Define expected tool behavior through tests
- Validate security properties through test cases
- Ensure agent integration works correctly
- Verify error handling is standardized

**Workflow:**
```
1. Agent uses this skill to generate failing tests (Red)
2. Agent implements minimal code to pass tests (Green)
3. Agent refactors for code quality (Refactor)
4. All tests pass with 100% security coverage
```

---

## Related Skills & Agents

- **Agent:** mcp-server-builder (primary user)
- **Skill:** MCP Tool Definition & Schema Validation (tool specs)
- **Skill:** Stateless Database Integration & Persistence (persistence patterns)
- **Framework:** pytest, Official MCP SDK

