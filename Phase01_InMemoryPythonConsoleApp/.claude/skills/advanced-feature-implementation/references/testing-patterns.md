# Testing Patterns for Advanced Features

Pytest fixtures and test cases for recurring tasks, due dates, and reminders.

## Table of Contents

1. [Fixtures](#fixtures)
2. [Recurrence Tests](#recurrence-tests)
3. [Due Date Tests](#due-date-tests)
4. [Overdue Tests](#overdue-tests)
5. [Reminder Tests](#reminder-tests)

## Fixtures

```python
# tests/unit/test_advanced_features.py

import pytest
from datetime import datetime, timedelta
from freezegun import freeze_time

from todo.services.task_service import TaskService
from todo.models.task import Task
from todo.models.enums import RecurrencePattern, ReminderType
from todo.models.recurrence import Recurrence
from todo.models.reminder import Reminder
from todo.models.exceptions import TaskNotFoundError, ValidationError


@pytest.fixture
def service() -> TaskService:
    """Fresh TaskService instance."""
    return TaskService()


@pytest.fixture
def task_with_due_date(service: TaskService) -> Task:
    """Task with a due date set."""
    task = service.add_task("Task with deadline")
    service.set_due_date(task.id, datetime.now() + timedelta(days=1))
    return task


@pytest.fixture
def recurring_task(service: TaskService) -> Task:
    """Daily recurring task."""
    task = service.add_task("Daily standup")
    service.set_due_date(task.id, datetime.now() + timedelta(hours=1))
    service.set_recurrence(task.id, RecurrencePattern.DAILY)
    return task
```

## Recurrence Tests

```python
class TestRecurrence:
    """Tests for recurring task functionality."""

    def test_set_recurrence_daily(self, service: TaskService) -> None:
        """Set daily recurrence."""
        task = service.add_task("Daily task")
        updated = service.set_recurrence(task.id, RecurrencePattern.DAILY)

        assert updated.recurrence is not None
        assert updated.recurrence.pattern == RecurrencePattern.DAILY
        assert updated.recurrence.interval == 1

    def test_set_recurrence_weekly(self, service: TaskService) -> None:
        """Set weekly recurrence."""
        task = service.add_task("Weekly task")
        updated = service.set_recurrence(
            task.id, RecurrencePattern.WEEKLY, interval=2
        )

        assert updated.recurrence.pattern == RecurrencePattern.WEEKLY
        assert updated.recurrence.interval == 2

    def test_set_recurrence_monthly(self, service: TaskService) -> None:
        """Set monthly recurrence."""
        task = service.add_task("Monthly task")
        updated = service.set_recurrence(task.id, RecurrencePattern.MONTHLY)

        assert updated.recurrence.pattern == RecurrencePattern.MONTHLY

    def test_set_recurrence_invalid_interval(self, service: TaskService) -> None:
        """Invalid interval raises ValidationError."""
        task = service.add_task("Task")
        with pytest.raises(ValidationError, match="at least 1"):
            service.set_recurrence(task.id, RecurrencePattern.DAILY, interval=0)

    def test_clear_recurrence(self, recurring_task: Task, service: TaskService) -> None:
        """Clear recurrence from task."""
        assert recurring_task.recurrence is not None

        updated = service.clear_recurrence(recurring_task.id)

        assert updated.recurrence is None

    def test_get_recurring_tasks(self, service: TaskService) -> None:
        """Get all recurring tasks."""
        t1 = service.add_task("Recurring")
        service.set_recurrence(t1.id, RecurrencePattern.DAILY)

        t2 = service.add_task("Not recurring")

        recurring = service.get_recurring_tasks()

        assert len(recurring) == 1
        assert recurring[0].id == t1.id

    @freeze_time("2025-01-01 09:00:00")
    def test_reschedule_recurring_daily(self, service: TaskService) -> None:
        """Reschedule daily task to next day."""
        task = service.add_task("Daily")
        service.set_due_date(task.id, datetime(2025, 1, 1, 9, 0))
        service.set_recurrence(task.id, RecurrencePattern.DAILY)

        rescheduled = service.reschedule_recurring(task.id)

        assert rescheduled.due_date == datetime(2025, 1, 2, 9, 0)
        assert rescheduled.completed is False

    @freeze_time("2025-01-01 09:00:00")
    def test_reschedule_recurring_weekly(self, service: TaskService) -> None:
        """Reschedule weekly task."""
        task = service.add_task("Weekly")
        service.set_due_date(task.id, datetime(2025, 1, 1, 9, 0))
        service.set_recurrence(task.id, RecurrencePattern.WEEKLY)

        rescheduled = service.reschedule_recurring(task.id)

        assert rescheduled.due_date == datetime(2025, 1, 8, 9, 0)

    @freeze_time("2025-01-15 09:00:00")
    def test_reschedule_recurring_monthly(self, service: TaskService) -> None:
        """Reschedule monthly task."""
        task = service.add_task("Monthly")
        service.set_due_date(task.id, datetime(2025, 1, 15, 9, 0))
        service.set_recurrence(task.id, RecurrencePattern.MONTHLY)

        rescheduled = service.reschedule_recurring(task.id)

        assert rescheduled.due_date == datetime(2025, 2, 15, 9, 0)

    def test_reschedule_non_recurring_raises(self, service: TaskService) -> None:
        """Reschedule non-recurring task raises error."""
        task = service.add_task("Not recurring")

        with pytest.raises(ValidationError, match="no recurrence"):
            service.reschedule_recurring(task.id)

    def test_complete_recurring_reschedules(
        self, recurring_task: Task, service: TaskService
    ) -> None:
        """complete_recurring auto-reschedules."""
        original_due = recurring_task.due_date

        result = service.complete_recurring(recurring_task.id)

        assert result.completed is False
        assert result.due_date > original_due

    def test_complete_recurring_non_recurring_marks_complete(
        self, service: TaskService
    ) -> None:
        """complete_recurring on non-recurring just marks complete."""
        task = service.add_task("One-time task")

        result = service.complete_recurring(task.id)

        assert result.completed is True
```

## Due Date Tests

```python
class TestDueDate:
    """Tests for due date management."""

    def test_set_due_date(self, service: TaskService) -> None:
        """Set due date on task."""
        task = service.add_task("Task")
        due = datetime(2025, 12, 31, 17, 0)

        updated = service.set_due_date(task.id, due)

        assert updated.due_date == due

    def test_clear_due_date(
        self, task_with_due_date: Task, service: TaskService
    ) -> None:
        """Clear due date from task."""
        assert task_with_due_date.due_date is not None

        updated = service.clear_due_date(task_with_due_date.id)

        assert updated.due_date is None

    def test_extend_due_date_days(
        self, task_with_due_date: Task, service: TaskService
    ) -> None:
        """Extend due date by days."""
        original = task_with_due_date.due_date

        updated = service.extend_due_date(task_with_due_date.id, days=3)

        assert updated.due_date == original + timedelta(days=3)

    def test_extend_due_date_hours(
        self, task_with_due_date: Task, service: TaskService
    ) -> None:
        """Extend due date by hours."""
        original = task_with_due_date.due_date

        updated = service.extend_due_date(task_with_due_date.id, hours=12)

        assert updated.due_date == original + timedelta(hours=12)

    def test_extend_due_date_combined(
        self, task_with_due_date: Task, service: TaskService
    ) -> None:
        """Extend due date by days and hours."""
        original = task_with_due_date.due_date

        updated = service.extend_due_date(
            task_with_due_date.id, days=1, hours=6
        )

        assert updated.due_date == original + timedelta(days=1, hours=6)

    def test_extend_no_due_date_raises(self, service: TaskService) -> None:
        """Extending task without due date raises error."""
        task = service.add_task("No due date")

        with pytest.raises(ValidationError, match="no due date"):
            service.extend_due_date(task.id, days=1)

    def test_get_tasks_with_due_date(self, service: TaskService) -> None:
        """Get all tasks with due dates."""
        t1 = service.add_task("Has due date")
        service.set_due_date(t1.id, datetime.now() + timedelta(days=1))

        t2 = service.add_task("No due date")

        with_due = service.get_tasks_with_due_date()

        assert len(with_due) == 1
        assert with_due[0].id == t1.id
```

## Overdue Tests

```python
class TestOverdue:
    """Tests for overdue detection."""

    @freeze_time("2025-01-15 12:00:00")
    def test_is_overdue_true(self, service: TaskService) -> None:
        """Task past due date is overdue."""
        task = service.add_task("Overdue task")
        service.set_due_date(task.id, datetime(2025, 1, 14, 12, 0))

        assert service.is_overdue(task.id) is True

    @freeze_time("2025-01-15 12:00:00")
    def test_is_overdue_false_future(self, service: TaskService) -> None:
        """Task with future due date is not overdue."""
        task = service.add_task("Future task")
        service.set_due_date(task.id, datetime(2025, 1, 16, 12, 0))

        assert service.is_overdue(task.id) is False

    def test_is_overdue_false_no_due_date(self, service: TaskService) -> None:
        """Task without due date is not overdue."""
        task = service.add_task("No deadline")

        assert service.is_overdue(task.id) is False

    @freeze_time("2025-01-15 12:00:00")
    def test_is_overdue_false_completed(self, service: TaskService) -> None:
        """Completed task is not overdue even if past due."""
        task = service.add_task("Done task")
        service.set_due_date(task.id, datetime(2025, 1, 14, 12, 0))
        service.mark_complete(task.id)

        assert service.is_overdue(task.id) is False

    @freeze_time("2025-01-15 12:00:00")
    def test_get_overdue(self, service: TaskService) -> None:
        """Get all overdue tasks."""
        # Overdue
        t1 = service.add_task("Overdue 1")
        service.set_due_date(t1.id, datetime(2025, 1, 13, 12, 0))

        t2 = service.add_task("Overdue 2")
        service.set_due_date(t2.id, datetime(2025, 1, 14, 12, 0))

        # Not overdue
        t3 = service.add_task("Future")
        service.set_due_date(t3.id, datetime(2025, 1, 16, 12, 0))

        overdue = service.get_overdue()

        assert len(overdue) == 2
        # Should be sorted oldest first
        assert overdue[0].id == t1.id
        assert overdue[1].id == t2.id

    @freeze_time("2025-01-15 12:00:00")
    def test_get_due_soon(self, service: TaskService) -> None:
        """Get tasks due within specified hours."""
        # Due in 6 hours
        t1 = service.add_task("Soon")
        service.set_due_date(t1.id, datetime(2025, 1, 15, 18, 0))

        # Due in 48 hours
        t2 = service.add_task("Later")
        service.set_due_date(t2.id, datetime(2025, 1, 17, 12, 0))

        due_24h = service.get_due_soon(hours=24)
        due_72h = service.get_due_soon(hours=72)

        assert len(due_24h) == 1
        assert due_24h[0].id == t1.id

        assert len(due_72h) == 2

    @freeze_time("2025-01-15 12:00:00")
    def test_get_due_today(self, service: TaskService) -> None:
        """Get tasks due today."""
        # Due today
        t1 = service.add_task("Today")
        service.set_due_date(t1.id, datetime(2025, 1, 15, 18, 0))

        # Due tomorrow
        t2 = service.add_task("Tomorrow")
        service.set_due_date(t2.id, datetime(2025, 1, 16, 12, 0))

        today = service.get_due_today()

        assert len(today) == 1
        assert today[0].id == t1.id
```

## Reminder Tests

```python
class TestReminders:
    """Tests for reminder system."""

    @freeze_time("2025-01-15 12:00:00")
    def test_get_reminders_overdue(self, service: TaskService) -> None:
        """Overdue tasks generate OVERDUE reminders."""
        task = service.add_task("Overdue")
        service.set_due_date(task.id, datetime(2025, 1, 15, 10, 0))

        reminders = service.get_reminders()

        assert len(reminders) == 1
        assert reminders[0].reminder_type == ReminderType.OVERDUE
        assert "OVERDUE" in reminders[0].message

    @freeze_time("2025-01-15 12:00:00")
    def test_get_reminders_due_now(self, service: TaskService) -> None:
        """Tasks due within 1 hour generate DUE_NOW reminders."""
        task = service.add_task("Due soon")
        service.set_due_date(task.id, datetime(2025, 1, 15, 12, 30))

        reminders = service.get_reminders()

        assert len(reminders) == 1
        assert reminders[0].reminder_type == ReminderType.DUE_NOW
        assert "minutes" in reminders[0].message

    @freeze_time("2025-01-15 12:00:00")
    def test_get_reminders_due_soon(self, service: TaskService) -> None:
        """Tasks due within lookahead generate DUE_SOON reminders."""
        task = service.add_task("Due in 6 hours")
        service.set_due_date(task.id, datetime(2025, 1, 15, 18, 0))

        reminders = service.get_reminders(lookahead_hours=24)

        assert len(reminders) == 1
        assert reminders[0].reminder_type == ReminderType.DUE_SOON

    @freeze_time("2025-01-15 12:00:00")
    def test_get_reminders_sorted_by_urgency(self, service: TaskService) -> None:
        """Reminders are sorted by urgency."""
        # Due soon
        t1 = service.add_task("Soon")
        service.set_due_date(t1.id, datetime(2025, 1, 15, 18, 0))

        # Overdue
        t2 = service.add_task("Overdue")
        service.set_due_date(t2.id, datetime(2025, 1, 15, 10, 0))

        # Due now
        t3 = service.add_task("Now")
        service.set_due_date(t3.id, datetime(2025, 1, 15, 12, 30))

        reminders = service.get_reminders()

        assert reminders[0].reminder_type == ReminderType.OVERDUE
        assert reminders[1].reminder_type == ReminderType.DUE_NOW
        assert reminders[2].reminder_type == ReminderType.DUE_SOON

    def test_get_reminders_excludes_completed(self, service: TaskService) -> None:
        """Completed tasks don't generate reminders."""
        task = service.add_task("Done")
        service.set_due_date(task.id, datetime.now() - timedelta(hours=1))
        service.mark_complete(task.id)

        reminders = service.get_reminders()

        assert len(reminders) == 0

    def test_get_reminders_excludes_no_due_date(self, service: TaskService) -> None:
        """Tasks without due dates don't generate reminders."""
        task = service.add_task("No deadline")

        reminders = service.get_reminders()

        assert len(reminders) == 0
```

## Running Tests

```bash
# Install freezegun for time mocking
uv add --dev freezegun

# Run advanced feature tests
uv run pytest tests/unit/test_advanced_features.py -v

# Run with coverage
uv run pytest tests/unit/test_advanced_features.py \
    --cov=todo.services --cov-report=term-missing
```

## Note on Time Testing

Use `freezegun` library to freeze time for deterministic tests:

```python
from freezegun import freeze_time

@freeze_time("2025-01-15 12:00:00")
def test_something():
    # datetime.now() returns 2025-01-15 12:00:00
    pass
```
