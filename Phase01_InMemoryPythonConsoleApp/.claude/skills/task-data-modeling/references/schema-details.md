# Task Schema Details

Comprehensive reference for Task entity fields, types, and constraints.

## Table of Contents

1. [Field Specifications](#field-specifications)
2. [Enum Definitions](#enum-definitions)
3. [Type Aliases](#type-aliases)
4. [Serialization Format](#serialization-format)
5. [Migration Considerations](#migration-considerations)

## Field Specifications

### id: str

- **Type**: `str` (UUID4 format)
- **Generation**: Auto-generated using `uuid.uuid4()`
- **Format**: `xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx`
- **Uniqueness**: Guaranteed unique across all tasks
- **Immutable**: Cannot be changed after creation

```python
from uuid import uuid4
task_id = str(uuid4())  # "a1b2c3d4-e5f6-4789-abcd-ef0123456789"
```

### title: str

- **Type**: `str`
- **Constraints**:
  - Minimum length: 1 character
  - Maximum length: 200 characters
  - Cannot be empty or whitespace-only
- **Normalization**: Strip leading/trailing whitespace

```python
# Valid
title = "Buy groceries"
title = "Complete project report for Q4 2025"

# Invalid
title = ""           # Empty
title = "   "        # Whitespace only
title = "x" * 201    # Too long
```

### description: str

- **Type**: `str`
- **Default**: `""` (empty string)
- **Constraints**: No length limit (practical limit: 10,000 chars)
- **Optional**: Yes

```python
description = "Need to buy milk, eggs, bread, and vegetables from the store"
description = ""  # Valid - optional field
```

### completed: bool

- **Type**: `bool`
- **Default**: `False`
- **States**:
  - `False`: Task is pending/incomplete
  - `True`: Task is done/completed

```python
task.completed = False  # Pending
task.completed = True   # Done
```

### created_at: datetime

- **Type**: `datetime`
- **Generation**: Auto-generated at task creation
- **Timezone**: Local timezone (consider UTC for production)
- **Immutable**: Should not be changed after creation

```python
from datetime import datetime
created_at = datetime.now()  # 2025-12-29 15:30:45.123456
```

### updated_at: datetime

- **Type**: `datetime`
- **Generation**: Auto-generated, updated on any field change
- **Update Triggers**:
  - Any field modification
  - mark_complete() / mark_incomplete()
  - update() method calls

```python
task.update(title="New title")  # updated_at refreshed
```

### priority: Priority

- **Type**: `Priority` enum
- **Default**: `Priority.MEDIUM`
- **Values**: HIGH, MEDIUM, LOW

```python
from enum import Enum

class Priority(Enum):
    HIGH = "high"      # Urgent tasks
    MEDIUM = "medium"  # Normal tasks (default)
    LOW = "low"        # Can wait
```

### tags: list[str]

- **Type**: `list[str]`
- **Default**: `[]` (empty list)
- **Constraints**:
  - Each tag: non-empty string
  - Recommended: lowercase, no spaces
  - Common patterns: "work", "home", "urgent", "personal"

```python
tags = ["work", "urgent"]
tags = ["home", "shopping"]
tags = []  # Valid - no tags
```

### due_date: datetime | None

- **Type**: `datetime | None`
- **Default**: `None`
- **Format**: Full datetime (date + time)
- **Validation**: Warn if date is in the past

```python
from datetime import datetime

due_date = datetime(2025, 12, 31, 23, 59)  # Dec 31, 2025 at 11:59 PM
due_date = None  # No deadline
```

### recurrence: Recurrence | None

- **Type**: `Recurrence | None`
- **Default**: `None`
- **Components**:
  - `pattern`: RecurrencePattern enum
  - `interval`: int (>= 1)

```python
@dataclass
class Recurrence:
    pattern: RecurrencePattern  # DAILY, WEEKLY, MONTHLY
    interval: int = 1           # Every N periods

# Examples
recurrence = Recurrence(RecurrencePattern.DAILY, 1)    # Every day
recurrence = Recurrence(RecurrencePattern.WEEKLY, 2)   # Every 2 weeks
recurrence = Recurrence(RecurrencePattern.MONTHLY, 1)  # Every month
recurrence = None  # Non-recurring task
```

## Enum Definitions

### Priority

```python
class Priority(Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

# String conversion
str(Priority.HIGH.value)  # "high"

# From string
Priority("high")  # Priority.HIGH
```

### RecurrencePattern

```python
class RecurrencePattern(Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"

# Next occurrence calculation
def next_occurrence(current: datetime, pattern: RecurrencePattern, interval: int) -> datetime:
    if pattern == RecurrencePattern.DAILY:
        return current + timedelta(days=interval)
    elif pattern == RecurrencePattern.WEEKLY:
        return current + timedelta(weeks=interval)
    elif pattern == RecurrencePattern.MONTHLY:
        return current + relativedelta(months=interval)
```

## Type Aliases

```python
from typing import TypeAlias

TaskId: TypeAlias = str
TagList: TypeAlias = list[str]
TaskDict: TypeAlias = dict[TaskId, "Task"]
```

## Serialization Format

### JSON Representation

```json
{
  "id": "a1b2c3d4-e5f6-4789-abcd-ef0123456789",
  "title": "Buy groceries",
  "description": "Milk, eggs, bread",
  "completed": false,
  "created_at": "2025-12-29T15:30:45.123456",
  "updated_at": "2025-12-29T15:30:45.123456",
  "priority": "medium",
  "tags": ["home", "shopping"],
  "due_date": "2025-12-30T18:00:00",
  "recurrence": {
    "pattern": "weekly",
    "interval": 1
  }
}
```

### Dictionary Conversion

```python
def to_dict(task: Task) -> dict:
    return {
        "id": task.id,
        "title": task.title,
        "description": task.description,
        "completed": task.completed,
        "created_at": task.created_at.isoformat(),
        "updated_at": task.updated_at.isoformat(),
        "priority": task.priority.value,
        "tags": task.tags,
        "due_date": task.due_date.isoformat() if task.due_date else None,
        "recurrence": {
            "pattern": task.recurrence.pattern.value,
            "interval": task.recurrence.interval
        } if task.recurrence else None
    }
```

## Migration Considerations

### Phase 1 to Phase 2 (Persistence)

When migrating from in-memory to persistent storage:

1. **ID Strategy**: UUID4 remains valid for database primary keys
2. **Datetime Storage**: Store as ISO 8601 strings or database datetime types
3. **Enum Storage**: Store as string values, not enum names
4. **Tags Storage**: Consider separate tags table for normalization
5. **Recurrence Storage**: Consider embedded JSON or separate table

### Backward Compatibility

```python
# Default values ensure backward compatibility
@dataclass
class Task:
    # New fields with defaults don't break existing code
    priority: Priority = Priority.MEDIUM  # Added in Intermediate
    tags: list[str] = field(default_factory=list)  # Added in Intermediate
    due_date: datetime | None = None  # Added in Advanced
    recurrence: Recurrence | None = None  # Added in Advanced
```
