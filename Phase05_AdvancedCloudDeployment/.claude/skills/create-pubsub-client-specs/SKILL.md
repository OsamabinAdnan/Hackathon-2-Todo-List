---
name: create-pubsub-client-specs
description: Generates code specifications for FastAPI/Chatbot to publish events (POST to /v1.0/publish) and subscribe (Dapr endpoint handlers) using Dapr client libraries. Use when creating Dapr pub/sub integration code for FastAPI and Chatbot services with proper event handling and subscription patterns.
---

# Create Pub/Sub Client Specs

This skill helps generate code specifications for FastAPI and Chatbot services to integrate with Dapr pub/sub, including publishing events to Dapr endpoints and subscribing to events with proper Dapr endpoint handlers.

## When to Use This Skill

Use this skill when:
- Implementing Dapr pub/sub integration in FastAPI services
- Creating event publishing functionality for Todo application
- Setting up event subscription handlers in Chatbot services
- Defining proper Dapr client library usage patterns
- Implementing reliable event-driven communication between services

## FastAPI Dapr Integration

### Basic Dapr Pub/Sub Setup
```python
from fastapi import FastAPI, BackgroundTasks, HTTPException
import httpx
import asyncio
from typing import Dict, Any
import json
from pydantic import BaseModel

app = FastAPI()

# Dapr configuration
DAPR_HTTP_ENDPOINT = "http://localhost:3500"
DAPR_STATE_STORE = "statestore"

class EventPayload(BaseModel):
    eventType: str
    data: Dict[str, Any]
    userId: str
    timestamp: str

@app.post("/publish-event")
async def publish_event(payload: EventPayload):
    """
    Publish an event to Dapr pub/sub
    """
    try:
        # Construct the Dapr pub/sub endpoint
        dapr_url = f"{DAPR_HTTP_ENDPOINT}/v1.0/publish/pubsub/{payload.eventType}"

        # Prepare the event data
        event_data = {
            "eventType": payload.eventType,
            "data": payload.data,
            "userId": payload.userId,
            "timestamp": payload.timestamp
        }

        # Publish to Dapr
        async with httpx.AsyncClient() as client:
            response = await client.post(
                dapr_url,
                json=event_data,
                headers={"Content-Type": "application/json"}
            )

        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail="Failed to publish event")

        return {"success": True, "message": f"Event {payload.eventType} published successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error publishing event: {str(e)}")
```

### Advanced Publishing with Error Handling
```python
import logging
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)

class EventType(str, Enum):
    TASK_CREATED = "task.created"
    TASK_UPDATED = "task.updated"
    TASK_COMPLETED = "task.completed"
    TASK_DELETED = "task.deleted"
    USER_LOGIN = "user.login"
    USER_LOGOUT = "user.logout"

class DaprPublisher:
    def __init__(self, dapr_endpoint: str = "http://localhost:3500"):
        self.dapr_endpoint = dapr_endpoint
        self.client = httpx.AsyncClient(timeout=httpx.Timeout(30.0))

    async def publish_event(self, topic: str, data: Dict[str, Any], metadata: Dict[str, str] = None) -> bool:
        """
        Publish an event to Dapr pub/sub with retry logic
        """
        url = f"{self.dapr_endpoint}/v1.0/publish/pubsub/{topic}"

        payload = {
            "data": data,
            "datacontenttype": "application/json",
            "metadata": metadata or {}
        }

        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = await self.client.post(url, json=payload)

                if response.status_code == 200:
                    logger.info(f"Event published successfully to topic: {topic}")
                    return True
                elif response.status_code == 400:
                    logger.error(f"Bad request when publishing to {topic}: {response.text}")
                    return False
                else:
                    logger.warning(f"Attempt {attempt + 1} failed to publish to {topic}: {response.status_code}")

            except httpx.RequestError as e:
                logger.warning(f"Attempt {attempt + 1} request error when publishing to {topic}: {str(e)}")

            if attempt < max_retries - 1:
                await asyncio.sleep(2 ** attempt)  # Exponential backoff

        logger.error(f"Failed to publish event to {topic} after {max_retries} attempts")
        return False

    async def close(self):
        await self.client.aclose()

# Initialize publisher
publisher = DaprPublisher()

@app.post("/api/{user_id}/tasks")
async def create_task(user_id: str, task_data: Dict[str, Any]):
    """
    Create a task and publish a task.created event
    """
    # Create the task (your business logic here)
    task_id = "generated_task_id"  # Replace with actual creation logic

    # Prepare event data
    event_data = {
        "taskId": task_id,
        "userId": user_id,
        "title": task_data.get("title"),
        "description": task_data.get("description"),
        "priority": task_data.get("priority", "medium"),
        "dueDate": task_data.get("dueDate"),
        "createdAt": datetime.utcnow().isoformat()
    }

    # Publish the event
    success = await publisher.publish_event(EventType.TASK_CREATED, event_data)

    if success:
        return {"taskId": task_id, "message": "Task created and event published"}
    else:
        # Log the failure but still return success for the task creation
        logger.error(f"Failed to publish task.created event for task {task_id}")
        return {"taskId": task_id, "message": "Task created but event publication failed"}

@app.on_event("shutdown")
async def shutdown_event():
    await publisher.close()
```

## Chatbot Dapr Subscription

### Dapr Subscription Handler
```python
from fastapi import Request
import json

@app.post("/dapr/subscribe")
async def dapr_subscribe():
    """
    Dapr subscription endpoint to define which topics this service subscribes to
    """
    subscriptions = [
        {
            "pubsubname": "pubsub",
            "topic": "task.created",
            "route": "/events/task-created"
        },
        {
            "pubsubname": "pubsub",
            "topic": "task.completed",
            "route": "/events/task-completed"
        },
        {
            "pubsubname": "pubsub",
            "topic": "user.login",
            "route": "/events/user-login"
        }
    ]
    return subscriptions

@app.post("/events/task-created")
async def handle_task_created(request: Request):
    """
    Handle task.created events
    """
    try:
        # Parse the incoming request
        body = await request.json()

        # Extract the actual event data
        event_data = body.get("data", {})
        event_type = body.get("eventType", "")
        user_id = event_data.get("userId", "")

        logger.info(f"Received task.created event for user {user_id}")

        # Process the event (e.g., update chatbot context, send notification)
        # Your business logic here

        # Example: Update user's task count in state
        state_url = f"{DAPR_HTTP_ENDPOINT}/v1.0/state/{DAPR_STATE_STORE}"
        state_key = f"user:{user_id}:task_count"

        async with httpx.AsyncClient() as client:
            # Get current count
            response = await client.get(f"{state_url}/{state_key}")
            current_count = int(response.text) if response.status_code == 200 else 0

            # Increment and save
            new_count = current_count + 1
            state_data = [{"key": state_key, "value": new_count}]
            await client.post(state_url, json=state_data)

        return {"status": "success", "processed": "task.created"}

    except Exception as e:
        logger.error(f"Error handling task.created event: {str(e)}")
        return {"status": "error", "message": str(e)}

@app.post("/events/task-completed")
async def handle_task_completed(request: Request):
    """
    Handle task.completed events
    """
    try:
        body = await request.json()
        event_data = body.get("data", {})
        user_id = event_data.get("userId", "")
        task_id = event_data.get("taskId", "")

        logger.info(f"Received task.completed event for task {task_id}")

        # Your business logic here
        # Example: Update completion statistics

        return {"status": "success", "processed": "task.completed"}

    except Exception as e:
        logger.error(f"Error handling task.completed event: {str(e)}")
        return {"status": "error", "message": str(e)}
```

## Dapr Client Library Usage

### Using Dapr Python SDK
```python
# Install: pip install dapr-ext-fastapi dapr

from dapr.ext.fastapi import DaprApp
from dapr.clients import DaprClient
from fastapi import FastAPI
import asyncio

app = FastAPI()
dapr_app = DaprApp(app)

@dapr_app.subscribe(pubsub='pubsub', topic='task.created')
async def handle_task_created(event_data: dict):
    """
    Handle task.created events using Dapr extension
    """
    print(f"Received task.created event: {event_data}")

    # Process the event
    user_id = event_data.get('userId')
    task_id = event_data.get('taskId')

    # Your business logic here
    print(f"Processing task {task_id} for user {user_id}")

# Publishing using DaprClient
@app.post("/publish-task-event")
async def publish_task_event(task_data: dict):
    with DaprClient() as client:
        # Publish to Dapr pub/sub
        result = client.publish_event(
            pubsub_name='pubsub',
            topic_name='task.created',
            data=json.dumps(task_data),
            data_content_type='application/json',
        )

        print(f"Published event with trace ID: {result.headers['dapr-trace-id']}")
        return {"published": True}
```

## Advanced Subscription Patterns

### Pattern Matching Subscription
```python
@app.post("/events/user-activity")
async def handle_user_activity(request: Request):
    """
    Generic handler for user-related events
    """
    try:
        body = await request.json()
        event_data = body.get("data", {})
        event_type = body.get("eventType", "")
        user_id = event_data.get("userId", "")

        logger.info(f"Processing {event_type} for user {user_id}")

        # Route to specific handler based on event type
        if event_type == "user.login":
            await handle_user_login_specific(event_data)
        elif event_type == "user.logout":
            await handle_user_logout_specific(event_data)
        elif event_type.startswith("task."):
            await handle_task_event_specific(event_type, event_data)

        return {"status": "success", "event_type": event_type}

    except Exception as e:
        logger.error(f"Error in generic event handler: {str(e)}")
        return {"status": "error", "message": str(e)}

async def handle_user_login_specific(event_data: dict):
    """Handle specific user login logic"""
    user_id = event_data.get("userId")
    login_time = event_data.get("timestamp")

    # Update user session state
    # Send welcome message to chatbot
    logger.info(f"User {user_id} logged in at {login_time}")

async def handle_user_logout_specific(event_data: dict):
    """Handle specific user logout logic"""
    user_id = event_data.get("userId")
    logout_time = event_data.get("timestamp")

    # Clean up user session
    logger.info(f"User {user_id} logged out at {logout_time}")

async def handle_task_event_specific(event_type: str, event_data: dict):
    """Handle specific task event logic"""
    user_id = event_data.get("userId")
    task_id = event_data.get("taskId")

    logger.info(f"Task event {event_type} for task {task_id}, user {user_id}")
```

## Error Handling and Retry Patterns

### Robust Error Handling
```python
import time
from functools import wraps

def retry_on_failure(max_retries=3, delay=1):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            last_exception = None

            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        await asyncio.sleep(delay * (2 ** attempt))  # Exponential backoff
                    else:
                        logger.error(f"All {max_retries} attempts failed: {str(e)}")

            raise last_exception
        return wrapper
    return decorator

@retry_on_failure(max_retries=3, delay=1)
@app.post("/events/reliable-handler")
async def reliable_event_handler(request: Request):
    """
    Event handler with built-in retry mechanism
    """
    body = await request.json()
    event_data = body.get("data", {})

    # Process the event
    # This will retry up to 3 times if it fails
    result = await process_event_with_business_logic(event_data)

    return {"status": "success", "result": result}

async def process_event_with_business_logic(event_data: dict):
    """Your actual business logic here"""
    # Simulate some processing
    await asyncio.sleep(0.1)

    # Example business logic
    if not event_data.get("userId"):
        raise ValueError("Missing userId in event data")

    return {"processed": True, "data": event_data}
```

## Dapr State Integration

### Combining Pub/Sub with State Management
```python
@app.post("/events/task-aggregate")
async def handle_task_aggregate(request: Request):
    """
    Aggregate task events and maintain state
    """
    body = await request.json()
    event_data = body.get("data", {})
    event_type = body.get("eventType", "")
    user_id = event_data.get("userId", "")

    # Get current user state
    state_key = f"aggregate:{user_id}"
    state_url = f"{DAPR_HTTP_ENDPOINT}/v1.0/state/{DAPR_STATE_STORE}"

    async with httpx.AsyncClient() as client:
        try:
            # Get current aggregate
            response = await client.get(f"{state_url}/{state_key}")
            if response.status_code == 200:
                current_state = response.json()
            else:
                current_state = {"total_tasks": 0, "completed_tasks": 0, "pending_tasks": 0}
        except:
            current_state = {"total_tasks": 0, "completed_tasks": 0, "pending_tasks": 0}

        # Update based on event type
        if event_type == "task.created":
            current_state["total_tasks"] += 1
            current_state["pending_tasks"] += 1
        elif event_type == "task.completed":
            current_state["completed_tasks"] += 1
            current_state["pending_tasks"] -= 1

        # Save updated state
        state_data = [{"key": state_key, "value": current_state}]
        await client.post(state_url, json=state_data)

    return {"status": "success", "aggregate": current_state}
```

## Output Format

Generate code specifications that include:
- Proper Dapr client library usage patterns
- Event publishing functions with error handling
- Subscription handlers with routing logic
- State management integration
- Retry mechanisms and error recovery
- Proper typing and documentation
- Security considerations for event data
- Performance optimization patterns