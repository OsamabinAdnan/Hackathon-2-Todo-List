# Testing Strategy - Phase 2 Overview

**Document Type**: Testing Specification
**Phase**: Phase 2 (Full-Stack Web Application)
**Methodology**: Test-Driven Development (TDD) with Red-Green-Refactor cycle
**Version**: 1.0.0
**Last Updated**: 2026-01-02

---

## Testing Philosophy

This project follows **strict Test-Driven Development (TDD)** principles:

1. **Red**: Write a failing test that defines expected behavior
2. **Green**: Write minimal code to make the test pass
3. **Refactor**: Improve code quality while keeping tests green

**Core Principle**: No production code is written without a failing test first.

---

## Testing Pyramid

```
           ╱╲
          ╱  ╲      E2E Tests (5-10%)
         ╱────╲     Critical user flows
        ╱      ╲
       ╱────────╲   Integration Tests (20-30%)
      ╱          ╲  API endpoints, database
     ╱────────────╲
    ╱              ╲ Unit Tests (60-70%)
   ╱────────────────╲ Business logic, utilities
```

### Distribution Target
- **Unit Tests**: 60-70% (fast, isolated, high coverage)
- **Integration Tests**: 20-30% (API + database, authentication)
- **E2E Tests**: 5-10% (critical user flows only)

---

## Test Coverage Requirements

### Backend (Python/FastAPI)
- **Overall Coverage**: 80%+ minimum
- **Critical Paths**: 100% coverage required:
  - Authentication logic (JWT, password hashing)
  - User isolation enforcement
  - Recurring task logic
  - Data validation

### Frontend (Next.js/TypeScript)
- **Overall Coverage**: 70%+ minimum
- **Critical Components**: 90%+ coverage:
  - Authentication forms (login, signup)
  - Task CRUD components
  - API client functions

### E2E (Playwright)
- **Critical Flows**: 100% coverage
  - Signup → Create Task → Logout
  - Login → Filter → Sort → Mark Complete
  - Recurring task auto-reschedule verification

---

## Testing Technologies

### Backend
- **Test Framework**: pytest
- **HTTP Testing**: httpx (async client)
- **Fixtures**: pytest fixtures for database setup
- **Mocking**: pytest-mock
- **Coverage**: pytest-cov

### Frontend
- **Unit/Component Tests**: Vitest + React Testing Library
- **E2E Tests**: Playwright
- **Mocking**: MSW (Mock Service Worker) for API mocking
- **Coverage**: Vitest built-in coverage (c8)

---

## Test Database Strategy

### Backend Testing Database
- Use **in-memory SQLite** for unit tests (fast, isolated)
- Use **PostgreSQL test instance** for integration tests (production-like)
- **Neon branching** for staging environment tests

**Database Setup Per Test:**
```python
@pytest.fixture
def test_db():
    # Create tables
    SQLModel.metadata.create_all(test_engine)
    yield
    # Drop tables
    SQLModel.metadata.drop_all(test_engine)
```

---

## Test Organization

### Backend Structure
```
backend/
├── tests/
│   ├── conftest.py              # Shared fixtures
│   ├── test_auth.py             # Authentication tests
│   ├── test_tasks_crud.py       # Task CRUD tests
│   ├── test_tasks_advanced.py   # Recurring, reminders
│   ├── test_models.py           # SQLModel validation
│   ├── test_security.py         # User isolation, XSS, SQL injection
│   ├── test_middleware.py       # JWT verification
│   └── test_utils.py            # Utility functions
└── pytest.ini
```

### Frontend Structure
```
frontend/
├── __tests__/
│   ├── components/
│   │   ├── TaskCard.test.tsx
│   │   ├── TaskForm.test.tsx
│   │   ├── LoginForm.test.tsx
│   │   └── Dashboard.test.tsx
│   ├── lib/
│   │   ├── api.test.ts
│   │   ├── auth.test.ts
│   │   └── utils.test.ts
│   └── hooks/
│       └── useTasks.test.ts
├── e2e/
│   ├── auth.spec.ts
│   ├── tasks.spec.ts
│   └── playwright.config.ts
├── vitest.config.ts
└── playwright.config.ts
```

---

## TDD Workflow with SDD

### Spec-Driven + Test-Driven Integration

**Step 1: Write Specification**
```bash
/sp.specify "User can create a task with title and description"
```

**Step 2: Write Failing Test (RED)**
```bash
/sp.red "Implement test for task creation endpoint"
```
Result: Test fails (endpoint doesn't exist yet)

**Step 3: Implement Code (GREEN)**
```bash
/sp.green "Implement POST /api/{user_id}/tasks endpoint"
```
Result: Test passes

**Step 4: Refactor (REFACTOR)**
```bash
/sp.refactor "Extract task validation into reusable function"
```
Result: Tests still pass, code is cleaner

**Step 5: Repeat**
Continue with next feature...

---

## Mandatory Test Scenarios

### Security Tests (Non-Negotiable)

#### 1. User Isolation
```python
def test_user_cannot_access_other_users_tasks():
    """User A cannot view User B's tasks"""
    user_a_token = create_test_token(user_id="user-a")

    response = client.get(
        "/api/user-b/tasks",
        headers={"Authorization": f"Bearer {user_a_token}"}
    )

    assert response.status_code == 403
    assert "permission" in response.json()["message"].lower()
```

#### 2. Token Expiry
```python
def test_expired_token_rejected():
    """Expired JWT token returns 401"""
    expired_token = create_token_with_expiry(seconds_ago=10)

    response = client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {expired_token}"}
    )

    assert response.status_code == 401
```

#### 3. SQL Injection Prevention
```python
def test_sql_injection_attempt_blocked():
    """SQL injection in task title is sanitized"""
    malicious_title = "Test'; DROP TABLE tasks; --"

    response = client.post(
        "/api/user-123/tasks",
        json={"title": malicious_title},
        headers=auth_headers
    )

    assert response.status_code == 201
    # Verify tables still exist
    assert db.execute("SELECT COUNT(*) FROM tasks").scalar() >= 0
```

### Business Logic Tests

#### 4. Recurring Task Auto-Reschedule
```python
def test_weekly_task_reschedules_correctly():
    """Completing weekly task creates new instance +7 days"""
    task = create_task(
        due_date="2026-01-03T09:00:00Z",
        is_recurring=True,
        recurrence_pattern="WEEKLY"
    )

    # Complete task
    response = client.patch(f"/api/user-123/tasks/{task.id}/complete")

    # Verify new task created with +7 days
    new_task = response.json()["new_recurring_task"]
    assert new_task["due_date"] == "2026-01-10T09:00:00Z"
```

### Validation Tests

#### 5. Input Validation
```python
def test_task_title_required():
    """Task creation fails without title"""
    response = client.post(
        "/api/user-123/tasks",
        json={"description": "Test"},
        headers=auth_headers
    )

    assert response.status_code == 400
    assert "title" in response.json()["details"]
```

---

## Test Data Management

### Test Fixtures
```python
# conftest.py
@pytest.fixture
def test_user():
    """Create test user"""
    user = User(
        id=uuid.uuid4(),
        email="test@example.com",
        password_hash=hash_password("password123"),
        name="Test User"
    )
    db.add(user)
    db.commit()
    return user

@pytest.fixture
def auth_headers(test_user):
    """Generate auth headers for test user"""
    token = create_jwt_token(test_user.id, test_user.email, test_user.name)
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def sample_task(test_user):
    """Create sample task"""
    task = Task(
        user_id=test_user.id,
        title="Test Task",
        description="Test Description",
        priority="HIGH"
    )
    db.add(task)
    db.commit()
    return task
```

---

## Performance Benchmarks

### Backend API
- **Task Creation**: < 100ms (p95)
- **Task List (20 items)**: < 200ms (p95)
- **Login**: < 300ms (p95)
- **JWT Verification**: < 10ms (p95)

### Frontend
- **Initial Load**: < 2s (FCP)
- **Task List Render**: < 100ms
- **Search Results**: < 50ms

### E2E Tests
- **Full Signup Flow**: < 5s
- **Login to Dashboard**: < 3s
- **Create Task**: < 2s

---

## Continuous Integration (CI)

### GitHub Actions Workflow
```yaml
name: Tests

on: [push, pull_request]

jobs:
  backend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
      - run: pip install -r backend/requirements.txt
      - run: pytest backend/tests --cov --cov-report=xml
      - uses: codecov/codecov-action@v3

  frontend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
      - run: npm install
      - run: npm run test -- --coverage
      - uses: codecov/codecov-action@v3

  e2e-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
      - run: npx playwright install
      - run: npm run test:e2e
```

---

## Test Reporting

### Coverage Reports
- Generate after every test run
- HTML report for local viewing
- XML report for CI integration
- Fail build if coverage < 80% (backend) or < 70% (frontend)

### Test Results
- JUnit XML format for CI
- Console output with colors (passed/failed/skipped)
- Test duration metrics
- Flaky test detection

---

## Testing Best Practices

### DO ✅
- Write tests before implementation (TDD)
- Test one thing per test
- Use descriptive test names (`test_user_cannot_access_other_users_tasks`)
- Mock external dependencies (APIs, time)
- Use fixtures for common setup
- Clean up after tests (database, files)
- Test error paths, not just happy paths
- Run tests in isolation (order-independent)

### DON'T ❌
- Write tests after implementation
- Test implementation details (test behavior, not internals)
- Share state between tests
- Use production database
- Skip security tests
- Ignore flaky tests
- Commit commented-out tests
- Mock everything (integration tests need real DB)

---

## Success Criteria

Phase 2 testing is complete when:

- ✅ 80%+ backend test coverage
- ✅ 70%+ frontend test coverage
- ✅ All security tests passing
- ✅ All E2E critical flows passing
- ✅ CI/CD pipeline green
- ✅ No flaky tests
- ✅ Performance benchmarks met
- ✅ All tests documented in specs

---

## References

- Backend Testing Spec: `@specs/testing/backend-testing.md`
- Frontend Testing Spec: `@specs/testing/frontend-testing.md`
- E2E Testing Spec: `@specs/testing/e2e-testing.md`

---

**Version**: 1.0.0
**Last Updated**: 2026-01-02
**Owner**: Phase 2 Development Team
