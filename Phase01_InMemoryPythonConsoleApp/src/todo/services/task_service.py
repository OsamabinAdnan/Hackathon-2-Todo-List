"""TaskService with CRUD operations and validation for the Todo CLI application."""

from dataclasses import dataclass, field
from datetime import date, datetime, timedelta, time
from typing import Set, Optional, List

from todo.models.task import Task, Priority, Recurrence
from todo.storage.task_store import TaskStore, get_task_store
from todo.services.results import SearchResult, ReminderResult


class ValidationError(Exception):
    """Raised when validation fails for task operations."""

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


@dataclass
class TaskService:
    """Service layer for task CRUD operations with validation.

    Attributes:
        _store: The underlying TaskStore instance.
    """

    _store: TaskStore = field(default_factory=get_task_store)

    def add_task(
        self,
        title: str,
        description: str = "",
        priority: Priority = Priority.NONE,
        tags: Optional[Set[str]] = None,
        due_date: Optional[date] = None,
    ) -> Task:
        """Create a new task with validation."""
        title = title.strip()
        description = description.strip()

        if not title:
            raise ValidationError("Title is required")
        if len(title) > 100:
            raise ValidationError("Title cannot exceed 100 characters")
        if len(description) > 500:
            raise ValidationError("Description cannot exceed 500 characters")

        processed_tags = self._validate_and_process_tags(tags or set())

        return self._store.add(
            title=title,
            description=description,
            priority=priority,
            tags=processed_tags,
            due_date=due_date,
        )

    def get_all_tasks(self) -> list[Task]:
        """Retrieve all tasks in creation order."""
        return self._store.get_all()

    def search_tasks(
        self,
        keyword: Optional[str] = None,
        status: Optional[bool] = None,
        priority: Optional[Priority] = None,
        tags: Optional[Set[str]] = None,
        sort_by: Optional[str] = None,
    ) -> SearchResult:
        """Search and filter tasks with cumulative AND logic."""
        tasks = self._store.get_all()
        filtered_tasks = []

        for task in tasks:
            # Keyword Filter
            if keyword:
                k = keyword.lower()
                title_match = k in task.title.lower()
                desc_match = k in task.description.lower()
                if not (title_match or desc_match):
                    continue

            # Status Filter
            if status is not None and task.completed != status:
                continue

            # Priority Filter
            if priority is not None and task.priority != priority:
                continue

            # Tags Filter (ANY match - task has at least one of the specified tags)
            if tags:
                if not any(tag in task.tags for tag in tags):
                    continue

            filtered_tasks.append(task)

        # Sorting with multi-level keys
        if sort_by:
            if sort_by == "priority":
                # Primary: Priority (desc), Secondary: Due date (asc), Tertiary: Title (asc)
                filtered_tasks.sort(key=lambda t: (
                    -t.priority.value,
                    t.due_date is None,
                    t.due_date if t.due_date else date.max,
                    t.title.lower()
                ))
            elif sort_by == "date":
                filtered_tasks.sort(key=lambda t: t.created_at, reverse=True)
            elif sort_by == "title":
                filtered_tasks.sort(key=lambda t: t.title.lower())
            elif sort_by == "due_date":
                # Put tasks with no due date at the end, then alphabetically
                filtered_tasks.sort(key=lambda t: (
                    t.due_date is None,
                    t.due_date if t.due_date else date.max,
                    t.title.lower()
                ))

        return SearchResult(
            tasks=filtered_tasks,
            total_count=len(filtered_tasks),
            filter_criteria={
                "keyword": keyword,
                "status": status,
                "priority": priority.name if priority else None,
                "tags": list(tags) if tags else None,
                "sort_by": sort_by
            }
        )

    def get_task(self, task_id: int) -> Task:
        """Retrieve a single task by ID."""
        if task_id <= 0:
            raise ValidationError("Invalid task ID")
        return self._store.get(task_id)

    def update_task(
        self,
        task_id: int,
        title: str | None = None,
        description: str | None = None,
        completed: bool | None = None,
        priority: Priority | None = None,
        tags: Set[str] | None = None,
        due_date: date | None = None,
    ) -> Task:
        """Update an existing task."""
        if task_id <= 0:
            raise ValidationError("Invalid task ID")

        if title is not None:
            title = title.strip()
            if not title:
                raise ValidationError("Title cannot be empty")
            if len(title) > 100:
                raise ValidationError("Title cannot exceed 100 characters")

        if description is not None:
            description = description.strip()
            if len(description) > 500:
                raise ValidationError("Description cannot exceed 500 characters")

        processed_tags = self._validate_and_process_tags(tags) if tags is not None else None

        return self._store.update(
            task_id,
            title=title,
            description=description,
            completed=completed,
            priority=priority,
            tags=processed_tags,
            due_date=due_date,
        )

    def _validate_and_process_tags(self, tags: Set[str]) -> Set[str]:
        """Validate and sanitize tags."""
        processed = set()
        for tag in tags:
            clean = tag.strip().lower()
            if clean:
                if len(clean) > 20:
                    raise ValidationError(f"Tag '{clean}' exceeds 20 characters")
                processed.add(clean)
        return processed

    def delete_task(self, task_id: int) -> bool:
        """Delete a task by ID."""
        if task_id <= 0:
            raise ValidationError("Invalid task ID")
        return self._store.delete(task_id)

    def toggle_task_completion(self, task_id: int) -> Task:
        """Toggle the completion status of a task."""
        if task_id <= 0:
            raise ValidationError("Invalid task ID")
        return self._store.toggle(task_id)

    def mark_task_complete(self, task_id: int) -> Task:
        """Mark a task as complete."""
        if task_id <= 0:
            raise ValidationError("Invalid task ID")
        return self._store.mark_complete(task_id)

    def mark_task_incomplete(self, task_id: int) -> Task:
        """Mark a task as incomplete."""
        if task_id <= 0:
            raise ValidationError("Invalid task ID")
        return self._store.mark_incomplete(task_id)

    def get_task_count(self) -> int:
        """Get the total number of tasks."""
        return self._store.count()

    def get_completed_count(self) -> int:
        """Get the number of completed tasks."""
        return self._store.count_completed()

    def task_exists(self, task_id: int) -> bool:
        """Check if a task exists."""
        return self._store.exists(task_id)

    def add_task_with_recurrence(
        self,
        title: str,
        description: str = "",
        priority: Priority = Priority.NONE,
        tags: Optional[Set[str]] = None,
        due_date: Optional[date] = None,
        recurrence: Recurrence = Recurrence.NONE,
    ) -> Task:
        """Create a new task with recurrence pattern."""
        title = title.strip()
        description = description.strip()

        if not title:
            raise ValidationError("Title is required")
        if len(title) > 100:
            raise ValidationError("Title cannot exceed 100 characters")
        if len(description) > 500:
            raise ValidationError("Description cannot exceed 500 characters")

        # Recurring tasks must have a due date
        if recurrence != Recurrence.NONE and due_date is None:
            raise ValidationError("Recurring tasks must have a due date")

        processed_tags = self._validate_and_process_tags(tags or set())

        return self._store.add(
            title=title,
            description=description,
            priority=priority,
            tags=processed_tags,
            due_date=due_date,
            recurrence=recurrence,
        )

    def update_task_with_recurrence(
        self,
        task_id: int,
        title: str | None = None,
        description: str | None = None,
        completed: bool | None = None,
        priority: Priority | None = None,
        tags: Set[str] | None = None,
        due_date: date | None = None,
        recurrence: Recurrence | None = None,
    ) -> Task:
        """Update an existing task with recurrence support."""
        if task_id <= 0:
            raise ValidationError("Invalid task ID")

        if title is not None:
            title = title.strip()
            if not title:
                raise ValidationError("Title cannot be empty")
            if len(title) > 100:
                raise ValidationError("Title cannot exceed 100 characters")

        if description is not None:
            description = description.strip()
            if len(description) > 500:
                raise ValidationError("Description cannot exceed 500 characters")

        # If setting recurrence, ensure due_date is set
        if recurrence is not None and recurrence != Recurrence.NONE and due_date is None:
            existing_task = self._store.get(task_id)
            if existing_task.due_date is None:
                raise ValidationError("Recurring tasks must have a due date")

        processed_tags = self._validate_and_process_tags(tags) if tags is not None else None

        return self._store.update(
            task_id,
            title=title,
            description=description,
            completed=completed,
            priority=priority,
            tags=processed_tags,
            due_date=due_date,
            recurrence=recurrence,
        )


_task_service: TaskService | None = None


def get_task_service() -> TaskService:
    """Get the global TaskService singleton instance."""
    global _task_service
    if _task_service is None:
        _task_service = TaskService()
    return _task_service


def reset_task_service() -> None:
    """Reset the TaskService singleton."""
    global _task_service
    _task_service = TaskService()


def calculate_next_occurrence(due_date: datetime, recurrence: Recurrence) -> datetime:
    """Calculate the next occurrence date for a recurring task.

    Args:
        due_date: The current due date of the task.
        recurrence: The recurrence pattern (DAILY, WEEKLY, MONTHLY).

    Returns:
        The next occurrence date.

    Raises:
        ValueError: If recurrence is NONE (non-recurring task).
    """
    if recurrence == Recurrence.NONE:
        raise ValueError("Cannot calculate next occurrence for non-recurring task")

    if recurrence == Recurrence.DAILY:
        return due_date + timedelta(days=1)

    elif recurrence == Recurrence.WEEKLY:
        return due_date + timedelta(weeks=1)

    elif recurrence == Recurrence.MONTHLY:
        # Calculate same day next month with edge case handling
        year = due_date.year
        month = due_date.month + 1

        if month > 12:
            month = 1
            year += 1

        # Get the last day of the target month using pure datetime arithmetic
        # First day of month AFTER target month
        if month == 12:
            first_of_following_month = datetime(year + 1, 1, 1)
        else:
            first_of_following_month = datetime(year, month + 1, 1)
        # Last day of target month (day before first of following month)
        last_day = (first_of_following_month - timedelta(days=1)).day

        # Handle edge case: Feb 29 in leap year -> Feb 28 in non-leap year
        # If original day is the last day of Feb in a leap year (29), target Feb
        is_last_day_of_feb = due_date.month == 2 and due_date.day == 29
        target_is_february = month == 2

        if is_last_day_of_feb and target_is_february:
            # Target is February - use last day (28 or 29 based on year)
            target_day = last_day
        else:
            # Clamp to valid day for the target month
            target_day = min(due_date.day, last_day)

        return datetime(year, month, target_day, due_date.hour, due_date.minute)

    # Should not reach here for valid Recurrence values
    raise ValueError(f"Invalid recurrence value: {recurrence}")


def complete_task(task_id: int) -> tuple[Task, Optional[Task]]:
    """Complete a task and auto-schedule if recurring.

    Args:
        task_id: The ID of the task to complete.

    Returns:
        Tuple of (completed_task, new_task) where new_task is None for non-recurring.
    """
    store = get_task_store()
    task = store.get(task_id)

    # Mark the task complete
    completed_task = store.mark_complete(task_id)

    # Check if we need to create a new instance
    if task.recurrence != Recurrence.NONE and task.due_date is not None:
        # Calculate next occurrence
        next_due = calculate_next_occurrence(task.due_date, task.recurrence)

        # Clone the task with new ID and updated due date
        new_task = store.add(
            title=task.title,
            description=task.description,
            priority=task.priority,
            tags=task.tags,
            due_date=next_due,
            recurrence=task.recurrence,
        )

        return completed_task, new_task

    return completed_task, None


def check_reminders() -> ReminderResult:
    """Check for overdue and due-soon tasks.

    Returns:
        ReminderResult with lists of overdue and due-soon tasks.
    """
    store = get_task_store()
    now = datetime.now()
    soon_threshold = now + timedelta(minutes=60)

    all_tasks = store.get_all()

    overdue_tasks = []
    due_soon_tasks = []

    for task in all_tasks:
        # Skip completed tasks
        if task.completed:
            continue

        # Skip tasks without due dates
        if task.due_date is None:
            continue

        # Skip date-only tasks (time = 00:00:00) per spec
        if task.due_date.time() == time(0, 0, 0):
            continue

        # Classify the task
        if task.due_date < now:
            overdue_tasks.append(task)
        elif now <= task.due_date < soon_threshold:
            due_soon_tasks.append(task)

    return ReminderResult(
        overdue_tasks=overdue_tasks,
        due_soon_tasks=due_soon_tasks,
        overdue_count=len(overdue_tasks),
        due_soon_count=len(due_soon_tasks),
    )


# Convenience functions that match test expectations
def add_task(
    title: str,
    description: str = "",
    priority: Priority = Priority.NONE,
    tags: Optional[Set[str]] = None,
    due_date: Optional[date] = None,
    recurrence: Recurrence = Recurrence.NONE,
) -> Task:
    """Add a task (convenience function for backward compatibility)."""
    service = get_task_service()
    return service.add_task_with_recurrence(
        title=title,
        description=description,
        priority=priority,
        tags=tags,
        due_date=due_date,
        recurrence=recurrence,
    )
