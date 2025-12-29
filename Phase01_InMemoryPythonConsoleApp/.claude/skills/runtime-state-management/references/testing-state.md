# Testing State Management

Patterns for testing applications with in-memory state.

## Table of Contents

1. [Fixtures](#fixtures)
2. [Isolation Patterns](#isolation-patterns)
3. [Mocking State](#mocking-state)
4. [CLI Testing](#cli-testing)
5. [Common Pitfalls](#common-pitfalls)

## Fixtures

### Auto-Reset Fixture

```python
# tests/conftest.py
import pytest
from todo.state import reset_state, get_state
from todo.context import AppContext


@pytest.fixture(autouse=True)
def isolate_state():
    """
    Automatically reset state before and after each test.

    This fixture runs for EVERY test, ensuring complete isolation.
    """
    # Setup: Reset any existing state
    reset_state()
    AppContext.reset()

    yield

    # Teardown: Clean up after test
    reset_state()
    AppContext.reset()
```

### Explicit State Fixture

```python
@pytest.fixture
def app_state():
    """
    Provide a fresh, initialized AppState.

    Use when tests need explicit access to state object.
    """
    from todo.state import AppState

    state = AppState()
    state.initialize()

    yield state

    state.cleanup()


@pytest.fixture
def task_service():
    """Provide isolated TaskService instance."""
    from todo.services.task_service import TaskService

    return TaskService()
```

### Pre-populated State

```python
@pytest.fixture
def state_with_tasks(app_state):
    """State pre-populated with sample tasks."""
    service = app_state.task_service

    service.add_task("Task 1", "Description 1")
    service.add_task("Task 2", "Description 2")
    service.add_task("Task 3", "Description 3")

    return app_state


@pytest.fixture
def diverse_tasks(task_service):
    """TaskService with diverse task types."""
    from todo.models.enums import Priority

    # High priority
    t1 = task_service.add_task("Urgent task")
    task_service.set_priority(t1.id, Priority.HIGH)

    # Completed
    t2 = task_service.add_task("Done task")
    task_service.mark_complete(t2.id)

    # With tags
    t3 = task_service.add_task("Tagged task")
    task_service.add_tag(t3.id, "work")

    return task_service
```

## Isolation Patterns

### Pattern 1: Module-Level Reset

```python
# tests/unit/test_task_service.py
import pytest
from todo.state import reset_state


@pytest.fixture(autouse=True)
def reset_module_state():
    """Reset state for this test module."""
    reset_state()
    yield
    reset_state()


class TestTaskService:
    def test_add_task(self, task_service):
        task = task_service.add_task("Test")
        assert task.title == "Test"

    def test_tasks_isolated(self, task_service):
        # This test gets fresh service, not affected by previous test
        assert task_service.get_all_tasks() == []
```

### Pattern 2: Context Manager Isolation

```python
from todo.context import AppContext


def test_with_isolated_context():
    """Test with completely isolated context."""
    from todo.services.task_service import TaskService

    # Create isolated context
    isolated_service = TaskService()

    with AppContext(task_service=isolated_service):
        ctx = AppContext.get()
        task = ctx.task_service.add_task("Isolated task")
        assert task.title == "Isolated task"

    # After context exits, global state is reset
    # Next test gets fresh state
```

### Pattern 3: Parametrized State

```python
@pytest.fixture(params=["empty", "with_tasks", "with_completed"])
def state_variant(request, task_service):
    """Test with different state configurations."""
    if request.param == "empty":
        pass
    elif request.param == "with_tasks":
        task_service.add_task("Task 1")
        task_service.add_task("Task 2")
    elif request.param == "with_completed":
        t = task_service.add_task("Done")
        task_service.mark_complete(t.id)

    return task_service, request.param


def test_list_behavior(state_variant):
    """Test list command with various states."""
    service, variant = state_variant

    tasks = service.get_all_tasks()

    if variant == "empty":
        assert len(tasks) == 0
    elif variant == "with_tasks":
        assert len(tasks) == 2
    elif variant == "with_completed":
        assert len(tasks) == 1
        assert tasks[0].completed is True
```

## Mocking State

### Mock TaskService

```python
import pytest
from unittest.mock import Mock, MagicMock
from todo.models.task import Task


@pytest.fixture
def mock_service():
    """Create mock TaskService."""
    service = Mock()

    # Configure return values
    service.add_task.return_value = Task(title="Mock Task")
    service.get_all_tasks.return_value = []
    service.get_task.return_value = Task(title="Found Task")

    return service


def test_add_calls_service(mock_service):
    """Verify service method is called correctly."""
    from todo.context import AppContext

    with AppContext(task_service=mock_service):
        ctx = AppContext.get()
        ctx.task_service.add_task("New task", "Description")

    mock_service.add_task.assert_called_once_with("New task", "Description")
```

### Mock with Side Effects

```python
@pytest.fixture
def service_with_errors():
    """Mock service that raises errors."""
    from todo.models.exceptions import TaskNotFoundError

    service = Mock()
    service.get_task.side_effect = TaskNotFoundError("not-found")
    service.delete_task.side_effect = TaskNotFoundError("not-found")

    return service


def test_handles_not_found(service_with_errors):
    """Test error handling when task not found."""
    from todo.context import AppContext
    from todo.models.exceptions import TaskNotFoundError

    with AppContext(task_service=service_with_errors):
        ctx = AppContext.get()

        with pytest.raises(TaskNotFoundError):
            ctx.task_service.get_task("fake-id")
```

### Spy Pattern

```python
@pytest.fixture
def spy_service(task_service, mocker):
    """Spy on real service methods."""
    mocker.spy(task_service, "add_task")
    mocker.spy(task_service, "delete_task")
    return task_service


def test_tracks_calls(spy_service):
    """Verify real methods are called."""
    task = spy_service.add_task("Test")

    assert spy_service.add_task.call_count == 1
    assert task.title == "Test"  # Real task created
```

## CLI Testing

### Basic CLI Test

```python
from typer.testing import CliRunner
from todo.cli.app import app

runner = CliRunner()


def test_add_command():
    """Test add command creates task."""
    result = runner.invoke(app, ["add", "Test task"])

    assert result.exit_code == 0
    assert "Created" in result.output


def test_list_empty():
    """Test list command with no tasks."""
    result = runner.invoke(app, ["list"])

    assert result.exit_code == 0
    assert "No tasks" in result.output
```

### CLI with Mock State

```python
def test_add_uses_service(mock_service):
    """Verify CLI uses injected service."""
    from todo.context import AppContext

    mock_service.add_task.return_value = Task(
        id="test-123",
        title="Test task"
    )

    with AppContext(task_service=mock_service):
        result = runner.invoke(app, ["add", "Test task"])

    assert result.exit_code == 0
    mock_service.add_task.assert_called_once()
```

### Capture Output

```python
def test_list_output_format(state_with_tasks):
    """Verify list output formatting."""
    result = runner.invoke(app, ["list"])

    # Check table headers
    assert "ID" in result.output
    assert "Title" in result.output
    assert "Status" in result.output

    # Check task appears
    assert "Task 1" in result.output
```

## Common Pitfalls

### Pitfall 1: Shared State Between Tests

```python
# BAD - Tests share state
class TestBad:
    service = TaskService()  # Shared across all tests!

    def test_add(self):
        self.service.add_task("Task")  # Affects other tests

    def test_count(self):
        # May fail if test_add ran first
        assert len(self.service.get_all_tasks()) == 0


# GOOD - Fresh state per test
class TestGood:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.service = TaskService()

    def test_add(self):
        self.service.add_task("Task")

    def test_count(self):
        # Always passes - fresh service
        assert len(self.service.get_all_tasks()) == 0
```

### Pitfall 2: Forgetting to Reset Global State

```python
# BAD - Global state leaks
def test_adds_to_global():
    from todo.state import get_service
    service = get_service()
    service.add_task("Leaked task")
    # Task persists to next test!


# GOOD - Use fixtures that reset
@pytest.fixture(autouse=True)
def reset_globals():
    from todo.state import reset_state
    reset_state()
    yield
    reset_state()
```

### Pitfall 3: Order-Dependent Tests

```python
# BAD - Test order matters
def test_1_setup():
    service.add_task("Setup task")


def test_2_use():
    # Depends on test_1 running first!
    task = service.get_all_tasks()[0]


# GOOD - Each test is independent
def test_uses_task(task_service):
    # Create own data
    task = task_service.add_task("My task")
    # Use it
    assert task.title == "My task"
```

### Pitfall 4: Async State Issues

```python
# If using async, ensure state is task-local
from contextvars import ContextVar

_service: ContextVar[TaskService | None] = ContextVar("service", default=None)


async def get_async_service() -> TaskService:
    """Thread/task-safe service access."""
    service = _service.get()
    if service is None:
        service = TaskService()
        _service.set(service)
    return service
```

## Running Tests

```bash
# Run all tests with fresh state
uv run pytest -v

# Run with state debugging
uv run pytest -v --capture=no

# Run specific test class
uv run pytest tests/unit/test_state.py::TestAppState -v

# Run with coverage
uv run pytest --cov=todo.state --cov-report=term-missing
```
