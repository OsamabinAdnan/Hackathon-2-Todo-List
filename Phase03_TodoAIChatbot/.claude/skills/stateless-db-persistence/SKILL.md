# Stateless Database Integration & Persistence Skill

## Overview

This skill implements stateless database patterns for MCP tools using SQLModel and Neon PostgreSQL, ensuring no server-side state retention between requests, conversation persistence across sessions, and atomic transactions with proper error recovery. All state is persisted to the database and retrieved per request for horizontal scalability.

**Skill Type:** Architecture & Implementation
**Phase:** Phase 3 (AI Chatbot Integration)
**Agent:** mcp-server-builder
**ORM:** SQLModel (SQLAlchemy + Pydantic)
**Database:** Neon Serverless PostgreSQL
**Pattern:** Stateless Request-Response with Database-Backed State

---

## When to Use This Skill

Use this skill when you need to:

1. **Design stateless MCP tool patterns** - No global state, all in database
2. **Implement SQLModel session management** - Fetch, process, close per request
3. **Create database migrations** - Alembic scripts for Conversation & Message tables
4. **Design indexed query strategies** - Fast lookups for user_id, conversation_id
5. **Implement transaction safety** - Atomic multi-step operations (all-or-nothing)
6. **Design error recovery patterns** - Connection timeouts, retry logic
7. **Implement conversation history retrieval** - Load context for multi-turn chats
8. **Configure connection pooling** - Neon pool optimization
9. **Prevent race conditions** - Concurrent operation safety
10. **Document state lifecycle** - Per-request state flow

---

## Core Concept: Stateless Request-Response Pattern

### Traditional (Stateful) Anti-Pattern

```
Request → Server keeps connection/cursor open
Request → Server holds Task data in memory
Request → Server processes
Response → Server keeps state
Request → Server uses old state
❌ Problem: Server can't scale horizontally, state is lost on restart
```

### Stateless Pattern (CORRECT)

```
Request 1 → Create session → Fetch data → Process → Commit/Rollback → Close session
Request 2 → Create NEW session → Fetch data → Process → Commit/Rollback → Close session
Request N → Create NEW session → Fetch data → Process → Commit/Rollback → Close session

✅ Benefit: Any server instance can handle any request, state persists in database
✅ Scalability: Load balancer can route to any backend server
✅ Resilience: Server restart doesn't lose conversation history
```

---

## 1. SQLModel Session Management

### Per-Request Session Lifecycle

Every MCP tool follows this pattern:

```python
from sqlalchemy.orm import Session
from sqlmodel import select
from app.models import Task, User
from app.database import SessionLocal

async def add_task(
    user_id: str,
    title: str,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """
    Stateless tool: Create session, execute, close.
    No state retained between requests.
    """
    # Step 1: Create new session for this request
    session = SessionLocal()  # Connection from pool

    try:
        # Step 2: Verify user exists (authentication context)
        user = session.exec(
            select(User).where(User.id == user_id)
        ).first()

        if not user:
            # Step 3: Handle error and CLOSE session before returning
            session.close()
            return {
                "error": "authentication_required",
                "message": "User not found",
                "status": "error"
            }

        # Step 4: Create task
        task = Task(
            user_id=user_id,
            title=title,
            description=description,
            created_at=datetime.utcnow()
        )
        session.add(task)

        # Step 5: Commit transaction (atomically)
        session.commit()

        # Step 6: Refresh to get database-generated fields (ID, timestamps)
        session.refresh(task)

        # Step 7: Prepare response
        response = {
            "task_id": str(task.id),
            "status": "created",
            "title": task.title,
            "created_at": task.created_at.isoformat()
        }

        return response

    except SQLAlchemyError as e:
        # Step 8: Rollback on any database error
        session.rollback()
        return {
            "error": "database_error",
            "message": "Failed to create task. Please retry.",
            "status": "error"
        }

    finally:
        # Step 9: ALWAYS close session (even on error)
        session.close()

    # Step 10: Return response
    # ⚠️ Session is closed before response is returned
    # ✅ No state kept on server
```

### Key Principles

1. **Session Created Fresh**: Each request gets new session from connection pool
2. **Operations Executed**: All database operations use this session
3. **Transaction Committed/Rolled Back**: Atomic all-or-nothing
4. **Session Closed Explicitly**: Always in `finally` block
5. **Response Returned**: After session is closed (no state kept)

### Connection Pool Management

```python
# database.py - Connection pooling configuration

from sqlalchemy import create_engine
from sqlmodel import SQLModel, Session

DATABASE_URL = "postgresql://user:pass@db.neon.tech/dbname?sslmode=require"

engine = create_engine(
    DATABASE_URL,
    echo=False,  # Set to True for SQL logging during development
    pool_size=5,  # Number of permanent connections to maintain
    max_overflow=10,  # Additional connections allowed when pool exhausted
    pool_timeout=30,  # Wait up to 30 seconds for a connection
    pool_recycle=3600,  # Recycle connections after 1 hour (Neon timeout prevention)
    pool_pre_ping=True,  # Test connection before use (detect stale connections)
)

def get_session():
    """Dependency injection for FastAPI - provides session per request"""
    with Session(engine) as session:
        yield session
```

---

## 2. Transaction Safety & Atomic Operations

### Single-Step Operation (add_task)

```python
async def add_task(user_id: str, title: str):
    session = SessionLocal()
    try:
        task = Task(user_id=user_id, title=title)
        session.add(task)
        session.commit()  # Atomic: Either all changes persist or none
        session.refresh(task)
        return {"task_id": task.id, "status": "created"}
    except Exception:
        session.rollback()  # Undo all changes
        return {"error": "database_error", "status": "error"}
    finally:
        session.close()
```

### Multi-Step Operation (complete_task)

```python
async def complete_task(user_id: str, task_id: str):
    """
    Multi-step transaction: Must be atomic
    1. Find task
    2. Verify ownership
    3. Update completion status + timestamp
    4. Commit (all-or-nothing)
    """
    session = SessionLocal()
    try:
        # Step 1: Find task
        task = session.exec(
            select(Task).where(
                (Task.id == task_id) & (Task.user_id == user_id)
            )
        ).first()

        if not task:
            session.close()
            return {"error": "task_not_found", "status": "error"}

        # Step 2: Check current state
        if task.completed:
            session.close()
            return {
                "error": "invalid_state",
                "message": "Task is already completed",
                "status": "error"
            }

        # Step 3: Update both fields together (atomic)
        task.completed = True
        task.completed_at = datetime.utcnow()
        session.add(task)

        # Step 4: Commit both updates together
        session.commit()
        session.refresh(task)

        return {
            "task_id": str(task.id),
            "status": "completed",
            "completed_at": task.completed_at.isoformat()
        }

    except Exception:
        session.rollback()
        return {"error": "database_error", "status": "error"}
    finally:
        session.close()
```

### Savepoint Pattern (Optional for Complex Operations)

```python
async def update_task(user_id: str, task_id: str, **updates):
    """
    Complex update with savepoints for error recovery
    """
    session = SessionLocal()
    try:
        # Find task
        task = session.exec(
            select(Task).where(
                (Task.id == task_id) & (Task.user_id == user_id)
            )
        ).first()

        if not task:
            return {"error": "task_not_found", "status": "error"}

        # Create savepoint before risky operations
        savepoint = session.begin_nested()

        try:
            # Apply updates
            for key, value in updates.items():
                if hasattr(task, key):
                    setattr(task, key, value)

            task.updated_at = datetime.utcnow()
            session.add(task)

            # Commit savepoint
            savepoint.commit()

            # Commit main transaction
            session.commit()
            session.refresh(task)

            return {"status": "updated", "task_id": str(task.id)}

        except Exception as inner_error:
            # Rollback just the savepoint, not entire transaction
            savepoint.rollback()
            raise inner_error

    except Exception:
        session.rollback()
        return {"error": "database_error", "status": "error"}
    finally:
        session.close()
```

---

## 3. Conversation History Retrieval

### Load Conversation Context

```python
from app.models import Conversation, Message

async def get_conversation_context(
    user_id: str,
    conversation_id: str,
    limit: int = 50
) -> List[Dict[str, Any]]:
    """
    Retrieve conversation history for AI agent context.
    Stateless: Creates session, loads history, closes.
    """
    session = SessionLocal()

    try:
        # Query messages ordered by creation time (oldest first)
        messages = session.exec(
            select(Message)
            .where(
                (Message.conversation_id == conversation_id) &
                (Message.user_id == user_id)
            )
            .order_by(Message.created_at.asc())
            .limit(limit)
        ).all()

        # Convert to dicts for agent context
        context = [
            {
                "role": msg.role,  # "user" or "assistant"
                "content": msg.content,
                "created_at": msg.created_at.isoformat()
            }
            for msg in messages
        ]

        return context

    except Exception as e:
        print(f"Error loading conversation context: {e}")
        return []

    finally:
        session.close()
```

### Store New Message

```python
async def store_message(
    user_id: str,
    conversation_id: str,
    role: str,  # "user" or "assistant"
    content: str
) -> Optional[str]:
    """
    Add message to conversation history.
    Stateless: Creates session, stores message, closes.
    """
    session = SessionLocal()

    try:
        message = Message(
            user_id=user_id,
            conversation_id=conversation_id,
            role=role,
            content=content,
            created_at=datetime.utcnow()
        )

        session.add(message)
        session.commit()
        session.refresh(message)

        return str(message.id)

    except Exception as e:
        session.rollback()
        print(f"Error storing message: {e}")
        return None

    finally:
        session.close()
```

---

## 4. Database Schema Design

### Conversation & Message Tables (Phase 3 Extensions)

```python
# app/models/conversation.py

from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import Optional, List
import uuid

class Conversation(SQLModel, table=True):
    """Chat conversation session"""
    __tablename__ = "conversations"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="users.id", index=True, nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    # Relationships
    messages: List["Message"] = Relationship(back_populates="conversation")

    # Index for fast lookups by user_id
    __table_args__ = (
        Index("idx_conversations_user_id", "user_id"),
    )


class Message(SQLModel, table=True):
    """Chat message history (immutable)"""
    __tablename__ = "messages"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="users.id", index=True, nullable=False)
    conversation_id: uuid.UUID = Field(
        foreign_key="conversations.id",
        index=True,
        nullable=False
    )
    role: str = Field(
        default="user",  # "user" or "assistant"
        nullable=False,
        index=True
    )
    content: str = Field(nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False, index=True)

    # Relationships
    conversation: Conversation = Relationship(back_populates="messages")

    # Composite index for fast conversation history retrieval
    __table_args__ = (
        Index("idx_messages_conversation_created", "conversation_id", "created_at"),
        Index("idx_messages_user_conversation", "user_id", "conversation_id"),
    )
```

### Database Indexes for Performance

| Index | Columns | Purpose |
|-------|---------|---------|
| **conversations_user_id** | conversations(user_id) | Fast user lookup |
| **messages_conversation_created** | messages(conversation_id, created_at) | Fast history retrieval ordered by time |
| **messages_user_conversation** | messages(user_id, conversation_id) | User-scoped conversation queries |
| **tasks_user_id** | tasks(user_id) | Fast task list filtering |
| **tasks_user_completed** | tasks(user_id, completed) | Filter by status |

---

## 5. Alembic Database Migrations

### Migration Script Template

```python
# alembic/versions/003_add_conversation_tables.py

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import uuid

def upgrade():
    """Add conversation and message tables for Phase 3"""

    # Create conversations table
    op.create_table(
        'conversations',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )

    # Create index
    op.create_index('idx_conversations_user_id', 'conversations', ['user_id'])

    # Create messages table
    op.create_table(
        'messages',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('conversation_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('conversations.id'), nullable=False),
        sa.Column('role', sa.String(), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )

    # Create indexes
    op.create_index('idx_messages_conversation_created', 'messages', ['conversation_id', 'created_at'])
    op.create_index('idx_messages_user_conversation', 'messages', ['user_id', 'conversation_id'])
    op.create_index('idx_messages_user_id', 'messages', ['user_id'])


def downgrade():
    """Rollback conversation tables"""
    op.drop_index('idx_messages_user_conversation')
    op.drop_index('idx_messages_conversation_created')
    op.drop_index('idx_messages_user_id')
    op.drop_table('messages')

    op.drop_index('idx_conversations_user_id')
    op.drop_table('conversations')
```

---

## 6. Error Recovery Patterns

### Connection Timeout Retry

```python
import time
from sqlalchemy.exc import OperationalError

async def list_tasks_with_retry(
    user_id: str,
    max_retries: int = 3
) -> Dict[str, Any]:
    """
    List tasks with automatic retry on connection failure.
    Useful for Neon connection pool exhaustion.
    """
    for attempt in range(max_retries):
        session = SessionLocal()

        try:
            tasks = session.exec(
                select(Task).where(Task.user_id == user_id)
            ).all()

            return {
                "tasks": [
                    {
                        "task_id": str(t.id),
                        "title": t.title,
                        "completed": t.completed
                    }
                    for t in tasks
                ],
                "status": "success"
            }

        except OperationalError as e:
            session.rollback()

            if attempt < max_retries - 1:
                # Exponential backoff: 100ms, 200ms, 400ms
                wait_time = 0.1 * (2 ** attempt)
                print(f"Retry {attempt + 1}/{max_retries}, waiting {wait_time}s")
                time.sleep(wait_time)
                continue
            else:
                # Final failure
                return {
                    "error": "database_error",
                    "message": "Database temporarily unavailable. Please try again.",
                    "status": "error"
                }

        except Exception as e:
            session.rollback()
            return {
                "error": "database_error",
                "message": str(e),
                "status": "error"
            }

        finally:
            session.close()

    return {"error": "database_error", "status": "error"}
```

### Conflict Resolution (Optimistic Locking)

```python
from sqlalchemy import __version__

class Task(SQLModel, table=True):
    """Task model with version for optimistic locking"""
    __tablename__ = "tasks"

    id: uuid.UUID = Field(primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="users.id", index=True)
    title: str
    version: int = Field(default=0)  # Increment on every update


async def update_task_with_conflict_detection(
    user_id: str,
    task_id: str,
    new_title: str,
    current_version: int
):
    """
    Update task only if version hasn't changed (no concurrent modification).
    """
    session = SessionLocal()

    try:
        task = session.exec(
            select(Task).where(
                (Task.id == task_id) & (Task.user_id == user_id)
            )
        ).first()

        if not task:
            return {"error": "task_not_found"}

        if task.version != current_version:
            return {
                "error": "conflict",
                "message": "Task was modified by another request",
                "current_version": task.version
            }

        # Update and increment version
        task.title = new_title
        task.version += 1
        session.add(task)
        session.commit()
        session.refresh(task)

        return {
            "status": "updated",
            "version": task.version
        }

    except Exception:
        session.rollback()
        return {"error": "database_error"}

    finally:
        session.close()
```

---

## 7. Pagination for Large Datasets

```python
async def list_tasks_paginated(
    user_id: str,
    page: int = 1,
    limit: int = 20
) -> Dict[str, Any]:
    """
    List tasks with pagination (for large message histories).
    Stateless: Each request loads only required page.
    """
    session = SessionLocal()

    try:
        # Count total
        total = session.exec(
            select(func.count(Task.id)).where(Task.user_id == user_id)
        ).one()

        # Calculate offset
        offset = (page - 1) * limit

        # Fetch page
        tasks = session.exec(
            select(Task)
            .where(Task.user_id == user_id)
            .order_by(Task.created_at.desc())
            .offset(offset)
            .limit(limit)
        ).all()

        total_pages = (total + limit - 1) // limit

        return {
            "tasks": [
                {
                    "task_id": str(t.id),
                    "title": t.title,
                    "completed": t.completed
                }
                for t in tasks
            ],
            "pagination": {
                "page": page,
                "limit": limit,
                "total": total,
                "pages": total_pages
            },
            "status": "success"
        }

    except Exception as e:
        return {
            "error": "database_error",
            "message": str(e),
            "status": "error"
        }

    finally:
        session.close()
```

---

## 8. Performance Optimization

### Query Optimization Checklist

- ✅ **Use indexes** for WHERE clauses (user_id, task_id, conversation_id)
- ✅ **Limit result sets** with LIMIT clause
- ✅ **Pagination** for large tables (messages, tasks)
- ✅ **Composite indexes** for multi-column filters
- ✅ **Connection pooling** (pool_size=5, max_overflow=10)
- ✅ **Connection reuse** via SQLModel session
- ✅ **Lazy loading prevention** (eager load relationships if needed)

### Query Analysis Example

```python
# SLOW: No index, full table scan
tasks = session.exec(select(Task)).all()  # ❌ O(n) - scans all tasks

# FAST: Indexed column, direct lookup
tasks = session.exec(select(Task).where(Task.user_id == user_id)).all()  # ✅ O(log n)

# SLOWER: Multiple queries (N+1 problem)
for task in tasks:
    user = session.exec(select(User).where(User.id == task.user_id)).first()  # ❌ N+1

# FASTER: Single query with relationship
tasks_with_users = session.exec(
    select(Task)
    .options(joinedload(Task.user))
    .where(Task.user_id == user_id)
).unique().all()  # ✅ Single query
```

---

## 9. State Lifecycle Documentation

### Per-Request State Flow

```
Request arrives at server
    ↓
Dependency injection provides SQLModel session (from pool)
    ↓
Tool function executes:
    - Fetch data from database
    - Process data
    - Store results in database
    ↓
Session committed or rolled back
    ↓
Session explicitly closed (returned to pool)
    ↓
Response returned to client
    ↓
⚠️ Server has NO state about request or data
✅ All state is in database
```

### Conversation Context Lifecycle

```
User sends message with conversation_id
    ↓
Server creates new session
    ↓
Load conversation history from Message table (ordered by created_at)
    ↓
Provide history to AI agent as context
    ↓
Agent calls MCP tools (each tool creates its own session)
    ↓
Store AI response as new Message (role="assistant")
    ↓
Close session
    ↓
Return response to client
    ↓
Next request loads full history again (from database, not memory)
✅ Conversation persists across server restarts
```

---

## 10. Monitoring & Debugging

### Connection Pool Monitoring

```python
from sqlalchemy import event
from sqlalchemy.pool import Pool

@event.listens_for(Pool, "connect")
def receive_connect(dbapi_conn, connection_record):
    print(f"Connection opened: {id(dbapi_conn)}")

@event.listens_for(Pool, "checkin")
def receive_checkin(dbapi_conn, connection_record):
    print(f"Connection returned to pool: {id(dbapi_conn)}")

@event.listens_for(Pool, "checkout")
def receive_checkout(dbapi_conn, connection_record, connection_proxy):
    print(f"Connection checked out from pool: {id(dbapi_conn)}")
```

### Query Logging

```python
import logging

logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

# Now all SQL queries will be logged
```

---

## Integration with MCP Server Builder Agent

This skill works with mcp-server-builder to:
- Design stateless tool session management
- Create database migration scripts
- Optimize query strategies with indexes
- Implement transaction safety
- Handle error recovery gracefully
- Store and retrieve conversation context

**Workflow:**
```
1. Agent uses Tool Definition skill to design tools
2. Agent uses this skill to plan stateless persistence
3. Agent creates database migrations
4. Agent implements session management per tool
5. Agent verifies no server-side state is retained
6. Agent implements error recovery patterns
```

---

## Related Skills & Agents

- **Agent:** mcp-server-builder (primary user)
- **Skill:** MCP Tool Definition & Schema Validation (tool specs)
- **Skill:** MCP Tool Security & Integration Testing (test validation)
- **ORM:** SQLModel with Neon PostgreSQL

---

## Key Takeaway

**Stateless = Scalable + Resilient + Maintainable**

Every MCP tool follows this pattern:
1. Create session (fresh per request)
2. Execute operation
3. Commit/Rollback
4. Close session
5. Return response

Result: Horizontally scalable, fault-tolerant, conversation-persistent application.

