"""
Recurring Task Service
Phase 5: Event-driven recurring task processing (FR-017, FR-018, FR-019)

This service consumes task completion events from Kafka via Dapr pub/sub
and creates the next occurrence of recurring tasks.
"""

from fastapi import FastAPI, Request
from datetime import datetime
import logging
import uvicorn

from app.config.settings import settings
from app.consumers.task_completion_consumer import process_task_completion_event
from app.utils.idempotency import is_event_processed, mark_event_processed

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Recurring Task Service",
    description="Event-driven service for creating next occurrences of recurring tasks",
    version="1.0.0-phase5"
)


@app.get("/")
async def root():
    """Service information endpoint."""
    return {
        "service": settings.SERVICE_NAME,
        "version": "1.0.0-phase5",
        "dapr_enabled": settings.DAPR_ENABLED,
        "description": "Consumes task completion events and creates next recurring task occurrences"
    }


@app.get("/health")
async def health():
    """Liveness probe endpoint."""
    return {
        "status": "healthy",
        "service": settings.SERVICE_NAME,
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/ready")
async def ready():
    """Readiness probe endpoint."""
    return {
        "status": "ready",
        "service": settings.SERVICE_NAME,
        "timestamp": datetime.utcnow().isoformat()
    }


# Dapr Subscription Declaration (FR-030)
@app.get("/dapr/subscribe")
async def dapr_subscribe():
    """
    Declare Dapr pub/sub subscriptions.

    Tells Dapr that this service wants to receive task.completed events
    from the 'task-events' topic.
    """
    subscriptions = []

    if settings.DAPR_ENABLED:
        subscriptions = [
            {
                "pubsubname": settings.PUBSUB_NAME,
                "topic": settings.TASK_EVENTS_TOPIC,
                "route": "/api/events/task-completed",
                "metadata": {
                    "rawPayload": "true"
                }
            }
        ]
        logger.info(f"Dapr subscriptions declared: {len(subscriptions)} topics")

    return subscriptions


# Task Completion Event Handler (FR-018, FR-019)
@app.post("/api/events/task-completed")
async def handle_task_completion_event(request: Request):
    """
    Handle incoming task completion events from Dapr pub/sub.

    This endpoint is called by Dapr when a task.completed event is published.
    It checks if the task is recurring and creates the next occurrence.
    """
    try:
        event_data = await request.json()
        event_id = event_data.get("event_id", "unknown")
        event_type = event_data.get("event_type", "unknown")

        # Only process task.completed events
        if event_type != "task.completed":
            logger.debug(f"Ignoring event type: {event_type}")
            return {"status": "SUCCESS", "message": f"Ignored event type: {event_type}"}

        logger.info(
            f"Received task.completed event",
            extra={"event_id": event_id, "event_type": event_type}
        )

        # Idempotency check (FR-022)
        if await is_event_processed(event_id, settings.SERVICE_NAME):
            logger.info(f"Event {event_id} already processed, skipping")
            return {"status": "SUCCESS", "message": "Already processed"}

        # Process the task completion event
        result = await process_task_completion_event(event_data)

        # Mark event as processed
        await mark_event_processed(event_id, settings.SERVICE_NAME)

        return {"status": "SUCCESS", "result": result}

    except Exception as e:
        logger.error(f"Error handling task completion event: {e}")
        # Return success to prevent Dapr retries for malformed events
        return {"status": "SUCCESS", "error": str(e)}


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=settings.SERVICE_PORT,
        reload=settings.ENVIRONMENT == "development"
    )
