---
name: agent-behavior-testing
description: "Create comprehensive test suites for OpenAI Agent SDK behavior using pytest with mock MCP tools, verifying intent parsing, tool selection, parameter extraction, error recovery, and multi-user isolation. Use when: (1) testing agent's natural language understanding for 7 intents (add_task, list_tasks, complete_task, update_task, delete_task, get_summary, query_tasks) with 15+ variations per intent (100+ total test cases), (2) mocking MCP tool implementations without database dependencies, (3) verifying correct tool selection for each intent with confidence scoring, (4) testing parameter extraction accuracy (title, priority, status, filters), (5) testing ambiguity resolution when multiple intents are possible, (6) testing error recovery when tool invocations fail, (7) verifying multi-user isolation in agent responses (never leak other users' data), (8) testing conversation history usage across multi-turn exchanges, (9) testing multilingual input (EN + Urdu) with correct intent detection, (10) testing response generation and formatting compliance, (11) testing tool chain orchestration (multiple tools in sequence)."
---

# Agent Behavior Testing

## Core Responsibility

Test OpenAI Agent SDK behavior with mock MCP tools using pytest. Verify:

1. **Intent Recognition**: Accurately detect user intent from 7 intents (100+ variations, 15+ per intent)
2. **Tool Selection**: Choose correct MCP tool for each intent with high confidence
3. **Parameter Extraction**: Correctly parse title, priority, status, filters from natural language
4. **Confidence Scoring**: Assign confidence scores reflecting intent clarity
5. **Ambiguity Resolution**: Handle unclear intent (multiple possible tools) gracefully
6. **Error Recovery**: Handle tool failures, retries, and partial success
7. **Multi-User Isolation**: Never expose data from other users
8. **Conversation History**: Use context from prior messages in multi-turn flows
9. **Multilingual Support**: Support English and Urdu input with correct intent detection
10. **Response Format**: Generate user-friendly responses with task summaries
11. **Tool Chaining**: Execute multiple tools in correct sequence

## Quick Start: Mock Tool Testing

```python
# Use mocks to avoid database dependencies
import pytest
from unittest.mock import AsyncMock, patch
from app.agents.openai import AgentSdk

@pytest.fixture
def mock_tools():
    """Mock MCP tools"""
    return {
        "add_task": AsyncMock(return_value={"id": "task-1", "title": "Buy milk"}),
        "list_tasks": AsyncMock(return_value={"tasks": [], "total": 0}),
        "complete_task": AsyncMock(return_value={"id": "task-1", "status": "completed"}),
        "update_task": AsyncMock(return_value={"id": "task-1", "priority": "high"}),
        "delete_task": AsyncMock(return_value={"status": "deleted"}),
        "get_task_summary": AsyncMock(return_value={"total": 5, "completed": 2}),
    }

@pytest.mark.asyncio
async def test_agent_intent_add_task(mock_tools):
    """Agent recognizes 'Add task' intent and calls add_task tool"""
    agent = AgentSdk(user_id="user-123")

    # Mock the tools
    with patch.object(agent, "tools", mock_tools):
        result = await agent.process_message("Add buy milk", trace_id="trace-1")

    assert result["status"] == "success"
    assert "add_task" in result["tools_used"]
    mock_tools["add_task"].assert_called_once()
```

## Section 1: Intent Recognition (7 Intents × 15+ Variations = 100+ Tests)

Test agent's ability to recognize all 7 core intents from natural language variations.

### Intent 1: Add Task (15+ Variations)

```python
@pytest.mark.asyncio
async def test_agent_intent_add_task_variations(mock_tools):
    """Agent recognizes various add task phrasings"""
    agent = AgentSdk(user_id="user-123")

    variations = [
        "Add buy milk",
        "Create a task: buy milk",
        "I need to buy milk",
        "Remind me to buy milk",
        "New task: buy milk",
        "Add 'buy milk' to my tasks",
        "Make a note: buy milk",
        "Put buy milk on my list",
        "Add buy milk with high priority",
        "Create task buy milk, priority high",
        "Add buy milk tomorrow",
        "Schedule buy milk",
        "I want to add buy milk",
        "Please add buy milk",
        "Add milk to shopping list",
    ]

    for variation in variations:
        with patch.object(agent, "tools", mock_tools):
            result = await agent.process_message(variation, trace_id="trace-1")

        assert result["intent"] == "add_task"
        assert "add_task" in result["tools_used"]
```

### Intent 2: List Tasks (15+ Variations)

```python
@pytest.mark.asyncio
async def test_agent_intent_list_tasks_variations(mock_tools):
    """Agent recognizes various list tasks phrasings"""
    agent = AgentSdk(user_id="user-123")

    variations = [
        "Show my tasks",
        "List tasks",
        "What tasks do I have?",
        "Show pending tasks",
        "List my high priority tasks",
        "What do I need to do?",
        "Show tasks due today",
        "Display my task list",
        "Get my tasks",
        "Show all tasks",
        "List tasks by priority",
        "What are my tasks?",
        "Tell me my tasks",
        "How many tasks do I have?",
        "Show incomplete tasks",
    ]

    for variation in variations:
        with patch.object(agent, "tools", mock_tools):
            result = await agent.process_message(variation, trace_id="trace-1")

        assert result["intent"] == "list_tasks"
        assert "list_tasks" in result["tools_used"]
```

### Intent 3: Complete Task (15+ Variations)

```python
@pytest.mark.asyncio
async def test_agent_intent_complete_task_variations(mock_tools):
    """Agent recognizes various task completion phrasings"""
    agent = AgentSdk(user_id="user-123")

    variations = [
        "Mark task as done",
        "Complete task 1",
        "I finished buy milk",
        "Done with buy milk",
        "Check off buy milk",
        "Mark buy milk complete",
        "Finish buy milk",
        "Task done: buy milk",
        "I'm done with buy milk",
        "Complete the task buy milk",
        "Mark buy milk as finished",
        "Done buying milk",
        "Check buy milk off",
        "Task accomplished: buy milk",
        "Checked buy milk off my list",
    ]

    for variation in variations:
        with patch.object(agent, "tools", mock_tools):
            result = await agent.process_message(variation, trace_id="trace-1")

        assert result["intent"] == "complete_task"
        assert "complete_task" in result["tools_used"]
```

### Intent 4: Update Task (15+ Variations)

```python
@pytest.mark.asyncio
async def test_agent_intent_update_task_variations(mock_tools):
    """Agent recognizes various task update phrasings"""
    agent = AgentSdk(user_id="user-123")

    variations = [
        "Update buy milk to high priority",
        "Change task priority to high",
        "Make buy milk high priority",
        "Set buy milk as urgent",
        "Modify task: buy milk → high priority",
        "Edit task buy milk",
        "Change buy milk priority",
        "Update the priority of buy milk",
        "Upgrade buy milk to high priority",
        "Mark buy milk as high priority",
        "I want to change buy milk",
        "Reschedule buy milk",
        "Edit buy milk",
        "Update buy milk details",
        "Modify buy milk task",
    ]

    for variation in variations:
        with patch.object(agent, "tools", mock_tools):
            result = await agent.process_message(variation, trace_id="trace-1")

        assert result["intent"] == "update_task"
        assert "update_task" in result["tools_used"]
```

### Intent 5: Delete Task (15+ Variations)

```python
@pytest.mark.asyncio
async def test_agent_intent_delete_task_variations(mock_tools):
    """Agent recognizes various task deletion phrasings"""
    agent = AgentSdk(user_id="user-123")

    variations = [
        "Delete buy milk",
        "Remove task buy milk",
        "Cancel buy milk",
        "Get rid of buy milk task",
        "I don't need buy milk anymore",
        "Delete the task buy milk",
        "Remove buy milk from my list",
        "Forget about buy milk",
        "Discard buy milk",
        "Delete task",
        "Get rid of this task",
        "Clear buy milk",
        "Erase buy milk from my tasks",
        "I don't want this task",
        "Remove buy milk",
    ]

    for variation in variations:
        with patch.object(agent, "tools", mock_tools):
            result = await agent.process_message(variation, trace_id="trace-1")

        assert result["intent"] == "delete_task"
        assert "delete_task" in result["tools_used"]
```

### Intent 6: Get Summary (15+ Variations)

```python
@pytest.mark.asyncio
async def test_agent_intent_get_summary_variations(mock_tools):
    """Agent recognizes various summary request phrasings"""
    agent = AgentSdk(user_id="user-123")

    variations = [
        "Give me a summary",
        "What's my task summary?",
        "Task statistics",
        "How many tasks have I completed?",
        "Summary of my tasks",
        "Task overview",
        "What's my progress?",
        "Show me task counts",
        "How many tasks pending?",
        "Give me a task report",
        "What's my task status?",
        "Summary report",
        "How are my tasks going?",
        "Tell me my task stats",
        "What's my task breakdown?",
    ]

    for variation in variations:
        with patch.object(agent, "tools", mock_tools):
            result = await agent.process_message(variation, trace_id="trace-1")

        assert result["intent"] == "get_summary"
        assert "get_task_summary" in result["tools_used"]
```

### Intent 7: Query Tasks (15+ Variations)

```python
@pytest.mark.asyncio
async def test_agent_intent_query_tasks_variations(mock_tools):
    """Agent recognizes various query/filter phrasings"""
    agent = AgentSdk(user_id="user-123")

    variations = [
        "Show high priority tasks",
        "Filter by priority high",
        "Show completed tasks",
        "Show pending tasks",
        "Find tasks with priority low",
        "Show tasks by status completed",
        "What are my high priority items?",
        "Show me urgent tasks",
        "Find urgent tasks",
        "List medium priority tasks",
        "Filter tasks by completed",
        "Show my pending items",
        "Display high priority work",
        "Find all urgent tasks",
        "Show tasks matching high priority",
    ]

    for variation in variations:
        with patch.object(agent, "tools", mock_tools):
            result = await agent.process_message(variation, trace_id="trace-1")

        assert result["intent"] in ["query_tasks", "list_tasks"]  # Similar
        assert len(result["tools_used"]) >= 1
```

## Section 2: Parameter Extraction

Test agent's ability to extract correct parameters from natural language.

### Title Extraction
```python
@pytest.mark.asyncio
async def test_agent_extracts_task_title_correctly(mock_tools):
    """Agent extracts task title from various formats"""
    agent = AgentSdk(user_id="user-123")

    test_cases = [
        ("Add buy milk", "buy milk"),
        ("Add task: complete report", "complete report"),
        ("Add 'buy milk' to my list", "buy milk"),
        ("Create task 'schedule meeting'", "schedule meeting"),
        ("Add buy milk and bread", "buy milk and bread"),
    ]

    for message, expected_title in test_cases:
        with patch.object(agent, "tools", mock_tools):
            result = await agent.process_message(message, trace_id="trace-1")

        assert result["parameters"]["title"].lower() == expected_title.lower()
```

### Priority Extraction
```python
@pytest.mark.asyncio
async def test_agent_extracts_priority_correctly(mock_tools):
    """Agent extracts priority from natural language"""
    agent = AgentSdk(user_id="user-123")

    test_cases = [
        ("Add buy milk with high priority", "high"),
        ("Add urgent task: buy milk", "high"),
        ("Add low priority: learn Python", "low"),
        ("Create task: regular work", "medium"),
        ("Important: call mom", "high"),
        ("Add buy milk ASAP", "high"),
    ]

    for message, expected_priority in test_cases:
        with patch.object(agent, "tools", mock_tools):
            result = await agent.process_message(message, trace_id="trace-1")

        assert result["parameters"].get("priority", "medium").lower() == expected_priority.lower()
```

### Status Extraction
```python
@pytest.mark.asyncio
async def test_agent_extracts_status_correctly(mock_tools):
    """Agent extracts status (pending/completed) from context"""
    agent = AgentSdk(user_id="user-123")

    test_cases = [
        ("Mark buy milk as complete", "completed"),
        ("Task done: buy milk", "completed"),
        ("List pending tasks", "pending"),
        ("Show completed items", "completed"),
        ("Complete task", "completed"),
    ]

    for message, expected_status in test_cases:
        with patch.object(agent, "tools", mock_tools):
            result = await agent.process_message(message, trace_id="trace-1")

        if "status" in result["parameters"]:
            assert result["parameters"]["status"].lower() == expected_status.lower()
```

## Section 3: Confidence Scoring

Test agent's confidence in intent classification.

### High Confidence (>0.8)
```python
@pytest.mark.asyncio
async def test_agent_high_confidence_clear_intent(mock_tools):
    """Clear intents receive high confidence (>0.8)"""
    agent = AgentSdk(user_id="user-123")

    clear_messages = [
        "Add buy milk",
        "Mark task complete",
        "Show my tasks",
        "Delete task",
    ]

    for message in clear_messages:
        with patch.object(agent, "tools", mock_tools):
            result = await agent.process_message(message, trace_id="trace-1")

        assert result["confidence"] > 0.8
```

### Medium Confidence (0.5-0.8)
```python
@pytest.mark.asyncio
async def test_agent_medium_confidence_ambiguous_intent(mock_tools):
    """Ambiguous intents receive medium confidence (0.5-0.8)"""
    agent = AgentSdk(user_id="user-123")

    ambiguous_messages = [
        "Buy milk",
        "Work on task",
        "Check tasks",
    ]

    for message in ambiguous_messages:
        with patch.object(agent, "tools", mock_tools):
            result = await agent.process_message(message, trace_id="trace-1")

        assert 0.4 < result["confidence"] < 0.9
```

## Section 4: Error Recovery

Test agent's handling of tool failures and retries.

### Tool Execution Failure → User-Friendly Error
```python
@pytest.mark.asyncio
async def test_agent_handles_tool_failure_gracefully(mock_tools):
    """When tool fails, agent returns user-friendly error"""
    agent = AgentSdk(user_id="user-123")
    mock_tools["add_task"].side_effect = Exception("Database error")

    with patch.object(agent, "tools", mock_tools):
        result = await agent.process_message("Add buy milk", trace_id="trace-1")

    assert result["status"] == "error"
    assert "try again" in result["response"].lower()
    # Never expose technical details
    assert "database" not in result["response"].lower()
```

### Retry Logic
```python
@pytest.mark.asyncio
async def test_agent_retries_failed_tool_execution(mock_tools):
    """Agent retries failed tool calls (exponential backoff)"""
    agent = AgentSdk(user_id="user-123")

    # Fail first 2 times, succeed on 3rd
    mock_tools["add_task"].side_effect = [
        Exception("Timeout"),
        Exception("Connection error"),
        {"id": "task-1", "title": "Buy milk"}
    ]

    with patch.object(agent, "tools", mock_tools):
        result = await agent.process_message("Add buy milk", trace_id="trace-1")

    assert result["status"] == "success"
    assert mock_tools["add_task"].call_count == 3  # 2 failures + 1 success
```

## Section 5: Multi-User Isolation

Verify agent never leaks other users' data.

### User A Cannot See User B's Tasks
```python
@pytest.mark.asyncio
async def test_agent_isolates_user_data(mock_tools):
    """Agent only uses tools for current user"""
    agent_a = AgentSdk(user_id="user-a")
    agent_b = AgentSdk(user_id="user-b")

    # Mock return different task lists for each user
    def get_tasks(user_id, *args, **kwargs):
        if user_id == "user-a":
            return {"tasks": [{"id": "1", "title": "User A task"}], "total": 1}
        else:
            return {"tasks": [{"id": "2", "title": "User B task"}], "total": 1}

    mock_tools["list_tasks"].side_effect = get_tasks

    with patch.object(agent_a, "tools", mock_tools):
        result_a = await agent_a.process_message("Show tasks", trace_id="trace-1")

    with patch.object(agent_b, "tools", mock_tools):
        result_b = await agent_b.process_message("Show tasks", trace_id="trace-1")

    # Verify isolation
    assert "User A task" in result_a["response"]
    assert "User A task" not in result_b["response"]
    assert "User B task" in result_b["response"]
```

## Section 6: Conversation History Usage

Test agent's ability to use prior messages in context.

### Single-Turn Message
```python
@pytest.mark.asyncio
async def test_agent_processes_single_turn_message(mock_tools):
    """Agent processes standalone message without history"""
    agent = AgentSdk(user_id="user-123")

    with patch.object(agent, "tools", mock_tools):
        result = await agent.process_message("Add buy milk", trace_id="trace-1")

    assert result["intent"] == "add_task"
    assert mock_tools["add_task"].call_count == 1
```

### Multi-Turn Conversation
```python
@pytest.mark.asyncio
async def test_agent_uses_conversation_history(mock_tools):
    """Agent uses prior messages to understand context"""
    agent = AgentSdk(user_id="user-123")
    history = []

    # Message 1: Add task
    with patch.object(agent, "tools", mock_tools):
        result1 = await agent.process_message("Add buy milk", trace_id="trace-1", history=history)
    history.append({"role": "user", "content": "Add buy milk"})
    history.append({"role": "assistant", "content": result1["response"]})

    # Message 2: Complete "it" (referring to task from message 1)
    with patch.object(agent, "tools", mock_tools):
        result2 = await agent.process_message("Complete it", trace_id="trace-2", history=history)

    # Agent should infer "it" = "buy milk" from history
    assert result2["intent"] == "complete_task"
    assert "buy milk" in result2.get("inferred_task", "").lower()
```

## Section 7: Multilingual Support

Test agent's handling of English and Urdu input.

### English Intent Recognition
```python
@pytest.mark.asyncio
async def test_agent_recognizes_english_intents(mock_tools):
    """Agent correctly processes English language input"""
    agent = AgentSdk(user_id="user-123", language="en")

    english_messages = [
        "Add buy milk",
        "Show my tasks",
        "Complete task",
        "Delete task",
        "Update priority to high",
    ]

    for message in english_messages:
        with patch.object(agent, "tools", mock_tools):
            result = await agent.process_message(message, trace_id="trace-1")

        assert result["language"] == "en"
        assert result["intent"] is not None
```

### Urdu Intent Recognition
```python
@pytest.mark.asyncio
async def test_agent_recognizes_urdu_intents(mock_tools):
    """Agent correctly processes Urdu language input"""
    agent = AgentSdk(user_id="user-123", language="ur")

    urdu_messages = [
        "کام شامل کریں دودھ خریدیں",  # Add buy milk
        "میرے کام دکھائیں",  # Show my tasks
        "کام مکمل کریں",  # Complete task
        "ترجیح بدل دیں اہم کو",  # Change priority to high
    ]

    for message in urdu_messages:
        with patch.object(agent, "tools", mock_tools):
            result = await agent.process_message(message, trace_id="trace-1", language="ur")

        assert result["language"] == "ur"
        assert result["intent"] is not None
```

## Section 8: Response Generation

Test quality of agent's responses.

### Response Contains Task Summary
```python
@pytest.mark.asyncio
async def test_agent_response_includes_task_summary(mock_tools):
    """Response includes task details in user-friendly format"""
    agent = AgentSdk(user_id="user-123")
    mock_tools["add_task"].return_value = {
        "id": "task-1",
        "title": "Buy milk",
        "priority": "medium",
        "status": "pending"
    }

    with patch.object(agent, "tools", mock_tools):
        result = await agent.process_message("Add buy milk", trace_id="trace-1")

    response = result["response"]
    assert "Buy milk" in response or "milk" in response.lower()
    assert "created" in response.lower() or "added" in response.lower()
```

### Response Never Leaks Implementation Details
```python
@pytest.mark.asyncio
async def test_agent_response_hides_technical_details(mock_tools):
    """Response never shows internal implementation details"""
    agent = AgentSdk(user_id="user-123")

    with patch.object(agent, "tools", mock_tools):
        result = await agent.process_message("Add buy milk", trace_id="trace-1")

    response = result["response"]
    # Never include:
    assert "UUID" not in response
    assert "database" not in response.lower()
    assert "SQL" not in response
    assert "JSON" not in response
    assert "traceback" not in response.lower()
```

## Section 9: Tool Chaining

Test agent's ability to execute multiple tools in sequence.

### Add Task → Get Summary Chain
```python
@pytest.mark.asyncio
async def test_agent_chains_add_and_summary(mock_tools):
    """Agent adds task then shows updated summary"""
    agent = AgentSdk(user_id="user-123")

    with patch.object(agent, "tools", mock_tools):
        result = await agent.process_message(
            "Add buy milk and show my summary",
            trace_id="trace-1"
        )

    assert result["intent"] in ["add_task", "get_summary"]
    tools_used = result["tools_used"]
    # Should use both add_task and get_task_summary
    assert "add_task" in tools_used
    assert "get_task_summary" in tools_used
    # Verify order: add first, then summary
    assert tools_used.index("add_task") < tools_used.index("get_task_summary")
```

---

## Testing Checklist

Use this checklist to validate complete agent behavior test coverage:

- [ ] All 7 intents recognized (100+ test cases, 15+ per intent)
- [ ] Title extraction works for various formats
- [ ] Priority extraction (high/medium/low)
- [ ] Status extraction (pending/completed)
- [ ] Confidence scoring (high >0.8, medium 0.5-0.8, low <0.5)
- [ ] Tool failures handled gracefully
- [ ] Retry logic with exponential backoff (max 3 attempts)
- [ ] Multi-user isolation (user A cannot see user B data)
- [ ] Conversation history used for context
- [ ] Multilingual support (EN + UR)
- [ ] Response generation (task summaries, user-friendly)
- [ ] No technical details leaked in responses
- [ ] Tool chaining (multiple tools in sequence)
- [ ] Ambiguity resolution (clarification or best guess)
- [ ] Response schema validation

---

## Quick Reference: Intent Codes

```python
# 7 Core Intents
"add_task"          # Create new task
"list_tasks"        # Show all tasks with optional filters
"complete_task"     # Mark task as completed
"update_task"       # Modify task properties (priority, description)
"delete_task"       # Remove task permanently
"get_summary"       # Show task statistics and progress
"query_tasks"       # Filter tasks by criteria (status, priority, date)
```

---

## Mock Tool Return Formats

```python
# add_task response
{
    "status": "success",
    "task": {
        "id": "uuid",
        "title": "...",
        "priority": "low|medium|high",
        "status": "pending",
        "created_at": "ISO-8601"
    }
}

# list_tasks response
{
    "tasks": [{...}, ...],
    "total": 10,
    "limit": 50,
    "offset": 0,
    "has_more": false
}

# complete_task response
{
    "status": "success",
    "task": {...}
}

# update_task response
{
    "status": "success",
    "task": {...}
}

# delete_task response
{
    "status": "success",
    "message": "Task deleted"
}

# get_task_summary response
{
    "total": 10,
    "completed": 3,
    "pending": 7,
    "by_priority": {
        "high": 2,
        "medium": 5,
        "low": 3
    }
}
```
