from datetime import datetime
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.requests import Request
from app.config.settings import settings
from app.database import init_db
import uvicorn
import logging

# Import routers
from app.routes import auth, tasks, users, chat
from app.routes import cron  # Phase 5: Cron endpoints for Dapr bindings
from app.routes import jobs  # Phase 5: Jobs endpoints for Dapr Jobs API callbacks

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Taskify API",
    description="Powerful multi-user task management application with JWT authentication, recurring tasks, and advanced features",
    version="2.0.0",
    docs_url="/docs",  # Swagger UI
    redoc_url="/redoc",  # ReDoc
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Register routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(tasks.router, prefix="/api", tags=["Tasks"])
app.include_router(users.router, prefix="/api/users", tags=["Users"])
app.include_router(chat.router, prefix="/api", tags=["Chat"])
app.include_router(cron.router, prefix="/api/cron", tags=["Cron"])  # Phase 5: Dapr Cron Bindings
app.include_router(jobs.router, prefix="/api/jobs", tags=["Jobs"])  # Phase 5: Dapr Jobs API


# Phase 5: Dapr Subscription Declaration Endpoint (FR-030)
# This tells Dapr which topics this service subscribes to
@app.get("/dapr/subscribe")
async def dapr_subscribe():
    """
    Dapr subscription declaration endpoint.

    Tells Dapr which pub/sub topics this service wants to subscribe to.
    This is called by Dapr sidecar during initialization.

    Note: This doesn't modify your app - it just declares what events
    this service is interested in receiving.
    """
    subscriptions = []

    # Only declare subscriptions if Dapr is enabled
    if settings.DAPR_ENABLED:
        subscriptions = [
            {
                "pubsubname": settings.PUBSUB_NAME,
                "topic": "task-events",
                "route": "/api/events/task",
                "metadata": {
                    "rawPayload": "true"
                }
            },
            {
                "pubsubname": settings.PUBSUB_NAME,
                "topic": "task-updates",
                "route": "/api/events/task-update",
                "metadata": {
                    "rawPayload": "true"
                }
            }
        ]
        logger.info(f"Dapr subscriptions declared: {len(subscriptions)} topics")

    return subscriptions


# Phase 5: Event handler endpoints for Dapr subscriptions
@app.post("/api/events/task")
async def handle_task_event(request: Request):
    """
    Handle incoming task events from Dapr pub/sub.

    This endpoint receives task-events published by other services.
    Currently logs events - extend for real-time sync, analytics, etc.
    """
    try:
        event_data = await request.json()
        event_type = event_data.get("event_type", "unknown")
        task_id = event_data.get("task_id", "unknown")

        logger.info(f"Received task event: {event_type} for task {task_id}")

        # Acknowledge receipt (required for Dapr)
        return {"status": "SUCCESS"}

    except Exception as e:
        logger.error(f"Error handling task event: {e}")
        # Return success to prevent Dapr retries for malformed events
        return {"status": "SUCCESS"}


@app.post("/api/events/task-update")
async def handle_task_update_event(request: Request):
    """
    Handle real-time task update events from Dapr pub/sub.

    This endpoint receives task-updates for real-time client sync.
    Can be extended to broadcast via WebSocket.
    """
    try:
        event_data = await request.json()
        task_id = event_data.get("task_id", "unknown")
        user_id = event_data.get("user_id", "unknown")

        logger.info(f"Received task-update event for task {task_id}, user {user_id[:8]}...")

        # Acknowledge receipt (required for Dapr)
        return {"status": "SUCCESS"}

    except Exception as e:
        logger.error(f"Error handling task-update event: {e}")
        return {"status": "SUCCESS"}

@app.on_event("startup")
async def startup():
    init_db()

@app.get("/", summary="API information", description="Get API information and available endpoints")
async def root():
    return {
        "message": "Taskify API",
        "description": "Powerful multi-user task management application with JWT authentication, recurring tasks, and advanced features",
        "version": "2.0.0",
        "endpoints": {
            "/": "API information and available endpoints (this endpoint)",
            "/health": "Health check endpoint for Kubernetes liveness/readiness probes",
            "/docs": "Interactive API documentation (Swagger UI)",
            "/redoc": "Alternative API documentation (ReDoc)",
            "/api/auth/signup": "POST endpoint to register a new user account",
            "/api/auth/login": "POST endpoint to authenticate user with email/password",
            "/api/auth/logout": "POST endpoint to end current user session (client-side token cleanup)",
            "/api/users/me": "GET endpoint to get current authenticated user information (requires JWT token)",
            "/api/users/me": "DELETE endpoint to delete current user account (requires JWT token)",
            "/api/users/me": "PATCH endpoint to update current user profile (requires JWT token)",
            "/api/{user_id}/tasks": "GET endpoint to retrieve all tasks with filtering, sorting, and pagination (requires JWT token)",
            "/api/{user_id}/tasks": "POST endpoint to create a new task (requires JWT token)",
            "/api/{user_id}/tasks/{task_id}": "GET endpoint to retrieve a specific task (requires JWT token)",
            "/api/{user_id}/tasks/{task_id}": "PUT endpoint to update a specific task (requires JWT token)",
            "/api/{user_id}/tasks/{task_id}": "DELETE endpoint to delete a specific task (requires JWT token)",
            "/api/{user_id}/tasks/{task_id}/complete": "PATCH endpoint to toggle task completion status (requires JWT token)",
            "/api/{user_id}/chat": "POST endpoint to send messages and get AI responses (requires JWT token)",
            "/api/{user_id}/conversations/{conversation_id}/messages": "GET endpoint to retrieve conversation history (requires JWT token)",
            "/api/{user_id}/conversations": "POST endpoint to create a new conversation (requires JWT token)",
            "/api/{user_id}/conversations": "GET endpoint to list all user's conversations (requires JWT token)",
            "/api/cron/overdue-check": "POST endpoint triggered by Dapr Cron Binding for overdue task monitoring (Phase 5)",
            "/api/cron/reminder-check": "POST endpoint triggered by Dapr Cron Binding for upcoming reminders (Phase 5)",
            "/dapr/subscribe": "GET endpoint for Dapr subscription declaration (Phase 5)"
        },
        "dapr_enabled": settings.DAPR_ENABLED
    }


@app.get("/health", summary="Health check", description="Simple health check endpoint for Kubernetes liveness/readiness probes")
async def health_check():
    """Health check endpoint for Kubernetes."""
    return {
        "status": "healthy",
        "message": "Taskify API is running",
        "timestamp": datetime.utcnow().isoformat(),
        "dapr_enabled": settings.DAPR_ENABLED,
        "version": "2.0.0-phase5"
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
