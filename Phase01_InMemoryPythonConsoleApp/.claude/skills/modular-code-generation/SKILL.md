---
name: modular-code-generation
description: Generate clean, modular Python code with proper separation of concerns (models, services, storage, utils). Use this skill when implementing features from specs, creating new modules, or scaffolding project structure. Enforces type hints, PEP 8, single responsibility, and constitution-compliant architecture patterns. For TUI-specific patterns, use the tui-designer agent skills.
---

# Modular Code Generation

Generate clean, modular Python code with separation of concerns for the core application layer.

## Overview

This skill provides patterns and templates for generating well-structured Python code that follows the constitution's principles:

- **Separation of Concerns**: Models, Services, Storage, Utils
- **Type Hints**: Full typing on all functions and classes
- **PEP 8 Compliance**: Clean, readable code formatting
- **Single Responsibility**: Each module/function does one thing well

> **Note**: For TUI components, screens, modals, and styling patterns, see the `tui-designer` agent and its specialized skills.

## Project Structure

### Core Layer (this skill)

```text
src/todo/
    __init__.py              # Package init with version
    models/
        __init__.py          # Export all models
        task.py              # Task dataclass
        enums.py             # Priority, RecurrencePattern, etc.
        filters.py           # TaskFilter, SortCriteria
        exceptions.py        # Custom exceptions
    services/
        __init__.py          # Export TaskService
        task_service.py      # Business logic
    storage/
        __init__.py          # Export storage classes
        base.py              # TaskStore Protocol
        memory.py            # InMemoryTaskStore
    utils/
        __init__.py
        formatting.py        # Output formatting helpers
        validation.py        # Input validation helpers

tests/
    __init__.py
    conftest.py              # Shared fixtures
    unit/
        __init__.py
        test_task.py
        test_task_service.py
    integration/
        __init__.py
        test_workflows.py
```

### TUI Layer (see tui-designer agent)

```text
src/todo/tui/               # Managed by tui-designer agent
    app.py                   # See tui-navigation-routing skill
    screens/                 # See tui-navigation-routing skill
    components/              # See tui-output-styling skill
    modals/                  # See tui-input-validation skill
    styles/                  # See tui-output-styling skill

tests/tui/                  # See tui-designer agent testing skills
```

## Module Templates

### 1. Model Module (unchanged)

```python
# src/todo/models/task.py
"""Task model for the Todo application."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Self
from uuid import uuid4

from .enums import Priority, RecurrencePattern


@dataclass
class Task:
    """
    Task entity representing a todo item.

    Attributes:
        id: Unique identifier (UUID4)
        title: Task title (required)
        description: Optional detailed description
        completed: Completion status
        priority: Task priority level
        tags: Category labels
        due_date: Optional deadline
        created_at: Creation timestamp
        updated_at: Last modification timestamp
    """

    title: str
    id: str = field(default_factory=lambda: str(uuid4()))
    description: str = ""
    completed: bool = False
    priority: Priority = Priority.MEDIUM
    tags: list[str] = field(default_factory=list)
    due_date: datetime | None = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self) -> None:
        """Validate task after initialization."""
        if not self.title.strip():
            raise ValueError("Title cannot be empty")

    def mark_complete(self) -> Self:
        """Mark task as completed."""
        self.completed = True
        self.updated_at = datetime.now()
        return self

    def mark_incomplete(self) -> Self:
        """Mark task as incomplete."""
        self.completed = False
        self.updated_at = datetime.now()
        return self
```

### 2. Enum Module (unchanged)

```python
# src/todo/models/enums.py
"""Enumerations for the Todo application."""

from enum import Enum


class Priority(Enum):
    """Task priority levels."""

    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

    @classmethod
    def from_string(cls, value: str) -> "Priority":
        """Convert string to Priority enum."""
        try:
            return cls(value.lower())
        except ValueError:
            valid = ", ".join(p.value for p in cls)
            raise ValueError(f"Invalid priority: {value}. Valid: {valid}")


class RecurrencePattern(Enum):
    """Recurrence frequency patterns."""

    NONE = "none"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"


class SortField(Enum):
    """Available sort fields."""

    CREATED_AT = "created_at"
    UPDATED_AT = "updated_at"
    TITLE = "title"
    PRIORITY = "priority"
    DUE_DATE = "due_date"


class SortOrder(Enum):
    """Sort direction."""

    ASC = "asc"
    DESC = "desc"
```

### 3. Exceptions Module (unchanged)

```python
# src/todo/models/exceptions.py
"""Custom exceptions for the Todo application."""


class TodoAppError(Exception):
    """Base exception for Todo app errors."""

    pass


class TaskNotFoundError(TodoAppError):
    """Raised when a task is not found by ID."""

    def __init__(self, task_id: str) -> None:
        self.task_id = task_id
        super().__init__(f"Task not found: {task_id}")


class ValidationError(TodoAppError):
    """Raised when input validation fails."""

    pass


class StorageError(TodoAppError):
    """Raised when storage operations fail."""

    pass
```

### 4. Service Module (unchanged)

```python
# src/todo/services/task_service.py
"""Task service with business logic."""

from dataclasses import dataclass, field
from datetime import datetime

from todo.models.task import Task
from todo.models.enums import Priority
from todo.models.exceptions import TaskNotFoundError, ValidationError


@dataclass
class TaskService:
    """
    Service layer for Task operations.

    Handles all business logic for task management.
    Uses in-memory storage via internal dictionary.
    """

    _tasks: dict[str, Task] = field(default_factory=dict)

    # === CREATE ===

    def add_task(self, title: str, description: str = "") -> Task:
        """
        Create a new task.

        Args:
            title: Task title (required, 1-200 chars)
            description: Optional description

        Returns:
            Created Task instance

        Raises:
            ValidationError: If title is invalid
        """
        title = self._validate_title(title)

        task = Task(title=title, description=description)
        self._tasks[task.id] = task
        return task

    # === READ ===

    def get_task(self, task_id: str) -> Task:
        """
        Get task by ID.

        Raises:
            TaskNotFoundError: If not found
        """
        if task_id not in self._tasks:
            raise TaskNotFoundError(task_id)
        return self._tasks[task_id]

    def get_all_tasks(self) -> list[Task]:
        """Get all tasks."""
        return list(self._tasks.values())

    # === UPDATE ===

    def update_task(
        self,
        task_id: str,
        title: str | None = None,
        description: str | None = None,
    ) -> Task:
        """
        Update task fields.

        Raises:
            TaskNotFoundError: If not found
            ValidationError: If title is invalid
        """
        task = self.get_task(task_id)

        if title is not None:
            task.title = self._validate_title(title)

        if description is not None:
            task.description = description

        task.updated_at = datetime.now()
        return task

    # === DELETE ===

    def delete_task(self, task_id: str) -> bool:
        """
        Delete task by ID.

        Raises:
            TaskNotFoundError: If not found
        """
        if task_id not in self._tasks:
            raise TaskNotFoundError(task_id)
        del self._tasks[task_id]
        return True

    # === HELPERS ===

    def _validate_title(self, title: str) -> str:
        """Validate and normalize title."""
        title = title.strip()
        if not title:
            raise ValidationError("Title cannot be empty")
        if len(title) > 200:
            raise ValidationError("Title cannot exceed 200 characters")
        return title
```

### 5. Storage Protocol

```python
# src/todo/storage/base.py
"""Storage protocol definition."""

from typing import Protocol

from todo.models.task import Task


class TaskStore(Protocol):
    """Protocol for task storage implementations."""

    def add(self, task: Task) -> Task:
        """Add a task to storage."""
        ...

    def get(self, task_id: str) -> Task | None:
        """Get task by ID, or None if not found."""
        ...

    def get_all(self) -> list[Task]:
        """Get all tasks."""
        ...

    def update(self, task: Task) -> Task:
        """Update an existing task."""
        ...

    def delete(self, task_id: str) -> bool:
        """Delete task by ID. Returns True if deleted."""
        ...

    def clear(self) -> int:
        """Clear all tasks. Returns count deleted."""
        ...
```

### 6. Package Init

```python
# src/todo/__init__.py
"""Todo application package."""

__version__ = "0.1.0"
__author__ = "Your Name"

from todo.models.task import Task
from todo.models.enums import Priority, RecurrencePattern
from todo.services.task_service import TaskService

__all__ = [
    "Task",
    "Priority",
    "RecurrencePattern",
    "TaskService",
]
```

## Code Generation Workflow

```
1. Read spec.md for feature requirements
   |
   v
2. Identify modules needed
   |
   +-- New model? -> Generate in models/
   +-- New service method? -> Add to services/
   +-- New storage? -> Add to storage/
   +-- New utility? -> Add to utils/
   +-- New TUI component? -> Use tui-designer agent skills
   |
   v
3. Generate code with:
   - Type hints on all functions
   - Docstrings with Args/Returns/Raises
   - Single responsibility per function
   - Proper imports (absolute within package)
   |
   v
4. Generate corresponding tests
   |
   v
5. Update __init__.py exports
```

## Code Style Guidelines

### Imports

```python
# Standard library
from dataclasses import dataclass
from datetime import datetime
from typing import Protocol

# Third-party (for core layer - no TUI imports here)
# TUI imports belong in tui-designer agent skills

# Local (absolute imports)
from todo.models.task import Task
from todo.models.exceptions import ValidationError
from todo.services.task_service import TaskService
```

### Service Method Pattern

```python
def service_method(self, param: str) -> Result:
    """
    Perform a service operation.

    Args:
        param: Description of parameter

    Returns:
        Result of the operation

    Raises:
        ValidationError: If param is invalid
        TaskNotFoundError: If task not found
    """
    # Validate inputs
    validated = self._validate_param(param)

    # Perform operation
    result = self._do_operation(validated)

    # Update timestamps if needed
    result.updated_at = datetime.now()

    return result
```

## Constitution Compliance Checklist

When generating code, verify:

- [ ] Type hints on all function parameters and return types
- [ ] Docstrings with Args/Returns/Raises sections
- [ ] Single responsibility per function/class
- [ ] No magic numbers (use constants or enums)
- [ ] Proper exception hierarchy
- [ ] Absolute imports within package
- [ ] F-strings for string formatting
- [ ] Meaningful variable names (no single letters except loops)
- [ ] No premature abstractions
- [ ] Tests mirror source structure

> **Note**: For TUI-specific checklist items (reactive patterns, keyboard bindings, stylesheets), see the `tui-designer` agent skills.
