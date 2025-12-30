"""In-memory storage for Task entities using dictionary with auto-incrementing IDs."""

from datetime import datetime

from todo.models.task import Task


class TaskNotFoundError(Exception):
    """Raised when a task is not found in the store."""

    def __init__(self, task_id: int) -> None:
        super().__init__(f"Task not found: {task_id}")
        self.task_id = task_id


class TaskStore:
    """In-memory storage for tasks using a dictionary with auto-incrementing integer keys.

    This class provides thread-safe-ish storage for tasks during a single session.
    For Phase 1, the storage is in-memory only and resets when the application restarts.

    Attributes:
        _tasks: Dictionary mapping task ID to Task instance.
        _next_id: Next available auto-incrementing ID.
    """

    def __init__(self) -> None:
        """Initialize an empty TaskStore."""
        self._tasks: dict[int, Task] = {}
        self._next_id: int = 1

    def add(self, title: str, description: str = "") -> Task:
        """Add a new task to the store.

        Args:
            title: Task title (1-100 characters).
            description: Optional task description (0-500 characters).

        Returns:
            The newly created Task instance.

        Raises:
            ValueError: If title is empty or exceeds 100 characters,
                       or description exceeds 500 characters.
        """
        if not title:
            raise ValueError("Task title cannot be empty")
        if len(title) > 100:
            raise ValueError("Task title cannot exceed 100 characters")
        if len(description) > 500:
            raise ValueError("Task description cannot exceed 500 characters")

        task_id = self._next_id
        self._next_id += 1

        task = Task(
            id=task_id,
            title=title,
            description=description,
            completed=False,
            created_at=datetime.now(),
            updated_at=None,
        )

        self._tasks[task_id] = task
        return task

    def get(self, task_id: int) -> Task:
        """Retrieve a task by ID.

        Args:
            task_id: The unique identifier of the task.

        Returns:
            The Task instance.

        Raises:
            TaskNotFoundError: If the task does not exist.
        """
        task = self._tasks.get(task_id)
        if task is None:
            raise TaskNotFoundError(task_id)
        return task

    def get_all(self) -> list[Task]:
        """Retrieve all tasks in creation order.

        Returns:
            List of all tasks sorted by creation order (oldest first).
        """
        return sorted(self._tasks.values(), key=lambda t: t.created_at)

    def update(
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
            TaskNotFoundError: If the task does not exist.
            ValueError: If validation fails.
        """
        task = self.get(task_id)

        if title is not None:
            if not title:
                raise ValueError("Task title cannot be empty")
            if len(title) > 100:
                raise ValueError("Task title cannot exceed 100 characters")
            task.title = title

        if description is not None:
            if len(description) > 500:
                raise ValueError("Task description cannot exceed 500 characters")
            task.description = description

        if completed is not None:
            task.completed = completed

        task.updated_at = datetime.now()
        return task

    def delete(self, task_id: int) -> bool:
        """Delete a task by ID and re-index remaining tasks.

        Args:
            task_id: The unique identifier of the task to delete.

        Returns:
            True if the task was deleted, False if it didn't exist.

        Raises:
            TaskNotFoundError: If the task does not exist.
        """
        if task_id not in self._tasks:
            raise TaskNotFoundError(task_id)

        del self._tasks[task_id]
        self._reindex()
        return True

    def _reindex(self) -> None:
        """Re-index all tasks to ensure sequential IDs starting from 1."""
        if not self._tasks:
            self._next_id = 1
            return

        # Get all tasks sorted by original creation order
        sorted_tasks = self.get_all()
        self._tasks.clear()

        for index, task in enumerate(sorted_tasks, start=1):
            task.id = index
            self._tasks[index] = task

        self._next_id = len(self._tasks) + 1

    def toggle(self, task_id: int) -> Task:
        """Toggle the completion status of a task.

        Args:
            task_id: The unique identifier of the task.

        Returns:
            The updated Task instance.

        Raises:
            TaskNotFoundError: If the task does not exist.
        """
        task = self.get(task_id)
        task.completed = not task.completed
        task.updated_at = datetime.now()
        return task

    def mark_complete(self, task_id: int) -> Task:
        """Mark a task as complete.

        Args:
            task_id: The unique identifier of the task.

        Returns:
            The updated Task instance.

        Raises:
            TaskNotFoundError: If the task does not exist.
        """
        task = self.get(task_id)
        task.completed = True
        task.updated_at = datetime.now()
        return task

    def mark_incomplete(self, task_id: int) -> Task:
        """Mark a task as incomplete.

        Args:
            task_id: The unique identifier of the task.

        Returns:
            The updated Task instance.

        Raises:
            TaskNotFoundError: If the task does not exist.
        """
        task = self.get(task_id)
        task.completed = False
        task.updated_at = datetime.now()
        return task

    def count(self) -> int:
        """Return the total number of tasks.

        Returns:
            Number of tasks in the store.
        """
        return len(self._tasks)

    def count_completed(self) -> int:
        """Return the number of completed tasks.

        Returns:
            Number of completed tasks.
        """
        return sum(1 for task in self._tasks.values() if task.completed)

    def clear(self) -> int:
        """Clear all tasks from the store.

        Returns:
            The number of tasks that were deleted.
        """
        count = len(self._tasks)
        self._tasks.clear()
        self._next_id = 1
        return count

    def exists(self, task_id: int) -> bool:
        """Check if a task exists.

        Args:
            task_id: The unique identifier of the task.

        Returns:
            True if the task exists, False otherwise.
        """
        return task_id in self._tasks


# Module-level singleton instance for Phase 1 in-memory storage
_task_store: TaskStore | None = None


def get_task_store() -> TaskStore:
    """Get the global TaskStore singleton instance.

    Returns:
        The TaskStore singleton instance.
    """
    global _task_store
    if _task_store is None:
        _task_store = TaskStore()
    return _task_store


def reset_task_store() -> None:
    """Reset the TaskStore singleton (useful for testing)."""
    global _task_store
    _task_store = TaskStore()
