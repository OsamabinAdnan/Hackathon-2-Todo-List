---
name: intermediate-feature-testing
description: Test filtering, search, sorting, and priority/tag behavior using pytest. Use this skill when writing tests for priority management, tag operations, search functionality, filtering by criteria, and sort operations. Provides test patterns for intermediate Todo features.
---

# Intermediate Feature Testing

Pytest patterns for testing priority, tags, search, filter, and sort functionality.

## Overview

This skill provides comprehensive test templates for:
- **Priority**: Setting, getting, filtering by priority
- **Tags**: Adding, removing, filtering by tags
- **Search**: Full-text search across title and description
- **Filter**: Combining multiple filter criteria
- **Sort**: Ordering by various fields

## Test File Structure

```
tests/
    unit/
        test_priority.py      # Priority tests
        test_tags.py          # Tag management tests
        test_search.py        # Search functionality tests
        test_filter.py        # Filter combination tests
        test_sort.py          # Sort operation tests
```

## Additional Fixtures

```python
# tests/conftest.py (add to existing)

@pytest.fixture
def tasks_with_priorities(task_service):
    """Tasks with different priorities."""
    from todo.models.enums import Priority

    high = task_service.add_task("High priority task")
    task_service.set_priority(high.id, Priority.HIGH)

    medium = task_service.add_task("Medium priority task")
    # Medium is default, no change needed

    low = task_service.add_task("Low priority task")
    task_service.set_priority(low.id, Priority.LOW)

    return task_service, {"high": high, "medium": medium, "low": low}


@pytest.fixture
def tasks_with_tags(task_service):
    """Tasks with various tags."""
    work = task_service.add_task("Work task")
    task_service.add_tag(work.id, "work")
    task_service.add_tag(work.id, "urgent")

    personal = task_service.add_task("Personal task")
    task_service.add_tag(personal.id, "personal")

    untagged = task_service.add_task("Untagged task")

    return task_service, {
        "work": work,
        "personal": personal,
        "untagged": untagged
    }


@pytest.fixture
def searchable_tasks(task_service):
    """Tasks for search testing."""
    task_service.add_task("Buy groceries", "Milk, eggs, bread")
    task_service.add_task("Call mom", "Discuss weekend plans")
    task_service.add_task("Review code", "Check pull request #123")
    task_service.add_task("Grocery list", "Create shopping list")
    return task_service
```

## Priority Tests

```python
# tests/unit/test_priority.py
"""Tests for priority management."""

import pytest
from todo.models.enums import Priority
from todo.models.exceptions import TaskNotFoundError


class TestSetPriority:
    """Tests for setting task priority."""

    def test_set_priority_high(self, task_service, sample_task):
        """Setting HIGH priority updates task."""
        # Act
        task_service.set_priority(sample_task.id, Priority.HIGH)

        # Assert
        task = task_service.get_task(sample_task.id)
        assert task.priority == Priority.HIGH

    def test_set_priority_low(self, task_service, sample_task):
        """Setting LOW priority updates task."""
        # Act
        task_service.set_priority(sample_task.id, Priority.LOW)

        # Assert
        task = task_service.get_task(sample_task.id)
        assert task.priority == Priority.LOW

    def test_default_priority_is_medium(self, task_service):
        """New tasks default to MEDIUM priority."""
        # Act
        task = task_service.add_task("New task")

        # Assert
        assert task.priority == Priority.MEDIUM

    def test_set_priority_updates_timestamp(self, task_service, sample_task):
        """Setting priority updates modified timestamp."""
        import time
        original = sample_task.updated_at
        time.sleep(0.01)

        # Act
        task_service.set_priority(sample_task.id, Priority.HIGH)

        # Assert
        task = task_service.get_task(sample_task.id)
        assert task.updated_at > original

    def test_set_priority_invalid_id_raises_error(self, task_service):
        """Setting priority on invalid ID raises error."""
        with pytest.raises(TaskNotFoundError):
            task_service.set_priority("invalid", Priority.HIGH)

    @pytest.mark.parametrize("priority", list(Priority))
    def test_all_priority_values_accepted(
        self, task_service, sample_task, priority
    ):
        """All Priority enum values are valid."""
        # Act
        task_service.set_priority(sample_task.id, priority)

        # Assert
        task = task_service.get_task(sample_task.id)
        assert task.priority == priority


class TestFilterByPriority:
    """Tests for filtering tasks by priority."""

    def test_filter_by_high_priority(self, tasks_with_priorities):
        """Filter returns only HIGH priority tasks."""
        service, tasks = tasks_with_priorities

        # Act
        result = service.filter_by_priority(Priority.HIGH)

        # Assert
        assert len(result) == 1
        assert result[0].id == tasks["high"].id

    def test_filter_by_priority_empty_result(self, task_service, sample_task):
        """Filter returns empty list when no matches."""
        # sample_task is MEDIUM by default

        # Act
        result = task_service.filter_by_priority(Priority.HIGH)

        # Assert
        assert result == []

    def test_filter_by_priority_multiple_matches(self, task_service):
        """Filter returns all matching tasks."""
        # Create multiple HIGH priority tasks
        t1 = task_service.add_task("Task 1")
        t2 = task_service.add_task("Task 2")
        task_service.set_priority(t1.id, Priority.HIGH)
        task_service.set_priority(t2.id, Priority.HIGH)

        # Act
        result = task_service.filter_by_priority(Priority.HIGH)

        # Assert
        assert len(result) == 2
```

## Tag Tests

```python
# tests/unit/test_tags.py
"""Tests for tag management."""

import pytest
from todo.models.exceptions import TaskNotFoundError, ValidationError


class TestAddTag:
    """Tests for adding tags to tasks."""

    def test_add_single_tag(self, task_service, sample_task):
        """Adding a tag adds it to task's tag list."""
        # Act
        task_service.add_tag(sample_task.id, "work")

        # Assert
        task = task_service.get_task(sample_task.id)
        assert "work" in task.tags

    def test_add_multiple_tags(self, task_service, sample_task):
        """Adding multiple tags adds all to list."""
        # Act
        task_service.add_tag(sample_task.id, "work")
        task_service.add_tag(sample_task.id, "urgent")
        task_service.add_tag(sample_task.id, "review")

        # Assert
        task = task_service.get_task(sample_task.id)
        assert set(task.tags) == {"work", "urgent", "review"}

    def test_add_duplicate_tag_no_effect(self, task_service, sample_task):
        """Adding same tag twice doesn't duplicate."""
        # Act
        task_service.add_tag(sample_task.id, "work")
        task_service.add_tag(sample_task.id, "work")

        # Assert
        task = task_service.get_task(sample_task.id)
        assert task.tags.count("work") == 1

    def test_add_tag_normalizes_case(self, task_service, sample_task):
        """Tags are normalized to lowercase."""
        # Act
        task_service.add_tag(sample_task.id, "WORK")

        # Assert
        task = task_service.get_task(sample_task.id)
        assert "work" in task.tags
        assert "WORK" not in task.tags

    def test_add_empty_tag_raises_error(self, task_service, sample_task):
        """Empty tag raises ValidationError."""
        with pytest.raises(ValidationError):
            task_service.add_tag(sample_task.id, "")

    def test_add_tag_invalid_id_raises_error(self, task_service):
        """Adding tag to invalid ID raises error."""
        with pytest.raises(TaskNotFoundError):
            task_service.add_tag("invalid", "work")


class TestRemoveTag:
    """Tests for removing tags from tasks."""

    def test_remove_existing_tag(self, task_service, sample_task):
        """Removing existing tag removes it."""
        task_service.add_tag(sample_task.id, "work")

        # Act
        task_service.remove_tag(sample_task.id, "work")

        # Assert
        task = task_service.get_task(sample_task.id)
        assert "work" not in task.tags

    def test_remove_nonexistent_tag_no_error(self, task_service, sample_task):
        """Removing non-existent tag doesn't raise error."""
        # Act - should not raise
        task_service.remove_tag(sample_task.id, "nonexistent")

        # Assert
        task = task_service.get_task(sample_task.id)
        assert task.tags == []


class TestFilterByTag:
    """Tests for filtering tasks by tags."""

    def test_filter_by_single_tag(self, tasks_with_tags):
        """Filter by tag returns matching tasks."""
        service, tasks = tasks_with_tags

        # Act
        result = service.filter_by_tag("work")

        # Assert
        assert len(result) == 1
        assert result[0].id == tasks["work"].id

    def test_filter_by_tag_case_insensitive(self, tasks_with_tags):
        """Tag filter is case insensitive."""
        service, tasks = tasks_with_tags

        # Act
        result = service.filter_by_tag("WORK")

        # Assert
        assert len(result) == 1

    def test_filter_by_tag_no_matches(self, tasks_with_tags):
        """Filter returns empty list when no matches."""
        service, _ = tasks_with_tags

        # Act
        result = service.filter_by_tag("nonexistent")

        # Assert
        assert result == []

    def test_filter_by_multiple_tags_and(self, tasks_with_tags):
        """Filter by multiple tags with AND logic."""
        service, tasks = tasks_with_tags

        # Act - task must have BOTH tags
        result = service.filter_by_tags(["work", "urgent"], match_all=True)

        # Assert
        assert len(result) == 1
        assert result[0].id == tasks["work"].id

    def test_filter_by_multiple_tags_or(self, tasks_with_tags):
        """Filter by multiple tags with OR logic."""
        service, tasks = tasks_with_tags

        # Act - task can have ANY tag
        result = service.filter_by_tags(["work", "personal"], match_all=False)

        # Assert
        assert len(result) == 2
```

## Search Tests

```python
# tests/unit/test_search.py
"""Tests for search functionality."""

import pytest


class TestSearch:
    """Tests for full-text search."""

    def test_search_by_title(self, searchable_tasks):
        """Search finds matches in title."""
        # Act
        result = searchable_tasks.search("groceries")

        # Assert
        assert len(result) == 1
        assert "groceries" in result[0].title.lower()

    def test_search_by_description(self, searchable_tasks):
        """Search finds matches in description."""
        # Act
        result = searchable_tasks.search("Milk")

        # Assert
        assert len(result) == 1
        assert "Buy groceries" in result[0].title

    def test_search_case_insensitive(self, searchable_tasks):
        """Search is case insensitive."""
        # Act
        result_lower = searchable_tasks.search("groceries")
        result_upper = searchable_tasks.search("GROCERIES")
        result_mixed = searchable_tasks.search("GrOcErIeS")

        # Assert
        assert len(result_lower) == len(result_upper) == len(result_mixed)

    def test_search_partial_match(self, searchable_tasks):
        """Search matches partial words."""
        # Act
        result = searchable_tasks.search("grocer")

        # Assert
        assert len(result) >= 1

    def test_search_multiple_matches(self, searchable_tasks):
        """Search returns all matching tasks."""
        # Act - "grocery" appears in two tasks
        result = searchable_tasks.search("grocery")

        # Assert
        assert len(result) == 2

    def test_search_no_matches(self, searchable_tasks):
        """Search returns empty list when no matches."""
        # Act
        result = searchable_tasks.search("nonexistent")

        # Assert
        assert result == []

    def test_search_empty_query_returns_all(self, searchable_tasks):
        """Empty search query returns all tasks."""
        # Act
        result = searchable_tasks.search("")

        # Assert
        assert len(result) == 4

    def test_search_whitespace_query(self, searchable_tasks):
        """Whitespace-only query returns all tasks."""
        # Act
        result = searchable_tasks.search("   ")

        # Assert
        assert len(result) == 4
```

## Sort Tests

```python
# tests/unit/test_sort.py
"""Tests for sort functionality."""

import pytest
from todo.models.enums import SortField, SortOrder


class TestSort:
    """Tests for task sorting."""

    def test_sort_by_title_ascending(self, task_service):
        """Sort by title A-Z."""
        task_service.add_task("Zebra task")
        task_service.add_task("Apple task")
        task_service.add_task("Mango task")

        # Act
        result = task_service.get_sorted(SortField.TITLE, SortOrder.ASC)

        # Assert
        titles = [t.title for t in result]
        assert titles == ["Apple task", "Mango task", "Zebra task"]

    def test_sort_by_title_descending(self, task_service):
        """Sort by title Z-A."""
        task_service.add_task("Zebra task")
        task_service.add_task("Apple task")
        task_service.add_task("Mango task")

        # Act
        result = task_service.get_sorted(SortField.TITLE, SortOrder.DESC)

        # Assert
        titles = [t.title for t in result]
        assert titles == ["Zebra task", "Mango task", "Apple task"]

    def test_sort_by_priority(self, tasks_with_priorities):
        """Sort by priority (high first)."""
        service, _ = tasks_with_priorities

        # Act
        result = service.get_sorted(SortField.PRIORITY, SortOrder.DESC)

        # Assert
        priorities = [t.priority for t in result]
        assert priorities[0].value == "high"
        assert priorities[-1].value == "low"

    def test_sort_by_created_at_ascending(self, task_service):
        """Sort by creation date (oldest first)."""
        import time
        t1 = task_service.add_task("First")
        time.sleep(0.01)
        t2 = task_service.add_task("Second")
        time.sleep(0.01)
        t3 = task_service.add_task("Third")

        # Act
        result = task_service.get_sorted(SortField.CREATED_AT, SortOrder.ASC)

        # Assert
        ids = [t.id for t in result]
        assert ids == [t1.id, t2.id, t3.id]

    def test_sort_by_created_at_descending(self, task_service):
        """Sort by creation date (newest first)."""
        import time
        t1 = task_service.add_task("First")
        time.sleep(0.01)
        t2 = task_service.add_task("Second")
        time.sleep(0.01)
        t3 = task_service.add_task("Third")

        # Act
        result = task_service.get_sorted(SortField.CREATED_AT, SortOrder.DESC)

        # Assert
        ids = [t.id for t in result]
        assert ids == [t3.id, t2.id, t1.id]

    def test_sort_empty_list(self, task_service):
        """Sorting empty list returns empty list."""
        # Act
        result = task_service.get_sorted(SortField.TITLE, SortOrder.ASC)

        # Assert
        assert result == []

    def test_sort_single_item(self, task_service, sample_task):
        """Sorting single item returns that item."""
        # Act
        result = task_service.get_sorted(SortField.TITLE, SortOrder.ASC)

        # Assert
        assert len(result) == 1
        assert result[0].id == sample_task.id
```

## Combined Filter Tests

```python
# tests/unit/test_filter.py
"""Tests for combining filters."""

import pytest
from todo.models.enums import Priority
from todo.models.filters import TaskFilter


class TestCombinedFilters:
    """Tests for combining multiple filter criteria."""

    def test_filter_by_priority_and_tag(self, task_service):
        """Combine priority and tag filters."""
        # Setup
        t1 = task_service.add_task("High work")
        task_service.set_priority(t1.id, Priority.HIGH)
        task_service.add_tag(t1.id, "work")

        t2 = task_service.add_task("High personal")
        task_service.set_priority(t2.id, Priority.HIGH)
        task_service.add_tag(t2.id, "personal")

        t3 = task_service.add_task("Low work")
        task_service.set_priority(t3.id, Priority.LOW)
        task_service.add_tag(t3.id, "work")

        # Act
        filter_criteria = TaskFilter(
            priority=Priority.HIGH,
            tags=["work"]
        )
        result = task_service.filter_tasks(filter_criteria)

        # Assert
        assert len(result) == 1
        assert result[0].id == t1.id

    def test_filter_completed_tasks_only(self, task_service):
        """Filter to show only completed tasks."""
        t1 = task_service.add_task("Done task")
        task_service.mark_complete(t1.id)
        task_service.add_task("Pending task")

        # Act
        filter_criteria = TaskFilter(completed=True)
        result = task_service.filter_tasks(filter_criteria)

        # Assert
        assert len(result) == 1
        assert result[0].completed is True

    def test_filter_incomplete_tasks_only(self, task_service):
        """Filter to show only incomplete tasks."""
        t1 = task_service.add_task("Done task")
        task_service.mark_complete(t1.id)
        task_service.add_task("Pending task")

        # Act
        filter_criteria = TaskFilter(completed=False)
        result = task_service.filter_tasks(filter_criteria)

        # Assert
        assert len(result) == 1
        assert result[0].completed is False

    def test_search_with_filter(self, task_service):
        """Combine search with filter."""
        t1 = task_service.add_task("Buy groceries")
        task_service.set_priority(t1.id, Priority.HIGH)

        t2 = task_service.add_task("Buy supplies")
        task_service.set_priority(t2.id, Priority.LOW)

        # Act - search "buy" + filter HIGH priority
        filter_criteria = TaskFilter(
            search_query="buy",
            priority=Priority.HIGH
        )
        result = task_service.filter_tasks(filter_criteria)

        # Assert
        assert len(result) == 1
        assert result[0].id == t1.id
```

## TUI Testing Patterns

### Testing Filter/Search via TUI

```python
# tests/tui/test_filtering.py
"""Tests for filter and search via TUI interface."""

import pytest
from textual.testing import AppTester
from todo.tui.app import TodoApp
from todo.models.enums import Priority


@pytest.fixture
async def app_with_tasks(task_service):
    """App with pre-populated tasks for filtering tests."""
    # Create tasks with different priorities and tags
    high = task_service.add_task("High priority task")
    task_service.set_priority(high.id, Priority.HIGH)
    task_service.add_tag(high.id, "work")

    low = task_service.add_task("Low priority task")
    task_service.set_priority(low.id, Priority.LOW)
    task_service.add_tag(low.id, "personal")

    app = TodoApp(task_service=task_service)
    async with AppTester.run_test(app) as tester:
        yield tester


class TestSearchTUI:
    """Tests for search via TUI."""

    async def test_search_shortcut_opens_search(self, app_with_tasks):
        """Pressing '/' opens search input."""
        await app_with_tasks.press("/")

        # Search input should be focused
        search_input = app_with_tasks.app.query_one("#search-input")
        assert search_input.has_focus

    async def test_search_filters_task_list(self, app_with_tasks):
        """Typing in search filters displayed tasks."""
        await app_with_tasks.press("/")
        await app_with_tasks.type("high")

        # Task list should only show matching tasks
        task_list = app_with_tasks.app.query_one("TaskListView")
        visible_tasks = task_list.query("TaskItem")
        assert len(visible_tasks) == 1


class TestPriorityFilterTUI:
    """Tests for priority filtering via TUI."""

    async def test_cycle_priority_with_p(self, app_with_tasks):
        """Pressing 'p' cycles task priority."""
        await app_with_tasks.press("p")

        # Priority should change on selected task
        # Verify via service or UI indicator


class TestTagFilterTUI:
    """Tests for tag filtering via TUI sidebar."""

    async def test_click_tag_filters_list(self, app_with_tasks):
        """Clicking tag in sidebar filters by that tag."""
        # Click on "work" tag in sidebar
        sidebar = app_with_tasks.app.query_one("Sidebar")
        work_tag = sidebar.query_one("[data-tag='work']")
        await app_with_tasks.click(work_tag)

        # Only work-tagged tasks should be visible
```

## Running Tests

```bash
# Run all intermediate feature tests
uv run pytest tests/unit/test_priority.py tests/unit/test_tags.py tests/unit/test_search.py tests/unit/test_sort.py -v

# Run TUI filter tests
uv run pytest tests/tui/test_filtering.py -v

# Run with markers
uv run pytest -m "not slow" -v

# Run specific test class
uv run pytest tests/unit/test_search.py::TestSearch -v
```

## Checklist

Before considering intermediate feature tests complete:
- [ ] All priority operations tested
- [ ] All tag operations tested
- [ ] Search functionality verified
- [ ] Sort in both directions tested
- [ ] Combined filters tested
- [ ] Edge cases covered (empty, no matches)
- [ ] Case insensitivity verified
