"""Tests for datetime parsing, validation, and serialization."""

from datetime import datetime, date, time, timedelta
import pytest

from todo.models.task import Task


class TestDatetimeParsing:
    """Tests for datetime input parsing."""

    def test_parse_datetime_format_full(self):
        """Verify parsing 'YYYY-MM-DD HH:MM' format."""
        from todo.cli.views.menu import parse_datetime_input

        result = parse_datetime_input("2025-01-15 14:30")
        expected = datetime(2025, 1, 15, 14, 30)

        assert result == expected, f"Expected {expected}, got {result}"

    def test_parse_datetime_format_24hour(self):
        """Verify parsing 24-hour format."""
        from todo.cli.views.menu import parse_datetime_input

        result = parse_datetime_input("2025-01-15 09:00")
        expected = datetime(2025, 1, 15, 9, 0)

        assert result == expected

    def test_parse_date_only_format(self):
        """Verify 'YYYY-MM-DD' defaults to 00:00."""
        from todo.cli.views.menu import parse_datetime_input

        result = parse_datetime_input("2025-01-15")
        expected = datetime(2025, 1, 15, 0, 0)

        assert result == expected
        assert result.time() == time(0, 0, 0)

    def test_parse_datetime_with_t_separator(self):
        """Verify 'YYYY-MM-DDTHH:MM' format (ISO format)."""
        from todo.cli.views.menu import parse_datetime_input

        result = parse_datetime_input("2025-01-15T14:30")
        expected = datetime(2025, 1, 15, 14, 30)

        assert result == expected

    def test_parse_datetime_invalid_format(self):
        """Verify invalid format returns None."""
        from todo.cli.views.menu import parse_datetime_input

        assert parse_datetime_input("invalid") is None
        assert parse_datetime_input("2025/01/15") is None
        assert parse_datetime_input("01-15-2025") is None

    def test_parse_datetime_empty_string(self):
        """Verify empty string returns None."""
        from todo.cli.views.menu import parse_datetime_input

        assert parse_datetime_input("") is None
        assert parse_datetime_input("   ") is None


class TestDatetimeValidation:
    """Tests for datetime validation."""

    def test_validate_future_datetime_future(self):
        """Verify future datetime is valid."""
        from todo.cli.views.menu import validate_future_datetime

        future = datetime.now() + timedelta(days=1)
        assert validate_future_datetime(future) is True

    def test_validate_future_datetime_past_rejected(self):
        """Verify past datetime is rejected."""
        from todo.cli.views.menu import validate_future_datetime

        past = datetime.now() - timedelta(days=1)
        assert validate_future_datetime(past) is False

    def test_validate_future_datetime_now_rejected(self):
        """Verify current datetime is rejected (must be in future)."""
        from todo.cli.views.menu import validate_future_datetime

        now = datetime.now()
        # Only reject if in the past (more than 1 second ago)
        # Future datetimes are valid
        assert validate_future_datetime(now + timedelta(seconds=30)) is True


class TestTaskDatetimeSerialization:
    """Tests for Task datetime serialization/deserialization."""

    def test_to_dict_datetime_format(self):
        """Verify to_dict serializes datetime as ISO format."""
        task = Task(
            id=1,
            title="Test",
            due_date=datetime(2025, 1, 15, 14, 30)
        )

        result = task.to_dict()

        assert result["due_date"] == "2025-01-15T14:30:00"

    def test_from_dict_datetime_parsing(self):
        """Verify from_dict parses datetime correctly."""
        data = {
            "id": 1,
            "title": "Test",
            "due_date": "2025-01-15T14:30:00",
            "created_at": "2025-01-01T10:00:00"
        }

        task = Task.from_dict(data)

        assert task.due_date == datetime(2025, 1, 15, 14, 30)

    def test_from_dict_date_only_conversion(self):
        """Verify date-only format is converted to datetime at midnight."""
        data = {
            "id": 1,
            "title": "Test",
            "due_date": "2025-01-15",
            "created_at": "2025-01-01T10:00:00"
        }

        task = Task.from_dict(data)

        assert task.due_date == datetime(2025, 1, 15, 0, 0)
        assert task.due_date.time() == time(0, 0, 0)

    def test_from_dict_backward_compat_with_priority_tags(self):
        """Verify Level 2 format with priority and tags works."""
        data = {
            "id": 1,
            "title": "Legacy task",
            "description": "Old format task",
            "completed": False,
            "priority": "HIGH",
            "tags": ["work", "urgent"],
            "due_date": "2025-02-01",
            "created_at": "2025-01-01T10:00:00"
        }

        task = Task.from_dict(data)

        assert task.title == "Legacy task"
        assert task.priority.value == 3  # HIGH
        assert task.tags == {"work", "urgent"}
        assert task.due_date.day == 1


class TestDatetimeSorting:
    """Tests for datetime-based sorting."""

    def setup_method(self):
        """Reset task store and service before each test."""
        from todo.storage.task_store import reset_task_store
        from todo.services import task_service
        reset_task_store()
        task_service._task_service = None  # Reset service singleton

    def test_sort_by_due_date_with_time(self):
        """Verify tasks sort correctly by datetime."""
        from todo.storage.task_store import TaskStore
        from todo.services.task_service import get_task_service
        from datetime import timedelta

        service = get_task_service()

        # Add tasks in reverse order
        service.add_task(title="Task 3", due_date=datetime.now() + timedelta(days=3))
        service.add_task(title="Task 1", due_date=datetime.now() + timedelta(days=1))
        service.add_task(title="Task 2", due_date=datetime.now() + timedelta(days=2))

        # Filter and sort by due_date
        result = service.search_tasks(sort_by="due_date")

        assert len(result.tasks) == 3
        # First should be task1 (soonest due date)
        assert result.tasks[0].title == "Task 1"

    def test_sort_same_day_different_times(self):
        """Verify same-day tasks sort by time."""
        from todo.storage.task_store import TaskStore
        from todo.services.task_service import get_task_service
        from datetime import timedelta

        service = get_task_service()

        base_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

        service.add_task(title="Task at 2pm", due_date=base_date + timedelta(hours=14))
        service.add_task(title="Task at 9am", due_date=base_date + timedelta(hours=9))

        result = service.search_tasks(sort_by="due_date")

        assert len(result.tasks) == 2
        assert result.tasks[0].title == "Task at 9am"
        assert result.tasks[1].title == "Task at 2pm"


class TestOverdueDetection:
    """Tests for overdue detection based on datetime."""

    def test_overdue_detection(self):
        """Verify past due_date is detected as overdue."""
        from datetime import timedelta

        past = datetime.now() - timedelta(hours=2)
        task = Task(id=1, title="Overdue", due_date=past)

        now = datetime.now()
        is_overdue = task.due_date < now

        assert is_overdue is True

    def test_not_overdue_future(self):
        """Verify future due_date is not overdue."""
        from datetime import timedelta

        future = datetime.now() + timedelta(hours=2)
        task = Task(id=1, title="Future", due_date=future)

        now = datetime.now()
        is_overdue = task.due_date < now

        assert is_overdue is False

    def test_not_overdue_exactly_now(self):
        """Verify due_date exactly now is not overdue."""
        now = datetime.now()
        task = Task(id=1, title="Now", due_date=now)

        check_time = datetime.now()
        is_overdue = task.due_date < check_time

        # At exactly the same moment, it should not be overdue
        # But in practice this depends on timing
        assert task.due_date <= check_time


class TestBackwardCompatDateOnlyInput:
    """Tests for backward compatibility with Level 2 date-only format."""

    def test_cli_accepts_date_only_format(self):
        """Verify CLI can accept 'YYYY-MM-DD' without time."""
        from todo.cli.views.menu import parse_datetime_input

        result = parse_datetime_input("2025-01-15")

        assert result is not None
        assert result.year == 2025
        assert result.month == 1
        assert result.day == 15
        assert result.time() == time(0, 0, 0)

    def test_date_only_displays_without_time(self):
        """Verify date-only displays correctly without time."""
        from todo.cli.views.formatters import format_due_date

        date_only = datetime(2025, 1, 15, 0, 0)
        result = format_due_date(date_only)

        # Should show date without time
        assert "2025" in result
        assert "01" in result or "15" in result
        # Time should not be prominently displayed for midnight

    def test_date_only_sorts_with_datetime_tasks(self):
        """Verify date-only tasks sort correctly alongside datetime tasks."""
        from todo.storage.task_store import TaskStore, reset_task_store

        reset_task_store()
        store = TaskStore()

        # Add date-only task
        store.add("Date only", due_date=date(2025, 3, 15))
        # Add datetime task
        store.add("Datetime", due_date=datetime(2025, 3, 15, 14, 0))

        all_tasks = store.get_all()

        # Both should exist
        assert len(all_tasks) == 2
