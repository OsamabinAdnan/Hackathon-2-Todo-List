# Database Schema Validation for User Isolation

This document provides guidelines for designing database schemas that ensure proper user isolation in stateless applications, particularly for the Phase 3 AI Chatbot.

## Core Database Isolation Principles

### 1. Mandatory User Relationships
- Every user-specific table must have a user_id foreign key
- Foreign key constraints must be enforced at the database level
- User_id must be part of the query for all user-specific operations
- Never allow queries that could return data from multiple users

### 2. Proper Indexing Strategy
- Create indexes on user_id columns for fast filtering
- Consider composite indexes for common query patterns
- Index foreign key relationships for join performance
- Balance index count against write performance

### 3. Data Access Patterns
- Always filter by user_id in WHERE clauses for user data
- Use JOINs with user_id constraints when relating tables
- Implement proper pagination for large datasets
- Use EXPLAIN to verify query plans use user_id indexes

## Schema Design Patterns

### Pattern 1: User Table Structure
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index for fast user lookups
CREATE INDEX idx_users_email ON users(email);
```

### Pattern 2: User-Scoped Conversation Table
```sql
CREATE TABLE conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    title VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Foreign key constraint enforces user relationship
    CONSTRAINT fk_conversations_user_id FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,

    -- Index for fast user-based queries
    INDEX idx_conversations_user_id (user_id),
    INDEX idx_conversations_created_at (created_at)
);
```

### Pattern 3: User-Scoped Message Table
```sql
CREATE TABLE messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID NOT NULL,
    user_id UUID NOT NULL,  -- Duplicate user_id for direct access control
    role ENUM('user', 'assistant') NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Foreign key constraints
    CONSTRAINT fk_messages_conversation_id FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE,
    CONSTRAINT fk_messages_user_id FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,

    -- Indexes for performance
    INDEX idx_messages_conversation_id (conversation_id),
    INDEX idx_messages_user_id (user_id),
    INDEX idx_messages_created_at (created_at)
);
```

## SQL Query Patterns

### Safe Query Pattern: Always Include User ID
```python
# GOOD: Query includes user_id filter
def get_user_conversations(user_id: str, db: Session):
    return db.query(Conversation).filter(
        Conversation.user_id == user_id
    ).all()

def get_conversation_by_id(user_id: str, conversation_id: str, db: Session):
    return db.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.user_id == user_id  # Critical: user isolation
    ).first()
```

### Unsafe Query Pattern: Missing User ID Filter
```python
# BAD: Missing user_id filter - security vulnerability!
def get_conversation_by_id(conversation_id: str, db: Session):
    # Any user could access any conversation with this query
    return db.query(Conversation).filter(
        Conversation.id == conversation_id
    ).first()
```

## Database Migration Guidelines

### 1. Adding User Isolation to Existing Tables
```sql
-- Add user_id column to existing table
ALTER TABLE existing_table ADD COLUMN user_id UUID;

-- Populate user_id for existing records (migration logic)
UPDATE existing_table SET user_id = ... WHERE ...;

-- Add NOT NULL constraint
ALTER TABLE existing_table ALTER COLUMN user_id SET NOT NULL;

-- Add foreign key constraint
ALTER TABLE existing_table ADD CONSTRAINT fk_existing_table_user_id
FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;

-- Add index for performance
CREATE INDEX idx_existing_table_user_id ON existing_table(user_id);
```

### 2. Validating Existing Schema
```sql
-- Check for tables that should have user_id but don't
SELECT table_name, column_name
FROM information_schema.columns
WHERE table_schema = 'public'
AND column_name != 'user_id'
AND table_name IN (
    SELECT table_name
    FROM information_schema.columns
    WHERE column_name = 'user_id'
);
```

## Validation Checklist

### Schema Validation
- [ ] All user-specific tables have user_id foreign key
- [ ] Foreign key constraints are properly defined with CASCADE DELETE
- [ ] Indexes exist on all user_id columns
- [ ] No circular dependencies between user-related tables
- [ ] Proper data types used for UUIDs and timestamps
- [ ] NOT NULL constraints applied appropriately

### Query Validation
- [ ] All SELECT queries for user data include user_id filter
- [ ] UPDATE queries include user_id in WHERE clause
- [ ] DELETE operations are protected by user_id filters
- [ ] JOIN operations maintain user isolation
- [ ] No raw SQL bypasses user_id filtering

### Performance Validation
- [ ] Indexes are used in query execution plans
- [ ] Composite indexes exist for multi-column filters
- [ ] Pagination is implemented for large result sets
- [ ] Connection pooling is properly configured
- [ ] Slow query logging is enabled

## Common Pitfalls

### Pitfall 1: Indirect Access Without User Filtering
```sql
-- PROBLEM: Even with foreign keys, direct access without user_id filter
SELECT * FROM messages WHERE conversation_id = ?;
-- This doesn't verify the user owns the conversation!

-- SOLUTION: Always include user_id in the query
SELECT m.* FROM messages m
JOIN conversations c ON m.conversation_id = c.id
WHERE c.id = ? AND c.user_id = ?;
```

### Pitfall 2: Incomplete Foreign Key Setup
```sql
-- PROBLEM: Missing CASCADE DELETE
CONSTRAINT fk_messages_conversation_id FOREIGN KEY (conversation_id) REFERENCES conversations(id);
-- If conversation is deleted, messages remain orphaned

-- SOLUTION: Include CASCADE DELETE
CONSTRAINT fk_messages_conversation_id FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE;
```

### Pitfall 3: Insufficient Indexing
```sql
-- PROBLEM: Slow queries due to missing indexes
-- Without index on user_id, this becomes a full table scan:
SELECT * FROM conversations WHERE user_id = ?;

-- SOLUTION: Add proper indexes
CREATE INDEX idx_conversations_user_id ON conversations(user_id);
```

## Monitoring and Auditing

### Database Query Logging
- Log all queries that access user-specific data
- Flag queries that don't include user_id filters
- Monitor for queries that return large result sets
- Track query performance and identify bottlenecks

### Access Pattern Analysis
- Regularly audit query patterns for user isolation compliance
- Monitor for queries that access multiple users' data simultaneously
- Review slow query logs for potential isolation issues
- Verify that all user-specific queries use proper indexes