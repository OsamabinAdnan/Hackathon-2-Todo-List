"""
OpenRouter Client Configuration
Sets up the OpenAI client with OpenRouter base URL
"""
from openai import AsyncOpenAI
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


def create_openrouter_client():
    """Create and configure OpenAI client with OpenRouter settings."""
    client = AsyncOpenAI(
        base_url=os.getenv("OPENROUTER_URL", "https://openrouter.ai/api/v1"),
        api_key=os.getenv("OPENROUTER_API_KEY"),
        default_headers={
            "HTTP-Referer": os.getenv("APP_URL", "http://localhost:3000"),  # Optional. Site URL for rankings on openrouter.ai.
            "X-Title": os.getenv("APP_NAME", "Todo AI Assistant"),  # Optional. Site title for rankings on openrouter.ai.
        }
    )
    return client