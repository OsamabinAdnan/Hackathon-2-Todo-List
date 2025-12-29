---
name: in-memory-state-validation
description: Confirm task state changes correctly in runtime using pytest. Use this skill when testing state isolation between tests, singleton behavior, state persistence within sessions, and proper cleanup. Ensures the in-memory storage behaves correctly throughout application lifecycle.
---

# In-Memory State Validation

Pytest patterns for validating in-memory state management and lifecycle.

## Overview

This skill provides comprehensive test templates for:
- **State Isolation**: Tests don't affect each other
- **Singleton Behavior**: Single service instance per session
- **State Persistence**: Data persists within session
- **State Cleanup**: Proper reset between tests
- **Concurrent Access**: Thread-safety patterns

## Test File Structure

```
tests/
    unit/
        test_state.py           # State management tests
        test_isolation.py       # Test isolation tests
    integration/
        test_state_lifecycle.py # Full lifecycle tests
    conftest.py                 # State fixtures
```

## Critical: Test Isolation Fixtures

```python
# tests/conftest.py
"""
Critical fixtures for state isolation.

These fixtures MUST be used to prevent test pollution.
"""

import pytest
from todo.state import reset_state, get_state
from todo.context import AppContext
from todo.services.task_service import TaskService


@pytest.fixture(autouse=True)
def isolate_state():
    """
    Automatically reset state before and after each test.

    This fixture runs for EVERY test automatically (autouse=True).
    Ensures complete isolation between tests.

    WARNING: Do not remove this fixture or tests will pollute each other.
    """
    # Setup: Clean slate
    reset_state()
    AppContext.reset()

    yield

    # Teardown: Clean up
    reset_state()
    AppContext.reset()


@pytest.fixture
def fresh_service():
    """
    Provide explicitly fresh TaskService.

    Use when test needs guaranteed new instance.
    """
    return TaskService()


@pytest.fixture
def global_service():
    """
    Provide the global singleton service.

    Use when testing singleton behavior.
    """
    from todo.state import get_service
    return get_service()
```

## State Isolation Tests

```python
# tests/unit/test_isolation.py
"""
Tests verifying test isolation works correctly.

These tests verify the test infrastructure itself.
"""

import pytest


class TestIsolationBetweenTests:
    """Verify tests don't affect each other."""

    def test_isolation_part1_add_tasks(self, fresh_service):
        """
        Part 1: Add tasks.

        This test adds tasks. Part 2 should NOT see them.
        """
        fresh_service.add_task("Task from part 1")
        fresh_service.add_task("Another task from part 1")

        assert len(fresh_service.get_all_tasks()) == 2

    def test_isolation_part2_empty_state(self, fresh_service):
        """
        Part 2: Verify empty state.

        This test runs after part 1. State should be empty.
        """
        # If isolation works, this is empty
        tasks = fresh_service.get_all_tasks()
        assert len(tasks) == 0

    def test_isolation_part3_independent(self, fresh_service):
        """
        Part 3: Independent test.

        Should have clean state regardless of test order.
        """
        fresh_service.add_task("Independent task")

        assert len(fresh_service.get_all_tasks()) == 1


class TestFixtureIsolation:
    """Verify fixture-created data is isolated."""

    @pytest.fixture
    def populated_service(self, fresh_service):
        """Service with test data."""
        fresh_service.add_task("Fixture task 1")
        fresh_service.add_task("Fixture task 2")
        return fresh_service

    def test_fixture_data_exists(self, populated_service):
        """Fixture creates expected data."""
        assert len(populated_service.get_all_tasks()) == 2

    def test_other_test_no_fixture_data(self, fresh_service):
        """Other test doesn't see fixture data."""
        # This test uses fresh_service, not populated_service
        assert len(fresh_service.get_all_tasks()) == 0
```

## State Persistence Tests

```python
# tests/unit/test_state.py
"""Tests for state management behavior."""

import pytest
from todo.services.task_service import TaskService


class TestStatePersistenceWithinSession:
    """State persists within a single test/session."""

    def test_added_task_persists(self, fresh_service):
        """Task added is retrievable."""
        task = fresh_service.add_task("Persistent task")

        # Should be able to get it back
        retrieved = fresh_service.get_task(task.id)
        assert retrieved.title == "Persistent task"

    def test_multiple_operations_persist(self, fresh_service):
        """Multiple operations accumulate correctly."""
        # Add tasks
        t1 = fresh_service.add_task("Task 1")
        t2 = fresh_service.add_task("Task 2")
        t3 = fresh_service.add_task("Task 3")

        # Modify some
        fresh_service.mark_complete(t1.id)
        fresh_service.update_task(t2.id, title="Updated Task 2")

        # Delete one
        fresh_service.delete_task(t3.id)

        # Verify final state
        tasks = fresh_service.get_all_tasks()
        assert len(tasks) == 2

        task1 = fresh_service.get_task(t1.id)
        assert task1.completed is True

        task2 = fresh_service.get_task(t2.id)
        assert task2.title == "Updated Task 2"

    def test_state_survives_operations(self, fresh_service):
        """State survives various operation sequences."""
        from todo.models.enums import Priority

        # Complex sequence
        task = fresh_service.add_task("Complex task")
        fresh_service.set_priority(task.id, Priority.HIGH)
        fresh_service.add_tag(task.id, "important")
        fresh_service.add_tag(task.id, "work")
        fresh_service.update_task(task.id, description="Details")

        # All changes persist
        final = fresh_service.get_task(task.id)
        assert final.priority == Priority.HIGH
        assert set(final.tags) == {"important", "work"}
        assert final.description == "Details"
```

## Singleton Behavior Tests

```python
# tests/unit/test_singleton.py
"""Tests for singleton service behavior."""

import pytest


class TestSingletonPattern:
    """Verify singleton provides same instance."""

    def test_get_service_returns_same_instance(self):
        """Multiple calls return same instance."""
        from todo.state import get_service

        service1 = get_service()
        service2 = get_service()

        assert service1 is service2

    def test_singleton_shares_state(self):
        """Changes via singleton visible everywhere."""
        from todo.state import get_service

        service1 = get_service()
        task = service1.add_task("Singleton task")

        service2 = get_service()
        retrieved = service2.get_task(task.id)

        assert retrieved.title == "Singleton task"

    def test_reset_clears_singleton(self):
        """Reset creates new instance."""
        from todo.state import get_service, reset_service

        service1 = get_service()
        service1.add_task("Before reset")

        reset_service()

        service2 = get_service()
        assert len(service2.get_all_tasks()) == 0
        assert service1 is not service2


class TestAppContextSingleton:
    """Verify AppContext singleton behavior."""

    def test_context_get_returns_same_instance(self):
        """Multiple get() calls return same context."""
        from todo.context import AppContext

        ctx1 = AppContext.get()
        ctx2 = AppContext.get()

        assert ctx1 is ctx2

    def test_context_shares_service(self):
        """Context provides shared service."""
        from todo.context import AppContext

        ctx1 = AppContext.get()
        task = ctx1.task_service.add_task("Context task")

        ctx2 = AppContext.get()
        retrieved = ctx2.task_service.get_task(task.id)

        assert retrieved.title == "Context task"

    def test_context_reset_clears_state(self):
        """Context reset clears everything."""
        from todo.context import AppContext

        ctx1 = AppContext.get()
        ctx1.task_service.add_task("Before reset")

        AppContext.reset()

        ctx2 = AppContext.get()
        assert len(ctx2.task_service.get_all_tasks()) == 0
```

## State Lifecycle Tests

```python
# tests/integration/test_state_lifecycle.py
"""Tests for complete state lifecycle."""

import pytest


class TestStateInitialization:
    """Tests for state initialization."""

    def test_initial_state_is_empty(self, fresh_service):
        """Fresh service starts with no tasks."""
        assert len(fresh_service.get_all_tasks()) == 0

    def test_state_initializes_on_first_access(self):
        """State created lazily on first access."""
        from todo.state import get_state, reset_state

        reset_state()

        # First access creates state
        state = get_state()
        assert state is not None
        assert state.is_initialized is True


class TestStateCleanup:
    """Tests for state cleanup."""

    def test_reset_removes_all_tasks(self, fresh_service):
        """Reset clears all tasks."""
        from todo.state import reset_state

        fresh_service.add_task("Task 1")
        fresh_service.add_task("Task 2")
        assert len(fresh_service.get_all_tasks()) == 2

        reset_state()

        # Need new service after reset
        from todo.state import get_service
        new_service = get_service()
        assert len(new_service.get_all_tasks()) == 0

    def test_cleanup_runs_callbacks(self):
        """Cleanup triggers registered callbacks."""
        from todo.state import AppState

        cleanup_called = []

        state = AppState()
        state.on_cleanup(lambda: cleanup_called.append(True))
        state.initialize()

        state.cleanup()

        assert len(cleanup_called) == 1


class TestStateWithContextManager:
    """Tests for context manager usage."""

    def test_context_manager_provides_state(self):
        """Context manager provides usable state."""
        from todo.context import AppContext
        from todo.services.task_service import TaskService

        with AppContext(task_service=TaskService()) as ctx:
            task = ctx.task_service.add_task("In context")
            assert task.title == "In context"

    def test_context_manager_cleans_up(self):
        """Context manager resets on exit."""
        from todo.context import AppContext
        from todo.services.task_service import TaskService

        with AppContext(task_service=TaskService()) as ctx:
            ctx.task_service.add_task("Temporary")

        # After context, should be reset
        # New context should be empty
        new_ctx = AppContext.get()
        # Note: Behavior depends on implementation
```

## Testing with Mocked State

```python
# tests/unit/test_mock_state.py
"""Tests using mocked state for isolation."""

import pytest
from unittest.mock import Mock, MagicMock


class TestWithMockedService:
    """Tests using mocked TaskService."""

    @pytest.fixture
    def mock_service(self):
        """Provide mock TaskService."""
        from todo.models.task import Task

        service = Mock()
        service.add_task.return_value = Task(title="Mock Task")
        service.get_all_tasks.return_value = []
        return service

    def test_cli_uses_injected_service(self, mock_service):
        """CLI can use injected mock service."""
        from todo.context import AppContext

        with AppContext(task_service=mock_service):
            ctx = AppContext.get()
            ctx.task_service.add_task("Test")

        mock_service.add_task.assert_called_once_with("Test")

    def test_mock_controls_return_values(self, mock_service):
        """Mock can control what service returns."""
        from todo.models.task import Task

        mock_service.get_all_tasks.return_value = [
            Task(title="Mock 1"),
            Task(title="Mock 2"),
        ]

        result = mock_service.get_all_tasks()
        assert len(result) == 2


class TestWithSpyService:
    """Tests using spy on real service."""

    def test_spy_tracks_calls(self, fresh_service, mocker):
        """Spy tracks method calls on real service."""
        mocker.spy(fresh_service, 'add_task')

        fresh_service.add_task("Spied task")

        assert fresh_service.add_task.call_count == 1

    def test_spy_real_behavior_preserved(self, fresh_service, mocker):
        """Spy doesn't change actual behavior."""
        mocker.spy(fresh_service, 'add_task')

        task = fresh_service.add_task("Real task")

        # Real task created
        assert task.title == "Real task"
        # And call tracked
        assert fresh_service.add_task.called
```

## TUI State Validation Patterns

### Testing State in TUI Context

```python
# tests/tui/test_tui_state.py
"""Tests for state management in TUI context."""

import pytest
from textual.testing import AppTester
from todo.tui.app import TodoApp
from todo.context import AppContext


@pytest.fixture
async def app_tester(task_service):
    """TUI app tester with fresh state."""
    app = TodoApp(task_service=task_service)
    async with AppTester.run_test(app) as tester:
        yield tester


class TestTUIStateIsolation:
    """Verify state isolation in TUI tests."""

    async def test_app_state_isolated_part1(self, app_tester):
        """Part 1: Add tasks via TUI."""
        await app_tester.press("a")
        await app_tester.type("Task from test 1")
        await app_tester.press("enter")

        tasks = app_tester.app.task_service.get_all_tasks()
        assert len(tasks) == 1

    async def test_app_state_isolated_part2(self, app_tester):
        """Part 2: State should be clean (no tasks from part 1)."""
        tasks = app_tester.app.task_service.get_all_tasks()
        assert len(tasks) == 0


class TestTUIReactiveState:
    """Verify reactive state updates in TUI."""

    async def test_reactive_task_count(self, app_tester):
        """Reactive task count updates correctly."""
        assert app_tester.app.task_count == 0

        await app_tester.press("a")
        await app_tester.type("New task")
        await app_tester.press("enter")

        # Reactive attribute should update
        assert app_tester.app.task_count == 1

    async def test_reactive_update_on_delete(self, app_tester, sample_task):
        """Reactive updates when task deleted."""
        initial = len(app_tester.app.query("TaskItem"))

        await app_tester.press("d")
        await app_tester.press("enter")  # Confirm delete

        final = len(app_tester.app.query("TaskItem"))
        assert final == initial - 1


class TestTUIStatePersistence:
    """Verify state persists within TUI session."""

    async def test_state_persists_across_screens(self, app_tester):
        """State persists when navigating screens."""
        # Add task
        await app_tester.press("a")
        await app_tester.type("Persistent task")
        await app_tester.press("enter")

        # Open help screen
        await app_tester.press("?")

        # Return to main
        await app_tester.press("escape")

        # Task should still exist
        tasks = app_tester.app.task_service.get_all_tasks()
        assert len(tasks) == 1

    async def test_state_persists_after_modal(self, app_tester):
        """State persists after modal interactions."""
        # Add first task
        await app_tester.press("a")
        await app_tester.type("Task 1")
        await app_tester.press("enter")

        # Open and cancel add modal
        await app_tester.press("a")
        await app_tester.press("escape")

        # First task still exists
        tasks = app_tester.app.task_service.get_all_tasks()
        assert len(tasks) == 1


class TestTUIServiceInjection:
    """Verify service injection works in TUI."""

    async def test_mock_service_injection(self, mock_service):
        """Mock service can be injected into TUI."""
        from todo.models.task import Task

        mock_service.get_all_tasks.return_value = [
            Task(title="Mock Task 1"),
            Task(title="Mock Task 2"),
        ]

        app = TodoApp(task_service=mock_service)
        async with AppTester.run_test(app) as tester:
            # TUI should use mock service
            tasks = tester.app.task_service.get_all_tasks()
            assert len(tasks) == 2

    async def test_context_service_shared(self, task_service):
        """AppContext service shared with TUI."""
        # Add task via context
        task_service.add_task("Context task")

        # TUI should see it
        app = TodoApp(task_service=task_service)
        async with AppTester.run_test(app) as tester:
            tasks = tester.app.task_service.get_all_tasks()
            assert len(tasks) == 1
```

## Running Tests

```bash
# Run all state validation tests
uv run pytest tests/unit/test_state.py tests/unit/test_isolation.py -v

# Run TUI state tests
uv run pytest tests/tui/test_tui_state.py -v

# Run with verbose state debugging
uv run pytest tests/unit/test_state.py -v -s

# Run isolation tests to verify infrastructure
uv run pytest tests/unit/test_isolation.py -v

# Run full lifecycle tests
uv run pytest tests/integration/test_state_lifecycle.py -v

# Check for test pollution (run multiple times)
uv run pytest tests/ --count=3 -v
```

## Common State Issues

### Issue 1: Tests Affecting Each Other

```python
# BAD - State leaks between tests
class TestBad:
    service = TaskService()  # Shared!

    def test_one(self):
        self.service.add_task("Leaks!")

    def test_two(self):
        # Sees task from test_one!
        ...

# GOOD - Fresh state per test
class TestGood:
    def test_one(self, fresh_service):
        fresh_service.add_task("Isolated")

    def test_two(self, fresh_service):
        # Guaranteed empty
        assert len(fresh_service.get_all_tasks()) == 0
```

### Issue 2: Forgetting to Reset Singleton

```python
# BAD - Singleton not reset
def test_modifies_singleton():
    service = get_service()
    service.add_task("Persists!")
    # No reset - affects next test

# GOOD - Use autouse fixture
@pytest.fixture(autouse=True)
def reset_between_tests():
    reset_state()
    yield
    reset_state()
```

## Checklist

Before considering state validation tests complete:
- [ ] Test isolation verified (autouse fixture)
- [ ] State persistence within session tested
- [ ] Singleton behavior verified
- [ ] Reset/cleanup verified
- [ ] Context manager tested
- [ ] Mock injection tested
- [ ] No test pollution (verified with --count)
- [ ] Lifecycle hooks tested
