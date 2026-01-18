from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator
from typing import List, Union, Any
import os
import json

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

settings = Settings()