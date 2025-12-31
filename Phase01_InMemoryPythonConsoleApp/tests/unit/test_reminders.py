"""Tests for reminder detection and notification logic."""

from datetime import datetime, timedelta, time
import pytest

from todo.models.task import Task, Recurrence
from todo.storage.task_store import TaskStore, get_task_store, reset_task_store


class TestReminderDetection:
    """Tests for check_reminders function."""

    def setup_method(self):
        """Reset task store and task service before each test."""
        from todo.services import task_service
        reset_task_store()
        task_service._task_service = None  # Reset service singleton too

    def test_no_reminders_all_completed(self):
        """Verify empty result when all tasks are completed."""
        from todo.services.task_service import check_reminders

        store = get_task_store()
        # Add and complete a task
        task = store.add("Done task", due_date=datetime.now() + timedelta(days=1))
        store.update(task.id, completed=True)

        result = check_reminders()

        assert result.overdue_count == 0
        assert result.due_soon_count == 0
        assert len(result.overdue_tasks) == 0
        assert len(result.due_soon_tasks) == 0

    def test_no_reminders_no_due_dates(self):
        """Verify empty result when no tasks have due dates."""
        from todo.services.task_service import check_reminders

        store = get_task_store()
        store.add("No due date task")

        result = check_reminders()

        assert result.overdue_count == 0
        assert result.due_soon_count == 0

    def test_overdue_detection(self):
        """Verify past due_date is classified as overdue."""
        from todo.services.task_service import check_reminders

        store = get_task_store()
        # Add task due yesterday
        task = store.add(
            "Overdue task",
            due_date=datetime.now() - timedelta(days=1)
        )

        result = check_reminders()

        assert result.overdue_count == 1
        assert len(result.overdue_tasks) == 1
        assert result.overdue_tasks[0].id == task.id

    def test_due_soon_detection(self):
        """Verify within 60 minutes is classified as due soon."""
        from todo.services.task_service import check_reminders

        store = get_task_store()
        # Add task due in 30 minutes
        task = store.add(
            "Due soon task",
            due_date=datetime.now() + timedelta(minutes=30)
        )

        result = check_reminders()

        assert result.due_soon_count == 1
        assert len(result.due_soon_tasks) == 1
        assert result.due_soon_tasks[0].id == task.id

    def test_boundary_exactly_60_minutes(self):
        """Verify threshold boundary at exactly 60 minutes."""
        from todo.services.task_service import check_reminders

        store = get_task_store()
        # Add task due in exactly 60 minutes
        task = store.add(
            "Boundary task",
            due_date=datetime.now() + timedelta(minutes=60)
        )

        result = check_reminders()

        # At exactly 60 minutes, it should be classified as due_soon (not overdue)
        # Now <= due < threshold means due_soon
        assert result.due_soon_count == 1

    def test_over_60_minutes_not_due_soon(self):
        """Verify more than 60 minutes is not due soon."""
        from todo.services.task_service import check_reminders

        store = get_task_store()
        # Add task due in 90 minutes
        store.add(
            "Future task",
            due_date=datetime.now() + timedelta(minutes=90)
        )

        result = check_reminders()

        assert result.overdue_count == 0
        assert result.due_soon_count == 0

    def test_date_only_tasks_excluded(self):
        """Verify tasks with time=00:00:00 are excluded from reminders."""
        from todo.services.task_service import check_reminders
        from datetime import date

        store = get_task_store()
        # Add date-only task (midnight) - use date type which becomes datetime at 00:00:00
        store.add(
            "Date only task",
            due_date=date.today() - timedelta(days=1)  # This will become midnight
        )

        result = check_reminders()

        # Date-only tasks should be excluded from time-based reminders
        assert result.overdue_count == 0
        assert result.due_soon_count == 0

    def test_explicit_time_tasks_included(self):
        """Verify tasks with explicit time (not midnight) are included."""
        from todo.services.task_service import check_reminders

        store = get_task_store()
        # Add task with explicit time (not midnight)
        store.add(
            "Timed task",
            due_date=datetime.now() - timedelta(hours=2)
        )

        result = check_reminders()

        assert result.overdue_count == 1

    def test_completed_tasks_excluded(self):
        """Verify completed=True tasks are excluded from reminders."""
        from todo.services.task_service import check_reminders

        store = get_task_store()
        # Add overdue task and mark complete
        task = store.add(
            "Completed overdue",
            due_date=datetime.now() - timedelta(days=1)
        )
        store.update(task.id, completed=True)

        result = check_reminders()

        assert result.overdue_count == 0

    def test_reminder_counts_accurate(self):
        """Verify overdue_count and due_soon_count are accurate."""
        from todo.services.task_service import check_reminders

        store = get_task_store()
        # Add 2 overdue tasks
        store.add("Overdue 1", due_date=datetime.now() - timedelta(days=1))
        store.add("Overdue 2", due_date=datetime.now() - timedelta(hours=5))
        # Add 1 due soon task
        store.add("Due soon", due_date=datetime.now() + timedelta(minutes=30))
        # Add 1 future task (not reminder)
        store.add("Future", due_date=datetime.now() + timedelta(days=1))

        result = check_reminders()

        assert result.overdue_count == 2
        assert result.due_soon_count == 1

    def test_mixed_tasks_classification(self):
        """Verify correct classification of overdue vs due-soon vs future."""
        from todo.services.task_service import check_reminders

        store = get_task_store()
        overdue = store.add("Overdue", due_date=datetime.now() - timedelta(days=1))
        due_soon = store.add("Due Soon", due_date=datetime.now() + timedelta(minutes=45))
        future = store.add("Future", due_date=datetime.now() + timedelta(hours=3))

        result = check_reminders()

        assert overdue.id in [t.id for t in result.overdue_tasks]
        assert due_soon.id in [t.id for t in result.due_soon_tasks]
        assert future.id not in [t.id for t in result.overdue_tasks]
        assert future.id not in [t.id for t in result.due_soon_tasks]


class TestReminderResult:
    """Tests for ReminderResult dataclass."""

    def test_reminder_result_creation(self):
        """Verify ReminderResult can be created with all fields."""
        from todo.services.results import ReminderResult

        task1 = Task(id=1, title="Task 1")
        task2 = Task(id=2, title="Task 2")

        result = ReminderResult(
            overdue_tasks=[task1],
            due_soon_tasks=[task2],
            overdue_count=1,
            due_soon_count=1
        )

        assert len(result.overdue_tasks) == 1
        assert len(result.due_soon_tasks) == 1
        assert result.overdue_count == 1
        assert result.due_soon_count == 1


class TestHumanizeTimeDiff:
    """Tests for humanize_time_diff helper function."""

    def test_humanize_positive_minutes(self):
        """Verify humanizing positive minutes."""
        from todo.cli.views.formatters import humanize_time_diff

        td = timedelta(minutes=30)
        result = humanize_time_diff(td)

        assert "30" in result
        assert "min" in result.lower()

    def test_humanize_positive_hours(self):
        """Verify humanizing hours and minutes."""
        from todo.cli.views.formatters import humanize_time_diff

        td = timedelta(hours=2, minutes=30)
        result = humanize_time_diff(td)

        assert "2" in result or "30" in result

    def test_humanize_positive_days(self):
        """Verify humanizing days."""
        from todo.cli.views.formatters import humanize_time_diff

        td = timedelta(days=3)
        result = humanize_time_diff(td)

        assert "3" in result
        assert "day" in result.lower()

    def test_humanize_negative_minutes(self):
        """Verify humanizing negative minutes (overdue)."""
        from todo.cli.views.formatters import humanize_time_diff

        td = timedelta(minutes=-30)
        result = humanize_time_diff(td)

        # Should indicate overdue
        assert "30" in result

    def test_humanize_negative_hours(self):
        """Verify humanizing negative hours (overdue)."""
        from todo.cli.views.formatters import humanize_time_diff

        td = timedelta(hours=-2)
        result = humanize_time_diff(td)

        # Should indicate overdue
        assert "2" in result
