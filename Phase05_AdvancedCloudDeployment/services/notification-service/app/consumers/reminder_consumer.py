"""
Reminder Event Consumer
Phase 5: Process reminder events and send notifications (FR-013, FR-014)

This consumer processes reminder.triggered events and logs notifications.
In a production system, this would integrate with email/SMS/push notification services.
"""

import logging
from typing import Any, Dict
from datetime import datetime

logger = logging.getLogger(__name__)


async def process_reminder_event(event_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process a reminder event and send notification.

    Currently logs the reminder. Can be extended to:
    - Send email notifications
    - Send push notifications
    - Send SMS alerts
    - Integrate with Slack/Discord webhooks

    Args:
        event_data: The reminder event payload

    Returns:
        Processing result dictionary
    """
    event_type = event_data.get("event_type", "unknown")
    task_id = event_data.get("task_id", "unknown")
    user_id = event_data.get("user_id", "unknown")
    title = event_data.get("title", "Unknown task")
    due_date = event_data.get("due_date")
    remind_at = event_data.get("remind_at")
    correlation_id = event_data.get("correlation_id")

    logger.info(
        f"Processing reminder event",
        extra={
            "event_type": event_type,
            "task_id": task_id,
            "user_id": user_id,
            "correlation_id": correlation_id
        }
    )

    if event_type == "reminder.triggered":
        return await _handle_reminder_triggered(
            task_id=task_id,
            user_id=user_id,
            title=title,
            due_date=due_date,
            remind_at=remind_at
        )
    elif event_type == "reminder.scheduled":
        return await _handle_reminder_scheduled(
            task_id=task_id,
            user_id=user_id,
            title=title,
            remind_at=remind_at
        )
    elif event_type == "reminder.cancelled":
        return await _handle_reminder_cancelled(
            task_id=task_id,
            user_id=user_id
        )
    else:
        logger.warning(f"Unknown reminder event type: {event_type}")
        return {"status": "ignored", "reason": f"Unknown event type: {event_type}"}


async def _handle_reminder_triggered(
    task_id: str,
    user_id: str,
    title: str,
    due_date: str,
    remind_at: str
) -> Dict[str, Any]:
    """
    Handle reminder.triggered event - send notification to user.

    This is the main notification handler. Currently logs the reminder.
    """
    # Format the notification message
    notification_message = f"Reminder: '{title}' is due soon!"

    if due_date:
        try:
            due_dt = datetime.fromisoformat(due_date.replace("Z", "+00:00"))
            notification_message += f" Due at: {due_dt.strftime('%Y-%m-%d %H:%M')}"
        except (ValueError, AttributeError):
            pass

    # Log the notification (in production, this would send to notification service)
    logger.info(
        f"📢 NOTIFICATION for user {user_id[:8]}...: {notification_message}",
        extra={
            "notification_type": "reminder",
            "task_id": task_id,
            "user_id": user_id,
            "title": title
        }
    )

    # TODO: In production, integrate with:
    # - Email service (SendGrid, AWS SES, etc.)
    # - Push notification service (Firebase, OneSignal, etc.)
    # - SMS service (Twilio, etc.)
    # - Webhook service (Slack, Discord, etc.)

    return {
        "status": "notified",
        "task_id": task_id,
        "user_id": user_id,
        "message": notification_message,
        "processed_at": datetime.utcnow().isoformat()
    }


async def _handle_reminder_scheduled(
    task_id: str,
    user_id: str,
    title: str,
    remind_at: str
) -> Dict[str, Any]:
    """
    Handle reminder.scheduled event - log for audit purposes.
    """
    logger.info(
        f"Reminder scheduled for task {task_id} at {remind_at}",
        extra={
            "task_id": task_id,
            "user_id": user_id,
            "remind_at": remind_at
        }
    )

    return {
        "status": "logged",
        "event_type": "reminder.scheduled",
        "task_id": task_id
    }


async def _handle_reminder_cancelled(
    task_id: str,
    user_id: str
) -> Dict[str, Any]:
    """
    Handle reminder.cancelled event - log for audit purposes.
    """
    logger.info(
        f"Reminder cancelled for task {task_id}",
        extra={
            "task_id": task_id,
            "user_id": user_id
        }
    )

    return {
        "status": "logged",
        "event_type": "reminder.cancelled",
        "task_id": task_id
    }
