# API Contracts: MCP Tools for AI-Powered Todo Chatbot

## Overview

This document defines the Model Context Protocol (MCP) tools that will be available to the OpenAI Agent for managing todo tasks. These tools follow the Official MCP SDK specification and integrate with the existing Phase 2 database schema.

Read `Official MCP SDK` for more details via context7 MCP server before proceeding.

## MCP Tool Specifications

### Tool 1: add_task

**Description**: Create a new task for the authenticated user

**Input Schema**:
```json
{
  "type": "object",
  "properties": {
    "user_id": {
      "type": "string",
      "format": "uuid",
      "description": "UUID of authenticated user (extracted from JWT)"
    },
    "title": {
      "type": "string",
      "minLength": 1,
      "maxLength": 200,
      "description": "Task title (required, non-empty)"
    },
    "description": {
      "type": "string",
      "maxLength": 1000,
      "description": "Task description (optional)"
    },
    "priority": {
      "type": "string",
      "enum": ["HIGH", "MEDIUM", "LOW", "NONE"],
      "default": "NONE",
      "description": "Task priority level (optional)"
    },
    "due_date": {
      "type": "string",
      "format": "date-time",
      "description": "Task due date/time in ISO 8601 format (optional)"
    },
    "tags": {
      "type": "array",
      "items": {
        "type": "string",
        "maxLength": 20
      },
      "maxItems": 5,
      "description": "Array of tags for the task (optional, max 5 tags)"
    }
  },
  "required": ["user_id", "title"]
}
```

**Output Schema**:
```json
{
  "type": "object",
  "properties": {
    "task_id": {
      "type": "string",
      "format": "uuid",
      "description": "UUID of created task"
    },
    "status": {
      "type": "string",
      "enum": ["created", "error"],
      "description": "Operation status"
    },
    "title": {
      "type": "string",
      "description": "Task title"
    },
    "created_at": {
      "type": "string",
      "format": "date-time",
      "description": "Task creation timestamp (UTC)"
    }
  }
}
```

**Example Request**:
```json
{
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "title": "Buy groceries",
  "description": "Milk, eggs, bread",
  "priority": "MEDIUM"
}
```

**Example Response**:
```json
{
  "task_id": "6ba7b810-9dad-11d1-80b4-00c04fd430c8",
  "status": "created",
  "title": "Buy groceries",
  "created_at": "2026-01-13T10:30:00Z"
}
```

**Security Requirements**:
- Validates user_id matches authenticated user
- Creates task associated with user_id only
- Returns 403 if user_id doesn't match authenticated context

---

### Tool 2: list_tasks

**Description**: Retrieve tasks for authenticated user with optional filtering

**Input Schema**:
```json
{
  "type": "object",
  "properties": {
    "user_id": {
      "type": "string",
      "format": "uuid",
      "description": "UUID of authenticated user (extracted from JWT)"
    },
    "status": {
      "type": "string",
      "enum": ["all", "pending", "completed"],
      "default": "all",
      "description": "Filter by task completion status (optional)"
    },
    "priority": {
      "type": "string",
      "enum": ["HIGH", "MEDIUM", "LOW", "NONE"],
      "description": "Filter by priority level (optional)"
    },
    "tags": {
      "type": "array",
      "items": {
        "type": "string"
      },
      "description": "Filter by tags (optional, any match)"
    },
    "page": {
      "type": "integer",
      "minimum": 1,
      "default": 1,
      "description": "Page number for pagination (optional)"
    },
    "limit": {
      "type": "integer",
      "minimum": 1,
      "maximum": 100,
      "default": 20,
      "description": "Number of items per page (optional)"
    }
  },
  "required": ["user_id"]
}
```

**Output Schema**:
```json
{
  "type": "object",
  "properties": {
    "tasks": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "task_id": {
            "type": "string",
            "format": "uuid"
          },
          "title": {
            "type": "string"
          },
          "description": {
            "type": "string"
          },
          "completed": {
            "type": "boolean"
          },
          "priority": {
            "type": "string",
            "enum": ["HIGH", "MEDIUM", "LOW", "NONE"]
          },
          "due_date": {
            "type": "string",
            "format": "date-time"
          },
          "tags": {
            "type": "array",
            "items": {
              "type": "string"
            }
          },
          "created_at": {
            "type": "string",
            "format": "date-time"
          },
          "completed_at": {
            "type": "string",
            "format": "date-time"
          }
        }
      }
    },
    "pagination": {
      "type": "object",
      "properties": {
        "page": {
          "type": "integer"
        },
        "limit": {
          "type": "integer"
        },
        "total": {
          "type": "integer"
        },
        "pages": {
          "type": "integer"
        }
      }
    }
  }
}
```

**Example Request**:
```json
{
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "pending",
  "limit": 10
}
```

**Example Response**:
```json
{
  "tasks": [
    {
      "task_id": "6ba7b810-9dad-11d1-80b4-00c04fd430c8",
      "title": "Buy groceries",
      "completed": false,
      "priority": "MEDIUM",
      "created_at": "2026-01-13T10:30:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 10,
    "total": 1,
    "pages": 1
  }
}
```

**Security Requirements**:
- Only returns tasks belonging to specified user_id
- Validates user_id matches authenticated context
- Returns 403 if user_id doesn't match authenticated context

---

### Tool 3: complete_task

**Description**: Mark a task as complete with timestamp

**Input Schema**:
```json
{
  "type": "object",
  "properties": {
    "user_id": {
      "type": "string",
      "format": "uuid",
      "description": "UUID of authenticated user (extracted from JWT)"
    },
    "task_id": {
      "type": "string",
      "format": "uuid",
      "description": "UUID of task to complete"
    }
  },
  "required": ["user_id", "task_id"]
}
```

**Output Schema**:
```json
{
  "type": "object",
  "properties": {
    "task_id": {
      "type": "string",
      "format": "uuid",
      "description": "UUID of completed task"
    },
    "status": {
      "type": "string",
      "enum": ["completed", "error"],
      "description": "Operation status"
    },
    "title": {
      "type": "string",
      "description": "Task title"
    },
    "completed_at": {
      "type": "string",
      "format": "date-time",
      "description": "Task completion timestamp (UTC)"
    }
  }
}
```

**Example Request**:
```json
{
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "task_id": "6ba7b810-9dad-11d1-80b4-00c04fd430c8"
}
```

**Example Response**:
```json
{
  "task_id": "6ba7b810-9dad-11d1-80b4-00c04fd430c8",
  "status": "completed",
  "title": "Buy groceries",
  "completed_at": "2026-01-13T11:00:00Z"
}
```

**Security Requirements**:
- Validates task belongs to user_id
- Validates user_id matches authenticated context
- Returns 403 if user_id doesn't match authenticated context
- Returns 404 if task doesn't exist for user

---

### Tool 4: delete_task

**Description**: Remove a task permanently (hard delete)

**Input Schema**:
```json
{
  "type": "object",
  "properties": {
    "user_id": {
      "type": "string",
      "format": "uuid",
      "description": "UUID of authenticated user (extracted from JWT)"
    },
    "task_id": {
      "type": "string",
      "format": "uuid",
      "description": "UUID of task to delete"
    }
  },
  "required": ["user_id", "task_id"]
}
```

**Output Schema**:
```json
{
  "type": "object",
  "properties": {
    "task_id": {
      "type": "string",
      "format": "uuid",
      "description": "UUID of deleted task"
    },
    "status": {
      "type": "string",
      "enum": ["deleted", "error"],
      "description": "Operation status"
    },
    "message": {
      "type": "string",
      "description": "Confirmation message"
    }
  }
}
```

**Example Request**:
```json
{
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "task_id": "6ba7b810-9dad-11d1-80b4-00c04fd430c8"
}
```

**Example Response**:
```json
{
  "task_id": "6ba7b810-9dad-11d1-80b4-00c04fd430c8",
  "status": "deleted",
  "message": "Task successfully deleted"
}
```

**Security Requirements**:
- Validates task belongs to user_id
- Validates user_id matches authenticated context
- Returns 403 if user_id doesn't match authenticated context
- Returns 404 if task doesn't exist for user

---

### Tool 5: update_task

**Description**: Modify task title, description, or other fields

**Input Schema**:
```json
{
  "type": "object",
  "properties": {
    "user_id": {
      "type": "string",
      "format": "uuid",
      "description": "UUID of authenticated user (extracted from JWT)"
    },
    "task_id": {
      "type": "string",
      "format": "uuid",
      "description": "UUID of task to update"
    },
    "title": {
      "type": "string",
      "minLength": 1,
      "maxLength": 200,
      "description": "New task title (optional)"
    },
    "description": {
      "type": "string",
      "maxLength": 1000,
      "description": "New task description (optional)"
    },
    "priority": {
      "type": "string",
      "enum": ["HIGH", "MEDIUM", "LOW", "NONE"],
      "description": "New priority level (optional)"
    },
    "status": {
      "type": "string",
      "enum": ["todo", "completed"],
      "description": "New completion status (optional)"
    },
    "due_date": {
      "type": "string",
      "format": "date-time",
      "description": "New due date/time (optional)"
    },
    "tags": {
      "type": "array",
      "items": {
        "type": "string",
        "maxLength": 20
      },
      "maxItems": 5,
      "description": "New tags array (optional)"
    }
  },
  "required": ["user_id", "task_id"]
}
```

**Output Schema**:
```json
{
  "type": "object",
  "properties": {
    "task_id": {
      "type": "string",
      "format": "uuid",
      "description": "UUID of updated task"
    },
    "status": {
      "type": "string",
      "enum": ["updated", "error"],
      "description": "Operation status"
    },
    "title": {
      "type": "string",
      "description": "Updated task title"
    },
    "updated_at": {
      "type": "string",
      "format": "date-time",
      "description": "Task update timestamp (UTC)"
    }
  }
}
```

**Example Request**:
```json
{
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "task_id": "6ba7b810-9dad-11d1-80b4-00c04fd430c8",
  "title": "Buy weekly groceries",
  "priority": "HIGH"
}
```

**Example Response**:
```json
{
  "task_id": "6ba7b810-9dad-11d1-80b4-00c04fd430c8",
  "status": "updated",
  "title": "Buy weekly groceries",
  "updated_at": "2026-01-13T11:30:00Z"
}
```

**Security Requirements**:
- Validates task belongs to user_id
- Validates user_id matches authenticated context
- Returns 403 if user_id doesn't match authenticated context
- Returns 404 if task doesn't exist for user

---

### Tool 6: get_task_summary

**Description**: Get user's task summary statistics

**Input Schema**:
```json
{
  "type": "object",
  "properties": {
    "user_id": {
      "type": "string",
      "format": "uuid",
      "description": "UUID of authenticated user (extracted from JWT)"
    }
  },
  "required": ["user_id"]
}
```

**Output Schema**:
```json
{
  "type": "object",
  "properties": {
    "total_tasks": {
      "type": "integer",
      "description": "Total number of tasks"
    },
    "completed_tasks": {
      "type": "integer",
      "description": "Number of completed tasks"
    },
    "pending_tasks": {
      "type": "integer",
      "description": "Number of pending tasks"
    },
    "by_priority": {
      "type": "object",
      "properties": {
        "HIGH": {
          "type": "integer"
        },
        "MEDIUM": {
          "type": "integer"
        },
        "LOW": {
          "type": "integer"
        },
        "NONE": {
          "type": "integer"
        }
      }
    },
    "by_status": {
      "type": "object",
      "properties": {
        "todo": {
          "type": "integer"
        },
        "completed": {
          "type": "integer"
        }
      }
    },
    "last_updated": {
      "type": "string",
      "format": "date-time",
      "description": "Last task update timestamp"
    }
  }
}
```

**Example Request**:
```json
{
  "user_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

**Example Response**:
```json
{
  "total_tasks": 5,
  "completed_tasks": 2,
  "pending_tasks": 3,
  "by_priority": {
    "HIGH": 1,
    "MEDIUM": 2,
    "LOW": 1,
    "NONE": 1
  },
  "by_status": {
    "todo": 3,
    "completed": 2
  },
  "last_updated": "2026-01-13T11:30:00Z"
}
```

**Security Requirements**:
- Only returns statistics for specified user_id
- Validates user_id matches authenticated context
- Returns 403 if user_id doesn't match authenticated context

---

## Error Response Format

All MCP tools return consistent error structure:

```json
{
  "error": {
    "code": "string (error code)",
    "message": "Human-readable message",
    "details": {
      "field": "context about error location"
    },
    "status": "error"
  }
}
```

### Standard Error Codes

| Error Code | HTTP Equivalent | Meaning | Example |
|-----------|-----------------|---------|---------|
| `invalid_parameter` | 400 | Parameter validation failed | title is empty |
| `task_not_found` | 404 | Task doesn't exist | task_id "xyz" not found for user |
| `unauthorized_access` | 403 | User doesn't own resource | User cannot access other user's task |
| `authentication_required` | 401 | Missing/invalid JWT token | user_id not provided or invalid |
| `database_error` | 500 | Database operation failed | Connection timeout |
| `rate_limit_exceeded` | 429 | Too many requests | Max operations per minute exceeded |
| `invalid_state` | 422 | Operation not allowed in current state | Cannot complete already-completed task |

---

## Rate Limiting

Each tool has per-user rate limits:

| Tool | Limit | Window | Rationale |
|------|-------|--------|-----------|
| add_task | 100 calls | Per minute | Prevent spam creation |
| list_tasks | 500 calls | Per minute | Frequent queries allowed |
| complete_task | 100 calls | Per minute | Prevent rapid completions |
| delete_task | 50 calls | Per minute | Destructive operation |
| update_task | 100 calls | Per minute | Modify operations |
| get_task_summary | 200 calls | Per minute | Read operation |

---

## Security Validation Points

### Before Tool Invocation
- ✅ JWT token is valid and not expired
- ✅ user_id extracted from token claims
- ✅ user_id matches parameter validation
- ✅ User has permission to perform operation

### During Tool Execution
- ✅ All queries filtered by user_id
- ✅ Parameters type-checked and validated
- ✅ Database operations parameterized
- ✅ Transaction committed or rolled back atomically

### In Error Responses
- ✅ No database structure leaked
- ✅ No other users' data exposed
- ✅ No stack traces in errors
- ✅ Actionable messages for agents

---

## Integration Notes

- All tools integrate with existing Phase 2 database schema
- User isolation is enforced at database query level
- Tools follow stateless architecture principles
- Authentication context is passed via user_id parameter
- All timestamps use UTC timezone consistently