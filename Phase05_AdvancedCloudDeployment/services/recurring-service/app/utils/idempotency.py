"""
Idempotency Utilities
Phase 5: Duplicate event detection (FR-022)

Provides in-memory idempotency tracking for event processing.
In production, this should use a distributed cache (Redis) or database.
"""

import logging
from typing import Dict
from datetime import datetime, timedelta
import asyncio

logger = logging.getLogger(__name__)

# In-memory cache for processed events
# Key: (event_id, service_name), Value: timestamp
_processed_events: Dict[str, datetime] = {}
_cache_lock = asyncio.Lock()

# Cache TTL - events older than this are removed from cache
CACHE_TTL_HOURS = 24


async def is_event_processed(event_id: str, service_name: str) -> bool:
    """
    Check if an event has already been processed by this service.

    Args:
        event_id: Unique event identifier
        service_name: Name of the processing service

    Returns:
        True if already processed, False otherwise
    """
    cache_key = f"{service_name}:{event_id}"

    async with _cache_lock:
        # Clean up old entries periodically
        await _cleanup_old_entries()

        if cache_key in _processed_events:
            logger.debug(f"Event {event_id} already processed by {service_name}")
            return True

        return False


async def mark_event_processed(event_id: str, service_name: str) -> None:
    """
    Mark an event as processed by this service.

    Args:
        event_id: Unique event identifier
        service_name: Name of the processing service
    """
    cache_key = f"{service_name}:{event_id}"

    async with _cache_lock:
        _processed_events[cache_key] = datetime.utcnow()
        logger.debug(f"Marked event {event_id} as processed by {service_name}")


async def _cleanup_old_entries() -> None:
    """
    Remove entries older than CACHE_TTL_HOURS from the cache.

    This prevents memory growth in long-running services.
    """
    cutoff = datetime.utcnow() - timedelta(hours=CACHE_TTL_HOURS)

    keys_to_remove = [
        key for key, timestamp in _processed_events.items()
        if timestamp < cutoff
    ]

    for key in keys_to_remove:
        del _processed_events[key]

    if keys_to_remove:
        logger.debug(f"Cleaned up {len(keys_to_remove)} old idempotency entries")


def get_cache_stats() -> Dict[str, int]:
    """
    Get statistics about the idempotency cache.

    Returns:
        Dictionary with cache statistics
    """
    return {
        "total_entries": len(_processed_events),
        "cache_ttl_hours": CACHE_TTL_HOURS
    }
