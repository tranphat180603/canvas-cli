"""ID handling utilities for Canvas API."""

from __future__ import annotations

import re
from typing import Any


def parse_context_code(context_code: str) -> tuple[str, int] | None:
    """
    Parse a Canvas context code into type and ID.

    Canvas context codes look like:
    - "course_123"
    - "user_456"
    - "group_789"

    Args:
        context_code: Canvas context code string

    Returns:
        Tuple of (context_type, context_id) or None if invalid
    """
    if not context_code:
        return None

    match = re.match(r"^(course|user|group|account|section)_(\d+)$", context_code)
    if match:
        return match.group(1), int(match.group(2))

    return None


def build_context_code(context_type: str, context_id: int) -> str:
    """
    Build a Canvas context code from type and ID.

    Args:
        context_type: Type of context (course, user, group, etc.)
        context_id: Numeric ID

    Returns:
        Context code string like "course_123"
    """
    return f"{context_type}_{context_id}"


def extract_id(value: Any) -> int | None:
    """
    Extract a numeric ID from various Canvas object types.

    Canvas objects can be:
    - Integers
    - Strings containing integers
    - Objects with .id attribute
    - Dicts with 'id' key

    Args:
        value: Value to extract ID from

    Returns:
        Integer ID or None
    """
    if value is None:
        return None

    if isinstance(value, int):
        return value

    if isinstance(value, str):
        try:
            return int(value)
        except ValueError:
            # Try to extract digits from the string
            match = re.search(r"\d+", value)
            if match:
                return int(match.group())
            return None

    if hasattr(value, "id"):
        return extract_id(value.id)

    if isinstance(value, dict) and "id" in value:
        return extract_id(value["id"])

    return None


def safe_int(value: Any, default: int = 0) -> int:
    """
    Safely convert a value to int with a default.

    Args:
        value: Value to convert
        default: Default value if conversion fails

    Returns:
        Integer value or default
    """
    result = extract_id(value)
    return result if result is not None else default


def to_sis_id(canvas_id: int, prefix: str = "") -> str:
    """
    Convert a Canvas ID to SIS ID format.

    Args:
        canvas_id: Canvas numeric ID
        prefix: Optional prefix for SIS ID

    Returns:
        SIS ID string
    """
    if prefix:
        return f"{prefix}{canvas_id}"
    return str(canvas_id)
