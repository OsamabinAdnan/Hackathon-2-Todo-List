"""
MCP Server for Todo AI Chatbot
Handles MCP tools for task operations
"""
from mcp.server.fastmcp import FastMCP
from mcp.server.auth.provider import TokenVerifier
from mcp.server.auth.settings import AuthSettings
from pydantic import AnyHttpUrl
from typing import Dict, Any
import os


class JWTTokenVerifier(TokenVerifier):
    """Custom JWT token verifier for the Todo application."""

    async def verify_token(self, token: str) -> Dict[str, Any]:
        """Verify JWT token and return user information."""
        from jose import jwt, JWTError
        from app.config.settings import settings

        try:
            payload = jwt.decode(
                token,
                settings.BETTER_AUTH_SECRET,
                algorithms=[settings.JWT_ALGORITHM]
            )
            return payload
        except JWTError:
            return None


# Initialize FastMCP server
mcp = FastMCP(
    "Todo MCP Server",
    json_response=True,
    # Token verifier for authentication
    token_verifier=JWTTokenVerifier(),
    # Auth settings for RFC 9728 Protected Resource Metadata
    auth=AuthSettings(
        issuer_url=AnyHttpUrl(os.getenv("AUTH_ISSUER_URL", "http://localhost:8000")),  # Authorization Server URL
        resource_server_url=AnyHttpUrl(os.getenv("SERVER_URL", "http://localhost:8000")),  # This server's URL
        required_scopes=["user"],
    ),
)