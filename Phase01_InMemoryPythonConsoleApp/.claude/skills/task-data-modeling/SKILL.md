---
name: task-data-modeling
description: Define in-memory data structures for the Todo app task entity. Use this skill when creating or reviewing the Task model with fields (id, title, description, completed, priority, tags, due_date, recurrence). Provides Python dataclass/Pydantic model patterns with type hints for Phase 1 in-memory storage. Triggers on data model design, Task entity creation, or schema definition tasks.
---

# Task Data Modeling

Define the in-memory data structure for Todo app tasks following the constitution's Architecture First and Clean Code principles.

## Overview

This skill provides the canonical Task model definition for Phase 1 of the In-Memory Python Console Todo App. The model supports all three levels (Basic, Intermediate, Advanced) with proper type hints and Python 3.13+ features.

## Task Entity Schema

### Core Fields (Basic Level)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | `str` | Yes | Unique identifier (UUID4) |
| `title` | `str` | Yes | Task title (1-200 chars) |
| `description` | `str` | No | Optional detailed description |
| `completed` | `bool` | Yes | Completion status (default: False) |
| `created_at` | `datetime` | Yes | Creation timestamp (auto-generated) |
| `updated_at` | `datetime` | Yes | Last modification timestamp |

### Extended Fields (Intermediate Level)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `priority` | `Priority` | No | Enum: HIGH, MEDIUM, LOW (default: MEDIUM) |
| `tags` | `list[str]` | No | Category labels (e.g., "work", "home") |

### Advanced Fields (Advanced Level)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `due_date` | `datetime | None` | No | Optional deadline |
| `recurrence` | `Recurrence | None` | No | Repeat pattern (daily, weekly, monthly) |

## Model Implementation

### Option 1: Dataclass (Recommended for Simplicity)

```python
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Self
from uuid import uuid4


class Priority(Enum):
    """Task priority levels."""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class RecurrencePattern(Enum):
    """Recurrence frequency patterns."""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"


@dataclass
class Recurrence:
    """Recurrence configuration for repeating tasks."""
    pattern: RecurrencePattern
    interval: int = 1  # e.g., every 2 weeks


@dataclass
class Task:
    """
    Task entity for the Todo application.

    Supports Basic, Intermediate, and Advanced features
    with in-memory storage compatibility.
    """
    # Core fields (Basic)
    title: str
    id: str = field(default_factory=lambda: str(uuid4()))
    description: str = ""
    completed: bool = False
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    # Extended fields (Intermediate)
    priority: Priority = Priority.MEDIUM
    tags: list[str] = field(default_factory=list)

    # Advanced fields
    due_date: datetime | None = None
    recurrence: Recurrence | None = None

    def mark_complete(self) -> Self:
        """Mark task as completed and update timestamp."""
        self.completed = True
        self.updated_at = datetime.now()
        return self

    def mark_incomplete(self) -> Self:
        """Mark task as incomplete and update timestamp."""
        self.completed = False
        self.updated_at = datetime.now()
        return self

    def update(self, **kwargs) -> Self:
        """Update task fields and refresh updated_at timestamp."""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self.updated_at = datetime.now()
        return self
```

### Option 2: Pydantic (Recommended for Validation)

```python
from datetime import datetime
from enum import Enum
from typing import Self
from uuid import uuid4

from pydantic import BaseModel, Field, field_validator


class Priority(str, Enum):
    """Task priority levels."""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class RecurrencePattern(str, Enum):
    """Recurrence frequency patterns."""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"


class Recurrence(BaseModel):
    """Recurrence configuration for repeating tasks."""
    pattern: RecurrencePattern
    interval: int = Field(default=1, ge=1)


class Task(BaseModel):
    """
    Task entity for the Todo application.

    Uses Pydantic for automatic validation and serialization.
    """
    # Core fields (Basic)
    id: str = Field(default_factory=lambda: str(uuid4()))
    title: str = Field(..., min_length=1, max_length=200)
    description: str = ""
    completed: bool = False
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    # Extended fields (Intermediate)
    priority: Priority = Priority.MEDIUM
    tags: list[str] = Field(default_factory=list)

    # Advanced fields
    due_date: datetime | None = None
    recurrence: Recurrence | None = None

    @field_validator("title")
    @classmethod
    def title_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Title cannot be empty or whitespace")
        return v.strip()

    model_config = {"validate_assignment": True}
```

## In-Memory Storage Structure

### TaskStore (Dictionary-Based)

```python
from typing import Protocol


class TaskStore(Protocol):
    """Protocol for task storage implementations."""

    def add(self, task: Task) -> Task: ...
    def get(self, task_id: str) -> Task | None: ...
    def get_all(self) -> list[Task]: ...
    def update(self, task_id: str, **kwargs) -> Task | None: ...
    def delete(self, task_id: str) -> bool: ...


class InMemoryTaskStore:
    """In-memory task storage using dictionary."""

    def __init__(self) -> None:
        self._tasks: dict[str, Task] = {}

    def add(self, task: Task) -> Task:
        self._tasks[task.id] = task
        return task

    def get(self, task_id: str) -> Task | None:
        return self._tasks.get(task_id)

    def get_all(self) -> list[Task]:
        return list(self._tasks.values())

    def update(self, task_id: str, **kwargs) -> Task | None:
        if task := self._tasks.get(task_id):
            task.update(**kwargs)
            return task
        return None

    def delete(self, task_id: str) -> bool:
        if task_id in self._tasks:
            del self._tasks[task_id]
            return True
        return False

    def clear(self) -> None:
        self._tasks.clear()
```

## Workflow: Creating the Task Model

1. **Choose implementation** (dataclass vs Pydantic based on validation needs)
2. **Create enums file**: `src/todo/models/enums.py`
3. **Create task model**: `src/todo/models/task.py`
4. **Create storage layer**: `src/todo/storage/memory.py`
5. **Export from package**: `src/todo/models/__init__.py`

## File Structure

```text
src/todo/
    models/
        __init__.py      # Export Task, Priority, Recurrence
        enums.py         # Priority, RecurrencePattern enums
        task.py          # Task dataclass/model
    storage/
        __init__.py      # Export InMemoryTaskStore
        memory.py        # InMemoryTaskStore implementation
```

## Validation Rules

| Field | Validation |
|-------|------------|
| `title` | Required, 1-200 chars, not empty/whitespace |
| `priority` | Must be valid Priority enum value |
| `tags` | List of non-empty strings |
| `due_date` | If set, should be in the future (warn if past) |
| `recurrence.interval` | Must be >= 1 |

## Constitution Compliance

- Type hints on all fields and methods (Principle II)
- Descriptive naming following PEP 8 (Principle III)
- Separation of model from storage (Principle II)
- Protocol for storage abstraction enabling future persistence swap (Principle II)
