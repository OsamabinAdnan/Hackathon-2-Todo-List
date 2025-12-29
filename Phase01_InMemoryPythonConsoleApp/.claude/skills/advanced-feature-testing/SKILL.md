---
name: advanced-feature-testing
description: Test recurring tasks and due-date handling for correct rescheduling using pytest. Use this skill when writing tests for recurrence patterns (daily, weekly, monthly), due date validation, overdue detection, reminder functionality, and automatic task rescheduling.
---

# Advanced Feature Testing

Pytest patterns for testing recurring tasks, due dates, and reminders.

## Overview

This skill provides comprehensive test templates for:
- **Recurring Tasks**: Daily, weekly, monthly recurrence patterns
- **Rescheduling**: Automatic next occurrence generation
- **Due Dates**: Setting, validating, overdue detection
- **Reminders**: Time-based notification triggers

## Test Dependencies

```python
# pyproject.toml - add to dev dependencies
[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
    "freezegun>=1.2.0",  # Time mocking
]
```

## Test File Structure

```
tests/
    unit/
        test_recurrence.py    # Recurring task tests
        test_due_dates.py     # Due date tests
        test_reminders.py     # Reminder tests
```

## Fixtures for Time-Based Tests

```python
# tests/conftest.py (add to existing)

import pytest
from datetime import datetime, timedelta
from freezegun import freeze_time

from todo.models.enums import RecurrencePattern


@pytest.fixture
def task_with_due_date(task_service):
    """Task with due date set to tomorrow."""
    tomorrow = datetime.now() + timedelta(days=1)
    task = task_service.add_task("Due tomorrow")
    task_service.set_due_date(task.id, tomorrow)
    return task_service, task


@pytest.fixture
def overdue_task(task_service):
    """Task with due date in the past."""
    yesterday = datetime.now() - timedelta(days=1)
    task = task_service.add_task("Overdue task")
    task_service.set_due_date(task.id, yesterday)
    return task_service, task


@pytest.fixture
def recurring_daily_task(task_service):
    """Task with daily recurrence."""
    task = task_service.add_task("Daily task")
    task_service.set_recurrence(task.id, RecurrencePattern.DAILY)
    task_service.set_due_date(task.id, datetime.now())
    return task_service, task


@pytest.fixture
def recurring_weekly_task(task_service):
    """Task with weekly recurrence."""
    task = task_service.add_task("Weekly task")
    task_service.set_recurrence(task.id, RecurrencePattern.WEEKLY)
    task_service.set_due_date(task.id, datetime.now())
    return task_service, task


@pytest.fixture
def recurring_monthly_task(task_service):
    """Task with monthly recurrence."""
    task = task_service.add_task("Monthly task")
    task_service.set_recurrence(task.id, RecurrencePattern.MONTHLY)
    task_service.set_due_date(task.id, datetime.now())
    return task_service, task
```

## Recurrence Tests

```python
# tests/unit/test_recurrence.py
"""Tests for recurring task functionality."""

import pytest
from datetime import datetime, timedelta
from freezegun import freeze_time

from todo.models.enums import RecurrencePattern
from todo.models.exceptions import TaskNotFoundError


class TestSetRecurrence:
    """Tests for setting recurrence pattern."""

    def test_set_daily_recurrence(self, task_service, sample_task):
        """Setting DAILY recurrence updates task."""
        # Act
        task_service.set_recurrence(sample_task.id, RecurrencePattern.DAILY)

        # Assert
        task = task_service.get_task(sample_task.id)
        assert task.recurrence == RecurrencePattern.DAILY

    def test_set_weekly_recurrence(self, task_service, sample_task):
        """Setting WEEKLY recurrence updates task."""
        # Act
        task_service.set_recurrence(sample_task.id, RecurrencePattern.WEEKLY)

        # Assert
        task = task_service.get_task(sample_task.id)
        assert task.recurrence == RecurrencePattern.WEEKLY

    def test_set_monthly_recurrence(self, task_service, sample_task):
        """Setting MONTHLY recurrence updates task."""
        # Act
        task_service.set_recurrence(sample_task.id, RecurrencePattern.MONTHLY)

        # Assert
        task = task_service.get_task(sample_task.id)
        assert task.recurrence == RecurrencePattern.MONTHLY

    def test_clear_recurrence(self, recurring_daily_task):
        """Setting NONE removes recurrence."""
        service, task = recurring_daily_task

        # Act
        service.set_recurrence(task.id, RecurrencePattern.NONE)

        # Assert
        updated = service.get_task(task.id)
        assert updated.recurrence == RecurrencePattern.NONE

    def test_set_recurrence_invalid_id_raises_error(self, task_service):
        """Setting recurrence on invalid ID raises error."""
        with pytest.raises(TaskNotFoundError):
            task_service.set_recurrence("invalid", RecurrencePattern.DAILY)

    @pytest.mark.parametrize("pattern", list(RecurrencePattern))
    def test_all_recurrence_patterns_valid(
        self, task_service, sample_task, pattern
    ):
        """All RecurrencePattern values are accepted."""
        # Act
        task_service.set_recurrence(sample_task.id, pattern)

        # Assert
        task = task_service.get_task(sample_task.id)
        assert task.recurrence == pattern


class TestCompleteRecurringTask:
    """Tests for completing recurring tasks."""

    @freeze_time("2024-01-15 10:00:00")
    def test_complete_daily_creates_next_occurrence(self, recurring_daily_task):
        """Completing daily task creates next occurrence."""
        service, task = recurring_daily_task
        original_count = len(service.get_all_tasks())

        # Act
        service.complete_recurring(task.id)

        # Assert
        tasks = service.get_all_tasks()
        assert len(tasks) == original_count + 1

        # Find new task
        new_task = [t for t in tasks if t.id != task.id][0]
        expected_due = datetime(2024, 1, 16, 10, 0, 0)
        assert new_task.due_date == expected_due
        assert new_task.completed is False

    @freeze_time("2024-01-15 10:00:00")
    def test_complete_weekly_creates_next_occurrence(self, recurring_weekly_task):
        """Completing weekly task creates next occurrence 7 days later."""
        service, task = recurring_weekly_task

        # Act
        service.complete_recurring(task.id)

        # Assert
        tasks = service.get_all_tasks()
        new_task = [t for t in tasks if t.id != task.id][0]
        expected_due = datetime(2024, 1, 22, 10, 0, 0)
        assert new_task.due_date == expected_due

    @freeze_time("2024-01-15 10:00:00")
    def test_complete_monthly_creates_next_occurrence(self, recurring_monthly_task):
        """Completing monthly task creates next occurrence."""
        service, task = recurring_monthly_task

        # Act
        service.complete_recurring(task.id)

        # Assert
        tasks = service.get_all_tasks()
        new_task = [t for t in tasks if t.id != task.id][0]
        expected_due = datetime(2024, 2, 15, 10, 0, 0)
        assert new_task.due_date == expected_due

    @freeze_time("2024-01-31 10:00:00")
    def test_monthly_recurrence_handles_month_end(self, task_service):
        """Monthly recurrence from Jan 31 goes to Feb 28/29."""
        task = task_service.add_task("Month end task")
        task_service.set_recurrence(task.id, RecurrencePattern.MONTHLY)
        task_service.set_due_date(task.id, datetime(2024, 1, 31, 10, 0, 0))

        # Act
        task_service.complete_recurring(task.id)

        # Assert - 2024 is leap year, so Feb 29
        tasks = task_service.get_all_tasks()
        new_task = [t for t in tasks if t.id != task.id][0]
        assert new_task.due_date.month == 2
        assert new_task.due_date.day == 29  # Leap year

    def test_complete_recurring_marks_original_complete(self, recurring_daily_task):
        """Completing recurring task marks original as complete."""
        service, task = recurring_daily_task

        # Act
        service.complete_recurring(task.id)

        # Assert
        original = service.get_task(task.id)
        assert original.completed is True

    def test_complete_non_recurring_task_no_new_task(self, task_service, sample_task):
        """Completing non-recurring task doesn't create new task."""
        original_count = len(task_service.get_all_tasks())

        # Act - mark complete normally
        task_service.mark_complete(sample_task.id)

        # Assert
        assert len(task_service.get_all_tasks()) == original_count

    def test_new_recurring_task_inherits_properties(self, task_service):
        """New recurring task inherits title, description, tags, priority."""
        from todo.models.enums import Priority

        task = task_service.add_task("Original", "Description")
        task_service.set_priority(task.id, Priority.HIGH)
        task_service.add_tag(task.id, "work")
        task_service.set_recurrence(task.id, RecurrencePattern.DAILY)
        task_service.set_due_date(task.id, datetime.now())

        # Act
        task_service.complete_recurring(task.id)

        # Assert
        tasks = task_service.get_all_tasks()
        new_task = [t for t in tasks if t.id != task.id][0]
        assert new_task.title == "Original"
        assert new_task.description == "Description"
        assert new_task.priority == Priority.HIGH
        assert "work" in new_task.tags
```

## Due Date Tests

```python
# tests/unit/test_due_dates.py
"""Tests for due date functionality."""

import pytest
from datetime import datetime, timedelta
from freezegun import freeze_time

from todo.models.exceptions import ValidationError


class TestSetDueDate:
    """Tests for setting due dates."""

    def test_set_due_date(self, task_service, sample_task):
        """Setting due date updates task."""
        due = datetime(2024, 12, 31, 23, 59, 59)

        # Act
        task_service.set_due_date(sample_task.id, due)

        # Assert
        task = task_service.get_task(sample_task.id)
        assert task.due_date == due

    def test_clear_due_date(self, task_with_due_date):
        """Setting None clears due date."""
        service, task = task_with_due_date

        # Act
        service.set_due_date(task.id, None)

        # Assert
        updated = service.get_task(task.id)
        assert updated.due_date is None

    def test_set_due_date_updates_timestamp(self, task_service, sample_task):
        """Setting due date updates modified timestamp."""
        import time
        original = sample_task.updated_at
        time.sleep(0.01)

        # Act
        task_service.set_due_date(sample_task.id, datetime.now())

        # Assert
        task = task_service.get_task(sample_task.id)
        assert task.updated_at > original


class TestOverdueDetection:
    """Tests for overdue task detection."""

    @freeze_time("2024-01-15 10:00:00")
    def test_task_is_overdue(self, task_service):
        """Task with past due date is overdue."""
        task = task_service.add_task("Past due")
        past = datetime(2024, 1, 14, 10, 0, 0)
        task_service.set_due_date(task.id, past)

        # Act
        is_overdue = task_service.is_overdue(task.id)

        # Assert
        assert is_overdue is True

    @freeze_time("2024-01-15 10:00:00")
    def test_task_is_not_overdue(self, task_service):
        """Task with future due date is not overdue."""
        task = task_service.add_task("Future due")
        future = datetime(2024, 1, 16, 10, 0, 0)
        task_service.set_due_date(task.id, future)

        # Act
        is_overdue = task_service.is_overdue(task.id)

        # Assert
        assert is_overdue is False

    @freeze_time("2024-01-15 10:00:00")
    def test_task_due_now_is_not_overdue(self, task_service):
        """Task due at exact current time is not overdue."""
        task = task_service.add_task("Due now")
        now = datetime(2024, 1, 15, 10, 0, 0)
        task_service.set_due_date(task.id, now)

        # Act
        is_overdue = task_service.is_overdue(task.id)

        # Assert
        assert is_overdue is False

    def test_task_without_due_date_not_overdue(self, task_service, sample_task):
        """Task without due date is never overdue."""
        # Act
        is_overdue = task_service.is_overdue(sample_task.id)

        # Assert
        assert is_overdue is False

    def test_completed_task_not_overdue(self, overdue_task):
        """Completed task is not considered overdue."""
        service, task = overdue_task
        service.mark_complete(task.id)

        # Act
        is_overdue = service.is_overdue(task.id)

        # Assert
        assert is_overdue is False


class TestGetOverdueTasks:
    """Tests for retrieving overdue tasks."""

    @freeze_time("2024-01-15 10:00:00")
    def test_get_overdue_tasks(self, task_service):
        """Get all overdue tasks."""
        # Setup
        past1 = task_service.add_task("Overdue 1")
        task_service.set_due_date(past1.id, datetime(2024, 1, 10))

        past2 = task_service.add_task("Overdue 2")
        task_service.set_due_date(past2.id, datetime(2024, 1, 14))

        future = task_service.add_task("Future")
        task_service.set_due_date(future.id, datetime(2024, 1, 20))

        no_due = task_service.add_task("No due date")

        # Act
        overdue = task_service.get_overdue_tasks()

        # Assert
        assert len(overdue) == 2
        overdue_ids = {t.id for t in overdue}
        assert past1.id in overdue_ids
        assert past2.id in overdue_ids

    @freeze_time("2024-01-15 10:00:00")
    def test_get_overdue_excludes_completed(self, task_service):
        """Get overdue excludes completed tasks."""
        task = task_service.add_task("Overdue but done")
        task_service.set_due_date(task.id, datetime(2024, 1, 10))
        task_service.mark_complete(task.id)

        # Act
        overdue = task_service.get_overdue_tasks()

        # Assert
        assert len(overdue) == 0


class TestDueDateFiltering:
    """Tests for filtering by due date."""

    @freeze_time("2024-01-15 10:00:00")
    def test_filter_due_today(self, task_service):
        """Filter tasks due today."""
        today = task_service.add_task("Due today")
        task_service.set_due_date(today.id, datetime(2024, 1, 15, 18, 0))

        tomorrow = task_service.add_task("Due tomorrow")
        task_service.set_due_date(tomorrow.id, datetime(2024, 1, 16))

        # Act
        due_today = task_service.get_due_today()

        # Assert
        assert len(due_today) == 1
        assert due_today[0].id == today.id

    @freeze_time("2024-01-15 10:00:00")  # Monday
    def test_filter_due_this_week(self, task_service):
        """Filter tasks due this week."""
        this_week = task_service.add_task("Due this week")
        task_service.set_due_date(this_week.id, datetime(2024, 1, 19))  # Friday

        next_week = task_service.add_task("Due next week")
        task_service.set_due_date(next_week.id, datetime(2024, 1, 25))

        # Act
        due_this_week = task_service.get_due_this_week()

        # Assert
        assert len(due_this_week) == 1
        assert due_this_week[0].id == this_week.id
```

## Reminder Tests

```python
# tests/unit/test_reminders.py
"""Tests for reminder functionality."""

import pytest
from datetime import datetime, timedelta
from freezegun import freeze_time


class TestSetReminder:
    """Tests for setting reminders."""

    def test_set_reminder(self, task_service, sample_task):
        """Setting reminder updates task."""
        reminder_time = datetime(2024, 1, 15, 9, 0, 0)

        # Act
        task_service.set_reminder(sample_task.id, reminder_time)

        # Assert
        task = task_service.get_task(sample_task.id)
        assert task.reminder == reminder_time

    def test_clear_reminder(self, task_service, sample_task):
        """Setting None clears reminder."""
        task_service.set_reminder(sample_task.id, datetime.now())

        # Act
        task_service.set_reminder(sample_task.id, None)

        # Assert
        task = task_service.get_task(sample_task.id)
        assert task.reminder is None


class TestGetDueReminders:
    """Tests for retrieving due reminders."""

    @freeze_time("2024-01-15 10:00:00")
    def test_get_due_reminders(self, task_service):
        """Get tasks with due reminders."""
        # Reminder in past - should trigger
        past_reminder = task_service.add_task("Past reminder")
        task_service.set_reminder(past_reminder.id, datetime(2024, 1, 15, 9, 0))

        # Reminder in future - should not trigger
        future_reminder = task_service.add_task("Future reminder")
        task_service.set_reminder(future_reminder.id, datetime(2024, 1, 15, 11, 0))

        # No reminder
        no_reminder = task_service.add_task("No reminder")

        # Act
        due_reminders = task_service.get_due_reminders()

        # Assert
        assert len(due_reminders) == 1
        assert due_reminders[0].id == past_reminder.id

    @freeze_time("2024-01-15 10:00:00")
    def test_due_reminders_excludes_completed(self, task_service):
        """Due reminders excludes completed tasks."""
        task = task_service.add_task("Completed with reminder")
        task_service.set_reminder(task.id, datetime(2024, 1, 15, 9, 0))
        task_service.mark_complete(task.id)

        # Act
        due_reminders = task_service.get_due_reminders()

        # Assert
        assert len(due_reminders) == 0

    @freeze_time("2024-01-15 10:00:00")
    def test_reminder_exactly_at_current_time(self, task_service):
        """Reminder at exact current time is due."""
        task = task_service.add_task("Exact time reminder")
        task_service.set_reminder(task.id, datetime(2024, 1, 15, 10, 0, 0))

        # Act
        due_reminders = task_service.get_due_reminders()

        # Assert
        assert len(due_reminders) == 1


class TestReminderWithRecurrence:
    """Tests for reminders on recurring tasks."""

    @freeze_time("2024-01-15 10:00:00")
    def test_recurring_task_reminder_carries_forward(self, task_service):
        """New recurring task gets reminder relative to new due date."""
        from todo.models.enums import RecurrencePattern

        # Setup: Task due today at noon with reminder 1 hour before
        task = task_service.add_task("Recurring with reminder")
        task_service.set_due_date(task.id, datetime(2024, 1, 15, 12, 0))
        task_service.set_reminder(task.id, datetime(2024, 1, 15, 11, 0))
        task_service.set_recurrence(task.id, RecurrencePattern.DAILY)

        # Act
        task_service.complete_recurring(task.id)

        # Assert
        tasks = task_service.get_all_tasks()
        new_task = [t for t in tasks if t.id != task.id][0]

        # New due date: tomorrow at noon
        assert new_task.due_date == datetime(2024, 1, 16, 12, 0)
        # New reminder: tomorrow at 11am (1 hour before due)
        assert new_task.reminder == datetime(2024, 1, 16, 11, 0)
```

## TUI Testing Patterns

### Testing Reminders and Due Dates via TUI

```python
# tests/tui/test_reminders.py
"""Tests for reminder display in TUI."""

import pytest
from datetime import datetime, timedelta
from freezegun import freeze_time
from textual.testing import AppTester
from todo.tui.app import TodoApp


@pytest.fixture
async def app_with_overdue(task_service):
    """App with overdue tasks for notification testing."""
    yesterday = datetime.now() - timedelta(days=1)
    task = task_service.add_task("Overdue task")
    task_service.set_due_date(task.id, yesterday)

    app = TodoApp(task_service=task_service)
    async with AppTester.run_test(app) as tester:
        yield tester


class TestReminderNotificationsTUI:
    """Tests for reminder display in TUI."""

    async def test_overdue_tasks_show_indicator(self, app_with_overdue):
        """Overdue tasks display warning indicator."""
        # Find the task item
        task_item = app_with_overdue.app.query_one("TaskItem")

        # Should have overdue styling
        assert "overdue" in task_item.classes

    async def test_reminder_modal_shows_on_launch(self, app_with_overdue):
        """Reminder modal shows when app launches with overdue tasks."""
        # Check for reminder modal or notification
        reminders = app_with_overdue.app.task_service.check_reminders()
        assert len(reminders) > 0


class TestRecurringTasksTUI:
    """Tests for recurring task handling in TUI."""

    async def test_complete_recurring_shows_next(self, app_tester):
        """Completing recurring task shows next occurrence."""
        from todo.models.enums import RecurrencePattern

        # Setup recurring task
        task = app_tester.app.task_service.add_task("Daily task")
        app_tester.app.task_service.set_recurrence(task.id, RecurrencePattern.DAILY)
        app_tester.app.task_service.set_due_date(task.id, datetime.now())

        # Complete via TUI
        await app_tester.press("space")

        # New task should appear in list
        tasks = app_tester.app.task_service.get_all_tasks()
        assert len(tasks) == 2  # Original (completed) + new


class TestDueDateDisplayTUI:
    """Tests for due date display in TUI."""

    @freeze_time("2024-01-15 10:00:00")
    async def test_due_today_highlighted(self, task_service):
        """Tasks due today are highlighted."""
        task = task_service.add_task("Due today")
        task_service.set_due_date(task.id, datetime(2024, 1, 15, 18, 0))

        app = TodoApp(task_service=task_service)
        async with AppTester.run_test(app) as tester:
            task_item = tester.app.query_one("TaskItem")
            assert "due-today" in task_item.classes
```

## Running Tests

```bash
# Run all advanced feature tests
uv run pytest tests/unit/test_recurrence.py tests/unit/test_due_dates.py tests/unit/test_reminders.py -v

# Run TUI reminder tests
uv run pytest tests/tui/test_reminders.py -v

# Run with time-frozen tests only
uv run pytest -k "freeze_time" -v

# Run specific test class
uv run pytest tests/unit/test_recurrence.py::TestCompleteRecurringTask -v
```

## Checklist

Before considering advanced feature tests complete:
- [ ] All recurrence patterns tested (daily, weekly, monthly)
- [ ] Rescheduling creates correct next occurrence
- [ ] Month-end edge cases handled
- [ ] Leap year handling verified
- [ ] Due date setting/clearing tested
- [ ] Overdue detection accurate
- [ ] Reminders trigger at correct time
- [ ] Completed tasks excluded from overdue/reminders
- [ ] Properties inherited on recurring task creation
