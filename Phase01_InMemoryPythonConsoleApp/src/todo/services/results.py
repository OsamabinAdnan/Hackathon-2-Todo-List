"""Result structures for CLI command outcomes."""

from dataclasses import dataclass
from enum import Enum

from todo.models.task import Task


class ResultStatus(Enum):
    """Status of a command result."""

    SUCCESS = "success"
    ERROR = "error"
    NOT_FOUND = "not_found"
    VALIDATION_ERROR = "validation_error"


@dataclass
class Result[T]:
    """Generic result structure for command outcomes.

    Attributes:
        status: The status of the operation.
        message: Human-readable message about the result.
        data: Optional data returned by the operation.
        error_code: Optional error code for errors.
    """

    status: ResultStatus
    message: str
    data: T | None = None
    error_code: str | None = None

    @classmethod
    def success(cls, message: str, data: T | None = None) -> "Result[T]":
        """Create a success result.

        Args:
            message: Success message.
            data: Optional data to include.

        Returns:
            A success Result instance.
        """
        return cls(status=ResultStatus.SUCCESS, message=message, data=data)

    @classmethod
    def error(cls, message: str, error_code: str | None = None) -> "Result[T]":
        """Create an error result.

        Args:
            message: Error message.
            error_code: Optional error code.

        Returns:
            An error Result instance.
        """
        return cls(
            status=ResultStatus.ERROR, message=message, error_code=error_code
        )

    @classmethod
    def not_found(cls, task_id: int) -> "Result[T]":
        """Create a not found result.

        Args:
            task_id: The ID of the task that was not found.

        Returns:
            A not found Result instance.
        """
        return cls(
            status=ResultStatus.NOT_FOUND,
            message=f"Task not found: {task_id}",
            error_code="TASK_NOT_FOUND",
        )

    @classmethod
    def validation_error(cls, message: str) -> "Result[T]":
        """Create a validation error result.

        Args:
            message: Validation error message.

        Returns:
            A validation error Result instance.
        """
        return cls(
            status=ResultStatus.VALIDATION_ERROR,
            message=message,
            error_code="VALIDATION_ERROR",
        )

    def is_success(self) -> bool:
        """Check if the result is successful.

        Returns:
            True if the status is SUCCESS.
        """
        return self.status == ResultStatus.SUCCESS

    def is_error(self) -> bool:
        """Check if the result is an error.

        Returns:
            True if the status is ERROR.
        """
        return self.status == ResultStatus.ERROR

    def is_not_found(self) -> bool:
        """Check if the result is not found.

        Returns:
            True if the status is NOT_FOUND.
        """
        return self.status == ResultStatus.NOT_FOUND

    def is_validation_error(self) -> bool:
        """Check if the result is a validation error.

        Returns:
            True if the status is VALIDATION_ERROR.
        """
        return self.status == ResultStatus.VALIDATION_ERROR


@dataclass
class TaskResult:
    """Result structure specifically for task operations.

    Attributes:
        task: The task involved in the operation (if applicable).
        previous_state: Previous state of the task (for updates).
    """

    task: Task | None = None
    previous_state: dict[str, object] | None = None


# Specific result types for common operations
AddTaskResult = Result[TaskResult]
UpdateTaskResult = Result[TaskResult]
DeleteTaskResult = Result[TaskResult]
ToggleTaskResult = Result[TaskResult]
ListTasksResult = Result[list[Task]]
GetTaskResult = Result[TaskResult]
