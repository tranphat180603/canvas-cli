"""Pagination handling utilities."""

from __future__ import annotations

from typing import Any

from .normalize_time import now_iso


def build_pagination_result(
    items: list[Any],
    page: int,
    page_size: int,
    has_more: bool,
    total_count: int | None = None,
) -> dict[str, Any]:
    """
    Build pagination metadata for response.

    Args:
        items: List of items on current page
        page: Current page number (1-indexed)
        page_size: Number of items per page
        has_more: Whether there are more items available
        total_count: Total count if known (optional)

    Returns:
        Pagination dict with page, page_size, next_page, total_count
    """
    result = {
        "page": page,
        "page_size": page_size,
        "next_page": page + 1 if has_more else None,
    }

    if total_count is not None:
        result["total_count"] = total_count

    return result


def build_tool_output(
    *,
    tool: str,
    items: list[dict[str, Any]],
    page: int,
    page_size: int,
    has_more: bool,
    errors: list[str] | None = None,
    total_count: int | None = None,
) -> dict[str, Any]:
    """
    Build a complete tool output response.

    Args:
        tool: Name of the tool
        items: List of response items
        page: Current page number
        page_size: Items per page
        has_more: Whether more items available
        errors: List of error messages (if any)
        total_count: Total count if known

    Returns:
        Complete tool output dict
    """
    return {
        "ok": len(errors or []) == 0,
        "source": "canvas",
        "tool": tool,
        "items": items,
        "pagination": build_pagination_result(items, page, page_size, has_more, total_count),
        "fetched_at": now_iso(),
        "errors": errors or [],
    }


def slice_items(
    items: list[Any],
    page: int,
    page_size: int,
) -> tuple[list[Any], bool]:
    """
    Slice a list of items based on pagination params.

    Args:
        items: Full list of items
        page: Page number (1-indexed)
        page_size: Number of items per page

    Returns:
        Tuple of (sliced items, has_more)
    """
    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size

    sliced = items[start_idx:end_idx]
    has_more = len(items) > end_idx

    return sliced, has_more
