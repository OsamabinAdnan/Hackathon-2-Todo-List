# API Contracts: Multi-User Full-Stack Todo Web Application

## Authentication Endpoints

### POST /api/auth/signup
**Description**: Create a new user account
**Authentication**: None required

**Request**:
```
{
  "email": "string (valid email format)",
  "password": "string (min 8 chars, mixed case, number, special char)"
}
```

**Response**:
- 201 Created:
```
{
  "user": {
    "id": "UUID",
    "email": "string"
  },
  "token": "JWT string"
}
```
- 400 Bad Request: Validation errors
- 409 Conflict: Email already exists

### POST /api/auth/login
**Description**: Authenticate user and return JWT token
**Authentication**: None required

**Request**:
```
{
  "email": "string (valid email format)",
  "password": "string"
}
```

**Response**:
- 200 OK:
```
{
  "user": {
    "id": "UUID",
    "email": "string"
  },
  "token": "JWT string"
}
```
- 400 Bad Request: Validation errors
- 401 Unauthorized: Invalid credentials

### POST /api/auth/logout
**Description**: Logout user (invalidate session)
**Authentication**: Bearer JWT required

**Request**:
```
Authorization: Bearer <token>
```

**Response**:
- 200 OK: Success
- 401 Unauthorized: Invalid/expired token

## Task Management Endpoints

### GET /api/{user_id}/tasks
**Description**: List user's tasks with optional filters
**Authentication**: Bearer JWT required

**Request**:
```
Authorization: Bearer <token>
Query parameters (optional):
- status: "todo" | "completed"
- priority: "low" | "medium" | "high" | "none"
- due_date: ISO date string
- search: keyword string (searches title/description)
- sort: "due_date" | "priority" | "title" | "created_date" (default: created_date)
- order: "asc" | "desc" (default: asc)
- page: number (default: 1)
- limit: number (default: 50, max: 100)
```

**Response**:
- 200 OK:
```
{
  "tasks": [
    {
      "id": "UUID",
      "title": "string",
      "description": "string (optional)",
      "status": "todo" | "completed",
      "priority": "low" | "medium" | "high" | "none",
      "due_date": "ISO datetime string (optional)",
      "recurrence_pattern": "none" | "daily" | "weekly" | "monthly" | "yearly",
      "tags": ["string"],
      "created_at": "ISO datetime string",
      "updated_at": "ISO datetime string"
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 50,
    "total": 100,
    "total_pages": 2
  }
}
```
- 401/403 Unauthorized: Invalid token or user_id mismatch
- 404 Not Found: User not found

### POST /api/{user_id}/tasks
**Description**: Create a new task
**Authentication**: Bearer JWT required

**Request**:
```
Authorization: Bearer <token>
{
  "title": "string (1-255 chars)",
  "description": "string (optional, max 1000 chars)",
  "priority": "low" | "medium" | "high" | "none" (default: "none")",
  "due_date": "ISO datetime string (optional)",
  "recurrence_pattern": "none" | "daily" | "weekly" | "monthly" | "yearly" (default: "none")",
  "tags": ["string"] (optional, max 5 tags, 20 chars each)
}
```

**Response**:
- 201 Created:
```
{
  "id": "UUID",
  "title": "string",
  "description": "string (optional)",
  "status": "todo",
  "priority": "low" | "medium" | "high" | "none",
  "due_date": "ISO datetime string (optional)",
  "recurrence_pattern": "none" | "daily" | "weekly" | "monthly" | "yearly",
  "tags": ["string"],
  "created_at": "ISO datetime string",
  "updated_at": "ISO datetime string"
}
```
- 400 Bad Request: Validation errors
- 401/403 Unauthorized: Invalid token or user_id mismatch

### GET /api/{user_id}/tasks/{task_id}
**Description**: Get a specific task
**Authentication**: Bearer JWT required

**Request**:
```
Authorization: Bearer <token>
```

**Response**:
- 200 OK:
```
{
  "id": "UUID",
  "title": "string",
  "description": "string (optional)",
  "status": "todo" | "completed",
  "priority": "low" | "medium" | "high" | "none",
  "due_date": "ISO datetime string (optional)",
  "recurrence_pattern": "none" | "daily" | "weekly" | "monthly" | "yearly",
  "tags": ["string"],
  "created_at": "ISO datetime string",
  "updated_at": "ISO datetime string"
}
```
- 401/403 Unauthorized: Invalid token or user_id mismatch
- 404 Not Found: Task not found

### PUT /api/{user_id}/tasks/{task_id}
**Description**: Update a task completely
**Authentication**: Bearer JWT required

**Request**:
```
Authorization: Bearer <token>
{
  "title": "string (1-255 chars)",
  "description": "string (optional, max 1000 chars)",
  "priority": "low" | "medium" | "high" | "none",
  "status": "todo" | "completed",
  "due_date": "ISO datetime string (optional)",
  "recurrence_pattern": "none" | "daily" | "weekly" | "monthly" | "yearly",
  "tags": ["string"] (optional, max 5 tags, 20 chars each)
}
```

**Response**:
- 200 OK: Returns updated task object (same format as GET /tasks/{task_id})
- 400 Bad Request: Validation errors
- 401/403 Unauthorized: Invalid token or user_id mismatch
- 404 Not Found: Task not found

### DELETE /api/{user_id}/tasks/{task_id}
**Description**: Delete a task
**Authentication**: Bearer JWT required

**Request**:
```
Authorization: Bearer <token>
```

**Response**:
- 204 No Content: Successfully deleted
- 401/403 Unauthorized: Invalid token or user_id mismatch
- 404 Not Found: Task not found

### PATCH /api/{user_id}/tasks/{task_id}/complete
**Description**: Toggle task completion status
**Authentication**: Bearer JWT required

**Request**:
```
Authorization: Bearer <token>
{
  "completed": "boolean (true for completed, false for todo)"
}
```

**Response**:
- 200 OK: Returns updated task object (same format as GET /tasks/{task_id})
- 400 Bad Request: Validation errors
- 401/403 Unauthorized: Invalid token or user_id mismatch
- 404 Not Found: Task not found

## Error Response Format

All error responses follow the same structure:

```
{
  "error": {
    "code": "string (error code)",
    "message": "string (human-readable message)",
    "details": "object (optional, specific error details)"
  }
}
```

## Common Error Codes

### 400 Bad Request
- `VALIDATION_ERROR`: Request body doesn't match schema
- `INVALID_INPUT`: Specific field validation failed

### 401 Unauthorized
- `TOKEN_MISSING`: No authorization header provided
- `TOKEN_INVALID`: JWT token is malformed or invalid
- `TOKEN_EXPIRED`: JWT token has expired

### 403 Forbidden
- `USER_MISMATCH`: Requested user_id doesn't match token user_id
- `INSUFFICIENT_PERMISSIONS`: User doesn't have permission for this action

### 404 Not Found
- `USER_NOT_FOUND`: Specified user doesn't exist
- `TASK_NOT_FOUND`: Specified task doesn't exist

### 409 Conflict
- `EMAIL_EXISTS`: Attempt to create user with existing email

### 500 Internal Server Error
- `INTERNAL_ERROR`: Unexpected server error occurred

## Rate Limiting

All authenticated endpoints are subject to rate limiting:
- 100 requests per minute per user
- Exempt endpoints: POST /auth/login, POST /auth/signup
- Response header: `X-RateLimit-Remaining`, `X-RateLimit-Reset`

## Security Headers

All responses include security headers:
- `Content-Security-Policy`: Prevent XSS
- `X-Content-Type-Options`: nosniff
- `X-Frame-Options`: DENY
- `X-XSS-Protection`: 1; mode=block