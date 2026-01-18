# MCP Tool Definition & Schema Validation Skill

## Overview

This skill generates MCP tool specifications using the Official MCP SDK patterns, ensuring tools are stateless, composable, secure, and aligned with Phase 3 Constitution requirements. Tools are generated from specs with proper parameter validation, error standardization, and agent-consumable documentation.

**Skill Type:** Specification-Driven Code Generation
**Phase:** Phase 3 (AI Chatbot Integration)
**Agent:** mcp-server-builder
**Dependencies:** Official MCP SDK, SQLModel, @specs/api/mcp-tools.md

---

## When to Use This Skill

Use this skill when you need to:

1. **Generate MCP tool schemas** from @specs/api/mcp-tools.md
2. **Define tool parameters** with JSON Schema validation constraints
3. **Standardize error responses** across all MCP tools
4. **Document tool preconditions** and composition patterns
5. **Validate security isolation** (user_id enforcement, authorization)
6. **Create tool implementation stubs** with parameter validators
7. **Document rate limiting** requirements per tool
8. **Ensure composability** (tools can call other tools or feed results)

---

## Core Capabilities

### 1. Official MCP SDK Schema Generation

Generate tool schemas compliant with Official MCP SDK specification:

```json
{
  "name": "add_task",
  "description": "Create a new task for the authenticated user",
  "inputSchema": {
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
      }
    },
    "required": ["user_id", "title"]
  },
  "outputSchema": {
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
}
```

### 2. Standardized Error Response Format

All MCP tools return consistent error structure:

```python
# Error Response Schema (all tools)
{
  "error": "error_code",  # See table below
  "message": "Human-readable message",
  "details": {
    "field": "context about error location"
  },
  "status": "error"
}
```

**Standard Error Codes:**

| Error Code | HTTP Equivalent | Meaning | Example |
|-----------|-----------------|---------|---------|
| `invalid_parameter` | 400 | Parameter validation failed | title is empty |
| `task_not_found` | 404 | Task doesn't exist | task_id "xyz" not found |
| `unauthorized_access` | 403 | User doesn't own resource | User cannot access other user's task |
| `authentication_required` | 401 | Missing/invalid JWT token | user_id not provided |
| `database_error` | 500 | Database operation failed | Connection timeout (with retry hint) |
| `rate_limit_exceeded` | 429 | Too many requests | Max 100 add_task calls/minute per user |
| `invalid_state` | 422 | Operation not allowed in current state | Cannot complete already-completed task |

### 3. Tool-Specific Parameter Validation

Define validators for each parameter type:

**user_id Validation:**
- Must be valid UUID format
- Extracted from JWT claim (sub or user_id field)
- Must match authenticated user context
- Cannot accept null or empty

**title Validation:**
- Non-empty string (minLength: 1)
- Max 200 characters
- Trim whitespace
- Reject special characters (optional: sanitize HTML)

**task_id Validation:**
- Valid UUID format
- Must exist in database for user
- Verified ownership before operation

**status Parameter Validation:**
- Enum: "all", "pending", "completed"
- Case-insensitive
- Default: "all" if omitted

### 4. The Five Core MCP Tools

#### **Tool 1: add_task**

```python
{
  "name": "add_task",
  "description": "Create a new task for the authenticated user",
  "preconditions": [
    "User must be authenticated (JWT token valid)",
    "user_id must be extracted from JWT token"
  ],
  "side_effects": [
    "Creates new row in tasks table",
    "Sets created_at to current UTC timestamp",
    "No state retained on server"
  ],
  "parameters": {
    "user_id": "UUID (required, from JWT)",
    "title": "string, 1-200 chars (required)",
    "description": "string, max 1000 chars (optional)"
  },
  "returns": {
    "task_id": "UUID of created task",
    "status": "'created' or 'error'",
    "title": "Task title as stored",
    "created_at": "ISO 8601 UTC timestamp"
  },
  "example": {
    "input": {
      "user_id": "550e8400-e29b-41d4-a716-446655440000",
      "title": "Buy groceries",
      "description": "Milk, eggs, bread"
    },
    "output": {
      "task_id": "6ba7b810-9dad-11d1-80b4-00c04fd430c8",
      "status": "created",
      "title": "Buy groceries",
      "created_at": "2026-01-12T10:30:00Z"
    }
  }
}
```

#### **Tool 2: list_tasks**

```python
{
  "name": "list_tasks",
  "description": "Retrieve tasks for authenticated user with optional filtering",
  "preconditions": [
    "User must be authenticated",
    "Only tasks owned by user are returned"
  ],
  "parameters": {
    "user_id": "UUID (required, from JWT)",
    "status": "string: 'all'|'pending'|'completed' (optional, default: 'all')",
    "page": "integer >= 1 (optional, default: 1)",
    "limit": "integer 1-100 (optional, default: 20)"
  },
  "returns": {
    "tasks": [
      {
        "task_id": "UUID",
        "title": "string",
        "description": "string or null",
        "completed": "boolean",
        "created_at": "ISO 8601 UTC"
      }
    ],
    "pagination": {
      "page": "current page",
      "limit": "items per page",
      "total": "total matching tasks",
      "pages": "total pages"
    }
  },
  "example": {
    "input": {
      "user_id": "550e8400-e29b-41d4-a716-446655440000",
      "status": "pending",
      "limit": 10
    },
    "output": {
      "tasks": [
        {
          "task_id": "6ba7b810-9dad-11d1-80b4-00c04fd430c8",
          "title": "Buy groceries",
          "completed": false,
          "created_at": "2026-01-12T10:30:00Z"
        }
      ],
      "pagination": {
        "page": 1,
        "limit": 10,
        "total": 1,
        "pages": 1
      }
    }
  }
}
```

#### **Tool 3: complete_task**

```python
{
  "name": "complete_task",
  "description": "Mark a task as complete with timestamp",
  "preconditions": [
    "Task must exist",
    "User must own the task",
    "Task must not already be completed"
  ],
  "side_effects": [
    "Updates task.completed to true",
    "Sets task.completed_at to current UTC timestamp",
    "Atomic transaction (all-or-nothing)"
  ],
  "parameters": {
    "user_id": "UUID (required)",
    "task_id": "UUID (required)"
  },
  "returns": {
    "task_id": "UUID",
    "status": "'completed' or 'error'",
    "title": "Task title",
    "completed_at": "ISO 8601 UTC timestamp"
  }
}
```

#### **Tool 4: delete_task**

```python
{
  "name": "delete_task",
  "description": "Remove a task permanently (hard delete)",
  "preconditions": [
    "Task must exist",
    "User must own the task"
  ],
  "side_effects": [
    "Removes row from tasks table (hard delete)",
    "Cannot be undone (consider soft-delete if retention needed)"
  ],
  "parameters": {
    "user_id": "UUID (required)",
    "task_id": "UUID (required)"
  },
  "returns": {
    "task_id": "UUID of deleted task",
    "status": "'deleted' or 'error'",
    "message": "Task successfully deleted"
  }
}
```

#### **Tool 5: update_task**

```python
{
  "name": "update_task",
  "description": "Modify task title, description, or other fields",
  "preconditions": [
    "Task must exist",
    "User must own the task"
  ],
  "parameters": {
    "user_id": "UUID (required)",
    "task_id": "UUID (required)",
    "title": "string, 1-200 chars (optional)",
    "description": "string, max 1000 chars (optional)"
  },
  "returns": {
    "task_id": "UUID",
    "status": "'updated' or 'error'",
    "title": "Updated task title",
    "updated_at": "ISO 8601 UTC timestamp"
  }
}
```

### 5. Tool Composability Patterns

Tools can be combined to achieve complex operations:

**Pattern 1: Find & Update**
```
1. list_tasks(user_id, status="all") → get all tasks
2. Find task by title match in results
3. update_task(user_id, task_id, new_title) → update matched task
```

**Pattern 2: Find & Delete**
```
1. list_tasks(user_id, status="all")
2. Find task by title
3. delete_task(user_id, task_id)
```

**Pattern 3: Task Summary**
```
1. list_tasks(user_id, status="all")
2. list_tasks(user_id, status="completed")
3. Count total, completed, pending
4. Calculate completion percentage
```

**Documentation Note:**
> Tools should be composable but stateless. Agent can call multiple tools in sequence,
> but each tool invocation is independent. Results from one tool become input to next.

### 6. Rate Limiting Specifications

Each tool has per-user rate limits to prevent abuse:

| Tool | Limit | Window | Rationale |
|------|-------|--------|-----------|
| add_task | 100 calls | Per minute | Prevent spam creation |
| list_tasks | 500 calls | Per minute | Frequent queries allowed |
| complete_task | 100 calls | Per minute | Prevent rapid completions |
| delete_task | 50 calls | Per minute | Destructive operation |
| update_task | 100 calls | Per minute | Modify operations |

**Error Response for Rate Limiting:**
```json
{
  "error": "rate_limit_exceeded",
  "message": "Rate limit exceeded: 100 add_task calls per minute",
  "details": {
    "limit": 100,
    "window": "1 minute",
    "tool": "add_task",
    "reset_in_seconds": 45
  },
  "status": "error"
}
```

### 7. Security & Authorization Checklist

Every tool must verify:

- ✅ **user_id Extraction**: Extract from JWT token (sub or user_id claim)
- ✅ **Ownership Verification**: Query includes `WHERE user_id = ?` (parameterized)
- ✅ **No Data Leakage**: Error messages don't reveal other users' data
- ✅ **Parameterized Queries**: All SQL via SQLModel with parameters (not string concat)
- ✅ **Timestamp Consistency**: All timestamps in UTC (no timezone conversions)
- ✅ **Transaction Safety**: Multi-step operations are atomic
- ✅ **Concurrent Access**: Handle simultaneous requests (optimistic locking if needed)
- ✅ **Input Sanitization**: Reject null, empty strings, oversized inputs

---

## Implementation Workflow

1. **Read Specifications**
   - @specs/api/mcp-tools.md (MCP tools specification)
   - @specs/database/schema.md (database schema)
   - @specs/features/ai-chatbot/ (Phase 3 features)

2. **Generate Tool Schemas**
   - Create JSON Schema for each tool (5 total)
   - Define input parameters with validation constraints
   - Define output schemas with examples
   - Document error conditions

3. **Define Error Standardization**
   - Create error code enum
   - Document error responses per tool
   - Map errors to rate limiting responses

4. **Document Tool Composition**
   - List common tool sequences
   - Show example multi-tool interactions
   - Document Agent orchestration patterns

5. **Validate Security**
   - Verify user_id in every tool
   - Check parameterized queries
   - Review error message disclosure

6. **Create Implementation Stubs**
   - Generate Python/FastAPI function signatures
   - Add parameter validation decorators
   - Add type hints for all parameters

7. **Generate Documentation**
   - Tool README with examples
   - Integration guide for agents
   - Rate limiting documentation

---

## Output Format

This skill produces:

1. **mcp_tools_schema.json** - Complete MCP SDK-compliant tool definitions
2. **mcp_tools.py** - Python implementation stubs with validators
3. **error_codes.py** - Standardized error definitions
4. **tool_composition_guide.md** - How tools work together
5. **security_checklist.md** - Authorization verification points
6. **rate_limiting_config.yaml** - Rate limit specifications

---

## Security Validation Points

### Before Tool Invocation
- ✅ JWT token is valid and not expired
- ✅ user_id extracted from token claims
- ✅ user_id matches API path parameter

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

## Integration with MCP Server Builder Agent

This skill works with mcp-server-builder agent to:
- Generate MCP tool schemas from specs
- Create tool implementations with validation
- Ensure tools are composable and stateless
- Validate security isolation per tool
- Document error handling patterns
- Define rate limiting per tool

**Usage in Agent Workflow:**
```
1. Agent reads @specs/api/mcp-tools.md
2. Agent uses this skill to generate tool schemas
3. Agent validates schemas against MCP SDK spec
4. Agent creates implementation stubs with validators
5. Agent documents tool composition patterns
6. Agent verifies security checklist is satisfied
```

---

## Related Skills & Agents

- **Agent:** mcp-server-builder (primary user)
- **Skill:** MCP Tool Security & Integration Testing (test generation)
- **Skill:** Stateless Database Integration & Persistence (database patterns)
- **Spec:** @specs/api/mcp-tools.md (source of truth)
- **Spec:** @specs/database/schema.md (schema reference)

---

## Notes for Claude Code

- Use Official MCP SDK format strictly
- Validate all parameters against JSON Schema
- Enforce user_id in every tool
- Return standardized error responses
- Document tool composition patterns
- Include rate limiting per tool
- Verify security checklist for each tool

