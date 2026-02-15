"""
Task Completion Event Consumer
Phase 5: Process task completion events and create next occurrences (FR-018, FR-019)

This consumer processes task.completed events for recurring tasks
and creates the next occurrence via Dapr Service Invocation.
"""

import logging
import httpx
from typing import Any, Dict, Optional
from datetime import datetime

from app.config.settings import settings
from app.utils.recurrence_calculator import calculate_next_due_date

logger = logging.getLogger(__name__)


async def process_task_completion_event(event_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process a task.completed event and create next occurrence if recurring.

    Args:
        event_data: The task.completed event payload

    Returns:
        Processing result dictionary
    """
    event_type = event_data.get("event_type", "unknown")
    task_id = event_data.get("task_id", "unknown")
    user_id = event_data.get("user_id", "unknown")
    task_data = event_data.get("task_data", {})
    correlation_id = event_data.get("correlation_id")

    logger.info(
        f"Processing task.completed event",
        extra={
            "event_type": event_type,
            "task_id": task_id,
            "user_id": user_id,
            "correlation_id": correlation_id
        }
    )

    # Check if task is recurring
    recurrence_pattern = task_data.get("recurrence_pattern", "none")

    if recurrence_pattern == "none" or not recurrence_pattern:
        logger.info(f"Task {task_id} is not recurring, no action needed")
        return {
            "status": "skipped",
            "reason": "Task is not recurring",
            "task_id": task_id
        }

    # Get current due date
    current_due_date_str = task_data.get("due_date")
    if not current_due_date_str:
        logger.info(f"Task {task_id} has no due date, cannot calculate next occurrence")
        return {
            "status": "skipped",
            "reason": "Task has no due date",
            "task_id": task_id
        }

    # Calculate next due date (FR-020, FR-021)
    try:
        current_due_date = datetime.fromisoformat(current_due_date_str.replace("Z", "+00:00"))
        next_due_date = calculate_next_due_date(current_due_date, recurrence_pattern)
    except Exception as e:
        logger.error(f"Error calculating next due date: {e}")
        return {
            "status": "error",
            "reason": f"Failed to calculate next due date: {str(e)}",
            "task_id": task_id
        }

    # Create next occurrence via Dapr Service Invocation (FR-026)
    result = await _create_next_task_occurrence(
        user_id=user_id,
        title=task_data.get("title", "Recurring Task"),
        description=task_data.get("description"),
        priority=task_data.get("priority", "none"),
        due_date=next_due_date,
        recurrence_pattern=recurrence_pattern,
        tags=task_data.get("tags", [])
    )

    return result


async def _create_next_task_occurrence(
    user_id: str,
    title: str,
    description: Optional[str],
    priority: str,
    due_date: datetime,
    recurrence_pattern: str,
    tags: list
) -> Dict[str, Any]:
    """
    Create the next occurrence of a recurring task via Dapr Service Invocation.

    Uses Dapr's service invocation to call the backend API for creating tasks.
    """
    logger.info(
        f"Creating next occurrence for recurring task",
        extra={
            "user_id": user_id,
            "title": title,
            "next_due_date": due_date.isoformat(),
            "recurrence_pattern": recurrence_pattern
        }
    )

    if not settings.DAPR_ENABLED:
        logger.info("Dapr disabled, skipping task creation")
        return {
            "status": "skipped",
            "reason": "Dapr disabled",
            "would_create": {
                "title": title,
                "due_date": due_date.isoformat()
            }
        }

    try:
        # Build task creation payload
        task_payload = {
            "title": title,
            "description": description,
            "priority": priority,
            "due_date": due_date.isoformat(),
            "recurrence_pattern": recurrence_pattern,
            "tags": tags
        }

        # Use Dapr Service Invocation to call backend API
        # URL format: http://localhost:<dapr-port>/v1.0/invoke/<app-id>/method/<endpoint>
        invoke_url = f"{settings.DAPR_INVOKE_URL}/{user_id}/tasks"

        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                invoke_url,
                json=task_payload,
                headers={"Content-Type": "application/json"}
            )

            if response.status_code in (200, 201):
                created_task = response.json()
                logger.info(
                    f"Successfully created next occurrence: {created_task.get('id')}",
                    extra={
                        "new_task_id": created_task.get("id"),
                        "user_id": user_id
                    }
                )
                return {
                    "status": "created",
                    "new_task_id": created_task.get("id"),
                    "title": title,
                    "due_date": due_date.isoformat()
                }
            else:
                logger.warning(
                    f"Failed to create next occurrence: {response.status_code}",
                    extra={"status_code": response.status_code, "response": response.text[:200]}
                )
                return {
                    "status": "error",
                    "reason": f"Backend returned {response.status_code}",
                    "details": response.text[:200]
                }

    except httpx.TimeoutException:
        logger.warning("Timeout creating next task occurrence")
        return {"status": "error", "reason": "Timeout calling backend"}
    except Exception as e:
        logger.error(f"Error creating next task occurrence: {e}")
        return {"status": "error", "reason": str(e)}
