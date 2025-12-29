---
name: intermediate-feature-implementation
description: Implement Intermediate Level features for the Todo app including priority assignment (high/medium/low), tags/categories management, search by keyword, filter by status/priority/date, and multi-criteria sorting. Use this skill when extending TaskService with organization and usability features beyond basic CRUD.
---

# Intermediate Feature Implementation

Implement priority assignment, tags/categories, search, filter, and sort operations for the Todo app's Intermediate Level.

## Overview

This skill extends the Basic Level TaskService with organization and usability features:

1. **Priority Assignment** - HIGH, MEDIUM, LOW levels
2. **Tags/Categories** - Multiple labels per task (work, home, urgent)
3. **Search** - Find tasks by keyword in title/description
4. **Filter** - Filter by status, priority, tags, date range
5. **Sort** - Order by multiple criteria (date, priority, alphabetically)

## Feature Summary

| Feature | Methods | Description |
|---------|---------|-------------|
| **Priority** | `set_priority()`, `get_by_priority()` | Assign/query priority levels |
| **Tags** | `add_tag()`, `remove_tag()`, `get_by_tag()` | Manage task categories |
| **Search** | `search()` | Keyword search in title/description |
| **Filter** | `filter_tasks()` | Multi-criteria filtering |
| **Sort** | `sort_tasks()`, `get_sorted()` | Multi-field sorting |

## Priority Implementation

### Priority Enum (from task-data-modeling skill)

```python
from enum import Enum

class Priority(Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

    @classmethod
    def from_string(cls, value: str) -> "Priority":
        """Convert string to Priority enum."""
        try:
            return cls(value.lower())
        except ValueError:
            raise ValueError(f"Invalid priority: {value}. Use high, medium, or low.")
```

### Priority Methods

```python
def set_priority(self, task_id: str, priority: Priority) -> Task:
    """
    Set task priority level.

    Args:
        task_id: The unique task identifier
        priority: Priority enum value (HIGH, MEDIUM, LOW)

    Returns:
        Updated Task instance

    Raises:
        TaskNotFoundError: If task_id does not exist
    """
    task = self.get_task(task_id)
    task.priority = priority
    task.updated_at = datetime.now()
    return task


def get_by_priority(self, priority: Priority) -> list[Task]:
    """
    Get all tasks with specified priority.

    Args:
        priority: Priority level to filter by

    Returns:
        List of tasks matching the priority
    """
    return [t for t in self._tasks.values() if t.priority == priority]


def get_high_priority(self) -> list[Task]:
    """Shortcut for high priority tasks."""
    return self.get_by_priority(Priority.HIGH)
```

## Tags/Categories Implementation

### Tag Methods

```python
def add_tag(self, task_id: str, tag: str) -> Task:
    """
    Add a tag to a task.

    Args:
        task_id: The unique task identifier
        tag: Tag string to add (normalized to lowercase)

    Returns:
        Updated Task instance

    Raises:
        TaskNotFoundError: If task_id does not exist
        ValidationError: If tag is empty
    """
    task = self.get_task(task_id)

    tag = tag.strip().lower()
    if not tag:
        raise ValidationError("Tag cannot be empty")

    if tag not in task.tags:
        task.tags.append(tag)
        task.updated_at = datetime.now()

    return task


def remove_tag(self, task_id: str, tag: str) -> Task:
    """
    Remove a tag from a task.

    Args:
        task_id: The unique task identifier
        tag: Tag string to remove

    Returns:
        Updated Task instance

    Raises:
        TaskNotFoundError: If task_id does not exist
    """
    task = self.get_task(task_id)

    tag = tag.strip().lower()
    if tag in task.tags:
        task.tags.remove(tag)
        task.updated_at = datetime.now()

    return task


def set_tags(self, task_id: str, tags: list[str]) -> Task:
    """
    Replace all tags on a task.

    Args:
        task_id: The unique task identifier
        tags: List of tag strings

    Returns:
        Updated Task instance
    """
    task = self.get_task(task_id)
    task.tags = [t.strip().lower() for t in tags if t.strip()]
    task.updated_at = datetime.now()
    return task


def get_by_tag(self, tag: str) -> list[Task]:
    """
    Get all tasks with a specific tag.

    Args:
        tag: Tag to filter by

    Returns:
        List of tasks containing the tag
    """
    tag = tag.strip().lower()
    return [t for t in self._tasks.values() if tag in t.tags]


def get_all_tags(self) -> list[str]:
    """
    Get all unique tags across all tasks.

    Returns:
        Sorted list of unique tags
    """
    all_tags: set[str] = set()
    for task in self._tasks.values():
        all_tags.update(task.tags)
    return sorted(all_tags)
```

## Search Implementation

### Keyword Search

```python
def search(
    self,
    keyword: str,
    case_sensitive: bool = False,
) -> list[Task]:
    """
    Search tasks by keyword in title and description.

    Args:
        keyword: Search term
        case_sensitive: Whether to match case (default: False)

    Returns:
        List of tasks matching the keyword
    """
    if not keyword.strip():
        return self.get_all_tasks()

    if not case_sensitive:
        keyword = keyword.lower()

    results: list[Task] = []
    for task in self._tasks.values():
        title = task.title if case_sensitive else task.title.lower()
        description = task.description if case_sensitive else task.description.lower()

        if keyword in title or keyword in description:
            results.append(task)

    return results


def search_in_title(self, keyword: str) -> list[Task]:
    """Search only in task titles."""
    keyword = keyword.lower()
    return [
        t for t in self._tasks.values()
        if keyword in t.title.lower()
    ]


def search_in_description(self, keyword: str) -> list[Task]:
    """Search only in task descriptions."""
    keyword = keyword.lower()
    return [
        t for t in self._tasks.values()
        if keyword in t.description.lower()
    ]
```

## Filter Implementation

### Filter Dataclass

```python
from dataclasses import dataclass
from datetime import datetime


@dataclass
class TaskFilter:
    """Filter criteria for tasks."""
    completed: bool | None = None
    priority: Priority | None = None
    tags: list[str] | None = None  # Match ANY of these tags
    tags_all: list[str] | None = None  # Match ALL of these tags
    created_after: datetime | None = None
    created_before: datetime | None = None
    due_before: datetime | None = None
    due_after: datetime | None = None
    has_due_date: bool | None = None
```

### Filter Methods

```python
def filter_tasks(self, criteria: TaskFilter) -> list[Task]:
    """
    Filter tasks by multiple criteria.

    Args:
        criteria: TaskFilter with filter conditions

    Returns:
        List of tasks matching ALL specified criteria
    """
    results = list(self._tasks.values())

    # Filter by completion status
    if criteria.completed is not None:
        results = [t for t in results if t.completed == criteria.completed]

    # Filter by priority
    if criteria.priority is not None:
        results = [t for t in results if t.priority == criteria.priority]

    # Filter by ANY tag
    if criteria.tags:
        tags_lower = [tag.lower() for tag in criteria.tags]
        results = [
            t for t in results
            if any(tag in t.tags for tag in tags_lower)
        ]

    # Filter by ALL tags
    if criteria.tags_all:
        tags_lower = [tag.lower() for tag in criteria.tags_all]
        results = [
            t for t in results
            if all(tag in t.tags for tag in tags_lower)
        ]

    # Filter by created date range
    if criteria.created_after:
        results = [t for t in results if t.created_at >= criteria.created_after]

    if criteria.created_before:
        results = [t for t in results if t.created_at <= criteria.created_before]

    # Filter by due date
    if criteria.has_due_date is True:
        results = [t for t in results if t.due_date is not None]
    elif criteria.has_due_date is False:
        results = [t for t in results if t.due_date is None]

    if criteria.due_before:
        results = [
            t for t in results
            if t.due_date and t.due_date <= criteria.due_before
        ]

    if criteria.due_after:
        results = [
            t for t in results
            if t.due_date and t.due_date >= criteria.due_after
        ]

    return results


def get_pending(self) -> list[Task]:
    """Get all incomplete tasks."""
    return self.filter_tasks(TaskFilter(completed=False))


def get_completed(self) -> list[Task]:
    """Get all completed tasks."""
    return self.filter_tasks(TaskFilter(completed=True))


def get_overdue(self) -> list[Task]:
    """Get tasks past their due date."""
    now = datetime.now()
    return [
        t for t in self._tasks.values()
        if t.due_date and t.due_date < now and not t.completed
    ]
```

## Sort Implementation

### Sort Enum and Options

```python
from enum import Enum
from dataclasses import dataclass


class SortField(Enum):
    """Available sort fields."""
    CREATED_AT = "created_at"
    UPDATED_AT = "updated_at"
    TITLE = "title"
    PRIORITY = "priority"
    DUE_DATE = "due_date"
    COMPLETED = "completed"


class SortOrder(Enum):
    """Sort direction."""
    ASC = "asc"
    DESC = "desc"


@dataclass
class SortCriteria:
    """Single sort criterion."""
    field: SortField
    order: SortOrder = SortOrder.ASC
```

### Sort Methods

```python
def sort_tasks(
    self,
    tasks: list[Task],
    criteria: list[SortCriteria],
) -> list[Task]:
    """
    Sort tasks by multiple criteria.

    Args:
        tasks: List of tasks to sort
        criteria: List of SortCriteria (applied in order)

    Returns:
        New sorted list of tasks
    """
    if not criteria:
        return tasks

    # Priority sort order: HIGH=0, MEDIUM=1, LOW=2
    priority_order = {Priority.HIGH: 0, Priority.MEDIUM: 1, Priority.LOW: 2}

    def sort_key(task: Task) -> tuple:
        keys = []
        for c in criteria:
            value: Any
            if c.field == SortField.TITLE:
                value = task.title.lower()
            elif c.field == SortField.PRIORITY:
                value = priority_order[task.priority]
            elif c.field == SortField.CREATED_AT:
                value = task.created_at
            elif c.field == SortField.UPDATED_AT:
                value = task.updated_at
            elif c.field == SortField.DUE_DATE:
                # None values go to end
                value = task.due_date or datetime.max
            elif c.field == SortField.COMPLETED:
                value = task.completed

            # Reverse for descending
            if c.order == SortOrder.DESC:
                if isinstance(value, bool):
                    value = not value
                elif isinstance(value, str):
                    # Reverse string for desc (hacky but works)
                    value = tuple(-ord(c) for c in value)
                elif isinstance(value, (int, float)):
                    value = -value
                elif isinstance(value, datetime):
                    # Invert datetime for descending
                    value = datetime.max - (value - datetime.min)

            keys.append(value)
        return tuple(keys)

    return sorted(tasks, key=sort_key)


def get_sorted(
    self,
    sort_by: SortField = SortField.CREATED_AT,
    order: SortOrder = SortOrder.DESC,
) -> list[Task]:
    """
    Get all tasks sorted by a single field.

    Args:
        sort_by: Field to sort by
        order: Sort direction (ASC or DESC)

    Returns:
        Sorted list of all tasks
    """
    criteria = [SortCriteria(sort_by, order)]
    return self.sort_tasks(self.get_all_tasks(), criteria)


# Convenience methods
def get_by_priority_order(self) -> list[Task]:
    """Get tasks sorted by priority (HIGH first)."""
    return self.get_sorted(SortField.PRIORITY, SortOrder.ASC)


def get_by_due_date(self) -> list[Task]:
    """Get tasks sorted by due date (earliest first)."""
    return self.get_sorted(SortField.DUE_DATE, SortOrder.ASC)


def get_alphabetically(self) -> list[Task]:
    """Get tasks sorted alphabetically by title."""
    return self.get_sorted(SortField.TITLE, SortOrder.ASC)


def get_recently_updated(self) -> list[Task]:
    """Get tasks sorted by most recently updated."""
    return self.get_sorted(SortField.UPDATED_AT, SortOrder.DESC)
```

## Combined Query Example

```python
def query_tasks(
    self,
    keyword: str | None = None,
    filter_criteria: TaskFilter | None = None,
    sort_criteria: list[SortCriteria] | None = None,
) -> list[Task]:
    """
    Combined search, filter, and sort.

    Args:
        keyword: Optional search term
        filter_criteria: Optional filter conditions
        sort_criteria: Optional sort order

    Returns:
        Filtered and sorted list of tasks
    """
    # Start with all tasks or search results
    if keyword:
        results = self.search(keyword)
    else:
        results = self.get_all_tasks()

    # Apply filters
    if filter_criteria:
        # Convert to set for intersection
        filtered = self.filter_tasks(filter_criteria)
        filtered_ids = {t.id for t in filtered}
        results = [t for t in results if t.id in filtered_ids]

    # Apply sorting
    if sort_criteria:
        results = self.sort_tasks(results, sort_criteria)

    return results
```

## Usage Examples

### Priority

```python
# Set priority
service.set_priority(task_id, Priority.HIGH)

# Get high priority tasks
urgent = service.get_high_priority()
```

### Tags

```python
# Add tags
service.add_tag(task_id, "work")
service.add_tag(task_id, "urgent")

# Get by tag
work_tasks = service.get_by_tag("work")

# List all tags
all_tags = service.get_all_tags()  # ["urgent", "work"]
```

### Search

```python
# Search in title and description
results = service.search("groceries")

# Case sensitive
results = service.search("API", case_sensitive=True)
```

### Filter

```python
# Filter incomplete high-priority tasks
criteria = TaskFilter(
    completed=False,
    priority=Priority.HIGH,
)
urgent_pending = service.filter_tasks(criteria)

# Filter by tag and date
criteria = TaskFilter(
    tags=["work"],
    created_after=datetime(2025, 1, 1),
)
work_2025 = service.filter_tasks(criteria)
```

### Sort

```python
# Sort by priority then due date
criteria = [
    SortCriteria(SortField.PRIORITY, SortOrder.ASC),
    SortCriteria(SortField.DUE_DATE, SortOrder.ASC),
]
sorted_tasks = service.sort_tasks(tasks, criteria)

# Convenience methods
by_priority = service.get_by_priority_order()
by_due = service.get_by_due_date()
alphabetical = service.get_alphabetically()
```

## File Structure

```text
src/todo/
    models/
        __init__.py
        task.py
        enums.py          # Priority, SortField, SortOrder
        filters.py        # TaskFilter, SortCriteria
        exceptions.py
    services/
        __init__.py
        task_service.py   # Extended with intermediate methods
```

## Constitution Compliance

- [x] Type hints on all methods (Principle II)
- [x] Descriptive method names (Principle III)
- [x] Enums for constrained values (Priority, SortField)
- [x] Dataclasses for structured input (TaskFilter, SortCriteria)
- [x] In-memory operations remain instant (Performance)
