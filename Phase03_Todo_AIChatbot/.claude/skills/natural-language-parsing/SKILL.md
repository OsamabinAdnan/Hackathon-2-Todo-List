# Natural Language Parsing & Intent Recognition Skill

## Overview

This skill generates agent prompts and behavior rules that map natural language user inputs to structured MCP tool operations with confidence scoring, ambiguity resolution, and multilingual support (English/Urdu). It includes task summary aggregation logic by filtering and combining list_tasks outputs.

**Skill Type:** Agent Behavior & NLP Pattern Definition
**Phase:** Phase 3 (AI Chatbot Integration)
**Agent:** openai-agent-orchestrator
**Dependencies:** OpenAI Agents SDK, MCP Tool Definitions, Phase 3 Constitution

---

## When to Use This Skill

Use this skill when you need to:

1. **Define Intent Mapping Rules** - Transform natural language patterns to MCP tool calls with examples
2. **Implement Confidence Scoring** - Disambiguate ambiguous commands with ranking algorithms
3. **Handle Edge Cases** - Address typos, slang, multi-part commands, context-dependent utterances
4. **Create Response Templates** - Generate confirmations, errors, and task summaries with consistent tone
5. **Support Multilingual NLU** - Implement language detection and localized intent patterns (English/Urdu)
6. **Test Intent Recognition** - Define 15+ test variations per command type for validation
7. **Aggregate Task Summaries** - Build task statistics from list_tasks output with filtering
8. **Voice Command Parsing** - Prepare agent for voice input preprocessing (Phase 3 bonus)

---

## Core Capabilities

### 1. Intent Classification Framework

Define explicit mapping between natural language patterns and MCP tool operations:

```python
# Intent Classification Hierarchy
{
  "intent_class": {
    "CREATE_TASK": {
      "patterns": [
        "Add {task_title}",
        "Create {task_title}",
        "I need to {task_title}",
        "Remind me to {task_title}",
        "Can you add {task_title}",
        "New task: {task_title}",
        "{task_title} needs to be done"
      ],
      "tool": "add_task",
      "required_params": ["title"],
      "optional_params": ["description", "priority", "due_date"],
      "confidence_threshold": 0.85,
      "ambiguity_markers": ["maybe", "might", "possibly"]
    },
    "LIST_TASKS": {
      "patterns": [
        "Show my tasks",
        "What tasks do I have",
        "List my tasks",
        "What's on my plate",
        "Get my task list",
        "Show all tasks"
      ],
      "tool": "list_tasks",
      "required_params": ["user_id"],
      "optional_params": ["status"],
      "default_params": {"status": "all"},
      "confidence_threshold": 0.90
    },
    "FILTER_TASKS": {
      "patterns": [
        "What's pending",
        "Show pending tasks",
        "Show completed tasks",
        "What have I finished",
        "List my pending",
        "Get my completed tasks"
      ],
      "tool": "list_tasks",
      "required_params": ["user_id", "status"],
      "status_mapping": {
        "pending": ["pending", "todo", "open", "not done", "incomplete"],
        "completed": ["completed", "done", "finished", "closed"]
      },
      "confidence_threshold": 0.88
    },
    "COMPLETE_TASK": {
      "patterns": [
        "Mark {task_id} complete",
        "Complete task {task_id}",
        "Finish {task_id}",
        "Done with {task_id}",
        "Task {task_id} is done"
      ],
      "tool": "complete_task",
      "required_params": ["task_id"],
      "confidence_threshold": 0.90,
      "state_validation": "task must exist and not already completed"
    },
    "DELETE_TASK": {
      "patterns": [
        "Delete {task_id}",
        "Remove {task_id}",
        "Cancel {task_id}",
        "Forget about {task_id}",
        "Get rid of {task_id}"
      ],
      "tool": "delete_task",
      "required_params": ["task_id"],
      "confidence_threshold": 0.92,
      "confirmation_required": true,
      "irreversible": true
    },
    "UPDATE_TASK": {
      "patterns": [
        "Update task {task_id} to {new_title}",
        "Change {task_id} to {new_title}",
        "Rename {task_id} {new_title}",
        "Modify {task_id}: {new_title}"
      ],
      "tool": "update_task",
      "required_params": ["task_id", "title"],
      "optional_params": ["description"],
      "confidence_threshold": 0.85
    },
    "TASK_SUMMARY": {
      "patterns": [
        "What's my task summary",
        "How many tasks do I have",
        "Task statistics",
        "Summarize my tasks",
        "Task overview"
      ],
      "tool_chain": ["list_tasks(all)", "list_tasks(completed)"],
      "aggregation": "calculate_statistics",
      "confidence_threshold": 0.88
    }
  }
}
```

### 2. Confidence Scoring Algorithm

Implement multi-factor confidence calculation for intent recognition:

```python
def calculate_intent_confidence(user_input, intent_pattern):
    """
    Calculate confidence score (0.0-1.0) for intent match.

    Factors (weighted):
    1. Pattern Match Score (40%) - Levenshtein similarity to defined patterns
    2. Semantic Similarity (30%) - Vector embedding similarity via OpenAI
    3. Parameter Extraction (20%) - Can we successfully extract required params?
    4. Language Quality (10%) - Grammar, spelling, punctuation
    """

    confidence = 0.0

    # Factor 1: Pattern Matching (40%)
    pattern_scores = []
    for pattern in intent_pattern["patterns"]:
        similarity = levenshtein_similarity(user_input, pattern)
        pattern_scores.append(similarity)
    pattern_score = max(pattern_scores) * 0.40

    # Factor 2: Semantic Similarity (30%)
    input_embedding = openai_embeddings(user_input)
    pattern_embedding = openai_embeddings(intent_pattern["patterns"][0])
    semantic_score = cosine_similarity(input_embedding, pattern_embedding) * 0.30

    # Factor 3: Parameter Extraction (20%)
    extraction_score = 0.20 if can_extract_required_params(user_input, intent_pattern) else 0.0

    # Factor 4: Language Quality (10%)
    quality_score = assess_input_quality(user_input) * 0.10

    confidence = pattern_score + semantic_score + extraction_score + quality_score

    return confidence, {
        "pattern_score": pattern_score,
        "semantic_score": semantic_score,
        "extraction_score": extraction_score,
        "quality_score": quality_score
    }
```

### 3. Ambiguity Resolution Strategy

Handle cases where multiple intents score above threshold:

```python
# Ambiguity Resolution Rules
{
  "ambiguity_resolution": {
    "rule_1": {
      "condition": "Multiple intents score > threshold",
      "strategy": "select_highest_confidence",
      "threshold": 0.85,
      "resolution_order": ["exact_match", "semantic_highest", "user_ask"]
    },
    "rule_2": {
      "condition": "Similar confidence scores within 0.05",
      "strategy": "ask_user_for_clarification",
      "example": "Did you mean to complete the task or update it? Please clarify."
    },
    "rule_3": {
      "condition": "No intent exceeds threshold (< 0.75)",
      "strategy": "request_clarification_with_suggestions",
      "example": "I'm not sure what you mean. Did you want to:\n1. Add a new task?\n2. View your tasks?\n3. Complete a task?"
    },
    "rule_4": {
      "condition": "Ambiguous parameter extraction",
      "strategy": "ask_for_missing_parameter",
      "example": "Which task would you like to mark complete? (Show list)"
    },
    "rule_5": {
      "condition": "Context-dependent command (e.g., 'Mark it complete')",
      "strategy": "reference_conversation_history",
      "lookup": "recent_task_reference_from_messages",
      "fallback": "ask_for_clarification"
    }
  }
}
```

### 4. Edge Case Handling

Define robust handling for common user input variations:

```python
# Edge Case Patterns
{
  "edge_cases": {
    "typos": {
      "detection": "levenshtein_distance <= 2",
      "example": "complte task 3" → detected as "complete task 3",
      "correction_strategy": "auto_correct_if_confidence > 0.90",
      "user_notification": "Did you mean 'complete task 3'? Yes/No"
    },
    "slang": {
      "detection": "match against slang_dictionary",
      "mapping": {
        "todo": "task",
        "done": "complete",
        "urgent": "high priority",
        "asap": "high priority, due today"
      },
      "processing": "normalize_before_intent_matching"
    },
    "multi_part_commands": {
      "detection": "conjunctions: 'and', 'then', 'also'",
      "example": "Add buy milk AND Mark task 3 complete",
      "strategy": "split_into_sequential_operations",
      "execution": "execute_in_order_with_context_flow",
      "confirmation": "confirm_each_operation_separately"
    },
    "negation": {
      "detection": "negation_words: 'not', 'don't', 'no', 'never'",
      "example": "Don't add milk",
      "processing": "interpret_as_cancel_or_prevent",
      "validation": "verify_user_intent_before_cancellation"
    },
    "imperative_fragments": {
      "detection": "incomplete_sentences_with_low_word_count",
      "example": "buy milk" (implied: "Add task: buy milk")",
      "strategy": "infer_complete_intent_from_context",
      "confidence_adjustment": "reduce_confidence_by_0.10_if_inferred"
    },
    "context_dependent": {
      "detection": "pronouns: 'it', 'that', 'this', 'the last one'",
      "example": "Mark it complete" (requires prior task mention)",
      "strategy": "lookup_conversation_history",
      "window": "last 5 messages",
      "fallback": "ask_for_clarification"
    }
  }
}
```

### 5. Response Template System

Define templates for confirmations, errors, and summaries with language support:

```python
# Response Templates (Language-Keyed)
{
  "response_templates": {
    "task_created": {
      "en": "✅ Task created: '{title}'. You now have {total} tasks ({pending} pending).",
      "ur": "✅ کام بنایا گیا: '{title}'۔ آپ کے پاس اب {total} کام ہیں ({pending} زیرِ التوا)۔"
    },
    "task_completed": {
      "en": "✅ Task '{title}' marked complete. Great job! {pending} pending tasks remaining.",
      "ur": "✅ '{title}' مکمل شدہ۔ بہترین کام! {pending} کام ابھی باقی ہیں۔"
    },
    "task_deleted": {
      "en": "🗑️ Task '{title}' deleted. You have {total} tasks remaining.",
      "ur": "🗑️ '{title}' حذف کیا گیا۔ آپ کے پاس {total} کام باقی ہیں۔"
    },
    "task_updated": {
      "en": "✏️ Task updated to '{new_title}'. Changes saved.",
      "ur": "✏️ '{new_title}' میں اپڈیٹ کیا گیا۔ تبدیلیاں محفوظ ہوگئیں۔"
    },
    "task_not_found": {
      "en": "❌ Task not found. Here are your tasks: {task_list}",
      "ur": "❌ کام نہیں ملا۔ یہاں آپ کے کام ہیں: {task_list}"
    },
    "ambiguous_input": {
      "en": "🤔 I'm not sure what you mean. Did you want to:\n{suggestions}",
      "ur": "🤔 مجھے نہیں پتا آپ کا کیا مطلب ہے۔ کیا آپ یہ کریں گے:\n{suggestions}"
    },
    "permission_denied": {
      "en": "🔒 You don't have permission to modify this task.",
      "ur": "🔒 آپ کو اس کام میں تبدیلی کی اجازت نہیں۔"
    }
  }
}
```

### 6. Task Summary Aggregation Logic

Aggregate task statistics from MCP tool outputs:

```python
# Task Summary Calculation
def calculate_task_summary(all_tasks_response, completed_tasks_response):
    """
    Aggregate task statistics from list_tasks responses.

    Input:
    - all_tasks_response: {tasks: [Task], pagination: {...}}
    - completed_tasks_response: {tasks: [Task], pagination: {...}}

    Output:
    - summary: {total, completed, pending, by_priority, by_status, by_date_range}
    """

    all_tasks = all_tasks_response["tasks"]
    completed_tasks = completed_tasks_response["tasks"]
    completed_ids = {t["task_id"] for t in completed_tasks}

    # Calculate Basic Counts
    total_count = len(all_tasks)
    completed_count = len(completed_tasks)
    pending_count = total_count - completed_count

    # Priority Distribution (from all tasks)
    priority_distribution = {
        "low": sum(1 for t in all_tasks if t.get("priority", "medium") == "low"),
        "medium": sum(1 for t in all_tasks if t.get("priority", "medium") == "medium"),
        "high": sum(1 for t in all_tasks if t.get("priority", "medium") == "high")
    }

    # Status Distribution
    status_distribution = {
        "completed": completed_count,
        "pending": pending_count,
        "overdue": sum(1 for t in all_tasks if is_overdue(t)),
        "due_today": sum(1 for t in all_tasks if is_due_today(t)),
        "due_this_week": sum(1 for t in all_tasks if is_due_this_week(t))
    }

    # Completion Rate
    completion_rate = (completed_count / total_count * 100) if total_count > 0 else 0

    summary = {
        "total": total_count,
        "completed": completed_count,
        "pending": pending_count,
        "completion_rate_percent": round(completion_rate, 1),
        "by_priority": priority_distribution,
        "by_status": status_distribution,
        "last_updated": datetime.utcnow().isoformat(),
        "high_priority_pending": sum(1 for t in all_tasks
                                     if t.get("priority") == "high"
                                     and t["task_id"] not in completed_ids)
    }

    return summary
```

### 7. Task Summary Response Formatting

Format aggregated statistics for user display:

```python
# Summary Display Formats
{
  "summary_display_formats": {
    "text_format": {
      "en": """📊 Task Summary
─────────────────
Total: {total} | Completed: {completed} ({completion_rate}%) | Pending: {pending}

By Priority:
  🔴 High: {high}
  🟡 Medium: {medium}
  🟢 Low: {low}

By Status:
  ✅ Completed: {completed}
  ⏳ Pending: {pending}
  ⚠️ Overdue: {overdue}
  📅 Due Today: {due_today}
  🗓️ Due This Week: {due_this_week}

{high_priority_warning}""",
      "ur": """📊 کاموں کا خلاصہ
─────────────────
کل: {total} | مکمل: {completed} ({completion_rate}%) | زیرِ التوا: {pending}

ترجیح کے لحاظ سے:
  🔴 اہم: {high}
  🟡 درمیانی: {medium}
  🟢 کم: {low}

حالت کے لحاظ سے:
  ✅ مکمل: {completed}
  ⏳ زیرِ التوا: {pending}
  ⚠️ تاخیر میں: {overdue}
  📅 آج کی سررسد: {due_today}
  🗓️ اس ہفتے: {due_this_week}

{high_priority_warning}"""
    },
    "json_format": {
      "structure": {
        "summary": {
          "total": "integer",
          "completed": "integer",
          "pending": "integer",
          "completion_rate_percent": "float"
        },
        "by_priority": {"high": "integer", "medium": "integer", "low": "integer"},
        "by_status": {"completed": "integer", "pending": "integer", "overdue": "integer", ...},
        "high_priority_pending": "integer"
      }
    }
  }
}
```

### 8. Multilingual NLU Support (English/Urdu)

Implement language detection and localized intent patterns:

```python
# Multilingual Intent Mapping
{
  "multilingual_intents": {
    "CREATE_TASK": {
      "en": {
        "patterns": [
          "Add {task_title}",
          "Create {task_title}",
          "I need to {task_title}",
          "New task: {task_title}"
        ]
      },
      "ur": {
        "patterns": [
          "{task_title} شامل کریں",
          "{task_title} بنائیں",
          "مجھے {task_title} کرنا ہے",
          "نیا کام: {task_title}"
        ]
      }
    },
    "COMPLETE_TASK": {
      "en": {
        "patterns": [
          "Mark {task_id} complete",
          "Complete task {task_id}",
          "Finish {task_id}"
        ]
      },
      "ur": {
        "patterns": [
          "{task_id} مکمل کریں",
          "{task_id} ختم کریں",
          "{task_id} ختم ہو گیا"
        ]
      }
    }
  },
  "language_detection": {
    "strategy": "openai_language_detection",
    "fallback": "english",
    "confidence_threshold": 0.80,
    "supported_languages": ["en", "ur"]
  }
}
```

### 9. Intent Recognition Testing Framework

Define 15+ test cases per intent type:

```python
# Test Cases per Intent (Example: CREATE_TASK)
{
  "test_cases": {
    "CREATE_TASK": [
      {
        "input": "Add buy milk",
        "expected_intent": "CREATE_TASK",
        "expected_params": {"title": "buy milk"},
        "min_confidence": 0.90,
        "category": "basic"
      },
      {
        "input": "I need to buy milk",
        "expected_intent": "CREATE_TASK",
        "expected_params": {"title": "buy milk"},
        "min_confidence": 0.85,
        "category": "basic"
      },
      {
        "input": "Create a task: buy milk",
        "expected_intent": "CREATE_TASK",
        "expected_params": {"title": "buy milk"},
        "min_confidence": 0.95,
        "category": "explicit"
      },
      {
        "input": "Can you add buying milk to my tasks?",
        "expected_intent": "CREATE_TASK",
        "expected_params": {"title": "buying milk"},
        "min_confidence": 0.80,
        "category": "polite"
      },
      {
        "input": "buy milk plz",
        "expected_intent": "CREATE_TASK",
        "expected_params": {"title": "buy milk"},
        "min_confidence": 0.75,
        "category": "casual"
      },
      {
        "input": "Add buy milk high priority",
        "expected_intent": "CREATE_TASK",
        "expected_params": {"title": "buy milk", "priority": "high"},
        "min_confidence": 0.85,
        "category": "with_attributes"
      },
      {
        "input": "complte buy milk" (typo),
        "expected_intent": "CREATE_TASK",
        "expected_params": {"title": "buy milk"},
        "min_confidence": 0.70,
        "category": "typo"
      },
      {
        "input": "Remind me to buy milk tomorrow",
        "expected_intent": "CREATE_TASK",
        "expected_params": {"title": "buy milk", "due_date": "tomorrow"},
        "min_confidence": 0.80,
        "category": "with_date"
      },
      {
        "input": "buy milk",
        "expected_intent": "CREATE_TASK",
        "expected_params": {"title": "buy milk"},
        "min_confidence": 0.75,
        "category": "minimal"
      },
      {
        "input": "میں نے دودھ خریدنا ہے" (Urdu),
        "expected_intent": "CREATE_TASK",
        "expected_params": {"title": "دودھ خریدنا"},
        "min_confidence": 0.85,
        "language": "ur",
        "category": "multilingual"
      },
      {
        "input": "Add task: buy milk and bread",
        "expected_intent": "CREATE_TASK or MULTI_PART",
        "expected_params": [{"title": "buy milk"}, {"title": "bread"}],
        "min_confidence": 0.80,
        "category": "multi_part"
      },
      {
        "input": "Maybe add buy milk?",
        "expected_intent": "CREATE_TASK",
        "expected_params": {"title": "buy milk"},
        "confidence_adjustment": -0.15,
        "min_confidence": 0.70,
        "category": "uncertain"
      },
      {
        "input": "I don't want to add milk",
        "expected_intent": "NONE or NEGATION_HANDLING",
        "expected_params": {},
        "category": "negation"
      },
      {
        "input": "Add buy milk for tomorrow",
        "expected_intent": "CREATE_TASK",
        "expected_params": {"title": "buy milk", "due_date": "tomorrow"},
        "min_confidence": 0.82,
        "category": "with_context"
      },
      {
        "input": "create a reminder to buy milk at 5pm",
        "expected_intent": "CREATE_TASK",
        "expected_params": {"title": "buy milk", "due_date": "today", "time": "5pm"},
        "min_confidence": 0.78,
        "category": "with_time"
      },
      {
        "input": "Add 'Call mom' to my tasks",
        "expected_intent": "CREATE_TASK",
        "expected_params": {"title": "Call mom"},
        "min_confidence": 0.90,
        "category": "quoted"
      }
    ]
  }
}
```

### 10. Voice Command Preprocessing (Phase 3 Bonus)

Prepare for voice input handling:

```python
# Voice Command Preprocessing
{
  "voice_preprocessing": {
    "steps": [
      {
        "step": "speech_to_text",
        "implementation": "openai_whisper_api",
        "languages": ["en", "ur"],
        "confidence_threshold": 0.90,
        "fallback": "ask_user_to_repeat"
      },
      {
        "step": "text_normalization",
        "replacements": {
          "gonna": "going to",
          "wanna": "want to",
          "gimme": "give me",
          "ur": "your"
        }
      },
      {
        "step": "punctuation_inference",
        "rule": "add_question_mark_if_intent_is_query",
        "example": "show my tasks" → "show my tasks?"
      }
    ],
    "voice_response_generation": {
      "conciseness_factor": 0.7,
      "max_response_length": "2 sentences",
      "emphasis": "use_action_verbs",
      "example_response": "✅ Task created: buy milk. You now have 5 tasks." (vs text: full summary)
    }
  }
}
```

---

## Implementation Workflow

1. **Read Specifications**
   - @specs/features/task-crud.md (task operations)
   - @specs/api/rest-endpoints.md (REST contracts)
   - @specs/features/ai-chatbot/ (Phase 3 features)

2. **Define Intent Classification**
   - Map natural language patterns to MCP tools
   - Specify required/optional parameters per intent
   - Set confidence thresholds

3. **Implement Confidence Scoring**
   - Pattern matching (Levenshtein similarity)
   - Semantic similarity (OpenAI embeddings)
   - Parameter extraction validation
   - Input quality assessment

4. **Build Ambiguity Resolution**
   - Multi-intent handling with ranking
   - User clarification requests
   - Context-aware disambiguation

5. **Define Edge Cases**
   - Typo correction with thresholds
   - Slang normalization
   - Multi-part command splitting
   - Negation handling
   - Context-dependent reference resolution

6. **Create Response Templates**
   - Confirmation messages with context
   - Error messages with remediation
   - Task summary formatting
   - Language-keyed responses (EN/UR)

7. **Build Task Summary Logic**
   - Aggregate list_tasks outputs
   - Calculate statistics (total, completed, pending)
   - Filter by priority/status/date
   - Format for display (text, JSON, markdown)

8. **Design Testing Framework**
   - 15+ test cases per intent
   - Edge case coverage
   - Multilingual validation
   - Confidence scoring verification

9. **Plan Multilingual Support**
   - Language detection logic
   - Localized intent patterns
   - UTF-8 encoding validation
   - Response templating per language

10. **Document Voice Integration**
    - Preprocessing steps for speech-to-text
    - Response conciseness for audio output
    - Phase 3 bonus architecture

---

## Output Format

This skill produces:

1. **intent_classification.json** - Complete intent mapping with patterns and thresholds
2. **confidence_scoring.py** - Scoring algorithm implementation with factor weighting
3. **ambiguity_resolution.py** - Disambiguation strategies and user clarification logic
4. **response_templates.yaml** - Multilingual response templates (EN/UR) for all scenarios
5. **task_summary_aggregation.py** - Task statistics calculation with filtering
6. **intent_test_cases.json** - 15+ test variations per intent (100+ total)
7. **multilingual_nlu.yaml** - Language detection and localized patterns
8. **voice_preprocessing.yaml** - Voice input handling for Phase 3 bonus

---

## Security & Validation Points

### Before Intent Recognition
- ✅ User is authenticated (JWT token valid)
- ✅ user_id extracted from token
- ✅ Conversation is owned by user

### During Intent Processing
- ✅ Confidence score exceeds threshold (minimum 0.75)
- ✅ Required parameters successfully extracted
- ✅ Parameter values validated (e.g., task_id exists)
- ✅ No injection attacks in user input
- ✅ Ambiguity resolved without assuming user intent

### In Response Generation
- ✅ Task summaries filtered by user_id
- ✅ No data from other users revealed
- ✅ Error messages don't expose system details
- ✅ Response templates use consistent tone/format
- ✅ Multilingual responses preserve meaning and accuracy

### For Testing
- ✅ 100% coverage of intent patterns
- ✅ Edge cases validated at confidence thresholds
- ✅ Multilingual patterns tested per language
- ✅ Typo correction verified with min/max levenshtein distances
- ✅ Context-dependent resolution validated with conversation history

---

## Integration with OpenAI Agent Orchestrator

This skill works with openai-agent-orchestrator agent to:
- Parse user natural language into structured intents
- Map intents to MCP tool calls
- Handle ambiguous commands with clarification
- Generate context-aware responses
- Aggregate task information for summaries
- Support multilingual interaction (Phase 3 bonus)
- Prepare for voice command processing (Phase 3 bonus)

**Usage in Agent Workflow:**
```
1. Agent receives user message from chat endpoint
2. Agent uses this skill to parse intent from message
3. Intent classification returns confidence score + parameters
4. Agent either calls MCP tool or asks for clarification
5. Tool response aggregated into user-friendly confirmation
6. Task summary calculated if requested
7. Response generated from templates (language-aware)
```

---

## Related Skills & Agents

- **Agent:** openai-agent-orchestrator (primary user)
- **Skill:** Tool Chaining & Multi-Step Orchestration (chains multiple tools)
- **Skill:** User Context & Conversation Management (provides JWT + user context)
- **Spec:** @specs/features/task-crud.md (task operations)
- **Spec:** @specs/features/ai-chatbot/ (Phase 3 chatbot spec)

---

## Notes for Claude Code

- Use OpenAI Embeddings API for semantic similarity
- Implement Levenshtein distance for typo detection
- Validate all patterns with 15+ test cases per intent
- Support UTF-8 encoding for Urdu/multilingual text
- Include confidence scoring factors with clear weighting
- Document ambiguity resolution with user examples
- Provide comprehensive task summary aggregation
- Prepare architecture for voice preprocessing (Phase 3 bonus)
