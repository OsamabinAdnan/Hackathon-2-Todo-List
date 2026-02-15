"""
Recurring Task Service Configuration
Phase 5: Event-driven recurring task processing

Settings for the recurring task service that consumes task completion
events from Kafka via Dapr pub/sub and creates next task occurrences.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator
from typing import List, Union, Any
import json


class Settings(BaseSettings):
    """Recurring task service configuration."""

    # Service Identity
    SERVICE_NAME: str = "recurring-service"
    SERVICE_PORT: int = 8002

    # Database (for idempotency tracking)
    NEON_DB_URL: str = "postgresql://localhost:5432/todo_app"

    # Backend API (for creating new tasks via Dapr service invocation)
    BACKEND_APP_ID: str = "backend"
    BACKEND_API_URL: str = "http://localhost:8000"

    # Dapr Configuration
    DAPR_HTTP_PORT: int = 3500
    DAPR_GRPC_PORT: int = 50001
    PUBSUB_NAME: str = "kafka-pubsub"
    STATE_STORE_NAME: str = "statestore"
    SECRET_STORE_NAME: str = "kubernetes-secrets"
    DAPR_ENABLED: bool = True

    # Topics to subscribe to
    TASK_EVENTS_TOPIC: str = "task-events"

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"  # json or text

    # Environment
    ENVIRONMENT: str = "development"

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra='ignore'
    )

    @property
    def DAPR_HTTP_URL(self) -> str:
        """Base URL for Dapr HTTP API"""
        return f"http://localhost:{self.DAPR_HTTP_PORT}"

    @property
    def DAPR_INVOKE_URL(self) -> str:
        """URL for Dapr service invocation"""
        return f"{self.DAPR_HTTP_URL}/v1.0/invoke/{self.BACKEND_APP_ID}/method"

    @property
    def DATABASE_URL(self) -> str:
        """Alias for database connection"""
        return self.NEON_DB_URL


settings = Settings()
