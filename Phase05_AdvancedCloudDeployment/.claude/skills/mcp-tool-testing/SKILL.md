---
name: mcp-tool-testing
description: "Create comprehensive test suites for MCP tools using pytest with SQLModel database fixtures, direct database verification, and transaction rollback. Use when: (1) writing unit tests for MCP tool implementations (add_task, list_tasks, complete_task, delete_task, update_task, get_task_summary), (2) setting up SQLModel fixtures with automatic transaction rollback for test isolation, (3) testing input validation (required fields, types, length constraints, enum values), (4) testing authorization with per-query user_id filtering for multi-user isolation, (5) testing database constraint violations (unique, foreign key, not null), (6) testing concurrent/concurrent operations with race condition detection, (7) testing query performance with result verification, (8) testing error handling with 25+ error codes from error taxonomy, (9) testing tool composition/chaining with sequential operations, (10) testing response schema validation, (11) testing edge cases (empty results, boundary values, special characters)."
---

# MCP Tool Testing

## Core Responsibility

Test MCP tool implementations end-to-end with direct database verification using pytest + SQLModel. Verify:

1. **Input Validation**: Required fields, types, ranges, enum values, format constraints
2. **Authorization**: User_id filtering, ownership verification, cross-user prevention
3. **Database Operations**: Create, read, update, delete with transaction safety
4. **Constraint Handling**: Unique, foreign key, not null violations → proper error responses
5. **Concurrency**: Race condition prevention with optimistic/row-level locking
6. **Query Performance**: Execution times, N+1 query prevention, proper indexing
7. **Error Taxonomy**: All 25+ error codes mapped to correct HTTP status codes
8. **Tool Chaining**: Sequential tool calls with data flow between steps
9. **Response Validation**: Schema compliance, field types, pagination metadata
10. **Edge Cases**: Empty results, boundary values, special characters, unicode

## Quick Start: Fixture-Based Testing

```python
# Use SQLModel fixtures with automatic rollback
import pytest
from sqlmodel import Session, create_engine
from sqlmodel.pool import StaticPool

@pytest.fixture
def session():
    """Database session with automatic rollback after each test"""
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
    # Automatic rollback on exit

@pytest.mark.asyncio
async def test_add_task_creates_task_in_database(session):
    """add_task tool persists task to database"""
    result = await add_task_tool(
        session=session,
        user_id="user-123",
        title="Buy milk",
        trace_id="trace-1"
    )

    assert result["status"] == "success"
    assert result["task"]["title"] == "Buy milk"

    # Verify in database
    task = session.query(Task).filter(
        Task.user_id == "user-123",
        Task.title == "Buy milk"
    ).first()
    assert task is not None
```

## Section 1: SQLModel Fixtures & Test Infrastructure

Set up reusable test fixtures for database operations.

### Basic Database Fixture
```python
import pytest
from sqlmodel import Session, create_engine, SQLModel
from sqlmodel.pool import StaticPool

@pytest.fixture
def engine():
    """Create in-memory SQLite for testing"""
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    return engine

@pytest.fixture
def session(engine):
    """Database session with automatic rollback"""
    connection = engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture
def user_a(session):
    """Create test user A"""
    user = User(id="user-a", email="a@test.com")
    session.add(user)
    session.commit()
    return user

@pytest.fixture
def user_b(session):
    """Create test user B"""
    user = User(id="user-b", email="b@test.com")
    session.add(user)
    session.commit()
    return user

@pytest.fixture
def task_factory(session):
    """Factory for creating test tasks"""
    def create_task(user_id, title="Test", priority="medium", status="pending"):
        task = Task(
            user_id=user_id,
            title=title,
            priority=priority,
            status=status
        )
        session.add(task)
        session.commit()
        session.refresh(task)
        return task
    return create_task
```

### Trace ID Fixture
```python
@pytest.fixture
def trace_id():
    """Generate trace ID for logging"""
    from uuid import uuid4
    return str(uuid4())
```

## Section 2: Input Validation Tests

Test all validation rules for tool parameters.

### add_task: Required Fields
```python
@pytest.mark.asyncio
async def test_add_task_missing_title_returns_validation_error(session, trace_id):
    """Missing 'title' field → ValidationError"""
    with pytest.raises(ValidationError) as exc:
        await add_task_tool(
            session=session,
            user_id="user-123",
            title="",  # Empty
            trace_id=trace_id
        )

    assert "title" in str(exc.value).lower()
```

### add_task: Title Length Constraints
```python
@pytest.mark.asyncio
async def test_add_task_title_too_long_returns_validation_error(session, trace_id):
    """Title > 500 chars → ValidationError"""
    with pytest.raises(ValidationError):
        await add_task_tool(
            session=session,
            user_id="user-123",
            title="x" * 501,
            trace_id=trace_id
        )

@pytest.mark.asyncio
async def test_add_task_title_max_length_accepted(session, trace_id):
    """Title exactly 500 chars → accepted"""
    result = await add_task_tool(
        session=session,
        user_id="user-123",
        title="x" * 500,
        trace_id=trace_id
    )

    assert result["status"] == "success"
    assert len(result["task"]["title"]) == 500
```

### add_task: Priority Enum Validation
```python
@pytest.mark.asyncio
async def test_add_task_invalid_priority_returns_validation_error(session, trace_id):
    """Priority not in ['low', 'medium', 'high'] → ValidationError"""
    with pytest.raises(ValidationError):
        await add_task_tool(
            session=session,
            user_id="user-123",
            title="Test",
            priority="urgent",  # Invalid
            trace_id=trace_id
        )

@pytest.mark.asyncio
async def test_add_task_valid_priorities_accepted(session, trace_id):
    """Valid priorities ['low', 'medium', 'high'] → accepted"""
    for priority in ["low", "medium", "high"]:
        result = await add_task_tool(
            session=session,
            user_id="user-123",
            title=f"Task {priority}",
            priority=priority,
            trace_id=trace_id
        )
        assert result["status"] == "success"
        assert result["task"]["priority"] == priority
```

### add_task: Special Characters in Title
```python
@pytest.mark.asyncio
async def test_add_task_special_characters_accepted(session, trace_id):
    """Special chars in title → accepted"""
    test_titles = [
        "Buy milk & bread",
        "Task with 'quotes' and \"double\"",
        "Task with émojis 🎉",
        "Task with\ttabs\tand\nnewlines",
    ]

    for title in test_titles:
        result = await add_task_tool(
            session=session,
            user_id="user-123",
            title=title,
            trace_id=trace_id
        )
        assert result["status"] == "success"
```

### list_tasks: Pagination Validation
```python
@pytest.mark.asyncio
async def test_list_tasks_limit_enforcement(session, user_a, task_factory, trace_id):
    """List respects limit parameter"""
    # Create 10 tasks
    for i in range(10):
        task_factory(user_a.id, f"Task {i}")

    result = await list_tasks_tool(
        session=session,
        user_id=user_a.id,
        limit=5,
        offset=0,
        trace_id=trace_id
    )

    assert len(result["tasks"]) == 5
    assert result["total"] == 10
    assert result["has_more"] is True
```

## Section 3: Authorization & User Isolation Tests

Enforce multi-user isolation - users can only access own tasks.

### User Can Access Own Tasks
```python
@pytest.mark.asyncio
async def test_list_tasks_user_sees_only_own_tasks(session, user_a, user_b, task_factory, trace_id):
    """User A only sees User A's tasks"""
    task_a = task_factory(user_a.id, "Task A")
    task_b = task_factory(user_b.id, "Task B")

    result = await list_tasks_tool(
        session=session,
        user_id=user_a.id,
        trace_id=trace_id
    )

    task_ids = [t["id"] for t in result["tasks"]]
    assert task_a.id in task_ids
    assert task_b.id not in task_ids
```

### User Cannot Access Another User's Task
```python
@pytest.mark.asyncio
async def test_complete_task_user_b_cannot_complete_user_a_task(session, user_a, user_b, task_factory, trace_id):
    """User B cannot complete User A's task → AuthorizationError"""
    task_a = task_factory(user_a.id, "Task A")

    with pytest.raises(AuthorizationError):
        await complete_task_tool(
            session=session,
            user_id=user_b.id,
            task_id=task_a.id,
            trace_id=trace_id
        )

    # Verify task unchanged
    db_task = session.query(Task).get(task_a.id)
    assert db_task.status == "pending"
```

### User Cannot Update Another User's Task
```python
@pytest.mark.asyncio
async def test_update_task_user_cannot_update_other_user_task(session, user_a, user_b, task_factory, trace_id):
    """User B trying to update User A's task → 403 Forbidden"""
    task_a = task_factory(user_a.id, "Task A", priority="low")

    with pytest.raises(AuthorizationError):
        await update_task_tool(
            session=session,
            user_id=user_b.id,
            task_id=task_a.id,
            priority="high",
            trace_id=trace_id
        )

    # Verify unchanged
    db_task = session.query(Task).get(task_a.id)
    assert db_task.priority == "low"
```

## Section 4: Constraint Violation Tests

Test database constraint handling.

### Duplicate Task Title for Same User
```python
@pytest.mark.asyncio
async def test_add_task_duplicate_title_allowed(session, user_a, task_factory, trace_id):
    """Same user can have duplicate titles"""
    task_factory(user_a.id, "Buy milk")

    result = await add_task_tool(
        session=session,
        user_id=user_a.id,
        title="Buy milk",  # Duplicate
        trace_id=trace_id
    )

    assert result["status"] == "success"
```

### Not Null Constraint
```python
@pytest.mark.asyncio
async def test_add_task_missing_user_id_raises_constraint_error(session, trace_id):
    """Missing user_id → ConstraintError (NOT NULL)"""
    with pytest.raises((ValueError, ValidationError)):
        await add_task_tool(
            session=session,
            user_id="",  # Empty/missing
            title="Test",
            trace_id=trace_id
        )
```

## Section 5: Concurrency & Race Condition Tests

Test concurrent operations with locking.

### Optimistic Locking - Version Mismatch
```python
@pytest.mark.asyncio
async def test_update_task_concurrent_modification_detected(session, user_a, task_factory, trace_id):
    """Concurrent updates → version mismatch detected"""
    task = task_factory(user_a.id, "Task", version=1)
    original_version = task.version

    # Simulate another request updating the task
    task.version += 1
    session.commit()

    # Try to update with old version → should fail
    with pytest.raises(Exception):  # VersionMismatchError or ConflictError
        await update_task_tool(
            session=session,
            user_id=user_a.id,
            task_id=task.id,
            title="New Title",
            expected_version=original_version,
            trace_id=trace_id
        )
```

## Section 6: Query Performance Tests

Test execution times and query efficiency.

### Query Execution Time
```python
@pytest.mark.asyncio
async def test_list_tasks_executes_within_100ms(session, user_a, task_factory, trace_id):
    """list_tasks completes in <100ms (without network latency)"""
    import time

    for i in range(100):
        task_factory(user_a.id, f"Task {i}")

    start = time.time()
    result = await list_tasks_tool(
        session=session,
        user_id=user_a.id,
        limit=50,
        trace_id=trace_id
    )
    elapsed_ms = (time.time() - start) * 1000

    assert elapsed_ms < 100
    assert len(result["tasks"]) == 50
```

## Section 7: Error Handling Tests

Test 25+ error codes from error taxonomy.

### Invalid Task ID Format
```python
@pytest.mark.asyncio
async def test_complete_task_invalid_task_id_returns_validation_error(session, user_a, trace_id):
    """Invalid task_id format → ValidationError"""
    with pytest.raises(ValidationError):
        await complete_task_tool(
            session=session,
            user_id=user_a.id,
            task_id="not-a-uuid",
            trace_id=trace_id
        )
```

### Task Not Found
```python
@pytest.mark.asyncio
async def test_complete_task_nonexistent_task_returns_404(session, user_a, trace_id):
    """Non-existent task_id → ResourceNotFoundError (403 to prevent enumeration)"""
    from uuid import uuid4

    with pytest.raises(Exception):  # AuthorizationError (403) or ResourceNotFoundError
        await complete_task_tool(
            session=session,
            user_id=user_a.id,
            task_id=str(uuid4()),
            trace_id=trace_id
        )
```

## Section 8: Tool Chaining Tests

Test sequential tool calls with data flow.

### Add Task → List Tasks → Complete Task Chain
```python
@pytest.mark.asyncio
async def test_tool_chain_add_list_complete(session, user_a, trace_id):
    """Sequential: add task → list → complete"""

    # Step 1: Add task
    add_result = await add_task_tool(
        session=session,
        user_id=user_a.id,
        title="Buy milk",
        trace_id=trace_id
    )
    task_id = add_result["task"]["id"]

    # Step 2: List tasks (should include new task)
    list_result = await list_tasks_tool(
        session=session,
        user_id=user_a.id,
        trace_id=trace_id
    )
    task_ids = [t["id"] for t in list_result["tasks"]]
    assert task_id in task_ids

    # Step 3: Complete task
    complete_result = await complete_task_tool(
        session=session,
        user_id=user_a.id,
        task_id=task_id,
        trace_id=trace_id
    )
    assert complete_result["task"]["status"] == "completed"

    # Step 4: Verify in list with status filter
    list_result2 = await list_tasks_tool(
        session=session,
        user_id=user_a.id,
        status="completed",
        trace_id=trace_id
    )
    completed_ids = [t["id"] for t in list_result2["tasks"]]
    assert task_id in completed_ids
```

### Add Multiple Tasks → Get Summary
```python
@pytest.mark.asyncio
async def test_tool_chain_add_tasks_get_summary(session, user_a, trace_id):
    """Add 3 tasks → get summary → verify counts"""

    # Add 3 tasks with different priorities
    for i, priority in enumerate(["high", "medium", "low"]):
        await add_task_tool(
            session=session,
            user_id=user_a.id,
            title=f"Task {i}",
            priority=priority,
            trace_id=trace_id
        )

    # Get summary
    summary = await get_task_summary_tool(
        session=session,
        user_id=user_a.id,
        trace_id=trace_id
    )

    assert summary["total"] == 3
    assert summary["completed"] == 0
    assert summary["pending"] == 3
    assert summary["by_priority"]["high"] == 1
    assert summary["by_priority"]["medium"] == 1
    assert summary["by_priority"]["low"] == 1
```

## Section 9: Response Schema Validation

Verify response formats match contracts.

### add_task Response Schema
```python
@pytest.mark.asyncio
async def test_add_task_response_schema(session, user_a, trace_id):
    """Response has required fields with correct types"""
    result = await add_task_tool(
        session=session,
        user_id=user_a.id,
        title="Test Task",
        trace_id=trace_id
    )

    # Required fields
    assert "status" in result
    assert "task" in result

    # Task fields
    task = result["task"]
    assert isinstance(task["id"], str)  # UUID
    assert isinstance(task["title"], str)
    assert isinstance(task["priority"], str)
    assert isinstance(task["status"], str)
    assert isinstance(task["created_at"], str)  # ISO format datetime
    assert "user_id" not in task  # Never expose user_id in response
```

### list_tasks Response Schema
```python
@pytest.mark.asyncio
async def test_list_tasks_response_schema(session, user_a, task_factory, trace_id):
    """Response includes pagination metadata"""
    task_factory(user_a.id, "Task 1")

    result = await list_tasks_tool(
        session=session,
        user_id=user_a.id,
        limit=10,
        offset=0,
        trace_id=trace_id
    )

    assert "tasks" in result
    assert isinstance(result["tasks"], list)
    assert "total" in result
    assert isinstance(result["total"], int)
    assert "limit" in result
    assert "offset" in result
    assert "has_more" in result
    assert isinstance(result["has_more"], bool)
```

## Section 10: Edge Cases

Test boundary values and special scenarios.

### Empty Task List
```python
@pytest.mark.asyncio
async def test_list_tasks_empty_returns_empty_array(session, user_a, trace_id):
    """No tasks → empty array, but metadata still present"""
    result = await list_tasks_tool(
        session=session,
        user_id=user_a.id,
        trace_id=trace_id
    )

    assert result["tasks"] == []
    assert result["total"] == 0
    assert result["has_more"] is False
```

### Boundary: Exactly At Pagination Limit
```python
@pytest.mark.asyncio
async def test_list_tasks_exactly_at_limit(session, user_a, task_factory, trace_id):
    """Exactly 50 tasks with limit=50 → has_more=False"""
    for i in range(50):
        task_factory(user_a.id, f"Task {i}")

    result = await list_tasks_tool(
        session=session,
        user_id=user_a.id,
        limit=50,
        trace_id=trace_id
    )

    assert len(result["tasks"]) == 50
    assert result["has_more"] is False
```

### Boundary: One More Than Limit
```python
@pytest.mark.asyncio
async def test_list_tasks_one_more_than_limit(session, user_a, task_factory, trace_id):
    """51 tasks with limit=50 → has_more=True"""
    for i in range(51):
        task_factory(user_a.id, f"Task {i}")

    result = await list_tasks_tool(
        session=session,
        user_id=user_a.id,
        limit=50,
        trace_id=trace_id
    )

    assert len(result["tasks"]) == 50
    assert result["total"] == 51
    assert result["has_more"] is True
```

---

## Testing Checklist

Use this checklist to validate complete MCP tool test coverage:

- [ ] Input validation (required fields, types, ranges, enums, formats)
- [ ] Title length constraints (min/max)
- [ ] Priority enum validation (low/medium/high)
- [ ] Pagination (limit enforcement, offset, has_more)
- [ ] User isolation (user A cannot access user B's tasks)
- [ ] Authorization failures (proper error types)
- [ ] Constraint violations (NOT NULL, unique, foreign key)
- [ ] Concurrent modification detection (version mismatch)
- [ ] Query performance (<100ms for list)
- [ ] 25+ error codes tested
- [ ] Tool chaining (sequential operations)
- [ ] Response schema validation (all fields, types)
- [ ] Edge cases (empty lists, boundary values)
- [ ] Response never exposes user_id

---

## Quick Reference: Tool Signatures

```python
# add_task
await add_task_tool(session, user_id, title, description="", priority="medium", trace_id)
# Returns: {"status": "success|error", "task": {...}, "error": "..."}

# list_tasks
await list_tasks_tool(session, user_id, limit=50, offset=0, status=None, priority=None, trace_id)
# Returns: {"tasks": [...], "total": int, "limit": int, "offset": int, "has_more": bool}

# complete_task
await complete_task_tool(session, user_id, task_id, trace_id)
# Returns: {"status": "success|error", "task": {...}, "error": "..."}

# update_task
await update_task_tool(session, user_id, task_id, title=None, priority=None, status=None, trace_id)
# Returns: {"status": "success|error", "task": {...}, "error": "..."}

# delete_task
await delete_task_tool(session, user_id, task_id, trace_id)
# Returns: {"status": "success|error", "message": "...", "error": "..."}

# get_task_summary
await get_task_summary_tool(session, user_id, trace_id)
# Returns: {"total": int, "completed": int, "pending": int, "by_priority": {...}}
```
