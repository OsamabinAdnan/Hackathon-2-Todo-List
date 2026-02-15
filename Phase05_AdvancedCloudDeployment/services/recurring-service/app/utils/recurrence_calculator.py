"""
Recurrence Calculator
Phase 5: Calculate next due dates for recurring tasks (FR-020, FR-021)

Handles date calculations for daily, weekly, monthly, and yearly recurrence patterns.
"""

import calendar
from datetime import datetime, timedelta
from typing import Optional
import logging

logger = logging.getLogger(__name__)


def calculate_next_due_date(
    current_due_date: datetime,
    recurrence_pattern: str
) -> datetime:
    """
    Calculate the next due date based on recurrence pattern.

    Args:
        current_due_date: The current task's due date
        recurrence_pattern: One of 'daily', 'weekly', 'monthly', 'yearly'

    Returns:
        The next due date

    Raises:
        ValueError: If recurrence_pattern is invalid
    """
    pattern = recurrence_pattern.lower() if recurrence_pattern else "none"

    if pattern == "daily":
        return _calculate_next_daily(current_due_date)
    elif pattern == "weekly":
        return _calculate_next_weekly(current_due_date)
    elif pattern == "monthly":
        return _calculate_next_monthly(current_due_date)
    elif pattern == "yearly":
        return _calculate_next_yearly(current_due_date)
    elif pattern == "none":
        raise ValueError("Cannot calculate next date for non-recurring task")
    else:
        raise ValueError(f"Unknown recurrence pattern: {recurrence_pattern}")


def _calculate_next_daily(current: datetime) -> datetime:
    """Calculate next daily occurrence."""
    return current + timedelta(days=1)


def _calculate_next_weekly(current: datetime) -> datetime:
    """Calculate next weekly occurrence."""
    return current + timedelta(weeks=1)


def _calculate_next_monthly(current: datetime) -> datetime:
    """
    Calculate next monthly occurrence.

    Handles edge cases like:
    - Jan 31 -> Feb 28/29 (not March 3)
    - Jan 30 -> Feb 28/29
    - Dec 31 -> Jan 31
    """
    year = current.year
    month = current.month + 1
    day = current.day

    # Handle year overflow
    if month > 12:
        year += 1
        month = 1

    # Handle day overflow (e.g., Jan 31 -> Feb 28)
    max_day = calendar.monthrange(year, month)[1]
    if day > max_day:
        day = max_day

    return current.replace(year=year, month=month, day=day)


def _calculate_next_yearly(current: datetime) -> datetime:
    """
    Calculate next yearly occurrence.

    Handles leap year edge case:
    - Feb 29, 2024 -> Feb 28, 2025 (non-leap year)
    - Feb 29, 2024 -> Feb 29, 2028 (next leap year occurrence)
    """
    year = current.year + 1
    month = current.month
    day = current.day

    # Handle leap year (Feb 29 -> Feb 28 in non-leap years)
    max_day = calendar.monthrange(year, month)[1]
    if day > max_day:
        day = max_day

    return current.replace(year=year, month=month, day=day)


def get_recurrence_description(pattern: str) -> str:
    """
    Get human-readable description of recurrence pattern.

    Args:
        pattern: Recurrence pattern string

    Returns:
        Human-readable description
    """
    descriptions = {
        "daily": "Repeats every day",
        "weekly": "Repeats every week",
        "monthly": "Repeats every month",
        "yearly": "Repeats every year",
        "none": "Does not repeat"
    }
    return descriptions.get(pattern.lower(), "Unknown recurrence")


def validate_recurrence_pattern(pattern: str) -> bool:
    """
    Validate if a recurrence pattern is valid.

    Args:
        pattern: Recurrence pattern to validate

    Returns:
        True if valid, False otherwise
    """
    valid_patterns = {"daily", "weekly", "monthly", "yearly", "none"}
    return pattern.lower() in valid_patterns if pattern else True
