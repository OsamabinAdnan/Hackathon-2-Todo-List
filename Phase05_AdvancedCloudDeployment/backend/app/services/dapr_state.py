"""
Dapr State Management Service
Phase 5: State store abstraction via Dapr HTTP API (FR-025)

This is an OPTIONAL cache layer - your database remains the source of truth.
When DAPR_ENABLED=False, all methods return gracefully without errors.
"""

import httpx
import logging
from typing import Any, Dict, Optional, List
import json

from app.config.settings import settings

logger = logging.getLogger(__name__)


class DaprStateService:
    """
    Wrapper for Dapr State Management API.

    Provides optional caching layer for conversation state.
    Falls back gracefully when Dapr is unavailable.

    Usage:
        state_service = DaprStateService()
        await state_service.save("key", {"data": "value"})
        data = await state_service.get("key")
    """

    def __init__(self, store_name: Optional[str] = None):
        """
        Initialize state service.

        Args:
            store_name: Dapr state store name (defaults to settings.STATE_STORE_NAME)
        """
        self.store_name = store_name or settings.STATE_STORE_NAME
        self.dapr_port = settings.DAPR_HTTP_PORT
        self.enabled = settings.DAPR_ENABLED
        self.base_url = f"http://localhost:{self.dapr_port}/v1.0/state/{self.store_name}"

    async def save(
        self,
        key: str,
        value: Any,
        metadata: Optional[Dict[str, str]] = None
    ) -> bool:
        """
        Save state to Dapr state store (optional cache).

        Args:
            key: State key
            value: State value (will be JSON serialized)
            metadata: Optional Dapr metadata

        Returns:
            True if saved successfully, False otherwise
        """
        if not self.enabled:
            logger.debug("Dapr disabled, skipping state save")
            return True  # Return True so app continues normally

        try:
            payload = [{"key": key, "value": value}]

            if metadata:
                payload[0]["metadata"] = metadata

            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.post(
                    self.base_url,
                    json=payload,
                    headers={"Content-Type": "application/json"}
                )

                if response.status_code in (200, 201, 204):
                    logger.debug(f"State saved: {key}")
                    return True
                else:
                    logger.warning(f"Failed to save state {key}: {response.status_code}")
                    return False

        except httpx.TimeoutException:
            logger.warning(f"Timeout saving state: {key}")
            return False
        except Exception as e:
            logger.warning(f"Error saving state {key}: {e}")
            return False

    async def get(self, key: str) -> Optional[Any]:
        """
        Get state from Dapr state store (optional cache).

        Args:
            key: State key

        Returns:
            State value if found, None otherwise
        """
        if not self.enabled:
            logger.debug("Dapr disabled, skipping state get")
            return None

        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self.base_url}/{key}")

                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 204:
                    # Key not found
                    return None
                else:
                    logger.warning(f"Failed to get state {key}: {response.status_code}")
                    return None

        except httpx.TimeoutException:
            logger.warning(f"Timeout getting state: {key}")
            return None
        except Exception as e:
            logger.warning(f"Error getting state {key}: {e}")
            return None

    async def delete(self, key: str) -> bool:
        """
        Delete state from Dapr state store.

        Args:
            key: State key to delete

        Returns:
            True if deleted successfully, False otherwise
        """
        if not self.enabled:
            logger.debug("Dapr disabled, skipping state delete")
            return True

        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.delete(f"{self.base_url}/{key}")

                if response.status_code in (200, 204):
                    logger.debug(f"State deleted: {key}")
                    return True
                else:
                    logger.warning(f"Failed to delete state {key}: {response.status_code}")
                    return False

        except httpx.TimeoutException:
            logger.warning(f"Timeout deleting state: {key}")
            return False
        except Exception as e:
            logger.warning(f"Error deleting state {key}: {e}")
            return False

    async def save_bulk(self, items: List[Dict[str, Any]]) -> bool:
        """
        Save multiple state items in bulk.

        Args:
            items: List of {"key": str, "value": Any} dicts

        Returns:
            True if all saved successfully, False otherwise
        """
        if not self.enabled:
            logger.debug("Dapr disabled, skipping bulk state save")
            return True

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    self.base_url,
                    json=items,
                    headers={"Content-Type": "application/json"}
                )

                if response.status_code in (200, 201, 204):
                    logger.debug(f"Bulk state saved: {len(items)} items")
                    return True
                else:
                    logger.warning(f"Failed to save bulk state: {response.status_code}")
                    return False

        except Exception as e:
            logger.warning(f"Error saving bulk state: {e}")
            return False


# Singleton instance for convenience
_state_service: Optional[DaprStateService] = None


def get_state_service() -> DaprStateService:
    """Get or create singleton state service instance."""
    global _state_service
    if _state_service is None:
        _state_service = DaprStateService()
    return _state_service
