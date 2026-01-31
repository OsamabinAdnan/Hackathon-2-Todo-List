# Tool Chaining & Multi-Step Orchestration Skill

## Overview

This skill implements agent runner patterns for orchestrating multiple MCP tool invocations in a single conversation turn. It defines tool chain composition, data flow mapping between tools, error recovery strategies with exponential backoff, idempotency patterns, rate limiting handling, and timeout management for complex multi-step task operations.

**Skill Type:** Agent Orchestration & Tool Composition
**Phase:** Phase 3 (AI Chatbot Integration)
**Agent:** openai-agent-orchestrator
**Dependencies:** MCP Tool Definitions, OpenAI Agents SDK, Error Handling Framework

---

## When to Use This Skill

Use this skill when you need to:

1. **Define Tool Chain Patterns** - Design sequences of tool invocations (e.g., list → update, list → delete)
2. **Map Data Flow Between Tools** - Transform output from one tool into input for the next
3. **Implement Error Recovery** - Handle failures with retry logic and exponential backoff
4. **Ensure Idempotency** - Support safe re-execution of operations without side effects
5. **Handle Rate Limiting** - Gracefully manage 429 Too Many Requests from MCP tools
6. **Implement Timeouts** - Prevent tool chains from hanging indefinitely
7. **Compose Tool Sequences** - Chain tools for complex operations (Find & Update, Task Summary)
8. **Generate User-Friendly Errors** - Format errors with clear recovery suggestions
9. **Validate Tool Compatibility** - Ensure tool outputs match subsequent tool inputs
10. **Trace Execution Flow** - Debug tool chains with comprehensive logging

---

## Core Capabilities

### 1. Core Tool Chain Patterns

Define the four primary multi-tool composition patterns:

```python
# Tool Chain Pattern Library
{
  "tool_chains": {
    "FIND_AND_UPDATE": {
      "description": "Find task by properties, then update it",
      "pattern": ["list_tasks", "update_task"],
      "use_cases": [
        "User says: 'Change task 1 to Call mom'",
        "User says: 'Update my grocery task to high priority'",
        "User says: 'Mark task as urgent' (find first, then update priority)"
      ],
      "flow": {
        "step_1": {
          "tool": "list_tasks",
          "input": {
            "user_id": "{current_user_id}",
            "status": "all"
          },
          "output": {
            "tasks": "array of Task objects",
            "extraction": "find task matching user criteria (by title, position, etc.)"
          }
        },
        "step_2": {
          "tool": "update_task",
          "input": {
            "user_id": "{current_user_id}",
            "task_id": "{extracted_from_step_1.task_id}",
            "title": "{user_provided_new_title}",
            "description": "{user_provided_description_or_null}"
          },
          "output": {
            "task_id": "uuid",
            "status": "'updated' or 'error'",
            "title": "updated title"
          }
        }
      },
      "data_mapping": {
        "list_tasks_output.tasks[i].task_id": "update_task_input.task_id",
        "list_tasks_output.tasks[i].title": "for_display_in_confirmation"
      }
    },
    "FIND_AND_DELETE": {
      "description": "Find task by properties, then delete it (with confirmation)",
      "pattern": ["list_tasks", "delete_task"],
      "use_cases": [
        "User says: 'Delete the grocery task'",
        "User says: 'Remove the meeting'",
        "User says: 'Get rid of task 3'"
      ],
      "flow": {
        "step_1": {
          "tool": "list_tasks",
          "input": {
            "user_id": "{current_user_id}",
            "status": "all"
          },
          "output": {
            "tasks": "array of Task objects",
            "extraction": "find task matching user criteria"
          }
        },
        "confirmation": {
          "user_prompt": "Are you sure you want to delete '{task_title}'? (Yes/No)",
          "required": true,
          "reason": "delete_task is irreversible"
        },
        "step_2": {
          "tool": "delete_task",
          "input": {
            "user_id": "{current_user_id}",
            "task_id": "{extracted_from_step_1.task_id}"
          },
          "output": {
            "task_id": "uuid",
            "status": "'deleted' or 'error'",
            "message": "deletion confirmation"
          }
        }
      },
      "data_mapping": {
        "list_tasks_output.tasks[i].task_id": "delete_task_input.task_id",
        "list_tasks_output.tasks[i].title": "for_confirmation_prompt"
      }
    },
    "FIND_AND_COMPLETE": {
      "description": "Find task by properties, then mark it complete",
      "pattern": ["list_tasks", "complete_task"],
      "use_cases": [
        "User says: 'Complete the grocery task'",
        "User says: 'Mark the meeting as done'",
        "User says: 'Finish task 2'"
      ],
      "flow": {
        "step_1": {
          "tool": "list_tasks",
          "input": {
            "user_id": "{current_user_id}",
            "status": "pending"
          },
          "output": {
            "tasks": "array of pending Task objects",
            "extraction": "find task matching user criteria"
          }
        },
        "step_2": {
          "tool": "complete_task",
          "input": {
            "user_id": "{current_user_id}",
            "task_id": "{extracted_from_step_1.task_id}"
          },
          "output": {
            "task_id": "uuid",
            "status": "'completed' or 'error'",
            "completed_at": "ISO 8601 timestamp"
          }
        }
      },
      "data_mapping": {
        "list_tasks_output.tasks[i].task_id": "complete_task_input.task_id",
        "list_tasks_output.tasks[i].title": "for_display_in_confirmation"
      }
    },
    "TASK_SUMMARY_GENERATION": {
      "description": "Fetch all tasks and completed tasks, then aggregate statistics",
      "pattern": ["list_tasks(all)", "list_tasks(completed)"],
      "use_cases": [
        "User says: 'What's my task summary?'",
        "User says: 'Show me my task statistics'",
        "User says: 'How many tasks do I have?'"
      ],
      "flow": {
        "step_1": {
          "tool": "list_tasks",
          "input": {
            "user_id": "{current_user_id}",
            "status": "all",
            "limit": 100
          },
          "output": {
            "tasks": "array of all Task objects",
            "pagination": "pagination metadata"
          }
        },
        "step_2": {
          "tool": "list_tasks",
          "input": {
            "user_id": "{current_user_id}",
            "status": "completed",
            "limit": 100
          },
          "output": {
            "tasks": "array of completed Task objects",
            "pagination": "pagination metadata"
          }
        },
        "aggregation": {
          "function": "calculate_task_summary",
          "calculation": {
            "total": "len(step_1.tasks)",
            "completed": "len(step_2.tasks)",
            "pending": "total - completed",
            "completion_rate": "completed / total * 100",
            "by_priority": "count by priority field",
            "by_status": "count by status field"
          }
        }
      },
      "data_mapping": {
        "list_tasks_all_output.tasks": "aggregate",
        "list_tasks_completed_output.tasks": "aggregate",
        "aggregation_result": "format_as_summary_response"
      }
    }
  }
}
```

### 2. Data Flow Mapping & Type Validation

Ensure compatibility between tool outputs and inputs:

```python
# Data Flow Validation Framework
{
  "data_flow_mapping": {
    "extraction_rules": {
      "extract_task_id": {
        "from_tool": "list_tasks",
        "from_field": "tasks[i].task_id",
        "expected_type": "uuid",
        "validation": "is_valid_uuid",
        "to_tool": "update_task|complete_task|delete_task",
        "to_field": "task_id"
      },
      "extract_task_title": {
        "from_tool": "list_tasks",
        "from_field": "tasks[i].title",
        "expected_type": "string",
        "validation": "len > 0 and len <= 200",
        "to_tool": "confirmation_message",
        "to_field": "task_name"
      },
      "extract_task_status": {
        "from_tool": "list_tasks",
        "from_field": "tasks[i].completed",
        "expected_type": "boolean",
        "validation": "is_boolean",
        "to_tool": "state_validation",
        "to_field": "current_status"
      }
    },
    "type_compatibility_checks": {
      "uuid_uuid": {
        "from_type": "uuid",
        "to_type": "uuid",
        "compatible": true,
        "conversion": "none"
      },
      "string_string": {
        "from_type": "string",
        "to_type": "string",
        "compatible": true,
        "conversion": "trim_whitespace"
      },
      "boolean_string_enum": {
        "from_type": "boolean",
        "to_type": "string (enum: 'pending'|'completed')",
        "compatible": true,
        "conversion": "true → 'completed', false → 'pending'"
      },
      "invalid_combination": {
        "from_type": "integer",
        "to_type": "uuid",
        "compatible": false,
        "error": "type_mismatch"
      }
    },
    "validation_pipeline": {
      "step_1": "extract_field_from_response",
      "step_2": "validate_type_matches_expected",
      "step_3": "validate_field_constraints",
      "step_4": "check_type_compatibility_with_next_tool",
      "step_5": "transform_if_needed",
      "step_6": "inject_into_next_tool_input"
    }
  }
}
```

### 3. Error Taxonomy & Recovery Strategies

Define all possible errors and how to recover from each:

```python
# Comprehensive Error Taxonomy
{
  "error_taxonomy": {
    "client_errors": {
      "invalid_task_id": {
        "http_equivalent": 400,
        "cause": "task_id doesn't exist or user doesn't own it",
        "user_message": "❌ Task not found. Would you like to see your tasks? (Yes/No)",
        "recovery": "retry_with_list_tasks_to_show_options",
        "retry_strategy": "none (data error, not transient)"
      },
      "malformed_input": {
        "http_equivalent": 400,
        "cause": "parameter extraction failed (e.g., invalid uuid format)",
        "user_message": "❌ I couldn't understand the task ID. {suggestions}",
        "recovery": "ask_user_for_clarification",
        "retry_strategy": "none (user input error)"
      },
      "permission_denied": {
        "http_equivalent": 403,
        "cause": "user_id doesn't own the task",
        "user_message": "🔒 You don't have permission to modify this task.",
        "recovery": "none (authorization error)",
        "retry_strategy": "none"
      },
      "authentication_required": {
        "http_equivalent": 401,
        "cause": "jwt_token missing or expired",
        "user_message": "🔓 Your session expired. Please log in again.",
        "recovery": "redirect_to_login",
        "retry_strategy": "none"
      }
    },
    "server_errors": {
      "database_error": {
        "http_equivalent": 500,
        "cause": "database connection failure, query timeout, transaction conflict",
        "user_message": "⚠️ Temporary issue accessing your tasks. Please try again.",
        "recovery": "retry_with_exponential_backoff",
        "retry_strategy": {
          "max_retries": 3,
          "initial_delay_ms": 100,
          "backoff_multiplier": 2,
          "max_delay_ms": 1000,
          "delays": [100, 200, 400]
        }
      },
      "service_unavailable": {
        "http_equivalent": 503,
        "cause": "mcp_server temporary outage, rate limit from upstream",
        "user_message": "⚠️ Service temporarily unavailable. Please try again in a moment.",
        "recovery": "retry_with_exponential_backoff",
        "retry_strategy": {
          "max_retries": 2,
          "initial_delay_ms": 500,
          "backoff_multiplier": 2,
          "max_delay_ms": 2000,
          "delays": [500, 1000]
        }
      }
    },
    "rate_limiting": {
      "rate_limit_exceeded": {
        "http_equivalent": 429,
        "cause": "per-user rate limit exceeded (e.g., 100 add_task calls/min)",
        "user_message": "⏱️ You're making requests too quickly. Please wait {wait_seconds} seconds before trying again.",
        "recovery": "wait_before_retry",
        "retry_strategy": {
          "max_retries": 1,
          "wait_time_seconds": "from_reset_in_seconds_header",
          "jitter": "add_random_0_to_1000ms",
          "user_notification": "show_countdown_timer"
        }
      }
    },
    "timeout_errors": {
      "tool_timeout": {
        "http_equivalent": 504,
        "cause": "mcp_tool didn't respond within timeout_ms",
        "user_message": "⏱️ Request took too long. Please try again.",
        "recovery": "retry_once_with_longer_timeout",
        "retry_strategy": {
          "max_retries": 1,
          "timeout_ms": "double_previous_timeout",
          "abort": "if_still_timeout_after_retry"
        }
      }
    }
  }
}
```

### 4. Retry Logic with Exponential Backoff

Implement intelligent retry mechanism for transient failures:

```python
async def execute_with_retry(
    tool_name: str,
    tool_input: dict,
    max_retries: int = 3,
    initial_delay_ms: int = 100,
    backoff_multiplier: float = 2.0,
    max_delay_ms: int = 2000,
    timeout_ms: int = 5000
) -> dict:
    """
    Execute tool with exponential backoff retry logic.

    Retryable Errors:
    - 500 Internal Server Error (database_error)
    - 503 Service Unavailable
    - 504 Gateway Timeout

    Non-Retryable Errors:
    - 400 Bad Request (malformed input)
    - 401 Unauthorized (auth failure)
    - 403 Forbidden (permission denied)
    - 429 Too Many Requests (handle separately)
    """

    attempt = 0
    delay_ms = initial_delay_ms
    last_error = None

    while attempt <= max_retries:
        try:
            # Execute tool with timeout
            result = await asyncio.wait_for(
                invoke_mcp_tool(tool_name, tool_input),
                timeout=timeout_ms / 1000
            )

            # Check if result is error
            if result.get("status") == "error":
                error_code = result.get("error")

                # Non-retryable errors
                if error_code in ["invalid_task_id", "permission_denied", "authentication_required"]:
                    return result  # Return immediately

                # Retryable errors
                if error_code in ["database_error", "service_unavailable"]:
                    if attempt < max_retries:
                        last_error = result
                        await asyncio.sleep(delay_ms / 1000)
                        delay_ms = min(
                            int(delay_ms * backoff_multiplier),
                            max_delay_ms
                        )
                        attempt += 1
                        continue
                    else:
                        # Max retries exceeded
                        return result

                # Unknown error - return immediately
                return result

            # Success
            return result

        except asyncio.TimeoutError:
            last_error = {"error": "tool_timeout", "message": f"Tool '{tool_name}' timed out after {timeout_ms}ms"}

            if attempt < max_retries:
                # Double timeout for next retry
                timeout_ms = timeout_ms * 2
                await asyncio.sleep(delay_ms / 1000)
                delay_ms = min(int(delay_ms * backoff_multiplier), max_delay_ms)
                attempt += 1
                continue
            else:
                return last_error

        except Exception as e:
            # Unexpected error - return immediately
            return {
                "error": "unexpected_error",
                "message": str(e),
                "status": "error"
            }

    # Should not reach here, but handle gracefully
    return last_error or {"error": "unknown_error", "status": "error"}
```

### 5. Idempotency Patterns

Ensure operations are safe to retry without side effects:

```python
# Idempotency Implementation
{
  "idempotency_patterns": {
    "complete_task": {
      "idempotent": true,
      "reason": "Marking already-completed task as complete is safe; no state change",
      "implementation": {
        "check_precondition": "if task.completed == true, return success immediately",
        "operation": "set task.completed = true, task.completed_at = now",
        "idempotency_key": "generate_from(user_id, task_id)",
        "key_validity": "24 hours"
      },
      "response_if_already_completed": {
        "status": "completed",
        "message": "Task was already completed.",
        "task_id": "uuid",
        "completed_at": "ISO 8601 timestamp"
      }
    },
    "delete_task": {
      "idempotent": true,
      "reason": "Soft delete or already deleted; deleting again is safe",
      "implementation": {
        "check_precondition": "if task.deleted_at is not null, return not_found",
        "operation": "set task.deleted_at = now (soft delete)",
        "hard_delete_policy": "hard delete after 30 days retention"
      },
      "response_if_already_deleted": {
        "error": "task_not_found",
        "message": "Task was already deleted.",
        "status": "error"
      }
    },
    "add_task": {
      "idempotent": false,
      "reason": "Creating multiple identical tasks is not idempotent",
      "implementation": {
        "idempotency_key": "generate_from(user_id, title, description, timestamp_window=1hour)",
        "check": "if idempotency_key exists, return previous result",
        "store_key": "in_database_with_ttl",
        "ttl": "24 hours"
      },
      "duplicate_detection": {
        "strategy": "idempotency_key_based",
        "window": "1 hour (same add_task within 1hr is duplicate)",
        "response": "return_original_result_with_201_or_200_status"
      }
    },
    "update_task": {
      "idempotent": true,
      "reason": "Setting fields to same values is safe",
      "implementation": {
        "check_precondition": "if all fields already match, return success immediately",
        "operation": "update fields, set updated_at = now",
        "idempotency_key": "generate_from(user_id, task_id, new_fields_hash)",
        "key_validity": "24 hours"
      }
    }
  }
}
```

### 6. Rate Limiting & Backpressure Handling

Manage per-user rate limits and prevent cascading failures:

```python
# Rate Limiting Strategy
{
  "rate_limiting": {
    "per_user_limits": {
      "add_task": {
        "limit": 100,
        "window": "per minute",
        "error_code": "rate_limit_exceeded",
        "handling": "wait_and_retry_after_reset"
      },
      "list_tasks": {
        "limit": 500,
        "window": "per minute",
        "error_code": "rate_limit_exceeded",
        "handling": "wait_and_retry_after_reset"
      },
      "complete_task": {
        "limit": 100,
        "window": "per minute",
        "error_code": "rate_limit_exceeded",
        "handling": "wait_and_retry_after_reset"
      },
      "delete_task": {
        "limit": 50,
        "window": "per minute",
        "error_code": "rate_limit_exceeded",
        "handling": "wait_and_retry_after_reset"
      },
      "update_task": {
        "limit": 100,
        "window": "per minute",
        "error_code": "rate_limit_exceeded",
        "handling": "wait_and_retry_after_reset"
      }
    },
    "handling_strategy": {
      "detect": "http_status_code == 429 or error == 'rate_limit_exceeded'",
      "extract_wait_time": "from response header: Retry-After (seconds)",
      "fallback_wait_time": "60 seconds",
      "user_notification": "⏱️ Please wait {wait_seconds} seconds before trying again.",
      "show_timer": true,
      "max_retries_after_rate_limit": 1,
      "jitter": "add_random_0_to_5000ms_to_avoid_thundering_herd"
    },
    "backpressure_strategy": {
      "circuit_breaker": {
        "open_after": "5 consecutive rate_limit errors",
        "duration": "60 seconds",
        "state_transitions": {
          "closed": "normal operation",
          "open": "reject requests immediately with clear message",
          "half_open": "allow 1 test request after duration expires"
        }
      },
      "request_queue": {
        "max_queue_size": 50,
        "overflow_strategy": "reject_with_error",
        "error_message": "Request queue full. Please try again later."
      }
    }
  }
}
```

### 7. Timeout Management

Prevent tool chains from hanging indefinitely:

```python
# Timeout Strategy
{
  "timeout_management": {
    "per_tool_timeouts": {
      "list_tasks": {
        "timeout_ms": 3000,
        "rationale": "query with pagination should be fast"
      },
      "add_task": {
        "timeout_ms": 2000,
        "rationale": "single task creation is quick"
      },
      "complete_task": {
        "timeout_ms": 2000,
        "rationale": "single field update is quick"
      },
      "delete_task": {
        "timeout_ms": 2000,
        "rationale": "soft delete is quick"
      },
      "update_task": {
        "timeout_ms": 2000,
        "rationale": "single task update is quick"
      }
    },
    "tool_chain_timeouts": {
      "FIND_AND_UPDATE": {
        "total_timeout_ms": 7000,
        "breakdown": {
          "list_tasks": 3000,
          "update_task": 2000,
          "buffer": 2000
        }
      },
      "FIND_AND_DELETE": {
        "total_timeout_ms": 7000,
        "breakdown": {
          "list_tasks": 3000,
          "delete_task": 2000,
          "buffer": 2000
        }
      },
      "TASK_SUMMARY_GENERATION": {
        "total_timeout_ms": 8000,
        "breakdown": {
          "list_tasks_all": 3000,
          "list_tasks_completed": 3000,
          "aggregation": 1000,
          "buffer": 1000
        }
      }
    },
    "timeout_handling": {
      "on_tool_timeout": {
        "action": "log_error_with_context",
        "retry": "once_with_doubled_timeout",
        "max_retry_timeout": "10 seconds",
        "user_message": "⏱️ Request took too long. Please try again."
      },
      "on_chain_timeout": {
        "action": "abort_remaining_steps",
        "user_message": "⏱️ Operation took too long. Please try again.",
        "partial_rollback": "if_partial_results_unsafe_to_use"
      }
    }
  }
}
```

### 8. Tool Composition Validation

Verify that tool chains are appropriate for the user's intent:

```python
# Tool Composition Validation
{
  "composition_validation": {
    "prerequisites_check": {
      "for_FIND_AND_UPDATE": {
        "preconditions": [
          "User intent is UPDATE_TASK or similar",
          "Task identifier can be extracted (task ID or search criteria)",
          "New values provided for update",
          "User has permission to modify task"
        ],
        "validation": "check_all_preconditions_before_chain_execution"
      },
      "for_FIND_AND_DELETE": {
        "preconditions": [
          "User intent is DELETE_TASK",
          "Task identifier can be extracted",
          "User confirms deletion (irreversible)",
          "User has permission to delete task"
        ],
        "validation": "check_all_preconditions_before_chain_execution"
      },
      "for_TASK_SUMMARY_GENERATION": {
        "preconditions": [
          "User intent is TASK_SUMMARY or similar",
          "User is authenticated",
          "User has at least 1 task"
        ],
        "validation": "check_all_preconditions_before_chain_execution"
      }
    },
    "compatibility_check": {
      "output_field_exists": "tool_output must contain required_field",
      "output_type_matches": "output type compatible with next tool's input type",
      "extraction_succeeds": "can extract_value from tool_output",
      "transformation_preserves_meaning": "if_transformation_required, verify_semantics"
    },
    "fallback_strategies": {
      "if_precondition_fails": {
        "strategy": "ask_user_for_missing_information",
        "example": "Which task would you like to update? (Show list: Yes/No)"
      },
      "if_compatibility_fails": {
        "strategy": "return_error_with_explanation",
        "user_message": "❌ Can't proceed with this operation. {reason}."
      }
    }
  }
}
```

### 9. Error Recovery User Responses

Generate user-friendly error recovery suggestions:

```python
# User-Friendly Error Recovery Messages
{
  "error_recovery_responses": {
    "invalid_task_id": {
      "message": "❌ Task not found.",
      "suggestions": [
        "Would you like to see your tasks? (Respond with 'yes' or 'list')",
        "I can help you create a new task or find an existing one.",
        "Try asking: 'Show my pending tasks' or 'List all tasks'"
      ]
    },
    "task_already_completed": {
      "message": "✅ This task is already completed!",
      "suggestions": [
        "Great job! Want to mark another task as complete?",
        "View your pending tasks: 'Show pending tasks'",
        "See your task summary: 'What's my task summary?'"
      ]
    },
    "permission_denied": {
      "message": "🔒 You don't have permission to modify this task.",
      "suggestions": [
        "This task may belong to another user or conversation.",
        "Check that you're working with your own tasks.",
        "Contact support if you believe this is an error."
      ]
    },
    "rate_limit_exceeded": {
      "message": "⏱️ You're making requests too quickly.",
      "suggestions": [
        "Please wait {wait_seconds} seconds before trying again.",
        "Show countdown timer while waiting",
        "Auto-retry when timer expires if user confirms"
      ]
    },
    "database_error_retry": {
      "message": "⚠️ Temporary issue. Retrying...",
      "suggestions": [
        "Showing progress: 'Attempting retry 1 of 3...'",
        "If all retries fail: 'Service temporarily unavailable. Please try again soon.'"
      ]
    },
    "timeout_error": {
      "message": "⏱️ Request took too long.",
      "suggestions": [
        "The server didn't respond in time.",
        "Try again with a simpler request.",
        "If problems persist, try again in a few moments."
      ]
    }
  }
}
```

### 10. Execution Tracing & Logging

Debug tool chains with comprehensive logging:

```python
# Execution Tracing Framework
{
  "execution_tracing": {
    "trace_format": {
      "trace_id": "uuid",
      "timestamp": "ISO 8601",
      "user_id": "uuid",
      "conversation_id": "uuid",
      "chain_type": "FIND_AND_UPDATE|FIND_AND_DELETE|...",
      "steps": [
        {
          "step_number": 1,
          "tool_name": "list_tasks",
          "input": {"user_id": "...", "status": "all"},
          "status": "success|error|timeout",
          "latency_ms": 150,
          "output": "{tasks: [...]}",
          "timestamp": "ISO 8601"
        },
        {
          "step_number": 2,
          "tool_name": "update_task",
          "input": {"user_id": "...", "task_id": "...", "title": "..."},
          "status": "success",
          "latency_ms": 200,
          "output": "{task_id: '...', status: 'updated'}",
          "timestamp": "ISO 8601"
        }
      ],
      "chain_status": "success|error|partial",
      "total_latency_ms": 350,
      "errors": []
    },
    "logging_levels": {
      "debug": "log_all_inputs_outputs_transformations",
      "info": "log_chain_start_end_and_errors",
      "warning": "log_retries_timeouts_rate_limits",
      "error": "log_failed_chains_with_context"
    },
    "log_storage": {
      "destination": "application_logs",
      "retention": "30 days",
      "encryption": "log_trace_ids_not_sensitive_data"
    }
  }
}
```

---

## Implementation Workflow

1. **Read Specifications**
   - @specs/features/task-crud.md (tool specifications)
   - @specs/api/rest-endpoints.md (error response contracts)
   - Error handling strategy documents

2. **Define Tool Chain Patterns**
   - Identify 4 core patterns (Find & Update, Find & Delete, Find & Complete, Summary)
   - Document each with use cases and data flow
   - Specify preconditions and postconditions

3. **Implement Data Flow Mapping**
   - Define extraction rules (output → input transformation)
   - Create type compatibility validation
   - Build transformation pipeline

4. **Build Error Taxonomy**
   - Classify errors (client, server, rate limiting, timeout)
   - Specify recovery strategy per error
   - Create user-friendly error messages

5. **Implement Retry Logic**
   - Configure exponential backoff parameters
   - Implement bounded retry attempts
   - Handle timeout escalation

6. **Define Idempotency Patterns**
   - Identify idempotent operations (complete, delete, update)
   - Implement idempotency keys with TTL
   - Handle duplicate detection

7. **Configure Rate Limiting**
   - Set per-tool rate limit thresholds
   - Implement circuit breaker pattern
   - Build request queue with backpressure

8. **Set Timeout Values**
   - Per-tool timeouts (list: 3s, create/update/delete: 2s)
   - Chain timeouts (7-8s total)
   - Timeout escalation strategy

9. **Create Composition Validation**
   - Build precondition checking
   - Implement compatibility checking
   - Design fallback strategies

10. **Build Execution Tracing**
    - Trace ID generation
    - Comprehensive step logging
    - Error context capture

---

## Output Format

This skill produces:

1. **tool_chain_patterns.json** - Complete tool chain definitions (Find & Update, Delete, Complete, Summary)
2. **data_flow_mapping.py** - Output extraction, type validation, transformation logic
3. **error_taxonomy.yaml** - Comprehensive error classification with recovery strategies
4. **retry_logic.py** - Exponential backoff implementation with bounded retries
5. **idempotency.py** - Idempotency key generation and duplicate detection
6. **rate_limiting.py** - Circuit breaker, request queue, backpressure handling
7. **timeout_config.yaml** - Per-tool and chain timeouts with escalation
8. **composition_validation.py** - Precondition and compatibility checking
9. **error_recovery_responses.yaml** - User-friendly recovery suggestions
10. **execution_trace.py** - Comprehensive tracing framework

---

## Security & Validation Points

### Before Tool Chain Execution
- ✅ User is authenticated (JWT valid)
- ✅ All preconditions are satisfied
- ✅ Tool compatibility verified
- ✅ Rate limits not exceeded

### During Tool Chain Execution
- ✅ Each tool call includes proper user_id
- ✅ Output validation passed before next step
- ✅ Type compatibility confirmed
- ✅ Timeout monitored per step
- ✅ Rate limit headers checked

### On Tool Chain Failure
- ✅ Error classified correctly
- ✅ Retry strategy appropriate for error type
- ✅ User receives actionable error message
- ✅ No data leakage in error responses
- ✅ Partial results safely handled/rolled back

### For Testing
- ✅ 100% coverage of error types
- ✅ All retry scenarios tested
- ✅ Timeout escalation verified
- ✅ Idempotency validated
- ✅ Rate limiting behavior tested

---

## Integration with OpenAI Agent Orchestrator

This skill works with openai-agent-orchestrator agent to:
- Compose multiple MCP tool calls in single turn
- Handle data flow between tools
- Recover from transient failures
- Manage rate limits and timeouts
- Generate user-friendly errors
- Trace execution for debugging

**Usage in Agent Workflow:**
```
1. Agent receives user message with intent requiring multiple tools
2. Agent selects appropriate tool chain (Find & Update, etc.)
3. Agent uses this skill to validate chain preconditions
4. Step 1 tool executes with retry logic and timeout
5. Output extracted and validated for compatibility
6. Step 2 tool executes with output from step 1
7. On error: classify, recover, notify user
8. On success: aggregate results and format response
```

---

## Related Skills & Agents

- **Agent:** openai-agent-orchestrator (primary user)
- **Skill:** Natural Language Parsing & Intent Recognition (determines which chain)
- **Skill:** User Context & Conversation Management (provides auth context)
- **Spec:** @specs/api/mcp-tools.md (tool definitions and contracts)

---

## Notes for Claude Code

- Implement retry logic with jitter to avoid thundering herd
- Use circuit breaker to prevent cascading failures
- Log all tool invocations with trace IDs for debugging
- Validate all data transformations between tool outputs/inputs
- Handle partial failures gracefully (rollback where needed)
- Provide clear user messages with recovery suggestions
- Test timeout escalation with delayed responses
- Verify idempotency key generation and TTL management
