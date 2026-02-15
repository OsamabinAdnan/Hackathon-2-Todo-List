"""
Dapr Secrets Service
Phase 5: Secrets management via Dapr HTTP API (FR-028)

This is an OPTIONAL secrets layer - your .env file remains the fallback.
When DAPR_ENABLED=False or Dapr unavailable, returns None so app uses .env values.
"""

import httpx
import logging
from typing import Any, Dict, Optional

from app.config.settings import settings

logger = logging.getLogger(__name__)


class DaprSecretsService:
    """
    Wrapper for Dapr Secrets Management API.

    Provides optional secrets retrieval from Kubernetes secrets via Dapr.
    Falls back to None when Dapr is unavailable (app uses .env values).

    Usage:
        secrets_service = DaprSecretsService()
        db_url = await secrets_service.get_secret("database", "NEON_DB_URL")
        if db_url is None:
            # Use .env value instead
            db_url = os.getenv("NEON_DB_URL")
    """

    def __init__(self, store_name: Optional[str] = None):
        """
        Initialize secrets service.

        Args:
            store_name: Dapr secret store name (defaults to settings.SECRET_STORE_NAME)
        """
        self.store_name = store_name or settings.SECRET_STORE_NAME
        self.dapr_port = settings.DAPR_HTTP_PORT
        self.enabled = settings.DAPR_ENABLED
        self.base_url = f"http://localhost:{self.dapr_port}/v1.0/secrets/{self.store_name}"

    async def get_secret(
        self,
        secret_name: str,
        key: Optional[str] = None
    ) -> Optional[Any]:
        """
        Get a secret from Dapr secret store.

        Args:
            secret_name: Name of the secret (e.g., "database-secrets")
            key: Optional specific key within the secret

        Returns:
            Secret value if found, None otherwise (app should use .env fallback)
        """
        if not self.enabled:
            logger.debug("Dapr disabled, returning None for secret lookup")
            return None

        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self.base_url}/{secret_name}")

                if response.status_code == 200:
                    secrets = response.json()
                    if key:
                        return secrets.get(key)
                    return secrets
                else:
                    logger.debug(f"Secret {secret_name} not found via Dapr: {response.status_code}")
                    return None

        except httpx.TimeoutException:
            logger.warning(f"Timeout getting secret: {secret_name}")
            return None
        except Exception as e:
            logger.debug(f"Error getting secret {secret_name}: {e}")
            return None

    async def get_bulk_secrets(
        self,
        metadata: Optional[Dict[str, str]] = None
    ) -> Optional[Dict[str, Dict[str, str]]]:
        """
        Get all secrets from the secret store.

        Args:
            metadata: Optional Dapr metadata for filtering

        Returns:
            Dict of secret_name -> {key: value} if found, None otherwise
        """
        if not self.enabled:
            logger.debug("Dapr disabled, returning None for bulk secrets")
            return None

        try:
            url = f"{self.base_url}/bulk"
            params = {}
            if metadata:
                params["metadata"] = metadata

            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url, params=params)

                if response.status_code == 200:
                    return response.json()
                else:
                    logger.debug(f"Bulk secrets not found: {response.status_code}")
                    return None

        except Exception as e:
            logger.debug(f"Error getting bulk secrets: {e}")
            return None


# Singleton instance
_secrets_service: Optional[DaprSecretsService] = None


def get_secrets_service() -> DaprSecretsService:
    """Get or create singleton secrets service instance."""
    global _secrets_service
    if _secrets_service is None:
        _secrets_service = DaprSecretsService()
    return _secrets_service


async def get_secret_with_fallback(
    secret_name: str,
    key: str,
    fallback_value: Optional[str] = None
) -> Optional[str]:
    """
    Convenience function to get secret with automatic fallback.

    Args:
        secret_name: Dapr secret name
        key: Key within the secret
        fallback_value: Value to return if Dapr unavailable

    Returns:
        Secret value from Dapr, or fallback_value if unavailable
    """
    service = get_secrets_service()
    value = await service.get_secret(secret_name, key)
    if value is not None:
        return value
    return fallback_value
