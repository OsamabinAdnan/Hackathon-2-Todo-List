"""
Todo AI Agent for Chatbot
Implements the AI agent that uses OpenAI function calling with custom tools for task management
Following the colleague's approach with proper async support.
"""
import os
import json
from dotenv import load_dotenv
from openai import AsyncOpenAI
from app.mcp.tools import add_task, list_tasks, complete_task, update_task, delete_task
from typing import Dict, Any, List
from uuid import UUID

load_dotenv()

# API Configuration with fallback options
# Primary: OpenRouter (free tier available)
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_URL = os.getenv("OPENROUTER_URL", "https://openrouter.ai/api/v1")
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "mistralai/devstral-2512:free")

# Fallback: Cohere API
COHERE_API_KEY = os.getenv("COHERE_API_KEY")
COHERE_URL = os.getenv("COHERE_URL", "https://api.cohere.ai/v1")
COHERE_MODEL = os.getenv("COHERE_MODEL", "command-r-plus")

# Last resort: Qwen API
QWEN_API_KEY = os.getenv("QWEN_API_KEY")
QWEN_URL = os.getenv("QWEN_URL", "https://api.qwen.cn")
QWEN_MODEL = os.getenv("QWEN_MODEL", "qwen3-coder-plus")

# Determine which API to use based on availability
if OPENROUTER_API_KEY:
    # Use OpenRouter API
    API_KEY = OPENROUTER_API_KEY
    BASE_URL = "https://openrouter.ai/api/v1"
    MODEL = os.getenv("OPENROUTER_MODEL", "mistralai/devstral-2512:free")
elif COHERE_API_KEY:
    # Use Cohere API
    API_KEY = COHERE_API_KEY
    BASE_URL = "https://api.cohere.ai/v1"  # Note: This may need adjustment
    MODEL = os.getenv("COHERE_MODEL", "command-r-plus")
elif QWEN_API_KEY and QWEN_URL and QWEN_MODEL:
    # Use Qwen API as fallback
    API_KEY = QWEN_API_KEY
    BASE_URL = QWEN_URL
    MODEL = QWEN_MODEL
else:
    raise Exception("No valid API key found. Please set OPENROUTER_API_KEY, COHERE_API_KEY, or QWEN_API_KEY/QWEN_URL/QWEN_MODEL")

class TodoChatAgent:
    def __init__(self, user_id: str, session):
        self.user_id = user_id
        self.session = session
        # Store context for task selection
        self.pending_task_selection = None

        # Initialize the AsyncOpenAI-compatible client with selected API details
        self.client = AsyncOpenAI(
            api_key=API_KEY,
            base_url=BASE_URL,
        )
        self.model = MODEL

        # Define available tools with proper function schemas
        self.tools_definitions = [
            {
                "type": "function",
                "function": {
                    "name": "add_task",
                    "description": "Create a new todo task with a title and optional description, priority, due date, tags, and recurrence pattern.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "title": {
                                "type": "string",
                                "description": "The title of the task"
                            },
                            "description": {
                                "type": "string",
                                "description": "Optional details about the task"
                            },
                            "priority": {
                                "type": "string",
                                "enum": ["high", "medium", "low", "none"],
                                "description": "Priority level of the task (high, medium, low, or none)"
                            },
                            "due_date": {
                                "type": "string",
                                "description": "Due date for the task in YYYY-MM-DD format or ISO format"
                            },
                            "tags": {
                                "type": "array",
                                "items": {
                                    "type": "string"
                                },
                                "description": "List of tags to categorize the task"
                            },
                            "recurrence_pattern": {
                                "type": "string",
                                "enum": ["daily", "weekly", "monthly", "none"],
                                "description": "How often the task repeats (daily, weekly, monthly, or none)"
                            }
                        },
                        "required": ["title"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "list_tasks",
                    "description": "Retrieve and display a list of tasks for the user. Use this when user says 'show tasks', 'list tasks', 'see my tasks', 'show completed tasks', 'what are my pending tasks', 'show high priority tasks', 'show tasks due today', or similar phrases that indicate wanting to view tasks. Do NOT use this when user wants to change a task's status.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "status": {
                                "type": "string",
                                "enum": ["all", "pending", "completed"],
                                "description": "Filter by status (all, pending, or completed)"
                            },
                            "priority": {
                                "type": "string",
                                "enum": ["high", "medium", "low", "none"],
                                "description": "Filter by priority level (high, medium, low, or none)"
                            },
                            "due_date": {
                                "type": "string",
                                "enum": ["today", "tomorrow", "this_week", "this_month"],
                                "description": "Filter by due date timeframe (today, tomorrow, this_week, this_month) or specific date in YYYY-MM-DD format"
                            }
                        }
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "complete_task",
                    "description": "Mark a specific task as completed (true) or incomplete (false) using its title or ID. Use this when user says 'mark task as completed', 'complete task', 'finish task', 'set task status to completed', or similar phrases that indicate changing a task's completion state.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "task_identifier": {
                                "type": "string",
                                "description": "The task title (partial match supported) or exact ID"
                            },
                            "completed": {
                                "type": "boolean",
                                "description": "Whether to mark the task as completed (true) or incomplete (false)",
                                "default": True
                            }
                        },
                        "required": ["task_identifier"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "update_task",
                    "description": "Update a task's title, description, priority, due date, tags, or recurrence pattern.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "task_identifier": {
                                "type": "string",
                                "description": "The task title (partial match supported) or exact ID"
                            },
                            "title": {
                                "type": "string",
                                "description": "New title"
                            },
                            "description": {
                                "type": "string",
                                "description": "New description"
                            },
                            "priority": {
                                "type": "string",
                                "enum": ["high", "medium", "low", "none"],
                                "description": "New priority level of the task (high, medium, low, or none)"
                            },
                            "due_date": {
                                "type": "string",
                                "description": "New due date for the task in YYYY-MM-DD format or ISO format"
                            },
                            "tags": {
                                "type": "array",
                                "items": {
                                    "type": "string"
                                },
                                "description": "New list of tags to categorize the task"
                            },
                            "recurrence_pattern": {
                                "type": "string",
                                "enum": ["daily", "weekly", "monthly", "none"],
                                "description": "New recurrence pattern for the task (daily, weekly, monthly, or none)"
                            }
                        },
                        "required": ["task_identifier"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "delete_task",
                    "description": "Delete a task permanently. Use this when user says 'delete task', 'remove task', 'task ko remove kardo', 'task delete karo', 'task hata do', 'task delete karde', or similar phrases that indicate wanting to permanently remove a task. When user provides specific details like status, priority, or due date, extract these as separate parameters rather than including them in the task_identifier. For example, if user says 'delete functionality checking task which duedate is 18/1/2026', use task_identifier='functionality checking', due_date='2026-01-18'. If user says 'delete task that is completed', use status='completed'. If multiple tasks match the identifier, the system will ask the user to specify which one to delete.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "task_identifier": {
                                "type": "string",
                                "description": "The task title (partial match supported) or exact ID. Only use the actual title, not additional descriptors like 'completed', 'due date', etc."
                            },
                            "status": {
                                "type": "string",
                                "enum": ["all", "pending", "completed"],
                                "description": "Filter by status (pending, or completed). Use this when user mentions 'completed', 'not completed', 'pending', etc."
                            },
                            "priority": {
                                "type": "string",
                                "enum": ["high", "medium", "low", "none"],
                                "description": "Filter by priority level (high, medium, low, or none). Use this when user mentions priority levels."
                            },
                            "due_date": {
                                "type": "string",
                                "enum": ["today", "tomorrow", "this_week", "this_month"],
                                "description": "Filter by due date timeframe (today, tomorrow, this_week, this_month) or specific date in YYYY-MM-DD format. Use this when user mentions specific dates like '18/1/2026' which should be formatted as '2026-01-18'."
                            }
                        },
                        "required": ["task_identifier"]
                    }
                }
            }
        ]

    def _get_system_prompt(self) -> str:
        return f"""
                - You are a helpful Todo Assistant for user {self.user_id}.
                - You help users manage their tasks using the available tools.
                - When specific tasks are referenced by name, try to find them using the tools.
                - Always confirm the action to the user in a friendly manner.
                - If the tool execution fails, explain why.
                - The current user ID is {self.user_id}.
                - Format your responses in plain text without markdown formatting like ** or *. Use simple formatting: put the task title first and then provide details.
                - You are able to understand English, Urdu and Roman Urdu Languages.
                - You can reply in English, Urdu or Roman Urdu depending on the language of the user.
                - You should not response other than tasks related to user {self.user_id}.
                - If user want to know that you know user {self.user_id}, then you can reply "I know user {self.user_id} and give reply with it name and email address".
                - When users provide complex task specifications (like mentioning status, due date, priority), use appropriate filter parameters in function calls instead of putting everything in the task title field.
                - For deletion requests with specific details, use the status, priority, and due_date parameters in delete_task function to accurately identify the task.
                """

    async def process_message(self, user_input: str, conversation_history: list = None) -> tuple[str, List[Dict[str, Any]]]:
        """
        Process a user message and return the assistant's response and tool calls.
        Handles tool calls automatically.
        """
        # Check if user is asking about their identity
        user_input_lower = user_input.lower().strip()
        if any(phrase in user_input_lower for phrase in ["who am i", "who i am", "my info", "about me", "identity", "user info"]):
            # Fetch user information from database
            from app.models.user import User
            from sqlmodel import select
            user_obj = self.session.exec(select(User).where(User.id == UUID(self.user_id))).first()
            if user_obj:
                user_info_response = f"I know you, your ID is {self.user_id} and I can provide your information: You are {user_obj.name}, with email {user_obj.email}. How can I help you with your tasks today?"
                return user_info_response, []

        # Check if user is responding to a task selection prompt (just a number)
        if user_input.strip().isdigit() and self.pending_task_selection:
            # User is selecting a task by number
            selected_index = int(user_input.strip())
            available_tasks = self.pending_task_selection.get("available_tasks", [])

            if 1 <= selected_index <= len(available_tasks):
                # Find the selected task
                selected_task = available_tasks[selected_index - 1]

                # Delete the selected task
                from app.mcp.tools import delete_task as delete_single_task
                result = delete_single_task(self.session, self.user_id, selected_task["id"])

                # Clear the pending selection
                self.pending_task_selection = None

                # Return the result directly
                if result["success"]:
                    return f"Task '{selected_task['title']}' has been deleted successfully.", []
                else:
                    return f"Failed to delete task: {result['message']}", []
            else:
                # Invalid selection
                self.pending_task_selection = None
                return f"Invalid selection. Please enter a number between 1 and {len(available_tasks)}.", []

        # Prepare the initial message history
        messages = [{"role": "system", "content": self._get_system_prompt()}]

        # Add conversation history if provided
        if conversation_history:
            messages.extend(conversation_history)

        # Add the current user message
        messages.append({"role": "user", "content": user_input})

        # First call to LLM
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            tools=self.tools_definitions,
            tool_choice="auto"
        )

        response_message = response.choices[0].message

        # Track tool calls that were executed
        executed_tool_calls = []

        # Handle tool calls
        if response_message.tool_calls:
            # Append the assistant's message with tool calls to history
            messages.append(response_message)

            for tool_call in response_message.tool_calls:
                function_name = tool_call.function.name
                function_args = json.loads(tool_call.function.arguments)

                tool_output = {
                    "success": False,
                    "message": "Unknown tool"
                }

                try:
                    # Execute the appropriate tool function with the session and user_id
                    if function_name == "add_task":
                        tool_output = add_task(self.session, self.user_id, **function_args)
                    elif function_name == "list_tasks":
                        # Handle parameters or default to "all"
                        status = function_args.get("status", "all")
                        priority = function_args.get("priority", None)
                        due_date = function_args.get("due_date", None)
                        tool_output = list_tasks(self.session, self.user_id, status=status, priority=priority, due_date=due_date)
                    elif function_name == "complete_task":
                        tool_output = complete_task(self.session, self.user_id, **function_args)
                    elif function_name == "update_task":
                        tool_output = update_task(self.session, self.user_id, **function_args)
                    elif function_name == "delete_task":
                        # Check if user is specifying a numbered task (e.g., "1", "2", etc.)
                        task_identifier = function_args.get("task_identifier", "")

                        # Check if the task_identifier is a number, which means user wants to select from a previous list
                        if task_identifier.isdigit():
                            # This means user is selecting a task from a previous list
                            # Check if we have stored available tasks from a previous selection prompt
                            if self.pending_task_selection:
                                # User is selecting from the previous list
                                selected_index = int(task_identifier)
                                available_tasks = self.pending_task_selection.get("available_tasks", [])

                                if 1 <= selected_index <= len(available_tasks):
                                    # Find the selected task
                                    selected_task = available_tasks[selected_index - 1]

                                    # Actually delete the selected task using the stored ID
                                    from app.mcp.tools import delete_task as actual_delete_task
                                    # Pass empty task_identifier and use the specific task ID
                                    actual_delete_result = actual_delete_task(self.session, self.user_id, selected_task["id"])

                                    # Clear the pending selection
                                    self.pending_task_selection = None

                                    tool_output = actual_delete_result
                                else:
                                    # Invalid selection
                                    tool_output = {
                                        "success": False,
                                        "message": f"Invalid selection. Please enter a number between 1 and {len(available_tasks)}."
                                    }
                                    self.pending_task_selection = None
                            else:
                                # No pending selection, treat as normal search with all parameters
                                # Extract all parameters for the delete_task function
                                status = function_args.get("status")
                                priority = function_args.get("priority")
                                due_date = function_args.get("due_date")

                                tool_output = delete_task(self.session, self.user_id, task_identifier, status=status, priority=priority, due_date=due_date)
                        else:
                            # Extract all parameters for the delete_task function
                            status = function_args.get("status")
                            priority = function_args.get("priority")
                            due_date = function_args.get("due_date")

                            tool_output = delete_task(self.session, self.user_id, task_identifier, status=status, priority=priority, due_date=due_date)

                        # If the tool returns multiple tasks, format a user-friendly response
                        if not tool_output.get("success") and "tasks" in tool_output:
                            # Format a message asking user to select which task to delete
                            tasks = tool_output["tasks"]
                            task_list_msg = f"I found {len(tasks)} tasks matching '{tool_output['task_identifier']}'. Which one would you like to delete?\n"
                            for task in tasks:
                                due_date_str = f", due date: {task['due_date']}" if task['due_date'] else ""
                                task_list_msg += f"{task['index']}. {task['title']}{due_date_str}, priority: {task['priority']}, status: {task['status']}\n"
                            task_list_msg += "Please respond with the number of the task you want to delete (e.g., '1' or '2')."

                            tool_output = {
                                "success": False,
                                "message": task_list_msg,
                                "needs_selection": True,
                                "available_tasks": tasks
                            }

                            # Store the available tasks for later selection
                            self.pending_task_selection = {
                                "task_identifier": tool_output.get("task_identifier", task_identifier),
                                "available_tasks": tasks
                            }

                    # Track the executed tool call
                    executed_tool_calls.append({
                        "tool": function_name,
                        "parameters": function_args,
                        "result": tool_output
                    })
                except Exception as e:
                    tool_output = {"success": False, "message": f"Error executing tool: {str(e)}"}

                # Append tool result to history
                messages.append({
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": function_name,
                    "content": json.dumps(tool_output)
                })

            # Second call to LLM to generate final response
            final_response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages
            )

            # If the response indicates that user needs to select a task, store the context
            response_content = final_response.choices[0].message.content
            if self.pending_task_selection and "respond with the number" in response_content:
                # Context is already stored, just return the response
                pass

            return final_response.choices[0].message.content, executed_tool_calls

        return response_message.content, executed_tool_calls

def create_todo_agent(user_id: str):
    """
    Factory function to create the Todo AI Agent
    """
    return lambda session: TodoChatAgent(user_id, session)

async def run_agent_with_input(agent_factory, user_input: str, session, conversation_history: list = None) -> tuple[str, List[Dict[str, Any]]]:
    """
    Run the agent with user input and user context

    Args:
        agent_factory: A function that creates an agent with session
        user_input: The user's message
        session: The database session
        conversation_history: List of previous messages for context

    Returns:
        Tuple of (response string from the agent execution, list of executed tool calls)
    """
    # Create the agent with session
    agent = agent_factory(session)

    # Run the agent with the user input and conversation history (async call)
    response, tool_calls = await agent.process_message(user_input, conversation_history)

    return response, tool_calls