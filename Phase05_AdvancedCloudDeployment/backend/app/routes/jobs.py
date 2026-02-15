"""
Jobs Endpoints for Dapr Jobs API Callbacks
Phase 5: Scheduled job trigger handlers (FR-009)

These endpoints are called by Dapr Jobs API when scheduled jobs trigger.
They handle reminder notifications and other scheduled tasks.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlmodel import Session, select
from datetime import datetime
from typing import Optional, Dict, Any
import logging
import asyncio
import uuid

from app.database import get_session
from app.models.task import Task
from app.config.settings import settings
from app.publishers.task_event_publisher import publish_task_event

router = APIRouter()
logger = logging.getLogger(__name__)


class ReminderEvent:
    """Reminder event data structure."""

    def __init__(self, data: Dict[str, Any]):
        self.task_id = data.get("task_id")
        self.user_id = data.get("user_id")
        self.title = data.get("title")
        self.due_date = data.get("due_date")
        self.remind_at = data.get("remind_at")
        self.event_type = data.get("event_type", "reminder.triggered")


@router.post("/trigger")
async def handle_job_trigger(
    request: Request,
    session: Session = Depends(get_session)
):
    """
    Callback endpoint triggered by Dapr Jobs API.

    When a scheduled job fires, Dapr calls this endpoint with the job data.
    This handles reminder notifications by publishing events to Kafka.

    Note: This does NOT modify any tasks - it only publishes reminder events.
    """
    try:
        job_data = await request.json()
        logger.info(f"Job trigger received: {job_data}")

        # Extract job metadata and data
        job_name = job_data.get("name", "unknown")
        data = job_data.get("data", {})

        # Handle reminder jobs
        if job_name.startswith("reminder-"):
            return await _handle_reminder_trigger(data, session)

        # Handle other job types here
        logger.info(f"Unknown job type: {job_name}")
        return {"status": "SUCCESS", "message": f"Job {job_name} acknowledged"}

    except Exception as e:
        logger.error(f"Error handling job trigger: {e}")
        # Return success to prevent Dapr retries for malformed jobs
        return {"status": "SUCCESS", "error": str(e)}


async def _handle_reminder_trigger(
    data: Dict[str, Any],
    session: Session
) -> Dict[str, Any]:
    """
    Handle reminder job trigger.

    Publishes a reminder event to Kafka for the notification service to process.
    """
    reminder = ReminderEvent(data)

    logger.info(
        f"Reminder triggered for task {reminder.task_id}",
        extra={
            "task_id": reminder.task_id,
            "user_id": reminder.user_id,
            "title": reminder.title
        }
    )

    # Verify task still exists and is not completed
    if reminder.task_id:
        try:
            task = session.get(Task, uuid.UUID(reminder.task_id))
            if not task:
                logger.info(f"Task {reminder.task_id} no longer exists, skipping reminder")
                return {"status": "SUCCESS", "message": "Task deleted, reminder skipped"}

            if task.status == "completed":
                logger.info(f"Task {reminder.task_id} already completed, skipping reminder")
                return {"status": "SUCCESS", "message": "Task completed, reminder skipped"}
        except Exception as e:
            logger.warning(f"Error checking task status: {e}")

    # Publish reminder event to Kafka (via Dapr pub/sub)
    if settings.DAPR_ENABLED:
        try:
            from app.publishers.reminder_event_publisher import publish_reminder_triggered
            asyncio.create_task(
                publish_reminder_triggered(
                    task_id=reminder.task_id,
                    user_id=reminder.user_id,
                    title=reminder.title,
                    due_date=reminder.due_date,
                    remind_at=reminder.remind_at
                )
            )
        except Exception as e:
            logger.warning(f"Failed to publish reminder event: {e}")

    return {
        "status": "SUCCESS",
        "message": f"Reminder processed for task {reminder.task_id}",
        "task_id": reminder.task_id
    }


@router.get("/health")
async def jobs_health():
    """Health check endpoint for jobs service."""
    return {
        "status": "healthy",
        "service": "jobs",
        "dapr_enabled": settings.DAPR_ENABLED,
        "timestamp": datetime.utcnow().isoformat()
    }
