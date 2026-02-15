"""
Reminder Scheduler Service
Phase 5: Dapr Jobs API for scheduled reminders (FR-008, FR-009, FR-010, FR-011)

Schedules reminders for tasks with due dates using Dapr's scheduled jobs.
Falls back gracefully when Dapr is unavailable.
"""

import httpx
import logging
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from uuid import UUID

from app.config.settings import settings

logger = logging.getLogger(__name__)


class ReminderScheduler:
    """
    Schedules task reminders using Dapr Jobs API.

    When a task with a due date is created/updated, this service schedules
    a reminder job that will trigger at the specified time.

    Falls back gracefully when Dapr is unavailable - reminders won't fire
    but the app continues working.
    """

    def __init__(self):
        self.dapr_port = settings.DAPR_HTTP_PORT
        self.enabled = settings.DAPR_ENABLED
        self.base_url = f"http://localhost:{self.dapr_port}/v1.0/jobs"

    def _get_job_name(self, task_id: UUID) -> str:
        """Generate unique job name for a task reminder."""
        return f"reminder-{task_id}"

    async def schedule_reminder(
        self,
        task_id: UUID,
        user_id: UUID,
        title: str,
        due_date: datetime,
        remind_before_minutes: int = 30
    ) -> bool:
        """
        Schedule a reminder for a task.

        Args:
            task_id: Task UUID
            user_id: User UUID who owns the task
            title: Task title for the reminder
            due_date: When the task is due
            remind_before_minutes: How many minutes before due_date to remind (default: 30)

        Returns:
            True if scheduled successfully, False otherwise
        """
        if not self.enabled:
            logger.debug("Dapr disabled, skipping reminder scheduling")
            return True  # Return True so app continues normally

        # Calculate remind_at time
        remind_at = due_date - timedelta(minutes=remind_before_minutes)

        # Don't schedule if remind_at is in the past
        if remind_at <= datetime.utcnow():
            logger.debug(f"Reminder time already passed for task {task_id}, skipping")
            return True

        job_name = self._get_job_name(task_id)

        try:
            # Dapr Jobs API payload
            job_data = {
                "name": job_name,
                "schedule": remind_at.isoformat() + "Z",  # One-time job at specific time
                "repeats": 1,
                "data": {
                    "task_id": str(task_id),
                    "user_id": str(user_id),
                    "title": title,
                    "due_date": due_date.isoformat() + "Z",
                    "remind_at": remind_at.isoformat() + "Z",
                    "event_type": "reminder.triggered"
                }
            }

            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.post(
                    self.base_url,
                    json=job_data,
                    headers={"Content-Type": "application/json"}
                )

                if response.status_code in (200, 201, 204):
                    logger.info(
                        f"Reminder scheduled for task {task_id} at {remind_at.isoformat()}",
                        extra={"task_id": str(task_id), "remind_at": remind_at.isoformat()}
                    )
                    return True
                else:
                    logger.warning(
                        f"Failed to schedule reminder for task {task_id}: {response.status_code}",
                        extra={"task_id": str(task_id), "status_code": response.status_code}
                    )
                    return False

        except httpx.TimeoutException:
            logger.warning(f"Timeout scheduling reminder for task {task_id}")
            return False
        except Exception as e:
            logger.warning(f"Error scheduling reminder for task {task_id}: {e}")
            return False

    async def cancel_reminder(self, task_id: UUID) -> bool:
        """
        Cancel a scheduled reminder for a task.

        Args:
            task_id: Task UUID

        Returns:
            True if cancelled successfully (or not found), False on error
        """
        if not self.enabled:
            logger.debug("Dapr disabled, skipping reminder cancellation")
            return True

        job_name = self._get_job_name(task_id)

        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.delete(f"{self.base_url}/{job_name}")

                if response.status_code in (200, 204, 404):
                    # 404 is OK - job might not exist
                    logger.info(f"Reminder cancelled for task {task_id}")
                    return True
                else:
                    logger.warning(
                        f"Failed to cancel reminder for task {task_id}: {response.status_code}"
                    )
                    return False

        except httpx.TimeoutException:
            logger.warning(f"Timeout cancelling reminder for task {task_id}")
            return False
        except Exception as e:
            logger.warning(f"Error cancelling reminder for task {task_id}: {e}")
            return False

    async def reschedule_reminder(
        self,
        task_id: UUID,
        user_id: UUID,
        title: str,
        new_due_date: datetime,
        remind_before_minutes: int = 30
    ) -> bool:
        """
        Reschedule a reminder for a task (cancel old, create new).

        Args:
            task_id: Task UUID
            user_id: User UUID
            title: Task title
            new_due_date: New due date
            remind_before_minutes: Minutes before due date to remind

        Returns:
            True if rescheduled successfully, False otherwise
        """
        # Cancel existing reminder
        await self.cancel_reminder(task_id)

        # Schedule new reminder
        return await self.schedule_reminder(
            task_id=task_id,
            user_id=user_id,
            title=title,
            due_date=new_due_date,
            remind_before_minutes=remind_before_minutes
        )


# Singleton instance
_reminder_scheduler: Optional[ReminderScheduler] = None


def get_reminder_scheduler() -> ReminderScheduler:
    """Get or create singleton reminder scheduler instance."""
    global _reminder_scheduler
    if _reminder_scheduler is None:
        _reminder_scheduler = ReminderScheduler()
    return _reminder_scheduler
