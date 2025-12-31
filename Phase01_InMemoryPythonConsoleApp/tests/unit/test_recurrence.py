"""Tests for recurrence calculation and auto-reschedule logic."""

from datetime import datetime, timedelta, date
import pytest

from todo.models.task import Task, Recurrence
from todo.storage.task_store import TaskStore, get_task_store, reset_task_store


class TestRecurrenceCalculation:
    """Tests for calculate_next_occurrence function."""

    def test_daily_recurrence_calculation(self):
        """Verify DAILY adds 1 day."""
        from todo.services.task_service import calculate_next_occurrence

        due_date = datetime(2025, 1, 15, 9, 0)
        result = calculate_next_occurrence(due_date, Recurrence.DAILY)

        expected = datetime(2025, 1, 16, 9, 0)
        assert result == expected, f"Expected {expected}, got {result}"

    def test_weekly_recurrence_calculation(self):
        """Verify WEEKLY adds 7 days."""
        from todo.services.task_service import calculate_next_occurrence

        due_date = datetime(2025, 1, 15, 9, 0)
        result = calculate_next_occurrence(due_date, Recurrence.WEEKLY)

        expected = datetime(2025, 1, 22, 9, 0)
        assert result == expected, f"Expected {expected}, got {result}"

    def test_monthly_recurrence_calculation(self):
        """Verify MONTHLY adds 1 month."""
        from todo.services.task_service import calculate_next_occurrence

        due_date = datetime(2025, 1, 15, 9, 0)
        result = calculate_next_occurrence(due_date, Recurrence.MONTHLY)

        expected = datetime(2025, 2, 15, 9, 0)
        assert result == expected, f"Expected {expected}, got {result}"

    def test_monthly_edge_case_jan31_to_feb(self):
        """Verify Jan 31 → Feb 28/29 (last day of month handling)."""
        from todo.services.task_service import calculate_next_occurrence

        due_date = datetime(2025, 1, 31, 9, 0)  # 2025 is non-leap year
        result = calculate_next_occurrence(due_date, Recurrence.MONTHLY)

        expected = datetime(2025, 2, 28, 9, 0)  # Feb 28 in non-leap year
        assert result == expected, f"Expected {expected}, got {result}"

    def test_monthly_edge_case_leap_year(self):
        """Verify Feb 29 → Mar 29 (same day, next month)."""
        from todo.services.task_service import calculate_next_occurrence

        due_date = datetime(2024, 2, 29, 9, 0)  # 2024 is leap year
        result = calculate_next_occurrence(due_date, Recurrence.MONTHLY)

        # Monthly recurrence goes to next month, same day clamped
        # Feb 29 -> Mar 29 (29 is valid in March)
        expected = datetime(2024, 3, 29, 9, 0)
        assert result == expected, f"Expected {expected}, got {result}"

    def test_monthly_edge_case_dec31_to_jan(self):
        """Verify Dec 31 → Jan 31 (year rollover)."""
        from todo.services.task_service import calculate_next_occurrence

        due_date = datetime(2025, 12, 31, 9, 0)
        result = calculate_next_occurrence(due_date, Recurrence.MONTHLY)

        expected = datetime(2026, 1, 31, 9, 0)
        assert result == expected, f"Expected {expected}, got {result}"

    def test_recurrence_none_raises_error(self):
        """Verify Recurrence.NONE raises ValueError."""
        from todo.services.task_service import calculate_next_occurrence

        due_date = datetime(2025, 1, 15, 9, 0)

        with pytest.raises(ValueError, match="Cannot calculate next occurrence for non-recurring task"):
            calculate_next_occurrence(due_date, Recurrence.NONE)


class TestCompleteRecurringTask:
    """Tests for auto-reschedule when completing recurring tasks."""

    def setup_method(self):
        """Reset task store and task service before each test."""
        from todo.services import task_service
        reset_task_store()
        task_service._task_service = None  # Reset service singleton too

    def test_complete_recurring_task_creates_next_instance(self):
        """Verify completing a recurring task creates a new task instance."""
        from todo.services.task_service import add_task, complete_task

        # Create a daily recurring task
        due_date = datetime.now() + timedelta(days=1)
        task = add_task(
            title="Daily standup",
            description="Team standup meeting",
            due_date=due_date,
            recurrence=Recurrence.DAILY
        )

        # Complete the task
        completed, new_task = complete_task(task.id)

        assert completed.completed is True, "Original task should be marked complete"
        assert new_task is not None, "New task should be created"
        assert new_task.completed is False, "New task should not be complete"
        assert new_task.id != task.id, "New task should have different ID"
        assert new_task.recurrence == Recurrence.DAILY, "New task should preserve recurrence"

    def test_complete_recurring_preserves_attributes(self):
        """Verify cloned task preserves title, description, priority, tags."""
        from todo.services.task_service import add_task, complete_task

        due_date = datetime.now() + timedelta(days=1)
        task = add_task(
            title="Weekly review",
            description="Review weekly progress",
            priority=2,  # MEDIUM
            tags={"review", "weekly"},
            due_date=due_date,
            recurrence=Recurrence.WEEKLY
        )

        completed, new_task = complete_task(task.id)

        assert new_task.title == "Weekly review"
        assert new_task.description == "Review weekly progress"
        assert new_task.priority == 2  # MEDIUM = 2
        assert new_task.tags == {"review", "weekly"}
        assert new_task.recurrence == Recurrence.WEEKLY

    def test_complete_recurring_generates_new_id(self):
        """Verify new task has a different ID from original."""
        from todo.services.task_service import add_task, complete_task

        due_date = datetime.now() + timedelta(days=1)
        task = add_task(
            title="Monthly task",
            due_date=due_date,
            recurrence=Recurrence.MONTHLY
        )

        completed, new_task = complete_task(task.id)

        assert new_task.id != task.id, "New task must have unique ID"

    def test_complete_non_recurring_no_new_instance(self):
        """Verify completing a non-recurring task does NOT create a new instance."""
        from todo.services.task_service import add_task, complete_task

        due_date = datetime.now() + timedelta(days=1)
        task = add_task(
            title="One-time task",
            due_date=due_date,
            recurrence=Recurrence.NONE
        )

        completed, new_task = complete_task(task.id)

        assert completed.completed is True
        assert new_task is None, "No new task should be created for non-recurring"

    def test_multiple_rapid_completions(self):
        """Verify multiple rapid completions create sequential future instances."""
        from todo.services.task_service import add_task, complete_task

        due_date = datetime.now() + timedelta(days=1)
        task = add_task(
            title="Daily habit",
            due_date=due_date,
            recurrence=Recurrence.DAILY
        )

        # Complete first time
        completed1, new1 = complete_task(task.id)
        assert new1 is not None

        # Complete second time
        completed2, new2 = complete_task(new1.id)
        assert new2 is not None

        # Complete third time
        completed3, new3 = complete_task(new2.id)
        assert new3 is not None

        # All original and clones should be complete
        assert completed1.completed is True
        assert completed2.completed is True
        assert completed3.completed is True
        assert new3.completed is False


class TestRecurrenceEnum:
    """Tests for Recurrence enum parsing."""

    def test_from_str_full_names(self):
        """Verify parsing full recurrence names."""
        assert Recurrence.from_str("DAILY") == Recurrence.DAILY
        assert Recurrence.from_str("WEEKLY") == Recurrence.WEEKLY
        assert Recurrence.from_str("MONTHLY") == Recurrence.MONTHLY
        assert Recurrence.from_str("NONE") == Recurrence.NONE

    def test_from_str_case_insensitive(self):
        """Verify parsing is case insensitive."""
        assert Recurrence.from_str("daily") == Recurrence.DAILY
        assert Recurrence.from_str("Weekly") == Recurrence.WEEKLY

    def test_from_str_shortcuts(self):
        """Verify parsing shorthand shortcuts."""
        assert Recurrence.from_str("d") == Recurrence.DAILY
        assert Recurrence.from_str("w") == Recurrence.WEEKLY
        assert Recurrence.from_str("m") == Recurrence.MONTHLY
        assert Recurrence.from_str("n") == Recurrence.NONE

    def test_from_str_invalid_returns_none(self):
        """Verify invalid input returns NONE."""
        assert Recurrence.from_str("invalid") == Recurrence.NONE
        assert Recurrence.from_str("") == Recurrence.NONE
