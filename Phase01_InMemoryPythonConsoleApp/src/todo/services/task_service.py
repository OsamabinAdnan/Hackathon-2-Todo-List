"""TaskService with CRUD operations and validation for the Todo CLI application."""

from dataclasses import dataclass, field

from todo.models.task import Task
from todo.storage.task_store import TaskStore, get_task_store


class ValidationError(Exception):
    """Raised when validation fails for task operations."""

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


@dataclass
class TaskService:
    """Service layer for task CRUD operations with validation.

    This class provides a clean interface between the CLI layer and the storage layer,
    handling validation, business logic, and error handling.

    Attributes:
        _store: The underlying TaskStore instance.
    """

    _store: TaskStore = field(default_factory=get_task_store)

    def add_task(self, title: str, description: str = "") -> Task:
        """Create a new task with validation.

        Args:
            title: Task title (1-100 characters, required).
            description: Optional task description (0-500 characters).

        Returns:
            The newly created Task instance.

        Raises:
            ValidationError: If title is empty or too long, or description is too long.
        """
        title = title.strip()
        description = description.strip()

        if not title:
            raise ValidationError("Title is required")
        if len(title) > 100:
            raise ValidationError("Title cannot exceed 100 characters")
        if len(description) > 500:
            raise ValidationError("Description cannot exceed 500 characters")

        return self._store.add(title, description)

    def get_all_tasks(self) -> list[Task]:
        """Retrieve all tasks in creation order.

        Returns:
            List of all tasks sorted by creation time (oldest first).
        """
        return self._store.get_all()

    def get_task(self, task_id: int) -> Task:
        """Retrieve a single task by ID.

        Args:
            task_id: The unique identifier of the task.

        Returns:
            The Task instance.

        Raises:
            ValidationError: If task_id is invalid.
            TaskNotFoundError: If the task does not exist.
        """
        if task_id <= 0:
            raise ValidationError("Invalid task ID")
        return self._store.get(task_id)

    def update_task(
        self,
        task_id: int,
        title: str | None = None,
        description: str | None = None,
        completed: bool | None = None,
    ) -> Task:
        """Update an existing task.

        Args:
            task_id: The unique identifier of the task to update.
            title: New title (1-100 characters, optional).
            description: New description (0-500 characters, optional).
            completed: New completion status (optional).

        Returns:
            The updated Task instance.

        Raises:
            ValidationError: If task_id is invalid or validation fails.
            TaskNotFoundError: If the task does not exist.
        """
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

        return self._store.update(task_id, title, description, completed)

    def delete_task(self, task_id: int) -> bool:
        """Delete a task by ID.

        Args:
            task_id: The unique identifier of the task to delete.

        Returns:
            True if the task was deleted.

        Raises:
            ValidationError: If task_id is invalid.
            TaskNotFoundError: If the task does not exist.
        """
        if task_id <= 0:
            raise ValidationError("Invalid task ID")
        return self._store.delete(task_id)

    def toggle_task_completion(self, task_id: int) -> Task:
        """Toggle the completion status of a task.

        Args:
            task_id: The unique identifier of the task.

        Returns:
            The updated Task instance.

        Raises:
            ValidationError: If task_id is invalid.
            TaskNotFoundError: If the task does not exist.
        """
        if task_id <= 0:
            raise ValidationError("Invalid task ID")
        return self._store.toggle(task_id)

    def mark_task_complete(self, task_id: int) -> Task:
        """Mark a task as complete.

        Args:
            task_id: The unique identifier of the task.

        Returns:
            The updated Task instance.

        Raises:
            ValidationError: If task_id is invalid.
            TaskNotFoundError: If the task does not exist.
        """
        if task_id <= 0:
            raise ValidationError("Invalid task ID")
        return self._store.mark_complete(task_id)

    def mark_task_incomplete(self, task_id: int) -> Task:
        """Mark a task as incomplete.

        Args:
            task_id: The unique identifier of the task.

        Returns:
            The updated Task instance.

        Raises:
            ValidationError: If task_id is invalid.
            TaskNotFoundError: If the task does not exist.
        """
        if task_id <= 0:
            raise ValidationError("Invalid task ID")
        return self._store.mark_incomplete(task_id)

    def get_task_count(self) -> int:
        """Get the total number of tasks.

        Returns:
            Number of tasks in the store.
        """
        return self._store.count()

    def get_completed_count(self) -> int:
        """Get the number of completed tasks.

        Returns:
            Number of completed tasks.
        """
        return self._store.count_completed()

    def task_exists(self, task_id: int) -> bool:
        """Check if a task exists.

        Args:
            task_id: The unique identifier of the task.

        Returns:
            True if the task exists, False otherwise.
        """
        return self._store.exists(task_id)


# Module-level singleton instance for Phase 1
_task_service: TaskService | None = None


def get_task_service() -> TaskService:
    """Get the global TaskService singleton instance.

    Returns:
        The TaskService singleton instance.
    """
    global _task_service
    if _task_service is None:
        _task_service = TaskService()
    return _task_service


def reset_task_service() -> None:
    """Reset the TaskService singleton (useful for testing)."""
    global _task_service
    _task_service = TaskService()
