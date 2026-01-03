# Backend Testing Specification

**Test Framework**: pytest
**Coverage Target**: 80%+ overall, 100% for critical paths
**Methodology**: Test-Driven Development (TDD)
**Version**: 1.0.0
**Last Updated**: 2026-01-02

---

## Testing Stack

### Core Testing Tools
- **pytest**: Test framework and runner
- **httpx**: Async HTTP client for API testing
- **pytest-asyncio**: Async test support
- **pytest-cov**: Code coverage reporting
- **pytest-mock**: Mocking and patching
- **faker**: Generate realistic test data
- **factory-boy**: Test fixtures and factories

### Database Testing
- **SQLite** (in-memory): Unit tests
- **PostgreSQL**: Integration tests
- **Alembic**: Migration testing

---

## Test Structure

```
backend/
├── tests/
│   ├── conftest.py                  # Shared fixtures
│   ├── test_auth.py                 # Authentication tests (250+ lines)
│   ├── test_tasks_crud.py           # Basic CRUD tests (300+ lines)
│   ├── test_tasks_intermediate.py   # Priority, tags, filters (200+ lines)
│   ├── test_tasks_advanced.py       # Recurring, reminders (200+ lines)
│   ├── test_models.py               # SQLModel validation (150+ lines)
│   ├── test_security.py             # Security tests (200+ lines)
│   ├── test_middleware.py           # JWT middleware (100+ lines)
│   ├── test_utils.py                # Utility functions (100+ lines)
│   └── factories.py                 # Test data factories
├── pytest.ini                        # Pytest configuration
└── .coveragerc                       # Coverage configuration
```

---

## Configuration Files

### pytest.ini
```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
asyncio_mode = auto
addopts =
    --verbose
    --cov=app
    --cov-report=html
    --cov-report=term-missing
    --cov-fail-under=80
markers =
    unit: Unit tests (fast, isolated)
    integration: Integration tests (database, API)
    security: Security tests (mandatory)
    slow: Slow-running tests
```

### .coveragerc
```ini
[run]
omit =
    tests/*
    */migrations/*
    */venv/*
    */__pycache__/*

[report]
exclude_lines =
    pragma: no cover
    def __repr__
    raise AssertionError
    raise NotImplementedError
    if __name__ == .__main__.:
```

---

## Test Fixtures (conftest.py)

### Database Fixtures
```python
import pytest
from sqlmodel import Session, SQLModel, create_engine
from sqlalchemy.pool import StaticPool
from app.database import get_session

# In-memory SQLite for unit tests
@pytest.fixture(scope="function")
def test_engine():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool
    )
    SQLModel.metadata.create_all(engine)
    yield engine
    SQLModel.metadata.drop_all(engine)

@pytest.fixture(scope="function")
def test_session(test_engine):
    with Session(test_engine) as session:
        yield session

@pytest.fixture(scope="function")
def client(test_session):
    """Override database session for tests"""
    from fastapi.testclient import TestClient
    from app.main import app

    def get_test_session():
        yield test_session

    app.dependency_overrides[get_session] = get_test_session
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()
```

### User Fixtures
```python
from app.models.user import User
from app.utils.security import hash_password
import uuid

@pytest.fixture
def test_user(test_session):
    """Create test user"""
    user = User(
        id=uuid.uuid4(),
        email="test@example.com",
        password_hash=hash_password("TestPass123!"),
        name="Test User"
    )
    test_session.add(user)
    test_session.commit()
    test_session.refresh(user)
    return user

@pytest.fixture
def test_user_2(test_session):
    """Create second test user for isolation tests"""
    user = User(
        id=uuid.uuid4(),
        email="test2@example.com",
        password_hash=hash_password("TestPass123!"),
        name="Test User 2"
    )
    test_session.add(user)
    test_session.commit()
    test_session.refresh(user)
    return user

@pytest.fixture
def auth_token(test_user):
    """Generate JWT token for test user"""
    from app.utils.jwt import create_jwt_token
    return create_jwt_token(test_user.id, test_user.email, test_user.name)

@pytest.fixture
def auth_headers(auth_token):
    """Generate authorization headers"""
    return {"Authorization": f"Bearer {auth_token}"}
```

### Task Fixtures
```python
from app.models.task import Task, Priority
from datetime import datetime, timedelta

@pytest.fixture
def sample_task(test_session, test_user):
    """Create sample task"""
    task = Task(
        user_id=test_user.id,
        title="Test Task",
        description="Test Description",
        priority=Priority.HIGH,
        tags=["work", "test"]
    )
    test_session.add(task)
    test_session.commit()
    test_session.refresh(task)
    return task

@pytest.fixture
def recurring_task(test_session, test_user):
    """Create recurring task"""
    task = Task(
        user_id=test_user.id,
        title="Weekly Meeting",
        description="Standup meeting",
        priority=Priority.MEDIUM,
        due_date=datetime.utcnow() + timedelta(days=1),
        is_recurring=True,
        recurrence_pattern="WEEKLY"
    )
    test_session.add(task)
    test_session.commit()
    test_session.refresh(task)
    return task
```

---

## Authentication Tests (test_auth.py)

### Signup Tests
```python
import pytest
from fastapi.testclient import TestClient

@pytest.mark.unit
def test_signup_creates_user(client, test_session):
    """Test successful user signup"""
    response = client.post("/api/auth/signup", json={
        "email": "newuser@example.com",
        "password": "SecurePass123!",
        "name": "New User"
    })

    assert response.status_code == 201
    data = response.json()
    assert data["user"]["email"] == "newuser@example.com"
    assert data["user"]["name"] == "New User"
    assert "token" in data
    assert "expires_at" in data
    assert "password_hash" not in data["user"]  # Security: Never expose password

@pytest.mark.unit
def test_signup_duplicate_email_rejected(client, test_user):
    """Test signup with existing email fails"""
    response = client.post("/api/auth/signup", json={
        "email": test_user.email,
        "password": "SecurePass123!",
        "name": "Duplicate User"
    })

    assert response.status_code == 409
    assert "already exists" in response.json()["message"].lower()

@pytest.mark.unit
@pytest.mark.parametrize("password,expected_error", [
    ("short", "at least 8 characters"),
    ("nouppercase1!", "uppercase"),
    ("NOLOWERCASE1!", "lowercase"),
    ("NoNumber!", "number"),
    ("NoSpecial123", "special character"),
])
def test_signup_weak_password_rejected(client, password, expected_error):
    """Test weak passwords are rejected"""
    response = client.post("/api/auth/signup", json={
        "email": "test@example.com",
        "password": password,
        "name": "Test User"
    })

    assert response.status_code == 400
    assert expected_error.lower() in response.json()["details"]["password"].lower()
```

### Login Tests
```python
@pytest.mark.unit
def test_login_with_valid_credentials(client, test_user):
    """Test login with correct credentials"""
    response = client.post("/api/auth/login", json={
        "email": test_user.email,
        "password": "TestPass123!"
    })

    assert response.status_code == 200
    data = response.json()
    assert data["user"]["email"] == test_user.email
    assert "token" in data
    assert len(data["token"]) > 50  # JWT token length

@pytest.mark.unit
def test_login_with_invalid_credentials(client, test_user):
    """Test login with wrong password"""
    response = client.post("/api/auth/login", json={
        "email": test_user.email,
        "password": "WrongPassword123!"
    })

    assert response.status_code == 401
    assert "invalid email or password" in response.json()["error"].lower()

@pytest.mark.unit
def test_login_with_nonexistent_email(client):
    """Test login with non-existent email"""
    response = client.post("/api/auth/login", json={
        "email": "nonexistent@example.com",
        "password": "TestPass123!"
    })

    assert response.status_code == 401
    # Generic error message (don't reveal if email exists)
    assert "invalid email or password" in response.json()["error"].lower()

@pytest.mark.unit
def test_login_updates_last_login_timestamp(client, test_user, test_session):
    """Test last_login_at is updated on successful login"""
    original_last_login = test_user.last_login_at

    response = client.post("/api/auth/login", json={
        "email": test_user.email,
        "password": "TestPass123!"
    })

    assert response.status_code == 200
    test_session.refresh(test_user)
    assert test_user.last_login_at is not None
    assert test_user.last_login_at != original_last_login
```

### JWT Token Tests
```python
from app.utils.jwt import create_jwt_token, verify_jwt_token
from datetime import datetime, timedelta

@pytest.mark.unit
def test_jwt_token_contains_correct_payload(test_user):
    """Test JWT token contains user info"""
    token = create_jwt_token(test_user.id, test_user.email, test_user.name)
    payload = verify_jwt_token(token)

    assert payload["user_id"] == str(test_user.id)
    assert payload["email"] == test_user.email
    assert payload["name"] == test_user.name
    assert "exp" in payload
    assert "iat" in payload

@pytest.mark.unit
def test_expired_token_rejected(test_user):
    """Test expired JWT token is rejected"""
    from jose import jwt
    import os

    payload = {
        "user_id": str(test_user.id),
        "email": test_user.email,
        "exp": datetime.utcnow() - timedelta(seconds=10)  # Expired 10 seconds ago
    }
    expired_token = jwt.encode(payload, os.getenv("BETTER_AUTH_SECRET"), algorithm="HS256")

    with pytest.raises(Exception) as exc_info:
        verify_jwt_token(expired_token)
    assert "expired" in str(exc_info.value).lower()

@pytest.mark.unit
def test_tampered_token_rejected(test_user):
    """Test token with invalid signature is rejected"""
    token = create_jwt_token(test_user.id, test_user.email, test_user.name)
    tampered_token = token[:-10] + "tampered123"

    with pytest.raises(Exception):
        verify_jwt_token(tampered_token)
```

---

## Task CRUD Tests (test_tasks_crud.py)

### Create Task Tests
```python
@pytest.mark.integration
def test_create_task_success(client, test_user, auth_headers):
    """Test creating task with valid data"""
    response = client.post(
        f"/api/{test_user.id}/tasks",
        json={
            "title": "New Task",
            "description": "Task description",
            "priority": "HIGH"
        },
        headers=auth_headers
    )

    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "New Task"
    assert data["user_id"] == str(test_user.id)
    assert data["completed"] == False
    assert data["priority"] == "HIGH"
    assert "id" in data
    assert "created_at" in data

@pytest.mark.integration
def test_create_task_without_title_fails(client, test_user, auth_headers):
    """Test creating task without title fails"""
    response = client.post(
        f"/api/{test_user.id}/tasks",
        json={"description": "No title"},
        headers=auth_headers
    )

    assert response.status_code == 400
    assert "title" in response.json()["details"]

@pytest.mark.integration
def test_create_task_without_auth_fails(client, test_user):
    """Test creating task without authentication fails"""
    response = client.post(
        f"/api/{test_user.id}/tasks",
        json={"title": "Unauthorized Task"}
    )

    assert response.status_code == 401
```

### Read Task Tests
```python
@pytest.mark.integration
def test_list_user_tasks(client, test_user, sample_task, auth_headers):
    """Test listing tasks for authenticated user"""
    response = client.get(
        f"/api/{test_user.id}/tasks",
        headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json()
    assert "tasks" in data
    assert len(data["tasks"]) >= 1
    assert data["tasks"][0]["user_id"] == str(test_user.id)

@pytest.mark.integration
def test_get_task_by_id(client, test_user, sample_task, auth_headers):
    """Test retrieving specific task by ID"""
    response = client.get(
        f"/api/{test_user.id}/tasks/{sample_task.id}",
        headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(sample_task.id)
    assert data["title"] == sample_task.title

@pytest.mark.integration
def test_get_nonexistent_task_returns_404(client, test_user, auth_headers):
    """Test getting non-existent task returns 404"""
    fake_uuid = "550e8400-e29b-41d4-a716-446655440000"
    response = client.get(
        f"/api/{test_user.id}/tasks/{fake_uuid}",
        headers=auth_headers
    )

    assert response.status_code == 404
```

### Update Task Tests
```python
@pytest.mark.integration
def test_update_task_title(client, test_user, sample_task, auth_headers):
    """Test updating task title"""
    response = client.put(
        f"/api/{test_user.id}/tasks/{sample_task.id}",
        json={"title": "Updated Title"},
        headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated Title"
    assert data["updated_at"] != data["created_at"]

@pytest.mark.integration
def test_update_task_partial_fields(client, test_user, sample_task, auth_headers):
    """Test partial update (only some fields)"""
    original_title = sample_task.title

    response = client.put(
        f"/api/{test_user.id}/tasks/{sample_task.id}",
        json={"priority": "LOW"},
        headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json()
    assert data["priority"] == "LOW"
    assert data["title"] == original_title  # Unchanged
```

### Delete Task Tests
```python
@pytest.mark.integration
def test_delete_task(client, test_user, sample_task, auth_headers, test_session):
    """Test deleting task"""
    response = client.delete(
        f"/api/{test_user.id}/tasks/{sample_task.id}",
        headers=auth_headers
    )

    assert response.status_code == 200
    assert "deleted" in response.json()["message"].lower()

    # Verify task is actually deleted from database
    from app.models.task import Task
    deleted_task = test_session.get(Task, sample_task.id)
    assert deleted_task is None
```

### Complete Task Tests
```python
@pytest.mark.integration
def test_mark_task_complete(client, test_user, sample_task, auth_headers):
    """Test marking task as complete"""
    response = client.patch(
        f"/api/{test_user.id}/tasks/{sample_task.id}/complete",
        headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json()["task"]
    assert data["completed"] == True
    assert data["completed_at"] is not None

@pytest.mark.integration
def test_toggle_task_completion(client, test_user, sample_task, auth_headers):
    """Test toggling task completion status"""
    # Mark complete
    response1 = client.patch(
        f"/api/{test_user.id}/tasks/{sample_task.id}/complete",
        headers=auth_headers
    )
    assert response1.json()["task"]["completed"] == True

    # Mark incomplete
    response2 = client.patch(
        f"/api/{test_user.id}/tasks/{sample_task.id}/complete",
        headers=auth_headers
    )
    assert response2.json()["task"]["completed"] == False
    assert response2.json()["task"]["completed_at"] is None
```

---

## Security Tests (test_security.py)

### User Isolation Tests (CRITICAL)
```python
@pytest.mark.security
def test_user_cannot_access_other_users_tasks(client, test_user, test_user_2, auth_headers, test_session):
    """Test User A cannot view User B's tasks"""
    # Create task for User B
    from app.models.task import Task
    user_b_task = Task(
        user_id=test_user_2.id,
        title="User B's Task"
    )
    test_session.add(user_b_task)
    test_session.commit()

    # User A tries to access User B's tasks
    response = client.get(
        f"/api/{test_user_2.id}/tasks",
        headers=auth_headers  # User A's token
    )

    assert response.status_code == 403
    assert "permission" in response.json()["message"].lower()

@pytest.mark.security
def test_user_cannot_update_other_users_task(client, test_user, test_user_2, sample_task, auth_headers):
    """Test User B cannot update User A's task"""
    # Get User B's token
    from app.utils.jwt import create_jwt_token
    user_b_token = create_jwt_token(test_user_2.id, test_user_2.email, test_user_2.name)
    user_b_headers = {"Authorization": f"Bearer {user_b_token}"}

    # User B tries to update User A's task
    response = client.put(
        f"/api/{test_user.id}/tasks/{sample_task.id}",
        json={"title": "Hacked Title"},
        headers=user_b_headers
    )

    assert response.status_code == 403

@pytest.mark.security
def test_user_cannot_delete_other_users_task(client, test_user, test_user_2, sample_task, auth_headers):
    """Test User B cannot delete User A's task"""
    from app.utils.jwt import create_jwt_token
    user_b_token = create_jwt_token(test_user_2.id, test_user_2.email, test_user_2.name)
    user_b_headers = {"Authorization": f"Bearer {user_b_token}"}

    response = client.delete(
        f"/api/{test_user.id}/tasks/{sample_task.id}",
        headers=user_b_headers
    )

    assert response.status_code == 403
```

### SQL Injection Prevention Tests
```python
@pytest.mark.security
def test_sql_injection_in_task_title(client, test_user, auth_headers, test_session):
    """Test SQL injection attempt in task title is blocked"""
    malicious_title = "Test'; DROP TABLE tasks; --"

    response = client.post(
        f"/api/{test_user.id}/tasks",
        json={"title": malicious_title},
        headers=auth_headers
    )

    # Should succeed (SQLModel parameterizes queries)
    assert response.status_code == 201

    # Verify tables still exist
    from app.models.task import Task
    tasks_count = test_session.query(Task).count()
    assert tasks_count >= 0  # Table exists

@pytest.mark.security
def test_sql_injection_in_search(client, test_user, auth_headers, test_session):
    """Test SQL injection in search query"""
    response = client.get(
        f"/api/{test_user.id}/tasks?search=' OR '1'='1",
        headers=auth_headers
    )

    # Should not return all tasks or crash
    assert response.status_code == 200
    # Only return user's own tasks
    for task in response.json()["tasks"]:
        assert task["user_id"] == str(test_user.id)
```

### XSS Prevention Tests
```python
@pytest.mark.security
def test_xss_attempt_in_task_description(client, test_user, auth_headers):
    """Test XSS script in task description"""
    xss_payload = "<script>alert('XSS')</script>"

    response = client.post(
        f"/api/{test_user.id}/tasks",
        json={
            "title": "Test Task",
            "description": xss_payload
        },
        headers=auth_headers
    )

    # Backend accepts (frontend must sanitize on display)
    assert response.status_code == 201
    # But script should be stored as-is (not executed server-side)
    assert response.json()["description"] == xss_payload
```

---

## Advanced Feature Tests (test_tasks_advanced.py)

### Recurring Task Tests
```python
@pytest.mark.integration
def test_daily_task_reschedules_correctly(client, test_user, auth_headers, test_session):
    """Test DAILY recurring task reschedules +1 day"""
    from datetime import datetime, timedelta

    # Create daily recurring task
    response = client.post(
        f"/api/{test_user.id}/tasks",
        json={
            "title": "Daily Task",
            "due_date": "2026-01-03T09:00:00Z",
            "is_recurring": True,
            "recurrence_pattern": "DAILY"
        },
        headers=auth_headers
    )
    task_id = response.json()["id"]

    # Complete task
    complete_response = client.patch(
        f"/api/{test_user.id}/tasks/{task_id}/complete",
        headers=auth_headers
    )

    # Verify new task created with +1 day
    new_task = complete_response.json()["new_recurring_task"]
    assert new_task is not None
    assert new_task["due_date"] == "2026-01-04T09:00:00Z"
    assert new_task["is_recurring"] == True
    assert new_task["completed"] == False

@pytest.mark.integration
def test_weekly_task_reschedules_correctly(client, test_user, auth_headers):
    """Test WEEKLY recurring task reschedules +7 days"""
    response = client.post(
        f"/api/{test_user.id}/tasks",
        json={
            "title": "Weekly Task",
            "due_date": "2026-01-06T14:00:00Z",
            "is_recurring": True,
            "recurrence_pattern": "WEEKLY"
        },
        headers=auth_headers
    )
    task_id = response.json()["id"]

    complete_response = client.patch(
        f"/api/{test_user.id}/tasks/{task_id}/complete",
        headers=auth_headers
    )

    new_task = complete_response.json()["new_recurring_task"]
    assert new_task["due_date"] == "2026-01-13T14:00:00Z"  # +7 days

@pytest.mark.integration
def test_monthly_task_reschedules_correctly(client, test_user, auth_headers):
    """Test MONTHLY recurring task reschedules +1 month"""
    response = client.post(
        f"/api/{test_user.id}/tasks",
        json={
            "title": "Monthly Task",
            "due_date": "2026-01-15T10:00:00Z",
            "is_recurring": True,
            "recurrence_pattern": "MONTHLY"
        },
        headers=auth_headers
    )
    task_id = response.json()["id"]

    complete_response = client.patch(
        f"/api/{test_user.id}/tasks/{task_id}/complete",
        headers=auth_headers
    )

    new_task = complete_response.json()["new_recurring_task"]
    assert new_task["due_date"] == "2026-02-15T10:00:00Z"  # +1 month

@pytest.mark.integration
def test_monthly_task_handles_month_end_edge_case(client, test_user, auth_headers):
    """Test monthly task handles Feb 31 → Feb 28"""
    response = client.post(
        f"/api/{test_user.id}/tasks",
        json={
            "title": "End of Month Task",
            "due_date": "2026-01-31T10:00:00Z",
            "is_recurring": True,
            "recurrence_pattern": "MONTHLY"
        },
        headers=auth_headers
    )
    task_id = response.json()["id"]

    complete_response = client.patch(
        f"/api/{test_user.id}/tasks/{task_id}/complete",
        headers=auth_headers
    )

    new_task = complete_response.json()["new_recurring_task"]
    # Jan 31 + 1 month = Feb 28 (2026 is not a leap year)
    assert new_task["due_date"] == "2026-02-28T10:00:00Z"
```

### Due Date Validation Tests
```python
@pytest.mark.integration
def test_past_due_date_rejected(client, test_user, auth_headers):
    """Test task with past due date is rejected"""
    from datetime import datetime, timedelta
    past_date = (datetime.utcnow() - timedelta(days=1)).isoformat() + "Z"

    response = client.post(
        f"/api/{test_user.id}/tasks",
        json={
            "title": "Past Task",
            "due_date": past_date
        },
        headers=auth_headers
    )

    assert response.status_code == 400
    assert "past" in response.json()["details"]["due_date"].lower()

@pytest.mark.integration
def test_recurring_task_requires_due_date(client, test_user, auth_headers):
    """Test recurring task without due date is rejected"""
    response = client.post(
        f"/api/{test_user.id}/tasks",
        json={
            "title": "Recurring Task",
            "is_recurring": True,
            "recurrence_pattern": "DAILY"
        },
        headers=auth_headers
    )

    assert response.status_code == 400
    assert "due_date" in response.json()["details"]
```

---

## Performance Tests

```python
import time
import pytest

@pytest.mark.slow
def test_task_list_performance(client, test_user, auth_headers, test_session):
    """Test listing 100 tasks completes < 200ms"""
    # Create 100 tasks
    from app.models.task import Task
    tasks = [
        Task(user_id=test_user.id, title=f"Task {i}")
        for i in range(100)
    ]
    test_session.add_all(tasks)
    test_session.commit()

    # Measure performance
    start = time.time()
    response = client.get(f"/api/{test_user.id}/tasks", headers=auth_headers)
    duration = (time.time() - start) * 1000  # Convert to ms

    assert response.status_code == 200
    assert duration < 200  # < 200ms

@pytest.mark.slow
def test_jwt_verification_performance(auth_token):
    """Test JWT verification completes < 10ms"""
    from app.utils.jwt import verify_jwt_token

    start = time.time()
    for _ in range(100):
        verify_jwt_token(auth_token)
    duration = (time.time() - start) * 1000 / 100  # Avg per verification

    assert duration < 10  # < 10ms average
```

---

## Running Tests

### Run All Tests
```bash
pytest
```

### Run Specific Test File
```bash
pytest tests/test_auth.py
```

### Run by Marker
```bash
pytest -m unit          # Only unit tests
pytest -m integration   # Only integration tests
pytest -m security      # Only security tests (mandatory)
```

### Run with Coverage
```bash
pytest --cov=app --cov-report=html
```

### Run in Parallel (faster)
```bash
pytest -n auto  # Uses all CPU cores
```

---

## Success Criteria

Backend testing is complete when:

- ✅ 80%+ overall test coverage
- ✅ 100% coverage for authentication logic
- ✅ 100% coverage for user isolation checks
- ✅ All security tests passing
- ✅ All integration tests passing
- ✅ Performance benchmarks met
- ✅ No flaky tests

---

**Version**: 1.0.0
**Last Updated**: 2026-01-02
**Owner**: Phase 2 Development Team
