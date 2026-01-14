# Database Schema: AI-Powered Todo Chatbot Integration

**Database**: Neon Serverless PostgreSQL
**ORM**: SQLModel (Python)
**Version**: 1.0.0
**Last Updated**: 2026-01-13

---

## Overview

The database schema extends the existing Phase 2 schema with conversation and message tables to support the AI chatbot functionality. All existing task and user data remains unchanged, maintaining compatibility with Phase 2 features.

**Design Principles:**
- User isolation enforced at database level (foreign keys, parameterized queries)
- Conversation and message history persistence for multi-turn AI context
- Timestamps for all entities (created_at, updated_at)
- UUID primary keys for security (non-sequential IDs)
- Proper indexing for query performance
- Immutable message history (no updates to existing messages)

---

## Entity Relationship Diagram

```
┌─────────────────┐
│     users       │
│─────────────────│
│ id (PK, UUID)   │
│ email (UNIQUE)  │
│ password_hash   │
│ name            │
│ created_at      │
│ updated_at      │
│ last_login_at   │
└────────┬────────┘
         │ 1
         │
         │ N
┌────────┴────────────┐
│       tasks         │
│─────────────────────│
│ id (PK, UUID)       │
│ user_id (FK)        │◄─── Foreign key to users.id
│ title               │
│ description         │
│ completed           │
│ priority            │
│ tags[]              │
│ due_date            │
│ is_recurring        │
│ recurrence_pattern  │
│ created_at          │
│ updated_at          │
│ completed_at        │
└─────────────────────┘

┌─────────────────────┐
│   conversations     │
│─────────────────────│
│ id (PK, UUID)       │
│ user_id (FK)        │◄─── Foreign key to users.id
│ title (optional)    │
│ created_at          │
│ updated_at          │
│ last_message_at     │
└────────┬────────────┘
         │ 1
         │
         │ N
┌────────┴────────────┐
│     messages        │
│─────────────────────│
│ id (PK, UUID)       │
│ conversation_id (FK)│◄─── Foreign key to conversations.id
│ user_id (FK)        │◄─── Foreign key to users.id (for isolation)
│ role (enum)         │◄─── 'user' or 'assistant'
│ content (text)      │
│ tool_calls (jsonb)  │◄─── JSON array of tool calls made
│ created_at          │
└─────────────────────┘
```

---

## Tables

### 1. `conversations` (New for Phase 3)

Stores chat session information and metadata.

**Table Name**: `conversations`

**Columns:**

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | UUID | PRIMARY KEY, DEFAULT gen_random_uuid() | Unique conversation identifier |
| `user_id` | UUID | NOT NULL, FOREIGN KEY → users(id) ON DELETE CASCADE | Owner of the conversation |
| `title` | VARCHAR(200) | NULL | Auto-generated title from first message or user-provided |
| `created_at` | TIMESTAMP WITH TIME ZONE | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Conversation creation timestamp |
| `updated_at` | TIMESTAMP WITH TIME ZONE | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Last update timestamp |
| `last_message_at` | TIMESTAMP WITH TIME ZONE | NULL | Timestamp of last message in conversation |

**Indexes:**
```sql
CREATE INDEX idx_conversations_user_id ON conversations(user_id);
CREATE INDEX idx_conversations_created_at ON conversations(created_at);
CREATE INDEX idx_conversations_last_message_at ON conversations(last_message_at);
```

**SQLModel Definition:**
```python
from sqlmodel import Field, SQLModel
from datetime import datetime
from typing import Optional
import uuid

class Conversation(SQLModel, table=True):
    __tablename__ = "conversations"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="users.id", nullable=False, index=True)
    title: Optional[str] = Field(default=None, max_length=200)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False, index=True)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    last_message_at: Optional[datetime] = Field(default=None, index=True)
```

**Security Notes:**
- `user_id` foreign key ensures conversations are tied to authenticated users
- All queries must filter by `user_id` for proper isolation
- `ON DELETE CASCADE` removes conversations when user is deleted

---

### 2. `messages` (New for Phase 3)

Stores individual chat messages (both user input and AI responses) with tool execution context.

**Table Name**: `messages`

**Columns:**

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | UUID | PRIMARY KEY, DEFAULT gen_random_uuid() | Unique message identifier |
| `conversation_id` | UUID | NOT NULL, FOREIGN KEY → conversations(id) ON DELETE CASCADE | Conversation this message belongs to |
| `user_id` | UUID | NOT NULL, FOREIGN KEY → users(id) | User who owns this conversation (for isolation) |
| `role` | VARCHAR(20) | NOT NULL | Message role: 'user' or 'assistant' |
| `content` | TEXT | NOT NULL | Message content (user input or AI response) |
| `tool_calls` | JSONB | NULL | JSON array of tools called during this message's processing |
| `created_at` | TIMESTAMP WITH TIME ZONE | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Message creation timestamp |

**Indexes:**
```sql
CREATE INDEX idx_messages_conversation_id ON messages(conversation_id);
CREATE INDEX idx_messages_user_id ON messages(user_id);
CREATE INDEX idx_messages_role ON messages(role);
CREATE INDEX idx_messages_created_at ON messages(created_at);
CREATE INDEX idx_messages_conversation_created ON messages(conversation_id, created_at);
```

**Foreign Key Constraints:**
```sql
ALTER TABLE messages
ADD CONSTRAINT fk_messages_conversation_id
FOREIGN KEY (conversation_id)
REFERENCES conversations(id)
ON DELETE CASCADE;

ALTER TABLE messages
ADD CONSTRAINT fk_messages_user_id
FOREIGN KEY (user_id)
REFERENCES users(id)
ON DELETE CASCADE;
```

**SQLModel Definition:**
```python
from sqlmodel import Field, SQLModel
from sqlalchemy import JSON
from datetime import datetime
from typing import Optional, List, Dict, Any
import uuid

class Message(SQLModel, table=True):
    __tablename__ = "messages"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    conversation_id: uuid.UUID = Field(foreign_key="conversations.id", nullable=False, index=True)
    user_id: uuid.UUID = Field(foreign_key="users.id", nullable=False, index=True)
    role: str = Field(max_length=20, nullable=False, index=True)  # 'user' or 'assistant'
    content: str = Field(nullable=False)  # Message content
    tool_calls: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSON))  # Tool execution details
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False, index=True)
```

**Indexing Strategy:**
- `conversation_id`: Fast retrieval of messages within a conversation
- `user_id`: User isolation filtering
- `role`: Filter user vs assistant messages
- `created_at`: Chronological ordering
- `(conversation_id, created_at)`: Composite index for conversation history queries

---

## Database Migrations

### Migration for Phase 3 (Chatbot Tables)

**File**: `backend/migrations/002_chatbot_tables.sql`

```sql
-- Create conversations table
CREATE TABLE conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(200),
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_message_at TIMESTAMP WITH TIME ZONE
);

-- Create indexes on conversations
CREATE INDEX idx_conversations_user_id ON conversations(user_id);
CREATE INDEX idx_conversations_created_at ON conversations(created_at);
CREATE INDEX idx_conversations_last_message_at ON conversations(last_message_at);

-- Create messages table
CREATE TABLE messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL,
    content TEXT NOT NULL,
    tool_calls JSONB,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes on messages
CREATE INDEX idx_messages_conversation_id ON messages(conversation_id);
CREATE INDEX idx_messages_user_id ON messages(user_id);
CREATE INDEX idx_messages_role ON messages(role);
CREATE INDEX idx_messages_created_at ON messages(created_at);
CREATE INDEX idx_messages_conversation_created ON messages(conversation_id, created_at);

-- Create updated_at trigger function (if not exists)
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply updated_at trigger to conversations
CREATE TRIGGER update_conversations_updated_at BEFORE UPDATE ON conversations
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
```

---

## Query Examples

### Get conversation history for AI context
```sql
SELECT role, content, tool_calls, created_at
FROM messages
WHERE conversation_id = '6ba7b810-9dad-11d1-80b4-00c04fd430c8'
  AND user_id = '550e8400-e29b-41d4-a716-446655440000'
ORDER BY created_at ASC;
```

### Get recent conversations for a user
```sql
SELECT id, title, last_message_at, created_at
FROM conversations
WHERE user_id = '550e8400-e29b-41d4-a716-446655440000'
ORDER BY last_message_at DESC NULLS LAST, created_at DESC
LIMIT 10;
```

### Add a new message to conversation
```sql
INSERT INTO messages (conversation_id, user_id, role, content, tool_calls)
VALUES (
    '6ba7b810-9dad-11d1-80b4-00c04fd430c8',
    '550e8400-e29b-41d4-a716-446655440000',
    'user',
    'Add a task to buy groceries',
    NULL
);
```

### Update conversation's last message timestamp
```sql
UPDATE conversations
SET last_message_at = CURRENT_TIMESTAMP,
    updated_at = CURRENT_TIMESTAMP
WHERE id = '6ba7b810-9dad-11d1-80b4-00c04fd430c8'
  AND user_id = '550e8400-e29b-41d4-a716-446655440000';
```

---

## Performance Optimization

### Query Performance
- All user-scoped queries use `user_id` index for isolation
- Conversation history queries use composite index `(conversation_id, created_at)`
- Messages are stored with chronological ordering for efficient retrieval

### Connection Pooling
- Use SQLAlchemy connection pool (default: 5 connections, max: 20)
- Neon serverless auto-scales connections

### Pagination
- Fetch messages in batches of 20-50 for conversation history
- Use `LIMIT` and `OFFSET` or cursor-based pagination
- Consider token counting for AI context window management

---

## Security Considerations

1. **User Isolation**: All queries MUST filter by both `user_id` and `conversation_id` from JWT token
2. **Message Immutability**: Messages are never updated after creation, only appended
3. **Tool Call Security**: Tool call data is stored but validated before execution
4. **SQL Injection**: Use parameterized queries (SQLModel handles this)
5. **Connection Security**: Always use SSL (`sslmode=require` in connection string)
6. **Secrets Management**: Store `DATABASE_URL` in environment variables, never commit to git

---

## Integration with Existing Schema

The new tables integrate seamlessly with the existing Phase 2 schema:
- `user_id` foreign keys maintain user isolation across all tables
- Existing `tasks` table remains unchanged and is accessed via MCP tools
- Authentication and user management remain the same as Phase 2
- All existing API endpoints continue to function unchanged

---

**Version**: 1.0.0
**Last Updated**: 2026-01-13
**Owner**: Phase 3 Development Team