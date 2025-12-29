---
name: basic-crud-implementation
description: Implement CRUD operations (Add, Delete, Update, View, Mark Complete) for the Todo app with robust in-memory dict management. Use this skill when implementing TaskService methods, writing CRUD logic, or creating the service layer. Provides Python patterns for create/read/update/delete with proper error handling, return types, and constitution compliance.
---

# Basic CRUD Implementation

Implement Add, Delete, Update, View, and Mark Complete operations for the Todo app's Basic Level with robust in-memory storage management.

## Overview

This skill provides implementation patterns for the five core CRUD operations required by the Basic Level of the Todo app constitution. All operations use in-memory dictionary storage with proper error handling and type hints.

## Operations Summary

| Operation | Method | Input | Output | Error Case |
|-----------|--------|-------|--------|------------|
| **Add** | `add_task()` | title, description? | Task | Validation error |
| **View All** | `get_all_tasks()` | - | list[Task] | - |
| **View One** | `get_task()` | task_id | Task | TaskNotFoundError |
| **Update** | `update_task()` | task_id, fields | Task | TaskNotFoundError |
| **Delete** | `delete_task()` | task_id | bool | TaskNotFoundError |
| **Mark Complete** | `toggle_complete()` | task_id | Task | TaskNotFoundError |

## TaskService Implementation

### Complete Service Class

```python
from dataclasses import dataclass, field
from datetime import datetime
from typing import Self
from uuid import uuid4

from todo.models.task import Task, Priority
from todo.models.exceptions import TaskNotFoundError, ValidationError


@dataclass
class TaskService:
    """
    Service layer for Task CRUD operations.

    Manages in-memory task storage with full CRUD support.
    Constitution compliant: Type hints, descriptive naming, single responsibility.
    """
    _tasks: dict[str, Task] = field(default_factory=dict)

    # ==================== CREATE ====================

    def add_task(
        self,
        title: str,
        description: str = "",
    ) -> Task:
        """
        Create a new task and add to storage.

        Args:
            title: Task title (required, 1-200 chars)
            description: Optional task description

        Returns:
            The created Task instance

        Raises:
            ValidationError: If title is empty or too long
        """
        # Validate title
        title = title.strip()
        if not title:
            raise ValidationError("Title cannot be empty")
        if len(title) > 200:
            raise ValidationError("Title cannot exceed 200 characters")

        # Create task with auto-generated id and timestamps
        task = Task(
            id=str(uuid4()),
            title=title,
            description=description,
            completed=False,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

        # Store and return
        self._tasks[task.id] = task
        return task

    # ==================== READ ====================

    def get_task(self, task_id: str) -> Task:
        """
        Retrieve a single task by ID.

        Args:
            task_id: The unique task identifier

        Returns:
            The Task instance

        Raises:
            TaskNotFoundError: If task_id does not exist
        """
        task = self._tasks.get(task_id)
        if task is None:
            raise TaskNotFoundError(f"Task not found: {task_id}")
        return task

    def get_all_tasks(self) -> list[Task]:
        """
        Retrieve all tasks.

        Returns:
            List of all Task instances (may be empty)
        """
        return list(self._tasks.values())

    def get_tasks_count(self) -> int:
        """Return total number of tasks."""
        return len(self._tasks)

    # ==================== UPDATE ====================

    def update_task(
        self,
        task_id: str,
        title: str | None = None,
        description: str | None = None,
    ) -> Task:
        """
        Update task fields by ID.

        Args:
            task_id: The unique task identifier
            title: New title (optional)
            description: New description (optional)

        Returns:
            The updated Task instance

        Raises:
            TaskNotFoundError: If task_id does not exist
            ValidationError: If new title is invalid
        """
        task = self.get_task(task_id)  # Raises TaskNotFoundError if not found

        # Update title if provided
        if title is not None:
            title = title.strip()
            if not title:
                raise ValidationError("Title cannot be empty")
            if len(title) > 200:
                raise ValidationError("Title cannot exceed 200 characters")
            task.title = title

        # Update description if provided
        if description is not None:
            task.description = description

        # Update timestamp
        task.updated_at = datetime.now()

        return task

    # ==================== DELETE ====================

    def delete_task(self, task_id: str) -> bool:
        """
        Delete a task by ID.

        Args:
            task_id: The unique task identifier

        Returns:
            True if deleted successfully

        Raises:
            TaskNotFoundError: If task_id does not exist
        """
        if task_id not in self._tasks:
            raise TaskNotFoundError(f"Task not found: {task_id}")

        del self._tasks[task_id]
        return True

    # ==================== MARK COMPLETE ====================

    def toggle_complete(self, task_id: str) -> Task:
        """
        Toggle task completion status.

        Args:
            task_id: The unique task identifier

        Returns:
            The updated Task instance with toggled status

        Raises:
            TaskNotFoundError: If task_id does not exist
        """
        task = self.get_task(task_id)  # Raises TaskNotFoundError if not found

        task.completed = not task.completed
        task.updated_at = datetime.now()

        return task

    def mark_complete(self, task_id: str) -> Task:
        """Mark task as completed (sets completed=True)."""
        task = self.get_task(task_id)
        task.completed = True
        task.updated_at = datetime.now()
        return task

    def mark_incomplete(self, task_id: str) -> Task:
        """Mark task as incomplete (sets completed=False)."""
        task = self.get_task(task_id)
        task.completed = False
        task.updated_at = datetime.now()
        return task

    # ==================== UTILITY ====================

    def clear_all(self) -> int:
        """
        Delete all tasks (useful for testing).

        Returns:
            Number of tasks deleted
        """
        count = len(self._tasks)
        self._tasks.clear()
        return count

    def task_exists(self, task_id: str) -> bool:
        """Check if a task exists without raising an error."""
        return task_id in self._tasks
```

## Custom Exceptions

```python
# src/todo/models/exceptions.py

class TodoAppError(Exception):
    """Base exception for Todo app."""
    pass


class TaskNotFoundError(TodoAppError):
    """Raised when a task is not found by ID."""
    pass


class ValidationError(TodoAppError):
    """Raised when input validation fails."""
    pass
```

## Usage Examples

### Add Task

```python
service = TaskService()

# Basic add
task = service.add_task("Buy groceries")
print(f"Created: {task.id} - {task.title}")

# Add with description
task = service.add_task(
    title="Complete project report",
    description="Include Q4 metrics and projections"
)
```

### View Tasks

```python
# Get all tasks
tasks = service.get_all_tasks()
for task in tasks:
    status = "[x]" if task.completed else "[ ]"
    print(f"{status} {task.title}")

# Get single task
task = service.get_task("some-uuid-here")
print(f"Title: {task.title}")
print(f"Completed: {task.completed}")
```

### Update Task

```python
# Update title only
task = service.update_task(task_id, title="New title")

# Update description only
task = service.update_task(task_id, description="New description")

# Update both
task = service.update_task(
    task_id,
    title="Updated title",
    description="Updated description"
)
```

### Delete Task

```python
try:
    service.delete_task(task_id)
    print("Task deleted successfully")
except TaskNotFoundError:
    print("Task not found")
```

### Mark Complete / Toggle

```python
# Toggle completion status
task = service.toggle_complete(task_id)
print(f"Now completed: {task.completed}")

# Explicit mark complete
task = service.mark_complete(task_id)

# Explicit mark incomplete
task = service.mark_incomplete(task_id)
```

## Error Handling Pattern

```python
from todo.models.exceptions import TaskNotFoundError, ValidationError

def handle_crud_operation():
    service = TaskService()

    try:
        # Attempt operation
        task = service.update_task(task_id, title="New title")
        return {"success": True, "task": task}

    except TaskNotFoundError as e:
        return {"success": False, "error": str(e), "code": "NOT_FOUND"}

    except ValidationError as e:
        return {"success": False, "error": str(e), "code": "VALIDATION"}
```

## File Structure

```text
src/todo/
    models/
        __init__.py
        task.py           # Task dataclass
        exceptions.py     # Custom exceptions
    services/
        __init__.py
        task_service.py   # TaskService class
```

## Testing Patterns

See `references/testing-patterns.md` for pytest fixtures and test cases for each CRUD operation.

## Constitution Compliance Checklist

- [x] Type hints on all methods (Principle II)
- [x] Descriptive method names (Principle III)
- [x] Single responsibility per method (Principle III)
- [x] Proper error handling with custom exceptions
- [x] In-memory dict storage (Phase 1 requirement)
- [x] Updated timestamps on modifications
