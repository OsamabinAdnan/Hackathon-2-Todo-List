---
name: advanced-feature-implementation
description: Implement Advanced Level features for the Todo app including recurring tasks with automatic rescheduling (daily/weekly/monthly), due date management, overdue detection, and TUI-based notifications. Use this skill when adding recurrence logic, due date handling, or time-based task automation to TaskService.
---

# Advanced Feature Implementation

Implement recurring tasks with auto-rescheduling and due date handling for the Todo app's Advanced Level.

## Overview

This skill extends TaskService with intelligent time-based features:

1. **Recurring Tasks** - Daily, weekly, monthly patterns with auto-rescheduling
2. **Due Date Management** - Set, update, clear due dates
3. **Overdue Detection** - Identify tasks past their deadline
4. **Reminders** - TUI-based notifications for upcoming/overdue tasks

## Feature Summary

| Feature | Methods | Description |
|---------|---------|-------------|
| **Recurrence** | `set_recurrence()`, `clear_recurrence()`, `reschedule_recurring()` | Configure repeat patterns |
| **Due Dates** | `set_due_date()`, `clear_due_date()`, `extend_due_date()` | Manage deadlines |
| **Overdue** | `get_overdue()`, `is_overdue()`, `get_due_soon()` | Track deadline status |
| **Reminders** | `get_reminders()`, `check_reminders()` | TUI notifications |

## Recurrence Implementation

### Recurrence Model (from task-data-modeling skill)

```python
from dataclasses import dataclass
from enum import Enum
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta


class RecurrencePattern(Enum):
    """Recurrence frequency patterns."""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"


@dataclass
class Recurrence:
    """Recurrence configuration for repeating tasks."""
    pattern: RecurrencePattern
    interval: int = 1  # Every N days/weeks/months

    def get_next_date(self, from_date: datetime) -> datetime:
        """Calculate next occurrence from a given date."""
        if self.pattern == RecurrencePattern.DAILY:
            return from_date + timedelta(days=self.interval)
        elif self.pattern == RecurrencePattern.WEEKLY:
            return from_date + timedelta(weeks=self.interval)
        elif self.pattern == RecurrencePattern.MONTHLY:
            return from_date + relativedelta(months=self.interval)
        raise ValueError(f"Unknown pattern: {self.pattern}")
```

### Recurrence Methods

```python
def set_recurrence(
    self,
    task_id: str,
    pattern: RecurrencePattern,
    interval: int = 1,
) -> Task:
    """
    Set task recurrence pattern.

    Args:
        task_id: The unique task identifier
        pattern: RecurrencePattern (DAILY, WEEKLY, MONTHLY)
        interval: Repeat every N periods (default: 1)

    Returns:
        Updated Task instance

    Raises:
        TaskNotFoundError: If task_id does not exist
        ValidationError: If interval < 1
    """
    if interval < 1:
        raise ValidationError("Recurrence interval must be at least 1")

    task = self.get_task(task_id)
    task.recurrence = Recurrence(pattern=pattern, interval=interval)
    task.updated_at = datetime.now()
    return task


def clear_recurrence(self, task_id: str) -> Task:
    """
    Remove recurrence from a task.

    Args:
        task_id: The unique task identifier

    Returns:
        Updated Task instance
    """
    task = self.get_task(task_id)
    task.recurrence = None
    task.updated_at = datetime.now()
    return task


def get_recurring_tasks(self) -> list[Task]:
    """Get all tasks with recurrence configured."""
    return [t for t in self._tasks.values() if t.recurrence is not None]


def reschedule_recurring(self, task_id: str) -> Task:
    """
    Reschedule a completed recurring task to its next occurrence.

    This should be called after marking a recurring task complete.
    Creates a new due date based on the recurrence pattern.

    Args:
        task_id: The unique task identifier

    Returns:
        Updated Task instance with new due date and reset completion

    Raises:
        TaskNotFoundError: If task_id does not exist
        ValidationError: If task has no recurrence configured
    """
    task = self.get_task(task_id)

    if task.recurrence is None:
        raise ValidationError("Task has no recurrence configured")

    # Calculate next due date
    base_date = task.due_date or datetime.now()
    task.due_date = task.recurrence.get_next_date(base_date)

    # Reset completion status
    task.completed = False
    task.updated_at = datetime.now()

    return task


def complete_recurring(self, task_id: str) -> Task:
    """
    Complete a recurring task and auto-reschedule.

    Combines mark_complete + reschedule for convenience.

    Args:
        task_id: The unique task identifier

    Returns:
        Task rescheduled to next occurrence
    """
    task = self.get_task(task_id)

    if task.recurrence is None:
        # Non-recurring: just mark complete
        return self.mark_complete(task_id)

    # Recurring: reschedule to next occurrence
    return self.reschedule_recurring(task_id)
```

## Due Date Implementation

### Due Date Methods

```python
def set_due_date(self, task_id: str, due_date: datetime) -> Task:
    """
    Set task due date.

    Args:
        task_id: The unique task identifier
        due_date: Deadline datetime

    Returns:
        Updated Task instance

    Raises:
        TaskNotFoundError: If task_id does not exist
    """
    task = self.get_task(task_id)
    task.due_date = due_date
    task.updated_at = datetime.now()
    return task


def clear_due_date(self, task_id: str) -> Task:
    """
    Remove due date from a task.

    Args:
        task_id: The unique task identifier

    Returns:
        Updated Task instance
    """
    task = self.get_task(task_id)
    task.due_date = None
    task.updated_at = datetime.now()
    return task


def extend_due_date(
    self,
    task_id: str,
    days: int = 0,
    hours: int = 0,
) -> Task:
    """
    Extend task due date by specified duration.

    Args:
        task_id: The unique task identifier
        days: Days to add
        hours: Hours to add

    Returns:
        Updated Task instance

    Raises:
        ValidationError: If task has no due date
    """
    task = self.get_task(task_id)

    if task.due_date is None:
        raise ValidationError("Task has no due date to extend")

    task.due_date += timedelta(days=days, hours=hours)
    task.updated_at = datetime.now()
    return task


def get_tasks_with_due_date(self) -> list[Task]:
    """Get all tasks that have a due date set."""
    return [t for t in self._tasks.values() if t.due_date is not None]
```

## Overdue Detection

### Overdue Methods

```python
def is_overdue(self, task_id: str) -> bool:
    """
    Check if a task is past its due date.

    Args:
        task_id: The unique task identifier

    Returns:
        True if overdue, False otherwise
    """
    task = self.get_task(task_id)

    if task.due_date is None:
        return False

    if task.completed:
        return False

    return datetime.now() > task.due_date


def get_overdue(self) -> list[Task]:
    """
    Get all incomplete tasks past their due date.

    Returns:
        List of overdue tasks sorted by due date (oldest first)
    """
    now = datetime.now()
    overdue = [
        t for t in self._tasks.values()
        if t.due_date and not t.completed and t.due_date < now
    ]
    return sorted(overdue, key=lambda t: t.due_date)


def get_due_soon(self, hours: int = 24) -> list[Task]:
    """
    Get incomplete tasks due within specified hours.

    Args:
        hours: Lookahead window in hours (default: 24)

    Returns:
        List of tasks due soon, sorted by due date
    """
    now = datetime.now()
    cutoff = now + timedelta(hours=hours)

    due_soon = [
        t for t in self._tasks.values()
        if t.due_date
        and not t.completed
        and now <= t.due_date <= cutoff
    ]
    return sorted(due_soon, key=lambda t: t.due_date)


def get_due_today(self) -> list[Task]:
    """Get incomplete tasks due today."""
    today = datetime.now().date()
    return [
        t for t in self._tasks.values()
        if t.due_date
        and not t.completed
        and t.due_date.date() == today
    ]


def get_due_this_week(self) -> list[Task]:
    """Get incomplete tasks due within the next 7 days."""
    return self.get_due_soon(hours=24 * 7)
```

## Reminder System

### Reminder Data Structures

```python
from dataclasses import dataclass
from enum import Enum


class ReminderType(Enum):
    """Types of reminders."""
    OVERDUE = "overdue"
    DUE_NOW = "due_now"
    DUE_SOON = "due_soon"
    UPCOMING = "upcoming"


@dataclass
class Reminder:
    """A reminder notification for a task."""
    task: Task
    reminder_type: ReminderType
    message: str
    due_in: timedelta | None = None  # Time until due (negative if overdue)
```

### Reminder Methods

```python
def get_reminders(self, lookahead_hours: int = 24) -> list[Reminder]:
    """
    Generate reminders for tasks needing attention.

    Args:
        lookahead_hours: Hours ahead to check for upcoming tasks

    Returns:
        List of Reminder objects sorted by urgency
    """
    reminders: list[Reminder] = []
    now = datetime.now()

    for task in self._tasks.values():
        if task.completed or task.due_date is None:
            continue

        time_diff = task.due_date - now

        if time_diff.total_seconds() < 0:
            # Overdue
            overdue_hours = abs(time_diff.total_seconds()) / 3600
            reminders.append(Reminder(
                task=task,
                reminder_type=ReminderType.OVERDUE,
                message=f"OVERDUE by {overdue_hours:.1f} hours: {task.title}",
                due_in=time_diff,
            ))

        elif time_diff.total_seconds() < 3600:
            # Due within 1 hour
            minutes = time_diff.total_seconds() / 60
            reminders.append(Reminder(
                task=task,
                reminder_type=ReminderType.DUE_NOW,
                message=f"DUE IN {minutes:.0f} minutes: {task.title}",
                due_in=time_diff,
            ))

        elif time_diff.total_seconds() < lookahead_hours * 3600:
            # Due soon
            hours = time_diff.total_seconds() / 3600
            reminders.append(Reminder(
                task=task,
                reminder_type=ReminderType.DUE_SOON,
                message=f"Due in {hours:.1f} hours: {task.title}",
                due_in=time_diff,
            ))

    # Sort by urgency (overdue first, then by time until due)
    type_order = {
        ReminderType.OVERDUE: 0,
        ReminderType.DUE_NOW: 1,
        ReminderType.DUE_SOON: 2,
        ReminderType.UPCOMING: 3,
    }

    return sorted(
        reminders,
        key=lambda r: (type_order[r.reminder_type], r.due_in or timedelta(0))
    )


def check_reminders(self, lookahead_hours: int = 24) -> list[Reminder]:
    """
    Check for reminders needing attention (for TUI integration).

    Args:
        lookahead_hours: Hours ahead to check

    Returns:
        List of Reminder objects for TUI display
    """
    return self.get_reminders(lookahead_hours)


# TUI Integration Example (using Textual)
"""
from textual.widgets import Static
from textual.app import ComposeResult
from textual.containers import Vertical

class ReminderNotification(Static):
    '''Widget to display task reminders in TUI.'''

    def __init__(self, reminder: Reminder) -> None:
        super().__init__()
        self.reminder = reminder

    def compose(self) -> ComposeResult:
        if self.reminder.reminder_type == ReminderType.OVERDUE:
            self.add_class("overdue")
        elif self.reminder.reminder_type == ReminderType.DUE_NOW:
            self.add_class("due-now")
        yield Static(self.reminder.message)


class ReminderPanel(Vertical):
    '''Panel showing all active reminders.'''

    def __init__(self, task_service: TaskService) -> None:
        super().__init__()
        self.task_service = task_service

    def compose(self) -> ComposeResult:
        reminders = self.task_service.check_reminders(lookahead_hours=24)
        if not reminders:
            yield Static("No upcoming deadlines.", classes="no-reminders")
        else:
            for reminder in reminders:
                yield ReminderNotification(reminder)
"""
```

## Usage Examples

### Recurring Tasks

```python
service = TaskService()

# Create a daily standup task
task = service.add_task("Daily standup", "Team sync meeting")
service.set_due_date(task.id, datetime(2025, 1, 1, 9, 0))
service.set_recurrence(task.id, RecurrencePattern.DAILY)

# Complete and auto-reschedule
service.complete_recurring(task.id)
# Task now due on 2025-01-02 09:00, completed=False

# Weekly report
task = service.add_task("Weekly report")
service.set_recurrence(task.id, RecurrencePattern.WEEKLY, interval=1)

# Bi-weekly review
task = service.add_task("Sprint review")
service.set_recurrence(task.id, RecurrencePattern.WEEKLY, interval=2)

# Monthly invoice
task = service.add_task("Send invoice")
service.set_recurrence(task.id, RecurrencePattern.MONTHLY)
```

### Due Date Management

```python
# Set due date
service.set_due_date(task_id, datetime(2025, 12, 31, 17, 0))

# Extend by 2 days
service.extend_due_date(task_id, days=2)

# Clear due date
service.clear_due_date(task_id)

# Check overdue
if service.is_overdue(task_id):
    print("Task is overdue!")

# Get all overdue tasks
overdue = service.get_overdue()
for task in overdue:
    print(f"Overdue: {task.title} (was due {task.due_date})")
```

### Reminders (TUI Integration)

```python
# Get tasks due within 48 hours
due_soon = service.get_due_soon(hours=48)

# Get today's tasks
today = service.get_due_today()

# Get reminders for TUI display
reminders = service.check_reminders(lookahead_hours=24)

# TUI would display these as styled notifications:
# - Overdue tasks: red background, urgent icon
# - Due now tasks: yellow background, warning icon
# - Due soon tasks: normal styling, clock icon

# Example: Using in a Textual modal
"""
from textual.screen import ModalScreen
from textual.widgets import Button, Static
from textual.containers import Vertical

class ReminderModal(ModalScreen):
    '''Modal displaying task reminders.'''

    BINDINGS = [("escape", "dismiss", "Close")]

    def __init__(self, reminders: list[Reminder]) -> None:
        super().__init__()
        self.reminders = reminders

    def compose(self) -> ComposeResult:
        with Vertical(id="reminder-dialog"):
            yield Static("Task Reminders", classes="title")
            for r in self.reminders:
                yield ReminderNotification(r)
            yield Button("Dismiss", variant="primary")
"""
```

## File Structure

```text
src/todo/
    models/
        __init__.py
        task.py
        enums.py           # RecurrencePattern, ReminderType
        recurrence.py      # Recurrence dataclass
        reminder.py        # Reminder dataclass
        exceptions.py
    services/
        __init__.py
        task_service.py    # Extended with advanced methods
```

## Workflow: Auto-Rescheduling

```
1. User completes recurring task
   |
   v
2. Call complete_recurring(task_id)
   |
   v
3. Check if task.recurrence exists
   |
   +-- No recurrence --> Mark complete, done
   |
   +-- Has recurrence --> Calculate next due date
                          |
                          v
                         Reset completed=False
                          |
                          v
                         Update due_date to next occurrence
                          |
                          v
                         Return rescheduled task
```

## Constitution Compliance

- [x] Type hints on all methods (Principle II)
- [x] Descriptive method names (Principle III)
- [x] Enums for constrained values (RecurrencePattern, ReminderType)
- [x] Dataclasses for structured data (Recurrence, Reminder)
- [x] In-memory operations remain instant (Performance)
- [x] TUI-based reminders via Textual widgets (Principle V)
