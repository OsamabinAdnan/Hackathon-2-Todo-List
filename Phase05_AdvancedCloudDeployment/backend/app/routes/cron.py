"""
Cron Endpoints for Dapr Bindings
Phase 5: Periodic task processing via Dapr Cron Binding (FR-027)

These endpoints are triggered by Dapr Cron Bindings for scheduled operations.
They do not affect your existing database or application logic.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from datetime import datetime, timedelta
import logging

from app.database import get_session
from app.models.task import Task
from app.config.settings import settings

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/overdue-check")
async def check_overdue_tasks(
    session: Session = Depends(get_session)
):
    """
    Endpoint triggered by Dapr Cron Binding to check for overdue tasks.

    This is called periodically by Dapr (configured in cron-binding.yaml).
    It logs overdue tasks for monitoring purposes.

    Note: This does NOT modify any tasks - it's for monitoring/alerting only.
    """
    logger.info("Cron: Starting overdue task check")

    try:
        # Find tasks that are overdue (due_date passed and not completed)
        now = datetime.utcnow()

        statement = select(Task).where(
            Task.due_date < now,
            Task.status != "completed"
        )

        overdue_tasks = session.exec(statement).all()

        overdue_count = len(overdue_tasks)

        if overdue_count > 0:
            logger.warning(f"Cron: Found {overdue_count} overdue tasks")

            # Log summary by user (for monitoring dashboards)
            user_overdue = {}
            for task in overdue_tasks:
                user_id = str(task.user_id)
                if user_id not in user_overdue:
                    user_overdue[user_id] = 0
                user_overdue[user_id] += 1

            for user_id, count in user_overdue.items():
                logger.info(f"Cron: User {user_id[:8]}... has {count} overdue tasks")
        else:
            logger.info("Cron: No overdue tasks found")

        return {
            "status": "success",
            "checked_at": now.isoformat(),
            "overdue_count": overdue_count
        }

    except Exception as e:
        logger.error(f"Cron: Error checking overdue tasks: {e}")
        return {
            "status": "error",
            "error": str(e),
            "checked_at": datetime.utcnow().isoformat()
        }


@router.post("/reminder-check")
async def check_upcoming_reminders(
    session: Session = Depends(get_session)
):
    """
    Endpoint triggered by Dapr Cron Binding to check for upcoming task reminders.

    Finds tasks with due dates within the next hour and logs them.
    Future enhancement: Publish reminder events to Kafka.

    Note: This does NOT modify any tasks - it's for monitoring/alerting only.
    """
    logger.info("Cron: Starting reminder check")

    try:
        now = datetime.utcnow()
        one_hour_later = now + timedelta(hours=1)

        # Find tasks due within the next hour that aren't completed
        statement = select(Task).where(
            Task.due_date >= now,
            Task.due_date <= one_hour_later,
            Task.status != "completed"
        )

        upcoming_tasks = session.exec(statement).all()

        upcoming_count = len(upcoming_tasks)

        if upcoming_count > 0:
            logger.info(f"Cron: Found {upcoming_count} tasks due within the next hour")

            for task in upcoming_tasks:
                logger.info(
                    f"Cron: Reminder - Task '{task.title}' "
                    f"due at {task.due_date.isoformat()} "
                    f"for user {str(task.user_id)[:8]}..."
                )
        else:
            logger.info("Cron: No upcoming tasks in the next hour")

        return {
            "status": "success",
            "checked_at": now.isoformat(),
            "upcoming_count": upcoming_count
        }

    except Exception as e:
        logger.error(f"Cron: Error checking reminders: {e}")
        return {
            "status": "error",
            "error": str(e),
            "checked_at": datetime.utcnow().isoformat()
        }


@router.get("/health")
async def cron_health():
    """
    Health check endpoint for cron service.
    """
    return {
        "status": "healthy",
        "service": "cron",
        "dapr_enabled": settings.DAPR_ENABLED,
        "timestamp": datetime.utcnow().isoformat()
    }
