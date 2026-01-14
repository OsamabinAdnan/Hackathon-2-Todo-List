---
name: test-generation
description: Create comprehensive test specs first describing unit/integration/E2E scenarios using pytest (FastAPI/SQLModel) and Vitest/React Testing Library (Next.js). Cover edge cases like auth failures, recurring tasks, priorities, filters, and browser notifications. Output failing test outlines tied to features for red phase. Use when (1) Writing failing tests BEFORE implementation code (Red phase), (2) Creating comprehensive test specs for new features, (3) Covering edge cases like authentication failures, recurring tasks, priority handling, filters, and browser notifications, (4) Generating test outlines tied to features for the red phase of TDD, (5) Setting up test infrastructure with proper fixtures and test data factories, (6) Ensuring test coverage meets requirements (Backend 80%+, Frontend 70%+, E2E 100%).
---

# Test Generation Skill

Comprehensive test creation following Test-Driven Development (TDD) principles, generating failing tests before implementation code to ensure all features are properly validated.

## Core Capabilities

### 1. Test Specification Creation

Generate comprehensive test specifications before implementation:

**Backend Test Specifications (pytest):**
```python
# Example: Task CRUD Test Specification
"""
Task CRUD Test Specification
==========================

Feature: Task Creation, Reading, Updating, Deletion
Spec: @specs/features/task-crud.md

Test Categories:
1. Unit Tests: Individual functions and methods
2. Integration Tests: API endpoints with database
3. Security Tests: Authentication and authorization

Coverage Target: 80%+ overall, 100% for auth/security
"""

# Unit Test Example
def test_create_task_with_valid_data_returns_task_object():
    """
    Test that creating a task with valid data returns a proper task object.

    Given: Valid task data (title, description, user_id)
    When: Task creation function is called
    Then: Returns Task object with correct attributes
    """
    # Arrange
    valid_task_data = {
        "title": "Test Task",
        "description": "Test Description",
        "user_id": "test_user_123"
    }

    # Act
    result = create_task(valid_task_data)

    # Assert
    assert result.title == "Test Task"
    assert result.description == "Test Description"
    assert result.user_id == "test_user_123"
    assert result.completed == False
    assert result.created_at is not None

# Integration Test Example
def test_create_task_endpoint_returns_201_with_task_data(client, test_user):
    """
    Test that POST /api/{user_id}/tasks endpoint creates task and returns 201.

    Given: Authenticated user and valid task data
    When: POST request to /api/{user_id}/tasks
    Then: Returns 201 status with task data
    """
    # Arrange
    headers = {"Authorization": f"Bearer {test_user.token}"}
    task_data = {
        "title": "Integration Test Task",
        "description": "Test via API endpoint"
    }

    # Act
    response = client.post(
        f"/api/{test_user.id}/tasks",
        json=task_data,
        headers=headers
    )

    # Assert
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Integration Test Task"
    assert "id" in data
    assert data["user_id"] == test_user.id
```

**Frontend Test Specifications (Vitest):**
```typescript
// Example: TaskList Component Test Specification
/**
 * TaskList Component Test Specification
 * ================================
 *
 * Feature: Display and interact with user tasks
 * Spec: @specs/ui/design-system.md
 *
 * Test Categories:
 * 1. Component Tests: Rendering and user interactions
 * 2. Hook Tests: Custom React hooks behavior
 * 3. Utility Tests: Helper functions and formatters
 *
 * Coverage Target: 70%+ overall, 90%+ for critical components
 */

import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { TaskList } from './TaskList';

describe('TaskList Component', () => {
  it('should render empty state when no tasks exist', () => {
    /**
     * Given: Empty tasks array
     * When: Component is rendered
     * Then: Shows "No tasks" message
     */
    // Arrange
    const emptyTasks = [];

    // Act
    render(<TaskList tasks={emptyTasks} />);

    // Assert
    expect(screen.getByText(/no tasks/i)).toBeInTheDocument();
  });

  it('should render tasks when tasks exist', () => {
    /**
     * Given: Array with tasks
     * When: Component is rendered
     * Then: Shows task items
     */
    // Arrange
    const tasks = [
      { id: '1', title: 'Test Task 1', completed: false },
      { id: '2', title: 'Test Task 2', completed: true }
    ];

    // Act
    render(<TaskList tasks={tasks} />);

    // Assert
    expect(screen.getByText('Test Task 1')).toBeInTheDocument();
    expect(screen.getByText('Test Task 2')).toBeInTheDocument();
  });
});
```

### 2. Edge Case Coverage

Generate tests for complex edge cases:

**Authentication Edge Cases:**
```python
def test_create_task_with_invalid_token_returns_401():
    """
    Test that creating a task with invalid token returns 401.

    Given: Invalid JWT token
    When: POST request to /api/{user_id}/tasks
    Then: Returns 401 Unauthorized
    """
    # Arrange
    headers = {"Authorization": "Bearer invalid_token_123"}
    task_data = {"title": "Unauthorized Task"}

    # Act
    response = client.post(
        "/api/test_user/tasks",
        json=task_data,
        headers=headers
    )

    # Assert
    assert response.status_code == 401

def test_create_task_with_expired_token_returns_401():
    """
    Test that creating a task with expired token returns 401.

    Given: Expired JWT token
    When: POST request to /api/{user_id}/tasks
    Then: Returns 401 Unauthorized
    """
    # Arrange
    expired_token = create_expired_token()
    headers = {"Authorization": f"Bearer {expired_token}"}
    task_data = {"title": "Expired Token Task"}

    # Act
    response = client.post(
        "/api/test_user/tasks",
        json=task_data,
        headers=headers
    )

    # Assert
    assert response.status_code == 401

def test_user_cannot_access_other_users_tasks():
    """
    Test that user cannot access tasks belonging to other users.

    Given: User A's token and User B's task ID
    When: GET request to /api/{user_b_id}/tasks/{task_id}
    Then: Returns 404 or 403 Forbidden
    """
    # Arrange
    user_a_token = get_user_a_token()
    user_b_task_id = get_user_b_task_id()
    headers = {"Authorization": f"Bearer {user_a_token}"}

    # Act
    response = client.get(
        f"/api/users/{user_b_id}/tasks/{user_b_task_id}",
        headers=headers
    )

    # Assert
    assert response.status_code in [403, 404]
```

**Recurring Task Edge Cases:**
```python
def test_recurring_task_handles_leap_year_edge_case():
    """
    Test that recurring tasks handle February 29th correctly.

    Given: Recurring task set for Feb 29th with yearly recurrence
    When: Task evaluation reaches non-leap year
    Then: Task is scheduled for Feb 28th or Mar 1st (business rule)
    """
    # Arrange
    recurring_task = create_recurring_task(
        title="Annual Checkup",
        due_date=datetime(2024, 2, 29),  # Leap year date
        recurrence_pattern="YEARLY"
    )

    # Act
    next_occurrence = calculate_next_occurrence(recurring_task, datetime(2025, 1, 1))

    # Assert
    # Business rule: Should handle leap year edge case appropriately
    assert next_occurrence.month in [2, 3]  # Either Feb 28th or Mar 1st
    assert next_occurrence.day in [28, 1]

def test_recurring_task_handles_month_end_edge_case():
    """
    Test that recurring tasks handle month-end dates correctly.

    Given: Recurring task set for Jan 31st with monthly recurrence
    When: Task evaluation reaches Feb (which has 28/29 days)
    Then: Task is scheduled for last day of month (Feb 28th/29th)
    """
    # Arrange
    recurring_task = create_recurring_task(
        title="Monthly Review",
        due_date=datetime(2024, 1, 31),  # Month with 31 days
        recurrence_pattern="MONTHLY"
    )

    # Act
    next_occurrence = calculate_next_occurrence(recurring_task, datetime(2024, 2, 1))

    # Assert
    assert next_occurrence.month == 2
    assert next_occurrence.day in [28, 29]  # Last day of February
```

### 3. Priority and Filter Test Cases

**Priority Handling Tests:**
```python
def test_tasks_filtered_by_priority_returns_correct_tasks():
    """
    Test that filtering tasks by priority returns only matching tasks.

    Given: Tasks with different priorities (HIGH, MEDIUM, LOW, NONE)
    When: GET request with priority filter
    Then: Returns only tasks with specified priority
    """
    # Arrange
    create_test_tasks_with_priorities()
    headers = {"Authorization": f"Bearer {test_user.token}"}

    # Act
    response = client.get(
        "/api/test_user/tasks?priority=HIGH",
        headers=headers
    )

    # Assert
    tasks = response.json()
    for task in tasks:
        assert task["priority"] == "HIGH"

def test_tasks_sorted_by_priority_returns_correct_order():
    """
    Test that sorting tasks by priority returns them in correct order.

    Given: Tasks with different priorities
    When: GET request with priority sort
    Then: Returns tasks in priority order (HIGH > MEDIUM > LOW > NONE)
    """
    # Arrange
    create_test_tasks_with_priorities()
    headers = {"Authorization": f"Bearer {test_user.token}"}

    # Act
    response = client.get(
        "/api/test_user/tasks?sort=priority",
        headers=headers
    )

    # Assert
    tasks = response.json()
    priorities_order = [task["priority"] for task in tasks]
    expected_order = ["HIGH", "MEDIUM", "LOW", "NONE"]  # Or whatever business rule
    assert is_correct_priority_order(priorities_order, expected_order)
```

### 4. E2E Test Generation

**Playwright E2E Tests:**
```typescript
import { test, expect } from '@playwright/test';

test.describe('Task Management E2E Tests', () => {
  test('user can create, view, update, and delete a task', async ({ page }) => {
    /**
     * Critical User Flow: Complete task lifecycle
     * Given: Authenticated user on dashboard
     * When: User performs full task CRUD operations
     * Then: All operations succeed and UI updates correctly
     */

    // 1. Setup: Login
    await page.goto('/login');
    await page.fill('[data-testid="email"]', 'test@example.com');
    await page.fill('[data-testid="password"]', 'password123');
    await page.click('[data-testid="login-button"]');

    // 2. Action: Create task
    await page.fill('[data-testid="task-title-input"]', 'E2E Test Task');
    await page.fill('[data-testid="task-description-input"]', 'Test description');
    await page.click('[data-testid="create-task-button"]');

    // 3. Verification: Task appears in list
    await expect(page.locator('text="E2E Test Task"')).toBeVisible();

    // 4. Action: Update task
    await page.click('[data-testid="edit-task-button"]');
    await page.fill('[data-testid="task-title-input"]', 'Updated E2E Task');
    await page.click('[data-testid="save-task-button"]');

    // 5. Verification: Task updated
    await expect(page.locator('text="Updated E2E Task"')).toBeVisible();

    // 6. Action: Delete task
    await page.click('[data-testid="delete-task-button"]');

    // 7. Verification: Task removed
    await expect(page.locator('text="Updated E2E Task"')).not.toBeVisible();
  });

  test('browser notifications work for due soon tasks', async ({ page, context }) => {
    /**
     * Feature: Browser notifications for due soon tasks
     * Given: Task with due date within 60 minutes
     * When: Time approaches due date
     * Then: Browser notification appears
     */

    // Enable notifications permission
    await context.grantPermissions(['notifications']);

    // Create task with near-future due date
    await page.goto('/tasks');
    await page.fill('[data-testid="task-title-input"]', 'Due Soon Task');
    await page.fill('[data-testid="due-date-input"]', getNearFutureDate());
    await page.click('[data-testid="create-task-button"]');

    // Wait and verify notification appears
    const notificationPromise = page.waitForEvent('notification');
    // Additional logic to verify notification behavior
  });
});
```

### 5. Test Data Factory Generation

**Backend Test Factories:**
```python
# backend/tests/factories.py
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import uuid

def create_test_user(**overrides) -> Dict[str, Any]:
    """Factory for creating test users with sensible defaults."""
    defaults = {
        "id": f"test_user_{uuid.uuid4()}",
        "email": f"test_{uuid.uuid4()}@example.com",
        "name": "Test User",
        "created_at": datetime.utcnow()
    }
    return {**defaults, **overrides}

def create_test_task(**overrides) -> Dict[str, Any]:
    """Factory for creating test tasks with sensible defaults."""
    defaults = {
        "id": f"test_task_{uuid.uuid4()}",
        "title": "Test Task",
        "description": "Test Description",
        "completed": False,
        "priority": "MEDIUM",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    return {**defaults, **overrides}

def create_test_token(user_id: str, **overrides) -> str:
    """Factory for creating valid test JWT tokens."""
    import jwt
    from datetime import datetime, timedelta

    payload = {
        "user_id": user_id,
        "exp": datetime.utcnow() + timedelta(hours=1),
        "iat": datetime.utcnow()
    }
    payload.update(overrides)

    return jwt.encode(payload, "test_secret", algorithm="HS256")

def create_recurring_task(**overrides) -> Dict[str, Any]:
    """Factory for creating recurring test tasks."""
    defaults = {
        "id": f"test_recurring_{uuid.uuid4()}",
        "title": "Recurring Test Task",
        "recurrence_pattern": "DAILY",  # DAILY, WEEKLY, MONTHLY
        "next_occurrence": datetime.utcnow() + timedelta(days=1)
    }
    return {**defaults, **overrides}
```

**Frontend Test Utilities:**
```typescript
// frontend/tests/utils.ts
import { render } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

// Create a test query client
const createTestQueryClient = () => new QueryClient({
  defaultOptions: {
    queries: {
      retry: false,
      cacheTime: 0
    }
  }
});

// Custom render function with providers
export const renderWithProviders = (ui: React.ReactElement, options = {}) => {
  const testQueryClient = createTestQueryClient();

  const Wrapper: React.FC<{ children: React.ReactNode }> = ({ children }) => (
    <QueryClientProvider client={testQueryClient}>
      <BrowserRouter>
        {children}
      </BrowserRouter>
    </QueryClientProvider>
  );

  return render(ui, { wrapper: Wrapper, ...options });
};

// Mock data factories
export const createMockTask = (overrides = {}) => ({
  id: `mock-task-${Date.now()}`,
  title: 'Mock Task',
  description: 'Mock Description',
  completed: false,
  priority: 'MEDIUM',
  created_at: new Date().toISOString(),
  updated_at: new Date().toISOString(),
  ...overrides
});

export const createMockUser = (overrides = {}) => ({
  id: `mock-user-${Date.now()}`,
  email: 'mock@example.com',
  name: 'Mock User',
  ...overrides
});
```

### 6. Coverage-Driven Test Generation

**Coverage Analysis Integration:**
```python
def generate_tests_for_uncovered_code():
    """
    Analyze coverage reports and generate tests for uncovered code paths.

    This function analyzes coverage data to identify:
    - Uncovered lines of code
    - Missing branch coverage
    - Untested edge cases
    - Error path coverage gaps
    """
    # This would typically integrate with coverage tools like coverage.py
    uncovered_paths = analyze_coverage_gaps()

    for path in uncovered_paths:
        if path.type == "error_path":
            yield generate_error_path_test(path)
        elif path.type == "branch":
            yield generate_branch_coverage_test(path)
        elif path.type == "edge_case":
            yield generate_edge_case_test(path)

def generate_security_tests_from_auth_spec():
    """
    Generate security tests based on authentication specification.

    Reads @specs/features/authentication.md to create targeted security tests.
    """
    auth_spec = read_spec_file("@specs/features/authentication.md")

    tests = []
    if "JWT" in auth_spec:
        tests.append(generate_jwt_security_tests())
    if "user_isolation" in auth_spec:
        tests.append(generate_user_isolation_tests())
    if "rate_limiting" in auth_spec:
        tests.append(generate_rate_limiting_tests())

    return tests
```

### 7. Red Phase Test Outlines

**Failing Test Templates:**
```python
def create_red_phase_test_outline(feature_spec_path: str):
    """
    Create a failing test outline tied to a specific feature for red phase.

    Args:
        feature_spec_path: Path to feature specification file

    Returns:
        String containing test outline ready for red phase
    """
    spec_content = read_spec_file(feature_spec_path)

    outline = f"""
# Red Phase Test Outline for: {feature_spec_path}

## Feature Requirements:
{extract_requirements_from_spec(spec_content)}

## Test Cases to Implement:

### Unit Tests:
1. test_{generate_test_name_from_spec(spec_content)}_returns_expected_result()
   - Arrange: [setup required objects]
   - Act: [execute function under test]
   - Assert: [verify expected behavior]
   - Expected: Test should FAIL initially

2. test_{generate_test_name_from_spec(spec_content)}_handles_edge_case()
   - Test edge case scenarios
   - Expected: Test should FAIL initially

### Integration Tests:
1. test_api_endpoint_{generate_endpoint_from_spec(spec_content)}_returns_correct_response()
   - Test API endpoint behavior
   - Expected: Test should FAIL initially

### Security Tests:
1. test_{generate_security_test_name_from_spec(spec_content)}_prevents_unauthorized_access()
   - Test security requirements
   - Expected: Test should FAIL initially

## Implementation Notes:
- Do NOT implement the feature yet
- Focus on defining what success looks like
- Ensure tests fail for the RIGHT reasons (not syntax errors)
- Verify tests align with specification requirements

## Next Steps:
1. Write the failing tests
2. Verify they fail appropriately
3. Move to green phase only after tests are properly failing
"""
    return outline
```

## Usage Examples

### Example 1: Red Phase for Task Creation
```
User: "@specs/features/task-crud.md generate failing tests for task creation"
Agent: [Triggers test-generation skill] → Creates comprehensive test suite with 15+ failing tests covering validation, authentication, edge cases, and security requirements; all tests fail appropriately with clear error messages
```

### Example 2: E2E Test Generation
```
User: "Generate E2E tests for the complete task management flow"
Agent: [Triggers test-generation skill] → Creates Playwright tests covering signup, login, task CRUD, filtering, and logout with proper page object patterns and error handling
```

### Example 3: Security Test Generation
```
User: "@specs/features/authentication.md generate security tests for user isolation"
Agent: [Triggers test-generation skill] → Creates tests verifying users cannot access other users' tasks, with proper authentication bypass attempts and edge cases
```

## Quality Checklist

- [ ] All tests follow Arrange-Act-Assert pattern
- [ ] Test names clearly describe expected behavior
- [ ] Edge cases and error paths are covered
- [ ] Tests are isolated and repeatable
- [ ] Coverage targets are met (Backend 80%+, Frontend 70%+, E2E 100%)
- [ ] Security-critical code has 100% coverage
- [ ] Tests fail for the right reasons (not syntax errors)
- [ ] Test data uses factories/fixtures appropriately
- [ ] Tests are written BEFORE implementation code (Red phase)
- [ ] Tests align with feature specifications
- [ ] Error handling paths are tested
- [ ] Authentication and authorization are tested
- [ ] User isolation is verified
- [ ] Performance edge cases are considered

## Integration Points

- **TDD Workflow**: Integrates with Red-Green-Refactor cycle
- **Spec-Driven Development**: Aligns with feature specifications
- **Test Infrastructure**: Sets up pytest, Vitest, and Playwright configurations
- **Coverage Tools**: Integrates with coverage.py, Istanbul, etc.
- **CI/CD Pipeline**: Automated test generation and execution
- **Code Review**: Provides test quality standards for review

## References

- **Backend Testing Spec**: `@specs/testing/backend-testing.md` for pytest requirements
- **Frontend Testing Spec**: `@specs/testing/frontend-testing.md` for Vitest patterns
- **E2E Testing Spec**: `@specs/testing/e2e-testing.md` for Playwright flows
- **Feature Specifications**: `@specs/features/task-crud.md` for requirements
- **API Specifications**: `@specs/api/rest-endpoints.md` for endpoint tests
- **Security Specifications**: `@specs/features/authentication.md` for auth tests
- **UI Component Specs**: `@specs/ui/design-system.md` for component tests