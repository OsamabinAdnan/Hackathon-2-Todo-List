# Testing Patterns for Intermediate Features

Pytest fixtures and test cases for priority, tags, search, filter, and sort operations.

## Table of Contents

1. [Fixtures](#fixtures)
2. [Priority Tests](#priority-tests)
3. [Tag Tests](#tag-tests)
4. [Search Tests](#search-tests)
5. [Filter Tests](#filter-tests)
6. [Sort Tests](#sort-tests)

## Fixtures

```python
# tests/unit/test_intermediate_features.py

import pytest
from datetime import datetime, timedelta

from todo.services.task_service import TaskService
from todo.models.task import Task
from todo.models.enums import Priority, SortField, SortOrder
from todo.models.filters import TaskFilter, SortCriteria
from todo.models.exceptions import TaskNotFoundError, ValidationError


@pytest.fixture
def service() -> TaskService:
    """Fresh TaskService instance."""
    return TaskService()


@pytest.fixture
def diverse_tasks(service: TaskService) -> TaskService:
    """Service with diverse tasks for testing filters/sorts."""
    # High priority work task
    t1 = service.add_task("Urgent report", "Q4 financials")
    service.set_priority(t1.id, Priority.HIGH)
    service.add_tag(t1.id, "work")
    service.add_tag(t1.id, "urgent")

    # Medium priority home task
    t2 = service.add_task("Buy groceries", "Milk, eggs")
    service.set_priority(t2.id, Priority.MEDIUM)
    service.add_tag(t2.id, "home")

    # Low priority task with due date
    t3 = service.add_task("Clean garage", "")
    service.set_priority(t3.id, Priority.LOW)
    service.add_tag(t3.id, "home")

    # Completed task
    t4 = service.add_task("Send email", "To manager")
    service.mark_complete(t4.id)
    service.add_tag(t4.id, "work")

    return service
```

## Priority Tests

```python
class TestPriority:
    """Tests for priority assignment and filtering."""

    def test_set_priority(self, service: TaskService) -> None:
        """Set task priority."""
        task = service.add_task("Test task")
        assert task.priority == Priority.MEDIUM  # Default

        updated = service.set_priority(task.id, Priority.HIGH)
        assert updated.priority == Priority.HIGH

    def test_set_priority_not_found(self, service: TaskService) -> None:
        """Set priority on non-existent task raises error."""
        with pytest.raises(TaskNotFoundError):
            service.set_priority("fake-id", Priority.HIGH)

    def test_get_by_priority(self, diverse_tasks: TaskService) -> None:
        """Filter tasks by priority."""
        high = diverse_tasks.get_by_priority(Priority.HIGH)
        assert len(high) == 1
        assert high[0].title == "Urgent report"

        medium = diverse_tasks.get_by_priority(Priority.MEDIUM)
        assert len(medium) == 2  # Buy groceries + Send email

    def test_get_high_priority(self, diverse_tasks: TaskService) -> None:
        """Shortcut for high priority tasks."""
        high = diverse_tasks.get_high_priority()
        assert len(high) == 1

    def test_priority_from_string(self) -> None:
        """Convert string to Priority enum."""
        assert Priority.from_string("high") == Priority.HIGH
        assert Priority.from_string("HIGH") == Priority.HIGH
        assert Priority.from_string("Medium") == Priority.MEDIUM

    def test_priority_from_invalid_string(self) -> None:
        """Invalid string raises ValueError."""
        with pytest.raises(ValueError, match="Invalid priority"):
            Priority.from_string("critical")
```

## Tag Tests

```python
class TestTags:
    """Tests for tag management."""

    def test_add_tag(self, service: TaskService) -> None:
        """Add tag to task."""
        task = service.add_task("Test task")
        updated = service.add_tag(task.id, "work")

        assert "work" in updated.tags

    def test_add_tag_normalizes(self, service: TaskService) -> None:
        """Tags are normalized to lowercase."""
        task = service.add_task("Test task")
        service.add_tag(task.id, "  WORK  ")

        assert "work" in task.tags
        assert "WORK" not in task.tags

    def test_add_tag_no_duplicates(self, service: TaskService) -> None:
        """Adding same tag twice doesn't duplicate."""
        task = service.add_task("Test task")
        service.add_tag(task.id, "work")
        service.add_tag(task.id, "work")

        assert task.tags.count("work") == 1

    def test_add_empty_tag_raises(self, service: TaskService) -> None:
        """Empty tag raises ValidationError."""
        task = service.add_task("Test task")
        with pytest.raises(ValidationError, match="cannot be empty"):
            service.add_tag(task.id, "")

    def test_remove_tag(self, service: TaskService) -> None:
        """Remove tag from task."""
        task = service.add_task("Test task")
        service.add_tag(task.id, "work")
        service.remove_tag(task.id, "work")

        assert "work" not in task.tags

    def test_remove_nonexistent_tag(self, service: TaskService) -> None:
        """Removing non-existent tag doesn't error."""
        task = service.add_task("Test task")
        service.remove_tag(task.id, "nonexistent")  # No error

    def test_set_tags(self, service: TaskService) -> None:
        """Replace all tags."""
        task = service.add_task("Test task")
        service.add_tag(task.id, "old")
        service.set_tags(task.id, ["new1", "new2"])

        assert "old" not in task.tags
        assert "new1" in task.tags
        assert "new2" in task.tags

    def test_get_by_tag(self, diverse_tasks: TaskService) -> None:
        """Filter tasks by tag."""
        work_tasks = diverse_tasks.get_by_tag("work")
        assert len(work_tasks) == 2

        home_tasks = diverse_tasks.get_by_tag("home")
        assert len(home_tasks) == 2

    def test_get_all_tags(self, diverse_tasks: TaskService) -> None:
        """Get all unique tags."""
        tags = diverse_tasks.get_all_tags()

        assert "work" in tags
        assert "home" in tags
        assert "urgent" in tags
        assert len(tags) == 3
```

## Search Tests

```python
class TestSearch:
    """Tests for keyword search."""

    def test_search_in_title(self, diverse_tasks: TaskService) -> None:
        """Search finds matches in title."""
        results = diverse_tasks.search("report")
        assert len(results) == 1
        assert results[0].title == "Urgent report"

    def test_search_in_description(self, diverse_tasks: TaskService) -> None:
        """Search finds matches in description."""
        results = diverse_tasks.search("financials")
        assert len(results) == 1

    def test_search_case_insensitive(self, diverse_tasks: TaskService) -> None:
        """Search is case insensitive by default."""
        results = diverse_tasks.search("URGENT")
        assert len(results) == 1

    def test_search_case_sensitive(self, diverse_tasks: TaskService) -> None:
        """Case sensitive search when specified."""
        results = diverse_tasks.search("URGENT", case_sensitive=True)
        assert len(results) == 0

        results = diverse_tasks.search("Urgent", case_sensitive=True)
        assert len(results) == 1

    def test_search_empty_returns_all(self, diverse_tasks: TaskService) -> None:
        """Empty search returns all tasks."""
        results = diverse_tasks.search("")
        assert len(results) == 4

    def test_search_no_matches(self, diverse_tasks: TaskService) -> None:
        """Search with no matches returns empty list."""
        results = diverse_tasks.search("nonexistent")
        assert results == []

    def test_search_partial_match(self, diverse_tasks: TaskService) -> None:
        """Search matches partial words."""
        results = diverse_tasks.search("groc")
        assert len(results) == 1
        assert results[0].title == "Buy groceries"
```

## Filter Tests

```python
class TestFilter:
    """Tests for multi-criteria filtering."""

    def test_filter_by_completed(self, diverse_tasks: TaskService) -> None:
        """Filter by completion status."""
        pending = diverse_tasks.filter_tasks(TaskFilter(completed=False))
        assert len(pending) == 3

        done = diverse_tasks.filter_tasks(TaskFilter(completed=True))
        assert len(done) == 1

    def test_filter_by_priority(self, diverse_tasks: TaskService) -> None:
        """Filter by priority."""
        high = diverse_tasks.filter_tasks(TaskFilter(priority=Priority.HIGH))
        assert len(high) == 1

    def test_filter_by_any_tag(self, diverse_tasks: TaskService) -> None:
        """Filter by ANY of specified tags."""
        criteria = TaskFilter(tags=["work", "urgent"])
        results = diverse_tasks.filter_tasks(criteria)
        # "Urgent report" has both, "Send email" has work
        assert len(results) == 2

    def test_filter_by_all_tags(self, diverse_tasks: TaskService) -> None:
        """Filter by ALL specified tags."""
        criteria = TaskFilter(tags_all=["work", "urgent"])
        results = diverse_tasks.filter_tasks(criteria)
        # Only "Urgent report" has both
        assert len(results) == 1

    def test_filter_combined(self, diverse_tasks: TaskService) -> None:
        """Filter with multiple criteria."""
        criteria = TaskFilter(
            completed=False,
            priority=Priority.HIGH,
            tags=["work"],
        )
        results = diverse_tasks.filter_tasks(criteria)
        assert len(results) == 1
        assert results[0].title == "Urgent report"

    def test_get_pending(self, diverse_tasks: TaskService) -> None:
        """Convenience method for incomplete tasks."""
        pending = diverse_tasks.get_pending()
        assert len(pending) == 3
        assert all(not t.completed for t in pending)

    def test_get_completed(self, diverse_tasks: TaskService) -> None:
        """Convenience method for completed tasks."""
        done = diverse_tasks.get_completed()
        assert len(done) == 1
        assert all(t.completed for t in done)

    def test_filter_by_date_range(self, service: TaskService) -> None:
        """Filter by created date range."""
        # Create tasks at different times
        old = service.add_task("Old task")
        old.created_at = datetime.now() - timedelta(days=30)

        new = service.add_task("New task")

        criteria = TaskFilter(
            created_after=datetime.now() - timedelta(days=7)
        )
        results = service.filter_tasks(criteria)
        assert len(results) == 1
        assert results[0].title == "New task"
```

## Sort Tests

```python
class TestSort:
    """Tests for sorting."""

    def test_sort_by_title(self, diverse_tasks: TaskService) -> None:
        """Sort alphabetically by title."""
        sorted_tasks = diverse_tasks.get_alphabetically()
        titles = [t.title for t in sorted_tasks]

        assert titles == sorted(titles)

    def test_sort_by_priority(self, diverse_tasks: TaskService) -> None:
        """Sort by priority (HIGH first)."""
        sorted_tasks = diverse_tasks.get_by_priority_order()

        # First task should be HIGH priority
        assert sorted_tasks[0].priority == Priority.HIGH
        # Last should be LOW
        assert sorted_tasks[-1].priority == Priority.LOW

    def test_sort_descending(self, diverse_tasks: TaskService) -> None:
        """Sort in descending order."""
        sorted_tasks = diverse_tasks.get_sorted(
            SortField.TITLE,
            SortOrder.DESC
        )
        titles = [t.title for t in sorted_tasks]

        assert titles == sorted(titles, reverse=True)

    def test_sort_multiple_criteria(self, diverse_tasks: TaskService) -> None:
        """Sort by multiple fields."""
        criteria = [
            SortCriteria(SortField.COMPLETED, SortOrder.ASC),
            SortCriteria(SortField.PRIORITY, SortOrder.ASC),
        ]
        sorted_tasks = diverse_tasks.sort_tasks(
            diverse_tasks.get_all_tasks(),
            criteria
        )

        # Incomplete tasks first, then by priority
        assert sorted_tasks[0].completed is False
        assert sorted_tasks[0].priority == Priority.HIGH

    def test_sort_by_due_date(self, service: TaskService) -> None:
        """Sort by due date."""
        t1 = service.add_task("Later")
        t1.due_date = datetime.now() + timedelta(days=7)

        t2 = service.add_task("Sooner")
        t2.due_date = datetime.now() + timedelta(days=1)

        t3 = service.add_task("No due date")

        sorted_tasks = service.get_by_due_date()

        # Sooner first, then Later, then no due date
        assert sorted_tasks[0].title == "Sooner"
        assert sorted_tasks[1].title == "Later"
        assert sorted_tasks[2].title == "No due date"

    def test_get_recently_updated(self, service: TaskService) -> None:
        """Sort by most recently updated."""
        t1 = service.add_task("First")
        t2 = service.add_task("Second")
        t3 = service.add_task("Third")

        # Update first task
        service.update_task(t1.id, title="First Updated")

        recent = service.get_recently_updated()
        assert recent[0].id == t1.id  # Most recently updated
```

## Running Tests

```bash
# Run intermediate feature tests
uv run pytest tests/unit/test_intermediate_features.py -v

# Run specific test class
uv run pytest tests/unit/test_intermediate_features.py::TestFilter -v

# Run with coverage
uv run pytest tests/unit/test_intermediate_features.py \
    --cov=todo.services --cov-report=term-missing
```
