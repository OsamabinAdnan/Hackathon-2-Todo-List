"""
Base Dapr Publisher
Phase 5: Event-driven architecture (FR-006, FR-007)

Provides base class for publishing events via Dapr HTTP pub/sub API.
All event publishing is non-blocking - failures are logged but don't
block the main operation.
"""

import httpx
import logging
import uuid
from typing import Any, Dict, Optional
from datetime import datetime

from app.config.settings import settings

logger = logging.getLogger(__name__)


class DaprPublisher:
    """
    Base class for publishing events via Dapr pub/sub HTTP API.

    All publishing is non-blocking - if Dapr/Kafka is unavailable,
    the main operation still succeeds and the failure is logged.
    """

    def __init__(self, topic: str):
        """
        Initialize publisher for a specific topic.

        Args:
            topic: Kafka topic name (e.g., 'task-events', 'reminders')
        """
        self.topic = topic
        self.pubsub_name = settings.PUBSUB_NAME
        self.dapr_url = settings.DAPR_PUBSUB_URL
        self.enabled = settings.DAPR_ENABLED

    def _get_publish_url(self) -> str:
        """Get the Dapr pub/sub publish URL for this topic."""
        return f"{self.dapr_url}/{self.topic}"

    def _generate_correlation_id(self) -> str:
        """Generate a unique correlation ID for distributed tracing."""
        return str(uuid.uuid4())

    async def publish(
        self,
        data: Dict[str, Any],
        correlation_id: Optional[str] = None,
        metadata: Optional[Dict[str, str]] = None
    ) -> bool:
        """
        Publish an event to the configured topic via Dapr.

        This method is non-blocking - failures are logged but don't
        raise exceptions to ensure the main operation succeeds.

        Args:
            data: Event payload to publish
            correlation_id: Optional correlation ID for tracing (auto-generated if not provided)
            metadata: Optional Dapr metadata headers

        Returns:
            True if publish succeeded, False otherwise
        """
        if not self.enabled:
            logger.debug(f"Dapr disabled, skipping publish to {self.topic}")
            return True

        # Ensure correlation_id is present
        if correlation_id is None:
            correlation_id = self._generate_correlation_id()

        # Add correlation_id to data if not present
        if "correlation_id" not in data:
            data["correlation_id"] = correlation_id

        # Add timestamp if not present
        if "timestamp" not in data:
            data["timestamp"] = datetime.utcnow().isoformat() + "Z"

        try:
            headers = {
                "Content-Type": "application/json",
            }

            # Add Dapr metadata as headers if provided
            if metadata:
                for key, value in metadata.items():
                    headers[f"metadata.{key}"] = value

            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.post(
                    self._get_publish_url(),
                    json=data,
                    headers=headers
                )

                if response.status_code in (200, 201, 204):
                    logger.info(
                        f"Published event to {self.topic}",
                        extra={
                            "topic": self.topic,
                            "correlation_id": correlation_id,
                            "event_type": data.get("event_type", "unknown")
                        }
                    )
                    return True
                else:
                    logger.warning(
                        f"Failed to publish event to {self.topic}: {response.status_code}",
                        extra={
                            "topic": self.topic,
                            "correlation_id": correlation_id,
                            "status_code": response.status_code,
                            "response": response.text[:200] if response.text else None
                        }
                    )
                    return False

        except httpx.TimeoutException:
            logger.warning(
                f"Timeout publishing event to {self.topic}",
                extra={
                    "topic": self.topic,
                    "correlation_id": correlation_id
                }
            )
            return False

        except httpx.RequestError as e:
            logger.warning(
                f"Error publishing event to {self.topic}: {str(e)}",
                extra={
                    "topic": self.topic,
                    "correlation_id": correlation_id,
                    "error": str(e)
                }
            )
            return False

        except Exception as e:
            # Catch-all for any unexpected errors - never block the main operation
            logger.error(
                f"Unexpected error publishing event to {self.topic}: {str(e)}",
                extra={
                    "topic": self.topic,
                    "correlation_id": correlation_id,
                    "error": str(e)
                },
                exc_info=True
            )
            return False

    async def publish_batch(
        self,
        events: list[Dict[str, Any]],
        correlation_id: Optional[str] = None
    ) -> int:
        """
        Publish multiple events to the configured topic.

        Args:
            events: List of event payloads to publish
            correlation_id: Optional shared correlation ID for the batch

        Returns:
            Number of successfully published events
        """
        if not events:
            return 0

        # Use shared correlation_id for batch or generate one
        shared_correlation_id = correlation_id or self._generate_correlation_id()

        success_count = 0
        for event in events:
            if await self.publish(event, correlation_id=shared_correlation_id):
                success_count += 1

        logger.info(
            f"Batch publish completed: {success_count}/{len(events)} events",
            extra={
                "topic": self.topic,
                "correlation_id": shared_correlation_id,
                "total": len(events),
                "success": success_count
            }
        )

        return success_count
