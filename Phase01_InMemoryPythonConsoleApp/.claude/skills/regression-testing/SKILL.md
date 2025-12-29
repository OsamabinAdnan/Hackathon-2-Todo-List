---
name: regression-testing
description: Ensure new features do not break existing functionality using pytest. Use this skill when writing regression tests after bug fixes, feature additions, or refactoring. Provides patterns for maintaining test suites that catch unintended side effects.
---

# Regression Testing

Pytest patterns for preventing feature breakage and catching unintended side effects.

## Overview

This skill provides comprehensive test templates for:
- **Bug Fix Verification**: Tests that reproduce fixed bugs
- **Feature Integration**: Tests that verify existing features after changes
- **Refactoring Safety**: Tests that ensure behavior preservation
- **Cross-Feature Impact**: Tests for feature interactions

## Test File Structure

```
tests/
    regression/
        __init__.py
        test_bug_fixes.py        # Tests for specific bug fixes
        test_feature_stability.py # Feature preservation tests
        test_cross_feature.py     # Feature interaction tests
    conftest.py                   # Regression-specific fixtures
```

## Regression Test Principles

### 1. Document the Bug/Issue

```python
# tests/regression/test_bug_fixes.py
"""
Regression tests for bug fixes.

Each test documents:
- Issue ID or description
- Steps to reproduce
- Expected vs actual behavior
- Fix verification
"""

import pytest


class TestBugFix001:
    """
    Bug #001: Task completion resets priority to MEDIUM.

    Reported: 2024-01-15
    Fixed: 2024-01-16
    Affected: TaskService.mark_complete()

    Steps to reproduce:
    1. Create task with HIGH priority
    2. Mark task as complete
    3. Priority changed to MEDIUM (bug)

    Expected: Priority should remain HIGH
    """

    def test_complete_preserves_priority(self, task_service):
        """Verify completing task preserves priority."""
        from todo.models.enums import Priority

        # Arrange
        task = task_service.add_task("High priority task")
        task_service.set_priority(task.id, Priority.HIGH)

        # Act
        task_service.mark_complete(task.id)

        # Assert
        completed_task = task_service.get_task(task.id)
        assert completed_task.priority == Priority.HIGH


class TestBugFix002:
    """
    Bug #002: Deleting task with tags leaves orphan tag references.

    Reported: 2024-01-20
    Fixed: 2024-01-21
    Affected: TaskService.delete_task()
    """

    def test_delete_task_cleans_up_properly(self, task_service):
        """Verify deleting task doesn't affect other tasks' tags."""
        # Arrange
        task1 = task_service.add_task("Task 1")
        task_service.add_tag(task1.id, "shared-tag")

        task2 = task_service.add_task("Task 2")
        task_service.add_tag(task2.id, "shared-tag")

        # Act
        task_service.delete_task(task1.id)

        # Assert - task2's tags unaffected
        remaining = task_service.get_task(task2.id)
        assert "shared-tag" in remaining.tags


class TestBugFix003:
    """
    Bug #003: Search returns completed tasks when filtering incomplete.

    Reported: 2024-01-25
    Fixed: 2024-01-26
    Affected: TaskService.search() with filters
    """

    def test_search_respects_completion_filter(self, task_service):
        """Search with completion filter excludes completed tasks."""
        from todo.models.filters import TaskFilter

        # Arrange
        task1 = task_service.add_task("Buy groceries")
        task_service.mark_complete(task1.id)

        task2 = task_service.add_task("Buy supplies")
        # task2 remains incomplete

        # Act
        filter_criteria = TaskFilter(
            search_query="buy",
            completed=False
        )
        result = task_service.filter_tasks(filter_criteria)

        # Assert - only incomplete task returned
        assert len(result) == 1
        assert result[0].id == task2.id
```

### 2. Feature Stability Tests

```python
# tests/regression/test_feature_stability.py
"""
Tests to ensure existing features remain stable after changes.

Run these after any refactoring or new feature addition.
"""

import pytest
from datetime import datetime, timedelta
from todo.models.enums import Priority, RecurrencePattern


class TestCoreFeatureStability:
    """Core CRUD operations remain stable."""

    def test_add_task_still_works(self, task_service):
        """Basic add task functionality preserved."""
        task = task_service.add_task("Test task", "Description")

        assert task.id is not None
        assert task.title == "Test task"
        assert task.description == "Description"
        assert task.completed is False
        assert task.created_at is not None

    def test_get_task_still_works(self, task_service, sample_task):
        """Basic get task functionality preserved."""
        retrieved = task_service.get_task(sample_task.id)

        assert retrieved.id == sample_task.id
        assert retrieved.title == sample_task.title

    def test_update_task_still_works(self, task_service, sample_task):
        """Basic update task functionality preserved."""
        updated = task_service.update_task(
            sample_task.id,
            title="Updated Title"
        )

        assert updated.title == "Updated Title"
        assert updated.updated_at > sample_task.created_at

    def test_delete_task_still_works(self, task_service, sample_task):
        """Basic delete task functionality preserved."""
        from todo.models.exceptions import TaskNotFoundError

        task_service.delete_task(sample_task.id)

        with pytest.raises(TaskNotFoundError):
            task_service.get_task(sample_task.id)

    def test_mark_complete_still_works(self, task_service, sample_task):
        """Basic completion functionality preserved."""
        task_service.mark_complete(sample_task.id)

        task = task_service.get_task(sample_task.id)
        assert task.completed is True


class TestPriorityFeatureStability:
    """Priority feature remains stable."""

    def test_set_priority_still_works(self, task_service, sample_task):
        """Setting priority preserved."""
        task_service.set_priority(sample_task.id, Priority.HIGH)

        task = task_service.get_task(sample_task.id)
        assert task.priority == Priority.HIGH

    def test_filter_by_priority_still_works(self, task_service):
        """Priority filtering preserved."""
        high = task_service.add_task("High")
        task_service.set_priority(high.id, Priority.HIGH)

        low = task_service.add_task("Low")
        task_service.set_priority(low.id, Priority.LOW)

        result = task_service.filter_by_priority(Priority.HIGH)

        assert len(result) == 1
        assert result[0].id == high.id


class TestTagFeatureStability:
    """Tag feature remains stable."""

    def test_add_tag_still_works(self, task_service, sample_task):
        """Adding tags preserved."""
        task_service.add_tag(sample_task.id, "work")

        task = task_service.get_task(sample_task.id)
        assert "work" in task.tags

    def test_filter_by_tag_still_works(self, task_service):
        """Tag filtering preserved."""
        work_task = task_service.add_task("Work task")
        task_service.add_tag(work_task.id, "work")

        personal_task = task_service.add_task("Personal task")
        task_service.add_tag(personal_task.id, "personal")

        result = task_service.filter_by_tag("work")

        assert len(result) == 1
        assert result[0].id == work_task.id


class TestSearchFeatureStability:
    """Search feature remains stable."""

    def test_search_by_title_still_works(self, task_service):
        """Title search preserved."""
        task_service.add_task("Buy groceries")
        task_service.add_task("Call mom")

        result = task_service.search("groceries")

        assert len(result) == 1
        assert "groceries" in result[0].title.lower()

    def test_search_by_description_still_works(self, task_service):
        """Description search preserved."""
        task_service.add_task("Shopping", "Buy milk and eggs")
        task_service.add_task("Call", "Phone mom")

        result = task_service.search("milk")

        assert len(result) == 1


class TestRecurrenceFeatureStability:
    """Recurrence feature remains stable."""

    def test_set_recurrence_still_works(self, task_service, sample_task):
        """Setting recurrence preserved."""
        task_service.set_recurrence(sample_task.id, RecurrencePattern.DAILY)

        task = task_service.get_task(sample_task.id)
        assert task.recurrence == RecurrencePattern.DAILY

    def test_complete_recurring_still_creates_next(self, task_service):
        """Recurring task completion creates next occurrence."""
        task = task_service.add_task("Daily task")
        task_service.set_recurrence(task.id, RecurrencePattern.DAILY)
        task_service.set_due_date(task.id, datetime.now())

        original_count = len(task_service.get_all_tasks())
        task_service.complete_recurring(task.id)

        assert len(task_service.get_all_tasks()) == original_count + 1
```

### 3. Cross-Feature Impact Tests

```python
# tests/regression/test_cross_feature.py
"""
Tests for interactions between features.

Ensures changes to one feature don't break another.
"""

import pytest
from datetime import datetime
from todo.models.enums import Priority, RecurrencePattern


class TestPriorityAndCompletion:
    """Priority and completion interaction tests."""

    def test_completing_high_priority_preserves_priority(self, task_service):
        """HIGH priority task stays HIGH after completion."""
        task = task_service.add_task("Important")
        task_service.set_priority(task.id, Priority.HIGH)

        task_service.mark_complete(task.id)

        completed = task_service.get_task(task.id)
        assert completed.priority == Priority.HIGH

    def test_incomplete_restores_original_priority(self, task_service):
        """Marking incomplete doesn't change priority."""
        task = task_service.add_task("Task")
        task_service.set_priority(task.id, Priority.HIGH)
        task_service.mark_complete(task.id)

        task_service.mark_incomplete(task.id)

        restored = task_service.get_task(task.id)
        assert restored.priority == Priority.HIGH


class TestTagsAndCompletion:
    """Tags and completion interaction tests."""

    def test_completing_task_preserves_tags(self, task_service):
        """Tags remain after completion."""
        task = task_service.add_task("Tagged task")
        task_service.add_tag(task.id, "work")
        task_service.add_tag(task.id, "urgent")

        task_service.mark_complete(task.id)

        completed = task_service.get_task(task.id)
        assert set(completed.tags) == {"work", "urgent"}

    def test_filter_by_tag_includes_completed(self, task_service):
        """Tag filter can include completed tasks."""
        task = task_service.add_task("Work task")
        task_service.add_tag(task.id, "work")
        task_service.mark_complete(task.id)

        # Filter without completion restriction
        result = task_service.filter_by_tag("work")

        assert len(result) == 1


class TestSearchAndFilters:
    """Search and filter interaction tests."""

    def test_search_with_priority_filter(self, task_service):
        """Search respects priority filter."""
        high = task_service.add_task("Buy groceries")
        task_service.set_priority(high.id, Priority.HIGH)

        low = task_service.add_task("Buy supplies")
        task_service.set_priority(low.id, Priority.LOW)

        from todo.models.filters import TaskFilter
        result = task_service.filter_tasks(TaskFilter(
            search_query="buy",
            priority=Priority.HIGH
        ))

        assert len(result) == 1
        assert result[0].id == high.id

    def test_search_with_tag_filter(self, task_service):
        """Search respects tag filter."""
        work = task_service.add_task("Buy office supplies")
        task_service.add_tag(work.id, "work")

        personal = task_service.add_task("Buy groceries")
        task_service.add_tag(personal.id, "personal")

        from todo.models.filters import TaskFilter
        result = task_service.filter_tasks(TaskFilter(
            search_query="buy",
            tags=["work"]
        ))

        assert len(result) == 1
        assert result[0].id == work.id


class TestRecurrenceAndProperties:
    """Recurrence and other property interaction tests."""

    def test_recurring_task_inherits_priority(self, task_service):
        """New recurring task gets original's priority."""
        task = task_service.add_task("Daily high priority")
        task_service.set_priority(task.id, Priority.HIGH)
        task_service.set_recurrence(task.id, RecurrencePattern.DAILY)
        task_service.set_due_date(task.id, datetime.now())

        task_service.complete_recurring(task.id)

        tasks = task_service.get_all_tasks()
        new_task = [t for t in tasks if t.id != task.id][0]
        assert new_task.priority == Priority.HIGH

    def test_recurring_task_inherits_tags(self, task_service):
        """New recurring task gets original's tags."""
        task = task_service.add_task("Daily work task")
        task_service.add_tag(task.id, "work")
        task_service.add_tag(task.id, "daily")
        task_service.set_recurrence(task.id, RecurrencePattern.DAILY)
        task_service.set_due_date(task.id, datetime.now())

        task_service.complete_recurring(task.id)

        tasks = task_service.get_all_tasks()
        new_task = [t for t in tasks if t.id != task.id][0]
        assert set(new_task.tags) == {"work", "daily"}


class TestSortAndFilters:
    """Sort and filter interaction tests."""

    def test_filtered_results_can_be_sorted(self, task_service):
        """Filtered results maintain correct sort order."""
        from todo.models.enums import SortField, SortOrder

        # Create tasks with different priorities
        z_high = task_service.add_task("Zebra task")
        task_service.set_priority(z_high.id, Priority.HIGH)

        a_high = task_service.add_task("Apple task")
        task_service.set_priority(a_high.id, Priority.HIGH)

        b_low = task_service.add_task("Banana task")
        task_service.set_priority(b_low.id, Priority.LOW)

        # Filter by HIGH priority, then sort by title
        from todo.models.filters import TaskFilter
        high_tasks = task_service.filter_tasks(TaskFilter(priority=Priority.HIGH))
        sorted_high = sorted(high_tasks, key=lambda t: t.title)

        assert sorted_high[0].title == "Apple task"
        assert sorted_high[1].title == "Zebra task"
```

## Regression Test Workflow

### After Bug Fix

```python
# 1. Write test that reproduces the bug
def test_bug_reproduction():
    # This test should FAIL before the fix
    ...

# 2. Verify test fails
# uv run pytest tests/regression/test_bug_fixes.py::TestBugXXX -v

# 3. Apply the fix

# 4. Verify test passes
# uv run pytest tests/regression/test_bug_fixes.py::TestBugXXX -v

# 5. Run full regression suite
# uv run pytest tests/regression/ -v
```

### After New Feature

```python
# 1. Run existing regression tests BEFORE implementing
# uv run pytest tests/regression/ -v

# 2. Implement new feature

# 3. Run regression tests again
# uv run pytest tests/regression/ -v

# 4. Add new feature stability tests
# 5. Add cross-feature tests if applicable
```

## TUI Regression Testing Patterns

### Testing TUI Feature Stability

```python
# tests/regression/test_tui_stability.py
"""Regression tests for TUI functionality."""

import pytest
from textual.testing import AppTester
from todo.tui.app import TodoApp


@pytest.fixture
async def app_tester(task_service):
    """TUI app tester for regression tests."""
    app = TodoApp(task_service=task_service)
    async with AppTester.run_test(app) as tester:
        yield tester


class TestTUIKeyboardStability:
    """Verify keyboard shortcuts remain stable."""

    async def test_add_shortcut_still_works(self, app_tester):
        """'a' key still opens add modal."""
        await app_tester.press("a")
        assert app_tester.app.query_one("AddTaskModal")

    async def test_delete_shortcut_still_works(self, app_tester, sample_task):
        """'d' key still triggers delete confirmation."""
        await app_tester.press("d")
        assert app_tester.app.query_one("ConfirmModal")

    async def test_quit_shortcut_still_works(self, app_tester):
        """'q' key still exits app."""
        await app_tester.press("q")
        assert app_tester.exit_code == 0

    async def test_navigation_still_works(self, app_tester):
        """j/k navigation still works."""
        await app_tester.press("j")
        await app_tester.press("k")
        # Should not crash


class TestTUIReactiveUpdates:
    """Verify reactive updates remain stable."""

    async def test_task_list_updates_on_add(self, app_tester):
        """Task list reactively updates when task added."""
        initial_count = len(app_tester.app.query("TaskItem"))

        await app_tester.press("a")
        await app_tester.type("New task")
        await app_tester.press("enter")

        # List should have one more item
        final_count = len(app_tester.app.query("TaskItem"))
        assert final_count == initial_count + 1

    async def test_status_bar_updates_on_complete(self, app_tester, sample_task):
        """Status bar updates when task completed."""
        await app_tester.press("space")

        status = app_tester.app.query_one("StatusBar")
        # Verify completed count updated


class TestTUIBugFixes:
    """TUI-specific bug fix regression tests."""

    async def test_bug_modal_escape_closes(self, app_tester):
        """
        Bug: Modal didn't close on escape.

        Fixed: 2024-XX-XX
        """
        await app_tester.press("a")
        assert app_tester.app.query_one("AddTaskModal")

        await app_tester.press("escape")
        assert len(app_tester.app.query("AddTaskModal")) == 0

    async def test_bug_focus_after_modal_close(self, app_tester):
        """
        Bug: Focus lost after closing modal.

        Fixed: 2024-XX-XX
        """
        await app_tester.press("a")
        await app_tester.press("escape")

        # Focus should return to task list
        task_list = app_tester.app.query_one("TaskListView")
        assert task_list.has_focus or task_list.has_focus_within
```

## Running Tests

```bash
# Run all regression tests
uv run pytest tests/regression/ -v

# Run TUI regression tests
uv run pytest tests/regression/test_tui_stability.py -v

# Run bug fix tests only
uv run pytest tests/regression/test_bug_fixes.py -v

# Run feature stability tests
uv run pytest tests/regression/test_feature_stability.py -v

# Run with markers
uv run pytest -m regression -v
```

## Checklist

Before considering regression tests complete:
- [ ] All bug fixes have reproduction tests
- [ ] Core features have stability tests
- [ ] Feature interactions are tested
- [ ] Tests document issue context
- [ ] All regression tests pass
- [ ] New features added to stability suite
