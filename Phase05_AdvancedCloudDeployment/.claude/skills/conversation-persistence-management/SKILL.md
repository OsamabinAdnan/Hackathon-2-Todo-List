---
name: conversation-persistence-management
description: "Manage conversation and message persistence for stateless chat endpoints with SQLModel models, atomic transactions, multi-user isolation, and race condition prevention. Use when: (1) designing Conversation/Message database schemas from @specs/database/schema.md, (2) implementing message storage operations (store user message, fetch history, store AI response), (3) managing database transactions with automatic rollback, (4) implementing pagination and token estimation for conversation history, (5) enforcing per-query user_id filtering for multi-user isolation, (6) preventing race conditions with row-level locking or optimistic versioning, (7) optimizing queries with proper indexing strategies."
---

# Conversation Persistence Management

## Core Responsibility

Implement production-grade database persistence for the stateless chat endpoint:
1. Define Conversation and Message SQLModel schemas with proper constraints
2. Store user messages and AI responses atomically
3. Retrieve conversation history with pagination and token filtering
4. Prevent cross-user access with user_id-scoped queries
5. Handle race conditions in concurrent scenarios
6. Manage connection pool and optimize query performance
7. Support conversation lifecycle (create, resume, stale detection)

## Quick Start: Database Schema

### Conversation Model
```python
- id: UUID (PK)
- user_id: UUID (FK to users.id, NOT NULL)
- created_at: datetime
- updated_at: datetime
- indexes: (user_id), (user_id, created_at)
- on_delete: CASCADE
```

### Message Model
```python
- id: UUID (PK)
- conversation_id: UUID (FK to conversations.id, NOT NULL)
- role: str (enum: "user", "assistant")
- content: str (up to 10,000 chars)
- tool_calls: JSON (optional, array of tool invocations)
- created_at: datetime
- indexes: (conversation_id), (conversation_id, created_at), (created_at)
```

## Section 1: SQLModel Schemas

Define Conversation and Message tables with proper constraints and indexes. See `references/sqlmodel-schemas.md`.

### Conversation Table
```python
class Conversation(SQLModel, table=True):
    __tablename__ = "conversations"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id", nullable=False, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    # Indexes
    __table_args__ = (
        Index("idx_conversations_user_id", "user_id"),
        Index("idx_conversations_user_created", "user_id", "created_at"),
    )
```

### Message Table
```python
class Message(SQLModel, table=True):
    __tablename__ = "messages"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    conversation_id: UUID = Field(
        foreign_key="conversations.id",
        nullable=False,
        index=True
    )
    role: str = Field(nullable=False)  # "user" or "assistant"
    content: str = Field(max_length=10000, nullable=False)
    tool_calls: Optional[list] = Field(default=None)  # JSON serialized
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    # Indexes
    __table_args__ = (
        Index("idx_messages_conversation_id", "conversation_id"),
        Index("idx_messages_conversation_created", "conversation_id", "created_at"),
        Index("idx_messages_created_at", "created_at"),
    )
```

## Section 2: Atomic Message Storage

Store messages with automatic transaction management and rollback.

### Store User Message
```python
async def store_user_message(
    session: AsyncSession,
    conversation_id: UUID,
    user_id: str,
    message_text: str,
    trace_id: str
) → UUID:
    """
    Persist user message atomically. Verify user owns conversation first.

    Returns: message_id (UUID)
    Raises: 403 if user not authorized, 500 on database error
    """
    try:
        # Verify ownership
        conversation = await session.get(Conversation, conversation_id)
        if not conversation or conversation.user_id != user_id:
            raise ValueError("Unauthorized")

        # Create and store message
        message = Message(
            conversation_id=conversation_id,
            role="user",
            content=message_text,
            created_at=datetime.utcnow()
        )
        session.add(message)
        await session.flush()  # Get ID without committing

        message_id = message.id
        await session.commit()

        logger.info(f"User message stored", extra={
            "message_id": str(message_id),
            "conversation_id": str(conversation_id),
            "user_id": user_id,
            "trace_id": trace_id
        })

        return message_id

    except Exception as e:
        await session.rollback()
        logger.error(f"Failed to store user message: {e}", extra={"trace_id": trace_id})
        raise
```

### Store AI Response
```python
async def store_ai_response(
    session: AsyncSession,
    conversation_id: UUID,
    user_id: str,
    response_text: str,
    tool_calls: list[dict],
    trace_id: str
) → UUID:
    """
    Persist AI response with tool call metadata. Atomic with rollback.

    Returns: message_id
    Raises: 403 if unauthorized, 500 on database error
    """
    try:
        # Verify ownership
        conversation = await session.get(Conversation, conversation_id)
        if not conversation or conversation.user_id != user_id:
            raise ValueError("Unauthorized")

        # Create message with tool calls
        message = Message(
            conversation_id=conversation_id,
            role="assistant",
            content=response_text,
            tool_calls=tool_calls if tool_calls else None,
            created_at=datetime.utcnow()
        )
        session.add(message)
        await session.flush()

        message_id = message.id
        await session.commit()

        logger.info(f"AI response stored", extra={
            "message_id": str(message_id),
            "conversation_id": str(conversation_id),
            "tools_called": len(tool_calls),
            "trace_id": trace_id
        })

        return message_id

    except Exception as e:
        await session.rollback()
        logger.error(f"Failed to store AI response: {e}", extra={"trace_id": trace_id})
        raise
```

## Section 3: History Retrieval & Pagination

Fetch conversation history with user_id filtering, pagination, and token limits.

### Get Conversation History
```python
async def get_conversation_history(
    session: AsyncSession,
    conversation_id: UUID,
    user_id: str,
    limit: int = 50,
    offset: int = 0,
    trace_id: str = None
) → list[dict]:
    """
    Fetch conversation messages with pagination (chronological, oldest first).

    CRITICAL: Verify user owns conversation (return 403, never 404).

    Args:
        limit: Max messages (default 50, max 100)
        offset: Pagination offset (default 0)

    Returns: Messages [{role, content, tool_calls, created_at}, ...]
    Raises: 403 if user not authorized
    """
    try:
        # Verify ownership (CRITICAL for multi-user isolation)
        conversation = await session.exec(
            select(Conversation).where(
                Conversation.id == conversation_id,
                Conversation.user_id == user_id
            )
        ).first()

        if not conversation:
            logger.warn(f"Unauthorized history access", extra={
                "conversation_id": str(conversation_id),
                "user_id": user_id,
                "trace_id": trace_id
            })
            raise ValueError("Unauthorized")

        # Enforce pagination limits
        limit = min(limit, 100)

        # Fetch messages (chronological: oldest first)
        messages = await session.exec(
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.asc())
            .offset(offset)
            .limit(limit)
        ).all()

        result = [
            {
                "id": str(msg.id),
                "role": msg.role,
                "content": msg.content,
                "tool_calls": msg.tool_calls or [],
                "created_at": msg.created_at.isoformat()
            }
            for msg in messages
        ]

        logger.debug(f"History retrieved", extra={
            "conversation_id": str(conversation_id),
            "message_count": len(result),
            "offset": offset,
            "limit": limit,
            "trace_id": trace_id
        })

        return result

    except Exception as e:
        logger.error(f"Failed to retrieve history: {e}", extra={"trace_id": trace_id})
        raise
```

## Section 4: Token Estimation & Truncation

Estimate token usage and truncate history for context window limits.

### Token Counting
```python
import tiktoken

class TokenCounter:
    """Count tokens in messages for context window management"""

    def __init__(self):
        self.encoding = tiktoken.encoding_for_model("gpt-4")

    def count_tokens(self, text: str) -> int:
        """Count tokens in text using GPT-4 tokenizer"""
        return len(self.encoding.encode(text))

    def estimate_message_tokens(self, message: dict) -> int:
        """Estimate tokens for single message (content + role overhead)"""
        # Rough estimate: 1 token per 4 chars + 4 tokens for role/metadata
        content_tokens = self.count_tokens(message["content"])
        role_tokens = 4
        return content_tokens + role_tokens

    def estimate_total_tokens(self, messages: list[dict]) -> int:
        """Sum token estimates for all messages"""
        return sum(self.estimate_message_tokens(m) for m in messages)
```

### History Truncation
```python
async def truncate_history_for_context(
    messages: list[dict],
    max_tokens: int = 8000,
    reserve_tokens: int = 500,
    trace_id: str = None
) → list[dict]:
    """
    Truncate oldest messages to fit within token limit.
    Keep newest messages to preserve conversation context.

    Args:
        max_tokens: Total context window (default 8K)
        reserve_tokens: Tokens reserved for response (default 500)
        messages: Conversation history (chronological order)

    Returns: Truncated message list
    """
    token_counter = TokenCounter()
    available_tokens = max_tokens - reserve_tokens
    total_tokens = token_counter.estimate_total_tokens(messages)

    if total_tokens <= available_tokens:
        return messages

    # Remove oldest messages until within limit
    truncated = messages.copy()
    removed_count = 0

    while truncated and total_tokens > available_tokens:
        oldest = truncated.pop(0)
        total_tokens -= token_counter.estimate_message_tokens(oldest)
        removed_count += 1

    logger.info(f"History truncated", extra={
        "original_messages": len(messages),
        "truncated_messages": len(truncated),
        "removed": removed_count,
        "tokens_before": token_counter.estimate_total_tokens(messages),
        "tokens_after": total_tokens,
        "available_tokens": available_tokens,
        "trace_id": trace_id
    })

    return truncated
```

## Section 5: Multi-User Isolation

Enforce user_id filtering in ALL queries to prevent cross-user access.

### Parameterized Queries (Prevent Injection)
```python
# ✅ SAFE: Parameterized query
async def get_user_conversations(
    session: AsyncSession,
    user_id: str
) → list[Conversation]:
    """Fetch user's conversations (parameterized, safe)"""
    result = await session.exec(
        select(Conversation).where(Conversation.user_id == user_id)
    ).all()
    return result

# ❌ UNSAFE: String concatenation (never do this)
# query = f"SELECT * FROM conversations WHERE user_id = {user_id}"  # SQL INJECTION!
```

### Critical Checks
```python
# ALWAYS verify ownership before returning data
async def get_message_safe(session, message_id: UUID, user_id: str):
    """Get message with ownership verification"""
    message = await session.get(Message, message_id)

    if not message:
        return None  # Return None, not 404 (prevent enumeration)

    # Fetch conversation to verify ownership
    conversation = await session.get(Conversation, message.conversation_id)

    if not conversation or conversation.user_id != user_id:
        raise PermissionError("Access denied")

    return message
```

## Section 6: Race Condition Prevention

Handle concurrent requests from same user to same conversation.

### Optimistic Locking (Version Column)
```python
class Conversation(SQLModel, table=True):
    id: UUID = Field(primary_key=True)
    user_id: UUID = Field(foreign_key="users.id")
    version: int = Field(default=1)  # Increment on update
    created_at: datetime
    updated_at: datetime

async def update_conversation_safe(
    session: AsyncSession,
    conversation_id: UUID,
    user_id: str,
    expected_version: int
) → bool:
    """
    Update conversation only if version matches (optimistic locking).
    Prevents lost updates in concurrent scenarios.
    """
    conversation = await session.get(Conversation, conversation_id)

    if not conversation or conversation.user_id != user_id:
        raise PermissionError("Access denied")

    if conversation.version != expected_version:
        raise ValueError("Conflict: conversation modified by another request")

    # Update and increment version
    conversation.updated_at = datetime.utcnow()
    conversation.version += 1

    await session.commit()
    return True
```

### Row-Level Locking (PostgreSQL)
```python
from sqlalchemy import text

async def get_conversation_for_update(
    session: AsyncSession,
    conversation_id: UUID,
    user_id: str
) → Conversation:
    """
    Fetch conversation with row-level lock (PostgreSQL FOR UPDATE).
    Prevents concurrent modifications.
    """
    result = await session.execute(
        select(Conversation)
        .where(
            Conversation.id == conversation_id,
            Conversation.user_id == user_id
        )
        .with_for_update()  # Row-level lock
    )

    conversation = result.scalar_one_or_none()
    if not conversation:
        raise PermissionError("Access denied")

    return conversation
```

## Section 7: Connection Pool Optimization

Manage database connection pool for performance and reliability.

### Connection Pool Configuration
```python
from sqlalchemy.ext.asyncio import create_async_engine

engine = create_async_engine(
    f"postgresql+asyncpg://{user}:{password}@{host}/{db}",
    echo=False,
    pool_size=5,              # Min connections in pool
    max_overflow=10,          # Max additional connections
    pool_timeout=30,          # Timeout for acquiring connection
    pool_recycle=3600,        # Recycle connections after 1 hour
    pool_pre_ping=True,       # Verify connection before use
    connect_args={
        "timeout": 10,
        "command_timeout": 10,
        "server_settings": {
            "application_name": "chat_service"
        }
    }
)
```

### Stale Conversation Detection
```python
from datetime import timedelta

async def cleanup_stale_conversations(
    session: AsyncSession,
    stale_days: int = 30,
    trace_id: str = None
):
    """
    Detect and potentially archive conversations older than 30 days.

    Option 1: Soft flag (add is_archived: bool)
    Option 2: Return metadata for client-side filtering
    """
    stale_threshold = datetime.utcnow() - timedelta(days=stale_days)

    stale = await session.exec(
        select(Conversation).where(
            Conversation.updated_at < stale_threshold
        )
    ).all()

    logger.info(f"Stale conversations detected", extra={
        "count": len(stale),
        "threshold_days": stale_days,
        "trace_id": trace_id
    })

    return stale
```

---

## References

See bundled reference files for implementation details:
- **sqlmodel-schemas.md** - Complete Conversation/Message SQLModel definitions with constraints
- **query-patterns.md** - Efficient query patterns with pagination, filtering, and optimization
- **transaction-safety.md** - ACID transaction management and error handling patterns
