---
name: chat-error-handling-recovery
description: "Implement graceful error handling and recovery strategies for chat endpoints with comprehensive error taxonomy, HTTP status code mapping, structured logging, and multilingual error messages. Use when: (1) designing error responses with proper HTTP status codes (400, 401, 403, 404, 409, 429, 500, 504), (2) handling authentication failures (missing/invalid/expired JWT), (3) handling authorization failures (cross-user access attempts), (4) handling agent execution errors (timeouts, tool failures, invalid responses), (5) handling database errors (constraint violations, connection failures), (6) handling rate limiting and backpressure scenarios, (7) implementing security audit logging for suspicious access, (8) providing multilingual error messages for Phase 3 bonus features."
---

# Chat Error Handling & Recovery

## Core Responsibility

Implement robust error handling for the chat endpoint with:
1. Comprehensive error taxonomy (auth, validation, database, agent, tool, rate limit, timeout)
2. HTTP status code mapping (400, 401, 403, 404, 409, 429, 500, 504)
3. Structured logging with trace ID and user context
4. User-friendly error messages (both dev and production)
5. Error recovery strategies for transient failures
6. Security audit logging for suspicious access
7. Multilingual error responses (English + Urdu)

## Quick Start: Error Taxonomy

| Category | HTTP | Examples | Recovery |
|----------|------|----------|----------|
| **Auth** | 401 | Missing token, expired, invalid signature | Redirect to login |
| **Authorization** | 403 | Access denied, wrong user | Block access, audit log |
| **Validation** | 400 | Invalid input, malformed JSON | Return validation errors |
| **Resource** | 404 | Not found, missing conversation | Return 404 (never expose) |
| **Conflict** | 409 | Duplicate resource, constraint violation | Retry or create new |
| **Rate Limit** | 429 | Per-user limit exceeded | Backoff and retry |
| **Server** | 500 | Database error, unhandled exception | Rollback, alert |
| **Timeout** | 504 | Agent >30s, tool >10s | Return timeout error |

## Section 1: Error Taxonomy & Classification

Comprehensive error classification for all failure scenarios. See `references/error-taxonomy.md`.

### Authentication Errors (401)
```python
class AuthenticationError(Exception):
    """Missing, invalid, or expired JWT"""
    codes = {
        "MISSING_TOKEN": "Authorization header required",
        "INVALID_TOKEN": "Invalid or malformed token",
        "EXPIRED_TOKEN": "Token expired",
        "INVALID_SIGNATURE": "Token signature verification failed",
        "MISSING_USER_ID": "Token missing required user_id claim"
    }
```

### Authorization Errors (403)
```python
class AuthorizationError(Exception):
    """User lacks permission to access resource"""
    codes = {
        "ACCESS_DENIED": "Access denied to resource",
        "WRONG_USER": "Resource belongs to different user",
        "INSUFFICIENT_PERMISSIONS": "User lacks required permissions",
        "CONVERSATION_NOT_OWNED": "Conversation owned by different user"
    }
```

### Validation Errors (400)
```python
class ValidationError(Exception):
    """Invalid input parameters"""
    codes = {
        "INVALID_MESSAGE": "Message invalid or empty",
        "MESSAGE_TOO_LONG": "Message exceeds 5000 chars",
        "INVALID_UUID": "Invalid conversation_id format",
        "MALFORMED_JSON": "Request body malformed JSON",
        "INVALID_PARAMETERS": "One or more parameters invalid"
    }
```

### Resource Errors (404)
```python
class ResourceNotFoundError(Exception):
    """Resource does not exist"""
    codes = {
        "CONVERSATION_NOT_FOUND": "Conversation not found",
        "MESSAGE_NOT_FOUND": "Message not found",
        "USER_NOT_FOUND": "User profile not found"
    }
```

### Conflict Errors (409)
```python
class ConflictError(Exception):
    """Resource state conflict or constraint violation"""
    codes = {
        "DUPLICATE_RESOURCE": "Resource already exists",
        "CONCURRENT_MODIFICATION": "Resource modified by another request",
        "CONSTRAINT_VIOLATION": "Database constraint violated",
        "VERSION_MISMATCH": "Optimistic locking version mismatch"
    }
```

### Rate Limit Errors (429)
```python
class RateLimitError(Exception):
    """Per-user rate limit exceeded"""
    codes = {
        "TOO_MANY_REQUESTS": "Rate limit exceeded, try again later",
        "QUOTA_EXCEEDED": "Daily quota exceeded",
        "BACKPRESSURE": "Server overloaded, try again later"
    }

    def __init__(self, code, retry_after_seconds=None):
        self.code = code
        self.retry_after = retry_after_seconds or 60
```

### Agent Errors
```python
class AgentExecutionError(Exception):
    """Agent execution failure"""
    codes = {
        "AGENT_TIMEOUT": "Agent execution timeout (>30s)",
        "AGENT_CRASHED": "Agent execution failed unexpectedly",
        "INVALID_RESPONSE": "Agent returned invalid response format",
        "TOOL_INVOCATION_FAILED": "One or more tools failed"
    }

class ToolExecutionError(Exception):
    """MCP tool execution failure"""
    codes = {
        "TOOL_TIMEOUT": "Tool execution timeout (>10s)",
        "TOOL_ERROR": "Tool invocation failed",
        "INVALID_PARAMETERS": "Tool parameters invalid",
        "PERMISSION_DENIED": "Tool access denied"
    }
```

### Database Errors (500)
```python
class DatabaseError(Exception):
    """Database operation failure"""
    codes = {
        "CONNECTION_FAILED": "Database connection failed",
        "QUERY_FAILED": "Query execution failed",
        "TRANSACTION_FAILED": "Transaction commit failed",
        "CONSTRAINT_VIOLATION": "Database constraint violated"
    }
```

### Timeout Errors (504)
```python
class TimeoutError(Exception):
    """Operation exceeded timeout"""
    codes = {
        "AGENT_TIMEOUT": "Agent execution timeout",
        "TOOL_TIMEOUT": "Tool execution timeout",
        "DATABASE_TIMEOUT": "Database query timeout",
        "EXTERNAL_SERVICE_TIMEOUT": "External service timeout"
    }
```

## Section 2: HTTP Status Code Mapping

Map error types to HTTP status codes with standard response format.

### Error Response Model
```python
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ErrorDetail(BaseModel):
    field: str  # Field name (if validation error)
    message: str  # Validation message
    expected: Optional[str]  # Expected format

class ErrorResponse(BaseModel):
    error: str  # Error code (e.g., "UNAUTHORIZED")
    message: str  # User-friendly message
    details: Optional[list[ErrorDetail] | dict] = None  # Additional context
    trace_id: str  # For debugging
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    retry_after: Optional[int] = None  # For 429 responses (seconds)
```

### Status Code Mapping
```python
ERROR_STATUS_CODES = {
    # 400 Bad Request
    "INVALID_MESSAGE": 400,
    "MESSAGE_TOO_LONG": 400,
    "MALFORMED_JSON": 400,
    "INVALID_PARAMETERS": 400,
    "INVALID_UUID": 400,

    # 401 Unauthorized
    "MISSING_TOKEN": 401,
    "INVALID_TOKEN": 401,
    "EXPIRED_TOKEN": 401,
    "INVALID_SIGNATURE": 401,

    # 403 Forbidden
    "ACCESS_DENIED": 403,
    "WRONG_USER": 403,
    "INSUFFICIENT_PERMISSIONS": 403,
    "CONVERSATION_NOT_OWNED": 403,

    # 404 Not Found (return 403 instead to prevent enumeration)
    "CONVERSATION_NOT_FOUND": 403,

    # 409 Conflict
    "DUPLICATE_RESOURCE": 409,
    "CONCURRENT_MODIFICATION": 409,
    "VERSION_MISMATCH": 409,

    # 429 Too Many Requests
    "TOO_MANY_REQUESTS": 429,
    "QUOTA_EXCEEDED": 429,

    # 500 Internal Server Error
    "DATABASE_ERROR": 500,
    "TRANSACTION_FAILED": 500,
    "UNHANDLED_ERROR": 500,

    # 504 Gateway Timeout
    "AGENT_TIMEOUT": 504,
    "TOOL_TIMEOUT": 504,
    "DATABASE_TIMEOUT": 504,
}
```

## Section 3: Structured Logging

Log all errors with trace ID and user context for debugging.

### Logging Configuration
```python
import structlog
import logging

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()
```

### Error Logging Patterns
```python
# Authentication failure
logger.warning(
    "authentication_failed",
    error_code="EXPIRED_TOKEN",
    user_id="unknown",
    trace_id=trace_id,
    ip_address=request.client.host
)

# Authorization failure (SECURITY AUDIT)
logger.warning(
    "authorization_failed",
    error_code="WRONG_USER",
    attempted_user_id=attacker_user_id,
    target_resource=conversation_id,
    actual_owner_id=actual_owner_id,
    trace_id=trace_id,
    ip_address=request.client.host
)

# Tool execution failure
logger.error(
    "tool_execution_failed",
    tool_name="add_task",
    error_code="TOOL_TIMEOUT",
    user_id=user_id,
    conversation_id=conversation_id,
    trace_id=trace_id,
    execution_time_ms=10500
)

# Database error (with stack trace)
logger.error(
    "database_error",
    error_code="QUERY_FAILED",
    query="SELECT * FROM conversations...",
    user_id=user_id,
    trace_id=trace_id,
    exc_info=True  # Include full stack trace
)
```

## Section 4: User-Friendly Error Messages

Generate appropriate error messages for different audiences.

### Message Templates
```python
ERROR_MESSAGES = {
    # Production messages (shown to users)
    "production": {
        "MISSING_TOKEN": "Please log in again",
        "INVALID_TOKEN": "Your session has expired. Please log in.",
        "EXPIRED_TOKEN": "Your session has expired. Please log in.",
        "ACCESS_DENIED": "You don't have permission to access this resource",
        "CONVERSATION_NOT_FOUND": "Conversation not found",
        "AGENT_TIMEOUT": "Request took too long. Please try again.",
        "DATABASE_ERROR": "We're experiencing technical difficulties. Please try again later.",
        "TOO_MANY_REQUESTS": "Too many requests. Please wait a moment and try again.",
    },

    # Development messages (detailed, never shown in production)
    "development": {
        "MISSING_TOKEN": "Authorization header missing",
        "INVALID_TOKEN": "Failed to decode JWT token: {error}",
        "EXPIRED_TOKEN": "JWT token expired at {exp_time}",
        "AGENT_TIMEOUT": "Agent execution timeout (>30s) after calling {tool_count} tools",
        "DATABASE_ERROR": "Database error: {error}",
        "TOOL_ERROR": "Tool '{tool}' failed: {error}",
    }
}

def get_error_message(error_code: str, environment: str = "production", **kwargs) -> str:
    """Get appropriate message for environment"""
    template = ERROR_MESSAGES.get(environment, {}).get(
        error_code,
        "An error occurred"
    )

    # Format template with kwargs
    try:
        return template.format(**kwargs)
    except KeyError:
        return template
```

## Section 5: Multilingual Error Responses

Support English and Urdu error messages for Phase 3.

### Language Detection
```python
def detect_user_language(user_id: str, session: AsyncSession) → str:
    """
    Get user's preferred language from profile.

    Returns: "en" (default) or "ur"
    """
    user_pref = await get_user_preferences(session, user_id)
    return user_pref.get("language", "en")

async def get_error_message_localized(
    error_code: str,
    user_id: str,
    session: AsyncSession,
    **kwargs
) → str:
    """Get error message in user's preferred language"""
    language = await detect_user_language(user_id, session)

    translations = {
        "ur": {  # Urdu
            "MISSING_TOKEN": "براہ کرم دوبارہ لاگ ان کریں",
            "EXPIRED_TOKEN": "آپ کا سیشن ختم ہو گیا۔ براہ کرم دوبارہ لاگ ان کریں۔",
            "ACCESS_DENIED": "آپ کو اس وسیلے تک رسائی کی اجازت نہیں ہے",
            "AGENT_TIMEOUT": "درخواست میں بہت وقت لگا۔ براہ کرم دوبارہ کوشش کریں۔",
            "DATABASE_ERROR": "ہم تکنیکی مسائل کا سامنا کر رہے ہیں۔ براہ کرم بعد میں دوبارہ کوشش کریں۔",
        },
        "en": {  # English
            "MISSING_TOKEN": "Please log in again",
            "EXPIRED_TOKEN": "Your session has expired. Please log in.",
            "ACCESS_DENIED": "You don't have permission to access this resource",
            "AGENT_TIMEOUT": "Request took too long. Please try again.",
            "DATABASE_ERROR": "We're experiencing technical difficulties. Please try again later.",
        }
    }

    message = translations.get(language, {}).get(error_code, "An error occurred")
    return message.format(**kwargs) if kwargs else message
```

## Section 6: Error Recovery Strategies

Implement retry logic and fallback strategies for transient errors.

### Exponential Backoff Retry
```python
import asyncio

async def retry_with_backoff(
    operation,
    max_retries: int = 3,
    initial_delay_ms: int = 100,
    backoff_multiplier: float = 2.0,
    max_delay_ms: int = 1000,
    trace_id: str = None
):
    """
    Retry operation with exponential backoff.

    Retries on: DatabaseError, TimeoutError, AgentExecutionError
    Does NOT retry on: ValidationError, AuthorizationError
    """
    retry_count = 0

    while retry_count < max_retries:
        try:
            return await operation()

        except (DatabaseError, TimeoutError, AgentExecutionError) as e:
            retry_count += 1

            if retry_count >= max_retries:
                logger.error(f"Operation failed after {max_retries} retries", extra={
                    "error": str(e),
                    "trace_id": trace_id
                })
                raise

            # Calculate delay: 100ms → 200ms → 400ms
            delay_ms = min(
                initial_delay_ms * (backoff_multiplier ** (retry_count - 1)),
                max_delay_ms
            )

            logger.warning(f"Retrying operation", extra={
                "retry_count": retry_count,
                "delay_ms": delay_ms,
                "error": str(e),
                "trace_id": trace_id
            })

            await asyncio.sleep(delay_ms / 1000)

        except (ValidationError, AuthorizationError):
            # Non-retryable errors
            raise
```

### Tool Failure Handling (Partial Success)
```python
async def execute_tools_with_recovery(tools: list[str], trace_id: str) → dict:
    """
    Execute tools, capture failures, allow partial success.

    Returns: {
        "results": [success/error results],
        "status": "success" | "partial" | "error",
        "failed_tools": ["tool1", "tool2"]
    }
    """
    results = []
    failed_tools = []

    for tool in tools:
        try:
            result = await invoke_mcp_tool(tool, trace_id)
            results.append({
                "tool": tool,
                "status": "success",
                "result": result
            })

        except ToolExecutionError as e:
            failed_tools.append(tool)
            results.append({
                "tool": tool,
                "status": "error",
                "error": str(e)
            })

            logger.warning(f"Tool execution failed", extra={
                "tool": tool,
                "error": str(e),
                "trace_id": trace_id
            })

    status = "success" if not failed_tools else ("partial" if len(failed_tools) < len(tools) else "error")

    return {
        "results": results,
        "status": status,
        "failed_tools": failed_tools
    }
```

## Section 7: Security Audit Logging

Log suspicious access attempts and security events.

### Audit Log Events
```python
async def log_security_event(
    event_type: str,  # "failed_auth", "unauthorized_access", "rate_limit_exceeded"
    user_id: Optional[str],
    attempted_action: str,
    target_resource: Optional[str],
    reason: str,
    trace_id: str,
    request: Request
):
    """
    Log security-relevant event for audit trail.

    Never log: passwords, tokens, sensitive user data
    Always log: who, what, when, where (IP), why
    """
    logger.warning(
        f"security_event",
        event_type=event_type,
        user_id=user_id,
        attempted_action=attempted_action,
        target_resource=target_resource,
        reason=reason,
        ip_address=request.client.host,
        user_agent=request.headers.get("User-Agent"),
        timestamp=datetime.utcnow().isoformat(),
        trace_id=trace_id
    )

    # Example: Attempted cross-user access
    if event_type == "unauthorized_access":
        logger.critical(
            "potential_security_breach",
            attacker_user_id=user_id,
            target_conversation=target_resource,
            attempted_action=attempted_action,
            ip_address=request.client.host,
            trace_id=trace_id,
            action="block_user"  # Could trigger account suspension
        )
```

## Section 8: Complete Error Handling Pipeline

Wire all error handling together in middleware.

```python
from fastapi import Request, Response
from fastapi.responses import JSONResponse

@app.middleware("http")
async def error_handling_middleware(request: Request, call_next):
    """
    Global error handling middleware.

    Catches all errors, logs, and returns appropriate HTTP responses.
    """
    trace_id = get_trace_id()
    start_time = time.time()

    try:
        response = await call_next(request)
        return response

    except AuthenticationError as e:
        await log_security_event(
            "failed_auth",
            user_id="unknown",
            attempted_action="access_endpoint",
            target_resource=request.url.path,
            reason=str(e),
            trace_id=trace_id,
            request=request
        )

        return JSONResponse(
            status_code=401,
            content={
                "error": "UNAUTHORIZED",
                "message": "Authentication required",
                "trace_id": trace_id
            }
        )

    except AuthorizationError as e:
        await log_security_event(
            "unauthorized_access",
            user_id=get_user_id_from_token(request),
            attempted_action="access_resource",
            target_resource=request.url.path,
            reason=str(e),
            trace_id=trace_id,
            request=request
        )

        return JSONResponse(
            status_code=403,
            content={
                "error": "ACCESS_DENIED",
                "message": "You don't have permission to access this resource",
                "trace_id": trace_id
            }
        )

    except ValidationError as e:
        return JSONResponse(
            status_code=400,
            content={
                "error": "INVALID_INPUT",
                "message": str(e),
                "trace_id": trace_id
            }
        )

    except RateLimitError as e:
        return JSONResponse(
            status_code=429,
            headers={"Retry-After": str(e.retry_after)},
            content={
                "error": "TOO_MANY_REQUESTS",
                "message": "Rate limit exceeded",
                "retry_after": e.retry_after,
                "trace_id": trace_id
            }
        )

    except TimeoutError as e:
        return JSONResponse(
            status_code=504,
            content={
                "error": "TIMEOUT",
                "message": "Request timeout",
                "trace_id": trace_id
            }
        )

    except Exception as e:
        logger.error(
            "unhandled_error",
            error=str(e),
            trace_id=trace_id,
            exc_info=True
        )

        return JSONResponse(
            status_code=500,
            content={
                "error": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected error occurred",
                "trace_id": trace_id
            }
        )
```

---

## References

See bundled reference files for implementation details:
- **error-taxonomy.md** - Comprehensive error classification and codes
- **status-code-mapping.md** - HTTP status code mapping with examples
- **multilingual-messages.md** - Error messages in English and Urdu
