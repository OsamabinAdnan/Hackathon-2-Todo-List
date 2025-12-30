"""Task data model for the Todo CLI application."""

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Task:
    """Represents a todo task with title, description, and completion status.

    Attributes:
        id: Unique sequential integer identifier (auto-generated).
        title: Task title (1-100 characters, required).
        description: Optional task description (0-500 characters).
        completed: Whether the task is complete (default: False).
        created_at: Timestamp when the task was created.
        updated_at: Timestamp when the task was last updated (None if never updated).
    """

    id: int
    title: str
    description: str = ""
    completed: bool = False
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime | None = None

    def __post_init__(self) -> None:
        """Validate task attributes after initialization."""
        if not self.title:
            raise ValueError("Task title cannot be empty")
        if len(self.title) > 100:
            raise ValueError("Task title cannot exceed 100 characters")
        if len(self.description) > 500:
            raise ValueError("Task description cannot exceed 500 characters")

    def mark_complete(self) -> None:
        """Mark the task as complete."""
        self.completed = True
        self.updated_at = datetime.now()

    def mark_incomplete(self) -> None:
        """Mark the task as incomplete."""
        self.completed = False
        self.updated_at = datetime.now()

    def toggle(self) -> None:
        """Toggle the completion status of the task."""
        self.completed = not self.completed
        self.updated_at = datetime.now()

    def update_title(self, new_title: str) -> None:
        """Update the task title.

        Args:
            new_title: The new title for the task (1-100 characters).
        """
        if not new_title:
            raise ValueError("Task title cannot be empty")
        if len(new_title) > 100:
            raise ValueError("Task title cannot exceed 100 characters")
        self.title = new_title
        self.updated_at = datetime.now()

    def update_description(self, new_description: str) -> None:
        """Update the task description.

        Args:
            new_description: The new description for the task (0-500 characters).
        """
        if len(new_description) > 500:
            raise ValueError("Task description cannot exceed 500 characters")
        self.description = new_description
        self.updated_at = datetime.now()

    def to_dict(self) -> dict[str, object]:
        """Convert the task to a dictionary representation.

        Returns:
            Dictionary containing all task attributes.
        """
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "completed": self.completed,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "Task":
        """Create a Task instance from a dictionary.

        Args:
            data: Dictionary containing task data.

        Returns:
            A new Task instance.
        """
        created_at = datetime.fromisoformat(data["created_at"])  # type: ignore[arg-type]
        updated_at = (
            datetime.fromisoformat(data["updated_at"])  # type: ignore[arg-type]
            if data.get("updated_at")
            else None
        )
        return cls(
            id=data["id"],  # type: ignore[arg-type]
            title=data["title"],  # type: ignore[arg-type]
            description=data.get("description", ""),  # type: ignore[arg-type]
            completed=data.get("completed", False),  # type: ignore[arg-type]
            created_at=created_at,
            updated_at=updated_at,
        )
