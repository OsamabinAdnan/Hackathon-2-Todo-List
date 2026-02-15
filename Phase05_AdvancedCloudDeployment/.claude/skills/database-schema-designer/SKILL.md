---
name: database-schema-designer
description: Generate SQLModel classes for PostgreSQL database tables with relationships, constraints, indexes, and migrations using Alembic. Use when (1) Creating database models from @specs/database/schema.md (User, Task tables), (2) Adding fields with proper types and constraints (e.g., priorities ENUM, due_date TIMESTAMP), (3) Defining relationships (one-to-many user-tasks with foreign keys), (4) Creating database indexes for query optimization, (5) Generating Alembic migrations for schema changes, (6) Implementing advanced features like recurring tasks with additional columns.
---

# Database Schema Designer

Generate production-ready SQLModel database schemas with proper relationships, constraints, indexes, and migration scripts for PostgreSQL with Neon serverless.

## Schema Design Workflow

### 1. Analyze Database Specification

Read `@specs/database/schema.md` to extract:
- Tables and their purpose
- Column names, types, and constraints
- Relationships (foreign keys, one-to-many, many-to-many)
- Indexes for query optimization
- ENUM types for restricted values
- Required fields vs optional fields
- Default values

### 2. Create SQLModel Base Classes

```python
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional
from datetime import datetime
from enum import Enum
import uuid

# ENUM definitions
class Priority(str, Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    NONE = "NONE"

class RecurrencePattern(str, Enum):
    DAILY = "DAILY"
    WEEKLY = "WEEKLY"
    MONTHLY = "MONTHLY"

# User Model
class User(SQLModel, table=True):
    __tablename__ = "users"

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    email: str = Field(unique=True, index=True, max_length=255)
    name: str = Field(max_length=200)
    hashed_password: str = Field(max_length=255)
    created_at: datetime = Field(default_factory=datetime.now)

    # Relationships
    tasks: list["Task"] = Relationship(back_populates="user", cascade_delete=True)

# Task Model
class Task(SQLModel, table=True):
    __tablename__ = "tasks"

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    user_id: str = Field(foreign_key="users.id", index=True)
    title: str = Field(max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    completed: bool = Field(default=False, index=True)
    priority: Priority = Field(default=Priority.NONE, index=True)
    tags: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    due_date: Optional[datetime] = Field(None, index=True)
    is_recurring: bool = Field(default=False)
    recurrence_pattern: Optional[RecurrencePattern] = None
    created_at: datetime = Field(default_factory=datetime.now, index=True)
    updated_at: datetime = Field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None

    # Relationships
    user: User = Relationship(back_populates="tasks")

    # Indexes (defined via __table_args__)
    __table_args__ = (
        Index("ix_tasks_user_priority", "user_id", "priority"),
        Index("ix_tasks_user_completed", "user_id", "completed"),
        Index("ix_tasks_user_due_date", "user_id", "due_date"),
    )
```

### 3. Define Relationships

**One-to-Many (User → Tasks):**
```python
# User model
tasks: list["Task"] = Relationship(back_populates="user", cascade_delete=True)

# Task model
user: User = Relationship(back_populates="tasks")
```

**Many-to-Many (Tasks ↔ Tags) - Using Link Table:**
```python
class TaskTagLink(SQLModel, table=True):
    __tablename__ = "task_tag_link"

    task_id: str = Field(foreign_key="tasks.id", primary_key=True)
    tag_id: str = Field(foreign_key="tags.id", primary_key=True)

class Tag(SQLModel, table=True):
    __tablename__ = "tags"

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    name: str = Field(unique=True, max_length=20, index=True)
    user_id: str = Field(foreign_key="users.id")

    # Relationships
    tasks: list["Task"] = Relationship(back_populates="tags", link_model=TaskTagLink)

# Update Task model
class Task(SQLModel, table=True):
    # ... existing fields ...
    tags: list["Tag"] = Relationship(back_populates="tasks", link_model=TaskTagLink)
```

### 4. Create Database Indexes

**Composite Indexes for Common Queries:**
```python
from sqlalchemy import Index

class Task(SQLModel, table=True):
    # ... fields ...

    __table_args__ = (
        # User-specific queries
        Index("ix_tasks_user_priority", "user_id", "priority"),
        Index("ix_tasks_user_completed", "user_id", "completed"),
        Index("ix_tasks_user_due_date", "user_id", "due_date"),

        # Sorting optimization
        Index("ix_tasks_user_created", "user_id", "created_at"),

        # Recurring tasks lookup
        Index("ix_tasks_recurring_due", "is_recurring", "due_date"),
    )
```

### 5. Generate Alembic Migrations

**Initialize Alembic:**
```bash
cd backend
alembic init alembic
```

**Configure alembic.ini:**
```ini
# alembic.ini
[alembic]
script_location = alembic
sqlalchemy.url = ${DATABASE_URL}
```

**Update env.py:**
```python
# alembic/env.py
from sqlmodel import SQLModel
from app.models import User, Task  # Import all models

target_metadata = SQLModel.metadata

def run_migrations_online():
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()
```

**Generate Migration:**
```bash
alembic revision --autogenerate -m "Create users and tasks tables"
```

**Review Generated Migration:**
```python
# alembic/versions/xxxx_create_users_and_tasks_tables.py
def upgrade():
    op.create_table(
        'users',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('hashed_password', sa.String(length=255), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=False)

    op.create_table(
        'tasks',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        # ... more columns ...
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    # ... indexes ...

def downgrade():
    op.drop_table('tasks')
    op.drop_table('users')
```

**Apply Migration:**
```bash
alembic upgrade head
```

### 6. Query Optimization Patterns

**Efficient Queries with Indexes:**
```python
from sqlmodel import Session, select
from sqlalchemy.orm import selectinload

# Optimized: Uses ix_tasks_user_priority index
def get_high_priority_tasks(session: Session, user_id: str):
    return session.exec(
        select(Task)
        .where(Task.user_id == user_id, Task.priority == Priority.HIGH)
        .order_by(Task.created_at.desc())
    ).all()

# Eager loading relationships (avoid N+1 queries)
def get_user_with_tasks(session: Session, user_id: str):
    return session.exec(
        select(User)
        .where(User.id == user_id)
        .options(selectinload(User.tasks))
    ).first()

# Pagination with count
from sqlalchemy import func

def get_tasks_paginated(session: Session, user_id: str, page: int, limit: int):
    query = select(Task).where(Task.user_id == user_id)

    # Count total (uses index)
    total = session.exec(select(func.count()).select_from(query.subquery())).one()

    # Get paginated results
    offset = (page - 1) * limit
    tasks = session.exec(query.offset(offset).limit(limit)).all()

    return tasks, total
```

## Advanced Features

See `references/advanced-schema-patterns.md` for:
- Soft deletes with `deleted_at` timestamp
- Audit trails with `created_by`, `updated_by` fields
- Full-text search with PostgreSQL `tsvector`
- Partitioning large tables by date ranges
- Database connection pooling for Neon serverless
- Transaction management and rollback strategies

## Migration Strategies

**Adding New Column:**
```bash
alembic revision -m "Add priority field to tasks"
```

```python
def upgrade():
    op.add_column('tasks', sa.Column('priority', sa.String(), server_default='NONE'))
    op.create_index('ix_tasks_priority', 'tasks', ['priority'])

def downgrade():
    op.drop_index('ix_tasks_priority')
    op.drop_column('tasks', 'priority')
```

**Modifying Existing Column:**
```python
def upgrade():
    # Add new column
    op.add_column('tasks', sa.Column('description_new', sa.String(length=1000)))

    # Copy data
    op.execute("UPDATE tasks SET description_new = description")

    # Drop old column
    op.drop_column('tasks', 'description')

    # Rename new column
    op.alter_column('tasks', 'description_new', new_column_name='description')

def downgrade():
    # Reverse operations
    op.alter_column('tasks', 'description', new_column_name='description_new')
    op.add_column('tasks', sa.Column('description', sa.Text()))
    op.execute("UPDATE tasks SET description = description_new")
    op.drop_column('tasks', 'description_new')
```

## Quality Checklist

- [ ] All models inherit from `SQLModel` with `table=True`
- [ ] Primary keys defined with appropriate types (UUID strings)
- [ ] Foreign keys defined with proper relationships
- [ ] Indexes created for frequently queried columns
- [ ] Composite indexes for multi-column queries
- [ ] ENUM types used for restricted value sets
- [ ] Timestamps (created_at, updated_at) included
- [ ] Cascade delete configured for dependent records
- [ ] Field constraints match specification (max_length, unique, nullable)
- [ ] Alembic migrations generated and reviewed
- [ ] Migration up/down operations tested

## References

- **Database Spec**: `@specs/database/schema.md` for complete schema definitions
- **Advanced Patterns**: `references/advanced-schema-patterns.md` for complex scenarios
- **SQLModel Docs**: https://sqlmodel.tiangolo.com for official reference
