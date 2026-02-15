"""
Notification Service Configuration
Phase 5: Event-driven notification processing

Settings for the notification service that consumes reminder events
from Kafka via Dapr pub/sub and logs notifications.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator
from typing import List, Union, Any
import json


class Settings(BaseSettings):
    """Notification service configuration."""

    # Service Identity
    SERVICE_NAME: str = "notification-service"
    SERVICE_PORT: int = 8001

    # Database (for idempotency tracking)
    NEON_DB_URL: str = "postgresql://localhost:5432/todo_app"

    # Dapr Configuration
    DAPR_HTTP_PORT: int = 3500
    DAPR_GRPC_PORT: int = 50001
    PUBSUB_NAME: str = "kafka-pubsub"
    STATE_STORE_NAME: str = "statestore"
    SECRET_STORE_NAME: str = "kubernetes-secrets"
    DAPR_ENABLED: bool = True

    # Topics to subscribe to
    REMINDERS_TOPIC: str = "reminders"

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
    def DAPR_PUBSUB_URL(self) -> str:
        """URL for Dapr pub/sub publishing"""
        return f"{self.DAPR_HTTP_URL}/v1.0/publish/{self.PUBSUB_NAME}"

    @property
    def DATABASE_URL(self) -> str:
        """Alias for database connection"""
        return self.NEON_DB_URL


settings = Settings()
