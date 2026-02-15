"""
Notification Service
Phase 5: Event-driven reminder notification processing (FR-012, FR-013, FR-014)

This service consumes reminder events from Kafka via Dapr pub/sub
and logs notifications (can be extended to send emails, push notifications, etc.)
"""

from fastapi import FastAPI, Request
from datetime import datetime
import logging
import uvicorn

from app.config.settings import settings
from app.consumers.reminder_consumer import process_reminder_event
from app.utils.idempotency import is_event_processed, mark_event_processed

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Notification Service",
    description="Event-driven notification service for Todo app reminders",
    version="1.0.0-phase5"
)


@app.get("/")
async def root():
    """Service information endpoint."""
    return {
        "service": settings.SERVICE_NAME,
        "version": "1.0.0-phase5",
        "dapr_enabled": settings.DAPR_ENABLED,
        "description": "Consumes reminder events and sends notifications"
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

    Tells Dapr that this service wants to receive events from the 'reminders' topic.
    """
    subscriptions = []

    if settings.DAPR_ENABLED:
        subscriptions = [
            {
                "pubsubname": settings.PUBSUB_NAME,
                "topic": "reminders",
                "route": "/api/events/reminder",
                "metadata": {
                    "rawPayload": "true"
                }
            }
        ]
        logger.info(f"Dapr subscriptions declared: {len(subscriptions)} topics")

    return subscriptions


# Reminder Event Handler (FR-013, FR-014)
@app.post("/api/events/reminder")
async def handle_reminder_event(request: Request):
    """
    Handle incoming reminder events from Dapr pub/sub.

    This endpoint is called by Dapr when a reminder event is published
    to the 'reminders' topic.
    """
    try:
        event_data = await request.json()
        event_id = event_data.get("event_id", "unknown")
        event_type = event_data.get("event_type", "unknown")

        logger.info(
            f"Received reminder event: {event_type}",
            extra={"event_id": event_id, "event_type": event_type}
        )

        # Idempotency check (FR-015)
        if await is_event_processed(event_id, settings.SERVICE_NAME):
            logger.info(f"Event {event_id} already processed, skipping")
            return {"status": "SUCCESS", "message": "Already processed"}

        # Process the reminder event
        result = await process_reminder_event(event_data)

        # Mark event as processed (FR-015)
        await mark_event_processed(event_id, settings.SERVICE_NAME)

        return {"status": "SUCCESS", "result": result}

    except Exception as e:
        logger.error(f"Error handling reminder event: {e}")
        # Return success to prevent Dapr retries for malformed events
        return {"status": "SUCCESS", "error": str(e)}


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=settings.SERVICE_PORT,
        reload=settings.ENVIRONMENT == "development"
    )
