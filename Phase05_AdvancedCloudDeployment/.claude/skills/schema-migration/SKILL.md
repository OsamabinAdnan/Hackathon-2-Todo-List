---
name: schema-migration
description: Automate creation of Alembic migration scripts for SQLModel schema evolutions with version control and backward compatibility. Use when (1) Adding new fields to existing tables (e.g., priority, due_date, recurrence fields to Task model), (2) Creating new tables (e.g., UserSession, Tag, Reminder), (3) Modifying column types or constraints, (4) Adding/removing database indexes for performance, (5) Establishing foreign key relationships between tables, (6) Ensuring backward compatibility during iterative development with proper up/down migrations.
---

# Schema Migration Skill

Automate database schema evolution using Alembic with SQLModel for PostgreSQL, ensuring version-controlled, backward-compatible migrations throughout iterative development.

## Core Capabilities

### 1. Alembic Setup and Configuration

Initialize Alembic for SQLModel-based PostgreSQL projects:

```bash
# Install Alembic
pip install alembic

# Initialize Alembic in backend directory
cd backend
alembic init alembic
```

**Configure `alembic.ini`:**
```ini
# alembic.ini
[alembic]
script_location = alembic
prepend_sys_path = .

# Database URL from environment variable
sqlalchemy.url = driver://user:pass@localhost/dbname

# Or use environment variable substitution
# sqlalchemy.url = ${DATABASE_URL}
```

**Configure `alembic/env.py` for SQLModel:**
```python
# alembic/env.py
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
import os

# Import SQLModel and all models
from sqlmodel import SQLModel
from app.models import User, Task  # Import ALL models here

# Alembic Config object
config = context.config

# Get DATABASE_URL from environment
database_url = os.getenv("DATABASE_URL")
if database_url:
    config.set_main_option("sqlalchemy.url", database_url)

# Setup logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Set target_metadata to SQLModel.metadata
target_metadata = SQLModel.metadata

def run_migrations_offline():
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    """Run migrations in 'online' mode."""
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

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
```

### 2. Auto-Generate Migrations

Create migrations automatically from SQLModel changes:

```bash
# Generate migration from model changes
alembic revision --autogenerate -m "Add priority and due_date to Task model"

# This creates: alembic/versions/xxxx_add_priority_and_due_date.py
```

**Example: Adding Fields to Task Model**

**Step 1: Update SQLModel**
```python
# app/models.py
from sqlmodel import SQLModel, Field
from datetime import datetime
from enum import Enum

class Priority(str, Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    NONE = "NONE"

class Task(SQLModel, table=True):
    __tablename__ = "tasks"

    id: str = Field(primary_key=True)
    user_id: str = Field(foreign_key="users.id")
    title: str = Field(max_length=200)
    description: Optional[str] = None
    completed: bool = Field(default=False)

    # NEW FIELDS
    priority: Priority = Field(default=Priority.NONE, index=True)
    due_date: Optional[datetime] = Field(None, index=True)
    is_recurring: bool = Field(default=False)
    recurrence_pattern: Optional[str] = None

    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
```

**Step 2: Generate Migration**
```bash
alembic revision --autogenerate -m "Add priority, due_date, and recurrence to tasks"
```

**Step 3: Review Generated Migration**
```python
# alembic/versions/abc123_add_priority_due_date_recurrence.py
"""Add priority, due_date, and recurrence to tasks

Revision ID: abc123
Revises: prev456
Create Date: 2025-01-02 12:00:00
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic
revision = 'abc123'
down_revision = 'prev456'
branch_labels = None
depends_on = None

def upgrade():
    # Add priority column with default value
    op.add_column('tasks', sa.Column('priority', sa.String(), server_default='NONE', nullable=False))
    op.create_index(op.f('ix_tasks_priority'), 'tasks', ['priority'], unique=False)

    # Add due_date column (nullable)
    op.add_column('tasks', sa.Column('due_date', sa.DateTime(), nullable=True))
    op.create_index(op.f('ix_tasks_due_date'), 'tasks', ['due_date'], unique=False)

    # Add recurrence fields
    op.add_column('tasks', sa.Column('is_recurring', sa.Boolean(), server_default='false', nullable=False))
    op.add_column('tasks', sa.Column('recurrence_pattern', sa.String(), nullable=True))

def downgrade():
    # Reverse operations in reverse order
    op.drop_column('tasks', 'recurrence_pattern')
    op.drop_column('tasks', 'is_recurring')

    op.drop_index(op.f('ix_tasks_due_date'), table_name='tasks')
    op.drop_column('tasks', 'due_date')

    op.drop_index(op.f('ix_tasks_priority'), table_name='tasks')
    op.drop_column('tasks', 'priority')
```

**Step 4: Apply Migration**
```bash
# Apply migration to database
alembic upgrade head

# Output:
# INFO  [alembic.runtime.migration] Running upgrade prev456 -> abc123, Add priority, due_date, and recurrence to tasks
```

### 3. Manual Migration Creation

For complex changes, create migrations manually:

```bash
# Create empty migration file
alembic revision -m "Add composite index for user tasks queries"
```

**Example: Adding Composite Indexes**
```python
# alembic/versions/def456_add_composite_indexes.py
"""Add composite indexes for user tasks queries

Revision ID: def456
Revises: abc123
"""
from alembic import op

revision = 'def456'
down_revision = 'abc123'

def upgrade():
    # Composite index for user + priority queries
    op.create_index(
        'ix_tasks_user_priority',
        'tasks',
        ['user_id', 'priority'],
        unique=False
    )

    # Composite index for user + completed queries
    op.create_index(
        'ix_tasks_user_completed',
        'tasks',
        ['user_id', 'completed'],
        unique=False
    )

    # Composite index for user + due_date queries
    op.create_index(
        'ix_tasks_user_due_date',
        'tasks',
        ['user_id', 'due_date'],
        unique=False
    )

def downgrade():
    op.drop_index('ix_tasks_user_due_date', table_name='tasks')
    op.drop_index('ix_tasks_user_completed', table_name='tasks')
    op.drop_index('ix_tasks_user_priority', table_name='tasks')
```

### 4. Data Migrations

Migrate existing data during schema changes:

**Example: Populating Default Values for Existing Records**
```python
# alembic/versions/ghi789_populate_default_priorities.py
"""Populate default priorities for existing tasks

Revision ID: ghi789
Revises: def456
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import table, column

revision = 'ghi789'
down_revision = 'def456'

def upgrade():
    # Reference existing table
    tasks = table('tasks',
        column('id', sa.String),
        column('priority', sa.String),
        column('completed', sa.Boolean)
    )

    # Set priority based on business logic
    # Example: Incomplete tasks without priority get MEDIUM
    op.execute(
        tasks.update()
        .where(tasks.c.priority == None)
        .where(tasks.c.completed == False)
        .values(priority='MEDIUM')
    )

    # Completed tasks get LOW priority
    op.execute(
        tasks.update()
        .where(tasks.c.priority == None)
        .where(tasks.c.completed == True)
        .values(priority='LOW')
    )

def downgrade():
    # Reset priorities to NULL (if column was nullable before)
    tasks = table('tasks', column('priority', sa.String))
    op.execute(
        tasks.update().values(priority=None)
    )
```

### 5. Creating New Tables

**Example: Adding UserSession Table**
```python
# First, create SQLModel
# app/models.py
class UserSession(SQLModel, table=True):
    __tablename__ = "user_sessions"

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    user_id: str = Field(foreign_key="users.id", index=True)
    refresh_token_hash: str = Field(max_length=255)
    device_info: Optional[str] = Field(None, max_length=500)
    ip_address: Optional[str] = Field(None, max_length=45)
    created_at: datetime = Field(default_factory=datetime.now)
    is_active: bool = Field(default=True, index=True)

    # Relationship
    user: User = Relationship(back_populates="sessions")

# Generate migration
alembic revision --autogenerate -m "Create user_sessions table"
```

**Generated Migration:**
```python
# alembic/versions/jkl012_create_user_sessions_table.py
def upgrade():
    op.create_table(
        'user_sessions',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('refresh_token_hash', sa.String(length=255), nullable=False),
        sa.Column('device_info', sa.String(length=500), nullable=True),
        sa.Column('ip_address', sa.String(length=45), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_user_sessions_user_id'), 'user_sessions', ['user_id'], unique=False)
    op.create_index(op.f('ix_user_sessions_is_active'), 'user_sessions', ['is_active'], unique=False)

def downgrade():
    op.drop_index(op.f('ix_user_sessions_is_active'), table_name='user_sessions')
    op.drop_index(op.f('ix_user_sessions_user_id'), table_name='user_sessions')
    op.drop_table('user_sessions')
```

### 6. Migration Management Commands

**Common Alembic Commands:**
```bash
# Show current migration version
alembic current

# Show migration history
alembic history --verbose

# Upgrade to latest migration
alembic upgrade head

# Upgrade to specific revision
alembic upgrade abc123

# Downgrade one migration
alembic downgrade -1

# Downgrade to specific revision
alembic downgrade abc123

# Downgrade all migrations
alembic downgrade base

# Show SQL without executing (dry run)
alembic upgrade head --sql

# Stamp database with specific revision (without running migration)
alembic stamp head
```

### 7. Backward Compatibility Strategies

**Strategy 1: Add Nullable Columns First**
```python
# Migration 1: Add nullable column
def upgrade():
    op.add_column('tasks', sa.Column('priority', sa.String(), nullable=True))

# Migration 2: Populate data
def upgrade():
    tasks = table('tasks', column('priority', sa.String))
    op.execute(tasks.update().values(priority='NONE'))

# Migration 3: Make column non-nullable
def upgrade():
    op.alter_column('tasks', 'priority', nullable=False)
```

**Strategy 2: Rename Columns Safely**
```python
# Step 1: Add new column
def upgrade():
    op.add_column('tasks', sa.Column('description_new', sa.String(length=1000)))

# Step 2: Copy data
def upgrade():
    op.execute("UPDATE tasks SET description_new = description")

# Step 3: Drop old column
def upgrade():
    op.drop_column('tasks', 'description')

# Step 4: Rename new column
def upgrade():
    op.alter_column('tasks', 'description_new', new_column_name='description')
```

**Strategy 3: Multi-Phase Deployments**
```python
# Phase 1: Add new field (nullable)
# Deploy code that works with AND without new field

# Phase 2: Populate field with data migration
# Application now uses new field

# Phase 3: Make field non-nullable (if needed)
# All records guaranteed to have value
```

## Migration Workflow

### Development Workflow
```bash
# 1. Update SQLModel models
# Edit app/models.py

# 2. Generate migration
alembic revision --autogenerate -m "Description of changes"

# 3. Review generated migration
# Check alembic/versions/xxxx_description.py

# 4. Test migration locally
alembic upgrade head

# 5. Test rollback
alembic downgrade -1

# 6. Commit migration file to version control
git add alembic/versions/xxxx_description.py
git commit -m "migration: Description of changes"
```

### Production Deployment Workflow
```bash
# 1. Backup database
pg_dump -U user -d database > backup_$(date +%Y%m%d).sql

# 2. Apply migrations
alembic upgrade head

# 3. Verify migration success
alembic current

# 4. Monitor application logs for errors

# 5. Rollback if needed
alembic downgrade -1
```

## Testing Migrations

```python
# tests/test_migrations.py
import pytest
from alembic import command
from alembic.config import Config
from sqlmodel import create_engine, Session

@pytest.fixture
def alembic_config():
    """Create Alembic configuration for testing."""
    config = Config("alembic.ini")
    config.set_main_option("sqlalchemy.url", "sqlite:///test.db")
    return config

def test_upgrade_downgrade(alembic_config):
    """Test that migrations can upgrade and downgrade."""
    # Upgrade to head
    command.upgrade(alembic_config, "head")

    # Downgrade one revision
    command.downgrade(alembic_config, "-1")

    # Upgrade again
    command.upgrade(alembic_config, "head")

def test_migration_data_integrity(alembic_config, test_session):
    """Test that data survives migration."""
    # Create test data before migration
    task = Task(title="Test Task", user_id="user123")
    test_session.add(task)
    test_session.commit()

    task_id = task.id

    # Run migration
    command.upgrade(alembic_config, "head")

    # Verify data still exists
    migrated_task = test_session.get(Task, task_id)
    assert migrated_task is not None
    assert migrated_task.title == "Test Task"
```

## Common Migration Patterns

### Pattern 1: Adding ENUM Column
```python
from alembic import op
import sqlalchemy as sa

def upgrade():
    # Create ENUM type
    priority_enum = sa.Enum('HIGH', 'MEDIUM', 'LOW', 'NONE', name='priority_enum')
    priority_enum.create(op.get_bind())

    # Add column with ENUM type
    op.add_column('tasks', sa.Column('priority', priority_enum, server_default='NONE'))

def downgrade():
    op.drop_column('tasks', 'priority')
    sa.Enum(name='priority_enum').drop(op.get_bind())
```

### Pattern 2: Renaming Table
```python
def upgrade():
    op.rename_table('old_table_name', 'new_table_name')

def downgrade():
    op.rename_table('new_table_name', 'old_table_name')
```

### Pattern 3: Changing Column Type
```python
def upgrade():
    # PostgreSQL specific - cast string to integer
    op.alter_column('tasks', 'priority_level',
                    type_=sa.Integer(),
                    postgresql_using='priority_level::integer')

def downgrade():
    op.alter_column('tasks', 'priority_level',
                    type_=sa.String())
```

## Quality Checklist

- [ ] Alembic initialized and configured with SQLModel.metadata
- [ ] DATABASE_URL loaded from environment in env.py
- [ ] All SQLModel table classes imported in env.py
- [ ] Migration includes both upgrade() and downgrade() functions
- [ ] Server defaults set for non-nullable columns being added
- [ ] Indexes created for frequently queried columns
- [ ] Foreign key constraints include ondelete behavior
- [ ] Data migrations preserve existing data
- [ ] Migrations tested locally (upgrade and downgrade)
- [ ] Migration file committed to version control

## References

- **Database Spec**: `@specs/database/schema.md` for schema definitions
- **Alembic Documentation**: https://alembic.sqlalchemy.org for migration patterns
- **SQLModel Documentation**: https://sqlmodel.tiangolo.com for model definitions
- **PostgreSQL Data Types**: https://www.postgresql.org/docs/current/datatype.html
