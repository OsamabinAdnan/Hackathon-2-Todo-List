from sqlmodel import Field, SQLModel
from datetime import datetime
from typing import Optional
import uuid
from sqlalchemy import Column, Text, JSON


class Conversation(SQLModel, table=True):
    __tablename__ = "conversations"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="users.id", index=True)  # Using uuid.UUID to match users.id type
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)


class Message(SQLModel, table=True):
    __tablename__ = "messages"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="users.id", index=True)  # Using uuid.UUID to match users.id type
    conversation_id: uuid.UUID = Field(foreign_key="conversations.id", index=True)
    role: str = Field(sa_column=Column(Text, nullable=False))  # "user" or "assistant"
    content: str = Field(sa_column=Column(Text, nullable=False))
    tool_calls: Optional[dict] = Field(sa_column=Column(JSON))  # Store tool calls if any
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)