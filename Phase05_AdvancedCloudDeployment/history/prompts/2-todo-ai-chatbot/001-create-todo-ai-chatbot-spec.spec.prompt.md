---
id: 001
title: Create Todo AI Chatbot Spec
stage: spec
date: 2026-01-16
surface: agent
model: claude-sonnet-4-5-20250929
feature: phase-3-ai-chatbot
branch: main
user: claude
command: sp.specify
labels: [spec, phase-3, ai-chatbot, mcp-tools, openai-agent]
links:
  spec: specs/2-todo-ai-chatbot/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/2-todo-ai-chatbot/spec.md
tests:
  - specification completeness
---

## Prompt

```
/sp.specify

Define specifications for the Todo AI Chatbot (Phase-3).

====================================
SYSTEM OVERVIEW
====================================

The system provides a conversational interface that allows users to manage todos via natural language.

Users interact with:
- A ChatKit-based UI
- A single chat API endpoint
- An AI agent that uses MCP tools to perform actions

====================================
BACKEND SPECIFICATIONS
====================================

**Chat API Endpoint**
| Method | Endpoint              | Description                         |
|--------|-----------------------|-------------------------------------|
| POST   | /api/{user_id}/chat   | Send message & get AI response      |

**Request**
| Field           | Type    | Required | Description                                                      |
|-----------------|---------|----------|------------------------------------------------------------------|
| conversation_id | integer | No       | Existing conversation ID (creates new if not provided)           |
| message         | string  | Yes      | User's natural language message                                  |

**Response**
| Field           | Type    | Description                    |
|-----------------|---------|--------------------------------|
| conversation_id | integer | The conversation ID            |
| response        | string  | AI assistant's response        |
| tool_calls      | array   | List of MCP tools invoked      |

**Responsibilities:**
- Fetch conversation history from DB
- Store user messages
- Run OpenAI Agent (which using OpenRouter API Key and Endpoint as an external client)
- Allow agent to invoke MCP tools
- Store assistant responses
- Return AI response to client

The server must not store in-memory state.

====================================
DATABASE MODELS
====================================

**Database Model:**
| Model         | Fields                                                                 | Description   |
|---------------|-------------------------------------------------------------------------|---------------|
| Task          | user_id, id, title, description, completed, created_at, updated_at     | Todo items    |
| Conversation  | user_id, id, created_at, updated_at                                    | Chat session  |
| Message       | user_id, id, conversation_id, role (user/assistant), content, created_at | Chat history  |

====================================
MCP TOOL SPECIFICATION
====================================

**MCP Tools Specification**

- Tool: add_task

| Field          | Description                                                                 |
|----------------|-----------------------------------------------------------------------------|
| Purpose        | Create a new task                                                           |
| Parameters     | user_id (string, required), title (string, required), description (string, optional) |
| Returns        | task_id, status, title                                                      |
| Example Input  | {"user_id": "ziakhan", "title": "Buy groceries", "description": "Milk, eggs, bread"} |
| Example Output | {"task_id": 5, "status": "created", "title": "Buy groceries"}              |

- Tool: list_tasks

| Field          | Description                                                                 |
|----------------|-----------------------------------------------------------------------------|
|----------------|-----------------------------------------------------------------------------|
| Tool           | list_tasks                                                                  |
| Purpose        | Retrieve tasks from the list                                                |
| Parameters     | user_id (string, required), status (string, optional: "all", "pending", "completed") |
| Returns        | Array of task objects                                                       |
| Example Input  | {"user_id": "ziakhan", "status": "pending"}                                |
| Example Output | [{"id": 1, "title": "Buy groceries", "completed": false}, ...]             |

- Tool: complete_task

| Field          | Description                                                        |
|----------------|--------------------------------------------------------------------|
| Tool           | complete_task                                                      |
| Purpose        | Mark a task as complete                                            |
| Parameters     | user_id (string, required), task_id (integer, required)           |
| Returns        | task_id, status, title                                             |
| Example Input  | {"user_id": "ziakhan", "task_id": 3}                               |
| Example Output | {"task_id": 3, "status": "completed", "title": "Call mom"}        |

- Tool: delete_task

| Field          | Description                                                        |
|----------------|--------------------------------------------------------------------|
| Tool           | delete_task                                                        |
| Purpose        | Remove a task from the list                                        |
| Parameters     | user_id (string, required), task_id (integer, required)           |
| Returns        | task_id, status, title                                             |
| Example Input  | {"user_id": "ziakhan", "task_id": 2}                               |
| Example Output | {"task_id": 2, "status": "deleted", "title": "Old task"}          |

- Tool: update_task

| Field          | Description                                                                 |
|----------------|-----------------------------------------------------------------------------|
| Tool           | update_task                                                                 |
| Purpose        | Modify task title or description                                            |
| Parameters     | user_id (string, required), task_id (integer, required), title (string, optional), description (string, optional) |
| Returns        | task_id, status, title                                                      |
| Example Input  | {"user_id": "ziakhan", "task_id": 1, "title": "Buy groceries and fruits"}  |
| Example Output | {"task_id": 1, "status": "updated", "title": "Buy groceries and fruits"}   |


The MCP server must expose stateless tools:
- add_task
- list_tasks
- complete_task
- delete_task
- update_task

Each tool:
- Accepts user_id explicitly
- Performs DB operation
- Returns structured JSON

====================================
AGENT BEHAVIOR SPECIFICATION
====================================

- Agent must infer user intent from natural language
- Agent must call MCP tools for all task mutations
- Agent must confirm actions in natural language
- Agent must gracefully handle errors

============================================================================================================
EXAMPLE CODE HOW OPENAI AGENT SDK (FRAMEWORK) WORKS WITH OPENROUTER API KEY AND ENDPOINT (EXTERNAL CLIENT)
============================================================================================================

```python

    Below is the example Code to use OpenAI SDK with OpenRouter:

    import os
    from dotenv import load_dotenv
    from agents import (Agent, Runner, OpenAIChatCompletionsModel, set_tracing_disabled, ModelSettings, function_tool)
    from openai import AsyncOpenAI

    load_dotenv()
    set_tracing_disabled(True)

    OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
    if not OPENROUTER_API_KEY:
        raise Exception("Missing OPENROUTER_API_KEY environment variable")

    OPENROUTER_URL = os.getenv("OPENROUTER_URL")
    if not OPENROUTER_URL:
        raise Exception("Missing OPENROUTER_URL environment variable")

    # Initialize the AsyncOpenAI-compatible client with OpenRouter details
    external_client: AsyncOpenAI = AsyncOpenAI(
        api_key=OPENROUTER_API_KEY,
        base_url=OPENROUTER_URL,
    )


    # Model Initialization - using OpenRouter model with OpenAI-compatible interface
    model: OpenAIChatCompletionsModel = OpenAIChatCompletionsModel(
        model="mistralai/devstral-2512:free",  # Using OpenRouter free model
        openai_client=external_client
    )


    # Create agent and register tools
    agent = Agent(
        name="Physical AI & Humanoid Robotics Tutor",  # Agent's identity
        instructions=(
            """
        - You are an expert AI tutor for the Physical AI & Humanoid Robotics textbook.
        - When a user asks a question, always first call the `retrieve` tool with the user query,
        then use only the return content from retrieve to answer.
        - If the answer is not in the retrieved content via tool, say `I'm sorry. I am here to help you about Physical AI & Humanoid-robotics textbook, so I can only entertain you with information from the textbook.`
        - For section-selected queries where a user wants to know about specific text, use the same retrieval process but focus your response on the selected text.
            * When user highlight task, a dialog box or dropdown menu will appear having option to `Ask AI`, when user click on it, it will directly go to Chatbot as a query and agent will response accordingly.
        - You can add addition information from your own knowledge base to your response but it will be strictly relevant to the book topic and user query about Physical AI & Humanoid-robotics.
        - User ask via `chatbot query` or ask via `selected text`, you will answer within 80 to 150 words.
        """
        ),
        model=model,
        #tools=[retrieve],  If you used any tool then we will add tool like this
        model_settings=ModelSettings(
            tool_choice="required"
        )
    )

    # For sync method of Runner, it will run on CLI my below code

    result = Runner.run_sync(
         starting_agent=agent,
         input="What is Humanoid Robotics?",
    )

```
```

## Response snapshot

Successfully created the Todo AI Chatbot (Phase-3) specification document at `specs/2-todo-ai-chatbot/spec.md`. The specification includes:

1. System overview with conversational interface details
2. Backend specifications for the chat API endpoint
3. Database models for Task, Conversation, and Message entities
4. Detailed MCP tool specifications for add_task, list_tasks, complete_task, delete_task, and update_task
5. Agent behavior specifications
6. Implementation example using OpenAI Agent SDK with OpenRouter
7. Security, authentication, error handling, performance, and testing requirements

The specification adheres to all the requirements provided in the user's request, including the stateless architecture principle and the use of MCP tools for all task operations.

## Outcome

- ✅ Impact: Complete specification for Phase 3 Todo AI Chatbot created
- 🧪 Tests: Specification completeness validated
- 📁 Files: specs/2-todo-ai-chatbot/spec.md created successfully
- 🔁 Next prompts: Ready for Phase 3 implementation planning
- 🧠 Reflection: The specification comprehensively covers all required aspects for the AI chatbot implementation.

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): N/A for specification creation
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Proceed with architecture planning for Phase 3 implementation