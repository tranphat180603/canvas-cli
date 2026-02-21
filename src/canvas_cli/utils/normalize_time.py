"""Time normalization utilities for ISO timestamp handling."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


def to_iso(dt: datetime | str | None) -> str | None:
    """
    Convert a datetime or string to ISO 8601 format with Z suffix.

    Args:
        dt: Datetime object, ISO string, or None

    Returns:
        ISO 8601 string with Z suffix, or None if input is None
    """
    if dt is None:
        return None

    if isinstance(dt, str):
        # Try to parse the string
        parsed = from_iso(dt)
        if parsed is None:
            return None
        dt = parsed

    # Ensure UTC timezone
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)

    # Format with Z suffix
    return dt.strftime("%Y-%m-%dT%H:%M:%S") + "Z"


def from_iso(iso_str: str | None) -> datetime | None:
    """
    Parse an ISO 8601 string to datetime.

    Args:
        iso_str: ISO 8601 formatted string

    Returns:
        Datetime object in UTC, or None if parsing fails
    """
    if not iso_str:
        return None

    # Common ISO formats to try
    formats = [
        "%Y-%m-%dT%H:%M:%SZ",
        "%Y-%m-%dT%H:%M:%S.%fZ",
        "%Y-%m-%dT%H:%M:%S%z",
        "%Y-%m-%dT%H:%M:%S.%f%z",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%dT%H:%M:%S.%f",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d",
    ]

    for fmt in formats:
        try:
            dt = datetime.strptime(iso_str, fmt)
            # Ensure UTC timezone
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt
        except ValueError:
            continue

    return None


def now_iso() -> str:
    """
    Get current time as ISO 8601 string.

    Returns:
        Current time in ISO 8601 format with Z suffix
    """
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S") + "Z"


def is_after(dt: datetime | str | None, since: str | None) -> bool:
    """
    Check if a datetime is after a given timestamp.

    Args:
        dt: Datetime or ISO string to check
        since: ISO string to compare against

    Returns:
        True if dt is after since, False otherwise
    """
    if since is None:
        return True

    if dt is None:
        return False

    since_dt = from_iso(since)
    if since_dt is None:
        return True

    check_dt = from_iso(to_iso(dt)) if isinstance(dt, str) else dt
    if check_dt is None:
        return False

    # Ensure both have timezone
    if check_dt.tzinfo is None:
        check_dt = check_dt.replace(tzinfo=timezone.utc)
    if since_dt.tzinfo is None:
        since_dt = since_dt.replace(tzinfo=timezone.utc)

    return check_dt > since_dt


def normalize_canvas_time(value: Any) -> str | None:
    """
    Normalize Canvas API time values to ISO string.

    Canvas sometimes returns datetime objects, sometimes strings.

    Args:
        value: Value from Canvas API (datetime, str, or None)

    Returns:
        ISO string or None
    """
    if value is None:
        return None

    if isinstance(value, datetime):
        return to_iso(value)

    if isinstance(value, str):
        return to_iso(value)

    return None
