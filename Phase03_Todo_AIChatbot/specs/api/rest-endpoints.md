# REST API Endpoints Specification

**API Version**: v1
**Base URL**:
- Development: `http://localhost:8000`
- Production: `https://api.yourdomain.com` (Hugging Face Spaces)

**Protocol**: HTTPS (production), HTTP (development)
**Content-Type**: `application/json`
**Character Encoding**: UTF-8

---

## Authentication

All endpoints except `/api/auth/signup` and `/api/auth/login` require authentication.

### Authorization Header
```http
Authorization: Bearer <jwt_token>
```

### Unauthorized Response (401)
```json
{
  "error": "Unauthorized",
  "message": "Invalid or expired token"
}
```

---

## Common Response Codes

| Code | Meaning | Description |
|------|---------|-------------|
| 200 | OK | Request succeeded |
| 201 | Created | Resource created successfully |
| 400 | Bad Request | Invalid input or validation error |
| 401 | Unauthorized | Missing, invalid, or expired token |
| 403 | Forbidden | User doesn't have permission (e.g., accessing another user's task) |
| 404 | Not Found | Resource doesn't exist |
| 409 | Conflict | Resource already exists (e.g., duplicate email) |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Server-side error |

---

## Authentication Endpoints

### POST /api/auth/signup

Create a new user account.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "SecurePass123!",
  "name": "John Doe"
}
```

**Validation:**
- `email`: Valid email format, unique
- `password`: Min 8 chars, must contain uppercase, lowercase, number, special char
- `name`: 2-50 characters

**Success Response (201):**
```json
{
  "user": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "user@example.com",
    "name": "John Doe",
    "created_at": "2026-01-02T10:30:00Z"
  },
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "expires_at": "2026-01-09T10:30:00Z"
}
```

**Error Response (400):**
```json
{
  "error": "Validation Error",
  "details": {
    "email": "Email already exists",
    "password": "Password must contain at least one uppercase letter"
  }
}
```

---

### POST /api/auth/login

Authenticate user and issue JWT token.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "SecurePass123!"
}
```

**Success Response (200):**
```json
{
  "user": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "user@example.com",
    "name": "John Doe"
  },
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "expires_at": "2026-01-09T10:30:00Z"
}
```

**Error Response (401):**
```json
{
  "error": "Invalid email or password"
}
```

**Rate Limiting:**
- Max 5 attempts per 15 minutes per IP address
- Returns 429 when limit exceeded

---

### POST /api/auth/logout

Revoke JWT token (add to blocklist).

**Headers:**
```http
Authorization: Bearer <jwt_token>
```

**Success Response (200):**
```json
{
  "message": "Successfully logged out"
}
```

---

### GET /api/auth/me

Get current authenticated user information.

**Headers:**
```http
Authorization: Bearer <jwt_token>
```

**Success Response (200):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  "name": "John Doe",
  "created_at": "2026-01-02T10:30:00Z"
}
```

---

## Task Endpoints

All task endpoints follow the pattern `/api/{user_id}/tasks` where `{user_id}` must match the authenticated user's ID from the JWT token.

### GET /api/{user_id}/tasks

List all tasks for the authenticated user with optional filtering, sorting, and search.

**Headers:**
```http
Authorization: Bearer <jwt_token>
```

**Query Parameters:**

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `status` | string | Filter by completion status | `all`, `todo`, `completed` |
| `priority` | string | Filter by priority level | `all`, `HIGH`, `MEDIUM`, `LOW`, `NONE` |
| `tags` | string | Comma-separated tags (ANY match) | `work,urgent` |
| `search` | string | Keyword search (title, description, tags) | `meeting` |
| `sort` | string | Sort field | `created`, `title`, `due_date`, `priority` |
| `order` | string | Sort order | `asc`, `desc` |
| `page` | integer | Page number (pagination) | `1` |
| `limit` | integer | Results per page | `20` (default) |

**Example Request:**
```http
GET /api/550e8400-e29b-41d4-a716-446655440000/tasks?status=todo&priority=HIGH&sort=due_date&order=asc
Authorization: Bearer <jwt_token>
```

**Success Response (200):**
```json
{
  "tasks": [
    {
      "id": "task-uuid-1",
      "user_id": "550e8400-e29b-41d4-a716-446655440000",
      "title": "Deploy to production",
      "description": "Deploy v2.0 release to production servers",
      "completed": false,
      "priority": "HIGH",
      "tags": ["work", "devops"],
      "due_date": "2026-01-15T14:30:00Z",
      "is_recurring": false,
      "recurrence_pattern": null,
      "created_at": "2026-01-02T10:00:00Z",
      "updated_at": "2026-01-02T10:00:00Z",
      "completed_at": null
    },
    {
      "id": "task-uuid-2",
      "user_id": "550e8400-e29b-41d4-a716-446655440000",
      "title": "Team meeting",
      "description": "Weekly standup with development team",
      "completed": false,
      "priority": "MEDIUM",
      "tags": ["work", "meeting"],
      "due_date": "2026-01-03T09:00:00Z",
      "is_recurring": true,
      "recurrence_pattern": "WEEKLY",
      "created_at": "2026-01-01T10:00:00Z",
      "updated_at": "2026-01-01T10:00:00Z",
      "completed_at": null
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 2,
    "total_pages": 1
  }
}
```

**Error Response (403):**
```json
{
  "error": "Forbidden",
  "message": "Cannot access tasks for another user"
}
```

---

### POST /api/{user_id}/tasks

Create a new task.

**Headers:**
```http
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

**Request Body:**
```json
{
  "title": "Complete project documentation",
  "description": "Write comprehensive documentation for Phase 2",
  "priority": "HIGH",
  "tags": ["work", "documentation"],
  "due_date": "2026-01-10T17:00:00Z",
  "is_recurring": false,
  "recurrence_pattern": null
}
```

**Required Fields:**
- `title`: string (1-200 characters)

**Optional Fields:**
- `description`: string (max 1000 characters)
- `priority`: enum (`HIGH`, `MEDIUM`, `LOW`, `NONE`) - default: `NONE`
- `tags`: array of strings (max 10 tags, each max 20 chars)
- `due_date`: ISO 8601 datetime (must be future date)
- `is_recurring`: boolean - default: `false`
- `recurrence_pattern`: enum (`DAILY`, `WEEKLY`, `MONTHLY`) - required if `is_recurring: true`

**Validation Rules:**
- If `is_recurring: true`, `due_date` is required
- `due_date` must be in the future
- `tags` are stored lowercase

**Success Response (201):**
```json
{
  "id": "task-uuid-3",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "title": "Complete project documentation",
  "description": "Write comprehensive documentation for Phase 2",
  "completed": false,
  "priority": "HIGH",
  "tags": ["work", "documentation"],
  "due_date": "2026-01-10T17:00:00Z",
  "is_recurring": false,
  "recurrence_pattern": null,
  "created_at": "2026-01-02T11:00:00Z",
  "updated_at": "2026-01-02T11:00:00Z",
  "completed_at": null
}
```

**Error Response (400):**
```json
{
  "error": "Validation Error",
  "details": {
    "title": "Title is required",
    "due_date": "Due date cannot be in the past"
  }
}
```

---

### GET /api/{user_id}/tasks/{id}

Get a specific task by ID.

**Headers:**
```http
Authorization: Bearer <jwt_token>
```

**Success Response (200):**
```json
{
  "id": "task-uuid-1",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "title": "Deploy to production",
  "description": "Deploy v2.0 release to production servers",
  "completed": false,
  "priority": "HIGH",
  "tags": ["work", "devops"],
  "due_date": "2026-01-15T14:30:00Z",
  "is_recurring": false,
  "recurrence_pattern": null,
  "created_at": "2026-01-02T10:00:00Z",
  "updated_at": "2026-01-02T10:00:00Z",
  "completed_at": null
}
```

**Error Response (404):**
```json
{
  "error": "Not Found",
  "message": "Task not found"
}
```

**Error Response (403):**
```json
{
  "error": "Forbidden",
  "message": "You don't have permission to access this task"
}
```

---

### PUT /api/{user_id}/tasks/{id}

Update an existing task.

**Headers:**
```http
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

**Request Body (Partial Update Allowed):**
```json
{
  "title": "Updated task title",
  "priority": "MEDIUM",
  "tags": ["updated", "work"]
}
```

**Updatable Fields:**
- `title`: string (1-200 characters)
- `description`: string (max 1000 characters)
- `priority`: enum (`HIGH`, `MEDIUM`, `LOW`, `NONE`)
- `tags`: array of strings
- `due_date`: ISO 8601 datetime
- `is_recurring`: boolean
- `recurrence_pattern`: enum (`DAILY`, `WEEKLY`, `MONTHLY`)

**Non-Updatable Fields:**
- `id`, `user_id`, `created_at`, `completed`, `completed_at`

**Success Response (200):**
```json
{
  "id": "task-uuid-1",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "title": "Updated task title",
  "description": "Deploy v2.0 release to production servers",
  "completed": false,
  "priority": "MEDIUM",
  "tags": ["updated", "work"],
  "due_date": "2026-01-15T14:30:00Z",
  "is_recurring": false,
  "recurrence_pattern": null,
  "created_at": "2026-01-02T10:00:00Z",
  "updated_at": "2026-01-02T12:30:00Z",
  "completed_at": null
}
```

**Error Response (400):**
```json
{
  "error": "Validation Error",
  "details": {
    "title": "Title cannot be empty"
  }
}
```

---

### DELETE /api/{user_id}/tasks/{id}

Delete a task permanently.

**Headers:**
```http
Authorization: Bearer <jwt_token>
```

**Success Response (200):**
```json
{
  "message": "Task deleted successfully",
  "deleted_id": "task-uuid-1"
}
```

**Error Response (404):**
```json
{
  "error": "Not Found",
  "message": "Task not found"
}
```

**Error Response (403):**
```json
{
  "error": "Forbidden",
  "message": "You don't have permission to delete this task"
}
```

---

### PATCH /api/{user_id}/tasks/{id}/complete

Toggle task completion status.

**Headers:**
```http
Authorization: Bearer <jwt_token>
```

**Behavior:**
- If task is incomplete → Mark as complete, set `completed_at` timestamp
- If task is complete → Mark as incomplete, clear `completed_at`
- If task is recurring and being marked complete → Create new task instance with next due date

**Success Response (200):**
```json
{
  "task": {
    "id": "task-uuid-1",
    "completed": true,
    "completed_at": "2026-01-02T13:00:00Z"
  },
  "new_recurring_task": null
}
```

**Success Response (200) - Recurring Task:**
```json
{
  "task": {
    "id": "task-uuid-2",
    "completed": true,
    "completed_at": "2026-01-02T13:00:00Z"
  },
  "new_recurring_task": {
    "id": "task-uuid-5",
    "title": "Team meeting",
    "due_date": "2026-01-09T09:00:00Z",
    "is_recurring": true,
    "recurrence_pattern": "WEEKLY"
  }
}
```

**Error Response (404):**
```json
{
  "error": "Not Found",
  "message": "Task not found"
}
```

---

## User Profile Endpoints

### PUT /api/users/profile

Update user profile information.

**Headers:**
```http
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

**Request Body:**
```json
{
  "name": "John Smith"
}
```

**Success Response (200):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  "name": "John Smith",
  "updated_at": "2026-01-02T14:00:00Z"
}
```

---

### POST /api/users/change-password

Change user password.

**Headers:**
```http
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

**Request Body:**
```json
{
  "current_password": "OldPass123!",
  "new_password": "NewSecurePass456!"
}
```

**Success Response (200):**
```json
{
  "message": "Password changed successfully"
}
```

**Error Response (400):**
```json
{
  "error": "Invalid current password"
}
```

---

## Error Response Format

All error responses follow this structure:

```json
{
  "error": "Error Type",
  "message": "Human-readable error message",
  "details": {
    "field_name": "Field-specific error message"
  }
}
```

**Example Multi-Field Validation Error (400):**
```json
{
  "error": "Validation Error",
  "message": "Request validation failed",
  "details": {
    "title": "Title is required",
    "due_date": "Due date cannot be in the past",
    "tags": "Maximum 10 tags allowed"
  }
}
```

---

## Rate Limiting

Rate limits are enforced per IP address (development) or per user (production).

| Endpoint Pattern | Limit | Window |
|------------------|-------|--------|
| `/api/auth/login` | 5 requests | 15 minutes |
| `/api/auth/signup` | 3 requests | 1 hour |
| `/api/{user_id}/tasks` (GET) | 100 requests | 1 minute |
| `/api/{user_id}/tasks` (POST) | 20 requests | 1 minute |
| `/api/{user_id}/tasks/*` (PUT/DELETE) | 50 requests | 1 minute |

**Rate Limit Exceeded Response (429):**
```json
{
  "error": "Too Many Requests",
  "message": "Rate limit exceeded. Try again in 5 minutes.",
  "retry_after": 300
}
```

**Response Headers:**
```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 0
X-RateLimit-Reset: 1704192900
```

---

## CORS Configuration

### Allowed Origins
- Development: `http://localhost:3000`
- Production: `https://yourdomain.com`, `https://www.yourdomain.com`

### Allowed Methods
```
GET, POST, PUT, PATCH, DELETE, OPTIONS
```

### Allowed Headers
```
Authorization, Content-Type
```

### Exposed Headers
```
X-RateLimit-Limit, X-RateLimit-Remaining, X-RateLimit-Reset
```

---

## OpenAPI/Swagger Documentation

Interactive API documentation will be available at:
- Development: `http://localhost:8000/docs`
- Production: `https://api.yourdomain.com/docs`

---

## Versioning Strategy

Current version: `v1`

Future versions will use URL path versioning:
- `https://api.yourdomain.com/v1/...` (current)
- `https://api.yourdomain.com/v2/...` (future)

Breaking changes require a new version. Non-breaking changes (e.g., adding optional fields) can be added to existing version.

---

**Version**: 1.0.0
**Last Updated**: 2026-01-02
**Owner**: Phase 2 Development Team
