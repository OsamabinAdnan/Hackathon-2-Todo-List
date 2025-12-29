---
name: basic-feature-testing
description: Validate correctness of CRUD operations and completion toggle using pytest. Use this skill when writing tests for add, delete, update, view tasks, and mark complete/incomplete functionality. Provides test patterns, fixtures, and assertions for basic Todo operations.
---

# Basic Feature Testing

Pytest patterns for testing CRUD operations and task completion in the Todo application.

## Overview

This skill provides comprehensive test templates for:
- **Create**: Adding new tasks with validation
- **Read**: Retrieving single and multiple tasks
- **Update**: Modifying task fields
- **Delete**: Removing tasks
- **Complete/Incomplete**: Toggling task status

## Test File Structure

```
tests/
    conftest.py           # Shared fixtures
    unit/
        test_task.py      # Task model tests
        test_task_service.py  # CRUD operation tests
```

## Shared Fixtures

```python
# tests/conftest.py
"""Shared pytest fixtures for Todo app tests."""

import pytest
from todo.services.task_service import TaskService
from todo.models.task import Task
from todo.models.enums import Priority


@pytest.fixture
def task_service():
    """
    Provide fresh TaskService for each test.

    Ensures complete isolation between tests.
    """
    return TaskService()


@pytest.fixture
def sample_task(task_service):
    """
    Provide a pre-created task.

    Use when test needs an existing task to operate on.
    """
    return task_service.add_task(
        title="Sample Task",
        description="Sample description"
    )


@pytest.fixture
def multiple_tasks(task_service):
    """
    Provide service with 3 pre-created tasks.

    Use for list, filter, and bulk operation tests.
    """
    tasks = [
        task_service.add_task("Task One"),
        task_service.add_task("Task Two"),
        task_service.add_task("Task Three"),
    ]
    return task_service, tasks
```

## CREATE Tests

```python
# tests/unit/test_task_service.py
"""Tests for TaskService CRUD operations."""

import pytest
from todo.services.task_service import TaskService
from todo.models.exceptions import ValidationError


class TestAddTask:
    """Tests for TaskService.add_task()."""

    def test_add_task_with_title_only(self, task_service):
        """Adding task with just title creates valid task."""
        # Act
        task = task_service.add_task("Buy groceries")

        # Assert
        assert task.title == "Buy groceries"
        assert task.description == ""
        assert task.completed is False
        assert task.id is not None

    def test_add_task_with_title_and_description(self, task_service):
        """Adding task with title and description stores both."""
        # Act
        task = task_service.add_task(
            title="Buy groceries",
            description="Milk, eggs, bread"
        )

        # Assert
        assert task.title == "Buy groceries"
        assert task.description == "Milk, eggs, bread"

    def test_add_task_generates_unique_ids(self, task_service):
        """Each added task gets a unique ID."""
        # Act
        task1 = task_service.add_task("Task 1")
        task2 = task_service.add_task("Task 2")
        task3 = task_service.add_task("Task 3")

        # Assert
        ids = {task1.id, task2.id, task3.id}
        assert len(ids) == 3  # All unique

    def test_add_task_sets_created_timestamp(self, task_service):
        """New task has created_at timestamp."""
        # Act
        task = task_service.add_task("Test task")

        # Assert
        assert task.created_at is not None

    def test_add_task_with_empty_title_raises_error(self, task_service):
        """Empty title raises ValidationError."""
        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            task_service.add_task("")

        assert "empty" in str(exc_info.value).lower()

    def test_add_task_with_whitespace_title_raises_error(self, task_service):
        """Whitespace-only title raises ValidationError."""
        # Act & Assert
        with pytest.raises(ValidationError):
            task_service.add_task("   ")

    def test_add_task_strips_whitespace_from_title(self, task_service):
        """Title whitespace is trimmed."""
        # Act
        task = task_service.add_task("  Buy groceries  ")

        # Assert
        assert task.title == "Buy groceries"

    @pytest.mark.parametrize("title", [
        "A",                    # Single character
        "A" * 200,              # Max length
        "Task with numbers 123",
        "Task with symbols !@#",
        "Unicode task",
    ])
    def test_add_task_accepts_valid_titles(self, task_service, title):
        """Various valid titles are accepted."""
        # Act
        task = task_service.add_task(title)

        # Assert
        assert task.title == title.strip()
```

## READ Tests

```python
class TestGetTask:
    """Tests for TaskService.get_task()."""

    def test_get_task_returns_correct_task(self, task_service, sample_task):
        """Getting task by ID returns the correct task."""
        # Act
        retrieved = task_service.get_task(sample_task.id)

        # Assert
        assert retrieved.id == sample_task.id
        assert retrieved.title == sample_task.title

    def test_get_task_with_invalid_id_raises_error(self, task_service):
        """Non-existent ID raises TaskNotFoundError."""
        from todo.models.exceptions import TaskNotFoundError

        # Act & Assert
        with pytest.raises(TaskNotFoundError) as exc_info:
            task_service.get_task("non-existent-id")

        assert "non-existent-id" in str(exc_info.value)


class TestGetAllTasks:
    """Tests for TaskService.get_all_tasks()."""

    def test_get_all_tasks_empty_list(self, task_service):
        """Empty service returns empty list."""
        # Act
        tasks = task_service.get_all_tasks()

        # Assert
        assert tasks == []

    def test_get_all_tasks_returns_all(self, multiple_tasks):
        """All added tasks are returned."""
        service, created_tasks = multiple_tasks

        # Act
        tasks = service.get_all_tasks()

        # Assert
        assert len(tasks) == 3
        task_ids = {t.id for t in tasks}
        expected_ids = {t.id for t in created_tasks}
        assert task_ids == expected_ids

    def test_get_all_tasks_returns_copy(self, task_service, sample_task):
        """Returned list is a copy, not internal reference."""
        # Act
        tasks1 = task_service.get_all_tasks()
        tasks1.clear()  # Modify returned list
        tasks2 = task_service.get_all_tasks()

        # Assert - original data unaffected
        assert len(tasks2) == 1
```

## UPDATE Tests

```python
class TestUpdateTask:
    """Tests for TaskService.update_task()."""

    def test_update_task_title(self, task_service, sample_task):
        """Updating title changes task title."""
        # Act
        updated = task_service.update_task(
            sample_task.id,
            title="New Title"
        )

        # Assert
        assert updated.title == "New Title"
        assert updated.description == sample_task.description

    def test_update_task_description(self, task_service, sample_task):
        """Updating description changes task description."""
        # Act
        updated = task_service.update_task(
            sample_task.id,
            description="New description"
        )

        # Assert
        assert updated.description == "New description"
        assert updated.title == sample_task.title

    def test_update_task_both_fields(self, task_service, sample_task):
        """Updating both fields changes both."""
        # Act
        updated = task_service.update_task(
            sample_task.id,
            title="New Title",
            description="New description"
        )

        # Assert
        assert updated.title == "New Title"
        assert updated.description == "New description"

    def test_update_task_updates_timestamp(self, task_service, sample_task):
        """Update changes updated_at timestamp."""
        import time
        original_updated = sample_task.updated_at

        # Small delay to ensure different timestamp
        time.sleep(0.01)

        # Act
        updated = task_service.update_task(
            sample_task.id,
            title="New Title"
        )

        # Assert
        assert updated.updated_at > original_updated

    def test_update_task_with_invalid_id_raises_error(self, task_service):
        """Updating non-existent task raises error."""
        from todo.models.exceptions import TaskNotFoundError

        # Act & Assert
        with pytest.raises(TaskNotFoundError):
            task_service.update_task("invalid-id", title="New")

    def test_update_task_with_empty_title_raises_error(
        self, task_service, sample_task
    ):
        """Updating with empty title raises ValidationError."""
        from todo.models.exceptions import ValidationError

        # Act & Assert
        with pytest.raises(ValidationError):
            task_service.update_task(sample_task.id, title="")
```

## DELETE Tests

```python
class TestDeleteTask:
    """Tests for TaskService.delete_task()."""

    def test_delete_task_removes_task(self, task_service, sample_task):
        """Deleted task is removed from service."""
        from todo.models.exceptions import TaskNotFoundError

        # Act
        result = task_service.delete_task(sample_task.id)

        # Assert
        assert result is True
        with pytest.raises(TaskNotFoundError):
            task_service.get_task(sample_task.id)

    def test_delete_task_reduces_count(self, multiple_tasks):
        """Deleting task reduces total count."""
        service, tasks = multiple_tasks

        # Act
        service.delete_task(tasks[0].id)

        # Assert
        remaining = service.get_all_tasks()
        assert len(remaining) == 2

    def test_delete_task_with_invalid_id_raises_error(self, task_service):
        """Deleting non-existent task raises error."""
        from todo.models.exceptions import TaskNotFoundError

        # Act & Assert
        with pytest.raises(TaskNotFoundError):
            task_service.delete_task("invalid-id")

    def test_delete_task_only_removes_specified(self, multiple_tasks):
        """Delete only removes the specified task."""
        service, tasks = multiple_tasks
        task_to_delete = tasks[1]
        remaining_ids = {tasks[0].id, tasks[2].id}

        # Act
        service.delete_task(task_to_delete.id)

        # Assert
        remaining = service.get_all_tasks()
        actual_ids = {t.id for t in remaining}
        assert actual_ids == remaining_ids
```

## COMPLETE/INCOMPLETE Tests

```python
class TestMarkComplete:
    """Tests for task completion operations."""

    def test_mark_complete_sets_flag(self, task_service, sample_task):
        """Marking complete sets completed to True."""
        # Precondition
        assert sample_task.completed is False

        # Act
        task_service.mark_complete(sample_task.id)

        # Assert
        task = task_service.get_task(sample_task.id)
        assert task.completed is True

    def test_mark_complete_updates_timestamp(self, task_service, sample_task):
        """Marking complete updates timestamp."""
        import time
        original = sample_task.updated_at
        time.sleep(0.01)

        # Act
        task_service.mark_complete(sample_task.id)

        # Assert
        task = task_service.get_task(sample_task.id)
        assert task.updated_at > original

    def test_mark_incomplete_clears_flag(self, task_service, sample_task):
        """Marking incomplete sets completed to False."""
        # Setup - complete first
        task_service.mark_complete(sample_task.id)

        # Act
        task_service.mark_incomplete(sample_task.id)

        # Assert
        task = task_service.get_task(sample_task.id)
        assert task.completed is False

    def test_toggle_complete_flips_status(self, task_service, sample_task):
        """Toggle flips completed status."""
        # Initially incomplete
        assert sample_task.completed is False

        # First toggle -> complete
        task_service.toggle_complete(sample_task.id)
        task = task_service.get_task(sample_task.id)
        assert task.completed is True

        # Second toggle -> incomplete
        task_service.toggle_complete(sample_task.id)
        task = task_service.get_task(sample_task.id)
        assert task.completed is False

    def test_mark_complete_invalid_id_raises_error(self, task_service):
        """Marking non-existent task raises error."""
        from todo.models.exceptions import TaskNotFoundError

        # Act & Assert
        with pytest.raises(TaskNotFoundError):
            task_service.mark_complete("invalid-id")
```

## TUI Testing Patterns

### Testing CRUD Operations via TUI

```python
# tests/tui/test_task_crud.py
"""Tests for CRUD operations via TUI interface."""

import pytest
from textual.testing import AppTester
from todo.tui.app import TodoApp


@pytest.fixture
async def app_tester(task_service):
    """Async fixture for TUI testing."""
    app = TodoApp(task_service=task_service)
    async with AppTester.run_test(app) as tester:
        yield tester


class TestAddTaskTUI:
    """Tests for adding tasks via TUI."""

    async def test_add_task_via_modal(self, app_tester):
        """Adding task via TUI modal creates task."""
        # Press 'a' to open add modal
        await app_tester.press("a")

        # Type task title
        await app_tester.type("Buy groceries")

        # Submit
        await app_tester.press("enter")

        # Verify task appears in list
        assert app_tester.app.task_service.get_all_tasks()

    async def test_cancel_add_modal(self, app_tester):
        """Pressing escape cancels add modal."""
        await app_tester.press("a")
        await app_tester.press("escape")

        # No task created
        assert len(app_tester.app.task_service.get_all_tasks()) == 0


class TestToggleCompleteTUI:
    """Tests for toggling completion via TUI."""

    async def test_toggle_complete_with_space(self, app_tester, sample_task):
        """Pressing space toggles task completion."""
        # Navigate to task and press space
        await app_tester.press("space")

        task = app_tester.app.task_service.get_task(sample_task.id)
        assert task.completed is True
```

## Running Tests

```bash
# Run all basic feature tests
uv run pytest tests/unit/test_task_service.py -v

# Run TUI tests
uv run pytest tests/tui/test_task_crud.py -v

# Run specific test class
uv run pytest tests/unit/test_task_service.py::TestAddTask -v

# Run with coverage
uv run pytest tests/unit/test_task_service.py --cov=todo.services --cov-report=term-missing

# Run parametrized tests only
uv run pytest -k "parametrize" -v
```

## Checklist

Before considering CRUD tests complete:
- [ ] All happy paths tested
- [ ] All error conditions tested
- [ ] Validation rules verified
- [ ] Timestamps verified
- [ ] ID uniqueness verified
- [ ] Isolation between tests verified
- [ ] Parametrized tests for multiple inputs
