# Quick Start Guide: AI-Powered Todo Chatbot Integration

## Overview
This guide provides a quick start for implementing the AI-Powered Todo Chatbot Integration (Phase 3) following the Spec-Driven Development approach.

## Prerequisites

### Environment Setup
1. Ensure Phase 2 backend is running and accessible
2. Verify database connection to Neon PostgreSQL
3. Confirm OpenAI API access is configured
4. Install required dependencies:
   ```bash
   # Backend dependencies
   pip install openai fastapi sqlmodel python-multipart

   # MCP SDK (Official)
   pip install mcp  # or appropriate MCP SDK package
   ```

### Configuration
1. Set up environment variables:
   ```bash
   # OpenAI API key
   OPENAI_API_KEY=your_openai_api_key_here

   # Database connection
   DATABASE_URL=postgresql://user:pass@ep-xxxx.neon.tech/dbname

   # JWT secret (same as Phase 2)
   BETTER_AUTH_SECRET=your_jwt_secret
   ```

## Getting Started

### 1. Review Specifications
Before implementing, review these key specification documents:
- Feature specification: `@specs/2-todo-ai-chatbot/spec.md`
- API contracts: `@specs/2-todo-ai-chatbot/contracts.md`
- Database schema: `@specs/2-todo-ai-chatbot/schema.md`
- MCP tools: `@specs/api/mcp-tools.md`

### 2. Database Setup
First, create the required database tables for conversations and messages:

1. Create Alembic migration for new tables:
   ```sql
   -- In backend/migrations/002_chatbot_tables.sql
   CREATE TABLE conversations (
       id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
       user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
       title VARCHAR(200),
       created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
       updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
       last_message_at TIMESTAMP WITH TIME ZONE
   );

   CREATE TABLE messages (
       id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
       conversation_id UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
       user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
       role VARCHAR(20) NOT NULL,
       content TEXT NOT NULL,
       tool_calls JSONB,
       created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
   );
   ```

2. Create SQLModel models:
   ```python
   # In backend/app/models/chat.py
   from sqlmodel import Field, SQLModel
   from sqlalchemy import JSON
   from datetime import datetime
   from typing import Optional, Dict, Any
   import uuid

   class Conversation(SQLModel, table=True):
       __tablename__ = "conversations"

       id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
       user_id: uuid.UUID = Field(foreign_key="users.id", nullable=False, index=True)
       title: Optional[str] = Field(default=None, max_length=200)
       created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False, index=True)
       updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
       last_message_at: Optional[datetime] = Field(default=None, index=True)

   class Message(SQLModel, table=True):
       __tablename__ = "messages"

       id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
       conversation_id: uuid.UUID = Field(foreign_key="conversations.id", nullable=False, index=True)
       user_id: uuid.UUID = Field(foreign_key="users.id", nullable=False, index=True)
       role: str = Field(max_length=20, nullable=False, index=True)
       content: str = Field(nullable=False)
       tool_calls: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSON))
       created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False, index=True)
   ```

### 3. Implement MCP Tools
Create the core MCP tools that the AI agent will use:

1. Define tool schemas in `backend/app/mcp/tools.py`:
   ```python
   # Example for add_task tool
   from typing import Dict, Any
   import uuid
   from sqlmodel import select
   from app.models.task import Task
   from app.database import get_session

   async def add_task(user_id: str, title: str, description: str = None,
                     priority: str = "NONE", due_date: str = None, tags: list = None) -> Dict[str, Any]:
       """
       MCP Tool: Create a new task for the authenticated user
       """
       async with get_session() as session:
           # Validate user_id format
           try:
               user_uuid = uuid.UUID(user_id)
           except ValueError:
               return {
                   "error": "invalid_parameter",
                   "message": "Invalid user_id format",
                   "status": "error"
               }

           # Create new task
           task = Task(
               user_id=user_uuid,
               title=title,
               description=description,
               priority=priority,
               due_date=due_date,
               tags=tags or [],
               completed=False
           )

           session.add(task)
           await session.commit()
           await session.refresh(task)

           return {
               "task_id": str(task.id),
               "status": "created",
               "title": task.title,
               "created_at": task.created_at.isoformat()
           }
   ```

2. Implement all 6 MCP tools (add_task, list_tasks, complete_task, delete_task, update_task, get_task_summary)

### 4. Create Chat Endpoint
Implement the main chat endpoint in `backend/app/routes/chat.py`:

```python
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import uuid
from app.middleware.auth import get_current_user
from app.models.user import User
from app.database import get_session
from sqlmodel import select
from app.models.chat import Conversation, Message
from app.utils.jwt import verify_token
import openai
import os

router = APIRouter()

class ChatRequest(BaseModel):
    conversation_id: Optional[str] = None
    message: str
    timestamp: Optional[str] = None

class ChatResponse(BaseModel):
    conversation_id: str
    response: str
    tool_calls: List[Dict[str, Any]]
    trace_id: str
    timestamp: str

@router.post("/{user_id}/chat", response_model=ChatResponse)
async def chat_endpoint(
    user_id: str,
    request: ChatRequest,
    token: str = Depends(verify_token)
):
    """
    Main chat endpoint that processes user messages and returns AI responses
    """
    # Validate user_id matches authenticated user
    if token.get("user_id") != user_id:
        raise HTTPException(status_code=403, detail="User ID mismatch")

    # Initialize OpenAI agent with MCP tools
    # ... implementation details

    # Retrieve conversation history if provided
    # ... implementation details

    # Store user message
    # ... implementation details

    # Execute agent with message and context
    # ... implementation details

    # Store agent response
    # ... implementation details

    # Return response
    # ... implementation details
```

### 5. Integrate with OpenAI Agent
Connect the chat endpoint with OpenAI Agent and MCP tools:

```python
# In backend/app/services/agent_service.py
import openai
from typing import Dict, Any, List
import uuid

class AgentService:
    def __init__(self):
        self.client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        # Register MCP tools with the agent
        self.tools = [
            # Define tools according to MCP specification
        ]

    async def process_message(
        self,
        user_id: str,
        message: str,
        conversation_history: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Process a user message through the OpenAI agent
        """
        # Build message array with system prompt and history
        messages = [
            {"role": "system", "content": "You are a helpful todo list assistant..."},
            *conversation_history,
            {"role": "user", "content": message}
        ]

        # Execute agent with tools
        response = await self.client.chat.completions.create(
            model="gpt-4",
            messages=messages,
            tools=self.tools,
            tool_choice="auto"
        )

        # Process tool calls and responses
        # ... implementation details

        return {
            "response": response.choices[0].message.content,
            "tool_calls": response.choices[0].message.tool_calls or []
        }
```

### 6. Run Tests
Execute the test suite to ensure everything works:

```bash
# Run backend tests
cd backend
pytest tests/ -v

# Run specific chat functionality tests
pytest tests/test_chat.py -v

# Run MCP tool tests
pytest tests/test_mcp_tools.py -v
```

### 7. Deploy
Deploy the MCP server to Hugging Face Spaces:

1. Create a `requirements.txt` with all dependencies
2. Add a `Dockerfile` or use Hugging Face's container system
3. Push to Hugging Face Spaces with the FastAPI app
4. Configure the OpenAI ChatKit to connect to your endpoint

## Key Commands

### Development
```bash
# Run backend locally
cd backend
uvicorn main:app --reload

# Run tests
cd backend
pytest

# Run specific test file
pytest tests/test_chat.py
```

### Database Migrations
```bash
# Apply migrations
cd backend
alembic upgrade head

# Create new migration
alembic revision --autogenerate -m "Add chatbot tables"
```

## Troubleshooting

### Common Issues

1. **JWT Authentication Issues**:
   - Verify `BETTER_AUTH_SECRET` matches Phase 2
   - Check that tokens are properly formatted
   - Ensure user_id in token matches URL parameter

2. **MCP Tool Registration**:
   - Verify tools follow MCP SDK specification
   - Check that all required parameters are defined
   - Ensure user_id validation is implemented in all tools

3. **Database Connection Issues**:
   - Verify `DATABASE_URL` is properly configured
   - Check that new tables were created
   - Ensure foreign key relationships are correct

4. **OpenAI API Issues**:
   - Verify `OPENAI_API_KEY` is set
   - Check API quota limits
   - Ensure proper error handling for API failures

## Next Steps

1. Complete implementation of all MCP tools
2. Implement conversation history management
3. Add rate limiting and security measures
4. Test integration with OpenAI ChatKit frontend
5. Deploy to Hugging Face Spaces
6. Connect ChatKit UI to your endpoint

## Resources

- Main specification: `@specs/2-todo-ai-chatbot/spec.md`
- API contracts: `@specs/2-todo-ai-chatbot/contracts.md`
- MCP tools: `@specs/api/mcp-tools.md`
- Database schema: `@specs/2-todo-ai-chatbot/schema.md`
- Implementation checklist: `@specs/2-todo-ai-chatbot/checklist.md`

---

**Version**: 1.0.0
**Created**: 2026-01-13
**Quick Start Team**: Phase 3 Development Team