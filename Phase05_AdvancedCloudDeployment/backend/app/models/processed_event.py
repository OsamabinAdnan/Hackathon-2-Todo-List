"""
ProcessedEvent Model - Idempotency Tracking
Phase 5: Event-driven architecture

Tracks which events have been processed by each consumer service
to prevent duplicate processing (at-least-once delivery guarantee).
"""

from sqlmodel import Field, SQLModel
from datetime import datetime
from typing import Optional
import uuid


class ProcessedEvent(SQLModel, table=True):
    """
    Tracks processed events for idempotency.

    Each event is tracked per service to allow multiple services
    to independently track their processing state.

    Attributes:
        id: Primary key
        event_id: Unique identifier of the processed event
        service_name: Name of the service that processed the event
        processed_at: Timestamp when the event was processed
        user_id: User ID associated with the event (for filtering)
    """
    __tablename__ = "processed_events"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    event_id: uuid.UUID = Field(nullable=False, index=True)
    service_name: str = Field(max_length=50, nullable=False, index=True)
    processed_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    user_id: uuid.UUID = Field(nullable=False, index=True)

    class Config:
        # Unique constraint on (event_id, service_name) to prevent duplicate processing
        table_args = (
            {"sqlite_autoincrement": True},
        )


class ProcessedEventCreate(SQLModel):
    """Schema for creating a processed event record."""
    event_id: uuid.UUID
    service_name: str
    user_id: uuid.UUID


class ProcessedEventRead(SQLModel):
    """Schema for reading a processed event record."""
    id: uuid.UUID
    event_id: uuid.UUID
    service_name: str
    processed_at: datetime
    user_id: uuid.UUID
