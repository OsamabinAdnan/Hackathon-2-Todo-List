# User Context & Conversation Management Skill

## Overview

This skill manages user authentication context, conversation state, and multi-turn history retrieval for AI agents. It handles JWT token extraction and validation, user identity verification, conversation history loading from database with pagination, message ordering, context window management, session management, user preference loading, and multi-user isolation enforcement.

**Skill Type:** Authentication & State Management
**Phase:** Phase 3 (AI Chatbot Integration)
**Agent:** openai-agent-orchestrator
**Dependencies:** Better Auth (JWT), SQLModel, Neon PostgreSQL, Conversation/Message Models

---

## When to Use This Skill

Use this skill when you need to:

1. **Extract JWT Tokens** - Parse Authorization headers and extract user identity
2. **Validate Token Claims** - Verify signature, expiry, and user_id matching
3. **Load User Details** - Fetch user preferences (language, timezone) from database
4. **Fetch Conversation History** - Retrieve messages for multi-turn context with pagination
5. **Resume Conversations** - Distinguish between new vs resumed conversations
6. **Manage Context Windows** - Optimize message history for API token limits
7. **Enforce User Isolation** - Prevent cross-user conversation hijacking
8. **Handle Session Timeouts** - Detect expired sessions and redirect to login
9. **Load User Preferences** - Retrieve language/timezone for personalization
10. **Track Conversation State** - Know whether conversation is new, resumed, or stale

---

## Core Capabilities

### 1. JWT Token Extraction & Validation

Extract user identity from Authorization headers and validate token integrity:

```python
# JWT Token Handling
{
  "token_extraction": {
    "source": "Authorization header",
    "format": "Authorization: Bearer {token}",
    "extraction_steps": [
      {
        "step": 1,
        "action": "get_authorization_header",
        "source": "request.headers['Authorization']",
        "expected_format": "Bearer {jwt_token}",
        "error_if_missing": "401 Unauthorized"
      },
      {
        "step": 2,
        "action": "parse_bearer_token",
        "regex": "^Bearer\\s+([A-Za-z0-9\\-._~+/]+=*)$",
        "extract_group": 1,
        "error_if_malformed": "401 Unauthorized: Invalid token format"
      },
      {
        "step": 3,
        "action": "validate_token_structure",
        "validation": "token has 3 parts separated by dots (header.payload.signature)",
        "error_if_invalid": "401 Unauthorized: Malformed JWT"
      }
    ]
  },
  "token_validation": {
    "algorithm": "HS256",
    "secret_source": "environment variable BETTER_AUTH_SECRET",
    "validation_steps": [
      {
        "step": 1,
        "action": "verify_signature",
        "implementation": "PyJWT.decode(token, secret, algorithms=['HS256'])",
        "error_on_invalid": "401 Unauthorized: Invalid token signature"
      },
      {
        "step": 2,
        "action": "check_expiry",
        "claim": "exp",
        "validation": "exp > current_timestamp",
        "error_on_expired": "401 Unauthorized: Token expired"
      },
      {
        "step": 3,
        "action": "verify_issued_at",
        "claim": "iat",
        "validation": "iat <= current_timestamp",
        "error_on_future_token": "401 Unauthorized: Token issued in future"
      },
      {
        "step": 4,
        "action": "check_required_claims",
        "required_claims": ["sub", "email", "iat", "exp"],
        "error_if_missing": "401 Unauthorized: Missing required token claims"
      }
    ]
  },
  "token_claims": {
    "sub": {
      "description": "Subject (user ID)",
      "type": "uuid",
      "extraction": "token_payload['sub']",
      "validation": "is_valid_uuid"
    },
    "email": {
      "description": "User email",
      "type": "string",
      "extraction": "token_payload['email']",
      "validation": "is_valid_email"
    },
    "iat": {
      "description": "Issued at timestamp",
      "type": "unix_timestamp",
      "extraction": "token_payload['iat']",
      "validation": ">= 0 and <= current_time"
    },
    "exp": {
      "description": "Expiration timestamp",
      "type": "unix_timestamp",
      "extraction": "token_payload['exp']",
      "validation": "> current_time (token not expired)"
    }
  },
  "error_handling": {
    "on_invalid_signature": {
      "status": 401,
      "error": "invalid_token",
      "message": "🔓 Your authentication token is invalid. Please log in again.",
      "action": "redirect_to_login"
    },
    "on_expired_token": {
      "status": 401,
      "error": "token_expired",
      "message": "🔓 Your session has expired. Please log in again.",
      "action": "redirect_to_login"
    },
    "on_missing_claims": {
      "status": 401,
      "error": "invalid_token",
      "message": "🔓 Your authentication token is incomplete. Please log in again.",
      "action": "redirect_to_login"
    }
  }
}
```

### 2. User Context Extraction

Extract and validate user_id from token, verify against URL path:

```python
# User Context Extraction
{
  "user_id_extraction": {
    "from_token": {
      "claim": "sub",
      "type": "uuid",
      "validation": "is_valid_uuid"
    },
    "from_url_path": {
      "pattern": "/api/{user_id}/chat",
      "capture_group": "user_id",
      "type": "uuid",
      "validation": "is_valid_uuid"
    },
    "matching_validation": {
      "rule": "token_user_id must equal url_path_user_id",
      "error_if_mismatch": {
        "status": 403,
        "error": "forbidden",
        "message": "🔒 You don't have permission to access this conversation.",
        "reason": "User ID mismatch: token claims different user than URL path"
      }
    }
  },
  "user_context_object": {
    "structure": {
      "user_id": "uuid (from token.sub)",
      "email": "string (from token.email)",
      "token_expires_at": "unix_timestamp (from token.exp)",
      "token_issued_at": "unix_timestamp (from token.iat)",
      "authenticated": "boolean (true if validation passed)",
      "authenticated_at": "ISO 8601 timestamp (server timestamp)"
    },
    "example": {
      "user_id": "550e8400-e29b-41d4-a716-446655440000",
      "email": "user@example.com",
      "token_expires_at": 1705776000,
      "token_issued_at": 1705689600,
      "authenticated": true,
      "authenticated_at": "2026-01-12T10:30:00Z"
    }
  }
}
```

### 3. User Details Fetching

Load user preferences and metadata from database:

```python
# User Details Retrieval
{
  "user_details_loading": {
    "query": "SELECT id, email, created_at, updated_at, preferences FROM users WHERE id = ?",
    "parameters": ["user_id (from token)"],
    "timeout_ms": 1000,
    "fields_to_fetch": {
      "id": "uuid",
      "email": "string",
      "created_at": "ISO 8601 timestamp",
      "updated_at": "ISO 8601 timestamp",
      "preferences": "json (language, timezone, theme)"
    }
  },
  "preferences_schema": {
    "language": {
      "type": "enum: 'en' | 'ur'",
      "default": "en",
      "purpose": "Language for agent responses and task summaries"
    },
    "timezone": {
      "type": "string (IANA timezone)",
      "default": "UTC",
      "example": "America/New_York",
      "purpose": "For due date/time calculations and reminders"
    },
    "theme": {
      "type": "enum: 'light' | 'dark' | 'system'",
      "default": "system",
      "purpose": "Chat UI appearance (frontend preference, not agent-relevant)"
    },
    "notifications_enabled": {
      "type": "boolean",
      "default": true,
      "purpose": "Whether to send task reminders (browser notifications)"
    }
  },
  "error_handling": {
    "user_not_found": {
      "status": 404,
      "error": "user_not_found",
      "message": "🔒 User not found. Please log in again.",
      "action": "redirect_to_login"
    },
    "database_error": {
      "status": 500,
      "error": "database_error",
      "message": "⚠️ Failed to load user preferences. Using defaults.",
      "fallback": "use_default_preferences"
    }
  }
}
```

### 4. Conversation State Management

Distinguish between new and resumed conversations:

```python
# Conversation State Management
{
  "conversation_state_handling": {
    "new_conversation": {
      "detection": "conversation_id is null or new_conversation_requested",
      "action": "create_new_conversation_record",
      "steps": [
        {
          "step": 1,
          "action": "generate_conversation_id",
          "method": "uuid.uuid4()",
          "store": "in_database"
        },
        {
          "step": 2,
          "action": "create_conversation_record",
          "table": "conversations",
          "fields": {
            "id": "generated_conversation_id",
            "user_id": "from_token.sub",
            "created_at": "current_timestamp",
            "updated_at": "current_timestamp"
          }
        },
        {
          "step": 3,
          "action": "send_initial_greeting",
          "message": "Hi! 👋 I'm your task assistant. How can I help?",
          "include_task_summary": true
        }
      ]
    },
    "resumed_conversation": {
      "detection": "conversation_id provided in request",
      "validation": [
        {
          "check": "conversation_exists_in_db",
          "query": "SELECT * FROM conversations WHERE id = ? AND user_id = ?",
          "error_if_not_found": "404 Not Found"
        },
        {
          "check": "conversation_belongs_to_user",
          "validation": "conversation.user_id == token.sub",
          "error_if_not_matched": "403 Forbidden"
        },
        {
          "check": "conversation_not_stale",
          "validation": "conversation.updated_at >= now() - 30 days",
          "error_if_stale": "conversation_expired",
          "action": "suggest_new_conversation"
        }
      ],
      "action": "load_conversation_history",
      "load_strategy": "fetch_recent_messages"
    },
    "conversation_stale_detection": {
      "stale_after_days": 30,
      "rationale": "Conversations older than 30 days are archived",
      "user_notification": "🗂️ This conversation is archived. Start a new one?",
      "options": ["New conversation", "Keep this one"]
    }
  }
}
```

### 5. Conversation History Retrieval with Pagination

Efficiently load message history for context:

```python
# Conversation History Loading
{
  "history_retrieval": {
    "query": """
      SELECT id, role, content, created_at, tool_calls
      FROM messages
      WHERE user_id = ? AND conversation_id = ?
      ORDER BY created_at ASC
      LIMIT ? OFFSET ?
    """,
    "parameters": [
      "user_id (from token)",
      "conversation_id (from request)",
      "limit (default 50, max 100)",
      "offset (for pagination)"
    ],
    "pagination_strategy": {
      "default_limit": 50,
      "max_limit": 100,
      "fallback_if_not_specified": "last 50 messages",
      "offset_based": true,
      "cursor_based_alternative": false
    },
    "message_ordering": {
      "retrieval_order": "ASC (chronological from oldest to newest)",
      "rationale": "Agent context window needs messages in order they occurred",
      "reverse_for_display": "DESC (show newest first in UI)"
    },
    "message_schema": {
      "id": "uuid",
      "role": "enum: 'user' | 'assistant'",
      "content": "string (message text)",
      "created_at": "ISO 8601 timestamp",
      "tool_calls": "array of tool invocations and results (if assistant message)"
    },
    "filtering": {
      "by_user_id": "CRITICAL - only return messages for authenticated user",
      "by_conversation_id": "CRITICAL - only return messages for this conversation",
      "hidden_fields_in_response": "dont_expose_other_users_tasks_in_context"
    }
  },
  "context_window_management": {
    "openai_api_context_limit": {
      "gpt_4": "8192 tokens",
      "gpt_4_turbo": "128000 tokens",
      "default_assumption": "gpt_4_turbo"
    },
    "token_estimation": {
      "method": "rough_estimate_4_chars_per_token",
      "more_accurate": "use_tiktoken_library_for_exact_count",
      "implementation": "count_tokens_before_sending_to_api"
    },
    "context_optimization": {
      "strategy_1": "limit_message_history_window",
      "window_size": {
        "default": 50,
        "if_tokens_exceed_limit": "reduce_to_25",
        "minimum": 5,
        "rationale": "Keep last N messages for context"
      },
      "strategy_2": "summarize_old_messages",
      "implementation": "if conversation > 100 messages, summarize first 50 into 3-5 sentence summary",
      "summary_format": "Here's a summary of earlier conversation: {summary}. Now continuing from message 51..."
    },
    "safety_margin": {
      "reserve_for_response": "20%_of_context_limit",
      "reserved_tokens": "if_limit_8192_then_reserve_1638",
      "rationale": "Ensure API has room for agent response"
    }
  },
  "error_handling": {
    "conversation_not_found": {
      "status": 404,
      "error": "conversation_not_found",
      "message": "🔍 Conversation not found. Starting a new one...",
      "action": "create_new_conversation"
    },
    "user_not_owner": {
      "status": 403,
      "error": "forbidden",
      "message": "🔒 You don't have access to this conversation.",
      "action": "refuse_access"
    },
    "database_error": {
      "status": 500,
      "error": "database_error",
      "message": "⚠️ Failed to load conversation history.",
      "fallback": "return_empty_context_and_warn_user"
    }
  }
}
```

### 6. Session Management

Handle session lifecycle and concurrent session tracking:

```python
# Session Management
{
  "session_lifecycle": {
    "session_creation": {
      "trigger": "user_logs_in",
      "session_record": {
        "id": "uuid",
        "user_id": "from_user_record",
        "created_at": "current_timestamp",
        "last_active_at": "current_timestamp",
        "ip_address": "from_request",
        "user_agent": "from_request",
        "device_id": "optional_fingerprint"
      },
      "store": "in_sessions_table"
    },
    "session_activity_tracking": {
      "on_each_api_call": "update last_active_at = current_timestamp",
      "purpose": "detect stale/inactive sessions",
      "timeout_threshold": "24 hours of inactivity"
    },
    "session_expiry": {
      "token_expiry": "7 days (from Better Auth)",
      "activity_timeout": "24 hours without activity",
      "hard_timeout": "30 days (max session duration)",
      "expiry_action": "invalidate_session_and_redirect_to_login"
    },
    "session_invalidation_triggers": [
      "user_logs_out_explicitly",
      "token_expires",
      "activity_timeout_reached",
      "user_password_changed",
      "logout_all_devices_requested"
    ]
  },
  "concurrent_session_management": {
    "allow_concurrent_sessions": true,
    "max_sessions_per_user": 5,
    "excess_session_handling": {
      "strategy": "invalidate_oldest_session",
      "notification": "notify_user_of_new_login",
      "message": "🔐 You're logged in from a new device: {device_info}. Is this you?"
    }
  },
  "logout_strategy": {
    "logout_single_session": {
      "action": "invalidate_current_session_only",
      "effect": "user_logged_out_on_this_device_only"
    },
    "logout_all_devices": {
      "action": "invalidate_all_sessions_for_user",
      "effect": "user_logged_out_everywhere",
      "confirmation": "Logging you out from all devices. You'll need to log in again."
    }
  }
}
```

### 7. Context Injection for Agent

Prepare context for OpenAI Agents SDK:

```python
# Agent Context Preparation
{
  "agent_context_construction": {
    "system_prompt_injection": {
      "template": """You are a helpful task management assistant.

User: {user_email}
Timezone: {user_timezone}
Language Preference: {user_language}

Current Task Summary:
- Total Tasks: {task_summary.total}
- Completed: {task_summary.completed}
- Pending: {task_summary.pending}
- High Priority Pending: {task_summary.high_priority_pending}

You can help the user:
1. Create new tasks
2. View and filter tasks
3. Mark tasks complete
4. Delete tasks
5. Update task details

Always be helpful, concise, and user-friendly in {user_language}.
      """,
      "variables": [
        "user_email (from user_details)",
        "user_timezone (from preferences)",
        "user_language (from preferences)",
        "task_summary (from MCP tool)",
        "message_history (conversation messages)"
      ]
    },
    "message_context_injection": {
      "format": [
        {
          "role": "system",
          "content": "constructed_system_prompt"
        },
        {
          "role": "user",
          "content": "historical_user_message_1"
        },
        {
          "role": "assistant",
          "content": "historical_assistant_response_1"
        },
        ... # more message pairs from conversation history
        {
          "role": "user",
          "content": "current_user_message"
        }
      ],
      "ordering": "chronological (oldest to newest)"
    },
    "context_size_optimization": {
      "max_messages_to_include": 50,
      "if_exceeds_token_limit": "truncate_oldest_messages_with_warning",
      "warning_message": "📝 Conversation is very long. Started showing context from message {X}."
    }
  }
}
```

### 8. Multi-User Isolation Enforcement

Prevent cross-user data access:

```python
# Multi-User Isolation Validation
{
  "isolation_enforcement": {
    "authentication_checks": [
      {
        "check": "user_is_authenticated",
        "method": "token_validation_passed",
        "error_if_false": "401 Unauthorized"
      },
      {
        "check": "user_id_in_token_matches_url",
        "method": "token.sub == url_params.user_id",
        "error_if_false": "403 Forbidden"
      }
    ],
    "authorization_checks": [
      {
        "check": "conversation_belongs_to_user",
        "query": "SELECT user_id FROM conversations WHERE id = ?",
        "validation": "result.user_id == token.sub",
        "error_if_false": "403 Forbidden"
      },
      {
        "check": "messages_belong_to_user",
        "query": "SELECT user_id FROM messages WHERE conversation_id = ? AND user_id != ?",
        "validation": "no rows returned (all messages belong to user)",
        "error_if_true": "403 Forbidden (cross-user message detected)"
      }
    ],
    "data_filtering": {
      "rule": "all_queries_filtered_by_user_id",
      "implementation": "WHERE user_id = ? (parameterized)",
      "examples": [
        "SELECT * FROM tasks WHERE user_id = ? (never forget WHERE clause)",
        "SELECT * FROM conversations WHERE user_id = ?",
        "SELECT * FROM messages WHERE user_id = ?"
      ]
    },
    "error_responses": {
      "unauthorized_access_attempt": {
        "status": 403,
        "error": "forbidden",
        "message": "🔒 You don't have permission to access this resource.",
        "logging": "log_access_attempt_for_audit"
      }
    }
  },
  "audit_logging": {
    "log_events": [
      "authentication_failure",
      "authorization_failure",
      "cross_user_access_attempt",
      "token_expiry",
      "session_timeout"
    ],
    "log_fields": [
      "timestamp",
      "user_id",
      "event_type",
      "resource_attempted",
      "ip_address",
      "user_agent"
    ],
    "retention": "90 days",
    "analysis": "detect_suspicious_access_patterns"
  }
}
```

### 9. Error Recovery & Retry

Handle authentication/context failures gracefully:

```python
# Error Recovery Strategies
{
  "recovery_strategies": {
    "token_expired": {
      "detection": "exp < current_timestamp",
      "action": "prompt_to_refresh_or_relogin",
      "options": [
        "Auto-refresh if refresh_token available",
        "Redirect to login page",
        "Return 401 to frontend for handling"
      ]
    },
    "conversation_not_found": {
      "detection": "conversation_id not in database",
      "action": "create_new_conversation",
      "notify_user": "🆕 Starting a new conversation"
    },
    "user_details_load_failure": {
      "detection": "database query timeout or error",
      "action": "use_cached_preferences_or_defaults",
      "impact": "language, timezone defaults to English/UTC"
    },
    "context_window_exceeded": {
      "detection": "conversation_history_tokens > api_limit",
      "action": "truncate_history_and_warn",
      "message": "📝 Conversation is very long. Showing recent messages."
    }
  }
}
```

### 10. Context Resumption for New Turns

Handle multi-turn conversation continuation:

```python
# Multi-Turn Conversation Management
{
  "new_turn_processing": {
    "on_each_user_message": {
      "step_1": "extract_auth_context",
      "step_2": "validate_token",
      "step_3": "load_user_details",
      "step_4": "retrieve_conversation_history",
      "step_5": "prepare_agent_context",
      "step_6": "invoke_agent_with_full_context",
      "step_7": "store_agent_response_in_messages_table"
    },
    "context_persistence": {
      "store_user_message": {
        "table": "messages",
        "fields": {
          "id": "uuid",
          "user_id": "from_token",
          "conversation_id": "from_request",
          "role": "'user'",
          "content": "message_text",
          "created_at": "current_timestamp"
        }
      },
      "store_agent_response": {
        "table": "messages",
        "fields": {
          "id": "uuid",
          "user_id": "from_token",
          "conversation_id": "from_request",
          "role": "'assistant'",
          "content": "agent_response_text",
          "tool_calls": "json array of tool invocations",
          "created_at": "current_timestamp"
        }
      }
    },
    "conversation_update": {
      "on_new_message": "UPDATE conversations SET updated_at = ? WHERE id = ?",
      "purpose": "track conversation freshness for expiry"
    }
  }
}
```

---

## Implementation Workflow

1. **Read Specifications**
   - @specs/features/authentication.md (JWT/Better Auth setup)
   - @specs/database/schema.md (User, Conversation, Message models)
   - @specs/api/rest-endpoints.md (chat endpoint contract)

2. **Implement JWT Extraction**
   - Parse Authorization header
   - Validate Bearer token format
   - Extract token string

3. **Implement Token Validation**
   - Verify signature with secret
   - Check expiry timestamp
   - Verify issued-at claim
   - Validate required claims

4. **Implement User Context Extraction**
   - Extract user_id from token (sub claim)
   - Verify URL path user_id matches
   - Create user_context object

5. **Implement User Details Loading**
   - Query users table by user_id
   - Extract preferences (language, timezone)
   - Cache for performance

6. **Implement Conversation State**
   - Detect new vs resumed conversation
   - Validate conversation ownership
   - Create/retrieve conversation record

7. **Implement History Retrieval**
   - Query messages ordered by created_at ASC
   - Implement pagination (limit/offset)
   - Filter by user_id AND conversation_id (CRITICAL)
   - Estimate token count for context window

8. **Implement Session Management**
   - Track session creation/last activity
   - Implement activity timeout (24 hours)
   - Handle concurrent sessions (max 5)
   - Implement logout strategies

9. **Implement Agent Context Preparation**
   - Inject system prompt with user preferences
   - Include message history (chronological)
   - Optimize context window size
   - Pass to OpenAI Agents SDK

10. **Implement Multi-User Isolation**
    - Enforce user_id filtering on all queries
    - Validate conversation/message ownership
    - Log access attempts for audit

---

## Output Format

This skill produces:

1. **jwt_handler.py** - Token extraction and validation
2. **user_context.py** - User identity and preference loading
3. **conversation_manager.py** - New/resumed conversation handling
4. **history_retriever.py** - Message history pagination and loading
5. **session_manager.py** - Session lifecycle and timeout
6. **agent_context_builder.py** - System prompt and message injection
7. **isolation_enforcer.py** - Multi-user data filtering
8. **error_recovery.py** - Auth failure and fallback handling
9. **audit_logger.py** - Security event logging

---

## Security & Validation Points

### Before Agent Receives Context
- ✅ JWT token extracted and validated
- ✅ Token signature verified with secret
- ✅ Token not expired
- ✅ user_id from token matches URL path
- ✅ User exists in database

### During Context Loading
- ✅ All queries filtered by user_id (parameterized)
- ✅ Conversation ownership verified
- ✅ Messages belong only to authenticated user
- ✅ Session is active (not timed out)

### In Agent Execution
- ✅ System prompt includes user context (not other users' tasks)
- ✅ Message history is only this user's messages
- ✅ MCP tool calls include user_id from token
- ✅ Tool results filtered by user_id

### For Testing
- ✅ 100% JWT validation coverage (valid, expired, malformed, missing)
- ✅ Cross-user access attempts blocked (403)
- ✅ Conversation isolation enforced
- ✅ Session timeout enforced
- ✅ Multi-turn context resumption verified

---

## Integration with OpenAI Agent Orchestrator

This skill works with openai-agent-orchestrator agent to:
- Validate authenticated user identity
- Load conversation history for context
- Prepare system prompt with user preferences
- Enforce multi-user isolation
- Manage conversation state (new vs resumed)
- Handle authentication failures

**Usage in Agent Workflow:**
```
1. Agent receives chat request with JWT token
2. Skill validates token and extracts user_id
3. Skill loads user preferences (language, timezone)
4. Skill retrieves conversation history
5. Skill constructs agent context with system prompt
6. Agent receives context with conversation history
7. Agent responds using context
8. Skill stores user message and agent response
```

---

## Related Skills & Agents

- **Agent:** openai-agent-orchestrator (primary user)
- **Skill:** Natural Language Parsing & Intent Recognition (uses user_id from context)
- **Skill:** Tool Chaining & Multi-Step Orchestration (uses user_id in tool calls)
- **Spec:** @specs/features/authentication.md (JWT/Better Auth)
- **Spec:** @specs/database/schema.md (User/Conversation/Message models)

---

## Notes for Claude Code

- Use PyJWT library for token validation
- Always filter queries by user_id (parameterized queries to prevent injection)
- Cache user preferences with 1-hour TTL to reduce database queries
- Implement token refresh for expired tokens (if refresh_token available)
- Log all authentication/authorization attempts for security audit
- Handle token validation timeouts gracefully (fail-secure)
- Estimate context window tokens accurately using tiktoken library
- Prepare system prompt that doesn't leak other users' data
- Test cross-user access prevention with multiple authenticated users
- Validate conversation ownership before loading history
