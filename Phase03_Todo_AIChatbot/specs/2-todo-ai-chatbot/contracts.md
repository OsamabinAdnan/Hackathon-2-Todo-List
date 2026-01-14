# API Contracts: AI-Powered Todo Chatbot Integration

## Chat Endpoint

### POST /api/{user_id}/chat
**Description**: Process user message and return AI response with MCP tool execution
**Authentication**: Bearer JWT required

**Request**:
```
Authorization: Bearer <token>
{
  "conversation_id": "optional UUID (null for new conversation)",
  "message": "string (user's natural language input, max 5000 chars)",
  "timestamp": "ISO datetime string (optional, defaults to now)"
}
```

**Response**:
- 200 OK:
```
{
  "conversation_id": "UUID of conversation (new or existing)",
  "response": "string (AI's natural language response)",
  "tool_calls": [
    {
      "tool": "string (tool name executed)",
      "parameters": "object (parameters passed to tool)",
      "result": "object (tool execution result or error)",
      "execution_time_ms": "number (how long tool took to execute)"
    }
  ],
  "trace_id": "UUID for debugging correlation",
  "timestamp": "ISO datetime string"
}
```

- 201 Created: New conversation created (when conversation_id was null in request)
- 400 Bad Request: Validation errors
- 401 Unauthorized: Invalid/expired token
- 403 Forbidden: User_id mismatch or insufficient permissions
- 404 Not Found: Conversation not found for user
- 409 Conflict: Rate limit exceeded
- 429 Too Many Requests: Rate limit exceeded with retry-after header
- 500 Internal Server Error: Unexpected server error
- 504 Gateway Timeout: Agent execution timeout

## MCP Tools API (Internal - Used by OpenAI Agent)

These endpoints are not directly accessible but represent the MCP tools that the OpenAI Agent will use internally:

### add_task (MCP Tool)
**Description**: Create a new task for authenticated user
**Called by**: OpenAI Agent internally

**Parameters**:
```
{
  "user_id": "UUID (from authentication context)",
  "title": "string (1-200 chars)",
  "description": "string (optional, max 1000 chars)",
  "priority": "string (optional: 'HIGH'|'MEDIUM'|'LOW'|'NONE', default: 'NONE')",
  "due_date": "ISO datetime string (optional)",
  "tags": "array of strings (optional, max 5 tags, 20 chars each)"
}
```

**Returns**:
```
{
  "task_id": "UUID of created task",
  "status": "string ('created' or 'error')",
  "title": "string (task title)",
  "created_at": "ISO datetime string"
}
```

### list_tasks (MCP Tool)
**Description**: List user's tasks with optional filters
**Called by**: OpenAI Agent internally

**Parameters**:
```
{
  "user_id": "UUID (from authentication context)",
  "status": "string (optional: 'all'|'pending'|'completed', default: 'all')",
  "priority": "string (optional: 'HIGH'|'MEDIUM'|'LOW'|'NONE')",
  "tags": "array of strings (optional)",
  "page": "integer (optional, default: 1)",
  "limit": "integer (optional, 1-100, default: 20)"
}
```

**Returns**:
```
{
  "tasks": [
    {
      "task_id": "UUID",
      "title": "string",
      "description": "string (or null)",
      "completed": "boolean",
      "priority": "string",
      "due_date": "ISO datetime string (or null)",
      "created_at": "ISO datetime string",
      "completed_at": "ISO datetime string (or null)"
    }
  ],
  "pagination": {
    "page": "integer",
    "limit": "integer",
    "total": "integer",
    "pages": "integer"
  }
}
```

### complete_task (MCP Tool)
**Description**: Mark a task as complete
**Called by**: OpenAI Agent internally

**Parameters**:
```
{
  "user_id": "UUID (from authentication context)",
  "task_id": "UUID of task to complete"
}
```

**Returns**:
```
{
  "task_id": "UUID",
  "status": "string ('completed' or 'error')",
  "title": "string (task title)",
  "completed_at": "ISO datetime string"
}
```

### delete_task (MCP Tool)
**Description**: Delete a task
**Called by**: OpenAI Agent internally

**Parameters**:
```
{
  "user_id": "UUID (from authentication context)",
  "task_id": "UUID of task to delete"
}
```

**Returns**:
```
{
  "task_id": "UUID of deleted task",
  "status": "string ('deleted' or 'error')",
  "message": "string (confirmation message)"
}
```

### update_task (MCP Tool)
**Description**: Update task properties
**Called by**: OpenAI Agent internally

**Parameters**:
```
{
  "user_id": "UUID (from authentication context)",
  "task_id": "UUID of task to update",
  "title": "string (optional, 1-200 chars)",
  "description": "string (optional, max 1000 chars)",
  "priority": "string (optional: 'HIGH'|'MEDIUM'|'LOW'|'NONE')",
  "status": "string (optional: 'todo'|'completed')",
  "due_date": "ISO datetime string (optional)",
  "tags": "array of strings (optional)"
}
```

**Returns**:
```
{
  "task_id": "UUID",
  "status": "string ('updated' or 'error')",
  "title": "string (updated title)",
  "updated_at": "ISO datetime string"
}
```

### get_task_summary (MCP Tool)
**Description**: Get user's task summary statistics
**Called by**: OpenAI Agent internally

**Parameters**:
```
{
  "user_id": "UUID (from authentication context)"
}
```

**Returns**:
```
{
  "total_tasks": "integer",
  "completed_tasks": "integer",
  "pending_tasks": "integer",
  "by_priority": {
    "HIGH": "integer",
    "MEDIUM": "integer",
    "LOW": "integer",
    "NONE": "integer"
  },
  "by_status": {
    "todo": "integer",
    "completed": "integer"
  },
  "last_updated": "ISO datetime string"
}
```

## Error Response Format

All error responses follow the same structure:

```
{
  "error": {
    "code": "string (error code)",
    "message": "string (human-readable message)",
    "details": "object (optional, specific error details)",
    "trace_id": "UUID for debugging correlation"
  }
}
```

## Common Error Codes

### 400 Bad Request
- `VALIDATION_ERROR`: Request body doesn't match schema
- `INVALID_INPUT`: Specific field validation failed
- `MESSAGE_TOO_LONG`: Message exceeds 5000 characters

### 401 Unauthorized
- `TOKEN_MISSING`: No authorization header provided
- `TOKEN_INVALID`: JWT token is malformed or invalid
- `TOKEN_EXPIRED`: JWT token has expired

### 403 Forbidden
- `USER_MISMATCH`: Requested user_id doesn't match token user_id
- `INSUFFICIENT_PERMISSIONS`: User doesn't have permission for this action
- `CROSS_USER_ACCESS_DENIED`: User attempted to access another user's resources

### 404 Not Found
- `USER_NOT_FOUND`: Specified user doesn't exist
- `CONVERSATION_NOT_FOUND`: Specified conversation doesn't exist for user
- `TASK_NOT_FOUND`: Specified task doesn't exist for user

### 409 Conflict
- `RATE_LIMIT_EXCEEDED`: User exceeded rate limits

### 429 Too Many Requests
- `TOO_MANY_REQUESTS`: Rate limit exceeded, includes Retry-After header

### 500 Internal Server Error
- `INTERNAL_ERROR`: Unexpected server error occurred
- `DATABASE_ERROR`: Database operation failed
- `AGENT_EXECUTION_ERROR`: AI agent execution failed

### 504 Gateway Timeout
- `AGENT_TIMEOUT`: AI agent execution exceeded timeout (30 seconds)

## Rate Limiting

All authenticated endpoints are subject to rate limiting:
- Chat endpoint: 100 requests per minute per user
- MCP tools (internal): Individual tool limits (add_task: 100/min, list_tasks: 500/min, complete_task: 100/min, delete_task: 50/min, update_task: 100/min)
- Response headers: `X-RateLimit-Remaining`, `X-RateLimit-Reset`, `Retry-After`

## Security Headers

All responses include security headers:
- `Content-Security-Policy`: Prevent XSS
- `X-Content-Type-Options`: nosniff
- `X-Frame-Options`: DENY
- `X-XSS-Protection`: 1; mode=block
- `Trace-ID`: For request correlation and debugging

## Request/Response Examples

### Successful Chat Request
**Request**:
```
POST /api/550e8400-e29b-41d4-a716-446655440000/chat
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
{
  "message": "Add a task to buy groceries"
}
```

**Response**:
```
200 OK
{
  "conversation_id": "6ba7b810-9dad-11d1-80b4-00c04fd430c8",
  "response": "I've added 'Buy groceries' to your tasks.",
  "tool_calls": [
    {
      "tool": "add_task",
      "parameters": {
        "user_id": "550e8400-e29b-41d4-a716-446655440000",
        "title": "Buy groceries"
      },
      "result": {
        "task_id": "7a8b9c0d-1e2f-3g4h-5i6j-7k8l9m0n1o2p",
        "status": "created",
        "title": "Buy groceries",
        "created_at": "2026-01-13T10:30:00Z"
      },
      "execution_time_ms": 45
    }
  ],
  "trace_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "timestamp": "2026-01-13T10:30:00Z"
}
```

### Error Response Example
**Response**:
```
403 Forbidden
{
  "error": {
    "code": "CROSS_USER_ACCESS_DENIED",
    "message": "Access denied: Cannot access resources for different user",
    "details": {
      "requested_user_id": "different-user-id",
      "authenticated_user_id": "actual-user-id"
    },
    "trace_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
  }
}
```