---
name: error-handling-logging
description: Implement structured logging, exception handlers, and error responses for FastAPI with monitoring integration. Use when (1) Setting up application-wide logging configuration with structlog or loguru, (2) Creating custom exception handlers for HTTP errors (401 Unauthorized, 404 Not Found, 422 Validation Error), (3) Implementing request/response logging middleware, (4) Adding error context for debugging (user_id, request_id, stack traces), (5) Integrating with monitoring tools (Sentry, DataDog, CloudWatch), (6) Ensuring consistent error response formats across all endpoints.
---

# Error Handling & Logging

Implement production-grade error handling and structured logging for FastAPI applications with monitoring integration and consistent error responses.

## Logging Setup

### 1. Configure Structured Logging

**Using Loguru (Recommended for FastAPI):**
```python
# app/config/logging.py
from loguru import logger
import sys
from pathlib import Path

# Remove default handler
logger.remove()

# Console handler with color
logger.add(
    sys.stderr,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level="INFO",
    colorize=True,
)

# File handler with rotation
logger.add(
    "logs/app_{time:YYYY-MM-DD}.log",
    rotation="00:00",  # Rotate at midnight
    retention="30 days",  # Keep logs for 30 days
    compression="zip",  # Compress old logs
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
    level="DEBUG",
)

# Error file handler
logger.add(
    "logs/errors_{time:YYYY-MM-DD}.log",
    rotation="00:00",
    retention="90 days",  # Keep error logs longer
    compression="zip",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
    level="ERROR",
)
```

**Usage in Application:**
```python
from loguru import logger

@router.post("/tasks")
async def create_task(task_data: TaskCreateRequest, current_user: User = Depends(get_current_user)):
    logger.info(f"Creating task for user {current_user.id}", extra={
        "user_id": current_user.id,
        "task_title": task_data.title
    })

    try:
        task = Task(**task_data.model_dump(), user_id=current_user.id)
        session.add(task)
        session.commit()

        logger.debug(f"Task {task.id} created successfully", extra={
            "task_id": task.id,
            "user_id": current_user.id
        })

        return TaskResponse.model_validate(task)

    except Exception as e:
        logger.error(f"Failed to create task: {str(e)}", extra={
            "user_id": current_user.id,
            "error": str(e),
            "error_type": type(e).__name__
        })
        raise
```

### 2. Request/Response Logging Middleware

```python
# app/middleware/logging.py
from fastapi import Request, Response
from loguru import logger
import time
import uuid

@app.middleware("http")
async def log_requests(request: Request, call_next):
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id

    # Log incoming request
    logger.info(
        f"Incoming request: {request.method} {request.url.path}",
        extra={
            "request_id": request_id,
            "method": request.method,
            "path": request.url.path,
            "query_params": dict(request.query_params),
            "client_ip": request.client.host,
            "user_agent": request.headers.get("user-agent"),
        }
    )

    start_time = time.time()

    try:
        response = await call_next(request)

        # Log response
        process_time = time.time() - start_time
        logger.info(
            f"Request completed: {request.method} {request.url.path}",
            extra={
                "request_id": request_id,
                "status_code": response.status_code,
                "process_time_ms": round(process_time * 1000, 2),
            }
        )

        response.headers["X-Request-ID"] = request_id
        response.headers["X-Process-Time"] = str(process_time)
        return response

    except Exception as e:
        process_time = time.time() - start_time
        logger.error(
            f"Request failed: {request.method} {request.url.path}",
            extra={
                "request_id": request_id,
                "error": str(e),
                "error_type": type(e).__name__,
                "process_time_ms": round(process_time * 1000, 2),
            }
        )
        raise
```

## Exception Handling

### 1. Custom Exception Classes

```python
# app/exceptions.py
from fastapi import HTTPException, status

class UnauthorizedError(HTTPException):
    def __init__(self, detail: str = "Unauthorized access"):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail)

class ForbiddenError(HTTPException):
    def __init__(self, detail: str = "Access forbidden"):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=detail)

class NotFoundError(HTTPException):
    def __init__(self, resource: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{resource} not found"
        )

class ValidationError(HTTPException):
    def __init__(self, detail: str):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail
        )

class DatabaseError(HTTPException):
    def __init__(self, detail: str = "Database operation failed"):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail
        )
```

### 2. Global Exception Handlers

```python
# app/main.py
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from loguru import logger
import traceback

app = FastAPI()

# Structured error response format
def create_error_response(
    request_id: str,
    status_code: int,
    error_type: str,
    message: str,
    details: dict = None
):
    return {
        "request_id": request_id,
        "error": {
            "type": error_type,
            "message": message,
            "details": details or {}
        }
    }

# Handle validation errors (422)
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    request_id = getattr(request.state, "request_id", "unknown")

    logger.warning(
        "Validation error",
        extra={
            "request_id": request_id,
            "errors": exc.errors(),
            "body": exc.body
        }
    )

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=create_error_response(
            request_id=request_id,
            status_code=422,
            error_type="ValidationError",
            message="Request validation failed",
            details={"validation_errors": exc.errors()}
        )
    )

# Handle HTTP exceptions (401, 403, 404, etc.)
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    request_id = getattr(request.state, "request_id", "unknown")

    logger.warning(
        f"HTTP {exc.status_code} error",
        extra={
            "request_id": request_id,
            "status_code": exc.status_code,
            "detail": exc.detail
        }
    )

    return JSONResponse(
        status_code=exc.status_code,
        content=create_error_response(
            request_id=request_id,
            status_code=exc.status_code,
            error_type=type(exc).__name__,
            message=exc.detail
        )
    )

# Handle uncaught exceptions (500)
@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    request_id = getattr(request.state, "request_id", "unknown")

    logger.error(
        f"Unhandled exception: {type(exc).__name__}",
        extra={
            "request_id": request_id,
            "error": str(exc),
            "error_type": type(exc).__name__,
            "traceback": traceback.format_exc()
        }
    )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=create_error_response(
            request_id=request_id,
            status_code=500,
            error_type="InternalServerError",
            message="An unexpected error occurred. Please try again later."
        )
    )
```

### 3. Error Response Format

**Consistent Structure:**
```json
{
  "request_id": "550e8400-e29b-41d4-a716-446655440000",
  "error": {
    "type": "ValidationError",
    "message": "Request validation failed",
    "details": {
      "validation_errors": [
        {
          "loc": ["body", "title"],
          "msg": "field required",
          "type": "value_error.missing"
        }
      ]
    }
  }
}
```

## Monitoring Integration

### 1. Sentry Integration

```python
# app/config/monitoring.py
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration

def init_sentry(dsn: str, environment: str):
    sentry_sdk.init(
        dsn=dsn,
        integrations=[
            FastApiIntegration(),
            SqlalchemyIntegration(),
        ],
        environment=environment,
        traces_sample_rate=0.1,  # 10% of transactions
        profiles_sample_rate=0.1,
        send_default_pii=False,  # Don't send personally identifiable info
    )

# app/main.py
from app.config.monitoring import init_sentry

if settings.SENTRY_DSN:
    init_sentry(settings.SENTRY_DSN, settings.ENVIRONMENT)
```

**Capture Custom Context:**
```python
from sentry_sdk import capture_exception, set_context, set_user

@router.post("/tasks")
async def create_task(current_user: User = Depends(get_current_user)):
    # Set user context for Sentry
    set_user({"id": current_user.id, "email": current_user.email})

    try:
        # Operation
        pass
    except Exception as e:
        set_context("task_creation", {
            "user_id": current_user.id,
            "task_data": task_data.model_dump()
        })
        capture_exception(e)
        raise
```

### 2. Health Check Endpoint

```python
# app/routes/health.py
from fastapi import APIRouter, Depends, status
from sqlmodel import Session, select
from app.database import get_session

router = APIRouter(tags=["health"])

@router.get("/health", status_code=status.HTTP_200_OK)
async def health_check(session: Session = Depends(get_session)):
    """Health check endpoint for monitoring."""
    try:
        # Check database connection
        session.exec(select(1)).one()

        return {
            "status": "healthy",
            "database": "connected",
            "version": "1.0.0"
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "unhealthy",
                "database": "disconnected",
                "error": str(e)
            }
        )
```

## Best Practices

### 1. Error Context Enrichment

Always include:
- `request_id`: Unique identifier for request tracing
- `user_id`: For user-specific debugging
- `resource_id`: ID of resource being accessed
- `operation`: What was being attempted
- `timestamp`: When error occurred

### 2. Security Considerations

- **Never log sensitive data**: Passwords, tokens, credit cards
- **Sanitize error messages**: Don't expose internal implementation details
- **Use appropriate log levels**:
  - `DEBUG`: Detailed diagnostic information
  - `INFO`: General informational messages
  - `WARNING`: Potentially harmful situations
  - `ERROR`: Error events that might still allow the app to continue
  - `CRITICAL`: Severe errors causing premature termination

### 3. Performance

- Use async logging to avoid blocking requests
- Rotate log files to prevent disk space issues
- Compress old logs
- Consider log aggregation services (ELK stack, CloudWatch)

## Quality Checklist

- [ ] Structured logging configured with contextual information
- [ ] Request/response logging middleware implemented
- [ ] Custom exception classes defined for common errors
- [ ] Global exception handlers for all HTTP status codes
- [ ] Consistent error response format across all endpoints
- [ ] Sensitive data excluded from logs
- [ ] Monitoring integration configured (Sentry/DataDog)
- [ ] Health check endpoint implemented
- [ ] Log rotation and retention policies set
- [ ] Request IDs generated and propagated

## References

- **Loguru Documentation**: https://loguru.readthedocs.io
- **FastAPI Error Handling**: https://fastapi.tiangolo.com/tutorial/handling-errors/
- **Sentry Integration**: https://docs.sentry.io/platforms/python/guides/fastapi/
