"""TaskService with CRUD operations and validation for the Todo CLI application."""

from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Set, Optional, List

from todo.models.task import Task, Priority
from todo.storage.task_store import TaskStore, get_task_store
from todo.services.results import SearchResult


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
