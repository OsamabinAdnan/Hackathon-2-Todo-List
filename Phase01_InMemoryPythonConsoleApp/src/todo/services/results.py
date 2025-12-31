"""Result structures for CLI command outcomes."""

from dataclasses import dataclass
from enum import Enum
from typing import List, Optional, Dict, Any

from todo.models.task import Task


@dataclass
class ReminderResult:
    """Result structure for reminder detection."""

    overdue_tasks: List[Task]
    due_soon_tasks: List[Task]
    overdue_count: int
    due_soon_count: int


class ResultStatus(Enum):
    """Status of a command result."""

    SUCCESS = "success"
    ERROR = "error"
    NOT_FOUND = "not_found"
    VALIDATION_ERROR = "validation_error"


@dataclass
class Result[T]:
    """Generic result structure for command outcomes."""

    status: ResultStatus
    message: str
    data: Optional[T] = None
    error_code: Optional[str] = None

    @classmethod
    def success(cls, message: str, data: Optional[T] = None) -> "Result[T]":
        """Create a success result."""
        return cls(status=ResultStatus.SUCCESS, message=message, data=data)

    @classmethod
    def error(cls, message: str, error_code: Optional[str] = None) -> "Result[T]":
        """Create an error result."""
        return cls(
            status=ResultStatus.ERROR, message=message, error_code=error_code
        )

    @classmethod
    def not_found(cls, task_id: int) -> "Result[T]":
        """Create a not found result."""
        return cls(
            status=ResultStatus.NOT_FOUND,
            message=f"Task not found: {task_id}",
            error_code="TASK_NOT_FOUND",
        )

    @classmethod
    def validation_error(cls, message: str) -> "Result[T]":
        """Create a validation error result."""
        return cls(
            status=ResultStatus.VALIDATION_ERROR,
            message=message,
            error_code="VALIDATION_ERROR",
        )

    def is_success(self) -> bool:
        """Check if the result is successful."""
        return self.status == ResultStatus.SUCCESS


@dataclass
class SearchResult:
    """Container for task search/filter results."""
    tasks: List[Task]
    total_count: int
    filter_criteria: Dict[str, Any]


@dataclass
class TaskResult:
    """Result structure specifically for task operations."""

    task: Optional[Task] = None
    previous_state: Optional[Dict[str, object]] = None


# Specific result types for common operations
AddTaskResult = Result[TaskResult]
UpdateTaskResult = Result[TaskResult]
DeleteTaskResult = Result[TaskResult]
ToggleTaskResult = Result[TaskResult]
ListTasksResult = Result[List[Task]]
GetTaskResult = Result[TaskResult]
SearchTasksResult = Result[SearchResult]
