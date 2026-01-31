from sqlmodel import Field, SQLModel
from sqlalchemy import ARRAY, String
from datetime import datetime
from typing import Optional, List
from enum import Enum
import uuid
from sqlmodel import Column

class Priority(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    NONE = "none"

class RecurrencePattern(str, Enum):
    NONE = "none"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    YEARLY = "yearly"

class TaskBase(SQLModel):
    title: str = Field(max_length=255)
    description: Optional[str] = Field(default=None, max_length=1000)
    status: str = Field(default="todo", max_length=20, index=True)
    priority: Priority = Field(default=Priority.NONE, index=True)
    due_date: Optional[datetime] = Field(default=None, index=True)
    recurrence_pattern: RecurrencePattern = Field(default=RecurrencePattern.NONE)
    user_id: uuid.UUID = Field(foreign_key="users.id", index=True)

class Task(TaskBase, table=True):
    __tablename__ = "tasks"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    title: str = Field(max_length=255)
    description: Optional[str] = Field(default=None, max_length=1000)
    status: str = Field(default="todo", max_length=20, index=True)
    priority: Priority = Field(default=Priority.NONE, index=True)
    due_date: Optional[datetime] = Field(default=None, index=True)
    recurrence_pattern: RecurrencePattern = Field(default=RecurrencePattern.NONE)
    user_id: uuid.UUID = Field(foreign_key="users.id", index=True)
    tags: List[str] = Field(default_factory=list, sa_column=Column(ARRAY(String)))
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False, index=True)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    completed_at: Optional[datetime] = None

class TaskCreate(SQLModel):
    title: str = Field(min_length=1, max_length=255)
    description: Optional[str] = Field(default=None, max_length=1000)
    priority: Priority = Field(default=Priority.NONE)
    due_date: Optional[datetime] = Field(default=None)
    recurrence_pattern: RecurrencePattern = Field(default=RecurrencePattern.NONE)
    tags: Optional[List[str]] = []

class TaskApiBase(SQLModel):
    title: str = Field(max_length=255)
    description: Optional[str] = Field(default=None, max_length=1000)
    status: str = Field(default="todo", max_length=20, index=True)
    priority: Priority = Field(default=Priority.NONE, index=True)
    due_date: Optional[datetime] = Field(default=None, index=True)
    recurrence_pattern: RecurrencePattern = Field(default=RecurrencePattern.NONE)


class TaskReadBase(SQLModel):
    title: str = Field(max_length=255)
    description: Optional[str] = Field(default=None, max_length=1000)
    status: str = Field(default="todo", max_length=20, index=True)
    priority: Priority = Field(default=Priority.NONE, index=True)
    due_date: Optional[datetime] = Field(default=None, index=True)
    recurrence_pattern: RecurrencePattern = Field(default=RecurrencePattern.NONE)


class TaskRead(TaskReadBase):
    id: uuid.UUID
    tags: List[str]
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime]

class TaskUpdate(SQLModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=255)
    description: Optional[str] = Field(default=None, max_length=1000)
    status: Optional[str] = Field(default=None, max_length=20)
    priority: Optional[Priority] = None
    due_date: Optional[datetime] = None
    recurrence_pattern: Optional[RecurrencePattern] = None
    tags: Optional[List[str]] = None

class TaskToggleComplete(SQLModel):
    completed: bool