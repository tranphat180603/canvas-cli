"""Schedule tools - todo, upcoming, calendar, planner."""

from typing import Any, Dict, List, Optional

import httpx
from canvasapi.exceptions import CanvasException

from ..canvas_client import CanvasClient
from ..utils.normalize_time import normalize_canvas_time
from ..utils.pagination import build_tool_output, slice_items
from .auth import resolve_auth


def serialize_todo(todo: Any) -> Dict[str, Any]:
    """Serialize a todo item to dict."""
    return {
        "id": getattr(todo, "id", None),
        "type": getattr(todo, "type", None),
        "assignment_id": getattr(todo, "assignment_id", None),
        "course_id": getattr(todo, "course_id", None),
        "html_url": getattr(todo, "html_url", None),
        "name": getattr(todo, "assignment", {}).get("name") if hasattr(todo, "assignment") else None,
        "context_name": getattr(todo, "context_name", None),
        "needs_grading_count": getattr(todo, "needs_grading_count", None),
        "ignore": getattr(todo, "ignore", None),
        "ignore_permanently": getattr(todo, "ignore_permanently", None),
    }


def serialize_calendar_event(event: Any) -> Dict[str, Any]:
    """Serialize a calendar event to dict."""
    return {
        "id": getattr(event, "id", None),
        "title": getattr(event, "title", None),
        "start_at": normalize_canvas_time(getattr(event, "start_at", None)),
        "end_at": normalize_canvas_time(getattr(event, "end_at", None)),
        "description": getattr(event, "description", None),
        "location_name": getattr(event, "location_name", None),
        "location_address": getattr(event, "location_address", None),
        "context_code": getattr(event, "context_code", None),
        "workflow_state": getattr(event, "workflow_state", None),
        "hidden": getattr(event, "hidden", None),
        "url": getattr(event, "url", None),
        "html_url": getattr(event, "html_url", None),
        "all_day": getattr(event, "all_day", None),
        "created_at": normalize_canvas_time(getattr(event, "created_at", None)),
        "updated_at": normalize_canvas_time(getattr(event, "updated_at", None)),
    }


def serialize_upcoming_event(event: Any) -> Dict[str, Any]:
    """Serialize an upcoming event to dict."""
    # Upcoming events can be assignments or calendar events
    result = {
        "id": getattr(event, "id", None),
        "title": getattr(event, "title", None)
        or getattr(event, "name", None),
        "type": getattr(event, "type", None),
        "html_url": getattr(event, "html_url", None),
    }

    # Handle assignment-like events
    if hasattr(event, "due_at"):
        result["due_at"] = normalize_canvas_time(event.due_at)
        result["course_id"] = getattr(event, "course_id", None)

    # Handle calendar-like events
    if hasattr(event, "start_at"):
        result["start_at"] = normalize_canvas_time(event.start_at)
        result["end_at"] = normalize_canvas_time(getattr(event, "end_at", None))

    return result


def serialize_planner_item(item: Dict[str, Any]) -> Dict[str, Any]:
    """Serialize a planner item to dict."""
    return {
        "id": item.get("id"),
        "title": item.get("title") or item.get("name"),
        "plannable_type": item.get("plannable_type"),
        "plannable_id": item.get("plannable_id"),
        "planner_override_id": item.get("planner_override_id"),
        "course_id": item.get("course_id"),
        "completed": item.get("completed", False),
        "html_url": item.get("html_url"),
        "start_at": normalize_canvas_time(item.get("start_at")),
        "end_at": normalize_canvas_time(item.get("end_at")),
        "due_at": normalize_canvas_time(item.get("due_at")),
        "created_at": normalize_canvas_time(item.get("created_at")),
        "updated_at": normalize_canvas_time(item.get("updated_at")),
    }


def canvas_get_todo_items(
    auth: Optional[Dict[str, Any]] = None,
    *,
    page: int = 1,
    page_size: int = 100,
    since: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Get todo items for the current user.

    Args:
        auth: Canvas auth with canvas_base_url and canvas_access_token
        page: Page number
        page_size: Items per page
        since: ISO timestamp for delta fetch

    Returns:
        Tool output with todo items
    """
    errors: List[str] = []

    try:
        auth_ctx = resolve_auth(auth)
        client = CanvasClient(auth_ctx)
        canvas = client.client

        paginated = canvas.get_todo_items()
        items, has_more = CanvasClient.extract_paginated_list(paginated, page, page_size)

        todos = [serialize_todo(todo) for todo in items]

        return build_tool_output(
            tool="canvas_get_todo_items",
            items=todos,
            page=page,
            page_size=page_size,
            has_more=has_more,
            errors=errors,
        )

    except CanvasException as e:
        errors.append(f"Canvas API error: {e}")
        return build_tool_output(
            tool="canvas_get_todo_items",
            items=[],
            page=page,
            page_size=page_size,
            has_more=False,
            errors=errors,
        )
    except Exception as e:
        errors.append(f"Unexpected error: {e}")
        return build_tool_output(
            tool="canvas_get_todo_items",
            items=[],
            page=page,
            page_size=page_size,
            has_more=False,
            errors=errors,
        )


def canvas_get_upcoming_events(
    auth: Optional[Dict[str, Any]] = None,
    *,
    page: int = 1,
    page_size: int = 100,
    since: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Get upcoming events for the current user.

    Args:
        auth: Canvas auth with canvas_base_url and canvas_access_token
        page: Page number
        page_size: Items per page
        since: ISO timestamp for delta fetch

    Returns:
        Tool output with upcoming events
    """
    errors: List[str] = []

    try:
        auth_ctx = resolve_auth(auth)
        client = CanvasClient(auth_ctx)
        canvas = client.client

        # get_upcoming_events returns a list, not PaginatedList
        events = list(canvas.get_upcoming_events())

        # Apply pagination
        sliced, has_more = slice_items(events, page, page_size)

        serialized = [serialize_upcoming_event(event) for event in sliced]

        return build_tool_output(
            tool="canvas_get_upcoming_events",
            items=serialized,
            page=page,
            page_size=page_size,
            has_more=has_more,
            errors=errors,
        )

    except CanvasException as e:
        errors.append(f"Canvas API error: {e}")
        return build_tool_output(
            tool="canvas_get_upcoming_events",
            items=[],
            page=page,
            page_size=page_size,
            has_more=False,
            errors=errors,
        )
    except Exception as e:
        errors.append(f"Unexpected error: {e}")
        return build_tool_output(
            tool="canvas_get_upcoming_events",
            items=[],
            page=page,
            page_size=page_size,
            has_more=False,
            errors=errors,
        )


def canvas_get_calendar_events(
    auth: Optional[Dict[str, Any]] = None,
    *,
    page: int = 1,
    page_size: int = 100,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    context_codes: Optional[List[str]] = None,
    since: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Get calendar events for the current user.

    Args:
        auth: Canvas auth with canvas_base_url and canvas_access_token
        page: Page number
        page_size: Items per page
        start_date: Start date filter (ISO format)
        end_date: End date filter (ISO format)
        context_codes: Context codes to filter (e.g., ['course_123'])
        since: ISO timestamp for delta fetch

    Returns:
        Tool output with calendar events
    """
    errors: List[str] = []

    try:
        auth_ctx = resolve_auth(auth)
        client = CanvasClient(auth_ctx)

        kwargs: Dict[str, Any] = {}
        if start_date:
            kwargs["start_date"] = start_date
        if end_date:
            kwargs["end_date"] = end_date
        if context_codes:
            kwargs["context_codes"] = context_codes

        canvas = client.client
        paginated = canvas.get_calendar_events(**kwargs)
        items, has_more = CanvasClient.extract_paginated_list(paginated, page, page_size)

        events = [serialize_calendar_event(event) for event in items]

        return build_tool_output(
            tool="canvas_get_calendar_events",
            items=events,
            page=page,
            page_size=page_size,
            has_more=has_more,
            errors=errors,
        )

    except CanvasException as e:
        errors.append(f"Canvas API error: {e}")
        return build_tool_output(
            tool="canvas_get_calendar_events",
            items=[],
            page=page,
            page_size=page_size,
            has_more=False,
            errors=errors,
        )
    except Exception as e:
        errors.append(f"Unexpected error: {e}")
        return build_tool_output(
            tool="canvas_get_calendar_events",
            items=[],
            page=page,
            page_size=page_size,
            has_more=False,
            errors=errors,
        )


def canvas_get_planner_items(
    auth: Optional[Dict[str, Any]] = None,
    *,
    page: int = 1,
    page_size: int = 100,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    context_codes: Optional[List[str]] = None,
    since: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Get planner items for the current user via direct HTTP request.

    The planner API is not fully supported by canvasapi, so we use httpx.

    Args:
        auth: Canvas auth with canvas_base_url and canvas_access_token
        page: Page number
        page_size: Items per page
        start_date: Start date filter (ISO format)
        end_date: End date filter (ISO format)
        context_codes: Context codes to filter
        since: ISO timestamp for delta fetch

    Returns:
        Tool output with planner items
    """
    errors: List[str] = []

    try:
        auth_ctx = resolve_auth(auth)
        client = CanvasClient(auth_ctx)
        base_url = client.base_url

        # Build URL
        url = f"{base_url}/planner/items"

        # Build params
        params: Dict[str, Any] = {"per_page": page_size}
        if page > 1:
            # Canvas uses page tokens, not page numbers
            # For simplicity, we'll use offset
            params["page"] = page
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date
        if context_codes:
            params["context_codes[]"] = context_codes

        headers = {"Authorization": f"Bearer {client.access_token}"}

        with httpx.Client() as http_client:
            response = http_client.get(url, params=params, headers=headers, timeout=30.0)
            response.raise_for_status()
            data = response.json()

        # Check for more pages via Link header
        has_more = 'rel="next"' in response.headers.get("link", "")

        # Serialize items
        items = [serialize_planner_item(item) for item in data]

        return build_tool_output(
            tool="canvas_get_planner_items",
            items=items,
            page=page,
            page_size=page_size,
            has_more=has_more,
            errors=errors,
        )

    except httpx.HTTPStatusError as e:
        errors.append(f"HTTP error: {e.response.status_code} - {e.response.text}")
        return build_tool_output(
            tool="canvas_get_planner_items",
            items=[],
            page=page,
            page_size=page_size,
            has_more=False,
            errors=errors,
        )
    except CanvasException as e:
        errors.append(f"Canvas API error: {e}")
        return build_tool_output(
            tool="canvas_get_planner_items",
            items=[],
            page=page,
            page_size=page_size,
            has_more=False,
            errors=errors,
        )
    except Exception as e:
        errors.append(f"Unexpected error: {e}")
        return build_tool_output(
            tool="canvas_get_planner_items",
            items=[],
            page=page,
            page_size=page_size,
            has_more=False,
            errors=errors,
        )
