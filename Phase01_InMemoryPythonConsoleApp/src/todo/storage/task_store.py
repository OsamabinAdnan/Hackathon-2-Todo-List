"""In-memory storage for Task entities using dictionary with auto-incrementing IDs."""

from datetime import datetime, date
from typing import Set, Optional

from todo.models.task import Task, Priority


class TaskNotFoundError(Exception):
    """Raised when a task is not found in the store."""

    def __init__(self, task_id: int) -> None:
        super().__init__(f"Task not found: {task_id}")
        self.task_id = task_id


class TaskStore:
    """In-memory storage for tasks using a dictionary with auto-incrementing integer keys.

    Attributes:
        _tasks: Dictionary mapping task ID to Task instance.
        _next_id: Next available auto-incrementing ID.
    """

    def __init__(self) -> None:
        """Initialize an empty TaskStore."""
        self._tasks: dict[int, Task] = {}
        self._next_id: int = 1

    def add(
        self,
        title: str,
        description: str = "",
        priority: Priority = Priority.NONE,
        tags: Optional[Set[str]] = None,
        due_date: Optional[date] = None,
    ) -> Task:
        """Add a new task to the store."""
        task_id = self._next_id
        self._next_id += 1

        task = Task(
            id=task_id,
            title=title,
            description=description,
            completed=False,
            priority=priority,
            tags=tags or set(),
            due_date=due_date,
            created_at=datetime.now(),
        )

        self._tasks[task_id] = task
        return task

    def get(self, task_id: int) -> Task:
        """Retrieve a task by ID."""
        task = self._tasks.get(task_id)
        if task is None:
            raise TaskNotFoundError(task_id)
        return task

    def get_all(self) -> list[Task]:
        """Retrieve all tasks in creation order."""
        return sorted(self._tasks.values(), key=lambda t: t.created_at)

    def update(
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
        task = self.get(task_id)

        if title is not None:
            task.title = title.strip()
        if description is not None:
            task.description = description.strip()
        if completed is not None:
            task.completed = completed
        if priority is not None:
            task.priority = priority
        if tags is not None:
            task.tags = tags
        if due_date is not None:
            task.due_date = due_date

        task.mark_updated()
        return task

    def delete(self, task_id: int) -> bool:
        """Delete a task by ID and re-index remaining tasks."""
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

        sorted_tasks = sorted(self._tasks.values(), key=lambda t: t.created_at)
        self._tasks.clear()

        for index, task in enumerate(sorted_tasks, start=1):
            task.id = index
            self._tasks[index] = task

        self._next_id = len(self._tasks) + 1

    def toggle(self, task_id: int) -> Task:
        """Toggle the completion status of a task."""
        task = self.get(task_id)
        task.completed = not task.completed
        task.mark_updated()
        return task

    def mark_complete(self, task_id: int) -> Task:
        """Mark a task as complete."""
        task = self.get(task_id)
        task.completed = True
        task.mark_updated()
        return task

    def mark_incomplete(self, task_id: int) -> Task:
        """Mark a task as incomplete."""
        task = self.get(task_id)
        task.completed = False
        task.mark_updated()
        return task

    def count(self) -> int:
        """Return the total number of tasks."""
        return len(self._tasks)

    def count_completed(self) -> int:
        """Return the number of completed tasks."""
        return sum(1 for task in self._tasks.values() if task.completed)

    def exists(self, task_id: int) -> bool:
        """Check if a task exists."""
        return task_id in self._tasks


_task_store: TaskStore | None = None


def get_task_store() -> TaskStore:
    """Get the global TaskStore singleton instance."""
    global _task_store
    if _task_store is None:
        _task_store = TaskStore()
    return _task_store


def reset_task_store() -> None:
    """Reset the TaskStore singleton."""
    global _task_store
    _task_store = TaskStore()
