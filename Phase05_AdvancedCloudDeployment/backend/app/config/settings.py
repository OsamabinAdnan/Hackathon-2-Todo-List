from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator
from typing import List, Union, Any, Optional
import os
import json
import logging
import httpx

logger = logging.getLogger(__name__)

class Settings(BaseSettings):
    # Database - Define the field name to match the environment variable
    NEON_DB_URL: str = "postgresql://localhost:5432/todo_app"

    # Authentication - JWT Token Configuration
    JWT_SECRET: str = "your-super-secret-jwt-key-here"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRY_DAYS: int = 7

    # CORS - Store as raw string and parse it
    ALLOWED_ORIGINS: Union[List[str], str] = ["http://localhost:3000", "http://localhost:3001", "http://localhost:8000", "https://taskify-with-chatbot-osamabinadnan.vercel.app", "https://osamabinadnan-fullstacktodoapp-with-todo-ai-chatbot.hf.space"]

    # Environment
    ENVIRONMENT: str = "development"

    # Security
    SALT_ROUNDS: int = 12

    # Dapr Configuration (Phase 5)
    DAPR_HTTP_PORT: int = 3500
    DAPR_GRPC_PORT: int = 50001
    PUBSUB_NAME: str = "kafka-pubsub"
    STATE_STORE_NAME: str = "statestore"
    SECRET_STORE_NAME: str = "kubernetes-secrets"
    DAPR_ENABLED: bool = True  # Set to False for local development without Dapr

    @property
    def DAPR_HTTP_URL(self) -> str:
        """Base URL for Dapr HTTP API"""
        return f"http://localhost:{self.DAPR_HTTP_PORT}"

    @property
    def DAPR_PUBSUB_URL(self) -> str:
        """URL for Dapr pub/sub publishing"""
        return f"{self.DAPR_HTTP_URL}/v1.0/publish/{self.PUBSUB_NAME}"

    @property
    def DAPR_STATE_URL(self) -> str:
        """URL for Dapr state management"""
        return f"{self.DAPR_HTTP_URL}/v1.0/state/{self.STATE_STORE_NAME}"

    @property
    def DAPR_SECRETS_URL(self) -> str:
        """URL for Dapr secrets management"""
        return f"{self.DAPR_HTTP_URL}/v1.0/secrets/{self.SECRET_STORE_NAME}"

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra='ignore'
    )

    @field_validator('ALLOWED_ORIGINS', mode='before')
    @classmethod
    def parse_allowed_origins(cls, v: Any) -> List[str]:
        """Parse ALLOWED_ORIGINS from various formats."""
        if isinstance(v, list):
            return v
        if isinstance(v, str):
            # Try to parse as JSON array
            if v.startswith('[') and v.endswith(']'):
                try:
                    return json.loads(v)
                except json.JSONDecodeError:
                    pass
            # Try to split by comma
            return [origin.strip() for origin in v.split(',') if origin.strip()]
        # Default fallback
        return ["http://localhost:3000", "http://localhost:3001", "http://localhost:8000"]

    @property
    def DATABASE_URL(self) -> str:
        """Alias NEON_DB_URL to DATABASE_URL for compatibility with SQLModel"""
        # Get the environment variable directly, falling back to the class attribute
        env_value = os.getenv("NEON_DB_URL", getattr(self, 'NEON_DB_URL', "postgresql://localhost:5432/todo_app"))
        return env_value

    # Phase 5: Optional Dapr Secrets Loading (FR-028)
    # These methods provide OPTIONAL secret loading from Dapr.
    # If Dapr unavailable, your .env values are used (no change to existing behavior).

    async def load_secrets_from_dapr(self) -> bool:
        """
        Optionally load secrets from Dapr secret store.

        This is called during startup if DAPR_ENABLED=True.
        If Dapr is unavailable or secrets not found, existing .env values are kept.

        Returns:
            True if secrets were loaded from Dapr, False otherwise (using .env fallback)
        """
        if not self.DAPR_ENABLED:
            logger.debug("Dapr disabled, using .env secrets")
            return False

        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                # Try to get database secrets from Dapr
                response = await client.get(f"{self.DAPR_SECRETS_URL}/database-secrets")

                if response.status_code == 200:
                    secrets = response.json()

                    # Update settings if secrets found (don't override if not present)
                    if "NEON_DB_URL" in secrets:
                        object.__setattr__(self, 'NEON_DB_URL', secrets["NEON_DB_URL"])
                        logger.info("Loaded NEON_DB_URL from Dapr secrets")

                    if "JWT_SECRET" in secrets:
                        object.__setattr__(self, 'JWT_SECRET', secrets["JWT_SECRET"])
                        logger.info("Loaded JWT_SECRET from Dapr secrets")

                    return True
                else:
                    logger.debug(f"Dapr secrets not found (status {response.status_code}), using .env")
                    return False

        except httpx.TimeoutException:
            logger.debug("Dapr secrets timeout, using .env fallback")
            return False
        except Exception as e:
            logger.debug(f"Dapr secrets error: {e}, using .env fallback")
            return False

    def get_secret_sync(self, secret_name: str, key: str, default: Optional[str] = None) -> Optional[str]:
        """
        Synchronous helper to get a secret (uses .env values).

        For async Dapr secret loading, use load_secrets_from_dapr() at startup.
        This method just returns the current setting value or default.

        Args:
            secret_name: Name of secret group (ignored in sync mode)
            key: Setting key to retrieve
            default: Default value if not found

        Returns:
            Current setting value or default
        """
        return getattr(self, key, default)


settings = Settings()