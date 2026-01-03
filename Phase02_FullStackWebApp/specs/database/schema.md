# Database Schema Specification

**Database**: Neon Serverless PostgreSQL
**ORM**: SQLModel (Python)
**Version**: 1.0.0
**Last Updated**: 2026-01-02

---

## Overview

The database schema supports a multi-user Todo application with strict user isolation. All data access is scoped by `user_id` to ensure users can only access their own data.

**Design Principles:**
- User isolation enforced at database level (foreign keys, row-level security)
- Timestamps for all entities (created_at, updated_at)
- UUID primary keys for security (non-sequential IDs)
- Proper indexing for query performance
- Soft delete not used (hard delete for simplicity)

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

Optional (Token Revocation):
┌─────────────────────┐
│  revoked_tokens     │
│─────────────────────│
│ token_hash (PK)     │
│ revoked_at          │
│ expires_at          │
└─────────────────────┘
```

---

## Tables

### 1. `users`

Stores user account information. Managed by Better Auth but with custom fields.

**Table Name**: `users`

**Columns:**

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | UUID | PRIMARY KEY, DEFAULT gen_random_uuid() | Unique user identifier |
| `email` | VARCHAR(255) | NOT NULL, UNIQUE | User email address (login identifier) |
| `password_hash` | VARCHAR(255) | NOT NULL | bcrypt/argon2 hashed password |
| `name` | VARCHAR(100) | NOT NULL | User display name |
| `created_at` | TIMESTAMP WITH TIME ZONE | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Account creation timestamp |
| `updated_at` | TIMESTAMP WITH TIME ZONE | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Last profile update timestamp |
| `last_login_at` | TIMESTAMP WITH TIME ZONE | NULL | Last successful login timestamp |

**Indexes:**
```sql
CREATE UNIQUE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_created_at ON users(created_at);
```

**SQLModel Definition:**
```python
from sqlmodel import Field, SQLModel
from datetime import datetime
from typing import Optional
import uuid

class User(SQLModel, table=True):
    __tablename__ = "users"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    email: str = Field(max_length=255, unique=True, index=True, nullable=False)
    password_hash: str = Field(max_length=255, nullable=False)
    name: str = Field(max_length=100, nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    last_login_at: Optional[datetime] = None
```

**Security Notes:**
- `password_hash` is NEVER returned in API responses
- Email uniqueness enforced at database level (prevents race conditions)
- Timestamps use UTC timezone

---

### 2. `tasks`

Stores user tasks with all Level 1, 2, and 3 features.

**Table Name**: `tasks`

**Columns:**

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | UUID | PRIMARY KEY, DEFAULT gen_random_uuid() | Unique task identifier |
| `user_id` | UUID | NOT NULL, FOREIGN KEY → users(id) ON DELETE CASCADE | Owner of the task |
| `title` | VARCHAR(200) | NOT NULL | Task title (1-200 chars) |
| `description` | TEXT | NULL | Task description (max 1000 chars, enforced at app level) |
| `completed` | BOOLEAN | NOT NULL, DEFAULT FALSE | Completion status |
| `priority` | VARCHAR(10) | NOT NULL, DEFAULT 'NONE' | Priority level: HIGH, MEDIUM, LOW, NONE |
| `tags` | TEXT[] | DEFAULT '{}' | Array of tags (lowercase, max 10 tags) |
| `due_date` | TIMESTAMP WITH TIME ZONE | NULL | Due date with time (optional) |
| `is_recurring` | BOOLEAN | NOT NULL, DEFAULT FALSE | Whether task repeats |
| `recurrence_pattern` | VARCHAR(10) | NULL | Recurrence: DAILY, WEEKLY, MONTHLY |
| `created_at` | TIMESTAMP WITH TIME ZONE | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Task creation timestamp |
| `updated_at` | TIMESTAMP WITH TIME ZONE | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Last update timestamp |
| `completed_at` | TIMESTAMP WITH TIME ZONE | NULL | Completion timestamp |

**Indexes:**
```sql
CREATE INDEX idx_tasks_user_id ON tasks(user_id);
CREATE INDEX idx_tasks_completed ON tasks(completed);
CREATE INDEX idx_tasks_due_date ON tasks(due_date) WHERE due_date IS NOT NULL;
CREATE INDEX idx_tasks_priority ON tasks(priority);
CREATE INDEX idx_tasks_created_at ON tasks(created_at);
CREATE INDEX idx_tasks_user_completed ON tasks(user_id, completed);
CREATE INDEX idx_tasks_tags ON tasks USING GIN(tags);
```

**Foreign Key Constraint:**
```sql
ALTER TABLE tasks
ADD CONSTRAINT fk_tasks_user_id
FOREIGN KEY (user_id)
REFERENCES users(id)
ON DELETE CASCADE;
```

**Check Constraints:**
```sql
-- Priority must be one of the valid values
ALTER TABLE tasks
ADD CONSTRAINT check_priority
CHECK (priority IN ('HIGH', 'MEDIUM', 'LOW', 'NONE'));

-- Recurrence pattern must be valid if recurring is true
ALTER TABLE tasks
ADD CONSTRAINT check_recurrence_pattern
CHECK (
    (is_recurring = FALSE AND recurrence_pattern IS NULL) OR
    (is_recurring = TRUE AND recurrence_pattern IN ('DAILY', 'WEEKLY', 'MONTHLY'))
);

-- Recurring tasks must have a due date
ALTER TABLE tasks
ADD CONSTRAINT check_recurring_due_date
CHECK (
    (is_recurring = FALSE) OR
    (is_recurring = TRUE AND due_date IS NOT NULL)
);
```

**SQLModel Definition:**
```python
from sqlmodel import Field, SQLModel, Column
from sqlalchemy import ARRAY, String, DateTime
from datetime import datetime
from typing import Optional, List
from enum import Enum
import uuid

class Priority(str, Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    NONE = "NONE"

class RecurrencePattern(str, Enum):
    DAILY = "DAILY"
    WEEKLY = "WEEKLY"
    MONTHLY = "MONTHLY"

class Task(SQLModel, table=True):
    __tablename__ = "tasks"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="users.id", nullable=False, index=True)
    title: str = Field(max_length=200, nullable=False)
    description: Optional[str] = Field(default=None, max_length=1000)
    completed: bool = Field(default=False, nullable=False, index=True)
    priority: Priority = Field(default=Priority.NONE, nullable=False, index=True)
    tags: List[str] = Field(default_factory=list, sa_column=Column(ARRAY(String)))
    due_date: Optional[datetime] = Field(default=None, index=True)
    is_recurring: bool = Field(default=False, nullable=False)
    recurrence_pattern: Optional[RecurrencePattern] = None
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False, index=True)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    completed_at: Optional[datetime] = None
```

**Indexing Strategy:**
- `user_id`: Fast filtering by user (most common query)
- `completed`: Filter active vs completed tasks
- `due_date`: Sort by due date, find overdue/due-soon tasks
- `priority`: Sort by priority
- `created_at`: Default sort order (newest first)
- `(user_id, completed)`: Composite index for common query pattern
- `tags` (GIN): Full-text search on array of tags

---

### 3. `revoked_tokens` (Optional)

Stores revoked JWT tokens to prevent use after logout. Optional for Phase 2 (can use stateless JWT without revocation).

**Table Name**: `revoked_tokens`

**Columns:**

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `token_hash` | VARCHAR(64) | PRIMARY KEY | SHA-256 hash of JWT token |
| `revoked_at` | TIMESTAMP WITH TIME ZONE | NOT NULL, DEFAULT CURRENT_TIMESTAMP | When token was revoked |
| `expires_at` | TIMESTAMP WITH TIME ZONE | NOT NULL | When token naturally expires (for cleanup) |

**Indexes:**
```sql
CREATE INDEX idx_revoked_tokens_expires_at ON revoked_tokens(expires_at);
```

**Cleanup Job:**
Run daily to remove expired tokens:
```sql
DELETE FROM revoked_tokens WHERE expires_at < CURRENT_TIMESTAMP;
```

**SQLModel Definition:**
```python
from sqlmodel import Field, SQLModel
from datetime import datetime

class RevokedToken(SQLModel, table=True):
    __tablename__ = "revoked_tokens"

    token_hash: str = Field(max_length=64, primary_key=True)
    revoked_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    expires_at: datetime = Field(nullable=False)
```

---

## Database Migrations

### Initial Migration (Phase 2 Setup)

**File**: `backend/migrations/001_initial_schema.sql`

```sql
-- Create UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create users table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    name VARCHAR(100) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_login_at TIMESTAMP WITH TIME ZONE
);

-- Create indexes on users
CREATE UNIQUE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_created_at ON users(created_at);

-- Create tasks table
CREATE TABLE tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    completed BOOLEAN NOT NULL DEFAULT FALSE,
    priority VARCHAR(10) NOT NULL DEFAULT 'NONE',
    tags TEXT[] DEFAULT '{}',
    due_date TIMESTAMP WITH TIME ZONE,
    is_recurring BOOLEAN NOT NULL DEFAULT FALSE,
    recurrence_pattern VARCHAR(10),
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP WITH TIME ZONE
);

-- Add check constraints to tasks
ALTER TABLE tasks
ADD CONSTRAINT check_priority
CHECK (priority IN ('HIGH', 'MEDIUM', 'LOW', 'NONE'));

ALTER TABLE tasks
ADD CONSTRAINT check_recurrence_pattern
CHECK (
    (is_recurring = FALSE AND recurrence_pattern IS NULL) OR
    (is_recurring = TRUE AND recurrence_pattern IN ('DAILY', 'WEEKLY', 'MONTHLY'))
);

ALTER TABLE tasks
ADD CONSTRAINT check_recurring_due_date
CHECK (
    (is_recurring = FALSE) OR
    (is_recurring = TRUE AND due_date IS NOT NULL)
);

-- Create indexes on tasks
CREATE INDEX idx_tasks_user_id ON tasks(user_id);
CREATE INDEX idx_tasks_completed ON tasks(completed);
CREATE INDEX idx_tasks_due_date ON tasks(due_date) WHERE due_date IS NOT NULL;
CREATE INDEX idx_tasks_priority ON tasks(priority);
CREATE INDEX idx_tasks_created_at ON tasks(created_at);
CREATE INDEX idx_tasks_user_completed ON tasks(user_id, completed);
CREATE INDEX idx_tasks_tags ON tasks USING GIN(tags);

-- Create revoked_tokens table (optional)
CREATE TABLE revoked_tokens (
    token_hash VARCHAR(64) PRIMARY KEY,
    revoked_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL
);

CREATE INDEX idx_revoked_tokens_expires_at ON revoked_tokens(expires_at);

-- Create updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply updated_at trigger to users
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Apply updated_at trigger to tasks
CREATE TRIGGER update_tasks_updated_at BEFORE UPDATE ON tasks
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
```

---

## Row-Level Security (Optional Enhancement)

For additional security, enable PostgreSQL Row-Level Security (RLS):

```sql
-- Enable RLS on tasks table
ALTER TABLE tasks ENABLE ROW LEVEL SECURITY;

-- Policy: Users can only see their own tasks
CREATE POLICY tasks_isolation_policy ON tasks
FOR ALL
TO authenticated_users
USING (user_id = current_setting('app.current_user_id')::UUID);

-- Set user context in each request (application level)
-- SET LOCAL app.current_user_id = '<user_id_from_jwt>';
```

---

## Seed Data (Development Only)

**File**: `backend/migrations/seed_dev.sql`

```sql
-- Create test user
INSERT INTO users (id, email, password_hash, name)
VALUES (
    '550e8400-e29b-41d4-a716-446655440000',
    'test@example.com',
    '$2b$12$KIX8NvCx1jKjv5ZLx3ZuqeSKJYUlwZdZl8HfV8fQ0qZq0aX2yGqMa', -- "password123"
    'Test User'
);

-- Create sample tasks
INSERT INTO tasks (user_id, title, description, priority, tags, due_date, is_recurring, recurrence_pattern)
VALUES
(
    '550e8400-e29b-41d4-a716-446655440000',
    'Complete project documentation',
    'Write comprehensive docs for Phase 2',
    'HIGH',
    ARRAY['work', 'documentation'],
    '2026-01-10 17:00:00+00',
    FALSE,
    NULL
),
(
    '550e8400-e29b-41d4-a716-446655440000',
    'Weekly team meeting',
    'Standup with development team',
    'MEDIUM',
    ARRAY['work', 'meeting'],
    '2026-01-06 09:00:00+00',
    TRUE,
    'WEEKLY'
),
(
    '550e8400-e29b-41d4-a716-446655440000',
    'Buy groceries',
    'Milk, eggs, bread, vegetables',
    'LOW',
    ARRAY['personal', 'shopping'],
    NULL,
    FALSE,
    NULL
);
```

---

## Query Examples

### Get all incomplete tasks for a user, sorted by priority
```sql
SELECT * FROM tasks
WHERE user_id = '550e8400-e29b-41d4-a716-446655440000'
AND completed = FALSE
ORDER BY
    CASE priority
        WHEN 'HIGH' THEN 1
        WHEN 'MEDIUM' THEN 2
        WHEN 'LOW' THEN 3
        ELSE 4
    END,
    due_date ASC NULLS LAST,
    created_at DESC;
```

### Get overdue tasks (past due date)
```sql
SELECT * FROM tasks
WHERE user_id = '550e8400-e29b-41d4-a716-446655440000'
AND completed = FALSE
AND due_date < CURRENT_TIMESTAMP;
```

### Get tasks due within next 60 minutes
```sql
SELECT * FROM tasks
WHERE user_id = '550e8400-e29b-41d4-a716-446655440000'
AND completed = FALSE
AND due_date BETWEEN CURRENT_TIMESTAMP AND CURRENT_TIMESTAMP + INTERVAL '60 minutes';
```

### Search tasks by keyword (case-insensitive)
```sql
SELECT * FROM tasks
WHERE user_id = '550e8400-e29b-41d4-a716-446655440000'
AND (
    title ILIKE '%meeting%' OR
    description ILIKE '%meeting%' OR
    'meeting' = ANY(tags)
);
```

### Filter tasks by tags (ANY match)
```sql
SELECT * FROM tasks
WHERE user_id = '550e8400-e29b-41d4-a716-446655440000'
AND tags && ARRAY['work', 'urgent']::TEXT[];  -- Contains any of these tags
```

---

## Performance Optimization

### Query Performance
- All user-scoped queries use `user_id` index
- Composite index `(user_id, completed)` optimizes most common filter
- GIN index on `tags` enables fast tag searches
- Partial index on `due_date` (only non-null) reduces index size

### Connection Pooling
- Use SQLAlchemy connection pool (default: 5 connections, max: 20)
- Neon serverless auto-scales connections

### Query Batching
- Fetch tasks in batches of 20 (pagination)
- Use `LIMIT` and `OFFSET` for pagination
- Return total count in separate query (cached)

---

## Backup & Recovery

### Neon Serverless Features
- Automatic daily backups (retained for 7 days)
- Point-in-time recovery (PITR)
- Branch-based development (separate dev/staging/prod branches)

### Manual Backup (Optional)
```bash
pg_dump -h <neon-host> -U <user> -d <database> > backup.sql
```

---

## Database Configuration

### Connection String Format
```
postgresql://<user>:<password>@<host>/<database>?sslmode=require
```

### Environment Variables
```bash
DATABASE_URL="postgresql://user:pass@ep-xxxx.neon.tech/tododb?sslmode=require"
DATABASE_POOL_SIZE=5
DATABASE_MAX_OVERFLOW=10
DATABASE_POOL_TIMEOUT=30
```

### SQLModel Engine Setup
```python
from sqlmodel import create_engine
import os

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(
    DATABASE_URL,
    pool_size=5,
    max_overflow=10,
    pool_timeout=30,
    echo=False  # Set True for SQL logging in development
)
```

---

## Security Considerations

1. **User Isolation**: All queries MUST filter by `user_id` from JWT token
2. **Password Storage**: NEVER store plaintext passwords, always use bcrypt/argon2
3. **SQL Injection**: Use parameterized queries (SQLModel handles this)
4. **Connection Security**: Always use SSL (`sslmode=require` in connection string)
5. **Secrets Management**: Store `DATABASE_URL` in environment variables, never commit to git

---

**Version**: 1.0.0
**Last Updated**: 2026-01-02
**Owner**: Phase 2 Development Team
