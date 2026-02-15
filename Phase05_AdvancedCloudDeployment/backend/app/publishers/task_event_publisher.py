"""
Task Event Publisher
Phase 5: Event-driven architecture (FR-001 to FR-005)

Publishes task lifecycle events (created, updated, completed, deleted)
to the task-events Kafka topic via Dapr pub/sub.
"""

import uuid
import logging
from typing import Any, Dict, Optional
from datetime import datetime
from enum import Enum

from app.publishers.base_publisher import DaprPublisher
from app.models.task import Task

logger = logging.getLogger(__name__)


class TaskEventType(str, Enum):
    """Task event types matching the task-event-schema.json contract."""
    CREATED = "task.created"
    UPDATED = "task.updated"
    COMPLETED = "task.completed"
    DELETED = "task.deleted"


# Global publisher instance for task events
_task_event_publisher: Optional[DaprPublisher] = None


def get_task_event_publisher() -> DaprPublisher:
    """Get or create the task event publisher singleton."""
    global _task_event_publisher
    if _task_event_publisher is None:
        _task_event_publisher = DaprPublisher(topic="task-events")
    return _task_event_publisher


def _task_to_dict(task: Task) -> Dict[str, Any]:
    """
    Convert a Task model to a dictionary for event payload.

    Args:
        task: Task SQLModel instance

    Returns:
        Dictionary representation of the task
    """
    return {
        "id": str(task.id),
        "title": task.title,
        "description": task.description,
        "status": task.status if hasattr(task, 'status') else ("completed" if task.completed else "pending"),
        "priority": task.priority.value if hasattr(task.priority, 'value') else str(task.priority),
        "due_date": task.due_date.isoformat() + "Z" if task.due_date else None,
        "recurrence_pattern": task.recurrence_pattern.value if hasattr(task, 'recurrence_pattern') and task.recurrence_pattern and hasattr(task.recurrence_pattern, 'value') else (str(task.recurrence_pattern) if hasattr(task, 'recurrence_pattern') and task.recurrence_pattern else "none"),
        "tags": task.tags if hasattr(task, 'tags') else [],
        "created_at": task.created_at.isoformat() + "Z" if task.created_at else None,
        "updated_at": task.updated_at.isoformat() + "Z" if task.updated_at else None,
        "completed_at": task.completed_at.isoformat() + "Z" if hasattr(task, 'completed_at') and task.completed_at else None,
    }


def _build_task_event(
    event_type: TaskEventType,
    task_id: uuid.UUID,
    user_id: uuid.UUID,
    task_data: Optional[Dict[str, Any]] = None,
    previous_data: Optional[Dict[str, Any]] = None,
    correlation_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Build a task event payload following the task-event-schema.json contract.

    Args:
        event_type: Type of task event
        task_id: ID of the affected task
        user_id: ID of the user who performed the action
        task_data: Full task object (null for deleted events)
        previous_data: Previous task state (for updated events only)
        correlation_id: Optional correlation ID for tracing

    Returns:
        Event payload dictionary
    """
    event = {
        "event_id": str(uuid.uuid4()),
        "event_type": event_type.value,
        "task_id": str(task_id),
        "user_id": str(user_id),
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "correlation_id": correlation_id or str(uuid.uuid4()),
        "task_data": task_data,
    }

    # Include previous_data only for update events
    if event_type == TaskEventType.UPDATED and previous_data:
        event["previous_data"] = previous_data

    return event


async def publish_task_created(
    task: Task,
    user_id: uuid.UUID,
    correlation_id: Optional[str] = None
) -> bool:
    """
    Publish a task.created event (FR-001).

    Args:
        task: The created task
        user_id: ID of the user who created the task
        correlation_id: Optional correlation ID for tracing

    Returns:
        True if publish succeeded, False otherwise
    """
    publisher = get_task_event_publisher()
    task_data = _task_to_dict(task)
    event = _build_task_event(
        event_type=TaskEventType.CREATED,
        task_id=task.id,
        user_id=user_id,
        task_data=task_data,
        correlation_id=correlation_id
    )

    logger.info(
        f"Publishing task.created event for task {task.id}",
        extra={"task_id": str(task.id), "user_id": str(user_id)}
    )

    return await publisher.publish(event, correlation_id=event["correlation_id"])


async def publish_task_updated(
    task: Task,
    user_id: uuid.UUID,
    previous_task: Optional[Task] = None,
    correlation_id: Optional[str] = None
) -> bool:
    """
    Publish a task.updated event (FR-002).

    Args:
        task: The updated task
        user_id: ID of the user who updated the task
        previous_task: Previous state of the task (optional)
        correlation_id: Optional correlation ID for tracing

    Returns:
        True if publish succeeded, False otherwise
    """
    publisher = get_task_event_publisher()
    task_data = _task_to_dict(task)
    previous_data = _task_to_dict(previous_task) if previous_task else None
    event = _build_task_event(
        event_type=TaskEventType.UPDATED,
        task_id=task.id,
        user_id=user_id,
        task_data=task_data,
        previous_data=previous_data,
        correlation_id=correlation_id
    )

    logger.info(
        f"Publishing task.updated event for task {task.id}",
        extra={"task_id": str(task.id), "user_id": str(user_id)}
    )

    return await publisher.publish(event, correlation_id=event["correlation_id"])


async def publish_task_completed(
    task: Task,
    user_id: uuid.UUID,
    correlation_id: Optional[str] = None
) -> bool:
    """
    Publish a task.completed event (FR-003).

    This event triggers the recurring task service to create
    the next occurrence if the task has a recurrence pattern.

    Args:
        task: The completed task
        user_id: ID of the user who completed the task
        correlation_id: Optional correlation ID for tracing

    Returns:
        True if publish succeeded, False otherwise
    """
    publisher = get_task_event_publisher()
    task_data = _task_to_dict(task)
    event = _build_task_event(
        event_type=TaskEventType.COMPLETED,
        task_id=task.id,
        user_id=user_id,
        task_data=task_data,
        correlation_id=correlation_id
    )

    logger.info(
        f"Publishing task.completed event for task {task.id}",
        extra={
            "task_id": str(task.id),
            "user_id": str(user_id),
            "is_recurring": task_data.get("recurrence_pattern", "none") != "none"
        }
    )

    return await publisher.publish(event, correlation_id=event["correlation_id"])


async def publish_task_deleted(
    task_id: uuid.UUID,
    user_id: uuid.UUID,
    correlation_id: Optional[str] = None
) -> bool:
    """
    Publish a task.deleted event (FR-004).

    Args:
        task_id: ID of the deleted task
        user_id: ID of the user who deleted the task
        correlation_id: Optional correlation ID for tracing

    Returns:
        True if publish succeeded, False otherwise
    """
    publisher = get_task_event_publisher()
    event = _build_task_event(
        event_type=TaskEventType.DELETED,
        task_id=task_id,
        user_id=user_id,
        task_data=None,  # No task data for deleted events
        correlation_id=correlation_id
    )

    logger.info(
        f"Publishing task.deleted event for task {task_id}",
        extra={"task_id": str(task_id), "user_id": str(user_id)}
    )

    return await publisher.publish(event, correlation_id=event["correlation_id"])


# Convenience function for generic task event publishing
async def publish_task_event(
    event_type: str,
    task: Optional[Task] = None,
    task_id: Optional[uuid.UUID] = None,
    user_id: uuid.UUID = None,
    previous_task: Optional[Task] = None,
    correlation_id: Optional[str] = None
) -> bool:
    """
    Generic task event publisher - routes to specific event functions.

    Args:
        event_type: One of 'created', 'updated', 'completed', 'deleted'
        task: Task object (required for created, updated, completed)
        task_id: Task ID (required for deleted, optional for others)
        user_id: User ID who performed the action
        previous_task: Previous task state (for updated events)
        correlation_id: Optional correlation ID for tracing

    Returns:
        True if publish succeeded, False otherwise
    """
    if event_type == "created" and task:
        return await publish_task_created(task, user_id, correlation_id)
    elif event_type == "updated" and task:
        return await publish_task_updated(task, user_id, previous_task, correlation_id)
    elif event_type == "completed" and task:
        return await publish_task_completed(task, user_id, correlation_id)
    elif event_type == "deleted" and (task_id or (task and task.id)):
        return await publish_task_deleted(task_id or task.id, user_id, correlation_id)
    else:
        logger.warning(f"Invalid event_type or missing required parameters: {event_type}")
        return False
