"""Task data model for the Todo CLI application."""

from dataclasses import dataclass, field
from datetime import datetime, date
from enum import IntEnum
from typing import Set, Optional


class Priority(IntEnum):
    """Priority levels for tasks."""
    NONE = 0
    LOW = 1
    MEDIUM = 2
    HIGH = 3

    @classmethod
    def from_str(cls, value: str) -> "Priority":
        """Parse priority from string."""
        try:
            return cls[value.upper()]
        except KeyError:
            return cls.NONE


@dataclass
class Task:
    """Represents a todo task with organization metadata.

    Attributes:
        id: Unique sequential integer identifier (auto-generated).
        title: Task title (1-100 characters, required).
        description: Optional task description (0-500 characters).
        completed: Whether the task is complete (default: False).
        priority: Task priority level (default: NONE).
        tags: Set of tags for categorization.
        due_date: Optional due date for the task.
        created_at: Timestamp when the task was created.
        updated_at: Timestamp when the task was last updated.
    """

    id: int
    title: str
    description: str = ""
    completed: bool = False
    priority: Priority = Priority.NONE
    tags: Set[str] = field(default_factory=set)
    due_date: Optional[date] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: Optional[datetime] = None

    def __post_init__(self) -> None:
        """Validate task attributes after initialization."""
        self.title = self.title.strip()
        if not self.title:
            raise ValueError("Task title cannot be empty")
        if len(self.title) > 100:
            raise ValueError("Task title cannot exceed 100 characters")
        if len(self.description) > 500:
            raise ValueError("Task description cannot exceed 500 characters")

        # Process tags
        self.tags = {tag.strip().lower()[:20] for tag in self.tags if tag.strip()}

    def mark_updated(self) -> None:
        """Update the last modified timestamp."""
        self.updated_at = datetime.now()

    def to_dict(self) -> dict[str, object]:
        """Convert the task to a dictionary representation."""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "completed": self.completed,
            "priority": self.priority.name,
            "tags": list(self.tags),
            "due_date": self.due_date.isoformat() if self.due_date else None,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "Task":
        """Create a Task instance from a dictionary."""
        created_at = datetime.fromisoformat(data["created_at"])  # type: ignore[arg-type]
        updated_at = (
            datetime.fromisoformat(data["updated_at"])  # type: ignore[arg-type]
            if data.get("updated_at")
            else None
        )
        due_date = (
            date.fromisoformat(data["due_date"])  # type: ignore[arg-type]
            if data.get("due_date")
            else None
        )
        return cls(
            id=data["id"],  # type: ignore[arg-type]
            title=data["title"],  # type: ignore[arg-type]
            description=data.get("description", ""),  # type: ignore[arg-type]
            completed=data.get("completed", False),  # type: ignore[arg-type]
            priority=Priority.from_str(data.get("priority", "NONE")),  # type: ignore[arg-type]
            tags=set(data.get("tags", [])),  # type: ignore[arg-type]
            due_date=due_date,
            created_at=created_at,
            updated_at=updated_at,
        )
