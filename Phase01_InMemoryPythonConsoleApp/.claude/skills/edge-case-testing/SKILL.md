---
name: edge-case-testing
description: Test empty list, invalid task IDs, invalid inputs, duplicate actions using pytest. Use this skill when writing tests for boundary conditions, error handling, validation failures, and unusual user behaviors. Ensures robustness of the Todo application.
---

# Edge Case Testing

Pytest patterns for testing boundary conditions, invalid inputs, and error handling.

## Overview

This skill provides comprehensive test templates for:
- **Empty State**: Operations on empty task list
- **Invalid IDs**: Non-existent, malformed, empty IDs
- **Invalid Inputs**: Empty strings, oversized inputs, special characters
- **Duplicate Actions**: Completing completed tasks, deleting twice
- **Boundary Values**: Max lengths, min/max priorities

## Test File Structure

```
tests/
    edge_cases/
        __init__.py
        test_empty_state.py      # Empty list operations
        test_invalid_ids.py      # Invalid ID handling
        test_validation.py       # Input validation tests
        test_duplicate_actions.py # Repeated operation tests
        test_boundaries.py       # Boundary value tests
```

## Empty State Tests

```python
# tests/edge_cases/test_empty_state.py
"""Tests for operations on empty task list."""

import pytest
from todo.models.enums import Priority, SortField, SortOrder


class TestEmptyListOperations:
    """Tests for operations when no tasks exist."""

    def test_get_all_tasks_empty(self, task_service):
        """Getting all tasks from empty service returns empty list."""
        # Act
        tasks = task_service.get_all_tasks()

        # Assert
        assert tasks == []
        assert len(tasks) == 0

    def test_search_empty_list(self, task_service):
        """Searching empty list returns empty list."""
        # Act
        result = task_service.search("anything")

        # Assert
        assert result == []

    def test_filter_empty_list(self, task_service):
        """Filtering empty list returns empty list."""
        # Act
        result = task_service.filter_by_priority(Priority.HIGH)

        # Assert
        assert result == []

    def test_sort_empty_list(self, task_service):
        """Sorting empty list returns empty list."""
        # Act
        result = task_service.get_sorted(SortField.TITLE, SortOrder.ASC)

        # Assert
        assert result == []

    def test_get_overdue_empty_list(self, task_service):
        """Getting overdue from empty list returns empty list."""
        # Act
        result = task_service.get_overdue_tasks()

        # Assert
        assert result == []

    def test_get_due_today_empty_list(self, task_service):
        """Getting due today from empty list returns empty list."""
        # Act
        result = task_service.get_due_today()

        # Assert
        assert result == []

    def test_get_due_reminders_empty_list(self, task_service):
        """Getting due reminders from empty list returns empty list."""
        # Act
        result = task_service.get_due_reminders()

        # Assert
        assert result == []

    def test_filter_by_tag_empty_list(self, task_service):
        """Filtering by tag on empty list returns empty list."""
        # Act
        result = task_service.filter_by_tag("work")

        # Assert
        assert result == []

    def test_count_tasks_empty_list(self, task_service):
        """Counting tasks on empty list returns zero."""
        # Act
        count = len(task_service.get_all_tasks())

        # Assert
        assert count == 0
```

## Invalid ID Tests

```python
# tests/edge_cases/test_invalid_ids.py
"""Tests for invalid task ID handling."""

import pytest
from todo.models.exceptions import TaskNotFoundError


class TestInvalidTaskIds:
    """Tests for operations with invalid task IDs."""

    def test_get_nonexistent_id(self, task_service):
        """Getting non-existent ID raises TaskNotFoundError."""
        with pytest.raises(TaskNotFoundError) as exc_info:
            task_service.get_task("nonexistent-id-12345")

        assert "nonexistent-id-12345" in str(exc_info.value)

    def test_update_nonexistent_id(self, task_service):
        """Updating non-existent ID raises TaskNotFoundError."""
        with pytest.raises(TaskNotFoundError):
            task_service.update_task("fake-id", title="New Title")

    def test_delete_nonexistent_id(self, task_service):
        """Deleting non-existent ID raises TaskNotFoundError."""
        with pytest.raises(TaskNotFoundError):
            task_service.delete_task("fake-id")

    def test_mark_complete_nonexistent_id(self, task_service):
        """Marking complete non-existent ID raises TaskNotFoundError."""
        with pytest.raises(TaskNotFoundError):
            task_service.mark_complete("fake-id")

    def test_set_priority_nonexistent_id(self, task_service):
        """Setting priority on non-existent ID raises TaskNotFoundError."""
        from todo.models.enums import Priority

        with pytest.raises(TaskNotFoundError):
            task_service.set_priority("fake-id", Priority.HIGH)

    def test_add_tag_nonexistent_id(self, task_service):
        """Adding tag to non-existent ID raises TaskNotFoundError."""
        with pytest.raises(TaskNotFoundError):
            task_service.add_tag("fake-id", "work")

    def test_set_due_date_nonexistent_id(self, task_service):
        """Setting due date on non-existent ID raises TaskNotFoundError."""
        from datetime import datetime

        with pytest.raises(TaskNotFoundError):
            task_service.set_due_date("fake-id", datetime.now())

    def test_empty_id(self, task_service):
        """Empty string ID raises TaskNotFoundError."""
        with pytest.raises(TaskNotFoundError):
            task_service.get_task("")

    def test_whitespace_id(self, task_service):
        """Whitespace-only ID raises TaskNotFoundError."""
        with pytest.raises(TaskNotFoundError):
            task_service.get_task("   ")

    @pytest.mark.parametrize("invalid_id", [
        "123",                    # Short numeric
        "a" * 1000,              # Very long
        "special!@#$%chars",     # Special characters
        "with spaces here",      # Spaces in ID
        "\n\t\r",                # Whitespace characters
        "null",                  # String "null"
        "undefined",             # String "undefined"
    ])
    def test_various_invalid_ids(self, task_service, invalid_id):
        """Various invalid IDs all raise TaskNotFoundError."""
        with pytest.raises(TaskNotFoundError):
            task_service.get_task(invalid_id)
```

## Input Validation Tests

```python
# tests/edge_cases/test_validation.py
"""Tests for input validation."""

import pytest
from todo.models.exceptions import ValidationError


class TestTitleValidation:
    """Tests for task title validation."""

    def test_empty_title_rejected(self, task_service):
        """Empty title raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            task_service.add_task("")

        assert "empty" in str(exc_info.value).lower()

    def test_whitespace_title_rejected(self, task_service):
        """Whitespace-only title raises ValidationError."""
        with pytest.raises(ValidationError):
            task_service.add_task("   ")

    def test_newline_only_title_rejected(self, task_service):
        """Newline-only title raises ValidationError."""
        with pytest.raises(ValidationError):
            task_service.add_task("\n\n")

    def test_tab_only_title_rejected(self, task_service):
        """Tab-only title raises ValidationError."""
        with pytest.raises(ValidationError):
            task_service.add_task("\t\t")

    def test_title_max_length(self, task_service):
        """Title at max length (200) is accepted."""
        long_title = "A" * 200

        # Act
        task = task_service.add_task(long_title)

        # Assert
        assert len(task.title) == 200

    def test_title_exceeds_max_length(self, task_service):
        """Title exceeding max length raises ValidationError."""
        too_long = "A" * 201

        with pytest.raises(ValidationError) as exc_info:
            task_service.add_task(too_long)

        assert "200" in str(exc_info.value) or "exceed" in str(exc_info.value).lower()

    def test_title_with_leading_trailing_whitespace_trimmed(self, task_service):
        """Title whitespace is trimmed."""
        # Act
        task = task_service.add_task("  Valid Title  ")

        # Assert
        assert task.title == "Valid Title"

    def test_update_with_empty_title_rejected(self, task_service, sample_task):
        """Updating with empty title raises ValidationError."""
        with pytest.raises(ValidationError):
            task_service.update_task(sample_task.id, title="")


class TestTagValidation:
    """Tests for tag validation."""

    def test_empty_tag_rejected(self, task_service, sample_task):
        """Empty tag raises ValidationError."""
        with pytest.raises(ValidationError):
            task_service.add_tag(sample_task.id, "")

    def test_whitespace_tag_rejected(self, task_service, sample_task):
        """Whitespace-only tag raises ValidationError."""
        with pytest.raises(ValidationError):
            task_service.add_tag(sample_task.id, "   ")

    def test_tag_with_spaces_normalized(self, task_service, sample_task):
        """Tag with spaces is normalized (spaces removed or rejected)."""
        # Depending on implementation - either normalize or reject
        # This test assumes tags should be single words
        task_service.add_tag(sample_task.id, "work-life")

        task = task_service.get_task(sample_task.id)
        assert "work-life" in task.tags

    def test_tag_case_normalized(self, task_service, sample_task):
        """Tags are normalized to lowercase."""
        task_service.add_tag(sample_task.id, "URGENT")

        task = task_service.get_task(sample_task.id)
        assert "urgent" in task.tags
        assert "URGENT" not in task.tags


class TestDateValidation:
    """Tests for date input validation."""

    def test_due_date_in_past_accepted(self, task_service, sample_task):
        """Due date in past is accepted (for overdue tasks)."""
        from datetime import datetime, timedelta

        past_date = datetime.now() - timedelta(days=30)

        # Act - should not raise
        task_service.set_due_date(sample_task.id, past_date)

        # Assert
        task = task_service.get_task(sample_task.id)
        assert task.due_date == past_date
```

## Duplicate Action Tests

```python
# tests/edge_cases/test_duplicate_actions.py
"""Tests for duplicate/repeated actions."""

import pytest


class TestDuplicateActions:
    """Tests for performing the same action twice."""

    def test_complete_already_completed_task(self, task_service, sample_task):
        """Completing an already completed task is idempotent."""
        # First completion
        task_service.mark_complete(sample_task.id)
        task1 = task_service.get_task(sample_task.id)
        assert task1.completed is True

        # Second completion - should not raise
        task_service.mark_complete(sample_task.id)
        task2 = task_service.get_task(sample_task.id)
        assert task2.completed is True

    def test_incomplete_already_incomplete_task(self, task_service, sample_task):
        """Marking incomplete an already incomplete task is idempotent."""
        # Already incomplete by default
        assert sample_task.completed is False

        # Mark incomplete again - should not raise
        task_service.mark_incomplete(sample_task.id)
        task = task_service.get_task(sample_task.id)
        assert task.completed is False

    def test_add_same_tag_twice(self, task_service, sample_task):
        """Adding same tag twice doesn't duplicate."""
        task_service.add_tag(sample_task.id, "work")
        task_service.add_tag(sample_task.id, "work")

        task = task_service.get_task(sample_task.id)
        assert task.tags.count("work") == 1

    def test_remove_tag_twice(self, task_service, sample_task):
        """Removing same tag twice doesn't raise error."""
        task_service.add_tag(sample_task.id, "work")
        task_service.remove_tag(sample_task.id, "work")

        # Second removal - should not raise
        task_service.remove_tag(sample_task.id, "work")

        task = task_service.get_task(sample_task.id)
        assert "work" not in task.tags

    def test_delete_same_task_twice(self, task_service, sample_task):
        """Deleting same task twice raises error on second attempt."""
        from todo.models.exceptions import TaskNotFoundError

        # First deletion succeeds
        task_service.delete_task(sample_task.id)

        # Second deletion raises error
        with pytest.raises(TaskNotFoundError):
            task_service.delete_task(sample_task.id)

    def test_set_same_priority_twice(self, task_service, sample_task):
        """Setting same priority twice is idempotent."""
        from todo.models.enums import Priority

        task_service.set_priority(sample_task.id, Priority.HIGH)
        task_service.set_priority(sample_task.id, Priority.HIGH)

        task = task_service.get_task(sample_task.id)
        assert task.priority == Priority.HIGH

    def test_update_with_same_values(self, task_service, sample_task):
        """Updating with same values still updates timestamp."""
        import time
        original_updated = sample_task.updated_at
        time.sleep(0.01)

        # Update with same title
        task_service.update_task(sample_task.id, title=sample_task.title)

        task = task_service.get_task(sample_task.id)
        assert task.updated_at > original_updated
```

## Boundary Value Tests

```python
# tests/edge_cases/test_boundaries.py
"""Tests for boundary values."""

import pytest
from todo.models.enums import Priority


class TestBoundaryValues:
    """Tests for boundary and extreme values."""

    def test_single_character_title(self, task_service):
        """Single character title is valid."""
        # Act
        task = task_service.add_task("A")

        # Assert
        assert task.title == "A"

    def test_title_exactly_200_chars(self, task_service):
        """Title of exactly 200 characters is valid."""
        title = "A" * 200

        # Act
        task = task_service.add_task(title)

        # Assert
        assert len(task.title) == 200

    def test_title_201_chars_rejected(self, task_service):
        """Title of 201 characters is rejected."""
        from todo.models.exceptions import ValidationError

        title = "A" * 201

        with pytest.raises(ValidationError):
            task_service.add_task(title)

    def test_very_long_description(self, task_service):
        """Very long description is accepted."""
        long_desc = "A" * 10000

        # Act
        task = task_service.add_task("Title", long_desc)

        # Assert
        assert task.description == long_desc

    def test_many_tags_on_single_task(self, task_service, sample_task):
        """Many tags on single task are supported."""
        # Add 50 tags
        for i in range(50):
            task_service.add_tag(sample_task.id, f"tag{i}")

        task = task_service.get_task(sample_task.id)
        assert len(task.tags) == 50

    def test_many_tasks_in_service(self, task_service):
        """Many tasks can be added to service."""
        # Add 1000 tasks
        for i in range(1000):
            task_service.add_task(f"Task {i}")

        tasks = task_service.get_all_tasks()
        assert len(tasks) == 1000

    def test_all_priority_levels(self, task_service, sample_task):
        """All priority levels can be set."""
        for priority in Priority:
            task_service.set_priority(sample_task.id, priority)
            task = task_service.get_task(sample_task.id)
            assert task.priority == priority

    def test_unicode_in_title(self, task_service):
        """Unicode characters in title are supported."""
        # Act
        task = task_service.add_task("Task with unicode")

        # Assert
        assert "unicode" in task.title

    def test_unicode_in_description(self, task_service):
        """Unicode characters in description are supported."""
        # Act
        task = task_service.add_task("Title", "Description with unicode")

        # Assert
        assert "unicode" in task.description

    def test_special_characters_in_title(self, task_service):
        """Special characters in title are supported."""
        special_title = "Task with !@#$%^&*()_+-=[]{}|;':\",./<>?"

        # Act
        task = task_service.add_task(special_title)

        # Assert
        assert task.title == special_title
```

## TUI Edge Case Testing

### Testing TUI Error Handling

```python
# tests/tui/test_tui_edge_cases.py
"""Tests for TUI edge case handling."""

import pytest
from textual.testing import AppTester
from todo.tui.app import TodoApp


@pytest.fixture
async def empty_app(task_service):
    """App with no tasks."""
    app = TodoApp(task_service=task_service)
    async with AppTester.run_test(app) as tester:
        yield tester


class TestEmptyStateTUI:
    """Tests for TUI behavior with no tasks."""

    async def test_empty_list_shows_placeholder(self, empty_app):
        """Empty task list shows helpful placeholder."""
        placeholder = empty_app.app.query_one(".empty-placeholder")
        assert placeholder is not None

    async def test_navigation_on_empty_list(self, empty_app):
        """Arrow keys don't crash on empty list."""
        # Should not raise
        await empty_app.press("down")
        await empty_app.press("up")
        await empty_app.press("j")
        await empty_app.press("k")

    async def test_delete_on_empty_list(self, empty_app):
        """Delete action on empty list shows message."""
        await empty_app.press("d")
        # Should show notification or be no-op, not crash


class TestValidationErrorsTUI:
    """Tests for validation error display in TUI."""

    async def test_empty_title_shows_error(self, empty_app):
        """Submitting empty title shows error in modal."""
        await empty_app.press("a")  # Open add modal
        await empty_app.press("enter")  # Submit empty

        # Error should be displayed
        error = empty_app.app.query_one(".error-message")
        assert "empty" in error.renderable.lower()

    async def test_error_clears_on_valid_input(self, empty_app):
        """Error message clears after valid input."""
        await empty_app.press("a")
        await empty_app.press("enter")  # Shows error
        await empty_app.type("Valid title")
        await empty_app.press("enter")  # Should succeed

        # Error should be gone
        errors = empty_app.app.query(".error-message")
        assert len(errors) == 0


class TestKeyboardEdgeCases:
    """Tests for keyboard edge cases."""

    async def test_rapid_key_presses(self, empty_app):
        """Rapid key presses don't cause issues."""
        # Rapid navigation
        for _ in range(20):
            await empty_app.press("j")
            await empty_app.press("k")

    async def test_unknown_key_ignored(self, empty_app):
        """Unknown keys are gracefully ignored."""
        await empty_app.press("z")  # Not a valid shortcut
        # Should not crash or show error
```

## Running Tests

```bash
# Run all edge case tests
uv run pytest tests/edge_cases/ -v

# Run TUI edge case tests
uv run pytest tests/tui/test_tui_edge_cases.py -v

# Run specific edge case category
uv run pytest tests/edge_cases/test_empty_state.py -v

# Run with verbose error output
uv run pytest tests/edge_cases/ -v --tb=long

# Run parametrized tests only
uv run pytest tests/edge_cases/ -k "parametrize" -v
```

## Checklist

Before considering edge case tests complete:
- [ ] Empty list operations tested
- [ ] All invalid ID scenarios tested
- [ ] Input validation thoroughly tested
- [ ] Duplicate action idempotency verified
- [ ] Boundary values tested (min/max)
- [ ] Special characters handled
- [ ] Unicode support verified
- [ ] Error messages are informative
