"""
Reminder Event Publisher
Phase 5: Event-driven reminder notifications (FR-012, FR-013)

Publishes reminder events to the reminders Kafka topic via Dapr pub/sub.
"""

import uuid
import logging
from typing import Any, Dict, Optional
from datetime import datetime

from app.publishers.base_publisher import DaprPublisher

logger = logging.getLogger(__name__)


class ReminderEventType:
    """Reminder event types."""
    TRIGGERED = "reminder.triggered"
    SCHEDULED = "reminder.scheduled"
    CANCELLED = "reminder.cancelled"


# Global publisher instance for reminder events
_reminder_publisher: Optional[DaprPublisher] = None


def get_reminder_publisher() -> DaprPublisher:
    """Get or create the reminder event publisher singleton."""
    global _reminder_publisher
    if _reminder_publisher is None:
        _reminder_publisher = DaprPublisher(topic="reminders")
    return _reminder_publisher


def _build_reminder_event(
    event_type: str,
    task_id: str,
    user_id: str,
    title: str,
    due_date: Optional[str] = None,
    remind_at: Optional[str] = None,
    correlation_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Build a reminder event payload following the reminder-event-schema.json contract.

    Args:
        event_type: Type of reminder event
        task_id: ID of the task
        user_id: ID of the user who owns the task
        title: Task title
        due_date: When the task is due
        remind_at: When the reminder was triggered
        correlation_id: Optional correlation ID for tracing

    Returns:
        Event payload dictionary
    """
    return {
        "event_id": str(uuid.uuid4()),
        "event_type": event_type,
        "task_id": task_id,
        "user_id": user_id,
        "title": title,
        "due_date": due_date,
        "remind_at": remind_at,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "correlation_id": correlation_id or str(uuid.uuid4())
    }


async def publish_reminder_triggered(
    task_id: str,
    user_id: str,
    title: str,
    due_date: Optional[str] = None,
    remind_at: Optional[str] = None,
    correlation_id: Optional[str] = None
) -> bool:
    """
    Publish a reminder.triggered event.

    This event is consumed by the notification service to send user notifications.

    Args:
        task_id: ID of the task
        user_id: ID of the user
        title: Task title
        due_date: When the task is due
        remind_at: When the reminder was triggered
        correlation_id: Optional correlation ID for tracing

    Returns:
        True if publish succeeded, False otherwise
    """
    publisher = get_reminder_publisher()
    event = _build_reminder_event(
        event_type=ReminderEventType.TRIGGERED,
        task_id=task_id,
        user_id=user_id,
        title=title,
        due_date=due_date,
        remind_at=remind_at,
        correlation_id=correlation_id
    )

    logger.info(
        f"Publishing reminder.triggered event for task {task_id}",
        extra={"task_id": task_id, "user_id": user_id}
    )

    return await publisher.publish(event, correlation_id=event["correlation_id"])


async def publish_reminder_scheduled(
    task_id: str,
    user_id: str,
    title: str,
    due_date: str,
    remind_at: str,
    correlation_id: Optional[str] = None
) -> bool:
    """
    Publish a reminder.scheduled event (for audit/logging).

    Args:
        task_id: ID of the task
        user_id: ID of the user
        title: Task title
        due_date: When the task is due
        remind_at: When the reminder will trigger
        correlation_id: Optional correlation ID

    Returns:
        True if publish succeeded, False otherwise
    """
    publisher = get_reminder_publisher()
    event = _build_reminder_event(
        event_type=ReminderEventType.SCHEDULED,
        task_id=task_id,
        user_id=user_id,
        title=title,
        due_date=due_date,
        remind_at=remind_at,
        correlation_id=correlation_id
    )

    logger.info(
        f"Publishing reminder.scheduled event for task {task_id}",
        extra={"task_id": task_id, "remind_at": remind_at}
    )

    return await publisher.publish(event, correlation_id=event["correlation_id"])


async def publish_reminder_cancelled(
    task_id: str,
    user_id: str,
    correlation_id: Optional[str] = None
) -> bool:
    """
    Publish a reminder.cancelled event (for audit/logging).

    Args:
        task_id: ID of the task
        user_id: ID of the user
        correlation_id: Optional correlation ID

    Returns:
        True if publish succeeded, False otherwise
    """
    publisher = get_reminder_publisher()
    event = _build_reminder_event(
        event_type=ReminderEventType.CANCELLED,
        task_id=task_id,
        user_id=user_id,
        title="",  # Not needed for cancellation
        correlation_id=correlation_id
    )

    logger.info(
        f"Publishing reminder.cancelled event for task {task_id}",
        extra={"task_id": task_id}
    )

    return await publisher.publish(event, correlation_id=event["correlation_id"])
