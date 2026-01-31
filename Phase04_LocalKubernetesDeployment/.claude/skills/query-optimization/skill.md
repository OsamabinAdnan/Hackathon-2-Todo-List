---
name: query-optimization
description: Craft efficient SQL queries for features like search by keyword or filter by priority/date with indexing for performance on large task lists. Use when (1) Implementing search functionality (keyword search across task titles/descriptions), (2) Creating complex filters (by priority, status, date range, tags), (3) Optimizing slow queries or improving database performance, (4) Implementing pagination and sorting for large datasets, (5) Preventing N+1 query problems through eager loading, (6) Creating composite indexes for common query patterns, (7) Implementing time-based queries (reminders, recurring tasks).
---
# Query Optimization Skill

Optimize PostgreSQL database queries for the Todo application using SQLModel ORM, focusing on performance for large datasets, efficient filtering, and proper indexing strategies.

## Core Capabilities

### 1. Query Performance Analysis

Analyze query performance using PostgreSQL's EXPLAIN ANALYZE:

```sql
-- Analyze a slow query
EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT)
SELECT * FROM tasks
WHERE user_id = 'user123'
  AND completed = false
  AND due_date <= '2025-01-03'
ORDER BY due_date;

-- Look for:
-- - Sequential scans on large tables
-- - Missing indexes
-- - High execution time
-- - High buffer usage
```

### 2. Efficient Filtering Patterns

**Single-Column Filters:**
```python
# Inefficient: Using functions on columns
tasks = session.exec(
    select(Task)
    .where(func.lower(Task.title).contains(func.lower(search_term)))
).all()

# Efficient: Use indexes with proper WHERE clauses
from sqlmodel import select
from datetime import datetime

# For status filtering
active_tasks = session.exec(
    select(Task)
    .where(Task.user_id == user_id)
    .where(Task.completed == False)
).all()

# For date range filtering
due_tasks = session.exec(
    select(Task)
    .where(Task.user_id == user_id)
    .where(Task.due_date >= start_date)
    .where(Task.due_date <= end_date)
).all()
```

**Multi-Condition Filtering:**
```python
# Combine conditions efficiently
def get_filtered_tasks(session, user_id, priority=None, status=None, due_date_start=None, due_date_end=None):
    query = select(Task).where(Task.user_id == user_id)

    if priority:
        query = query.where(Task.priority == priority)

    if status is not None:
        query = query.where(Task.completed == status)

    if due_date_start:
        query = query.where(Task.due_date >= due_date_start)

    if due_date_end:
        query = query.where(Task.due_date <= due_date_end)

    return session.exec(query.order_by(Task.created_at.desc())).all()
```

### 3. Composite Indexes for Performance

**Designing Efficient Composite Indexes:**

```sql
-- For user-specific queries with common filters
CREATE INDEX ix_tasks_user_priority_completed ON tasks (user_id, priority, completed);
CREATE INDEX ix_tasks_user_due_date_completed ON tasks (user_id, due_date, completed);
CREATE INDEX ix_tasks_user_created_at ON tasks (user_id, created_at);

-- For search functionality
CREATE INDEX ix_tasks_user_title_gin ON tasks USING gin (to_tsvector('english', title)) WHERE user_id IS NOT NULL;
CREATE INDEX ix_tasks_user_description_gin ON tasks USING gin (to_tsvector('english', description)) WHERE user_id IS NOT NULL;

-- For tag-based queries (if using JSONB for tags)
CREATE INDEX ix_tasks_user_tags_gin ON tasks USING gin (tags) WHERE user_id IS NOT NULL;
```

**Python Implementation:**
```python
# Define indexes in SQLModel models
from sqlmodel import Field, SQLModel, create_engine
from sqlalchemy import Index
from typing import Optional
from datetime import datetime

class Task(SQLModel, table=True):
    __tablename__ = "tasks"

    # Composite indexes for common query patterns
    __table_args__ = (
        Index("ix_tasks_user_priority_completed", "user_id", "priority", "completed"),
        Index("ix_tasks_user_due_date_completed", "user_id", "due_date", "completed"),
        Index("ix_tasks_user_created_at", "user_id", "created_at"),
    )

    id: str = Field(primary_key=True)
    user_id: str = Field(index=True)  # Single column index
    title: str = Field(max_length=200, index=True)  # For search
    description: Optional[str] = Field(default=None, max_length=1000)
    completed: bool = Field(default=False, index=True)
    priority: str = Field(default="NONE", index=True)
    tags: Optional[list[str]] = Field(default=None, sa_column=Column(JSON))  # JSONB for tags
    due_date: Optional[datetime] = Field(default=None, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
```

### 4. Search Optimization

**Full-Text Search Implementation:**
```python
from sqlalchemy import text
from sqlmodel import select

def search_tasks(session, user_id: str, search_term: str):
    """Efficient full-text search across task fields."""
    # Use PostgreSQL full-text search with proper indexes
    search_query = select(Task).where(
        Task.user_id == user_id
    ).where(
        text("to_tsvector('english', COALESCE(title, '') || ' ' || COALESCE(description, '')) @@ plainto_tsquery('english', :search_term)")
    ).params(search_term=search_term)

    return session.exec(search_query).all()

def keyword_search_tasks(session, user_id: str, keyword: str):
    """Alternative keyword search using LIKE with indexes."""
    # Ensure proper indexing on searchable columns
    search_pattern = f"%{keyword}%"
    return session.exec(
        select(Task)
        .where(Task.user_id == user_id)
        .where(
            (Task.title.ilike(search_pattern)) |
            (Task.description.ilike(search_pattern))
        )
    ).all()
```

### 5. Pagination and Sorting

**Efficient Pagination with Cursor-Based Approach:**
```python
from typing import List, Optional, Tuple
from sqlmodel import select, desc, asc

def get_tasks_paginated(
    session,
    user_id: str,
    limit: int = 20,
    cursor: Optional[str] = None,
    sort_by: str = "created_at",
    sort_order: str = "desc"
):
    """
    Efficient pagination using cursor-based approach to avoid OFFSET performance issues.
    """
    query = select(Task).where(Task.user_id == user_id)

    # Apply sorting
    if sort_order == "desc":
        sort_column = desc(getattr(Task, sort_by))
    else:
        sort_column = asc(getattr(Task, sort_by))

    query = query.order_by(sort_column)

    # Apply cursor if provided
    if cursor:
        if sort_order == "desc":
            query = query.where(getattr(Task, sort_by) < cursor)
        else:
            query = query.where(getattr(Task, sort_by) > cursor)

    # Limit results
    query = query.limit(limit)

    tasks = session.exec(query).all()

    # Get next cursor for pagination
    next_cursor = None
    if tasks:
        next_cursor = getattr(tasks[-1], sort_by)

    return tasks, next_cursor

def get_tasks_offset_pagination(session, user_id: str, page: int = 1, per_page: int = 20):
    """
    Traditional offset pagination (use for small datasets or when cursor not available).
    """
    offset = (page - 1) * per_page

    # Count total for pagination info
    count_query = select(Task).where(Task.user_id == user_id)
    total = session.exec(count_query).count()

    # Get paginated results
    results = session.exec(
        select(Task)
        .where(Task.user_id == user_id)
        .order_by(desc(Task.created_at))
        .offset(offset)
        .limit(per_page)
    ).all()

    return results, total
```

### 6. Preventing N+1 Query Problems

**Eager Loading with SQLModel:**
```python
from sqlmodel import select, Session
from sqlalchemy.orm import selectinload

def get_tasks_with_users(session: Session, user_ids: List[str]):
    """Load tasks with related user data to prevent N+1 queries."""
    # Bad: Causes N+1 queries
    # tasks = session.exec(select(Task)).all()
    # for task in tasks:
    #     user = task.user  # Separate query for each task

    # Good: Single query with joined data
    tasks = session.exec(
        select(Task)
        .where(Task.user_id.in_(user_ids))
        .options(selectinload(Task.user))  # Eager load user relationship
    ).all()

    return tasks

def get_tasks_with_relationships(session: Session, user_id: str):
    """Load tasks with multiple relationships efficiently."""
    from sqlalchemy.orm import selectinload

    tasks = session.exec(
        select(Task)
        .where(Task.user_id == user_id)
        .options(
            selectinload(Task.user),
            selectinload(Task.tags)  # If tags is a relationship
        )
    ).all()

    return tasks
```

### 7. Query Optimization Patterns

**Batch Operations:**
```python
def batch_update_task_status(session: Session, task_ids: List[str], new_status: bool):
    """Efficiently update multiple records in a single query."""
    from sqlalchemy import update

    stmt = (
        update(Task)
        .where(Task.id.in_(task_ids))
        .values(completed=new_status, updated_at=datetime.utcnow())
    )

    result = session.exec(stmt)
    session.commit()
    return result.rowcount

def bulk_insert_tasks(session: Session, tasks_data: List[dict]):
    """Efficiently insert multiple records."""
    from sqlalchemy import insert

    stmt = insert(Task)
    session.exec(stmt, tasks_data)
    session.commit()
```

**Conditional Queries:**
```python
def get_task_statistics(session: Session, user_id: str):
    """Get task statistics with a single optimized query."""
    from sqlalchemy import func, case

    stats = session.exec(
        select(
            func.count(Task.id).label('total'),
            func.count(case((Task.completed == True, 1))).label('completed'),
            func.count(case((Task.completed == False, 1))).label('pending'),
            func.count(case((Task.priority == 'HIGH', 1))).label('high_priority'),
            func.count(case((Task.priority == 'MEDIUM', 1))).label('medium_priority'),
            func.count(case((Task.priority == 'LOW', 1))).label('low_priority'),
            func.avg(case((Task.completed == False,
                         func.extract('epoch', Task.due_date - func.now()) / 86400.0)))
                .label('avg_days_to_due')
        )
        .where(Task.user_id == user_id)
    ).one()

    return {
        'total': stats.total or 0,
        'completed': stats.completed or 0,
        'pending': stats.pending or 0,
        'high_priority': stats.high_priority or 0,
        'medium_priority': stats.medium_priority or 0,
        'low_priority': stats.low_priority or 0,
        'avg_days_to_due': float(stats.avg_days_to_due) if stats.avg_days_to_due else None
    }
```

### 8. Performance Monitoring

**Query Timing and Analysis:**
```python
import time
from contextlib import contextmanager

@contextmanager
def measure_query_time(operation_name: str = "Query"):
    """Context manager to measure query execution time."""
    start_time = time.time()
    try:
        yield
    finally:
        end_time = time.time()
        execution_time = (end_time - start_time) * 1000  # Convert to milliseconds
        print(f"{operation_name} executed in {execution_time:.2f}ms")

        # Log slow queries
        if execution_time > 100:  # Log queries taking more than 100ms
            print(f"⚠️  SLOW QUERY ALERT: {operation_name} took {execution_time:.2f}ms")

# Usage example
def get_user_tasks_with_timing(session, user_id: str):
    with measure_query_time(f"Get tasks for user {user_id}"):
        tasks = session.exec(
            select(Task)
            .where(Task.user_id == user_id)
            .order_by(Task.created_at.desc())
            .limit(50)
        ).all()
    return tasks
```

### 9. Index Optimization Guidelines

**Index Selection Strategy:**
1. **Single-column indexes**: For columns frequently used in WHERE clauses
2. **Composite indexes**: For multi-column queries (order matters!)
3. **Partial indexes**: For filtered queries (WHERE conditions)
4. **Expression indexes**: For function-based queries

**Index Creation Examples:**
```sql
-- Single column (for basic filtering)
CREATE INDEX ix_tasks_user_id ON tasks (user_id);

-- Composite (order matters - most selective first)
CREATE INDEX ix_tasks_user_completed_priority ON tasks (user_id, completed, priority);

-- Partial (only for active records)
CREATE INDEX ix_tasks_user_active ON tasks (user_id, created_at) WHERE completed = false;

-- Expression (for case-insensitive search)
CREATE INDEX ix_tasks_title_lower ON tasks (lower(title));

-- GIN for JSON/Array columns
CREATE INDEX ix_tasks_tags_gin ON tasks USING gin (tags);
```

### 10. Query Optimization Checklist

- [ ] Use indexes for all WHERE clause columns
- [ ] Create composite indexes for multi-column queries
- [ ] Avoid SELECT * - only select needed columns
- [ ] Use LIMIT for large result sets
- [ ] Implement proper pagination (cursor-based for large datasets)
- [ ] Use eager loading to prevent N+1 queries
- [ ] Analyze query plans with EXPLAIN ANALYZE
- [ ] Monitor query execution time
- [ ] Use prepared statements when possible
- [ ] Consider read replicas for read-heavy operations

## References

- **Database Spec**: `@specs/database/schema.md` for schema definitions
- **SQLModel Documentation**: https://sqlmodel.tiangolo.com for ORM patterns
- **PostgreSQL Performance**: https://www.postgresql.org/docs/current/performance-tips.html
- **Indexing Best Practices**: https://www.postgresql.org/docs/current/indexes.html