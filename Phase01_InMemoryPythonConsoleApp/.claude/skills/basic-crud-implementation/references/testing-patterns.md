# Testing Patterns for CRUD Operations

Pytest fixtures and test cases for TaskService CRUD operations.

## Table of Contents

1. [Fixtures](#fixtures)
2. [Add Task Tests](#add-task-tests)
3. [Get Task Tests](#get-task-tests)
4. [Update Task Tests](#update-task-tests)
5. [Delete Task Tests](#delete-task-tests)
6. [Toggle Complete Tests](#toggle-complete-tests)

## Fixtures

```python
# tests/unit/test_task_service.py

import pytest
from datetime import datetime

from todo.services.task_service import TaskService
from todo.models.task import Task
from todo.models.exceptions import TaskNotFoundError, ValidationError


@pytest.fixture
def service() -> TaskService:
    """Fresh TaskService instance for each test."""
    return TaskService()


@pytest.fixture
def service_with_tasks(service: TaskService) -> TaskService:
    """TaskService pre-populated with sample tasks."""
    service.add_task("Task 1", "Description 1")
    service.add_task("Task 2", "Description 2")
    service.add_task("Task 3", "Description 3")
    return service


@pytest.fixture
def sample_task(service: TaskService) -> Task:
    """Single task for testing."""
    return service.add_task("Sample Task", "Sample Description")
```

## Add Task Tests

```python
class TestAddTask:
    """Tests for TaskService.add_task()"""

    def test_add_task_basic(self, service: TaskService) -> None:
        """Add task with title only."""
        task = service.add_task("Buy groceries")

        assert task.title == "Buy groceries"
        assert task.description == ""
        assert task.completed is False
        assert task.id is not None
        assert isinstance(task.created_at, datetime)

    def test_add_task_with_description(self, service: TaskService) -> None:
        """Add task with title and description."""
        task = service.add_task("Buy groceries", "Milk, eggs, bread")

        assert task.title == "Buy groceries"
        assert task.description == "Milk, eggs, bread"

    def test_add_task_strips_whitespace(self, service: TaskService) -> None:
        """Title whitespace should be stripped."""
        task = service.add_task("  Buy groceries  ")

        assert task.title == "Buy groceries"

    def test_add_task_empty_title_raises(self, service: TaskService) -> None:
        """Empty title should raise ValidationError."""
        with pytest.raises(ValidationError, match="cannot be empty"):
            service.add_task("")

    def test_add_task_whitespace_title_raises(self, service: TaskService) -> None:
        """Whitespace-only title should raise ValidationError."""
        with pytest.raises(ValidationError, match="cannot be empty"):
            service.add_task("   ")

    def test_add_task_title_too_long_raises(self, service: TaskService) -> None:
        """Title over 200 chars should raise ValidationError."""
        long_title = "x" * 201
        with pytest.raises(ValidationError, match="exceed 200"):
            service.add_task(long_title)

    def test_add_task_unique_ids(self, service: TaskService) -> None:
        """Each task should have a unique ID."""
        task1 = service.add_task("Task 1")
        task2 = service.add_task("Task 2")

        assert task1.id != task2.id

    def test_add_task_stored_in_service(self, service: TaskService) -> None:
        """Task should be retrievable after adding."""
        task = service.add_task("Test task")

        retrieved = service.get_task(task.id)
        assert retrieved.id == task.id
        assert retrieved.title == task.title
```

## Get Task Tests

```python
class TestGetTask:
    """Tests for TaskService.get_task() and get_all_tasks()"""

    def test_get_task_exists(self, service: TaskService, sample_task: Task) -> None:
        """Get existing task by ID."""
        retrieved = service.get_task(sample_task.id)

        assert retrieved.id == sample_task.id
        assert retrieved.title == sample_task.title

    def test_get_task_not_found_raises(self, service: TaskService) -> None:
        """Non-existent task should raise TaskNotFoundError."""
        with pytest.raises(TaskNotFoundError, match="not found"):
            service.get_task("non-existent-id")

    def test_get_all_tasks_empty(self, service: TaskService) -> None:
        """Empty service returns empty list."""
        tasks = service.get_all_tasks()

        assert tasks == []

    def test_get_all_tasks_returns_all(
        self, service_with_tasks: TaskService
    ) -> None:
        """Get all returns all added tasks."""
        tasks = service_with_tasks.get_all_tasks()

        assert len(tasks) == 3
        titles = [t.title for t in tasks]
        assert "Task 1" in titles
        assert "Task 2" in titles
        assert "Task 3" in titles

    def test_get_tasks_count(self, service_with_tasks: TaskService) -> None:
        """Count returns correct number."""
        assert service_with_tasks.get_tasks_count() == 3

    def test_task_exists_true(self, service: TaskService, sample_task: Task) -> None:
        """task_exists returns True for existing task."""
        assert service.task_exists(sample_task.id) is True

    def test_task_exists_false(self, service: TaskService) -> None:
        """task_exists returns False for non-existent task."""
        assert service.task_exists("fake-id") is False
```

## Update Task Tests

```python
class TestUpdateTask:
    """Tests for TaskService.update_task()"""

    def test_update_title(self, service: TaskService, sample_task: Task) -> None:
        """Update task title."""
        updated = service.update_task(sample_task.id, title="New Title")

        assert updated.title == "New Title"
        assert updated.description == sample_task.description

    def test_update_description(
        self, service: TaskService, sample_task: Task
    ) -> None:
        """Update task description."""
        updated = service.update_task(
            sample_task.id, description="New Description"
        )

        assert updated.title == sample_task.title
        assert updated.description == "New Description"

    def test_update_both_fields(
        self, service: TaskService, sample_task: Task
    ) -> None:
        """Update both title and description."""
        updated = service.update_task(
            sample_task.id,
            title="New Title",
            description="New Description",
        )

        assert updated.title == "New Title"
        assert updated.description == "New Description"

    def test_update_updates_timestamp(
        self, service: TaskService, sample_task: Task
    ) -> None:
        """Update should refresh updated_at timestamp."""
        original_updated_at = sample_task.updated_at

        updated = service.update_task(sample_task.id, title="New Title")

        assert updated.updated_at >= original_updated_at

    def test_update_not_found_raises(self, service: TaskService) -> None:
        """Update non-existent task raises TaskNotFoundError."""
        with pytest.raises(TaskNotFoundError):
            service.update_task("fake-id", title="New Title")

    def test_update_empty_title_raises(
        self, service: TaskService, sample_task: Task
    ) -> None:
        """Update with empty title raises ValidationError."""
        with pytest.raises(ValidationError, match="cannot be empty"):
            service.update_task(sample_task.id, title="")

    def test_update_title_too_long_raises(
        self, service: TaskService, sample_task: Task
    ) -> None:
        """Update with title over 200 chars raises ValidationError."""
        with pytest.raises(ValidationError, match="exceed 200"):
            service.update_task(sample_task.id, title="x" * 201)

    def test_update_no_changes(
        self, service: TaskService, sample_task: Task
    ) -> None:
        """Update with no arguments still updates timestamp."""
        original_title = sample_task.title
        updated = service.update_task(sample_task.id)

        assert updated.title == original_title
```

## Delete Task Tests

```python
class TestDeleteTask:
    """Tests for TaskService.delete_task()"""

    def test_delete_task_success(
        self, service: TaskService, sample_task: Task
    ) -> None:
        """Delete existing task returns True."""
        result = service.delete_task(sample_task.id)

        assert result is True
        assert service.task_exists(sample_task.id) is False

    def test_delete_task_not_found_raises(self, service: TaskService) -> None:
        """Delete non-existent task raises TaskNotFoundError."""
        with pytest.raises(TaskNotFoundError, match="not found"):
            service.delete_task("fake-id")

    def test_delete_reduces_count(
        self, service_with_tasks: TaskService
    ) -> None:
        """Delete should reduce task count."""
        initial_count = service_with_tasks.get_tasks_count()
        tasks = service_with_tasks.get_all_tasks()

        service_with_tasks.delete_task(tasks[0].id)

        assert service_with_tasks.get_tasks_count() == initial_count - 1

    def test_clear_all(self, service_with_tasks: TaskService) -> None:
        """clear_all removes all tasks."""
        count = service_with_tasks.clear_all()

        assert count == 3
        assert service_with_tasks.get_tasks_count() == 0
```

## Toggle Complete Tests

```python
class TestToggleComplete:
    """Tests for TaskService completion methods"""

    def test_toggle_complete_false_to_true(
        self, service: TaskService, sample_task: Task
    ) -> None:
        """Toggle incomplete task to complete."""
        assert sample_task.completed is False

        toggled = service.toggle_complete(sample_task.id)

        assert toggled.completed is True

    def test_toggle_complete_true_to_false(
        self, service: TaskService, sample_task: Task
    ) -> None:
        """Toggle complete task to incomplete."""
        service.mark_complete(sample_task.id)

        toggled = service.toggle_complete(sample_task.id)

        assert toggled.completed is False

    def test_toggle_updates_timestamp(
        self, service: TaskService, sample_task: Task
    ) -> None:
        """Toggle should update updated_at."""
        original = sample_task.updated_at

        toggled = service.toggle_complete(sample_task.id)

        assert toggled.updated_at >= original

    def test_toggle_not_found_raises(self, service: TaskService) -> None:
        """Toggle non-existent task raises TaskNotFoundError."""
        with pytest.raises(TaskNotFoundError):
            service.toggle_complete("fake-id")

    def test_mark_complete(
        self, service: TaskService, sample_task: Task
    ) -> None:
        """mark_complete sets completed=True."""
        task = service.mark_complete(sample_task.id)

        assert task.completed is True

    def test_mark_incomplete(
        self, service: TaskService, sample_task: Task
    ) -> None:
        """mark_incomplete sets completed=False."""
        service.mark_complete(sample_task.id)

        task = service.mark_incomplete(sample_task.id)

        assert task.completed is False

    def test_mark_complete_idempotent(
        self, service: TaskService, sample_task: Task
    ) -> None:
        """Calling mark_complete twice keeps completed=True."""
        service.mark_complete(sample_task.id)
        task = service.mark_complete(sample_task.id)

        assert task.completed is True
```

## Running Tests

```bash
# Run all CRUD tests
uv run pytest tests/unit/test_task_service.py -v

# Run specific test class
uv run pytest tests/unit/test_task_service.py::TestAddTask -v

# Run with coverage
uv run pytest tests/unit/test_task_service.py --cov=todo.services --cov-report=term-missing
```

## Coverage Target

Per constitution requirement: **100% coverage for core CRUD logic**

```bash
# Verify coverage meets requirement
uv run pytest --cov=todo.services.task_service --cov-fail-under=100
```
